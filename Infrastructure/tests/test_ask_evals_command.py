from __future__ import annotations

import json
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
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke")

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "gpt-5.3-codex-spark"
    assert "--reasoning" not in cmd
    assert "--reasoning-effort" not in cmd
    assert "--profile" not in cmd
    assert "--codex-arg" in cmd
    assert cmd[cmd.index("--codex-arg") + 1] == "--ignore-user-config"


def test_release_evals_do_not_force_smoke_model(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="release")

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" not in cmd


def test_run_evals_renders_local_review_dashboard(tmp_path: Path) -> None:
    scorecard_path = tmp_path / "Infrastructure/artifacts/skills/example-skill/run-1/scorecard.json"
    scorecard_path.parent.mkdir(parents=True)
    scorecard_path.write_text(
        json.dumps({
            "skill": "example-skill",
            "skill_path": "Plugins/example-skill",
            "eval_mode": "smoke",
            "runner_mode": "codex",
            "run_id": "run-1",
            "cases": [
                {"id": "happy-path", "name": "Happy Path", "passed": True, "tier1_failures": [], "warnings": []}
            ],
        }),
        encoding="utf-8",
    )
    completed = mock.Mock(
        returncode=0,
        stdout=f"Skill evals: example-skill\nScorecard: {scorecard_path}\nRESULT: PASS\n",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke")

    assert result.status == "success"
    assert result.data["dashboard_path"] == "Infrastructure/artifacts/skill-reviews/example-skill-dashboard-smoke.html"
    assert result.data["dashboard_tab"] == "evals"
    assert result.data["scorecard_path"] == "Infrastructure/artifacts/skills/example-skill/run-1/scorecard.json"
    assert result.data["browser_instruction"] == "Open dashboard_url in the Codex in-app browser after evals complete."

    html_path = tmp_path / result.data["dashboard_path"]
    html_text = html_path.read_text(encoding="utf-8")
    assert "Evaluation Results" in html_text
    assert "Happy Path" in html_text
    assert 'href="#evals"' in html_text
    assert 'data-auto-refresh-seconds="0"' in html_text
    assert "Static evidence snapshot" in html_text


def test_run_evals_renders_dashboard_for_failed_scorecard(tmp_path: Path) -> None:
    scorecard_path = tmp_path / "Infrastructure/artifacts/skills/example-skill/run-2/scorecard.json"
    scorecard_path.parent.mkdir(parents=True)
    scorecard_path.write_text(
        json.dumps({
            "skill": "example-skill",
            "skill_path": "Plugins/example-skill",
            "eval_mode": "smoke",
            "runner_mode": "codex",
            "run_id": "run-2",
            "cases": [
                {
                    "id": "blocked-path",
                    "name": "Blocked Path",
                    "passed": False,
                    "tier1_failures": ["codex returned non-zero exit code: 1"],
                    "warnings": [],
                }
            ],
        }),
        encoding="utf-8",
    )
    completed = mock.Mock(
        returncode=2,
        stdout=f"Skill evals: example-skill\nScorecard: {scorecard_path}\nRESULT: FAIL\n",
        stderr="runner failed",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke")

    assert result.status == "error"
    assert result.errors[0].code == "ERR_VALIDATION"
    assert result.data["dashboard_path"] == "Infrastructure/artifacts/skill-reviews/example-skill-dashboard-smoke.html"
    assert result.data["dashboard_tab"] == "evals"
    assert result.data["scorecard_path"] == "Infrastructure/artifacts/skills/example-skill/run-2/scorecard.json"

    html_path = tmp_path / result.data["dashboard_path"]
    html_text = html_path.read_text(encoding="utf-8")
    assert "Evaluation Results" in html_text
    assert "Blocked Path" in html_text
    assert "codex returned non-zero exit code: 1" in html_text


def test_run_evals_dashboard_marks_blocked_runner_environment(tmp_path: Path) -> None:
    scorecard_path = tmp_path / "Infrastructure/artifacts/skills/example-skill/run-3/scorecard.json"
    scorecard_path.parent.mkdir(parents=True)
    scorecard_path.write_text(
        json.dumps({
            "skill": "example-skill",
            "skill_path": "Plugins/example-skill",
            "eval_mode": "smoke",
            "runner_mode": "codex",
            "run_id": "run-3",
            "blocked_cases": 1,
            "cases": [
                {
                    "id": "nested-sandbox",
                    "name": "Nested Sandbox",
                    "passed": False,
                    "blocked": True,
                    "tier1_failures": [],
                    "warnings": ["[codex] blocked_runtime: runner could not execute local commands"],
                }
            ],
        }),
        encoding="utf-8",
    )
    completed = mock.Mock(
        returncode=2,
        stdout=f"Skill evals: example-skill\nScorecard: {scorecard_path}\nRESULT: FAIL\n",
        stderr="runner blocked",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke")

    assert result.status == "error"
    html_text = (tmp_path / result.data["dashboard_path"]).read_text(encoding="utf-8")
    assert "0/0 latest eval cases passed; 1 blocked by runner environment." in html_text
    assert "Nested Sandbox" in html_text
    assert "blocked_runtime" in html_text


def test_run_evals_can_skip_dashboard(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="Skill evals: example-skill\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "success"
    assert "dashboard_path" not in result.data
