from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_ab_preview import build_ab_preview_receipt
from ask.skills_sdk.eval_profiles import select_judge_profile
from ask.skills_sdk.eval_ab_preflight import PreflightProbe, build_lane_preflight


AB_PLAN_SCHEMA_VERSION = "skills-sdk.ab-plan-receipt.v1"
AB_PLAN_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/ab-plan-receipt.v1.schema.json"
DEFAULT_EVIDENCE_ROOT = ".harness/artifacts/sdk-ab-evals"
_PROMPT_FIXTURE_LIMIT_BYTES = 64 * 1024
_PROMPT_SKILL_LIMIT_BYTES = 128 * 1024


def _digest_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _digest_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _experiment_id_from_seed(seed: str) -> str:
    return f"ex_{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16]}"


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
    return _experiment_id_from_seed("\n".join(parts))


def _variant_command(
    *,
    label: str,
    repo_root_label: str,
    sandbox_mode: str,
    approval_policy: str,
    evidence_root: str,
    experiment_id: str,
    prompt: str,
    codex_profile: str,
) -> dict[str, Any]:
    variant_root = f"{evidence_root}/{experiment_id}/{codex_profile}/{label}"
    output_path = f"{variant_root}/last-message.json"
    event_log_path = f"{variant_root}/codex-events.jsonl"
    prompt_path = f"{variant_root}/prompt.md"
    return {
        "variant_label": label,
        "codex_profile": codex_profile,
        "command_argv": _codex_command_argv(
            sandbox_mode, approval_policy, repo_root_label, output_path, codex_profile,
        ),
        "execution_argv": _planned_execution_argv(codex_profile, _codex_command_argv(
            sandbox_mode, approval_policy, repo_root_label, output_path, codex_profile,
        )),
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


def _codex_command_argv(
    sandbox_mode: str,
    approval_policy: str,
    repo_root_label: str,
    output_path: str,
    codex_profile: str,
) -> list[str]:
    return [
        "codex",
        "exec",
        "--profile",
        codex_profile,
        "--disable",
        "apps",
        "-c",
        f'approval_policy="{approval_policy}"',
        "--sandbox",
        sandbox_mode,
        "--cd",
        repo_root_label,
        "--json",
        "--output-last-message",
        output_path,
        "-",
    ]


def _planned_execution_argv(codex_profile: str, command_argv: list[str]) -> list[str]:
    """Return the transport argv without exposing the opaque credential source."""
    if codex_profile == "oss-cloud":
        return ["op", "run", "--env-file", "<operator-approved-opaque-env-stream>", "--", *command_argv]
    return list(command_argv)


def _contained_fixture_prompt(repo_root: Path, raw_path: str) -> tuple[str, str]:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise ValueError("fixture prompt source must be repo-relative")
    if ".." in candidate.parts:
        raise ValueError("fixture prompt source must not traverse parent directories")
    raw_candidate = repo_root / candidate
    current = raw_candidate
    while current != repo_root:
        if current.is_symlink():
            raise ValueError("fixture prompt source must not traverse a symlink")
        current = current.parent
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError("fixture prompt source must remain inside the repository") from exc
    relative = resolved.relative_to(repo_root.resolve()).as_posix()
    if not relative.startswith("Infrastructure/tests/fixtures/skills_sdk/"):
        raise ValueError("fixture prompt source is outside the controlled SDK fixture root")
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError("fixture prompt source must be a regular file")
    if resolved.stat().st_size > _PROMPT_FIXTURE_LIMIT_BYTES:
        raise ValueError(f"fixture prompt source exceeds {_PROMPT_FIXTURE_LIMIT_BYTES} bytes")
    raw_bytes = resolved.read_bytes()
    return relative, raw_bytes.decode("utf-8")


def _contained_skill_prompt(repo_root: Path, query: str) -> tuple[str, str, str]:
    from ask.commands.skills_impl import _skills_sdk_eval_source_path  # noqa: PLC0415

    source = _skills_sdk_eval_source_path(repo_root, query)
    if source is None:
        raise ValueError(f"skill source is unavailable for variant {query!r}")
    if source.is_symlink():
        raise ValueError("variant skill source must not traverse a symlink")
    resolved = source.resolve()
    try:
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("variant skill source must remain inside the repository") from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError("variant skill source must be a regular file")
    if resolved.stat().st_size > _PROMPT_SKILL_LIMIT_BYTES:
        raise ValueError(f"variant skill source exceeds {_PROMPT_SKILL_LIMIT_BYTES} bytes")
    raw_bytes = resolved.read_bytes()
    return relative, raw_bytes.decode("utf-8"), _digest_bytes(raw_bytes)


def _variant_prompt(repo_root: Path, variant: dict[str, str], fixture: dict[str, Any]) -> str:
    skill_path, skill_text, skill_digest = _contained_skill_prompt(repo_root, variant["query"])
    fixture_path, fixture_text = _contained_fixture_prompt(repo_root, fixture["path"])
    expected_digest = str(fixture.get("digest") or "")
    actual_digest = _digest_bytes((repo_root / fixture_path).read_bytes())
    if expected_digest != actual_digest:
        raise ValueError(f"fixture digest mismatch: expected {expected_digest}, got {actual_digest}")
    return (
        "Run one self-contained Skills SDK A/B evaluation in read-only mode.\n"
        "Do not call tools, inspect the repository, execute commands, or ask follow-up questions.\n"
        "Treat the embedded skill variant and controlled fixture as the complete input and return sanitized evidence only.\n"
        f"Variant: {variant['label']}\n"
        f"Skill query: {variant['query']}\n"
        f"Package id: {variant['package_id']}\n"
        f"Package digest: {variant['package_digest']}\n"
        f"Skill source digest: {skill_digest}\n"
        f"Fixture digest: {fixture['digest']}\n"
        f"\n--- BEGIN VARIANT SKILL {skill_path} ---\n{skill_text}\n--- END VARIANT SKILL ---\n"
        f"\n--- BEGIN FIXTURE {fixture_path} ---\n{fixture_text}\n--- END FIXTURE ---\n"
        "Do not include secrets or claim work outside these inputs."
    )


def _build_ab_plan_receipt(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    skill_a_identity: dict[str, str] | None,
    skill_b_identity: dict[str, str] | None,
    execution_profile_id: str = "codex-read-only",
    judge_profile_id: str = "oss-local",
    execution_lane: str = "all",
    evidence_root: str = DEFAULT_EVIDENCE_ROOT,
    preflight_probe: PreflightProbe | None = None,
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
    blockers += [] if execution_lane in {"all", "oss-local"} else ["execution_lane_invalid"]
    evidence_root_label, evidence_blocker = _planned_evidence_root(repo_root, evidence_root)
    blockers += [evidence_blocker] if evidence_blocker else []
    experiment_id, runtime_profile_gates = _planned_commands(
        repo_root,
        preview,
        blockers=blockers,
        evidence_root_label=evidence_root_label,
        execution_profile_id=execution_profile_id,
        judge_profile_id=judge_profile_id,
        execution_lane=execution_lane,
        preflight_probe=preflight_probe,
    )
    status, command_plan = _plan_status(blockers, runtime_profile_gates)
    return _plan_payload(preview, status, blockers, evidence_root_label, experiment_id, command_plan, runtime_profile_gates, execution_lane)


def build_ab_plan_receipt(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
    """Build a canonical plan while keeping the public call surface narrow."""
    return _build_ab_plan_receipt(repo_root, **kwargs)


def _plan_status(
    blockers: list[str], runtime_profile_gates: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    blockers.extend(_runtime_preflight_blockers(runtime_profile_gates))
    status = "blocked" if blockers else "planned"
    command_plan = (
        runtime_profile_gates[0]["command_plan"]
        if status == "planned" and runtime_profile_gates
        else []
    )
    return status, command_plan


def _runtime_preflight_blockers(runtime_profile_gates: list[dict[str, Any]]) -> list[str]:
    return [
        f"{gate['lane']}:{item['blocker_class']}"
        for gate in runtime_profile_gates
        for item in gate["preflight"]["admission"]["blockers"]
    ]


def _preview_receipt(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
    return build_ab_preview_receipt(repo_root, **kwargs)


def _planned_commands(
    repo_root: Path,
    preview: dict[str, Any],
    *,
    blockers: list[str],
    evidence_root_label: str | None,
    execution_profile_id: str,
    judge_profile_id: str,
    execution_lane: str,
    preflight_probe: PreflightProbe | None,
) -> tuple[str | None, list[dict[str, Any]]]:
    if blockers or evidence_root_label is None:
        return _experiment_id_from_seed("\n".join(blockers or ["evidence_root_unavailable"])), []
    experiment_id = _experiment_id(preview, execution_profile_id, judge_profile_id)
    gates = []
    profile_ids = ("oss-local", "oss-cloud") if execution_lane == "all" else ("oss-local",)
    for order, profile_id in enumerate(profile_ids, start=1):
        profile = select_judge_profile(profile_id)
        codex_profile = str(profile["codex_profile"])
        preflight = build_lane_preflight(profile, preflight_probe)
        gates.append({
            "order": order,
            "lane": profile_id,
            "codex_profile": codex_profile,
            "judge_profile": profile,
            "status": "planned" if preflight["admission"]["status"] == "pass" else "blocked",
            "blockers": preflight["admission"]["blockers"],
            "preflight": preflight,
            "command_plan": [],
        })
    if all(gate["preflight"]["admission"]["status"] == "pass" for gate in gates):
        _populate_variant_commands(repo_root, preview, evidence_root_label, experiment_id, gates, blockers)
    return experiment_id, gates


def _populate_variant_commands(
    repo_root: Path,
    preview: dict[str, Any],
    evidence_root_label: str,
    experiment_id: str,
    gates: list[dict[str, Any]],
    blockers: list[str],
) -> None:
    for gate in gates:
        try:
            gate["command_plan"] = _variant_commands(
                repo_root, preview, evidence_root_label, experiment_id, gate["codex_profile"],
            )
        except ValueError as exc:
            blockers.append(f"variant_prompt_invalid:{exc}")


def _variant_commands(
    repo_root: Path,
    preview: dict[str, Any], evidence_root_label: str, experiment_id: str, codex_profile: str,
) -> list[dict[str, Any]]:
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
            prompt=_variant_prompt(repo_root, preview["skill_a"], preview["fixture"]),
            codex_profile=codex_profile,
        ),
        _variant_command(
            label="B",
            repo_root_label=".",
            sandbox_mode=sandbox_mode,
            approval_policy=approval_policy,
            evidence_root=evidence_root_label,
            experiment_id=experiment_id,
            prompt=_variant_prompt(repo_root, preview["skill_b"], preview["fixture"]),
            codex_profile=codex_profile,
        ),
    ]


def _plan_payload(
    preview: dict[str, Any],
    status: str,
    blockers: list[str],
    evidence_root_label: str | None,
    experiment_id: str | None,
    command_plan: list[dict[str, Any]],
    runtime_profile_gates: list[dict[str, Any]],
    execution_lane: str,
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
        "execution_lane": execution_lane,
        "codex_profile": "oss-local" if runtime_profile_gates else None,
        "runtime_profile_gates": runtime_profile_gates,
        "evidence_root": evidence_root_label,
        "experiment_id": experiment_id,
        "command_variant_labels": [plan["variant_label"] for plan in command_plan],
        "command_plan": command_plan,
        "secret_boundary": preview["secret_boundary"],
        "execution_boundary": "codex_exec_sandbox",
        "judge_boundary": "post_run_sanitized_evidence_only",
        "mutation_performed": False,
        "network_accessed": _preflight_network_accessed(runtime_profile_gates),
        "provider_invoked": False,
        "codex_exec_invoked": False,
        "blockers": blockers,
        "acceptance_trace": preview["acceptance_trace"],
        "agent_summary": "A/B eval execution plan is ready; Codex has not been invoked." if status == "planned" else f"A/B eval execution plan is blocked: {', '.join(blockers)}.",
    }


def _preflight_network_accessed(runtime_profile_gates: list[dict[str, Any]]) -> bool:
    return any(
        gate.get("preflight", {}).get("model_catalog", {}).get("network_accessed") is True
        for gate in runtime_profile_gates
    )
