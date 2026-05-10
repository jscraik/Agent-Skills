#!/usr/bin/env python3
"""Regression tests for the HE lifecycle release eval wrapper."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_lifecycle_release_evals import summarize


class LifecycleReleaseEvalSummaryTests(unittest.TestCase):
    def test_summarize_separates_timeout_content_tool_and_selection_signal(self) -> None:
        raw_selection_warning = json.dumps(
            {
                "cases": [
                    {
                        "id": "route-case",
                        "name": "route case",
                        "category": "edge",
                        "warnings": [
                            "[codex] should_trigger expected skill to be selected, "
                            "but selection signal was unavailable for this run."
                        ],
                    }
                ]
            }
        )
        results = [
            {
                "skill": "he-router",
                "returncode": 124,
                "status": "timeout",
                "timeout_seconds": 300,
                "duration_seconds": 300.1,
                "raw_output": "",
                "errors": [{"code": "ERR_TIMEOUT", "message": "timed out"}],
            },
            {
                "skill": "he-spec",
                "returncode": 1,
                "status": "error",
                "failure_classification": {
                    "content_failure_cases": [
                        {
                            "id": "spec-case",
                            "name": "spec case",
                            "category": "happy",
                            "tier1_failures": ["regex failed: /safe_to_continue/"],
                        }
                    ],
                    "timeout_cases": [],
                    "other_failure_cases": [],
                },
                "raw_output": "",
                "errors": [{"code": "ERR_VALIDATION", "message": "Evaluation run failed."}],
            },
            {
                "skill": "he-work",
                "returncode": 126,
                "status": "blocked",
                "raw_output": "",
                "errors": [{"code": "ERR_ASK_UNAVAILABLE", "message": "./bin/ask is missing"}],
            },
            {
                "skill": "he-code-review",
                "returncode": 0,
                "status": "success",
                "raw_output": raw_selection_warning,
                "errors": [],
            },
        ]

        summary = summarize(results)
        breakdown = summary["failure_breakdown"]

        self.assertEqual(summary["status"], "fail")
        self.assertEqual([item["skill"] for item in breakdown["timeout_failures"]], ["he-router"])
        self.assertEqual([item["skill"] for item in breakdown["content_failures"]], ["he-spec"])
        self.assertEqual([item["skill"] for item in breakdown["tool_preflight_failures"]], ["he-work"])
        self.assertEqual(
            [item["skill"] for item in breakdown["selection_signal_warnings"]],
            ["he-code-review"],
        )
        self.assertEqual(breakdown["other_failures"], [])

    def test_summarize_keeps_timeout_case_classification(self) -> None:
        results = [
            {
                "skill": "he-eval-report",
                "returncode": 1,
                "status": "error",
                "failure_classification": {
                    "timeout_cases": [
                        {
                            "id": "release-confidence-timeout-block",
                            "name": "release confidence timeout block",
                            "category": "negative",
                            "tier1_failures": ["[codex] codex returned non-zero exit code: 124"],
                        }
                    ],
                    "content_failure_cases": [],
                    "other_failure_cases": [],
                },
                "raw_output": "",
                "errors": [{"code": "ERR_VALIDATION", "message": "Evaluation run failed."}],
            }
        ]

        summary = summarize(results)
        timeout_failures = summary["failure_breakdown"]["timeout_failures"]

        self.assertEqual(len(timeout_failures), 1)
        self.assertEqual(timeout_failures[0]["skill"], "he-eval-report")
        self.assertEqual(
            timeout_failures[0]["case_classification"][0]["id"],
            "release-confidence-timeout-block",
        )
        self.assertEqual(summary["failure_breakdown"]["content_failures"], [])


if __name__ == "__main__":
    unittest.main()
