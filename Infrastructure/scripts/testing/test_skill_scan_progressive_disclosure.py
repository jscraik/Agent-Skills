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
FAILED_LOAD_MSG = "Failed to load module from %s"


def load_module():
    """
    Load and execute the skill_scan.py module from the known SCRIPT path and return the imported module object.
    
    Returns:
        module (module): The loaded Python module object for `skill_scan.py`.
    
    Raises:
        RuntimeError: If the module spec or loader cannot be created for the SCRIPT path.
    """
    spec = importlib.util.spec_from_file_location("skill_scan", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(FAILED_LOAD_MSG % SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _skill_with_required_headings(extra_body: str) -> str:
    """
    Constructs a minimal SKILL.md content string containing the required progressive-disclosure headings and appends additional body text.
    
    Parameters:
        extra_body (str): Additional Markdown content to append after the required sections.
    
    Returns:
        str: A complete SKILL.md-formatted string with front-matter, the required headings ("When to use", "Required inputs", "Deliverables", "Failure mode", "Gotchas"), and the provided extra body appended.
    """
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
        """
        Prepare each test by loading the `skill_scan` module and storing it on `self.module` for use in test methods.
        """
        self.module = load_module()

    def test_strict_mode_fails_for_missing_relocation_signposts(self) -> None:
        """
        Verifies that strict progressive-disclosure linting fails for a targeted skill that lacks relocation signposting.
        
        Creates a temporary repository layout for a targeted skill under Plugins/.../skills/scaffolding_templates/skill-creator with a minimal SKILL.md that omits relocation signposts, patches the scanned repository roots to the temporary layout, invokes cmd_lint_progressive_disclosure("strict"), and asserts the command returns 1.
        """
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
        """
        Verify that strict-mode progressive-disclosure linting accepts a targeted skill when relocation signposting and a valid local reference link are present.
        
        Creates a temporary plugin skill containing a SKILL.md with required headings, relocation-style signposting, and a reference file, patches the module's repository roots to the temporary layout, runs the linter in "strict" mode, and asserts the command returns 0.
        """
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
        """
        Verify the strict progressive-disclosure relocation guard does not apply to skills located under non-targeted repository paths.
        
        Creates a temporary repository tree with a skill placed under Plugins/plugin-factory/... that intentionally lacks relocation signposting, runs cmd_lint_progressive_disclosure("strict") with REPO_ROOT and ROOTS patched to scan only Plugins, and asserts the command returns 0.
        """
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
        """
        Verifies that strict progressive-disclosure linting accepts SKILL.md link references that use an Infrastructure/... path.
        
        Creates a minimal skill layout where SKILL.md contains relocation signposting and a link to Infrastructure/references/governance.md, runs the linter in "strict" mode, and asserts the linter reports success (exit code 0).
        """
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

    def test_strict_mode_ignores_relocation_in_frontmatter(self) -> None:
        """
        Verify that strict progressive-disclosure linting ignores relocation-style text in YAML frontmatter and only validates the body.

        Creates a temporary plugin skill with a SKILL.md whose frontmatter contains relocation/signposting language but whose body omits relocation signposts, runs cmd_lint_progressive_disclosure("strict"), and asserts the command returns 1 because the linter should fail when relocation text appears only in frontmatter.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "plugins" / "skill-factory" / "skills" / "scaffolding_templates" / "skill-creator"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            (refs_dir / "details.md").write_text("# details\n", encoding="utf-8")

            # Create SKILL.md with relocation text in frontmatter but not in body
            frontmatter_with_relocation = """---
name: sample-skill
description: "Required operational context is never removed. Read when: details needed."
metadata:
  skill-type: scaffolding_templates
  notes: "See references/details.md for relocated context"
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

Keep this concise.
"""
            (skill_dir / "SKILL.md").write_text(frontmatter_with_relocation, encoding="utf-8")

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "ROOTS", ("plugins",)),
            ):
                rc = self.module.cmd_lint_progressive_disclosure("strict")

            self.assertEqual(rc, 1)


if __name__ == "__main__":
    main()