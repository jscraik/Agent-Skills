#!/usr/bin/env python3
"""Regression tests for lifecycle-aware skill scaffolding."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "utilities" / "skill-builder" / "scripts" / "init_skill.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class SkillCreatorLifecycleScaffoldTests(unittest.TestCase):
    def test_creates_skill_with_lifecycle_metadata_and_honest_starter_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-skill",
                "--path",
                tmpdir,
                "--description",
                "Use when a repo needs example-skill workflow help.",
                "--owner",
                "Agent Skills Team",
                "--review-cadence",
                "monthly",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

            skill_md = Path(tmpdir) / "example-skill" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")
            self.assertIn("lifecycle_state: incubating", content)
            self.assertIn("maturity: experimental", content)
            self.assertIn("owner: Agent Skills Team", content)
            self.assertIn("review_cadence: monthly", content)
            self.assertIn("last_reviewed:", content)
            self.assertIn("metadata_source: frontmatter", content)
            self.assertIn("## Gotchas", content)
            self.assertIn("## See Also", content)
            self.assertIn("**Topic map:**", content)
            self.assertNotIn("[TODO:", content)

    def test_requires_owner_for_governed_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-skill",
                "--path",
                tmpdir,
                "--description",
                "Use when a repo needs example-skill workflow help.",
                "--review-cadence",
                "monthly",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--owner", result.stderr)


if __name__ == "__main__":
    unittest.main()
