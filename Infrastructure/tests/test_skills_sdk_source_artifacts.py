from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest



REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk import typed_contracts as contracts  # noqa: E402
from ask.skills_sdk.contracts import read_skill_frontmatter_fields  # noqa: E402

FIXTURE_MANIFEST = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/fixture-manifest.json"
VALID_SKILL_PATH = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
INVALID_SKILL_PATH = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/invalid_missing_frontmatter/SKILL.md"
VALID_ORIGINS = {"real_emitter", "schema_positive", "schema_negative", "visual_projection", "source_artifact"}


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

    def test_valid_skill_frontmatter_parses_as_typed_yaml(self) -> None:
        model = contracts.validate_skill_frontmatter(
            read_skill_frontmatter_fields(VALID_SKILL_PATH)
        )

        self.assertEqual(model.name, "skills-sdk-valid-fixture")
        self.assertIn("fixture", model.description)

    def test_invalid_skill_fixture_keeps_frontmatter_failure_visible(self) -> None:
        self.assertEqual(read_skill_frontmatter_fields(INVALID_SKILL_PATH), {})


if __name__ == "__main__":
    unittest.main()
