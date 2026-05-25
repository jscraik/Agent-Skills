import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# pyright: reportMissingImports=false

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from ask.commands import repo_impl as repo_module  # noqa: E402
from ask.envelope import CallResult, ErrorObject  # noqa: E402

_ask_bootstrap_signal = repo_module._ask_bootstrap_signal
repo_closeout = repo_module.repo_closeout
repo_doctor = repo_module.repo_doctor
COMMAND_HANDLE_CHECK_COMMAND = repo_module.COMMAND_HANDLE_CHECK_COMMAND


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


def _handles_result(violations: int = 0, generated_violations: int = 0) -> CallResult:
    return _result(
        status="error" if violations or generated_violations else "success",
        data={
            "command_surface": {
                "status": "fail" if violations else "pass",
                "handle_count": 93,
                "violations": [{} for _ in range(violations)],
            },
            "command_surface_projection_check": {
                "status": "pass",
                "path": ".skillsets/command-surface.json",
                "violations": [],
            },
            "command_handle_check": {
                "status": "fail" if generated_violations else "pass",
                "command_handle_count": 7,
                "checked_count": 14,
                "violations": [
                    {
                        "code": "COMMAND_HANDLE_DRIFT",
                        "handle": f"handle-{index}",
                        "path": f".agents/skills/handle-{index}/SKILL.md",
                    }
                    for index in range(generated_violations)
                ],
            }
        },
    )


def _handles_projection_drift_result() -> CallResult:
    return _result(
        status="error",
        data={
            "command_surface": {
                "status": "pass",
                "handle_count": 93,
                "violations": [],
            },
            "command_surface_projection_check": {
                "status": "fail",
                "path": ".skillsets/command-surface.json",
                "violations": [{"code": "COMMAND_SURFACE_PROJECTION_DRIFT"}],
            },
            "command_handle_check": {
                "status": "pass",
                "command_handle_count": 7,
                "checked_count": 14,
                "violations": [],
            },
        },
    )


def _handles_generated_check_failed_without_violations_result() -> CallResult:
    return _result(
        status="error",
        data={
            "command_surface": {
                "status": "pass",
                "handle_count": 93,
                "violations": [],
            },
            "command_surface_projection_check": {
                "status": "pass",
                "path": ".skillsets/command-surface.json",
                "violations": [],
            },
            "command_handle_check": {
                "status": "fail",
                "command_handle_count": 7,
                "checked_count": 14,
                "violations": [],
            },
        },
    )


def _handles_projection_check_failed_without_violations_result() -> CallResult:
    return _result(
        status="error",
        data={
            "command_surface": {
                "status": "pass",
                "handle_count": 93,
                "violations": [],
            },
            "command_surface_projection_check": {
                "status": "fail",
                "path": ".skillsets/command-surface.json",
                "violations": [],
            },
            "command_handle_check": {
                "status": "pass",
                "command_handle_count": 7,
                "checked_count": 14,
                "violations": [],
            },
        },
    )


def _handles_missing_generated_subcheck_result() -> CallResult:
    return _result(
        data={
            "command_surface": {
                "status": "pass",
                "handle_count": 93,
                "violations": [],
            },
            "command_handle_check": {
                "status": "pass",
                "command_handle_count": 7,
                "checked_count": 14,
                "violations": [],
            },
        },
    )


def _surface_result(warning_count: int = 0) -> CallResult:
    blocking_counts = {"tracked_historical_artifact": warning_count} if warning_count else {}
    return _result(
        data={
            "repo_surface": {
                "status": "warning" if warning_count else "success",
                "summary": {
                    "total_paths": 20,
                    "blocking_findings": warning_count,
                    "counts_by_code": {"tracked_historical_artifact": warning_count},
                    "blocking_counts_by_code": blocking_counts,
                    "blocking_counts_by_classification": (
                        {"historical_artifact": warning_count} if warning_count else {}
                    ),
                },
            }
        },
    )


