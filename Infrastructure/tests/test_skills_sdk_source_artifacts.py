from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest



REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import typed_contracts as contracts  # noqa: E402

FIXTURE_MANIFEST = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/fixture-manifest.json"
VALID_ORIGINS = {"real_emitter", "schema_positive", "schema_negative", "visual_projection", "source_artifact"}
SOURCE_ARTIFACTS = {
    "skill_md": REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md",
    "sdk_spec": REPO_ROOT / ".harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md",
    "sdk_plan": REPO_ROOT / ".harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-execution-plan.md",
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class TestSkillsSdkSourceArtifacts(unittest.TestCase):
    def test_fixture_manifest_uses_sidecar_provenance(self) -> None:
        payload = _json(FIXTURE_MANIFEST)

        self.assertEqual(payload["schema_version"], "skills-sdk.fixture-manifest.v1")
        fixtures = payload["fixtures"]
        self.assertIsInstance(fixtures, list)
        self.assertGreater(len(fixtures), 0)

        for entry in fixtures:
            self.assertIsInstance(entry, dict)
            self.assertIn(entry["origin"], VALID_ORIGINS)
            self.assertTrue(entry["schema_version"])
            self.assertTrue(entry["source_artifact_class"])
            self.assertTrue(entry["static_fixture_rationale"])
            self.assertTrue((REPO_ROOT / str(entry["path"])).exists())

    def test_source_artifact_classes_have_artifact_aware_markdown_contracts(self) -> None:
        required_terms = {
            "skill_md": ("# Skills SDK Valid Fixture",),
            "sdk_spec": ("# PU-011", "Approved Scope"),
            "sdk_plan": ("# PU-011", "Execution Slices", "Validation Commands"),
        }

        for artifact_class, path in SOURCE_ARTIFACTS.items():
            with self.subTest(artifact_class=artifact_class):
                text = path.read_text(encoding="utf-8")
                for term in required_terms[artifact_class]:
                    self.assertIn(term, text)

    def test_valid_skill_frontmatter_parses_as_typed_yaml(self) -> None:
        skill_path = SOURCE_ARTIFACTS["skill_md"]
        text = skill_path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _start, frontmatter, _body = text.split("---\n", 2)
        payload = {}
        for line in frontmatter.splitlines():
            if not line.strip():
                continue
            key, value = line.split(":", 1)
            payload[key.strip()] = value.strip()

        model = contracts.validate_skill_frontmatter(payload)

        self.assertEqual(model.name, "skills-sdk-valid-fixture")
        self.assertIn("fixture", model.description)

    def test_invalid_skill_fixture_keeps_frontmatter_failure_visible(self) -> None:
        invalid_skill = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/invalid_missing_frontmatter/SKILL.md"
        text = invalid_skill.read_text(encoding="utf-8")

        self.assertNotIn("---\n", text[:8])
        self.assertIn("Invalid", text)


if __name__ == "__main__":
    unittest.main()
