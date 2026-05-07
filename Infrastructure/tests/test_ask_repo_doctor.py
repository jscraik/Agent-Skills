import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from ask.commands.repo import repo_closeout, repo_doctor  # noqa: E402
from ask.envelope import CallResult, ErrorObject  # noqa: E402


def _result(status: str = "success", data: dict | None = None) -> CallResult:
    result = CallResult(status=status)
    result.data.update(data or {})
    if status != "success":
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="fixture failure"))
    return result


def _status_result(skills_synced: bool = True, is_git: bool = True) -> CallResult:
    return _result(
        data={
            "repo_root": ".",
            "is_git": is_git,
            "skills_synced": skills_synced,
        }
    )


def _catalog_result(drift: bool = False) -> CallResult:
    if drift:
        return _result(
            status="error",
            data={
                "catalog_parity": {
                    "drift_detected": True,
                    "drift_class": "readme_count_mismatch",
                    "decision_status": "blocked_catalog_parity",
                    "operator_action": "Update README count.",
                }
            },
        )
    return _result(
        data={
            "catalog_parity": {
                "drift_detected": False,
                "decision_status": "resolved",
                "canonical_count": 21,
            }
        }
    )


def _budget_result(violations: int = 0) -> CallResult:
    return _result(
        status="error" if violations else "success",
        data={
            "runtime_budget": {
                "status": "fail" if violations else "pass",
                "default_visible_count": 10,
                "estimated_description_tokens": 1000,
                "violations": [{} for _ in range(violations)],
            }
        },
    )


def _handles_result(violations: int = 0) -> CallResult:
    return _result(
        status="error" if violations else "success",
        data={
            "command_surface": {
                "status": "fail" if violations else "pass",
                "handle_count": 93,
                "violations": [{} for _ in range(violations)],
            }
        },
    )


def _surface_result(warning_count: int = 0) -> CallResult:
    return _result(
        data={
            "repo_surface": {
                "status": "warning" if warning_count else "success",
                "summary": {
                    "total_paths": 20,
                    "blocking_findings": warning_count,
                    "counts_by_code": {"tracked_historical_artifact": warning_count},
                },
            }
        },
    )


