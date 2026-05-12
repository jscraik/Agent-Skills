#!/usr/bin/env python3
"""Validate BLUF-first review structure in durable HE Markdown artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FIELD_RE = re.compile(r"(?m)^(BLUF|Decision Needed|Top Risks|Next Action):\s*\S")
HEADING_RE = re.compile(r"(?m)^(#{2,4})\s+(.+?)\s*$")
BLUF_RE = re.compile(r"(?m)^BLUF:\s*(\S.+)$")

EXEMPT_HEADINGS = {
    "Command Summary",
    "BLUF-Only Summary",
    "No-Fog Gate",
    "References",
    "Validation",
}


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def section_body(text: str, start: int, level: int) -> str:
    pattern = re.compile(rf"(?m)^#{{1,{level}}}\s+")
    match = pattern.search(text, start)
    end = match.start() if match else len(text)
    return text[start:end]


def validate(path: Path, *, compact: bool) -> list[str]:
    text = strip_frontmatter(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if "## Command Summary" not in text:
        errors.append("missing ## Command Summary")
    else:
        command_summary = text.split("## Command Summary", 1)[1].split("\n## ", 1)[0]
        found_fields = {match.group(1) for match in FIELD_RE.finditer(command_summary)}
        for field in ("BLUF", "Decision Needed", "Top Risks", "Next Action"):
            if field not in found_fields:
                errors.append(f"Command Summary missing non-empty {field}:")

    if not compact and "## BLUF-Only Summary" not in text:
        errors.append("missing ## BLUF-Only Summary")

    blufs = [match.group(1).strip() for match in BLUF_RE.finditer(text)]
    if not blufs:
        errors.append("no non-empty BLUF lines found")
    for index, bluf in enumerate(blufs, start=1):
        if len(bluf.split()) > 35:
            errors.append(f"BLUF {index} is too long ({len(bluf.split())} words)")
        if bluf.endswith(":"):
            errors.append(f"BLUF {index} ends like a label instead of a sentence")

    for heading in HEADING_RE.finditer(text):
        level = len(heading.group(1))
        title = heading.group(2).strip()
        if title in EXEMPT_HEADINGS or (title.startswith("<") and title.endswith(">")):
            continue
        body = section_body(text, heading.end(), level)
        if not BLUF_RE.search(body):
            errors.append(f"section lacks BLUF: {title}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--compact", action="store_true", help="Allow small artifacts without BLUF-Only Summary")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = []
    failed = False
    for path in args.paths:
        errors = validate(path, compact=args.compact)
        failed = failed or bool(errors)
        results.append({"path": str(path), "status": "pass" if not errors else "fail", "errors": errors})

    result = {"schema_version": 1, "status": "fail" if failed else "pass", "results": results}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for item in results:
            print(f"{item['path']}: {item['status']}")
            for error in item["errors"]:
                print(f"  error: {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
