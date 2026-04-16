#!/usr/bin/env python3
"""Regression tests for the Skill Graph bootstrap utility."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import unittest


SCRIPT = Path(__file__).resolve().parents[0] / "bootstrap_recursive_skill_graph_artifacts.py"
DEFAULT_SCOPES = [
    "frontend/ui/ui-ux-creative-coding",
    "frontend/ui/react-ui-patterns",
    "frontend/ui/frontend-ui-design",
]


def _bootstrap_script(
    *,
    controls_root: Path,
    lessons_root: Path,
    manifest: Path,
    extra_args: list[str] | None = None,
) -> dict:
    args = [
        sys.executable,
        str(SCRIPT),
        "--controls-root",
        str(controls_root),
        "--lessons-root",
        str(lessons_root),
        "--manifest",
        str(manifest),
    ]
    if extra_args:
        args.extend(extra_args)
    proc = subprocess.run(
        args,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.stdout:
        output = proc.stdout.strip()
    else:
        output = "{}"
    summary = json.loads(output)
    return_code = proc.returncode
    if return_code != 0:
        raise RuntimeError(f"bootstrap failed: {proc.stderr or proc.stdout}")
    return summary


class BootstrapRecursiveSkillGraphArtifactsTests(unittest.TestCase):
    def test_bootstrap_initializes_required_control_and_lessons_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            controls_root = root / "controls"
            lessons_root = root / "lessons"
            manifest = root / "pilot" / "artifact-parity-manifest.json"

            summary = _bootstrap_script(
                controls_root=controls_root,
                lessons_root=lessons_root,
                manifest=manifest,
                extra_args=["--scope-skills-comma", ",".join(DEFAULT_SCOPES)],
            )

            self.assertEqual(summary["status"], "ok")
            self.assertGreater(summary["changed_count"], 0)

            self.assertEqual((controls_root / "kill-switch.txt").read_text(encoding="utf-8").strip(), "off")
            self.assertEqual((controls_root / "rollback-required.txt").read_text(encoding="utf-8").strip(), "off")
            self.assertEqual((controls_root / "rollout-mode.txt").read_text(encoding="utf-8").strip(), "observe_only")
            self.assertEqual((controls_root / "auto_capture.disabled").read_text(encoding="utf-8").strip(), "0")
            self.assertEqual((controls_root / "auto_apply.disabled").read_text(encoding="utf-8").strip(), "0")

            for scope_skill in DEFAULT_SCOPES:
                skill_root = controls_root / "skills" / scope_skill
                self.assertEqual((skill_root / "auto_capture.disabled").read_text(encoding="utf-8").strip(), "0")
                self.assertEqual((skill_root / "auto_apply.disabled").read_text(encoding="utf-8").strip(), "0")

            self.assertTrue((lessons_root / "canonical-lessons.jsonl").exists())
            self.assertEqual((lessons_root / "canonical-lessons.jsonl").read_text(encoding="utf-8"), "")
            index = json.loads((lessons_root / "canonical-lesson-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index.get("schema_version"), "1.0")
            self.assertEqual(index.get("scopes"), {})
            self.assertTrue(manifest.exists())

    def test_bootstrap_without_overwrite_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            controls_root = root / "controls"
            lessons_root = root / "lessons"
            manifest = root / "pilot" / "artifact-parity-manifest.json"

            controls_root.mkdir(parents=True)
            (controls_root / "kill-switch.txt").write_text("on\n", encoding="utf-8")
            lessons_root.mkdir(parents=True)
            (lessons_root / "canonical-lessons.jsonl").write_text("{}", encoding="utf-8")

            _bootstrap_script(
                controls_root=controls_root,
                lessons_root=lessons_root,
                manifest=manifest,
            )

            self.assertEqual((controls_root / "kill-switch.txt").read_text(encoding="utf-8"), "on\n")
            self.assertEqual((lessons_root / "canonical-lessons.jsonl").read_text(encoding="utf-8"), "{}")


if __name__ == "__main__":
    unittest.main()
