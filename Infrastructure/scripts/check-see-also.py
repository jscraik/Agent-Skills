#!/usr/bin/env python3
"""Compatibility wrapper for the relocated see-also gate script."""

from __future__ import annotations

import runpy
from pathlib import Path

TARGET = (
    Path(__file__).resolve().parent
    / "validation-and-linting"
    / "check-see-also.py"
)

if not TARGET.is_file():
    raise FileNotFoundError(f"Missing target script: {TARGET}")

runpy.run_path(str(TARGET), run_name="__main__")
