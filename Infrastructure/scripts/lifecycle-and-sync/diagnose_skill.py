#!/usr/bin/env python3
"""Diagnose why a skill is not loading in Codex.

Usage:
    python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py <skill-name>
    python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py --all
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT))
if str(SCRIPTS_ROOT / "validation-and-linting") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "validation-and-linting"))

from verify_skill_catalog_freshness import analyze_skill_file, canonical_skill_map, discover_skill_files

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
SKILL_INDEX = REPO_ROOT / "SKILL.md"

CODEX_SKILLS = Path.home() / ".codex" / "skills"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"


@dataclass
class DiagnosticResult:
    check: str
    status: str  # pass | fail | warn | skip
    message: str
    details: Optional[str] = None


def find_skill_dir(skill_name: str) -> Optional[Path]:
    candidate = Path(skill_name).expanduser()
    if candidate.exists():
        if candidate.is_file() and candidate.name == "SKILL.md":
            candidate = candidate.parent
        if candidate.is_dir() and (candidate / "SKILL.md").exists():
            return candidate.resolve()

    if SKILLS_DIR.is_dir():
        flat_path = SKILLS_DIR / skill_name
        if flat_path.is_dir() and (flat_path / "SKILL.md").exists():
            return flat_path

    system_path = SKILLS_DIR / ".system" / skill_name
    if system_path.is_dir() and (system_path / "SKILL.md").exists():
        return system_path

    for root in (REPO_ROOT / "Skills", REPO_ROOT / "Plugins"):
        if not root.is_dir():
            continue
        for path in root.rglob(skill_name):
            if path.is_dir() and (path / "SKILL.md").exists():
                rel_parts = path.relative_to(REPO_ROOT).parts
                if "fixtures" in rel_parts and "budget-archive" in rel_parts:
                    continue
                return path
    return None


def check_skill_md(skill_dir: Path) -> DiagnosticResult:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return DiagnosticResult("SKILL.md", "fail", "SKILL.md not found")

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return DiagnosticResult("SKILL.md", "fail", "Missing YAML frontmatter")

    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return DiagnosticResult("SKILL.md", "fail", "Invalid frontmatter format")

    frontmatter = fm_match.group(1)
    has_name = bool(re.search(r"^name:\s*.+$", frontmatter, re.MULTILINE))
    has_desc = bool(re.search(r"^description:\s*.+$", frontmatter, re.MULTILINE))

    if not has_name:
        return DiagnosticResult("SKILL.md", "fail", "Missing name in frontmatter")
    if not has_desc:
        return DiagnosticResult("SKILL.md", "warn", "Missing description in frontmatter")

    return DiagnosticResult("SKILL.md", "pass", "Valid YAML frontmatter")


def check_nested_git(skill_dir: Path) -> DiagnosticResult:
    nested_git = skill_dir / ".git"
    if nested_git.exists():
        return DiagnosticResult(
            "nested .git",
            "fail",
            "Nested .git directory detected",
            f"Remove nested git metadata: rm -rf {nested_git}",
        )
    return DiagnosticResult("nested .git", "pass", "No nested .git directory")


def check_loader_entry(skill_name: str, target_dir: Path, label: str) -> DiagnosticResult:
    if not target_dir.exists():
        return DiagnosticResult(f"loader ({label})", "skip", f"Directory not present: {target_dir}")

    entry = target_dir / skill_name
    if not entry.exists():
        return DiagnosticResult(f"loader ({label})", "warn", f"Skill entry not found: {entry}")

    if not entry.is_symlink() and not (entry.is_dir() and (entry / "SKILL.md").exists()):
        return DiagnosticResult(f"loader ({label})", "warn", f"Entry exists but is not a valid skill directory: {entry}")

    try:
        resolved = entry.resolve()
        source = find_skill_dir(skill_name)
        if source and resolved != source.resolve():
            return DiagnosticResult(
                f"loader ({label})",
                "warn",
                f"Entry points to unexpected location: {resolved}",
                f"Expected: {source.resolve()}",
            )
    except Exception as exc:
        return DiagnosticResult(f"loader ({label})", "fail", f"Cannot resolve entry: {exc}")

    return DiagnosticResult(f"loader ({label})", "pass", f"Entry OK in {target_dir}")


def check_skill_index(skill_name: str) -> DiagnosticResult:
    if not SKILL_INDEX.exists():
        return DiagnosticResult("SKILL index", "fail", f"Missing index file: {SKILL_INDEX}")

    text = SKILL_INDEX.read_text(encoding="utf-8")
    if f"`{skill_name}`" in text:
        return DiagnosticResult("SKILL index", "pass", "Skill appears in SKILL.md")
    return DiagnosticResult("SKILL index", "warn", "Skill not found in SKILL.md")


def diagnose_skill(skill_name: str) -> List[DiagnosticResult]:
    results: List[DiagnosticResult] = []
    skill_dir = find_skill_dir(skill_name)

    if not skill_dir:
        results.append(DiagnosticResult("discovery", "fail", f"Skill not found: {skill_name}"))
        return results

    results.append(DiagnosticResult("discovery", "pass", f"Found skill: {skill_dir}"))
    results.append(check_skill_md(skill_dir))
    results.append(check_nested_git(skill_dir))
    results.append(check_loader_entry(skill_name, CODEX_SKILLS, "codex"))
    results.append(check_loader_entry(skill_name, AGENTS_SKILLS, "agents"))
    results.append(check_skill_index(skill_name))

    return results


def print_results(skill_name: str, results: List[DiagnosticResult]) -> bool:
    print(f"\n=== Diagnosing: {skill_name} ===")
    has_fail = False
    for result in results:
        icon = {
            "pass": "PASS",
            "fail": "FAIL",
            "warn": "WARN",
            "skip": "SKIP",
        }.get(result.status, "INFO")
        print(f"{icon:4} [{result.check}] {result.message}")
        if result.details:
            print(f"     {result.details}")
        if result.status == "fail":
            has_fail = True
    return not has_fail


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose skill loading issues in Codex")
    parser.add_argument("skill_name", nargs="?", help="Skill name to diagnose")
    parser.add_argument("--all", action="store_true", help="Diagnose all catalog skills")
    args = parser.parse_args()

    if not args.all and not args.skill_name:
        parser.error("Specify <skill-name> or --all")

    skill_names: List[str] = []
    if args.all:
        discovered = discover_skill_files(REPO_ROOT)
        for report in discovered.values():
            analysis = analyze_skill_file(REPO_ROOT, report.path)
            if analysis and analysis.frontmatter.get("name"):
                skill_names.append(str(analysis.frontmatter.get("name")))
        skill_names = sorted(set(skill_names))
    else:
        skill_names = [args.skill_name]

    overall_ok = True
    for name in skill_names:
        ok = print_results(name, diagnose_skill(name))
        if not ok:
            overall_ok = False

    print("\n=== Summary ===")
    print(f"Skills checked: {len(skill_names)}")
    print(f"Result: {PASS if overall_ok else FAIL}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
