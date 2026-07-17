from __future__ import annotations

import json
import os
from pathlib import Path
from copy import deepcopy
import shutil
import subprocess
import sys
from typing import Callable
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk.eval_ab_run import (  # noqa: E402
    CodexRunResult,
    _codex_runner_env,
    _default_codex_runner,
    build_ab_run_receipt,
)
from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt  # noqa: E402
from ask.skills_sdk import schema_validation  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_plan_receipt, validate_ab_run_receipt  # noqa: E402
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
TestRunner = Callable[[list[str], str, Path, int], CodexRunResult]
PreflightProbe = Callable[[dict[str, object]], dict[str, object]]


def _test_execution_argv(command_argv: list[str]) -> list[str]:
    profile = command_argv[command_argv.index("--profile") + 1]
    if profile == "oss-cloud":
        return ["op", "run", "--env-file", "<operator-approved-opaque-env-stream>", "--", *command_argv]
    return list(command_argv)


def _build_test_ab_run_receipt(
    evidence_root: str,
    runner: TestRunner,
    preflight_probe: PreflightProbe = declared_profile_preflight,
) -> dict[str, object]:
    return build_ab_run_receipt(
        REPO_ROOT,
        skill_a=SKILL_A,
        skill_b=SKILL_B,
        fixture=FIXTURE,
        skill_a_identity=IDENTITY_A,
        skill_b_identity=IDENTITY_B,
        evidence_root=evidence_root,
        runner=runner,
        preflight_probe=preflight_probe,
    )


def _forbidden_test_runner(calls: list[list[str]]) -> TestRunner:
    def runner(argv: list[str], *_args: object) -> CodexRunResult:
        calls.append(argv)
        raise AssertionError("runner must not be invoked for a blocked plan")

    return runner


def _cloud_auth_blocked_probe(profile: dict[str, object]) -> dict[str, object]:
    facts = declared_profile_preflight(profile)
    if profile["id"] == "oss-cloud":
        facts["auth"] = {
            **facts["auth"],
            "status": "blocked",
            "auth_reference": "codex_cli_auth",
            "auth_source": "missing_or_invalid",
            "blocker": {
                "blocker_class": "cloud_auth_unavailable",
                "reason": "typed cloud-only blocker",
            },
        }
        facts["model_catalog"] = {
            **facts["model_catalog"],
            "status": "blocked",
            "network_accessed": False,
            "http_status": None,
            "catalog_digest": None,
            "matched_model": None,
            "blocker": {
                "blocker_class": "cloud_catalog_unavailable",
                "reason": "cloud catalog probe requires authenticated preflight",
            },
        }
    return facts


def _local_runtime_blocked_probe(profile: dict[str, object]) -> dict[str, object]:
    facts = declared_profile_preflight(profile)
    if profile["id"] == "oss-local":
        facts["runtime"] = {
            **facts["runtime"],
            "status": "blocked",
            "blocker": {
                "blocker_class": "local_runtime_unavailable",
                "reason": "typed local-only blocker",
            },
        }
    return facts


