import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills_impl import (  # noqa: E402
    _doctor_sdk_layer_for,
    _skill_doctor_next_command,
    skills_doctor,
)
from ask.envelope import CallResult, ErrorObject  # noqa: E402


def _proof_result(handle: str, status: str = "pass") -> CallResult:
    result = CallResult(status="success" if status == "pass" else "error")
    result.data["proof"] = {
        "schema_version": "command-handle-proof.v1",
        "handle": handle,
        "status": status,
        "gates": {
            "resolver": status == "pass",
            "generated_command_handle_check": status == "pass",
            "workspace_command_handle_exists": status == "pass",
            "codex_user_link": status == "pass",
            "codex_user_command_handle_exists": status == "pass",
        },
    }
    if status != "pass":
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="proof failed"))
    return result


def _audit_result(status: str = "success") -> CallResult:
    result = CallResult(status=status)
    result.data["diagnostics"] = {"exit_code": 0 if status == "success" else 1}
    if status != "success":
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="audit failed"))
    return result


def _assert_consumer_usable_schema_refs(test_case: unittest.TestCase, schemas: dict[str, dict[str, str]]) -> None:
    for schema_name in ("doctor", "events", "lifecycle_event", "profiles", "package", "memory"):
        with test_case.subTest(schema_name=schema_name):
            schema_ref = schemas[schema_name]
            test_case.assertEqual(schema_ref["name"], schema_name)
            test_case.assertTrue(schema_ref["version"].endswith(".v1"))
            test_case.assertEqual(schema_ref["owner"], "Agent Skills Kit")
            test_case.assertIn(schema_ref["stability"], {"experimental", "stable"})
            test_case.assertTrue(schema_ref.get("path") or schema_ref.get("missing_schema_reason"))


