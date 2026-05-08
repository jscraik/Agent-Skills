"""Agentic-eval validity checks for HE eval reports."""

from __future__ import annotations

from report_contract import AGENTIC_EVAL_FIELDS, YES_NO_VALUES
from report_fields import field_value, section_body, section_present, validate_required_fields


def validate_agentic_eval_validity(text: str, errors: list[str], *, enforce_values: bool):
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
