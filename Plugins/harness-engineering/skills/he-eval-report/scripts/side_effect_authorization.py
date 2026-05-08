"""Side-effect authorization checks for HE eval reports."""

from __future__ import annotations

from report_fields import (
    YES_NO_VALUES,
    field_value,
    is_blankish,
    section_body,
    section_present,
    validate_required_fields,
)


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


def has_external_influence(value: str | None):
    if is_blankish(value):
        return False
    return value.lower() not in {"none", "n/a", "na", "no"}


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


def validate_side_effect_decision_consistency(body: str, errors: list[str]):
    decision = field_value(body, "Validator Decision:")
    blocks_completion = field_value(body, "Blocks Completion:")
    protected_action = field_value(body, "Protected Action:")
    user_evidence = field_value(body, "User Authorization Evidence:")
    external_influence = field_value(body, "External Party Influence:")
    add_missing_user_evidence_error(protected_action, decision, user_evidence, errors)
    add_external_influence_error(external_influence, decision, errors)
    add_not_run_error(decision, blocks_completion, errors)


def add_missing_user_evidence_error(
    protected_action: str | None,
    decision: str | None,
    user_evidence: str | None,
    errors: list[str],
):
    if is_blankish(protected_action):
        return
    if not decision or decision.lower() != "approved":
        return
    if not is_blankish(user_evidence):
        return
    errors.append(
        "side-effect authorization cannot approve a protected action without user authorization evidence"
    )


def add_external_influence_error(external_influence: str | None, decision: str | None, errors: list[str]):
    if not decision or decision.lower() != "approved":
        return
    if not has_external_influence(external_influence):
        return
    errors.append("side-effect authorization cannot approve when external party influence is present")


def add_not_run_error(decision: str | None, blocks_completion: str | None, errors: list[str]):
    if not decision or decision.lower() != "not-run":
        return
    if blocks_completion and blocks_completion.lower() == "yes":
        return
    errors.append("side-effect authorization not-run validator decisions must block completion")
