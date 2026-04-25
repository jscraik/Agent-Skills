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
    DEFAULT_PROJECTION_MODE,
    ROOT_SKILL_SET_NAMES,
    SYSTEM_BRIDGE_SKILL_NAMES,
    policy_identity,
)
from skill_discovery import (  # type: ignore  # noqa: E402
    HIDDEN_FLAT_SKILL_NAMES as DISCOVERY_HIDDEN_FLAT_SKILL_NAMES,
    PLUGIN_HIDDEN_LANE_SKILL_NAMES as DISCOVERY_PLUGIN_HIDDEN_LANE_SKILL_NAMES,
    PLUGIN_VISIBLE_ROUTER_SKILL_NAMES as DISCOVERY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
    USER_SKILL_SCOPE_PRECEDENCE,
    classify_skill_scope,
    discover_catalog_entries,
    discover_skill_entries,
    is_plugin_owned_skill_dir,
    iter_flat_skill_dirs,
    iter_plugin_skill_dirs,
    iter_repo_skill_dirs,
    iter_system_lane_skill_dirs,
)

DEFAULT_MAX_VISIBLE = 30
ADVANCED_WARN_VISIBLE = 60
BRIDGE_SKILLS = set(SYSTEM_BRIDGE_SKILL_NAMES)
ROOT_SKILL_SETS = set(ROOT_SKILL_SET_NAMES)
SCOPE_PRECEDENCE = USER_SKILL_SCOPE_PRECEDENCE


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


