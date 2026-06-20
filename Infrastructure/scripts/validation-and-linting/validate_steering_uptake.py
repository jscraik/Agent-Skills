#!/usr/bin/env python3
"""Validate high-signal steering uptake surfaces."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
DOC_REL_PATH = Path("Docs/agents/19-high-signal-steering-feedback.md")
LEDGER_REL_PATH = Path(".harness/quality/steering-uptake.md")
README_REL_PATH = Path("Docs/agents/README.md")
AGENTS_REL_PATH = Path("AGENTS.md")
DOC_PATH = ROOT / DOC_REL_PATH
LEDGER_PATH = ROOT / LEDGER_REL_PATH
README_PATH = ROOT / README_REL_PATH
AGENTS_PATH = ROOT / AGENTS_REL_PATH
VALID_STATUSES = {"open", "validated", "blocked"}
VALID_FAILURE_CATEGORIES = {
    "missing context",
    "stale state",
    "weak validation",
    "hidden assumptions",
    "retrieval failure",
    "poor workflow design",
    "runtime ambiguity",
    "architecture drift",
    "lack of verification",
    "weak observability",
    "missing guardrails",
    "missing decomposition",
    "unclear authority boundaries",
    "excessive context noise",
    "poor task routing",
    "insufficient deterministic enforcement",
}
VALID_IMPROVEMENT_TYPES = {
    "validator",
    "schema",
    "schema contract",
    "schema constraint",
    "trace event",
    "runtime check",
    "workflow rule",
    "recovery handler",
    "CI gate",
    "repo artifact",
    "skill improvement",
    "context-routing improvement",
    "governance rule",
    "reusable primitive",
    "implementation note",
    "retrieval improvement",
    "stale-state prevention",
    "claim-vs-evidence verification",
    "generated runtime guardrail",
    "runtime projection guardrail",
    "runtime persistence guardrail",
    "doctor blocker",
    "selection policy",
    "eval contract",
}
OPEN_VALIDATION_MARKERS = {
    "pending",
    "blocked",
    "in progress",
    "in-progress",
    "after push",
    "after-push",
    "next proof",
    "next-proof",
    "not claimed",
    "not-claimed",
}
REQUIRED_HEADERS = [
    "Date",
    "Trigger",
    "Failure pattern",
    "Mechanism",
    "Durable guardrail",
    "Validation",
    "Status",
]
REQUIRED_DOC_PHRASES = (
    "Stop Rule",
    "Proof Before Proceeding",
    "Scope Closure Authority",
    "full implementation",
    "explicitly approves that scope change",
    "claim-vs-evidence closeout check",
    "closeout caveat",
    "changes future behavior",
    "Uptake Loop",
    "local or systemic",
    "sibling patterns",
    "API philosophy",
    "error-handling doctrine",
    "runtime safety assumption",
    "operational standard",
    "lint rule",
    "schema constraint",
    "style rule",
    "CI check",
    "shared utility",
    "reusable abstraction",
    "architectural policy",
    "not doing what Jamie wants",
    "feedback signal",
    "root operational failure",
    "durable system improvement",
    "explicit remaining proof",
    "known taxonomy values",
    "Required Evidence",
    "validate_steering_uptake.py",
    "After any fabricated runtime handle is attempted",
    "immediately preceding tool result",
)
STEERING_DOC_LINK_RE = re.compile(
    r"\[[^\]]+\]\((?:/)?Docs/agents/19-high-signal-steering-feedback\.md\)"
)
REQUIRED_AGENTS_STEERING_PHRASES = (
    "High-Signal Steering Feedback",
    "opening and reading it in the current turn",
    ".harness/quality/steering-uptake.md",
    "validate_steering_uptake.py --json",
)


@dataclass
class Finding:
    code: str
    message: str
    path: str


def _relative(path: Path, root: Path = ROOT) -> str:
    """
    Produce the path string relative to the repository root when the given path is inside it.

    Parameters:
        path (Path): The filesystem path to convert.

    Returns:
        str: The path as a string relative to `root` if `path` is inside `root`, otherwise the original path as a string.
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _read(path: Path) -> str:
    """
    Read text from the given file path using UTF-8 encoding.

    Returns:
        The file contents as a string.
    """
    return path.read_text(encoding="utf-8")


