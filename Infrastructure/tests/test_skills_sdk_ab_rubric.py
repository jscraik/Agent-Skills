from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_rubric import (  # noqa: E402
    AB_RUBRIC_ID,
    build_ab_rubric_preview_receipt,
    canonical_ab_rubric_digest,
)
from ask.skills_sdk.typed_contracts import validate_ab_rubric_receipt  # noqa: E402


class TestSkillsSdkAbRubric(unittest.TestCase):
    def test_builder_emits_stable_non_invoking_rubric_contract(self) -> None:
        receipt = build_ab_rubric_preview_receipt()

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["operation"], "ab_rubric")
        self.assertEqual(receipt["rubric"]["rubric_id"], AB_RUBRIC_ID)
        self.assertEqual(receipt["rubric_digest"], canonical_ab_rubric_digest())
        self.assertTrue(receipt["rubric"]["stable_across_stages"])
        self.assertTrue(receipt["calibration_required"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])

        dimension_weights = [dimension["weight"] for dimension in receipt["rubric"]["dimensions"]]
        self.assertAlmostEqual(sum(dimension_weights), 1.0)
        self.assertEqual(
            {policy["stage"] for policy in receipt["rubric"]["stage_policies"]},
            {"local_oss_loop", "cloud_oss_loop", "external_validation"},
        )
        self.assertEqual(
            receipt["rubric"]["judge_output_contract"],
            {
                "decision_schema_version": "skills-sdk.ab-judge-decision.v0",
                "requires_dimension_scores": True,
                "requires_evidence_refs": True,
                "requires_reason_per_dimension": True,
                "unvalidated_judges_are_advisory": True,
            },
        )
        validate_ab_rubric_receipt(receipt)

    def test_cli_requires_preview_gate(self) -> None:
        proc = subprocess.run(
            [str(REPO_ROOT / "bin/ask"), "sdk", "eval", "ab-rubric", "--json", "--robot"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("requires --preview", payload["errors"][0]["message"])

    def test_cli_preview_returns_rubric_receipt(self) -> None:
        proc = subprocess.run(
            [str(REPO_ROOT / "bin/ask"), "sdk", "eval", "ab-rubric", "--preview", "--json", "--robot"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        receipt = payload["data"]["skills_sdk_eval_ab_rubric"]["receipt"]
        self.assertEqual(receipt["rubric"]["stage_policies"][0]["default_model"], "qwen3.5:9b-mlx")
        validate_ab_rubric_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
