#!/usr/bin/env python3
"""Diagnose why a skill isn't loading in Codex.

Usage:
    python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py <skill-name>
    python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py --all  # Check all skills

Checks:
    1. SKILL.md exists and has valid YAML frontmatter
    2. Symlink exists in the expected loader directories
    3. Symlink points to correct location
    4. No nested .git directory (breaks skill discovery)
    5. Skill appears in root SKILL.md index
    6. Task profile exists if referenced
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT))
if str(SCRIPTS_ROOT / "lifecycle-and-sync") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "lifecycle-and-sync"))
if str(SCRIPTS_ROOT / "validation-and-linting") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "validation-and-linting"))

from verify_skill_catalog_freshness import analyze_skill_file, canonical_skill_map, discover_skill_files
from command_surface import resolve_skill_handle

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
SKILL_INDEX = REPO_ROOT / "SKILL.md"

CODEX_SKILLS = Path.home() / ".codex" / "skills"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"


@dataclass
class DiagnosticResult:
    check: str
    status: str  # "pass", "fail", "warn", "info", "skip"
    message: str
    details: Optional[str] = None


def find_skill_dir(skill_name: str) -> Optional[Path]:
    """Find skill directory by name, searching multiple locations."""
    candidate = Path(skill_name).expanduser()
    if candidate.exists():
        if candidate.is_file() and candidate.name == "SKILL.md":
            candidate = candidate.parent
        if candidate.is_dir() and (candidate / "SKILL.md").exists():
            return candidate.resolve()

    # Check flat skills directory first
    if SKILLS_DIR.is_dir():
        flat_path = SKILLS_DIR / skill_name
        if flat_path.is_dir() and (flat_path / "SKILL.md").exists():
            return flat_path

    # Check .system lane
    system_path = SKILLS_DIR / ".system" / skill_name
    if system_path.is_dir() and (system_path / "SKILL.md").exists():
        return system_path

    # Search topic-cluster directories under Skills/
    skills_root = REPO_ROOT / "Skills"
    if skills_root.is_dir():
        for category_dir in skills_root.iterdir():
            if not category_dir.is_dir():
                continue
            skill_path = category_dir / skill_name
            if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                return skill_path

    # Search plugin directories
    plugins_root = REPO_ROOT / "Plugins"
    if plugins_root.is_dir():
        plugin_candidates: List[Path] = []
        for plugin_skill_dir in plugins_root.rglob(skill_name):
            if not (plugin_skill_dir.is_dir() and (plugin_skill_dir / "SKILL.md").exists()):
                continue
            rel_parts = plugin_skill_dir.relative_to(plugins_root).parts
            # Archived fixture snapshots are not loadable runtime skills.
            if "fixtures" in rel_parts and "budget-archive" in rel_parts:
                continue
            plugin_candidates.append(plugin_skill_dir)

        if plugin_candidates:
            plugin_candidates.sort(key=lambda path: (len(path.parts), str(path)))
            return plugin_candidates[0]

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


def check_symlink(skill_name: str, target_dir: Path, label: str, allow_real_dir: bool = False) -> DiagnosticResult:
    """Check if a skill entry exists and points to the expected location."""
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
        if allow_real_dir and symlink_path.is_dir() and (symlink_path / "SKILL.md").exists():
            return DiagnosticResult(f"symlink ({label})", "pass", f"Directory entry OK in {target_dir}")
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


def check_workspace_flat_projection(skill_name: str) -> DiagnosticResult:
    """Check the SDK-flat workspace projection for a skill."""
    projected = SKILLS_DIR / skill_name / "SKILL.md"
    if not projected.is_file():
        return DiagnosticResult(
            "workspace projection",
            "fail",
            f"SDK-flat projection missing: {projected.relative_to(REPO_ROOT)}",
        )
    return DiagnosticResult(
        "workspace projection",
        "pass",
        f"SDK-flat projection OK: {projected.relative_to(REPO_ROOT)}",
    )


def is_plugin_owned_skill(skill_arg: str, skill_dir: Path) -> bool:
    """Return whether the audited skill is plugin-owned and not expected in the default runtime index."""
    candidate = Path(skill_arg).expanduser()
    paths = [candidate]
    if not candidate.is_absolute():
        paths.append(REPO_ROOT / candidate)
    paths.append(skill_dir)

    for path in paths:
        try:
            rel_parts = path.resolve().relative_to(REPO_ROOT).parts
        except ValueError:
            continue
        if rel_parts and rel_parts[0] == "Plugins":
            return True
    return False


def check_plugin_runtime_surface(skill_name: str, label: str) -> DiagnosticResult:
    """Skip default-runtime checks for plugin-owned skills."""
    return DiagnosticResult(
        f"symlink ({label})",
        "skip",
        f"Plugin-owned skill is not expected as a default user-runtime symlink: {skill_name}",
    )


def rooted_manifest_skill_set(skill_dir: Path) -> Optional[str]:
    """Return the rooted skill set that owns a latent skill, when known."""
    skill_md = (skill_dir / "SKILL.md").resolve()
    skillsets_dir = REPO_ROOT / ".skillsets"
    if not skillsets_dir.is_dir():
        return None

    for manifest_path in sorted(skillsets_dir.glob("*/manifest.jsonl")):
        try:
            lines = manifest_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue

        for line in lines:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            source_path = entry.get("source_path")
            if not source_path:
                continue
            if entry.get("runtime_visibility") != "latent":
                continue
            try:
                source_skill_md = (REPO_ROOT / source_path).resolve()
            except OSError:
                continue
            if source_skill_md == skill_md:
                return manifest_path.parent.name

    return None


def check_rooted_latent_runtime_surface(skill_name: str, skill_set: str, label: str) -> DiagnosticResult:
    """Skip flat symlink checks for latent skills routed by rooted manifests."""
    return DiagnosticResult(
        f"symlink ({label})",
        "skip",
        f"Rooted latent skill is routed through .skillsets/{skill_set}/manifest.jsonl "
        f"and is not expected as a first-level user-runtime symlink: {skill_name}",
    )


def check_skill_index(skill_name: str) -> DiagnosticResult:
    """Check if skill appears in root SKILL.md index."""
    if not SKILL_INDEX.exists():
        return DiagnosticResult("skill index", "skip", "Root SKILL.md not found")

    content = SKILL_INDEX.read_text(encoding="utf-8")
    if f"- `{skill_name}` —" in content:
        return DiagnosticResult("skill index", "pass", "Listed in SKILL.md index")
    else:
        return DiagnosticResult(
            "skill index",
            "info",
            "Not found in SKILL.md index",
            "Run `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` to regenerate the surfaced catalog.",
        )


def check_plugin_skill_index(skill_name: str) -> DiagnosticResult:
    """Skip root index checks for plugin-owned skills outside the default visible catalog."""
    return DiagnosticResult(
        "skill index",
        "skip",
        f"Plugin-owned skill is not expected in the root default visible skill index: {skill_name}",
    )


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
    default_rel = "Infrastructure/references/task-profile.json"
    default_path = skill_dir / default_rel
    if default_path.exists():
        return DiagnosticResult("task profile", "pass", f"Task profile exists (implicit path): {default_rel}")

    return DiagnosticResult("task profile", "skip", "No task profile found (neither legacy binding nor implicit path)")


def check_lifecycle_readiness(skill_dir: Path) -> DiagnosticResult:
    """Check governed lifecycle readiness for a skill."""
    skill_files = discover_skill_files(REPO_ROOT)
    canonical_by_name = canonical_skill_map(skill_files, REPO_ROOT)
    skill_file = skill_dir / "SKILL.md"
    try:
        rel_parts = skill_dir.resolve().relative_to(SKILLS_DIR.resolve()).parts
    except ValueError:
        rel_parts = ()
    if len(rel_parts) == 1:
        resolution = resolve_skill_handle(rel_parts[0], repo_root_path=REPO_ROOT)
        source_path = resolution.get("source_path") if resolution.get("status") == "ok" else None
        if isinstance(source_path, str):
            source_skill_file = REPO_ROOT / source_path
            if source_skill_file.is_file():
                skill_file = source_skill_file
    report = analyze_skill_file(skill_file, REPO_ROOT, canonical_by_name)

    if report.readiness == "blocked":
        return DiagnosticResult(
            "lifecycle readiness",
            "fail",
            "blocked",
            "; ".join(report.findings) or "governed asset is blocked",
        )
    if report.readiness == "degraded":
        return DiagnosticResult(
            "lifecycle readiness",
            "warn",
            "degraded",
            "; ".join(report.findings) or "governed asset is degraded",
        )
    if report.details:
        return DiagnosticResult("lifecycle readiness", "pass", "healthy", report.details)
    return DiagnosticResult("lifecycle readiness", "pass", "healthy")


def diagnose_skill(skill_name: str) -> List[DiagnosticResult]:
    """Run all diagnostic checks for a skill."""
    results: List[DiagnosticResult] = []

    # Find skill directory
    skill_dir = find_skill_dir(skill_name)
    if not skill_dir:
        results.append(DiagnosticResult("skill directory", "fail", f"Skill '{skill_name}' not found in repository"))
        return results

    results.append(DiagnosticResult("skill directory", "pass", f"Found at {skill_dir.relative_to(REPO_ROOT)}"))
    resolved_skill_name = skill_dir.name

    # Run checks
    results.append(check_skill_md(skill_dir))
    results.append(check_nested_git(skill_dir))
    # Skill audits may be invoked with a path argument (for example, utilities/my-skill).
    # Symlink/index checks must always use the canonical skill directory name.
    plugin_owned = is_plugin_owned_skill(skill_name, skill_dir)
    if plugin_owned:
        results.append(check_plugin_runtime_surface(resolved_skill_name, "codex"))
        results.append(check_plugin_runtime_surface(resolved_skill_name, "agents"))
        results.append(check_plugin_skill_index(resolved_skill_name))
    else:
        resolution = resolve_skill_handle(resolved_skill_name, repo_root_path=REPO_ROOT)
        sdk_flat = (
            resolution.get("status") == "ok"
            and resolution.get("handle_source") == "sdk_flat_registry"
            and resolution.get("runtime_visibility") == "flat"
        )
        if sdk_flat:
            results.append(check_workspace_flat_projection(resolved_skill_name))
            results.append(check_symlink(resolved_skill_name, CODEX_SKILLS, "codex"))
            results.append(check_symlink(resolved_skill_name, AGENTS_SKILLS, "agents"))
        elif rooted_skill_set := rooted_manifest_skill_set(skill_dir):
            results.append(check_rooted_latent_runtime_surface(resolved_skill_name, rooted_skill_set, "codex"))
            results.append(check_rooted_latent_runtime_surface(resolved_skill_name, rooted_skill_set, "agents"))
        else:
            results.append(check_symlink(resolved_skill_name, CODEX_SKILLS, "codex"))
            results.append(check_symlink(resolved_skill_name, AGENTS_SKILLS, "agents"))
        results.append(check_skill_index(resolved_skill_name))
    results.append(check_task_profile(skill_dir))
    results.append(check_lifecycle_readiness(skill_dir))

    return results


def format_result(result: DiagnosticResult) -> str:
    """Format a single result for display."""
    symbols = {"pass": "✓", "fail": "✗", "warn": "⚠", "info": "ℹ", "skip": "○"}
    colors = {"pass": "\033[32m", "fail": "\033[31m", "warn": "\033[33m", "info": "\033[36m", "skip": "\033[90m"}
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
    info_count = sum(1 for r in results if r.status == "info")

    for result in results:
        print(format_result(result))

    print("-" * 50)

    if fail_count > 0:
        print(f"❌ {fail_count} failure(s), {warn_count} warning(s), {info_count} advisory note(s)")
        return 1
    elif warn_count > 0:
        print(f"⚠️  {warn_count} warning(s), {info_count} advisory note(s)")
        return 0
    elif info_count > 0:
        print(f"ℹ️  {info_count} advisory note(s)")
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

    # From topic-cluster directories under Skills/
    skills_root = REPO_ROOT / "Skills"
    if skills_root.is_dir():
        for category_dir in skills_root.iterdir():
            if not category_dir.is_dir():
                continue
            for skill_dir in category_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skill_names.append(skill_dir.name)

    # From plugin skills under Plugins/
    plugins_root = REPO_ROOT / "Plugins"
    if plugins_root.is_dir():
        for plugin_dir in plugins_root.iterdir():
            if not plugin_dir.is_dir():
                continue
            plugin_skills = plugin_dir / "skills"
            if not plugin_skills.is_dir():
                continue
            for type_dir in plugin_skills.iterdir():
                if not type_dir.is_dir():
                    continue
                for skill_dir in type_dir.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        skill_names.append(skill_dir.name)

    # From .system lane
    system_lane = REPO_ROOT / ".agents" / "skills" / ".system"
    if system_lane.is_dir():
        for skill_dir in system_lane.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_names.append(skill_dir.name)

    skill_names = sorted(set(skill_names))

    print(f"🔍 Diagnosing {len(skill_names)} skills...\n")

    total_fails = 0
    total_warns = 0
    total_infos = 0
    failing_skills: List[str] = []
    warning_skills: List[str] = []
    advisory_skills: List[str] = []

    for skill_name in skill_names:
        results = diagnose_skill(skill_name)
        fails = sum(1 for r in results if r.status == "fail")
        warns = sum(1 for r in results if r.status == "warn")
        infos = sum(1 for r in results if r.status == "info")

        total_fails += fails
        total_warns += warns
        total_infos += infos
        if fails > 0:
            failing_skills.append(skill_name)
            print(f"✗ {skill_name}: {fails} fail(s), {warns} warn(s), {infos} advisory note(s)")
        elif warns > 0:
            warning_skills.append(skill_name)
            print(f"⚠ {skill_name}: {fails} fail(s), {warns} warn(s), {infos} advisory note(s)")
        elif infos > 0:
            advisory_skills.append(skill_name)
            print(f"ℹ {skill_name}: {infos} advisory note(s)")

    print()
    print(
        f"Summary: {len(skill_names)} skills, {total_fails} failures, "
        f"{total_warns} warnings, {total_infos} advisory notes"
    )

    if failing_skills:
        print(f"\nSkills with failures: {', '.join(failing_skills)}")
        return 1

    if warning_skills:
        print(f"\nSkills with warnings: {', '.join(warning_skills)}")

    if advisory_skills:
        print(f"\nSkills with advisory notes: {', '.join(advisory_skills)}")

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
