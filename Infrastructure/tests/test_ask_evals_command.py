from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import evals  # noqa: E402


def test_smoke_evals_use_codex_spark_without_reasoning_level(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "gpt-5.3-codex-spark"
    assert "--reasoning" not in cmd
    assert "--reasoning-effort" not in cmd
    assert "--profile" not in cmd
    assert "--codex-arg" in cmd
    assert cmd[cmd.index("--codex-arg") + 1] == "--ignore-user-config"


def test_smoke_evals_accept_model_override_for_quota_recovery(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            skip_tessl=True,
            model="gpt-5.4-mini",
        )

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "gpt-5.4-mini"


def test_smoke_evals_pass_case_filters_to_skill_runner(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            skip_tessl=True,
            cases=["doctor-runtime", "budget-limited"],
        )

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert cmd.count("--case") == 2
    first = cmd.index("--case")
    second = cmd.index("--case", first + 1)
    assert cmd[first + 1] == "doctor-runtime"
    assert cmd[second + 1] == "budget-limited"


def test_smoke_evals_splits_comma_separated_case_filters(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            skip_tessl=True,
            cases=["doctor-runtime,budget-limited"],
        )

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert cmd.count("--case") == 2
    first = cmd.index("--case")
    second = cmd.index("--case", first + 1)
    assert cmd[first + 1] == "doctor-runtime"
    assert cmd[second + 1] == "budget-limited"


def test_release_evals_do_not_force_smoke_model(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="release", skip_tessl=True)

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" not in cmd


def _write_example_skill(tmp_path: Path) -> Path:
    skill_root = tmp_path / "Skills" / "example-skill"
    references = skill_root / "references"
    references.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("# Example Skill\n", encoding="utf-8")
    (references / "evals.yaml").write_text(
        'cases:\n  - id: smoke-example\n    prompt: "Do the example task."\n',
        encoding="utf-8",
    )
    (references / "contract.yaml").write_text("version: 1\n", encoding="utf-8")
    (skill_root / "secret-not-staged.txt").write_text("do not copy\n", encoding="utf-8")
    return skill_root


def test_evals_can_block_tessl_project_save_when_policy_disables_automatic_run(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
        mock.patch.dict(evals.os.environ, {"ASK_TESSL_PROJECT_SAVE_APPROVED": ""}, clear=False),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            allow_tessl_project_save=False,
        )

    assert result.status == "error"
    assert run.call_count == 1
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["approval"]["required"] is True
    assert tessl_eval["approval"]["rerun_with"] == "--allow-tessl-project-save"
    assert "compatibility approval gate" in tessl_eval["blocker"]
    assert "ask-tessl-evals" in tessl_eval["staged_source"]
    assert tessl_eval["policy"]["no_registry_upload"] is True
    assert tessl_eval["policy"]["network_permission_required_by_repo"] is False


def test_evals_run_native_tessl_by_default_with_temp_staged_source(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    skill_root = _write_example_skill(tmp_path)

    def fake_run(cmd: list[str], **kwargs: object) -> mock.Mock:
        if cmd[1:4] != ["eval", "run", "--json"]:
            return completed

        staged_source = Path(cmd[4])
        assert cmd[:4] == ["/usr/local/bin/tessl", "eval", "run", "--json"]
        assert staged_source != skill_root
        assert staged_source.exists()
        assert "ask-tessl-evals" in str(staged_source)
        assert staged_source.is_relative_to(Path(str(kwargs["cwd"])))
        assert (staged_source / "SKILL.md").read_text(encoding="utf-8") == "# Example Skill\n"
        assert (staged_source / "references" / "evals.yaml").exists()
        assert (staged_source / "references" / "contract.yaml").exists()
        assert (staged_source / "tessl.json").exists()
        assert (staged_source / "scenarios" / "smoke-example" / "task.md").exists()
        assert (
            staged_source / "scenarios" / "smoke-example" / "task.md"
        ).read_text(encoding="utf-8") == "Do the example task.\n"
        assert not (staged_source / "secret-not-staged.txt").exists()
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run) as run,
        mock.patch.dict(evals.os.environ, {"ASK_TESSL_PROJECT_SAVE_APPROVED": ""}, clear=False),
    ):
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke")

    assert result.status == "success"
    assert run.call_count == 2
    tessl_cmd = run.call_args_list[1].args[0]
    assert tessl_cmd[:4] == ["/usr/local/bin/tessl", "eval", "run", "--json"]
    assert tessl_cmd[4] != "Skills/example-skill"
    assert "publish" not in tessl_cmd
    assert "upload" not in tessl_cmd
    assert "registry" not in tessl_cmd
    assert result.data["tessl_eval"]["source_path"] == "Skills/example-skill"
    assert result.data["tessl_eval"]["staged_files"] == [
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "scenarios/smoke-example/task.md",
        "tessl.json",
    ]
    assert result.data["tessl_eval"]["policy"]["no_registry_upload"] is True
    assert result.data["tessl_eval"]["policy"]["temp_staged_project_input_only"] is True
    assert result.data["tessl_eval"]["policy"]["network_permission_required_by_repo"] is False
    assert result.data["tessl_eval"]["policy"]["project_save_default"] == "automatic"


def test_evals_skip_tessl_escape_hatch(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    assert run.call_count == 1
    assert result.data["tessl_eval"]["status"] == "skipped"


def test_evals_classify_missing_tessl_project_link(tmp_path: Path) -> None:
    completed_eval = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_tessl = mock.Mock(
        returncode=1,
        stdout="",
        stderr="No existing project safely matches this directory.",
    )
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=[completed_eval, completed_tessl]),
    ):
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke")

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert "project/workspace is linked" in tessl_eval["blocker"]
    assert "tessl.json" in tessl_eval["staged_files"]
