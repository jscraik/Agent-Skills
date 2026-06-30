#!/usr/bin/env python3
"""Regression tests for governed SDK stage skill shape validation helpers."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "check_sdk_stage_skill_shape.py"
)

spec = importlib.util.spec_from_file_location("sdk_stage_shape_validator", VALIDATOR_PATH)
assert spec is not None
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def reference_entry(path: str, kind: str, *, bounded_unit: bool = True) -> dict:
    return {
        "path": path,
        "kind": kind,
        "provenance": "test fixture",
        "load_when": "the test needs this reference",
        "allowed_claims": ["fixture claim"],
        "forbidden_claims": ["runtime readiness"],
        "freshness": "test",
        "context_budget": "small",
        "claim_scope": "fixture",
        "bounded_unit": bounded_unit,
    }


class SdkStageShapeValidatorTests(unittest.TestCase):
    def test_accepts_bounded_local_markdown_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            (references_dir / "expert.md").write_text("# Expert\n", encoding="utf-8")

            validator.validate_source_context_references(
                root,
                skill_dir,
                {"references": [reference_entry("references/expert.md", "expert_viewpoint")]},
                references_dir / "source-context.yaml",
            )

    def test_accepts_bounded_composite_runbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            (references_dir / "runbook.md").write_text("# Runbook\n", encoding="utf-8")

            validator.validate_source_context_references(
                root,
                skill_dir,
                {"references": [reference_entry("references/runbook.md", "composite_runbook")]},
                references_dir / "source-context.yaml",
            )

    def test_rejects_unbounded_mixed_markdown_dossier(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            (references_dir / "mixed.md").write_text("# Mixed\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                validator.validate_source_context_references(
                    root,
                    skill_dir,
                    {
                        "references": [
                            reference_entry(
                                "references/mixed.md",
                                "substantial_context",
                                bounded_unit=False,
                            )
                        ]
                    },
                    references_dir / "source-context.yaml",
                )

    def test_allows_upstream_pack_export_without_runtime_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)

            validator.validate_source_context_references(
                root,
                skill_dir,
                {
                    "references": [
                        reference_entry(
                            "/Users/jamiecraik/dev/knowledge-OS/exports/skills/harness-engineering-pack.md",
                            "upstream_pack_export",
                        )
                    ]
                },
                references_dir / "source-context.yaml",
            )

    def test_load_yaml_requires_repo_wrapper_when_pyyaml_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_context = Path(tmpdir) / "source-context.yaml"
            source_context.write_text(
                """schema_version: source-context.v1
skill: fixture
references:
  - path: references/expert.md
    kind: expert_viewpoint
    bounded_unit: true
""",
                encoding="utf-8",
            )

            original_yaml = validator.yaml
            try:
                validator.yaml = None
                with self.assertRaises(SystemExit):
                    validator.load_yaml(source_context)
            finally:
                validator.yaml = original_yaml


if __name__ == "__main__":
    unittest.main()
