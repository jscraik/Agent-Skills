import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# pyright: reportMissingImports=false  # test-only cross-module imports; JSC-385; expires 2026-12-31; ADR: local test bootstrap

from test_ask_repo_doctor import (  # noqa: E402  # test-only cross-module imports; JSC-385; expires 2026-12-31; ADR: local test bootstrap
    COMMAND_HANDLE_CHECK_COMMAND,
    REPO_ROOT,
    _bootstrap_proof,
    _budget_result,
    _catalog_result,
    _closeout_doctor_payload,
    _handles_projection_check_failed_without_violations_result,
    _handles_projection_drift_result,
    _handles_result,
    _result,
    _status_result,
    _surface_result,
    repo_closeout,
    repo_doctor,
)
from ask.envelope import CallResult, ErrorObject  # noqa: E402  # test-only Infrastructure import; JSC-385; expires 2026-12-31; ADR: local test bootstrap
from ask.commands.repo_impl import _runtime_evidence_schema_validation  # noqa: E402  # test-only Infrastructure import; JSC-388; expires 2026-12-31; ADR: closeout subprocess failure coverage
from helpers.ask_repo_doctor_fixtures import write_runtime_card as _write_runtime_card  # noqa: E402  # test-only Infrastructure import; JSC-385; expires 2026-12-31; ADR: local test bootstrap


