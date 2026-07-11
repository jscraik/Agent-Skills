#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

from check_oss_local_smoke_output import _findings


EXPECTED_MODEL = "minimax-m2.7:cloud"
EXPECTED_PROVIDER = "ollama-cloud"
DEFAULT_PROFILE_SOURCE = Path.home() / ".codex" / "oss-cloud.config.toml"
DEFAULT_OP_ENV_FILE = Path.home() / ".codex" / ".env"
DEFAULT_MARKER = "CODEX_OSS_CLOUD_OK"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded oss-cloud Codex marker smoke through 1Password.")
    parser.add_argument("--profile-source", default=str(DEFAULT_PROFILE_SOURCE))
    parser.add_argument("--op-env-file", default=str(DEFAULT_OP_ENV_FILE))
    parser.add_argument("--op-bin", default=shutil.which("op") or "op")
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
    if stat.S_ISFIFO(mode):
        return path
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("OLLAMA_API_KEY=op://") and len(line) > len("OLLAMA_API_KEY=op://"):
            return path
    return None


def _auth_source(path: Path) -> str:
    if _approved_env_file(path) is None:
        return "missing_or_invalid"
    return "op_fifo" if stat.S_ISFIFO(path.stat().st_mode) else "op_reference"


def _paths(output_dir: str | None) -> dict[str, Path]:
    root = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="ask-oss-cloud-smoke."))
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return {
        "root": root,
        "stdout": root / "stdout.txt",
        "stderr": root / "stderr.txt",
        "last_message": root / "last-message.txt",
    }


def _command(args: argparse.Namespace, paths: dict[str, Path], env_file: Path) -> list[str]:
    return [
        args.op_bin,
        "run",
        "--env-file",
        str(env_file),
        "--",
        "env",
        f"CODEX_HOME={Path(args.profile_source).expanduser().parent.resolve(strict=False)}",
        "codex",
        "exec",
        "--profile",
        "oss-cloud",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--json",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--output-last-message",
        str(paths["last_message"]),
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
    args: argparse.Namespace,
    paths: dict[str, Path],
    profile: Path,
    findings: list[dict[str, str]],
    *,
    command: list[str] | None,
    exit_code: int | None,
    duration_seconds: float,
    provider_invoked: bool,
) -> dict[str, Any]:
    if command is not None:
        findings.extend(_findings("\n".join((_read(paths["stdout"]), _read(paths["stderr"]))), 7000))
        if exit_code != 0:
            findings.append({"code": "oss_cloud_smoke_exit_nonzero", "message": f"Codex exited with {exit_code}."})
        if _read(paths["last_message"]).strip() != args.marker:
            findings.append({"code": "oss_cloud_smoke_marker_mismatch", "message": "Cloud smoke marker did not match."})
    return {
        "schema_version": "skills-sdk.oss-cloud-smoke-run.v0",
        "status": "pass" if provider_invoked and not findings else "blocked",
        "lane": "oss-cloud",
        "codex_profile": "oss-cloud",
        "model": _profile_value(profile, "model") if profile.is_file() else None,
        "model_provider": _profile_value(profile, "model_provider") if profile.is_file() else None,
        "auth_source": _auth_source(Path(args.op_env_file).expanduser()),
        "provider_invoked": provider_invoked,
        "command": command,
        "duration_seconds": duration_seconds,
        "exit_code": exit_code,
        "marker": args.marker,
        "stdout_path": str(paths["stdout"]),
        "stderr_path": str(paths["stderr"]),
        "last_message_path": str(paths["last_message"]),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds < 1:
        raise SystemExit("--timeout-seconds must be positive")
    profile = Path(args.profile_source).expanduser()
    paths = _paths(args.output_dir)
    findings = _profile_findings(profile)
    env_file = _approved_env_file(Path(args.op_env_file).expanduser())
    if env_file is None:
        findings.append({"code": "oss_cloud_credential_reference_missing", "message": "Approved OLLAMA_API_KEY 1Password reference is required."})
    if not Path(args.op_bin).is_file() and shutil.which(args.op_bin) is None:
        findings.append({"code": "oss_cloud_op_missing", "message": "1Password CLI is required for oss-cloud."})
    if findings:
        receipt = _receipt(args, paths, profile, findings, command=None, exit_code=None, duration_seconds=0.0, provider_invoked=False)
    else:
        command = _command(args, paths, env_file)
        exit_code, duration_seconds = _run(command, paths, args)
        receipt = _receipt(args, paths, profile, findings, command=command, exit_code=exit_code, duration_seconds=duration_seconds, provider_invoked=True)
    print(json.dumps(receipt, sort_keys=True, indent=2) if args.json else receipt["status"])
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
