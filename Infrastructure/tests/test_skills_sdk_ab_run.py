from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_run import CodexRunResult, _codex_runner_env, _execute_variant, build_ab_run_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_run_receipt  # noqa: E402


SKILL_A = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
SKILL_B = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
FIXTURE = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json"
IDENTITY_A = {
    "skill_ir_schema_version": "skills-sdk.skill-ir.v0",
    "package_id": "skills-sdk-valid-fixture",
    "package_digest": f"sha256:{'1' * 64}",
}
IDENTITY_B = {
    "skill_ir_schema_version": "skills-sdk.skill-ir.v0",
    "package_id": "skills-sdk-scenario-quality-fixture",
    "package_digest": f"sha256:{'2' * 64}",
}
TestRunner = Callable[[list[str], str, Path, int], CodexRunResult]


def _build_test_ab_run_receipt(evidence_root: str, runner: TestRunner) -> dict[str, object]:
    return build_ab_run_receipt(
        REPO_ROOT,
        skill_a=SKILL_A,
        skill_b=SKILL_B,
        fixture=FIXTURE,
        skill_a_identity=IDENTITY_A,
        skill_b_identity=IDENTITY_B,
        evidence_root=evidence_root,
        runner=runner,
    )


class TestSkillsSdkAbRun(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_root = ".harness/test-sdk-ab-run"
        shutil.rmtree(REPO_ROOT / self.evidence_root, ignore_errors=True)

    def tearDown(self) -> None:
        shutil.rmtree(REPO_ROOT / self.evidence_root, ignore_errors=True)

    def test_codex_runner_env_keeps_secret_names_out_of_skill_execution(self) -> None:
        env = _codex_runner_env(
            {
                "PATH": "/usr/bin",
                "HOME": "/tmp/home",
                "OLLAMA_API_KEY": "secret",
                "OPENAI_API_KEY": "secret",
                "SESSION_TOKEN": "secret",
                "CODEX_HOME": "/tmp/codex",
            }
        )

        self.assertEqual(env["PATH"], "/usr/bin")
        self.assertEqual(env["HOME"], "/tmp/home")
        self.assertEqual(env["CODEX_HOME"], "/tmp/codex")
        self.assertNotIn("OLLAMA_API_KEY", env)
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("SESSION_TOKEN", env)

    def test_execute_variant_rejects_external_evidence_paths_before_runner_starts(self) -> None:
        calls: list[list[str]] = []

        def fake_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            calls.append(command_argv)
            return CodexRunResult(exit_code=0, stdout="", stderr="")

        base_plan = {
            "variant_label": "A",
            "command_argv": ["codex", "exec", "--output-last-message", "unused"],
            "sandbox_mode": "read-only",
            "runner_prompt_input_path": f"{self.evidence_root}/A/prompt.txt",
            "runner_stdout_capture_path": f"{self.evidence_root}/A/codex-stdout.jsonl",
            "output_last_message_path": f"{self.evidence_root}/A/last-message.json",
        }

        for key, unsafe_path in (
            ("runner_prompt_input_path", "/tmp/ab-run-prompt.txt"),
            ("runner_stdout_capture_path", "../ab-run-stdout.jsonl"),
            ("output_last_message_path", "/tmp/ab-run-last-message.json"),
        ):
            with self.subTest(key=key):
                command_plan = dict(base_plan)
                command_plan[key] = unsafe_path

                with self.assertRaises(ValueError):
                    _execute_variant(
                        REPO_ROOT,
                        command_plan=command_plan,
                        prompt="prompt",
                        timeout_seconds=1,
                        runner=fake_runner,
                    )

        self.assertEqual(calls, [])

    def test_builder_executes_with_injected_runner_and_records_evidence(self) -> None:
        calls: list[list[str]] = []

        def fake_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            calls.append(command_argv)
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"variant": len(calls), "prompt_digest_input": prompt[:24]}), encoding="utf-8")
            return CodexRunResult(exit_code=0, stdout='{"event":"done"}\n', stderr="")

        receipt = build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=fake_runner,
        )

        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["command_variant_labels"], ["A", "B"])
        self.assertEqual({result["variant_label"] for result in receipt["variant_results"]}, {"A", "B"})
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(receipt["network_accessed"])
        self.assertTrue(receipt["provider_invoked"])
        self.assertFalse(receipt["judge_provider_invoked"])
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertEqual(len(calls), 2)
        for result in receipt["variant_results"]:
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["exit_code"], 0)
            self.assertTrue((REPO_ROOT / result["prompt_stdin_path"]).is_file())
            self.assertTrue((REPO_ROOT / result["runner_stdout_capture_path"]).is_file())
            self.assertTrue((REPO_ROOT / result["runner_stderr_capture_path"]).is_file())
            self.assertTrue((REPO_ROOT / result["output_last_message_path"]).is_file())
            self.assertTrue(str(result["output_last_message_digest"]).startswith("sha256:"))
        validate_ab_run_receipt(receipt)

    def test_builder_blocks_failed_variant_without_judge_invocation(self) -> None:
        def fake_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            if command_argv[command_argv.index("--output-last-message") + 1].endswith("/A/last-message.json"):
                output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text("{}", encoding="utf-8")
                return CodexRunResult(exit_code=0, stdout='{"event":"done"}\n', stderr="")
            return CodexRunResult(exit_code=2, stdout="", stderr="boom")

        receipt = build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=fake_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("B:codex_exec_exit_2", receipt["blockers"])
        self.assertIn("B:output_last_message_missing", receipt["blockers"])
        self.assertFalse(receipt["judge_provider_invoked"])
        validate_ab_run_receipt(receipt)

    def test_builder_preserves_timeout_output_as_text_evidence(self) -> None:
        def timeout_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            raise subprocess.TimeoutExpired(command_argv, timeout_seconds, output=b"partial stdout", stderr=b"partial stderr")

        receipt = build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=timeout_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("A:codex_exec_timeout", receipt["blockers"])
        self.assertIn("B:codex_exec_timeout", receipt["blockers"])
        for result in receipt["variant_results"]:
            self.assertEqual(result["exit_code"], 124)
            self.assertTrue(str(result["runner_stdout_digest"]).startswith("sha256:"))
            self.assertTrue(str(result["runner_stderr_digest"]).startswith("sha256:"))
            self.assertEqual((REPO_ROOT / result["runner_stdout_capture_path"]).read_text(encoding="utf-8"), "partial stdout")
            self.assertEqual((REPO_ROOT / result["runner_stderr_capture_path"]).read_text(encoding="utf-8"), "partial stderr")
        validate_ab_run_receipt(receipt)

    def test_builder_clears_stale_output_before_variant_rerun(self) -> None:
        def successful_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"prompt": prompt[:12]}), encoding="utf-8")
            return CodexRunResult(exit_code=0, stdout='{"event":"done"}\n', stderr="")

        first_receipt = _build_test_ab_run_receipt(self.evidence_root, successful_runner)
        self.assertEqual(first_receipt["status"], "completed")

        def missing_output_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int
        ) -> CodexRunResult:
            return CodexRunResult(exit_code=0, stdout='{"event":"done"}\n', stderr="")

        second_receipt = _build_test_ab_run_receipt(self.evidence_root, missing_output_runner)

        self.assertEqual(second_receipt["status"], "blocked")
        self.assertIn("A:output_last_message_missing", second_receipt["blockers"])
        self.assertIn("B:output_last_message_missing", second_receipt["blockers"])
        for result in second_receipt["variant_results"]:
            self.assertIsNone(result["output_last_message_digest"])
        validate_ab_run_receipt(second_receipt)

    def test_builder_does_not_claim_provider_invocation_when_codex_never_starts(self) -> None:
        def missing_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            raise OSError("codex not found")

        receipt = build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=missing_runner,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("A:codex_exec_unavailable", receipt["blockers"])
        self.assertIn("B:codex_exec_unavailable", receipt["blockers"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["judge_provider_invoked"])
        self.assertNotIn("codex_exec_started", receipt["variant_results"][0])
        validate_ab_run_receipt(receipt)

    def test_cli_requires_execute_gate(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-run",
                "--skill-a",
                SKILL_A,
                "--skill-b",
                SKILL_B,
                "--fixture",
                FIXTURE,
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

    def test_cli_rejects_non_positive_timeout_before_dispatch(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-run",
                "--skill-a",
                SKILL_A,
                "--skill-b",
                SKILL_B,
                "--fixture",
                "Infrastructure/tests/fixtures/skills_sdk/missing-ab-fixture.json",
                "--timeout-seconds",
                "0",
                "--execute",
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
        self.assertIn("must be >= 1", payload["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
