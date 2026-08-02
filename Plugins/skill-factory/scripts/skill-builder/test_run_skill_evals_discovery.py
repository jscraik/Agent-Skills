#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import json
import io
import sys
import tempfile
import textwrap
import unittest
import unittest.mock
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
REPO_ROOT = SCRIPT_DIR.parents[3]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)
SKILL_DIR = SCRIPT_DIR.parents[1] / "skills" / "code_quality_review" / "skill-builder"


existing_runner = sys.modules.get("run_skill_evals")
if existing_runner is not None:
    existing_path = Path(str(getattr(existing_runner, "__file__", ""))).resolve()
    if existing_path.parent != SCRIPT_DIR:
        del sys.modules["run_skill_evals"]

existing_trace_checks = sys.modules.get("deterministic_trace_checks")
if existing_trace_checks is not None:
    existing_path = Path(str(getattr(existing_trace_checks, "__file__", ""))).resolve()
    if existing_path.parent != SCRIPT_DIR:
        del sys.modules["deterministic_trace_checks"]

from run_skill_evals import (  # noqa: E402
    EvalCase,
    _resolve_existing_optional_case_artifact_path,
    main,
    run_discovery_smoke,
    _dependency_manifest_paths,
    _release_dependency_scan_roots,
    _snyk_release_gate_passed,
)




