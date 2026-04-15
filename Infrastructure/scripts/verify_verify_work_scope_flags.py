#!/usr/bin/env python3
"""Fail if verify-work usage contract drifts from governance scope contract."""

from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_help(repo_root: Path) -> str:
    script_path = repo_root / "Infrastructure/scripts/verify-work.sh"
    try:
        script_text = script_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"could not read {script_path}: {exc}") from exc

    marker = "cat <<'USAGE'"
    start_marker = script_text.find(marker)
    if start_marker < 0:
        raise RuntimeError("verify-work usage block start marker not found")
    start = script_text.find("\n", start_marker)
    if start < 0:
        raise RuntimeError("verify-work usage block start line is malformed")
    start += 1

    end = script_text.find("\nUSAGE", start)
    if end < 0:
        raise RuntimeError("verify-work usage block end marker not found")
    return script_text[start:end]


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
        "--persistent-artifacts",
        "project-local scope (default)",
        "Validation artifacts are ephemeral.",
        "Validation artifacts are persistent.",
        "Backward-compatible alias for --workspace-governance",
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
