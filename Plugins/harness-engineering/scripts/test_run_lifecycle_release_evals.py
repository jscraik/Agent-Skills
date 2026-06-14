#!/usr/bin/env python3
"""Regression tests for the HE lifecycle release eval wrapper."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_lifecycle_release_evals import _classify_case_failures, _run_skill_builder_eval, run_skill, summarize


class LifecycleReleaseEvalSummaryTests(unittest.TestCase):
    def test_cli_rejects_model_other_than_fixed_spark(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "run_lifecycle_release_evals.py"),
                "--mode",
                "release",
                "--eval-runner",
                "codex",
                "--skill",
                "he-reconcile",
                "--model",
                "gpt-5.4",
                "--json",
            ],
            cwd=SCRIPT_DIR.parents[2],
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--model is fixed to gpt-5.3-codex-spark", result.stderr)

    def test_direct_codex_eval_uses_fixed_spark_model_without_reasoning(self) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout=json.dumps({"decision": "pass"}),
            stderr="",
        )
        with mock.patch("run_lifecycle_release_evals.subprocess.run", return_value=completed) as run:
            result = _run_skill_builder_eval(
                Path("/tmp/repo"),
                "he-reconcile",
                "release",
                "codex",
                (),
                (),
                90,
                "gpt-5.4",
                None,
                Path("/tmp/codex-home"),
            )

        self.assertEqual(result["status"], "success")
        cmd = run.call_args.args[0]
        self.assertIn("--model", cmd)
        self.assertEqual(cmd[cmd.index("--model") + 1], "gpt-5.3-codex-spark")
        self.assertIn("--codex-arg", cmd)
        self.assertEqual(cmd[cmd.index("--codex-arg") + 1], "--ignore-user-config")
        self.assertNotIn("--reasoning", cmd)
        self.assertNotIn("--reasoning-effort", cmd)

    def test_direct_codex_eval_omits_codex_home_by_default_for_runner_isolation(self) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout=json.dumps({"decision": "pass"}),
            stderr="",
        )
        with mock.patch("run_lifecycle_release_evals.subprocess.run", return_value=completed) as run:
            result = _run_skill_builder_eval(
                Path("/tmp/repo"),
                "he-reconcile",
                "release",
                "codex",
                (),
                (),
                90,
                None,
                None,
                None,
            )

        self.assertEqual(result["status"], "success")
        cmd = run.call_args.args[0]
        self.assertNotIn("--codex-home", cmd)

    def test_usage_limit_jsonl_classifies_as_tool_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl = Path(tmpdir) / "codex_events.jsonl"
            jsonl.write_text(
                '{"type":"error","message":"You have hit your usage limit for GPT-5.3-Codex-Spark."}\n',
                encoding="utf-8",
            )
            parsed = {
                "cases": [
                    {
                        "id": "explicit-eval-route",
                        "name": "Explicit eval route",
                        "category": "happy",
                        "tier1_failures": ["[codex] codex returned non-zero exit code: 1"],
                        "runners": {
                            "codex": {
                                "artifacts": {
                                    "jsonl": str(jsonl),
                                }
                            }
                        },
                    }
                ]
            }

            classified = _classify_case_failures(parsed)

        self.assertEqual(len(classified["tool_preflight_cases"]), 1)
        self.assertEqual(classified["tool_preflight_cases"][0]["id"], "explicit-eval-route")
        self.assertEqual(classified["other_failure_cases"], [])

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
                "skill": "he-reconcile",
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
        self.assertEqual([item["skill"] for item in breakdown["timeout_failures"]], ["he-reconcile"])
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

    def test_codex_release_defaults_to_split_case_execution(self) -> None:
        with (
            mock.patch(
                "run_lifecycle_release_evals._list_skill_builder_cases",
                return_value=(["case-a", "case-b"], None),
            ),
            mock.patch("run_lifecycle_release_evals._run_skill_builder_eval") as run_case,
        ):
            run_case.side_effect = [
                {
                    "skill": "he-reconcile",
                    "returncode": 0,
                    "status": "success",
                    "decision": "pass",
                    "case_filters": ["case-a"],
                    "failure_classification": {
                        "timeout_cases": [],
                        "content_failure_cases": [],
                        "other_failure_cases": [],
                    },
                    "raw_output": "",
                    "errors": [],
                },
                {
                    "skill": "he-reconcile",
                    "returncode": 1,
                    "status": "error",
                    "decision": "fail",
                    "case_filters": ["case-b"],
                    "failure_classification": {
                        "timeout_cases": [],
                        "content_failure_cases": [
                            {
                                "id": "case-b",
                                "name": "case b",
                                "category": "edge",
                                "tier1_failures": ["regex failed: /blocked/"],
                            }
                        ],
                        "other_failure_cases": [],
                    },
                    "raw_output": "",
                    "errors": [{"code": "ERR_VALIDATION", "message": "Evaluation run failed."}],
                },
            ]

            result = run_skill(
                Path("/tmp/repo"),
                "he-reconcile",
                "release",
                "codex",
                (),
                (),
                90,
                None,
                None,
                True,
                Path("/tmp/codex-home"),
            )

        self.assertTrue(result["split_cases"])
        self.assertEqual(result["returncode"], 2)
        self.assertEqual(result["status"], "error")
        self.assertEqual(len(result["case_results"]), 2)
        self.assertEqual(
            result["failure_classification"]["content_failure_cases"][0]["id"],
            "case-b",
        )
        self.assertEqual(run_case.call_count, 2)
        first_call = run_case.call_args_list[0].args
        self.assertEqual(first_call[-1], Path("/tmp/codex-home"))

    def test_split_case_execution_preserves_case_timeout_classification(self) -> None:
        with (
            mock.patch(
                "run_lifecycle_release_evals._list_skill_builder_cases",
                return_value=(["slow-case"], None),
            ),
            mock.patch("run_lifecycle_release_evals._run_skill_builder_eval") as run_case,
        ):
            run_case.return_value = {
                "skill": "he-work",
                "returncode": 124,
                "status": "timeout",
                "decision": "timeout",
                "case_filters": ["slow-case"],
                "timeout_seconds": 60,
                "errors": [{"code": "ERR_TIMEOUT", "message": "timed out after 60 seconds"}],
                "raw_output": "",
            }

            result = run_skill(
                Path("/tmp/repo"),
                "he-work",
                "release",
                "codex",
                (),
                (),
                60,
                None,
                None,
                True,
                Path("/tmp/codex-home"),
            )

        self.assertEqual(result["status"], "timeout")
        self.assertEqual(
            result["failure_classification"]["timeout_cases"][0]["id"],
            "slow-case",
        )

    def test_split_case_execution_reports_slow_pass_cases_without_failing(self) -> None:
        with (
            mock.patch(
                "run_lifecycle_release_evals._list_skill_builder_cases",
                return_value=(["slow-pass"], None),
            ),
            mock.patch("run_lifecycle_release_evals._run_skill_builder_eval") as run_case,
        ):
            run_case.return_value = {
                "skill": "he-spec",
                "returncode": 0,
                "status": "success",
                "decision": "pass",
                "case_filters": ["slow-pass"],
                "duration_seconds": 121.5,
                "failure_classification": {
                    "timeout_cases": [],
                    "content_failure_cases": [],
                    "other_failure_cases": [],
                    "tool_preflight_cases": [],
                },
                "raw_output": "",
                "errors": [],
            }

            result = run_skill(
                Path("/tmp/repo"),
                "he-spec",
                "release",
                "codex",
                (),
                (),
                300,
                None,
                None,
                True,
                Path("/tmp/codex-home"),
            )

        summary = summarize([result])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["slow_cases"][0]["id"], "slow-pass")
        self.assertEqual(summary["status"], "pass")
        self.assertEqual(
            summary["failure_breakdown"]["slow_pass_cases"][0]["cases"][0]["id"],
            "slow-pass",
        )
        self.assertEqual(summary["failure_breakdown"]["timeout_failures"], [])
        self.assertEqual(summary["failure_breakdown"]["content_failures"], [])

    def test_split_case_execution_can_be_bounded_by_case_count(self) -> None:
        with (
            mock.patch(
                "run_lifecycle_release_evals._list_skill_builder_cases",
                return_value=(["case-a", "case-b", "case-c"], None),
            ),
            mock.patch("run_lifecycle_release_evals._run_skill_builder_eval") as run_case,
        ):
            run_case.return_value = {
                "skill": "he-reconcile",
                "returncode": 0,
                "status": "success",
                "decision": "pass",
                "case_filters": ["case-a"],
                "failure_classification": {
                    "timeout_cases": [],
                    "content_failure_cases": [],
                    "other_failure_cases": [],
                    "tool_preflight_cases": [],
                },
                "raw_output": "",
                "errors": [],
            }

            result = run_skill(
                Path("/tmp/repo"),
                "he-reconcile",
                "release",
                "codex",
                (),
                (),
                90,
                None,
                None,
                True,
                Path("/tmp/codex-home"),
                1,
            )

        self.assertEqual(run_case.call_count, 1)
        self.assertTrue(result["bounded_run"])
        self.assertEqual(result["discovered_case_count"], 3)
        self.assertEqual(result["executed_case_count"], 1)
        self.assertEqual(result["skipped_case_count"], 2)
        self.assertEqual(result["max_cases"], 1)

    def test_split_case_execution_stops_after_tool_preflight_limit(self) -> None:
        with (
            mock.patch(
                "run_lifecycle_release_evals._list_skill_builder_cases",
                return_value=(["case-a", "case-b"], None),
            ),
            mock.patch("run_lifecycle_release_evals._run_skill_builder_eval") as run_case,
        ):
            run_case.return_value = {
                "skill": "he-reconcile",
                "returncode": 1,
                "status": "error",
                "decision": "fail",
                "case_filters": ["case-a"],
                "failure_classification": {
                    "timeout_cases": [],
                    "content_failure_cases": [],
                    "other_failure_cases": [],
                    "tool_preflight_cases": [
                        {
                            "id": "case-a",
                            "name": "case-a",
                            "category": None,
                            "tier1_failures": [
                                "[codex] Codex runner preflight failed before producing final output."
                            ],
                        }
                    ],
                },
                "raw_output": "",
                "errors": [
                    {
                        "code": "ERR_CODEX_RUNNER_PREFLIGHT",
                        "message": "Codex live eval runner failed before producing final output.",
                    }
                ],
            }

            result = run_skill(
                Path("/tmp/repo"),
                "he-reconcile",
                "release",
                "codex",
                (),
                (),
                90,
                None,
                None,
                True,
                Path("/tmp/codex-home"),
            )

        self.assertEqual(run_case.call_count, 1)
        self.assertTrue(result["bounded_run"])
        self.assertEqual(result["early_stop_reason"], "tool_preflight_failure_limit")
        self.assertEqual(result["executed_case_count"], 1)
        self.assertEqual(result["skipped_case_count"], 1)
        self.assertEqual(result["errors"][0]["code"], "ERR_CODEX_RUNNER_PREFLIGHT")

    def test_split_case_execution_can_disable_tool_preflight_early_stop(self) -> None:
        with (
            mock.patch(
                "run_lifecycle_release_evals._list_skill_builder_cases",
                return_value=(["case-a", "case-b"], None),
            ),
            mock.patch("run_lifecycle_release_evals._run_skill_builder_eval") as run_case,
        ):
            run_case.return_value = {
                "skill": "he-reconcile",
                "returncode": 1,
                "status": "error",
                "decision": "fail",
                "case_filters": ["case-a"],
                "failure_classification": {
                    "timeout_cases": [],
                    "content_failure_cases": [],
                    "other_failure_cases": [],
                    "tool_preflight_cases": [
                        {
                            "id": "case-a",
                            "name": "case-a",
                            "category": None,
                            "tier1_failures": [
                                "[codex] Codex runner preflight failed before producing final output."
                            ],
                        }
                    ],
                },
                "raw_output": "",
                "errors": [
                    {
                        "code": "ERR_CODEX_RUNNER_PREFLIGHT",
                        "message": "Codex live eval runner failed before producing final output.",
                    }
                ],
            }

            result = run_skill(
                Path("/tmp/repo"),
                "he-reconcile",
                "release",
                "codex",
                (),
                (),
                90,
                None,
                None,
                True,
                Path("/tmp/codex-home"),
                None,
                0,
            )

        self.assertEqual(run_case.call_count, 2)
        self.assertFalse(result["bounded_run"])
        self.assertIsNone(result["early_stop_reason"])
        self.assertEqual(result["executed_case_count"], 2)
        self.assertEqual(result["skipped_case_count"], 0)

    def test_codex_auth_preflight_error_is_classified_as_tool_preflight(self) -> None:
        summary = summarize(
            [
                {
                    "skill": "he-spec",
                    "returncode": 1,
                    "status": "error",
                    "raw_output": "",
                    "raw_error": (
                        "ERROR: Selected Codex home is missing authenticated Codex state "
                        "for live Codex runs: /tmp/empty"
                    ),
                    "errors": [{"code": "ERR_VALIDATION", "message": "Evaluation run failed."}],
                }
            ]
        )

        breakdown = summary["failure_breakdown"]
        self.assertEqual(summary["eval_runtime"]["codex_model"], "gpt-5.3-codex-spark")
        self.assertEqual(summary["eval_runtime"]["reasoning_flags"], [])
        self.assertEqual(
            [item["skill"] for item in breakdown["tool_preflight_failures"]],
            ["he-spec"],
        )
        self.assertEqual(breakdown["other_failures"], [])

    def test_codex_no_final_output_case_is_tool_preflight_not_content(self) -> None:
        classification = _classify_case_failures(
            {
                "cases": [
                    {
                        "id": "approved-intent-to-spec",
                        "name": "Approved intent to spec",
                        "category": "happy",
                        "passed": False,
                        "tier1_failed": True,
                        "tier1_failures": ["[codex] codex returned non-zero exit code: 1"],
                        "warnings": [
                            "[codex] No events found in JSONL trace.",
                            "[codex] skipped acceptance assertions because the runner exited "
                            "non-zero and produced no final output",
                        ],
                    }
                ]
            }
        )

        self.assertEqual(
            classification["tool_preflight_cases"][0]["id"],
            "approved-intent-to-spec",
        )
        self.assertEqual(classification["content_failure_cases"], [])


if __name__ == "__main__":
    unittest.main()
