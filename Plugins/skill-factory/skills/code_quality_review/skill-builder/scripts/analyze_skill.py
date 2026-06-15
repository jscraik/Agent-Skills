#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

impl = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "analyze_skill.py"
if not impl.is_file():
    raise FileNotFoundError(f"Implementation not found: {impl}")
impl_dir = str(impl.parent)
if impl_dir not in sys.path:
    sys.path.insert(0, impl_dir)
runpy.run_path(str(impl), run_name="__main__")
