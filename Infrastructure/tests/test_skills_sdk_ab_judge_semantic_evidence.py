from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_judge import (  # noqa: E402
    CodexJudgeResult,
    build_ab_judge_preview_receipt,
    build_ab_judge_score_receipt,
)


RUN_RECEIPT = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"


class TestSkillsSdkAbJudgeSemanticEvidence(unittest.TestCase):
    def test_hash_only_run_receipts_block_before_scoring(self) -> None:
        test_root = REPO_ROOT / ".harness/test-sdk-ab-judge-semantic-evidence"
        shutil.rmtree(test_root, ignore_errors=True)
        try:
            test_root.mkdir(parents=True, exist_ok=True)
            receipt_path = test_root / "ab-run-receipt.json"
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            for result in run_receipt["variant_results"]:
                result.pop("semantic_output_excerpt", None)
            for gate in run_receipt.get("runtime_profile_gates", []):
                for result in gate["variant_results"]:
                    result.pop("semantic_output_excerpt", None)
            receipt_path.write_text(json.dumps(run_receipt), encoding="utf-8")

            def fake_runner(
                prompt: str,
                judge_profile: dict[str, object],
                timeout_seconds: int,
                repo_root: Path,
                output_file: Path,
            ) -> CodexJudgeResult:
                self.fail("runner should not be invoked without semantic output evidence")

            preview = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=str(receipt_path))
            score = build_ab_judge_score_receipt(
                REPO_ROOT,
                run_receipt=str(receipt_path),
                evidence_root=".harness/test-sdk-ab-judge-semantic-evidence/score",
                runner=fake_runner,
            )
        finally:
            shutil.rmtree(test_root, ignore_errors=True)

        self.assertEqual(preview["status"], "blocked")
        self.assertIn("A:semantic_output_evidence_missing", preview["blockers"])
        self.assertIn("B:semantic_output_evidence_missing", preview["blockers"])
        self.assertEqual(score["status"], "blocked")
        self.assertFalse(score["provider_invoked"])
        self.assertIn("judge_input_preview_blocked", score["blockers"])


if __name__ == "__main__":
    unittest.main()
