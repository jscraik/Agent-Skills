#!/usr/bin/env python3
"""Verify skill catalog freshness and phase-one lifecycle readiness."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SKIP_DIRS = {
    ".git",
    "artifacts",
    "node_modules",
    "docs",
    "skills",
    "skills-antigravity",
    "skills-antigravity-test",
    "templates",
    "references",
    "skills-system",
    ".worktrees",
}
SKIP_PATH_PREFIXES = {
    ("plugins", "cache"),
    (".agents", "plugins-runtime", "cache"),
    (".codex", ".tmp"),
    (".codex", "skills", ".system"),
}
SKIP_PATH_PARTS = {
    "fixtures",
}

PILOT_SKILL_PROFILE_PATHS = {
    "utilities/skill-builder",
    "frontend/tools/agentation",
    "utilities/systematic-debugging",
    "interview/interview-me",
}
LEARNING_POSTURE_VALUES = {"learn", "guided", "execute"}
AUTOPILOT_DEGRADED_ACCEPTED = "degraded_pairings_acknowledged"
VALID_LIFECYCLE_STATES = {"incubating", "active", "maintenance", "deprecated"}
VALID_MATURITY_LEVELS = {"experimental", "validated", "canonical"}
VALID_METADATA_SOURCES = {"frontmatter", "plugin_manifest", "inherited"}
GOVERNED_SKILL_PATHS = {
    "utilities/coding-harness/SKILL.md",
    "utilities/plugin-builder/SKILL.md",
    "utilities/skill-builder/SKILL.md",
    "plugins/skill-factory/skills/skill-builder/SKILL.md",
}
GOVERNED_PLUGIN_ALIAS_ENFORCED_PATHS = {
    "utilities/plugin-builder/SKILL.md",
}
GOVERNED_PLUGIN_MANIFEST_PATHS = {
    "plugins/skill-factory/.codex-plugin/plugin.json",
}
SOLUTION_SKIP_FILENAMES = {"README.md", "solution-entry-template.md"}
PLACEHOLDER_PATTERNS = (
    "[TODO:",
    "Replace with ",
    "adjacent-skill-name",
    "adjacent-router-or-skill",
    "[[topic-name]]",
)
CADENCE_DAYS = {
    "weekly": 7,
    "biweekly": 14,
    "monthly": 31,
    "quarterly": 92,
    "semiannual": 183,
    "annual": 366,
    "yearly": 366,
}
REQUIRED_SKILL_FIELDS = (
    "lifecycle_state",
    "maturity",
    "owner",
    "review_cadence",
    "metadata_source",
)


@dataclass
class AssetReport:
    path: Path
    kind: str
    readiness: str
    findings: List[str]
    details: Optional[str] = None


def parse_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def validate_learning_posture_profile(profile: Dict[str, Any], issues: List[str]) -> None:
    learning_posture = profile.get("learning_posture")
    if not isinstance(learning_posture, dict):
        issues.append("pilot skill missing required task-profile learning_posture block")
        return

    supported = learning_posture.get("supported")
    if not isinstance(supported, list) or not supported:
        issues.append("learning_posture.supported must be a non-empty list")
        return

    clean_supported = []
    for item in supported:
        posture = str(item).strip()
        if posture not in LEARNING_POSTURE_VALUES:
            issues.append(f"learning_posture.supported contains invalid value: `{posture}`")
        else:
            clean_supported.append(posture)

    default = str(learning_posture.get("default", "")).strip()
    if default not in LEARNING_POSTURE_VALUES:
        issues.append("learning_posture.default must be learn|guided|execute")
    elif default not in clean_supported:
        issues.append("learning_posture.default must be included in learning_posture.supported")

    delegation_mode = str(profile.get("delegation", {}).get("mode", "")).strip().lower()
    if delegation_mode == "autopilot":
        if "learn" in clean_supported:
            issues.append("invalid posture/mode pairing: autopilot cannot support learn")
        if "guided" in clean_supported:
            acknowledged = learning_posture.get(AUTOPILOT_DEGRADED_ACCEPTED)
            if not isinstance(acknowledged, list) or not acknowledged:
                issues.append(
                    "autopilot + guided is degraded and requires explicit "
                    "degraded_pairings_acknowledged entries"
                )
    elif delegation_mode in {"manual", "co-pilot"}:
        return
    elif delegation_mode:
        issues.append(f"delegation.mode must be autopilot | co-pilot | manual, found `{delegation_mode}`")
    else:
        issues.append("delegation.mode missing while validating pilot learning_posture constraints")


def discover_skill_files(repo_root: Path) -> List[Path]:
    files: Dict[str, Path] = {}
    for path in sorted(repo_root.rglob("SKILL.md")):
        rel = path.relative_to(repo_root)
        if rel.as_posix() == "SKILL.md":
            continue
        if should_skip_skill_path(rel):
            continue
        files[rel.as_posix()] = path

    # Some canonical aliases live under symlinked directories and may not be
    # traversed by rglob(). Include explicitly governed entries so lifecycle
    # validation always enforces governed path policy.
    for governed_rel in sorted(GOVERNED_SKILL_PATHS):
        candidate = repo_root / governed_rel
        if not candidate.is_file():
            continue
        if (
            governed_rel not in GOVERNED_PLUGIN_ALIAS_ENFORCED_PATHS
            and _resolves_into_plugin_tree(candidate, repo_root)
        ):
            continue
        rel = candidate.relative_to(repo_root)
        if rel.as_posix() == "SKILL.md":
            continue
        if should_skip_skill_path(rel):
            continue
        files[rel.as_posix()] = candidate

    return [files[key] for key in sorted(files)]


def _resolves_into_plugin_tree(path: Path, repo_root: Path) -> bool:
    """
    Return True when a path under a symlink alias ultimately resolves into plugins/.

    Governed utility aliases may point at packaged plugin skills; adding both
    paths to discovery makes strict lifecycle checks regress on valid alias
    layouts. We only force-include governed paths that remain outside plugins/.
    """
    try:
        resolved = path.resolve(strict=True)
        rel = resolved.relative_to(repo_root.resolve())
    except (FileNotFoundError, RuntimeError, ValueError):
        return False
    return bool(rel.parts) and rel.parts[0] == "plugins"


def should_skip_skill_path(rel: Path) -> bool:
    if rel.parts and rel.parts[0] in SKIP_DIRS:
        return True
    if any(part in SKIP_PATH_PARTS for part in rel.parts):
        return True
    for prefix in SKIP_PATH_PREFIXES:
        if rel.parts[: len(prefix)] == prefix:
            return True
    return False


def discover_plugin_manifests(repo_root: Path) -> List[Path]:
    return sorted(repo_root.glob("plugins/**/.codex-plugin/plugin.json"))


def discover_solution_files(repo_root: Path) -> List[Path]:
    solutions_dir = repo_root / "docs" / "solutions"
    if not solutions_dir.exists():
        return []
    return sorted(
        path
        for path in solutions_dir.rglob("*.md")
        if path.name not in SOLUTION_SKIP_FILENAMES
    )


def parse_frontmatter(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    result: Dict[str, str] = {}

    if len(lines) < 3 or lines[0].strip() != "---":
        return result

    idx = 1
    while idx < len(lines) and lines[idx].strip() != "---":
        line = lines[idx]
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("\"'")
        idx += 1

    return result


def parse_frontmatter_and_body(path: Path) -> Tuple[Dict[str, str], str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm = parse_frontmatter(path)
    if not fm:
        return {}, text

    lines = text.splitlines()
    idx = 1
    while idx < len(lines) and lines[idx].strip() != "---":
        idx += 1
    if idx >= len(lines):
        return {}, text
    return fm, "\n".join(lines[idx + 1 :]).strip()


def canonical_skill_map(skill_files: List[Path], repo_root: Path) -> Dict[str, Path]:
    mapping: Dict[str, Path] = {}
    plugin_only_candidates: Dict[str, Path] = {}
    for skill_file in skill_files:
        rel = skill_file.relative_to(repo_root).as_posix()
        name = parse_frontmatter(skill_file).get("name", "").strip()
        if not name:
            continue
        if rel.startswith("plugins/"):
            plugin_only_candidates.setdefault(name, skill_file)
            continue
        mapping.setdefault(name, skill_file)

    # Some canonical skill aliases are symlinked into non-plugin roots and may not
    # be discovered by rglob() in all environments. Include governed non-plugin
    # paths directly so packaged copies can still inherit canonical metadata.
    for governed_rel in sorted(GOVERNED_SKILL_PATHS):
        if governed_rel.startswith("plugins/"):
            continue
        candidate = repo_root / governed_rel
        if not candidate.exists():
            continue
        name = parse_frontmatter(candidate).get("name", "").strip()
        if name:
            mapping.setdefault(name, candidate)

    # Plugin-native skills without a non-plugin canonical counterpart inherit
    # lifecycle metadata from their plugin source of truth.
    for name, skill_file in plugin_only_candidates.items():
        mapping.setdefault(name, skill_file)
    return mapping


def readiness_rank(readiness: str) -> int:
    return {"healthy": 0, "degraded": 1, "blocked": 2}.get(readiness, 3)


def escalate(readiness: str, candidate: str) -> str:
    return candidate if readiness_rank(candidate) > readiness_rank(readiness) else readiness


def parse_iso_date(value: str) -> Optional[date]:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def cadence_window_days(review_cadence: str) -> Optional[int]:
    cadence = review_cadence.strip().lower()
    if cadence in CADENCE_DAYS:
        return CADENCE_DAYS[cadence]
    match = re.fullmatch(r"(\d+)\s*d", cadence)
    if match:
        return int(match.group(1))
    return None


def evaluate_overdue(review_cadence: str, last_reviewed: str, *, today: date) -> Optional[str]:
    cadence_days = cadence_window_days(review_cadence)
    reviewed_on = parse_iso_date(last_reviewed)
    if cadence_days is None or reviewed_on is None:
        return None
    if today > reviewed_on + timedelta(days=cadence_days):
        return (
            "stale_review_cadence: "
            f"review_cadence `{review_cadence}` is overdue from last_reviewed `{last_reviewed}`"
        )
    return None


def find_placeholder_text(text: str) -> List[str]:
    findings = []
    for token in PLACEHOLDER_PATTERNS:
        if token in text:
            findings.append(f"scaffold_quality_gap: contains starter placeholder token `{token}`")
    return findings


def is_packaged_skill(skill_path: Path, repo_root: Path) -> bool:
    return skill_path.relative_to(repo_root).as_posix().startswith("plugins/")


def has_lifecycle_metadata(frontmatter: Dict[str, str]) -> bool:
    return any(frontmatter.get(field, "").strip() for field in REQUIRED_SKILL_FIELDS + ("last_reviewed",))


def analyze_skill_file(
    path: Path,
    repo_root: Path,
    canonical_by_name: Dict[str, Path],
    *,
    today: Optional[date] = None,
) -> AssetReport:
    today = today or date.today()
    frontmatter, body = parse_frontmatter_and_body(path)
    rel = path.relative_to(repo_root).as_posix()
    readiness = "healthy"
    findings: List[str] = []
    details: Optional[str] = None

    if not frontmatter:
        return AssetReport(path=path, kind="skill", readiness="blocked", findings=["missing or invalid YAML frontmatter"])

    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()
    governed = rel in GOVERNED_SKILL_PATHS or has_lifecycle_metadata(frontmatter)
    packaged = is_packaged_skill(path, repo_root)

    if not name:
        findings.append("missing skill name in frontmatter")
        readiness = escalate(readiness, "blocked")
    if not description:
        findings.append("missing skill description in frontmatter")
        readiness = escalate(readiness, "blocked")
    elif len(description) < 20 or not re.search(r"[a-zA-Z]", description):
        findings.append("description quality is too low for reliable routing")
        readiness = escalate(readiness, "degraded")

    if name:
        skill_dir = rel.removesuffix("/SKILL.md")
        if skill_dir in PILOT_SKILL_PROFILE_PATHS:
            profile_path_str = frontmatter.get("knowledge_graph_profile", "").strip()
            profile_path = (path.parent / profile_path_str).resolve() if profile_path_str else path.parent / "references" / "task-profile.json"
            if not profile_path.exists():
                findings.append("pilot skill missing references/task-profile.json")
                readiness = escalate(readiness, "degraded")
            else:
                profile_payload = parse_json(profile_path)
                if profile_payload is None:
                    findings.append(f"pilot task-profile parse failed: {profile_path}")
                    readiness = escalate(readiness, "degraded")
                else:
                    profile_issues: List[str] = []
                    validate_learning_posture_profile(profile_payload, profile_issues)
                    if profile_issues:
                        findings.extend(profile_issues)
                        readiness = escalate(readiness, "degraded")

    findings.extend(find_placeholder_text(body))
    if any(item.startswith("scaffold_quality_gap:") for item in findings):
        readiness = escalate(readiness, "degraded")

    if not governed:
        return AssetReport(path=path, kind="skill", readiness=readiness, findings=findings)

    if packaged:
        canonical_path = canonical_by_name.get(name)
        if canonical_path is None:
            findings.append("representation_split_brain: packaged skill has no canonical source skill for inheritance")
            readiness = escalate(readiness, "blocked")
        else:
            details = f"inherits lifecycle metadata from {canonical_path.relative_to(repo_root)}"
            canonical_frontmatter = parse_frontmatter(canonical_path)
            for field in REQUIRED_SKILL_FIELDS + ("last_reviewed",):
                local_value = frontmatter.get(field, "").strip()
                canonical_value = canonical_frontmatter.get(field, "").strip()
                if local_value and canonical_value and local_value != canonical_value:
                    findings.append(
                        "representation_split_brain: "
                        f"packaged field `{field}` disagrees with canonical source `{canonical_path.relative_to(repo_root)}`"
                    )
                    readiness = escalate(readiness, "blocked")
            if canonical_frontmatter.get("owner", "").strip() and not frontmatter.get("metadata_source", "").strip():
                findings.append("metadata_source inherited from canonical skill")

        return AssetReport(path=path, kind="packaged_skill", readiness=readiness, findings=findings, details=details)

    for field in REQUIRED_SKILL_FIELDS:
        value = frontmatter.get(field, "").strip()
        if not value:
            findings.append(f"missing_metadata: governed skill missing `{field}`")
            readiness = escalate(readiness, "blocked")

    lifecycle_state = frontmatter.get("lifecycle_state", "").strip()
    if lifecycle_state and lifecycle_state not in VALID_LIFECYCLE_STATES:
        findings.append(f"missing_metadata: invalid lifecycle_state `{lifecycle_state}`")
        readiness = escalate(readiness, "blocked")

    maturity = frontmatter.get("maturity", "").strip()
    if maturity and maturity not in VALID_MATURITY_LEVELS:
        findings.append(f"missing_metadata: invalid maturity `{maturity}`")
        readiness = escalate(readiness, "blocked")

    metadata_source = frontmatter.get("metadata_source", "").strip()
    if metadata_source and metadata_source not in VALID_METADATA_SOURCES:
        findings.append(f"missing_metadata: invalid metadata_source `{metadata_source}`")
        readiness = escalate(readiness, "blocked")

    overdue = evaluate_overdue(
        frontmatter.get("review_cadence", "").strip(),
        frontmatter.get("last_reviewed", "").strip(),
        today=today,
    )
    if overdue:
        findings.append(overdue)
        readiness = escalate(readiness, "degraded")

    return AssetReport(path=path, kind="skill", readiness=readiness, findings=findings)


def analyze_plugin_manifest(path: Path, repo_root: Path, *, today: Optional[date] = None) -> AssetReport:
    today = today or date.today()
    payload = parse_json(path)
    rel = path.relative_to(repo_root).as_posix()
    readiness = "healthy"
    findings: List[str] = []

    if payload is None:
        return AssetReport(path=path, kind="plugin_manifest", readiness="blocked", findings=["invalid JSON manifest"])

    governed = rel in GOVERNED_PLUGIN_MANIFEST_PATHS or "governance" in payload
    if not governed:
        return AssetReport(path=path, kind="plugin_manifest", readiness="healthy", findings=[])

    if payload.get("schema_version") != 1:
        findings.append("missing_metadata: plugin manifest must declare schema_version 1")
        readiness = escalate(readiness, "blocked")
    if not str(payload.get("name", "")).strip():
        findings.append("missing_metadata: plugin manifest missing name")
        readiness = escalate(readiness, "blocked")
    if not str(payload.get("description", "")).strip():
        findings.append("missing_metadata: plugin manifest missing description")
        readiness = escalate(readiness, "blocked")

    governance = payload.get("governance")
    if not isinstance(governance, dict):
        findings.append("missing_metadata: governed plugin manifest missing governance block")
        readiness = escalate(readiness, "blocked")
        return AssetReport(path=path, kind="plugin_manifest", readiness=readiness, findings=findings)

    required_fields = ("lifecycle_state", "maturity", "owner", "review_cadence", "metadata_source")
    for field in required_fields:
        value = str(governance.get(field, "")).strip()
        if not value:
            findings.append(f"missing_metadata: governed plugin manifest missing `governance.{field}`")
            readiness = escalate(readiness, "blocked")

    lifecycle_state = str(governance.get("lifecycle_state", "")).strip()
    if lifecycle_state and lifecycle_state not in VALID_LIFECYCLE_STATES:
        findings.append(f"missing_metadata: invalid governance.lifecycle_state `{lifecycle_state}`")
        readiness = escalate(readiness, "blocked")

    maturity = str(governance.get("maturity", "")).strip()
    if maturity and maturity not in VALID_MATURITY_LEVELS:
        findings.append(f"missing_metadata: invalid governance.maturity `{maturity}`")
        readiness = escalate(readiness, "blocked")

    metadata_source = str(governance.get("metadata_source", "")).strip()
    if metadata_source and metadata_source != "plugin_manifest":
        findings.append("missing_metadata: governed plugin manifest must use metadata_source `plugin_manifest`")
        readiness = escalate(readiness, "blocked")

    overdue = evaluate_overdue(
        str(governance.get("review_cadence", "")).strip(),
        str(governance.get("last_reviewed", "")).strip(),
        today=today,
    )
    if overdue:
        findings.append(overdue)
        readiness = escalate(readiness, "degraded")

    return AssetReport(path=path, kind="plugin_manifest", readiness=readiness, findings=findings)


def analyze_solution_entry(path: Path, repo_root: Path, *, today: Optional[date] = None) -> AssetReport:
    today = today or date.today()
    frontmatter, body = parse_frontmatter_and_body(path)
    readiness = "healthy"
    findings: List[str] = []

    if not frontmatter:
        return AssetReport(path=path, kind="solution_entry", readiness="blocked", findings=["missing or invalid YAML frontmatter"])

    title = frontmatter.get("title", "").strip()
    governed_asset = frontmatter.get("governed_asset", "").strip()
    asset_family = frontmatter.get("asset_family", "").strip()
    source_artifact = frontmatter.get("source_artifact", "").strip()
    owner = frontmatter.get("owner", "").strip()
    freshness_reviewed_on = frontmatter.get("freshness_reviewed_on", "").strip()
    review_after_days = frontmatter.get("review_after_days", "").strip()

    if not title:
        findings.append("missing_metadata: solution entry missing `title`")
        readiness = escalate(readiness, "blocked")
    if not (governed_asset or asset_family):
        findings.append("orphaned_solution_link: solution entry must declare `governed_asset` or `asset_family`")
        readiness = escalate(readiness, "blocked")
    if not source_artifact:
        findings.append("missing_metadata: solution entry missing `source_artifact`")
        readiness = escalate(readiness, "blocked")
    if not owner:
        findings.append("unknown_owner: solution entry missing `owner`")
        readiness = escalate(readiness, "blocked")
    if not freshness_reviewed_on:
        findings.append("missing_metadata: solution entry missing `freshness_reviewed_on`")
        readiness = escalate(readiness, "blocked")
    if not review_after_days:
        findings.append("missing_metadata: solution entry missing `review_after_days`")
        readiness = escalate(readiness, "blocked")

    if "## Problem" not in body:
        findings.append("missing_metadata: solution entry missing `## Problem` section")
        readiness = escalate(readiness, "blocked")
    if "## Resolution" not in body:
        findings.append("missing_metadata: solution entry missing `## Resolution` section")
        readiness = escalate(readiness, "blocked")

    reviewed_on = parse_iso_date(freshness_reviewed_on) if freshness_reviewed_on else None
    try:
        review_window = int(review_after_days) if review_after_days else None
    except ValueError:
        review_window = None
    if freshness_reviewed_on and reviewed_on is None:
        findings.append("missing_metadata: freshness_reviewed_on must be an ISO date")
        readiness = escalate(readiness, "blocked")
    if review_after_days and review_window is None:
        findings.append("missing_metadata: review_after_days must be an integer day count")
        readiness = escalate(readiness, "blocked")
    if reviewed_on and review_window is not None and today > reviewed_on + timedelta(days=review_window):
        findings.append(
            "stale_review_cadence: "
            f"solution freshness is overdue from freshness_reviewed_on `{freshness_reviewed_on}`"
        )
        readiness = escalate(readiness, "degraded")

    return AssetReport(path=path, kind="solution_entry", readiness=readiness, findings=findings)


def analyze_repo(repo_root: Path, *, today: Optional[date] = None) -> Tuple[List[AssetReport], Dict[str, List[Path]]]:
    today = today or date.today()
    skill_files = discover_skill_files(repo_root)
    canonical_by_name = canonical_skill_map(skill_files, repo_root)
    reports: List[AssetReport] = []
    names_seen: Dict[str, List[Path]] = {}

    for skill_file in skill_files:
        report = analyze_skill_file(skill_file, repo_root, canonical_by_name, today=today)
        reports.append(report)
        name = parse_frontmatter(skill_file).get("name", "").strip()
        if name:
            if is_packaged_skill(skill_file, repo_root):
                canonical_path = canonical_by_name.get(name)
                # Packaged plugin copies inherit metadata from canonical skills and
                # should not count as duplicate catalog entries by themselves.
                if canonical_path is not None and canonical_path != skill_file:
                    continue
            names_seen.setdefault(name, []).append(skill_file)

    for manifest in discover_plugin_manifests(repo_root):
        reports.append(analyze_plugin_manifest(manifest, repo_root, today=today))

    for solution_entry in discover_solution_files(repo_root):
        reports.append(analyze_solution_entry(solution_entry, repo_root, today=today))

    duplicate_names = {name: paths for name, paths in names_seen.items() if len(paths) > 1 and name}
    return reports, duplicate_names


def render_report(report: AssetReport, repo_root: Path) -> str:
    rel = report.path.relative_to(repo_root)
    lines = [f"- {rel} [{report.kind}] -> {report.readiness}"]
    if report.details:
        lines.append(f"  - {report.details}")
    for finding in report.findings:
        lines.append(f"  - {finding}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify skill catalog freshness and lifecycle readiness")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--strict", action="store_true", help="Return non-zero when degraded or blocked reports are found")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root
    reports, duplicate_names = analyze_repo(repo_root)

    degraded_or_blocked = [report for report in reports if report.readiness in {"degraded", "blocked"}]
    readiness_counts = {
        "healthy": sum(1 for report in reports if report.readiness == "healthy"),
        "degraded": sum(1 for report in reports if report.readiness == "degraded"),
        "blocked": sum(1 for report in reports if report.readiness == "blocked"),
    }

    if degraded_or_blocked:
        print("Lifecycle readiness findings:")
        for report in degraded_or_blocked:
            print(render_report(report, repo_root))

    if duplicate_names:
        print("Duplicate skill names:")
        for name, paths in sorted(duplicate_names.items()):
            rendered = ", ".join(str(path.relative_to(repo_root)) for path in paths)
            print(f"- {name}: {rendered}")

    print(
        "Catalog check complete. "
        f"assets={len(reports)} healthy={readiness_counts['healthy']} "
        f"degraded={readiness_counts['degraded']} blocked={readiness_counts['blocked']} "
        f"duplicates={len(duplicate_names)}"
    )

    if args.strict and (degraded_or_blocked or duplicate_names):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
