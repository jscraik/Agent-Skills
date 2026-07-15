from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt  # noqa: E402
from ask.skills_sdk import schema_validation  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_plan_receipt  # noqa: E402
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

    def _assert_gate_identities(self, receipt: dict[str, object]) -> None:
        identities = [(gate["order"], gate["lane"], gate["codex_profile"]) for gate in receipt["runtime_profile_gates"]]
        self.assertEqual(identities, [(1, "oss-local", "oss-local"), (2, "oss-cloud", "oss-cloud")])

    def _assert_command_argv(self, receipt: dict[str, object]) -> None:
        first = receipt["command_plan"][0]
        self.assertEqual(first["command_argv"][:8], ["codex", "exec", "--profile", "oss-local", "--ask-for-approval", "on-request", "--sandbox", "read-only"])
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

    def test_validator_rejects_missing_or_reordered_runtime_lane(self) -> None:
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
