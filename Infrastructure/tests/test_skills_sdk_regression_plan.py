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

from ask.skills_sdk.regression_plan import build_regression_plan_receipt  # noqa: E402


RUN_ID = "019eef9f-1398-7022-8090-96cfc46150c8"
FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
FIXTURE_EVALS = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill/references/evals.yaml"


def _view_payload() -> dict[str, object]:
    return {
        "data": {
            "id": RUN_ID,
            "attributes": {
                "status": "completed",
                "scenarios": [
                    {
                        "id": "happy-scenario-quality",
                        "path": "happy-scenario-quality",
                        "solutions": [
                            {"variant": "usage-spec", "assessmentResults": [{"score": 0.25, "max_score": 1.0}]},
                            {"variant": "baseline", "assessmentResults": [{"score": 1.0, "max_score": 1.0}]},
                        ],
                    }
                ],
            },
        }
    }


def _plan_payload() -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.eval-regression-plan-input.v1",
        "source_run_id": RUN_ID,
        "regressions": [
            {
                "scenario_id": "happy-scenario-quality",
                "owner": "criteria",
                "failure_mode": "The rubric rewards generic success rather than the concrete scenario-quality artifact contract.",
                "patch_plan": [
                    {
                        "file": FIXTURE_EVALS,
                        "change": "Retain the scenario and tighten acceptance around evidence-bearing rubric fields.",
                    }
                ],
                "retained_regression": {
                    "status": "retained",
                    "path": FIXTURE_EVALS,
                },
                "validation_commands": [
                    "./bin/ask sdk eval scenario-quality Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill --preview --json --robot"
                ],
            }
        ],
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


class TestSkillsSdkRegressionPlan(unittest.TestCase):
    def test_missing_plan_blocks_with_owner_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            view_path = Path(temp_dir) / "view.json"
            view_path.write_text(json.dumps(_view_payload()), encoding="utf-8")

            receipt = build_regression_plan_receipt(
                REPO_ROOT,
                view_json=view_path,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                run_id=RUN_ID,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_rerun"])
        self.assertEqual(receipt["regression_count"], 1)
        self.assertEqual(receipt["regressions"][0]["scenario_id"], "happy-scenario-quality")
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("regression_plan_artifact_present", blocker_ids)
        self.assertIn("owner_classified", blocker_ids)
        self.assertIn("retained_regression_present", blocker_ids)

    def test_complete_plan_is_ready_for_internal_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            view_path = Path(temp_dir) / "view.json"
            plan_path = Path(temp_dir) / "plan.json"
            view_path.write_text(json.dumps(_view_payload()), encoding="utf-8")
            plan_path.write_text(json.dumps(_plan_payload()), encoding="utf-8")

            receipt = build_regression_plan_receipt(
                REPO_ROOT,
                view_json=view_path,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                run_id=RUN_ID,
                plan_path=plan_path,
            )

        self.assertEqual(receipt["status"], "preview")
        self.assertTrue(receipt["ready_for_live_rerun"])
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(receipt["regressions"][0]["owner"], "criteria")
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["promotion_performed"])

    def test_retained_regression_must_be_repo_local(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            view_path = Path(temp_dir) / "view.json"
            plan_path = Path(temp_dir) / "plan.json"
            outside_path = Path(temp_dir) / "external-regression.md"
            view_path.write_text(json.dumps(_view_payload()), encoding="utf-8")
            outside_path.write_text("external regression evidence\n", encoding="utf-8")
            plan = _plan_payload()
            plan["regressions"][0]["retained_regression"]["path"] = str(outside_path)
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            receipt = build_regression_plan_receipt(
                REPO_ROOT,
                view_json=view_path,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                run_id=RUN_ID,
                plan_path=plan_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_rerun"])
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("retained_regression_present", blocker_ids)

    def test_retained_regression_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            view_path = Path(temp_dir) / "view.json"
            plan_path = Path(temp_dir) / "plan.json"
            view_path.write_text(json.dumps(_view_payload()), encoding="utf-8")
            plan = _plan_payload()
            traversal_path = (
                "../agent-skills/Infrastructure/tests/fixtures/skills_sdk/"
                "scenario_quality_skill/references/evals.yaml"
            )
            plan["regressions"][0]["retained_regression"]["path"] = traversal_path
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            receipt = build_regression_plan_receipt(
                REPO_ROOT,
                view_json=view_path,
                source_path=REPO_ROOT / FIXTURE_SKILL,
                query=FIXTURE_SKILL,
                run_id=RUN_ID,
                plan_path=plan_path,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["ready_for_live_rerun"])
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("retained_regression_present", blocker_ids)

    def test_regression_plan_command_requires_preview(self) -> None:
        process = _run_ask(
            "sdk",
            "eval",
            "regression-plan",
            "--view-json",
            "missing.json",
            "--skill",
            FIXTURE_SKILL,
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("require --preview", envelope["errors"][0]["message"])

    def test_regression_plan_command_builds_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            view_path = Path(temp_dir) / "view.json"
            plan_path = Path(temp_dir) / "plan.json"
            view_path.write_text(json.dumps(_view_payload()), encoding="utf-8")
            plan_path.write_text(json.dumps(_plan_payload()), encoding="utf-8")

            process = _run_ask(
                "sdk",
                "eval",
                "regression-plan",
                "--view-json",
                str(view_path),
                "--skill",
                FIXTURE_SKILL,
                "--plan-json",
                str(plan_path),
                "--preview",
                "--json",
                "--robot",
            )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_regression_plan"]
        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready_for_live_rerun"])
        self.assertEqual(payload["receipt"]["regression_count"], 1)


if __name__ == "__main__":
    unittest.main()
