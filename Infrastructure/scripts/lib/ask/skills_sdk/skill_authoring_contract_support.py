"""Shared value objects and small primitives for authoring-contract checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


AUTHORING_CONTRACT_SCHEMA_VERSION = "skills-sdk.authoring-contract.v1"
GOLD_STANDARD_RUBRIC = "skills-sdk.gold-standard.v1"
ENTRYPOINT_SECTION_ROLES = frozenset(
    {"routing", "action", "safety", "output", "proof", "reference"}
)
BLOCKER_CATEGORIES = frozenset(
    {"tool", "input", "credential", "permission", "evidence"}
)
DECISION_BOUNDARY_KINDS = frozenset(
    {"scope", "authority", "side_effect", "stop_condition", "evidence_claim"}
)
READINESS_LANES = frozenset({"structural", "package", "behavioral", "runtime"})


@dataclass
class AuthoringContext:
    """Mutable receipt state for one deterministic authoring-contract check."""

    repo_root: Path | None
    skill_md: Path | None
    frontmatter: dict[str, Any]
    contract: dict[str, Any]
    text: str
    entrypoint_text: str
    source_path: str | None
    headings: set[str]
    sections: dict[str, str]
    duplicate_headings: set[str]
    scenario_ids: set[str]
    checks: list[dict[str, Any]] = field(default_factory=list)
    blockers: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class CheckSpec:
    """Inputs for one authoring-contract check."""

    name: str
    ok: bool
    evidence: dict[str, Any]
    blocker_id: str
    message: str


def is_nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_scenario_ids(value: object, declared_ids: set[str]) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(case_id, str) and case_id in declared_ids for case_id in value)
    )


def as_bool(value: object) -> bool:
    return value is True or (
        isinstance(value, str) and value.strip().casefold() in {"1", "true", "yes", "on"}
    )


def rubric_profile_ids(contract: dict[str, Any]) -> set[str]:
    raw = contract.get("rubric_profiles", contract.get("rubric_profile"))
    if isinstance(raw, str) and raw.strip():
        return {raw.strip()}
    if isinstance(raw, list):
        return {item.strip() for item in raw if isinstance(item, str) and item.strip()}
    return set()


def contained_regular_reference(skill_md: Path | None, path: object) -> bool:
    if skill_md is None or not isinstance(path, str):
        return False
    skill_root = skill_md.parent.resolve(strict=False)
    references_root = skill_md.parent / "references"
    unresolved = skill_md.parent / path
    try:
        resolved_references = references_root.resolve(strict=False)
        resolved_candidate = unresolved.resolve(strict=False)
    except OSError:
        return False
    return (
        resolved_references.is_relative_to(skill_root)
        and resolved_candidate.is_relative_to(resolved_references)
        and unresolved.is_file()
        and not unresolved.is_symlink()
    )


def repo_relative(repo_root: Path | None, path: Path | None) -> str | None:
    if path is None:
        return None
    if repo_root is None:
        return path.as_posix()
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def expected_focused_proof(repo_root: Path | None, skill_md: Path | None) -> str | None:
    source_path = repo_relative(repo_root, skill_md.parent if skill_md else None)
    if source_path is None:
        return None
    return f"./bin/ask sdk eval scenario-quality {source_path} --preview --json --robot"


def expected_behavior_proof(repo_root: Path | None, skill_md: Path | None) -> str | None:
    source_path = repo_relative(repo_root, skill_md.parent if skill_md else None)
    if source_path is None:
        return None
    return (
        f"./bin/ask evals run {source_path} --mode smoke --runner codex "
        "--case <case-id> --skip-tessl --no-dashboard --json --robot"
    )


def declared_scenario_ids(skill_md: Path | None) -> set[str]:
    if skill_md is None:
        return set()
    path = skill_md.parent / "references" / "evals.yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return set()
    from ask.skills_sdk.scenario_quality import _yaml_safe_load  # noqa: PLC0415

    try:
        payload = _yaml_safe_load(text) or {}
    except ValueError:
        return set()
    cases = payload.get("cases") if isinstance(payload, dict) else None
    rows = cases if isinstance(cases, list) else []
    return {
        case_id.strip()
        for row in rows
        if isinstance(row, dict)
        for case_id in [row.get("id")]
        if isinstance(case_id, str) and case_id.strip()
    }


def add_check(context: AuthoringContext, spec: CheckSpec) -> None:
    status = "pass" if spec.ok else "blocked_validation"
    context.checks.append(
        {
            "name": spec.name,
            "status": status,
            "dimension": "authoring_contract",
            "evidence": spec.evidence,
        }
    )
    if not spec.ok:
        context.blockers.append(
            {
                "rule_id": spec.blocker_id,
                "dimension": "authoring_contract",
                "severity": "blocked",
                "path": context.source_path,
                "message": spec.message,
            }
        )


def receipt(
    *,
    required: bool,
    declared: bool,
    status: str,
    checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": AUTHORING_CONTRACT_SCHEMA_VERSION,
        "required_for_package_readiness": required,
        "declared": declared,
        "status": status,
        "checks": checks,
        "blockers": blockers,
        "what_this_proves": (
            [
                "declared_authoring_rules",
                "typed_blocker_contract",
                "reference_and_mutation_links",
            ]
            if status == "pass"
            else []
        ),
        "what_this_does_not_prove": [
            "behavioral_eval_pass",
            "runtime_skill_activation",
            "external_distribution",
        ],
    }
