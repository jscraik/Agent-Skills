#!/usr/bin/env python3
"""Control-plane helpers for skill router rollout mode precedence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _read_bool_control(path: Path) -> bool:
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8").strip().lower()
    return content not in {"off", "false", "0", "no", "inactive"}


def _read_mode(path: Path, default: str = "observe_only") -> str:
    if not path.exists():
        return default
    mode = path.read_text(encoding="utf-8").strip().lower()
    return mode if mode in {"off", "observe_only", "active"} else default


@dataclass
class ControlResolution:
    effective_mode: str
    reason: str


def resolve_rollout_mode(controls_dir: Path | None, requested_policy_mode: str) -> ControlResolution:
    """Resolve effective mode using control files before requested policy mode."""
    requested = requested_policy_mode.lower().strip()
    if requested not in {"observe_only", "co_pilot", "autopilot"}:
        requested = "observe_only"

    if controls_dir is None:
        return ControlResolution(effective_mode=requested, reason="no_controls_dir")

    kill_switch = _read_bool_control(controls_dir / "kill-switch.txt")
    rollback_required = _read_bool_control(controls_dir / "rollback-required.txt")
    rollout_mode = _read_mode(controls_dir / "rollout-mode.txt", default="observe_only")

    if kill_switch:
        return ControlResolution(effective_mode="observe_only", reason="kill_switch")
    if rollback_required:
        return ControlResolution(effective_mode="observe_only", reason="rollback_required")
    if rollout_mode == "off":
        return ControlResolution(effective_mode="observe_only", reason="rollout_mode_off")
    if rollout_mode == "observe_only":
        return ControlResolution(effective_mode="observe_only", reason="rollout_mode_observe_only")

    return ControlResolution(effective_mode=requested, reason="rollout_mode_active")
