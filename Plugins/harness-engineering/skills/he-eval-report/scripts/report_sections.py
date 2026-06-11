"""Required section, gate, and drift checks for HE eval reports."""

from __future__ import annotations

from report_fields import ReportDocument
from report_contract import DRIFT_AREAS, DRIFT_VALUES, GATE_FIELDS, LINEAR_FIELDS, REQUIRED_SECTIONS


def validate_sections(document: ReportDocument, errors: list[str]):
    for section in REQUIRED_SECTIONS:
        if not document.section_present(section):
            errors.append(f"missing required section: {section}")


def validate_linear_fields(document: ReportDocument, errors: list[str]):
    body = document.section_body("Linear Backlink Map") or document.text
    for field in LINEAR_FIELDS:
        if document.field_value(field, section="Linear Backlink Map") is None and field not in body:
            errors.append(f"missing Linear backlink field: {field}")


def validate_gate_matrix(document: ReportDocument, errors: list[str], warnings: list[str]):
    """
    Validate gate matrix entries in the report and record any missing required fields.
    
    If no gate entries are present, a warning is appended to `warnings`. Otherwise each gate entry is checked for the presence of every field listed in `GATE_FIELDS`; for any missing field an error message is appended to `errors` naming the gate and the missing field.
    
    Parameters:
        document (ReportDocument): Source report object providing `gate_entries()` to enumerate gate matrix rows.
        errors (list[str]): Mutable list to which error messages for missing fields will be appended.
        warnings (list[str]): Mutable list to which a warning is appended if no gate entries are found.
    """
    entries = document.gate_entries()
    if not entries:
        warnings.append("no Gate: entries found in eval gate matrix")
        return
    for index, entry in enumerate(entries, start=1):
        gate_name = entry.get("Gate:", f"#{index}")
        for field in GATE_FIELDS:
            if field not in entry:
                errors.append(f"gate matrix entry {gate_name!r} is missing field: {field}")


def validate_drift_classifications(
    document: ReportDocument, errors: list[str], *, enforce_values: bool = True
):
    """
    Validate drift area classifications in the report and append problem messages to `errors`.
    
    Checks each area in DRIFT_AREAS for a classification value (first in the "Drift Validation" section, then anywhere else). For each area:
    - If no value is found, appends "missing drift classification: {area}" to `errors`.
    - If a value is present and not accepted, appends "invalid drift classification for {area} {value!r}" to `errors`.
    
    Parameters:
        document (ReportDocument): The parsed report document to inspect.
        errors (list[str]): Mutable list that will be extended with error messages.
        enforce_values (bool, keyword-only): If True (default), the value must be one of DRIFT_VALUES. If False, values starting with "[REQUIRED:" are treated as acceptable and skipped from validation.
    """
    for area in DRIFT_AREAS:
        value = document.field_value(area, section="Drift Validation")
        if value is None:
            value = document.field_value(area)
        if value is None:
            errors.append(f"missing drift classification: {area}")
            continue
        value = value.strip()
        if not enforce_values and value.startswith("[REQUIRED:"):
            continue
        if value not in DRIFT_VALUES:
            errors.append(f"invalid drift classification for {area} {value!r}")
