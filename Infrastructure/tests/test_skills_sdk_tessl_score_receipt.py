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

from ask.skills_sdk.tessl_score_receipt import build_tessl_score_receipt  # noqa: E402


RUN_ID = "019eebb6-78af-7357-a3e6-bd77c147d821"


def _view_payload(*, status: str = "completed", missing_baseline: bool = False) -> dict[str, object]:
    scenarios: list[dict[str, object]] = []
    for index in range(2):
        baseline_results: list[dict[str, float]] | None = [{"score": 0.5, "max_score": 1.0}]
        if missing_baseline and index == 1:
            baseline_results = None
        scenarios.append(
            {
                "id": f"scenario-{index}",
                "path": f"scenario-{index}",
                "solutions": [
                    {"variant": "usage-spec", "assessmentResults": [{"score": 1.0, "max_score": 1.0}]},
                    {"variant": "baseline", "assessmentResults": baseline_results},
                ],
            }
        )
    attrs: dict[str, object] = {"status": status, "scenarios": scenarios}
    if status == "failed":
        attrs["failureReason"] = {"code": "EVAL_PARTIAL_FAILURE", "message": "1 of 4 scenario evaluations failed"}
    return {"data": {"id": RUN_ID, "attributes": attrs}}


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
    def test_complete_view_json_builds_pass_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        summary = receipt["score_summary"]
        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["ready"])
        self.assertFalse(receipt["memory_derived"])
        self.assertEqual(summary["usage_percent"], 100.0)
        self.assertEqual(summary["baseline_percent"], 50.0)
        self.assertEqual(summary["missing_scenario_count"], 0)

    def test_partial_failed_view_json_is_blocked_with_partial_scores(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_view_payload(status="failed", missing_baseline=True)), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        summary = receipt["score_summary"]
        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["blocker_class"], "blocked_validation")
        self.assertEqual(summary["scored_scenario_count"], 1)
        self.assertEqual(summary["missing_scenario_count"], 1)
        self.assertEqual(summary["usage_percent"], 100.0)
        self.assertEqual(summary["baseline_percent"], 50.0)

    def test_zero_max_points_view_json_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "view.json"
            path.write_text(json.dumps(_zero_max_view_payload()), encoding="utf-8")

            receipt = build_tessl_score_receipt(REPO_ROOT, view_json=path, skill="Skills/github/teach", run_id=RUN_ID)

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready"])
        self.assertEqual(receipt["blocker_class"], "blocked_validation")
        self.assertIn("positive max points", receipt["blocker"])

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
        self.assertEqual(payload["receipt"]["score_summary"]["baseline_percent"], 50.0)


if __name__ == "__main__":
    unittest.main()
