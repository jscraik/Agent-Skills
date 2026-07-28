from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands.skills_impl import skills_sdk_eval_run  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_eval_run_receipt  # noqa: E402
from eval_runner_helpers import internal_result_with_scorecard, successful_internal_result  # noqa: E402


PROFILE_IDENTITY = {
    "model": "qwen3.5:9b-mlx",
    "model_family": "qwen3.5",
    "provider": "ollama",
    "identity_source": "codex-profile-config",
}


class TestSkillsSdkEvalRunnerReceipts(unittest.TestCase):
    def _run_internal(self, result):
        with (
            mock.patch("ask.commands.evals.run_evals", return_value=result),
            mock.patch("ask.commands.skills_impl._skills_sdk_eval_execution_identity", return_value=None),
            mock.patch("ask.commands.skills_impl._skills_sdk_eval_profile_execution_identity", return_value=PROFILE_IDENTITY),
        ):
            return skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
                codex_profile="oss-local",
            )

    def test_internal_oss_eval_uses_profile_identity_when_skill_has_no_lane_policy(self) -> None:
        result = self._run_internal(successful_internal_result("oss-local"))

        receipt = validate_eval_run_receipt(result.data["skills_sdk_eval_run"]["receipt"])
        self.assertEqual(result.status, "success")
        self.assertEqual(receipt.execution_model, "qwen3.5:9b-mlx")
        self.assertEqual(receipt.execution_model_provider, "ollama")

    def test_internal_runner_persists_its_receipt_beside_repo_owned_scorecard(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "Infrastructure" / "artifacts") as temp_dir:
            scorecard_path = Path(temp_dir) / "scorecard.json"
            result = self._run_internal(internal_result_with_scorecard(scorecard_path))

            payload = result.data["skills_sdk_eval_run"]
            receipt_path = payload["receipt_path"]
            self.assertIsInstance(receipt_path, str)
            persisted_path = REPO_ROOT / receipt_path
            self.assertTrue(persisted_path.is_file())
            self.assertEqual(json.loads(persisted_path.read_text(encoding="utf-8")), payload["receipt"])

    def test_internal_runner_does_not_persist_receipt_for_external_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scorecard_path = Path(temp_dir) / "scorecard.json"
            result = self._run_internal(internal_result_with_scorecard(scorecard_path))

            self.assertIsNone(result.data["skills_sdk_eval_run"]["receipt_path"])
            self.assertFalse((scorecard_path.parent / "sdk-eval-run-receipt.json").exists())
