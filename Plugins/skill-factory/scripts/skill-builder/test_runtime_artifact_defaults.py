#!/usr/bin/env python3
"""Prevent skill-quality tooling and plans from regenerating tracked reports."""

from __future__ import annotations

from importlib import import_module
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

refresh_benchmark_policy = import_module("refresh_benchmark_policy")


class RuntimeArtifactDefaultTests(unittest.TestCase):
    def test_benchmark_refresh_defaults_are_runtime_owned(self) -> None:
        with patch.object(sys, "argv", ["refresh_benchmark_policy.py"]):
            args = refresh_benchmark_policy.parse_args()

        self.assertEqual(
            args.benchmark_json,
            ".tmp/agent-skills-artifacts/industry-benchmark-latest.json",
        )
        self.assertEqual(
            args.report_json,
            ".tmp/agent-skills-artifacts/benchmark-policy-refresh-report.json",
        )

    def test_workflow_guides_do_not_restore_tracked_benchmark_outputs(self) -> None:
        retired_paths = (
            "Infrastructure/artifacts/industry-benchmark-latest.json",
            "Infrastructure/artifacts/benchmark-policy-refresh-report.json",
        )
        guides = (
            REPO_ROOT / "Docs/skill-graphs/workflows/benchmark-policy-refresh.md",
            REPO_ROOT / "Docs/skill-graphs/workflows/skill-quality.md",
        )

        for guide in guides:
            source = guide.read_text(encoding="utf-8")
            with self.subTest(guide=guide.name):
                for retired_path in retired_paths:
                    self.assertNotIn(retired_path, source)

    def test_authoring_plan_keeps_ai_session_evidence_untracked(self) -> None:
        retired_root = "Infrastructure/artifacts/ai/sessions/"
        plan = (
            REPO_ROOT
            / "docs/plans/2026-04-06-feat-skill-authoring-family-certification-plan.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn(retired_root, plan)
        self.assertIn(".tmp/agent-skills-artifacts/ai/sessions/", plan)
        self.assertFalse(
            (
                REPO_ROOT
                / retired_root
                / "2026-04-06-skill-authoring-family-certification.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
