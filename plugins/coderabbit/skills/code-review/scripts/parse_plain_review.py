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


def _append_tagged_finding(text: str, findings: dict[str, list[str]]) -> str | None:
    match = TAGGED_FINDING_PATTERN.match(text)
    if match is None:
        return None
    severity = match.group(1).lower()
    findings[severity].append(match.group(2).strip())
    return severity


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

        severity = _append_tagged_finding(line, findings)
        if severity is not None:
            current = severity
            continue

        bullet = _extract_bullet(line)
        if bullet is not None:
            severity = _append_tagged_finding(bullet, findings)
            if severity is not None:
                current = severity
                continue
            if current is None:
                findings.setdefault('unclassified', []).append(bullet)
                continue
        if current is not None and bullet is not None:
            findings[current].append(bullet)

    # Build actions from critical and warning findings
    actions = []
    for finding in findings["critical"]:
        actions.append(f"[CRITICAL] {finding}")
    for finding in findings["warning"]:
        actions.append(f"[WARNING] {finding}")

    # Determine risk note based on findings
    risk_note = ""
    if findings["critical"]:
        risk_note = f"{len(findings['critical'])} critical issue(s) require immediate attention."
    elif findings["warning"]:
        risk_note = f"{len(findings['warning'])} warning(s) should be reviewed before merge."
    else:
        risk_note = "No critical or warning issues detected."

    # Determine next step
    if findings["critical"]:
        next_step = "Address critical findings before proceeding."
    elif findings["warning"]:
        next_step = "Review and address warnings as appropriate."
    else:
        next_step = "Review informational findings and proceed when ready."

    return {
        "schema_version": 1,
        "summary": "Parsed CodeRabbit plain review output into severity buckets.",
        "findings": findings,
        "actions": actions,
        "validation": [],
        "risk_note": risk_note,
        "next_step": next_step,
        "rerun_status": "",
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