class RunSkillEvalsDiscoveryTests(unittest.TestCase):
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

                    ## Copy-paste payload examples

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
                        should_trigger: true
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
        self.assertEqual(summary["cases"][0]["warnings"], [])
        self.assertTrue(summary["cases"][0]["runners"]["discovery-smoke"]["metrics"]["selected_skill"])
        self.assertEqual(summary["cases"][0]["riteway"]["unit"], "discovery smoke")
        self.assertIn("eval_contract_migration", summary)
        self.assertIn("release_manifest", summary["artifacts"])
        self.assertEqual(release_manifest["artifacts"]["junit"], summary["artifacts"]["junit"])
        self.assertEqual(
            release_manifest["artifacts"]["release_manifest"],
            summary["artifacts"]["release_manifest"],
        )


    def test_discovery_smoke_accepts_legacy_payload_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
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

                    ## Round 6: Confirmation

                    Does this capture it well enough for me to build?
                    Anything to add or change before I build it?
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "last-message.md"

            exit_code, _, _, warnings = run_discovery_smoke(
                skill_md_path=skill_md,
                skill_dir=skill_dir,
                case=EvalCase(
                    id="discovery-round-one",
                    name="discovery smoke",
                    prompt="Help define the skill.",
                    smoke_mode="discovery-round-one",
                    should_trigger=True,
                    acceptance=[],
                ),
                output_last_message_path=output_path,
            )

        self.assertEqual(0, exit_code)
        self.assertNotIn("discovery-interview.md missing payload examples section", "\n".join(warnings))


    def test_pass_rate_policy_calibrates_only_when_artifact_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "reports" / "demo-skill" / "01-calibrated"
            case_dir.mkdir(parents=True)
            (case_dir / "calibration.json").write_text('{"baseline": 0.9}\n', encoding="utf-8")

            self.assertEqual(
                _resolve_existing_optional_case_artifact_path(case_dir, "calibration.json"),
                str((case_dir / "calibration.json").resolve()),
            )
            self.assertIsNone(
                _resolve_existing_optional_case_artifact_path(case_dir, "missing-calibration.json")
            )


    def test_snyk_release_gate_is_not_required_for_skill_md_only_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")

            self.assertEqual(_dependency_manifest_paths(skill_dir), [])
            self.assertTrue(_snyk_release_gate_passed({"required": False, "status": "not_applicable"}))


    def test_snyk_release_gate_requires_success_for_manifest_backed_packages(self) -> None:
        self.assertTrue(_snyk_release_gate_passed({"required": True, "status": "success"}))
        blocking_statuses = [
            "not_applicable",
            "blocked_auth",
            "blocked_missing_binary",
            "blocked_no_supported_projects",
            "advisory",
            "error",
        ]
        for status in blocking_statuses:
            self.assertFalse(_snyk_release_gate_passed({"required": True, "status": status}))


    def test_dependency_manifest_detection_ignores_generated_dependency_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            (skill_dir / "node_modules" / "left-pad").mkdir(parents=True)
            (skill_dir / "package.json").write_text("{}", encoding="utf-8")
            (skill_dir / "node_modules" / "left-pad" / "package.json").write_text("{}", encoding="utf-8")

            manifests = _dependency_manifest_paths(skill_dir)

        self.assertEqual([path.name for path in manifests], ["package.json"])


    def test_dependency_manifest_detection_includes_plugin_root_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_root = Path(tmpdir) / "Plugins" / "demo-plugin"
            skill_dir = plugin_root / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            (plugin_root / "package.json").write_text("{}", encoding="utf-8")

            manifests = _dependency_manifest_paths(skill_dir)
            scan_roots = _release_dependency_scan_roots(skill_dir)

        self.assertEqual([path.name for path in manifests], ["package.json"])
        self.assertEqual(scan_roots[-1].name, "demo-plugin")


    @unittest.mock.patch("run_skill_evals.shutil.which", return_value="/usr/local/bin/snyk")
    @unittest.mock.patch("run_skill_evals.sp.run")
    def test_release_mode_blocks_manifest_backed_package_without_snyk_auth(self, mock_run, _mock_which) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo-skill\nversion: '1.0.0'\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            (skill_dir / "package.json").write_text('{"name":"demo-skill"}\n', encoding="utf-8")
            (refs_dir / "discovery-interview.md").write_text(
                "## Request user input mini-templates\n\nWhat should this skill do?\n\n## Copy-paste payload examples\n",
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
                        eval_modes: [release]
                        should_trigger: true
                        acceptance:
                          - contains: "Round 1 question:"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            mock_run.side_effect = [
                unittest.mock.Mock(returncode=0, stdout="abc123\n", stderr=""),
                unittest.mock.Mock(returncode=0, stdout="main\n", stderr=""),
                unittest.mock.Mock(returncode=2, stdout="", stderr="Use snyk auth to authenticate."),
            ]

            reports_dir = Path(tmpdir) / "reports"
            exit_code = main(
                [
                    str(skill_dir),
                    "--runner",
                    "discovery-smoke",
                    "--eval-mode",
                    "release",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))
            release_manifest = json.loads((report_dirs[-1] / "release_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["decision"], "blocked")
        self.assertEqual(summary["security_dependency_screening"]["status"], "blocked_auth")
        self.assertEqual(
            release_manifest["run"]["security_dependency_screening"]["status"],
            "blocked_auth",
        )


    def test_runner_capacity_blocker_marks_summary_decision_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, unittest.mock.patch(
            "run_skill_evals._preflight_codex_live_runner",
            return_value=([], []),
        ), unittest.mock.patch(
            "run_skill_evals.run_codex_exec",
            return_value=(
                1,
                (
                    '{"type":"error","message":"You\'ve hit your usage limit for '
                    'GPT-5.3-Codex-Spark. Switch to another model now."}'
                ),
                "",
                [],
            ),
        ):
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: capacity-case
                        name: capacity case
                        prompt: Use the skill.
                        eval_modes: [smoke]
                        should_trigger: true
                        acceptance:
                          - contains: "done"
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
                    "codex",
                    "--eval-mode",
                    "smoke",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["decision"], "blocked")
        self.assertEqual(summary["blocked_cases"], 1)
        self.assertEqual(summary["blocked_class_summary"]["blocked_runtime"], 1)


    def test_discovery_smoke_requires_explicit_smoke_mode_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "behavior-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: behavior-skill
                    ---

                    ## Workflow
                    Do behavior work.
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
                      - id: behavior
                        name: behavior
                        prompt: Review this skill behavior.
                        acceptance:
                          - contains: "validation"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            reports_dir = Path(tmpdir) / "reports"
            with unittest.mock.patch("sys.stderr") as stderr:
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

            self.assertEqual(exit_code, 1)
            self.assertIn("requires eval cases with `smoke_mode`", "".join(call.args[0] for call in stderr.write.call_args_list if call.args))


    def test_main_reports_invalid_reporting_metadata_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo-skill\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    reporting:
                      preferred_source_format: [MDX]
                    cases:
                      - id: discovery-round-one
                        name: discovery smoke
                        prompt: Help define the skill.
                        smoke_mode: discovery-round-one
                        should_trigger: true
                        acceptance:
                          - contains: "Round 1 question:"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with unittest.mock.patch("sys.stderr", stderr):
                exit_code = main(
                    [
                        str(skill_dir),
                        "--runner",
                        "discovery-smoke",
                        "--reports-dir",
                        str(Path(tmpdir) / "reports"),
                        "--format",
                        "json",
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("ERROR:", stderr.getvalue())
        self.assertIn("preferred_source_format", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


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

                    ## Copy-paste payload examples

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


    def test_discovery_smoke_accepts_legacy_payload_examples_heading(self) -> None:
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

                    ## Payload examples

                    ## Round 6: Confirmation

                    Does this capture the docs work well enough for me to implement?
                    Anything to add or change before I implement it?
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            case = EvalCase(
                id="legacy-heading",
                name="legacy-heading",
                prompt="discover",
                acceptance=[],
                smoke_mode="discovery-round-one",
            )
            exit_code, _response, _stderr, warnings = run_discovery_smoke(
                skill_md_path=skill_md,
                skill_dir=skill_dir,
                case=case,
                output_last_message_path=skill_dir / "legacy-heading.txt",
            )

        self.assertEqual(exit_code, 0)
        self.assertNotIn("discovery-interview.md missing payload examples section", "\n".join(warnings))




if __name__ == "__main__":
    unittest.main()
