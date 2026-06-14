#!/usr/bin/env python3
"""Validate JSON envelope contracts for public ask wrapper fixtures."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_PROOF_HANDLE = "he-phase-work"
DEFAULT_RUNTIME_PROOF_EVIDENCE_DIR = ""
DARWIN_CONFSTR_WARNING = "warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"


def parse_args() -> argparse.Namespace:
    """
    Builds and returns the CLI argument namespace for public wrapper fixture checks.
    
    The returned namespace contains the flags and options that control which fixture suites run and where to operate:
    - runtime_separation (bool): run runtime-separation fixture checks.
    - runtime_proof (bool): run runtime proof-plane fixture checks.
    - runtime_proof_handle (str): skill handle used for proof-plane fixtures (default from module constant).
    - runtime_proof_evidence_dir (str): evidence directory used for proof-plane conformance fixtures (default from module constant).
    - repo_root (str): repository root override; empty string means use the script's default resolution.
    
    Returns:
        argparse.Namespace: Parsed CLI arguments with the attributes described above.
    """
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

    stdout = _strip_known_platform_stdout_noise(proc.stdout)
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{' '.join(command)} did not emit JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit(f"{' '.join(command)} did not emit a JSON object")
    return proc.returncode, payload


def _strip_known_platform_stdout_noise(stdout: str) -> str:
    """Remove known macOS hook-runner warnings that can precede wrapper JSON."""
    lines = stdout.splitlines()
    while lines and lines[0].endswith(DARWIN_CONFSTR_WARNING):
        lines.pop(0)
    if not lines:
        return stdout
    return "\n".join(lines) + ("\n" if stdout.endswith("\n") else "")


def _assert_envelope(
    repo_root: Path,
    command: list[str],
    timeout_seconds: int,
    *,
    require_success: bool = True,
) -> dict[str, Any]:
    """
    Validate a wrapper command's JSON envelope against the required contract and return the parsed payload.
    
    Parameters:
        repo_root (Path): Directory to run the command in.
        command (list[str]): Command and arguments to execute.
        timeout_seconds (int): Seconds to wait before timing out the command.
        require_success (bool): If True, treat a non-zero process exit code as a failure and raise SystemExit.
    
    Returns:
        dict[str, Any]: The validated top-level JSON object (the envelope).
    
    Raises:
        SystemExit: If `require_success` is True and the command exited non-zero; if the payload is missing any of the top-level keys `status`, `trace_id`, `metadata`, or `data`; if `metadata` is not an object or lacks `version` or `next_steps`; if `metadata["next_steps"]` is not a list; or if `status` is not one of `"success"`, `"error"`, or `"partial"`.
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
    """
    Locate and return a nested value from a JSON-like mapping by following a sequence of keys.
    
    Parameters:
        payload (dict[str, Any]): Top-level mapping to traverse.
        command_label (str): Label used in error messages to identify the command producing `payload`.
        path (list[str]): Sequence of keys representing the nested path to locate (in order).
    
    Returns:
        Any: The value found at the end of `path` within `payload`.
    
    Raises:
        SystemExit: If any intermediate value is not a mapping or a key along `path` is missing; the error message includes `command_label` and the dotted missing path.
    """
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
    """
    Validate and return a non-empty string located at the given nested path in a JSON payload.
    
    Parameters:
        payload (dict[str, Any]): Parsed JSON envelope to inspect.
        command_label (str): Human-readable label for the command used in error messages.
        path (list[str]): Sequence of keys describing the nested path to the target field.
        expected (str | None): If provided, require the field's value to exactly match this string.
    
    Returns:
        str: The trimmed, non-empty string value found at the specified path.
    
    Raises:
        SystemExit: If path traversal fails, the located value is not a non-empty string, or it does not match `expected`.
    """
    value = _assert_path(payload, command_label, path)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"{command_label} {'.'.join(path)} is not a non-empty string")
    if expected is not None and value != expected:
        raise SystemExit(f"{command_label} {'.'.join(path)} expected {expected!r}, got {value!r}")
    return value


