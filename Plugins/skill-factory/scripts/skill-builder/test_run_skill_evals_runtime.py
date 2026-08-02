#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import subprocess as sp
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

from defusedxml import ElementTree as ET  # noqa: E402
import run_skill_evals  # noqa: E402

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
    _classify_runner_blocker,
    _codex_exec_prefix,
    _filter_cases,
    _preflight_codex_live_runner,
    _filter_cases_for_eval_mode,
    _isolated_codex_home_for_eval,
    _is_smoke_only_case,
    _mark_no_case_evidence_blocked,
    _repo_mise_node_version,
    _scrub_mcp_servers_from_toml,
    _write_junit_report,
    load_evals,
    run_codex_exec,
)




class RunSkillEvalsRuntimeTests(unittest.TestCase):
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


    def test_release_scenario_set_filters_exact_case_ids(self) -> None:
        cases = [
            EvalCase(
                id="writer-gap-gathering",
                name="Writer gap gathering",
                prompt="ok",
                acceptance=["ok"],
            ),
            EvalCase(
                id="generated-eval.writer-gap-gathering",
                name="Generated writer gap gathering",
                prompt="generated",
                acceptance=["generated"],
            ),
        ]

        selected = _filter_cases(
            cases,
            case_filters=["writer-gap-gathering"],
            categories=[],
            exact_case_ids=True,
        )
        self.assertEqual([case.id for case in selected], ["writer-gap-gathering"])


    def test_non_release_case_filter_keeps_substring_matching(self) -> None:
        cases = [
            EvalCase(
                id="writer-gap-gathering",
                name="Writer gap gathering",
                prompt="ok",
                acceptance=["ok"],
            ),
            EvalCase(
                id="generated-eval.writer-gap-gathering",
                name="Generated writer gap gathering",
                prompt="generated",
                acceptance=["generated"],
            ),
        ]

        selected = _filter_cases(
            cases,
            case_filters=["writer-gap-gathering"],
            categories=[],
        )
        self.assertEqual(
            [case.id for case in selected],
            ["writer-gap-gathering", "generated-eval.writer-gap-gathering"],
        )


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


    def test_no_case_evidence_marks_summary_blocked_validation(self) -> None:
        summary = {
            "cases": [],
            "blocked_class_summary": {key: 0 for key in run_skill_evals.RUNNER_BLOCKER_TAXONOMY},
        }

        marked = _mark_no_case_evidence_blocked(summary)

        self.assertTrue(marked)
        self.assertTrue(summary["no_case_evidence"])
        self.assertEqual(summary["blocked_class_summary"]["blocked_validation"], 1)


    def test_new_family_contract_cases_survive_smoke_filter(self) -> None:
        evals_path = SKILL_DIR / "references" / "evals.yaml"

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

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
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


    def test_isolated_codex_home_uses_standalone_profile_without_cloud_base_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            home_root = Path(tmpdir) / "home-root"
            default_home = home_root / ".codex"
            default_home.mkdir(parents=True)
            (default_home / "auth.json").write_text('{"token":"test"}', encoding="utf-8")
            (default_home / "config.toml").write_text('model_provider = "openai"\n', encoding="utf-8")
            (default_home / "oss-local.config.toml").write_text(
                'model = "qwen3.5:9b-mlx"\nmodel_provider = "ollama"\n', encoding="utf-8"
            )

            with unittest.mock.patch("run_skill_evals.Path.home", return_value=home_root):
                with unittest.mock.patch.dict("run_skill_evals.os.environ", {}, clear=True):
                    isolated_home, _warnings = _isolated_codex_home_for_eval("oss-local")

        self.assertTrue((isolated_home / "oss-local.config.toml").is_file())
        self.assertFalse((isolated_home / "config.toml").exists())


    def test_isolated_codex_config_drops_mcp_servers(self) -> None:
        source = textwrap.dedent(
            """
            model = "gpt-test"

            [profiles.test]
            model = "gpt-profile"

            [mcp_servers.linear]
            url = "https://mcp.linear.app/mcp"

            [mcp_servers.linear.tools.save_comment]
            enabled = false

            [tools]
            web_search = true
            """
        ).lstrip()

        scrubbed = _scrub_mcp_servers_from_toml(source)

        self.assertIn("[profiles.test]", scrubbed)
        self.assertIn("[tools]", scrubbed)
        self.assertNotIn("[mcp_servers.linear]", scrubbed)
        self.assertNotIn("save_comment", scrubbed)


    def test_run_codex_exec_ignores_user_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            fake_proc = unittest.mock.Mock(returncode=0, stdout="", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

        self.assertEqual((rc, stdout, stderr, warnings), (0, "", "", []))
        cmd = mocked_run.call_args.args[0]
        self.assertIn("--ignore-user-config", cmd)
        self.assertLess(cmd.index("--ignore-user-config"), cmd.index("--sandbox"))


    def test_codex_exec_prefix_wraps_default_mise_codex_with_repo_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            workspace = root / "workspace"
            codex_bin = home / ".local/share/mise/installs/npm-openai-codex/latest/bin/codex"
            node_bin = home / ".local/share/mise/installs/node/24.13.1/bin/node"
            codex_bin.parent.mkdir(parents=True)
            node_bin.parent.mkdir(parents=True)
            codex_bin.write_text("#!/usr/bin/env node\n", encoding="utf-8")
            node_bin.write_text("#!/bin/sh\n", encoding="utf-8")
            workspace.mkdir()
            (workspace / ".mise.toml").write_text('[tools]\n"node" = "24.13.1"\n', encoding="utf-8")

            with (
                unittest.mock.patch("run_skill_evals.Path.home", return_value=home),
                unittest.mock.patch("run_skill_evals.WORKSPACE_ROOT", workspace),
            ):
                prefix = _codex_exec_prefix(None)

        self.assertEqual(prefix, [str(node_bin), str(codex_bin.resolve()), "exec"])


    def test_repo_mise_node_version_uses_toml_tools_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / ".mise.toml").write_text('[env]\nnode = "not-a-tool"\n[tools]\n"node" = "24.13.1"\n', encoding="utf-8")

            with unittest.mock.patch("run_skill_evals.WORKSPACE_ROOT", workspace):
                version = _repo_mise_node_version()

        self.assertEqual(version, "24.13.1")


    def test_run_codex_exec_skips_ignore_user_config_when_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            fake_proc = unittest.mock.Mock(returncode=0, stdout="", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=False,
            ), unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

        self.assertEqual((rc, stdout, stderr), (0, "", ""))
        self.assertTrue(any("--ignore-user-config" in warning for warning in warnings))
        cmd = mocked_run.call_args.args[0]
        self.assertNotIn("--ignore-user-config", cmd)


    def test_run_codex_exec_retries_no_output_timeout_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            fake_proc = unittest.mock.Mock(returncode=0, stdout="done", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch(
                "run_skill_evals.sp.run",
                side_effect=[
                    sp.TimeoutExpired(cmd=["codex"], timeout=1),
                    fake_proc,
                ],
            ) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

        self.assertEqual((rc, stdout, stderr), (0, "done", ""))
        self.assertEqual(mocked_run.call_count, 2)
        self.assertTrue(any("retrying once" in warning for warning in warnings))


    def test_run_codex_exec_preserves_timeout_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            jsonl_path = workspace_root / "trace.jsonl"

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch(
                "run_skill_evals.sp.run",
                side_effect=sp.TimeoutExpired(
                    cmd=["codex"],
                    timeout=1,
                    output="partial stdout",
                    stderr="partial stderr",
                ),
            ) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=jsonl_path,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

            persisted_jsonl = jsonl_path.read_text(encoding="utf-8")

        self.assertEqual(rc, 124)
        self.assertEqual(stdout, "partial stdout")
        self.assertIn("partial stderr", stderr)
        self.assertIn("codex exec timed out after 1.0 seconds.", stderr)
        self.assertEqual(mocked_run.call_count, 1)
        self.assertEqual(warnings, [])
        self.assertEqual(persisted_jsonl, "partial stdout")


    def test_run_codex_exec_keeps_last_message_artifact_on_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            output_last_message_path.write_text("partial final message", encoding="utf-8")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch(
                "run_skill_evals.sp.run",
                side_effect=sp.TimeoutExpired(cmd=["codex"], timeout=1),
            ) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

            last_message = output_last_message_path.read_text(encoding="utf-8")

        self.assertEqual((rc, stdout), (124, ""))
        self.assertIn("codex exec timed out after 1.0 seconds.", stderr)
        self.assertEqual(mocked_run.call_count, 1)
        self.assertEqual(last_message, "partial final message")
        self.assertEqual(warnings, [])


    def test_timeout_with_only_subprocess_stderr_is_no_output(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text="Command timed out after 10 seconds",
                exit_code=124,
            ),
            "timeout_no_output",
        )


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




if __name__ == "__main__":
    unittest.main()