class TestAskRepoDoctorCloseout(unittest.TestCase):
    def setUp(self) -> None:
        self.bootstrap_patch = patch("ask.commands.repo_impl.run_bootstrap_checks", return_value=_bootstrap_proof())
        self.bootstrap_patch.start()
        self.addCleanup(self.bootstrap_patch.stop)
        self.package_patch = patch("ask.commands.repo_impl.skills_package", return_value=_result(data={
            "skill_package": {
                "status": "ready",
                "target": "skill-factory-router",
                "handle": "skill-factory-router",
                "readiness_level": "ready",
                "promotion_status": "ready",
                "checkout_test_status": "pass",
                "missing_fields": [],
                "blocked_reasons": [],
                "install_ready": True,
                "promotion_ready": True,
                "share_ready": True,
            }
        }))
        self.package_patch.start()
        self.addCleanup(self.package_patch.stop)

    def test_closeout_changed_runtime_evidence_exposes_shared_workspace_boundary(self) -> None:
        """
        Verify that when a runtime evidence card is changed and present, repo_closeout reports it and exposes shared-workspace truth boundaries and the schema validation command.

        Asserts that:
        - runtime evidence status is "present" with a single runtime card and preserved `runtime_status`.
        - truth boundaries identify PR truth separately while schema proof is recorded by closeout.
        - focused validation includes a `runtime_evidence_cards` step and the schema validation command references `validate_runtime_cards.py`.
        """
        changed_files = [".harness/evidence/runtime-proof/context7/codex/runtime-card.json"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            _write_runtime_card(repo_root, changed_files[0])
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "present")
        self.assertEqual(runtime_evidence["runtime_card_count"], 1)
        self.assertEqual(runtime_evidence["runtime_cards"][0]["runtime_status"], "blocked_runtime")
        self.assertEqual(runtime_evidence["truth_boundaries"]["pr_truth"], "not_checked_by_repo_closeout")
        self.assertEqual(
            runtime_evidence["truth_boundaries"]["schema_proof"],
            "checked_by_repo_closeout",
        )
        self.assertIn(
            "runtime_evidence_cards",
            [command["id"] for command in closeout["focused_validation"]],
        )
        self.assertIn(
            "validate_runtime_cards.py",
            runtime_evidence["schema_validation"]["command"],
        )
        self.assertEqual(runtime_evidence["schema_validation"]["status"], "pass")


    def test_closeout_skips_changed_file_detection_without_changed_flag(self) -> None:
        changed_files = ["Skills/product-strategy/example/SKILL.md"]
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files) as collect_mock, patch(
            "ask.commands.repo_impl.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=False)

        closeout = result.data["repo_closeout"]
        collect_mock.assert_not_called()
        self.assertEqual(result.status, "success")
        self.assertFalse(closeout["changed_mode_requested"])
        self.assertEqual(closeout["changed_files"], [])
        self.assertEqual(closeout["runtime_evidence"]["status"], "skipped")
        self.assertEqual(
            closeout["runtime_evidence"]["truth_boundaries"]["command_proof"],
            "not_checked_by_repo_closeout",
        )
        self.assertTrue(closeout["commit_readiness"]["ready"])

    def test_closeout_strict_diagnostic_debt_uses_doctor_next_command(self) -> None:
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo_impl.repo_doctor",
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
            "ask.commands.repo_impl.collect_changed_files",
            side_effect=RuntimeError("git command failed"),
        ), patch(
            "ask.commands.repo_impl.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("changed_file_detection_failed", closeout["commit_readiness"]["blockers"])
        self.assertEqual(closeout["changed_files_error"], "git command failed")
        self.assertEqual(closeout["next_command"], "./bin/ask repo status --json --robot")

    def test_closeout_normalizes_git_startup_failure(self) -> None:
        with patch("ask.commands.repo_impl.subprocess.run", side_effect=OSError("git missing")), patch(
            "ask.commands.repo_impl.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("changed_file_detection_failed", closeout["commit_readiness"]["blockers"])
        self.assertIn("git command could not start", closeout["changed_files_error"])
        self.assertIn("git missing", closeout["changed_files_error"])

    def test_runtime_evidence_validation_normalizes_subprocess_startup_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            card_path = repo_root / "runtime-card.json"
            card_path.write_text("{}", encoding="utf-8")
            for error in (OSError("python3 missing"), subprocess.TimeoutExpired(["python3"], 30)):
                with self.subTest(error=type(error).__name__), patch(
                    "ask.commands.repo_impl.subprocess.run",
                    side_effect=error,
                ):
                    report = _runtime_evidence_schema_validation(repo_root, [card_path])

                self.assertEqual(report["status"], "fail")
                self.assertIsNone(report["returncode"])
                self.assertIn("could not complete", report["stderr"])

    def test_closeout_changed_non_skill_file_recommends_scoped_validation(self) -> None:
        changed_files = ["Infrastructure/scripts/lib/ask/commands/repo.py"]
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
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
            [
                "repo_doctor",
                "skill_profiles_readiness",
                "skill_events_readiness",
                "skill_memory_readiness",
                "skill_package_readiness",
                "changed_validation",
            ],
        )
        self.assertEqual(closeout["surface_policy"]["status"], "warning")
        self.assertEqual(closeout["surface_policy"]["blocking_findings"], 7)
        self.assertEqual(
            closeout["surface_policy"]["diagnostic_summary"]["top_blocking_codes"],
            [{"code": "tracked_historical_artifact", "count": 7}],
        )
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
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo_impl.repo_doctor",
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
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo_impl.repo_doctor",
            return_value=_result(data={"doctor": doctor}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True, strict=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        self.assertIn("strict_diagnostic_debt", closeout["commit_readiness"]["blockers"])
        self.assertEqual(closeout["next_command"], "./bin/ask repo surface --json --robot")

    def test_catalog_parity_drift_blocks_and_selects_catalog_doctor(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(drift=True),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result(4515)):
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
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result(violations=2)), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(violations=3),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
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
            "ask.commands.repo_impl.repo_status",
            return_value=_status_result(skills_synced=False, is_git=False),
        ), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ) as catalog_mock, patch(
            "ask.commands.repo_impl.skills_budget",
            return_value=_budget_result(),
        ) as budget_mock, patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ) as handles_mock, patch(
            "ask.commands.repo_impl.repo_surface",
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

    def test_runtime_projection_states_gate_or_skip_downstream_checks(self) -> None:
        sync_command = "./bin/ask skills sync --scope workspace --projection flat --json --robot"
        cases = tuple((state, "error", "block", sync_command) for state in (None, "corrupt")) + (("unmaterialized_linked_worktree", "success", "warn", sync_command),)
        with patch("ask.commands.repo_impl.repo_status") as status_mock, patch(
            "ask.commands.repo_impl.doctor_catalog", side_effect=AssertionError("catalog should be gated")
        ) as catalog_mock, patch(
            "ask.commands.repo_impl.skills_budget", side_effect=AssertionError("budget should be gated")
        ) as budget_mock, patch(
            "ask.commands.repo_impl.skills_handles", side_effect=AssertionError("handles should be gated")
        ) as handles_mock, patch(
            "ask.commands.repo_impl.repo_surface", side_effect=AssertionError("surface should be gated")
        ) as surface_mock:
            for state, expected_status, expected_signal, next_command in cases:
                status = _status_result(skills_synced=False, is_git=True)
                status.data.update({"skills_projection_state": state} if state else {})
                status_mock.return_value = status
                with self.subTest(state=state):
                    result = repo_doctor(REPO_ROOT)
                    doctor = result.data["doctor"]
                    self.assertEqual(result.status, expected_status)
                    self.assertEqual(doctor["signals"]["projection_sync"]["state"], expected_signal)
                    self.assertEqual(doctor["signals"]["catalog_parity"]["state"], "skipped")
                    self.assertEqual(doctor["signals"]["projection_sync"]["details"]["projection_state"], state or "missing")
                    if state == "unmaterialized_linked_worktree":
                        self.assertFalse(doctor["blocking"])
                        self.assertEqual(doctor["signals"]["projection_sync"]["details"]["runtime_verification"], "not_run")
                        self.assertEqual(doctor["next_command"], sync_command)
                    else:
                        self.assertTrue(doctor["blocking"])
                        self.assertEqual(doctor["blockers"][0]["id"], "projection_sync")
                        self.assertEqual(doctor["next_command"], next_command)
        catalog_mock.assert_not_called()
        budget_mock.assert_not_called()
        handles_mock.assert_not_called()
        surface_mock.assert_not_called()

    def test_runtime_budget_command_failure_blocks(self) -> None:
        failed_budget = _result(status="error", data={"runtime_budget": {"status": "fail"}})
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=failed_budget), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(doctor["signals"]["runtime_budget"]["state"], "error")
        self.assertEqual(doctor["next_command"], "./bin/ask runtime budget --json --robot")

    def test_runtime_budget_policy_violations_keep_violation_summary(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result(violations=2)), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
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
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=failed_handles,
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(doctor["signals"]["command_handles"]["state"], "block")
        self.assertEqual(doctor["next_command"], COMMAND_HANDLE_CHECK_COMMAND)

    def test_command_surface_violations_keep_violation_summary(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(violations=3),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "error")
        self.assertEqual(
            doctor["signals"]["command_handles"]["summary"],
            "SDK handle validation found 3 violation(s).",
        )
        self.assertEqual(
            doctor["signals"]["command_handles"]["details"]["failure_code"],
            "sdk_handle_validation_failed",
        )

    def test_command_surface_violations_block_repo_doctor(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(violations=2),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        command_signal = doctor["signals"]["command_handles"]
        self.assertEqual(result.status, "error")
        self.assertEqual(command_signal["state"], "block")
        self.assertEqual(
            command_signal["summary"],
            "SDK handle validation found 2 violation(s).",
        )
        self.assertEqual(doctor["next_command"], COMMAND_HANDLE_CHECK_COMMAND)
        self.assertEqual(
            command_signal["details"]["failure_code"],
            "sdk_handle_validation_failed",
        )
        self.assertEqual(command_signal["details"]["violation_count"], 2)

    def test_removed_projection_drift_does_not_block_sdk_handle_signal(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_projection_drift_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        command_signal = doctor["signals"]["command_handles"]
        self.assertEqual(result.status, "success")
        self.assertEqual(command_signal["state"], "pass")
        self.assertEqual(command_signal["summary"], "SDK skill handles validate cleanly.")
        self.assertNotIn("failure_code", command_signal["details"])

    def test_removed_projection_check_failure_does_not_block_sdk_handle_signal(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_projection_check_failed_without_violations_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        command_signal = doctor["signals"]["command_handles"]
        self.assertEqual(result.status, "success")
        self.assertEqual(command_signal["state"], "pass")
        self.assertEqual(command_signal["summary"], "SDK skill handles validate cleanly.")
        self.assertNotIn("failure_code", command_signal["details"])
        self.assertEqual(doctor["next_command"], "./bin/ask repo status --json --robot")

    def test_non_git_repo_status_gates_downstream_checks(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result(is_git=False)), patch(
            "ask.commands.repo_impl.doctor_catalog",
            side_effect=AssertionError("doctor_catalog should be gated"),
        ), patch(
            "ask.commands.repo_impl.skills_budget",
            side_effect=AssertionError("skills_budget should be gated"),
        ), patch(
            "ask.commands.repo_impl.skills_handles",
            side_effect=AssertionError("skills_handles should be gated"),
        ), patch(
            "ask.commands.repo_impl.repo_surface",
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
        with patch("ask.commands.repo_impl.repo_status", return_value=failed_status), patch(
            "ask.commands.repo_impl.doctor_catalog",
            side_effect=AssertionError("doctor_catalog should be gated"),
        ), patch(
            "ask.commands.repo_impl.skills_budget",
            side_effect=AssertionError("skills_budget should be gated"),
        ), patch(
            "ask.commands.repo_impl.skills_handles",
            side_effect=AssertionError("skills_handles should be gated"),
        ), patch(
            "ask.commands.repo_impl.repo_surface",
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
        with patch("ask.commands.repo_impl.repo_status", side_effect=RuntimeError("boom")), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
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
