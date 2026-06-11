import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.review_execute import build_review_execution  # noqa: E402
from ask.skills_sdk.review_plan import TRACE_DIR, canonical_receipt_digest  # noqa: E402
from ask.skills_sdk.review_verify import build_review_verification  # noqa: E402


EXECUTE_SCHEMA_PATH = (
    REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-execution-receipt.v1.schema.json"
)


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


def _run_json_command(*args: str, expect_success: bool = True) -> dict:
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if expect_success and process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    if not expect_success and process.returncode == 0:
        raise AssertionError(f"{' '.join(args)} unexpectedly passed\nSTDOUT:\n{process.stdout}")
    return json.loads(process.stdout)


class TestSkillsSdkReviewExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(EXECUTE_SCHEMA_PATH.read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self.plan_path = REPO_ROOT / ".harness/artifacts/sdk-review-plan/test-execute-plan.json"
        self.handoff_path = REPO_ROOT / ".harness/artifacts/sdk-review-handoff/test-execute-handoff.json"
        self.execute_path = REPO_ROOT / ".harness/artifacts/sdk-review-execute/test-execute.json"
        self.artifact_dir = REPO_ROOT / "artifacts/reviews/sdk-review-handoff/Skills-agent-ops-simplify"
        self._cleanup_paths()

    def tearDown(self) -> None:
        self._cleanup_paths()

    def _cleanup_paths(self) -> None:
        if self.plan_path.exists():
            try:
                plan = json.loads(self.plan_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                plan = None
            if isinstance(plan, dict):
                trace_path = REPO_ROOT / TRACE_DIR / f"{canonical_receipt_digest(plan)}.trace.json"
                if trace_path.exists():
                    trace_path.unlink()
        for path in (self.plan_path, self.handoff_path, self.execute_path):
            if path.exists():
                path.unlink()
        if self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir)

    def _write_handoff(self) -> dict:
        _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "plan",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--receipt-out",
            ".harness/artifacts/sdk-review-plan/test-execute-plan.json",
            "--json",
            "--robot",
        )
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "handoff",
            "--plan",
            ".harness/artifacts/sdk-review-plan/test-execute-plan.json",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--receipt-out",
            ".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            "--json",
            "--robot",
        )
        return payload["data"]["review_handoff"]

    def test_execution_receipt_materializes_required_artifacts_and_verifies(self) -> None:
        handoff = self._write_handoff()

        receipt = build_review_execution(
            REPO_ROOT,
            handoff_path=".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
        )

        _validate_schema_subset(self.schema, receipt, {"sdk-review-execution": self.schema})
        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["review_execution_completed"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertFalse(receipt["receipt_written"])
        self.assertEqual(receipt["failed_artifacts"], [])
        self.assertEqual(sorted(result["action"] for result in receipt["artifact_results"]), ["written", "written", "written"])
        for artifact in handoff["required_artifacts"]:
            self.assertTrue((REPO_ROOT / artifact).is_file())
        self.assertIn("independent_reviewer_approval", receipt["not_proven"])
        self.assertIn("ci_passed", receipt["not_proven"])

        verification = build_review_verification(
            REPO_ROOT,
            handoff_path=".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
        )
        self.assertEqual(verification["status"], "pass")
        self.assertTrue(verification["review_artifacts_verified"])

    def test_cli_execute_emits_robot_envelope_and_writes_receipt(self) -> None:
        self._write_handoff()

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "execute",
            "--handoff",
            ".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            "--receipt-out",
            ".harness/artifacts/sdk-review-execute/test-execute.json",
            "--json",
            "--robot",
        )

        receipt = payload["data"]["review_execution"]
        _validate_schema_subset(self.schema, receipt, {"sdk-review-execution": self.schema})
        self.assertEqual(payload["status"], "success")
        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["receipt_written"])
        self.assertEqual(receipt["receipt_path"], ".harness/artifacts/sdk-review-execute/test-execute.json")
        self.assertTrue(self.execute_path.exists())
        persisted_receipt = json.loads(self.execute_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted_receipt, receipt)

    def test_execution_preserves_existing_non_empty_artifacts(self) -> None:
        handoff = self._write_handoff()
        first_artifact = REPO_ROOT / handoff["required_artifacts"][0]
        first_artifact.parent.mkdir(parents=True, exist_ok=True)
        first_artifact.write_text("existing review evidence\n", encoding="utf-8")

        receipt = build_review_execution(
            REPO_ROOT,
            handoff_path=".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
        )

        first_result = next(result for result in receipt["artifact_results"] if result["path"] == handoff["required_artifacts"][0])
        self.assertEqual(first_result["action"], "preserved")
        self.assertEqual(first_artifact.read_text(encoding="utf-8"), "existing review evidence\n")

    def test_cli_execute_reports_directory_collision_as_failed_artifact(self) -> None:
        handoff = self._write_handoff()
        first_artifact = REPO_ROOT / handoff["required_artifacts"][0]
        first_artifact.mkdir(parents=True, exist_ok=True)

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "execute",
            "--handoff",
            ".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            "--json",
            "--robot",
            expect_success=False,
        )

        receipt = payload["data"]["review_execution"]
        first_result = next(result for result in receipt["artifact_results"] if result["path"] == handoff["required_artifacts"][0])
        self.assertEqual(payload["status"], "error")
        self.assertEqual(receipt["status"], "fail")
        self.assertFalse(receipt["review_execution_completed"])
        self.assertEqual(receipt["failed_artifacts"], [handoff["required_artifacts"][0]])
        self.assertEqual(first_result["action"], "blocked")
        self.assertEqual(first_result["reason"], "not_file")
        validation_evidence_path = REPO_ROOT / handoff["required_artifacts"][2]
        validation_evidence = json.loads(validation_evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(validation_evidence["status"], "local_execution_failed")
        self.assertEqual(validation_evidence["commands"][0]["outcome"], "fail")
        self.assertEqual(validation_evidence["commands"][0]["failed_artifacts"], [handoff["required_artifacts"][0]])

    def test_execution_prevalidates_all_required_artifact_paths_before_writing(self) -> None:
        handoff = self._write_handoff()
        valid_artifact = handoff["required_artifacts"][0]
        handoff["required_artifacts"] = [valid_artifact, "../outside-review.md"]
        self.handoff_path.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "required artifact must resolve inside the repository root"):
            build_review_execution(
                REPO_ROOT,
                handoff_path=".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            )

        self.assertFalse((REPO_ROOT / valid_artifact).exists())

    def test_cli_execute_reports_parent_file_collision_as_failed_artifact(self) -> None:
        handoff = self._write_handoff()
        parent_collision = self.artifact_dir / "parent-file"
        parent_collision.parent.mkdir(parents=True, exist_ok=True)
        parent_collision.write_text("not a directory\n", encoding="utf-8")
        handoff["required_artifacts"] = [
            parent_collision.relative_to(REPO_ROOT).as_posix() + "/review-summary.md",
        ]
        self.handoff_path.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "execute",
            "--handoff",
            ".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            "--json",
            "--robot",
            expect_success=False,
        )

        receipt = payload["data"]["review_execution"]
        self.assertEqual(payload["status"], "error")
        self.assertEqual(receipt["status"], "fail")
        self.assertFalse(receipt["review_execution_completed"])
        self.assertEqual(receipt["failed_artifacts"], handoff["required_artifacts"])
        self.assertEqual(receipt["artifact_results"][0]["action"], "blocked")
        self.assertEqual(receipt["artifact_results"][0]["reason"], "parent_not_directory")

    def test_execution_refuses_required_artifact_paths_outside_repo(self) -> None:
        handoff = self._write_handoff()
        handoff["required_artifacts"] = ["../outside-review.md"]
        self.handoff_path.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "required artifact must resolve inside the repository root"):
            build_review_execution(
                REPO_ROOT,
                handoff_path=".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            )

    def test_cli_execute_reports_invalid_utf8_handoff_as_validation_error(self) -> None:
        self.handoff_path.parent.mkdir(parents=True, exist_ok=True)
        self.handoff_path.write_bytes(b"\xff\xfe")

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "execute",
            "--handoff",
            ".harness/artifacts/sdk-review-handoff/test-execute-handoff.json",
            "--json",
            "--robot",
            expect_success=False,
        )

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("review handoff receipt must be valid UTF-8 JSON", payload["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
