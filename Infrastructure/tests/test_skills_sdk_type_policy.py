from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import ModuleType
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/validate_skills_sdk_type_policy.py"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_skills_sdk_type_policy", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Skills SDK type-policy validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestSkillsSdkTypePolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = _load_validator()

    def test_policy_declares_branded_ids_and_duration_schema(self) -> None:
        policy = json.loads(
            (REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/type-policy.v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(policy["id_contract"]["brands"]["trace_id"], "tr")
        self.assertEqual(
            policy["id_contract"]["schema_path"],
            "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json",
        )
        self.assertTrue(policy["id_contract"]["new_values_must_not_use_uuid"])
        self.assertEqual(policy["duration_contract"]["schema_path"], "Infrastructure/config/schemas/skills-sdk/duration.v1.schema.json")

    def test_current_branded_schema_changes_pass(self) -> None:
        paths = (
            "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json",
            "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-trace.v1.schema.json",
            "Infrastructure/config/schemas/skills-sdk/ab-plan-receipt.v0.schema.json",
            "Infrastructure/config/schemas/skills-sdk/ab-run-receipt.v0.schema.json",
            "Infrastructure/config/schemas/skills-sdk/ab-judge-preview-receipt.v0.schema.json",
            "Infrastructure/config/schemas/skills-sdk/ab-judge-score-receipt.v0.schema.json",
        )
        self.assertEqual(self.validator.validate_paths(REPO_ROOT, paths), ())

    def test_full_policy_surface_includes_policy_json(self) -> None:
        self.assertIn(self.validator.POLICY_PATH, self.validator._policy_surface_paths(REPO_ROOT))

    def test_unbranded_identity_schema_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text(
                (REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            id_schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json"
            id_schema_path.parent.mkdir(parents=True, exist_ok=True)
            id_schema_path.write_text(
                (REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json"
            schema_path.parent.mkdir(parents=True, exist_ok=True)
            original = (REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json").read_text(encoding="utf-8")
            broken = original.replace('"pattern": "^rp_[a-z0-9]{12,32}$"', '"minLength": 1', 1)
            schema_path.write_text(broken, encoding="utf-8")
            issues = self.validator.validate_paths(
                temp_root,
                ("Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json",),
            )
        self.assertIn("unbranded_identity_schema", {issue.code for issue in issues})

    def test_permissive_branded_id_schema_fails_policy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text(
                (REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            id_schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json"
            id_schema_path.parent.mkdir(parents=True, exist_ok=True)
            branded_schema = json.loads(
                (REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json").read_text(encoding="utf-8")
            )
            branded_schema["pattern"] = "^.*$"
            id_schema_path.write_text(json.dumps(branded_schema), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/conditional.schema.json"
            schema_path.write_text(
                json.dumps({"type": "object", "properties": {"trace_id": {"type": "string", "pattern": "^tr_[a-z0-9]{12,32}$"}}}),
                encoding="utf-8",
            )

            issues = self.validator.validate_paths(temp_root, ("Infrastructure/config/schemas/skills-sdk/conditional.schema.json",))

        self.assertIn("type_policy_invalid", {issue.code for issue in issues})

    def test_conditional_identity_requires_brand_and_string_type(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
            id_schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json"
            id_schema_path.write_text((REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json").read_text(encoding="utf-8"), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/conditional.schema.json"
            schema_path.parent.mkdir(parents=True, exist_ok=True)
            schema_path.write_text(
                json.dumps({"type": "object", "then": {"properties": {"request_id": {"type": "integer", "pattern": "^rq_[a-z0-9]{12,32}$"}, "trace_id": {"type": "string"}}}}),
                encoding="utf-8",
            )
            issues = self.validator.validate_paths(temp_root, ("Infrastructure/config/schemas/skills-sdk/conditional.schema.json",))
        codes = {issue.code for issue in issues}
        self.assertIn("identity_schema_type", codes)
        self.assertIn("unbranded_identity_schema", codes)

    def test_schema_identity_walks_anyof_and_else_branches(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
            id_schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json"
            id_schema_path.parent.mkdir(parents=True, exist_ok=True)
            id_schema_path.write_text((REPO_ROOT / id_schema_path.relative_to(temp_root)).read_text(encoding="utf-8"), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/conditional-branches.schema.json"
            schema_path.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "anyOf": [{"properties": {"request_id": {"type": "string", "pattern": "^bad$"}}}],
                        "else": {"properties": {"trace_id": {"type": "string", "pattern": "^bad$"}}},
                    }
                ),
                encoding="utf-8",
            )
            issues = self.validator.validate_paths(temp_root, ("Infrastructure/config/schemas/skills-sdk/conditional-branches.schema.json",))
        paths = {issue.path for issue in issues if issue.code == "unbranded_identity_schema"}
        self.assertTrue(any(".anyOf" in path for path in paths))
        self.assertTrue(any(".else" in path for path in paths))

    def test_nullable_identity_accepts_unordered_json_schema_type_array(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
            id_schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/branded-id.v1.schema.json"
            id_schema_path.parent.mkdir(parents=True, exist_ok=True)
            id_schema_path.write_text((REPO_ROOT / id_schema_path.relative_to(temp_root)).read_text(encoding="utf-8"), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/nullable.schema.json"
            schema_path.write_text(
                json.dumps({"type": "object", "properties": {"trace_id": {"type": ["null", "string"], "pattern": "^tr_[a-z0-9]{12,32}$"}}}),
                encoding="utf-8",
            )
            issues = self.validator.validate_paths(temp_root, ("Infrastructure/config/schemas/skills-sdk/nullable.schema.json",))
        self.assertNotIn("identity_schema_type", {issue.code for issue in issues})
        self.assertNotIn("unbranded_identity_schema", {issue.code for issue in issues})

    def test_manual_newtype_and_unitless_duration_fail(self) -> None:
        path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/type-policy-bad.py"
        path.write_text(
            "from typing import NewType, Optional\nReceiptId = NewType('ReceiptId', str)\ndef run(budget_seconds: Optional[int]) -> None: ...\n",
            encoding="utf-8",
        )
        try:
            issues = self.validator.validate_paths(REPO_ROOT, ("Infrastructure/tests/fixtures/skills_sdk/type-policy-bad.py",))
        finally:
            path.unlink()
        codes = {issue.code for issue in issues}
        self.assertIn("manual_newtype_forbidden", codes)
        self.assertIn("unitless_duration_annotation", codes)

    def test_aliased_newtype_is_forbidden(self) -> None:
        path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/type-policy-aliased-newtype.py"
        path.write_text("from typing import NewType as NT\nReceiptId = NT('ReceiptId', str)\n", encoding="utf-8")
        try:
            issues = self.validator.validate_paths(REPO_ROOT, ("Infrastructure/tests/fixtures/skills_sdk/type-policy-aliased-newtype.py",))
        finally:
            path.unlink()
        self.assertIn("manual_newtype_forbidden", {issue.code for issue in issues})

    def test_attribute_duration_annotation_is_checked(self) -> None:
        path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/type-policy-attribute.py"
        path.write_text("class Runner:\n    def run(self) -> None:\n        self.timeout_seconds: int = 1\n", encoding="utf-8")
        try:
            issues = self.validator.validate_paths(REPO_ROOT, ("Infrastructure/tests/fixtures/skills_sdk/type-policy-attribute.py",))
        finally:
            path.unlink()
        self.assertIn("unitless_duration_annotation", {issue.code for issue in issues})

    def test_stringized_duration_annotations_are_checked(self) -> None:
        path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/type-policy-stringized.py"
        path.write_text('def run(timeout_seconds: "int") -> None: ...\n', encoding="utf-8")
        try:
            issues = self.validator.validate_paths(REPO_ROOT, ("Infrastructure/tests/fixtures/skills_sdk/type-policy-stringized.py",))
        finally:
            path.unlink()
        self.assertIn("unitless_duration_annotation", {issue.code for issue in issues})

    def test_changed_policy_validates_policy_object(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy = json.loads((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"))
            policy.pop("id_contract")
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            for filename in ("branded-id.v1.schema.json", "duration.v1.schema.json"):
                target = temp_root / "Infrastructure/config/schemas/skills-sdk" / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((REPO_ROOT / target.relative_to(temp_root)).read_text(encoding="utf-8"), encoding="utf-8")
            issues = self.validator.validate_paths(temp_root, (self.validator.POLICY_PATH,))
        self.assertIn("type_policy_invalid", {issue.code for issue in issues})

    def test_existing_legacy_duration_fields_remain_compatible_until_owner_migration(self) -> None:
        path = "Infrastructure/scripts/lib/ask/commands/plugins.py"
        issues = self.validator.validate_paths(REPO_ROOT, (path,))
        self.assertNotIn("unitless_duration_annotation", {issue.code for issue in issues})

    def test_legacy_duration_fields_accept_merge_base_baseline(self) -> None:
        annotation = ast.parse("def f(timeout_seconds: int): ...").body[0].args.args[0].annotation
        merge_base_result = mock.Mock(returncode=0, stdout="base-head\n")
        matching_base = mock.Mock(returncode=0, stdout="def f(timeout_seconds: int): ...\n")
        with mock.patch.object(self.validator.subprocess, "run", side_effect=[merge_base_result, matching_base]):
            self.assertTrue(
                self.validator._legacy_annotation_exists_in_parent(
                    REPO_ROOT, "fixture.py", "timeout_seconds", annotation, owner_path=("f",)
                )
            )

    def test_legacy_attribute_duration_fields_accept_merge_base_baseline(self) -> None:
        annotation = ast.parse("class Runner:\n    def run(self):\n        self.timeout_seconds: int = 1\n").body[0].body[0].body[0].annotation
        merge_base_result = mock.Mock(returncode=0, stdout="base-head\n")
        matching_base = mock.Mock(returncode=0, stdout="class Runner:\n    def run(self):\n        self.timeout_seconds: int = 1\n")
        with mock.patch.object(self.validator.subprocess, "run", side_effect=[merge_base_result, matching_base]):
            self.assertTrue(
                self.validator._legacy_annotation_exists_in_parent(
                    REPO_ROOT, "fixture.py", "timeout_seconds", annotation, owner_path=("Runner", "run")
                )
            )

    def test_legacy_duration_fields_ignore_non_base_parent(self) -> None:
        annotation = ast.parse("def f(timeout_seconds: int): ...").body[0].args.args[0].annotation
        merge_base_result = mock.Mock(returncode=0, stdout="base-head\n")
        non_matching_base = mock.Mock(returncode=0, stdout="def f(timeout_seconds: str): ...\n")
        with mock.patch.object(self.validator.subprocess, "run", side_effect=[merge_base_result, non_matching_base]):
            self.assertFalse(
                self.validator._legacy_annotation_exists_in_parent(
                    REPO_ROOT, "fixture.py", "timeout_seconds", annotation, owner_path=("f",)
                )
            )

    def test_legacy_duration_exemption_is_scoped_to_owner(self) -> None:
        annotation = ast.parse("def run(timeout_seconds: int): ...").body[0].args.args[0].annotation
        merge_base_result = mock.Mock(returncode=0, stdout="base-head\n")
        matching_base = mock.Mock(returncode=0, stdout="class Existing:\n    def run(timeout_seconds: int): ...\n")
        with mock.patch.object(self.validator.subprocess, "run", side_effect=[merge_base_result, matching_base]):
            self.assertTrue(
                self.validator._legacy_annotation_exists_in_parent(
                    REPO_ROOT, "fixture.py", "timeout_seconds", annotation, owner_path=("Existing", "run")
                )
            )
        merge_base_result = mock.Mock(returncode=0, stdout="base-head\n")
        matching_base = mock.Mock(returncode=0, stdout="class Existing:\n    def run(timeout_seconds: int): ...\n")
        with mock.patch.object(self.validator.subprocess, "run", side_effect=[merge_base_result, matching_base]):
            self.assertFalse(
                self.validator._legacy_annotation_exists_in_parent(
                    REPO_ROOT, "fixture.py", "timeout_seconds", annotation, owner_path=("New", "run")
                )
            )

    def test_new_numeric_duration_schema_property_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
            for filename in ("branded-id.v1.schema.json", "duration.v1.schema.json"):
                target = temp_root / "Infrastructure/config/schemas/skills-sdk" / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((REPO_ROOT / target.relative_to(temp_root)).read_text(encoding="utf-8"), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/new-duration.schema.json"
            schema_path.write_text(json.dumps({"type": "object", "properties": {"timeout_seconds": {"type": "number"}}}), encoding="utf-8")
            issues = self.validator.validate_paths(temp_root, (str(schema_path.relative_to(temp_root)),))
        self.assertIn("unitless_duration_schema_property", {issue.code for issue in issues})

    def test_ref_backed_numeric_duration_schema_property_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
            for filename in ("branded-id.v1.schema.json", "duration.v1.schema.json"):
                target = temp_root / "Infrastructure/config/schemas/skills-sdk" / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((REPO_ROOT / target.relative_to(temp_root)).read_text(encoding="utf-8"), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/ref-duration.schema.json"
            schema_path.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "properties": {"timeout_seconds": {"$ref": "#/$defs/seconds"}},
                        "$defs": {"seconds": {"type": "integer"}},
                    }
                ),
                encoding="utf-8",
            )
            issues = self.validator.validate_paths(temp_root, (str(schema_path.relative_to(temp_root)),))
        self.assertIn("unitless_duration_schema_property", {issue.code for issue in issues})

    def test_duration_schema_contract_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
            for filename in ("branded-id.v1.schema.json", "duration.v1.schema.json"):
                target = temp_root / "Infrastructure/config/schemas/skills-sdk" / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                source = json.loads((REPO_ROOT / target.relative_to(temp_root)).read_text(encoding="utf-8"))
                if filename == "duration.v1.schema.json":
                    source["properties"]["unit"]["enum"] = ["seconds"]
                target.write_text(json.dumps(source), encoding="utf-8")
            issues = self.validator.validate_paths(temp_root, (self.validator.POLICY_PATH,))
        self.assertIn("duration_schema_units", {issue.code for issue in issues})

    def test_identity_fields_are_derived_from_policy_brands(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            policy_path = temp_root / self.validator.POLICY_PATH
            policy_path.parent.mkdir(parents=True)
            policy = json.loads((REPO_ROOT / self.validator.POLICY_PATH).read_text(encoding="utf-8"))
            policy["id_contract"]["brands"]["session_id"] = "ss"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            for filename in ("branded-id.v1.schema.json", "duration.v1.schema.json"):
                target = temp_root / "Infrastructure/config/schemas/skills-sdk" / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((REPO_ROOT / target.relative_to(temp_root)).read_text(encoding="utf-8"), encoding="utf-8")
            schema_path = temp_root / "Infrastructure/config/schemas/skills-sdk/session.schema.json"
            schema_path.write_text(json.dumps({"type": "object", "properties": {"session_id": {"type": "string", "pattern": "^anything$"}}}), encoding="utf-8")
            issues = self.validator.validate_paths(temp_root, (str(schema_path.relative_to(temp_root)),))
        self.assertIn("unbranded_identity_schema", {issue.code for issue in issues})

    def test_new_legacy_named_duration_field_is_not_allowlisted_by_name(self) -> None:
        path = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/type-policy-new-legacy.py"
        path.write_text("def run(timeout_seconds: int) -> None: ...\n", encoding="utf-8")
        try:
            issues = self.validator.validate_paths(REPO_ROOT, ("Infrastructure/tests/fixtures/skills_sdk/type-policy-new-legacy.py",))
        finally:
            path.unlink()
        self.assertIn("unitless_duration_annotation", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
