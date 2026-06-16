#!/usr/bin/env python3
"""Resolve SDK-flat skills from canonical source and runtime projection.

The SDK registry is the public source of truth for current skill visibility.
Generated rooted manifests and command-surface metadata are obsolete artifacts;
they must not participate in SDK skill resolution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from skill_discovery import (
    REPO_ROOT,
    classify_skill_scope,
    discover_skill_entries,
    normalize_skill_description,
    parse_skill_frontmatter,
)


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
    runtime_visibility = "flat" if runtime_projection_path else str(metadata_visibility or "source")

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


def build_sdk_skill_records(*, repo_root_path: Path | None = None, visibility: str = "default") -> list[SdkSkillRecord]:
    """Return SDK skill records from flat runtime first, then canonical source."""
    root = (repo_root_path or REPO_ROOT).resolve()
    records: list[SdkSkillRecord] = []
    seen: set[str] = set()
    for entry in discover_skill_entries(source="auto", visibility=visibility):
        handle = entry.name
        if handle in seen:
            continue
        record = _record_from_skill_dir(handle, entry.source_dir, root=root)
        if record is None:
            continue
        records.append(record)
        seen.add(handle)
    return sorted(records, key=lambda item: (item.scope, item.owner, item.handle))


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

    matches = [
        record
        for record in build_sdk_skill_records(repo_root_path=repo_root_path, visibility="advanced")
        if record.handle == requested or record.name == requested
    ]
    if not matches:
        return {
            "status": "error",
            "error_code": "unknown_handle",
            "handle": requested,
            "operator_action": "Run ./bin/ask skills list --json --robot to list SDK-visible skills.",
        }
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
