#!/usr/bin/env python3
from pathlib import Path
import runpy

root = next(
    p for p in Path(__file__).resolve().parents
    if (p / "Infrastructure/scripts/skill-refactor").is_dir()
)
target = root / "Infrastructure/scripts/skill-refactor/correlate_multi_source_skill_failures.py"
globals().update(runpy.run_path(str(target), run_name=__name__))
