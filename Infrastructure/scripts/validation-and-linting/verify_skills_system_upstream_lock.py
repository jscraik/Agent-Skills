#!/usr/bin/env python3
"""Validate the pinned upstream lock for skills-system managed skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


LOCK_SCHEMA_VERSION = "skills-system-upstream-lock.v1"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
MCP_SERVER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
TOOL_PREFIX_RE = re.compile(r"^mcp__[A-Za-z][A-Za-z0-9_]*__$")
SURFACE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def parse_args() -> argparse.Namespace:
    """
    Build and parse command-line arguments for the skills-system validation CLI.
    
    Returns:
        namespace (argparse.Namespace): Parsed arguments with attributes:
            - repo_root (str): Repository root path.
            - lock (str): Path to the upstream lock JSON relative to repo root.
            - emit_current (bool): If true, emit current managed-directory digests as JSON and exit.
    """
    parser = argparse.ArgumentParser(
        description="Verify skills-system pin and managed directory digests."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--lock",
        default="Infrastructure/GOVERNANCE/skills-system-upstream.lock.json",
        help="Path to upstream lock JSON relative to repo root.",
    )
    parser.add_argument(
        "--emit-current",
        action="store_true",
        help="Emit current managed directory digests as JSON and exit.",
    )
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    """
    Compute the SHA-256 hexadecimal digest of the given bytes.
    
    Parameters:
        data (bytes): Input bytes to hash.
    
    Returns:
        str: Lowercase hexadecimal SHA-256 digest of `data`.
    """
    return hashlib.sha256(data).hexdigest()


def tree_digest(path: Path) -> str:
    """
    Compute a deterministic SHA-256 digest that represents the contents and structure of the directory tree rooted at `path`.
    
    Parameters:
        path (Path): Root directory to snapshot; must exist and be a directory.
    
    Returns:
        str: Lowercase hexadecimal SHA-256 digest (64 characters) of the directory tree.
    
    Raises:
        FileNotFoundError: If `path` does not exist.
        NotADirectoryError: If `path` exists but is not a directory.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_dir():
        raise NotADirectoryError(path)

    entries: list[str] = []
    for candidate in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
        rel = candidate.relative_to(path).as_posix()
        if candidate.is_dir() and not candidate.is_symlink():
            continue
        if candidate.is_symlink():
            target = candidate.readlink().as_posix()
            entries.append(f"L {rel}\0{target}")
            continue
        if candidate.is_file():
            entries.append(f"F {rel}\0{sha256_bytes(candidate.read_bytes())}")
            continue
        entries.append(f"O {rel}")
    return sha256_bytes("\n".join(entries).encode("utf-8"))


def _expect(condition: bool, message: str, issues: list[str]) -> None:
    """
    Append `message` to `issues` when `condition` is false.
    
    Parameters:
        condition (bool): Predicate to evaluate.
        message (str): Issue message to append if the predicate is false.
        issues (list[str]): Mutable list of issue messages that will be mutated in-place.
    """
    if not condition:
        issues.append(message)


def emit_current(repo_root: Path, lock_payload: dict[str, Any]) -> int:
    """
    Generate a snapshot of current tree digests for managed directories in the provided lock payload.
    
    Reads `managed_dirs` from `lock_payload`, computes a SHA-256 tree digest for each entry that is an object with non-empty `name` and `path`, and prints a JSON snapshot containing `schema_version` and `managed_dirs` entries of the form `{"name", "path", "tree_sha256"}`.
    
    Parameters:
        repo_root (Path): Base directory used to resolve each managed directory's relative `path`.
        lock_payload (dict[str, Any]): Parsed lock file content; expected to contain a `managed_dirs` list of objects with `name` and `path`.
    
    Returns:
        int: `0` on success; `1` if `managed_dirs` is missing or not a list.
    """
    managed = lock_payload.get("managed_dirs")
    if not isinstance(managed, list):
        print("lock file missing managed_dirs list", file=sys.stderr)
        return 1

    snapshot: dict[str, Any] = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "managed_dirs": [],
    }
    for item in managed:
        if not isinstance(item, dict):
            print(f"Warning: skipping malformed managed entry (not a dict): {item!r} (repo_root={repo_root})", file=sys.stderr)
            continue
        name = str(item.get("name", "")).strip()
        rel = str(item.get("path", "")).strip()
        if not name or not rel:
            print(f"Warning: skipping managed entry with missing name or path: {item!r} (repo_root={repo_root})", file=sys.stderr)
            continue
        target = (repo_root / rel).resolve()
        try:
            digest = tree_digest(target)
        except FileNotFoundError:
            print(f"Error: managed directory not found: {target} (from path={rel!r}, repo_root={repo_root})", file=sys.stderr)
            raise
        snapshot["managed_dirs"].append(
            {
                "name": name,
                "path": rel,
                "tree_sha256": digest,
            }
        )

    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


