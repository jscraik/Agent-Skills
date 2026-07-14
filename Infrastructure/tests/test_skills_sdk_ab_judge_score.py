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
from unittest.mock import patch

from pydantic import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_judge import (  # noqa: E402
    CodexJudgeResult,
    _clear_text_evidence,
    _codex_judge_command,
    _parse_judge_decision,
    _run_codex_judge,
    _score_evidence_paths,
    _write_text_evidence,
    build_ab_judge_score_receipt,
)
from ask.commands.sdk_eval import _AB_SCORE_PROFILE_CHOICES  # noqa: E402
from ask.skills_sdk import eval_ab_judge_codex as codex_judge  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_judge_score_receipt  # noqa: E402


RUN_RECEIPT = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"


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


def _comparison_payload_for_decision_test(experiment_id: str) -> dict[str, object]:
    return {
        "experiment_id": experiment_id,
        "rubric": {
            "winner_policy": {
                "minimum_normalized_delta": 0.05,
                "minimum_confidence": "medium",
                "tie_result": "inconclusive",
            },
            "dimensions": [
                {"id": "task_success", "weight": 0.35},
                {"id": "instruction_following", "weight": 0.20},
                {"id": "evidence_quality", "weight": 0.20},
                {"id": "repo_safety", "weight": 0.15},
                {"id": "maintainability", "weight": 0.10},
            ],
        },
    }


