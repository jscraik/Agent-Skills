#!/usr/bin/env python3
"""Skill-local wrapper for the Goal Governor board validator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
IMPL_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "goal-governor" / "check_goal_board_impl.py"
SPEC = importlib.util.spec_from_file_location("goal_governor_check_goal_board_impl", IMPL_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"cannot load Goal Governor board validator: {IMPL_PATH}")

_impl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_impl)

for _name in dir(_impl):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_impl, _name)


if __name__ == "__main__":
    raise SystemExit(_impl.main(sys.argv))
