from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_profiles import (
    EVAL_PROFILE_ACCEPTANCE_TRACE,
    select_execution_profile,
    select_judge_profile,
)


AB_PREVIEW_SCHEMA_VERSION = "skills-sdk.ab-preview-receipt.v0"
AB_PREVIEW_SCHEMA_URI = "https://jscraik.local/agent-skills/schemas/skills-sdk/ab-preview-receipt.v0.schema.json"


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _fixture_identity(repo_root: Path, fixture: str) -> tuple[dict[str, str | int] | None, str | None]:
    fixture_path = Path(fixture)
    if not fixture_path.is_absolute():
        fixture_path = repo_root / fixture_path
    try:
        resolved = fixture_path.resolve()
        resolved.relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return None, "fixture_outside_repo"
    if not resolved.is_file():
        return None, "fixture_missing"
    return {
        "path": _repo_relative(repo_root, resolved),
        "digest": _digest_file(resolved),
        "size_bytes": resolved.stat().st_size,
    }, None


def _variant(label: str, query: str, package_identity: dict[str, str]) -> dict[str, str]:
    return {
        "label": label,
        "query": query,
        "skill_ir_schema_version": package_identity["skill_ir_schema_version"],
        "package_id": package_identity["package_id"],
        "package_digest": package_identity["package_digest"],
    }


def build_ab_preview_receipt(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    skill_a_identity: dict[str, str] | None,
    skill_b_identity: dict[str, str] | None,
    execution_profile_id: str = "codex-read-only",
    judge_profile_id: str = "oss-local",
) -> dict[str, Any]:
    inputs = _preview_inputs(
        repo_root,
        fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile_id,
        judge_profile_id=judge_profile_id,
    )
    blockers = inputs["blockers"]
    skill_execution_secret_names: list[str] = []
    judge_profile = inputs["judge_profile"]
    judge_secret_names = [] if judge_profile is None else list(judge_profile["secret_env_names"])
    status = "blocked" if blockers else "preview"
    return _preview_payload(
        status=status,
        blockers=blockers,
        skill_a=None if skill_a_identity is None else _variant("A", skill_a, skill_a_identity),
        skill_b=None if skill_b_identity is None else _variant("B", skill_b, skill_b_identity),
        fixture_identity=inputs["fixture_identity"],
        execution_profile=inputs["execution_profile"],
        judge_profile=judge_profile,
        skill_execution_secret_names=skill_execution_secret_names,
        judge_secret_names=judge_secret_names,
    )


def _preview_inputs(
    repo_root: Path,
    fixture: str,
    *,
    skill_a_identity: dict[str, str] | None,
    skill_b_identity: dict[str, str] | None,
    execution_profile_id: str,
    judge_profile_id: str,
) -> dict[str, Any]:
    blockers = _identity_blockers(skill_a_identity, skill_b_identity)
    fixture_identity, fixture_blocker = _fixture_identity(repo_root, fixture)
    if fixture_blocker:
        blockers.append(fixture_blocker)
    execution_profile, execution_blocker = _select_execution_profile(execution_profile_id)
    judge_profile, judge_blocker = _select_judge_profile(judge_profile_id)
    blockers.extend(blocker for blocker in (execution_blocker, judge_blocker) if blocker)
    return {
        "blockers": blockers,
        "fixture_identity": fixture_identity,
        "execution_profile": execution_profile,
        "judge_profile": judge_profile,
    }


def _identity_blockers(skill_a_identity: dict[str, str] | None, skill_b_identity: dict[str, str] | None) -> list[str]:
    blockers: list[str] = []
    if skill_a_identity is None:
        blockers.append("skill_a_identity_unresolved")
    if skill_b_identity is None:
        blockers.append("skill_b_identity_unresolved")
    return blockers


def _select_execution_profile(profile_id: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return select_execution_profile(profile_id), None
    except ValueError:
        return None, "execution_profile_unknown"


def _select_judge_profile(profile_id: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return select_judge_profile(profile_id), None
    except ValueError:
        return None, "judge_profile_unknown"


def _preview_payload(
    *,
    status: str,
    blockers: list[str],
    skill_a: dict[str, str] | None,
    skill_b: dict[str, str] | None,
    fixture_identity: dict[str, str | int] | None,
    execution_profile: dict[str, Any] | None,
    judge_profile: dict[str, Any] | None,
    skill_execution_secret_names: list[str],
    judge_secret_names: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": AB_PREVIEW_SCHEMA_VERSION,
        "schema_uri": AB_PREVIEW_SCHEMA_URI,
        "status": status,
        "operation": "ab_preview",
        "skill_a": skill_a,
        "skill_b": skill_b,
        "fixture": fixture_identity,
        "execution_profile": execution_profile,
        "judge_profile": judge_profile,
        "evidence_plan": _evidence_plan(),
        "secret_boundary": _secret_boundary(skill_execution_secret_names, judge_secret_names),
        "execution_boundary": "codex_exec_sandbox",
        "judge_boundary": "post_run_sanitized_evidence_only",
        "mutation_performed": False,
        "network_accessed": False,
        "provider_invoked": False,
        "codex_exec_invoked": False,
        "blockers": blockers,
        "acceptance_trace": EVAL_PROFILE_ACCEPTANCE_TRACE,
        "agent_summary": (
            "A/B eval preview is ready to run later through Codex sandbox execution."
            if status == "preview"
            else f"A/B eval preview is blocked: {', '.join(blockers)}."
        ),
    }


def _evidence_plan() -> dict[str, Any]:
    return {
        "codex_json_events": True,
        "output_diff": True,
        "validation_results": True,
        "judge_decision": True,
        "winner_values": ["skill_a", "skill_b", "inconclusive"],
    }


def _secret_boundary(skill_execution_secret_names: list[str], judge_secret_names: list[str]) -> dict[str, Any]:
    return {
        "skill_execution_env_secret_names": skill_execution_secret_names,
        "judge_env_secret_names": judge_secret_names,
        "skill_execution_receives_judge_secrets": False,
    }
