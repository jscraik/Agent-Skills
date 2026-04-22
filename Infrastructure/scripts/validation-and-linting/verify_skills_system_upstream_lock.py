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


def parse_args() -> argparse.Namespace:
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
    return hashlib.sha256(data).hexdigest()


def tree_digest(path: Path) -> str:
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
    if not condition:
        issues.append(message)


def emit_current(repo_root: Path, lock_payload: dict[str, Any]) -> int:
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
            continue
        name = str(item.get("name", "")).strip()
        rel = str(item.get("path", "")).strip()
        if not name or not rel:
            continue
        target = (repo_root / rel).resolve()
        snapshot["managed_dirs"].append(
            {
                "name": name,
                "path": rel,
                "tree_sha256": tree_digest(target),
            }
        )

    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


def main() -> int:
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

    if issues:
        print("skills-system upstream lock validation failed:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print("skills-system upstream lock validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