def _bootstrap_proof(
    *,
    status: str = "success",
    path_status: str = "pass",
    shim_status: str = "pass",
    manual_remediation: list[str] | None = None,
) -> dict:
    return {
        "status": status,
        "checks": {
            "entrypoint_executable": {
                "status": "pass",
                "path_type": "regular_file",
                "safe_to_chmod": True,
            },
            "fallback_command": {
                "status": "pass",
                "defer_to": None,
            },
            "path_discovery": {
                "status": path_status,
                "resolved_path": "/tmp/repo/bin/ask" if path_status == "pass" else None,
            },
            "shim_smoke": {
                "status": shim_status,
                "repo_identity_status": "pass" if shim_status == "pass" else "skipped",
            },
        },
        "remediation": {
            "applied": [],
            "manual": manual_remediation or [],
        },
    }


def _closeout_doctor_payload(warning_count: int = 0, diagnostic_debt: list[dict] | None = None) -> dict:
    blocking_counts = {"tracked_historical_artifact": warning_count} if warning_count else {}
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
                    "blocking_counts_by_code": blocking_counts,
                    "blocking_counts_by_classification": (
                        {"historical_artifact": warning_count} if warning_count else {}
                    ),
                    "diagnostic_summary": {
                        "diagnostic_class": "repo_surface_ownership_debt",
                        "top_blocking_codes": [
                            {"code": "tracked_historical_artifact", "count": warning_count}
                        ] if warning_count else [],
                        "next_action": "classify_allowlist_or_cleanup_tracked_surface",
                        "operator_rule": "Do not flatten diagnostics.",
                    },
                }
            },
        },
    }


