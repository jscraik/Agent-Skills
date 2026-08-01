from __future__ import annotations

import ast
import json
from copy import deepcopy
import shutil
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_run import CodexRunResult, build_ab_run_receipt  # noqa: E402
from ask.skills_sdk import schema_validation  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_plan_receipt, validate_ab_run_receipt  # noqa: E402
from helpers.schema_validator import _validate_schema_subset  # noqa: E402
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


class TestSkillsSdkAbPlan(unittest.TestCase):
    def test_skills_command_defers_optional_ab_contract_imports(self) -> None:
        """The general ask command must load without the optional Pydantic lane."""
        source_path = REPO_ROOT / "Infrastructure/scripts/lib/ask/commands/skills_impl.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        top_level_imports = [
            node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.module
        ]
        self.assertFalse(
            any(module.startswith("ask.skills_sdk.eval_ab_") for module in top_level_imports),
            "A/B contracts must remain lazy so repo validation does not require Pydantic",
        )

    def _managed_v1_result(self, payload: dict[str, object]) -> schema_validation.SchemaValidationResult:
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/ab-plan-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        return schema_validation.validate_payload_against_schema(
            payload,
            schema,
            {schema_path.name: schema},
            schema_path=schema_path,
            payload_source="ab-plan-receipt.v1.fixture",
            truth_lane="schema_contract",
        )

    def test_v1_fixture_passes_managed_schema_validator(self) -> None:
        payload = json.loads(
            (REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.v1.json").read_text(
                encoding="utf-8"
            )
        )
        result = self._managed_v1_result(payload)
        self.assertEqual(result.status, "pass", result.diagnostics)

    def test_v1_schema_rejects_duplicate_command_variant_labels(self) -> None:
        payload = json.loads(
            (REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.v1.json").read_text(
                encoding="utf-8"
            )
        )
        payload["command_variant_labels"] = ["A", "A"]
        self.assertEqual(self._managed_v1_result(payload).status, "fail")

    def test_managed_v1_validator_rejects_invalid_json_numbers(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.v1.json"
        for invalid_number in (-0.5, float("nan"), float("inf"), float("-inf"), False):
            with self.subTest(invalid_number=invalid_number):
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
                payload["judge_profile"]["model_settings"]["temperature"] = invalid_number
                self.assertEqual(self._managed_v1_result(payload).status, "fail")

    def test_managed_validator_checks_dormant_definitions(self) -> None:
        schema = {
            "$defs": {"unused": {"type": "number", "unsupportedKeyword": True}},
            "type": "object",
        }
        result = schema_validation.validate_payload_against_schema(
            {}, schema, {}, schema_path="inline", payload_source="inline", truth_lane="schema_contract",
        )
        self.assertEqual(result.status, "fail")

    def test_managed_validator_enforces_number_bounds_through_local_ref(self) -> None:
        schema = {
            "$defs": {"value": {"type": "number", "minimum": 0}},
            "$ref": "#/$defs/value",
        }
        result = schema_validation.validate_payload_against_schema(
            -0.5, schema, {}, schema_path="inline", payload_source="inline", truth_lane="schema_contract",
        )
        self.assertEqual(result.status, "fail")

    def test_managed_validator_resolves_local_ref_inside_any_of(self) -> None:
        schema = {
            "$defs": {"value": {"type": "string", "const": "expected"}},
            "anyOf": [{"$ref": "#/$defs/value"}, {"type": "null"}],
        }
        result = schema_validation.validate_payload_against_schema(
            "expected",
            schema,
            {},
            schema_path="inline",
            payload_source="inline",
            truth_lane="schema_contract",
        )
        self.assertEqual(result.status, "pass", result.diagnostics)

    def _assert_v1_schema_valid(self, payload: dict[str, object]) -> None:
        schema = json.loads(
            (
                REPO_ROOT
                / "Infrastructure/config/schemas/skills-sdk/ab-plan-receipt.v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        _validate_schema_subset(schema, payload, {})

    def _assert_v1_schema_invalid(self, payload: dict[str, object]) -> None:
        with self.assertRaises(AssertionError):
            self._assert_v1_schema_valid(payload)

    def _schema_status_guard(self, preflight: dict[str, object]) -> object:
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/ab-plan-receipt.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        guard = schema["$defs"]["AbLanePreflight"]["allOf"][0]
        return schema_validation.validate_payload_against_schema(
            preflight,
            guard,
            {},
            schema_path=schema_path,
            payload_source="planned-preflight-status-probe",
            truth_lane="schema_contract",
        )

    def test_base_v0_fixture_remains_readable_and_new_producer_emits_v1(self) -> None:
        base_fixture = json.loads(
            (REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.json").read_text()
        )
        self.assertEqual(validate_ab_plan_receipt(base_fixture).schema_version, "skills-sdk.ab-plan-receipt.v0")
        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        self.assertEqual(receipt["schema_version"], "skills-sdk.ab-plan-receipt.v1")
        v1_fixture = json.loads(
            (REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.v1.json").read_text()
        )
        self.assertEqual(validate_ab_plan_receipt(v1_fixture).schema_version, "skills-sdk.ab-plan-receipt.v1")

    def test_unknown_version_and_v1_claims_under_v0_are_rejected(self) -> None:
        fixture = json.loads(
            (REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.json").read_text()
        )
        fixture["schema_version"] = "skills-sdk.ab-plan-receipt.v9"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_ab_plan_receipt(fixture)
        fixture["schema_version"] = "skills-sdk.ab-plan-receipt.v0"
        fixture["codex_profile"] = "oss-local"
        with self.assertRaisesRegex(ValueError, "Extra inputs"):
            validate_ab_plan_receipt(fixture)

    def test_typed_preflight_blocker_is_recorded_before_execution(self) -> None:
        def blocked_probe(profile: dict[str, object]) -> dict[str, object]:
            facts = declared_profile_preflight(profile)
            facts["model_catalog"] = {
                **facts["model_catalog"], "status": "blocked",
                "blocker": {"blocker_class": "model_catalog_entry_missing", "reason": "selected model absent"},
            }
            return facts

        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=blocked_probe,
        )
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["runtime_profile_gates"][0]["status"], "blocked")
        self.assertEqual(
            receipt["runtime_profile_gates"][0]["preflight"]["admission"]["blockers"][0]["blocker_class"],
            "model_catalog_entry_missing",
        )
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertEqual(receipt["command_plan"], [])
        self.assertEqual(receipt["command_variant_labels"], [])
        self.assertTrue(
            all(gate["command_plan"] == [] for gate in receipt["runtime_profile_gates"])
        )
        validate_ab_plan_receipt(receipt)
        self._assert_v1_schema_valid(receipt)

    def test_blocked_and_planned_packet_shapes_fail_closed_in_model_and_schema(self) -> None:
        planned = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )

        planned_without_packet = deepcopy(planned)
        planned_without_packet["command_plan"] = []
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(planned_without_packet)
        self._assert_v1_schema_invalid(planned_without_packet)

        blocked = self._blocked_plan(planned)
        validate_ab_plan_receipt(blocked)
        self._assert_v1_schema_valid(blocked)
        blocked_with_packet = deepcopy(blocked)
        blocked_with_packet["runtime_profile_gates"][0]["command_plan"] = deepcopy(
            planned["runtime_profile_gates"][0]["command_plan"]
        )
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(blocked_with_packet)
        self._assert_v1_schema_invalid(blocked_with_packet)

        planned_with_blockers = deepcopy(planned)
        planned_with_blockers["blockers"] = ["contradictory_planned_blocker"]
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(planned_with_blockers)
        self._assert_v1_schema_invalid(planned_with_blockers)

        blocked_without_blockers = self._blocked_plan(planned)
        blocked_without_blockers["blockers"] = []
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(blocked_without_blockers)
        self._assert_v1_schema_invalid(blocked_without_blockers)

    def test_v0_plan_requires_exact_a_and_b_packets(self) -> None:
        fixture_path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["command_plan"][1]["variant_label"] = "A"
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(fixture)

    def _blocked_plan(self, planned: dict[str, object]) -> dict[str, object]:
        blocked = deepcopy(planned)
        blocker = {
            "blocker_class": "preflight_evidence_missing",
            "reason": "permanent packet-shape regression probe",
        }
        blocked.update({
            "status": "blocked", "blockers": ["typed_preflight_blocker"],
            "command_variant_labels": [], "command_plan": [],
        })
        gate = blocked["runtime_profile_gates"][0]
        gate.update({"status": "blocked", "blockers": [blocker]})
        gate["preflight"]["runtime"].update({"status": "blocked", "blocker": blocker})
        gate["preflight"]["admission"].update({"status": "blocked", "blockers": [blocker]})
        for runtime_gate in blocked["runtime_profile_gates"]:
            runtime_gate["command_plan"] = []
        return blocked

    def test_builder_records_codex_command_plan_without_invocation(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        self.assertEqual(receipt["status"], "planned")
        self.assertEqual(receipt["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(receipt["command_variant_labels"], ["A", "B"])
        self.assertEqual({plan["variant_label"] for plan in receipt["command_plan"]}, {"A", "B"})
        self.assertEqual(receipt["codex_profile"], "oss-local")
        self._assert_gate_identities(receipt)
        self._assert_command_argv(receipt)
        self._assert_plan_evidence(receipt)
        validate_ab_plan_receipt(receipt)

    def test_explicit_oss_local_lane_plans_without_cloud_preflight(self) -> None:
        probed_lanes: list[str] = []

        def local_only_probe(profile: dict[str, object]) -> dict[str, object]:
            probed_lanes.append(str(profile["id"]))
            if profile["id"] != "oss-local":
                raise AssertionError("oss-local execution lane must not probe cloud")
            return declared_profile_preflight(profile)

        receipt = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            execution_lane="oss-local",
            preflight_probe=local_only_probe,
        )

        self.assertEqual(receipt["status"], "planned")
        self.assertEqual(receipt["execution_lane"], "oss-local")
        self.assertEqual(probed_lanes, ["oss-local"])
        self.assertEqual(
            [(gate["order"], gate["lane"]) for gate in receipt["runtime_profile_gates"]],
            [(1, "oss-local")],
        )
        self.assertEqual(receipt["command_variant_labels"], ["A", "B"])
        validate_ab_plan_receipt(receipt)
        self.assertEqual(self._managed_v1_result(receipt).status, "pass")

    def test_default_all_lane_still_rejects_a_single_local_gate(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            execution_lane="oss-local",
            preflight_probe=declared_profile_preflight,
        )
        forged = deepcopy(receipt)
        forged.pop("execution_lane")
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(forged)
        self.assertEqual(self._managed_v1_result(forged).status, "fail")

    def test_explicit_oss_local_run_omits_cloud_and_default_all_rejects_one_gate(self) -> None:
        evidence_root = ".harness/test-sdk-ab-plan-local-run"
        shutil.rmtree(REPO_ROOT / evidence_root, ignore_errors=True)
        probed_lanes: list[str] = []
        calls: list[list[str]] = []
        def local_only_probe(profile: dict[str, object]) -> dict[str, object]:
            probed_lanes.append(str(profile["id"]))
            return declared_profile_preflight(profile)
        def local_runner(command_argv: list[str], _prompt: str, root: Path, _timeout: object) -> CodexRunResult:
            calls.append(command_argv)
            output_path = root / command_argv[command_argv.index("--output-last-message") + 1]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("local", encoding="utf-8")
            return CodexRunResult(0, '{"type":"response.completed"}\n', "", command_argv)
        try:
            receipt = build_ab_run_receipt(
                REPO_ROOT,
                skill_a=SKILL_A,
                skill_b=SKILL_B,
                fixture=FIXTURE,
                skill_a_identity=IDENTITY_A,
                skill_b_identity=IDENTITY_B,
                execution_lane="oss-local",
                evidence_root=evidence_root,
                runner=local_runner,
                preflight_probe=local_only_probe,
            )
            self.assertEqual((receipt["status"], receipt["execution_lane"]), ("completed", "oss-local"))
            self.assertEqual((probed_lanes, len(calls)), (["oss-local"], 2))
            self.assertEqual([gate["lane"] for gate in receipt["runtime_profile_gates"]], ["oss-local"])
            validate_ab_run_receipt(receipt)
            run_schema = json.loads((REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/ab-run-receipt.v1.schema.json").read_text())
            self.assertEqual(schema_validation.validate_payload_against_schema(receipt, run_schema, {"ab-run-receipt.v1.schema.json": run_schema}, schema_path="ab-run-receipt.v1.schema.json", payload_source="local-run", truth_lane="schema_contract").status, "pass")

            forged = deepcopy(receipt) | {"execution_lane": "all", "runtime_profile_gates": receipt["runtime_profile_gates"][:1]}
            with self.assertRaises(ValueError):
                validate_ab_run_receipt(forged)
        finally:
            shutil.rmtree(REPO_ROOT / evidence_root, ignore_errors=True)

    def _assert_gate_identities(self, receipt: dict[str, object]) -> None:
        identities = [(gate["order"], gate["lane"], gate["codex_profile"]) for gate in receipt["runtime_profile_gates"]]
        self.assertEqual(identities, [(1, "oss-local", "oss-local"), (2, "oss-cloud", "oss-cloud")])

    def _assert_command_argv(self, receipt: dict[str, object]) -> None:
        first = receipt["command_plan"][0]
        self.assertEqual(first["command_argv"][:8], ["codex", "exec", "--profile", "oss-local", "-c", 'approval_policy="on-request"', "--sandbox", "read-only"])
        self.assertEqual(first["approval_policy"], "on-request")
        self.assertIn("--json", first["command_argv"])
        for gate in receipt["runtime_profile_gates"]:
            for command in gate["command_plan"]:
                argv = command["command_argv"]
                self.assertEqual(argv[argv.index("--profile") + 1], gate["codex_profile"])
                expected = argv if gate["codex_profile"] == "oss-local" else ["op", "run", "--env-file", "<operator-approved-opaque-env-stream>", "--", *argv]
                self.assertEqual(command["execution_argv"], expected)

    def _assert_plan_evidence(self, receipt: dict[str, object]) -> None:
        first = receipt["command_plan"][0]
        self.assertEqual(first["runner_stdout_capture_path"], first["event_log_path"])
        self.assertEqual(first["planned_write_paths"], [first["output_last_message_path"]])
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertTrue(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_validator_rejects_judge_metadata_without_matching_runtime_argv(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        receipt["runtime_profile_gates"][0]["command_plan"][0]["command_argv"][3] = "fast"
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(receipt)

    def test_validator_rejects_direct_cloud_execution_without_op_wrapper(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        cloud_command = receipt["runtime_profile_gates"][1]["command_plan"][0]
        cloud_command["execution_argv"] = list(cloud_command["command_argv"])
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(receipt)
        self._assert_v1_schema_invalid(receipt)

    def test_durable_plan_rejects_path_shaped_cloud_env_references(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        for reference in ("~/.codex/.env", "/tmp/operator/.codex/.env"):
            with self.subTest(reference=reference):
                candidate = deepcopy(receipt)
                candidate["runtime_profile_gates"][1]["command_plan"][0]["execution_argv"][3] = reference
                with self.assertRaises(ValueError):
                    validate_ab_plan_receipt(candidate)
                self._assert_v1_schema_invalid(candidate)

    def test_validator_rejects_missing_or_reordered_runtime_lane(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        forged = deepcopy(receipt)
        for command in forged["runtime_profile_gates"][1]["command_plan"]:
            command["execution_argv"][0] = "evil/op"
        with self.assertRaises(ValueError):
            validate_ab_plan_receipt(forged)
        self._assert_v1_schema_invalid(forged)

        receipt = build_ab_plan_receipt(
            REPO_ROOT, skill_a=SKILL_A, skill_b=SKILL_B, fixture=FIXTURE,
            skill_a_identity=IDENTITY_A, skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        for gates in (receipt["runtime_profile_gates"][1:], list(reversed(receipt["runtime_profile_gates"]))):
            candidate = dict(receipt)
            candidate["runtime_profile_gates"] = gates
            with self.assertRaises(ValueError):
                validate_ab_plan_receipt(candidate)

    def test_planned_v1_requires_pass_for_every_required_preflight_fact(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            preflight_probe=declared_profile_preflight,
        )
        for lane_index in (0, 1):
            for fact_name in ("profile_config", "model_catalog", "runtime", "catalog"):
                with self.subTest(lane=lane_index, fact=fact_name):
                    candidate = deepcopy(receipt)
                    preflight = candidate["runtime_profile_gates"][lane_index]["preflight"]
                    preflight[fact_name]["status"] = "not_applicable"
                    with self.assertRaises(ValueError):
                        validate_ab_plan_receipt(candidate)
                    if fact_name == "runtime":
                        self._assert_v1_schema_invalid(candidate)
                    else:
                        self.assertEqual(self._schema_status_guard(preflight).status, "fail")

    def test_cli_plan_returns_non_executing_receipt(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-plan",
                "--skill-a",
                SKILL_A,
                "--skill-b",
                SKILL_B,
                "--fixture",
                FIXTURE,
                "--preview",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 2, proc.stderr)
        payload = json.loads(proc.stdout)
        receipt = payload["data"]["skills_sdk_eval_ab_plan"]["receipt"]
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(receipt["evidence_root"], ".harness/artifacts/sdk-ab-evals")
        self.assertTrue(receipt["blockers"])
        self.assertFalse(receipt["codex_exec_invoked"])
        validate_ab_plan_receipt(receipt)

    def test_builder_blocks_external_evidence_root(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root="/tmp/sdk-ab-evals",
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("evidence_root_outside_repo", receipt["blockers"])
        self.assertEqual(receipt["command_plan"], [])
        validate_ab_plan_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
