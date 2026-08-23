#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from check_oss_local_smoke_output import DEFAULT_MAX_TOKENS_USED, _findings

LIB_DIR = Path(__file__).resolve().parents[1] / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))
_catalog = importlib.import_module("ask.skills_sdk.local_codex_catalog")
augment_local_codex_profile_config = _catalog.augment_local_codex_profile_config


DEFAULT_PROFILE_SOURCE = Path("/Users/jamiecraik/.codex/oss-local.config.toml")
DEFAULT_MARKER = "CODEX_OSS_LOCAL_OK"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded oss-local Codex marker smoke and validate captures.")
    parser.add_argument("--profile-source", default=str(DEFAULT_PROFILE_SOURCE))
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--marker", default=DEFAULT_MARKER)
    parser.add_argument("--max-tokens-used", type=int, default=DEFAULT_MAX_TOKENS_USED)
    parser.add_argument("--work-dir", default=str(Path.cwd()))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _profile_value(profile_path: Path, key: str) -> str | None:
    prefix = f"{key} = "
    for line in _read(profile_path).splitlines():
        if not line.startswith(prefix):
            continue
        return line.removeprefix(prefix).strip().strip('"')
    return None


def _write_receipt(receipt: dict[str, Any], *, emit_json: bool) -> None:
    if emit_json:
        print(json.dumps(receipt, sort_keys=True, indent=2))
        return
    if receipt["status"] == "pass":
        print(f"oss-local smoke pass: {receipt['last_message_path']}")
    else:
        for finding in receipt["findings"]:
            print(f"{finding['code']}: {finding['message']}", file=sys.stderr)


def _profile_source(raw_path: str) -> Path:
    profile_source = Path(raw_path).expanduser()
    if not profile_source.exists() or profile_source.is_dir():
        raise SystemExit(f"profile source must resolve to a file: {profile_source}")
    profile_source = profile_source.resolve()
    if not profile_source.is_file():
        raise SystemExit(f"profile source must resolve to a file: {profile_source}")
    return profile_source


def _prepare_paths(args: argparse.Namespace) -> dict[str, Path]:
    output_root = Path(args.output_dir) if args.output_dir else Path(tempfile.mkdtemp(prefix="ask-oss-local-smoke."))
    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    codex_home = output_root / "codex-home"
    codex_home.mkdir(parents=True, exist_ok=True)
    profile_target = codex_home / "oss-local.config.toml"
    shutil.copy2(_profile_source(args.profile_source), profile_target)
    augment_local_codex_profile_config(profile_target, _profile_value(profile_target, "model"))
    return {
        "root": output_root,
        "stdout": output_root / "stdout.txt",
        "stderr": output_root / "stderr.txt",
        "last_message": output_root / "last-message.txt",
        "codex_home": codex_home,
    }


def _codex_command(last_message_path: Path, marker: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--profile",
        "oss-local",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--json",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--output-last-message",
        str(last_message_path),
        f"Reply exactly {marker}",
    ]


def _run_codex(command: list[str], paths: dict[str, Path], *, work_dir: str, timeout_seconds: int) -> tuple[int, float]:
    env = dict(os.environ)
    env["CODEX_HOME"] = str(paths["codex_home"])
    started = time.monotonic()
    with paths["stdout"].open("w", encoding="utf-8") as stdout, paths["stderr"].open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=work_dir,
                env=env,
                stdin=subprocess.DEVNULL,
                text=True,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_seconds,
                check=False,
            )
            return completed.returncode, round(time.monotonic() - started, 3)
        except subprocess.TimeoutExpired:
            return 124, round(time.monotonic() - started, 3)


def _receipt(paths: dict[str, Path], command: list[str], exit_code: int, duration_seconds: float, args: argparse.Namespace) -> dict[str, Any]:
    combined = "\n".join([_read(paths["stdout"]), _read(paths["stderr"]), _read(paths["last_message"])])
    findings = _findings(combined, args.max_tokens_used)
    if exit_code != 0:
        findings.append({"code": "codex_smoke_exit_nonzero", "message": f"Codex exited with {exit_code}."})
    last_message = _read(paths["last_message"]).strip()
    if last_message != args.marker:
        findings.append({"code": "codex_smoke_marker_mismatch", "message": f"Expected {args.marker!r}; got {last_message!r}."})
    return {
        "schema_version": "skills-sdk.oss-local-smoke-run.v0",
        "status": "pass" if not findings else "fail",
        "command": command,
        "codex_profile": "oss-local",
        "model": _profile_value(paths["codex_home"] / "oss-local.config.toml", "model"),
        "model_provider": _profile_value(paths["codex_home"] / "oss-local.config.toml", "model_provider"),
        "work_dir": str(Path(args.work_dir).expanduser().resolve()),
        "duration_seconds": duration_seconds,
        "exit_code": exit_code,
        "marker": args.marker,
        "stdout_path": str(paths["stdout"]),
        "stderr_path": str(paths["stderr"]),
        "last_message_path": str(paths["last_message"]),
        "max_tokens_used": args.max_tokens_used,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds < 1:
        raise SystemExit("--timeout-seconds must be positive")
    paths = _prepare_paths(args)
    command = _codex_command(paths["last_message"], args.marker)
    exit_code, duration_seconds = _run_codex(command, paths, work_dir=args.work_dir, timeout_seconds=args.timeout_seconds)
    receipt = _receipt(paths, command, exit_code, duration_seconds, args)
    (paths["root"] / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2), encoding="utf-8")
    _write_receipt(receipt, emit_json=args.json)
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
