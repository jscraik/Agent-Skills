from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import runtime_adapters  # noqa: E402

VALIDATOR = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "validate_runtime_cards.py"

def _resolve_autofix_handle(_handle: str, *, repo_root_path: Path) -> dict[str, object]:
    del repo_root_path
    return {
        "status": "ok",
        "handle": "autofix",
        "source_path": "Skills/agent-ops/autofix/SKILL.md",
        "runtime_visibility": "flat",
    }


def _assert_partial_probe_and_recovery(testcase: unittest.TestCase, repo_root: Path, summary: dict, card: dict) -> None:
    probe = json.loads((repo_root / summary["probe_artifact_path"]).read_text(encoding="utf-8"))
    testcase.assertEqual(probe["proof"]["status"], "partial")
    testcase.assertEqual(probe["proof"]["structural_status"], "pass")
    testcase.assertEqual(probe["proof"]["live_proof_status"], "partial")
    recovery_plan = card["recovery_plan"]
    testcase.assertEqual(recovery_plan["recovery_status"], "partial")
    testcase.assertTrue(any("telemetry" in item for item in recovery_plan["preconditions"]))
    testcase.assertIn("skill invocation counters", recovery_plan["next_commands"][0]["preconditions"][2])


class TestRuntimeProofValidation(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *args],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_runtime_evidence_writer_sanitizes_handle_path_segment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            repo_root.mkdir()
            proof = {
                "schema_version": "sdk-skill-proof.v1",
                "handle": "../escape",
                "runtime_target": "codex",
                "status": "fail",
                "resolution": {},
                "runtime_failure": {
                    "failed_check_id": "codex_user_runtime_ready",
                    "message": "Codex runtime handle is unavailable.",
                    "recovery_guidance": "Refresh the Codex runtime projection.",
                },
            }

            summary = runtime_adapters.emit_sdk_skill_runtime_evidence(
                repo_root=repo_root,
                proof=proof,
                actor_type="agent",
            )

            self.assertEqual(summary["evidence_dir"], ".harness/evidence/runtime-proof/escape/codex")
            self.assertTrue((repo_root / summary["runtime_card_path"]).is_file())
            self.assertFalse((repo_root.parent / "escape").exists())
            process = self.run_validator(
                str(repo_root / summary["runtime_card_path"]),
                "--require-shared-workspace",
                "--workspace-root",
                "${WORKSPACE_ROOT}",
                "--json",
            )
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_runtime_card_embeds_redacted_runtime_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            workspace_runtime = repo_root / ".agents" / "skills"
            workspace_handle = workspace_runtime / "autofix" / "SKILL.md"
            workspace_handle.parent.mkdir(parents=True)
            workspace_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")
            codex_handle = repo_root / ".tmp-home" / ".codex" / "skills" / "autofix" / "SKILL.md"
            proof = {
                "schema_version": "sdk-skill-proof.v1",
                "handle": "autofix",
                "runtime_target": "codex",
                "status": "fail",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                },
                "gates": {
                    "resolver": True,
                    "canonical_source_exists": True,
                    "codex_user_runtime_ready": False,
                },
                "gate_policy": {"required": ["codex_user_runtime_ready"]},
                "runtime_failure": {
                    "failed_check_id": "codex_user_runtime_ready",
                    "message": "Codex runtime handle is unavailable.",
                    "recovery_guidance": "Preview user runtime sync before applying it.",
                },
                "runtime_diagnostics": {
                    "schema_version": "sdk-skill-runtime-diagnostics.v1",
                    "selected_runtime_target": "codex",
                    "failed_gate": "codex_user_runtime_ready",
                    "expected_workspace_runtime": str(workspace_runtime.resolve(strict=False)),
                    "runtime_modes": {"codex_user_runtime": "missing_root"},
                    "missing_runtime_roots": [
                        {
                            "runtime": "codex_user_runtime",
                            "path": str(codex_handle.resolve(strict=False)),
                            "expected_under": str(workspace_runtime.resolve(strict=False)),
                        }
                    ],
                    "recovery_commands": [
                        {
                            "kind": "preview_user_runtime_sync",
                            "command": "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot",
                            "preconditions": ["Workspace flat projection validates cleanly."],
                            "permission_profile": {
                                "filesystem": "read workspace and user runtime links",
                                "network": "not required",
                            },
                            "expected_outcome": "Reports the user-runtime relink plan before mutation.",
                        },
                        {
                            "kind": "rerun_runtime_proof",
                            "command": "./bin/ask skills proof autofix --runtime-target codex --json --robot",
                            "preconditions": ["User runtime now points at the workspace projection."],
                            "permission_profile": {
                                "filesystem": "read workspace and user runtime links",
                                "network": "not required",
                            },
                            "expected_outcome": "Updates runtime evidence with pass or a narrower blocker.",
                        },
                    ],
                },
            }

            summary = runtime_adapters.emit_sdk_skill_runtime_evidence(
                repo_root=repo_root,
                proof=proof,
                actor_type="agent",
            )

            card_path = repo_root / summary["runtime_card_path"]
            card = json.loads(card_path.read_text(encoding="utf-8"))
            diagnostics = card["runtime_diagnostics"]
            self.assertEqual(
                diagnostics["expected_workspace_runtime"],
                "${WORKSPACE_ROOT}/.agents/skills",
            )
            self.assertEqual(
                card["verifier_results"][0]["runtime_diagnostics"],
                diagnostics,
            )
            self.assertEqual(
                diagnostics["missing_runtime_roots"][0]["expected_under"],
                "${WORKSPACE_ROOT}/.agents/skills",
            )
            recovery_commands = card["recovery_plan"]["next_commands"]
            self.assertEqual(
                recovery_commands[0]["command"],
                "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot",
            )
            self.assertEqual(
                recovery_commands[1]["command"],
                "./bin/ask skills proof autofix --runtime-target codex --json --robot",
            )
            process = self.run_validator(
                str(card_path),
                "--require-shared-workspace",
                "--workspace-root",
                "${WORKSPACE_ROOT}",
                "--json",
            )
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_runtime_card_attaches_codex_session_evidence_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            repo_root.mkdir()
            sessions_root = Path(temp_dir) / "sessions"
            rollout_path = sessions_root / "2026" / "05" / "25" / "rollout-session.jsonl"
            rollout_path.parent.mkdir(parents=True)
            session_id = "019e5d55-runtime-proof-session"
            turn_id = "019e5d55-runtime-proof-turn"
            observed_at = runtime_adapters._utc_now()
            rollout_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": observed_at,
                                "type": "session_meta",
                                "payload": {
                                    "id": session_id,
                                    "cwd": str(repo_root),
                                    "originator": "Codex Desktop",
                                    "thread_source": "root",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": observed_at,
                                "type": "turn_context",
                                "payload": {
                                    "turn_id": turn_id,
                                    "cwd": str(repo_root),
                                    "approval_policy": "on-request",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": observed_at,
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_started",
                                    "turn_id": turn_id,
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            proof = {
                "schema_version": "sdk-skill-proof.v1",
                "handle": "autofix",
                "runtime_target": "codex",
                "status": "pass",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                },
                "gates": {
                    "resolver": True,
                    "canonical_source_exists": True,
                    "codex_user_runtime_ready": True,
                },
                "gate_policy": {"required": ["codex_user_runtime_ready"]},
            }

            summary = runtime_adapters.emit_sdk_skill_runtime_evidence(
                repo_root=repo_root,
                proof=proof,
                actor_type="agent",
                codex_sessions_root=sessions_root,
                agents_otel_stats_path=Path(temp_dir) / "missing-stats.json",
            )

            self.assertEqual(summary["runtime_session_status"], "observed")
            card = json.loads((repo_root / summary["runtime_card_path"]).read_text(encoding="utf-8"))
            self.assertEqual(card["runtime_session"]["session_id"], session_id)
            self.assertEqual(card["runtime_session"]["latest_turn_id"], turn_id)
            self.assertEqual(card["thread_runs"][0]["thread_id"], session_id)
            self.assertEqual(card["thread_runs"][0]["cwd"], "${WORKSPACE_ROOT}")
            self.assertEqual(card["turn_events"][0]["turn_id"], turn_id)
            self.assertEqual(card["limitations"][0]["class"], "skill_invocation_not_asserted")
            process = self.run_validator(
                str(repo_root / summary["runtime_card_path"]),
                "--require-shared-workspace",
                "--workspace-root",
                "${WORKSPACE_ROOT}",
                "--json",
            )
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_runtime_card_attaches_agents_observability_stats_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            repo_root.mkdir()
            sessions_root = Path(temp_dir) / "sessions"
            rollout_path = sessions_root / "2026" / "05" / "25" / "rollout-session.jsonl"
            rollout_path.parent.mkdir(parents=True)
            session_id = "019e60a9-observed-session"
            turn_id = "019e60a9-observed-turn"
            observed_at = runtime_adapters._utc_now()
            rollout_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": observed_at,
                                "type": "session_meta",
                                "payload": {
                                    "id": session_id,
                                    "cwd": str(repo_root),
                                    "originator": "Codex Desktop",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": observed_at,
                                "type": "turn_context",
                                "payload": {"turn_id": turn_id, "cwd": str(repo_root)},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            stats_path = Path(temp_dir) / "stats.json"
            stats_path.write_text(
                json.dumps(
                    {
                        "last_ingest_at": "2026-05-25T19:57:15Z",
                        "last_ingest_by_kind": {
                            "logs": "2026-05-25T19:57:15Z",
                            "traces": "2026-05-25T19:56:20Z",
                        },
                        "skill_invocation_event_count": 0,
                        "plugin_backed_skill_invocation_count": 0,
                        "telemetry_confidence": {
                            "overall_status": "degraded",
                            "live_presence_by_signal": {"logs": {"codex": True}},
                            "signal_freshness": {
                                "logs": {"freshness": "fresh"},
                                "traces": {"freshness": "fresh"},
                            },
                            "reasons": ["auth ingest errors recorded"],
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            proof = {
                "schema_version": "sdk-skill-proof.v1",
                "handle": "autofix",
                "runtime_target": "codex",
                "status": "pass",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                },
                "gates": {"codex_user_runtime_ready": True},
                "gate_policy": {"required": ["codex_user_runtime_ready"]},
            }

            summary = runtime_adapters.emit_sdk_skill_runtime_evidence(
                repo_root=repo_root,
                proof=proof,
                actor_type="agent",
                codex_sessions_root=sessions_root,
                agents_otel_stats_path=stats_path,
            )
            self.assertEqual(summary["runtime_session_status"], "observed")
            self.assertEqual(summary["observability_status"], "observed")
            self.assertEqual(summary["status"], "partial")
            self.assertEqual(summary["claim_status"], "partial")
            self.assertEqual(summary["failed_check_id"], "runtime_observability_degraded")
            card = json.loads((repo_root / summary["runtime_card_path"]).read_text(encoding="utf-8"))
            receipt = json.loads((repo_root / summary["evidence_receipt_path"]).read_text(encoding="utf-8"))
            self.assertEqual(card["runtime_status"], "partial")
            self.assertEqual(card["runtime_session"]["runtime_status"], "partial")
            self.assertEqual(card["evidence_receipts"][0]["claim_status"], "partial")
            self.assertEqual(receipt["claim_status"], "partial")
            self.assertIn("observability is degraded", receipt["blocker"])
            self.assertEqual(card["runtime_session"]["observability"]["source"], "agents_otel_stats")
            self.assertTrue(card["runtime_session"]["observability"]["codex_log_presence"])
            self.assertEqual(
                card["runtime_session"]["observability"]["skill_invocation_event_count"],
                0,
            )
            self.assertTrue(
                any(run["source"] == "agents_otel_stats" for run in card["thread_runs"])
            )
            self.assertTrue(
                any(
                    event["event_type"] == "agents_observability_stats_observed"
                    for event in card["turn_events"]
                )
            )
            self.assertEqual(card["limitations"][0]["class"], "skill_invocation_not_asserted")
            _assert_partial_probe_and_recovery(self, repo_root, summary, card)
            process = self.run_validator(
                str(repo_root / summary["runtime_card_path"]),
                "--require-shared-workspace",
                "--workspace-root",
                "${WORKSPACE_ROOT}",
                "--json",
            )
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_runtime_card_marks_stale_codex_session_partial(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            repo_root.mkdir()
            sessions_root = Path(temp_dir) / "sessions"
            rollout_path = sessions_root / "2000" / "01" / "01" / "rollout-session.jsonl"
            rollout_path.parent.mkdir(parents=True)
            session_id = "019e60a9-stale-session"
            turn_id = "019e60a9-stale-turn"
            rollout_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2000-01-01T00:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": session_id,
                                    "cwd": str(repo_root),
                                    "originator": "Codex Desktop",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2000-01-01T00:00:01Z",
                                "type": "turn_context",
                                "payload": {"turn_id": turn_id, "cwd": str(repo_root)},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            proof = {
                "schema_version": "sdk-skill-proof.v1",
                "handle": "autofix",
                "runtime_target": "codex",
                "status": "pass",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                },
                "gates": {"codex_user_runtime_ready": True},
                "gate_policy": {"required": ["codex_user_runtime_ready"]},
            }

            summary = runtime_adapters.emit_sdk_skill_runtime_evidence(
                repo_root=repo_root,
                proof=proof,
                actor_type="agent",
                codex_sessions_root=sessions_root,
                agents_otel_stats_path=Path(temp_dir) / "missing-stats.json",
            )

            self.assertEqual(summary["status"], "partial")
            self.assertEqual(summary["claim_status"], "partial")
            self.assertEqual(summary["failed_check_id"], "runtime_session_stale")
            card = json.loads((repo_root / summary["runtime_card_path"]).read_text(encoding="utf-8"))
            self.assertEqual(card["runtime_status"], "partial")
            self.assertEqual(card["runtime_session"]["runtime_status"], "partial")
            self.assertIn("session evidence is stale", card["runtime_session"]["unavailable_reason"])

    def test_build_sdk_skill_proof_rejects_per_handle_symlink_without_user_runtime_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            workspace_runtime = repo_root / ".agents" / "skills"
            source_handle = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            source_handle.parent.mkdir(parents=True)
            source_handle.write_text("---\\nname: autofix\\n---\\n", encoding="utf-8")
            workspace_runtime.mkdir(parents=True)

            home_path = repo_root / ".tmp-home"
            codex_handle = home_path / ".codex" / "skills" / "autofix" / "SKILL.md"
            codex_handle.parent.mkdir(parents=True, exist_ok=True)
            codex_handle.symlink_to(source_handle)

            def resolve_skill_handle_fn(
                _handle: str,
                *,
                repo_root_path: Path,
            ) -> dict[str, object]:
                del repo_root_path
                return {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "runtime_visibility": "flat",
                }

            proof = runtime_adapters.build_sdk_skill_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="codex",
                resolve_skill_handle_fn=resolve_skill_handle_fn,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "fail")
            self.assertFalse(proof["gates"]["codex_user_link"])
            self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
            self.assertIsNone(proof["runtime_satisfied_by"])
            self.assertEqual(
                proof["runtime_diagnostics"]["runtime_modes"]["codex_user_runtime"],
                "foreign_or_unmanaged_root",
            )

    def test_build_sdk_skill_proof_accepts_flat_source_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            source_handle = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            source_handle.parent.mkdir(parents=True)
            source_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")

            workspace_runtime = repo_root / ".agents" / "skills"
            workspace_handle_dir = workspace_runtime / "autofix"
            workspace_handle_dir.parent.mkdir(parents=True)
            workspace_handle_dir.symlink_to(source_handle.parent)

            home_path = repo_root / ".tmp-home"
            agents_runtime = home_path / ".agents" / "skills"
            agents_runtime.parent.mkdir(parents=True, exist_ok=True)
            agents_runtime.symlink_to(workspace_runtime)

            def resolve_skill_handle_fn(
                _handle: str,
                *,
                repo_root_path: Path,
            ) -> dict[str, object]:
                del repo_root_path
                return {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "runtime_visibility": "flat",
                }

            proof = runtime_adapters.build_sdk_skill_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="agents",
                resolve_skill_handle_fn=resolve_skill_handle_fn,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "pass")
            self.assertTrue(proof["gates"]["agents_user_link"])
            self.assertTrue(proof["gates"]["agents_user_runtime_ready"])
            self.assertEqual(proof["runtime_satisfied_by"], "agents_user_runtime")

    def test_build_sdk_skill_proof_any_rejects_split_alias_with_valid_agents_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            source_handle = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            source_handle.parent.mkdir(parents=True)
            source_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")

            workspace_runtime = repo_root / ".agents" / "skills"
            workspace_handle_dir = workspace_runtime / "autofix"
            workspace_handle_dir.parent.mkdir(parents=True)
            workspace_handle_dir.symlink_to(source_handle.parent)

            home_path = repo_root / ".tmp-home"
            agents_runtime = home_path / ".agents" / "skills"
            agents_runtime.parent.mkdir(parents=True, exist_ok=True)
            agents_runtime.symlink_to(workspace_runtime)

            foreign_runtime = Path(temp_dir) / "foreign" / "skills"
            foreign_runtime.mkdir(parents=True)
            codex_runtime = home_path / ".codex" / "skills"
            codex_runtime.parent.mkdir(parents=True, exist_ok=True)
            codex_runtime.symlink_to(foreign_runtime)

            proof = runtime_adapters.build_sdk_skill_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="any",
                resolve_skill_handle_fn=_resolve_autofix_handle,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "fail")
            self.assertTrue(proof["gates"]["agents_user_runtime_ready"])
            self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
            self.assertFalse(proof["gates"]["user_runtime_alias_consistent"])
            self.assertEqual(proof["runtime_satisfied_by"], "agents_user_runtime")
            self.assertEqual(proof["runtime_diagnostics"]["failed_gate"], "user_runtime_alias_consistent")
            self.assertEqual(proof["runtime_diagnostics"]["runtime_aliases"]["status"], "split_brain")
            self.assertEqual(proof["runtime_failure"]["failed_check_id"], "user_runtime_alias_consistent")

    def test_build_sdk_skill_proof_uses_canonical_source_under_user_runtime_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            source_handle = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            source_handle.parent.mkdir(parents=True)
            source_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")

            external_handle = Path(temp_dir) / "external" / "autofix" / "SKILL.md"
            external_handle.parent.mkdir(parents=True)
            external_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")

            workspace_runtime = repo_root / ".agents" / "skills"
            workspace_runtime.mkdir(parents=True)
            (workspace_runtime / "autofix").symlink_to(external_handle.parent)

            home_path = repo_root / ".tmp-home"
            agents_runtime = home_path / ".agents" / "skills"
            agents_runtime.parent.mkdir(parents=True, exist_ok=True)
            agents_runtime.symlink_to(workspace_runtime)

            def resolve_skill_handle_fn(
                _handle: str,
                *,
                repo_root_path: Path,
            ) -> dict[str, object]:
                del repo_root_path
                return {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "runtime_visibility": "flat",
                }

            proof = runtime_adapters.build_sdk_skill_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="agents",
                resolve_skill_handle_fn=resolve_skill_handle_fn,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "pass")
            self.assertTrue(proof["gates"]["agents_user_link"])
            self.assertTrue(proof["gates"]["canonical_source_exists"])
            self.assertTrue(proof["gates"]["agents_user_runtime_ready"])
            self.assertEqual(proof["runtime_satisfied_by"], "agents_user_runtime")

    def test_build_sdk_skill_proof_reports_blocked_runtime_with_actionable_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            workspace_runtime = repo_root / ".agents" / "skills"
            source_handle = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            source_handle.parent.mkdir(parents=True)
            source_handle.write_text("---\\nname: autofix\\n---\\n", encoding="utf-8")
            workspace_handle_dir = workspace_runtime / "autofix"
            workspace_handle_dir.parent.mkdir(parents=True)
            workspace_handle_dir.symlink_to(source_handle.parent)

            home_path = repo_root / ".tmp-home"
            (home_path / ".codex" / "skills").mkdir(parents=True, exist_ok=True)

            agents_link = home_path / ".agents" / "skills"
            agents_link.parent.mkdir(parents=True, exist_ok=True)
            agents_link.symlink_to(workspace_runtime)

            def resolve_skill_handle_fn(
                _handle: str,
                *,
                repo_root_path: Path,
            ) -> dict[str, object]:
                del repo_root_path
                return {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "runtime_visibility": "flat",
                }

            proof = runtime_adapters.build_sdk_skill_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="codex",
                resolve_skill_handle_fn=resolve_skill_handle_fn,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "fail")
            runtime_failure = proof["runtime_failure"]
            self.assertEqual(runtime_failure["failed_check_id"], "codex_user_runtime_ready")
            self.assertEqual(proof["runtime_diagnostics"]["failed_gate"], "codex_user_runtime_ready")
            self.assertEqual(
                proof["runtime_diagnostics"]["runtime_modes"]["codex_user_runtime"],
                "foreign_or_unmanaged_root",
            )
            self.assertIn("dry-run", proof["runtime_diagnostics"]["recovery_risk"])
            recovery_kinds = {entry["kind"] for entry in proof["runtime_diagnostics"]["recovery_commands"]}
            self.assertTrue(
                {
                    "preview_user_runtime_sync",
                    "refresh_workspace_projection",
                    "apply_user_runtime_sync",
                    "rerun_runtime_proof",
                }.issubset(recovery_kinds)
            )
            recovery_commands = {
                entry["kind"]: entry["command"]
                for entry in proof["runtime_diagnostics"]["recovery_commands"]
            }
            self.assertEqual(
                recovery_commands["preview_user_runtime_sync"],
                "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot",
            )
            self.assertEqual(
                recovery_commands["refresh_workspace_projection"],
                "./bin/ask skills sync --scope workspace --projection flat --json --robot",
            )
            self.assertEqual(
                recovery_commands["apply_user_runtime_sync"],
                "./bin/ask skills sync --scope user --projection flat --json --robot",
            )

if __name__ == "__main__":
    unittest.main()
