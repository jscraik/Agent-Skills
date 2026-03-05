#!/usr/bin/env python3
"""Diagnose why a skill isn't loading in Codex or Claude Code.

Usage:
    python3 scripts/diagnose_skill.py <skill-name>
    python3 scripts/diagnose_skill.py --all  # Check all skills

Checks:
    1. SKILL.md exists and has valid YAML frontmatter
    2. Symlink exists in ~/.agents/skills/, ~/.codex/skills/, and ~/.claude/skills/
    3. Symlink points to correct location
    4. No nested .git directory (breaks skill discovery)
    5. Skill appears in root SKILL.md index
    6. Task profile exists if referenced
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
SKILL_INDEX = REPO_ROOT / "SKILL.md"

CODEX_SKILLS = Path.home() / ".codex" / "skills"
CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"


@dataclass
class DiagnosticResult:
    check: str
    status: str  # "pass", "fail", "warn", "skip"
    message: str
    details: Optional[str] = None


def find_skill_dir(skill_name: str) -> Optional[Path]:
    """Find skill directory by name, searching multiple locations."""
    # Check flat skills directory first
    if SKILLS_DIR.is_dir():
        flat_path = SKILLS_DIR / skill_name
        if flat_path.is_dir() and (flat_path / "SKILL.md").exists():
            return flat_path

    # Search category folders
    for category_dir in REPO_ROOT.iterdir():
        if not category_dir.is_dir():
            continue
        if category_dir.name.startswith(".") or category_dir.name in ("skills", "skills-system", "skills-antigravity", ".agents"):
            continue
        skill_path = category_dir / skill_name
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            return skill_path

    return None


def check_skill_md(skill_dir: Path) -> DiagnosticResult:
    """Check if SKILL.md exists and has valid frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return DiagnosticResult("SKILL.md", "fail", "SKILL.md not found")

    content = skill_md.read_text(encoding="utf-8")

    # Check for YAML frontmatter
    if not content.startswith("---"):
        return DiagnosticResult("SKILL.md", "fail", "Missing YAML frontmatter")

    # Extract frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return DiagnosticResult("SKILL.md", "fail", "Invalid frontmatter format")

    frontmatter = fm_match.group(1)

    # Check for required fields
    has_name = bool(re.search(r"^name:\s*.+$", frontmatter, re.MULTILINE))
    has_desc = bool(re.search(r"^description:\s*.+$", frontmatter, re.MULTILINE))

    if not has_name:
        return DiagnosticResult("SKILL.md", "fail", "Missing 'name' in frontmatter")
    if not has_desc:
        return DiagnosticResult("SKILL.md", "warn", "Missing 'description' in frontmatter")

    return DiagnosticResult("SKILL.md", "pass", "Valid YAML frontmatter with name and description")


def check_nested_git(skill_dir: Path) -> DiagnosticResult:
    """Check for nested .git directory (breaks skill discovery)."""
    nested_git = skill_dir / ".git"
    if nested_git.exists():
        return DiagnosticResult(
            "nested .git",
            "fail",
            "Nested .git directory detected - this breaks skill loading",
            "Remove the nested .git: rm -rf {}/.git".format(skill_dir)
        )
    return DiagnosticResult("nested .git", "pass", "No nested .git directory")


def check_symlink(skill_name: str, target_dir: Path, label: str) -> DiagnosticResult:
    """Check if symlink exists and points to correct location."""
    if not target_dir.exists():
        return DiagnosticResult(
            f"symlink ({label})",
            "skip",
            f"Target skill directory not present in this environment: {target_dir}",
        )

    symlink_path = target_dir / skill_name

    if not symlink_path.exists():
        return DiagnosticResult(f"symlink ({label})", "warn", f"Symlink not found in {target_dir}")

    if not symlink_path.is_symlink():
        return DiagnosticResult(f"symlink ({label})", "warn", f"Exists but not a symlink in {target_dir}")

    # Resolve symlink target
    try:
        resolved = symlink_path.resolve()
        skill_dir = find_skill_dir(skill_name)
        if skill_dir and resolved != skill_dir.resolve():
            return DiagnosticResult(
                f"symlink ({label})",
                "warn",
                f"Symlink points to unexpected location: {resolved}"
            )
    except Exception as e:
        return DiagnosticResult(f"symlink ({label})", "fail", f"Cannot resolve symlink: {e}")

    return DiagnosticResult(f"symlink ({label})", "pass", f"Symlink OK in {target_dir}")


def check_skill_index(skill_name: str) -> DiagnosticResult:
    """Check if skill appears in root SKILL.md index."""
    if not SKILL_INDEX.exists():
        return DiagnosticResult("skill index", "skip", "Root SKILL.md not found")

    content = SKILL_INDEX.read_text(encoding="utf-8")
    # Look for skill name as a markdown list item: - `skill-name` —
    escaped_name = re.escape(skill_name)
    pattern = rf"^- `({escaped_name})`\s*—"
    if re.search(pattern, content, re.MULTILINE):
        return DiagnosticResult("skill index", "pass", "Listed in SKILL.md index")
    else:
        return DiagnosticResult("skill index", "warn", "Not found in SKILL.md index (run sync_skills.sh)")


