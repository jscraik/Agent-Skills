#!/usr/bin/env python3
"""Stable skill entrypoint for keep-codex-fast."""

from __future__ import annotations

import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "agent-ops" / "keep_codex_fast.py"


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
