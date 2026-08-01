from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any, Callable

from ask.skills_sdk.ab_contracts import _codex_profile_from_argv, _validate_execution_argv
from ask.skills_sdk.ab_transport_contracts import (
    actual_opaque_env_path,
    approved_op_binary,
    approved_op_env_invocation,
    is_actual_opaque_env_reference,
    is_approved_op_binary,
    opaque_env_identity_digest,
)
from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt
from ask.skills_sdk.typed_contracts import validate_ab_plan_receipt


AB_RUN_SCHEMA_VERSION = "skills-sdk.ab-run-receipt.v1"
AB_RUN_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/ab-run-receipt.v1.schema.json"
_SEMANTIC_OUTPUT_EXCERPT_BYTES = 4096
_PROVIDER_EVENT_TYPES = frozenset({"response.completed", "agent_message.completed"})
_PLAN_BLOCKED_NOT_RUN_REASON = "execution_packet_suppressed_by_blocked_plan"


@dataclass(frozen=True)
class CodexRunResult:
    exit_code: int
    stdout: str
    stderr: str
    executed_argv: list[str] | None = None


@dataclass(frozen=True)
class VariantPaths:
    prompt: Path
    stdout: Path
    stderr: Path
    output: Path


CodexRunner = Callable[[list[str], str, Path, int], CodexRunResult]
_CODEX_ENV_ALLOWLIST = frozenset(
    {
        "CODEX_CONFIG_HOME",
        "CODEX_HOME",
        "HOME",
        "LANG",
        "LC_ALL",
        "LOGNAME",
        "PATH",
        "SHELL",
        "TERM",
        "TMPDIR",
        "USER",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
    }
)
_SECRET_ENV_MARKERS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL", "COOKIE")


def _digest_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _digest_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _codex_runner_env(source: dict[str, str] | None = None) -> dict[str, str]:
    env = source if source is not None else os.environ
    return {
        name: value
        for name, value in env.items()
        if name in _CODEX_ENV_ALLOWLIST and not any(marker in name.upper() for marker in _SECRET_ENV_MARKERS)
    }


def _repo_path(repo_root: Path, repo_relative_path: str) -> Path:
    raw_path = Path(repo_relative_path)
    if raw_path.is_absolute():
        raise ValueError("A/B evidence paths must be repo-relative")
    resolved = (repo_root / raw_path).resolve()
    resolved.relative_to(repo_root.resolve())
    return resolved


def _default_codex_runner(
    command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int,
    *, expected_auth_stream_identity: str | None = None,
) -> CodexRunResult:
    if _codex_profile_from_argv(command_argv) == "oss-cloud":
        default_stream = actual_opaque_env_path()
        env_file = os.environ.get(
            "SKILLS_SDK_OSS_CLOUD_ENV_FILE", str(default_stream) if default_stream else "",
        )
        with approved_op_env_invocation(
            env_file, expected_identity_digest=expected_auth_stream_identity,
        ) as invocation:
            proc = subprocess.run(
                invocation.runtime_argv(command_argv),
                cwd=repo_root,
                input=prompt,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout_seconds,
                env=_codex_runner_env(),
                pass_fds=invocation.pass_fds,
            )
            execution_argv = invocation.receipt_argv(command_argv)
    else:
        execution_argv = _execution_argv_for_run(command_argv)
        proc = subprocess.run(
            execution_argv,
            cwd=repo_root,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            env=_codex_runner_env(),
        )
    return CodexRunResult(
        exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr, executed_argv=execution_argv,
    )


def _execution_argv_for_run(command_argv: list[str]) -> list[str]:
    profile = _codex_profile_from_argv(command_argv)
    if profile == "oss-local":
        return list(command_argv)
    default_stream = actual_opaque_env_path()
    env_file = os.environ.get("SKILLS_SDK_OSS_CLOUD_ENV_FILE", str(default_stream) if default_stream else "")
    if not is_actual_opaque_env_reference(env_file):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    op_binary = approved_op_binary()
    if op_binary is None:
        raise ValueError("cloud execution requires an approved 1Password CLI binary")
    return [op_binary, "run", "--env-file", env_file, "--", *command_argv]


def _variant_prompt(variant: dict[str, str], fixture: dict[str, Any]) -> str:
    return (
        f"Run Skills SDK A/B variant {variant['label']} against fixture {fixture['path']}.\n"
        f"Skill query: {variant['query']}\n"
        f"Package id: {variant['package_id']}\n"
        f"Package digest: {variant['package_digest']}\n"
        f"Fixture digest: {fixture['digest']}\n"
        "Return sanitized evidence only. Do not include secrets."
    )