def _is_table_row(line: str) -> bool:
    return "|" in line.strip()


def _collect_table_lines(lines: list[str], start_index: int) -> list[str]:
    table_lines: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if not _is_table_row(stripped):
            break
        table_lines.append(stripped)
    return table_lines


def _find_table_lines(markdown: str) -> list[str]:
    lines = markdown.splitlines()
    malformed_candidate: list[str] = []
    for index, line in enumerate(lines):
        if not _is_table_row(line):
            continue
        candidate = _collect_table_lines(lines, index)
        if len(candidate) < 2:
            continue
        if _is_table_separator(candidate[1]):
            return candidate
        if not malformed_candidate:
            malformed_candidate = candidate
    return malformed_candidate


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
    table_lines = _find_table_lines(markdown)

    if len(table_lines) < 3:
        if len(table_lines) >= 2:
            return _table_cells(table_lines[0]), []
        return [], []

    if not _is_table_separator(table_lines[1]):
        return _table_cells(table_lines[0]), []

    headers = _table_cells(table_lines[0])
    rows: list[list[str]] = []
    for line in table_lines[2:]:
        cells = _table_cells(line)
        if any(cells):
            rows.append(cells)
    return headers, rows


def _table_cells(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in text:
        if escaped:
            if char == "|":
                current.append("|")
            else:
                current.extend(["\\", char])
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def _is_table_separator(line: str) -> bool:
    cells = _table_cells(line)
    if not cells:
        return False
    for cell in cells:
        stripped = cell.strip()
        if len(stripped) < 3:
            return False
        if not set(stripped) <= {"-", ":"}:
            return False
        if "-" not in stripped:
            return False
    return True


def _has_malformed_table_separator(markdown: str) -> bool:
    table_lines = _find_table_lines(markdown)
    return len(table_lines) >= 2 and not _is_table_separator(table_lines[1])


def _contains_steering_doc_link(text: str) -> bool:
    return bool(STEERING_DOC_LINK_RE.search(text))


def _tag_values(text: str, label: str) -> set[str]:
    marker = f"{label}:"
    if marker not in text:
        return set()
    value_text = text.split(marker, 1)[1].split(".", 1)[0]
    return {value.strip() for value in re.split(r";|,", value_text) if value.strip()}


def _validate_doc(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    doc_path = root / DOC_REL_PATH
    if not doc_path.exists():
        findings.append(Finding("STEERING_DOC_MISSING", "High-signal steering feedback doc is missing.", _relative(doc_path, root)))
        return findings

    doc = _read(doc_path)
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in doc:
            findings.append(Finding("STEERING_DOC_INCOMPLETE", f"Missing required phrase: {phrase}", _relative(doc_path, root)))
    return findings


def _validate_ledger_shape(headers: list[str], rows: list[list[str]], ledger: str, ledger_path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if headers != REQUIRED_HEADERS:
        findings.append(Finding("STEERING_LEDGER_HEADERS", f"Expected headers {REQUIRED_HEADERS}, got {headers}", _relative(ledger_path, root)))
    if headers and not rows and _has_malformed_table_separator(ledger):
        findings.append(Finding("STEERING_LEDGER_SEPARATOR", "Ledger table must include a Markdown separator row before data rows.", _relative(ledger_path, root)))
    if not rows:
        findings.append(Finding("STEERING_LEDGER_EMPTY", "Ledger must contain at least one steering uptake row.", _relative(ledger_path, root)))
    return findings


def _validate_tag_values(index: int, text: str, label: str, allowed: set[str], code_prefix: str, path: Path, root: Path) -> list[Finding]:
    if f"{label}:" not in text:
        return [Finding(f"{code_prefix}_MISSING", f"Row {index} is missing {label}.", _relative(path, root))]
    values = _tag_values(text, label)
    unknown = values - allowed
    if not values:
        return [Finding(f"{code_prefix}_MISSING", f"Row {index} has an empty {label} list.", _relative(path, root))]
    if unknown:
        return [Finding(f"{code_prefix}_UNKNOWN", f"Row {index} uses unknown {label} values: {sorted(unknown)}.", _relative(path, root))]
    return []


def _validate_ledger_row_status(index: int, record: dict[str, str], ledger_path: Path, root: Path) -> list[Finding]:
    validation_text = record["Validation"].lower()
    if record["Status"] == "open" and not any(marker in validation_text for marker in OPEN_VALIDATION_MARKERS):
        return [Finding("STEERING_LEDGER_OPEN_UNCLEAR", f"Row {index} is open but does not name the pending, blocked, in-progress, after-push, next-proof, or not-claimed condition.", _relative(ledger_path, root))]
    if record["Status"] == "validated" and "validate_steering_uptake.py" not in record["Validation"]:
        return [Finding("STEERING_LEDGER_VALIDATION_WEAK", f"Row {index} marked validated without steering validator evidence.", _relative(ledger_path, root))]
    return []


def _validate_ledger_taxonomy(index: int, record: dict[str, str], ledger_path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_validate_tag_values(index, record["Mechanism"], "Category", VALID_FAILURE_CATEGORIES, "STEERING_LEDGER_CATEGORY", ledger_path, root))
    findings.extend(_validate_tag_values(index, record["Durable guardrail"], "Improvement type", VALID_IMPROVEMENT_TYPES, "STEERING_LEDGER_IMPROVEMENT_TYPE", ledger_path, root))
    return findings


def _validate_ledger_row(index: int, row: list[str], ledger_path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if len(row) != len(REQUIRED_HEADERS):
        return [Finding("STEERING_LEDGER_ROW_WIDTH", f"Row {index} has {len(row)} cells, expected {len(REQUIRED_HEADERS)}.", _relative(ledger_path, root))]
    record = dict(zip(REQUIRED_HEADERS, row))
    for field in REQUIRED_HEADERS:
        if not record[field] or record[field].lower() in {"none", "n/a", "todo"}:
            findings.append(Finding("STEERING_LEDGER_FIELD_EMPTY", f"Row {index} has weak value for {field}.", _relative(ledger_path, root)))
    if record["Status"] not in VALID_STATUSES:
        findings.append(Finding("STEERING_LEDGER_STATUS", f"Row {index} has invalid status {record['Status']!r}.", _relative(ledger_path, root)))
    findings.extend(_validate_ledger_row_status(index, record, ledger_path, root))
    findings.extend(_validate_ledger_taxonomy(index, record, ledger_path, root))
    return findings


def _validate_ledger(root: Path) -> list[Finding]:
    ledger_path = root / LEDGER_REL_PATH
    if not ledger_path.exists():
        return [Finding("STEERING_LEDGER_MISSING", "Steering uptake ledger is missing.", _relative(ledger_path, root))]
    ledger = _read(ledger_path)
    headers, rows = _table_rows(ledger)
    findings = _validate_ledger_shape(headers, rows, ledger, ledger_path, root)
    for index, row in enumerate(rows, start=1):
        findings.extend(_validate_ledger_row(index, row, ledger_path, root))
    return findings


def _validate_readme(root: Path) -> list[Finding]:
    readme_path = root / README_REL_PATH
    if not readme_path.exists():
        return [Finding("AGENT_DOC_INDEX_MISSING", "Agent docs index is missing.", _relative(readme_path, root))]
    if not _contains_steering_doc_link(_read(readme_path)):
        return [Finding("STEERING_DOC_NOT_INDEXED", "Agent docs index must link the steering feedback doc.", _relative(readme_path, root))]
    return []


def _validate_agents(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents_path = root / AGENTS_REL_PATH
    if not agents_path.exists():
        return [Finding("AGENTS_STEERING_ROUTING_MISSING", "Root AGENTS.md is missing.", _relative(agents_path, root))]
    agents = _read(agents_path)
    for phrase in REQUIRED_AGENTS_STEERING_PHRASES:
        if phrase not in agents:
            findings.append(Finding("AGENTS_STEERING_ROUTING_WEAK", f"Root AGENTS.md must require steering uptake routing phrase: {phrase}", _relative(agents_path, root)))
    return findings


def validate(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_validate_doc(root))
    findings.extend(_validate_ledger(root))
    findings.extend(_validate_readme(root))
    findings.extend(_validate_agents(root))
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
            _relative(AGENTS_PATH),
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
