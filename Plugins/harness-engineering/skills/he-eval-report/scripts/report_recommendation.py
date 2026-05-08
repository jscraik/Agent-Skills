"""Completion recommendation and consistency checks for HE eval reports."""

from __future__ import annotations

import re
from pathlib import Path

from report_contract import RECOMMENDATIONS
from report_fields import ReportDocument


def find_recommendation(document: ReportDocument):
    recommendation_body = document.section_body("Linear Completion Recommendation") or document.text
    match = re.search(r"(?mi)^Classification:\s*(.+?)\s*$", recommendation_body)
    if not match:
        match = re.search(r"(?mi)^Linear Completion Recommendation:\s*(.+?)\s*$", recommendation_body)
    if not match:
        return None
    value = match.group(1).strip()
    for recommendation in RECOMMENDATIONS:
        if value == recommendation:
            return recommendation
        if value.startswith(f"{recommendation} "):
            return recommendation
    return value


def validate_recommendation(document: ReportDocument, errors: list[str]):
    recommendation = find_recommendation(document)
    if recommendation is None:
        errors.append("missing Linear completion recommendation classification")
    elif recommendation not in RECOMMENDATIONS:
        errors.append(f"invalid Linear completion recommendation: {recommendation!r}")


def validate_consistency(document: ReportDocument, path: Path, warnings: list[str]):
    for entry in document.gate_entries():
        status = entry.get("Status:", "").lower()
        evidence = " ".join(entry.get(field, "") for field in ("Actual:", "Evidence:", "Required Action:"))
        if status == "pass" and re.search(r"(?i)\bnot[- ]run\b", evidence):
            gate_name = entry.get("Gate:", "<unnamed>")
            warnings.append(f"gate {gate_name!r} is pass but contains not-run evidence; verify it is not overstated")
    if ".harness/evals/" not in str(path):
        warnings.append("report path is outside .harness/evals/")
