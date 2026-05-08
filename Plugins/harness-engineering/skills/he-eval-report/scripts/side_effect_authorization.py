"""Side-effect authorization checks for HE eval reports."""

from __future__ import annotations

from report_contract import (
    SIDE_EFFECT_AUTHORIZATION_FIELDS,
    VALIDATOR_CONFIDENCE_VALUES,
    VALIDATOR_DECISIONS,
    YES_NO_VALUES,
)
from report_fields import ReportDocument, field_value, validate_required_fields
from side_effect_consistency import validate_side_effect_decision_consistency


def validate_side_effect_authorization(document: ReportDocument, errors: list[str], *, enforce_values: bool):
    if not document.section_present("Side-Effect Authorization"):
        return
    body = document.section_body("Side-Effect Authorization")
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


def validate_side_effect_enum_values(body: str, errors: list[str]):
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