def check_task_profile(skill_dir: Path) -> DiagnosticResult:
    """Check if task profile exists via legacy binding or implicit default path."""
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Legacy explicit binding (non-official frontmatter key).
    profile_match = re.search(r"^knowledge_graph_profile:\s*(.+)$", content, re.MULTILINE)
    if profile_match:
        profile_path = profile_match.group(1).strip()
        full_path = skill_dir / profile_path

        if not full_path.exists():
            return DiagnosticResult("task profile", "warn", f"Referenced profile not found: {profile_path}")

        return DiagnosticResult("task profile", "pass", f"Task profile exists (legacy binding): {profile_path}")

    # Official/frontmatter-minimal path: profile is discovered by convention.
    default_rel = "references/task-profile.json"
    default_path = skill_dir / default_rel
    if default_path.exists():
        return DiagnosticResult("task profile", "pass", f"Task profile exists (implicit path): {default_rel}")

    return DiagnosticResult("task profile", "skip", "No task profile found (neither legacy binding nor implicit path)")


def diagnose_skill(skill_name: str) -> List[DiagnosticResult]:
    """Run all diagnostic checks for a skill."""
    results: List[DiagnosticResult] = []

    # Find skill directory
    skill_dir = find_skill_dir(skill_name)
    if not skill_dir:
        results.append(DiagnosticResult("skill directory", "fail", f"Skill '{skill_name}' not found in repository"))
        return results

    results.append(DiagnosticResult("skill directory", "pass", f"Found at {skill_dir.relative_to(REPO_ROOT)}"))

    # Run checks
    results.append(check_skill_md(skill_dir))
    results.append(check_nested_git(skill_dir))
    results.append(check_symlink(skill_name, CODEX_SKILLS, "codex"))
    results.append(check_symlink(skill_name, CLAUDE_SKILLS, "claude"))
    results.append(check_symlink(skill_name, AGENTS_SKILLS, "agents"))
    results.append(check_skill_index(skill_name))
    results.append(check_task_profile(skill_dir))

    return results


def format_result(result: DiagnosticResult) -> str:
    """Format a single result for display."""
    symbols = {"pass": "✓", "fail": "✗", "warn": "⚠", "skip": "○"}
    colors = {"pass": "\033[32m", "fail": "\033[31m", "warn": "\033[33m", "skip": "\033[90m"}
    reset = "\033[0m"

    symbol = symbols.get(result.status, "?")
    color = colors.get(result.status, "")
    line = f"  {color}{symbol}{reset} {result.check}: {result.message}"
    if result.details:
        line += f"\n      → {result.details}"
    return line


def print_report(skill_name: str, results: List[DiagnosticResult]) -> int:
    """Print diagnostic report and return exit code."""
    print(f"\n📋 Diagnostic report: {skill_name}")
    print("-" * 50)

    fail_count = sum(1 for r in results if r.status == "fail")
    warn_count = sum(1 for r in results if r.status == "warn")

    for result in results:
        print(format_result(result))

    print("-" * 50)

    if fail_count > 0:
        print(f"❌ {fail_count} failure(s), {warn_count} warning(s)")
        return 1
    elif warn_count > 0:
        print(f"⚠️  {warn_count} warning(s)")
        return 0
    else:
        print("✅ All checks passed")
        return 0


def diagnose_all_skills() -> int:
    """Diagnose all skills and return exit code."""
    # Find all skill directories
    skill_names: List[str] = []

    # From flat skills directory
    if SKILLS_DIR.is_dir():
        for item in SKILLS_DIR.iterdir():
            if item.is_symlink() and (item / "SKILL.md").exists():
                skill_names.append(item.name)

    # From category directories
    for category_dir in REPO_ROOT.iterdir():
        if not category_dir.is_dir():
            continue
        if category_dir.name.startswith(".") or category_dir.name in ("skills", "skills-system", "skills-antigravity", "scripts", "artifacts", "docs", "references", "templates"):
            continue
        for skill_dir in category_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_names.append(skill_dir.name)

    skill_names = sorted(set(skill_names))

    print(f"🔍 Diagnosing {len(skill_names)} skills...\n")

    total_fails = 0
    total_warns = 0
    failing_skills: List[str] = []
    warning_skills: List[str] = []

    for skill_name in skill_names:
        results = diagnose_skill(skill_name)
        fails = sum(1 for r in results if r.status == "fail")
        warns = sum(1 for r in results if r.status == "warn")

        total_fails += fails
        total_warns += warns
        if fails > 0:
            failing_skills.append(skill_name)
            symbol = "✗" if fails > 0 else "⚠"
            print(f"{symbol} {skill_name}: {fails} fail(s), {warns} warn(s)")
        elif warns > 0:
            warning_skills.append(skill_name)
            print(f"⚠ {skill_name}: {fails} fail(s), {warns} warn(s)")

    print()
    print(f"Summary: {len(skill_names)} skills, {total_fails} failures, {total_warns} warnings")

    if failing_skills:
        print(f"\nSkills with failures: {', '.join(failing_skills)}")
        return 1

    if warning_skills:
        print(f"\nSkills with warnings: {', '.join(warning_skills)}")

    print("\n✅ All skills healthy")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Diagnose skill loading issues")
    p.add_argument("skill_name", nargs="?", help="Skill name to diagnose")
    p.add_argument("--all", action="store_true", help="Diagnose all skills")
    args = p.parse_args()

    if args.all:
        return diagnose_all_skills()

    if not args.skill_name:
        p.error("Specify a skill name or use --all")

    results = diagnose_skill(args.skill_name)
    return print_report(args.skill_name, results)


if __name__ == "__main__":
    raise SystemExit(main())
