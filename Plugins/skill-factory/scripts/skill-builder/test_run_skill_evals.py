#!/usr/bin/env python3
"""Compatibility entrypoint for the split run_skill_evals test modules."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def main() -> int:
    suite = unittest.defaultTestLoader.discover(
        str(SCRIPT_DIR), pattern="test_run_skill_evals_*.py", top_level_dir=str(SCRIPT_DIR)
    )
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
