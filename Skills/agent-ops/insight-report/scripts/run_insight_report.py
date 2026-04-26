#!/usr/bin/env python3
"""Compatibility runner for the insight-report skill."""

from __future__ import annotations

import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
RUNNER = (
    REPO_ROOT
    / "Infrastructure"
    / "references"
    / "deferred-skill-context"
    / "agent-ops-insight-report"
    / "scripts"
    / "run_insight_report.py"
)


if __name__ == "__main__":
    if not RUNNER.is_file():
        raise SystemExit(f"insight-report runner missing: {RUNNER}")
    runpy.run_path(str(RUNNER), run_name="__main__")
