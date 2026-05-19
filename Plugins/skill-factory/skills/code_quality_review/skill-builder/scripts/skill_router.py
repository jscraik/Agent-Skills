#!/usr/bin/env python3
"""Compatibility wrapper for the canonical skill router implementation."""

from pathlib import Path
import runpy
import sys

_IMPL_PATH = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "skill_router.py"
sys.path.insert(0, str(_IMPL_PATH.parent))

_run_name = "__main__" if __name__ == "__main__" else "skill_router"
globals().update(runpy.run_path(str(_IMPL_PATH), run_name=_run_name))
