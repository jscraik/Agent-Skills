#!/usr/bin/env python3
"""Runtime surface policy shared by discovery, sync, and budget checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from selection_policy import (
    DEFAULT_INCLUDE_FIRST_PARTY_REPO_SKILLS,
    HIDDEN_FLAT_SKILL_NAMES,
    PLUGIN_HIDDEN_LANE_SKILL_NAMES,
    PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
    ROOT_SKILL_SET_NAMES,
)

HIDDEN_FLAT_SKILLS = set(HIDDEN_FLAT_SKILL_NAMES)
PLUGIN_HIDDEN_LANE_SKILLS = set(PLUGIN_HIDDEN_LANE_SKILL_NAMES)
PLUGIN_VISIBLE_ROUTER_SKILLS = set(PLUGIN_VISIBLE_ROUTER_SKILL_NAMES)
ROOT_SKILL_SETS = set(ROOT_SKILL_SET_NAMES)

PROJECTION_FLAT = "flat"
PROJECTION_ROOTED = "rooted"
PROJECTION_MIXED = "mixed"


@dataclass(frozen=True)
class RuntimeSurfaceReport:
    projection_mode: str
    first_level_names: set[str]
    expected_first_level_names: set[str]
    extra_first_level_names: list[str]
    missing_first_level_names: list[str]
    root_skill_set_names: set[str]
    flat_skill_names: set[str]

    @property
    def is_valid_projection(self) -> bool:
        """Return whether the first-level runtime shape maps to a supported projection."""
        return self.projection_mode in {PROJECTION_FLAT, PROJECTION_ROOTED}


def runtime_surface_report(first_level_names: Iterable[str]) -> RuntimeSurfaceReport:
    """Classify a runtime surface and return first-level policy drift details."""
    actual = {name for name in first_level_names if name}
    root_names = actual & ROOT_SKILL_SETS
    flat_names = actual - ROOT_SKILL_SETS

    if root_names and actual - ROOT_SKILL_SETS:
        projection_mode = PROJECTION_MIXED
        expected = set(ROOT_SKILL_SETS)
    elif root_names:
        projection_mode = PROJECTION_ROOTED
        expected = set(ROOT_SKILL_SETS)
    else:
        projection_mode = PROJECTION_FLAT
        expected = set(actual) if DEFAULT_INCLUDE_FIRST_PARTY_REPO_SKILLS else set()

    return RuntimeSurfaceReport(
        projection_mode=projection_mode,
        first_level_names=actual,
        expected_first_level_names=expected,
        extra_first_level_names=sorted(actual - expected),
        missing_first_level_names=sorted(expected - actual),
        root_skill_set_names=root_names,
        flat_skill_names=flat_names,
    )


def active_projection_mode(first_level_names: Iterable[str]) -> str:
    """Return the active runtime projection mode from first-level runtime entries."""
    return runtime_surface_report(first_level_names).projection_mode


def is_default_visible_skill_name(name: str, *, plugin_owned: bool = False) -> bool:
    """Return whether a skill name belongs on the default runtime discovery surface."""
    if name in HIDDEN_FLAT_SKILLS:
        return False
    if not DEFAULT_INCLUDE_FIRST_PARTY_REPO_SKILLS and name not in ROOT_SKILL_SETS:
        return False
    if plugin_owned and name not in PLUGIN_VISIBLE_ROUTER_SKILLS:
        return False
    if plugin_owned and name in PLUGIN_HIDDEN_LANE_SKILLS:
        return False
    return True


def expected_first_level_runtime_names(projection_mode: str) -> set[str]:
    """Return the expected first-level runtime entries for a projection mode."""
    if projection_mode == PROJECTION_ROOTED:
        return set(ROOT_SKILL_SETS)
    if projection_mode == PROJECTION_FLAT:
        return set()
    raise ValueError(f"Unsupported projection mode: {projection_mode}")


def rooted_runtime_name_drift(first_level_names: Iterable[str]) -> tuple[list[str], list[str]]:
    """Return (extra, missing) first-level entries for a rooted runtime surface."""
    report = runtime_surface_report(first_level_names)
    expected = expected_first_level_runtime_names(PROJECTION_ROOTED)
    return sorted(report.first_level_names - expected), sorted(expected - report.first_level_names)
