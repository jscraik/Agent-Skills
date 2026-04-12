#!/usr/bin/env python3
"""Fail if verify-work help text drifts from governance scope contract."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_help(repo_root: Path) -> str:
    cmd = ["bash", "scripts/verify-work.sh", "--help"]
    completed = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        detail = stderr or stdout or "no output"
        raise RuntimeError(f"verify-work help command failed: {detail}")
    return completed.stdout


def _assert_contains(help_text: str, needle: str, failures: list[str]) -> None:
    if needle not in help_text:
        failures.append(f"missing required help token: {needle}")


def main() -> int:
    repo_root = _repo_root()
    try:
        help_text = _run_help(repo_root)
    except RuntimeError as exc:
        print(f"[verify_verify_work_scope_flags] {exc}")
        return 1

    failures: list[str] = []
    required_tokens = [
        "--project-governance",
        "--workspace-governance",
        "project-local scope (default)",
        "Validation artifacts are ephemeral.",
        "Validation artifacts are persistent.",
    ]
    for token in required_tokens:
        _assert_contains(help_text, token, failures)

    if failures:
        for failure in failures:
            print(f"[verify_verify_work_scope_flags] {failure}")
        return 1

    print("[verify_verify_work_scope_flags] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
