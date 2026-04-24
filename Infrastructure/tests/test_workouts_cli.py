import os
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


class TestWorkoutsCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workouts-cli-"))
        self.telemetry_dir = self.temp_dir / "telemetry"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_workouts_finds_fixture(self) -> None:
        result = workouts.list_workouts(REPO_ROOT)

        self.assertEqual(result.status, "success")
        self.assertIn(WORKOUT_ID, {item["id"] for item in result.data["workouts"]})

    def test_run_score_and_promote_dry_run(self) -> None:
        with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=2)
            score_result = workouts.score_workout(REPO_ROOT, WORKOUT_ID)
            promote_result = workouts.promote_workout(REPO_ROOT, WORKOUT_ID, if_better=True, dry_run=True)

        self.assertEqual(run_result.status, "success")
        self.assertEqual(run_result.data["scorecard"]["metrics"]["attempts"], 2)
        self.assertEqual(run_result.data["scorecard"]["metrics"]["pass_rate"], 1.0)
        self.assertTrue((self.telemetry_dir / "runs.jsonl").is_file())
        self.assertEqual(score_result.status, "success")
        self.assertEqual(promote_result.status, "success")
        self.assertEqual(promote_result.data["rollback_validation"]["status"], "pass")
        self.assertTrue(promote_result.data["promotion"]["dry_run"])

    def test_run_workout_records_subprocess_timeout(self) -> None:
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
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"scorecard"', result.stdout)


if __name__ == "__main__":
    unittest.main()
