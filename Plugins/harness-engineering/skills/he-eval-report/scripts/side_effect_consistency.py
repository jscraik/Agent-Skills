"""Consistency checks for side-effect authorization decisions."""

from __future__ import annotations

from report_fields import field_value, is_blankish


def validate_side_effect_decision_consistency(body: str, errors: list[str]):
    decision = field_value(body, "Validator Decision:")
    blocks = field_value(body, "Blocks Completion:")
    action = field_value(body, "Protected Action:")
    user_evidence = field_value(body, "User Authorization Evidence:")
    influence = field_value(body, "External Party Influence:")
    if action and decision and decision.lower() == "approved" and is_blankish(user_evidence):
        errors.append(
            "side-effect authorization cannot approve a protected action without user authorization evidence"
        )
    if decision and decision.lower() == "approved" and has_external_influence(influence):
        errors.append("side-effect authorization cannot approve when external party influence is present")
    if decision and decision.lower() == "not-run" and (not blocks or blocks.lower() != "yes"):
        errors.append("side-effect authorization not-run validator decisions must block completion")


def has_external_influence(value: str | None):
    if is_blankish(value):
        return False
    return value.lower() not in {"none", "n/a", "na", "no"}
