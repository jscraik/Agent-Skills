#!/usr/bin/env python3
"""Delegate keep-codex-fast smoke coverage to the repo test surface."""

from __future__ import annotations

import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
TEST_PATH = REPO_ROOT / "Infrastructure" / "tests" / "test_keep_codex_fast.py"


if __name__ == "__main__":
    runpy.run_path(str(TEST_PATH), run_name="__main__")
