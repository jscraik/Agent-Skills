#!/usr/bin/env python3
"""Validate coding-harness skill docs for current command contracts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILES = [
    "SKILL.md",
    "references/agent-install.json",
    "references/setup-and-commands.md",
    "references/agent-install-guide.md",
]

BANNED_PATTERNS = {
    "verify-greptile": re.compile(r"\bverify-greptile\b"),
    "request-greptile-review": re.compile(r"\brequest-greptile-review\b"),
    "Greptile Review": re.compile(r"\bGreptile Review\b"),
    "legacy preflight invocation": re.compile(
        r"source scripts/codex-preflight\.sh && preflight_repo"
    ),
}

REQUIRED_PATTERNS = {
    "verify-coderabbit": re.compile(r"\bverify-coderabbit\b"),
    "current preflight invocation": re.compile(
        r"bash scripts/codex-preflight\.sh --stack auto --mode required"
    ),
}


def load_files() -> list[tuple[Path, str]]:
    loaded: list[tuple[Path, str]] = []
    missing: list[str] = []
    for rel_path in TARGET_FILES:
        path = SKILL_ROOT / rel_path
        if not path.exists():
            missing.append(rel_path)
            continue
        loaded.append((path, path.read_text(encoding="utf-8")))

    if missing:
        print("FAIL missing expected files:")
        for item in missing:
            print(f"- {item}")
        sys.exit(1)
    return loaded


def find_line_number(text: str, match_start: int) -> int:
    return text.count("\n", 0, match_start) + 1


def main() -> int:
    files = load_files()
    violations: list[str] = []
    combined = "\n".join(text for _, text in files)

    for path, text in files:
        for label, pattern in BANNED_PATTERNS.items():
            for match in pattern.finditer(text):
                line = find_line_number(text, match.start())
                violations.append(f"{path.name}:{line}: banned pattern '{label}'")

    for label, pattern in REQUIRED_PATTERNS.items():
        if not pattern.search(combined):
            violations.append(f"missing required pattern '{label}'")

    if violations:
        print("FAIL reference contract check:")
        for item in violations:
            print(f"- {item}")
        return 1

    print("PASS reference contract check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
