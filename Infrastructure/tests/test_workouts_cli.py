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
    "skill-factory/skill-builder-sdk-pipeline",
    "skill-factory/skill-refactor",
}


class TestWorkoutsCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workouts-cli-"))
        self.telemetry_dir = self.temp_dir / "telemetry"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_workouts_finds_fixture(self) -> None:
        result = workouts.list_workouts(REPO_ROOT)

        self.assertEqual(result.status, "success")
        self.assertTrue(DIAGNOSTIC_WORKOUT_IDS.issubset({item["id"] for item in result.data["workouts"]}))

    def test_list_workouts_reports_yaml_syntax_errors(self) -> None:
        workout_dir = self.temp_dir / ".workouts" / "broken"
        workout_dir.mkdir(parents=True)
        (workout_dir / "workout.yaml").write_text("id: [unterminated\n", encoding="utf-8")

        result = workouts.list_workouts(self.temp_dir)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["workouts"][0]["status"], "invalid")
        self.assertIn("Invalid YAML", result.data["workouts"][0]["error"])

    def test_run_score_and_promote_dry_run(self) -> None:
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

    def test_promote_defaults_malformed_context_budget_limit(self) -> None:
        with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)
            scorecard_path = Path(run_result.data["scorecard_path"])
            scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
            scorecard["limits"]["max_skill_context_tokens"] = "not-an-int"
            scorecard_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            promote_result = workouts.promote_workout(REPO_ROOT, WORKOUT_ID, if_better=True, dry_run=True)

        self.assertEqual(run_result.status, "success")
        self.assertEqual(promote_result.status, "success")
        self.assertEqual(
            promote_result.data["promotion"]["context_budget"]["max_skill_context_tokens"],
            workouts.DEFAULT_MAX_SKILL_CONTEXT_TOKENS,
        )

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

    def test_run_workout_records_seed_failure(self) -> None:
        def _mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if any("seed.sh" in part for part in cmd):
                return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="seed failed")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        with (
            mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}),
            mock.patch.object(workouts.subprocess, "run", side_effect=_mock_run),
        ):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)

        self.assertEqual(run_result.status, "error")
        attempt = run_result.data["attempts"][0]
        self.assertEqual(attempt["outcome"], "failure")
        self.assertEqual(attempt["failure_type"], "tool_error")
        self.assertEqual(attempt["seed_exit_code"], 1)
        self.assertEqual(attempt["verify_exit_code"], 0)

    def test_run_workout_records_verify_failure(self) -> None:
        def _mock_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if any("verify.py" in part for part in cmd):
                return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="verify failed")
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        with (
            mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}),
            mock.patch.object(workouts.subprocess, "run", side_effect=_mock_run),
        ):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)

        self.assertEqual(run_result.status, "error")
        attempt = run_result.data["attempts"][0]
        self.assertEqual(attempt["outcome"], "failure")
        self.assertEqual(attempt["failure_type"], "tool_error")
        self.assertEqual(attempt["seed_exit_code"], 0)
        self.assertEqual(attempt["verify_exit_code"], 1)

    def test_run_workout_records_contract_violation(self) -> None:
        hash_iter = iter(["hash_before", "hash_after"])

        def _mock_sha256(path: Path) -> str:
            return next(hash_iter)

        with (
            mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(self.telemetry_dir)}),
            mock.patch.object(
                workouts.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            ),
            mock.patch.object(workouts, "_sha256", side_effect=_mock_sha256),
        ):
            run_result = workouts.run_workout(REPO_ROOT, WORKOUT_ID, attempts=1)

        self.assertEqual(run_result.status, "error")
        attempt = run_result.data["attempts"][0]
        self.assertEqual(attempt["outcome"], "failure")
        self.assertEqual(attempt["failure_type"], "contract_violation")

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
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"scorecard"', result.stdout)

    def test_load_structured_file_allows_quoted_brackets_without_pyyaml(self) -> None:
        """Quoted brackets in YAML scalars must not be rejected when PyYAML is unavailable."""
        yaml_path = self.temp_dir / "test.yaml"
        yaml_path.write_text('script: "echo [ok]"\nother: \'foo {bar}\'\n', encoding="utf-8")

        with mock.patch.dict("sys.modules", {"yaml": None}):
            # Force re-import to pick up the ImportError path
            import importlib
            import ask.commands.workouts as _workouts
            importlib.reload(_workouts)
            loaded = _workouts._load_structured_file(yaml_path)

        self.assertEqual(loaded.get("script"), "echo [ok]")
        self.assertEqual(loaded.get("other"), "foo {bar}")

    def test_load_structured_file_rejects_unquoted_brackets_without_pyyaml(self) -> None:
        """Unquoted flow syntax must still be rejected when PyYAML is unavailable."""
        yaml_path = self.temp_dir / "test.yaml"
        yaml_path.write_text("items: [a, b]\n", encoding="utf-8")

        with mock.patch.dict("sys.modules", {"yaml": None}):
            import importlib
            import ask.commands.workouts as _workouts
            importlib.reload(_workouts)
            with self.assertRaises(ValueError) as ctx:
                _workouts._load_structured_file(yaml_path)

        self.assertIn("flow syntax detected", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
