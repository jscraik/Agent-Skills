import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills_impl import skills_doctor  # noqa: E402
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


class TestAskSkillsDoctor(unittest.TestCase):
    def test_doctor_reports_pass_for_reachable_skill_with_outcome_candidate(self) -> None:
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
        self.assertEqual(doctor["status"], "pass")
        self.assertEqual(doctor["handle"], "autofix")
        self.assertEqual(doctor["checks"]["resolver"]["status"], "pass")
        self.assertEqual(doctor["checks"]["runtime_reachability"]["status"], "pass")
        self.assertEqual(doctor["checks"]["structural_audit"]["status"], "pass")
        self.assertEqual(doctor["checks"]["outcome_proof"]["status"], "available_not_run")
        self.assertIn("blocked_user_input", doctor["readiness_taxonomy"]["blockers"])
        self.assertIn("timeout_no_output", doctor["readiness_taxonomy"]["blockers"])
        self.assertIn("strict_audit_not_run", doctor["readiness_taxonomy"]["warnings"])
        self.assertEqual(doctor["lifecycle_event"]["schema_version"], "capability-lifecycle-event.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_type"], "skill_doctor_completed")
        self.assertIn("eval_blocked", doctor["lifecycle_event_types"])
        self.assertEqual(doctor["warnings"], [])

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
        self.assertIn("definition", runtime_blockers[0])
        self.assertIn("blocked_runtime", doctor["lifecycle_event"]["outcome"]["blocker_classes"])
        self.assertTrue(result.errors)

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
        self.assertIn("maturity", metadata["capability_contract"]["present"])
        self.assertIn("compatible_roles", metadata["package_contract"]["missing"])
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
