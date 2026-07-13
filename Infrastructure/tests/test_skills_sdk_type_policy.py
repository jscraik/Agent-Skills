from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import ModuleType


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

    def test_existing_legacy_duration_fields_remain_compatible_until_owner_migration(self) -> None:
        path = "Infrastructure/scripts/lib/ask/commands/plugins.py"
        issues = self.validator.validate_paths(REPO_ROOT, (path,))
        self.assertNotIn("unitless_duration_annotation", {issue.code for issue in issues})

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
