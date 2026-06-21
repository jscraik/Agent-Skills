from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_judge import OllamaJudgeResult, _write_text_evidence, build_ab_judge_score_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_judge_score_receipt  # noqa: E402


RUN_RECEIPT = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.json"


def _decision(experiment_id: str) -> dict[str, object]:
    dimensions = [
        "task_success",
        "instruction_following",
        "evidence_quality",
        "repo_safety",
        "maintainability",
    ]
    return {
        "schema_version": "skills-sdk.ab-judge-decision.v0",
        "experiment_id": experiment_id,
        "dimension_scores": [
            {
                "dimension_id": dimension,
                "skill_a_score": 3.0,
                "skill_b_score": 4.0,
                "reason": f"skill_b has stronger {dimension} evidence",
                "evidence_refs": ["variant_results", "output_last_message_digest"],
            }
            for dimension in dimensions
        ],
        "normalized_score_a": 0.60,
        "normalized_score_b": 0.80,
        "winner": "skill_b",
        "confidence": "medium",
        "reason": "skill_b has stronger sanitized receipt evidence across the rubric.",
        "evidence_refs": ["variant_results", "rubric_digest"],
    }


class TestSkillsSdkAbJudgeScore(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_root = ".harness/test-sdk-ab-judge-score"
        self._remove_evidence_root()

    def tearDown(self) -> None:
        self._remove_evidence_root()

    def _remove_evidence_root(self) -> None:
        path = REPO_ROOT / self.evidence_root
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()

    def test_builder_scores_with_injected_local_judge(self) -> None:
        calls: list[tuple[str, str, int]] = []

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            calls.append((prompt, str(judge_profile["model"]), timeout_seconds))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return OllamaJudgeResult(
                exit_code=0,
                stdout=json.dumps(_decision(run_receipt["experiment_id"])),
                stderr="",
            )

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            timeout_seconds=12,
            runner=fake_runner,
        )

        self.assertEqual(receipt["status"], "scored")
        self.assertEqual(receipt["operation"], "ab_judge_score")
        self.assertEqual(receipt["judge_profile"]["id"], "oss-local")
        self.assertEqual(receipt["judge_profile"]["model"], "qwen3.5:latest")
        self.assertEqual(receipt["decision"]["winner"], "skill_b")
        self.assertEqual(receipt["decision"]["confidence"], "medium")
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(receipt["advisory_only"])
        self.assertTrue(receipt["calibration_required"])
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(len(calls), 1)
        self.assertIn("qwen3.5:latest", calls[0])
        self.assertTrue((REPO_ROOT / receipt["judge_output_path"]).is_file())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_invalid_judge_output(self) -> None:
        def invalid_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            return OllamaJudgeResult(exit_code=0, stdout="not json", stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=invalid_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_output_invalid_json", receipt["blockers"])
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue((REPO_ROOT / receipt["judge_output_path"]).is_file())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_unavailable_local_judge(self) -> None:
        def missing_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            raise FileNotFoundError("ollama")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=missing_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_provider_unavailable", receipt["blockers"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue((REPO_ROOT / receipt["judge_output_path"]).parent.is_dir())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_schema_extra_judge_keys(self) -> None:
        def extra_key_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["unexpected"] = "blocked"
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=extra_key_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_decision_keys_invalid", receipt["blockers"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_winner_mismatched_to_scores(self) -> None:
        def mismatched_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["winner"] = "skill_a"
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=mismatched_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_decision_winner_mismatch", receipt["blockers"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_low_confidence_directional_winner(self) -> None:
        def low_confidence_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["confidence"] = "low"
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=low_confidence_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_decision_winner_mismatch", receipt["blockers"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_normalized_scores_mismatched_to_dimension_rows(self) -> None:
        def mismatched_score_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
        ) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["dimension_scores"] = [
                {
                    **row,
                    "skill_a_score": 5.0,
                    "skill_b_score": 1.0,
                    "reason": "skill_a has stronger evidence",
                }
                for row in decision["dimension_scores"]
            ]
            decision["normalized_score_a"] = 0.20
            decision["normalized_score_b"] = 0.90
            decision["winner"] = "skill_b"
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=mismatched_score_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_decision_normalized_scores_mismatch", receipt["blockers"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_non_finite_judge_scores(self) -> None:
        def non_finite_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["normalized_score_a"] = math.nan
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=non_finite_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_output_invalid_json", receipt["blockers"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_file_evidence_root_before_writing(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        evidence_root.parent.mkdir(parents=True, exist_ok=True)
        evidence_root.write_text("not a directory", encoding="utf-8")

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            self.fail("runner should not be invoked when evidence root is a file")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=fake_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("evidence_root_not_directory", receipt["blockers"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["mutation_performed"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_file_ancestor_evidence_root_before_writing(self) -> None:
        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            self.fail("runner should not be invoked when an evidence root ancestor is a file")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root="AGENTS.md/judges",
            runner=fake_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("evidence_root_not_directory", receipt["blockers"])
        self.assertFalse(receipt["mutation_performed"])
        validate_ab_judge_score_receipt(receipt)

    def test_cli_requires_execute_gate(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-score",
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
        self.assertIn("requires --execute", payload["errors"][0]["message"])

    def test_evidence_writer_rejects_paths_outside_repo(self) -> None:
        with self.assertRaises(ValueError):
            _write_text_evidence(REPO_ROOT, "../sdk-ab-judge-escape.txt", "blocked")
        self.assertFalse((REPO_ROOT.parent / "sdk-ab-judge-escape.txt").exists())


if __name__ == "__main__":
    unittest.main()
