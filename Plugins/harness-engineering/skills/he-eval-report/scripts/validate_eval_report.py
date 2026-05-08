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
    "Agentic Eval Validity",
    "Side-Effect Authorization",
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

AGENTIC_EVAL_FIELDS = [
    "Evaluated Capability / Task:",
    "Task Validity:",
    "Outcome Validity:",
    "Trajectory / Transcript Evidence:",
    "Grader Coverage:",
    "Trial Policy:",
    "Pass@k / Pass^k Reporting:",
    "Authorization Validator:",
    "Saturation / Maintenance Signal:",
    "Blocks Completion:",
    "Required Action:",
]

SIDE_EFFECT_AUTHORIZATION_FIELDS = [
    "Protected Action:",
    "User Authorization Evidence:",
    "Agent Justification:",
    "External Party Influence:",
    "Validator Decision:",
    "Validator Confidence:",
    "Suggested Next Step:",
    "Blocks Completion:",
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
YES_NO_VALUES = {"yes", "no"}
VALIDATOR_DECISIONS = {"approved", "blocked", "exempt", "not-run"}
VALIDATOR_CONFIDENCE_VALUES = {"high", "medium", "low", "not-run"}
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


def section_body(text: str, section: str) -> str:
    pattern = rf"(?ms)^#{{1,3}}\s+{re.escape(section)}\s*$\n(?P<body>.*?)(?=^#{{1,3}}\s+|\Z)"
    match = re.search(pattern, text)
    return match.group("body") if match else ""


def field_value(text: str, field: str) -> str | None:
    match = re.search(rf"(?mi)^{re.escape(field)}\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else None


def is_blankish(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().lower() in {"", "n/a", "na", "none", "unknown", "tbd", "todo"}


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


def validate_agentic_eval_validity(
    text: str, errors: list[str], *, enforce_values: bool
) -> None:
    if not section_present(text, "Agentic Eval Validity"):
        return
    body = section_body(text, "Agentic Eval Validity")
    validate_required_fields(
        body,
        AGENTIC_EVAL_FIELDS,
        errors,
        "agentic eval validity",
        enforce_values=enforce_values,
        optional_blank_fields={"Required Action:"},
    )
    blocks_completion = field_value(body, "Blocks Completion:")
    if enforce_values and blocks_completion and blocks_completion.lower() not in YES_NO_VALUES:
        errors.append("agentic eval validity Blocks Completion must be yes or no")


def validate_side_effect_authorization(
    text: str, errors: list[str], *, enforce_values: bool
) -> None:
    if not section_present(text, "Side-Effect Authorization"):
        return
    body = section_body(text, "Side-Effect Authorization")
    validate_required_fields(
        body,
        SIDE_EFFECT_AUTHORIZATION_FIELDS,
        errors,
        "side-effect authorization",
        enforce_values=enforce_values,
        optional_blank_fields={"Suggested Next Step:"},
    )
    if not enforce_values:
        return
    validate_side_effect_enum_values(body, errors)
    validate_side_effect_decision_consistency(body, errors)


def validate_required_fields(
    body: str,
    fields: list[str],
    errors: list[str],
    label: str,
    *,
    enforce_values: bool,
    optional_blank_fields: set[str] | None = None,
) -> None:
    optional_blank_fields = optional_blank_fields or set()
    for field in fields:
        if field not in body:
            errors.append(f"{label} section is missing field: {field}")
            continue
        if (
            enforce_values
            and field not in optional_blank_fields
            and is_blankish(field_value(body, field))
        ):
            errors.append(f"{label} field is blank: {field}")


def validate_side_effect_enum_values(body: str, errors: list[str]) -> None:
    decision = field_value(body, "Validator Decision:")
    confidence = field_value(body, "Validator Confidence:")
    blocks_completion = field_value(body, "Blocks Completion:")
    if decision and decision.lower() not in VALIDATOR_DECISIONS:
        errors.append(
            "side-effect authorization Validator Decision must be approved, blocked, exempt, or not-run"
        )
    if confidence and confidence.lower() not in VALIDATOR_CONFIDENCE_VALUES:
        errors.append(
            "side-effect authorization Validator Confidence must be high, medium, low, or not-run"
        )
    if blocks_completion and blocks_completion.lower() not in YES_NO_VALUES:
        errors.append("side-effect authorization Blocks Completion must be yes or no")


def validate_side_effect_decision_consistency(body: str, errors: list[str]) -> None:
    decision = field_value(body, "Validator Decision:")
    blocks_completion = field_value(body, "Blocks Completion:")
    protected_action = field_value(body, "Protected Action:")
    user_evidence = field_value(body, "User Authorization Evidence:")
    external_influence = field_value(body, "External Party Influence:")
    if (
        not is_blankish(protected_action)
        and decision
        and decision.lower() == "approved"
        and is_blankish(user_evidence)
    ):
        errors.append(
            "side-effect authorization cannot approve a protected action without user authorization evidence"
        )
    if (
        external_influence
        and external_influence.lower() not in {"none", "n/a", "na", "no"}
        and decision
        and decision.lower() == "approved"
    ):
        errors.append(
            "side-effect authorization cannot approve when external party influence is present"
        )
    if (
        decision
        and decision.lower() == "not-run"
        and (not blocks_completion or blocks_completion.lower() != "yes")
    ):
        errors.append(
            "side-effect authorization not-run validator decisions must block completion"
        )


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