def _word_count(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def _estimated_tokens_from_words(words: int) -> int:
    return (words * 4 + 2) // 3


def _first_level_skill_entries() -> list[dict[str, str]]:
    skills_dir = REPO_ROOT / ".agents" / "skills"
    if not skills_dir.is_dir():
        return []
    entries: list[dict[str, str]] = []
    for item in sorted(skills_dir.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir() and (item / "SKILL.md").exists():
            entries.append(_candidate_payload(name=item.name, source_dir=item.resolve()))
    return entries


def _system_lane_entries() -> list[dict[str, str]]:
    entries = [
        _candidate_payload(name=skill_dir.name, source_dir=skill_dir)
        for skill_dir in iter_system_lane_skill_dirs()
    ]
    return sorted(entries, key=lambda entry: (entry["name"], entry["path"]))


def _iter_known_skill_dirs() -> list[Path]:
    seen: set[tuple[int, int] | str] = set()
    dirs: list[Path] = []
    for skill_dir in [
        *iter_repo_skill_dirs(),
        *iter_plugin_skill_dirs(),
        *iter_system_lane_skill_dirs(),
    ]:
        try:
            stat = skill_dir.stat()
            key: tuple[int, int] | str = (stat.st_dev, stat.st_ino)
        except OSError:
            key = skill_dir.resolve().as_posix()
        if key in seen or not (skill_dir / "SKILL.md").exists():
            continue
        seen.add(key)
        dirs.append(skill_dir)
    return sorted(dirs, key=lambda path: _rel(path))


def _scope_payloads() -> tuple[dict[str, int], list[dict[str, str]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_scope: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)

    for skill_dir in _iter_known_skill_dirs():
        name = skill_dir.name
        scope = classify_skill_scope(skill_dir)
        payload = {
            **_candidate_payload(name=name, source_dir=skill_dir),
            "scope": scope,
        }
        by_scope[scope].append(payload)
        if scope in SCOPE_PRECEDENCE:
            by_name[name].append(payload)

    scope_counts = {
        scope: len(by_scope.get(scope, []))
        for scope in ("global", "project", "local-plugin", "system", "primary-runtime", "unknown", "external")
    }
    entries = [
        payload
        for scope_entries in by_scope.values()
        for payload in scope_entries
    ]
    shadowed_entries: list[dict[str, Any]] = []
    unresolved_scope_collisions: list[dict[str, Any]] = []
    for name, candidates in sorted(by_name.items()):
        if len(candidates) < 2:
            continue
        max_rank = max(SCOPE_PRECEDENCE[candidate["scope"]] for candidate in candidates)
        winners = [candidate for candidate in candidates if SCOPE_PRECEDENCE[candidate["scope"]] == max_rank]
        if len(winners) != 1:
            unresolved_scope_collisions.append({
                "name": name,
                "candidates": candidates,
            })
            continue
        winner = winners[0]
        shadowed_entries.append({
            "name": name,
            "selected": winner,
            "suppressed": [candidate for candidate in candidates if candidate != winner],
        })

    return scope_counts, entries, shadowed_entries, unresolved_scope_collisions


def _largest_description_payloads(entries: list[Any], *, limit: int = 10) -> list[dict[str, Any]]:
    payloads = []
    for entry in entries:
        words = _word_count(entry.description)
        payloads.append({
            "name": entry.name,
            "path": _rel(entry.source_dir),
            "description_words": words,
            "description": entry.description,
        })
    return sorted(payloads, key=lambda payload: (-payload["description_words"], payload["name"]))[:limit]


def _iter_default_visibility_candidates() -> list[tuple[str, Path]]:
    """
    Return default-surface candidates before name deduplication.

    `discover_skill_entries` intentionally keeps only the first seen skill name.
    This helper preserves every candidate that survives default visibility
    filters so duplicate-name drift can be detected reliably.
    """
    skill_dirs = list(iter_flat_skill_dirs())
    if not skill_dirs:
        skill_dirs = list(iter_repo_skill_dirs())
        skill_dirs.extend(iter_plugin_skill_dirs())
        skill_dirs.extend(iter_system_lane_skill_dirs())

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
        plugin_owned = is_plugin_owned_skill_dir(source_dir)
        if plugin_owned and name not in DISCOVERY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES:
            continue
        if plugin_owned and name in DISCOVERY_PLUGIN_HIDDEN_LANE_SKILL_NAMES:
            continue
        try:
            skill_dir.relative_to(REPO_ROOT)
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
    default_entries = list(discover_skill_entries(visibility="default"))
    advanced_entries = list(discover_skill_entries(visibility="advanced"))
    catalog_entries = list(discover_catalog_entries(advanced=False))
    first_level_entries = _first_level_skill_entries()
    hidden_system_entries = _system_lane_entries()
    scope_counts, scoped_entries, shadowed_entries, unresolved_scope_collisions = _scope_payloads()

    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for name, source_dir in _iter_default_visibility_candidates():
        by_name[name].append(_candidate_payload(name=name, source_dir=source_dir))

    duplicate_default_names = [
        {
            "name": name,
            "entries": entries,
        }
        for name, entries in sorted(by_name.items())
        if len(entries) > 1
    ]

    first_level = set(_first_level_skill_names())
    bridge_exposed = sorted(first_level & BRIDGE_SKILLS)
    policy_default = set(DEFAULT_VISIBLE_FLAT_SKILL_NAMES)
    # Bridge skills are intentionally not expected in default first-level discovery.
    # They can exist in policy metadata while remaining routed through the hidden
    # `.system` lane and are validated separately via BRIDGE_SKILLS_EXPOSED_FIRST_LEVEL.
    expected_default = policy_default - BRIDGE_SKILLS
    default_names = {entry.name for entry in default_entries}
    catalog_names = {entry.name for entry in catalog_entries}
    extra_default = sorted(default_names - expected_default)
    missing_default = sorted(expected_default - default_names)
    catalog_only_default_names = sorted(catalog_names - default_names)
    discovery_only_default_names = sorted(default_names - catalog_names)
    estimated_description_words = sum(_word_count(entry.description) for entry in default_entries)
    unmapped_skill_names = sorted(
        entry["name"]
        for entry in scoped_entries
        if entry["scope"] in {"unknown", "external"}
    )
    primary_runtime_entries = sorted(
        [entry for entry in scoped_entries if entry["scope"] == "primary-runtime"],
        key=lambda entry: (entry["name"], entry["path"]),
    )
    plugin_runtime_entries = sorted(
        [entry for entry in scoped_entries if entry["scope"] == "local-plugin"],
        key=lambda entry: (entry["name"], entry["path"]),
    )

    violations: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []
    if len(default_entries) > default_max:
        violations.append({
            "code": "DEFAULT_SKILL_BUDGET_EXCEEDED",
            "message": f"default skill count {len(default_entries)} exceeds budget {default_max}",
        })
    if len(advanced_entries) > ADVANCED_WARN_VISIBLE:
        advisories.append({
            "code": "ADVANCED_SKILL_VISIBILITY_HIGH",
            "message": (
                f"advanced skill count {len(advanced_entries)} exceeds informational threshold "
                f"{ADVANCED_WARN_VISIBLE}"
            ),
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
    if catalog_only_default_names or discovery_only_default_names:
        violations.append({
            "code": "CATALOG_DEFAULT_DRIFT",
            "message": "catalog default surface differs from discovery default surface",
            "catalog_only_default_names": catalog_only_default_names,
            "discovery_only_default_names": discovery_only_default_names,
        })
    if unresolved_scope_collisions:
        violations.append({
            "code": "UNRESOLVED_SCOPE_COLLISIONS",
            "message": "skill sources with the same name remain tied at the same user scope precedence",
            "collisions": unresolved_scope_collisions,
        })

    status = "pass" if not violations else "fail"
    return {
        "status": status,
        "budget_status": status,
        "projection_mode": DEFAULT_PROJECTION_MODE,
        "policy_identity": policy_identity(),
        "default_visible_count": len(default_entries),
        "default_visible_max": default_max,
        "advanced_visible_count": len(advanced_entries),
        "advanced_visible_warn": ADVANCED_WARN_VISIBLE,
        "catalog_default_count": len(catalog_entries),
        "first_level_default_entries": first_level_entries,
        "first_level_default_count": len(first_level_entries),
        "hidden_system_entries": hidden_system_entries,
        "hidden_system_count": len(hidden_system_entries),
        "primary_runtime_entries": primary_runtime_entries,
        "plugin_runtime_entries": plugin_runtime_entries,
        "scope_counts": scope_counts,
        "shadowed_entries": shadowed_entries,
        "suppressed_entries": [
            suppressed
            for shadow in shadowed_entries
            for suppressed in shadow["suppressed"]
        ],
        "unresolved_scope_collisions": unresolved_scope_collisions,
        "duplicate_default_names": duplicate_default_names,
        "largest_descriptions": _largest_description_payloads(advanced_entries),
        "root_skill_set_count": len({entry["name"] for entry in first_level_entries} & ROOT_SKILL_SETS),
        "unmapped_skill_names": unmapped_skill_names,
        "estimated_description_words": estimated_description_words,
        "estimated_description_tokens": _estimated_tokens_from_words(estimated_description_words),
        "catalog_default_skill_names": sorted(catalog_names),
        "system_bridge_skills": sorted(BRIDGE_SKILLS),
        "first_level_bridge_skills": bridge_exposed,
        "policy_default_skill_names": sorted(policy_default),
        "effective_default_policy_skill_names": sorted(expected_default),
        "default_visible_skill_names": sorted(default_names),
        "advisories": advisories,
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
        for advisory in report["advisories"]:
            print(f"- {advisory['code']}: {advisory['message']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
