#!/usr/bin/env python3
"""Verify the default Codex skill surface stays within runtime budget."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
if str(LIFECYCLE_DIR) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE_DIR))

from selection_policy import (  # type: ignore  # noqa: E402
    DEFAULT_VISIBLE_FLAT_SKILL_NAMES,
    SYSTEM_BRIDGE_SKILL_NAMES,
    policy_identity,
)
from skill_discovery import (  # type: ignore  # noqa: E402
    HIDDEN_FLAT_SKILL_NAMES as DISCOVERY_HIDDEN_FLAT_SKILL_NAMES,
    PLUGIN_HIDDEN_LANE_SKILL_NAMES as DISCOVERY_PLUGIN_HIDDEN_LANE_SKILL_NAMES,
    PLUGIN_VISIBLE_ROUTER_SKILL_NAMES as DISCOVERY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
    _is_plugin_owned_skill_dir,
    _iter_flat_skill_dirs,
    _iter_plugin_skill_dirs,
    _iter_repo_skill_dirs,
    _iter_system_lane_skill_dirs,
    discover_catalog_entries,
    discover_skill_entries,
)

DEFAULT_MAX_VISIBLE = 30
ADVANCED_WARN_VISIBLE = 60
BRIDGE_SKILLS = set(SYSTEM_BRIDGE_SKILL_NAMES)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _candidate_payload(*, name: str, source_dir: Path) -> dict[str, str]:
    rel_path = _rel(source_dir)
    category = Path(rel_path).parent.as_posix() or "uncategorized"
    return {
        "name": name,
        "path": rel_path,
        "category": category,
    }


def _iter_default_visibility_candidates() -> list[tuple[str, Path]]:
    """
    Return default-surface candidates before name deduplication.

    `discover_skill_entries` intentionally keeps only the first seen skill name.
    This helper preserves every candidate that survives default visibility
    filters so duplicate-name drift can be detected reliably.
    """
    skill_dirs = list(_iter_flat_skill_dirs())
    if not skill_dirs:
        skill_dirs = list(_iter_repo_skill_dirs())
        skill_dirs.extend(_iter_plugin_skill_dirs())
        skill_dirs.extend(_iter_system_lane_skill_dirs())

    candidates: list[tuple[str, Path]] = []
    for skill_dir in skill_dirs:
        source_dir = skill_dir.resolve()
        skill_md = source_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        name = skill_dir.name.strip() or source_dir.name
        if not name:
            continue
        if name in DISCOVERY_HIDDEN_FLAT_SKILL_NAMES:
            continue
        if name not in DEFAULT_VISIBLE_FLAT_SKILL_NAMES:
            continue
        plugin_owned = _is_plugin_owned_skill_dir(source_dir)
        if plugin_owned and name not in DISCOVERY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES:
            continue
        if plugin_owned and name in DISCOVERY_PLUGIN_HIDDEN_LANE_SKILL_NAMES:
            continue
        try:
            source_dir.relative_to(REPO_ROOT)
        except ValueError:
            continue
        candidates.append((name, source_dir))
    return candidates


def _first_level_skill_names() -> list[str]:
    skills_dir = REPO_ROOT / ".agents" / "skills"
    if not skills_dir.is_dir():
        return []
    names: list[str] = []
    for item in sorted(skills_dir.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir() and (item / "SKILL.md").exists():
            names.append(item.name)
    return names


def build_report(default_max: int = DEFAULT_MAX_VISIBLE) -> dict[str, Any]:
    default_entries = [entry for entry in discover_skill_entries(visibility="default") if entry.source_dir.is_relative_to(REPO_ROOT)]
    advanced_entries = [entry for entry in discover_skill_entries(visibility="advanced") if entry.source_dir.is_relative_to(REPO_ROOT)]
    catalog_entries = [entry for entry in discover_catalog_entries(advanced=False) if entry.source_dir.is_relative_to(REPO_ROOT)]

    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for name, source_dir in _iter_default_visibility_candidates():
        by_name[name].append(_candidate_payload(name=name, source_dir=source_dir))

    duplicate_default_names = {
        name: entries
        for name, entries in sorted(by_name.items())
        if len(entries) > 1
    }

    first_level = set(_first_level_skill_names())
    bridge_exposed = sorted(first_level & BRIDGE_SKILLS)
    policy_default = set(DEFAULT_VISIBLE_FLAT_SKILL_NAMES)
    # Bridge skills are intentionally not expected in default first-level discovery.
    # They can exist in policy metadata while remaining routed through the hidden
    # `.system` lane and are validated separately via BRIDGE_SKILLS_EXPOSED_FIRST_LEVEL.
    expected_default = policy_default - BRIDGE_SKILLS
    default_names = {entry.name for entry in default_entries}
    extra_default = sorted(default_names - expected_default)
    missing_default = sorted(expected_default - default_names)

    violations: list[dict[str, Any]] = []
    if len(default_entries) > default_max:
        violations.append({
            "code": "DEFAULT_SKILL_BUDGET_EXCEEDED",
            "message": f"default skill count {len(default_entries)} exceeds budget {default_max}",
        })
    if duplicate_default_names:
        violations.append({
            "code": "DUPLICATE_DEFAULT_SKILL_NAMES",
            "message": "default skill discovery contains duplicate names",
            "duplicates": duplicate_default_names,
        })
    if bridge_exposed:
        violations.append({
            "code": "BRIDGE_SKILLS_EXPOSED_FIRST_LEVEL",
            "message": "system bridge skills must not appear as first-level .agents/skills entries",
            "skills": bridge_exposed,
        })
    if extra_default or missing_default:
        violations.append({
            "code": "DEFAULT_POLICY_NAME_DRIFT",
            "message": "default discovery names differ from effective selection policy",
            "extra": extra_default,
            "missing": missing_default,
        })
    if sorted(entry.name for entry in catalog_entries) != sorted(entry.name for entry in default_entries):
        violations.append({
            "code": "CATALOG_DEFAULT_DRIFT",
            "message": "catalog default surface differs from discovery default surface",
        })

    return {
        "status": "pass" if not violations else "fail",
        "policy_identity": policy_identity(),
        "default_visible_count": len(default_entries),
        "default_visible_max": default_max,
        "advanced_visible_count": len(advanced_entries),
        "advanced_visible_warn": ADVANCED_WARN_VISIBLE,
        "catalog_default_count": len(catalog_entries),
        "system_bridge_skills": sorted(BRIDGE_SKILLS),
        "first_level_bridge_skills": bridge_exposed,
        "policy_default_skill_names": sorted(policy_default),
        "effective_default_policy_skill_names": sorted(expected_default),
        "default_visible_skill_names": sorted(default_names),
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default-max", type=int, default=DEFAULT_MAX_VISIBLE, help="Maximum default-visible skills")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    report = build_report(default_max=args.default_max)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"Runtime budget: {report['status']} "
            f"(default={report['default_visible_count']}/{report['default_visible_max']}, "
            f"advanced={report['advanced_visible_count']})"
        )
        for violation in report["violations"]:
            print(f"- {violation['code']}: {violation['message']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
