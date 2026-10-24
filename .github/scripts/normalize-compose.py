#!/usr/bin/env python3
"""Normalize docker compose files to the repository convention.

Rules (see repo README / PR description):
  * `environment` and `labels` use mapping form (`KEY: value`), never `- KEY=value`.
  * `ports` and `volumes` stay sequences.
  * Service fields are ordered per FIELD_ORDER; `network_mode` takes the
    `networks` slot; any field outside FIELD_ORDER keeps its absolute index.
  * Comments travel with the field they document. Commented-out field blocks
    (`# ports:`) are ordered as if they were that field. No comment is lost.
  * Blank lines between services are kept, blank lines inside a service dropped.
  * Exactly one trailing newline, no trailing whitespace.

Operates on lines, never round-trips through a YAML library, so comments and
formatting survive untouched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FIELD_ORDER = [
    "image",
    "container_name",
    "restart",
    "user",
    "depends_on",
    "profiles",
    "cap_add",
    "networks",
    "dns",
    "ports",
    "environment",
    "volumes",
    "labels",
    "healthcheck",
]
# network_mode is mutually exclusive with networks and lives in its slot.
SLOT = {name: i for i, name in enumerate(FIELD_ORDER)}
SLOT["network_mode"] = SLOT["networks"]

MAPPING_FIELDS = {"environment", "labels"}

# Content pad of a field-level comment: 4 spaces of indent plus `# `.
FIELD_COMMENT_PAD = 5

FIELD_RE = re.compile(r"^    ([A-Za-z_][A-Za-z0-9_.-]*):(?:\s|$)")
SERVICE_RE = re.compile(r"^  ([A-Za-z0-9_.-]+):\s*$")
TOPLEVEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):")
# `    # ports:` / `    #    ports:` / `    ## extra_hosts:` -- a commented-out
# field header, with any amount of padding between the hashes and the key.
# Some files write these flush to column 0, so the line indent is not a filter.
# A trailing `# note` after the key is still a bare header, e.g.
# `# extends: # uncomment this section for hardware acceleration`.
COMMENT_FIELD_RE = re.compile(r"^ {0,6}#+( *)([a-z_][a-z0-9_]*):(?: +#.*)?\s*$")
# `  # mealie:` -- a commented-out service (or other service-level key).
COMMENT_SERVICE_RE = re.compile(r"^ {0,2}#+ ?[A-Za-z0-9_.-]+:\s*$")
# Content of a comment line, i.e. what follows the hashes.
COMMENT_BODY_RE = re.compile(r"^(\s*)#+( *)(.*)$")
ITEM_RE = re.compile(r"^(\s*)- (.*)$")


class Block:
    """A service field plus the comments that document it."""

    def __init__(self, name: str, lines: list[str], lead: list[str], commented: bool,
                 pad: int = 0):
        self.name = name
        self.lines = lines
        self.lead = lead
        self.commented = commented
        self.pad = pad  # comment-content indent of a commented-out header

    @property
    def known(self) -> bool:
        return self.name in SLOT

    def reindent(self) -> None:
        """Put the block's body on a 2-space step below its header (indent 6).

        Relative nesting inside the body is preserved; only the common offset
        moves, so 4-space and 8-space outliers both land on 6.
        """
        if self.commented or len(self.lines) < 2:
            return
        body = self.lines[1:]
        indents = [
            len(l) - len(l.lstrip())
            for l in body
            if l.strip() and not l.strip().startswith("#")
        ]
        if not indents:
            return
        shift = 6 - min(indents)
        if shift == 0:
            return
        if shift > 0:
            self.lines[1:] = [(" " * shift) + l if l.strip() else l for l in body]
        else:
            self.lines[1:] = [l[-shift:] if l.strip() else l for l in body]

    def render(self) -> list[str]:
        return self.lead + self.lines


def needs_quotes(value: str) -> bool:
    """True when a bare scalar would change meaning or break the parse."""
    if value == "":
        return False  # rendered as `KEY:` (null) -- intentional
    if value[0] in "*&!%@`{[|>'\"" or value.startswith("- "):
        return True
    if value != value.strip():
        return True
    if ": " in value or value.endswith(":") or " #" in value:
        return True
    # Numbers whose YAML value would not round-trip to the same text, e.g.
    # `022` (octal -> 18), `1.10` (-> 1.1), `0x1f`, `1_000`.
    if re.fullmatch(r"[-+]?[0-9][0-9_]*(\.[0-9_]*)?([eE][-+]?[0-9]+)?", value) or \
            re.fullmatch(r"0[xXoObB][0-9a-fA-F_]+", value):
        try:
            parsed = int(value, 0) if "." not in value and "e" not in value.lower() \
                else float(value)
            if str(parsed) != value:
                return True
        except ValueError:
            return True
    if value.lower() in {
        "y", "n", "yes", "no", "on", "off", "true", "false", "null", "~",
    }:
        return True
    return False


def to_mapping(lines: list[str]) -> list[str]:
    """Convert `- KEY=value` sequence entries to `KEY: value` mapping entries."""
    out = []
    for line in lines:
        m = ITEM_RE.match(line)
        if not m:
            out.append(line)
            continue
        indent, item = m.groups()
        # A trailing `# comment` on the item is YAML comment syntax, not part of
        # the value: detach it and re-attach it to the mapping entry.
        comment = ""
        if "#" in item:
            head, sep, rest = item.partition("#")
            if head.rstrip() != head or head == "":
                comment = " " + sep + rest
                item = head.rstrip()
        if "=" not in item:
            out.append(f"{indent}{item.strip()}:{comment}")
            continue
        key, _, value = item.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value == "":
            out.append(f"{indent}{key}:{comment}")
        elif needs_quotes(value):
            out.append(f'{indent}{key}: "{value}"{comment}')
        else:
            out.append(f"{indent}{key}: {value}{comment}")
    return out


def is_continuation(line: str, block: "Block | None") -> bool:
    """True when `line` is part of an open commented-out field block.

    A continuation is a comment line whose content is either a sequence item
    (`#   - 5432:5432`) or indented deeper than the header's own content
    (`#   file: hwaccel.transcoding.yml` under `# extends:`).
    """
    if block is None or not block.commented:
        return False
    m = COMMENT_BODY_RE.match(line)
    if not m or not m.group(3):
        return False
    pad = len(m.group(1)) + len(m.group(2))
    return m.group(3).startswith("- ") or pad > block.pad


def ends_service_body(lines: list[str], j: int) -> bool:
    """True when `lines[j]` is a document-level comment, not service content.

    Comments at service level or shallower are ambiguous: they may introduce
    the next service, or document a commented-out field inside the current one.
    Scanning forward to the next real line settles it -- if that line is a
    service field (indent >= 4) the comment is service content.
    """
    line = lines[j]
    if not line.strip().startswith("#"):
        return False
    if len(line) - len(line.lstrip()) > 2:
        return False
    m = COMMENT_BODY_RE.match(line)
    if m and m.group(3).startswith("- "):
        return False  # a commented-out sequence item
    for nxt in lines[j + 1:]:
        if not nxt.strip() or nxt.strip().startswith("#"):
            continue
        return not nxt.startswith("    ")
    return True


def split_blocks(body: list[str]) -> tuple[list[Block], list[str]]:
    """Split a service body into field blocks plus any trailing trivia."""
    blocks: list[Block] = []
    lead: list[str] = []
    cur: Block | None = None

    def detachable(line: str, deep_ok: bool = False) -> bool:
        """True for a trailing comment that documents the *next* field.

        Commented-out sequence items (`#   - proxy`) always belong to the block
        they follow. Comments whose content is indented past field level
        (`#      LE_EMAIL: ""`) document the body they sit in, unless the next
        block is itself a commented-out field, which they plausibly introduce.
        """
        m = COMMENT_BODY_RE.match(line)
        if not m or not line.strip().startswith("#"):
            return False
        if m.group(3).startswith("- "):
            return False
        pad = len(m.group(1)) + len(m.group(2))
        return pad <= FIELD_COMMENT_PAD or deep_ok

    def flush_trailing_trivia(deep_ok: bool = False) -> None:
        """Move trailing comments off the current block; they lead the next one."""
        nonlocal lead
        if cur is None or cur.commented:
            return  # a commented-out block's comment lines *are* its body
        cut = len(cur.lines)
        while cut > 1 and detachable(cur.lines[cut - 1], deep_ok):
            cut -= 1
        lead = cur.lines[cut:] + lead
        del cur.lines[cut:]

    for line in body:
        stripped = line.strip()
        if not stripped:
            continue  # blank lines inside a service are dropped
        cfield = COMMENT_FIELD_RE.match(line)
        if cfield and not is_continuation(line, cur):
            flush_trailing_trivia(deep_ok=True)
            pad = len(line) - len(line.lstrip()) + len(cfield.group(1))
            cur = Block(cfield.group(2), [line], lead, commented=True, pad=pad)
            blocks.append(cur)
            lead = []
            continue
        if is_continuation(line, cur):
            cur.lines.append(line)
            continue
        field = FIELD_RE.match(line)
        if field:
            # Collapse stray whitespace (tabs included) after the key colon.
            head, sep, rest = line.partition(":")
            if rest.strip():
                line = f"{head}{sep} {rest.strip()}"
            flush_trailing_trivia()
            cur = Block(field.group(1), [line], lead, commented=False)
            blocks.append(cur)
            lead = []
            continue
        if cur is None or detachable(line):
            lead.append(line)
            continue
        cur.lines.append(line)

    if cur is not None:
        flush_trailing_trivia()
    return blocks, lead


def reorder(blocks: list[Block]) -> list[Block]:
    """Known fields sort into schema order; unknown fields pin their index."""
    known = sorted(
        (b for b in blocks if b.known),
        key=lambda b: (SLOT[b.name], blocks.index(b)),
    )
    result: list[Block | None] = [None] * len(blocks)
    for i, b in enumerate(blocks):
        if not b.known:
            result[i] = b
    it = iter(known)
    for i in range(len(result)):
        if result[i] is None:
            result[i] = next(it)
    return [b for b in result if b is not None]


def normalize(text: str) -> str:
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    lines = [line.rstrip() for line in lines]

    out: list[str] = []
    i = 0
    in_services = False
    while i < len(lines):
        line = lines[i]
        if TOPLEVEL_RE.match(line):
            in_services = line.startswith("services:")
            out.append(line)
            i += 1
            continue
        service = SERVICE_RE.match(line) if in_services else None
        if not service:
            out.append(line)
            i += 1
            continue

        # Collect this service's body: everything until the next service or
        # top-level key, minus trailing blank lines (which separate services).
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() and (TOPLEVEL_RE.match(nxt) or SERVICE_RE.match(nxt)):
                break
            # A comment at service level or shallower ends the body when what
            # follows it belongs to the document rather than to this service
            # (a commented-out service `# mealie:`, or a banner comment such as
            # `# Media server invitation` sitting above the next service). It is
            # left verbatim, blank lines around it included.
            if ends_service_body(lines, j):
                break
            j += 1
        body = lines[i + 1 : j]
        tail = []
        while body and not body[-1].strip():
            tail.append(body.pop())

        blocks, trailing = split_blocks(body)
        for b in blocks:
            b.reindent()
            if b.name in MAPPING_FIELDS and not b.commented:
                b.lines = [b.lines[0]] + to_mapping(b.lines[1:])
        out.append(line)
        for b in reorder(blocks):
            out.extend(b.render())
        out.extend(trailing)
        out.extend(tail)
        i = j

    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    changed = 0
    for arg in argv:
        path = Path(arg)
        original = path.read_text()
        result = normalize(original)
        if result != original:
            path.write_text(result)
            changed += 1
            print(f"normalized {path}")
        else:
            print(f"unchanged  {path}")
    print(f"\n{changed} file(s) changed, {len(argv) - changed} unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
