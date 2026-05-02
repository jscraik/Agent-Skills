"""Contract tests for the insight-report compatibility runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path


RUNNER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_insight_report.py"


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("insight_report_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_runner_points_to_deferred_source():
    module = _load_runner_module()

    assert module.RUNNER.is_file()
    assert module.RUNNER.name == "run_insight_report.py"
    assert "Infrastructure/references/deferred-skill-context/agent-ops-insight-report" in module.RUNNER.as_posix()
