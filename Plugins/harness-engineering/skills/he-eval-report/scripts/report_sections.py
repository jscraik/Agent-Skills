"""Required section, gate, and drift checks for HE eval reports."""

from __future__ import annotations

import re

from report_fields import section_present
from report_contract import DRIFT_AREAS, DRIFT_VALUES, GATE_FIELDS, LINEAR_FIELDS, REQUIRED_SECTIONS


def validate_sections(text: str, errors: list[str]):
    for section in REQUIRED_SECTIONS:
        if not section_present(text, section):
            errors.append(f"missing required section: {section}")


def validate_linear_fields(text: str, errors: list[str]):
    for field in LINEAR_FIELDS:
        if field not in text:
            errors.append(f"missing Linear backlink field: {field}")


def validate_gate_matrix(text: str, errors: list[str], warnings: list[str]):
    if "Gate:" not in text:
        warnings.append("no Gate: entries found in eval gate matrix")
        return
    for field in GATE_FIELDS:
        if field not in text:
            errors.append(f"gate matrix is missing field: {field}")


def validate_drift_classifications(text: str, errors: list[str]):
    for area in DRIFT_AREAS:
        match = re.search(rf"(?mi)^{re.escape(area)}\s*([A-Za-z -]+)", text)
        if not match:
            errors.append(f"missing drift classification: {area}")
            continue
        value = match.group(1).strip()
        if value not in DRIFT_VALUES:
            errors.append(f"invalid drift classification for {area} {value!r}")
