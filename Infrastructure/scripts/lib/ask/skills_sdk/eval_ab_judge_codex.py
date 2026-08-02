from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ask.skills_sdk.ab_transport_contracts import (
    actual_opaque_env_path,
    approved_op_binary,
    approved_op_env_invocation,
    is_actual_opaque_env_reference,
)
from ask.skills_sdk.local_codex_catalog import augment_local_codex_profile_config

_CODEX_PROFILE_SOURCE_DIR_ENV = "ASK_CODEX_PROFILE_SOURCE_DIR"
_CODEX_TMPDIR_ENV = "ASK_CODEX_TMPDIR"
_CODEX_OP_ENV_FILE_ENV = "ASK_CODEX_OP_ENV_FILE"
_MINIMAL_CODEX_CONFIG = 'model_reasoning_effort = "none"\n'


@dataclass(frozen=True)
class CodexJudgeResult:
    exit_code: int
    stdout: str
    stderr: str
    output_text: str = ""
    executed_argv: list[str] | None = None


class CodexProfileConfigError(RuntimeError):
    pass


def _run_codex_judge(
    prompt: str,
    judge_profile: dict[str, Any],
    timeout_seconds: int,
    repo_root: Path,
    output_file: Path,
) -> CodexJudgeResult:
    work_dir = _codex_judge_work_dir(output_file)
    _prepare_codex_judge_work_dir(work_dir)
    command = _codex_judge_command(judge_profile, work_dir, output_file)
    with tempfile.TemporaryDirectory(prefix="codex-oss-home.", dir=_codex_temp_parent()) as codex_home_raw:
        with tempfile.TemporaryDirectory(prefix="codex-oss-sqlite.", dir=_codex_temp_parent()) as sqlite_home_raw:
            codex_home = Path(codex_home_raw)
            sqlite_home = Path(sqlite_home_raw)
            _write_minimal_codex_config(codex_home)
            _copy_codex_profile_config(judge_profile, codex_home)
            completed, command = _execute_codex_judge_command(
                command, prompt, judge_profile, timeout_seconds, repo_root, codex_home, sqlite_home,
            )
    return CodexJudgeResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        output_text=completed.stdout,
        executed_argv=command,
    )


def _execute_codex_judge_command(
    command: list[str], prompt: str, judge_profile: dict[str, Any], timeout_seconds: int,
    repo_root: Path, codex_home: Path, sqlite_home: Path,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    kwargs: dict[str, Any] = {
        "input": prompt, "text": True, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE,
        "check": False, "timeout": timeout_seconds,
        "env": _codex_judge_env(judge_profile, repo_root, codex_home, sqlite_home),
    }
    if _codex_profile_id(judge_profile) != "oss-cloud":
        return subprocess.run(command, **kwargs), command
    op_env_file = _codex_op_env_file_path(judge_profile)
    if op_env_file is None:
        raise CodexProfileConfigError("oss-cloud judge execution requires the approved op run env boundary")
    with approved_op_env_invocation(op_env_file) as invocation:
        kwargs["pass_fds"] = invocation.pass_fds
        completed = subprocess.run(invocation.runtime_argv(command[5:]), **kwargs)
        return completed, invocation.receipt_argv(command[5:])


def _codex_judge_command(judge_profile: dict[str, Any], work_dir: Path, output_file: Path) -> list[str]:
    codex_profile = _codex_profile_id(judge_profile)
    codex_command = [
        "codex",
        "exec",
        "--profile",
        codex_profile,
        "--disable",
        "apps",
        "-c",
        'approval_policy="on-request"',
        "--cd",
        str(work_dir),
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--json",
        "--output-last-message",
        str(output_file),
        "-",
    ]
    model_override = _codex_model_override(judge_profile)
    if model_override is not None:
        codex_command[4:4] = ["-c", f"model={_json_toml_string(model_override)}"]
    for override in reversed(_codex_model_setting_overrides(judge_profile)):
        codex_command[4:4] = ["-c", override]
    op_env_file = _codex_op_env_file_path(judge_profile)
    op_bin = _codex_op_bin() if op_env_file is not None else None
    if op_env_file is not None and op_bin is not None:
        return [op_bin, "run", "--env-file", str(op_env_file), "--", *codex_command]
    if codex_profile == "oss-cloud":
        raise CodexProfileConfigError("oss-cloud judge execution requires the approved op run env boundary")
    return codex_command


def _codex_profile_id(judge_profile: dict[str, Any]) -> str:
    return str(judge_profile.get("codex_profile") or judge_profile["id"])


def _codex_model_override(judge_profile: dict[str, Any]) -> str | None:
    if _codex_profile_id(judge_profile) == str(judge_profile["id"]):
        return None
    model = judge_profile.get("model")
    return model if isinstance(model, str) and model else None


def _codex_model_setting_overrides(judge_profile: dict[str, Any]) -> list[str]:
    settings = judge_profile.get("model_settings")
    if not isinstance(settings, dict):
        return []
    overrides: list[str] = []
    valid_keys = sorted(key for key in settings if isinstance(key, str) and key)
    for key in valid_keys:
        value = settings[key]
        if isinstance(value, bool):
            encoded = "true" if value else "false"
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            encoded = str(value)
        elif isinstance(value, str):
            encoded = _json_toml_string(value)
        else:
            continue
        overrides.append(f"model_settings.{key}={encoded}")
    return overrides


def _json_toml_string(value: str) -> str:
    return json.dumps(value)


def _codex_judge_work_dir(output_file: Path) -> Path:
    digest = hashlib.sha256(str(output_file).encode("utf-8")).hexdigest()[:16]
    return Path(_codex_temp_parent() or tempfile.gettempdir()) / "ask-sdk-ab-judge-workspaces" / digest


def _prepare_codex_judge_work_dir(work_dir: Path) -> None:
    if work_dir.is_symlink():
        raise OSError("codex judge workspace must not be a symlink")
    if work_dir.exists():
        if not work_dir.is_dir():
            raise OSError("codex judge workspace must be a directory")
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)


