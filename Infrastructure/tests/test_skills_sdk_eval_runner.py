from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_runner import run_deterministic_eval  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_eval_run_receipt, validate_robot_envelope  # noqa: E402
from ask.commands.skills_impl import skills_sdk_eval_run  # noqa: E402
from ask.envelope import CallResult  # noqa: E402


PASS_DATASET = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json"
FAIL_DATASET = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-fail.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


class TestSkillsSdkEvalRunner(unittest.TestCase):
    def test_runner_passes_exact_match_jsonl_dataset(self) -> None:
        payload = run_deterministic_eval(REPO_ROOT, dataset=PASS_DATASET)
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "pass")
        self.assertEqual(model.case_count, 2)
        self.assertEqual(model.passed_count, 2)
        self.assertEqual(model.failed_count, 0)
        self.assertFalse(model.mutation_performed)

    def test_runner_reports_exact_match_failures(self) -> None:
        payload = run_deterministic_eval(REPO_ROOT, dataset=FAIL_DATASET)
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "fail")
        self.assertEqual(model.case_count, 1)
        self.assertEqual(model.passed_count, 0)
        self.assertEqual(model.failed_count, 1)
        self.assertEqual(model.cases[0].status, "fail")

    def test_runner_blocks_missing_dataset(self) -> None:
        payload = run_deterministic_eval(REPO_ROOT, dataset="Infrastructure/tests/fixtures/skills_sdk/evals/missing.jsonl")
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "blocked")
        self.assertEqual(model.case_count, 0)
        self.assertIn("dataset not found", model.blockers[0])

    def test_public_cli_runs_deterministic_eval_dataset(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "eval",
                "run",
                "--dataset",
                PASS_DATASET,
                "--skill",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_eval_run"]
        self.assertIsInstance(payload, dict)
        receipt = validate_eval_run_receipt(payload["receipt"])

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["passed_count"], 2)
        self.assertEqual(receipt.skill_ir_schema_version, "skills-sdk.skill-ir.v0")
        self.assertFalse(payload["mutation_performed"])

    def test_public_cli_returns_validation_error_for_failing_dataset(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "eval",
                "run",
                "--dataset",
                FAIL_DATASET,
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_eval_run"]

        self.assertEqual(envelope.status, "error")
        self.assertEqual(envelope.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["failed_count"], 1)

    def test_sdk_internal_runner_delegates_to_existing_eval_backend(self) -> None:
        internal_result = CallResult(status="success")
        internal_result.data.update(
            {
                "eval_status": "pass",
                "resolved_skill_path": "Skills/agent-ops/testing",
                "raw_output": "Scorecard: Infrastructure/artifacts/evals/testing.json",
                "tessl_eval": {"status": "skipped", "reason": "--skip-tessl"},
            }
        )

        with mock.patch("ask.commands.evals.run_evals", return_value=internal_result) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
            )

        run.assert_called_once_with(
            REPO_ROOT,
            "Skills/agent-ops/testing",
            mode="smoke",
            runner="codex",
            dashboard=True,
            skip_tessl=True,
            cases=None,
        )
        payload = result.data["skills_sdk_eval_run"]
        self.assertEqual(result.status, "success")
        self.assertEqual(payload["runner"], "internal_skill_builder_v0")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["receipt"]["runner"], "internal_skill_builder_v0")
        self.assertEqual(payload["receipt"]["target_path"], "Skills/agent-ops/testing")
        self.assertEqual(payload["internal_eval"]["tessl_eval"]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
