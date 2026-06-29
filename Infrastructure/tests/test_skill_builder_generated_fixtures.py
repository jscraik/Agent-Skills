from __future__ import annotations

import importlib.util
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


def test_codex_profile_runner_preserves_profile_config(tmp_path: Path) -> None:
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
    assert "--ignore-user-config" not in cmd
    assert mocked_run.call_args.kwargs["start_new_session"] is True
    assert any("explicit --profile" in warning for warning in warnings)
    assert any("Disabled Codex apps" in warning for warning in warnings)


def test_codex_help_probe_runs_in_isolated_session() -> None:
    runner = _load_runner_module()
    runner._CODEX_HELP_CACHE.clear()
    fake_proc = mock.Mock(returncode=0, stdout="--profile\n", stderr="")

    with mock.patch.object(runner.sp, "run", return_value=fake_proc) as mocked_run:
        help_text = runner._codex_help_text(None)

    assert "--profile" in help_text
    assert mocked_run.call_args.kwargs["start_new_session"] is True


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
