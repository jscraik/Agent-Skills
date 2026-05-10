"""Agentic-eval validity checks for HE eval reports."""

from __future__ import annotations

from report_contract import AGENTIC_EVAL_FIELDS, YES_NO_VALUES
from report_fields import ReportDocument, field_value, validate_required_fields


def validate_agentic_eval_validity(document: ReportDocument, errors: list[str], *, enforce_values: bool):
    if not document.section_present("Agentic Eval Validity"):
        return
    body = document.section_body("Agentic Eval Validity")
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