def _assert_non_error_status(payload: dict[str, Any], command_label: str) -> None:
    """
    Abort execution when the envelope's top-level status indicates an error.
    
    Raises SystemExit with a message including `command_label` if `payload["status"]` equals "error".
    
    Parameters:
        payload (dict[str, Any]): Parsed top-level JSON envelope to inspect.
        command_label (str): Human-readable label for the command used in the error message.
    
    Raises:
        SystemExit: If the envelope's `status` is `"error"`.
    """
    status = payload.get("status")
    if status == "error":
        raise SystemExit(f"{command_label} returned error envelope")


def _assert_blockers(value: Any, command_label: str) -> None:
    """
    Validate that `blocked_runtime.blockers` is a non-empty list of valid blocker objects.
    
    Each element must be a dict and must contain at least one of the keys `"rule_id"` or `"message"`
    with a non-empty, non-whitespace string value. On validation failure, raises SystemExit with an
    error message prefixed by `command_label` describing the failing path.
    
    Parameters:
        value (Any): The value to validate as `blocked_runtime.blockers`.
        command_label (str): Label identifying the command used in error messages.
    """
    if not isinstance(value, list) or not value:
        raise SystemExit(f"{command_label} blocked_runtime.blockers must be a non-empty list")
    for index, blocker in enumerate(value):
        if not isinstance(blocker, dict):
            raise SystemExit(f"{command_label} blocked_runtime.blockers[{index}] is not an object")
        required_fields = ("rule_id", "message")
        if not all(
            isinstance(blocker.get(key), str) and blocker.get(key, "").strip()
            for key in required_fields
        ):
            raise SystemExit(f"{command_label} blocked_runtime.blockers[{index}] missing rule_id or message")


def _assert_runtime_separation_fixtures(repo_root: Path, timeout_seconds: int) -> None:
    """
    Validate the runtime-separation wrapper fixtures by running several wrapper commands and asserting their JSON envelopes conform to the expected contract.
    
    Runs the repository status, skills list, and plugins doctor commands and validates each command's top-level JSON envelope. If an installed plugin is discovered from the plugins list, also validates the plugins status command for that plugin.
    
    Parameters:
    	repo_root (Path): Filesystem path to the repository root where wrapper commands are executed.
    	timeout_seconds (int): Maximum time in seconds to wait for each command to complete.
    """
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
    """
    Validate runtime-proof fixtures for a given skill handle by running the wrapper's `skills explain`, `skills proof`, and `skills conformance run` commands and asserting their JSON envelopes conform to expected schema and values.
    
    Parameters:
    	repo_root (Path): Repository root used as the working directory for invoked wrapper commands.
    	timeout_seconds (int): Per-command timeout in seconds.
    	handle (str): Skill handle to use for explain and proof commands.
    	evidence_dir (str): Evidence directory path passed to the conformance run command.
    
    Raises:
    	SystemExit: If any command times out, emits non-JSON output, returns a malformed envelope, fails required status/schema checks, contains invalid enumerated values, or when required blocker structures are missing or malformed.
    """
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
    """
    Run the selected wrapper fixture suites (runtime-separation and/or runtime-proof) and report success.
    
    Depending on CLI flags, executes runtime-separation and/or runtime-proof validations against the repository root and prints which suites passed.
    
    Returns:
        int: Exit code 0 on success.
    """
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
        runtime_proof_evidence_dir = args.runtime_proof_evidence_dir or tempfile.mkdtemp(
            prefix="jsc-364-wrapper-codex-parity-"
        )
        _assert_runtime_proof_fixtures(
            repo_root,
            timeout_seconds,
            handle=args.runtime_proof_handle,
            evidence_dir=runtime_proof_evidence_dir,
        )
        completed.append("runtime-proof")

    print(f"{', '.join(completed)} wrapper fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
