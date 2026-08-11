from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from ask.skills_sdk.handoff_readiness import _repo_relative, _skill_dir, build_candidate_identity


AB_FIXTURE_STAGE_SCHEMA_VERSION = "skills-sdk.ab-fixture-stage.v1"
_EVIDENCE_ROOT = (".harness", "evidence", "handoff")


@dataclass(frozen=True)
class AbFixtureStageRequest:
    """One source-owned scenario prompt staged for a bounded A/B execution."""

    skill: str
    case_id: str
    fixture_path: Path
    operation: Literal["preview", "execute"]


def stage_ab_fixture(
    repo_root: Path,
    *,
    source_path: Path,
    request: AbFixtureStageRequest,
) -> dict[str, Any]:
    """Stage one canonical scenario prompt without inventing an A/B task fixture."""
    target, target_error = _fixture_target(repo_root, request.fixture_path)
    candidate = build_candidate_identity(repo_root, source_path)
    prompt, scenario_error = _scenario_prompt(_skill_dir(source_path), request.case_id)
    blockers = [error for error in (target_error, scenario_error) if error]
    if target is not None and (target.exists() or target.is_symlink()):
        blockers.append(f"fixture path already exists: {_repo_relative(repo_root, target)}")
    fixture = _fixture_identity(repo_root, target, prompt) if target is not None and prompt is not None else None
    if blockers or request.operation == "preview":
        return _receipt(request, candidate, fixture, blockers, mutation_performed=False)
    if target is None or prompt is None:
        return _receipt(request, candidate, fixture, ["fixture staging inputs are invalid"], mutation_performed=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(prompt.encode("utf-8"))
    return _receipt(request, candidate, fixture, [], mutation_performed=True)


def _fixture_target(repo_root: Path, requested_path: Path) -> tuple[Path | None, str | None]:
    target = requested_path if requested_path.is_absolute() else repo_root / requested_path
    target = target.resolve(strict=False)
    evidence_root = (repo_root.joinpath(*_EVIDENCE_ROOT)).resolve()
    try:
        target.relative_to(evidence_root)
    except ValueError:
        return None, "fixture path must be contained by .harness/evidence/handoff"
    if target == evidence_root:
        return None, "fixture path must name a new file below .harness/evidence/handoff"
    return target, None


def _scenario_prompt(skill_dir: Path, case_id: str) -> tuple[str | None, str | None]:
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.is_file() or evals_path.is_symlink():
        return None, "skill is missing a regular references/evals.yaml"
    try:
        from ask.skills_sdk.scenario_quality import _yaml_safe_load

        payload = _yaml_safe_load(evals_path.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError):
        return None, "skill references/evals.yaml is unreadable"
    raw_cases = payload.get("cases") if isinstance(payload, dict) else None
    if not isinstance(raw_cases, list):
        return None, "skill references/evals.yaml must contain cases"
    matches = [
        case.get("prompt")
        for case in raw_cases
        if isinstance(case, dict) and case.get("id") == case_id and isinstance(case.get("prompt"), str)
    ]
    if len(matches) != 1:
        return None, f"skill must contain exactly one prompt for scenario: {case_id}"
    return matches[0], None


def _fixture_identity(repo_root: Path, target: Path, prompt: str) -> dict[str, Any]:
    payload = prompt.encode("utf-8")
    return {
        "path": _repo_relative(repo_root, target),
        "digest": f"sha256:{hashlib.sha256(payload).hexdigest()}",
        "size_bytes": len(payload),
    }


def _receipt(
    request: AbFixtureStageRequest,
    candidate: dict[str, str],
    fixture: dict[str, Any] | None,
    blockers: list[str],
    *,
    mutation_performed: bool,
) -> dict[str, Any]:
    status = "blocked" if blockers else ("pass" if request.operation == "execute" else "preview")
    return {
        "schema_version": AB_FIXTURE_STAGE_SCHEMA_VERSION,
        "status": status,
        "operation": "ab_fixture_stage",
        "skill": request.skill,
        "case_id": request.case_id,
        "candidate": candidate,
        "fixture": fixture,
        "blockers": blockers,
        "mutation_performed": mutation_performed,
        "agent_summary": (
            "Canonical scenario fixture staged for the bounded A/B run."
            if status == "pass"
            else "Canonical scenario fixture staging is blocked."
            if status == "blocked"
            else "Canonical scenario fixture staging preview is valid; rerun with --execute to write it."
        ),
    }
