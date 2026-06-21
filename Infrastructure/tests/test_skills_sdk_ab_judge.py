from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_judge import build_ab_judge_preview_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_rubric import AB_RUBRIC_ID, canonical_ab_rubric_digest  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_judge_preview_receipt  # noqa: E402


RUN_RECEIPT = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.json"


class TestSkillsSdkAbJudgePreview(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_root = REPO_ROOT / ".harness/test-sdk-ab-judge"
        shutil.rmtree(self.evidence_root, ignore_errors=True)
        self.evidence_root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.evidence_root, ignore_errors=True)

    def test_builder_creates_sanitized_judge_input_without_provider_invocation(self) -> None:
        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT)

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["operation"], "ab_judge_preview")
        self.assertEqual(receipt["judge_profile"]["id"], "oss-local")
        self.assertEqual(receipt["judge_profile"]["model"], "qwen3.5:latest")
        self.assertEqual(receipt["rubric_id"], AB_RUBRIC_ID)
        self.assertEqual(receipt["rubric_digest"], canonical_ab_rubric_digest())
        self.assertEqual(receipt["allowed_winners"], ["skill_a", "skill_b", "inconclusive"])
        self.assertTrue(receipt["calibration_required"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])

        comparison = receipt["comparison_payload"]
        self.assertEqual(comparison["schema_version"], "skills-sdk.ab-judge-decision.v0")
        self.assertEqual(comparison["rubric"]["rubric_id"], AB_RUBRIC_ID)
        self.assertEqual(comparison["rubric_digest"], canonical_ab_rubric_digest())
        self.assertTrue(comparison["rubric"]["judge_output_contract"]["unvalidated_judges_are_advisory"])
        self.assertEqual({row["variant_label"] for row in comparison["variant_results"]}, {"A", "B"})
        self.assertNotIn("output_last_message_path", comparison["variant_results"][0])
        self.assertNotIn("command_argv", comparison["variant_results"][0])
        validate_ab_judge_preview_receipt(receipt)

    def test_builder_blocks_non_completed_run_receipt(self) -> None:
        receipt = build_ab_judge_preview_receipt(
            REPO_ROOT,
            run_receipt="Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.json",
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
        validate_ab_judge_preview_receipt(receipt)

    def test_builder_accepts_ab_run_robot_envelope(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
        envelope_path = self.evidence_root / "ab-run-envelope.json"
        envelope_path.write_text(
            json.dumps({"status": "success", "data": {"skills_sdk_eval_ab_run": {"receipt": run_receipt}}}),
            encoding="utf-8",
        )

        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=envelope_path.relative_to(REPO_ROOT).as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["comparison_payload"]["experiment_id"], run_receipt["experiment_id"])
        validate_ab_judge_preview_receipt(receipt)

    def test_cli_requires_preview_gate(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-preview",
                "--run-receipt",
                RUN_RECEIPT,
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("requires --preview", payload["errors"][0]["message"])

    def test_cli_preview_returns_judge_input_receipt(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-preview",
                "--run-receipt",
                RUN_RECEIPT,
                "--preview",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        receipt = payload["data"]["skills_sdk_eval_ab_judge_preview"]["receipt"]
        self.assertEqual(receipt["status"], "preview")
        self.assertFalse(receipt["provider_invoked"])
        validate_ab_judge_preview_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
