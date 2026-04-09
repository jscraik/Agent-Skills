#!/usr/bin/env python3
"""Parse CodeRabbit plain review output into a stable severity envelope."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEVERITIES = ("critical", "warning", "info")
HEADING_PATTERNS = {
    "critical": re.compile(r"^(?:#{1,6}\s*)?critical(?:\s+(?:issues?|findings?))?\s*:?\s*$", re.IGNORECASE),
    "warning": re.compile(r"^(?:#{1,6}\s*)?warnings?(?:\s+(?:issues?|findings?))?\s*:?\s*$", re.IGNORECASE),
    "info": re.compile(
        r"^(?:#{1,6}\s*)?(?:info|informational)(?:\s+(?:issues?|findings?))?\s*:?\s*$",
        re.IGNORECASE,
    ),
}
BULLET_PATTERN = re.compile(r"^(?:[-*]\s+|\d+\.\s+)(.+)$")
TAGGED_FINDING_PATTERN = re.compile(r"^\[(critical|warning|info)\]\s*(.+)$", re.IGNORECASE)


def _read_text(input_path: str) -> str:
    if input_path == "-":
        return sys.stdin.read()
    return Path(input_path).read_text(encoding="utf-8")


def _detect_severity(line: str) -> str | None:
    for severity, pattern in HEADING_PATTERNS.items():
        if pattern.search(line):
            return severity
    return None


def _extract_bullet(line: str) -> str | None:
    match = BULLET_PATTERN.match(line)
    if match is None:
        return None
    return match.group(1).strip()


def parse_plain_output(text: str) -> dict[str, object]:
    findings: dict[str, list[str]] = {severity: [] for severity in SEVERITIES}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        detected = _detect_severity(line)
        if detected is not None:
            current = detected
            continue

        tagged_match = TAGGED_FINDING_PATTERN.match(line)
        if tagged_match is not None:
            severity = tagged_match.group(1).lower()
            findings[severity].append(tagged_match.group(2).strip())
            current = severity
            continue

        bullet = _extract_bullet(line)
        if bullet is not None:
            bullet_tagged_match = TAGGED_FINDING_PATTERN.match(bullet)
            if bullet_tagged_match is not None:
                severity = bullet_tagged_match.group(1).lower()
                findings[severity].append(bullet_tagged_match.group(2).strip())
                current = severity
                continue
        if current is not None and bullet is not None:
            findings[current].append(bullet)

    counts = {severity: len(entries) for severity, entries in findings.items()}
    return {
        "schema_version": 1,
        "summary": "Parsed CodeRabbit plain review output into severity buckets.",
        "counts": counts,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="-",
        help="Path to plain review output file, or '-' to read stdin.",
    )
    args = parser.parse_args()

    try:
        text = _read_text(args.input)
    except OSError as exc:
        print(f"error: failed to read input: {exc}", file=sys.stderr)
        return 1

    payload = parse_plain_output(text)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
