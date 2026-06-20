import json
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands.skills_impl import skills_doctor  # noqa: E402
from ask.skills_sdk.contracts import read_skill_frontmatter_fields  # noqa: E402
from ask.skills_sdk.risk import build_risk_classification  # noqa: E402


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/risk-classification.v1.schema.json"


def _risk_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _write_skill(root: Path, body: str, frontmatter: str | None = None) -> Path:
    skill_dir = root / "sample"
    skill_dir.mkdir()
    frontmatter_text = frontmatter or "name: sample\ndescription: sample skill"
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"---\n{frontmatter_text}\n---\n\n{body}\n", encoding="utf-8")
    return skill_md


class TestSkillsSdkRiskClassifier(unittest.TestCase):
    def assert_schema_valid(self, payload: dict) -> None:
        _validate_schema_subset(_risk_schema(), payload, {"risk-classification": _risk_schema()})

    def test_docs_only_skill_uses_low_cost_advisory_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = _write_skill(Path(tmp), "# Sample\n\nPlain authoring guidance.")
            frontmatter = read_skill_frontmatter_fields(skill_md)
            payload = build_risk_classification(skill_md, frontmatter, skill_md.read_text())

        self.assert_schema_valid(payload)
        self.assertEqual(payload["source_kind"], "docs_only")
        self.assertEqual(payload["risk_tier"], "low")
        self.assertEqual(payload["blocking_behavior"], "advisory")
        self.assertEqual(payload["sensor_ids"], ["manifest_source", "static_metadata"])

    def test_referenced_skill_selects_reference_boundary_sensor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = _write_skill(
                Path(tmp),
                "# Sample\n\nRead the material in references/policy.md first.",
            )
            (skill_md.parent / "references").mkdir()
            frontmatter = read_skill_frontmatter_fields(skill_md)
            payload = build_risk_classification(skill_md, frontmatter, skill_md.read_text())

        self.assert_schema_valid(payload)
        self.assertEqual(payload["source_kind"], "referenced")
        self.assertEqual(payload["risk_tier"], "medium")
        self.assertIn("reference_boundary", payload["sensor_ids"])

    def test_scripted_skill_selects_static_and_codex_sandbox_boundary_sensors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = _write_skill(Path(tmp), "# Sample\n\nRun scripts/check.py before handoff.")
            (skill_md.parent / "scripts").mkdir()
            frontmatter = read_skill_frontmatter_fields(skill_md)
            payload = build_risk_classification(skill_md, frontmatter, skill_md.read_text())

        self.assert_schema_valid(payload)
        self.assertEqual(payload["source_kind"], "scripted")
        self.assertEqual(payload["risk_tier"], "high")
        self.assertEqual(payload["blocking_behavior"], "block")
        self.assertIn("static_script_scan", payload["sensor_ids"])
        self.assertIn("codex_sandbox_boundary", payload["sensor_ids"])

    def test_external_source_fails_into_privileged_risk_without_running_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_json = Path(tmp) / "package.json"
            package_json.write_text('{"name":"external-skill"}\n', encoding="utf-8")
            payload = build_risk_classification(package_json, {}, package_json.read_text())

        self.assert_schema_valid(payload)
        self.assertEqual(payload["source_kind"], "external")
        self.assertEqual(payload["risk_tier"], "privileged")
        self.assertIn("external_adapter_detection", payload["sensor_ids"])
        self.assertIn("intake_quarantine_boundary", payload["sensor_ids"])

    def test_missing_source_uses_placeholder_lifecycle_receipt(self) -> None:
        payload = build_risk_classification(Path("/missing/SKILL.md"), {}, "")

        self.assert_schema_valid(payload)
        self.assertEqual(payload["source_kind"], "placeholder")
        self.assertEqual(payload["blocking_behavior"], "skip_optional")
        self.assertEqual(payload["sensor_ids"], ["placeholder_lifecycle"])

    def test_doctor_embeds_risk_classification_check_for_skill_paths(self) -> None:
        result = skills_doctor(
            REPO_ROOT,
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md",
        )

        risk_check = result.data["skill_doctor"]["checks"]["risk_classification"]
        classification = risk_check["classification"]
        self.assertEqual(risk_check["status"], "pass")
        self.assertEqual(classification["schema_version"], "skills-sdk.risk-classification.v1")
        self.assertEqual(classification["source_kind"], "docs_only")
        self.assertIn("manifest_source", classification["sensor_ids"])
        self.assert_schema_valid(classification)


if __name__ == "__main__":
    unittest.main()
