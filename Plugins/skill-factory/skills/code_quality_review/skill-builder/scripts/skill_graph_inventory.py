#!/usr/bin/env python3
"""Shared canonical inventory policy helpers for skill-graph onboarding scripts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set

DEFAULT_INVENTORY_POLICY = "Docs/skill-graphs/governance/inventory-policy.json"
DEFAULT_SYSTEM_PREFIXES = ("Skills/.system/", ".agents/skills/.system/")
SYSTEM_SLICE_MODES = {"exclude", "separate"}
MIRROR_PREFIXES = ("plugins/cache/", ".agents/plugins-runtime/cache/")
SCOPE_ALIAS_PREFIXES = (
    ("plugins/harness-engineering/skills/", "product/ops/"),
)


@dataclass(frozen=True)
class InventoryPolicy:
    allowlist_scope_skills: Set[str]
    include_prefixes: Sequence[str]
    exclude_prefixes: Sequence[str]
    system_prefixes: Sequence[str]
    system_slice_mode: str
    source_path: Path


@dataclass(frozen=True)
class InventorySkill:
    skill_md: Path
    relative_skill_dir: str
    scope_skill: str
    inventory_slice: str
    source_skill_dirs: tuple[str, ...] = ()


def _normalize_prefixes(values: Iterable[str]) -> List[str]:
    out: List[str] = []
    for raw in values:
        value = str(raw).strip().replace("\\", "/")
        if not value:
            continue
        if not value.endswith("/"):
            value += "/"
        out.append(value)
    return sorted(set(out))


def _normalize_scope_skills(values: Iterable[str]) -> Set[str]:
    out: Set[str] = set()
    for raw in values:
        value = str(raw).strip().strip("/")
        if value:
            out.add(value)
    return out


def load_inventory_policy(
    repo_root: Path,
    policy_rel_path: str = DEFAULT_INVENTORY_POLICY,
    system_slice_mode_override: Optional[str] = None,
) -> InventoryPolicy:
    policy_path = (repo_root / policy_rel_path).resolve()
    if not policy_path.exists():
        raise FileNotFoundError(
            f"Missing inventory policy: {policy_path}. "
            "Create Docs/skill-graphs/governance/inventory-policy.json."
        )

    raw = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Inventory policy must be a JSON object: {policy_path}")

    include_prefixes = _normalize_prefixes(raw.get("include_prefixes", []))
    exclude_prefixes = _normalize_prefixes(raw.get("exclude_prefixes", []))
    system_prefixes = _normalize_prefixes(raw.get("system_prefixes", DEFAULT_SYSTEM_PREFIXES))
    allowlist_scope_skills = _normalize_scope_skills(raw.get("allowlist_scope_skills", []))
    system_slice_mode = str(raw.get("system_slice_mode", "exclude")).strip().lower()
    if system_slice_mode_override:
        system_slice_mode = str(system_slice_mode_override).strip().lower()
    if system_slice_mode not in SYSTEM_SLICE_MODES:
        raise ValueError(
            f"inventory policy system_slice_mode must be one of {sorted(SYSTEM_SLICE_MODES)} "
            f"(got {system_slice_mode!r})"
        )

    return InventoryPolicy(
        allowlist_scope_skills=allowlist_scope_skills,
        include_prefixes=include_prefixes,
        exclude_prefixes=exclude_prefixes,
        system_prefixes=system_prefixes,
        system_slice_mode=system_slice_mode,
        source_path=policy_path,
    )


def is_mirror_path(relative_skill_dir: str) -> bool:
    """Return True when *relative_skill_dir* belongs to a projection/cache mirror."""
    return relative_skill_dir.startswith(MIRROR_PREFIXES)


def resolve_scope_skill_for_path(relative_skill_dir: str) -> str:
    """Resolve semantic scope skill for a physical skill directory.

    This mapping is the contract bridge for category reshapes where runtime
    plugin paths intentionally differ from the canonical scope taxonomy used in
    allowlists/task-profiles.
    """
    rel_dir = relative_skill_dir.strip().strip("/")
    if not rel_dir:
        return relative_skill_dir

    # Cache/runtime projections can include an intermediate plugin version segment.
    for cache_prefix in (
        "plugins/cache/agent-skills-local/harness-engineering/",
        ".agents/plugins-runtime/cache/agent-skills-local/harness-engineering/",
    ):
        if rel_dir.startswith(cache_prefix):
            remainder = rel_dir[len(cache_prefix) :]
            suffix = ""
            if remainder.startswith("skills/"):
                suffix = remainder[len("skills/") :]
            else:
                segments = remainder.split("/", 2)
                if len(segments) >= 3 and segments[1] == "skills":
                    suffix = segments[2]
            if suffix:
                return f"product/ops/{suffix}".strip("/")

    for source_prefix, scope_prefix in SCOPE_ALIAS_PREFIXES:
        if rel_dir.startswith(source_prefix):
            suffix = rel_dir[len(source_prefix) :]
            if suffix:
                return f"{scope_prefix}{suffix}".strip("/")
    return rel_dir


def _classify_slice(
    rel_skill_md: str,
    rel_skill_dir: str,
    scope_skill: str,
    policy: InventoryPolicy,
) -> Optional[str]:
    if rel_skill_md == "SKILL.md":
        return None
    if any(rel_skill_md.startswith(prefix) for prefix in policy.exclude_prefixes):
        return None

    if any(rel_skill_md.startswith(prefix) for prefix in policy.system_prefixes):
        if policy.system_slice_mode == "separate":
            return "system"
        return None

    use_scope_alias = scope_skill != rel_skill_dir

    if policy.allowlist_scope_skills:
        allowlist_candidates = {rel_skill_dir}
        if use_scope_alias:
            allowlist_candidates.add(scope_skill)
        if allowlist_candidates.isdisjoint(policy.allowlist_scope_skills):
            return None
    if policy.include_prefixes:
        include_candidates = (
            rel_skill_md,
            f"{rel_skill_dir}/",
        )
        if use_scope_alias:
            include_candidates = include_candidates + (f"{scope_skill}/",)
        if not any(
            candidate.startswith(prefix)
            for candidate in include_candidates
            for prefix in policy.include_prefixes
        ):
            return None
    return "operational"


def _selection_rank(relative_skill_dir: str, scope_skill: str) -> tuple[int, int, int, str]:
    is_cache = is_mirror_path(relative_skill_dir)
    scope_matches_path = relative_skill_dir == scope_skill
    depth = relative_skill_dir.count("/")
    return (1 if is_cache else 0, 0 if scope_matches_path else 1, depth, relative_skill_dir)


def discover_inventory_skills(repo_root: Path, policy: InventoryPolicy) -> List[InventorySkill]:
    rows_by_scope: dict[str, InventorySkill] = {}
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        rel_skill_md = skill_md.relative_to(repo_root).as_posix()
        rel_skill_dir = skill_md.parent.relative_to(repo_root).as_posix()
        scope_skill = resolve_scope_skill_for_path(rel_skill_dir)
        inventory_slice = _classify_slice(rel_skill_md, rel_skill_dir, scope_skill, policy)
        if not inventory_slice:
            continue
        row = InventorySkill(
            skill_md=skill_md,
            relative_skill_dir=rel_skill_dir,
            scope_skill=scope_skill,
            inventory_slice=inventory_slice,
            source_skill_dirs=(rel_skill_dir,),
        )
        existing = rows_by_scope.get(scope_skill)
        if existing is None:
            rows_by_scope[scope_skill] = row
            continue
        if existing.relative_skill_dir == row.relative_skill_dir:
            merged_sources = tuple(sorted(set(existing.source_skill_dirs + row.source_skill_dirs)))
            if merged_sources != existing.source_skill_dirs:
                rows_by_scope[scope_skill] = InventorySkill(
                    skill_md=existing.skill_md,
                    relative_skill_dir=existing.relative_skill_dir,
                    scope_skill=existing.scope_skill,
                    inventory_slice=existing.inventory_slice,
                    source_skill_dirs=merged_sources,
                )
            continue
        if not is_mirror_path(existing.relative_skill_dir) and not is_mirror_path(row.relative_skill_dir):
            raise ValueError(
                "Duplicate semantic scope_skill claimed by non-mirror sources: "
                f"{scope_skill} -> {existing.relative_skill_dir}, {row.relative_skill_dir}"
            )
        merged_sources = tuple(sorted(set(existing.source_skill_dirs + row.source_skill_dirs)))
        if _selection_rank(row.relative_skill_dir, row.scope_skill) < _selection_rank(
            existing.relative_skill_dir, existing.scope_skill
        ):
            rows_by_scope[scope_skill] = InventorySkill(
                skill_md=row.skill_md,
                relative_skill_dir=row.relative_skill_dir,
                scope_skill=row.scope_skill,
                inventory_slice=row.inventory_slice,
                source_skill_dirs=merged_sources,
            )
        else:
            rows_by_scope[scope_skill] = InventorySkill(
                skill_md=existing.skill_md,
                relative_skill_dir=existing.relative_skill_dir,
                scope_skill=existing.scope_skill,
                inventory_slice=existing.inventory_slice,
                source_skill_dirs=merged_sources,
            )
    return sorted(rows_by_scope.values(), key=lambda item: item.scope_skill)
