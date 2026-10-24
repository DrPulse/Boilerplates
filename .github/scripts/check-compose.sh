#!/usr/bin/env bash
# Render a compose file to canonical form, for before/after comparison.
#
# The stack directory is copied to a scratch dir so the real tree is never
# touched, every variable referenced by the file is set to a non-empty
# placeholder, and an empty .env is provided for stacks using `env_file:` --
# so interpolation is deterministic and identical on both sides of the diff.
set -uo pipefail

file="$1"
dir=$(dirname "$file")
base=$(basename "$file")

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
cp -r "$dir/." "$scratch/"

: > "$scratch/.env"
# Variables that already carry a `${VAR:-default}` fallback are left alone.
# Port- and id-like variables need numeric values; everything else gets a
# path-like value that is valid as a volume source, a user, or a plain string.
grep -ohE '\$\{[A-Za-z_][A-Za-z0-9_]*:-' "$file" | tr -d '${:-' | sort -u > "$scratch/.defaulted"
grep -ohE '\$\{?[A-Za-z_][A-Za-z0-9_]*' "$file" | tr -d '${' | sort -u |
  grep -vxF -f "$scratch/.defaulted" |
  awk '/(^|_)(PORT|PORTS|UID|GID)$/ {print $0 "=1000"; next} {print $0 "=/placeholder"}' \
  > "$scratch/.placeholders.env"

(cd "$scratch" && docker compose -p compose-gate --env-file .placeholders.env -f "$base" config 2>&1) |
  grep -v 'level=warning'
