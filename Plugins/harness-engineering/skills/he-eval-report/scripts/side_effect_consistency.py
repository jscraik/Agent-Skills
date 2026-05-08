"""Decision-consistency checks for side-effect authorization."""

from __future__ import annotations

from report_fields import field_value, is_blankish


def validate_side_effect_decision_consistency(body: str, errors: list[str]):
    decision = field_value(body, "Validator Decision:")
    blocks_completion = field_value(body, "Blocks Completion:")
    protected_action = field_value(body, "Protected Action:")
    user_evidence = field_value(body, "User Authorization Evidence:")
    external_influence = field_value(body, "External Party Influence:")
    add_missing_user_evidence_error(protected_action, decision, user_evidence, errors)
    add_external_influence_error(external_influence, decision, errors)
    add_not_run_error(decision, blocks_completion, errors)


def has_external_influence(value: str | None):
    if is_blankish(value):
        return False
    return value.lower() not in {"none", "n/a", "na", "no"}


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
