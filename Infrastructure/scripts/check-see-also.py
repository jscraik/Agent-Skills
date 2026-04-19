#!/usr/bin/env python3
"""Compatibility wrapper for the relocated see-also gate script."""

from __future__ import annotations

import runpy
from pathlib import Path

target = (
    Path(__file__).resolve().parent
    / "validation-and-linting"
    / "check-see-also.py"
)

if not target.is_file():
    raise FileNotFoundError(f"Missing target script: {target}")

runpy.run_path(str(target), run_name="__main__")
