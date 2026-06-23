from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_ab_preview import build_ab_preview_receipt


AB_PLAN_SCHEMA_VERSION = "skills-sdk.ab-plan-receipt.v0"
AB_PLAN_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/ab-plan-receipt.v0.schema.json"
DEFAULT_EVIDENCE_ROOT = ".harness/artifacts/sdk-ab-evals"


def _digest_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _planned_evidence_root(repo_root: Path, evidence_root: str) -> tuple[str | None, str | None]:
    root = Path(evidence_root)
    if root.is_absolute():
        candidate = root
    else:
        candidate = repo_root / root
    try:
        resolved = candidate.resolve()
        resolved.relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return None, "evidence_root_outside_repo"
    return _repo_relative(repo_root, resolved), None


def _experiment_id(preview_receipt: dict[str, Any], execution_profile_id: str, judge_profile_id: str) -> str:
    parts = [
        str(preview_receipt["skill_a"]["package_digest"]),
        str(preview_receipt["skill_b"]["package_digest"]),
        str(preview_receipt["fixture"]["digest"]),
        execution_profile_id,
        judge_profile_id,
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def _variant_command(
    *,
    label: str,
    repo_root_label: str,
    sandbox_mode: str,
    approval_policy: str,
    evidence_root: str,
    experiment_id: str,
    prompt: str,
) -> dict[str, Any]:
    variant_root = f"{evidence_root}/{experiment_id}/{label}"
    output_path = f"{variant_root}/last-message.json"
    event_log_path = f"{variant_root}/codex-events.jsonl"
    prompt_path = f"{variant_root}/prompt.md"
    return {
        "variant_label": label,
        "command_argv": _codex_command_argv(sandbox_mode, approval_policy, repo_root_label, output_path),
        "sandbox_mode": sandbox_mode,
        "approval_policy": approval_policy,
        "event_log_path": event_log_path,
        "output_last_message_path": output_path,
        "prompt_stdin_path": prompt_path,
        "runner_stdout_capture_path": event_log_path,
        "runner_prompt_input_path": prompt_path,
        "prompt_stdin_digest": _digest_text(prompt),
        "planned_write_paths": [output_path],
        "allowed_secret_env_names": [],
    }


def _codex_command_argv(sandbox_mode: str, approval_policy: str, repo_root_label: str, output_path: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--sandbox",
        sandbox_mode,
        "--ask-for-approval",
        approval_policy,
        "--cd",
        repo_root_label,
        "--json",
        "--output-last-message",
        output_path,
        "-",
    ]


def _variant_prompt(variant: dict[str, str], fixture: dict[str, Any]) -> str:
    return (
        f"Run Skills SDK A/B variant {variant['label']} against fixture {fixture['path']}.\n"
        f"Skill query: {variant['query']}\n"
        f"Package id: {variant['package_id']}\n"
        f"Package digest: {variant['package_digest']}\n"
        f"Fixture digest: {fixture['digest']}\n"
        "Return sanitized evidence only. Do not include secrets."
    )


def build_ab_plan_receipt(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    skill_a_identity: dict[str, str] | None,
    skill_b_identity: dict[str, str] | None,
    execution_profile_id: str = "codex-read-only",
    judge_profile_id: str = "oss-local",
    evidence_root: str = DEFAULT_EVIDENCE_ROOT,
) -> dict[str, Any]:
    preview = _preview_receipt(
        repo_root,
        skill_a=skill_a,
        skill_b=skill_b,
        fixture=fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile_id,
        judge_profile_id=judge_profile_id,
    )
    blockers = list(preview["blockers"])
    evidence_root_label, evidence_blocker = _planned_evidence_root(repo_root, evidence_root)
    if evidence_blocker:
        blockers.append(evidence_blocker)

    experiment_id, command_plan = _planned_commands(
        preview,
        blockers=blockers,
        evidence_root_label=evidence_root_label,
        execution_profile_id=execution_profile_id,
        judge_profile_id=judge_profile_id,
    )

    status = "blocked" if blockers else "planned"
    return _plan_payload(preview, status, blockers, evidence_root_label, experiment_id, command_plan)


def _preview_receipt(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
    return build_ab_preview_receipt(repo_root, **kwargs)


def _planned_commands(
    preview: dict[str, Any],
    *,
    blockers: list[str],
    evidence_root_label: str | None,
    execution_profile_id: str,
    judge_profile_id: str,
) -> tuple[str | None, list[dict[str, Any]]]:
    if blockers or evidence_root_label is None:
        return None, []
    experiment_id = _experiment_id(preview, execution_profile_id, judge_profile_id)
    return experiment_id, _variant_commands(preview, evidence_root_label, experiment_id)


def _variant_commands(preview: dict[str, Any], evidence_root_label: str, experiment_id: str) -> list[dict[str, Any]]:
    sandbox_mode = preview["execution_profile"]["sandbox_mode"]
    approval_policy = preview["execution_profile"]["approval_policy"]
    return [
        _variant_command(
            label="A",
            repo_root_label=".",
            sandbox_mode=sandbox_mode,
            approval_policy=approval_policy,
            evidence_root=evidence_root_label,
            experiment_id=experiment_id,
            prompt=_variant_prompt(preview["skill_a"], preview["fixture"]),
        ),
        _variant_command(
            label="B",
            repo_root_label=".",
            sandbox_mode=sandbox_mode,
            approval_policy=approval_policy,
            evidence_root=evidence_root_label,
            experiment_id=experiment_id,
            prompt=_variant_prompt(preview["skill_b"], preview["fixture"]),
        ),
    ]


def _plan_payload(
    preview: dict[str, Any],
    status: str,
    blockers: list[str],
    evidence_root_label: str | None,
    experiment_id: str | None,
    command_plan: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": AB_PLAN_SCHEMA_VERSION,
        "schema_uri": AB_PLAN_SCHEMA_URI,
        "status": status,
        "operation": "ab_plan",
        "skill_a": preview["skill_a"],
        "skill_b": preview["skill_b"],
        "fixture": preview["fixture"],
        "execution_profile": preview["execution_profile"],
        "judge_profile": preview["judge_profile"],
        "evidence_root": evidence_root_label,
        "experiment_id": experiment_id,
        "command_variant_labels": [plan["variant_label"] for plan in command_plan],
        "command_plan": command_plan,
        "secret_boundary": preview["secret_boundary"],
        "execution_boundary": "codex_exec_sandbox",
        "judge_boundary": "post_run_sanitized_evidence_only",
        "mutation_performed": False,
        "network_accessed": False,
        "provider_invoked": False,
        "codex_exec_invoked": False,
        "blockers": blockers,
        "acceptance_trace": preview["acceptance_trace"],
        "agent_summary": (
            "A/B eval execution plan is ready; Codex has not been invoked."
            if status == "planned"
            else f"A/B eval execution plan is blocked: {', '.join(blockers)}."
        ),
    }