class TestAskSkillsDoctor(unittest.TestCase):
    def test_doctor_reports_warning_for_reachable_skill_with_package_gaps(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
            "command_handle_path": ".agents/skills/autofix/SKILL.md",
        }

        with (
            patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            patch("ask.commands.skills_impl.skills_proof", return_value=_proof_result("autofix")),
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=["agent-ops/autofix"]),
        ):
            result = skills_doctor(REPO_ROOT, "autofix")

        self.assertEqual(result.status, "success")
        doctor = result.data["skill_doctor"]
        self.assertEqual(doctor["schema_version"], "skill-doctor.v1")
        self.assertEqual(doctor["status"], "warning")
        self.assertEqual(doctor["handle"], "autofix")
        self.assertEqual(doctor["checks"]["resolver"]["status"], "pass")
        self.assertEqual(doctor["checks"]["runtime_reachability"]["status"], "pass")
        self.assertEqual(doctor["checks"]["structural_audit"]["status"], "pass")
        self.assertEqual(doctor["checks"]["outcome_proof"]["status"], "available_not_run")
        self.assertEqual(doctor["checks"]["resolver"]["sdk_layer"], "Catalog")
        self.assertEqual(doctor["checks"]["runtime_reachability"]["sdk_layer"], "Runtime Adapters")
        self.assertEqual(doctor["checks"]["structural_audit"]["sdk_layer"], "Validation")
        self.assertEqual(doctor["checks"]["package_readiness"]["sdk_layer"], "Packaging")
        self.assertIn(
            "capability_contract_incomplete",
            [warning["class"] for warning in doctor["warnings"]],
        )
        self.assertEqual(doctor["checks"]["outcome_proof"]["sdk_layer"], "Evidence")
        _assert_consumer_usable_schema_refs(self, doctor["contract_schemas"])
        self.assertEqual(doctor["contract_schema_versions"]["doctor"], "skill-doctor.v1")
        self.assertIn("blocked_user_input", doctor["readiness_taxonomy"]["blockers"])
        self.assertIn("timeout_no_output", doctor["readiness_taxonomy"]["blockers"])
        self.assertIn("strict_audit_not_run", doctor["readiness_taxonomy"]["warnings"])
        self.assertEqual(doctor["lifecycle_event"]["schema_version"], "capability-lifecycle-event.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_type"], "skill_doctor_completed")
        self.assertIn("eval_blocked", doctor["lifecycle_event_types"])
        self.assertEqual(len(doctor["warnings"]), 1)

    def test_doctor_blocks_when_runtime_reachability_fails(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
            "command_handle_path": ".agents/skills/autofix/SKILL.md",
        }

        with (
            patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            patch("ask.commands.skills_impl.skills_proof", return_value=_proof_result("autofix", status="fail")),
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=[]),
        ):
            result = skills_doctor(REPO_ROOT, "autofix")

        self.assertEqual(result.status, "error")
        doctor = result.data["skill_doctor"]
        self.assertEqual(doctor["status"], "blocked")
        runtime_blockers = [blocker for blocker in doctor["blockers"] if blocker["class"] == "blocked_runtime"]
        self.assertEqual(len(runtime_blockers), 1)
        self.assertEqual(runtime_blockers[0]["sdk_layer"], "Runtime Adapters")
        self.assertIn("definition", runtime_blockers[0])
        self.assertIn("blocked_runtime", doctor["lifecycle_event"]["outcome"]["blocker_classes"])
        self.assertTrue(result.errors)

    def test_doctor_selects_structural_audit_next_when_validation_blocks(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
            "command_handle_path": ".agents/skills/autofix/SKILL.md",
        }

        with (
            patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            patch("ask.commands.skills_impl.skills_proof", return_value=_proof_result("autofix")),
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result("error")),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=["agent-ops/autofix"]),
        ):
            result = skills_doctor(REPO_ROOT, "autofix")

        self.assertEqual(result.status, "error")
        doctor = result.data["skill_doctor"]
        self.assertEqual(doctor["status"], "blocked")
        self.assertEqual(
            doctor["next_command"],
            "./bin/ask skills audit Skills/agent-ops/autofix --level compat --json --robot",
        )
        validation_blockers = [blocker for blocker in doctor["blockers"] if blocker["class"] == "blocked_validation"]
        self.assertEqual(len(validation_blockers), 1)
        self.assertEqual(validation_blockers[0]["sdk_layer"], "Validation")

    def test_doctor_next_command_covers_blocker_and_warning_ladder(self) -> None:
        cases = [
            {
                "name": "runtime blocker",
                "blockers": [{"class": "blocked_runtime"}],
                "warnings": [],
                "checks": {"runtime_reachability": {"command": "./bin/ask skills proof autofix --json --robot"}},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": False,
                "expected": "./bin/ask skills proof autofix --json --robot",
            },
            {
                "name": "validation blocker without command",
                "blockers": [{"class": "blocked_validation"}],
                "warnings": [],
                "checks": {},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": False,
                "expected": "./bin/ask skills audit Skills/agent-ops/autofix --level compat --json --robot",
            },
            {
                "name": "missing source blocker",
                "blockers": [{"class": "blocked_missing_source"}],
                "warnings": [],
                "checks": {},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": None,
                "strict": False,
                "expected": "./bin/ask skills resolve autofix --json --robot",
            },
            {
                "name": "resolution blocker",
                "blockers": [{"class": "blocked_resolution"}],
                "warnings": [],
                "checks": {},
                "handle": None,
                "query": "unknown-skill",
                "audit_target": None,
                "strict": False,
                "expected": "./bin/ask skills resolve unknown-skill --json --robot",
            },
            {
                "name": "generic blocker",
                "blockers": [{"class": "blocked_environment"}],
                "warnings": [],
                "checks": {},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": False,
                "expected": "./bin/ask skills doctor autofix --json --robot",
            },
            {
                "name": "outcome proof warning",
                "blockers": [],
                "warnings": [{"class": "outcome_proof_missing"}],
                "checks": {},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": False,
                "expected": "./bin/ask skills prove autofix --json --robot",
            },
            {
                "name": "strict package warning",
                "blockers": [],
                "warnings": [{"class": "capability_contract_incomplete"}],
                "checks": {},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": True,
                "expected": "./bin/ask skills package autofix --json --robot",
            },
            {
                "name": "strict metadata warning",
                "blockers": [],
                "warnings": [{"class": "metadata_incomplete"}],
                "checks": {},
                "handle": "autofix",
                "query": "autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": True,
                "expected": "./bin/ask skills prove autofix --json --robot",
            },
            {
                "name": "path fallback",
                "blockers": [],
                "warnings": [],
                "checks": {},
                "handle": None,
                "query": "Skills/agent-ops/autofix",
                "audit_target": "Skills/agent-ops/autofix",
                "strict": False,
                "expected": "./bin/ask skills audit Skills/agent-ops/autofix --level strict --json --robot",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    _skill_doctor_next_command(
                        blockers=case["blockers"],
                        warnings=case["warnings"],
                        checks=case["checks"],
                        normalized_handle=case["handle"],
                        query=case["query"],
                        audit_target=case["audit_target"],
                        strict=case["strict"],
                    ),
                    case["expected"],
                )

    def test_doctor_sdk_layer_defaults_unknown_keys_to_contracts(self) -> None:
        self.assertEqual(_doctor_sdk_layer_for("check", "new_check"), "Contracts")
        self.assertEqual(_doctor_sdk_layer_for("blocker", "new_blocker"), "Contracts")
        self.assertEqual(_doctor_sdk_layer_for("warning", "new_warning"), "Contracts")
        self.assertEqual(_doctor_sdk_layer_for("new_kind", "resolver"), "Contracts")

    def test_doctor_accepts_repo_relative_source_path(self) -> None:
        with (
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=[]),
        ):
            result = skills_doctor(REPO_ROOT, "Skills/agent-ops/autofix")

        self.assertEqual(result.status, "success")
        doctor = result.data["skill_doctor"]
        self.assertEqual(doctor["target_kind"], "canonical_source_path")
        self.assertEqual(doctor["checks"]["resolver"]["status"], "skipped")
        self.assertEqual(doctor["checks"]["canonical_source"]["status"], "pass")
        self.assertEqual(doctor["checks"]["structural_audit"]["status"], "pass")
        metadata = doctor["checks"]["capability_metadata"]
        self.assertEqual(metadata["status"], "pass")
        self.assertEqual(metadata["sdk_layer"], "Catalog")
        self.assertIn("maturity", metadata["capability_contract"]["present"])
        self.assertIn("compatible_roles", metadata["package_contract"]["missing"])
        package_check = doctor["checks"]["package_readiness"]
        self.assertEqual(package_check["status"], "warning")
        self.assertEqual(package_check["sdk_layer"], "Packaging")
        readiness = metadata["package_readiness"]
        self.assertEqual(readiness["readiness_level"], "versioned_capability")
        self.assertEqual(readiness["required_fields"]["present"], metadata["package_contract"]["present"])
        self.assertEqual(readiness["required_fields"]["missing"], metadata["package_contract"]["missing"])
        self.assertEqual(readiness["values"], metadata["package_contract"]["values"])
        self.assertEqual(readiness["role_compatibility"], metadata["package_contract"]["role_compatibility"])
        self.assertEqual(readiness["runtime_contract"], metadata["package_contract"]["runtime_contract"])
        self.assertEqual(readiness["install_gate"], metadata["package_contract"]["install_gate"])
        self.assertEqual(readiness["promotion_gate"], metadata["package_contract"]["promotion_gate"])
        self.assertFalse(metadata["package_contract"]["install_gate"]["install_ready"])
        self.assertIn("compatible_roles", metadata["package_contract"]["install_gate"]["blocked_reasons"])
        self.assertFalse(readiness["promotion_gate"]["share_ready"])
        self.assertFalse(metadata["package_contract"]["promotion_gate"]["share_ready"])
        self.assertIn("compatible_roles", readiness["promotion_gate"]["recommended_next_fields"])


if __name__ == "__main__":
    unittest.main()
