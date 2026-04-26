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
    SYSTEM_BRIDGE_SKILL_NAMES,
    policy_identity,
)
from runtime_surface_policy import (  # type: ignore  # noqa: E402
    DEFAULT_VISIBLE_FLAT_SKILLS,
    PROJECTION_MIXED,
    PROJECTION_ROOTED,
    ROOT_SKILL_SETS,
    is_default_visible_skill_name,
    runtime_surface_report,
)
from skill_discovery import (  # type: ignore  # noqa: E402
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
SCOPE_PRECEDENCE = USER_SKILL_SCOPE_PRECEDENCE


def _rel(path: Path) -> str:
    """
    Return the given Path as a POSIX-style string relative to REPO_ROOT when the path is inside REPO_ROOT.

    Returns:
        str: The path as a POSIX string relative to REPO_ROOT if possible; otherwise the absolute POSIX path.
    """
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _candidate_payload(*, name: str, source_dir: Path) -> dict[str, str]:
    """
    Builds a minimal skill candidate payload used in reporting.

    Parameters:
        name (str): Skill name.
        source_dir (Path): Filesystem path to the skill directory; its path is converted to a repository-relative POSIX string and used to derive the category.

    Returns:
        dict[str, str]: Payload with keys:
            - "name": the provided skill name.
            - "path": repository-relative POSIX path to the skill directory.
            - "category": parent directory of the path as POSIX string, or "uncategorized" if there is no parent.
    """
    rel_path = _rel(source_dir)
    category = Path(rel_path).parent.as_posix() or "uncategorized"
    return {
        "name": name,
        "path": rel_path,
        "category": category,
    }


def _word_count(text: str) -> int:
    """
    Count the number of words in the given text.

    Parameters:
        text (str): The input string to measure.

    Returns:
        int: Number of word tokens (segments separated by whitespace).
    """
    return len([word for word in text.split() if word.strip()])


def _estimated_tokens_from_words(words: int) -> int:
    """
    Estimate the number of tokens corresponding to a given word count using a 4:3 heuristic.

    Parameters:
        words (int): Number of words to convert.

    Returns:
        int: Estimated token count computed as (words * 4 + 2) // 3.
    """
    return (words * 4 + 2) // 3


def _first_level_skill_entries() -> list[dict[str, str]]:
    """
    Collects first-level skill entries from the repository's .agents/skills directory.

    Returns:
        list[dict[str, str]]: A list of skill payloads for each non-hidden first-level directory that contains a `SKILL.md`. Each payload includes `name`, `path` (relative to the repository root), and `category`.
    """
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
    """
    Collect candidate payloads for all system-lane skill directories, sorted by skill name then path.

    Returns:
        list[dict[str, str]]: A list of candidate payloads (each containing `name`, `path`, and `category`) for system-lane skills, sorted by `name` and `path`.
    """
    entries = [
        _candidate_payload(name=skill_dir.name, source_dir=skill_dir)
        for skill_dir in iter_system_lane_skill_dirs()
    ]
    return sorted(entries, key=lambda entry: (entry["name"], entry["path"]))


def _iter_known_skill_dirs() -> list[Path]:
    """
    Collects all unique known skill directories from repository, plugins, and system lanes.

    Scans directories provided by iter_repo_skill_dirs(), iter_plugin_skill_dirs(), and iter_system_lane_skill_dirs(), includes only those that contain a SKILL.md, and deduplicates candidates by filesystem identity (device/inode) when available or by resolved path on error. The returned list is sorted using the repository-relative ordering produced by _rel.

    Returns:
        list[Path]: Unique skill directory paths, sorted relative to the repository root.
    """
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
    return sorted(dirs, key=_rel)


def _scope_payloads() -> tuple[dict[str, int], list[dict[str, str]], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Classify known skill directories by scope and produce scope counts, flattened entries, resolved shadowing, and unresolved collisions.

    Returns:
        scope_counts (dict[str, int]): Counts of discovered skills keyed by scope names:
            "global", "project", "local-plugin", "system", "primary-runtime", "unknown", and "external".
        entries (list[dict[str, str]]): Flattened list of per-skill payloads. Each payload includes at least
            `name`, `path`, `category`, and `scope`.
        shadowed_entries (list[dict[str, Any]]): List of resolved name collisions where a single candidate was
            chosen by scope precedence. Each item has:
            - `name`: the skill name,
            - `selected`: the winning payload,
            - `suppressed`: list of payloads that were shadowed by the selected candidate.
        unresolved_scope_collisions (list[dict[str, Any]]): List of name collisions that could not be
            uniquely resolved because multiple candidates share the top precedence rank. Each item has:
            - `name`: the skill name,
            - `candidates`: list of competing payloads.
    """
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
    """
    Build payloads for entries with the largest description word counts.

    Parameters:
        entries (list[Any]): Iterable of objects each exposing `name` (str), `description` (str),
            and `source_dir` (Path). `description` is used to compute word counts.
        limit (int): Maximum number of payloads to return.

    Returns:
        list[dict[str, Any]]: A list of payloads sorted by descending `description_words` then `name`.
        Each payload contains:
            - `name` (str): entry name
            - `path` (str): POSIX path of `source_dir` relative to repository root
            - `description_words` (int): word count of `description`
            - `description` (str): original description text
    """
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
    Collects all skill directory candidates that qualify for the default visibility surface before deduplication by name.

    Only directories that contain a SKILL.md, whose derived name is non-empty and present in DEFAULT_VISIBLE_FLAT_SKILL_NAMES, and that are located under REPO_ROOT are included. Plugin-owned skill directories are further filtered by DISCOVERY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES and DISCOVERY_PLUGIN_HIDDEN_LANE_SKILL_NAMES. Entries listed in DISCOVERY_HIDDEN_FLAT_SKILL_NAMES are excluded.

    Returns:
        candidates (list[tuple[str, pathlib.Path]]): List of (skill name, resolved source directory Path) tuples for every candidate that survives the default-visibility filters.
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
        plugin_owned = is_plugin_owned_skill_dir(source_dir)
        if not is_default_visible_skill_name(name, plugin_owned=plugin_owned):
            continue
        try:
            skill_dir.relative_to(REPO_ROOT)
        except ValueError:
            continue
        candidates.append((name, source_dir))
    return candidates


def _first_level_skill_names() -> list[str]:
    """
    Collects the top-level skill directory names from the repository's .agents/skills directory.

    Returns:
        list[str]: Names of non-hidden directories directly under `.agents/skills` that contain a `SKILL.md` file. If the directory does not exist, returns an empty list.
    """
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


def _skill_file_word_count(entry: dict[str, str]) -> int:
    """
    Count the words in the SKILL.md file for a skill entry.

    Parameters:
        entry (dict[str, str]): Skill payload containing a "path" key (path relative to REPO_ROOT) pointing to the skill directory.

    Returns:
        int: Number of words in the SKILL.md file, or 0 if the file does not exist.
    """
    skill_path = REPO_ROOT / entry["path"] / "SKILL.md"
    if not skill_path.is_file():
        return 0
    return _word_count(skill_path.read_text(encoding="utf-8", errors="ignore"))


def build_report(default_max: int = DEFAULT_MAX_VISIBLE) -> dict[str, Any]:
    """
    Builds a verification report comparing discovered, catalog, and policy skill surfaces and checks runtime budget and naming/visibility invariants.

    The returned report aggregates discovery results (default and advanced visibility), catalog defaults, first-level and hidden system entries, scope classification and shadowing, duplicate-name detection, description-size estimates, and any violations or advisories produced by the checks described in the module summary.

    Parameters:
        default_max (int): Maximum allowed count for the effective default visible skill set used to determine budget violations.

    Returns:
        dict: A report dictionary containing (at minimum) the following keys:
            - status: "pass" if no violations were found, otherwise "fail".
            - budget_status: same value as `status`.
            - projection_mode: "flat", "rooted", or "mixed".
            - policy_identity: identifier for the policy surface in effect.
            - default_visible_count, default_visible_max: effective default count and the provided budget.
            - advanced_visible_count, advanced_visible_warn: advanced discovery count and informational threshold.
            - catalog_default_count: number of catalog default entries.
            - first_level_default_entries, first_level_default_count: entries discovered at the first-level and their count.
            - hidden_system_entries, hidden_system_count: system-lane entries and their count.
            - primary_runtime_entries, plugin_runtime_entries: scoped runtime entry lists.
            - scope_counts: mapping of scope names to counts.
            - shadowed_entries: reported winners and suppressed candidates for name collisions by scope precedence.
            - suppressed_entries: flattened list of suppressed entries.
            - unresolved_scope_collisions: list of names that remain tied at top precedence.
            - duplicate_default_names: list of duplicate default-name candidate groups.
            - largest_descriptions: entries with the largest descriptions (by word count).
            - root_skill_set_count: effective root skill-set size when in rooted mode.
            - unmapped_skill_names: names classified as "unknown" or "external".
            - estimated_description_words, estimated_description_tokens: description size estimates.
            - catalog_default_skill_names, policy_default_skill_names, effective_default_policy_skill_names, default_visible_skill_names: various name lists for surfaces and policies.
            - system_bridge_skills, first_level_bridge_skills: bridge skill lists and any exposed at first level.
            - advisories: informational conditions detected.
            - violations: policy and budget violations detected with diagnostic details.
    """
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
    surface_report = runtime_surface_report(first_level)
    projection_mode = surface_report.projection_mode
    rooted_mode = projection_mode == PROJECTION_ROOTED
    mixed_mode = projection_mode == PROJECTION_MIXED
    root_skill_set_count = len(first_level & ROOT_SKILL_SETS)
    bridge_exposed = sorted(first_level & BRIDGE_SKILLS)
    policy_default = set(DEFAULT_VISIBLE_FLAT_SKILLS)
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
    estimated_description_words = (
        sum(_skill_file_word_count(entry) for entry in first_level_entries if entry["name"] in ROOT_SKILL_SETS)
        if rooted_mode
        else sum(_word_count(entry.description) for entry in default_entries)
    )
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
    effective_default_count = root_skill_set_count if rooted_mode else len(default_entries)
    if effective_default_count > default_max:
        violations.append({
            "code": "DEFAULT_SKILL_BUDGET_EXCEEDED",
            "message": f"default skill count {effective_default_count} exceeds budget {default_max}",
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
    if mixed_mode:
        violations.append({
            "code": "MIXED_RUNTIME_PROJECTION",
            "message": (
                "first-level runtime entries mix rooted root skill sets with non-root entries; "
                "fix the projection before budget validation"
            ),
            "root_skill_set_names": sorted(surface_report.root_skill_set_names),
            "extra": surface_report.extra_first_level_names,
            "missing": surface_report.missing_first_level_names,
        })
    elif rooted_mode:
        if surface_report.missing_first_level_names or surface_report.extra_first_level_names:
            violations.append({
                "code": "ROOTED_POLICY_NAME_DRIFT",
                "message": "rooted first-level runtime entries differ from root skill-set policy",
                "extra": surface_report.extra_first_level_names,
                "missing": surface_report.missing_first_level_names,
            })
    elif extra_default or missing_default:
        violations.append({
            "code": "DEFAULT_POLICY_NAME_DRIFT",
            "message": "default discovery names differ from effective selection policy",
            "extra": extra_default,
            "missing": missing_default,
        })
    if not rooted_mode and (catalog_only_default_names or discovery_only_default_names):
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
        "projection_mode": projection_mode,
        "runtime_surface": {
            "projection_mode": projection_mode,
            "first_level_names": sorted(surface_report.first_level_names),
            "expected_first_level_names": sorted(surface_report.expected_first_level_names),
            "extra_first_level_names": surface_report.extra_first_level_names,
            "missing_first_level_names": surface_report.missing_first_level_names,
            "root_skill_set_names": sorted(surface_report.root_skill_set_names),
            "flat_skill_names": sorted(surface_report.flat_skill_names),
        },
        "policy_identity": policy_identity(),
        "default_visible_count": effective_default_count,
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
        "root_skill_set_count": root_skill_set_count,
        "unmapped_skill_names": unmapped_skill_names,
        "estimated_description_words": estimated_description_words,
        "estimated_description_tokens": _estimated_tokens_from_words(estimated_description_words),
        "catalog_default_skill_names": sorted(catalog_names),
        "system_bridge_skills": sorted(BRIDGE_SKILLS),
        "first_level_bridge_skills": bridge_exposed,
        "policy_default_skill_names": sorted(policy_default),
        "effective_default_policy_skill_names": sorted(surface_report.expected_first_level_names - BRIDGE_SKILLS),
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
