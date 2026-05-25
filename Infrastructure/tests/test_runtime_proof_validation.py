from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import runtime_adapters  # noqa: E402

SCHEMAS_DIR = REPO_ROOT / "Infrastructure" / "config" / "schemas"
FIXTURES_DIR = REPO_ROOT / "Infrastructure" / "tests" / "fixtures" / "runtime_proof"
VALIDATOR = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "validate_runtime_cards.py"

SCHEMA_NAMES = [
    "runtime-card.v1.schema.json",
    "evidence-receipt.v1.schema.json",
    "artifact-record.v1.schema.json",
    "runtime-session-summary.v1.schema.json",
    "recovery-plan-summary.v1.schema.json",
]


def _load_validator_module() -> object:
    spec = importlib.util.spec_from_file_location("validate_runtime_cards", VALIDATOR)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestRuntimeProofValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            schema_name: json.loads((SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"))
            for schema_name in SCHEMA_NAMES
        }

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
                "schema_version": "command-handle-proof.v2",
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

            summary = runtime_adapters.emit_command_handle_runtime_evidence(
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
                "schema_version": "command-handle-proof.v2",
                "handle": "autofix",
                "runtime_target": "codex",
                "status": "fail",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "command_handle_path": ".agents/skills/autofix/SKILL.md",
                },
                "gates": {
                    "resolver": True,
                    "generated_command_handle_check": True,
                    "workspace_command_handle_exists": True,
                    "codex_user_runtime_ready": False,
                },
                "gate_policy": {"required": ["codex_user_runtime_ready"]},
                "runtime_failure": {
                    "failed_check_id": "codex_user_runtime_ready",
                    "message": "Codex runtime handle is unavailable.",
                    "recovery_guidance": "Preview user runtime sync before applying it.",
                },
                "runtime_diagnostics": {
                    "schema_version": "command-handle-runtime-diagnostics.v1",
                    "selected_runtime_target": "codex",
                    "failed_gate": "codex_user_runtime_ready",
                    "expected_workspace_runtime": str(workspace_runtime.resolve(strict=False)),
                    "runtime_modes": {"codex_user_runtime": "missing_root"},
                    "missing_command_handles": [
                        {
                            "runtime": "codex_user_runtime",
                            "path": str(codex_handle.resolve(strict=False)),
                            "expected_under": str(workspace_runtime.resolve(strict=False)),
                        }
                    ],
                    "recovery_commands": [
                        {
                            "kind": "preview_user_runtime_sync",
                            "command": "./bin/ask skills sync --scope user --projection rooted --dry-run --json --robot",
                            "preconditions": ["Workspace rooted projection validates cleanly."],
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

            summary = runtime_adapters.emit_command_handle_runtime_evidence(
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
                diagnostics["missing_command_handles"][0]["expected_under"],
                "${WORKSPACE_ROOT}/.agents/skills",
            )
            recovery_commands = card["recovery_plan"]["next_commands"]
            self.assertEqual(
                recovery_commands[0]["command"],
                "./bin/ask skills sync --scope user --projection rooted --dry-run --json --robot",
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
            rollout_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-25T18:00:00Z",
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
                                "timestamp": "2026-05-25T18:00:01Z",
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
                                "timestamp": "2026-05-25T18:00:02Z",
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
                "schema_version": "command-handle-proof.v2",
                "handle": "autofix",
                "runtime_target": "codex",
                "status": "pass",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "command_handle_path": ".agents/skills/autofix/SKILL.md",
                },
                "gates": {
                    "resolver": True,
                    "generated_command_handle_check": True,
                    "workspace_command_handle_exists": True,
                    "codex_user_runtime_ready": True,
                },
                "gate_policy": {"required": ["codex_user_runtime_ready"]},
            }

            summary = runtime_adapters.emit_command_handle_runtime_evidence(
                repo_root=repo_root,
                proof=proof,
                actor_type="agent",
                codex_sessions_root=sessions_root,
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

    def test_build_command_handle_proof_accepts_handle_bridge_without_root_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            workspace_runtime = repo_root / ".agents" / "skills"
            workspace_handle = workspace_runtime / "autofix" / "SKILL.md"
            workspace_handle.parent.mkdir(parents=True)
            workspace_handle.write_text("---\\nname: autofix\\n---\\n", encoding="utf-8")

            home_path = repo_root / ".tmp-home"
            codex_handle = home_path / ".codex" / "skills" / "autofix" / "SKILL.md"
            codex_handle.parent.mkdir(parents=True, exist_ok=True)
            codex_handle.symlink_to(workspace_handle)

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
                    "command_handle_path": ".agents/skills/autofix/SKILL.md",
                }

            def check_command_handles_fn(*, repo_root_path: Path) -> dict[str, object]:
                del repo_root_path
                return {"status": "pass", "violations": []}

            proof = runtime_adapters.build_command_handle_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="codex",
                resolve_skill_handle_fn=resolve_skill_handle_fn,
                check_command_handles_fn=check_command_handles_fn,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "pass")
            self.assertFalse(proof["gates"]["codex_user_link"])
            self.assertTrue(proof["gates"]["codex_user_command_handle_exists"])
            self.assertTrue(proof["gates"]["codex_user_command_handle_points_to_workspace"])
            self.assertTrue(proof["gates"]["codex_user_runtime_ready"])
            self.assertEqual(proof["runtime_satisfied_by"], "codex_user_runtime")
            self.assertEqual(
                proof["runtime_diagnostics"]["runtime_modes"]["codex_user_runtime"],
                "handle_bridge",
            )
            missing = proof["runtime_diagnostics"]["missing_command_handles"]
            self.assertTrue(any(entry["runtime"] == "agents_user_runtime" for entry in missing))
            self.assertFalse(any(entry["runtime"] == "codex_user_runtime" for entry in missing))

    def test_build_command_handle_proof_reports_blocked_runtime_with_actionable_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            workspace_runtime = repo_root / ".agents" / "skills"
            workspace_handle = workspace_runtime / "autofix" / "SKILL.md"
            workspace_handle.parent.mkdir(parents=True)
            workspace_handle.write_text("---\\nname: autofix\\n---\\n", encoding="utf-8")

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
                    "command_handle_path": ".agents/skills/autofix/SKILL.md",
                }

            def check_command_handles_fn(*, repo_root_path: Path) -> dict[str, object]:
                del repo_root_path
                return {"status": "pass", "violations": []}

            proof = runtime_adapters.build_command_handle_proof(
                repo_root=repo_root,
                handle="autofix",
                runtime_target="codex",
                resolve_skill_handle_fn=resolve_skill_handle_fn,
                check_command_handles_fn=check_command_handles_fn,
                home_path=home_path,
            )

            self.assertEqual(proof["status"], "fail")
            runtime_failure = proof["runtime_failure"]
            self.assertEqual(runtime_failure["failed_check_id"], "codex_user_runtime_ready")
            self.assertEqual(proof["runtime_diagnostics"]["failed_gate"], "codex_user_runtime_ready")
            missing = proof["runtime_diagnostics"]["missing_command_handles"]
            self.assertTrue(any(entry["runtime"] == "codex_user_runtime" for entry in missing))
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

    def test_schema_files_accept_valid_runtime_card_fixture(self) -> None:
        payload = json.loads((FIXTURES_DIR / "valid-runtime-card.json").read_text(encoding="utf-8"))

        _validate_schema_subset(self.schemas["runtime-card.v1.schema.json"], payload, self.schemas)

    def test_validator_contract_primitives_match_schema_enums_and_conditionals(self) -> None:
        validator = _load_validator_module()

        runtime_card_schema = self.schemas["runtime-card.v1.schema.json"]
        receipt_schema = self.schemas["evidence-receipt.v1.schema.json"]
        artifact_schema = self.schemas["artifact-record.v1.schema.json"]
        session_schema = self.schemas["runtime-session-summary.v1.schema.json"]
        recovery_schema = self.schemas["recovery-plan-summary.v1.schema.json"]

        self.assertEqual(set(runtime_card_schema["definitions"]["runtimeTarget"]["enum"]), validator._runtime_targets())
        self.assertEqual(set(receipt_schema["definitions"]["runtimeTarget"]["enum"]), validator._runtime_targets())
        self.assertEqual(set(session_schema["definitions"]["runtimeTarget"]["enum"]), validator._runtime_targets())
        self.assertEqual(set(runtime_card_schema["definitions"]["runtimeStatus"]["enum"]), validator._runtime_statuses())
        self.assertEqual(set(receipt_schema["definitions"]["runtimeStatus"]["enum"]), validator._runtime_statuses())
        self.assertEqual(set(session_schema["definitions"]["runtimeStatus"]["enum"]), validator._runtime_statuses())
        self.assertEqual(set(recovery_schema["definitions"]["runtimeStatus"]["enum"]), validator._runtime_statuses())
        self.assertEqual(set(receipt_schema["definitions"]["claimStatus"]["enum"]), validator._claim_statuses())
        self.assertEqual(set(artifact_schema["definitions"]["claimStatus"]["enum"]), validator._claim_statuses())
        self.assertEqual(set(receipt_schema["properties"]["evidence_type"]["enum"]), validator._evidence_types())
        self.assertEqual(set(runtime_card_schema["definitions"]["actorType"]["enum"]), validator._actor_types())
        self.assertEqual(set(artifact_schema["definitions"]["actorType"]["enum"]), validator._actor_types())
        self.assertEqual(set(session_schema["definitions"]["actorType"]["enum"]), validator._actor_types())
        self.assertEqual(set(runtime_card_schema["definitions"]["mutationScope"]["enum"]), validator._mutation_scopes())
        self.assertEqual(set(artifact_schema["definitions"]["mutationScope"]["enum"]), validator._mutation_scopes())
        self.assertEqual(set(runtime_card_schema["definitions"]["visibilityStatus"]["enum"]), validator._visibility_statuses())
        self.assertEqual(set(artifact_schema["definitions"]["visibilityStatus"]["enum"]), validator._visibility_statuses())
        self.assertEqual(set(session_schema["definitions"]["visibilityStatus"]["enum"]), validator._visibility_statuses())
        self.assertEqual(set(artifact_schema["properties"]["artifact_type"]["enum"]), validator._artifact_types())

        conditional_requirements = {}
        for rule in receipt_schema["allOf"]:
            field, condition = tuple(rule["if"]["properties"].items())[0]
            marker = condition.get("const", tuple(condition.get("enum", [])))
            conditional_requirements[(field, marker)] = set(rule["then"]["required"])
        self.assertEqual(conditional_requirements[("evidence_type", "command")], {"command", "exit_code"})
        self.assertEqual(
            conditional_requirements[("runtime_status", "blocked_runtime")],
            {"probe_command", "probe_exit_code", "probe_artifact_path", "blocker_class"},
        )
        self.assertEqual(conditional_requirements[("claim_status", ("blocked", "partial"))], {"blocker"})

    def test_validator_accepts_valid_runtime_card_fixture(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "valid-runtime-card.json"), "--require-shared-workspace", "--json")

        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["checked"][0]["kind"], "runtime_card")

    def test_validator_rejects_command_receipt_without_command(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-missing-command.json"), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("command", fields)

    def test_validator_rejects_receipt_without_runtime_target(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-missing-runtime-target.json"), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("runtime_target", fields)

    def test_validator_rejects_blocked_runtime_without_blocker_class(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-missing-blocker-class.json"), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("blocker_class", fields)

    def test_shared_workspace_gate_rejects_agent_only_visibility(self) -> None:
        process = self.run_validator(
            str(FIXTURES_DIR / "invalid-agent-only-artifact.json"),
            "--require-shared-workspace",
            "--json",
        )

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("visibility_status", fields)

    def test_shared_workspace_gate_rejects_foreign_workspace_root(self) -> None:
        process = self.run_validator(
            str(FIXTURES_DIR / "valid-runtime-card.json"),
            "--require-shared-workspace",
            "--workspace-root",
            "/tmp/other-checkout",
            "--json",
        )

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("workspace_root", fields)

    def test_validator_accepts_standalone_runtime_session_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "valid-runtime-session-summary.json"), "--json")

        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked"][0]["kind"], "runtime_session_summary")

    def test_validator_rejects_invalid_runtime_session_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-runtime-session-summary.json"), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("runtime_target", fields)

    def test_validator_accepts_standalone_recovery_plan_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "valid-recovery-plan-summary.json"), "--json")

        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked"][0]["kind"], "recovery_plan_summary")

    def test_validator_rejects_invalid_recovery_plan_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-recovery-plan-summary.json"), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        fields = {finding["field"] for finding in payload["findings"]}
        self.assertIn("command", fields)

    def test_validator_accepts_evidence_directory(self) -> None:
        process = self.run_validator("--evidence-dir", str(FIXTURES_DIR), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        checked_paths = {Path(item["path"]).name for item in payload["checked"]}
        self.assertNotIn("unrelated-tool-output.json", checked_paths)
        self.assertIn("valid-runtime-card.json", checked_paths)
        self.assertIn("valid-runtime-session-summary.json", checked_paths)
        self.assertIn("valid-recovery-plan-summary.json", checked_paths)
        self.assertGreaterEqual(len(payload["findings"]), 3)

    def test_validator_rejects_explicit_unknown_json_path(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "unrelated-tool-output.json"), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked"][0]["kind"], "unknown")
        self.assertEqual(payload["findings"][0]["kind"], "unknown")
        self.assertEqual(payload["findings"][0]["message"], "could not infer runtime proof artifact kind")

    def test_validator_reports_missing_explicit_file(self) -> None:
        missing_path = FIXTURES_DIR / "does-not-exist.json"
        process = self.run_validator(str(missing_path), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked_count"], 0)
        self.assertEqual(payload["findings"][0]["path"], str(missing_path))
        self.assertEqual(payload["findings"][0]["kind"], "unknown")
        self.assertEqual(payload["findings"][0]["message"], "file does not exist")

    def test_validator_reports_invalid_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_json_path = Path(temp_dir) / "broken-runtime-card.json"
            invalid_json_path.write_text("{not json", encoding="utf-8")

            process = self.run_validator(str(invalid_json_path), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked_count"], 0)
        self.assertEqual(payload["findings"][0]["path"], str(invalid_json_path))
        self.assertEqual(payload["findings"][0]["kind"], "unknown")
        self.assertTrue(payload["findings"][0]["message"].startswith("invalid JSON:"))

    def test_validator_reports_invalid_schema_json(self) -> None:
        validator = _load_validator_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_schema_dir = Path(temp_dir)
            for schema_name in SCHEMA_NAMES:
                (temp_schema_dir / schema_name).write_text(
                    (SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            (temp_schema_dir / "runtime-card.v1.schema.json").write_text("{not json", encoding="utf-8")

            validator._schema_dir = lambda: temp_schema_dir
            findings = validator._schema_findings()

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "runtime_card")
        self.assertEqual(findings[0].field, "$")
        self.assertTrue(findings[0].message.startswith("schema JSON is invalid:"))

    def test_evidence_directory_with_only_unknown_json_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_dir = Path(temp_dir)
            (evidence_dir / "unrelated.json").write_text('{"tool": "not-runtime-proof"}', encoding="utf-8")

            process = self.run_validator("--evidence-dir", str(evidence_dir), "--json")

        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked_count"], 0)
        self.assertEqual(payload["findings"][0]["message"], "no runtime proof artifacts found")

    def test_conditional_enum_matching_is_order_insensitive(self) -> None:
        validator = _load_validator_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_schema_dir = Path(temp_dir)
            for schema_name in SCHEMA_NAMES:
                (temp_schema_dir / schema_name).write_text(
                    (SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            receipt_path = temp_schema_dir / "evidence-receipt.v1.schema.json"
            receipt_schema = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_schema["allOf"][2]["if"]["properties"]["claim_status"]["enum"] = ["partial", "blocked"]
            receipt_path.write_text(json.dumps(receipt_schema), encoding="utf-8")
            validator._schema_dir = lambda: temp_schema_dir

            required = validator._schema_conditional_required(
                "evidence-receipt.v1.schema.json",
                "claim_status",
                ("blocked", "partial"),
            )

        self.assertEqual(required, ["blocker"])

    def test_single_value_conditional_enum_matches_string_marker(self) -> None:
        validator = _load_validator_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_schema_dir = Path(temp_dir)
            for schema_name in SCHEMA_NAMES:
                (temp_schema_dir / schema_name).write_text(
                    (SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            receipt_path = temp_schema_dir / "evidence-receipt.v1.schema.json"
            receipt_schema = json.loads(receipt_path.read_text(encoding="utf-8"))
            evidence_type_condition = receipt_schema["allOf"][0]["if"]["properties"]["evidence_type"]
            evidence_type_condition.pop("const")
            evidence_type_condition["enum"] = ["command"]
            receipt_path.write_text(json.dumps(receipt_schema), encoding="utf-8")
            validator._schema_dir = lambda: temp_schema_dir

            required = validator._schema_conditional_required(
                "evidence-receipt.v1.schema.json",
                "evidence_type",
                "command",
            )

        self.assertEqual(required, ["command", "exit_code"])


if __name__ == "__main__":
    unittest.main()
