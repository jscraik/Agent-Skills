#!/usr/bin/env python3
"""Validate the repository-owned cache prelude in a generated prek hook."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path


START = "# agent-skills prek home begin"
END = "# agent-skills prek home end"


def validate_hook(hook_path: Path, repo_root: Path, git_common_dir: Path) -> None:
    """Validate one generated hook's cache prelude and command shape."""
    text = hook_path.read_text(encoding="utf-8")
    if "Agent Skills direct pre-commit shim." in text or "Agent Skills direct commit-message shim." in text:
        return
    commands = _extract_commands(text)
    root_assignment = _root_assignment(commands)
    _validate_root_assignment(root_assignment, repo_root, git_common_dir)
    if commands[1:] != _expected_commands():
        raise ValueError("generated hook cache prelude does not match the approved contract")


def _extract_commands(text: str) -> list[str]:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("generated hook must contain one cache prelude")
    block = text.split(START, 1)[1].split(END, 1)[0]
    commands = [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(commands) != 10:
        raise ValueError("generated hook cache prelude has an unexpected command count")
    return commands


def _root_assignment(commands: list[str]) -> str:
    root_assignments = [
        line for line in commands if line.startswith("export CODEX_HOOK_CACHE_ROOT=")
    ]
    if len(root_assignments) != 1:
        raise ValueError("generated hook must assign CODEX_HOOK_CACHE_ROOT once")
    return root_assignments[0]


def _validate_root_assignment(
    root_assignment: str, repo_root: Path, git_common_dir: Path
) -> None:
    root_value = _parse_root_value(root_assignment)
    _validate_root_path(root_value, repo_root, git_common_dir)
    if any(token in root_assignment for token in ("$", "`", ";", "&&", "||")):
        raise ValueError("generated hook cache root assignment contains shell syntax")
    if shlex.quote(root_value) != root_assignment.split("=", 1)[1]:
        raise ValueError("generated hook cache root assignment is not canonical shell quoting")


def _parse_root_value(root_assignment: str) -> str:
    try:
        root_tokens = shlex.split(root_assignment)
    except ValueError as exc:
        raise ValueError("generated hook cache root assignment is not shell syntax") from exc
    if (
        len(root_tokens) != 2
        or root_tokens[0] != "export"
        or not root_tokens[1].startswith("CODEX_HOOK_CACHE_ROOT=")
    ):
        raise ValueError("generated hook cache root assignment has an unexpected shape")
    return root_tokens[1].split("=", 1)[1]


def _validate_root_path(root_value: str, repo_root: Path, git_common_dir: Path) -> None:
    root_path = Path(root_value)
    if not root_path.is_absolute():
        raise ValueError("generated hook cache root must be absolute")
    root_path = root_path.resolve(strict=False)
    repo_root = repo_root.resolve()
    git_common_dir = git_common_dir.resolve()
    if (
        root_path == repo_root
        or repo_root in root_path.parents
        or root_path == git_common_dir
        or git_common_dir in root_path.parents
    ):
        raise ValueError("generated hook cache root must be outside repository metadata")

def _expected_commands() -> list[str]:
    return [
        'export PREK_HOME="$CODEX_HOOK_CACHE_ROOT/prek"',
        'AGENT_SKILLS_REPO_ROOT="$(git rev-parse --show-toplevel)"',
        'AGENT_SKILLS_GIT_COMMON_DIR="$(git rev-parse --path-format=absolute --git-common-dir)"',
        'source "$AGENT_SKILLS_REPO_ROOT/Infrastructure/scripts/lib/secure-hook-cache.sh"',
        'CODEX_HOOK_CACHE_ROOT="$(validate_hook_cache_path "$CODEX_HOOK_CACHE_ROOT" "$AGENT_SKILLS_REPO_ROOT" "$AGENT_SKILLS_GIT_COMMON_DIR")"',
        'PREK_HOME="$(validate_hook_cache_path "$PREK_HOME" "$AGENT_SKILLS_REPO_ROOT" "$AGENT_SKILLS_GIT_COMMON_DIR")"',
        'secure_hook_cache_dir "$CODEX_HOOK_CACHE_ROOT"',
        'secure_hook_cache_dir "$PREK_HOME"',
        'cd "$AGENT_SKILLS_REPO_ROOT"',
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("hook_path", type=Path)
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("git_common_dir", type=Path)
    args = parser.parse_args()
    try:
        validate_hook(args.hook_path, args.repo_root, args.git_common_dir)
    except (OSError, ValueError) as exc:
        print(f"generated hook validation failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