class TestAskRepoDoctor(unittest.TestCase):
    def setUp(self) -> None:
        self.bootstrap_patch = patch("ask.commands.repo_impl.run_bootstrap_checks", return_value=_bootstrap_proof())
        self.bootstrap_patch.start()
        self.addCleanup(self.bootstrap_patch.stop)

    def test_all_pass_returns_existing_inspection_next_command(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ) as handles_mock, patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
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
        handles_mock.assert_called_once_with(
            REPO_ROOT,
            check=True,
            include_handles=False,
            check_command_handle_files=True,
        )

    def test_missing_path_shim_is_warning_not_false_pass(self) -> None:
        with patch(
            "ask.commands.repo_impl.run_bootstrap_checks",
            return_value=_bootstrap_proof(status="warning", path_status="warn", shim_status="skipped"),
        ):
            signal = _ask_bootstrap_signal(REPO_ROOT)

        self.assertEqual(signal["state"], "warn")
        self.assertEqual(signal["severity"], "warning")
        self.assertEqual(signal["next_command"], "bash scripts/bootstrap-ask.sh --json")
        self.assertEqual(signal["details"]["manual_remediation"], [])

    def test_missing_path_shim_reports_manual_remediation(self) -> None:
        with patch(
            "ask.commands.repo_impl.run_bootstrap_checks",
            return_value=_bootstrap_proof(
                status="warning",
                path_status="warn",
                shim_status="skipped",
                manual_remediation=["add_repo_bin_to_path"],
            ),
        ):
            signal = _ask_bootstrap_signal(REPO_ROOT)

        self.assertEqual(signal["state"], "warn")
        self.assertEqual(signal["details"]["manual_remediation"], ["add_repo_bin_to_path"])

    def test_wrong_path_shim_reports_identity_remediation(self) -> None:
        with patch(
            "ask.commands.repo_impl.run_bootstrap_checks",
            return_value=_bootstrap_proof(
                status="warning",
                path_status="pass",
                shim_status="fail",
                manual_remediation=["fix_ask_path_shim_identity"],
            ),
        ):
            signal = _ask_bootstrap_signal(REPO_ROOT)

        self.assertEqual(signal["state"], "warn")
        self.assertEqual(signal["details"]["manual_remediation"], ["fix_ask_path_shim_identity"])

    def test_repo_surface_warning_is_diagnostic_advisory_not_blocker(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result(7)):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        self.assertEqual(result.status, "success")
        self.assertFalse(doctor["blocking"])
        self.assertEqual(doctor["blockers"], [])
        self.assertEqual(doctor["diagnostic_debt"][0]["id"], "repo_surface")
        self.assertIn("tracked_historical_artifact=7", doctor["diagnostic_debt"][0]["summary"])
        self.assertEqual(
            doctor["signals"]["repo_surface"]["details"]["diagnostic_summary"]["diagnostic_class"],
            "repo_surface_ownership_debt",
        )
        self.assertEqual(
            doctor["signals"]["repo_surface"]["details"]["diagnostic_summary"]["top_blocking_codes"],
            [{"code": "tracked_historical_artifact", "count": 7}],
        )
        self.assertEqual(doctor["next_command"], "./bin/ask repo surface --json --robot")
        self.assertEqual(doctor["next_command_kind"], "diagnostic_advisory")
        self.assertFalse(doctor["next_command_blocks_task"])
        self.assertEqual(doctor["selected_next_command"]["id"], "repo_surface")
        self.assertEqual(result.data["selected_next_command"], doctor["selected_next_command"])
        self.assertEqual(result.metadata["next_steps"], [])

    def test_repo_doctor_leaves_metadata_next_steps_empty_to_avoid_conflicts(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(drift=True),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        self.assertEqual(
            result.data["doctor"]["next_command"],
            "./bin/ask repo doctor-catalog --json --robot",
        )
        self.assertEqual(result.metadata["next_steps"], [])

    def test_closeout_without_changes_reports_ready_existing_next_command(self) -> None:
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=[]), patch(
            "ask.commands.repo_impl.repo_doctor",
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
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
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
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
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
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
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
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
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
            [COMMAND_HANDLE_CHECK_COMMAND],
        )
        self.assertEqual(
            closeout["next_command"],
            COMMAND_HANDLE_CHECK_COMMAND,
        )

    def test_closeout_generated_projection_only_requires_handle_validation(self) -> None:
        changed_files = [".skillsets/command-surface.json"]
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
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
            [COMMAND_HANDLE_CHECK_COMMAND],
        )
        self.assertEqual(
            closeout["next_command"],
            COMMAND_HANDLE_CHECK_COMMAND,
        )
        self.assertIn(
            COMMAND_HANDLE_CHECK_COMMAND,
            [command["command"] for command in closeout["focused_validation"]],
        )

    def test_closeout_generated_projection_with_other_changes_prioritizes_handles(self) -> None:
        """
        Verify that when a generated command-surface projection is present alongside other changes, repo_closeout prioritizes command-handle validation.
        
        Asserts that sync is not needed, the chosen next command is the command-handle check, and the focused validation sequence places `skill_handles` before `changed_validation` (expected order: repo_doctor, skill_profiles_readiness, skill_events_readiness, skill_memory_readiness, skill_package_readiness, skill_handles, changed_validation).
        """
        changed_files = [
            ".skillsets/command-surface.json",
            "Docs/agents/04-validation.md",
        ]
        with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
            "ask.commands.repo_impl.repo_doctor",
            return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
        ):
            result = repo_closeout(REPO_ROOT, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        self.assertFalse(closeout["sync"]["needed"])
        self.assertEqual(
            closeout["next_command"],
            COMMAND_HANDLE_CHECK_COMMAND,
        )
        self.assertEqual(
            [command["id"] for command in closeout["focused_validation"]],
            [
                "repo_doctor",
                "skill_profiles_readiness",
                "skill_events_readiness",
                "skill_memory_readiness",
                "skill_package_readiness",
                "skill_handles",
                "changed_validation",
            ],
        )

    def test_closeout_changed_runtime_evidence_exposes_shared_workspace_boundary(self) -> None:
        """
        Verify that when a runtime evidence card is changed and present, repo_closeout reports it and exposes shared-workspace truth boundaries and the schema validation command.
        
        Asserts that:
        - runtime evidence status is "present" with a single runtime card and preserved `runtime_status`.
        - truth boundaries indicate the PR and schema validation are not checked by closeout.
        - focused validation includes a `runtime_evidence_cards` step and the schema validation command references `validate_runtime_cards.py`.
        """
        changed_files = [".harness/evidence/runtime-proof/context7/codex/runtime-card.json"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            card_path = repo_root / changed_files[0]
            card_path.parent.mkdir(parents=True)
            card_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "card_id": "runtime-card-context7-codex",
                        "created_at": "2026-05-25T09:00:00Z",
                        "skill_handle": "context7",
                        "command_handle": "$context7",
                        "runtime_target": "codex",
                        "runtime_status": "blocked_runtime",
                        "runtime_session": {
                            "session_id": "runtime-proof-context7-codex",
                            "runtime_target": "codex",
                            "runtime_status": "blocked_runtime",
                            "created_at": "2026-05-25T09:00:00Z",
                            "workspace_root": str(repo_root.resolve()),
                            "actor_type": "agent",
                            "visibility_status": "user_observable",
                        },
                        "thread_runs": [],
                        "turn_events": [],
                        "artifacts": [],
                        "workspace_root": str(repo_root.resolve()),
                        "evidence_receipts": [],
                        "verifier_results": [],
                        "permission_profile": {},
                        "actor_type": "agent",
                        "mutation_scope": "evidence_write",
                        "visibility_status": "user_observable",
                        "limitations": [],
                        "recovery_plan": {
                            "recovery_status": "blocked_runtime",
                            "reason": "Codex runtime unavailable.",
                            "next_commands": [],
                            "preconditions": [],
                            "permission_profile": {},
                            "expected_outcome": "Runtime proof can be rerun.",
                        },
                    }
                ),
                encoding="utf-8",
            )
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

    def test_closeout_changed_runtime_evidence_reports_invalid_card(self) -> None:
        changed_files = [".harness/evidence/runtime-proof/context7/codex/runtime-card.json"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            card_path = repo_root / changed_files[0]
            card_path.parent.mkdir(parents=True)
            card_path.write_text("{not json", encoding="utf-8")
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "invalid")
        self.assertEqual(runtime_evidence["runtime_card_count"], 1)
        self.assertEqual(runtime_evidence["invalid_runtime_card_count"], 1)
        self.assertEqual(runtime_evidence["changed_scope"]["status"], "invalid")
        self.assertEqual(runtime_evidence["workspace_scope"]["status"], "invalid")
        self.assertEqual(runtime_evidence["runtime_cards"][0]["read_status"], "invalid")
        self.assertIn("invalid JSON", runtime_evidence["runtime_cards"][0]["error"])
        self.assertFalse(closeout["commit_readiness"]["ready"])
        self.assertIn("runtime_evidence_invalid", closeout["commit_readiness"]["blockers"])
        self.assertIn("validate_runtime_cards.py", closeout["next_command"])
        self.assertEqual(runtime_evidence["truth_boundaries"]["pr_truth"], "not_checked_by_repo_closeout")
        self.assertEqual(
            runtime_evidence["truth_boundaries"]["schema_proof"],
            "checked_by_repo_closeout",
        )
        self.assertIn(
            "runtime_evidence_cards",
            [command["id"] for command in closeout["focused_validation"]],
        )

    def test_closeout_changed_runtime_evidence_blocks_schema_invalid_card(self) -> None:
        changed_files = [".harness/evidence/runtime-proof/context7/codex/runtime-card.json"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            card_path = repo_root / changed_files[0]
            card_path.parent.mkdir(parents=True)
            card_path.write_text(
                json.dumps({"card_id": "runtime-card-context7-codex", "runtime_session": {}}),
                encoding="utf-8",
            )
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "invalid")
        self.assertEqual(runtime_evidence["changed_scope"]["status"], "invalid")
        self.assertEqual(runtime_evidence["schema_validation"]["status"], "fail")
        self.assertIn("runtime_evidence_invalid", closeout["commit_readiness"]["blockers"])
        self.assertTrue(runtime_evidence["schema_validation"]["findings"])

    def test_closeout_changed_runtime_evidence_reports_invalid_absolute_card_path(self) -> None:
        """
        Validate that repo_closeout marks an absolute-path runtime evidence card with invalid JSON as invalid and blocks commit readiness.
        
        Asserts that:
        - the closeout runtime_evidence status is `"invalid"`,
        - the changed_scope status is `"invalid"`,
        - `"runtime_evidence_invalid"` appears in commit_readiness blockers,
        - the focused_validation list includes a `runtime_evidence_cards` command.
        """
        relative_card = ".harness/evidence/runtime-proof/context7/codex/runtime-card.json"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            card_path = repo_root / relative_card
            card_path.parent.mkdir(parents=True)
            card_path.write_text("{not json", encoding="utf-8")
            changed_files = [str(card_path)]
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "invalid")
        self.assertEqual(runtime_evidence["changed_scope"]["status"], "invalid")
        self.assertIn("runtime_evidence_invalid", closeout["commit_readiness"]["blockers"])
        self.assertIn(
            "runtime_evidence_cards",
            [command["id"] for command in closeout["focused_validation"]],
        )

    def test_closeout_changed_runtime_evidence_symlink_is_invalid(self) -> None:
        relative_card = ".harness/evidence/runtime-proof/context7/codex/runtime-card.json"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            outside_root = Path(tmpdir) / "outside"
            card_path = repo_root / relative_card
            outside_card = outside_root / "runtime-card.json"
            card_path.parent.mkdir(parents=True)
            outside_card.parent.mkdir(parents=True)
            outside_card.write_text("{}", encoding="utf-8")
            try:
                card_path.symlink_to(outside_card)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            changed_files = [relative_card]
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "invalid")
        self.assertEqual(runtime_evidence["changed_scope"]["status"], "invalid")
        self.assertEqual(runtime_evidence["runtime_cards"][0]["read_status"], "invalid")
        self.assertIn("must not be a symlink", runtime_evidence["runtime_cards"][0]["error"])
        self.assertIn("runtime_evidence_invalid", closeout["commit_readiness"]["blockers"])

    def test_closeout_changed_code_is_not_blocked_by_unrelated_invalid_runtime_card(self) -> None:
        changed_files = ["Infrastructure/bin/ask"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            stale_card_path = repo_root / ".harness/evidence/runtime-proof/context7/codex/runtime-card.json"
            stale_card_path.parent.mkdir(parents=True)
            stale_card_path.write_text("{not json", encoding="utf-8")
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "success")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "not_applicable")
        self.assertEqual(runtime_evidence["changed_scope"]["status"], "not_applicable")
        self.assertEqual(runtime_evidence["workspace_scope"]["status"], "invalid")
        self.assertTrue(closeout["commit_readiness"]["ready"])
        self.assertNotIn("runtime_evidence_invalid", closeout["commit_readiness"]["blockers"])
        self.assertNotIn(
            "runtime_evidence_cards",
            [command["id"] for command in closeout["focused_validation"]],
        )

    def test_closeout_changed_runtime_evidence_deletion_blocks_readiness(self) -> None:
        changed_files = [".harness/evidence/runtime-proof/context7/codex/runtime-card.json"]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            with patch("ask.commands.repo_impl.collect_changed_files", return_value=changed_files), patch(
                "ask.commands.repo_impl.repo_doctor",
                return_value=_result(data={"doctor": {"blocking": False, "diagnostic_debt": [], "signals": {}}}),
            ):
                result = repo_closeout(repo_root, changed=True)

        closeout = result.data["repo_closeout"]
        self.assertEqual(result.status, "error")
        runtime_evidence = closeout["runtime_evidence"]
        self.assertEqual(runtime_evidence["status"], "deleted")
        self.assertEqual(runtime_evidence["changed_scope"]["status"], "deleted")
        self.assertEqual(runtime_evidence["deleted_runtime_card_count"], 1)
        self.assertEqual(runtime_evidence["runtime_cards"][0]["read_status"], "deleted")
        self.assertFalse(closeout["commit_readiness"]["ready"])
        self.assertIn("runtime_evidence_deleted", closeout["commit_readiness"]["blockers"])
        self.assertNotIn("runtime_evidence_invalid", closeout["commit_readiness"]["blockers"])
        self.assertIn("validate_runtime_cards.py", closeout["next_command"])

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

    def test_unsynced_projection_prioritizes_sync_before_downstream_checks(self) -> None:
        with patch(
            "ask.commands.repo_impl.repo_status",
            return_value=_status_result(skills_synced=False, is_git=True),
        ), patch(
            "ask.commands.repo_impl.doctor_catalog",
            side_effect=AssertionError("doctor_catalog should be gated"),
        ) as catalog_mock, patch(
            "ask.commands.repo_impl.skills_budget",
            side_effect=AssertionError("skills_budget should be gated"),
        ) as budget_mock, patch(
            "ask.commands.repo_impl.skills_handles",
            side_effect=AssertionError("skills_handles should be gated"),
        ) as handles_mock, patch(
            "ask.commands.repo_impl.repo_surface",
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

    def test_command_handle_violations_keep_violation_summary(self) -> None:
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
            "Command-handle validation found 3 violation(s).",
        )
        self.assertEqual(
            doctor["signals"]["command_handles"]["details"]["failure_code"],
            "command_surface_validation_failed",
        )

    def test_generated_command_handle_violations_block_repo_doctor(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_result(generated_violations=2),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        command_signal = doctor["signals"]["command_handles"]
        self.assertEqual(result.status, "error")
        self.assertEqual(command_signal["state"], "block")
        self.assertEqual(
            command_signal["summary"],
            "Generated command-handle check found 2 violation(s).",
        )
        self.assertEqual(doctor["next_command"], COMMAND_HANDLE_CHECK_COMMAND)
        self.assertEqual(
            command_signal["details"]["failure_code"],
            "generated_command_handle_check_failed",
        )
        self.assertEqual(command_signal["details"]["generated_command_handles"]["violation_count"], 2)
        self.assertEqual(
            command_signal["details"]["generated_command_handles"]["violation_codes"],
            ["COMMAND_HANDLE_DRIFT"],
        )

    def test_command_surface_projection_drift_is_classified_separately(self) -> None:
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
        self.assertEqual(result.status, "error")
        self.assertEqual(
            command_signal["summary"],
            "Command-surface projection check found 1 violation(s).",
        )
        self.assertEqual(command_signal["details"]["failure_code"], "command_surface_projection_check_failed")
        self.assertEqual(command_signal["details"]["command_surface_projection"]["violation_count"], 1)
        self.assertEqual(command_signal["details"]["generated_command_handles"]["violation_count"], 0)

    def test_generated_command_handle_check_failure_without_violations_blocks_repo_doctor(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_generated_check_failed_without_violations_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        command_signal = doctor["signals"]["command_handles"]
        self.assertEqual(result.status, "error")
        self.assertEqual(command_signal["state"], "block")
        self.assertEqual(
            command_signal["details"]["failure_code"],
            "generated_command_handle_check_status_failed",
        )
        self.assertEqual(
            command_signal["summary"],
            "Generated command-handle check failed without explicit violations.",
        )
        self.assertEqual(command_signal["details"]["generated_command_handles"]["status"], "fail")
        self.assertEqual(command_signal["details"]["generated_command_handles"]["violation_count"], 0)
        self.assertEqual(doctor["next_command"], COMMAND_HANDLE_CHECK_COMMAND)

    def test_command_surface_projection_check_failure_without_violations_blocks_repo_doctor(self) -> None:
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
        self.assertEqual(result.status, "error")
        self.assertEqual(command_signal["state"], "block")
        self.assertEqual(
            command_signal["details"]["failure_code"],
            "command_surface_projection_check_status_failed",
        )
        self.assertEqual(
            command_signal["summary"],
            "Command-surface projection check failed without explicit violations.",
        )
        self.assertEqual(command_signal["details"]["command_surface_projection"]["status"], "fail")
        self.assertEqual(command_signal["details"]["command_surface_projection"]["violation_count"], 0)
        self.assertEqual(doctor["next_command"], COMMAND_HANDLE_CHECK_COMMAND)

    def test_missing_generated_command_handle_subcheck_blocks_repo_doctor(self) -> None:
        with patch("ask.commands.repo_impl.repo_status", return_value=_status_result()), patch(
            "ask.commands.repo_impl.doctor_catalog",
            return_value=_catalog_result(),
        ), patch("ask.commands.repo_impl.skills_budget", return_value=_budget_result()), patch(
            "ask.commands.repo_impl.skills_handles",
            return_value=_handles_missing_generated_subcheck_result(),
        ), patch("ask.commands.repo_impl.repo_surface", return_value=_surface_result()):
            result = repo_doctor(REPO_ROOT)

        doctor = result.data["doctor"]
        command_signal = doctor["signals"]["command_handles"]
        self.assertEqual(result.status, "error")
        self.assertEqual(command_signal["state"], "block")
        self.assertEqual(command_signal["details"]["failure_code"], "command_handle_subcheck_missing")
        self.assertEqual(
            command_signal["details"]["missing_required_checks"],
            ["command_surface_projection_check"],
        )
        self.assertEqual(doctor["next_command"], COMMAND_HANDLE_CHECK_COMMAND)

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


if __name__ == "__main__":
    unittest.main()