def _validate_upstream(payload: dict[str, Any], repo_root: Path, issues: list[str]) -> None:
    """
    Validate upstream section and schema_version in lock payload.

    Parameters:
        payload (dict[str, Any]): Parsed lock file content.
        repo_root (Path): Repository root directory.
        issues (list[str]): Mutable list of issue messages that will be mutated in-place.
    """
    _expect(
        payload.get("schema_version") == LOCK_SCHEMA_VERSION,
        f"schema_version must be {LOCK_SCHEMA_VERSION}",
        issues,
    )

    upstream = payload.get("upstream")
    _expect(isinstance(upstream, dict), "upstream must be an object", issues)
    if isinstance(upstream, dict):
        ref = str(upstream.get("ref", "")).strip()
        _expect(bool(SHA40_RE.match(ref)), "upstream.ref must be a 40-char lowercase sha", issues)
        _expect(
            str(upstream.get("repo", "")).strip() == "openai/skills",
            "upstream.repo must be openai/skills",
            issues,
        )
        _expect(
            str(upstream.get("path", "")).strip() == "skills/.system",
            "upstream.path must be skills/.system",
            issues,
        )

    marker = repo_root / "skills-system/.codex-system-skills.marker"
    _expect(marker.is_file(), "skills-system marker missing: skills-system/.codex-system-skills.marker", issues)


def _validate_bridge_entries(payload: dict[str, Any], repo_root: Path, issues: list[str]) -> None:
    """
    Validate bridge_entries section in lock payload.

    Parameters:
        payload (dict[str, Any]): Parsed lock file content.
        repo_root (Path): Repository root directory.
        issues (list[str]): Mutable list of issue messages that will be mutated in-place.
    """
    bridge_entries = payload.get("bridge_entries")
    _expect(isinstance(bridge_entries, list), "bridge_entries must be a list", issues)
    if isinstance(bridge_entries, list):
        for entry in bridge_entries:
            rel = str(entry).strip()
            if not rel:
                issues.append("bridge_entries contains an empty value")
                continue
            target = repo_root / rel
            if not target.exists() and not target.is_symlink():
                issues.append(f"missing bridge entry: {rel}")


def _validate_managed_dirs(payload: dict[str, Any], repo_root: Path, issues: list[str]) -> None:
    """
    Validate managed_dirs section in lock payload.

    Parameters:
        payload (dict[str, Any]): Parsed lock file content.
        repo_root (Path): Repository root directory.
        issues (list[str]): Mutable list of issue messages that will be mutated in-place.
    """
    managed = payload.get("managed_dirs")
    _expect(isinstance(managed, list), "managed_dirs must be a list", issues)
    if isinstance(managed, list):
        for item in managed:
            if not isinstance(item, dict):
                issues.append("managed_dirs items must be objects")
                continue
            name = str(item.get("name", "")).strip() or "<unnamed>"
            rel = str(item.get("path", "")).strip()
            expected = str(item.get("tree_sha256", "")).strip()
            if not rel:
                issues.append(f"{name}: path is required")
                continue
            if not re.match(r"^[0-9a-f]{64}$", expected):
                issues.append(f"{name}: tree_sha256 must be a 64-char lowercase sha256")
                continue
            target = repo_root / rel
            if not target.is_dir():
                issues.append(f"{name}: missing managed directory: {rel}")
                continue
            actual = tree_digest(target)
            if actual != expected:
                issues.append(
                    f"{name}: digest mismatch for {rel} (expected {expected}, got {actual})"
                )


