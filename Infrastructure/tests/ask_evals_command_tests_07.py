from ask_evals_command_tests_06 import *  # noqa: F403

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
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

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
        result = evals.run_evals(
            tmp_path,
            "Plugins/harness-engineering/skills/team_automation/he-brainstorm",
            skip_tessl=True,
        )

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
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

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
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_auth"
    assert result.data["blocker_class"] == "blocked_auth"
    assert "blocked_auth" in result.data["blocker_taxonomy"]


def test_run_evals_classifies_scorecard_runtime_blocker(tmp_path: Path) -> None:
    scorecard_path = tmp_path / "reports" / "scorecard.json"
    scorecard_path.parent.mkdir(parents=True)
    scorecard_path.write_text(
        json.dumps({
            "decision": "blocked",
            "blocked_class_summary": {"blocked_runtime": 21},
            "cases": [],
        }),
        encoding="utf-8",
    )
    completed = mock.Mock(
        returncode=2,
        stdout=f"Skill evals: autoreview\nScorecard: {scorecard_path}\nRESULT: FAIL\n",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_runtime"
    assert result.data["blocker_class"] == "blocked_runtime"
    assert result.errors[0].code == "ERR_RUNTIME"
    assert result.errors[0].message == "Evaluation run blocked."


def test_run_evals_uses_default_tessl_workspace_from_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("ASK_TESSL_WORKSPACE", "jscraik")
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] is None
    assert result.data["tessl_workspace_source"] is None


def test_run_evals_without_workspace_uses_jscraik_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ASK_TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE_NAME", raising=False)
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] is None
    assert result.data["tessl_workspace_source"] is None


def test_run_evals_preserves_jscraik_tessl_workspace_argument(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
            tessl_workspace="jscraik",
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] is None
    assert result.data["tessl_workspace_source"] is None
    assert "--tessl-workspace jscraik" not in result.data["validation_commands"][0]


def test_run_evals_blocks_stale_tessl_workspace_argument(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
            tessl_workspace="not-jscraik",
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] is None
    assert result.data["tessl_eval"]["status"] == "skipped"


def test_run_evals_live_private_uses_jscraik_default_workspace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ASK_TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE_NAME", raising=False)
    monkeypatch.setenv("ASK_EXTERNAL_EFFECTS", "deny")
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run") as run:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            dashboard=False,
            tessl_live_private=True,
        )
    run.assert_not_called()

    assert result.status == "error"
    assert result.data["tessl_workspace"] == "jscraik"
    assert result.data["tessl_workspace_source"] == "default"
    assert result.errors[0].message.startswith("Tessl eval blocked")
    assert "external-effect policy" in result.errors[0].message


def test_run_evals_blocks_invalid_default_tessl_workspace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("ASK_TESSL_WORKSPACE", "skills-sdk")
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] is None
    assert result.data["tessl_eval"]["status"] == "skipped"


