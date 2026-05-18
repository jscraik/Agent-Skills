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
    entries = document.gate_entries()
    if not entries:
        warnings.append("no Gate: entries found in eval gate matrix")
        return
    for index, entry in enumerate(entries, start=1):
        gate_name = entry.get("Gate:", f"#{index}")
        for field in GATE_FIELDS:
            if field not in entry:
                errors.append(f"gate matrix entry {gate_name!r} is missing field: {field}")


def validate_drift_classifications(document: ReportDocument, errors: list[str]):
    for area in DRIFT_AREAS:
        value = document.field_value(area, section="Drift Validation")
        if value is None:
            value = document.field_value(area)
        if value is None:
            errors.append(f"missing drift classification: {area}")
            continue
        value = value.strip()
        if value not in DRIFT_VALUES:
            errors.append(f"invalid drift classification for {area} {value!r}")
