#!/usr/bin/env python3
"""Compatibility wrapper for the canonical skill router implementation."""

from pathlib import Path
import runpy
import sys

_IMPL_PATH = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "skill_router.py"
if not _IMPL_PATH.is_file():
    raise FileNotFoundError(f"Implementation not found: {_IMPL_PATH}")
_IMPL_DIR = str(_IMPL_PATH.parent)
if _IMPL_DIR not in sys.path:
    sys.path.insert(0, _IMPL_DIR)

_run_name = "__main__" if __name__ == "__main__" else "skill_router"
globals().update(runpy.run_path(str(_IMPL_PATH), run_name=_run_name))
