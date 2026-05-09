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


def _closeout_doctor_payload(warning_count: int = 0, diagnostic_debt: list[dict] | None = None) -> dict:
    return {
        "blocking": False,
        "diagnostic_debt": diagnostic_debt or [],
        "signals": {
            "runtime_budget": {
                "details": {
                    "status": "pass",
                    "default_visible_count": 10,
                    "estimated_description_tokens": 1000,
                    "violation_count": 0,
                }
            },
            "repo_surface": {
                "details": {
                    "status": "warning" if warning_count else "success",
                    "blocking_findings": warning_count,
                    "total_paths": 20,
                    "counts_by_code": {"tracked_historical_artifact": warning_count},
                }
            },
        },
    }


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
        self.assertEqual(doctor["next_command_kind"], "normal_inspection")
        self.assertFalse(doctor["next_command_blocks_task"])
        self.assertEqual(result.data["next_command_kind"], doctor["next_command_kind"])
        self.assertEqual(result.metadata["next_steps"], [])

    def test_repo_surface_warning_is_diagnostic_advisory_not_blocker(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result(7)):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "success")
        self.assertFalse(doctor["blocking"])
        self.assertEqual(doctor["blockers"], [])
        self.assertEqual(doctor["diagnostic_debt"][0]["id"], "repo_surface")
        self.assertEqual(doctor["next_command"], "./bin/ask repo surface --json --robot")
        self.assertEqual(doctor["next_command_kind"], "diagnostic_advisory")
        self.assertFalse(doctor["next_command_blocks_task"])
        self.assertEqual(doctor["selected_next_command"]["id"], "repo_surface")
        self.assertEqual(result.data["selected_next_command"], doctor["selected_next_command"])
        self.assertEqual(result.metadata["next_steps"], [])

    def test_repo_doctor_leaves_metadata_next_steps_empty_to_avoid_conflicts(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(drift=True),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        self.assertEqual(
            result.data["doctor"]["next_command"],
            "./bin/ask repo doctor-catalog --json --robot",
        )
        self.assertEqual(result.metadata["next_steps"], [])

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
            "./bin/ask skills sync --scope workspace --projection rooted --json --robot",
        )

    def test_closeout_changed_plugin_reference_does_not_require_sync(self) -> None:
        changed_files = ["Plugins/harness-engineering/references/xp-operating-contract.md"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertFalse(closeout["sync"]["needed"])
        self.assertEqual(
            closeout["next_command"],
            "./bin/ask repo validate --changed-files "
            "Plugins/harness-engineering/references/xp-operating-contract.md --json --robot",
        )

    def test_closeout_changed_plugin_skill_requires_sync(self) -> None:
        changed_files = ["Plugins/harness-engineering/skills/goal-governor/SKILL.md"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertTrue(closeout["sync"]["needed"])
        self.assertEqual(
            closeout["next_command"],
            "./bin/ask skills sync --scope workspace --projection rooted --json --robot",
        )

    def test_closeout_changed_skill_source_with_projection_update_requires_handle_validation(self) -> None:
        changed_files = [
            ".skillsets/harness-engineering/manifest.jsonl",
            "Plugins/harness-engineering/skills/he-router/SKILL.md",
        ]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertTrue(closeout["commit_readiness"]["ready"])
        self.assertFalse(closeout["sync"]["needed"])
        self.assertTrue(closeout["sync"]["projection_update_present"])
        self.assertEqual(closeout["sync"]["commands"], [])
        self.assertEqual(
            closeout["sync"]["validation_commands"],
            ["./bin/ask skills handles --check --json --robot"],
        )
        self.assertEqual(
            closeout["next_command"],
            "./bin/ask skills handles --check --json --robot",
        )

    def test_closeout_generated_projection_only_requires_handle_validation(self) -> None:
        changed_files = [".skillsets/command-surface.json"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertTrue(closeout["commit_readiness"]["ready"])
        self.assertFalse(closeout["sync"]["needed"])
        self.assertEqual(closeout["sync"]["commands"], [])
        self.assertEqual(
            closeout["sync"]["validation_commands"],
            ["./bin/ask skills handles --check --json --robot"],
        )
        self.assertEqual(
            closeout["next_command"],
            "./bin/ask skills handles --check --json --robot",
        )
        self.assertIn(
            "./bin/ask skills handles --check --json --robot",
            [command["command"] for command in closeout["focused_validation"]],
        )

    def test_closeout_generated_projection_with_other_changes_prioritizes_handles(self) -> None:
        changed_files = [
            ".skillsets/command-surface.json",
            "Docs/agents/04-validation.md",
        ]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertFalse(closeout["sync"]["needed"])
        self.assertEqual(
            closeout["next_command"],
            "./bin/ask skills handles --check --json --robot",
        )
        self.assertEqual(
            [command["id"] for command in closeout["focused_validation"]],
            ["repo_doctor", "skill_handles", "changed_validation"],
        )

    def test_closeout_skips_changed_file_detection_without_changed_flag(self) -> None:
        changed_files = ["Skills/product-strategy/example/SKILL.md"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files) as collect_mock, patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=False)

        closeout = result.data["repo_closeout"]
        collect_mock.assert_not_called()
        self.assertEqual(result.status, "success")
        self.assertFalse(closeout["changed_mode_requested"])
        self.assertEqual(closeout["changed_files"], [])
        self.assertTrue(closeout["commit_readiness"]["ready"])

    def test_closeout_strict_diagnostic_debt_uses_doctor_next_command(self) -> None:
        with patch("ask.commands.repo.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(
                data={
                    "doctor": {
                        "blocking": False,
                        "diagnostic_debt": [{"id": "repo_surface"}],
                        "next_command": "./bin/ask repo surface --json --robot",
                        "signals": {},
                    }
                }
            ),
        ):
            result = repo_closeout(REPO_ROOT, strict=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("strict_diagnostic_debt", closeout["commit_readiness"]["blockers"])
        self.assertEqual(closeout["next_command"], "./bin/ask repo surface --json --robot")

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

    def test_closeout_normalizes_git_startup_failure(self) -> None:
        with patch("ask.commands.repo.subprocess.run", side_effect=OSError("git missing")), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("changed_file_detection_failed", closeout["commit_readiness"]["blockers"])
        self.assertIn("git command could not start", closeout["changed_files_error"])
        self.assertIn("git missing", closeout["changed_files_error"])

    def test_closeout_changed_non_skill_file_recommends_scoped_validation(self) -> None:
        changed_files = ["Infrastructure/scripts/lib/ask/commands/repo.py"]
        with patch("ask.commands.repo.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": _closeout_doctor_payload(warning_count=7)}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertEqual(closeout["changed_files"], changed_files)
        self.assertEqual(closeout["changed_file_count"], 1)
        self.assertFalse(closeout["sync"]["needed"])
        self.assertEqual(closeout["sync"]["commands"], [])
        self.assertEqual(closeout["sync"]["validation_commands"], [])
        self.assertEqual(
            [command["id"] for command in closeout["focused_validation"]],
            ["repo_doctor", "changed_validation"],
        )
        self.assertEqual(closeout["surface_policy"]["status"], "warning")
        self.assertEqual(closeout["surface_policy"]["blocking_findings"], 7)
        self.assertEqual(closeout["runtime_budget"]["status"], "pass")
        self.assertTrue(closeout["commit_readiness"]["ready"])
        self.assertEqual(closeout["commit_readiness"]["blockers"], [])
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

    def test_strict_closeout_uses_diagnostic_debt_remediation(self) -> None:
        doctor = {
            "blocking": False,
            "next_command": "./bin/ask repo status --json --robot",
            "diagnostic_debt": [
                {
                    "id": "repo_surface",
                    "next_command": "./bin/ask repo surface --json --robot",
                }
            ],
            "signals": {},
        }
        with patch("ask.commands.repo.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo.repo_doctor",
            return_value=_result(data={"doctor": doctor}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True, strict=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("strict_diagnostic_debt", closeout["commit_readiness"]["blockers"])
        self.assertEqual(closeout["next_command"], "./bin/ask repo surface --json --robot")

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
        self.assertEqual(doctor["next_command_kind"], "blocking_repair")
        self.assertTrue(doctor["next_command_blocks_task"])
        self.assertEqual(result.data["next_command_kind"], doctor["next_command_kind"])
        self.assertEqual(doctor["selected_next_command"]["id"], "catalog_parity")
        self.assertEqual(doctor["signals"]["repo_surface"]["state"], "warn")
        self.assertEqual(doctor["diagnostic_debt"][0]["id"], "repo_surface")

    def test_runtime_budget_priority_beats_command_handle_blocker(self) -> None:
        with patch("ask.commands.repo.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo.skills_budget", return_value=_budget_result(violations=2)), patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(violations=3),
        ), patch("ask.commands.repo.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(doctor["blockers"][0]["id"], "runtime_budget")
        self.assertEqual(doctor["next_command"], "./bin/ask runtime budget --json --robot")
        self.assertEqual(doctor["selected_next_command"]["id"], "runtime_budget")
        self.assertEqual(
            [item["id"] for item in doctor["secondary_next_commands"]],
            ["command_handles"],
        )

    def test_non_git_root_prioritizes_repo_status_before_projection_sync(self) -> None:
        with patch(
            "ask.commands.repo.repo_status",
            return_value=_status_result(skills_synced=False, is_git=False),
        ), patch(
            "ask.commands.repo.doctor_catalog",
            return_value=_catalog_result(),
        ) as catalog_mock, patch(
            "ask.commands.repo.skills_budget",
            return_value=_budget_result(),
        ) as budget_mock, patch(
            "ask.commands.repo.skills_handles",
            return_value=_handles_result(),
        ) as handles_mock, patch(
            "ask.commands.repo.repo_surface",
            return_value=_surface_result(),
        ) as surface_mock:
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertTrue(doctor["blocking"])
        self.assertEqual(doctor["blockers"][0]["id"], "repo_status")
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["runtime_budget"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["command_handles"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["repo_surface"]["state"], "skipped")
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")
        catalog_mock.assert_not_called()
        budget_mock.assert_not_called()
        handles_mock.assert_not_called()
        surface_mock.assert_not_called()

    def test_unsynced_projection_prioritizes_sync_before_downstream_checks(self) -> None:
        with patch(
            "ask.commands.repo.repo_status",
            return_value=_status_result(skills_synced=False, is_git=True),
        ), patch(
            "ask.commands.repo.doctor_catalog",
            side_effect=AssertionError("doctor_catalog should be gated"),
        ) as catalog_mock, patch(
            "ask.commands.repo.skills_budget",
            side_effect=AssertionError("skills_budget should be gated"),
        ) as budget_mock, patch(
            "ask.commands.repo.skills_handles",
            side_effect=AssertionError("skills_handles should be gated"),
        ) as handles_mock, patch(
            "ask.commands.repo.repo_surface",
            side_effect=AssertionError("repo_surface should be gated"),
        ) as surface_mock:
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertTrue(doctor["blocking"])
        self.assertEqual(doctor["blockers"][0]["id"], "projection_sync")
        self.assertEqual(
            doctor["next_command"],
            "./bin/ask skills sync --scope workspace --projection rooted --json --robot",
        )
        self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["runtime_budget"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["command_handles"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["repo_surface"]["state"], "skipped")
        catalog_mock.assert_not_called()
        budget_mock.assert_not_called()
        handles_mock.assert_not_called()
        surface_mock.assert_not_called()

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
        self.assertEqual(doctor["next_command_kind"], "blocking_repair")
        self.assertTrue(doctor["next_command_blocks_task"])
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")

    def test_repo_status_error_result_gates_downstream_checks(self) -> None:
        failed_status = CallResult(status="error")
        failed_status.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message="Repository status is unavailable.",
                fix_suggestion="Rerun repo status.",
            )
        )
        with patch("ask.commands.repo.repo_status", return_value=failed_status), patch(
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
        self.assertEqual(doctor["blockers"][0]["id"], "repo_status")
        self.assertEqual(
            doctor["signals"]["repo_status"]["summary"],
            "Repository status is unavailable.",
        )
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["runtime_budget"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["command_handles"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["repo_surface"]["state"], "skipped")

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
        self.assertNotIn("projection_sync", blocker_ids)
        self.assertEqual(doctor["signals"]["projection_sync"]["state"], "skipped")
        self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")


if __name__ == "__main__":
    unittest.main()
