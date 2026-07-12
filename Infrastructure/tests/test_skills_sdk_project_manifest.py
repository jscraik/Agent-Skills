from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.project_manifest import (  # noqa: E402
    MANIFEST_SCHEMA_VERSION,
    evaluate_manifest_file,
    evaluate_manifest_payload,
    evaluate_repo_manifest,
    normalize_root_path,
)


def _full_manifest() -> dict:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "project_id": "owner-repo",
        "skill_roots": [
            {
                "path": ".agents/skills",
                "classification": "canonical_project_source",
                "default_for_create": True,
                "default_for_install": True,
                "default_for_update": True,
            }
        ],
        "eval_suite": {"path": ".harness/evals/skills"},
        "evidence": {"output_path": ".harness/session-evidence/skills"},
        "trust_policy": "local_owner",
        "precedence_policy": "project_over_user_after_trust",
    }


class TestProjectManifestStates(unittest.TestCase):
    def test_absent_manifest_reports_absent_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evaluation = evaluate_repo_manifest(Path(tmp))
        self.assertEqual(evaluation.state, "absent")
        self.assertFalse(evaluation.is_valid)
        self.assertFalse(evaluation.is_present)
        self.assertEqual(evaluation.blockers, ())

    def test_none_repo_root_reports_absent(self) -> None:
        evaluation = evaluate_repo_manifest(None)
        self.assertEqual(evaluation.state, "absent")

    def test_full_contract_manifest_is_valid(self) -> None:
        evaluation = evaluate_manifest_payload(_full_manifest(), path="skills-sdk.json")
        self.assertEqual(evaluation.state, "valid")
        self.assertTrue(evaluation.is_valid)
        self.assertFalse(evaluation.legacy_compat)
        self.assertEqual(evaluation.manifest, _full_manifest())

    def test_invalid_json_is_distinct_from_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "skills-sdk.json"
            manifest_path.write_text("{not-json", encoding="utf-8")
            evaluation = evaluate_manifest_file(manifest_path)
        self.assertEqual(evaluation.state, "invalid")
        self.assertNotEqual(evaluation.state, "absent")
        self.assertIn("manifest_invalid_json", evaluation.blocker_codes())

    def test_non_object_manifest_is_invalid(self) -> None:
        evaluation = evaluate_manifest_payload(["not", "an", "object"], path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_not_object", evaluation.blocker_codes())

    def test_wrong_schema_version_is_deterministic_blocker(self) -> None:
        manifest = _full_manifest()
        manifest["schema_version"] = "skills-sdk.project.v2"
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertEqual(evaluation.blocker_codes(), ["manifest_schema_version_unsupported"])

    def test_missing_schema_version_is_invalid(self) -> None:
        manifest = _full_manifest()
        del manifest["schema_version"]
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_schema_version_unsupported", evaluation.blocker_codes())

    def test_duplicate_roots_are_blocked(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"] = [
            {"path": ".agents/skills", "classification": "canonical_project_source"},
            {"path": "/.agents/skills/", "classification": "generated_runtime_projection"},
        ]
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_duplicate_skill_root", evaluation.blocker_codes())

    def test_normalize_root_path_collapses_lexical_parent_segments(self) -> None:
        self.assertEqual(
            normalize_root_path(".agents/skills"),
            normalize_root_path(".agents/skills/../skills"),
        )

    def test_unsupported_classification_is_blocked(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"][0]["classification"] = "not_a_real_classification"
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_unsupported_classification", evaluation.blocker_codes())

    def test_non_string_classification_is_blocked_without_type_error(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"][0]["classification"] = []
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_unsupported_classification", evaluation.blocker_codes())

    def test_ambiguous_lifecycle_default_is_blocked(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"] = [
            {
                "path": ".agents/skills",
                "classification": "canonical_project_source",
                "default_for_create": True,
            },
            {
                "path": ".codex/skills",
                "classification": "canonical_project_source",
                "default_for_create": True,
            },
        ]
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_ambiguous_lifecycle_default", evaluation.blocker_codes())

    def test_single_default_per_action_is_valid(self) -> None:
        evaluation = evaluate_manifest_payload(_full_manifest(), path="skills-sdk.json")
        self.assertEqual(evaluation.state, "valid")

    def test_non_boolean_lifecycle_default_is_blocked(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"][0]["default_for_create"] = "yes"
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_lifecycle_default_not_boolean", evaluation.blocker_codes())

    def test_skill_roots_must_be_array(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"] = {"path": ".agents/skills"}
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_skill_roots_not_array", evaluation.blocker_codes())

    def test_full_contract_validates_evidence_and_policy_values(self) -> None:
        manifest = _full_manifest()
        manifest["evidence"] = {"output_path": 42}
        manifest["trust_policy"] = "not-a-policy"
        manifest["precedence_policy"] = "not-a-policy"
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_evidence_invalid", evaluation.blocker_codes())
        self.assertIn("manifest_unsupported_trust_policy", evaluation.blocker_codes())
        self.assertIn("manifest_unsupported_precedence_policy", evaluation.blocker_codes())

    def test_full_contract_requires_root_defaults_and_non_empty_roots(self) -> None:
        manifest = _full_manifest()
        manifest["skill_roots"] = []
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_skill_roots_empty", evaluation.blocker_codes())

        manifest["skill_roots"] = [{"path": ".agents/skills", "classification": "canonical_project_source"}]
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertEqual(evaluation.blocker_codes().count("manifest_skill_root_field_missing"), 3)

    def test_legacy_manifest_rejects_malformed_present_contract_fields(self) -> None:
        manifest = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "project_id": "owner-repo",
            "skill_roots": [{"path": ".agents/skills"}],
            "evidence": "not-an-object",
            "trust_policy": "not-a-policy",
        }
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "invalid")
        self.assertTrue(evaluation.legacy_compat)
        self.assertIn("manifest_evidence_invalid", evaluation.blocker_codes())
        self.assertIn("manifest_unsupported_trust_policy", evaluation.blocker_codes())

    def test_legacy_evidence_shape_remains_compatible(self) -> None:
        legacy = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "project": {"id": "owner-repo"},
            "skill_sources": [{"root": ".agents/skills", "kind": "canonical_project_source"}],
            "evidence": {"registry": ".harness/evidence/registry", "events": ".harness/evidence/events", "receipts": ".harness/evidence/receipts"},
        }
        evaluation = evaluate_manifest_payload(legacy, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "valid")
        self.assertTrue(evaluation.legacy_compat)

    def test_legacy_partial_manifest_is_valid_but_flagged(self) -> None:
        """A correct schema_version with legacy skill_sources stays valid, never absent."""
        legacy = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "project": {"id": "x-writer-canary"},
            "skill_sources": [
                {"root": ".codex/skills", "kind": "canonical_project_source"}
            ],
        }
        evaluation = evaluate_manifest_payload(legacy, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "valid")
        self.assertTrue(evaluation.legacy_compat)
        self.assertIn("project_id", evaluation.missing_contract_fields)
        self.assertIn("legacy", evaluation.compatibility_note().lower())

    def test_partial_full_form_missing_fields_is_legacy_valid(self) -> None:
        """The start-fixture manifest (only default_for_update) is tolerated."""
        manifest = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "project_id": "x-writer-canary",
            "skill_roots": [
                {
                    "path": ".codex/skills",
                    "classification": "canonical_project_source",
                    "default_for_update": True,
                }
            ],
        }
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        self.assertEqual(evaluation.state, "valid")
        self.assertTrue(evaluation.legacy_compat)

    def test_existing_non_file_manifest_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "skills-sdk.json"
            manifest_path.mkdir()
            evaluation = evaluate_manifest_file(manifest_path)
        self.assertEqual(evaluation.state, "invalid")
        self.assertIn("manifest_unreadable", evaluation.blocker_codes())

    def test_blocker_dicts_carry_class_and_definition(self) -> None:
        manifest = _full_manifest()
        manifest["schema_version"] = "wrong"
        evaluation = evaluate_manifest_payload(manifest, path="skills-sdk.json")
        blocker = evaluation.blocker_dicts()[0]
        self.assertEqual(blocker["class"], "manifest_schema_version_unsupported")
        self.assertIn("message", blocker)
        self.assertIn("definition", blocker)


if __name__ == "__main__":
    unittest.main()
