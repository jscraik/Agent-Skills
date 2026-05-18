#!/usr/bin/env python3
"""Compatibility wrapper for the steering uptake validator."""

from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "validation-and-linting/validate_steering_uptake.py"),
        run_name="__main__",
    )
