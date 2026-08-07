#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from check_oss_local_smoke_output import _findings  # noqa: E402


EXPECTED_MODEL = "deepseek-v4-flash:cloud"
EXPECTED_PROVIDER = "ollama-cloud"
DEFAULT_PROFILE_SOURCE = Path.home() / ".codex" / "oss-cloud.config.toml"
DEFAULT_AUTH_ENV_FILE = Path.home() / ".codex" / ".env"
DEFAULT_AUTH_WRAPPER = Path("/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh")
DEFAULT_CODEX_EXEC_WRAPPER = Path("/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh")
DEFAULT_MARKER = "CODEX_OSS_CLOUD_OK"
CLOUD_SMOKE_MAX_TOKENS_USED = 20000
CLOUD_SMOKE_NON_BLOCKING_CODES = frozenset({"codex_runtime_metadata_fallback"})
ISOLATED_CODEX_CONFIG = f'''model = "{EXPECTED_MODEL}"
model_provider = "{EXPECTED_PROVIDER}"
approval_policy = "on-request"
approvals_reviewer = "auto_review"
default_permissions = "readonly-net"
model_reasoning_effort = "high"
model_reasoning_summary = "concise"
web_search = "cached"

[features]
plugins = false
skill_mcp_dependency_install = false
apps = false
code_mode = false
code_mode_only = false

[permissions.readonly-net]
extends = ":read-only"
description = "Bounded read-only cloud smoke profile."

[permissions.readonly-net.network]
enabled = true
allow_local_binding = false

[permissions.readonly-net.network.domains]
"ollama.com" = "allow"

[model_providers.ollama-cloud]
name = "Ollama Cloud"
base_url = "https://ollama.com/v1"
wire_api = "responses"
env_key = "OLLAMA_API_KEY"
'''


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded oss-cloud Codex marker smoke through 1Password.")
    parser.add_argument("--profile-source", default=str(DEFAULT_PROFILE_SOURCE))
    parser.add_argument("--env-file", default=str(DEFAULT_AUTH_ENV_FILE))
    parser.add_argument("--auth-wrapper", default=str(DEFAULT_AUTH_WRAPPER))
    parser.add_argument("--codex-exec-wrapper", default=str(DEFAULT_CODEX_EXEC_WRAPPER))
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--marker", default=DEFAULT_MARKER)
    parser.add_argument("--work-dir", default=str(Path.cwd()))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def _profile_value(path: Path, key: str) -> str | None:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    value = payload.get(key)
    return value if isinstance(value, str) else None


def _profile_findings(path: Path) -> list[dict[str, str]]:
    try:
        profile = path.resolve(strict=True)
    except OSError:
        profile = path
    if not profile.is_file():
        return [{"code": "oss_cloud_profile_missing", "message": "oss-cloud profile source must be a regular file."}]
    findings: list[dict[str, str]] = []
    if _profile_value(profile, "model") != EXPECTED_MODEL:
        findings.append({"code": "oss_cloud_model_mismatch", "message": f"Expected model {EXPECTED_MODEL!r}."})
    if _profile_value(profile, "model_provider") != EXPECTED_PROVIDER:
        findings.append({"code": "oss_cloud_provider_mismatch", "message": f"Expected provider {EXPECTED_PROVIDER!r}."})
    return findings


def _approved_env_file(path: Path) -> Path | None:
    if path.is_symlink():
        return None
    try:
        mode = path.stat().st_mode
    except OSError:
        return None
    return path if stat.S_ISFIFO(mode) else None


def _auth_source(path: Path) -> str:
    if _approved_env_file(path) is None:
        return "missing_or_invalid"
    return "1password_desktop_fifo"


def _paths(output_dir: str | None) -> dict[str, Path]:
    root = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="ask-oss-cloud-smoke."))
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return {
        "root": root,
        "codex_home": root / "codex-home",
        "stdout": root / "stdout.txt",
        "stderr": root / "stderr.txt",
        "last_message": root / "last-message.txt",
    }


def _isolated_codex_home(profile: Path, paths: dict[str, Path]) -> Path:
    """Prepare a context-minimal Codex home for the bounded marker call."""
    codex_home = paths["codex_home"]
    codex_home.mkdir(parents=True, exist_ok=True)
    shutil.copy2(profile.resolve(strict=True), codex_home / "oss-cloud.config.toml")
    (codex_home / "config.toml").write_text(ISOLATED_CODEX_CONFIG, encoding="utf-8")
    return codex_home


