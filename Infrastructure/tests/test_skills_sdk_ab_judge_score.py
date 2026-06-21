from __future__ import annotations

import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from pydantic import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_judge import (  # noqa: E402
    OllamaJudgeResult,
    _clear_text_evidence,
    _run_ollama_judge,
    _score_evidence_paths,
    _write_text_evidence,
    build_ab_judge_score_receipt,
)
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

    def test_builder_blocks_local_judge_startup_oserror(self) -> None:
        def permission_denied_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
        ) -> OllamaJudgeResult:
            raise PermissionError("ollama")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=permission_denied_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_provider_unavailable", receipt["blockers"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertTrue(receipt["mutation_performed"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_clears_stale_output_when_local_judge_unavailable(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
        stale_output = (
            REPO_ROOT
            / self.evidence_root
            / run_receipt["experiment_id"]
            / "judge"
            / "ollama-output.json"
        )
        stale_output.parent.mkdir(parents=True, exist_ok=True)
        stale_output.write_text('{"stale": true}', encoding="utf-8")

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
        self.assertFalse(stale_output.exists())
        self.assertIsNone(receipt["judge_output_digest"])
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

    def test_typed_contract_rejects_decision_for_different_experiment(self) -> None:
        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(_decision(run_receipt["experiment_id"])), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=fake_runner,
        )
        receipt["decision"]["experiment_id"] = "0000000000000000"

        with self.assertRaises(ValidationError):
            validate_ab_judge_score_receipt(receipt)

    def test_typed_contract_rejects_persisted_score_arithmetic_mismatch(self) -> None:
        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int) -> OllamaJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return OllamaJudgeResult(exit_code=0, stdout=json.dumps(_decision(run_receipt["experiment_id"])), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=fake_runner,
        )
        receipt["decision"]["dimension_scores"] = [
            {
                **row,
                "skill_a_score": 5.0,
                "skill_b_score": 1.0,
                "reason": "skill_a has stronger evidence",
            }
            for row in receipt["decision"]["dimension_scores"]
        ]
        receipt["decision"]["normalized_score_a"] = 0.20
        receipt["decision"]["normalized_score_b"] = 0.90
        receipt["decision"]["winner"] = "skill_b"

        with self.assertRaises(ValidationError):
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

    def test_evidence_preflight_rejects_paths_outside_repo(self) -> None:
        evidence = _score_evidence_paths(REPO_ROOT, "../sdk-ab-judge-escape", "1234567890abcdef")

        self.assertEqual(evidence["blocker"], "evidence_root_outside_repo")
        self.assertFalse((REPO_ROOT.parent / "sdk-ab-judge-escape.txt").exists())

    def test_evidence_preflight_rejects_malformed_experiment_id(self) -> None:
        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "../../../scratch")

        self.assertEqual(evidence["blocker"], "experiment_id_invalid")
        self.assertIsNone(evidence["prompt_path"])
        self.assertIsNone(evidence["output_path"])

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_evidence_preflight_rejects_symlinked_experiment_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        experiment_root = evidence_root / "1234567890abcdef"
        with tempfile.TemporaryDirectory(prefix="sdk-ab-judge-outside-") as outside_dir:
            outside = Path(outside_dir)
            evidence_root.mkdir(parents=True, exist_ok=True)
            experiment_root.symlink_to(outside, target_is_directory=True)

            evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "1234567890abcdef")

            self.assertEqual(evidence["blocker"], "score_evidence_path_outside_repo")
            self.assertIsNone(evidence["prompt_path"])
            self.assertIsNone(evidence["output_path"])
            if experiment_root.is_symlink():
                experiment_root.unlink()

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_evidence_preflight_rejects_symlinked_score_file(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / "1234567890abcdef" / "judge"
        with tempfile.TemporaryDirectory(prefix="sdk-ab-judge-outside-") as outside_dir:
            outside = Path(outside_dir) / "prompt.txt"
            outside.write_text("outside", encoding="utf-8")
            score_dir.mkdir(parents=True, exist_ok=True)
            (score_dir / "prompt.txt").symlink_to(outside)

            evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "1234567890abcdef")

            self.assertEqual(evidence["blocker"], "score_evidence_path_outside_repo")
            self.assertIsNone(evidence["prompt_path"])
            self.assertIsNone(evidence["output_path"])

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_evidence_preflight_rejects_repo_internal_symlinked_experiment_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        experiment_root = evidence_root / "1234567890abcdef"
        target_root = evidence_root / "alternate-target"
        evidence_root.mkdir(parents=True, exist_ok=True)
        target_root.mkdir(parents=True, exist_ok=True)
        experiment_root.symlink_to(target_root, target_is_directory=True)

        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "1234567890abcdef")

        self.assertEqual(evidence["blocker"], "score_evidence_path_outside_repo")
        self.assertIsNone(evidence["prompt_path"])
        self.assertIsNone(evidence["output_path"])

    def test_evidence_preflight_rejects_directory_score_file_leaf(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / "1234567890abcdef" / "judge"
        (score_dir / "prompt.txt").mkdir(parents=True, exist_ok=True)

        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "1234567890abcdef")

        self.assertEqual(evidence["blocker"], "score_evidence_path_outside_repo")
        self.assertIsNone(evidence["prompt_path"])
        self.assertIsNone(evidence["output_path"])

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_clear_text_evidence_unlinks_leaf_symlink_not_target(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / "1234567890abcdef" / "judge"
        with tempfile.TemporaryDirectory(prefix="sdk-ab-judge-target-") as target_dir:
            target = Path(target_dir) / "ollama-output.json"
            target.write_text("old-output", encoding="utf-8")
            score_dir.mkdir(parents=True, exist_ok=True)
            symlink = score_dir / "ollama-output.json"
            symlink.symlink_to(target)

            _clear_text_evidence(REPO_ROOT, symlink)

            self.assertFalse(symlink.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "old-output")

    @unittest.skipIf(not hasattr(Path, "symlink_to"), "symlink support unavailable")
    def test_write_text_evidence_rejects_leaf_symlink(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / "1234567890abcdef" / "judge"
        with tempfile.TemporaryDirectory(prefix="sdk-ab-judge-target-") as target_dir:
            target = Path(target_dir) / "prompt.txt"
            target.write_text("original", encoding="utf-8")
            score_dir.mkdir(parents=True, exist_ok=True)
            symlink = score_dir / "prompt.txt"
            symlink.symlink_to(target)

            _write_text_evidence(REPO_ROOT, symlink, "new prompt")

            self.assertTrue(symlink.is_symlink())
            self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_write_text_evidence_resets_existing_file_permissions(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / "1234567890abcdef" / "judge"
        prompt_file = score_dir / "prompt.txt"
        score_dir.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text("old prompt", encoding="utf-8")
        prompt_file.chmod(0o644)

        _write_text_evidence(REPO_ROOT, prompt_file, "new prompt")

        self.assertEqual(prompt_file.read_text(encoding="utf-8"), "new prompt")
        self.assertEqual(prompt_file.stat().st_mode & 0o777, 0o600)

    def test_evidence_preflight_rejects_existing_file_experiment_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        evidence_root.mkdir(parents=True, exist_ok=True)
        (evidence_root / "1234567890abcdef").write_text("not a directory", encoding="utf-8")

        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "1234567890abcdef")

        self.assertEqual(evidence["blocker"], "evidence_root_not_directory")
        self.assertIsNone(evidence["prompt_path"])
        self.assertIsNone(evidence["output_path"])

    def test_local_ollama_runner_strips_ambient_cloud_auth(self) -> None:
        captured_env: dict[str, str] = {}

        def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured_env.update(kwargs["env"])
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="{}", stderr="")

        with mock.patch.dict(
            os.environ,
            {
                "OLLAMA_HOST": "https://ollama.com",
                "OLLAMA_API_KEY": "secret",
                "OLLAMA_KEEP_ALIVE": "1h",
            },
        ):
            with mock.patch("subprocess.run", side_effect=fake_run):
                result = _run_ollama_judge(
                    "prompt",
                    {"host": "http://localhost:11434", "model": "qwen3.5:latest"},
                    5,
                )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_env["OLLAMA_HOST"], "http://localhost:11434")
        self.assertNotIn("OLLAMA_API_KEY", captured_env)
        self.assertNotIn("OLLAMA_KEEP_ALIVE", captured_env)


if __name__ == "__main__":
    unittest.main()
