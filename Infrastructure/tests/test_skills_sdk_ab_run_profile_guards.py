from __future__ import annotations

import json
from copy import deepcopy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk import schema_validation  # noqa: E402
from ask.skills_sdk.ab_transport_contracts import opaque_env_identity_digest  # noqa: E402
from ask.skills_sdk.eval_ab_run import (  # noqa: E402
    CodexRunResult,
    _default_codex_runner,
    _execute_variant,
    build_ab_run_receipt,
)
from ask.skills_sdk.eval_ab_preflight import _cloud_catalog_fact  # noqa: E402
from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_run_receipt  # noqa: E402
from skills_sdk_preflight_fixtures import declared_profile_preflight  # noqa: E402


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


def _test_execution_argv(command_argv: list[str]) -> list[str]:
    profile = command_argv[command_argv.index("--profile") + 1]
    if profile == "oss-cloud":
        return ["op", "run", "--env-file", "<operator-approved-opaque-env-stream>", "--", *command_argv]
    return list(command_argv)


class TestSkillsSdkAbRunProfileGuards(unittest.TestCase):
    evidence_root = ".harness/test-sdk-ab-run-profile-guards"

    def setUp(self) -> None:
        shutil.rmtree(REPO_ROOT / self.evidence_root, ignore_errors=True)

    def tearDown(self) -> None:
        shutil.rmtree(REPO_ROOT / self.evidence_root, ignore_errors=True)

    def _receipt(self, runner):
        return build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=runner,
            preflight_probe=declared_profile_preflight,
        )

    def _schema_result(self, receipt: dict[str, object]):
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/ab-run-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        return schema_validation.validate_payload_against_schema(
            receipt,
            schema,
            {},
            schema_path=schema_path,
            payload_source="ab-run-profile-guard-regression",
            truth_lane="schema_contract",
        )

    def test_missing_executed_argv_blocks_without_claiming_a_runtime_profile(self) -> None:
        def missing_argv_runner(command_argv, prompt, repo_root, timeout_seconds):
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("response without runner argv", encoding="utf-8")
            return CodexRunResult(exit_code=0, stdout='{"type":"response.completed"}\n', stderr="")

        receipt = self._receipt(missing_argv_runner)
        result = receipt["runtime_profile_gates"][0]["variant_results"][0]
        self.assertEqual(receipt["status"], "blocked")
        self.assertIsNone(result["codex_profile"])
        self.assertIsNone(result["execution_argv"])
        self.assertIn("A:executed_argv_missing", receipt["blockers"])
        validate_ab_run_receipt(receipt)

    def test_malformed_short_cloud_argv_becomes_typed_blocker(self) -> None:
        def malformed_cloud_runner(command_argv, prompt, repo_root, timeout_seconds):
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("sanitized response", encoding="utf-8")
            if command_argv[command_argv.index("--profile") + 1] == "oss-cloud":
                return CodexRunResult(
                    exit_code=0,
                    stdout='{"type":"response.completed"}\n',
                    stderr="",
                    executed_argv=["op", "run", "--env-file"],
                )
            return CodexRunResult(
                exit_code=0,
                stdout='{"type":"response.completed"}\n',
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = self._receipt(malformed_cloud_runner)
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("A:execution_argv_invalid", receipt["blockers"])
        self.assertIn("A:executed_argv_missing", receipt["blockers"])
        validate_ab_run_receipt(receipt)

    def test_v1_schema_requires_executed_argv_for_pass_and_rejects_profile_tampering(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        fixture = json.loads(fixture_path.read_text())
        result = fixture["runtime_profile_gates"][0]["variant_results"][0]

        missing = deepcopy(fixture)
        missing["runtime_profile_gates"][0]["variant_results"][0].pop("execution_argv")
        self.assertEqual(self._schema_result(missing).status, "fail")

        substituted = deepcopy(fixture)
        substituted["runtime_profile_gates"][0]["variant_results"][0]["execution_argv"][3] = "fast"
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(substituted)
        self.assertEqual(self._schema_result(substituted).status, "fail")

        duplicated = deepcopy(fixture)
        duplicated["runtime_profile_gates"][0]["variant_results"][0]["execution_argv"] = (
            list(result["execution_argv"][:4]) + ["--profile", "oss-local"] + list(result["execution_argv"][4:])
        )
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(duplicated)
        self.assertEqual(self._schema_result(duplicated).status, "fail")

        unbound = deepcopy(fixture)
        unbound["runtime_profile_gates"][0]["variant_results"][0]["codex_profile"] = None
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(unbound)
        self.assertEqual(self._schema_result(unbound).status, "fail")

    def test_schema_rejects_completed_cloud_after_blocked_local(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        candidate = json.loads(fixture_path.read_text())
        local_gate, cloud_gate = candidate["runtime_profile_gates"]
        candidate.update({"status": "blocked", "blockers": ["oss-local:typed_blocker"]})
        local_gate.update({"status": "blocked", "blockers": ["oss-local:typed_blocker"]})
        cloud_gate.update({"status": "completed", "blockers": []})
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)
        self.assertEqual(self._schema_result(candidate).status, "fail")

    def test_validator_rejects_direct_or_regular_cloud_credential_paths(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        candidate = json.loads(fixture_path.read_text())
        cloud_command = candidate["runtime_profile_gates"][1]["command_plan"][0]
        cloud_command["execution_argv"][3] = "/tmp/regular-credential-file"
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)
        self.assertEqual(self._schema_result(candidate).status, "fail")

        with tempfile.TemporaryDirectory() as directory:
            env_dir = Path(directory) / ".codex"
            env_dir.mkdir()
            env_file = env_dir / ".env"
            env_file.write_text("opaque reference only", encoding="utf-8")
            candidate["runtime_profile_gates"][1]["command_plan"][0]["execution_argv"][3] = str(env_file)
            with self.assertRaises(ValueError):
                validate_ab_run_receipt(candidate)
            self.assertEqual(self._schema_result(candidate).status, "fail")

        candidate["runtime_profile_gates"][1]["command_plan"][0]["execution_argv"][3] = "~/.codex/.env"
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)
        self.assertEqual(self._schema_result(candidate).status, "fail")

    def test_execute_variant_rejects_external_evidence_paths_before_runner_starts(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        candidate = json.loads(fixture_path.read_text())
        for gate in candidate["runtime_profile_gates"]:
            if gate["lane"] != "oss-cloud":
                continue
            for packet in (*gate["command_plan"], *gate["variant_results"]):
                packet["execution_argv"][0] = "evil/op"
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)
        self.assertEqual(self._schema_result(candidate).status, "fail")

        calls: list[list[str]] = []

        def fake_runner(command_argv, prompt, repo_root, timeout):
            calls.append(command_argv)
            return CodexRunResult(exit_code=0, stdout="", stderr="", executed_argv=_test_execution_argv(command_argv))

        base_plan = {
            "variant_label": "A", "command_argv": ["codex", "exec", "--output-last-message", "unused"],
            "sandbox_mode": "read-only", "runner_prompt_input_path": f"{self.evidence_root}/A/prompt.txt",
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
                    _execute_variant(REPO_ROOT, command_plan=command_plan, prompt="prompt", timeout_seconds=1, runner=fake_runner)
        self.assertEqual(calls, [])

    def test_run_blocks_before_subprocess_when_runtime_profile_argv_is_mismatched(self) -> None:
        plan = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root, preflight_probe=declared_profile_preflight,
        )
        plan["runtime_profile_gates"][0]["command_plan"][0]["command_argv"][3] = "fast"
        calls: list[list[str]] = []

        def runner(command_argv, prompt, repo_root, timeout):
            calls.append(command_argv)
            return CodexRunResult(0, "", "", executed_argv=_test_execution_argv(command_argv))

        with patch("ask.skills_sdk.eval_ab_run._build_plan", return_value=plan), self.assertRaises(ValueError):
            self._receipt(runner)
        self.assertEqual(calls, [])

    def test_run_rejects_tampered_preflight_before_filesystem_or_runner(self) -> None:
        plan = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root, preflight_probe=declared_profile_preflight,
        )
        plan["runtime_profile_gates"][0]["preflight"]["runtime"].update({"status": "not_applicable", "blocker": None})
        calls: list[list[str]] = []

        def forbidden_runner(command_argv, prompt, repo_root, timeout):
            calls.append(command_argv)
            raise AssertionError("runner reached with a canonically invalid v1 plan")

        with patch("ask.skills_sdk.eval_ab_run._build_plan", return_value=plan), self.assertRaises(ValueError):
            self._receipt(forbidden_runner)
        self.assertEqual(calls, [])
        self.assertFalse((REPO_ROOT / self.evidence_root).exists())

    def test_v1_schema_rejects_completed_receipts_without_side_effects(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        for field in ("mutation_performed", "provider_invoked", "network_accessed"):
            candidate = json.loads(fixture_path.read_text())
            candidate[field] = False
            self.assertEqual(self._schema_result(candidate).status, "fail", field)

    def test_v1_schema_rejects_duplicate_labels_and_failed_completed_variants(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        duplicated = json.loads(fixture_path.read_text())
        duplicated["command_variant_labels"] = ["A", "A"]
        self.assertEqual(self._schema_result(duplicated).status, "fail")

        failed = json.loads(fixture_path.read_text())
        failed["variant_results"][0].update({"status": "blocked", "exit_code": 1, "blockers": ["failed"]})
        self.assertEqual(self._schema_result(failed).status, "fail")

    def test_v1_schema_allows_zero_gate_blocked_receipt(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        blocked = json.loads(fixture_path.read_text())
        blocked.update({"status": "blocked", "blockers": ["plan_blocked"], "runtime_profile_gates": [], "command_plan": [], "variant_results": []})
        self.assertEqual(self._schema_result(blocked).status, "pass")

    def test_v1_schema_rejects_blocked_receipt_when_all_gates_completed(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        blocked = json.loads(fixture_path.read_text())
        blocked.update({"status": "blocked", "blockers": ["contradictory_status"]})
        self.assertEqual(self._schema_result(blocked).status, "fail")

        blocked["blockers"] = []
        self.assertEqual(self._schema_result(blocked).status, "fail")

    def test_v1_schema_rejects_passing_preflight_with_blockers(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        candidate = json.loads(fixture_path.read_text())
        preflight = candidate["runtime_profile_gates"][0]["preflight"]
        preflight["admission"]["blockers"] = [{"blocker_class": "preflight_evidence_missing", "reason": "contradictory"}]
        self.assertEqual(self._schema_result(candidate).status, "fail")

    def test_cloud_catalog_probe_failure_preserves_network_attempt(self) -> None:
        approved = {"status": "pass", "auth_source": "op_fifo", "auth_reference": "codex_cli_auth", "secret_value_observed": False}
        with patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"):
            fact = _cloud_catalog_fact(
                "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), approved,
                lambda _command: (_ for _ in ()).throw(subprocess.TimeoutExpired(["op", "run"], 1)),
            )
        self.assertEqual(fact["status"], "blocked")
        self.assertTrue(fact["network_accessed"])
        self.assertIn("timeout", fact["blocker"]["reason"])


    def test_default_cloud_runner_blocks_same_path_fifo_replacement(self) -> None:
        captured: list[list[str]] = []

        def forbidden_run(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            captured.append(argv)
            raise AssertionError("subprocess must not receive a replacement auth stream")

        command = [
            "codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request",
            "--sandbox", "read-only", "--json", "-",
        ]
        with tempfile.TemporaryDirectory() as directory:
            env_dir = Path(directory) / ".codex"
            env_dir.mkdir()
            env_file = env_dir / ".env"
            os.mkfifo(env_file)
            original_identity = opaque_env_identity_digest(env_file)
            env_file.unlink()
            os.mkfifo(env_file)
            with (
                patch("ask.skills_sdk.eval_ab_run.subprocess.run", side_effect=forbidden_run),
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}),
                patch("ask.skills_sdk.ab_transport_contracts.Path.home", return_value=Path(directory)),
            ):
                with self.assertRaisesRegex(ValueError, "identity changed"):
                    _default_codex_runner(
                        command, "prompt", REPO_ROOT, 1,
                        expected_auth_stream_identity=original_identity,
                    )

        self.assertEqual(captured, [])
