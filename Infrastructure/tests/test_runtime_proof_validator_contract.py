from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
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


def _conditional_requirements(receipt_schema: dict[str, object]) -> dict[tuple[str, object], set[str]]:
    return {
        (field, condition.get("const", tuple(condition.get("enum", [])))): set(rule["then"]["required"])
        for rule in receipt_schema["allOf"]
        for field, condition in rule["if"]["properties"].items()
    }


class TestRuntimeProofValidatorContract(unittest.TestCase):
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

    def test_schema_files_accept_valid_runtime_card_fixture(self) -> None:
        payload = json.loads((FIXTURES_DIR / "valid-runtime-card.json").read_text(encoding="utf-8"))
        _validate_schema_subset(self.schemas["runtime-card.v1.schema.json"], payload, self.schemas)

    def test_validator_contract_primitives_match_schema_enums_and_conditionals(self) -> None:
        validator = _load_validator_module()
        runtime_card = self.schemas["runtime-card.v1.schema.json"]
        receipt = self.schemas["evidence-receipt.v1.schema.json"]
        artifact = self.schemas["artifact-record.v1.schema.json"]
        session = self.schemas["runtime-session-summary.v1.schema.json"]
        recovery = self.schemas["recovery-plan-summary.v1.schema.json"]
        checks = [
            (runtime_card["definitions"]["runtimeTarget"]["enum"], validator._runtime_targets()),
            (receipt["definitions"]["runtimeTarget"]["enum"], validator._runtime_targets()),
            (session["definitions"]["runtimeTarget"]["enum"], validator._runtime_targets()),
            (runtime_card["definitions"]["runtimeStatus"]["enum"], validator._runtime_statuses()),
            (receipt["definitions"]["runtimeStatus"]["enum"], validator._runtime_statuses()),
            (session["definitions"]["runtimeStatus"]["enum"], validator._runtime_statuses()),
            (recovery["definitions"]["runtimeStatus"]["enum"], validator._runtime_statuses()),
            (receipt["definitions"]["claimStatus"]["enum"], validator._claim_statuses()),
            (artifact["definitions"]["claimStatus"]["enum"], validator._claim_statuses()),
            (receipt["properties"]["evidence_type"]["enum"], validator._evidence_types()),
            (runtime_card["definitions"]["actorType"]["enum"], validator._actor_types()),
            (artifact["definitions"]["actorType"]["enum"], validator._actor_types()),
            (session["definitions"]["actorType"]["enum"], validator._actor_types()),
            (runtime_card["definitions"]["mutationScope"]["enum"], validator._mutation_scopes()),
            (artifact["definitions"]["mutationScope"]["enum"], validator._mutation_scopes()),
            (runtime_card["definitions"]["visibilityStatus"]["enum"], validator._visibility_statuses()),
            (artifact["definitions"]["visibilityStatus"]["enum"], validator._visibility_statuses()),
            (session["definitions"]["visibilityStatus"]["enum"], validator._visibility_statuses()),
            (artifact["properties"]["artifact_type"]["enum"], validator._artifact_types()),
        ]
        for actual, expected in checks:
            self.assertEqual(set(actual), expected)
        requirements = _conditional_requirements(receipt)
        self.assertEqual(requirements[("evidence_type", "command")], {"command", "exit_code"})
        self.assertEqual(
            requirements[("runtime_status", "blocked_runtime")],
            {"probe_command", "probe_exit_code", "probe_artifact_path", "blocker_class"},
        )
        self.assertEqual(requirements[("claim_status", ("blocked", "partial"))], {"blocker"})

    def test_validator_accepts_valid_runtime_card_fixture(self) -> None:
        process = self.run_validator(
            str(FIXTURES_DIR / "valid-runtime-card.json"),
            "--require-shared-workspace",
            "--workspace-root",
            "${WORKSPACE_ROOT}",
            "--json",
        )
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["status"], "pass")

    def test_validator_rejects_command_receipt_without_command(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-missing-command.json"), "--json")
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("command", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_validator_rejects_receipt_without_runtime_target(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-missing-runtime-target.json"), "--json")
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("runtime_target", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_validator_rejects_blocked_runtime_without_blocker_class(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-missing-blocker-class.json"), "--json")
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("blocker_class", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_shared_workspace_gate_rejects_agent_only_visibility(self) -> None:
        process = self.run_validator(
            str(FIXTURES_DIR / "invalid-agent-only-artifact.json"),
            "--require-shared-workspace",
            "--json",
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("visibility_status", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_shared_workspace_gate_rejects_foreign_workspace_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = json.loads((FIXTURES_DIR / "valid-runtime-card.json").read_text(encoding="utf-8"))
            fixture["workspace_root"] = str(REPO_ROOT)
            fixture["runtime_session"]["workspace_root"] = str(REPO_ROOT)
            fixture["artifacts"][0]["workspace_root"] = str(REPO_ROOT)
            explicit_fixture = Path(temp_dir) / "valid-runtime-card-explicit-workspace.json"
            explicit_fixture.write_text(json.dumps(fixture), encoding="utf-8")
            process = self.run_validator(
                str(explicit_fixture), "--require-shared-workspace", "--workspace-root", "/tmp/other-checkout", "--json"
            )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("workspace_root", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_validator_accepts_standalone_runtime_session_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "valid-runtime-session-summary.json"), "--json")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["checked"][0]["kind"], "runtime_session_summary")

    def test_validator_rejects_invalid_runtime_session_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-runtime-session-summary.json"), "--json")
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("runtime_target", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_validator_accepts_standalone_recovery_plan_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "valid-recovery-plan-summary.json"), "--json")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["checked"][0]["kind"], "recovery_plan_summary")

    def test_validator_rejects_invalid_recovery_plan_summary(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "invalid-recovery-plan-summary.json"), "--json")
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("command", {finding["field"] for finding in json.loads(process.stdout)["findings"]})

    def test_validator_accepts_evidence_directory(self) -> None:
        process = self.run_validator("--evidence-dir", str(FIXTURES_DIR), "--json")
        self.assertNotEqual(process.returncode, 0)
        checked = {Path(item["path"]).name for item in json.loads(process.stdout)["checked"]}
        self.assertNotIn("unrelated-tool-output.json", checked)
        self.assertTrue({"valid-runtime-card.json", "valid-runtime-session-summary.json", "valid-recovery-plan-summary.json"} <= checked)

    def test_validator_rejects_explicit_unknown_json_path(self) -> None:
        process = self.run_validator(str(FIXTURES_DIR / "unrelated-tool-output.json"), "--json")
        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked"][0]["kind"], "unknown")
        self.assertEqual(payload["findings"][0]["message"], "could not infer runtime proof artifact kind")

    def test_validator_reports_missing_explicit_file(self) -> None:
        missing_path = FIXTURES_DIR / "does-not-exist.json"
        process = self.run_validator(str(missing_path), "--json")
        self.assertNotEqual(process.returncode, 0)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["checked_count"], 0)
        self.assertEqual(payload["findings"][0]["path"], str(missing_path))
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
        self.assertTrue(payload["findings"][0]["message"].startswith("invalid JSON:"))

    def test_validator_reports_invalid_schema_json(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_dir = Path(temp_dir)
            for schema_name in SCHEMA_NAMES:
                (schema_dir / schema_name).write_text((SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"), encoding="utf-8")
            (schema_dir / "runtime-card.v1.schema.json").write_text("{not json", encoding="utf-8")
            validator._schema_dir = lambda: schema_dir
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
            schema_dir = Path(temp_dir)
            for schema_name in SCHEMA_NAMES:
                (schema_dir / schema_name).write_text((SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"), encoding="utf-8")
            receipt_path = schema_dir / "evidence-receipt.v1.schema.json"
            receipt_schema = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_schema["allOf"][2]["if"]["properties"]["claim_status"]["enum"] = ["partial", "blocked"]
            receipt_path.write_text(json.dumps(receipt_schema), encoding="utf-8")
            validator._schema_dir = lambda: schema_dir
            required = validator._schema_conditional_required("evidence-receipt.v1.schema.json", "claim_status", ("blocked", "partial"))
        self.assertEqual(required, ["blocker"])

    def test_single_value_conditional_enum_matches_string_marker(self) -> None:
        validator = _load_validator_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_dir = Path(temp_dir)
            for schema_name in SCHEMA_NAMES:
                (schema_dir / schema_name).write_text((SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"), encoding="utf-8")
            receipt_path = schema_dir / "evidence-receipt.v1.schema.json"
            receipt_schema = json.loads(receipt_path.read_text(encoding="utf-8"))
            condition = receipt_schema["allOf"][0]["if"]["properties"]["evidence_type"]
            condition.pop("const")
            condition["enum"] = ["command"]
            receipt_path.write_text(json.dumps(receipt_schema), encoding="utf-8")
            validator._schema_dir = lambda: schema_dir
            required = validator._schema_conditional_required("evidence-receipt.v1.schema.json", "evidence_type", "command")
        self.assertEqual(required, ["command", "exit_code"])


if __name__ == "__main__":
    unittest.main()