def _execute_variant(
    repo_root: Path,
    *,
    command_plan: dict[str, Any],
    prompt: str,
    timeout_seconds: int,
    runner: CodexRunner,
) -> dict[str, Any]:
    variant_label = command_plan["variant_label"]
    paths = _variant_paths(repo_root, command_plan)
    _prepare_variant_paths(paths, prompt)
    _clear_stale_variant_output(paths)
    result, run_error, codex_exec_started = _run_variant(command_plan, prompt, repo_root, timeout_seconds, runner)
    _write_runner_outputs(paths, result)
    provider_invoked = _provider_event_observed(result.stdout)
    output_digest = _digest_file(paths.output)
    execution_argv = result.executed_argv
    blockers = _variant_blockers(
        variant_label, run_error, result.exit_code, output_digest, provider_invoked, execution_argv,
    )
    return _variant_result(
        repo_root, command_plan, paths, result, execution_argv, output_digest,
        blockers, provider_invoked, codex_exec_started,
    )


def _variant_result(
    repo_root: Path, command_plan: dict[str, Any], paths: VariantPaths, result: CodexRunResult,
    execution_argv: list[str] | None, output_digest: str | None, blockers: list[str],
    provider_invoked: bool, codex_exec_started: bool,
) -> dict[str, Any]:
    semantic_excerpt = _semantic_output_excerpt(paths.output)
    declared_profile = _codex_profile_from_argv(command_plan["command_argv"])
    recorded_execution_argv = None
    executed_profile = None
    if execution_argv is not None:
        try:
            recorded_execution_argv, executed_profile = _validated_recorded_execution_argv(
                execution_argv, command_plan["command_argv"], declared_profile,
            )
        except ValueError:
            blockers.append(f"{command_plan['variant_label']}:execution_argv_invalid")
            blockers.append(f"{command_plan['variant_label']}:executed_argv_missing")
    return {
        "variant_label": command_plan["variant_label"],
        "codex_profile": executed_profile,
        "status": "pass" if not blockers else "blocked",
        "exit_code": result.exit_code,
        "command_argv": command_plan["command_argv"],
        "execution_argv": recorded_execution_argv,
        "sandbox_mode": command_plan["sandbox_mode"],
        "prompt_stdin_path": command_plan["runner_prompt_input_path"],
        "prompt_stdin_digest": _digest_file(paths.prompt),
        "runner_stdout_capture_path": command_plan["runner_stdout_capture_path"],
        "runner_stdout_digest": _digest_file(paths.stdout),
        "runner_stderr_capture_path": paths.stderr.relative_to(repo_root).as_posix(),
        "runner_stderr_digest": _digest_file(paths.stderr),
        "output_last_message_path": command_plan["output_last_message_path"],
        "output_last_message_digest": output_digest,
        "semantic_output_excerpt": semantic_excerpt,
        "codex_exec_started": codex_exec_started,
        "provider_invoked": provider_invoked,
        "network_accessed": False,
        "blockers": blockers,
    }


def _validated_recorded_execution_argv(
    execution_argv: list[str], command_argv: list[str], declared_profile: str,
) -> tuple[list[str], str]:
    if declared_profile == "oss-cloud":
        if len(execution_argv) < 5:
            raise ValueError("cloud execution requires the approved op run wrapper")
        if not is_actual_opaque_env_reference(execution_argv[3]):
            raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    recorded = _redact_execution_argv(execution_argv)
    _validate_execution_argv(recorded, command_argv, declared_profile)
    codex_argv = recorded[5:] if declared_profile == "oss-cloud" else recorded
    return recorded, _codex_profile_from_argv(codex_argv)


def _redact_execution_argv(execution_argv: list[str]) -> list[str]:
    redacted = list(execution_argv)
    if (
        len(redacted) >= 5
        and is_approved_op_binary(redacted[0])
        and redacted[1:3] == ["run", "--env-file"]
        and redacted[4] == "--"
    ):
        redacted[3] = "<operator-approved-opaque-env-stream>"
    return redacted


def _variant_paths(repo_root: Path, command_plan: dict[str, Any]) -> VariantPaths:
    stdout_path = _repo_path(repo_root, command_plan["runner_stdout_capture_path"])
    return VariantPaths(
        prompt=_repo_path(repo_root, command_plan["runner_prompt_input_path"]),
        stdout=stdout_path,
        stderr=stdout_path.with_name("codex-stderr.txt"),
        output=_repo_path(repo_root, command_plan["output_last_message_path"]),
    )


