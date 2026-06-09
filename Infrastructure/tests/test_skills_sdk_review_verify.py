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

from ask.skills_sdk.review_plan import TRACE_DIR, canonical_receipt_digest  # noqa: E402
from ask.skills_sdk.review_verify import build_review_verification  # noqa: E402


VERIFY_SCHEMA_PATH = (
    REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-verification-receipt.v1.schema.json"
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


class TestSkillsSdkReviewVerify(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(VERIFY_SCHEMA_PATH.read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self.plan_path = REPO_ROOT / ".harness/artifacts/sdk-review-plan/test-verify-plan.json"
        self.handoff_path = REPO_ROOT / ".harness/artifacts/sdk-review-handoff/test-verify-handoff.json"
        self.verify_path = REPO_ROOT / ".harness/artifacts/sdk-review-verify/test-verify.json"
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
        for path in (self.plan_path, self.handoff_path, self.verify_path):
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
            ".harness/artifacts/sdk-review-plan/test-verify-plan.json",
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
            ".harness/artifacts/sdk-review-plan/test-verify-plan.json",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--receipt-out",
            ".harness/artifacts/sdk-review-handoff/test-verify-handoff.json",
            "--json",
            "--robot",
        )
        return payload["data"]["review_handoff"]

    def _write_required_artifacts(self, handoff: dict[str, object]) -> None:
        for artifact in handoff["required_artifacts"]:
            path = REPO_ROOT / str(artifact)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"review evidence for {artifact}\n", encoding="utf-8")

    def test_verification_receipt_is_schema_valid_when_required_artifacts_exist(self) -> None:
        handoff = self._write_handoff()
        self._write_required_artifacts(handoff)

        receipt = build_review_verification(
            REPO_ROOT,
            handoff_path=".harness/artifacts/sdk-review-handoff/test-verify-handoff.json",
        )

        _validate_schema_subset(self.schema, receipt, {"sdk-review-verification": self.schema})
        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["review_artifacts_verified"])
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["receipt_written"])
        self.assertEqual(receipt["missing_or_invalid_artifacts"], [])
        self.assertIn("external_service_state", receipt["not_proven"])
        self.assertIn("ci_passed", receipt["not_proven"])
        self.assertTrue(all(result["sha256"] for result in receipt["artifact_results"]))

    def test_verification_reports_missing_required_artifacts_without_claiming_completion(self) -> None:
        self._write_handoff()

        receipt = build_review_verification(
            REPO_ROOT,
            handoff_path=".harness/artifacts/sdk-review-handoff/test-verify-handoff.json",
        )

        _validate_schema_subset(self.schema, receipt, {"sdk-review-verification": self.schema})
        self.assertEqual(receipt["status"], "fail")
        self.assertFalse(receipt["review_artifacts_verified"])
        self.assertEqual(len(receipt["missing_or_invalid_artifacts"]), 3)
        self.assertTrue(all(result["reason"] == "missing" for result in receipt["artifact_results"]))
        self.assertIn("pr_mergeable", receipt["not_proven"])

    def test_cli_verify_emits_robot_envelope_and_writes_only_when_requested(self) -> None:
        handoff = self._write_handoff()
        self._write_required_artifacts(handoff)

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "verify",
            "--handoff",
            ".harness/artifacts/sdk-review-handoff/test-verify-handoff.json",
            "--receipt-out",
            ".harness/artifacts/sdk-review-verify/test-verify.json",
            "--json",
            "--robot",
        )

        receipt = payload["data"]["review_verification"]
        _validate_schema_subset(self.schema, receipt, {"sdk-review-verification": self.schema})
        self.assertEqual(payload["status"], "success")
        self.assertEqual(receipt["status"], "pass")
        self.assertTrue(receipt["receipt_written"])
        self.assertEqual(receipt["receipt_path"], ".harness/artifacts/sdk-review-verify/test-verify.json")
        self.assertTrue(self.verify_path.exists())
        persisted_receipt = json.loads(self.verify_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted_receipt, receipt)

    def test_cli_verify_missing_artifacts_is_structured_error_with_receipt_data(self) -> None:
        self._write_handoff()

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "verify",
            "--handoff",
            ".harness/artifacts/sdk-review-handoff/test-verify-handoff.json",
            "--json",
            "--robot",
            expect_success=False,
        )

        receipt = payload["data"]["review_verification"]
        self.assertEqual(payload["status"], "error")
        self.assertEqual(receipt["status"], "fail")
        self.assertFalse(receipt["review_artifacts_verified"])
        self.assertIn("missing_or_invalid_artifacts", payload["errors"][0]["fix_suggestion"])

    def test_verify_refuses_required_artifact_paths_outside_repo(self) -> None:
        handoff = self._write_handoff()
        handoff["required_artifacts"] = ["../outside-review.md"]
        self.handoff_path.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "required artifact must resolve inside the repository root"):
            build_review_verification(
                REPO_ROOT,
                handoff_path=".harness/artifacts/sdk-review-handoff/test-verify-handoff.json",
            )


if __name__ == "__main__":
    unittest.main()
