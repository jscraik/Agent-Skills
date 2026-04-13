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
    """
    Parse CLI arguments for the runtime-separation wrapper script.
    
    Creates an ArgumentParser using the module docstring as the description and recognises the following options:
    - `--runtime-separation`: enable runtime-separation fixture checks.
    - `--repo-root`: optional repository root override (may be empty).
    
    Returns:
        args (argparse.Namespace): Namespace with attributes `runtime_separation` (bool) and `repo_root` (str).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-separation", action="store_true", help="Run runtime-separation fixture checks")
    parser.add_argument("--repo-root", default="", help="Repository root override")
    return parser.parse_args()


def _run_json(repo_root: Path, command: list[str], timeout_seconds: int) -> tuple[int, dict[str, Any]]:
    """
    Run an external command in repo_root and parse its stdout as a JSON object.
    
    Parameters:
    	repo_root (Path): Working directory for the command.
    	command (list[str]): Command and arguments to execute.
    	timeout_seconds (int): Seconds to wait before timing out the command.
    
    Returns:
    	tuple[int, dict[str, Any]]: A pair of the process exit code and the parsed JSON object from stdout.
    
    Raises:
    	SystemExit: If the command times out, if stdout is not valid JSON, or if the parsed JSON is not an object.
    """
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
    """
    Validate that the command at repo_root produced a JSON envelope matching the wrapper contract and return the parsed payload.
    
    Parameters:
        repo_root (Path): Working directory to run the command in.
        command (list[str]): Command and arguments to execute.
        timeout_seconds (int): Seconds to wait before timing out the command.
        require_success (bool): If True, treat a non-zero exit code as a failure and raise SystemExit.
    
    Returns:
        dict[str, Any]: The validated top-level JSON object (the envelope).
    
    Raises:
        SystemExit: If `require_success` is True and the command exited non‑zero; if required envelope keys are missing; if `metadata` is not an object or lacks `version` or `next_steps`; if `metadata["next_steps"]` is not a list; or if `status` is not one of "success", "error" or "partial".
    """
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
    """
    Run runtime-separation wrapper fixture checks and validate their JSON envelope contracts.
    
    Parses CLI arguments, requires the --runtime-separation flag, resolves the repository root, runs a set of `bin/ask ... --json` commands and validates each command's top-level JSON envelope. If an installed plugin is discovered from `plugins list`, its `plugins status <name> --json` envelope is also validated. On success prints a confirmation message and exits with code 0.
    
    Returns:
        int: 0 on success.
    
    Raises:
        SystemExit: if the required `--runtime-separation` flag is not provided.
    """
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
