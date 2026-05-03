#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
import unittest.mock
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
REPO_ROOT = SCRIPT_DIR.parents[2]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

from defusedxml import ElementTree as ET

from run_skill_evals import (
    EvalCase,
    _acceptance_skip_reason,
    _preflight_codex_live_runner,
    _filter_cases_for_eval_mode,
    _isolated_codex_home_for_eval,
    _is_smoke_only_case,
    _write_junit_report,
    load_evals,
    load_neutral_baseline_approvals,
    main,
    run_discovery_smoke,
)


class RunSkillEvalsModeTests(unittest.TestCase):
    def test_acceptance_skip_reason_only_triggers_for_empty_nonzero_output(self) -> None:
        self.assertEqual(
            _acceptance_skip_reason(exit_code=1, output_text=""),
            "skipped acceptance assertions because the runner exited non-zero and produced no final output",
        )
        self.assertEqual(
            _acceptance_skip_reason(exit_code=2, output_text="   \n"),
            "skipped acceptance assertions because the runner exited non-zero and produced no final output",
        )
        self.assertIsNone(_acceptance_skip_reason(exit_code=1, output_text="partial response"))
        self.assertIsNone(_acceptance_skip_reason(exit_code=0, output_text=""))

    def test_repo_evals_include_family_contract_cases(self) -> None:
        evals_path = REPO_ROOT / "utilities" / "skill-builder" / "references" / "evals.yaml"

        cases = load_evals(evals_path)
        case_map = {case.id: case for case in cases}

        for case_id in [
            "clarification-package-ambiguous",
            "plugin-only-handoff",
            "mixed-authoring-install-handoff",
            "audit-package-validation-first",
            "provenance-import-rollback",
            "builder-round-metadata-contract",
        ]:
            self.assertIn(case_id, case_map)
            self.assertEqual(case_map[case_id].eval_modes, ("smoke", "release"))
            self.assertEqual(case_map[case_id].timeout_profile, "codex-heavy")

    def test_builder_round_metadata_case_has_baseline_contract_fields(self) -> None:
        evals_path = REPO_ROOT / "utilities" / "skill-builder" / "references" / "evals.yaml"
        cases = load_evals(evals_path)
        case_map = {case.id: case for case in cases}
        target = case_map["builder-round-metadata-contract"]

        self.assertEqual(target.baseline_type, "neutral_repo_baseline")
        self.assertEqual(target.metric_availability, "unavailable")
        self.assertEqual(target.iteration_round_state, "reviewed")
        self.assertEqual(target.readiness_state, "comparison_incomplete")
        self.assertEqual(target.neutral_baseline_approval_id, "planner-approved-neutral-baseline-skill-builder")
        self.assertIsInstance(target.comparison_inputs, dict)
        self.assertEqual(target.comparison_inputs["prompt_set"], "frozen-first-response-contract")

        approvals = load_neutral_baseline_approvals(evals_path)
        self.assertIn("planner-approved-neutral-baseline-skill-builder", approvals)

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

    def test_new_family_contract_cases_survive_smoke_filter(self) -> None:
        evals_path = REPO_ROOT / "utilities" / "skill-builder" / "references" / "evals.yaml"

        cases = load_evals(evals_path)
        selected = _filter_cases_for_eval_mode(cases, eval_mode="smoke")
        selected_ids = {case.id for case in selected}

        self.assertTrue(
            {
                "clarification-package-ambiguous",
                "plugin-only-handoff",
                "mixed-authoring-install-handoff",
                "audit-package-validation-first",
                "provenance-import-rollback",
                "builder-round-metadata-contract",
            }.issubset(selected_ids)
        )

    def test_preflight_codex_live_runner_rejects_repo_local_home_without_auth(self) -> None:
        """
        Verifies that _preflight_codex_live_runner rejects a repository-local `.codex` directory when the user's default Codex home is unauthenticated.
        
        Asserts that no warnings are returned, exactly one error is produced, and that the error message includes:
        - the phrase "missing authenticated Codex state",
        - guidance that a repo-local `.codex` is suitable only for discovery/static smoke, and
        - the filesystem path to the default home `.codex`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            repo_home = workspace_root / ".codex"
            repo_home.mkdir()
            home_root = workspace_root / "home-root"
            default_home = home_root / ".codex"
            default_home.mkdir(parents=True)
            (default_home / "auth.json").write_text("{}", encoding="utf-8")

            with unittest.mock.patch("run_skill_evals.Path.home", return_value=home_root):
                errors, warnings = _preflight_codex_live_runner(
                    workspace_root=workspace_root,
                    codex_bin=None,
                    codex_home=repo_home,
                )

        self.assertEqual(warnings, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("missing authenticated Codex state", errors[0])
        self.assertIn("Repo-local `.codex` is suitable for discovery/static smoke", errors[0])
        self.assertIn(str(default_home), errors[0])

    def test_preflight_codex_live_runner_accepts_logged_in_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            codex_home = workspace_root / ".codex"
            codex_home.mkdir()
            (codex_home / "auth.json").write_text("{}", encoding="utf-8")
            fake_proc = unittest.mock.Mock(returncode=0, stdout="Logged in using ChatGPT\n", stderr="")

            with unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
                errors, warnings = _preflight_codex_live_runner(
                    workspace_root=workspace_root,
                    codex_bin=None,
                    codex_home=codex_home,
                )

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        mocked_run.assert_called_once()

    def test_preflight_codex_live_runner_warns_when_env_auth_is_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            codex_home = workspace_root / ".codex"
            codex_home.mkdir()
            fake_proc = unittest.mock.Mock(returncode=1, stdout="Not logged in\n", stderr="")

            with unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc):
                with unittest.mock.patch.dict("run_skill_evals.os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
                    errors, warnings = _preflight_codex_live_runner(
                        workspace_root=workspace_root,
                        codex_bin=None,
                        codex_home=codex_home,
                    )

        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("auth environment variables are present", warnings[0])

    def test_isolated_codex_home_copies_auth_config_and_keeps_sessions_private(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            home_root = Path(tmpdir) / "home-root"
            default_home = home_root / ".codex"
            default_home.mkdir(parents=True)
            (default_home / "auth.json").write_text('{"token":"test"}', encoding="utf-8")
            (default_home / "config.toml").write_text("[profiles.test]\nmodel = \"gpt-test\"\n", encoding="utf-8")

            with unittest.mock.patch("run_skill_evals.Path.home", return_value=home_root):
                with unittest.mock.patch.dict("run_skill_evals.os.environ", {}, clear=True):
                    isolated_home, warnings = _isolated_codex_home_for_eval()

        self.assertNotEqual(isolated_home, default_home)
        self.assertTrue((isolated_home / "auth.json").exists())
        self.assertTrue((isolated_home / "config.toml").exists())
        self.assertTrue((isolated_home / "sessions").is_dir())
        self.assertTrue((isolated_home / "logs").is_dir())
        self.assertIn("Using isolated CODEX_HOME", "\n".join(warnings))

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
            exit_code = main(
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

    def test_summary_and_manifest_include_iteration_round_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
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
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    neutral_baseline_approvals:
                      - id: planner-approved-neutral-baseline-skill-builder
                        rationale: approved for this synthetic regression test
                        approved_by: test
                    cases:
                      - id: builder-round-metadata-contract
                        name: builder round metadata contract
                        prompt: Define one explicit iteration contract.
                        smoke_mode: discovery-round-one
                        baseline_type: neutral_repo_baseline
                        neutral_baseline_approval_id: planner-approved-neutral-baseline-skill-builder
                        comparison_inputs:
                          prompt_set: frozen-first-response-contract
                        iteration_round_state: reviewed
                        metric_availability: unavailable
                        readiness_state: comparison_incomplete
                        comparison_review_artifact: comparison_review.md
                        acceptance:
                          - contains: "## Inputs"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            reports_dir = Path(tmpdir) / "reports"
            exit_code = main(
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

        case = summary["cases"][0]
        self.assertEqual(case["baseline_type"], "neutral_repo_baseline")
        self.assertEqual(case["iteration_round_state"], "reviewed")
        self.assertEqual(case["metric_availability"], "unavailable")
        self.assertEqual(case["readiness_state"], "comparison_incomplete")
        self.assertIn("comparison_review.md", case["comparison_review_artifact"])
        self.assertEqual(case["neutral_baseline_approval"]["id"], "planner-approved-neutral-baseline-skill-builder")
        self.assertEqual(summary["readiness_summary"]["comparison_incomplete"], 1)
        self.assertEqual(summary["round_state_summary"]["reviewed"], 1)
        self.assertIn("planner-approved-neutral-baseline-skill-builder", summary["neutral_baseline_approvals_used"])
        self.assertEqual(
            release_manifest["run"]["readiness_summary"]["comparison_incomplete"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
