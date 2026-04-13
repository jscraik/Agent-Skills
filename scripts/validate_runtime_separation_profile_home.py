#!/usr/bin/env python3
"""Emit profile-home runtime-separation artifact from an existing current artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """
    Builds and parses the command-line arguments for the script.
    
    The parser recognises three options used by the script to locate inputs and control output.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - output (str): Path to write the generated artifact (required).
            - repo_current (str): Path to the runtime-separation current artifact; empty string if not provided (defaults to GOVERNANCE/runtime-separation/current.json when empty).
            - repo_root (str): Repository root override; empty string if not provided (defaults to the script's parent directory when empty).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Output artifact path")
    parser.add_argument(
        "--repo-current",
        default="",
        help="Path to runtime-separation current artifact (defaults to GOVERNANCE/runtime-separation/current.json)",
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root override (defaults to script parent directory)",
    )
    return parser.parse_args()


def _json_digest(value: Any) -> str:
    """
    Compute a SHA-256 hex digest of the canonical JSON serialization of a value.
    
    Parameters:
        value (Any): JSON-serialisable Python object; keys are sorted and compact separators are used during serialization.
    
    Returns:
        str: Hexadecimal SHA-256 digest of the UTF-8 encoded JSON serialization.
    """
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    """
    Load and return a JSON object from the given filesystem path.
    
    Parameters:
        path (Path): Filesystem path to a UTF-8 encoded JSON file.
    
    Returns:
        dict[str, Any]: The parsed JSON object.
    
    Raises:
        ValueError: If the JSON root is not an object.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def main() -> int:
    """
    Generate a runtime-separation profile-home JSON artifact from an existing "current" artifact and write it to the specified output path.
    
    Resolves repository and input/output paths, loads and validates the current artifact's `summary` object, normalises and derives required summary fields (including computing SHA-256 JSON digests when absent), constructs the profile-home payload with schema version `runtime-separation.profile-home.v1`, and writes the resulting JSON file to the provided output path.
    
    Returns:
        int: Exit code (0 on success).
    
    Raises:
        SystemExit: If the current artifact is missing a valid `summary` object.
    """
    args = parse_args()

    repo_root = Path(args.repo_root).expanduser() if args.repo_root else Path(__file__).resolve().parents[1]
    if not repo_root.is_absolute():
        repo_root = (Path.cwd() / repo_root).resolve()

    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = (repo_root / output_path).resolve()

    repo_current_override = Path(args.repo_current).expanduser() if args.repo_current else None
    if repo_current_override is not None and not repo_current_override.is_absolute():
        repo_current_override = (repo_root / repo_current_override).resolve()
    current_path = repo_current_override or (repo_root / "GOVERNANCE" / "runtime-separation" / "current.json")

    current = _load_json(current_path)
    summary = current.get("summary")
    if not isinstance(summary, dict):
        raise SystemExit(f"runtime-separation profile-home: missing summary in {current_path}")

    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in os.sys.path:
        os.sys.path.insert(0, str(scripts_dir))

    from selection_policy import payload as selection_payload, policy_identity  # type: ignore

    policy_id = summary.get("policy_identity")
    if not isinstance(policy_id, str) or not policy_id:
        policy_id = policy_identity()

    discovery_id = summary.get("discovery_identity")
    if not isinstance(discovery_id, str) or not discovery_id:
        discovery_id = policy_id

    canonical_root_digest = summary.get("canonical_root_digest")
    if not isinstance(canonical_root_digest, str) or not canonical_root_digest:
        canonical_root_digest = _json_digest(selection_payload())

    command_checks = summary.get("command_checks")
    if not isinstance(command_checks, dict):
        command_checks = {}

    plugin_package_root_parity = summary.get("plugin_package_root_parity")
    if not isinstance(plugin_package_root_parity, list):
        plugin_package_root_parity = []

    command_checks_digest = summary.get("command_checks_digest")
    if not isinstance(command_checks_digest, str) or not command_checks_digest:
        command_checks_digest = _json_digest(command_checks)

    payload = {
        "schema_version": "runtime-separation.profile-home.v1",
        "profile_home_root": str(repo_root),
        "summary": {
            "policy_identity": policy_id,
            "discovery_identity": discovery_id,
            "canonical_root_digest": canonical_root_digest,
            "command_checks": command_checks,
            "plugin_package_root_parity": plugin_package_root_parity,
            "command_checks_digest": command_checks_digest,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"runtime-separation profile-home artifact written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
