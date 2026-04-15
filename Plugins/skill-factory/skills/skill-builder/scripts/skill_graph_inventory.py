#!/usr/bin/env python3
"""Shared canonical inventory policy helpers for skill-graph onboarding scripts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set

DEFAULT_INVENTORY_POLICY = "docs/skill-graphs/governance/inventory-policy.json"
DEFAULT_SYSTEM_PREFIXES = ("Skills/.system/", ".agents/skills/.system/")
SYSTEM_SLICE_MODES = {"exclude", "separate"}


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
    inventory_slice: str


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
            "Create docs/skill-graphs/governance/inventory-policy.json."
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


def _classify_slice(rel_skill_md: str, rel_skill_dir: str, policy: InventoryPolicy) -> Optional[str]:
    if rel_skill_md == "SKILL.md":
        return None
    if any(rel_skill_md.startswith(prefix) for prefix in policy.exclude_prefixes):
        return None

    if any(rel_skill_md.startswith(prefix) for prefix in policy.system_prefixes):
        if policy.system_slice_mode == "separate":
            return "system"
        return None

    if policy.allowlist_scope_skills and rel_skill_dir not in policy.allowlist_scope_skills:
        return None
    if policy.include_prefixes and not any(rel_skill_md.startswith(prefix) for prefix in policy.include_prefixes):
        return None
    return "operational"


def discover_inventory_skills(repo_root: Path, policy: InventoryPolicy) -> List[InventorySkill]:
    rows: List[InventorySkill] = []
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        rel_skill_md = skill_md.relative_to(repo_root).as_posix()
        rel_skill_dir = skill_md.parent.relative_to(repo_root).as_posix()
        inventory_slice = _classify_slice(rel_skill_md, rel_skill_dir, policy)
        if not inventory_slice:
            continue
        rows.append(
            InventorySkill(
                skill_md=skill_md,
                relative_skill_dir=rel_skill_dir,
                inventory_slice=inventory_slice,
            )
        )
    return rows
