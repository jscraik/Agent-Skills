from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.tessl_acceptance_policy import TESSL_ACCEPTANCE_SCORE, TESSL_TARGET_SCORE  # noqa: E402
from ask.skills_sdk.tessl_score_receipt import build_tessl_score_receipt  # noqa: E402


RUN_ID = "019eebb6-78af-7357-a3e6-bd77c147d821"


def _view_payload(
    *,
    status: str = "completed",
    missing_baseline: bool = False,
    usage_score: float = 1.0,
    baseline_score: float = 0.5,
    usage_max: float = 1.0,
    baseline_max: float = 1.0,
) -> dict[str, object]:
    scenarios: list[dict[str, object]] = []
    for index in range(2):
        baseline_results: list[dict[str, float]] | None = [{"score": baseline_score, "max_score": baseline_max}]
        if missing_baseline and index == 1:
            baseline_results = None
        scenarios.append(
            {
                "id": f"scenario-{index}",
                "path": f"scenario-{index}",
                "solutions": [
                    {"variant": "usage-spec", "assessmentResults": [{"score": usage_score, "max_score": usage_max}]},
                    {"variant": "baseline", "assessmentResults": baseline_results},
                ],
            }
        )
    attrs: dict[str, object] = {"status": status, "scenarios": scenarios}
    if status == "failed":
        attrs["failureReason"] = {"code": "EVAL_PARTIAL_FAILURE", "message": "1 of 4 scenario evaluations failed"}
    return {"data": {"id": RUN_ID, "attributes": attrs}}


def _malformed_numeric_view_payload() -> dict[str, object]:
    payload = _view_payload()
    scenarios = payload["data"]["attributes"]["scenarios"]  # type: ignore[index]
    scenarios[0]["solutions"][0]["assessmentResults"][0]["score"] = "not-a-number"  # type: ignore[index]
    return payload


def _zero_max_view_payload() -> dict[str, object]:
    return {
        "data": {
            "id": RUN_ID,
            "attributes": {
                "status": "completed",
                "scenarios": [
                    {
                        "id": "scenario-zero",
                        "path": "scenario-zero",
                        "solutions": [
                            {"variant": "usage-spec", "assessmentResults": [{"score": 0.0, "max_score": 0.0}]},
                            {"variant": "baseline", "assessmentResults": [{"score": 0.0, "max_score": 0.0}]},
                        ],
                    }
                ],
            },
        }
    }


def _missing_score_view_payload() -> dict[str, object]:
    return {
        "data": {
            "id": RUN_ID,
            "attributes": {
                "status": "completed",
                "scenarios": [
                    {
                        "id": "scenario-incomplete",
                        "path": "scenario-incomplete",
                        "solutions": [
                            {"variant": "usage-spec", "assessmentResults": [{"score": 1.0, "max_score": 1.0}]},
                            {"variant": "baseline", "assessmentResults": [{"max_score": 1.0}]},
                        ],
                    }
                ],
            },
        }
    }


def _score_exceeds_max_view_payload() -> dict[str, object]:
    return {
        "data": {
            "id": RUN_ID,
            "attributes": {
                "status": "completed",
                "scenarios": [
                    {
                        "id": "scenario-corrupt-score",
                        "path": "scenario-corrupt-score",
                        "solutions": [
                            {"variant": "usage-spec", "assessmentResults": [{"score": 10.0, "max_score": 1.0}]},
                            {"variant": "baseline", "assessmentResults": [{"score": 0.5, "max_score": 1.0}]},
                        ],
                    }
                ],
            },
        }
    }


