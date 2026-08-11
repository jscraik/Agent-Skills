import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.commands.skills_impl import (  # noqa: E402
    _doctor_sdk_layer_for,
    _skill_doctor_operation_context,
    _skill_doctor_next_command_decision,
    _skill_package_operation_context,
    skills_doctor,
    skills_proof,
    skills_sdk_check,
)
from ask.envelope import CallResult, ErrorObject  # noqa: E402
from helpers.schema_validator import (  # noqa: E402
    _validate_schema_subset,
)


def _assert_skill_doctor_schema_validates(test_case: unittest.TestCase, payload: dict) -> None:
    schema_path = (
        REPO_ROOT / "Infrastructure" / "config" / "schemas" / "skill-doctor.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        _validate_schema_subset(schema, payload, {})
    except AssertionError as exc:
        test_case.fail(f"skill-doctor schema validation failed: {exc}")


def _load_skill_doctor_schema() -> dict:
    schema_path = (
        REPO_ROOT / "Infrastructure" / "config" / "schemas" / "skill-doctor.v1.schema.json"
    )
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _proof_result(handle: str, status: str = "pass", runtime_target: str = "any") -> CallResult:
    result = CallResult(status="success" if status == "pass" else "error")
    result.data["proof"] = {
        "schema_version": "command-handle-proof.v2",
        "handle": handle,
        "runtime_target": runtime_target,
        "status": status,
        "gates": {
            "resolver": status == "pass",
            "canonical_source_exists": status == "pass",
            "codex_user_link": status == "pass",
            "codex_user_runtime_ready": status == "pass",
            "user_runtime_ready": status == "pass",
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
    def test_doctor_accepts_legacy_positional_flags(self) -> None:
        captured: dict[str, object] = {}

        def fake_doctor(_repo_root: Path, _target: str, **options: object) -> CallResult:
            captured.update(options)
            return CallResult()

        with patch("ask.commands.skills_impl._skills_doctor", side_effect=fake_doctor):
            skills_doctor(REPO_ROOT, "autofix", True, True, "source")

        self.assertEqual(captured, {"strict": True, "codex_parity": True, "validation_scope": "source"})

    def test_doctor_merges_legacy_positional_and_keyword_options(self) -> None:
        captured: dict[str, object] = {}

        def fake_doctor(_repo_root: Path, _target: str, **options: object) -> CallResult:
            captured.update(options)
            return CallResult()

        with patch("ask.commands.skills_impl._skills_doctor", side_effect=fake_doctor):
            skills_doctor(REPO_ROOT, "autofix", True, validation_scope="source")

        self.assertEqual(
            captured,
            {"strict": True, "codex_parity": False, "validation_scope": "source"},
        )

    def test_sdk_check_accepts_legacy_positional_flags(self) -> None:
        captured: dict[str, object] = {}

        def fake_sdk_check(_repo_root: Path, _target: str, **options: object) -> CallResult:
            captured.update(options)
            return CallResult()

        with patch("ask.commands.skills_impl._skills_sdk_check", side_effect=fake_sdk_check):
            skills_sdk_check(REPO_ROOT, "autofix", True, True)

        self.assertEqual(captured, {"strict": True, "codex_parity": True})

    def test_sdk_check_rejects_unsupported_validation_scope_keyword(self) -> None:
        with self.assertRaisesRegex(TypeError, "validation_scope"):
            skills_sdk_check(REPO_ROOT, "autofix", validation_scope="source")

    def test_operation_context_events_are_json_serializable(self) -> None:
        for context in (_skill_package_operation_context(), _skill_doctor_operation_context()):
            with self.subTest(primary_profile=context["primary_profile"]):
                json.dumps(context)
                self.assertTrue(all(isinstance(event, dict) for event in context["events"].values()))

    def test_runtime_target_codex_fails_closed_when_only_agents_runtime_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            repo_root = sandbox / "repo"
            canonical_source = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            canonical_source.parent.mkdir(parents=True)
            canonical_source.write_text("---\nname: autofix\n---\n", encoding="utf-8")
            workspace_handle = repo_root / ".agents" / "skills" / "autofix" / "SKILL.md"
            workspace_handle.parent.mkdir(parents=True)
            workspace_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")
            home = sandbox / "home"
            home.mkdir()
            (home / ".agents").mkdir()
            (home / ".agents" / "skills").symlink_to(repo_root / ".agents" / "skills")
            (home / ".codex").mkdir()

            resolution = {
                "status": "ok",
                "handle": "autofix",
                "source_path": "Skills/agent-ops/autofix/SKILL.md",
            }

            with (
                patch("ask.commands.skills_impl.Path.home", return_value=home),
                patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            ):
                default_result = skills_proof(repo_root, "autofix")
                codex_result = skills_proof(repo_root, "autofix", runtime_target="codex")
                agents_result = skills_proof(repo_root, "autofix", runtime_target="agents")

            default_proof = default_result.data["proof"]
            self.assertEqual(default_result.status, "success")
            self.assertEqual(default_proof["runtime_target"], "any")
            self.assertEqual(default_proof["runtime_satisfied_by"], "agents_user_runtime")
            self.assertTrue(default_proof["gates"]["agents_user_runtime_ready"])
            self.assertFalse(default_proof["gates"]["codex_user_runtime_ready"])

            codex_proof = codex_result.data["proof"]
            self.assertEqual(codex_result.status, "error")
            self.assertEqual(codex_proof["runtime_target"], "codex")
            self.assertEqual(codex_proof["status"], "fail")
            self.assertIsNone(codex_proof["runtime_satisfied_by"])
            self.assertIn("agents_user_runtime", codex_proof["available_runtimes"])
            self.assertEqual(
                codex_proof["validation_commands"],
                ["./bin/ask skills proof autofix --runtime-target codex --json --robot"],
            )
            self.assertIn("codex_user_runtime_ready", codex_proof["gate_policy"]["required"])
            self.assertEqual(
                codex_proof["runtime_failure"]["failed_check_id"],
                "codex_user_runtime_ready",
            )
            diagnostics = codex_proof["runtime_diagnostics"]
            self.assertEqual(diagnostics["failed_gate"], "codex_user_runtime_ready")
            self.assertEqual(
                diagnostics["runtime_modes"]["codex_user_runtime"],
                "missing_root",
            )
            self.assertEqual(
                diagnostics["runtime_modes"]["agents_user_runtime"],
                "root_symlink",
            )
            self.assertIn("preview_user_runtime_sync", [
                item["kind"] for item in diagnostics["recovery_commands"]
            ])

            agents_proof = agents_result.data["proof"]
            self.assertEqual(agents_result.status, "success")
            self.assertEqual(agents_proof["runtime_target"], "agents")
            self.assertEqual(agents_proof["runtime_satisfied_by"], "agents_user_runtime")
            self.assertIn("agents_user_runtime_ready", agents_proof["gate_policy"]["required"])

    def test_runtime_target_codex_rejects_per_handle_workspace_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            repo_root = sandbox / "repo"
            canonical_source = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            canonical_source.parent.mkdir(parents=True)
            canonical_source.write_text("---\nname: autofix\n---\n", encoding="utf-8")
            workspace_handle = repo_root / ".agents" / "skills" / "autofix" / "SKILL.md"
            workspace_handle.parent.mkdir(parents=True)
            workspace_handle.write_text("---\nname: autofix\n---\n", encoding="utf-8")
            home = sandbox / "home"
            codex_root = home / ".codex" / "skills"
            codex_root.mkdir(parents=True)
            (codex_root / "autofix").symlink_to(workspace_handle.parent)
            (home / ".agents").mkdir()

            resolution = {
                "status": "ok",
                "handle": "autofix",
                "source_path": "Skills/agent-ops/autofix/SKILL.md",
            }

            with (
                patch("ask.commands.skills_impl.Path.home", return_value=home),
                patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            ):
                result = skills_proof(repo_root, "autofix", runtime_target="codex")

            proof = result.data["proof"]
            self.assertEqual(result.status, "error")
            self.assertEqual(proof["status"], "fail")
            self.assertEqual(proof["runtime_target"], "codex")
            self.assertIsNone(proof["runtime_satisfied_by"])
            self.assertFalse(proof["gates"]["codex_user_link"])
            self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
            self.assertEqual(
                proof["runtime_diagnostics"]["runtime_modes"]["codex_user_runtime"],
                "foreign_or_unmanaged_root",
            )
            self.assertIn("runtime_failure", proof)

    def test_runtime_target_rejects_invalid_value_before_resolution(self) -> None:
        result = skills_proof(REPO_ROOT, "autofix", runtime_target="cloud")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        proof = result.data["proof"]
        self.assertEqual(proof["status"], "fail")
        self.assertEqual(proof["runtime_target"], "cloud")
        self.assertEqual(proof["gate_policy"]["required"], ["runtime_target"])
        failure = result.data["runtime_failure"]
        self.assertEqual(failure["schema_version"], "skill-runtime-failure.v1")
        self.assertEqual(failure["error_code"], "ERR_VALIDATION")
        self.assertEqual(failure["failed_check_id"], "runtime_target")
        self.assertEqual(failure["path"], "runtime_target")
        self.assertEqual(proof["runtime_failure"], failure)
        self.assertIn("--runtime-target any", failure["validation_commands"][0])

    def test_runtime_target_normalizes_noncanonical_values(self) -> None:
        spaced_result = skills_proof(REPO_ROOT, "autofix", runtime_target=" CoDeX ")
        none_result = skills_proof(REPO_ROOT, "autofix", runtime_target=None)

        spaced_proof = spaced_result.data["proof"]
        self.assertEqual(spaced_proof["runtime_target"], "codex")
        self.assertIn("codex_user_runtime_ready", spaced_proof["gate_policy"]["required"])

        none_proof = none_result.data["proof"]
        self.assertEqual(none_result.status, "error")
        self.assertEqual(none_proof["runtime_target"], "none")
        self.assertEqual(none_proof["gate_policy"]["required"], ["runtime_target"])
        self.assertEqual(
            none_result.data["runtime_failure"]["failed_check_id"],
            "runtime_target",
        )

    def test_cli_runtime_target_rejects_invalid_value_with_runtime_failure_json(self) -> None:
        process = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "Infrastructure" / "bin" / "ask"),
                "skills",
                "proof",
                "autofix",
                "--runtime-target",
                "cloud",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(process.returncode, 2, process.stderr)
        payload = json.loads(process.stdout)
        proof = payload["data"]["proof"]
        failure = payload["data"]["runtime_failure"]
        self.assertEqual(payload["status"], "error")
        self.assertEqual(proof["status"], "fail")
        self.assertEqual(proof["runtime_target"], "cloud")
        self.assertEqual(failure["schema_version"], "skill-runtime-failure.v1")
        self.assertEqual(failure["error_code"], "ERR_VALIDATION")
        self.assertEqual(failure["failed_check_id"], "runtime_target")
        self.assertEqual(failure["path"], "runtime_target")
        self.assertIn("--runtime-target any", failure["validation_commands"][0])
        self.assertIn("Use --runtime-target any", failure["recovery_guidance"])

    def test_schema_subset_validator_rejects_missing_required_doctor_fields(self) -> None:
        schema = _load_skill_doctor_schema()
        invalid_payload = {
            "schema_version": "skill-doctor.v1",
            "query": "autofix",
        }

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(schema, invalid_payload, {})

        self.assertIn("missing required key", str(context.exception))

    def test_doctor_reports_warning_for_reachable_skill_with_package_gaps(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
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
        self.assertEqual(doctor["checks"]["runtime_reachability"]["runtime_target"], "any")
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
        self.assertEqual(
            doctor["contract_schemas"]["doctor"]["path"],
            "Infrastructure/config/schemas/skill-doctor.v1.schema.json",
        )
        self.assertEqual(doctor["contract_schema_versions"]["doctor"], "skill-doctor.v1")
        self.assertIn("blocked_user_input", doctor["readiness_taxonomy"]["blockers"])
        self.assertIn("timeout_no_output", doctor["readiness_taxonomy"]["blockers"])
        self.assertIn("strict_audit_not_run", doctor["readiness_taxonomy"]["warnings"])
        self.assertEqual(doctor["lifecycle_event"]["schema_version"], "capability-lifecycle-event.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_type"], "skill_doctor_completed")
        self.assertIn("eval_blocked", doctor["lifecycle_event_types"])
        self.assertEqual(len(doctor["warnings"]), 1)
        _assert_skill_doctor_schema_validates(self, doctor)

    def test_doctor_accepts_current_release_aggregate_as_outcome_proof(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
        }
        release_evidence = {
            "status": "pass",
            "evidence_class": "oss_local_release_aggregate",
            "evidence_ref": "Infrastructure/artifacts/skills/autofix/current/aggregate.json",
            "evidence_digest": "sha256:release-proof",
            "scenario_set": "autofix-release-8-v1",
            "case_count": 8,
        }

        with (
            patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            patch("ask.commands.skills_impl.skills_proof", return_value=_proof_result("autofix")),
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=[]),
            patch("ask.commands.skills_impl._eval_shard_outcome_proof", return_value=release_evidence),
        ):
            result = skills_doctor(REPO_ROOT, "autofix")

        doctor = result.data["skill_doctor"]
        self.assertEqual(doctor["checks"]["outcome_proof"]["status"], "pass")
        self.assertEqual(
            doctor["checks"]["outcome_proof"]["evidence_class"],
            "oss_local_release_aggregate",
        )
        self.assertEqual(
            doctor["checks"]["outcome_proof"]["evidence_ref"],
            "Infrastructure/artifacts/skills/autofix/current/aggregate.json",
        )
        self.assertNotIn(
            "outcome_proof_missing",
            [warning["class"] for warning in doctor["warnings"]],
        )
        _assert_skill_doctor_schema_validates(self, doctor)

    def test_doctor_blocks_when_runtime_reachability_fails(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
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
        _assert_skill_doctor_schema_validates(self, doctor)

    def test_doctor_codex_parity_uses_codex_targeted_runtime_proof(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
        }
        proof_calls = []

        def _codex_proof(
            repo_root: Path,
            handle: str,
            runtime_target: str = "any",
        ) -> CallResult:
            proof_calls.append((handle, runtime_target))
            return _proof_result(handle, status="fail", runtime_target=runtime_target)

        with (
            patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            patch("ask.commands.skills_impl.skills_proof", side_effect=_codex_proof),
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=["agent-ops/autofix"]),
        ):
            result = skills_doctor(REPO_ROOT, "autofix", codex_parity=True)

        self.assertEqual(proof_calls, [("autofix", "codex")])
        self.assertEqual(result.status, "error")
        doctor = result.data["skill_doctor"]
        runtime_check = doctor["checks"]["runtime_reachability"]
        self.assertEqual(runtime_check["status"], "fail")
        self.assertTrue(runtime_check["codex_parity"])
        self.assertEqual(runtime_check["runtime_target"], "codex")
        self.assertEqual(
            runtime_check["command"],
            "./bin/ask skills proof autofix --runtime-target codex --json --robot",
        )
        self.assertEqual(doctor["next_command"], runtime_check["command"])
        self.assertEqual(doctor["next_command_decision"]["command"], runtime_check["command"])
        self.assertEqual(doctor["next_command_decision"]["source_class"], "blocked_runtime")
        self.assertEqual(doctor["next_command_decision"]["source_check"], "runtime_reachability")
        self.assertIn("blocked_runtime", doctor["next_command_decision"]["reason"])
        self.assertIn("blocked_runtime", doctor["lifecycle_event"]["outcome"]["blocker_classes"])
        _assert_skill_doctor_schema_validates(self, doctor)

    def test_doctor_preserves_runtime_failure_context_in_runtime_check(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
        }
        proof_result = CallResult(status="error")
        proof_result.data["runtime_failure"] = {
            "schema_version": "skill-runtime-failure.v1",
            "command": "skills proof",
            "error_code": "ERR_VALIDATION",
            "failed_check_id": "codex_user_runtime_ready",
            "path": "gates.codex_user_runtime_ready",
            "message": "Codex runtime proof failed.",
            "recovery_guidance": "Sync the Codex user runtime and rerun proof.",
            "validation_commands": [
                "./bin/ask skills proof autofix --runtime-target codex --json --robot"
            ],
        }

        with (
            patch("ask.commands.skills_impl.resolve_skill_handle", return_value=resolution),
            patch("ask.commands.skills_impl.skills_proof", return_value=proof_result),
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=[]),
        ):
            result = skills_doctor(REPO_ROOT, "autofix", codex_parity=True)

        self.assertEqual(result.status, "error")
        runtime_check = result.data["skill_doctor"]["checks"]["runtime_reachability"]
        self.assertEqual(runtime_check["runtime_failure"], proof_result.data["runtime_failure"])
        self.assertEqual(runtime_check["error_code"], "ERR_VALIDATION")
        self.assertEqual(runtime_check["failed_check_id"], "codex_user_runtime_ready")
        self.assertEqual(runtime_check["path"], "gates.codex_user_runtime_ready")
        self.assertEqual(
            runtime_check["recovery_guidance"],
            "Sync the Codex user runtime and rerun proof.",
        )
        _assert_skill_doctor_schema_validates(self, result.data["skill_doctor"])

    def test_doctor_codex_parity_blocks_path_targets_without_skill_handle(self) -> None:
        with (
            patch("ask.commands.skills_impl.audit_skill", return_value=_audit_result()),
            patch("ask.commands.skills_impl._skill_workout_candidates", return_value=[]),
        ):
            result = skills_doctor(REPO_ROOT, "Skills/agent-ops/autofix", codex_parity=True)

        self.assertEqual(result.status, "error")
        doctor = result.data["skill_doctor"]
        runtime_check = doctor["checks"]["runtime_reachability"]
        self.assertEqual(runtime_check["status"], "fail")
        self.assertTrue(runtime_check["codex_parity"])
        self.assertEqual(runtime_check["runtime_target"], "codex")
        self.assertEqual(
            runtime_check["reason"],
            "Codex parity requires an SDK skill handle so Codex runtime proof can run.",
        )
        self.assertIn("blocked_runtime", doctor["lifecycle_event"]["outcome"]["blocker_classes"])
        _assert_skill_doctor_schema_validates(self, doctor)

    def test_doctor_selects_structural_audit_next_when_validation_blocks(self) -> None:
        resolution = {
            "status": "ok",
            "handle": "autofix",
            "source_path": "Skills/agent-ops/autofix/SKILL.md",
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
                    _skill_doctor_next_command_decision(
                        blockers=case["blockers"],
                        warnings=case["warnings"],
                        checks=case["checks"],
                        normalized_handle=case["handle"],
                        query=case["query"],
                        audit_target=case["audit_target"],
                        strict=case["strict"],
                    )["command"],
                    case["expected"],
                )

    def test_doctor_next_command_decision_explains_precedence(self) -> None:
        decision = _skill_doctor_next_command_decision(
            blockers=[{"class": "blocked_runtime"}],
            warnings=[{"class": "outcome_proof_missing"}],
            checks={
                "runtime_reachability": {
                    "command": "./bin/ask skills proof autofix --runtime-target codex --json --robot"
                }
            },
            normalized_handle="autofix",
            query="autofix",
            audit_target="Skills/agent-ops/autofix",
            strict=False,
        )

        self.assertEqual(
            decision["command"],
            "./bin/ask skills proof autofix --runtime-target codex --json --robot",
        )
        self.assertEqual(decision["precedence"], "blocker")
        self.assertEqual(decision["source_class"], "blocked_runtime")
        self.assertEqual(decision["source_check"], "runtime_reachability")
        self.assertIn("blocked_runtime", decision["reason"])

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
        self.assertNotIn("runtime_reachability", doctor["checks"])
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
        _assert_skill_doctor_schema_validates(self, doctor)

    def test_doctor_invalid_path_payload_matches_public_schema(self) -> None:
        with patch("ask.commands.skills_impl._skill_workout_candidates", return_value=[]):
            result = skills_doctor(REPO_ROOT, "../outside")

        self.assertEqual(result.status, "error")
        doctor = result.data["skill_doctor"]
        self.assertEqual(doctor["target_kind"], "invalid_path")
        self.assertIsNone(doctor["handle"])
        self.assertIsNone(doctor["canonical_source_path"])
        self.assertIsNone(doctor["audit_target"])
        self.assertEqual(doctor["checks"]["resolver"]["status"], "skipped")
        self.assertEqual(doctor["checks"]["canonical_source"]["status"], "fail")
        self.assertNotIn("runtime_reachability", doctor["checks"])
        self.assertIn("blocked_missing_source", doctor["lifecycle_event"]["outcome"]["blocker_classes"])
        _assert_skill_doctor_schema_validates(self, doctor)


if __name__ == "__main__":
    unittest.main()
