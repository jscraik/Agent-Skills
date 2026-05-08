#!/usr/bin/env python3
"""Validate Harness Engineering eval report structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Executive Eval Summary",
    "Evaluated Slice",
    "Linear Definition of Done Status",
    "Linear Backlink Map",
    "Source Artifact Trace",
    "Functional Validation Results",
    "Eval Gate Matrix",
    "Drift Validation",
    "Architecture Integrity Check",
    "Routing Determinism Check",
    "Context Load Check",
    "Agent-Native Check",
    "Governance Simplicity Check",
    "Moat Protection Check",
    "Proof Artifacts",
    "Failures / Regressions",
    "Linear Completion Recommendation",
    "Follow-Up Work",
    "Core / ADR Update Recommendation",
    "Evidence & Traceability Matrix",
]

LINEAR_FIELDS = [
    "Linear Project:",
    "Linear Milestone:",
    "Linear Parent Issue:",
    "Linear Sub-Issues:",
    "Linear Status Recommendation:",
    "Proof Artifact Links:",
]

GATE_FIELDS = [
    "Gate:",
    "Expected:",
    "Actual:",
    "Status:",
    "Evidence:",
    "Confidence:",
    "Blocks Closure:",
    "Required Action:",
]

DRIFT_AREAS = [
    "Architecture Drift:",
    "Routing Drift:",
    "Context Drift:",
    "Governance Drift:",
    "Agent-Native Drift:",
    "Moat Drift:",
]

DRIFT_VALUES = {"Improved", "Neutral", "Regressed", "Unknown"}
RECOMMENDATIONS = {
    "Complete",
    "Complete with follow-up",
    "Blocked",
    "Needs rework",
    "Unsafe to close",
}


def section_present(text: str, section: str) -> bool:
    pattern = rf"(?m)^#{{1,3}}\s+{re.escape(section)}\s*$"
    return re.search(pattern, text) is not None


def find_recommendation(text: str) -> str | None:
    match = re.search(r"(?mi)^Classification:\s*(.+?)\s*$", text)
    if not match:
        match = re.search(r"(?mi)^Linear Completion Recommendation:\s*(.+?)\s*$", text)
    if not match:
        return None
    value = match.group(1).strip()
    for recommendation in RECOMMENDATIONS:
        if value == recommendation or value.startswith(f"{recommendation} "):
            return recommendation
    return value


def validate_sections(text: str, errors: list[str]) -> None:
    for section in REQUIRED_SECTIONS:
        if not section_present(text, section):
            errors.append(f"missing required section: {section}")


def validate_linear_fields(text: str, errors: list[str]) -> None:
    for field in LINEAR_FIELDS:
        if field not in text:
            errors.append(f"missing Linear backlink field: {field}")


def validate_gate_matrix(text: str, errors: list[str], warnings: list[str]) -> None:
    if "Gate:" not in text:
        warnings.append("no Gate: entries found in eval gate matrix")
        return
    for field in GATE_FIELDS:
        if field not in text:
            errors.append(f"gate matrix is missing field: {field}")


def validate_drift_classifications(text: str, errors: list[str]) -> None:
    for area in DRIFT_AREAS:
        match = re.search(rf"(?mi)^{re.escape(area)}\s*([A-Za-z -]+)", text)
        if not match:
            errors.append(f"missing drift classification: {area}")
            continue
        value = match.group(1).strip()
        if value not in DRIFT_VALUES:
            errors.append(f"invalid drift classification for {area} {value!r}")


def validate_recommendation(text: str, errors: list[str]) -> None:
    recommendation = find_recommendation(text)
    if recommendation is None:
        errors.append("missing Linear completion recommendation classification")
    elif recommendation not in RECOMMENDATIONS:
        errors.append(f"invalid Linear completion recommendation: {recommendation!r}")


def validate_consistency(text: str, path: Path, warnings: list[str]) -> None:
    has_not_run = re.search(r"(?i)\bnot[- ]run\b", text)
    has_pass_status = re.search(r"(?mi)^Status:\s*pass\s*$", text)
    if has_not_run and has_pass_status:
        warnings.append("report contains both not-run evidence and pass statuses; verify gates are not overstated")
    if ".harness/evals/" not in str(path):
        warnings.append("report path is outside .harness/evals/")


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"report does not exist: {path}"], warnings
    if path.is_dir():
        return [f"report path is a directory: {path}"], warnings

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return ["report is empty"], warnings

    validate_sections(text, errors)
    validate_linear_fields(text, errors)
    validate_gate_matrix(text, errors, warnings)
    validate_drift_classifications(text, errors)
    validate_recommendation(text, errors)
    validate_consistency(text, path, warnings)

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Harness Engineering eval report.")
    parser.add_argument("report", type=Path, help="Path to the eval report markdown file.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    errors, warnings = validate(args.report)
    result = {
        "schema_version": 1,
        "report": str(args.report),
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in errors:
            print(f"error: {error}")
        for warning in warnings:
            print(f"warning: {warning}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