class TestAskRepoDoctor(unittest.TestCase):
    def test_all_pass_returns_existing_inspection_next_command(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "success")
        self.assertFalse(doctor["blocking"])
        self.assertEqual(doctor["blockers"], [])
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")

    def test_closeout_without_changes_reports_ready_existing_next_command(self) -> None:
        with patch("ask.commands.repo.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertTrue(closeout["commit_readiness"]["ready"])
        self.assertEqual(closeout["changed_files"], [])
        self.assertEqual(closeout["next_command"], "./bin/ask repo status --json --robot")

    def test_closeout_changed_skill_source_requires_sync_before_validation(self) -> None:
        changed_files = ["Skills/product-strategy/example/SKILL.md"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertFalse(closeout["commit_readiness"]["ready"])
        self.assertIn("sync_required", closeout["commit_readiness"]["blockers"])
        self.assertTrue(closeout["sync"]["needed"])
        self.assertEqual(
            closeout["next_command"],
            "bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh",
        )

    def test_closeout_checks_changed_files_even_without_changed_flag(self) -> None:
        changed_files = ["Skills/product-strategy/example/SKILL.md"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=False)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertFalse(closeout["changed_mode_requested"])
        self.assertEqual(closeout["changed_files"], changed_files)
        self.assertIn("sync_required", closeout["commit_readiness"]["blockers"])

    def test_closeout_blocks_when_changed_file_detection_fails(self) -> None:
        with patch(
            "ask.commands.repo.collect_changed_files",
            side_effect=RuntimeError("git command failed"),
        ), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("changed_file_detection_failed", closeout["commit_readiness"]["blockers"])
        self.assertEqual(closeout["changed_files_error"], "git command failed")
        self.assertEqual(closeout["next_command"], "./bin/ask repo status --json --robot")

    def test_closeout_changed_non_skill_file_recommends_scoped_validation(self) -> None:
        changed_files = ["Infrastructure/scripts/lib/ask/commands/repo.py"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertTrue(closeout["commit_readiness"]["ready"])
        self.assertEqual(
            closeout["next_command"],
            "./bin/ask repo validate --changed-files "
            "Infrastructure/scripts/lib/ask/commands/repo.py --json --robot",
        )

    def test_closeout_blocks_on_doctor_blocker(self) -> None:
        doctor = {
            "blocking": True,
            "next_command": "./bin/ask repo doctor-catalog --json --robot",
            "diagnostic_debt": [],
            "signals": {},
        }
        with patch("ask.commands.repo.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(status="error", data={"doctor": doctor}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("repo_doctor_blocking", closeout["commit_readiness"]["blockers"])
        self.assertEqual(closeout["next_command"], "./bin/ask repo doctor-catalog --json --robot")

    def test_catalog_parity_drift_blocks_and_selects_catalog_doctor(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(drift=True),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result(4515)):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertTrue(doctor["blocking"])
        self.assertEqual(doctor["blockers"][0]["id"], "catalog_parity")
        self.assertEqual(doctor["next_command"], "./bin/ask repo doctor-catalog --json --robot")
        self.assertEqual(doctor["signals"]["repo_surface"]["state"], "warn")
        self.assertEqual(doctor["diagnostic_debt"][0]["id"], "repo_surface")

    def test_non_git_root_prioritizes_repo_status_before_projection_sync(self) -> None:
        with patch(
            "ask.commands.repo.repo_status",
            return_value=_status_result(skills_synced=False, is_git=False),
        ), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertTrue(doctor["blocking"])
        self.assertEqual(doctor["blockers"][0]["id"], "repo_status")
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "skipped")
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")

    def test_runtime_budget_command_failure_blocks(self) -> None:
        failed_budget = _result(status="error", data={"runtime_budget": {"status": "fail"}})
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=failed_budget), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(doctor["signals"]["runtime_budget"]["state"], "error")
        self.assertEqual(doctor["next_command"], "./bin/ask runtime budget --json --robot")

    def test_runtime_budget_policy_violations_keep_violation_summary(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result(violations=2)), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(doctor["signals"]["runtime_budget"]["state"], "block")
        self.assertEqual(
            doctor["signals"]["runtime_budget"]["summary"],
            "Runtime budget has 2 policy violation(s).",
        )

    def test_command_handle_failure_without_violations_blocks(self) -> None:
        failed_handles = _result(
            status="error",
            data={"command_surface": {"status": "fail", "handle_count": 93, "violations": []}},
        )
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=failed_handles,
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(doctor["signals"]["command_handles"]["state"], "block")
        self.assertEqual(doctor["next_command"], "./bin/ask skills handles --check --json --robot")

    def test_command_handle_violations_keep_violation_summary(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(violations=3),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(
            doctor["signals"]["command_handles"]["summary"],
            "Command-handle validation found 3 violation(s).",
        )

    def test_non_git_repo_status_gates_downstream_checks(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result(is_git=False)), patch(
            "ask.commands.repo.doctor_catalog",
            side_effect=AssertionError("doctor_catalog should be gated"),
        ), patch(
            "ask.commands.repo.skills_budget",
            side_effect=AssertionError("skills_budget should be gated"),
        ), patch(
            "ask.commands.repo.skills_handles",
            side_effect=AssertionError("skills_handles should be gated"),
        ), patch(
            "ask.commands.repo.repo_surface",
            side_effect=AssertionError("repo_surface should be gated"),
        ):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertTrue(doctor["blocking"])
        self.assertEqual(doctor["blockers"][0]["id"], "repo_status")
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")

    def test_unexpected_signal_exception_returns_doctor_blocker(self) -> None:
        with patch("ask.commands.repo.repo_status", side_effect=RuntimeError("boom")), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertTrue(doctor["blocking"])
        blocker_ids = {blocker["id"] for blocker in doctor["blockers"]}
        self.assertIn("repo_status", blocker_ids)
        self.assertIn("projection_sync", blocker_ids)
        self.assertEqual(doctor["signals"]["repo_status"]["state"], "error")
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "error")
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")


if __name__ == "__main__":
    unittest.main()
