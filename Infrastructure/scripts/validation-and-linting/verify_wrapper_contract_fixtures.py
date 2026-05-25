#!/usr/bin/env python3
"""Validate JSON envelope contracts for public ask wrapper fixtures."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_PROOF_HANDLE = "he-heartbeat"
DEFAULT_RUNTIME_PROOF_EVIDENCE_DIR = "/tmp/jsc-364-wrapper-codex-parity"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for public wrapper fixture checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-separation", action="store_true", help="Run runtime-separation fixture checks")
    parser.add_argument("--runtime-proof", action="store_true", help="Run runtime proof-plane fixture checks")
    parser.add_argument("--runtime-proof-handle", default=DEFAULT_RUNTIME_PROOF_HANDLE, help="Skill handle for proof-plane fixtures")
    parser.add_argument(
        "--runtime-proof-evidence-dir",
        default=DEFAULT_RUNTIME_PROOF_EVIDENCE_DIR,
        help="Evidence directory for proof-plane conformance fixtures",
    )
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


def _assert_path(payload: dict[str, Any], command_label: str, path: list[str]) -> Any:
    value: Any = payload
    traversed: list[str] = []
    for part in path:
        traversed.append(part)
        if not isinstance(value, dict) or part not in value:
            dotted = ".".join(traversed)
            raise SystemExit(f"{command_label} missing path: {dotted}")
        value = value[part]
    return value


def _assert_string_field(payload: dict[str, Any], command_label: str, path: list[str], expected: str | None = None) -> str:
    value = _assert_path(payload, command_label, path)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"{command_label} {'.'.join(path)} is not a non-empty string")
    if expected is not None and value != expected:
        raise SystemExit(f"{command_label} {'.'.join(path)} expected {expected!r}, got {value!r}")
    return value


def _assert_non_error_status(payload: dict[str, Any], command_label: str) -> None:
    status = payload.get("status")
    if status == "error":
        raise SystemExit(f"{command_label} returned error envelope")


def _assert_blockers(value: Any, command_label: str) -> None:
    if not isinstance(value, list) or not value:
        raise SystemExit(f"{command_label} blocked_runtime.blockers must be a non-empty list")
    for index, blocker in enumerate(value):
        if not isinstance(blocker, dict):
            raise SystemExit(f"{command_label} blocked_runtime.blockers[{index}] is not an object")
        if not any(isinstance(blocker.get(key), str) and blocker.get(key, "").strip() for key in ("rule_id", "message")):
            raise SystemExit(f"{command_label} blocked_runtime.blockers[{index}] missing rule_id or message")


def _assert_runtime_separation_fixtures(repo_root: Path, timeout_seconds: int) -> None:
    commands = [
        ["Infrastructure/bin/ask", "repo", "status", "--json"],
        ["Infrastructure/bin/ask", "skills", "list", "--json"],
        ["Infrastructure/bin/ask", "plugins", "doctor", "--json"],
    ]
    for command in commands:
        _assert_envelope(repo_root, command, timeout_seconds)

    plugin_name: str | None = None
    exit_code, plugins_payload = _run_json(repo_root, ["Infrastructure/bin/ask", "plugins", "list", "--json"], timeout_seconds)
    if exit_code == 0:
        plugins = plugins_payload.get("data", {}).get("installed_state", {}).get("plugins", [])
        if isinstance(plugins, list) and plugins:
            candidate = plugins[0].get("name") if isinstance(plugins[0], dict) else None
            if isinstance(candidate, str) and candidate.strip():
                plugin_name = candidate.strip()

    if plugin_name:
        _assert_envelope(repo_root, ["Infrastructure/bin/ask", "plugins", "status", plugin_name, "--json"], timeout_seconds)


def _assert_runtime_proof_fixtures(
    repo_root: Path,
    timeout_seconds: int,
    *,
    handle: str,
    evidence_dir: str,
) -> None:
    explain_command = ["Infrastructure/bin/ask", "skills", "explain", handle, "--json", "--robot"]
    explain_payload = _assert_envelope(repo_root, explain_command, timeout_seconds)
    _assert_string_field(
        explain_payload,
        "skills explain",
        ["data", "explanation", "reachability", "proof_command"],
        f"./bin/ask skills proof {handle} --json --robot",
    )
    _assert_string_field(
        explain_payload,
        "skills explain",
        ["data", "explanation", "next_command"],
        f"./bin/ask skills proof {handle} --json --robot",
    )

    proof_command = [
        "Infrastructure/bin/ask",
        "skills",
        "proof",
        handle,
        "--runtime-target",
        "any",
        "--json",
        "--robot",
    ]
    proof_payload = _assert_envelope(repo_root, proof_command, timeout_seconds, require_success=False)
    _assert_non_error_status(proof_payload, "skills proof")
    _assert_string_field(proof_payload, "skills proof", ["data", "proof", "schema_version"], "command-handle-proof.v2")
    proof_status = _assert_string_field(proof_payload, "skills proof", ["data", "proof", "status"])
    if proof_status not in {"pass", "fail"}:
        raise SystemExit(f"skills proof status is invalid: {proof_status}")
    if not isinstance(_assert_path(proof_payload, "skills proof", ["data", "proof", "gates"]), dict):
        raise SystemExit("skills proof gates is not an object")
    if not isinstance(_assert_path(proof_payload, "skills proof", ["data", "proof", "gate_policy"]), dict):
        raise SystemExit("skills proof gate_policy is not an object")

    conformance_command = [
        "Infrastructure/bin/ask",
        "skills",
        "conformance",
        "run",
        "--suite",
        "codex-parity",
        "--evidence-dir",
        evidence_dir,
        "--json",
        "--robot",
    ]
    conformance_payload = _assert_envelope(repo_root, conformance_command, timeout_seconds, require_success=False)
    _assert_non_error_status(conformance_payload, "skills conformance run")
    _assert_string_field(
        conformance_payload,
        "skills conformance run",
        ["data", "skills_conformance", "schema_version"],
        "skills-conformance-evidence.v1",
    )
    _assert_string_field(
        conformance_payload,
        "skills conformance run",
        ["data", "skills_conformance", "model_contract_status"],
        "pass",
    )
    live_status = _assert_string_field(
        conformance_payload,
        "skills conformance run",
        ["data", "skills_conformance", "live_parity_status"],
    )
    if live_status not in {"pass", "blocked_runtime", "not_checked"}:
        raise SystemExit(f"skills conformance run live_parity_status is invalid: {live_status}")
    blocked_runtime = _assert_path(conformance_payload, "skills conformance run", ["data", "skills_conformance", "blocked_runtime"])
    if not isinstance(blocked_runtime, dict):
        raise SystemExit("skills conformance run blocked_runtime is not an object")
    if live_status == "blocked_runtime":
        _assert_blockers(blocked_runtime.get("blockers"), "skills conformance run")


def main() -> int:
    """Run selected public wrapper fixture checks."""
    args = parse_args()

    repo_root = Path(args.repo_root).expanduser() if args.repo_root else Path(__file__).resolve().parents[3]
    if not repo_root.is_absolute():
        repo_root = (Path.cwd() / repo_root).resolve()

    timeout_seconds = int(os.environ.get("WRAPPER_FIXTURE_TIMEOUT_SECONDS", "45"))

    run_runtime_separation = args.runtime_separation or not args.runtime_proof
    run_runtime_proof = args.runtime_proof or not args.runtime_separation

    completed: list[str] = []
    if run_runtime_separation:
        _assert_runtime_separation_fixtures(repo_root, timeout_seconds)
        completed.append("runtime-separation")
    if run_runtime_proof:
        _assert_runtime_proof_fixtures(
            repo_root,
            timeout_seconds,
            handle=args.runtime_proof_handle,
            evidence_dir=args.runtime_proof_evidence_dir,
        )
        completed.append("runtime-proof")

    print(f"{', '.join(completed)} wrapper fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
