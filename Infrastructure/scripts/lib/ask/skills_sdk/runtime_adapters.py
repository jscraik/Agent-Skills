from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import runtime_failure_payload, skills_validation_command


ResolveSkillHandle = Callable[..., dict[str, Any]]
CheckCommandHandles = Callable[..., dict[str, Any]]
SUPPORTED_RUNTIME_TARGETS = {"any", "codex", "agents"}
EVIDENCE_RUNTIME_TARGETS = {"codex", "agents"}
RUNTIME_REACHABILITY_FAILURES = {
    "user_runtime_ready",
    "codex_user_runtime_ready",
    "agents_user_runtime_ready",
    "codex_user_link",
    "agents_user_link",
    "codex_user_command_handle_exists",
    "agents_user_command_handle_exists",
}


def normalize_runtime_target(runtime_target: object) -> str:
    return str(runtime_target).strip().lower()


def invalid_runtime_target_failure(handle: str, runtime_target: object) -> dict[str, Any]:
    normalized_target = normalize_runtime_target(runtime_target)
    safe_handle = handle.strip().lstrip("$") or handle
    recovery_guidance = "Use --runtime-target any, --runtime-target codex, or --runtime-target agents."
    return runtime_failure_payload(
        command="skills proof",
        error_code="ERR_VALIDATION",
        failed_check_id="runtime_target",
        path="runtime_target",
        message=f"Invalid runtime target '{normalized_target}'.",
        recovery_guidance=recovery_guidance,
        validation_commands=[
            skills_validation_command("proof", safe_handle, "--runtime-target", "any"),
        ],
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _runtime_status_for_proof(proof: dict[str, Any]) -> str:
    if proof.get("status") == "pass":
        return "implemented_enforced"
    runtime_failure = proof.get("runtime_failure")
    failed_check_id = (
        str(runtime_failure.get("failed_check_id"))
        if isinstance(runtime_failure, dict) and runtime_failure.get("failed_check_id")
        else "runtime_reachability"
    )
    return "blocked_runtime" if failed_check_id in RUNTIME_REACHABILITY_FAILURES else "stale_or_drifted"


def _claim_status_for_runtime(runtime_status: str) -> str:
    return "pass" if runtime_status == "implemented_enforced" else "blocked"


def _runtime_display_name(runtime_target: str) -> str:
    return "Codex" if runtime_target == "codex" else "Agents"


def _runtime_evidence_context(
    *,
    repo_root: Path,
    proof: dict[str, Any],
    actor_type: str,
) -> dict[str, Any]:
    handle = str(proof.get("handle") or "unknown").strip().lstrip("$") or "unknown"
    runtime_target = str(proof.get("runtime_target") or "")
    resolution = proof.get("resolution") if isinstance(proof.get("resolution"), dict) else {}
    source_path = str(resolution.get("source_path") or repo_root / ".agents" / "skills" / handle / "SKILL.md")
    source = Path(source_path)
    canonical_source_path = _repo_relative(repo_root, source if source.is_absolute() else repo_root / source_path)
    evidence_dir = repo_root / ".harness" / "evidence" / "runtime-proof" / handle / runtime_target
    runtime_status = _runtime_status_for_proof(proof)
    runtime_failure = proof.get("runtime_failure") if isinstance(proof.get("runtime_failure"), dict) else {}
    return {
        "repo_root": repo_root,
        "handle": handle,
        "runtime_target": runtime_target,
        "created_at": _utc_now(),
        "evidence_dir": evidence_dir,
        "card_path": evidence_dir / "runtime-card.json",
        "receipt_path": evidence_dir / "evidence-receipt.json",
        "artifact_path": evidence_dir / "artifact-record.json",
        "probe_path": evidence_dir / "probe.json",
        "command": skills_validation_command("proof", handle, "--runtime-target", runtime_target),
        "runtime_status": runtime_status,
        "claim_status": _claim_status_for_runtime(runtime_status),
        "runtime_failure": runtime_failure,
        "failed_check_id": str(runtime_failure.get("failed_check_id") or "runtime_reachability"),
        "blocker": str(
            runtime_failure.get("message")
            or f"{_runtime_display_name(runtime_target)} runtime proof passed."
        ),
        "exit_code": 0 if proof.get("status") == "pass" else 2,
        "source_paths": [
            canonical_source_path,
            "Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py",
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
        ],
        "actor_type": actor_type,
    }


def _artifact_record(
    context: dict[str, Any],
    *,
    artifact_id: str,
    artifact_type: str,
    path: str,
    consumer_contract: str,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "path": path,
        "source_identity": {"source_paths": context["source_paths"]},
        "workspace_root": str(context["repo_root"].resolve()),
        "actor_type": context["actor_type"],
        "mutation_scope": "evidence_write",
        "visibility_status": "user_observable",
        "generated_by": context["command"],
        "validation_status": context["claim_status"],
        "consumer_contract": consumer_contract,
    }


def _probe_payload(context: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "command-handle-runtime-probe.v1",
        "handle": context["handle"],
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "observed_at": context["created_at"],
        "command": context["command"],
        "exit_code": context["exit_code"],
        "proof": proof,
    }


def _receipt_payload(context: dict[str, Any], relative_card_path: str, relative_probe_path: str) -> dict[str, Any]:
    receipt = {
        "receipt_id": f"runtime-proof-{context['handle']}-{context['runtime_target']}",
        "claim": (
            "$"
            + context["handle"]
            + f" is reachable in the {_runtime_display_name(context['runtime_target'])} runtime."
        ),
        "claim_status": context["claim_status"],
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "evidence_type": "command",
        "command": context["command"],
        "exit_code": context["exit_code"],
        "probe_command": context["command"],
        "probe_exit_code": context["exit_code"],
        "probe_artifact_path": relative_probe_path,
        "blocker_class": context["runtime_status"] if context["runtime_status"] != "implemented_enforced" else "none",
        "artifact_path": relative_card_path,
        "source_paths": context["source_paths"],
        "verifier": "ask.skills.proof",
        "observed_at": context["created_at"],
    }
    if context["claim_status"] == "blocked":
        receipt["blocker"] = context["blocker"]
    return receipt


def _recovery_plan(context: dict[str, Any]) -> dict[str, Any]:
    recovery_reason = (
        str(context["runtime_failure"].get("recovery_guidance"))
        if context["claim_status"] == "blocked"
        else (
            "$"
            + context["handle"]
            + f" is reachable in the {_runtime_display_name(context['runtime_target'])} runtime."
        )
    )
    return {
        "recovery_status": context["runtime_status"],
        "reason": recovery_reason,
        "next_commands": [
            {
                "command": context["command"],
                "preconditions": [
                    f"{_runtime_display_name(context['runtime_target'])} skill runtime points at "
                    "the workspace command-handle projection."
                ],
                "permission_profile": {
                    "filesystem": "read workspace and user runtime skill links",
                    "network": "not required",
                },
                "expected_outcome": (
                    "RuntimeCard is updated with implemented_enforced proof or typed blocked_runtime evidence."
                ),
            }
        ],
        "preconditions": [
            "Run workspace and user skill sync if the runtime link or command handle is absent."
        ],
        "permission_profile": {
            "filesystem": "workspace evidence write and user runtime link read",
            "network": "not required",
        },
        "expected_outcome": "Operator can rerun the proof command and inspect schema-valid runtime evidence.",
    }


def _runtime_card_payload(
    context: dict[str, Any],
    *,
    proof: dict[str, Any],
    artifact_record: dict[str, Any],
    probe_record: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    runtime_session = {
        "session_id": f"runtime-proof-{context['handle']}-{context['runtime_target']}",
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "created_at": context["created_at"],
        "workspace_root": str(context["repo_root"].resolve()),
        "actor_type": context["actor_type"],
        "visibility_status": "user_observable",
    }
    if context["claim_status"] == "blocked":
        runtime_session["unavailable_reason"] = context["blocker"]
    return {
        "schema_version": 1,
        "card_id": f"runtime-card-{context['handle']}-{context['runtime_target']}",
        "created_at": context["created_at"],
        "runtime_target": context["runtime_target"],
        "runtime_status": context["runtime_status"],
        "skill_handle": context["handle"],
        "command_handle": "$" + context["handle"],
        "runtime_session": runtime_session,
        "thread_runs": [],
        "turn_events": [],
        "artifacts": [artifact_record, probe_record],
        "evidence_receipts": [receipt],
        "verifier_results": [
            {
                "verifier": "ask.skills.proof",
                "status": proof.get("status"),
                "runtime_target": context["runtime_target"],
                "required_gates": proof.get("gate_policy", {}).get("required", []),
                "gates": proof.get("gates", {}),
                "failed_check_id": context["failed_check_id"] if context["claim_status"] == "blocked" else None,
            }
        ],
        "permission_profile": {
            "filesystem": "workspace evidence write",
            "network": "not required",
        },
        "workspace_root": str(context["repo_root"].resolve()),
        "actor_type": context["actor_type"],
        "mutation_scope": "evidence_write",
        "visibility_status": "user_observable",
        "limitations": [
            {
                "class": "manual_session_gate",
                "message": (
                    "Runtime reachability proves command-handle wiring; it does not execute an interactive "
                    "Codex session."
                ),
            }
        ],
        "recovery_plan": _recovery_plan(context),
    }


def emit_command_handle_runtime_evidence(
    *,
    repo_root: Path,
    proof: dict[str, Any],
    actor_type: str = "agent",
) -> dict[str, Any]:
    """Write schema-valid runtime proof artifacts for an explicit runtime target."""
    runtime_target = str(proof.get("runtime_target") or "")
    if runtime_target not in EVIDENCE_RUNTIME_TARGETS:
        return {
            "status": "skipped",
            "reason": "runtime evidence is only emitted for explicit codex or agents targets",
        }

    context = _runtime_evidence_context(repo_root=repo_root, proof=proof, actor_type=actor_type)
    relative_card_path = _repo_relative(repo_root, context["card_path"])
    relative_receipt_path = _repo_relative(repo_root, context["receipt_path"])
    relative_artifact_path = _repo_relative(repo_root, context["artifact_path"])
    relative_probe_path = _repo_relative(repo_root, context["probe_path"])

    probe = _probe_payload(context, proof)
    receipt = _receipt_payload(context, relative_card_path, relative_probe_path)
    card_record = _artifact_record(
        context,
        artifact_id=f"runtime-card-{context['handle']}-{context['runtime_target']}",
        artifact_type="runtime_card",
        path=relative_card_path,
        consumer_contract="RuntimeCard v1 consumed by validate_runtime_cards.py and governed closeout.",
    )
    probe_record = _artifact_record(
        context,
        artifact_id=f"runtime-probe-{context['handle']}-{context['runtime_target']}",
        artifact_type="verifier_output",
        path=relative_probe_path,
        consumer_contract="Probe JSON records the raw command-handle proof used by the RuntimeCard.",
    )
    card = _runtime_card_payload(
        context,
        proof=proof,
        artifact_record=card_record,
        probe_record=probe_record,
        receipt=receipt,
    )

    _write_json(context["probe_path"], probe)
    _write_json(context["receipt_path"], receipt)
    _write_json(context["artifact_path"], card_record)
    _write_json(context["card_path"], card)

    return {
        "status": context["runtime_status"],
        "evidence_dir": _repo_relative(repo_root, context["evidence_dir"]),
        "runtime_card_path": relative_card_path,
        "evidence_receipt_path": relative_receipt_path,
        "artifact_record_path": relative_artifact_path,
        "probe_artifact_path": relative_probe_path,
        "validation_command": (
            "python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py "
            f"{relative_card_path} --require-shared-workspace --workspace-root {repo_root.resolve()} --json"
        ),
    }


def build_command_handle_proof(
    *,
    repo_root: Path,
    handle: str,
    runtime_target: object,
    resolve_skill_handle_fn: ResolveSkillHandle,
    check_command_handles_fn: CheckCommandHandles,
    home_path: Path,
) -> dict[str, Any]:
    """Build the runtime reachability proof for a generated skill command handle."""
    runtime_target = normalize_runtime_target(runtime_target)
    normalized = handle.strip().lstrip("$") or handle
    if runtime_target not in SUPPORTED_RUNTIME_TARGETS:
        runtime_failure = invalid_runtime_target_failure(normalized, runtime_target)
        return {
            "schema_version": "command-handle-proof.v2",
            "handle": normalized,
            "runtime_target": runtime_target,
            "status": "fail",
            "validation_commands": runtime_failure["validation_commands"],
            "gates": {
                "runtime_target": False,
            },
            "gate_policy": {
                "required": ["runtime_target"],
                "runtime_target": runtime_target,
                "required_semantics": runtime_failure["recovery_guidance"],
                "supporting_runtime_diagnostics": [],
            },
            "available_runtimes": [],
            "runtime_satisfied_by": None,
            "resolution": None,
            "command_handle_check": None,
            "workspace_runtime": None,
            "user_runtime_links": None,
            "user_runtime_command_handles": None,
            "runtime_failure": runtime_failure,
        }
    resolution = resolve_skill_handle_fn(handle, repo_root_path=repo_root)
    normalized = str(resolution.get("handle", normalized))
    handle_check = check_command_handles_fn(repo_root_path=repo_root)
    workspace_handle = repo_root / str(resolution.get("command_handle_path", ""))
    user_codex_handle = home_path / ".codex" / "skills" / str(normalized) / "SKILL.md"
    user_agents_handle = home_path / ".agents" / "skills" / str(normalized) / "SKILL.md"
    codex_skills = home_path / ".codex" / "skills"
    agents_skills = home_path / ".agents" / "skills"
    expected_runtime = repo_root / ".agents" / "skills"

    handle_violations = [
        violation
        for violation in handle_check.get("violations", [])
        if violation.get("handle") == normalized
    ]
    handle_check_ok = handle_check.get("status") == "pass" or not handle_violations

    def link_payload(path: Path) -> dict[str, object]:
        payload: dict[str, object] = {
            "path": str(path),
            "exists": path.exists(),
            "is_symlink": path.is_symlink(),
        }
        if path.is_symlink():
            payload["target"] = str(path.resolve())
            payload["points_to_workspace_runtime"] = path.resolve() == expected_runtime.resolve()
        else:
            payload["target"] = None
            payload["points_to_workspace_runtime"] = False
        return payload

    gates = {
        "resolver": resolution.get("status") == "ok",
        "generated_command_handle_check": handle_check_ok,
        "workspace_command_handle_exists": workspace_handle.is_file(),
        "codex_user_link": codex_skills.is_symlink() and codex_skills.resolve() == expected_runtime.resolve(),
        "agents_user_link": agents_skills.is_symlink() and agents_skills.resolve() == expected_runtime.resolve(),
        "codex_user_command_handle_exists": user_codex_handle.is_file(),
        "agents_user_command_handle_exists": user_agents_handle.is_file(),
    }
    core_gates = (
        gates["resolver"],
        gates["generated_command_handle_check"],
        gates["workspace_command_handle_exists"],
    )
    codex_runtime_ready = (
        gates["codex_user_link"] and gates["codex_user_command_handle_exists"]
    )
    agents_runtime_ready = (
        gates["agents_user_link"] and gates["agents_user_command_handle_exists"]
    )
    user_runtime_ready = codex_runtime_ready or agents_runtime_ready
    gates["codex_user_runtime_ready"] = codex_runtime_ready
    gates["agents_user_runtime_ready"] = agents_runtime_ready
    gates["user_runtime_ready"] = user_runtime_ready
    required_runtime_gate = {
        "any": "user_runtime_ready",
        "codex": "codex_user_runtime_ready",
        "agents": "agents_user_runtime_ready",
    }[runtime_target]
    required_runtime_ready = bool(gates[required_runtime_gate])
    validation_args = [str(normalized)]
    if runtime_target != "any":
        validation_args.extend(["--runtime-target", runtime_target])
    proof = {
        "schema_version": "command-handle-proof.v2",
        "handle": normalized,
        "runtime_target": runtime_target,
        "status": "pass" if all(core_gates) and required_runtime_ready else "fail",
        "validation_commands": [
            skills_validation_command("proof", *validation_args),
        ],
        "gates": gates,
        "gate_policy": {
            "required": [
                "resolver",
                "generated_command_handle_check",
                "workspace_command_handle_exists",
                required_runtime_gate,
            ],
            "runtime_target": runtime_target,
            "required_semantics": (
                "user_runtime_ready accepts either supported user runtime link."
                if runtime_target == "any"
                else f"{required_runtime_gate} must be true for runtime_target={runtime_target}."
            ),
            "supporting_runtime_diagnostics": [
                "codex_user_link",
                "codex_user_command_handle_exists",
                "codex_user_runtime_ready",
                "agents_user_link",
                "agents_user_command_handle_exists",
                "agents_user_runtime_ready",
            ],
        },
        "available_runtimes": [
            runtime_name
            for runtime_name, ready in (
                ("codex_user_runtime", codex_runtime_ready),
                ("agents_user_runtime", agents_runtime_ready),
            )
            if ready
        ],
        "runtime_satisfied_by": (
            "codex_user_runtime"
            if runtime_target in {"any", "codex"} and codex_runtime_ready
            else "agents_user_runtime"
            if runtime_target in {"any", "agents"} and agents_runtime_ready
            else None
        ),
        "resolution": resolution,
        "command_handle_check": {
            key: value
            for key, value in handle_check.items()
            if key != "violations" or value
        },
        "workspace_runtime": {
            "path": str(expected_runtime),
            "command_handle_path": str(workspace_handle),
            "command_handle_exists": workspace_handle.is_file(),
        },
        "user_runtime_links": {
            "codex_skills": link_payload(codex_skills),
            "agents_skills": link_payload(agents_skills),
        },
        "user_runtime_command_handles": {
            "codex_handle": str(user_codex_handle),
            "codex_handle_exists": user_codex_handle.is_file(),
            "agents_handle": str(user_agents_handle),
            "agents_handle_exists": user_agents_handle.is_file(),
        },
    }
    if proof["status"] != "pass":
        failed_check_id = next(
            (
                check_id
                for check_id in proof["gate_policy"]["required"]
                if not gates.get(check_id)
            ),
            "runtime_reachability",
        )
        recovery_guidance = (
            "Run ./bin/ask skills sync --scope workspace --projection rooted, "
            "then ./bin/ask skills sync --scope user --projection rooted, and rerun proof."
        )
        proof["runtime_failure"] = runtime_failure_payload(
            command="skills proof",
            error_code="ERR_VALIDATION",
            failed_check_id=str(failed_check_id),
            path=f"gates.{failed_check_id}",
            message=f"Command handle proof failed for '{normalized}'.",
            recovery_guidance=recovery_guidance,
            validation_commands=proof["validation_commands"],
        )
    if required_runtime_ready:
        runtime = proof["runtime_satisfied_by"]
        operator_action = (
            "Open or reload a Codex session and verify the handle appears in the picker or can be invoked as a $ handle."
            if runtime == "codex_user_runtime"
            else "Open or reload the Agents runtime and verify the handle is available there."
        )
        proof["live_runtime_invocation"] = {
            "status": "manual_session_gate",
            "runtime_satisfied_by": runtime,
            "operator_action": operator_action,
        }
    return proof
