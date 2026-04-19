#!/usr/bin/env python3
"""Tests for progressive-disclosure relocation guard in skill_scan.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main, mock


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "skill_scan.py"


def load_module():
    spec = importlib.util.spec_from_file_location("skill_scan", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _skill_with_required_headings(extra_body: str) -> str:
    return f"""---
name: sample-skill
description: test
metadata:
  skill-type: scaffolding_templates
---

## When to use
Use this for tests.

## Required inputs
Inputs here.

## Deliverables
Deliverables here.

## Failure mode
Failure handling here.

## Gotchas
Gotchas here.

{extra_body}
"""


class SkillScanProgressiveDisclosureTests(TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_strict_mode_fails_for_missing_relocation_signposts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "Plugins" / "skill-factory" / "skills" / "scaffolding_templates" / "skill-creator"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            (refs_dir / "details.md").write_text("# details\n", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(
                _skill_with_required_headings("Keep this concise."),
                encoding="utf-8",
            )

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "ROOTS", ("Plugins",)),
            ):
                rc = self.module.cmd_lint_progressive_disclosure("strict")

            self.assertEqual(rc, 1)

    def test_strict_mode_passes_when_relocation_signposts_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "Plugins" / "skill-factory" / "skills" / "infrastructure_ops" / "skill-installer"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            (refs_dir / "details.md").write_text("# details\n", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(
                _skill_with_required_headings(
                    "Required operational context is never removed.\n"
                    "Read when: full decision context is needed.\n"
                    "See [details](./references/details.md).\n"
                ),
                encoding="utf-8",
            )

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "ROOTS", ("Plugins",)),
            ):
                rc = self.module.cmd_lint_progressive_disclosure("strict")

            self.assertEqual(rc, 0)

    def test_strict_mode_ignores_non_targeted_skills_for_relocation_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "Plugins" / "plugin-factory" / "skills" / "scaffolding_templates" / "plugin-creator"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            (refs_dir / "details.md").write_text("# details\n", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(
                _skill_with_required_headings("No relocation signposts by design."),
                encoding="utf-8",
            )

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "ROOTS", ("Plugins",)),
            ):
                rc = self.module.cmd_lint_progressive_disclosure("strict")

            self.assertEqual(rc, 0)

    def test_strict_mode_accepts_infrastructure_references_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "Plugins" / "skill-factory" / "skills" / "code_quality_review" / "skill-builder"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            (refs_dir / "governance.md").write_text("# governance\n", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(
                _skill_with_required_headings(
                    "Preserve valuable context by relocating it with explicit signposting.\n"
                    "Read when: governance details are needed.\n"
                    "See [governance](Infrastructure/references/governance.md).\n"
                ),
                encoding="utf-8",
            )

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "ROOTS", ("Plugins",)),
            ):
                rc = self.module.cmd_lint_progressive_disclosure("strict")

            self.assertEqual(rc, 0)


if __name__ == "__main__":
    main()
