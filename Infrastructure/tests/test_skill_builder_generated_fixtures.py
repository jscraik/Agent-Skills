from __future__ import annotations

import importlib.util
import json
import sys
import textwrap
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py"
RUNNER_DIR = RUNNER_PATH.parent


def _load_runner_module():
    if str(RUNNER_DIR) not in sys.path:
        sys.path.insert(0, str(RUNNER_DIR))
    spec = importlib.util.spec_from_file_location("skill_builder_run_skill_evals", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_release_eval_fixture(tmp_path: Path) -> Path:
    references_dir = tmp_path / "references"
    fixtures_dir = references_dir / "evals"
    fixtures_dir.mkdir(parents=True)
    evals_path = references_dir / "evals.yaml"
    evals_path.write_text(
        textwrap.dedent(
            """
            cases:
              - id: canonical-case
                name: Canonical case
                prompt: Check the canonical case.
                acceptance:
                  - contains: canonical
                eval_modes: [smoke, release]
            """
        ),
        encoding="utf-8",
    )
    return evals_path


def _write_reviewed_generated_fixture(fixtures_dir: Path) -> None:
    (fixtures_dir / "eval.reader-state-map.md").write_text(
        textwrap.dedent(
            """
            # eval.reader-state-map: Reader State Map

            Knowledge claim: Writer builds a reader-state map before rewriting.
            Behavior under test: Reader-state mapping.
            Expected agent move: Produces a reader-state map and cites missing assumptions.
            Failure mode: Rewrites directly with no reader map.
            Given: A README has unstated prerequisites.
            Should: Write reader-state-map.md with citations and missing assumptions.
            Expected failure: Rewrites directly with no reader map.
            """
        ),
        encoding="utf-8",
    )


def _assert_generated_fixture_case(runner, cases) -> None:
    case_map = {case.id: case for case in cases}
    release_cases = runner._filter_cases_for_eval_mode(cases, eval_mode="release")
    smoke_cases = runner._filter_cases_for_eval_mode(cases, eval_mode="smoke")

    assert "generated-eval.reader-state-map" in case_map
    assert case_map["generated-eval.reader-state-map"].eval_modes == ("release",)
    assert case_map["generated-eval.reader-state-map"].reproduce == "references/evals/eval.reader-state-map.md"
    assert {"type": "not_contains", "value": "Rewrites directly with no reader map."} in case_map[
        "generated-eval.reader-state-map"
    ].acceptance
    assert [case.id for case in release_cases] == ["canonical-case", "generated-eval.reader-state-map"]
    assert [case.id for case in smoke_cases] == ["canonical-case"]


def test_release_evals_import_reviewed_generated_fixtures(tmp_path: Path) -> None:
    runner = _load_runner_module()
    evals_path = _write_release_eval_fixture(tmp_path)
    _write_reviewed_generated_fixture(evals_path.parent / "evals")
    cases = runner.load_evals(evals_path)

    _assert_generated_fixture_case(runner, cases)


def test_codex_profile_runner_ignores_base_user_config_while_preserving_profile(tmp_path: Path) -> None:
    runner = _load_runner_module()
    output_last_message_path = tmp_path / "last.txt"
    fake_proc = mock.Mock(returncode=0, stdout="", stderr="")

    with (
        mock.patch.object(runner, "_codex_supports_exec_flag", return_value=True),
        mock.patch.object(runner.sp, "run", return_value=fake_proc) as mocked_run,
    ):
        rc, stdout, stderr, warnings = runner.run_codex_exec(
            workspace_root=tmp_path,
            prompt="Route only.",
            output_last_message_path=output_last_message_path,
            output_schema_path=None,
            sandbox="read-only",
            ask_for_approval=None,
            model=None,
            profile="oss-local",
            codex_home=tmp_path / ".codex",
            jsonl_path=None,
            codex_bin=None,
            timeout_sec=1,
            timeout_profile="default",
        )

    cmd = mocked_run.call_args.args[0]
    assert (rc, stdout, stderr) == (0, "", "")
    assert "--profile" in cmd
    assert cmd[cmd.index("--profile") + 1] == "oss-local"
    assert "--disable" in cmd
    assert cmd[cmd.index("--disable") + 1] == "apps"
    assert "--ignore-user-config" in cmd
    assert cmd.index("--ignore-user-config") < cmd.index("--profile")
    assert mocked_run.call_args.kwargs["start_new_session"] is True
    assert any("preserving the explicit --profile" in warning for warning in warnings)
    assert any("Disabled Codex apps" in warning for warning in warnings)


def test_codex_help_probe_runs_in_isolated_session() -> None:
    runner = _load_runner_module()
    runner._codex_help_text.cache_clear()
    fake_proc = mock.Mock(returncode=0, stdout="--profile\n", stderr="")

    with mock.patch.object(runner.sp, "run", return_value=fake_proc) as mocked_run:
        help_text = runner._codex_help_text(None)

    assert "--profile" in help_text
    assert mocked_run.call_args.kwargs["start_new_session"] is True


def test_codex_tool_payload_errors_block_runtime_before_skill_scoring() -> None:
    runner = _load_runner_module()

    blocker = runner._classify_runner_blocker(
        output_text="",
        stdout_text='{"type":"error","message":"input[32]: unknown input item type: agent_message"}',
        stderr_text=(
            "failed to parse function arguments: invalid type: string \"15000\", expected usize\n"
            "Fatal error: tool exec invoked with incompatible payload\n"
        ),
        exit_code=1,
    )

    assert blocker == "blocked_runtime"


def test_provisional_workflow_closeout_records_prompt_only_case_dir(tmp_path: Path) -> None:
    runner = _load_runner_module()
    reports_base = tmp_path / "Infrastructure/artifacts/skills/example-skill/run-widened"
    case_dir = reports_base / "02-happy-scorecard"
    case_dir.mkdir(parents=True)
    (case_dir / "prompt.txt").write_text("Task: score the fixture\n", encoding="utf-8")

    closeout_path = runner._write_provisional_workflow_closeout(
        reports_base=reports_base,
        workspace_root=tmp_path,
        skill_dir=tmp_path / "Skills/example-skill",
        eval_mode="smoke",
        runner_mode="codex",
        next_reproduce_command="python3 run_skill_evals.py Skills/example-skill --eval-mode smoke --runner codex",
    )

    closeout = json.loads(closeout_path.read_text(encoding="utf-8"))
    assert closeout["schema_version"] == "skills-sdk.eval-closeout.v1"
    assert closeout["status"] == "blocked"
    assert closeout["blocker_class"] == "blocked_missing_artifact"
    assert closeout["mutation_allowed"] is False
    assert closeout["registry_update_allowed"] is False
    assert closeout["closeout_validation"]["status"] == "pass"
    assert closeout["cases"] == [
        {
            "id": "happy-scorecard",
            "status": "blocked",
            "blocker_class": "blocked_missing_artifact",
            "expected_artifacts": ["result.json"],
            "actual_artifacts": ["prompt.txt"],
            "result_path": "Infrastructure/artifacts/skills/example-skill/run-widened/02-happy-scorecard",
        }
    ]


def test_next_reproduce_command_preserves_filters_and_runner_selection() -> None:
    runner = _load_runner_module()
    args = runner.build_arg_parser().parse_args([
        "Skills/example-skill",
        "--eval-mode",
        "smoke",
        "--runners",
        "codex,codex-kimi",
        "--case",
        "case-one",
        "--case",
        "case-two,case-three",
        "--category",
        "safety",
        "--timeout-sec",
        "17",
        "--timeout-profile",
        "codex-heavy",
        "--model",
        "gpt-example",
        "--profile",
        "oss-local",
    ])

    command = runner._build_next_reproduce_command(
        args,
        selected_runners=["codex", "codex-kimi"],
        capture_jsonl=True,
    )

    assert command == (
        "python3 Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py "
        "Skills/example-skill --eval-mode smoke --runners codex,codex-kimi "
        "--case case-one --case case-two,case-three --category safety "
        "--timeout-sec 17.0 --timeout-profile codex-heavy --capture-jsonl "
        "--model gpt-example --profile oss-local"
    )


def test_discovery_question_assertion_accepts_scope_question_before_edits() -> None:
    runner = _load_runner_module()

    failures = runner.evaluate_assertions_text(
        (
            "Before making edits, which documentation path or surface should I inspect first: "
            "canonical docs, generated projections, publication surfaces, or audit-only?"
        ),
        [{"type": "discovery_question", "value": "ask for scope before edits"}],
        skill_name="technical-writer",
        selected_skill=True,
    )

    assert failures == []


def test_discovery_question_assertion_rejects_edit_claims() -> None:
    runner = _load_runner_module()

    failures = runner.evaluate_assertions_text(
        "I updated the README. Which docs should I inspect next?",
        [{"type": "discovery_question", "value": "ask for scope before edits"}],
        skill_name="technical-writer",
        selected_skill=True,
    )

    assert failures == ["discovery_question failed: response claimed an edit before discovery"]


def test_isolated_codex_home_copies_profile_configs(tmp_path: Path) -> None:
    runner = _load_runner_module()
    source_home = tmp_path / "source-codex"
    source_home.mkdir()
    for name in ("auth.json", "config.toml", "oss-local.config.toml", "oss-cloud.config.toml"):
        (source_home / name).write_text(f"{name}\n", encoding="utf-8")

    with (
        mock.patch.object(runner, "_effective_codex_home", return_value=source_home),
        mock.patch.object(runner.atexit, "register"),
    ):
        isolated_home, warnings = runner._isolated_codex_home_for_eval()

    assert not [warning for warning in warnings if "Could not copy" in warning]
    for name in ("auth.json", "config.toml", "oss-local.config.toml", "oss-cloud.config.toml"):
        assert (isolated_home / name).read_text(encoding="utf-8") == f"{name}\n"
