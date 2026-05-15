#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

_IMPL_PATH = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "skill_gate.py"
_IMPL_DIR = _IMPL_PATH.parent
if str(_IMPL_DIR) not in sys.path:
    sys.path.insert(0, str(_IMPL_DIR))

_run_name = "__main__" if __name__ == "__main__" else "skill_gate"
globals().update(runpy.run_path(str(_IMPL_PATH), run_name=_run_name))
