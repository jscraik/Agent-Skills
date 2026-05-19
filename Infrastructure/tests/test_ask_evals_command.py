from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import evals  # noqa: E402
from ask.skill_review_dashboard import _parse_plugin_eval, render_skill_review_dashboard  # noqa: E402


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
    assert result.data["validation_commands"] == [
        "./bin/ask evals run Plugins/example-skill --mode smoke --runner codex --json --robot"
    ]


def test_release_evals_do_not_force_smoke_model(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="release")

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" not in cmd


def test_smoke_evals_can_use_discovery_smoke_without_codex_args(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            runner="discovery-smoke",
        )

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--runner" in cmd
    assert cmd[cmd.index("--runner") + 1] == "discovery-smoke"
    assert "--model" not in cmd
    assert "--ignore-user-config" not in cmd


def test_evals_resolve_runtime_projection_to_canonical_source(tmp_path: Path) -> None:
    projected = tmp_path / ".agents" / "skills" / "evals-router"
    projected.mkdir(parents=True)
    (projected / "SKILL.md").write_text("---\nname: evals-router\n---\n", encoding="utf-8")
    canonical = tmp_path / "Skills" / "agent-ops" / "evals-router" / "references"
    canonical.mkdir(parents=True)
    (canonical / "evals.yaml").write_text("cases: []\n", encoding="utf-8")
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            ".agents/skills/evals-router",
            mode="smoke",
            runner="discovery-smoke",
            dashboard=False,
        )

    assert result.status == "success"
    assert result.data["requested_path"] == ".agents/skills/evals-router"
    assert result.data["resolved_skill_path"] == "Skills/agent-ops/evals-router"
    assert result.data["validation_commands"] == [
        "./bin/ask evals run Skills/agent-ops/evals-router --mode smoke --runner discovery-smoke --no-dashboard --json --robot"
    ]
    assert run.call_args.args[0][2] == "Skills/agent-ops/evals-router"


