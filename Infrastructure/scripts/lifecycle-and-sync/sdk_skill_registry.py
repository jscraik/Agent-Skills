#!/usr/bin/env python3
"""Resolve SDK-flat skills from canonical source and runtime projection.

The SDK registry is the public source of truth for current skill visibility.
Generated rooted manifests and command-surface metadata are obsolete artifacts;
they must not participate in SDK skill resolution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from selection_policy import (
    EXCLUDED_SCAN_SEGMENTS,
    HIDDEN_FLAT_SKILL_NAMES,
    PLUGIN_SKILL_COLLISION_POLICIES,
    PLUGIN_SKILL_ROOT_GLOB,
    REPO_SCAN_ROOTS,
    SYSTEM_BRIDGE_SKILL_NAMES,
)
from skill_discovery import REPO_ROOT, classify_skill_scope, normalize_skill_description, parse_skill_frontmatter


@dataclass(frozen=True)
class SdkSkillRecord:
    handle: str
    name: str
    source_path: str
    runtime_projection_path: str | None
    runtime_visibility: str
    projection_mode: str
    owner: str
    description: str
    scope: str
    provenance: dict[str, Any]

    def to_resolution(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.update({
            "status": "ok",
            "kind": "skill",
            "handle_source": "sdk_flat_registry",
        })
        return {key: value for key, value in payload.items() if value is not None}


def _repo_relative(path: Path, root: Path, *, resolve: bool = True) -> str | None:
    try:
        candidate = path.resolve() if resolve else path
        return candidate.relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _canonical_skill_file(runtime_skill_dir: Path) -> Path:
    skill_md = runtime_skill_dir / "SKILL.md"
    try:
        return skill_md.resolve()
    except OSError:
        return skill_md


def _record_from_skill_dir(handle: str, skill_dir: Path, *, root: Path) -> SdkSkillRecord | None:
    skill_md = _canonical_skill_file(skill_dir)
    if not skill_md.is_file():
        return None
    source_path = _repo_relative(skill_md, root)
    if not source_path:
        return None

    runtime_projection_path: str | None = None
    flat_skill_md = root / ".agents" / "skills" / handle / "SKILL.md"
    if flat_skill_md.is_file():
        try:
            if flat_skill_md.resolve() == skill_md.resolve():
                runtime_projection_path = _repo_relative(flat_skill_md, root, resolve=False)
        except OSError:
            runtime_projection_path = None

    fm = parse_skill_frontmatter(skill_md)
    metadata_visibility = (
        fm.get("metadata.runtime_visibility")
        or fm.get("metadata.runtime-visibility")
        or fm.get("runtime_visibility")
        or fm.get("runtime-visibility")
    )
    scope = classify_skill_scope(skill_md.parent, root)
    source_parts = Path(source_path).parts
    owner = (
        fm.get("metadata.owner")
        or fm.get("owner")
        or (source_parts[1] if len(source_parts) > 1 and source_parts[0] == "Skills" else "")
        or (source_parts[1] if len(source_parts) > 1 and source_parts[0] == "Plugins" else "")
    )
    description = normalize_skill_description(fm.get("metadata.short-description") or fm.get("description", ""))
    declared_runtime_visibility = str(metadata_visibility or "").strip().lower()
    if declared_runtime_visibility == "hidden":
        runtime_visibility = "hidden"
    elif runtime_projection_path:
        runtime_visibility = "flat"
    else:
        runtime_visibility = str(metadata_visibility or "source")

    return SdkSkillRecord(
        handle=handle,
        name=fm.get("name") or handle,
        source_path=source_path,
        runtime_projection_path=runtime_projection_path,
        runtime_visibility=runtime_visibility,
        projection_mode="flat" if runtime_projection_path else "source",
        owner=str(owner),
        description=description,
        scope=scope,
        provenance={
            "resolver": "sdk_skill_registry.v1",
            "projection_mode": "flat" if runtime_projection_path else "source",
            "source": "flat_runtime" if runtime_projection_path else "canonical_source",
        },
    )


def _is_excluded_skill_path(skill_md: Path, scan_root: Path) -> bool:
    try:
        rel_parts = skill_md.relative_to(scan_root).parts
    except ValueError:
        return True
    return any(part in EXCLUDED_SCAN_SEGMENTS for part in rel_parts)


def _iter_flat_skill_dirs(root: Path) -> list[tuple[str, Path]]:
    flat_root = root / ".agents" / "skills"
    if not flat_root.is_dir():
        return []
    rows: list[tuple[str, Path]] = []
    for item in sorted(flat_root.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir() and (item / "SKILL.md").exists():
            rows.append((item.name, item))
    return rows


def _iter_repo_skill_dirs(root: Path) -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for root_name in REPO_SCAN_ROOTS:
        scan_root = root / root_name
        if not scan_root.is_dir():
            continue
        for skill_md in sorted(scan_root.rglob("SKILL.md")):
            if _is_excluded_skill_path(skill_md, scan_root):
                continue
            fm = parse_skill_frontmatter(skill_md)
            handle = str(fm.get("name") or skill_md.parent.name).strip()
            if handle:
                rows.append((handle, skill_md.parent))
    return rows


def _plugin_scan_patterns() -> list[str]:
    patterns: set[str] = set()
    for raw_pattern in (
        *PLUGIN_SKILL_ROOT_GLOB.split(),
        "./Plugins/cache/*/*/skills",
        "./Plugins/cache/*/*/*/skills",
    ):
        if not raw_pattern:
            continue
        patterns.add(raw_pattern)
        if raw_pattern.endswith("/*/skills"):
            nested_pattern = raw_pattern[: -len("/*/skills")] + "/*/*/skills"
            patterns.add(nested_pattern)
    return sorted(patterns)


def _cache_plugin_source_root(plugin_root: Path, root: Path) -> str | None:
    try:
        rel_parts = plugin_root.relative_to(root).parts
    except ValueError:
        return None
    if rel_parts[:2] == ("Plugins", "cache") and len(rel_parts) >= 5 and rel_parts[-1] == "skills":
        return rel_parts[3]
    return None


def _iter_plugin_skill_dirs(root: Path) -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    seen_roots: set[str] = set()
    for pattern in _plugin_scan_patterns():
        for plugin_root in sorted(root.glob(pattern)):
            try:
                plugin_root_key = plugin_root.resolve().as_posix()
            except OSError:
                plugin_root_key = plugin_root.as_posix()
            if plugin_root_key in seen_roots or not plugin_root.is_dir():
                continue
            seen_roots.add(plugin_root_key)
            cache_rel = _cache_plugin_source_root(plugin_root, root)
            if cache_rel and (root / "Plugins" / cache_rel / "skills").is_dir():
                continue
            for skill_md in sorted(plugin_root.rglob("SKILL.md")):
                if _is_excluded_skill_path(skill_md, plugin_root):
                    continue
                fm = parse_skill_frontmatter(skill_md)
                handle = str(fm.get("name") or skill_md.parent.name).strip()
                if handle:
                    rows.append((handle, skill_md.parent))
    return rows


def _iter_system_skill_dirs(root: Path) -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for system_root in (root / ".agents" / "skills" / ".system", root / "skills-system"):
        if not system_root.is_dir():
            continue
        for item in sorted(system_root.iterdir()):
            if not item.is_dir() or not (item / "SKILL.md").exists():
                continue
            fm = parse_skill_frontmatter(item / "SKILL.md")
            handle = str(fm.get("name") or item.name).strip()
            if handle:
                rows.append((handle, item))
        if rows:
            break
    return rows


def build_sdk_skill_record_candidates(
    *, repo_root_path: Path | None = None, visibility: str = "default"
) -> list[SdkSkillRecord]:
    """Return all root-aware SDK skill candidates before duplicate collapse."""
    root = (repo_root_path or REPO_ROOT).resolve()
    records: list[SdkSkillRecord] = []
    for handle, skill_dir in (
        *_iter_flat_skill_dirs(root),
        *_iter_repo_skill_dirs(root),
        *_iter_plugin_skill_dirs(root),
        *_iter_system_skill_dirs(root),
    ):
        if visibility != "advanced" and handle in HIDDEN_FLAT_SKILL_NAMES:
            continue
        if visibility == "advanced" and handle in HIDDEN_FLAT_SKILL_NAMES:
            continue
        record = _record_from_skill_dir(handle, skill_dir, root=root)
        if record is None:
            continue
        if record.runtime_visibility == "hidden":
            continue
        record = _apply_qualified_collision_policy(record)
        records.append(record)
    return sorted(records, key=lambda item: (item.scope, item.owner, item.handle, item.source_path))


def build_sdk_skill_records(
    *, repo_root_path: Path | None = None, visibility: str = "default"
) -> list[SdkSkillRecord]:
    """Return SDK skill records from flat runtime first, then canonical source."""
    records: list[SdkSkillRecord] = []
    seen: set[str] = set()
    candidates = sorted(
        build_sdk_skill_record_candidates(repo_root_path=repo_root_path, visibility=visibility),
        key=_record_publish_priority,
    )
    for record in candidates:
        if record.handle in seen:
            continue
        records.append(record)
        seen.add(record.handle)
    return sorted(records, key=lambda item: (item.scope, item.owner, item.handle))


def _distinct_records(records: list[SdkSkillRecord]) -> list[SdkSkillRecord]:
    distinct: list[SdkSkillRecord] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        key = (record.handle, record.source_path)
        if key in seen:
            continue
        distinct.append(record)
        seen.add(key)
    return distinct


def _collision_policy_path(path: str) -> str:
    parts = Path(path).parts
    if parts and parts[-1] == "SKILL.md":
        parts = parts[:-1]
    if len(parts) >= 7 and parts[0] in {"Plugins", "plugins"} and parts[1] == "cache":
        return "/".join(("Plugins", "cache", parts[2], parts[3], *parts[5:]))
    if parts and parts[0] == "plugins":
        return "/".join(("Plugins", *parts[1:]))
    return "/".join(parts)


def _suppress_duplicate_policy_rank(record: SdkSkillRecord) -> int:
    normalized_path = _collision_policy_path(record.source_path)
    for policy in PLUGIN_SKILL_COLLISION_POLICIES:
        if policy.get("resolution") != "suppress_duplicate":
            continue
        if policy.get("name") != record.handle:
            continue
        canonical_path = _collision_policy_path(str(policy.get("canonical_path") or ""))
        suppressed_paths = {
            _collision_policy_path(str(path))
            for path in policy.get("suppressed_paths", ())
        }
        policy_paths = {
            _collision_policy_path(str(path))
            for path in policy.get("paths", ())
        }
        if normalized_path == canonical_path:
            return 0
        if normalized_path in suppressed_paths:
            return 2
        if normalized_path in policy_paths:
            return 1
    return 0


def _record_publish_priority(record: SdkSkillRecord) -> tuple[str, int, int, str, str, str]:
    runtime_rank = 0 if record.runtime_projection_path else 1
    return (
        record.handle,
        _suppress_duplicate_policy_rank(record),
        runtime_rank,
        record.scope,
        record.owner,
        record.source_path,
    )


def _qualified_policy_name(handle: str, source_path: str) -> str | None:
    normalized_path = _collision_policy_path(source_path)
    for policy in PLUGIN_SKILL_COLLISION_POLICIES:
        if policy.get("resolution") != "keep_qualified":
            continue
        if policy.get("name") != handle:
            continue
        qualified_names = {
            _collision_policy_path(str(path)): str(name)
            for path, name in dict(policy.get("qualified_names", {})).items()
        }
        qualified_name = qualified_names.get(normalized_path)
        if qualified_name:
            return qualified_name
    return None


def _apply_qualified_collision_policy(record: SdkSkillRecord) -> SdkSkillRecord:
    qualified_name = _qualified_policy_name(record.handle, record.source_path)
    if not qualified_name or qualified_name == record.handle:
        return record
    provenance = dict(record.provenance)
    provenance.update({
        "qualified_from": record.handle,
        "qualification_policy": "keep_qualified",
    })
    return replace(record, handle=qualified_name, name=qualified_name, provenance=provenance)


def _policy_manages_collision(handle: str, source_paths: set[str]) -> bool:
    normalized_paths = {_collision_policy_path(path) for path in source_paths}
    if handle in SYSTEM_BRIDGE_SKILL_NAMES and any(
        path.startswith(".agents/skills/.system/") for path in normalized_paths
    ):
        return True
    for policy in PLUGIN_SKILL_COLLISION_POLICIES:
        if policy.get("resolution") != "suppress_duplicate":
            continue
        policy_paths = {_collision_policy_path(str(path)) for path in policy.get("paths", ())}
        if normalized_paths and normalized_paths.issubset(policy_paths):
            return True
    for policy in PLUGIN_SKILL_COLLISION_POLICIES:
        if policy.get("resolution") != "keep_qualified":
            continue
        qualified_names = {
            _collision_policy_path(str(path)): str(name)
            for path, name in dict(policy.get("qualified_names", {})).items()
        }
        if normalized_paths and normalized_paths.issubset(qualified_names.keys()):
            mapped_names = {qualified_names[path] for path in normalized_paths}
            if mapped_names == {handle}:
                return True
    return False


def sdk_duplicate_handle_violations(records: list[SdkSkillRecord]) -> list[dict[str, str]]:
    """Return duplicate SDK handle violations after policy-managed collisions."""
    source_paths_by_handle: dict[str, set[str]] = {}
    for record in records:
        source_paths_by_handle.setdefault(record.handle, set()).add(_collision_policy_path(record.source_path))
    violations: list[dict[str, str]] = []
    for handle, source_paths in sorted(source_paths_by_handle.items()):
        if len(source_paths) <= 1:
            continue
        if _policy_manages_collision(handle, source_paths):
            continue
        violations.append({"code": "DUPLICATE_SDK_SKILL_HANDLE", "handle": handle})
    return violations


def resolve_sdk_skill_handle(handle: str, *, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Resolve a skill handle through the current SDK-flat registry."""
    requested = handle.strip().removeprefix("$").strip()
    if not requested:
        return {
            "status": "error",
            "error_code": "empty_handle",
            "handle": requested,
            "operator_action": "Pass a skill handle such as agents-md.",
        }

    matches = _distinct_records([
        record
        for record in build_sdk_skill_record_candidates(repo_root_path=repo_root_path, visibility="advanced")
        if record.handle == requested or record.name == requested
    ])
    if not matches:
        return {
            "status": "error",
            "error_code": "unknown_handle",
            "handle": requested,
            "operator_action": "Run ./bin/ask skills list --json --robot to list SDK-visible skills.",
        }
    if len(matches) > 1 and _policy_manages_collision(requested, {match.source_path for match in matches}):
        matches = sorted(matches, key=_record_publish_priority)[:1]
    if len(matches) > 1:
        return {
            "status": "error",
            "error_code": "ambiguous_handle",
            "handle": requested,
            "matches": [match.to_resolution() for match in matches],
            "operator_action": "Rename or hide duplicate SDK skill handles before projection.",
        }

    payload = matches[0].to_resolution()
    if requested != payload.get("handle"):
        payload["requested_handle"] = requested
        payload["alias_resolution"] = payload.get("handle")
    return payload
