#!/usr/bin/env python3
"""Validate generated he-spec and he-plan artifact shape.

This gate checks the artifact that Jamie reviews, not the skill package that
generated it. It catches reader-contract failures that normal skill audits
cannot see: process-heavy bodies, missing visual decisions, weak requirement
IDs, and plan units without execution proof.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
MERMAID_RE = re.compile(r"```mermaid\b", re.IGNORECASE)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
TABLE_RE = re.compile(r"(?m)^\|.+\|\s*$")
NOT_NEEDED_RE = re.compile(r"\bnot needed\b", re.IGNORECASE)
FR_RE = re.compile(r"\bFR-\d{3,}\b")
NFR_RE = re.compile(r"\bNFR-\d{3,}\b")
SA_RE = re.compile(r"\bSA-\d{3,}\b")
PU_RE = re.compile(r"\bPU-\d{3,}\b")
VAC_RE = re.compile(r"\bVAC-\d{3,}\b")

SPEC_SECTIONS = [
    "Command Summary",
    "Purpose",
    "Problem Statement",
    "User / Operator Scenarios",
    "Goals",
    "Non-Goals",
    "Current State / Evidence",
    "Proposed Behavior",
    "Requirements",
    "Interfaces",
    "Data / Domain Contract",
    "Enforcement Contract",
    "Security, Privacy, and Safety",
    "Failure and Recovery",
    "Validation Plan",
    "Acceptance Criteria",
    "Visual References / Diagrams",
    "Evidence and References",
]

PLAN_SECTIONS = [
    "Command Summary",
    "Objective",
    "Source Contract",
    "Scope and Boundaries",
    "Current State / Evidence",
    "Implementation Strategy",
    "Enforcement Contract",
    "Work Units",
    "Validation Gates",
    "Review Plan",
    "Rollback Plan",
    "Risk Register",
    "Visual References / Diagrams",
    "Final Decision",
]

CONFORMANCE_TRIGGERS = re.compile(
    r"\b(CLI|API|protocol|ledger|manifest|schema|generated file|file format|"
    r"data contract|domain contract|consumer behavior)\b",
    re.IGNORECASE,
)
CONFORMANCE_TERMS = (
    "required field",
    "optional field",
    "enum",
    "unknown-field",
    "unknown field",
    "compatibility",
    "versioning",
    "consumer behavior",
    "error handling",
)
ENFORCEMENT_TERMS = (
    "essential_decisions",
    "fillable_gaps",
    "guardrails",
    "refusal_triggers",
    "durable_memory",
    "professional_output",
)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def headings(text: str) -> list[str]:
    return [match.group(1).strip() for match in H2_RE.finditer(text)]


def section_body(text: str, section: str) -> str:
    marker = f"## {section}"
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def has_visual_decision(text: str) -> bool:
    body = section_body(text, "Visual References / Diagrams")
    return bool(
        body.strip()
        and (
            MERMAID_RE.search(body)
            or IMAGE_RE.search(body)
            or TABLE_RE.search(body)
            or NOT_NEEDED_RE.search(body)
        )
    )


def check_enforcement_contract(text: str) -> list[str]:
    errors: list[str] = []
    body = section_body(text, "Enforcement Contract")
    if not body.strip():
        return ["Enforcement Contract section is empty"]
    lower = body.lower()
    for term in ENFORCEMENT_TERMS:
        if term not in lower:
            errors.append(f"Enforcement Contract missing required field: {term}")
    return errors


def check_section_order(found: list[str], required: list[str]) -> list[str]:
    errors: list[str] = []
    cursor = -1
    for section in required:
        try:
            index = found.index(section)
        except ValueError:
            errors.append(f"missing required section: {section}")
            continue
        if index < cursor:
            errors.append(f"section out of order: {section}")
        cursor = max(cursor, index)
    return errors


def validate_spec(text: str) -> list[str]:
    errors = check_section_order(headings(text), SPEC_SECTIONS)
    errors.extend(check_enforcement_contract(text))

    prefix = text.split("## Purpose", 1)[0]
    forbidden_prefix = ("Mode Decision", "Selection Evidence", "Blackboard Delta", "Validation Outcomes")
    for label in forbidden_prefix:
        if label in prefix:
            errors.append(f"Harness process section appears before spec body: {label}")

    if not FR_RE.search(text):
        errors.append("missing stable FR-* requirement IDs")
    if not (SA_RE.search(text) or VAC_RE.search(text)):
        errors.append("missing stable SA-* or VAC-* acceptance IDs")
    if "Non-Functional Requirements" in text and not NFR_RE.search(text):
        errors.append("Non-Functional Requirements section has no stable NFR-* IDs")
    if CONFORMANCE_TRIGGERS.search(text) and not any(term in text.lower() for term in CONFORMANCE_TERMS):
        errors.append("format/API/data contract content lacks conformance rules")
    if not has_visual_decision(text):
        errors.append("Visual References / Diagrams must contain Mermaid, table, image, or Not needed reason")
    return errors


def validate_plan(text: str) -> list[str]:
    errors = check_section_order(headings(text), PLAN_SECTIONS)
    errors.extend(check_enforcement_contract(text))
    work_units = section_body(text, "Work Units")
    if not PU_RE.search(work_units):
        errors.append("Work Units section missing stable PU-* IDs")
    for phrase in (
        "allowed path",
        "forbidden path",
        "validation",
        "stop condition",
        "rollback",
        "handoff",
    ):
        if phrase not in work_units.lower():
            errors.append(f"Work Units missing required execution field: {phrase}")
    if not (FR_RE.search(text) or NFR_RE.search(text) or SA_RE.search(text) or VAC_RE.search(text)):
        errors.append("plan lacks source requirement or acceptance ID mapping")
    if not has_visual_decision(text):
        errors.append("Visual References / Diagrams must contain Mermaid, table, image, or Not needed reason")
    return errors


def infer_kind(path: Path, text: str, explicit: str) -> str:
    if explicit != "auto":
        return explicit
    lower = str(path).lower()
    artifact_match = re.search(r"(?m)^artifact_type:\s*(\S+)", text)
    artifact_type = artifact_match.group(1).lower() if artifact_match else ""
    if "he-plan" in artifact_type or "/plan/" in lower or lower.endswith("-plan.md"):
        return "plan"
    if "he-spec" in artifact_type or "/specs/" in lower or "spec" in lower:
        return "spec"
    return "unknown"


def validate(path: Path, *, kind: str) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    body = strip_frontmatter(raw)
    resolved_kind = infer_kind(path, raw, kind)
    if resolved_kind == "spec":
        errors = validate_spec(body)
    elif resolved_kind == "plan":
        errors = validate_plan(body)
    else:
        errors = ["could not infer artifact kind; pass --kind spec or --kind plan"]
    return {
        "path": str(path),
        "kind": resolved_kind,
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--kind", choices=("auto", "spec", "plan"), default="auto")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = [validate(path, kind=args.kind) for path in args.paths]
    failed = any(result["status"] == "fail" for result in results)
    payload = {"schema_version": 1, "status": "fail" if failed else "pass", "results": results}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        for result in results:
            print(f"{result['path']}: {result['kind']} {result['status']}")
            for error in result["errors"]:
                print(f"  error: {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