def test_run_evals_classifies_user_input_blocker_without_scorecard(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=1,
        stdout='{"user_input_requested_during_turn": true}',
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

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


def test_run_evals_classifies_codex_usage_limit_as_runtime(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=1,
        stdout="",
        stderr=(
            "ERROR: You've hit your usage limit for GPT-5.3-Codex-Spark. "
            "Switch to another model now, or try again at 11:00 PM.\n"
        ),
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_runtime"
    assert result.data["blocker_class"] == "blocked_runtime"
    assert result.errors[0].code == "ERR_RUNTIME"
    assert result.data["lifecycle_event"]["outcome"]["status"] == "blocked_runtime"
    assert result.data["lifecycle_event"]["outcome"]["blocker_classes"] == ["blocked_runtime"]


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
            skip_tessl=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["blocker_class"] == "blocked_validation"
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_blocked",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "blocked_validation"


def test_run_evals_stores_repo_relative_raw_output(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path, "autoresearch")
    report_dir = tmp_path / "Infrastructure" / "artifacts" / "skills" / "autoresearch" / "run-1"
    skill = tmp_path / "Skills" / "agent-ops" / "autoresearch"
    skill.mkdir(parents=True)
    absolute_report = report_dir / "scorecard.json"
    absolute_report.write_text(
        json.dumps({
            "status": "pass",
            "cases": [],
            "no_case_reason": "path sanitization fixture",
        }),
        encoding="utf-8",
    )
    completed.stdout = f"Reports: {report_dir}\nScorecard: {absolute_report}\n"
    completed.stderr = f"checked {skill}\n"

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoresearch",
            mode="smoke",
            runner="discovery-smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "success"
    assert str(tmp_path) not in result.data["raw_output"]
    assert str(tmp_path) not in result.data["raw_error"]
    assert "Infrastructure/artifacts/skills/autoresearch/run-1/scorecard.json" in result.data["raw_output"]


def test_run_evals_classifies_timeout_without_output(tmp_path: Path) -> None:
    timeout = subprocess.TimeoutExpired(
        cmd=["run_skill_evals.py"],
        timeout=300,
        output="",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", side_effect=timeout):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "timeout_no_output"
    assert result.data["blocker_class"] == "timeout_no_output"
    assert result.data["timeout_classification"]["class"] == "timeout_no_output"
    assert result.data["timeout_classification"]["partial_output_artifact"] is None


def test_run_evals_classifies_timeout_output_shape(tmp_path: Path) -> None:
    timeout = subprocess.TimeoutExpired(
        cmd=["run_skill_evals.py"],
        timeout=300,
        output="partial scorecard line",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", side_effect=timeout):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "timeout_partial_output"
    assert result.data["blocker_class"] == "timeout_partial_output"
    artifact = result.data["timeout_classification"]["partial_output_artifact"]
    assert artifact is not None
    assert artifact.startswith("Infrastructure/artifacts/evals/timeouts/")
    assert "partial scorecard line" in (tmp_path / artifact).read_text(encoding="utf-8")


def test_run_evals_can_skip_dashboard(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "success"
    assert result.data["dashboard"] == {
        "status": "not_requested",
        "reason": "disabled_by_option",
        "tab": "evals",
    }
    assert "dashboard_path" not in result.data


def test_run_evals_keeps_passing_receipt_when_dashboard_is_unavailable(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_render_eval_dashboard", side_effect=OSError("read-only dashboard root")),
    ):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=True,
            skip_tessl=True,
        )

    assert result.status == "success"
    assert result.errors == []
    assert result.data["eval_status"] == "pass"
    assert result.data["dashboard"] == {
        "status": "unavailable",
        "reason": "render_failed",
        "error_type": "OSError",
        "tab": "evals",
    }
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


def test_plugin_eval_deferred_budget_fail_is_nonblocking_when_active_budget_good() -> None:
    parsed = _parse_plugin_eval(
        """# Plugin Eval Report

## At a Glance
- Score: 86/100
- Grade: B+
- Risk: high
- Checks: 1 fail, 0 warn, 2 info
- Active budget: 1293 tokens (good)

## Checks
- [FAIL] deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline.
"""
    )

    assert parsed["fail_count"] == 1
    assert parsed["blocking_fail_count"] == 0
    assert parsed["posture"] == "deferred_budget_guardrail"


def test_plugin_eval_deferred_budget_fail_is_nonblocking_when_active_budget_moderate_and_grade_b() -> None:
    parsed = _parse_plugin_eval(
        """# Plugin Eval Report

## At a Glance
- Score: 86/100
- Grade: B
- Risk: high
- Checks: 1 fail, 0 warn, 2 info
- Active budget: 2228 tokens (moderate)

## Checks
- [FAIL] deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline.
"""
    )

    assert parsed["grade_acceptable"] is True
    assert parsed["fail_count"] == 1
    assert parsed["blocking_fail_count"] == 0
    assert parsed["posture"] == "deferred_budget_guardrail"


def test_plugin_eval_deferred_budget_fail_still_blocks_low_grade() -> None:
    parsed = _parse_plugin_eval(
        """# Plugin Eval Report

## At a Glance
- Score: 72/100
- Grade: C
- Risk: high
- Checks: 1 fail, 0 warn, 2 info
- Active budget: 1293 tokens (good)

## Checks
- [FAIL] deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline.
"""
    )

    assert parsed["grade_acceptable"] is False
    assert parsed["fail_count"] == 1
    assert parsed["blocking_fail_count"] == 1
    assert parsed["posture"] == "blocking"


def test_plugin_eval_deferred_budget_mention_does_not_hide_other_failures() -> None:
    parsed = _parse_plugin_eval(
        """# Plugin Eval Report

## At a Glance
- Score: 90/100
- Grade: A-
- Risk: high
- Checks: 1 fail, 0 warn, 2 info
- Active budget: 1293 tokens (good)

## Checks
- [FAIL] missing_contract: required evidence is missing.
- [INFO] deferred_cost_tokens-budget-high was reviewed as a future follow-up.
"""
    )

    assert parsed["grade_acceptable"] is True
    assert parsed["fail_count"] == 1
    assert parsed["blocking_fail_count"] == 1
    assert parsed["posture"] == "blocking"


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
    assert 'id="tab-quality"' in html_text
    assert 'aria-labelledby="tab-quality"' in html_text
    assert 'id="tab-evals"' in html_text
    assert 'aria-labelledby="tab-evals"' in html_text


def test_review_dashboard_coerces_non_string_eval_notes() -> None:
    html_text = _render_eval_cases({
        "available": True,
        "message": "done",
        "score": 100,
        "cases": [{"name": "case", "category": "happy", "score": 100, "notes": [1]}],
    })

    assert "1" in html_text

__all__ = [name for name in globals() if not name.startswith("__")]