def test_benchmark_portfolio_exposes_validation_command(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="Benchmark OK\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.benchmark_portfolio(tmp_path)

    assert result.status == "success"
    assert result.data["validation_commands"] == ["./bin/ask evals benchmark --json --robot"]


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
                {
                    "id": "happy-path",
                    "name": "Happy Path",
                    "passed": True,
                    "tier1_failures": [],
                    "warnings": [],
                    "runners": {
                        "codex": {
                            "metrics": {
                                "expected_signals": {
                                    "composite": 92,
                                    "risk_factors": [],
                                    "missing_signals": [],
                                    "forbidden_signals_found": [],
                                }
                            }
                        }
                    },
                }
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
    assert str(tmp_path) not in result.data["raw_output"]
    assert result.data["browser_instruction"] == "Open dashboard_url in the Codex in-app browser after evals complete."
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_completed",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "pass"

    html_path = tmp_path / result.data["dashboard_path"]
    html_text = html_path.read_text(encoding="utf-8")
    assert "Evaluation Results" in html_text
    assert "Happy Path" in html_text
    assert "expected signals: 92%" in html_text
    assert 'href="#evals"' in html_text
    assert 'data-auto-refresh-seconds="0"' in html_text
    assert "Static evidence snapshot" in html_text
    assert "Review Lanes" in html_text
    assert "dynamic run-trace behavior checks" in html_text
    assert "disposable tile.json package-shape check" in html_text
    assert "opt-in local dependency security screening" in html_text


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


def test_run_evals_reuses_nested_review_report_for_dashboard(tmp_path: Path) -> None:
    scorecard_path = tmp_path / "Infrastructure/artifacts/skills/he-brainstorm/run-1/scorecard.json"
    scorecard_path.parent.mkdir(parents=True)
    scorecard_path.write_text(
        json.dumps({
            "skill": "he-brainstorm",
            "skill_path": "Plugins/harness-engineering/skills/team_automation/he-brainstorm",
            "eval_mode": "smoke",
            "runner_mode": "codex",
            "run_id": "run-1",
            "cases": [
                {
                    "id": "happy-path",
                    "name": "Happy Path",
                    "passed": True,
                    "tier1_failures": [],
                    "warnings": [],
                }
            ],
        }),
        encoding="utf-8",
    )
    nested_report = tmp_path / "Infrastructure/artifacts/skill-reviews/harness-engineering/he-brainstorm.json"
    nested_report.parent.mkdir(parents=True)
    nested_report.write_text(
        json.dumps({
            "status": "success",
            "errors": [],
            "data": {
                "target": "Plugins/harness-engineering/skills/team_automation/he-brainstorm",
                "review_mode": "external_review",
                "plugin_eval": {
                    "stdout": "Score: 91/100\nGrade: A\nRisk: low\nChecks: 0 fail, 0 warn, 0 info",
                },
                "tessl_review": {
                    "stdout": "Review Score: 96%\nDescription: 100%\nContent: 96%",
                },
            },
        }),
        encoding="utf-8",
    )
    completed = mock.Mock(
        returncode=0,
        stdout=f"Skill evals: he-brainstorm\nScorecard: {scorecard_path}\nRESULT: PASS\n",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/harness-engineering/skills/team_automation/he-brainstorm")

    assert result.status == "success"
    assert result.data["dashboard_source_report"] == (
        "Infrastructure/artifacts/skill-reviews/harness-engineering/he-brainstorm.json"
    )
    assert not (tmp_path / "Infrastructure/artifacts/skill-reviews/he-brainstorm-eval-latest.json").exists()


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
    assert "0/1 latest eval cases passed; 1 blocked by runner environment; 0 scored." in html_text
    assert "Nested Sandbox" in html_text
    assert "blocked_runtime" in html_text


def test_run_evals_classifies_auth_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=1,
        stdout="",
        stderr="ERROR: Selected Codex home is missing authenticated Codex state for live Codex runs",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_auth"
    assert result.data["blocker_class"] == "blocked_auth"
    assert "blocked_auth" in result.data["blocker_taxonomy"]


def test_run_evals_classifies_user_input_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=1,
        stdout='{"user_input_requested_during_turn": true}',
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_user_input"
    assert result.data["blocker_class"] == "blocked_user_input"
    assert result.data["blocker_taxonomy"]["blocked_user_input"] == (
        "The runner requested user input and should not be treated as hung."
    )
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_blocked",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "blocked_user_input"
    assert result.data["lifecycle_event"]["outcome"]["blocker_classes"] == ["blocked_user_input"]


def test_run_evals_classifies_discovery_smoke_filter_blocker(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=1,
        stdout="",
        stderr=(
            "ERROR: discovery-smoke runner requires eval cases with `smoke_mode`; "
            "none matched the selected filters. Use a live runner such as `codex` "
            "for behavior evals, or add discovery-specific smoke_mode cases.\n"
        ),
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoresearch",
            mode="smoke",
            runner="discovery-smoke",
            dashboard=False,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["blocker_class"] == "blocked_validation"
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_blocked",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "blocked_validation"


def test_eval_blocker_taxonomy_matches_capability_readiness_classes() -> None:
    expected = {
        "blocked_user_input",
        "blocked_auth",
        "blocked_runtime",
        "timeout_no_output",
        "timeout_partial_output",
        "blocked_missing_tool",
        "blocked_missing_artifact",
        "blocked_environment",
        "blocked_validation",
    }

    assert set(evals.EVAL_BLOCKER_TAXONOMY) == expected


def test_run_evals_classifies_missing_tool_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=1, stdout="", stderr="plugin-eval: command not found")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_missing_tool"
    assert result.data["blocker_class"] == "blocked_missing_tool"


def test_run_evals_classifies_missing_artifact_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=1, stdout="", stderr="scorecard not found after eval run")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_missing_artifact"
    assert result.data["blocker_class"] == "blocked_missing_artifact"


def test_run_evals_classifies_environment_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=1, stdout="", stderr="repo mismatch: selected workspace root is wrong")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_environment"
    assert result.data["blocker_class"] == "blocked_environment"


def test_run_evals_classifies_validation_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=1, stdout="", stderr="strict audit failed during policy validation")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["blocker_class"] == "blocked_validation"


