"""Side-effect authorization checks for HE eval reports."""

from __future__ import annotations

from report_fields import YES_NO_VALUES, field_value, section_body, section_present, validate_required_fields
from side_effect_consistency import validate_side_effect_decision_consistency


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

VALIDATOR_DECISIONS = {"approved", "blocked", "exempt", "not-run"}
VALIDATOR_CONFIDENCE_VALUES = {"high", "medium", "low", "not-run"}


def validate_side_effect_authorization(text: str, errors: list[str], *, enforce_values: bool):
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