def _command(args: argparse.Namespace, paths: dict[str, Path], env_file: Path) -> list[str]:
    codex_home = _isolated_codex_home(Path(args.profile_source).expanduser(), paths)
    return [
        "bash",
        args.auth_wrapper,
        "--env-file",
        str(env_file),
        "--require-env",
        "OLLAMA_API_KEY",
        "--",
        "env",
        "-u",
        "CODEX_CONFIG_HOME",
        f"CODEX_HOME={codex_home}",
        "bash",
        args.codex_exec_wrapper,
        "--profile",
        "oss-cloud",
        "--strict-config",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--model",
        EXPECTED_MODEL,
        f"Reply exactly {args.marker}",
    ]


def _run(command: list[str], paths: dict[str, Path], args: argparse.Namespace) -> tuple[int, float]:
    started = time.monotonic()
    with paths["stdout"].open("w", encoding="utf-8") as stdout, paths["stderr"].open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=args.work_dir,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                check=False,
                text=True,
                timeout=args.timeout_seconds,
            )
            return completed.returncode, round(time.monotonic() - started, 3)
        except subprocess.TimeoutExpired:
            return 124, round(time.monotonic() - started, 3)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _receipt(
    args: argparse.Namespace, paths: dict[str, Path], profile: Path, findings: list[dict[str, str]], *,
    command: list[str] | None, exit_code: int | None, duration_seconds: float, provider_invoked: bool,
) -> dict[str, Any]:
    warnings = _runtime_findings(args, paths, findings, command, exit_code)
    return {
        "schema_version": "skills-sdk.oss-cloud-smoke-run.v0",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if provider_invoked and not findings else "blocked",
        "lane": "oss-cloud",
        "codex_profile": "oss-cloud",
        "model": _profile_value(profile, "model") if profile.is_file() else None,
        "model_provider": _profile_value(profile, "model_provider") if profile.is_file() else None,
        "auth_source": _auth_source(Path(args.env_file).expanduser()),
        "provider_invoked": provider_invoked,
        "command": _redacted_command(command),
        "duration_seconds": duration_seconds,
        "exit_code": exit_code,
        "marker": args.marker,
        "stdout_path": str(paths["stdout"]),
        "stderr_path": str(paths["stderr"]),
        "last_message_path": str(paths["last_message"]),
        "warnings": warnings,
        "findings": findings,
    }


def _runtime_findings(
    args: argparse.Namespace, paths: dict[str, Path], findings: list[dict[str, str]],
    command: list[str] | None, exit_code: int | None,
) -> list[dict[str, str]]:
    if command is None:
        return []
    runtime_findings = _findings(
        "\n".join((_read(paths["stdout"]), _read(paths["stderr"]))), CLOUD_SMOKE_MAX_TOKENS_USED,
    )
    warnings = [item for item in runtime_findings if item["code"] in CLOUD_SMOKE_NON_BLOCKING_CODES]
    findings.extend(item for item in runtime_findings if item["code"] not in CLOUD_SMOKE_NON_BLOCKING_CODES)
    if exit_code != 0:
        findings.append({"code": "oss_cloud_smoke_exit_nonzero", "message": f"Codex exited with {exit_code}."})
    if _read(paths["stdout"]).strip() != args.marker:
        findings.append({"code": "oss_cloud_smoke_marker_mismatch", "message": "Cloud smoke marker did not match."})
    return warnings


def _redacted_command(command: list[str] | None) -> list[str] | None:
    if command is None:
        return None
    redacted = list(command)
    for index, value in enumerate(redacted[:-1]):
        if value == "--env-file":
            redacted[index + 1] = "<operator-approved-opaque-env-stream>"
    return redacted


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds < 1:
        raise SystemExit("--timeout-seconds must be positive")
    profile = Path(args.profile_source).expanduser()
    paths = _paths(args.output_dir)
    findings = _profile_findings(profile)
    env_file = _approved_env_file(Path(args.env_file).expanduser())
    if env_file is None:
        findings.append({"code": "oss_cloud_auth_stream_missing", "message": "Desktop-owned OLLAMA_API_KEY FIFO is required."})
    if not Path(args.auth_wrapper).is_file() or Path(args.auth_wrapper).is_symlink():
        findings.append({"code": "oss_cloud_auth_wrapper_missing", "message": "Configs auth-backed wrapper is required for oss-cloud."})
    if not Path(args.codex_exec_wrapper).is_file() or not Path(args.codex_exec_wrapper).stat().st_mode & stat.S_IXUSR:
        findings.append({"code": "oss_cloud_exec_wrapper_missing", "message": "Configs Codex execution wrapper is required for oss-cloud."})
    if findings:
        receipt = _receipt(args, paths, profile, findings, command=None, exit_code=None, duration_seconds=0.0, provider_invoked=False)
    else:
        command = _command(args, paths, env_file)
        exit_code, duration_seconds = _run(command, paths, args)
        receipt = _receipt(args, paths, profile, findings, command=command, exit_code=exit_code, duration_seconds=duration_seconds, provider_invoked=True)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")) if args.json else receipt["status"])
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