def _codex_op_env_file_available(judge_profile: dict[str, Any]) -> bool:
    return _codex_op_env_file_path(judge_profile) is not None and _codex_op_bin() is not None


def _codex_op_bin() -> str | None:
    return approved_op_binary()


def _codex_op_env_file_path(judge_profile: dict[str, Any]) -> Path | None:
    if _codex_profile_id(judge_profile) != "oss-cloud":
        return None
    if not judge_profile.get("secret_env_names"):
        return None
    configured = os.environ.get(_CODEX_OP_ENV_FILE_ENV)
    default_stream = actual_opaque_env_path()
    candidate = configured if configured is not None else str(default_stream) if default_stream else ""
    if not is_actual_opaque_env_reference(candidate):
        return None
    return Path(candidate)


def _copy_codex_profile_config(judge_profile: dict[str, Any], codex_home: Path) -> Path:
    profile_id = _codex_profile_id(judge_profile)
    source = _codex_profile_source_path(profile_id)
    if source is None:
        raise CodexProfileConfigError(f"missing Codex profile config for {profile_id}")
    codex_home.mkdir(parents=True, exist_ok=True)
    target = codex_home / f"{profile_id}.config.toml"
    shutil.copy2(source, target)
    augment_local_codex_profile_config(target, _codex_profile_model(judge_profile))
    target.chmod(0o600)
    return target


def _write_minimal_codex_config(codex_home: Path) -> Path:
    codex_home.mkdir(parents=True, exist_ok=True)
    target = codex_home / "config.toml"
    target.write_text(_MINIMAL_CODEX_CONFIG, encoding="utf-8")
    target.chmod(0o600)
    return target


def _codex_profile_source_path(profile_id: str) -> Path | None:
    config_name = f"{profile_id}.config.toml"
    candidates: list[tuple[Path, Path]] = []
    configured_source_dir = os.environ.get(_CODEX_PROFILE_SOURCE_DIR_ENV)
    if configured_source_dir:
        configured_root = Path(configured_source_dir).expanduser()
        candidates.append((configured_root / config_name, configured_root))
    current_codex_home = os.environ.get("CODEX_HOME")
    if current_codex_home:
        codex_home = Path(current_codex_home).expanduser()
        candidates.append((codex_home / config_name, codex_home))
    dot_codex = Path.home() / ".codex"
    candidates.append((dot_codex / config_name, dot_codex))
    for candidate, root in candidates:
        try:
            safe_candidate = _safe_regular_file(candidate, root)
            if safe_candidate is not None:
                return safe_candidate
        except OSError:
            continue
    return None


def _safe_regular_file(path: Path, root: Path) -> Path | None:
    root_real = os.path.realpath(root)
    path_real = os.path.realpath(path)
    if os.path.commonpath([root_real, path_real]) != root_real:
        return None
    if path.is_symlink() or not path.is_file():
        return None
    return path


def _codex_profile_model(judge_profile: dict[str, Any]) -> str | None:
    model = judge_profile.get("model")
    return model if isinstance(model, str) and model else None


def _codex_temp_parent() -> str | None:
    configured_tmp = os.environ.get(_CODEX_TMPDIR_ENV)
    if configured_tmp and Path(configured_tmp).is_dir():
        return configured_tmp
    private_tmp = Path("/private/tmp")
    return str(private_tmp) if private_tmp.is_dir() else None


def _codex_judge_env(
    judge_profile: dict[str, Any],
    repo_root: Path,
    codex_home: Path,
    sqlite_home: Path,
) -> dict[str, str]:
    allowed_secret_names = {
        name
        for name in judge_profile.get("secret_env_names", [])
        if isinstance(name, str) and name
    }
    passthrough_names = {
        "HOME", "LANG", "LC_ALL", "LC_CTYPE", "PATH",
        "PWD", "SHELL", "TERM", "TMPDIR", "USER",
    }
    env = {
        key: value
        for key, value in os.environ.items()
        if key in passthrough_names or key in allowed_secret_names
    }
    env["CODEX_HOME"] = str(codex_home)
    env["CODEX_SQLITE_HOME"] = str(sqlite_home)
    repo_mise_config = repo_root / ".mise.toml"
    if repo_mise_config.is_file() and "MISE_TRUSTED_CONFIG_PATHS" not in env:
        env["MISE_TRUSTED_CONFIG_PATHS"] = str(repo_mise_config)
    return env
