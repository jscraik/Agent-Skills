#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys


def find_impl() -> Path:
    current = Path(__file__).resolve()
    for ancestor in current.parents:
        candidate = (
            ancestor
            / "Plugins"
            / "skill-factory"
            / "scripts"
            / "skill-builder"
            / "quick_validate.py"
        )
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Implementation not found for wrapper: {current}")


impl = find_impl()
if not impl.is_file():
    raise FileNotFoundError(f"Implementation not found: {impl}")
impl_dir = str(impl.parent)
if impl_dir not in sys.path:
    sys.path.insert(0, impl_dir)
runpy.run_path(str(impl), run_name="__main__")
