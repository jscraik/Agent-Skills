#!/usr/bin/env python3
"""Runtime surface policy shared by discovery, sync, and budget checks."""

from __future__ import annotations

from typing import Iterable

from selection_policy import (
    DEFAULT_VISIBLE_FLAT_SKILL_NAMES,
    HIDDEN_FLAT_SKILL_NAMES,
    PLUGIN_HIDDEN_LANE_SKILL_NAMES,
    PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
    ROOT_SKILL_SET_NAMES,
)

DEFAULT_VISIBLE_FLAT_SKILLS = set(DEFAULT_VISIBLE_FLAT_SKILL_NAMES)
HIDDEN_FLAT_SKILLS = set(HIDDEN_FLAT_SKILL_NAMES)
PLUGIN_HIDDEN_LANE_SKILLS = set(PLUGIN_HIDDEN_LANE_SKILL_NAMES)
PLUGIN_VISIBLE_ROUTER_SKILLS = set(PLUGIN_VISIBLE_ROUTER_SKILL_NAMES)
ROOT_SKILL_SETS = set(ROOT_SKILL_SET_NAMES)


def active_projection_mode(first_level_names: Iterable[str]) -> str:
    """Infer the active runtime projection mode from first-level runtime entries."""
    return "rooted" if set(first_level_names) & ROOT_SKILL_SETS else "flat"


def is_default_visible_skill_name(name: str, *, plugin_owned: bool = False) -> bool:
    """Return whether a skill name belongs on the default runtime discovery surface."""
    if name in HIDDEN_FLAT_SKILLS:
        return False
    if name not in DEFAULT_VISIBLE_FLAT_SKILLS and name not in ROOT_SKILL_SETS:
        return False
    if plugin_owned and name not in PLUGIN_VISIBLE_ROUTER_SKILLS:
        return False
    if plugin_owned and name in PLUGIN_HIDDEN_LANE_SKILLS:
        return False
    return True


def expected_first_level_runtime_names(projection_mode: str) -> set[str]:
    """Return the expected first-level runtime entries for a projection mode."""
    if projection_mode == "rooted":
        return set(ROOT_SKILL_SETS)
    if projection_mode == "flat":
        return set(DEFAULT_VISIBLE_FLAT_SKILLS)
    raise ValueError(f"Unsupported projection mode: {projection_mode}")


def rooted_runtime_name_drift(first_level_names: Iterable[str]) -> tuple[list[str], list[str]]:
    """Return (extra, missing) first-level entries for a rooted runtime surface."""
    actual = set(first_level_names)
    expected = expected_first_level_runtime_names("rooted")
    return sorted(actual - expected), sorted(expected - actual)
