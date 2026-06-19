#!/usr/bin/env python3
"""Run skill diagnosis only for skill packages touched by a changed-files list."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DIAGNOSE_SKILL = REPO_ROOT / "Infrastructure" / "scripts" / "diagnose_skill.py"


def _nearest_skill_dir(changed_path: Path) -> Path | None:
    candidate = changed_path if changed_path.is_dir() else changed_path.parent
    try:
        candidate.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return None

    while candidate != REPO_ROOT and candidate != candidate.parent:
        if (candidate / "SKILL.md").is_file():
            return candidate
        candidate = candidate.parent
    return None


def changed_skill_dirs(changed_files_path: Path) -> list[Path]:
    skill_dirs: set[Path] = set()
    for raw_line in changed_files_path.read_text(encoding="utf-8").splitlines():
        raw_path = raw_line.strip()
        if not raw_path:
            continue
        changed_path = (REPO_ROOT / raw_path).resolve()
        if not changed_path.exists():
            continue
        skill_dir = _nearest_skill_dir(changed_path)
        if skill_dir is not None:
            skill_dirs.add(skill_dir)
    return sorted(skill_dirs, key=lambda path: path.relative_to(REPO_ROOT).as_posix())


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: diagnose_changed_skills.py <changed-files-list>", file=sys.stderr)
        return 2

    changed_files_path = Path(argv[1])
    if not changed_files_path.is_file():
        print(f"Changed-files list not found: {changed_files_path}", file=sys.stderr)
        return 2

    skill_dirs = changed_skill_dirs(changed_files_path)
    if not skill_dirs:
        print("Skipping skill diagnosis: push diff does not touch existing skill packages")
        return 0

    print(f"Diagnosing {len(skill_dirs)} changed skill package(s)...")
    exit_code = 0
    for skill_dir in skill_dirs:
        rel = skill_dir.relative_to(REPO_ROOT).as_posix()
        print(f"\n==> {rel}")
        result = subprocess.run([sys.executable, str(DIAGNOSE_SKILL), rel], cwd=REPO_ROOT)
        if result.returncode != 0:
            exit_code = result.returncode
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
