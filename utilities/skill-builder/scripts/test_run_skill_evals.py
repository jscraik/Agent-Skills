#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import json
import tempfile
import textwrap
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_skill_evals
from run_skill_evals import (
    EvalCase,
    _filter_cases_for_eval_mode,
    _is_smoke_only_case,
    _write_junit_report,
    load_evals,
    run_discovery_smoke,
)


class RunSkillEvalsModeTests(unittest.TestCase):
    def test_smoke_mode_filters_release_only_and_pressure_cases(self) -> None:
        cases = [
            EvalCase(
                id="happy",
                name="Happy",
                prompt="ok",
                acceptance=["ok"],
                category="happy",
            ),
            EvalCase(
                id="pressure",
                name="Pressure",
                prompt="bad",
                acceptance=["bad"],
                category="pressure",
            ),
            EvalCase(
                id="explicit-release",
                name="Explicit release",
                prompt="release",
                acceptance=["release"],
                eval_modes=("release",),
            ),
            EvalCase(
                id="explicit-smoke",
                name="Explicit smoke",
                prompt="smoke",
                acceptance=["smoke"],
                eval_modes=("smoke",),
            ),
        ]

        selected = _filter_cases_for_eval_mode(cases, eval_mode="smoke")
        self.assertEqual([case.id for case in selected], ["happy", "explicit-smoke"])

    def test_release_mode_keeps_all_cases_by_default(self) -> None:
        cases = [
            EvalCase(id="happy", name="Happy", prompt="ok", acceptance=["ok"], category="happy"),
            EvalCase(
                id="explicit-smoke",
                name="Explicit smoke",
                prompt="smoke",
                acceptance=["smoke"],
                eval_modes=("smoke",),
            ),
            EvalCase(
                id="explicit-release",
                name="Explicit release",
                prompt="release",
                acceptance=["release"],
                eval_modes=("release",),
            ),
        ]

        selected = _filter_cases_for_eval_mode(cases, eval_mode="release")
        self.assertEqual([case.id for case in selected], ["happy", "explicit-release"])

    def test_release_mode_keeps_dual_tagged_smoke_cases_for_live_runners(self) -> None:
        cases = [
            EvalCase(
                id="discovery-round-one",
                name="Discovery round one",
                prompt="discover",
                acceptance=["discover"],
                smoke_mode="discovery-round-one",
                eval_modes=("smoke", "release"),
            ),
            EvalCase(
                id="smoke-only-discovery",
                name="Smoke only discovery",
                prompt="smoke",
                acceptance=["smoke"],
                smoke_mode="discovery-round-six",
                eval_modes=("smoke",),
            ),
            EvalCase(
                id="release-only",
                name="Release only",
                prompt="release",
                acceptance=["release"],
                eval_modes=("release",),
            ),
        ]

        selected = _filter_cases_for_eval_mode(cases, eval_mode="release")
        routed = [case for case in selected if not _is_smoke_only_case(case)]
        self.assertEqual([case.id for case in routed], ["discovery-round-one", "release-only"])

    def test_load_evals_parses_eval_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            evals_path = Path(tmpdir) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: sample
                        name: sample
                        prompt: hi
                        acceptance: ["ok"]
                        eval_modes: [smoke, release]
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            cases = load_evals(evals_path)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].eval_modes, ("smoke", "release"))

    def test_write_junit_report_outputs_failures(self) -> None:
        summary = {
            "skill": "skill-builder",
            "generated_at": "2026-03-21T00:00:00Z",
            "run_id": "run-1",
            "tier2_mode": "warn",
            "tier1_failures": 1,
            "cases": [
                {
                    "id": "good",
                    "name": "good",
                    "timeout_sec": 10,
                    "tier1_failed": False,
                    "tier2_failed": False,
                    "tier1_failures": [],
                    "tier2_findings": [],
                    "warnings": [],
                    "dir": "/tmp/good",
                },
                {
                    "id": "bad",
                    "name": "bad",
                    "timeout_sec": 20,
                    "tier1_failed": True,
                    "tier2_failed": False,
                    "tier1_failures": ["runner failed"],
                    "tier2_findings": [],
                    "warnings": ["warned"],
                    "dir": "/tmp/bad",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "junit.xml"
            _write_junit_report(summary, out)
            tree = ET.parse(out)

        suite = tree.getroot()
        self.assertEqual(suite.tag, "testsuite")
        self.assertEqual(suite.attrib["tests"], "2")
        self.assertEqual(suite.attrib["failures"], "1")
        cases = suite.findall("testcase")
        self.assertEqual(len(cases), 2)
        self.assertIsNotNone(cases[1].find("failure"))

    def test_write_junit_report_marks_tier2_fail_mode_cases_as_failures(self) -> None:
        summary = {
            "skill": "skill-builder",
            "generated_at": "2026-03-21T00:00:00Z",
            "run_id": "run-2",
            "tier2_mode": "fail",
            "tier1_failures": 0,
            "cases": [
                {
                    "id": "tier2-only",
                    "name": "tier2-only",
                    "timeout_sec": 15,
                    "tier1_failed": False,
                    "tier2_failed": True,
                    "tier1_failures": [],
                    "tier2_findings": ["rubric score below threshold"],
                    "warnings": [],
                    "dir": "/tmp/tier2-only",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "junit.xml"
            _write_junit_report(summary, out)
            tree = ET.parse(out)

        suite = tree.getroot()
        self.assertEqual(suite.attrib["failures"], "1")
        case_el = suite.find("testcase")
        assert case_el is not None
        self.assertIsNotNone(case_el.find("failure"))
        self.assertIsNone(case_el.find("skipped"))

    def test_release_manifest_includes_final_artifact_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
                    version: "1.2.3"
                    compatibility: codex
                    release_channel: stable
                    schema_version: 1
                    ---

                    ## Discovery interview
                    - ask one round at a time
                    - use a plain-language question
                    - explain why the round matters
                    - avoid dumping the whole interview plan at once
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "discovery-interview.md").write_text(
                textwrap.dedent(
                    """
                    ## Request user input mini-templates

                    What should this skill help you do?

                    ## Copy paste payload examples

                    ## Round 6: Confirmation

                    Does this capture it well enough for me to build?
                    Anything to add or change before I build it?
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: discovery-round-one
                        name: discovery smoke
                        prompt: Help define the skill.
                        smoke_mode: discovery-round-one
                        acceptance:
                          - contains: "Round 1 question:"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            reports_dir = Path(tmpdir) / "reports"
            exit_code = run_skill_evals.main(
                [
                    str(skill_dir),
                    "--runner",
                    "discovery-smoke",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(exit_code, 0)
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            self.assertTrue(report_dirs)
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))
            release_manifest = json.loads((report_dirs[-1] / "release_manifest.json").read_text(encoding="utf-8"))

        self.assertIn("junit", summary["artifacts"])
        self.assertIn("release_manifest", summary["artifacts"])
        self.assertEqual(release_manifest["artifacts"]["junit"], summary["artifacts"]["junit"])
        self.assertEqual(
            release_manifest["artifacts"]["release_manifest"],
            summary["artifacts"]["release_manifest"],
        )

    def test_discovery_smoke_uses_skill_specific_questions_and_canonical_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "docs-expert"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                textwrap.dedent(
                    """
                    ---
                    name: docs-expert
                    ---

                    ## Discovery interview
                    - ask one round at a time
                    - use a plain-language question
                    - explain why the round matters
                    - avoid dumping the whole interview plan at once
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "discovery-interview.md").write_text(
                textwrap.dedent(
                    """
                    ## Request user input mini-templates

                    Which documentation surface should this update target first?

                    ## Copy paste payload examples

                    ## Round 6: Confirmation

                    Does this capture the docs work well enough for me to implement?
                    Anything to add or change before I implement it?
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            round_one_case = EvalCase(
                id="round-one",
                name="round-one",
                prompt="discover",
                acceptance=[],
                smoke_mode="discovery-round-one",
            )
            round_six_case = EvalCase(
                id="round-six",
                name="round-six",
                prompt="discover",
                acceptance=[],
                smoke_mode="discovery-round-six",
            )
            round_one_path = skill_dir / "round-one.txt"
            round_six_path = skill_dir / "round-six.txt"

            round_one_exit, round_one_response, _, _ = run_discovery_smoke(
                skill_md_path=skill_md,
                skill_dir=skill_dir,
                case=round_one_case,
                output_last_message_path=round_one_path,
            )
            round_six_exit, round_six_response, _, _ = run_discovery_smoke(
                skill_md_path=skill_md,
                skill_dir=skill_dir,
                case=round_six_case,
                output_last_message_path=round_six_path,
            )
            self.assertEqual(round_one_exit, 0)
            self.assertIn("## Inputs", round_one_response)
            self.assertIn("## Outputs", round_one_response)
            self.assertIn("Which documentation surface should this update target first?", round_one_response)
            self.assertEqual(round_one_path.read_text(encoding="utf-8"), round_one_response)

            self.assertEqual(round_six_exit, 0)
            self.assertIn("## Outputs", round_six_response)
            self.assertIn("Does this capture the docs work well enough for me to implement?", round_six_response)
            self.assertIn("Anything to add or change before I implement it?", round_six_response)
            self.assertEqual(round_six_path.read_text(encoding="utf-8"), round_six_response)


if __name__ == "__main__":
    unittest.main()
