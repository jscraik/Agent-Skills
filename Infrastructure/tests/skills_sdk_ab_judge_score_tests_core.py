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
    _codex_judge_command_shape,
    _judge_prompt,
    _parse_judge_decision,
    _run_codex_judge,
    _score_evidence_paths,
    _validate_judge_execution_argv,
    _write_text_evidence,
    build_ab_judge_score_receipt,
)
from ask.commands.sdk_eval import _AB_SCORE_PROFILE_CHOICES  # noqa: E402
from ask.skills_sdk import eval_ab_judge_codex as codex_judge  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_judge_score_receipt  # noqa: E402


RUN_RECEIPT = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
_EXPERIMENTAL_MALWARE_WARNING = (
    "warning: Malware checks are experimental and may change without warning. "
    "Pass `--preview-features malware-check` to disable this warning.\n"
)


def _assert_robot_cli_stderr(testcase: unittest.TestCase, stderr: str) -> None:
    """Keep robot-output tests strict while admitting the runner's known warning."""
    testcase.assertIn(stderr, {"", _EXPERIMENTAL_MALWARE_WARNING})


def _judge_result(
    judge_profile: dict[str, object],
    *,
    stdout: str,
    stderr: str = "",
    exit_code: int = 0,
    output_file: Path | None = None,
) -> CodexJudgeResult:
    executed_argv = (
        _codex_judge_command(judge_profile, codex_judge._codex_judge_work_dir(output_file), output_file)
        if output_file is not None else None
    )
    return CodexJudgeResult(
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        executed_argv=executed_argv,
    )


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
        captured_env.update(kwargs.get("env") or {})
        if "CODEX_HOME" in captured_env:
            copied_profile = Path(captured_env["CODEX_HOME"]) / f"{profile_id}.config.toml"
            captured_profile_text = copied_profile.read_text(encoding="utf-8")
        else:
            captured_profile_text = config_text
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("{}", encoding="utf-8")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="{}", stderr="")

    with tempfile.TemporaryDirectory() as profile_dir:
        env_dir = Path(profile_dir) / ".codex"
        env_dir.mkdir()
        auth_env_file = env_dir / ".env" if profile_id == "oss-cloud" else None
        if auth_env_file is not None:
            os.mkfifo(auth_env_file)
        Path(profile_dir, f"{profile_id}.config.toml").write_text(config_text, encoding="utf-8")
        env = {"ASK_CODEX_PROFILE_SOURCE_DIR": profile_dir, **(extra_env or {})}
        if auth_env_file is not None:
            env["SKILLS_SDK_OSS_CLOUD_ENV_FILE"] = str(auth_env_file)
        base_env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
        with (
            patch.object(subprocess, "run", fake_run),
            patch.dict(os.environ, {**base_env, **env}, clear=True),
            patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=Path(profile_dir)),
        ):
            result = _run_codex_judge("prompt", judge_profile, 5, REPO_ROOT, output_file)
        return result, captured_command, captured_env, captured_profile_text, auth_env_file

class _SkillsSdkAbJudgeScoreBase(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_root = '.harness/test-sdk-ab-judge-score'
        self._remove_evidence_root()

    def tearDown(self) -> None:
        self._remove_evidence_root()

    def _remove_evidence_root(self) -> None:
        path = REPO_ROOT / self.evidence_root
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()

__all__ = [name for name in globals() if not name.startswith("__")]