def _run_codex_with_captured_subprocess(
    profile_id: str,
    config_text: str,
    judge_profile: dict[str, object],
    extra_env: dict[str, str] | None = None,
) -> tuple[CodexJudgeResult, list[str], dict[str, str], str, Path | None]:
    captured_env: dict[str, str] = {}
    captured_command: list[str] = []
    captured_profile_text = ""
    output_file = REPO_ROOT / ".harness/test-sdk-ab-judge-score" / "judge" / "codex-last-message.json"

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal captured_profile_text
        captured_command.extend(args)
        captured_env.update(kwargs["env"])
        copied_profile = Path(captured_env["CODEX_HOME"]) / f"{profile_id}.config.toml"
        captured_profile_text = copied_profile.read_text(encoding="utf-8")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("{}", encoding="utf-8")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="{}", stderr="")

    original_run = subprocess.run
    try:
        with tempfile.TemporaryDirectory() as profile_dir:
            op_env_file = Path(profile_dir) / "codex.env" if profile_id == "oss-cloud" else None
            if op_env_file is not None:
                op_env_file.write_text("OLLAMA_API_KEY=op://vault/item/credential\\n", encoding="utf-8")
            Path(profile_dir, f"{profile_id}.config.toml").write_text(config_text, encoding="utf-8")
            env = {"ASK_CODEX_PROFILE_SOURCE_DIR": profile_dir, **(extra_env or {})}
            if op_env_file is not None:
                env["ASK_CODEX_OP_ENV_FILE"] = str(op_env_file)
            subprocess.run = fake_run  # type: ignore[assignment]
            base_env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
            with patch.dict(os.environ, {**base_env, **env}, clear=True):
                result = _run_codex_judge("prompt", judge_profile, 5, REPO_ROOT, output_file)
            return result, captured_command, captured_env, captured_profile_text, op_env_file
    finally:
        subprocess.run = original_run  # type: ignore[assignment]


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

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            calls.append((prompt, str(judge_profile["model"]), timeout_seconds))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(
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
        self.assertEqual(receipt["judge_profile"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(receipt["judge_profile"]["model_role"], "local_sandbox_eval_default")
        self.assertEqual(receipt["judge_profile"]["model_settings"]["num_ctx"], 8192)
        self.assertEqual(receipt["decision"]["winner"], "skill_b")
        self.assertEqual(receipt["decision"]["confidence"], "medium")
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(receipt["advisory_only"])
        self.assertTrue(receipt["calibration_required"])
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(len(calls), 1)
        self.assertIn("qwen3.5:9b-mlx", calls[0])
        self.assertTrue((REPO_ROOT / receipt["judge_output_path"]).is_file())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_scores_with_code_heavy_local_judge_profile(self) -> None:
        calls: list[str] = []

        def fake_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            calls.append(str(judge_profile["codex_profile"]))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(_decision(run_receipt["experiment_id"])), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            judge_profile_id="oss-local-code",
            runner=fake_runner,
        )

        self.assertEqual(receipt["status"], "scored")
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(receipt["judge_profile"]["id"], "oss-local-code")
        self.assertEqual(receipt["judge_profile"]["codex_profile"], "oss-local-code")
        self.assertEqual(receipt["judge_profile"]["model"], "qwen3-coder:30b")
        self.assertEqual(receipt["judge_profile"]["model_role"], "code_heavy_specialist")
        self.assertEqual(receipt["codex_profile"], "oss-local-code")
        self.assertEqual(calls, ["oss-local-code"])
        self.assertIn("--profile", receipt["judge_command_argv"])
        self.assertIn("oss-local-code", receipt["judge_command_argv"])
        validate_ab_judge_score_receipt(receipt)

    def test_codex_command_uses_large_transcript_model_settings(self) -> None:
        judge_profile = {
            "id": "oss-local-large-transcript",
            "codex_profile": "oss-local",
            "model": "qwen3.5:9b-mlx",
            "model_settings": {"num_ctx": 16384, "temperature": 0.1, "top_p": 0.9},
        }
        result, command, _env, _profile_text, _op_env_file = _run_codex_with_captured_subprocess(
            "oss-local",
            'model = "qwen3.5:9b-mlx"\n',
            judge_profile,
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--profile", command)
        self.assertEqual(command[command.index("--profile") + 1], "oss-local")
        self.assertIn("model_settings.num_ctx=16384", command)

    def test_codex_model_settings_skip_non_string_keys_before_sorting(self) -> None:
        overrides = codex_judge._codex_model_setting_overrides(
            {
                "id": "mixed-settings",
                "model_settings": {1: 16384, "num_ctx": 8192, "temperature": 0.1, "bad": object()},
            }
        )

        self.assertEqual(overrides, ["model_settings.num_ctx=8192", "model_settings.temperature=0.1"])

    def test_builder_scores_with_injected_cloud_judge_profile(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            calls.append((prompt, str(judge_profile["id"])))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(_decision(run_receipt["experiment_id"])), stderr="")

        with tempfile.TemporaryDirectory() as profile_dir:
            op_env_file = Path(profile_dir) / "codex.env"
            op_env_file.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            with patch.dict(os.environ, {"ASK_CODEX_OP_ENV_FILE": str(op_env_file)}):
                receipt = build_ab_judge_score_receipt(
                    REPO_ROOT,
                    run_receipt=RUN_RECEIPT,
                    evidence_root=self.evidence_root,
                    judge_profile_id="oss-cloud",
                    runner=fake_runner,
                )

        self.assertEqual(receipt["status"], "scored")
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(receipt["judge_profile"]["id"], "oss-cloud")
        self.assertEqual(receipt["codex_profile"], "oss-cloud")
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertEqual(calls[0][1], "oss-cloud")
        validate_ab_judge_score_receipt(receipt)

    def test_cli_accepts_cloud_judge_profile_before_execute_gate(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-score",
                "--run-receipt",
                RUN_RECEIPT,
                "--judge-profile",
                "oss-cloud",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        payload = json.loads(proc.stdout)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(payload["status"], "error")

    def test_cli_accepts_declared_local_code_judge_profile_before_execute_gate(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-score",
                "--run-receipt",
                RUN_RECEIPT,
                "--judge-profile",
                "oss-local-code",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        payload = json.loads(proc.stdout)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(payload["status"], "error")
        self.assertIn("requires --execute", payload["errors"][0]["message"])
        self.assertEqual(payload["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("requires --execute", payload["errors"][0]["message"])

    def test_ab_judge_score_cli_choices_exclude_codex_fast(self) -> None:
        self.assertIn("oss-local-code", _AB_SCORE_PROFILE_CHOICES)
        self.assertIn("oss-local-fallback", _AB_SCORE_PROFILE_CHOICES)
        self.assertNotIn("codex-fast", _AB_SCORE_PROFILE_CHOICES)

    def test_builder_blocks_invalid_judge_output(self) -> None:
        def invalid_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            return CodexJudgeResult(exit_code=0, stdout="not json", stderr="")

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

    def test_builder_blocks_codex_metadata_fallback_before_scoring(self) -> None:
        def fallback_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(
                exit_code=0,
                stdout=json.dumps(_decision(run_receipt["experiment_id"])),
                stderr="warning: Model metadata for qwen3.5:9b-mlx not found. Defaulting to fallback metadata.",
            )

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=fallback_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("codex_runtime_metadata_fallback", receipt["blockers"])
        self.assertIsNone(receipt["decision"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_visible_thinking_before_scoring(self) -> None:
        def thinking_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(
                exit_code=0,
                stdout="<think>hidden chain should not leak</think>\n" + json.dumps(_decision(run_receipt["experiment_id"])),
                stderr="",
            )

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=thinking_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("codex_runtime_visible_thinking", receipt["blockers"])
        self.assertIsNone(receipt["decision"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_allows_codex_jsonl_reasoning_telemetry_when_guard_allows_it(self) -> None:
        def telemetry_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            reasoning_event = json.dumps({
                "type": "item.completed",
                "item": {"id": "item_1", "type": "reasoning", "text": "structured telemetry"},
            })
            output_file.write_text(json.dumps(_decision(run_receipt["experiment_id"])), encoding="utf-8")
            return CodexJudgeResult(
                exit_code=0,
                stdout=reasoning_event,
                stderr="",
            )

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=telemetry_runner,
        )

        self.assertEqual(receipt["status"], "scored")
        self.assertEqual(receipt["blockers"], [])
        self.assertIsNotNone(receipt["decision"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_codex_token_budget_blowout_before_scoring(self) -> None:
        def costly_runner(
            prompt: str,
            judge_profile: dict[str, object],
            timeout_seconds: int,
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            usage_event = json.dumps({
                "type": "turn.completed",
                "usage": {"input_tokens": 8231, "output_tokens": 53, "reasoning_output_tokens": 0},
            })
            stdout = json.dumps(_decision(run_receipt["experiment_id"])) + "\n" + usage_event + "\n"
            return CodexJudgeResult(exit_code=0, stdout=stdout, stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=costly_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("codex_runtime_token_budget_exceeded", receipt["blockers"])
        self.assertIsNone(receipt["decision"])
        validate_ab_judge_score_receipt(receipt)

    def test_parse_judge_decision_accepts_fenced_json_and_derives_normalized_scores(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
        comparison_payload = _comparison_payload_for_decision_test(run_receipt["experiment_id"])
        model_payload = _decision(run_receipt["experiment_id"])
        model_payload["dimension_scores"][-1]["skill_a_score"] = 4.5
        model_payload["dimension_scores"][-1]["skill_b_score"] = 4.5
        model_payload["normalized_score_a"] = 0.97
        model_payload["normalized_score_b"] = 0.97
        raw_output = "```json\n" + json.dumps(model_payload) + "\n```"

        decision, blocker = _parse_judge_decision(raw_output, comparison_payload)

        self.assertIsNone(blocker)
        self.assertIsNotNone(decision)
        self.assertAlmostEqual(decision["normalized_score_a"], 0.63)
        self.assertAlmostEqual(decision["normalized_score_b"], 0.81)

        malformed_output = raw_output.replace("}], \"normalized_score_a\"", "]}, \"normalized_score_a\"")
        repaired_decision, repaired_blocker = _parse_judge_decision(malformed_output, comparison_payload)

        self.assertIsNone(repaired_blocker)
        self.assertIsNotNone(repaired_decision)
        self.assertAlmostEqual(repaired_decision["normalized_score_a"], 0.63)

        missing_comma_output = raw_output.replace('", "evidence_refs"', '"\n\n"evidence_refs"', 1)
        comma_repaired_decision, comma_repaired_blocker = _parse_judge_decision(missing_comma_output, comparison_payload)

        self.assertIsNone(comma_repaired_blocker)
        self.assertIsNotNone(comma_repaired_decision)
        self.assertAlmostEqual(comma_repaired_decision["normalized_score_b"], 0.81)

    def test_builder_blocks_unavailable_local_judge(self) -> None:
        def missing_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            raise FileNotFoundError("codex")

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
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
            raise PermissionError("codex")

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
            / "codex-last-message.json"
        )
        stale_output.parent.mkdir(parents=True, exist_ok=True)
        stale_output.write_text('{"stale": true}', encoding="utf-8")

        def missing_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            raise FileNotFoundError("codex")

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
        def extra_key_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["unexpected"] = "blocked"
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

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
        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(_decision(run_receipt["experiment_id"])), stderr="")

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
        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(_decision(run_receipt["experiment_id"])), stderr="")

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
        def mismatched_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["winner"] = "skill_a"
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

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
        def low_confidence_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["confidence"] = "low"
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

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
            repo_root: Path,
            output_file: Path,
        ) -> CodexJudgeResult:
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
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

        receipt = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=RUN_RECEIPT,
            evidence_root=self.evidence_root,
            runner=mismatched_score_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_decision_winner_mismatch", receipt["blockers"])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_non_finite_judge_scores(self) -> None:
        def non_finite_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
            decision = _decision(run_receipt["experiment_id"])
            decision["normalized_score_a"] = math.nan
            return CodexJudgeResult(exit_code=0, stdout=json.dumps(decision), stderr="")

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

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
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
        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
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
    def test_evidence_preflight_rejects_symlinked_evidence_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        target_root = REPO_ROOT / ".harness/test-sdk-ab-judge-score-target"
        shutil.rmtree(target_root, ignore_errors=True)
        try:
            target_root.mkdir(parents=True, exist_ok=True)
            evidence_root.symlink_to(target_root, target_is_directory=True)

            evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, "1234567890abcdef")

            self.assertEqual(evidence["blocker"], "score_evidence_path_outside_repo")
            self.assertIsNone(evidence["prompt_path"])
            self.assertIsNone(evidence["output_path"])
        finally:
            if evidence_root.is_symlink():
                evidence_root.unlink()
            shutil.rmtree(target_root, ignore_errors=True)

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
            target = Path(target_dir) / "codex-last-message.json"
            target.write_text("old-output", encoding="utf-8")
            score_dir.mkdir(parents=True, exist_ok=True)
            symlink = score_dir / "codex-last-message.json"
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

    def test_local_codex_runner_uses_oss_local_profile(self) -> None:
        result, captured_command, captured_env, captured_profile_text, _op_env_file = _run_codex_with_captured_subprocess(
            "oss-local",
            'model = "qwen3.5:9b-mlx"\nmodel_provider = "ollama"\nsandbox_mode = "read-only"\n',
            {"id": "oss-local", "codex_profile": "oss-local", "model": "qwen3.5:9b-mlx"},
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:4], ["codex", "exec", "--profile", "oss-local"])
        self.assertIn("--sandbox", captured_command)
        self.assertIn("read-only", captured_command)
        self.assertIn("--ephemeral", captured_command)
        self.assertIn("--output-last-message", captured_command)
        self.assertIn("--cd", captured_command)
        self.assertNotEqual(captured_command[captured_command.index("--cd") + 1], str(REPO_ROOT))
        self.assertEqual(result.output_text, "{}")
        self.assertIn("CODEX_HOME", captured_env)
        self.assertIn("CODEX_SQLITE_HOME", captured_env)
        self.assertIn('model = "qwen3.5:9b-mlx"', captured_profile_text)
        self.assertIn('model_catalog_json = "', captured_profile_text)
        self.assertIn("model_context_window = 262144", captured_profile_text)
        self.assertIn("hide_agent_reasoning = true", captured_profile_text)
        self.assertNotIn("OPENAI_API_KEY", captured_env)
        self.assertNotIn("OLLAMA_API_KEY", captured_env)
        self.assertNotIn("GITHUB_TOKEN", captured_env)

    def test_code_heavy_codex_runner_uses_dedicated_local_profile(self) -> None:
        result, captured_command, _captured_env, captured_profile_text, _op_env_file = _run_codex_with_captured_subprocess(
            "oss-local-code",
            'model = "qwen3-coder:30b"\nmodel_provider = "ollama"\nsandbox_mode = "read-only"\n',
            {"id": "oss-local-code", "codex_profile": "oss-local-code", "model": "qwen3-coder:30b"},
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:4], ["codex", "exec", "--profile", "oss-local-code"])
        self.assertIn('model = "qwen3-coder:30b"', captured_profile_text)

    def test_fallback_codex_runner_uses_dedicated_local_profile(self) -> None:
        result, captured_command, _captured_env, captured_profile_text, _op_env_file = _run_codex_with_captured_subprocess(
            "oss-local-fallback",
            'model = "qwen3.5:latest"\nmodel_provider = "ollama"\nsandbox_mode = "read-only"\n',
            {"id": "oss-local-fallback", "codex_profile": "oss-local-fallback", "model": "qwen3.5:latest"},
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:4], ["codex", "exec", "--profile", "oss-local-fallback"])
        self.assertIn('model = "qwen3.5:latest"', captured_profile_text)

    def test_cloud_codex_runner_wraps_codex_with_op_env_file(self) -> None:
        result, captured_command, captured_env, captured_profile_text, op_env_file = _run_codex_with_captured_subprocess(
            "oss-cloud",
            'model = "minimax-m2.7:cloud"\nmodel_provider = "ollama-cloud"\nsandbox_mode = "read-only"\n',
            {"id": "oss-cloud", "model": "minimax-m2.7:cloud", "secret_env_names": ["OLLAMA_API_KEY"]},
            {"OPENAI_API_KEY": "other-token", "GITHUB_TOKEN": "repo-token"},
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(captured_command[0].endswith("/op") or captured_command[0] == "op")
        self.assertEqual(captured_command[1:5], ["run", "--env-file", str(op_env_file), "--"])
        codex_segments = [captured_command[index:index + 4] for index in range(len(captured_command) - 3)]
        self.assertIn(["codex", "exec", "--profile", "oss-cloud"], codex_segments)
        self.assertNotIn("OLLAMA_API_KEY", captured_env)
        self.assertIn('model = "minimax-m2.7:cloud"', captured_profile_text)
        self.assertNotIn("OPENAI_API_KEY", captured_env)
        self.assertNotIn("GITHUB_TOKEN", captured_env)

    def test_cloud_codex_command_uses_oss_cloud_profile(self) -> None:
        output_file = REPO_ROOT / self.evidence_root / "judge" / "codex-last-message.json"

        with tempfile.TemporaryDirectory() as profile_dir:
            op_env_file = Path(profile_dir) / "codex.env"
            op_env_file.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            with patch.dict(os.environ, {"ASK_CODEX_OP_ENV_FILE": str(op_env_file)}):
                command = _codex_judge_command(
                    {"id": "oss-cloud", "model": "minimax-m2.7:cloud", "secret_env_names": ["OLLAMA_API_KEY"]},
                    codex_judge._codex_judge_work_dir(output_file),
                    output_file,
                )

        self.assertEqual(
            command[:9],
            [command[0], "run", "--env-file", str(op_env_file), "--", "codex", "exec", "--profile", "oss-cloud"],
        )
        self.assertEqual(
            command[9:],
            [
                "--cd",
                str(codex_judge._codex_judge_work_dir(output_file)),
                "--sandbox",
                "read-only",
                "--ephemeral",
                "--json",
                "--output-last-message",
                str(output_file),
                "-",
            ],
        )
        self.assertNotEqual(command[11], str(REPO_ROOT))

    def test_cloud_op_env_file_requires_a_1password_reference(self) -> None:
        profile = {"id": "oss-cloud", "model": "minimax-m2.7:cloud", "secret_env_names": ["OLLAMA_API_KEY"]}
        with tempfile.TemporaryDirectory() as profile_dir:
            env_file = Path(profile_dir) / "codex.env"
            env_file.write_text("", encoding="utf-8")
            with patch.dict(os.environ, {"ASK_CODEX_OP_ENV_FILE": str(env_file)}):
                self.assertIsNone(codex_judge._codex_op_env_file_path(profile))
            env_file.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            with patch.dict(os.environ, {"ASK_CODEX_OP_ENV_FILE": str(env_file)}):
                self.assertEqual(codex_judge._codex_op_env_file_path(profile), env_file)

    @unittest.skipIf(not hasattr(os, "mkfifo"), "fifo support unavailable")
    def test_cloud_codex_command_accepts_op_env_fifo(self) -> None:
        output_file = REPO_ROOT / self.evidence_root / "judge" / "codex-last-message.json"
        profile = {"id": "oss-cloud", "model": "minimax-m2.7:cloud", "secret_env_names": ["OLLAMA_API_KEY"]}
        with tempfile.TemporaryDirectory() as profile_dir:
            op_env_file = Path(profile_dir) / "codex.env"
            os.mkfifo(op_env_file)
            env_patch = patch.dict(os.environ, {"ASK_CODEX_OP_ENV_FILE": str(op_env_file)})
            bin_patch = patch.object(codex_judge, "_codex_op_bin", return_value="/opt/homebrew/bin/op")
            with env_patch, bin_patch:
                command = _codex_judge_command(profile, codex_judge._codex_judge_work_dir(output_file), output_file)
        self.assertEqual(command[1:5], ["run", "--env-file", str(op_env_file), "--"])
        self.assertEqual(command[5:9], ["codex", "exec", "--profile", "oss-cloud"])
