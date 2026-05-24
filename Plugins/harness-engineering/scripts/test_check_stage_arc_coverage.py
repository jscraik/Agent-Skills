#!/usr/bin/env python3
"""Tests for check_stage_arc_coverage.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_stage_arc_coverage import validate


VALID_SKILL = """---
name: he-example
---
# Example
## Outputs
Return stage_arc_boundary with left_arc, active_arc, right_arc, coding_lens,
and testing_lens.
## Procedure
Apply ../../references/stage-arc-boundary-contract.md.
"""


class StageArcCoverageTests(unittest.TestCase):
    def test_valid_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "he-example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(VALID_SKILL, encoding="utf-8")

            self.assertEqual(validate(root), [])

    def test_missing_lenses_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "he-example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                VALID_SKILL.replace("coding_lens,\nand testing_lens", "coverage"),
                encoding="utf-8",
            )

            errors = validate(root)

        self.assertEqual(len(errors), 1)
        self.assertIn("coding_lens", errors[0])
        self.assertIn("testing_lens", errors[0])


if __name__ == "__main__":
    unittest.main()
