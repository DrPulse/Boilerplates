#!/usr/bin/env python3
"""
Parse Renovate PR information and output GitHub Actions variables.
This script handles service name extraction, version parsing, and update type detection.
"""

import json
import os
import re
import sys


def extract_service_name(pr_title: str) -> str:
    """
    Extract service name from Renovate PR title.

    Handles formats:
    - "Update docker/image-name to v1.2.3"
    - "Update actions/checkout action to v5"
    - "Update dependency package-name to v1.2.3"
    - "Lock file maintenance"
    """
    try:
        if "/" in pr_title:
            # Format with slash: "Update docker/image-name to ..."
            return pr_title.split("/")[1].split(" ")[0]
        elif pr_title.lower().startswith("update "):
            # Format without slash: "Update package-name to ..."
            title_lower = pr_title.lower()
            if " to " in title_lower:
                return pr_title.split(" ")[1].split(" ")[0]
            elif " action" in title_lower:
                return pr_title.split(" ")[1]
        elif "lock file" in pr_title.lower():
            return "Lock Files"
        else:
            # Fallback: use first meaningful word after common prefixes
            words = pr_title.split()
            if len(words) > 1:
                return words[1]
    except (IndexError, AttributeError) as e:
        print(
            f"Warning: Could not parse service name from title '{pr_title}': {e}",
            file=sys.stderr,
        )
        return pr_title[:50]  # Use first 50 chars as fallback

    return "Unknown"


def extract_versions_from_body(pr_body: str) -> tuple[str, str, str]:
    """
    Extract old version, new version, and update type from PR body table.

    Looks for pattern: | [link](url) | type | `old_version` -> `new_version` |
    Returns: (old_version, new_version, update_type)
    """
    if not pr_body:
        return "", "", ""

    # Try with arrow character (→) or ASCII arrow (->)
    table_match = re.search(
        r"\|\s*\[.*?\]\(.*?\)\s*\|\s*(\w+)\s*\|\s*`(.*?)`\s*(?:->|→)\s*`(.*?)`\s*\|",
        pr_body,
    )

    if table_match:
        update_type = table_match.group(1).lower()  # patch, minor, major
        old_version = table_match.group(2)
        new_version = table_match.group(3)
        return old_version, new_version, update_type

    return "", "", ""


def extract_version_from_title(pr_title: str) -> str:
    """Extract version from PR title as fallback."""
    version_match = re.search(r"to [v]?(\d+[\.\d]*\w*)", pr_title)
    if version_match:
        return version_match.group(1)
    return ""


def determine_update_type(old_version: str, new_version: str) -> str:
    """
    Determine if update is major, minor, or patch.
    Returns: "major", "minor", "patch", or "unknown"
    """
    if not old_version or not new_version:
        return "unknown"

    try:
        # Strip 'v' prefix and split into parts
        old_parts = old_version.lstrip("v").split(".")
        new_parts = new_version.lstrip("v").split(".")

        # Ensure we have at least major.minor.patch
        while len(old_parts) < 3:
            old_parts.append("0")
        while len(new_parts) < 3:
            new_parts.append("0")

        # Extract numeric parts (ignore suffixes like -alpha, -beta)
        old_major = int(re.match(r"(\d+)", old_parts[0]).group(1))
        new_major = int(re.match(r"(\d+)", new_parts[0]).group(1))

        if new_major > old_major:
            return "major"

        old_minor = int(re.match(r"(\d+)", old_parts[1]).group(1))
        new_minor = int(re.match(r"(\d+)", new_parts[1]).group(1))

        if new_minor > old_minor:
            return "minor"

        # If we get here, it's likely a patch or build number change
        return "patch"

    except (ValueError, AttributeError, IndexError) as e:
        print(
            f"Warning: Could not parse versions '{old_version}' -> '{new_version}': {e}",
            file=sys.stderr,
        )
        return "unknown"


def main():
    """Main entry point."""
    # Get inputs from environment variables
    pr_title = os.environ.get("PR_TITLE", "")
    pr_body = os.environ.get("PR_BODY", "")

    if not pr_title:
        print("Error: PR_TITLE environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Extract service name
    service_name = extract_service_name(pr_title)

    # Extract versions and update type from PR body
    old_version, new_version, update_type = extract_versions_from_body(pr_body)

    # Fallback to title if body extraction failed
    if not new_version:
        new_version = extract_version_from_title(pr_title)

    # Fallback: determine update type manually if not found in PR body
    if not update_type:
        update_type = determine_update_type(old_version, new_version)

    # Build version display
    if old_version and new_version:
        version_display = f"`{old_version}` -> `{new_version}`"
    elif new_version:
        version_display = f"`{new_version}`"
    else:
        version_display = ""

    # Output results as JSON for easy parsing
    result = {
        "service_name": service_name,
        "old_version": old_version,
        "new_version": new_version,
        "update_type": update_type,
        "version_display": version_display,
    }

    # Write to GitHub Actions output
    # Using the new multiline format for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            for key, value in result.items():
                # Escape multiline values
                value_str = (
                    str(value)
                    .replace("%", "%25")
                    .replace("\n", "%0A")
                    .replace("\r", "%0D")
                )
                f.write(f"{key}={value_str}\n")

    # Also print as JSON for debugging
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
