#!/usr/bin/env python3
"""Advisory checker for HE PR safety trace and Codex provenance fields."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PUBLIC_TRACE_TRIGGER_RE = re.compile(
    r"\b(harness engineering trace|pr safety trace|he[ _-]trace[ _-]id|he_trace_id|hetrace_|"
    r"provenance source|provenance status|redaction status|codex_provenance)\b",
    re.IGNORECASE,
)
RAW_SENSITIVE_RE = re.compile(
    r"(/Users/[^\s)]+/(?:\.codex|\.agents)[^\s)]*|"
    r"/(?:home|tmp|var|private|opt|srv|mnt|Volumes)/[^\s)]*(?:\.codex|\.agents|"
    r"codex|session|transcript|rollout|otel|trace)[^\s)]*|"
    r"rollout-[^\s)]*\.jsonl|"
    r"(?:transcript_path|rollout_path|evidence_location|validation_evidence_location)"
    r"\s*[:=]\s*(?:/|[A-Za-z]:\\|\\\\)|"
    r"\b(?:thread_id|turn_id|codex_session_id|session_tree_id|otel_trace_id|"
    r"trace_id)\s*[:=]\s*"
    r"(?!hash:|not_available|raw_local|hash_only)[A-Za-z0-9_.:-]+)",
    re.IGNORECASE,
)

ABSOLUTE_LOCAL_FIELD_RE = re.compile(
    r"(?mi)(?:^|[{,])\s*[\"'`]?(collector_output|sensitive_output|source_file|transcript_path|"
    r"rollout_path|evidence_location|validation_evidence_location|rollout_trace_bundle)"
    r"[\"'`]?\s*[:=]\s*[\"'`]?(?:/|[A-Za-z]:\\|\\\\)"
)

PUBLIC_HASH_ROW_RE = re.compile(
    r"(?mi)^\|\s*(codex\s+session(?:\s+id)?|codex\s+thread(?:\s+id)?|"
    r"codex\s+turns?(?:\s+ids?)?|otel\s+trace(?:\s+id)?)\s*\|\s*([^|]+?)\s*\|"
)

SENSITIVE_ID_FIELD_RE = re.compile(
    r"(?mi)(?:^|[{,])\s*[\"'`]?(thread_id|turn_id|codex_session_id|session_tree_id|"
    r"otel_trace_id|trace_id)[\"'`]?\s*[:=]\s*[\"'`]?([^\"'`\s,)]+)"
)

JSON_CODEX_BLOCK_RE = re.compile(
    r"(?ms)\"codex_provenance\"\s*:\s*\{(?P<body>[^{}]*)\}"
)

REQUIRED_PUBLIC_TERMS = (
    ("he trace id", re.compile(r"\bhe[ _-]trace[ _-]id\b|\bhetrace_", re.IGNORECASE)),
    ("provenance source", re.compile(r"\bprovenance[ _-]source\b", re.IGNORECASE)),
    ("provenance status", re.compile(r"\bprovenance[ _-]status\b", re.IGNORECASE)),
    ("redaction status", re.compile(r"\bredaction[ _-]status\b", re.IGNORECASE)),
)
REQUIRED_PUBLIC_FIELD_LABELS = tuple(label for label, _pattern in REQUIRED_PUBLIC_TERMS)

REQUIRED_CODEX_FIELDS = (
    "status",
    "source",
    "redaction_status",
    "proves",
    "does_not_prove",
)

CODEX_BLOCK_RE = re.compile(
    r"(?ms)^(?P<indent>[ \t]*)codex_provenance:\s*$"
    r"(?P<body>(?:\n(?P=indent)[ \t]+.*|\n[ \t]*$)*)"
)


def _line_for(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _codex_blocks(text: str) -> list[tuple[int, str]]:
    return [(_line_for(text, match.start()), match.group("body")) for match in CODEX_BLOCK_RE.finditer(text)]


def _normalize_table_cell(value: str) -> str:
    normalized = value.strip().strip("`").lower()
    normalized = re.sub(r"[_-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _markdown_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_markdown_table_separator(line: str) -> bool:
    cells = _markdown_table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _public_hash_value_is_safe(value: str) -> bool:
    normalized = value.strip().strip("\"'`").lower()
    if normalized in {"not_available", "not applicable", "not_applicable", "none", "0 hashed turn ids"}:
        return True
    if re.fullmatch(r"\d+\s+hashed\s+turn\s+ids?", normalized):
        return True
    if re.fullmatch(r"hash:[a-z0-9][a-z0-9_.:-]{5,}", normalized):
        return True
    if re.fullmatch(r"(?:hash:[a-z0-9][a-z0-9_.:-]{5,})(?:\s*,\s*hash:[a-z0-9][a-z0-9_.:-]{5,})*", normalized):
        return True
    return False


def _sensitive_id_value_is_safe(value: str) -> bool:
    normalized = value.strip().strip("\"'`").lower()
    return (
        re.fullmatch(r"hash:[a-z0-9][a-z0-9_.:-]{5,}", normalized) is not None
        or normalized in {"not_available", "not_applicable", "raw_local", "hash_only"}
    )


def validate_text(path: Path, text: str) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    seen_findings: set[tuple[str, int, str]] = set()

    def add_finding(severity: str, message: str, line: int) -> None:
        key = (severity, line, message)
        if key in seen_findings:
            return
        seen_findings.add(key)
        findings.append({"severity": severity, "message": message, "line": line})

    triggered = bool(PUBLIC_TRACE_TRIGGER_RE.search(text))
    if triggered:
        for label, pattern in REQUIRED_PUBLIC_TERMS:
            if not pattern.search(text):
                add_finding(
                    "fail",
                    f"provenance-related artifact missing public trace term: {label}",
                    1,
                )

    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        if index + 1 >= len(lines) or not _is_markdown_table_separator(lines[index + 1]):
            continue

        headers = _markdown_table_cells(line)
        normalized_headers = [_normalize_table_cell(header) for header in headers]
        if not headers or "field" not in normalized_headers:
            continue

        field_index = normalized_headers.index("field")
        row_labels: set[str] = set()
        has_public_trace_signal = False
        cursor = index + 2
        while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
            if _is_markdown_table_separator(lines[cursor]):
                cursor += 1
                continue

            cells = _markdown_table_cells(lines[cursor])
            if len(cells) != len(headers):
                add_finding(
                    "fail",
                    (
                        "malformed markdown table row in public trace table: "
                        f"expected {len(headers)} cells, found {len(cells)}"
                    ),
                    cursor + 1,
                )
                row_text = lines[cursor].lower()
                if PUBLIC_TRACE_TRIGGER_RE.search(row_text):
                    has_public_trace_signal = True
                cursor += 1
                continue

            label = _normalize_table_cell(cells[field_index])
            row_labels.add(label)
            if label in REQUIRED_PUBLIC_FIELD_LABELS or PUBLIC_TRACE_TRIGGER_RE.search(lines[cursor]):
                has_public_trace_signal = True
            cursor += 1

        if has_public_trace_signal:
            for label in REQUIRED_PUBLIC_FIELD_LABELS:
                if label not in row_labels:
                    add_finding("fail", f"public trace table missing field: {label}", index + 1)

    if re.search(r"(?m)^\s*codex_provenance:\s*$", text):
        blocks = _codex_blocks(text)
        if not blocks:
            add_finding("fail", "codex_provenance token present but no block was found", 1)
        for line, block in blocks:
            for field in REQUIRED_CODEX_FIELDS:
                if not re.search(rf"(?m)^\s*{re.escape(field)}\s*:", block):
                    add_finding("fail", f"codex_provenance block missing field: {field}", line)

    for match in JSON_CODEX_BLOCK_RE.finditer(text):
        line = _line_for(text, match.start())
        block = match.group("body")
        for field in REQUIRED_CODEX_FIELDS:
            if not re.search(rf"(?m)[\"']?{re.escape(field)}[\"']?\s*:", block):
                add_finding("fail", f"codex_provenance block missing field: {field}", line)

    for match in RAW_SENSITIVE_RE.finditer(text):
        add_finding(
            "fail",
            "raw local Codex/session provenance appears in public trace text",
            _line_for(text, match.start()),
        )

    for match in ABSOLUTE_LOCAL_FIELD_RE.finditer(text):
        add_finding(
            "fail",
            "absolute local path appears in public provenance field",
            _line_for(text, match.start()),
        )

    for match in SENSITIVE_ID_FIELD_RE.finditer(text):
        value = match.group(2)
        if not _sensitive_id_value_is_safe(value):
            add_finding(
                "fail",
                "raw local Codex/session provenance appears in public trace text",
                _line_for(text, match.start()),
            )

    for match in PUBLIC_HASH_ROW_RE.finditer(text):
        label = match.group(1)
        value = match.group(2)
        if not _public_hash_value_is_safe(value):
            add_finding(
                "fail",
                f"public {label} row must use hash-only, count-only, or not_available value",
                _line_for(text, match.start()),
            )

    status = "fail" if any(f["severity"] == "fail" for f in findings) else "pass"
    if findings and status == "pass":
        status = "warn"
    return {
        "path": str(path),
        "triggered": triggered,
        "status": status,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = [validate_text(path, path.read_text(encoding="utf-8")) for path in args.paths]
    failed = any(result["status"] == "fail" for result in results)
    warned = any(result["status"] == "warn" for result in results)
    payload = {
        "schema_version": 1,
        "status": "fail" if failed else "warn" if warned else "pass",
        "results": results,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        for result in results:
            for finding in result["findings"]:
                print(
                    f"{result['path']}:{finding['line']}: "
                    f"{finding['severity']}: {finding['message']}"
                )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
