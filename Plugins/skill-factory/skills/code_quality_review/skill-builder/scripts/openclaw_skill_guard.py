#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

_IMPL_PATH = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "openclaw_skill_guard.py"
if not _IMPL_PATH.is_file():
    raise FileNotFoundError(f"Implementation not found: {_IMPL_PATH}")
_IMPL_DIR = _IMPL_PATH.parent
if str(_IMPL_DIR) not in sys.path:
    sys.path.insert(0, str(_IMPL_DIR))

globals().update(runpy.run_path(str(_IMPL_PATH), run_name=__name__))
