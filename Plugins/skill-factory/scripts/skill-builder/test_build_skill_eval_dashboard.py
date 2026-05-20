#!/usr/bin/env python3
"""Regression tests for aggregate skill eval dashboard rendering."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_skill_eval_dashboard import build_dashboard, collect_scorecards, summarize_run, to_markdown
from eval_signal_contract import (
    EXPECTED_SIGNAL_COMPOSITE_KEY,
    EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY,
    EXPECTED_SIGNAL_METRIC_KEY,
    EXPECTED_SIGNAL_MISSING_KEY,
    EXPECTED_SIGNAL_RISK_FACTORS_KEY,
)


class BuildSkillEvalDashboardTests(unittest.TestCase):
    def test_summarize_run_uses_expected_signal_contract_metrics(self) -> None:
        summary = summarize_run(
            {
                "runner_mode": "discovery-smoke",
                "tier2_mode": "warn",
                "passed": False,
                "cases": [
                    {
                        "id": "case-a",
                        "passed": False,
                        "tier1_failed": True,
                        "tier2_failed": False,
                        "runners": {
                            "discovery-smoke": {
                                "metrics": {
                                    EXPECTED_SIGNAL_METRIC_KEY: {
                                        EXPECTED_SIGNAL_COMPOSITE_KEY: 75,
                                        EXPECTED_SIGNAL_RISK_FACTORS_KEY: ["expected signal score below 80"],
                                        EXPECTED_SIGNAL_MISSING_KEY: ["required term: canonical source"],
                                        EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY: [],
                                    }
                                }
                            }
                        },
                    },
                    {
                        "id": "case-b",
                        "passed": True,
                        "tier1_failed": False,
                        "tier2_failed": False,
                        "runners": {
                            "discovery-smoke": {
                                "metrics": {
                                    EXPECTED_SIGNAL_METRIC_KEY: {
                                        EXPECTED_SIGNAL_COMPOSITE_KEY: 100,
                                        EXPECTED_SIGNAL_RISK_FACTORS_KEY: [],
                                        EXPECTED_SIGNAL_MISSING_KEY: [],
                                        EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY: [],
                                    }
                                }
                            }
                        },
                    },
                ],
            }
        )

        self.assertEqual(summary["expected_signal_summary"]["runs"], 2)
        self.assertEqual(summary["expected_signal_summary"]["average"], 88)
        self.assertEqual(summary["expected_signal_summary"]["minimum"], 75)
        self.assertEqual(summary["expected_signal_summary"]["missing_signal_count"], 1)
        self.assertEqual(summary["expected_signal_summary"]["risky_cases"][0]["case"], "case-a")

    def test_build_dashboard_markdown_includes_expected_signal_average(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "Infrastructure" / "artifacts" / "skills"
            scorecard_path = root / "skill-builder" / "run-1" / "scorecard.json"
            scorecard_path.parent.mkdir(parents=True)
            scorecard_path.write_text(
                json.dumps(
                    {
                        "runner_mode": "discovery-smoke",
                        "passed": True,
                        "cases": [
                            {
                                "id": "case-a",
                                "passed": True,
                                "runners": {
                                    "discovery-smoke": {
                                        "metrics": {
                                            EXPECTED_SIGNAL_METRIC_KEY: {
                                                EXPECTED_SIGNAL_COMPOSITE_KEY: 92,
                                                EXPECTED_SIGNAL_RISK_FACTORS_KEY: [],
                                                EXPECTED_SIGNAL_MISSING_KEY: [],
                                                EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY: [],
                                            }
                                        }
                                    }
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            dashboard = build_dashboard(collect_scorecards(root))
            markdown = to_markdown(dashboard)

        latest = dashboard["skills"]["skill-builder"]["latest"]
        self.assertEqual(latest["expected_signal_summary"]["average"], 92)
        self.assertIn("| skill-builder | 1 | 0 | 0 | 92% |", markdown)

    def test_collect_scorecards_includes_latest_scorecards(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "Infrastructure" / "artifacts" / "skills"
            scorecard_path = root / "skill-builder" / "latest-scorecard.json"
            scorecard_path.parent.mkdir(parents=True)
            scorecard_path.write_text(
                json.dumps({"runner_mode": "discovery-smoke", "passed": True, "cases": []}),
                encoding="utf-8",
            )

            scorecards = collect_scorecards(root)

        self.assertIn("skill-builder", scorecards)
        self.assertEqual(scorecards["skill-builder"][0][0], "latest")


if __name__ == "__main__":
    unittest.main()
