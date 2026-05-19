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
    """
    Produce the path string relative to the repository root when the given path is inside it.
    
    Parameters:
        path (Path): The filesystem path to convert.
    
    Returns:
        str: The path as a string relative to `ROOT` if `path` is inside `ROOT`, otherwise the original path as a string.
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _read(path: Path) -> str:
    """
    Read and return the text contents of the given file path using UTF-8 encoding.
    
    Returns:
        The file contents as a string.
    """
    return path.read_text(encoding="utf-8")


def _table_rows(markdown: str) -> tuple[list[str], list[list[str]]]:
    """
    Extracts the header and data rows from the first Markdown-style table found in the input text.
    
    Parameters:
        markdown (str): Text that may contain one or more Markdown tables.
    
    Returns:
        tuple[list[str], list[list[str]]]: 
            `headers`: list of header column names (trimmed of surrounding whitespace and outer pipes).
            `rows`: list of data rows; each row is a list of trimmed cell strings. Returns ([], []) if no complete Markdown table (header and divider) is found.
    """
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
    """
    Validate the steering feedback documentation, ledger, and agent docs index under the given repository root.
    
    Performs these checks:
    - Ensures the main steering feedback doc exists and contains required phrases.
    - Ensures the steering uptake ledger exists, has the expected table headers, at least one row, correct column counts, non-empty required fields, valid `Status` values, and that rows marked `validated` include validator evidence.
    - Ensures the agent docs index README exists and references the steering feedback doc.
    
    Parameters:
        root (Path): Repository root used to resolve the expected documentation paths.
    
    Returns:
        list[Finding]: A list of findings describing missing files or content issues; empty if all checks pass.
    """
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
    """
    Run the steering uptake validator and print its results to stdout.
    
    Parses optional CLI arguments (currently `--json`) from `argv` if provided; otherwise uses system arguments. Executes `validate()` and emits a payload describing the checked files and any findings. When `--json` is set, prints the full payload as pretty JSON; otherwise prints a one-line status ("pass" or "fail") followed by one line per finding in the format "<code>: <path>: <message>".
    
    Parameters:
        argv (Iterable[str] | None): Optional list of command-line arguments to parse. If `None`, the process's command-line arguments are used.
    
    Returns:
        int: Exit code — `0` when no findings were produced, `1` when one or more findings exist.
    """
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