def _non_finite_score_view_payload() -> dict[str, object]:
    payload = _view_payload()
    scenarios = payload["data"]["attributes"]["scenarios"]  # type: ignore[index]
    scenarios[0]["solutions"][0]["assessmentResults"][0]["score"] = "nan"  # type: ignore[index]
    return payload


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkTesslScoreReceipt(unittest.TestCase):
    def test_selected_tessl_acceptance_policy_is_explicit(self) -> None:
        self.assertEqual(TESSL_ACCEPTANCE_SCORE, 85)
        self.assertEqual(TESSL_TARGET_SCORE, 90)

    def test_acceptance_floor_closes_live_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(
                json.dumps(_view_payload(usage_score=TESSL_ACCEPTANCE_SCORE / 100, baseline_score=0.5)),
                encoding="utf-8",
            )

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["ready"])
        self.assertEqual(receipt["score_summary"]["usage_percent"], float(TESSL_ACCEPTANCE_SCORE))

    def test_complete_view_json_builds_pass_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        summary = receipt["score_summary"]
        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["ready"])
        self.assertFalse(receipt["memory_derived"])
        self.assertEqual(receipt["feedback_loop"]["status"], "closed")
        self.assertEqual(summary["usage_percent"], 100.0)
        self.assertEqual(summary["baseline_percent"], 50.0)
        self.assertEqual(summary["missing_scenario_count"], 0)
        self.assertEqual(summary["regressions"], [])
        self.assertEqual(summary["ties"], [])
        self.assertEqual(summary["wins"], ["scenario-0", "scenario-1"])

    def test_baseline_win_blocks_handoff_feedback_loop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload(usage_score=0.25, baseline_score=1.0)), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        summary = receipt["score_summary"]
        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["blocker_class"], "blocked_validation")
        self.assertIn("feedback loop is open", receipt["blocker"])
        self.assertEqual(summary["usage_percent"], 25.0)
        self.assertEqual(summary["baseline_percent"], 100.0)
        self.assertEqual(summary["ties"], [])
        self.assertEqual(summary["wins"], [])
        self.assertEqual(receipt["feedback_loop"]["status"], "open")
        self.assertEqual(receipt["feedback_loop"]["regression_count"], 2)
        self.assertIn("scenario-0", receipt["feedback_loop"]["regression_paths"])
        lesson_sources = {lesson["source"] for lesson in receipt["feedback_loop"]["lessons_learned"]}
        self.assertIn("tessl_baseline_win", lesson_sources)
        self.assertTrue(
            all(lesson["internal_regression_required"] for lesson in receipt["feedback_loop"]["lessons_learned"] if lesson["source"] == "tessl_baseline_win")
        )
        self.assertTrue(
            any("internal regression cases" in action for action in receipt["feedback_loop"]["required_next_actions"])
        )

    def test_low_usage_blocks_live_handoff_even_with_lift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload(usage_score=0.75, baseline_score=0.25)), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertIn("below the live handoff threshold", receipt["blocker"])
        self.assertEqual(receipt["feedback_loop"]["status"], "open")
        lesson_sources = {lesson["source"] for lesson in receipt["feedback_loop"]["lessons_learned"]}
        self.assertIn("tessl_low_usage_score", lesson_sources)
        self.assertTrue(
            any("handoff threshold" in action for action in receipt["feedback_loop"]["required_next_actions"])
        )

    def test_partial_failed_view_json_is_blocked_with_partial_scores(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload(status="failed", missing_baseline=True)), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        summary = receipt["score_summary"]
        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["blocker_class"], "blocked_validation")
        self.assertEqual(receipt["feedback_loop"]["status"], "open")
        self.assertEqual(summary["scored_scenario_count"], 1)
        self.assertEqual(summary["missing_scenario_count"], 1)
        self.assertEqual(summary["usage_percent"], 100.0)
        self.assertEqual(summary["baseline_percent"], 50.0)
        self.assertEqual(summary["wins"], ["scenario-0"])

    def test_pending_view_json_is_blocked_even_with_scores(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload(status="running")), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertIn("not complete yet", receipt["blocker"])
        self.assertEqual(receipt["feedback_loop"]["status"], "open")

    def test_zero_max_points_view_json_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_zero_max_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["blocker_class"], "blocked_validation")
        self.assertIn("positive max points", receipt["blocker"])

    def test_malformed_numeric_scores_are_blocked_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_malformed_numeric_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["score_summary"]["missing_scenario_count"], 1)

    def test_missing_assessment_score_is_blocked_as_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_missing_score_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["score_summary"]["missing_scenario_count"], 1)
        self.assertIn("complete scored baseline", receipt["blocker"])

    def test_score_above_max_is_blocked_as_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_score_exceeds_max_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["score_summary"]["missing_scenario_count"], 1)
        self.assertIn("valid positive max points", receipt["blocker"])
        self.assertFalse(any("None%" in action for action in receipt["feedback_loop"]["required_next_actions"]))

    def test_non_finite_score_is_blocked_as_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_non_finite_score_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["score_summary"]["missing_scenario_count"], 1)
        self.assertIn("valid positive max points", receipt["blocker"])

    def test_mismatched_expected_run_id_blocks_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id="expected-run")

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["blocker_class"], "blocked_validation")
        self.assertEqual(receipt["expected_run_id"], "expected-run")
        self.assertIn(RUN_ID, receipt["blocker"])

    def test_scenario_max_uses_larger_variant_denominator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(
                json.dumps(_view_payload(usage_score=2.0, baseline_score=1.0, usage_max=2.0, baseline_max=4.0)),
                encoding="utf-8",
            )

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        summary = receipt["score_summary"]
        self.assertEqual(summary["max_points"], 8.0)
        self.assertEqual(summary["usage_percent"], 50.0)
        self.assertEqual(summary["baseline_percent"], 25.0)
        self.assertEqual(summary["wins"], ["scenario-0", "scenario-1"])

    def test_failed_view_next_action_does_not_wait_for_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload(status="failed")), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        actions = receipt["feedback_loop"]["required_next_actions"]
        self.assertTrue(any("Inspect failureReason" in action for action in actions))
        self.assertFalse(any("Wait for Tessl completion" in action for action in actions))

    def test_tessl_score_command_requires_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload()), encoding="utf-8")

            process = _run_ask("sdk", "eval", "tessl-score", "--view-json", str(path), "--skill", "Skills/github/teach", "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("require --preview", envelope["errors"][0]["message"])

    def test_tessl_score_command_reads_explicit_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload()), encoding="utf-8")

            process = _run_ask(
                "sdk",
                "eval",
                "tessl-score",
                "--view-json",
                str(path),
                "--skill",
                "Skills/github/teach",
                "--run-id",
                RUN_ID,
                "--preview",
                "--json",
                "--robot",
            )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_tessl_score"]
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["receipt"]["feedback_loop"]["status"], "closed")
        self.assertEqual(payload["receipt"]["score_summary"]["baseline_percent"], 50.0)

    def test_tessl_score_command_returns_error_for_blocked_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_zero_max_view_payload()), encoding="utf-8")

            process = _run_ask(
                "sdk",
                "eval",
                "tessl-score",
                "--view-json",
                str(path),
                "--skill",
                "Skills/github/teach",
                "--preview",
                "--json",
                "--robot",
            )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_tessl_score"]
        self.assertEqual(envelope["status"], "error")
        self.assertEqual(payload["status"], "blocked")

    def test_tessl_score_command_returns_error_for_missing_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing-view.json"

            process = _run_ask(
                "sdk",
                "eval",
                "tessl-score",
                "--view-json",
                str(missing),
                "--skill",
                "Skills/github/teach",
                "--preview",
                "--json",
                "--robot",
            )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_tessl_score"]
        self.assertEqual(envelope["status"], "error")
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("agent_summary", payload["receipt"])


if __name__ == "__main__":
    unittest.main()
