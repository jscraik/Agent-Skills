"""Behaviour checks for the deterministic skill-spotlight helper."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "lifecycle-and-sync" / "skill_spotlight.py"
SPEC = importlib.util.spec_from_file_location("skill_spotlight", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
skill_spotlight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skill_spotlight)


class SkillSpotlightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.original_runs_root = skill_spotlight.RUNS_ROOT
        self.original_skills_root = skill_spotlight.SKILLS_ROOT
        self.addCleanup(self.tmpdir.cleanup)
        self.addCleanup(self._restore_roots)

    def _restore_roots(self) -> None:
        skill_spotlight.RUNS_ROOT = self.original_runs_root
        skill_spotlight.SKILLS_ROOT = self.original_skills_root

    def test_malformed_run_record_is_ignored(self) -> None:
        runs_root = self.root / "runs"
        run_dir = runs_root / "run_invalid"
        run_dir.mkdir(parents=True)
        (run_dir / "run.json").write_text("not json", encoding="utf-8")
        skill_spotlight.RUNS_ROOT = runs_root

        self.assertEqual(skill_spotlight.analyze_failures(), {})

    def test_fallback_selects_oldest_skill_deterministically(self) -> None:
        skills_root = self.root / "skills"
        for name, timestamp in (("newer", 2_000_000_000), ("older", 1_000_000_000)):
            entrypoint = skills_root / name / "SKILL.md"
            entrypoint.parent.mkdir(parents=True)
            entrypoint.write_text("# skill\n", encoding="utf-8")
            os.utime(entrypoint, (timestamp, timestamp))
        skill_spotlight.RUNS_ROOT = self.root / "no-runs"
        skill_spotlight.SKILLS_ROOT = skills_root

        spotlight = skill_spotlight.pick_spotlight()

        self.assertEqual(spotlight["skill"], "older")
        self.assertIn("Least-recently-modified", spotlight["signal"])


if __name__ == "__main__":
    unittest.main()
