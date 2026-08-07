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
    configs_auth_wrapper,
    configs_codex_exec_wrapper,
    is_actual_opaque_env_reference,
)
from ask.skills_sdk.local_codex_catalog import augment_local_codex_profile_config

_CODEX_PROFILE_SOURCE_DIR_ENV = "ASK_CODEX_PROFILE_SOURCE_DIR"
_CODEX_TMPDIR_ENV = "ASK_CODEX_TMPDIR"
_CODEX_AUTH_ENV_FILE_ENV = "SKILLS_SDK_OSS_CLOUD_ENV_FILE"
_CODEX_RUNTIME_OUTPUT_NAME = "codex-last-message.json"
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
    if _codex_profile_id(judge_profile) == "oss-cloud":
        completed, execution_argv = _execute_codex_judge_command(
            command, prompt, judge_profile, timeout_seconds, repo_root, None, None, work_dir,
        )
        runtime_output = work_dir / _CODEX_RUNTIME_OUTPUT_NAME
        _copy_contained_judge_output(runtime_output, output_file, work_dir)
        output_text = _read_runtime_output(runtime_output, completed.stdout)
        return CodexJudgeResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            output_text=output_text,
            executed_argv=execution_argv,
        )
    with tempfile.TemporaryDirectory(prefix="codex-oss-home.", dir=_codex_temp_parent()) as codex_home_raw:
        with tempfile.TemporaryDirectory(prefix="codex-oss-sqlite.", dir=_codex_temp_parent()) as sqlite_home_raw:
            codex_home = Path(codex_home_raw)
            sqlite_home = Path(sqlite_home_raw)
            _write_minimal_codex_config(codex_home)
            _copy_codex_profile_config(judge_profile, codex_home)
            completed, command = _execute_codex_judge_command(
                command, prompt, judge_profile, timeout_seconds, repo_root, codex_home, sqlite_home, work_dir,
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
    repo_root: Path, codex_home: Path | None, sqlite_home: Path | None, work_dir: Path,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    kwargs: dict[str, Any] = {
        "input": prompt, "text": True, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE,
        "check": False, "timeout": timeout_seconds,
        "env": _codex_judge_env(judge_profile, repo_root, codex_home, sqlite_home),
        "cwd": work_dir,
    }
    return subprocess.run(command, **kwargs), command


def _codex_judge_command(judge_profile: dict[str, Any], work_dir: Path, output_file: Path) -> list[str]:
    if _codex_profile_id(judge_profile) == "oss-cloud":
        return _cloud_judge_command(judge_profile, work_dir)
    return _local_judge_command(judge_profile, work_dir, output_file)


def _cloud_judge_command(judge_profile: dict[str, Any], work_dir: Path) -> list[str]:
    env_file = _codex_auth_env_file_path(judge_profile)
    auth_wrapper = configs_auth_wrapper()
    codex_exec_wrapper = configs_codex_exec_wrapper()
    if env_file is None or auth_wrapper is None or codex_exec_wrapper is None:
        raise CodexProfileConfigError("oss-cloud judge execution requires the Configs auth-backed wrapper boundary")
    command = [
        "bash", auth_wrapper, "--env-file", str(env_file), "--require-env", "OLLAMA_API_KEY", "--",
        "bash", codex_exec_wrapper, "--profile", "oss-cloud", "--strict-config",
        "-c", 'approval_policy="on-request"', "--cd", str(work_dir), "--sandbox", "read-only",
        "--ephemeral", "--skip-git-repo-check", "--json", "--output-last-message",
        _CODEX_RUNTIME_OUTPUT_NAME, "-",
    ]
    model = _codex_profile_model(judge_profile)
    if model is not None:
        command[11:11] = ["--model", model]
    for override in reversed(_codex_model_setting_overrides(judge_profile)):
        command[command.index("--strict-config"):command.index("--strict-config")] = ["-c", override]
    return command


def _local_judge_command(judge_profile: dict[str, Any], work_dir: Path, output_file: Path) -> list[str]:
    codex_profile = _codex_profile_id(judge_profile)
    codex_command = [
        "codex",
        "exec",
        "--profile",
        codex_profile,
        "-c",
        'approval_policy="on-request"',
        "--cd",
        str(work_dir),
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
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
    return codex_command


def _read_runtime_output(runtime_output: Path, fallback: str) -> str:
    if runtime_output.is_symlink() or not runtime_output.is_file():
        return fallback
    try:
        return runtime_output.read_text(encoding="utf-8")
    except OSError:
        return fallback


def _copy_contained_judge_output(runtime_output: Path, output_file: Path, work_dir: Path) -> None:
    """Copy the contained runtime receipt into the repo-owned evidence path."""
    if runtime_output.is_symlink() or not runtime_output.is_file() or output_file.is_symlink():
        return
    try:
        runtime_output.resolve().relative_to(work_dir.resolve())
    except (OSError, ValueError):
        return
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_file.with_name(f".{output_file.name}.{os.getpid()}.tmp")
    if temporary_output.is_symlink():
        return
    try:
        shutil.copyfile(runtime_output, temporary_output)
        temporary_output.chmod(0o600)
        os.replace(temporary_output, output_file)
    finally:
        if temporary_output.exists() and not temporary_output.is_symlink():
            temporary_output.unlink()


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
    return Path("/private/tmp/ask-sdk-ab-variant-workspaces") / "judge" / digest


def _prepare_codex_judge_work_dir(work_dir: Path) -> None:
    if work_dir.is_symlink():
        raise OSError("codex judge workspace must not be a symlink")
    if work_dir.exists():
        if not work_dir.is_dir():
            raise OSError("codex judge workspace must be a directory")
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)


def _codex_auth_boundary_available(judge_profile: dict[str, Any]) -> bool:
    return (
        _codex_auth_env_file_path(judge_profile) is not None
        and configs_auth_wrapper() is not None
        and configs_codex_exec_wrapper() is not None
    )


def _codex_auth_env_file_path(judge_profile: dict[str, Any]) -> Path | None:
    if _codex_profile_id(judge_profile) != "oss-cloud":
        return None
    if not judge_profile.get("secret_env_names"):
        return None
    configured = os.environ.get(_CODEX_AUTH_ENV_FILE_ENV)
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
    """Create an isolated base config before layering the selected profile."""
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
    codex_home: Path | None,
    sqlite_home: Path | None,
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
    if codex_home is not None and sqlite_home is not None:
        env["CODEX_HOME"] = str(codex_home)
        env["CODEX_SQLITE_HOME"] = str(sqlite_home)
    repo_mise_config = repo_root / ".mise.toml"
    if repo_mise_config.is_file() and "MISE_TRUSTED_CONFIG_PATHS" not in env:
        env["MISE_TRUSTED_CONFIG_PATHS"] = str(repo_mise_config)
    return env
