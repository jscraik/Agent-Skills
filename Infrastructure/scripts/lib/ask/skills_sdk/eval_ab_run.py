from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any, Callable

from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt


AB_RUN_SCHEMA_VERSION = "skills-sdk.ab-run-receipt.v0"
AB_RUN_SCHEMA_URI = "https://jscraik.local/agent-skills/schemas/skills-sdk/ab-run-receipt.v0.schema.json"
_SEMANTIC_OUTPUT_EXCERPT_BYTES = 4096


@dataclass(frozen=True)
class CodexRunResult:
    exit_code: int
    stdout: str
    stderr: str


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


def _default_codex_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
    proc = subprocess.run(
        command_argv,
        cwd=repo_root,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
        env=_codex_runner_env(),
    )
    return CodexRunResult(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


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
    output_digest = _digest_file(paths.output)
    blockers = _variant_blockers(variant_label, run_error, result.exit_code, output_digest)
    semantic_excerpt = _semantic_output_excerpt(paths.output)
    return {
        "variant_label": variant_label,
        "status": "pass" if not blockers else "blocked",
        "exit_code": result.exit_code,
        "command_argv": command_plan["command_argv"],
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
        "blockers": blockers,
    }


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
        return CodexRunResult(exit_code=127, stdout="", stderr=str(exc)), "codex_exec_unavailable", False


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


def _variant_blockers(variant_label: str, run_error: str | None, exit_code: int, output_digest: str | None) -> list[str]:
    blockers: list[str] = []
    if run_error:
        blockers.append(f"{variant_label}:{run_error}")
    if exit_code != 0:
        blockers.append(f"{variant_label}:codex_exec_exit_{exit_code}")
    if output_digest is None:
        blockers.append(f"{variant_label}:output_last_message_missing")
    return blockers


def build_ab_run_receipt(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    skill_a_identity: dict[str, str] | None,
    skill_b_identity: dict[str, str] | None,
    execution_profile_id: str = "codex-read-only",
    judge_profile_id: str = "oss-local",
    evidence_root: str = ".harness/artifacts/sdk-ab-evals",
    timeout_seconds: int = 1800,
    runner: CodexRunner | None = None,
) -> dict[str, Any]:
    plan = _build_plan(
        repo_root,
        skill_a=skill_a,
        skill_b=skill_b,
        fixture=fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile_id,
        judge_profile_id=judge_profile_id,
        evidence_root=evidence_root,
    )
    blockers = list(plan["blockers"])
    variant_results = _execute_variants(repo_root, plan, timeout_seconds, runner or _default_codex_runner)
    for variant_result in variant_results:
        blockers.extend(variant_result["blockers"])
    status = "completed" if not blockers else "blocked"
    codex_exec_started = any(result.get("codex_exec_started") is True for result in variant_results)
    receipt_variant_results = [_strip_internal_variant_state(result) for result in variant_results]
    return _run_payload(plan, status, blockers, receipt_variant_results, codex_exec_started, timeout_seconds)


def _build_plan(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
    return build_ab_plan_receipt(repo_root, **kwargs)


def _execute_variants(
    repo_root: Path,
    plan: dict[str, Any],
    timeout_seconds: int,
    runner: CodexRunner,
) -> list[dict[str, Any]]:
    if plan["blockers"]:
        return []
    return [
        _execute_variant(
            repo_root,
            command_plan=command_plan,
            prompt=_variant_prompt(_variant_for_plan(plan, command_plan), plan["fixture"]),
            timeout_seconds=timeout_seconds,
            runner=runner,
        )
        for command_plan in plan["command_plan"]
    ]


def _variant_for_plan(plan: dict[str, Any], command_plan: dict[str, Any]) -> dict[str, str]:
    return plan["skill_a"] if command_plan["variant_label"] == "A" else plan["skill_b"]


def _strip_internal_variant_state(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "codex_exec_started"}


def _run_payload(
    plan: dict[str, Any],
    status: str,
    blockers: list[str],
    receipt_variant_results: list[dict[str, Any]],
    codex_exec_started: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    return {
        "schema_version": AB_RUN_SCHEMA_VERSION,
        "schema_uri": AB_RUN_SCHEMA_URI,
        "status": status,
        "operation": "ab_run",
        "skill_a": plan["skill_a"],
        "skill_b": plan["skill_b"],
        "fixture": plan["fixture"],
        "execution_profile": plan["execution_profile"],
        "judge_profile": plan["judge_profile"],
        "evidence_root": plan["evidence_root"],
        "experiment_id": plan["experiment_id"],
        "command_variant_labels": plan["command_variant_labels"],
        "command_plan": plan["command_plan"],
        "variant_results": receipt_variant_results,
        "secret_boundary": plan["secret_boundary"],
        "execution_boundary": "codex_exec_sandbox",
        "judge_boundary": "post_run_sanitized_evidence_only",
        "mutation_performed": bool(receipt_variant_results),
        "network_accessed": codex_exec_started,
        "provider_invoked": codex_exec_started,
        "judge_provider_invoked": False,
        "codex_exec_invoked": codex_exec_started,
        "timeout_seconds": timeout_seconds,
        "blockers": blockers,
        "acceptance_trace": plan["acceptance_trace"],
        "agent_summary": (
            "A/B eval Codex execution completed; judge scoring has not been invoked."
            if status == "completed"
            else f"A/B eval Codex execution is blocked: {', '.join(blockers)}."
        ),
    }
