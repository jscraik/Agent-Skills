#!/usr/bin/env python3
"""Validate Harness Engineering eval report structure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_validity import validate_agentic_eval_validity
from report_recommendation import validate_consistency, validate_recommendation
from report_sections import (
    validate_drift_classifications,
    validate_gate_matrix,
    validate_linear_fields,
    validate_sections,
)
from side_effect_authorization import validate_side_effect_authorization


def validate(path: Path):
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"report does not exist: {path}"], warnings
    if path.is_dir():
        return [f"report path is a directory: {path}"], warnings

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return ["report is empty"], warnings

    enforce_values = path.name != "eval-report-template.md"
    validate_sections(text, errors)
    validate_linear_fields(text, errors)
    validate_gate_matrix(text, errors, warnings)
    validate_agentic_eval_validity(text, errors, enforce_values=enforce_values)
    validate_side_effect_authorization(text, errors, enforce_values=enforce_values)
    validate_drift_classifications(text, errors)
    validate_recommendation(text, errors)
    validate_consistency(text, path, warnings)

    return errors, warnings


def main():
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
