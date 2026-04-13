#!/usr/bin/env python3
"""Validate JSON envelope contracts for ask wrappers used by runtime-separation checks."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-separation", action="store_true", help="Run runtime-separation fixture checks")
    parser.add_argument("--repo-root", default="", help="Repository root override")
    return parser.parse_args()


def _run_json(repo_root: Path, command: list[str], timeout_seconds: int) -> tuple[int, dict[str, Any]]:
    try:
        proc = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"{' '.join(command)} timed out after {timeout_seconds}s") from exc

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{' '.join(command)} did not emit JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit(f"{' '.join(command)} did not emit a JSON object")
    return proc.returncode, payload


def _assert_envelope(
    repo_root: Path,
    command: list[str],
    timeout_seconds: int,
    *,
    require_success: bool = True,
) -> dict[str, Any]:
    exit_code, payload = _run_json(repo_root, command, timeout_seconds)
    if require_success and exit_code != 0:
        raise SystemExit(f"{' '.join(command)} exited {exit_code}")

    for key in ("status", "trace_id", "metadata", "data"):
        if key not in payload:
            raise SystemExit(f"{' '.join(command)} missing envelope key: {key}")

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise SystemExit(f"{' '.join(command)} metadata is not an object")
    for key in ("version", "next_steps"):
        if key not in metadata:
            raise SystemExit(f"{' '.join(command)} metadata missing key: {key}")
    if not isinstance(metadata.get("next_steps"), list):
        raise SystemExit(f"{' '.join(command)} metadata.next_steps is not a list")

    status = payload.get("status")
    if status not in {"success", "error", "partial"}:
        raise SystemExit(f"{' '.join(command)} returned invalid status: {status}")

    return payload


def main() -> int:
    args = parse_args()
    if not args.runtime_separation:
        raise SystemExit("missing required --runtime-separation flag")

    repo_root = Path(args.repo_root).expanduser() if args.repo_root else Path(__file__).resolve().parents[1]
    if not repo_root.is_absolute():
        repo_root = (Path.cwd() / repo_root).resolve()

    timeout_seconds = int(os.environ.get("WRAPPER_FIXTURE_TIMEOUT_SECONDS", "45"))

    commands = [
        ["bin/ask", "repo", "status", "--json"],
        ["bin/ask", "skills", "list", "--json"],
        ["bin/ask", "plugins", "doctor", "--json"],
    ]
    for command in commands:
        _assert_envelope(repo_root, command, timeout_seconds)

    plugin_name: str | None = None
    exit_code, plugins_payload = _run_json(repo_root, ["bin/ask", "plugins", "list", "--json"], timeout_seconds)
    if exit_code == 0:
        plugins = plugins_payload.get("data", {}).get("installed_state", {}).get("plugins", [])
        if isinstance(plugins, list) and plugins:
            candidate = plugins[0].get("name") if isinstance(plugins[0], dict) else None
            if isinstance(candidate, str) and candidate.strip():
                plugin_name = candidate.strip()

    if plugin_name:
        _assert_envelope(repo_root, ["bin/ask", "plugins", "status", plugin_name, "--json"], timeout_seconds)

    print("runtime-separation wrapper fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