def _prepare_variant_paths(paths: VariantPaths, prompt: str) -> None:
    paths.prompt.parent.mkdir(parents=True, exist_ok=True)
    paths.stdout.parent.mkdir(parents=True, exist_ok=True)
    paths.output.parent.mkdir(parents=True, exist_ok=True)
    paths.prompt.write_bytes(prompt.encode("utf-8"))


def _clear_stale_variant_output(paths: VariantPaths) -> None:
    if not paths.output.exists():
        return
    if not paths.output.is_file():
        raise ValueError("A/B output path must be a file")
    paths.output.unlink()


def _run_variant(
    command_plan: dict[str, Any],
    prompt: str,
    repo_root: Path,
    timeout_seconds: int,
    runner: CodexRunner,
) -> tuple[CodexRunResult, str | None, bool]:
    try:
        return runner(command_plan["command_argv"], prompt, repo_root, timeout_seconds), None, True
    except subprocess.TimeoutExpired as exc:
        return (
            CodexRunResult(
                exit_code=124,
                stdout=_timeout_output_text(exc.stdout),
                stderr=_timeout_output_text(exc.stderr),
            ),
            "codex_exec_timeout",
            True,
        )
    except OSError as exc:
        return CodexRunResult(
            exit_code=127, stdout="", stderr=str(exc),
        ), "codex_exec_unavailable", False
    except ValueError as exc:
        return CodexRunResult(
            exit_code=2, stdout="", stderr=str(exc),
        ), "codex_exec_preflight_blocked", False


def _timeout_output_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _write_runner_outputs(paths: VariantPaths, result: CodexRunResult) -> None:
    with paths.stdout.open("w", encoding="utf-8") as stdout_handle:
        stdout_handle.write(result.stdout)
    with paths.stderr.open("w", encoding="utf-8") as stderr_handle:
        stderr_handle.write(result.stderr)


def _provider_event_observed(stdout: str) -> bool:
    """Return true only when Codex JSONL contains an observable model response."""
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type", event.get("event"))
        if event_type in _PROVIDER_EVENT_TYPES:
            return True
        item = event.get("item")
        if event_type == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            return True
    return False


def _semantic_output_excerpt(path: Path) -> str | None:
    if not path.exists() or not path.is_file() or path.is_symlink():
        return None
    try:
        data = path.read_bytes()[: _SEMANTIC_OUTPUT_EXCERPT_BYTES + 1]
    except OSError:
        return None
    text = data[:_SEMANTIC_OUTPUT_EXCERPT_BYTES].decode("utf-8", errors="replace")
    compact = text.replace("\x00", "").strip()
    return compact or None


def _variant_blockers(
    variant_label: str, run_error: str | None, exit_code: int, output_digest: str | None,
    provider_invoked: bool, execution_argv: list[str] | None,
) -> list[str]:
    blockers: list[str] = []
    if run_error:
        blockers.append(f"{variant_label}:{run_error}")
    if exit_code != 0:
        blockers.append(f"{variant_label}:codex_exec_exit_{exit_code}")
    if output_digest is None:
        blockers.append(f"{variant_label}:output_last_message_missing")
    if not provider_invoked:
        blockers.append(f"{variant_label}:provider_event_missing")
    if execution_argv is None:
        blockers.append(f"{variant_label}:executed_argv_missing")
    return blockers


def _build_ab_run_receipt(
    repo_root: Path,
    *, skill_a: str, skill_b: str, fixture: str,
    skill_a_identity: dict[str, str] | None,
    skill_b_identity: dict[str, str] | None,
    execution_profile_id: str = "codex-read-only",
    judge_profile_id: str = "oss-local",
    execution_lane: str = "all",
    evidence_root: str = ".harness/artifacts/sdk-ab-evals",
    timeout_seconds: int = 1800,
    runner: CodexRunner | None = None,
    preflight_probe: Any = None,
) -> dict[str, Any]:
    plan = _validated_v1_plan(
        _build_plan(
            repo_root,
            skill_a=skill_a,
            skill_b=skill_b,
            fixture=fixture,
            skill_a_identity=skill_a_identity,
            skill_b_identity=skill_b_identity,
            execution_profile_id=execution_profile_id,
            judge_profile_id=judge_profile_id,
            execution_lane=execution_lane,
            evidence_root=evidence_root,
            preflight_probe=preflight_probe,
        )
    )
    blockers = list(plan["blockers"])
    runtime_profile_gates, variant_results = _execute_runtime_profile_gates(
        repo_root, plan, timeout_seconds, runner or _default_codex_runner,
    )
    blockers.extend(_execution_blockers(runtime_profile_gates, variant_results))
    status = "completed" if not blockers else "blocked"
    side_effects = _run_side_effects(plan, variant_results)
    receipt_variant_results = runtime_profile_gates[0]["variant_results"] if runtime_profile_gates else []
    return _run_payload(plan, status, blockers, receipt_variant_results, runtime_profile_gates, side_effects["codex_exec_started"], side_effects["provider_invoked"], side_effects["network_accessed"], timeout_seconds)


