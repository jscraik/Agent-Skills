#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

impl = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "upgrade_skill.py"
sys.path.insert(0, str(impl.parent))
runpy.run_path(str(impl), run_name="__main__")
