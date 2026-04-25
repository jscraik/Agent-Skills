#!/usr/bin/env python3
"""Regression tests for public-safe skill link handling."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_GATE = (
    REPO_ROOT
    / "Plugins"
    / "skill-factory"
    / "skills"
    / "code_quality_review"
    / "skill-builder"
    / "scripts"
    / "skill_gate.py"
)


def load_skill_gate():
    spec = importlib.util.spec_from_file_location("skill_gate_public_paths", SKILL_GATE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load skill_gate from {SKILL_GATE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SkillGatePublicPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_skill_gate()

    def _doc(self, path: Path, body: str):
        return self.module.SkillDoc(
            path=path,
            raw="---\nname: sample\ndescription: test\n---\nbody",
            frontmatter={"name": "sample", "description": "test"},
            body=body,
            fm_start_line=1,
            fm_end_line=4,
        )

    def test_repo_scheme_links_resolve_without_path_warnings(self) -> None:
        doc = self._doc(
            SKILL_GATE,
            "See [gate](repo:Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/skill_gate.py).",
        )

        codes = {finding.code for finding in self.module.check_path_safety(doc)}

        self.assertNotIn("PATH_REPO_LINK_MISSING", codes)
        self.assertNotIn("PATH_REPO_LINK_TRAVERSAL", codes)
        self.assertNotIn("PATH_ABSOLUTE", codes)

    def test_repo_scheme_rejects_missing_or_escaping_targets(self) -> None:
        doc = self._doc(
            SKILL_GATE,
            "\n".join(
                [
                    "See [missing](repo:Plugins/missing/SKILL.md).",
                    "See [escape](repo:../outside.md).",
                ]
            ),
        )

        codes = {finding.code for finding in self.module.check_path_safety(doc)}

        self.assertIn("PATH_REPO_LINK_MISSING", codes)
        self.assertIn("PATH_REPO_LINK_TRAVERSAL", codes)

    def test_local_absolute_paths_warn_when_embedded_in_markdown_links(self) -> None:
        doc = self._doc(
            SKILL_GATE,
            "See [local](/Users/example/dev/repo/Skills/sample/SKILL.md).",
        )

        codes = {finding.code for finding in self.module.check_path_safety(doc)}

        self.assertIn("PATH_ABSOLUTE", codes)

    def test_symlinked_doc_allows_existing_physical_parent_traversal_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repo"
            physical_dir = root / "fixtures" / "archive" / "deferred-store" / "skills" / "sample"
            public_ref = root / "fixtures" / "archive" / "references" / "details.md"
            active_dir = root / "skills" / "sample"
            physical_dir.mkdir(parents=True)
            public_ref.parent.mkdir(parents=True)
            active_dir.mkdir(parents=True)
            (root / ".git").mkdir()
            public_ref.write_text("# details\n", encoding="utf-8")
            physical_skill = physical_dir / "SKILL.md"
            physical_skill.write_text("# skill\n", encoding="utf-8")
            active_skill = active_dir / "SKILL.md"
            active_skill.symlink_to(physical_skill)

            doc = self._doc(
                active_skill,
                "Read [details](../../../references/details.md).",
            )

            codes = {finding.code for finding in self.module.check_path_safety(doc)}

            self.assertNotIn("PATH_TRAVERSAL", codes)


if __name__ == "__main__":
    unittest.main()