def build_ab_run_receipt(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
    """Build a canonical run receipt while keeping the public call surface narrow."""
    return _build_ab_run_receipt(repo_root, **kwargs)


def _execution_blockers(
    runtime_profile_gates: list[dict[str, Any]], variant_results: list[dict[str, Any]],
) -> list[str]:
    gate_blockers = [
        item if isinstance(item, str) else f"{gate['lane']}:{item['blocker_class']}"
        for gate in runtime_profile_gates
        for item in gate["blockers"]
    ]
    return gate_blockers + [item for result in variant_results for item in result["blockers"]]


def _run_side_effects(plan: dict[str, Any], variant_results: list[dict[str, Any]]) -> dict[str, bool]:
    preflight_network_accessed = any(
        gate["preflight"]["model_catalog"].get("network_accessed") is True
        for gate in plan["runtime_profile_gates"]
    )
    return {
        "codex_exec_started": any(result.get("codex_exec_started") is True for result in variant_results),
        "provider_invoked": any(result.get("provider_invoked") is True for result in variant_results),
        "network_accessed": preflight_network_accessed or any(
            result.get("network_accessed") is True for result in variant_results
        ),
    }


def _build_plan(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
    return build_ab_plan_receipt(repo_root, **kwargs)


def _validated_v1_plan(plan: dict[str, Any]) -> dict[str, Any]:
    validated = validate_ab_plan_receipt(plan)
    if validated.schema_version != "skills-sdk.ab-plan-receipt.v1":
        raise ValueError("A/B execution requires a canonical v1 plan receipt")
    return validated.model_dump(mode="json")


def _execute_runtime_profile_gates(
    repo_root: Path,
    plan: dict[str, Any],
    timeout: int,
    runner: CodexRunner,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not plan.get("runtime_profile_gates"):
        return [], []
    if plan["status"] == "blocked":
        return [_blocked_plan_gate(gate) for gate in plan["runtime_profile_gates"]], []
    gate_results: list[dict[str, Any]] = []
    all_results: list[dict[str, Any]] = []
    prior_blocked = False
    for gate in plan["runtime_profile_gates"]:
        if prior_blocked:
            gate_results.append(_not_run_gate(gate))
            continue
        if gate["preflight"]["admission"]["status"] != "pass":
            gate_results.append(_preflight_blocked_gate(gate))
            prior_blocked = True
            continue
        results = _execute_runtime_gate(repo_root, plan, gate, timeout, runner)
        gate_blockers = [blocker for result in results for blocker in result["blockers"]]
        prior_blocked = bool(gate_blockers)
        all_results.extend(results)
        gate_results.append({
            "order": gate["order"], "lane": gate["lane"],
            "codex_profile": gate["codex_profile"],
            "status": "completed" if not gate_blockers else "blocked",
            "blockers": gate_blockers,
            "preflight": gate["preflight"],
            "command_plan": gate["command_plan"],
            "variant_results": [_strip_internal_variant_state(result) for result in results],
        })
    return gate_results, all_results


def _blocked_plan_gate(gate: dict[str, Any]) -> dict[str, Any]:
    if gate["preflight"]["admission"]["status"] != "pass":
        return _preflight_blocked_gate(gate)
    return {
        "order": gate["order"],
        "lane": gate["lane"],
        "codex_profile": gate["codex_profile"],
        "status": "not_run_with_reason",
        "blockers": [_PLAN_BLOCKED_NOT_RUN_REASON],
        "preflight": gate["preflight"],
        "command_plan": [],
        "variant_results": [],
    }


def _not_run_gate(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "order": gate["order"], "lane": gate["lane"], "codex_profile": gate["codex_profile"],
        "status": "not_run_with_reason", "blockers": ["prior_runtime_profile_gate_blocked"],
        "preflight": gate["preflight"],
        "command_plan": [],
        "variant_results": [],
    }


def _preflight_blocked_gate(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "order": gate["order"], "lane": gate["lane"], "codex_profile": gate["codex_profile"],
        "status": "blocked", "blockers": gate["preflight"]["admission"]["blockers"],
        "preflight": gate["preflight"], "command_plan": [], "variant_results": [],
    }


def _execute_runtime_gate(
    repo_root: Path, plan: dict[str, Any], gate: dict[str, Any], timeout: int, runner: CodexRunner,
) -> list[dict[str, Any]]:
    gate_runner = _runner_bound_to_auth_identity(gate, runner)
    results = []
    for command_plan in gate["command_plan"]:
        result = _execute_variant(
            repo_root, command_plan=command_plan,
            prompt=_variant_prompt(_variant_for_plan(plan, command_plan), plan["fixture"]),
            timeout_seconds=timeout, runner=gate_runner,
        )
        if result["codex_profile"] is not None and result["codex_profile"] != gate["codex_profile"]:
            raise ValueError("executed Codex argv profile does not match runtime gate")
        results.append(result)
    return results


def _runner_bound_to_auth_identity(gate: dict[str, Any], runner: CodexRunner) -> CodexRunner:
    if gate["lane"] != "oss-cloud":
        return runner
    expected_identity = gate["preflight"]["auth"].get("auth_stream_identity_digest")
    if expected_identity is None:
        return runner
    default_stream = actual_opaque_env_path()
    env_file = os.environ.get("SKILLS_SDK_OSS_CLOUD_ENV_FILE", str(default_stream) if default_stream else "")

    def bound_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
        if opaque_env_identity_digest(env_file) != expected_identity:
            raise ValueError("cloud execution auth stream identity changed before runner start")
        if runner is _default_codex_runner:
            return _default_codex_runner(
                command_argv, prompt, repo_root, timeout_seconds,
                expected_auth_stream_identity=expected_identity,
            )
        return runner(command_argv, prompt, repo_root, timeout_seconds)

    return bound_runner


def _variant_for_plan(plan: dict[str, Any], command_plan: dict[str, Any]) -> dict[str, str]:
    return plan["skill_a"] if command_plan["variant_label"] == "A" else plan["skill_b"]


def _strip_internal_variant_state(result: dict[str, Any]) -> dict[str, Any]:
    internal_keys = {"codex_exec_started", "provider_invoked", "network_accessed"}
    return {key: value for key, value in result.items() if key not in internal_keys}


def _run_payload(
    plan: dict[str, Any], status: str, blockers: list[str],
    receipt_variant_results: list[dict[str, Any]], runtime_profile_gates: list[dict[str, Any]],
    codex_exec_started: bool, provider_invoked: bool, network_accessed: bool, timeout_seconds: int,
) -> dict[str, Any]:
    return {
        "schema_version": AB_RUN_SCHEMA_VERSION, "schema_uri": AB_RUN_SCHEMA_URI,
        "status": status, "operation": "ab_run",
        "skill_a": plan["skill_a"],
        "skill_b": plan["skill_b"],
        "fixture": plan["fixture"],
        "execution_profile": plan["execution_profile"],
        "judge_profile": plan["judge_profile"],
        "execution_lane": plan["execution_lane"],
        "codex_profile": "oss-local",
        "runtime_profile_gates": runtime_profile_gates,
        "evidence_root": plan["evidence_root"],
        "experiment_id": plan["experiment_id"],
        "command_variant_labels": plan["command_variant_labels"],
        "command_plan": plan["command_plan"],
        "variant_results": receipt_variant_results,
        "secret_boundary": plan["secret_boundary"],
        "execution_boundary": "codex_exec_sandbox",
        "judge_boundary": "post_run_sanitized_evidence_only",
        "mutation_performed": bool(receipt_variant_results),
        "network_accessed": network_accessed,
        "provider_invoked": provider_invoked,
        "judge_provider_invoked": False,
        "codex_exec_invoked": codex_exec_started,
        "timeout": {"value": float(timeout_seconds), "unit": "s"},
        "blockers": blockers,
        "acceptance_trace": plan["acceptance_trace"],
        "agent_summary": (
            "A/B eval Codex execution completed; judge scoring has not been invoked."
            if status == "completed"
            else f"A/B eval Codex execution is blocked: {', '.join(blockers)}."
        ),
    }
