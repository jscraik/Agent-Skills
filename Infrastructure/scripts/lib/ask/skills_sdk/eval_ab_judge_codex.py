from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_CODEX_PROFILE_SOURCE_DIR_ENV = "ASK_CODEX_PROFILE_SOURCE_DIR"
_CODEX_TMPDIR_ENV = "ASK_CODEX_TMPDIR"
_CODEX_OP_ENV_FILE_ENV = "ASK_CODEX_OP_ENV_FILE"


@dataclass(frozen=True)
class CodexJudgeResult:
    exit_code: int
    stdout: str
    stderr: str
    output_text: str = ""


class CodexProfileConfigError(RuntimeError):
    pass


def _run_codex_judge(
    prompt: str,
    judge_profile: dict[str, Any],
    timeout_seconds: int,
    repo_root: Path,
    output_file: Path,
) -> CodexJudgeResult:
    command = _codex_judge_command(judge_profile, repo_root, output_file)
    with tempfile.TemporaryDirectory(prefix="codex-oss-home.", dir=_codex_temp_parent()) as codex_home_raw:
        with tempfile.TemporaryDirectory(prefix="codex-oss-sqlite.", dir=_codex_temp_parent()) as sqlite_home_raw:
            codex_home = Path(codex_home_raw)
            sqlite_home = Path(sqlite_home_raw)
            _copy_codex_profile_config(judge_profile, codex_home)
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout_seconds,
                env=_codex_judge_env(judge_profile, repo_root, codex_home, sqlite_home),
            )
    return CodexJudgeResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        output_text=completed.stdout,
    )


def _codex_judge_command(judge_profile: dict[str, Any], repo_root: Path, output_file: Path) -> list[str]:
    codex_command = [
        "codex", "exec", "--profile", str(judge_profile["id"]), "--cd", str(repo_root),
        "--sandbox", "read-only", "--ephemeral", "--json",
        "--output-last-message", str(output_file), "-",
    ]
    op_env_file = _codex_op_env_file_path(judge_profile)
    op_bin = _codex_op_bin() if op_env_file is not None else None
    if op_env_file is not None and op_bin is not None:
        return [op_bin, "run", "--env-file", str(op_env_file), "--", *codex_command]
    return codex_command


def _codex_op_env_file_available(judge_profile: dict[str, Any]) -> bool:
    return _codex_op_env_file_path(judge_profile) is not None and _codex_op_bin() is not None


def _codex_op_bin() -> str | None:
    homebrew_op = Path("/opt/homebrew/bin/op")
    if homebrew_op.is_file():
        return str(homebrew_op)
    return shutil.which("op")


def _codex_op_env_file_path(judge_profile: dict[str, Any]) -> Path | None:
    if judge_profile.get("id") != "oss-cloud":
        return None
    if not judge_profile.get("secret_env_names"):
        return None
    configured = os.environ.get(_CODEX_OP_ENV_FILE_ENV)
    candidate = Path(configured).expanduser() if configured else Path.home() / ".codex" / ".env"
    try:
        return _safe_regular_file(candidate, candidate.parent)
    except OSError:
        return None


def _copy_codex_profile_config(judge_profile: dict[str, Any], codex_home: Path) -> Path:
    profile_id = str(judge_profile["id"])
    source = _codex_profile_source_path(profile_id)
    if source is None:
        raise CodexProfileConfigError(f"missing Codex profile config for {profile_id}")
    codex_home.mkdir(parents=True, exist_ok=True)
    target = codex_home / f"{profile_id}.config.toml"
    shutil.copy2(source, target)
    target.chmod(0o600)
    return target


def _codex_profile_source_path(profile_id: str) -> Path | None:
    config_name = f"{profile_id}.config.toml"
    candidates: list[tuple[Path, Path]] = []
    configured_source_dir = os.environ.get(_CODEX_PROFILE_SOURCE_DIR_ENV)
    if configured_source_dir:
        configured_root = Path(configured_source_dir).expanduser()
        candidates.append((configured_root / config_name, configured_root))
    configs_root = Path.home() / "dev" / "configs" / "codex"
    candidates.append((configs_root / config_name, configs_root))
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
