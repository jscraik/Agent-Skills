"""Completion recommendation and consistency checks for HE eval reports."""

from __future__ import annotations

import re
from pathlib import Path


RECOMMENDATIONS = {
    "Complete",
    "Complete with follow-up",
    "Blocked",
    "Needs rework",
    "Unsafe to close",
}


def find_recommendation(text: str):
    match = re.search(r"(?mi)^Classification:\s*(.+?)\s*$", text)
    if not match:
        match = re.search(r"(?mi)^Linear Completion Recommendation:\s*(.+?)\s*$", text)
    if not match:
        return None
    value = match.group(1).strip()
    for recommendation in RECOMMENDATIONS:
        if value == recommendation:
            return recommendation
        if value.startswith(f"{recommendation} "):
            return recommendation
    return value


def validate_recommendation(text: str, errors: list[str]):
    recommendation = find_recommendation(text)
    if recommendation is None:
        errors.append("missing Linear completion recommendation classification")
    elif recommendation not in RECOMMENDATIONS:
        errors.append(f"invalid Linear completion recommendation: {recommendation!r}")


def validate_consistency(text: str, path: Path, warnings: list[str]):
    has_not_run = re.search(r"(?i)\bnot[- ]run\b", text)
    has_pass_status = re.search(r"(?mi)^Status:\s*pass\s*$", text)
    if has_not_run and has_pass_status:
        warnings.append("report contains both not-run evidence and pass statuses; verify gates are not overstated")
    if ".harness/evals/" not in str(path):
        warnings.append("report path is outside .harness/evals/")