def _validate_local_compatibility_overrides(payload: dict[str, Any], issues: list[str]) -> None:
    """
    Validate local_compatibility_overrides section in lock payload.

    Parameters:
        payload (dict[str, Any]): Parsed lock file content.
        issues (list[str]): Mutable list of issue messages that will be mutated in-place.
    """
    overrides = payload.get("local_compatibility_overrides")
    _expect(
        isinstance(overrides, list),
        "local_compatibility_overrides must be a list",
        issues,
    )
    if not isinstance(overrides, list):
        return

    for index, item in enumerate(overrides):
        label = f"local_compatibility_overrides[{index}]"
        if not isinstance(item, dict):
            issues.append(f"{label} must be an object")
            continue

        surface_raw = item.get("surface", "")
        mcp_server_raw = item.get("mcp_server", "")
        tool_prefix_raw = item.get("tool_prefix", "")

        # Verify types are strings before validation
        if not isinstance(surface_raw, str):
            issues.append(f"{label}.surface must be a string")
            surface_raw = ""  # Prevent further validation
        if not isinstance(mcp_server_raw, str):
            issues.append(f"{label}.mcp_server must be a string")
            mcp_server_raw = ""  # Prevent further validation
        if not isinstance(tool_prefix_raw, str):
            issues.append(f"{label}.tool_prefix must be a string")
            tool_prefix_raw = ""  # Prevent further validation

        # Only validate strings (strip and check regex)
        surface = surface_raw.strip() if isinstance(surface_raw, str) else ""
        mcp_server = mcp_server_raw.strip() if isinstance(mcp_server_raw, str) else ""
        tool_prefix = tool_prefix_raw.strip() if isinstance(tool_prefix_raw, str) else ""

        # Check for non-empty surface and mcp_server
        if isinstance(surface_raw, str) and not surface:
            issues.append(f"{label}.surface must be a non-empty string")
        if isinstance(mcp_server_raw, str) and not mcp_server:
            issues.append(f"{label}.mcp_server must be a non-empty string")

        # Proceed with regex validation only when values are present
        if surface and not SURFACE_RE.fullmatch(surface):
            issues.append(f"{label}.surface must match {SURFACE_RE.pattern}")
        if mcp_server and not MCP_SERVER_RE.fullmatch(mcp_server):
            issues.append(f"{label}.mcp_server must match {MCP_SERVER_RE.pattern}")
        if tool_prefix and not TOOL_PREFIX_RE.fullmatch(tool_prefix):
            issues.append(f"{label}.tool_prefix must match {TOOL_PREFIX_RE.pattern}")
        # Only run cross-check when both surface and mcp_server are present and valid
        if (isinstance(mcp_server_raw, str) and isinstance(tool_prefix_raw, str)
            and mcp_server and tool_prefix and tool_prefix != f"mcp__{mcp_server}__"):
            issues.append(
                f"{label}.tool_prefix must align with mcp_server "
                f"(expected mcp__{mcp_server}__)"
            )


def main() -> int:
    """
    Validate a skills-system upstream lock file according to the tool's schema and exit with a status code.
    
    Performs these high-level actions: parses CLI arguments, loads and JSON-decodes the specified lock file, validates required top-level fields (including schema_version and upstream metadata), checks presence of the repository marker file, verifies bridge_entries refer to existing paths or symlinks, and validates each managed_dirs entry by confirming the path exists and its computed tree SHA-256 matches the declared `tree_sha256`. When invoked with `--emit-current` the function emits a JSON snapshot of current managed directory digests instead of performing validation. Validation failures and structural/JSON errors are printed to stderr.
    
    Returns:
        int: `0` on successful validation or successful `--emit-current`; `1` on missing lock file, invalid JSON, structural/schema/validation failures, or other validation errors.
    """
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    lock_path = (repo_root / args.lock).resolve()

    if not lock_path.is_file():
        print(f"lock file missing: {lock_path}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"invalid JSON in lock file: {exc}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict):
        print("lock payload root must be an object", file=sys.stderr)
        return 1

    if args.emit_current:
        return emit_current(repo_root, payload)

    issues: list[str] = []
    _validate_upstream(payload, repo_root, issues)
    _validate_bridge_entries(payload, repo_root, issues)
    _validate_managed_dirs(payload, repo_root, issues)
    _validate_local_compatibility_overrides(payload, issues)

    if issues:
        print("skills-system upstream lock validation failed:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print("skills-system upstream lock validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
