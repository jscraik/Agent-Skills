#!/usr/bin/env python3
"""Validate high-signal steering uptake surfaces."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = ROOT / "Docs/agents/19-high-signal-steering-feedback.md"
LEDGER_PATH = ROOT / ".harness/quality/steering-uptake.md"
README_PATH = ROOT / "Docs/agents/README.md"
VALID_STATUSES = {"open", "validated", "blocked"}
REQUIRED_HEADERS = [
    "Date",
    "Trigger",
    "Failure pattern",
    "Mechanism",
    "Durable guardrail",
    "Validation",
    "Status",
]


@dataclass
class Finding:
    code: str
    message: str
    path: str


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _table_rows(markdown: str) -> tuple[list[str], list[list[str]]]:
    table_lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 3:
        return [], []

    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: list[list[str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if any(cells):
            rows.append(cells)
    return headers, rows


def validate(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    doc_path = root / _relative(DOC_PATH)
    ledger_path = root / _relative(LEDGER_PATH)
    readme_path = root / _relative(README_PATH)

    if not doc_path.exists():
        findings.append(Finding("STEERING_DOC_MISSING", "High-signal steering feedback doc is missing.", _relative(doc_path)))
    else:
        doc = _read(doc_path)
        for phrase in ["Stop Rule", "Uptake Loop", "Required Evidence", "validate_steering_uptake.py"]:
            if phrase not in doc:
                findings.append(Finding("STEERING_DOC_INCOMPLETE", f"Missing required phrase: {phrase}", _relative(doc_path)))

    if not ledger_path.exists():
        findings.append(Finding("STEERING_LEDGER_MISSING", "Steering uptake ledger is missing.", _relative(ledger_path)))
    else:
        ledger = _read(ledger_path)
        headers, rows = _table_rows(ledger)
        if headers != REQUIRED_HEADERS:
            findings.append(Finding("STEERING_LEDGER_HEADERS", f"Expected headers {REQUIRED_HEADERS}, got {headers}", _relative(ledger_path)))
        if not rows:
            findings.append(Finding("STEERING_LEDGER_EMPTY", "Ledger must contain at least one steering uptake row.", _relative(ledger_path)))
        for index, row in enumerate(rows, start=1):
            if len(row) != len(REQUIRED_HEADERS):
                findings.append(Finding("STEERING_LEDGER_ROW_WIDTH", f"Row {index} has {len(row)} cells, expected {len(REQUIRED_HEADERS)}.", _relative(ledger_path)))
                continue
            record = dict(zip(REQUIRED_HEADERS, row))
            for field in REQUIRED_HEADERS:
                if not record[field] or record[field].lower() in {"none", "n/a", "todo"}:
                    findings.append(Finding("STEERING_LEDGER_FIELD_EMPTY", f"Row {index} has weak value for {field}.", _relative(ledger_path)))
            if record["Status"] not in VALID_STATUSES:
                findings.append(Finding("STEERING_LEDGER_STATUS", f"Row {index} has invalid status {record['Status']!r}.", _relative(ledger_path)))
            if record["Status"] == "validated" and "validate_steering_uptake.py" not in record["Validation"]:
                findings.append(Finding("STEERING_LEDGER_VALIDATION_WEAK", f"Row {index} marked validated without steering validator evidence.", _relative(ledger_path)))

    if not readme_path.exists():
        findings.append(Finding("AGENT_DOC_INDEX_MISSING", "Agent docs index is missing.", _relative(readme_path)))
    elif "19-high-signal-steering-feedback" not in _read(readme_path):
        findings.append(Finding("STEERING_DOC_NOT_INDEXED", "Agent docs index must link the steering feedback doc.", _relative(readme_path)))

    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    findings = validate()
    payload = {
        "status": "fail" if findings else "pass",
        "checked": [
            _relative(DOC_PATH),
            _relative(LEDGER_PATH),
            _relative(README_PATH),
        ],
        "findings": [finding.__dict__ for finding in findings],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])
        for finding in findings:
            print(f"{finding.code}: {finding.path}: {finding.message}")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
