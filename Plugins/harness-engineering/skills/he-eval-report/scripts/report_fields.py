"""Markdown section and field helpers for HE eval report validation."""

from __future__ import annotations

import re

from report_contract import YES_NO_VALUES


def section_present(text: str, section: str):
    pattern = rf"(?m)^#{{1,3}}\s+{re.escape(section)}\s*$"
    return re.search(pattern, text) is not None


def section_body(text: str, section: str):
    pattern = rf"(?ms)^#{{1,3}}\s+{re.escape(section)}\s*$\n(?P<body>.*?)(?=^#{{1,3}}\s+|\Z)"
    match = re.search(pattern, text)
    return match.group("body") if match else ""


def field_value(text: str, field: str):
    match = re.search(rf"(?mi)^{re.escape(field)}\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else None


def is_blankish(value: str | None):
    if value is None:
        return True
    return value.strip().lower() in {"", "n/a", "na", "none", "unknown", "tbd", "todo"}


def validate_required_fields(
    body: str,
    fields: list[str],
    errors: list[str],
    label: str,
    *,
    enforce_values: bool,
    optional_blank_fields: set[str] | None = None,
):
    optional_blank_fields = optional_blank_fields or set()
    for field in fields:
        if field not in body:
            errors.append(f"{label} section is missing field: {field}")
            continue
        if field in optional_blank_fields:
            continue
        if enforce_values and is_blankish(field_value(body, field)):
            errors.append(f"{label} field is blank: {field}")