class TestSkillsSdkAbRun(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_root = ".harness/test-sdk-ab-run"
        shutil.rmtree(REPO_ROOT / self.evidence_root, ignore_errors=True)

    def tearDown(self) -> None:
        shutil.rmtree(REPO_ROOT / self.evidence_root, ignore_errors=True)

    def _schema_status_guard(self, preflight: dict[str, object]) -> object:
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/ab-run-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        guard = schema["$defs"]["AbLanePreflight"]["allOf"][0]
        return schema_validation.validate_payload_against_schema(
            preflight,
            guard,
            {},
            schema_path=schema_path,
            payload_source="completed-preflight-status-probe",
            truth_lane="schema_contract",
        )

    def _full_v1_schema_result(self, receipt: dict[str, object]) -> object:
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/ab-run-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        return schema_validation.validate_payload_against_schema(
            receipt,
            schema,
            {},
            schema_path=schema_path,
            payload_source="full-ab-run-v1-regression",
            truth_lane="schema_contract",
        )

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
    def test_default_cloud_runner_executes_only_through_opaque_op_boundary(self) -> None:
        captured: list[list[str]] = []

        def fake_run(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            captured.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout='{"type":"item.completed","item":{"type":"agent_message"}}\n', stderr="")

        command = [
            "codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request",
            "--sandbox", "read-only", "--json", "-",
        ]
        with (
            patch("ask.skills_sdk.eval_ab_run.subprocess.run", side_effect=fake_run),
            patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": "~/.codex/.env"}),
        ):
            result = _default_codex_runner(command, "prompt", REPO_ROOT, 1)

        self.assertEqual(captured[0][:5], ["op", "run", "--env-file", "~/.codex/.env", "--"])
        self.assertEqual(captured[0][5:], command)
        self.assertEqual(result.executed_argv, captured[0])
    def test_provider_event_absence_is_a_typed_variant_blocker(self) -> None:
        def no_provider_event_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object,
        ) -> CodexRunResult:
            return CodexRunResult(exit_code=0, stdout='{"type":"thread.started"}\n', stderr="", executed_argv=_test_execution_argv(command_argv))

        receipt = _build_test_ab_run_receipt(self.evidence_root, no_provider_event_runner)
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("A:provider_event_missing", receipt["blockers"])
        self.assertIn("B:provider_event_missing", receipt["blockers"])
        validate_ab_run_receipt(receipt)

    def test_local_success_is_preserved_when_cloud_gate_blocks(self) -> None:
        def local_then_cloud_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object,
        ) -> CodexRunResult:
            profile = command_argv[command_argv.index("--profile") + 1]
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            if profile == "oss-local":
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text("local response", encoding="utf-8")
                return CodexRunResult(
                    exit_code=0,
                    stdout='{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n',
                    stderr="",
                    executed_argv=_test_execution_argv(command_argv),
                )
            return CodexRunResult(exit_code=2, stdout="", stderr="cloud blocked", executed_argv=_test_execution_argv(command_argv))

        receipt = _build_test_ab_run_receipt(self.evidence_root, local_then_cloud_runner)
        local_gate, cloud_gate = receipt["runtime_profile_gates"]
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(local_gate["status"], "completed")
        self.assertEqual(cloud_gate["status"], "blocked")
        self.assertEqual(receipt["variant_results"], local_gate["variant_results"])
        validate_ab_run_receipt(receipt)

    def test_v0_and_v1_run_fixtures_are_readable_under_own_semantics(self) -> None:
        fixture_root = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid"
        v0 = json.loads((fixture_root / "ab-run-receipt.json").read_text())
        v1 = json.loads((fixture_root / "ab-run-receipt.v1.json").read_text())
        self.assertEqual(validate_ab_run_receipt(v0).schema_version, "skills-sdk.ab-run-receipt.v0")
        self.assertEqual(validate_ab_run_receipt(v1).schema_version, "skills-sdk.ab-run-receipt.v1")

    def test_v0_run_requires_exact_a_and_b_commands_and_results(self) -> None:
        fixture_root = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid"
        fixture = json.loads((fixture_root / "ab-run-receipt.json").read_text())
        fixture["command_plan"][1]["variant_label"] = "A"
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(fixture)

        fixture = json.loads((fixture_root / "ab-run-receipt.json").read_text())
        fixture["variant_results"][1]["variant_label"] = "A"
        with self.assertRaises(ValueError):
            validate_ab_run_receipt(fixture)

    def test_v1_reader_rejects_claimed_profile_not_proven_by_executed_argv(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        fixture = json.loads(fixture_path.read_text())
        variants: dict[str, list[str]] = {
            "substituted": ["codex", "exec", "--profile", "fast"],
            "omitted": ["codex", "exec", "--sandbox", "read-only"],
            "duplicated": ["codex", "exec", "--profile", "oss-local", "--profile", "oss-local"],
            "misplaced": ["codex", "--profile", "oss-local", "exec"],
        }
        for label, prefix in variants.items():
            with self.subTest(label=label):
                candidate = deepcopy(fixture)
                result = candidate["runtime_profile_gates"][0]["variant_results"][0]
                suffix = result["command_argv"][4:]
                result["command_argv"] = prefix + suffix
                with self.assertRaises(ValueError):
                    validate_ab_run_receipt(candidate)

    def test_completed_v1_requires_pass_for_every_required_preflight_fact(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        for lane_index in (0, 1):
            for fact_name in ("profile_config", "model_catalog", "runtime", "catalog"):
                with self.subTest(lane=lane_index, fact=fact_name):
                    candidate = deepcopy(fixture)
                    preflight = candidate["runtime_profile_gates"][lane_index]["preflight"]
                    preflight[fact_name]["status"] = "not_applicable"
                    with self.assertRaises(ValueError):
                        validate_ab_run_receipt(candidate)
                    if fact_name == "runtime":
                        self.assertEqual(self._full_v1_schema_result(candidate).status, "fail")
                    else:
                        self.assertEqual(self._schema_status_guard(preflight).status, "fail")

    def test_preflight_blocker_prevents_runner_invocation_and_redacts_auth(self) -> None:
        calls: list[list[str]] = []

        def runner(argv: list[str], prompt: str, root: Path, timeout: int) -> CodexRunResult:
            calls.append(argv)
            raise AssertionError("runner must not be invoked")

        def blocked_probe(profile: dict[str, object]) -> dict[str, object]:
            facts = declared_profile_preflight(profile)
            blocker_class = "local_runtime_unavailable" if profile["id"] == "oss-local" else "cloud_auth_unavailable"
            facts["runtime"] = {
                **facts["runtime"], "status": "blocked",
                "blocker": {"blocker_class": blocker_class, "reason": "typed test blocker"},
            }
            return facts

        receipt = build_ab_run_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root, runner=runner, preflight_probe=blocked_probe,
        )
        self.assertEqual(calls, [])
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["runtime_profile_gates"][0]["status"], "blocked")
        self.assertEqual(receipt["runtime_profile_gates"][1]["status"], "blocked")
        self.assertEqual(receipt["command_plan"], [])
        self.assertEqual(receipt["command_variant_labels"], [])
        self.assertFalse((REPO_ROOT / self.evidence_root).exists())
        self.assertNotIn("test-secret-value", json.dumps(receipt))
        validate_ab_run_receipt(receipt)

    def test_cloud_only_preflight_block_builds_canonical_non_executing_run_receipt(self) -> None:
        calls: list[list[str]] = []
        receipt = _build_test_ab_run_receipt(
            self.evidence_root,
            _forbidden_test_runner(calls),
            _cloud_auth_blocked_probe,
        )

        local_gate, cloud_gate = receipt["runtime_profile_gates"]
        self.assertEqual(calls, [])
        self.assertFalse((REPO_ROOT / self.evidence_root).exists())
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["command_plan"], [])
        self.assertEqual(receipt["variant_results"], [])
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])
        self.assertEqual(local_gate["status"], "not_run_with_reason")
        self.assertEqual(local_gate["blockers"], ["execution_packet_suppressed_by_blocked_plan"])
        self.assertEqual(local_gate["variant_results"], [])
        self.assertEqual(cloud_gate["status"], "blocked")
        self.assertEqual(cloud_gate["blockers"], cloud_gate["preflight"]["admission"]["blockers"])
        self.assertIn(
            "cloud_auth_unavailable",
            {blocker["blocker_class"] for blocker in cloud_gate["blockers"]},
        )
        self.assertEqual(cloud_gate["variant_results"], [])
        validate_ab_run_receipt(receipt)

    def test_local_only_preflight_block_builds_canonical_non_executing_run_receipt(self) -> None:
        calls: list[list[str]] = []
        receipt = _build_test_ab_run_receipt(
            self.evidence_root,
            _forbidden_test_runner(calls),
            _local_runtime_blocked_probe,
        )

        local_gate, cloud_gate = receipt["runtime_profile_gates"]
        self.assertEqual(calls, [])
        self.assertFalse((REPO_ROOT / self.evidence_root).exists())
        self.assertEqual(local_gate["status"], "blocked")
        self.assertEqual(local_gate["blockers"], local_gate["preflight"]["admission"]["blockers"])
        self.assertEqual(local_gate["blockers"][0]["blocker_class"], "local_runtime_unavailable")
        self.assertEqual(local_gate["variant_results"], [])
        self.assertEqual(cloud_gate["status"], "not_run_with_reason")
        self.assertEqual(cloud_gate["blockers"], ["execution_packet_suppressed_by_blocked_plan"])
        self.assertEqual(cloud_gate["variant_results"], [])
        validate_ab_run_receipt(receipt)

    def test_non_preflight_blocked_plan_marks_both_empty_gates_not_run(self) -> None:
        plan = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            preflight_probe=declared_profile_preflight,
        )
        plan["status"] = "blocked"
        plan["blockers"] = ["external_plan_policy_blocked"]
        plan["command_variant_labels"] = []
        plan["command_plan"] = []
        for gate in plan["runtime_profile_gates"]:
            gate["command_plan"] = []
        validate_ab_plan_receipt(plan)
        calls: list[list[str]] = []

        def forbidden_runner(argv: list[str], *_args: object) -> CodexRunResult:
            calls.append(argv)
            raise AssertionError("runner must not be invoked for a blocked plan")

        with patch("ask.skills_sdk.eval_ab_run._build_plan", return_value=plan):
            receipt = _build_test_ab_run_receipt(self.evidence_root, forbidden_runner)

        self.assertEqual(calls, [])
        self.assertFalse((REPO_ROOT / self.evidence_root).exists())
        self.assertEqual(
            [gate["status"] for gate in receipt["runtime_profile_gates"]],
            ["not_run_with_reason", "not_run_with_reason"],
        )
        self.assertTrue(
            all(gate["blockers"] == ["execution_packet_suppressed_by_blocked_plan"] for gate in receipt["runtime_profile_gates"])
        )
        self.assertTrue(all(gate["variant_results"] == [] for gate in receipt["runtime_profile_gates"]))
        validate_ab_run_receipt(receipt)

    def test_pre_execution_plan_blocker_without_runtime_gates_is_valid(self) -> None:
        receipt = build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture="Infrastructure/tests/fixtures/skills_sdk/missing-deterministic-fixture.json",
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=_forbidden_test_runner([]),
            preflight_probe=declared_profile_preflight,
        )
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["runtime_profile_gates"], [])
        self.assertTrue(receipt["blockers"])
        validate_ab_run_receipt(receipt)

    def test_builder_executes_with_injected_runner_and_records_evidence(self) -> None:
        calls: list[list[str]] = []

        def fake_runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int) -> CodexRunResult:
            calls.append(command_argv)
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"variant": len(calls), "prompt_digest_input": prompt[:24]}), encoding="utf-8")
            return CodexRunResult(
                exit_code=0,
                stdout='{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n',
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = build_ab_run_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root, runner=fake_runner,
            preflight_probe=declared_profile_preflight,
        )
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["command_variant_labels"], ["A", "B"])
        self.assertEqual({result["variant_label"] for result in receipt["variant_results"]}, {"A", "B"})
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(receipt["network_accessed"])
        self.assertTrue(receipt["provider_invoked"])
        self.assertFalse(receipt["judge_provider_invoked"])
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertEqual(len(calls), 4)
        self.assertEqual([gate["lane"] for gate in receipt["runtime_profile_gates"]], ["oss-local", "oss-cloud"])
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
                return CodexRunResult(exit_code=0, stdout='{"event":"done"}\n', stderr="", executed_argv=_test_execution_argv(command_argv))
            return CodexRunResult(exit_code=2, stdout="", stderr="boom", executed_argv=_test_execution_argv(command_argv))

        receipt = build_ab_run_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root=self.evidence_root,
            runner=fake_runner,
            preflight_probe=declared_profile_preflight,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("B:codex_exec_exit_2", receipt["blockers"])
        self.assertIn("B:output_last_message_missing", receipt["blockers"])
        self.assertFalse(receipt["judge_provider_invoked"])
        validate_ab_run_receipt(receipt)

    def test_builder_records_parse_failure_without_provider_or_network_claim(self) -> None:
        def parse_failure_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object
        ) -> CodexRunResult:
            return CodexRunResult(
                exit_code=2,
                stdout="",
                stderr="error: unexpected argument '--ask-for-approval' found",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = _build_test_ab_run_receipt(self.evidence_root, parse_failure_runner)

        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        validate_ab_run_receipt(receipt)

    def test_builder_records_app_server_initialization_failure_without_provider_claim(self) -> None:
        def initialization_failure_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object
        ) -> CodexRunResult:
            return CodexRunResult(
                exit_code=1,
                stdout='{"type":"thread.started","thread_id":"fixture"}\n',
                stderr="failed to initialize in-process app-server client: Operation not permitted",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = _build_test_ab_run_receipt(self.evidence_root, initialization_failure_runner)

        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        self.assertEqual(receipt["runtime_profile_gates"][0]["status"], "blocked")
        self.assertEqual(receipt["runtime_profile_gates"][1]["status"], "not_run_with_reason")
        self.assertEqual(receipt["runtime_profile_gates"][1]["variant_results"], [])
        validate_ab_run_receipt(receipt)

    def test_error_and_metadata_items_do_not_prove_provider_invocation(self) -> None:
        event_streams = (
            '{"type":"item.completed","item":{"type":"error","message":"failed"}}\n',
            '{"type":"item.completed","item":{"type":"metadata","name":"usage"}}\n',
            '{"type":"item.completed"}\n',
            'not-json\n',
        )
        for stdout in event_streams:
            with self.subTest(stdout=stdout):
                def runner(command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object) -> CodexRunResult:
                    return CodexRunResult(exit_code=1, stdout=stdout, stderr="blocked", executed_argv=_test_execution_argv(command_argv))

                receipt = _build_test_ab_run_receipt(self.evidence_root, runner)
                self.assertFalse(receipt["provider_invoked"])
                self.assertTrue(receipt["network_accessed"])
                validate_ab_run_receipt(receipt)

    def test_builder_records_successful_observable_codex_execution(self) -> None:
        def successful_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object
        ) -> CodexRunResult:
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("observable response", encoding="utf-8")
            return CodexRunResult(
                exit_code=0,
                stdout='{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n',
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = _build_test_ab_run_receipt(self.evidence_root, successful_runner)

        self.assertEqual(receipt["status"], "completed")
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        validate_ab_run_receipt(receipt)

    def test_mixed_provider_evidence_blocks_non_proving_variant(self) -> None:
        def mixed_evidence_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object
        ) -> CodexRunResult:
            output_path = repo_root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("sanitized response", encoding="utf-8")
            is_variant_a = output_path.as_posix().endswith("/A/last-message.json")
            stdout = (
                '{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n'
                if is_variant_a
                else '{"type":"item.completed","item":{"type":"metadata","name":"usage"}}\n'
            )
            return CodexRunResult(
                exit_code=0,
                stdout=stdout,
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = _build_test_ab_run_receipt(self.evidence_root, mixed_evidence_runner)

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("B:provider_event_missing", receipt["blockers"])
        self.assertEqual(receipt["runtime_profile_gates"][0]["status"], "blocked")
        self.assertEqual(receipt["runtime_profile_gates"][1]["status"], "not_run_with_reason")
        validate_ab_run_receipt(receipt)

    def test_builder_preserves_provider_claim_for_nonzero_post_invocation_failure(self) -> None:
        def post_invocation_failure_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object
        ) -> CodexRunResult:
            return CodexRunResult(
                exit_code=1,
                stdout='{"type":"response.completed"}\n{"type":"error","message":"provider stream failed"}\n',
                stderr="provider stream failed",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = _build_test_ab_run_receipt(self.evidence_root, post_invocation_failure_runner)

        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        validate_ab_run_receipt(receipt)

    def test_builder_preserves_provider_claim_when_last_message_is_missing(self) -> None:
        def missing_last_message_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: object
        ) -> CodexRunResult:
            return CodexRunResult(
                exit_code=0,
                stdout='{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n',
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

        receipt = _build_test_ab_run_receipt(self.evidence_root, missing_last_message_runner)

        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["codex_exec_invoked"])
        self.assertTrue(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        self.assertIn("A:output_last_message_missing", receipt["blockers"])
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
            preflight_probe=declared_profile_preflight,
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
            return CodexRunResult(
                exit_code=0,
                stdout='{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n',
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

        first_receipt = _build_test_ab_run_receipt(self.evidence_root, successful_runner)
        self.assertEqual(first_receipt["status"], "completed")

        def missing_output_runner(
            command_argv: list[str], prompt: str, repo_root: Path, timeout_seconds: int
        ) -> CodexRunResult:
            return CodexRunResult(
                exit_code=0,
                stdout='{"type":"item.completed","item":{"type":"agent_message","text":"ok"}}\n',
                stderr="",
                executed_argv=_test_execution_argv(command_argv),
            )

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
            preflight_probe=declared_profile_preflight,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("A:codex_exec_unavailable", receipt["blockers"])
        self.assertIn("B:codex_exec_unavailable", receipt["blockers"])
        self.assertTrue(receipt["mutation_performed"])
        self.assertTrue(receipt["network_accessed"])
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
