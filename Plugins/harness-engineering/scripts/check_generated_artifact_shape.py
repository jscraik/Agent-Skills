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
USER_STORY_RE = re.compile(
    r"\bAs an?\s+[^,\n]+,\s*I want\s+[^,\n]+,\s*so that\s+[^\n]+",
    re.IGNORECASE,
)
USER_STORIES_HEADING_RE = re.compile(r"(?im)^###\s+User Stories\b")

SPEC_SECTIONS = [
    "Command Summary",
    "Purpose",
    "Problem Statement",
    "User / Operator Scenarios",
    "Goals",
    "Non-Goals",
    "Current State / Evidence",
    "Authority and Scope Boundary",
    "Proposed Behavior",
    "Requirements",
    "Interfaces",
    "Data / Domain Contract",
    "Enforcement Contract",
    "Proof and Runtime Boundary",
    "Coding and Testing Lenses",
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
    "Authority and Scope Boundary",
    "Current State / Evidence",
    "Implementation Strategy",
    "Runtime Persistence and State",
    "Enforcement Contract",
    "Coding and Testing Lenses",
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
AUTHORITY_TERMS = (
    "requested_depth",
    "approved_execution_boundary",
    "downscope_authority",
    "external_mutation_boundary",
    "freshness_required",
    "human_acceptance_boundary",
)
SPEC_RUNTIME_TERMS = (
    "proof_boundary",
    "non_proof_sources",
    "runtime_state",
    "resumption_key",
    "runtime_invocation_receipt",
    "artifact_chain_key",
    "persistent_artifacts",
    "live_state_refresh",
    "session_evidence_status",
)
PLAN_RUNTIME_TERMS = (
    "runtime_state",
    "resumption_key",
    "runtime_invocation_receipt",
    "artifact_chain_key",
    "persistent_artifacts",
    "live_state_refresh",
    "session_evidence_status",
    "proof_boundary",
)
LENS_TERMS = ("coding_lens", "testing_lens")


def strip_frontmatter(text: str) -> str:
    """
    Remove leading YAML frontmatter delimited by '---\\n' markers from the start of a markdown string.
    
    If the text begins with a YAML frontmatter block (starting with '---\\n' and containing a second '---\\n' delimiter), returns the text after that block; otherwise returns the original text.
    
    Parameters:
        text (str): The input markdown text that may start with YAML frontmatter.
    
    Returns:
        str: The input text with the leading YAML frontmatter removed when present, otherwise the original text.
    """
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
    """
    Validate that the "Enforcement Contract" H2 section exists and contains every required enforcement term.
    
    Parameters:
        text (str): Full markdown document to inspect.
    
    Returns:
        list[str]: `["Enforcement Contract section is empty"]` if the section is missing or blank; otherwise one error per missing required term formatted as `"Enforcement Contract missing required field: <term>"`.
    """
    errors: list[str] = []
    body = section_body(text, "Enforcement Contract")
    if not body.strip():
        return ["Enforcement Contract section is empty"]
    lower = body.lower()
    for term in ENFORCEMENT_TERMS:
        if term not in lower:
            errors.append(f"Enforcement Contract missing required field: {term}")
    return errors


def check_required_terms(text: str, section: str, terms: tuple[str, ...], label: str) -> list[str]:
    """
    Validate that a named H2 section in the given markdown contains each required term and return descriptive errors for missing items.
    
    If the specified section is missing or empty, returns a single error indicating the section is empty. Otherwise returns one error message per term from `terms` that does not appear in the section body (search is case-insensitive); each message is prefixed using `label`.
    
    Parameters:
        text (str): Full markdown document text to search.
        section (str): Exact H2 section title to extract (e.g., "Authority and Scope Boundary").
        terms (tuple[str, ...]): Required phrases to check for (matched case-insensitively).
        label (str): Short label used in returned error messages for missing terms.
    
    Returns:
        list[str]: Error messages describing the empty section or each missing required term.
    """
    body = section_body(text, section)
    if not body.strip():
        return [f"{section} section is empty"]
    lower = body.lower()
    return [f"{label} missing required field: {term}" for term in terms if term not in lower]


def check_section_order(found: list[str], required: list[str]) -> list[str]:
    """
    Validate that each required section title appears in the list of found headings and that they appear in the specified order.
    
    Parameters:
        found (list[str]): Headings discovered in the document, in occurrence order.
        required (list[str]): Required section titles in the expected order.
    
    Returns:
        list[str]: Error messages for violations. Each entry is either
            "missing required section: <section>" when a required title is absent,
            or "section out of order: <section>" when a required title appears before a previously matched required section.
    """
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
    """
    Validate a spec markdown artifact for required sections, required terms, stable IDs, and other shape/contract rules.
    
    Performs checks on headings order, presence and required terms of enforcement/authority/runtime/lens sections, required narrative sections (Problem Statement, User / Operator Scenarios, Proposed Behavior), user-stories formatting and minimum count when requested, presence of stable requirement/acceptance IDs, conformance-rule triggers, forbidden pre-body harness sections, and presence of visual evidence (Mermaid/table/image or explicit "not needed" justification). Each detected rule violation is returned as a separate error message.
    
    Parameters:
        text (str): The full markdown content of the spec to validate.
    
    Returns:
        list[str]: A list of error message strings describing each violation; empty list if the spec passes all checks.
    """
    errors = check_section_order(headings(text), SPEC_SECTIONS)
    errors.extend(check_enforcement_contract(text))
    errors.extend(check_required_terms(text, "Authority and Scope Boundary", AUTHORITY_TERMS, "Authority and Scope Boundary"))
    errors.extend(check_required_terms(text, "Proof and Runtime Boundary", SPEC_RUNTIME_TERMS, "Proof and Runtime Boundary"))
    errors.extend(check_required_terms(text, "Coding and Testing Lenses", LENS_TERMS, "Coding and Testing Lenses"))

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
    problem = section_body(text, "Problem Statement")
    if not problem.strip():
        errors.append("Problem Statement must describe the user/operator problem")
    scenarios = section_body(text, "User / Operator Scenarios")
    if not scenarios.strip():
        errors.append("User / Operator Scenarios must describe testable journeys")
    if USER_STORIES_HEADING_RE.search(scenarios):
        story_count = len(USER_STORY_RE.findall(scenarios))
        if story_count == 0:
            errors.append("User Stories must use 'As a..., I want..., so that...' format")
        elif story_count < 3:
            errors.append("User Stories section must include at least three stories when requested")
    proposed = section_body(text, "Proposed Behavior")
    if not proposed.strip():
        errors.append("Proposed Behavior must include the user-facing solution")
    if re.search(r"(?im)^###\s+User-Facing Solution\b", proposed):
        user_facing_solution_body = re.sub(r"(?im)^###\s+User-Facing Solution\b", "", proposed).strip()
        if not re.search(r"\b(users?|operators?|customers?|admins?)\b", user_facing_solution_body, re.IGNORECASE):
            errors.append("User-Facing Solution must stay grounded in user/operator value")
    if not has_visual_decision(text):
        errors.append("Visual References / Diagrams must contain Mermaid, table, image, or Not needed reason")
    return errors


def validate_plan(text: str) -> list[str]:
    """
    Validate a plan Markdown document for required structure, sections, terms, identifiers, and wiring.
    
    Performs content checks specific to plan artifacts and returns any violations found. Key checks:
    - required H2 section ordering and presence;
    - required phrases in "Enforcement Contract", "Authority and Scope Boundary", "Runtime Persistence and State", and "Coding and Testing Lenses";
    - "Work Units" contains at least one stable `PU-*` ID and the execution phrases: "allowed path", "forbidden path", "validation", "stop condition", "rollback", and "handoff";
    - presence of at least one source/acceptance mapping (`FR-*`, `NFR-*`, `SA-*`, or `VAC-*`);
    - when present, "Validation Gates" must reference observable behavior, proof, prior art, source requirements, or acceptance IDs;
    - "Visual References / Diagrams" must include a Mermaid diagram, image, table row, or an explicit "not needed" justification.
    
    Parameters:
        text (str): Markdown content of the plan to validate.
    
    Returns:
        list[str]: Error messages for each validation failure; empty when no violations are found.
    """
    errors = check_section_order(headings(text), PLAN_SECTIONS)
    errors.extend(check_enforcement_contract(text))
    errors.extend(check_required_terms(text, "Authority and Scope Boundary", AUTHORITY_TERMS, "Authority and Scope Boundary"))
    errors.extend(check_required_terms(text, "Runtime Persistence and State", PLAN_RUNTIME_TERMS, "Runtime Persistence and State"))
    errors.extend(check_required_terms(text, "Coding and Testing Lenses", LENS_TERMS, "Coding and Testing Lenses"))
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
    validation = section_body(text, "Validation Gates")
    if validation and not re.search(r"(?is)(observable behavior|external behavior|expected outcome|proof|prior[- ]art|source requirement|acceptance ID)", validation):
        errors.append("Validation Gates must tie testing decisions to observable behavior, source IDs, or proof")
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
