import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.knowledge_source_context import merge_knowledge_source_context  # noqa: E402
from ask.skills_sdk.knowledge_ingest import build_knowledge_ingest  # noqa: E402
from ask.skills_sdk.operational_references import validate_operational_references  # noqa: E402
from tests.test_skills_sdk_knowledge_ingest import _write_extraction, _write_skill  # noqa: E402


def _manifest(target_path: str) -> dict[str, object]:
    return {"capsules": [{"target_path": target_path}]}


class TestSkillsSdkOperationalReferenceContract(unittest.TestCase):
    def test_apply_validates_source_context_before_writing_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            source_context = skill_dir / "references" / "source-context.yaml"
            source_context.write_text(
                "schema_version: 1\nskill: improve-agent-native\n"
                "references: []\nallowed_claims:\n  invalid: true\n",
                encoding="utf-8",
            )
            extraction = _write_extraction(Path(tmp))

            with self.assertRaisesRegex(ValueError, "allowed_claims must be a list"):
                build_knowledge_ingest(
                    root, extraction=str(extraction), skill="Skills/agent-ops/improve-agent-native",
                    apply=True, preflight_security=False,
                )

            self.assertFalse((skill_dir / "references" / "harness-evidence-boundary.md").exists())

    def test_merge_rejects_non_list_allowed_claims(self) -> None:
        loaded = {"references": [], "allowed_claims": {"invalid": True}}

        with self.assertRaisesRegex(ValueError, "allowed_claims must be a list"):
            merge_knowledge_source_context(
                loaded,
                eval_routes={"scenarios": False, "fixtures": False},
                manifest=_manifest("references/capsule.md"),
            )

    def test_merge_replaces_stale_generated_operational_routes(self) -> None:
        loaded = {
            "references": [
                {"path": "references/keep.md", "kind": "package_companion"},
                {"path": "references/old.md", "kind": "operational_reference"},
                {"path": "references/old-capsule.md", "kind": "generated_knowledge_capsule"},
                {"path": "references/old-capsules/*.md", "kind": "generated_knowledge_capsules_flat"},
            ]
        }

        merged = merge_knowledge_source_context(
            loaded,
            eval_routes={"scenarios": False, "fixtures": False},
            manifest=_manifest("references/current.md"),
        )

        paths = {entry["path"] for entry in merged["references"]}
        self.assertIn("references/keep.md", paths)
        self.assertIn("references/current.md", paths)
        self.assertNotIn("references/old.md", paths)
        self.assertNotIn("references/old-capsule.md", paths)
        self.assertNotIn("references/old-capsules/*.md", paths)
        self.assertNotIn("references/knowledge-capsules/", paths)

    def test_validation_blocks_heading_only_capsule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            extraction = Path(tmp) / "extraction"
            references = extraction / "references"
            references.mkdir(parents=True)
            (references / "capsule.md").write_text(
                "# Capsule\n\n## Claim Cards\n\n## Checklists\n",
                encoding="utf-8",
            )
            findings: list[str] = []

            validate_operational_references(
                extraction,
                _manifest("references/capsule.md"),
                findings,
            )

            self.assertTrue(
                any(finding.startswith("references:weak_operational_reference:") for finding in findings)
            )

    def test_validation_blocks_child_heading_only_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            extraction = Path(tmp) / "extraction"
            references = extraction / "references"
            references.mkdir(parents=True)
            (references / "capsule.md").write_text(
                "# Capsule\n\n## Claim Cards\n\n### Empty\n\n## Checklists\n\n### Empty\n",
                encoding="utf-8",
            )
            findings: list[str] = []

            validate_operational_references(
                extraction,
                _manifest("references/capsule.md"),
                findings,
            )

            self.assertTrue(
                any(finding.startswith("references:weak_operational_reference:") for finding in findings)
            )

    def test_validation_ignores_sections_inside_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            extraction = Path(tmp) / "extraction"
            references = extraction / "references"
            references.mkdir(parents=True)
            (references / "capsule.md").write_text(
                "# Capsule\n\n```markdown\n## Claim Cards\n\nExample claim.\n\n"
                "## Checklists\n\n- [ ] Example check.\n```\n",
                encoding="utf-8",
            )
            findings: list[str] = []

            validate_operational_references(
                extraction,
                _manifest("references/capsule.md"),
                findings,
            )

            self.assertTrue(
                any(finding.startswith("references:weak_operational_reference:") for finding in findings)
            )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_validation_blocks_capsule_under_symlinked_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            extraction = Path(tmp) / "extraction"
            references = extraction / "references"
            references.mkdir(parents=True)
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "capsule.md").write_text("# Capsule\n", encoding="utf-8")
            try:
                (references / "linked").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            findings: list[str] = []

            validate_operational_references(
                extraction,
                _manifest("references/linked/capsule.md"),
                findings,
            )

            self.assertIn(
                "references:symlinked_capsule:references/linked/capsule.md",
                findings,
            )

    def test_validation_reports_capsule_read_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            extraction = Path(tmp) / "extraction"
            references = extraction / "references"
            references.mkdir(parents=True)
            (references / "directory.md").mkdir()
            findings: list[str] = []

            validate_operational_references(
                extraction,
                _manifest("references/directory.md"),
                findings,
            )

            self.assertIn(
                "references:missing_or_invalid_capsule:references/directory.md",
                findings,
            )


if __name__ == "__main__":
    unittest.main()