def test_run_evals_classifies_timeout_without_output(tmp_path: Path) -> None:
    timeout = subprocess.TimeoutExpired(
        cmd=["run_skill_evals.py"],
        timeout=300,
        output="",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", side_effect=timeout):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "timeout_no_output"
    assert result.data["blocker_class"] == "timeout_no_output"


def test_run_evals_classifies_timeout_output_shape(tmp_path: Path) -> None:
    timeout = subprocess.TimeoutExpired(
        cmd=["run_skill_evals.py"],
        timeout=300,
        output="partial scorecard line",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", side_effect=timeout):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "error"
    assert result.data["eval_status"] == "timeout_partial_output"
    assert result.data["blocker_class"] == "timeout_partial_output"


def test_run_evals_can_skip_dashboard(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="Skill evals: example-skill\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", dashboard=False)

    assert result.status == "success"
    assert "dashboard_path" not in result.data


def test_plugin_eval_b_plus_warning_is_budget_guardrail() -> None:
    parsed = _parse_plugin_eval(
        """# Plugin Eval Report

## At a Glance
- Score: 88/100
- Grade: B+
- Risk: medium
- Checks: 0 fail, 1 warn, 2 info

## Fix First
- [warn/warning] invoke_cost_tokens is heavy relative to the current Codex baseline.
"""
    )

    assert parsed["grade_acceptable"] is True
    assert parsed["posture"] == "budget_guardrail"
    assert parsed["fail_count"] == 0
    assert parsed["warn_count"] == 1


def test_review_dashboard_renders_plugin_eval_acceptance_policy(tmp_path: Path) -> None:
    report_path = tmp_path / "review.json"
    output_path = tmp_path / "review.html"
    report_path.write_text(
        json.dumps({
            "status": "success",
            "errors": [],
            "data": {
                "target": "Skills/example/example-skill",
                "policy": {
                    "mode": "local_internal_only",
                    "primary_gate": "local_eval_ask_audit",
                    "plugin_eval_min_acceptable_grade": "B+",
                },
                "tessl_review": {
                    "stdout": "Overall: PASSED (0 errors, 0 warnings)\n  Description: 100%\n  Content: 90%\nReview Score: 95%\n",
                },
                "plugin_eval": {
                    "stdout": "Score: 88/100\nGrade: B+\nRisk: medium\nChecks: 0 fail, 1 warn, 2 info\n- [warn/warning] invoke_cost_tokens is heavy\n",
                },
                "ask_audit": {
                    "data": {
                        "openclaw": {
                            "status": "success",
                            "stdout": "RESULT: PASS\n0 critical · 0 warn · 0 info\n",
                        }
                    }
                },
            },
        }),
        encoding="utf-8",
    )

    render_skill_review_dashboard(report_path, output_path, tmp_path)

    html_text = output_path.read_text(encoding="utf-8")
    assert "Plugin Eval" in html_text
    assert "Local policy accepts <code>B+</code> or better" in html_text
    assert "Acceptable as a budget guardrail" in html_text
    assert "Plugin Eval floor: B+" in html_text


def test_review_dashboard_renders_review_mode_details(tmp_path: Path) -> None:
    report_path = tmp_path / "review.json"
    output_path = tmp_path / "review.html"
    report_path.write_text(
        json.dumps({
            "status": "success",
            "errors": [],
            "data": {
                "target": "Skills/example/example-skill",
                "policy": {
                    "mode": "local_internal_only",
                    "primary_gate": "local_eval_ask_audit",
                    "plugin_eval_min_acceptable_grade": "B+",
                    "snyk_default": "disabled_until_requested",
                },
                "review_mode_details": {
                    "local_evals": {
                        "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
                        "role": "dynamic run-trace behavior checks",
                    },
                    "plugin_eval": {
                        "command": "plugin-eval analyze <path> --format markdown",
                        "role": "budget and ergonomics guardrail",
                    },
                    "tessl_lint": {
                        "command": "tessl skill lint <temporary-tile.json>",
                        "role": "disposable tile.json package-shape check",
                    },
                    "tessl_review": {
                        "command": "tessl skill review <temporary-skill-directory>",
                        "role": "local best-practice/content review",
                    },
                    "snyk": {
                        "command": "./bin/ask skills external-review <path> --include-snyk --json --robot",
                        "role": "opt-in local dependency security screening; release-required for manifest-backed candidates",
                        "release_required": "manifest-backed candidates",
                    },
                },
                "ask_audit": {
                    "data": {
                        "openclaw": {
                            "status": "success",
                            "stdout": "RESULT: PASS\n0 critical · 0 warn · 0 info\n",
                        }
                    }
                },
            },
        }),
        encoding="utf-8",
    )

    render_skill_review_dashboard(report_path, output_path, tmp_path)

    html_text = output_path.read_text(encoding="utf-8")
    assert "Review Lanes" in html_text
    assert "dynamic run-trace behavior checks" in html_text
    assert "budget and ergonomics guardrail" in html_text
    assert "disposable tile.json package-shape check" in html_text
    assert "local best-practice/content review" in html_text
    assert "opt-in local dependency security screening" in html_text
    assert "release-required for manifest-backed candidates" in html_text


def test_dashboard_report_uses_canonical_skill_builder_scripts(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="Dashboard JSON: out.json\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.dashboard_report(tmp_path)

    assert result.status == "success"
    assert result.data["validation_commands"] == ["./bin/ask evals dashboard --json --robot"]
    cmd = run.call_args.args[0]
    assert cmd[1] == "Plugins/skill-factory/scripts/skill-builder/build_skill_eval_dashboard.py"
