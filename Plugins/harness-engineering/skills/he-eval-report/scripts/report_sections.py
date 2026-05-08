"""Required section, gate, and drift checks for HE eval reports."""

from __future__ import annotations

import re

from report_fields import section_present


REQUIRED_SECTIONS = [
    "Executive Eval Summary",
    "Evaluated Slice",
    "Linear Definition of Done Status",
    "Linear Backlink Map",
    "Source Artifact Trace",
    "Functional Validation Results",
    "Eval Gate Matrix",
    "Agentic Eval Validity",
    "Side-Effect Authorization",
    "Drift Validation",
    "Architecture Integrity Check",
    "Routing Determinism Check",
    "Context Load Check",
    "Agent-Native Check",
    "Governance Simplicity Check",
    "Moat Protection Check",
    "Proof Artifacts",
    "Failures / Regressions",
    "Linear Completion Recommendation",
    "Follow-Up Work",
    "Core / ADR Update Recommendation",
    "Evidence & Traceability Matrix",
]

LINEAR_FIELDS = [
    "Linear Project:",
    "Linear Milestone:",
    "Linear Parent Issue:",
    "Linear Sub-Issues:",
    "Linear Status Recommendation:",
    "Proof Artifact Links:",
]

GATE_FIELDS = [
    "Gate:",
    "Expected:",
    "Actual:",
    "Status:",
    "Evidence:",
    "Confidence:",
    "Blocks Closure:",
    "Required Action:",
]

DRIFT_AREAS = [
    "Architecture Drift:",
    "Routing Drift:",
    "Context Drift:",
    "Governance Drift:",
    "Agent-Native Drift:",
    "Moat Drift:",
]

DRIFT_VALUES = {"Improved", "Neutral", "Regressed", "Unknown"}


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
