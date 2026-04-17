#!/usr/bin/env python3
"""Compatibility wrapper for moved script entrypoint."""

from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "validation-and-linting/docs_lint.py"), run_name="__main__")
