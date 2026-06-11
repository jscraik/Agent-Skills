#!/usr/bin/env python3
"""Validate Harness Engineering eval report structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from agentic_validity import validate_agentic_eval_validity
from report_fields import ReportDocument
from report_recommendation import find_recommendation, validate_consistency, validate_recommendation
from report_sections import (
    validate_drift_classifications,
    validate_gate_matrix,
    validate_linear_fields,
    validate_sections,
)
from side_effect_authorization import validate_side_effect_authorization


NOT_RUN_PASS_WARNING = (
    "report contains both not-run evidence and pass statuses; verify gates are not overstated"
)
TEMPLATE_PLACEHOLDER_RE = re.compile(r"\[[A-Z_ -]*REQUIRED[^\]]*\]|<(?:canonical-slug|Title Matching First H1|one substantive paragraph|accept \| challenge \| rework \| none|repo-relative plan or PR artifact|issue key when tracked|milestone when tracked)[^>]*>")


def validate_unresolved_placeholders(text: str, errors: list[str]) -> None:
    """
    Detects unresolved template placeholders in the report text and records an error if any are found.
    
    Parameters:
        text (str): Full markdown content of the report to scan.
        errors (list[str]): Mutable list that will receive the error message "report contains unresolved required template placeholder" if a placeholder is detected.
    """
    if TEMPLATE_PLACEHOLDER_RE.search(text):
        errors.append("report contains unresolved required template placeholder")


def validate_not_run_pass_consistency(document: ReportDocument, warnings: list[str]) -> None:
    """
    Warns when a "Side-Effect Authorization" declares "Validator Decision: not-run" but the report indicates a passing status or a completing recommendation.
    
    If the "Side-Effect Authorization" section is present and its "Validator Decision:" field equals "not-run" (case-insensitive), appends NOT_RUN_PASS_WARNING to `warnings` when either the report's "Status:" field equals "pass" (case-insensitive) or the recommendation is "Complete" or "Complete with follow-up".
    
    Parameters:
        document (ReportDocument): Parsed report document providing section and field lookup helpers.
        warnings (list[str]): Mutable list of warning messages to which the function may append.
    """
    if not document.section_present("Side-Effect Authorization"):
        return
    decision = document.field_value("Validator Decision:", section="Side-Effect Authorization")
    if not decision or decision.strip().lower() != "not-run":
        return

    status = document.field_value("Status:")
    recommendation = find_recommendation(document)
    status_pass = bool(status and status.strip().lower() == "pass")
    recommendation_complete = recommendation in {"Complete", "Complete with follow-up"}
    if status_pass or recommendation_complete:
        warnings.append(NOT_RUN_PASS_WARNING)


def validate(path: Path):
    """
    Validate an eval report Markdown file at the given filesystem path and collect validation issues.
    
    Performs a series of structural and content checks on the report (sections, fields, gate matrix, drift classifications, recommendation, consistency, side-effect authorization, and — unless the file is the template named "eval-report-template.md" — unresolved template placeholders and not-run/pass consistency). Returns any errors (fatal validation failures) and warnings (non-fatal issues) discovered.
    
    Parameters:
        path (Path): Filesystem path to the eval report Markdown file to validate.
    
    Returns:
        tuple[list[str], list[str]]: A pair (errors, warnings). `errors` is a list of validation error messages; `warnings` is a list of non-fatal warning messages.
    """
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
    document = ReportDocument.parse(text)
    validate_sections(document, errors)
    validate_linear_fields(document, errors)
    validate_gate_matrix(document, errors, warnings)
    validate_agentic_eval_validity(document, errors, enforce_values=enforce_values)
    validate_side_effect_authorization(document, errors, enforce_values=enforce_values)
    validate_drift_classifications(document, errors, enforce_values=enforce_values)
    validate_recommendation(document, errors)
    validate_consistency(document, path, warnings)
    if enforce_values:
        validate_unresolved_placeholders(text, errors)
        validate_not_run_pass_consistency(document, warnings)

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
