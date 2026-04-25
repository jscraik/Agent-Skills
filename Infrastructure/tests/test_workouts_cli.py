import os
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands import workouts  # noqa: E402


WORKOUT_ID = "agent-ops/verification-before-completion"
DIAGNOSTIC_WORKOUT_IDS = {
    WORKOUT_ID,
    "harness-engineering/he-spec",
    "skill-factory/skill-refactor",
}


class TestWorkoutsCLI(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create a temporary directory for the test and set the telemetry directory path.
        
        Creates a filesystem temporary directory with prefix "workouts-cli-" and assigns its Path to self.temp_dir. Sets self.telemetry_dir to the Path of the "telemetry" subdirectory inside that temporary directory.
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workouts-cli-"))
        self.telemetry_dir = self.temp_dir / "telemetry"

    def tearDown(self) -> None:
        """
        Remove the temporary test directory and its contents.
        
        Deletes the directory at self.temp_dir recursively; any filesystem errors during removal are ignored.
        """
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_workouts_finds_fixture(self) -> None:
        result = workouts.list_workouts(REPO_ROOT)

        self.assertEqual(result.status, "success")
        self.assertTrue(DIAGNOSTIC_WORKOUT_IDS.issubset({item["id"] for item in result.data["workouts"]}))

    def test_run_score_and_promote_dry_run(self) -> None:
        """
        Verifies that running a workout, scoring it, and performing a dry-run promotion produce the expected metrics, telemetry artifacts, and promotion payload.
        
        Asserts that:
        - The run completes successfully and the scorecard metrics report attempts == 2, pass_rate == 1.0, tool_steps == 4, and retries == 1.
        - A telemetry runs file (`runs.jsonl`) is written to the telemetry directory.
        - Scoring succeeds.
        - Promotion (dry run) succeeds, its rollback validation status is "pass", and `promotion.dry_run` is true.
        - The promotion payload uses schema version "skill-workout-amendment.v1" and includes `previous_hash`, `new_hash`, `score_before`, and `score_after`.
        - No amendments directory is created for a dry-run promotion.
        """
        with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=2)
            score_result = workouts.score_workout(REPO_ROOT, WORKOUT_ID)
            promote_result = workouts.promote_workout(REPO_ROOT, WORKOUT_ID, if_better=True, dry_run=True)

        self.assertEqual(run_result.status, "success")
        self.assertEqual(run_result.data["scorecard"]["metrics"]["attempts"], 2)
        self.assertEqual(run_result.data["scorecard"]["metrics"]["pass_rate"], 1.0)
        self.assertEqual(run_result.data["scorecard"]["metrics"]["tool_steps"], 4)
        self.assertEqual(run_result.data["scorecard"]["metrics"]["retries"], 1)
        self.assertTrue((self.telemetry_dir / "runs.jsonl").is_file())
        self.assertEqual(score_result.status, "success")
        self.assertEqual(promote_result.status, "success")
        self.assertEqual(promote_result.data["rollback_validation"]["status"], "pass")
        self.assertTrue(promote_result.data["promotion"]["dry_run"])
        self.assertEqual(promote_result.data["promotion"]["schema_version"], "skill-workout-amendment.v1")
        self.assertIn("previous_hash", promote_result.data["promotion"])
        self.assertIn("new_hash", promote_result.data["promotion"])
        self.assertIn("score_before", promote_result.data["promotion"])
        self.assertIn("score_after", promote_result.data["promotion"])
        self.assertFalse((self.telemetry_dir / "amendments").exists())

    def test_promote_writes_accepted_amendment_record(self) -> None:
        with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)
            promote_result = workouts.promote_workout(REPO_ROOT, WORKOUT_ID, if_better=True, dry_run=False)

        self.assertEqual(run_result.status, "success")
        self.assertEqual(promote_result.status, "success")
        promotion = promote_result.data["promotion"]
        self.assertEqual(promotion["state"], "accepted")
        self.assertEqual(promotion["previous_hash"], promotion["new_hash"])
        self.assertTrue(promotion["rollback_command"])
        self.assertEqual(promotion["context_budget"]["status"], "pass")
        accepted_records = list((self.telemetry_dir / "amendments" / "accepted").glob("*.json"))
        self.assertEqual(len(accepted_records), 1)
        accepted_payload = json.loads(accepted_records[0].read_text(encoding="utf-8"))
        self.assertEqual(accepted_payload["schema_version"], "skill-workout-amendment.v1")
        self.assertEqual(accepted_payload["state"], "accepted")

    def test_promote_rejects_and_records_context_budget_regression(self) -> None:
        """
        Verifies that promoting a workout that exceeds the skill context budget is rejected and recorded.
        
        Runs a workout, modifies its scorecard to simulate a context-budget regression and mark it promotion-ineligible, then attempts promotion (non-dry-run). Asserts the promotion operation errors, includes "context_budget_exceeded" in rejection reasons, sets promotion state to "rejected" with context budget status "fail", and writes exactly one rejected amendment record whose payload state is "rejected".
        """
        with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)
            scorecard_path = Path(run_result.data["scorecard_path"])
            scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
            scorecard["metrics"]["estimated_skill_context_tokens"] = 9999
            scorecard["limits"]["max_skill_context_tokens"] = 1
            scorecard["promotion_eligible"] = False
            scorecard_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            promote_result = workouts.promote_workout(REPO_ROOT, WORKOUT_ID, if_better=True, dry_run=False)

        self.assertEqual(run_result.status, "success")
        self.assertEqual(promote_result.status, "error")
        self.assertIn("context_budget_exceeded", promote_result.data["promotion"]["rejection_reasons"])
        self.assertEqual(promote_result.data["promotion"]["state"], "rejected")
        self.assertEqual(promote_result.data["promotion"]["context_budget"]["status"], "fail")
        rejected_records = list((self.telemetry_dir / "amendments" / "rejected").glob("*.json"))
        self.assertEqual(len(rejected_records), 1)
        rejected_payload = json.loads(rejected_records[0].read_text(encoding="utf-8"))
        self.assertEqual(rejected_payload["state"], "rejected")

    def test_score_workout_reports_corrupted_scorecard(self) -> None:
        with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)
            scorecard_path = Path(run_result.data["scorecard_path"])
            scorecard_path.write_text("{not json\n", encoding="utf-8")
            score_result = workouts.score_workout(REPO_ROOT, WORKOUT_ID)

        self.assertEqual(run_result.status, "success")
        self.assertEqual(score_result.status, "error")
        self.assertEqual(score_result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("corrupted or malformed", score_result.errors[0].message)
        self.assertEqual(score_result.data["scorecard_path"], str(scorecard_path))
        self.assertIn("parse_error", score_result.data)

    def test_all_diagnostic_workouts_run_and_score(self) -> None:
        for workout_id in sorted(DIAGNOSTIC_WORKOUT_IDS):
            telemetry_dir = self.temp_dir / workout_id.replace("/", "__")
            with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(telemetry_dir)}):
                run_result = workouts.run_workout(REPO_ROOT, workout_id, attempts=1)
                score_result = workouts.score_workout(REPO_ROOT, workout_id)

            self.assertEqual(run_result.status, "success", workout_id)
            self.assertEqual(run_result.data["scorecard"]["metrics"]["pass_rate"], 1.0)
            self.assertGreater(run_result.data["scorecard"]["metrics"]["tool_steps"], 0)
            self.assertEqual(score_result.status, "success", workout_id)

    def test_run_workout_records_subprocess_timeout(self) -> None:
        """
        Verifies that run_workout records a subprocess timeout as a failure and surfaces the expected error and scorecard fields.
        
        Mocks subprocess.run to raise subprocess.TimeoutExpired and sets SKILL_TELEMETRY_DIR; asserts the returned result has status "error", the first error code is "ERR_VALIDATION", the scorecard pass_rate is 0.0, the first attempt outcome is "failure" with failure_type "timeout", and both seed and verify exit codes are 124.
        """
        timeout = subprocess.TimeoutExpired(cmd=["bash", "seed.sh"], timeout=60, output="", stderr="")
        with (
            mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}),
            mock.patch.object(workouts.subprocess, "run", side_effect=timeout),
        ):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)

        self.assertEqual(run_result.status, "error")
        self.assertEqual(run_result.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(run_result.data["scorecard"]["metrics"]["pass_rate"], 0.0)
        attempt = run_result.data["attempts"][0]
        self.assertEqual(attempt["outcome"], "failure")
        self.assertEqual(attempt["failure_type"], "timeout")
        self.assertEqual(attempt["seed_exit_code"], 124)
        self.assertEqual(attempt["verify_exit_code"], 124)

    def test_ask_workouts_run_json_contract(self) -> None:
        """
        Verifies that running the CLI command `ask workouts run <WORKOUT_ID> --json` exits successfully and emits JSON output containing a `scorecard` entry.
        
        This test sets the telemetry directory environment, invokes the CLI, asserts the process exit code is 0, and asserts the captured stdout includes the string `"scorecard"`.
        """
        env = os.environ.copy()
        env["SKILL_TELEMETRY_DIR"] = str(self.telemetry_dir)
        result = subprocess.run(
            [
                "python3",
                "Infrastructure/bin/ask",
                "workouts",
                "run",
                WORKOUT_ID,
                "--attempts",
                "1",
                "--json",
            ],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"scorecard"', result.stdout)


if __name__ == "__main__":
    unittest.main()
