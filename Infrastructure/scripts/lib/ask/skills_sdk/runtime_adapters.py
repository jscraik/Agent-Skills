from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import runtime_failure_payload, skills_validation_command


ResolveSkillHandle = Callable[..., dict[str, Any]]
CheckCommandHandles = Callable[..., dict[str, Any]]
SUPPORTED_RUNTIME_TARGETS = {"any", "codex", "agents"}


def normalize_runtime_target(runtime_target: str) -> str:
    return runtime_target.strip().lower()


def invalid_runtime_target_failure(handle: str, runtime_target: str) -> dict[str, Any]:
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


def build_command_handle_proof(
    *,
    repo_root: Path,
    handle: str,
    runtime_target: str,
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
