"""Deterministic admission checks for Skills SDK authoring contracts.

This facade selects the strict contract and coordinates independent validators.
The validators prove declared structure and proof links; behavioral and runtime
evidence remain separate lanes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ask.skills_sdk.skill_authoring_contract_markdown import (
    level_two_heading_sections,
    without_fenced_content,
)
from ask.skills_sdk.skill_authoring_contract_support import (
    AUTHORING_CONTRACT_SCHEMA_VERSION,
    GOLD_STANDARD_RUBRIC,
    AuthoringContext,
    declared_scenario_ids,
    receipt,
    repo_relative,
    rubric_profile_ids,
)
from ask.skills_sdk.skill_authoring_contract_validators import (
    validate_behavior_proof,
    validate_blocker_matrix,
    validate_critical_rules,
    validate_decision_boundaries,
    validate_entrypoint_budget,
    validate_focused_proof,
    validate_invocation,
    validate_mutation_targets,
    validate_output_contract,
    validate_phase_model,
    validate_primary_job,
    validate_readiness_evidence,
    validate_reference_routes,
    validate_schema,
    validate_steering_terms,
)


def authoring_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
    reference_contract: dict[str, Any],
    text: str,
) -> dict[str, Any]:
    """Validate the strict authoring contract selected by gold-standard packages."""
    profiles = rubric_profile_ids(reference_contract)
    declared = reference_contract.get("authoring_contract")
    required = GOLD_STANDARD_RUBRIC in profiles
    if not required:
        return _not_applicable_receipt(declared, profiles)
    if not isinstance(declared, dict):
        return _missing_contract_receipt(repo_root, skill_md)
    context = _context(repo_root, skill_md, frontmatter, declared, text)
    _run_validators(context)
    return receipt(
        required=True,
        declared=True,
        status="blocked_validation" if context.blockers else "pass",
        checks=context.checks,
        blockers=context.blockers,
    )


def _not_applicable_receipt(declared: object, profiles: set[str]) -> dict[str, Any]:
    return receipt(
        required=False,
        declared=isinstance(declared, dict),
        status="not_applicable",
        checks=[
            {
                "name": "authoring_contract_required",
                "status": "not_applicable",
                "dimension": "authoring_contract",
                "evidence": {"rubric_profiles": sorted(profiles)},
            }
        ],
        blockers=[],
    )


def _missing_contract_receipt(
    repo_root: Path | None, skill_md: Path | None
) -> dict[str, Any]:
    return receipt(
        required=True,
        declared=False,
        status="blocked_validation",
        checks=[
            {
                "name": "authoring_contract_declared",
                "status": "blocked_validation",
                "dimension": "authoring_contract",
                "evidence": {"expected": "references/contract.yaml: authoring_contract"},
            }
        ],
        blockers=[
            {
                "rule_id": "authoring_contract_missing",
                "dimension": "authoring_contract",
                "severity": "blocked",
                "path": repo_relative(repo_root, skill_md),
                "message": "Gold-standard SDK packages must declare an authoring contract in references/contract.yaml.",
            }
        ],
    )


def _context(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
    contract: dict[str, Any],
    text: str,
) -> AuthoringContext:
    sections, duplicate_headings = level_two_heading_sections(text)
    return AuthoringContext(
        repo_root=repo_root,
        skill_md=skill_md,
        frontmatter=frontmatter,
        contract=contract,
        text=text,
        entrypoint_text=without_fenced_content(text),
        source_path=repo_relative(repo_root, skill_md),
        headings=set(sections),
        sections=sections,
        duplicate_headings=duplicate_headings,
        scenario_ids=declared_scenario_ids(skill_md),
    )


def _run_validators(context: AuthoringContext) -> None:
    validate_schema(context, AUTHORING_CONTRACT_SCHEMA_VERSION)
    validate_primary_job(context)
    validate_invocation(context)
    validate_entrypoint_budget(context)
    rules = validate_critical_rules(context)
    validate_steering_terms(context)
    validate_phase_model(context)
    validate_decision_boundaries(context)
    validate_blocker_matrix(context)
    routes = validate_reference_routes(context)
    validate_output_contract(context)
    validate_mutation_targets(context, rules, routes)
    validate_focused_proof(context)
    validate_behavior_proof(context)
    validate_readiness_evidence(context)
