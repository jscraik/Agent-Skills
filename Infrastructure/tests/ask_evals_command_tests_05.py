from ask_evals_command_tests_04 import *  # noqa: F403

def test_tessl_run_budget_preflight_blocks_at_reserve(tmp_path: Path) -> None:
    used_runs = [{} for _ in range(evals.TESSL_WORKSPACE_RUN_LIMIT - evals.TESSL_WORKSPACE_RUN_RESERVE)]

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        assert cmd[1:3] == ["eval", "list"]
        return mock.Mock(returncode=0, stdout=json.dumps(used_runs), stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_run_budget_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            tmp_path,
            {},
        )

    assert preflight["status"] == "blocked"
    assert preflight["blocker_class"] == "blocked_environment"
    assert preflight["remaining_runs"] == evals.TESSL_WORKSPACE_RUN_RESERVE


def test_tessl_live_budget_preflight_blocks_over_cap_and_generated_cases(tmp_path: Path) -> None:
    evals_root = tmp_path / "evals"
    for index in range(evals.TESSL_LIVE_PRIVATE_MAX_SCENARIOS + 1):
        case_id = f"case-{index:02d}"
        case_root = evals_root / case_id
        case_root.mkdir(parents=True)
        (case_root / "task.md").write_text("Do the task.\n", encoding="utf-8")
        (case_root / "criteria.json").write_text("[]\n", encoding="utf-8")
    generated_root = evals_root / "generated-eval.expensive-context-loop"
    generated_root.mkdir(parents=True)
    (generated_root / "task.md").write_text("Generated task.\n", encoding="utf-8")
    (generated_root / "criteria.json").write_text("[]\n", encoding="utf-8")

    preflight = evals._tessl_live_budget_preflight(tmp_path)

    assert preflight["status"] == "blocked"
    assert preflight["blocker_class"] == "blocked_validation"
    assert preflight["scenario_count"] == evals.TESSL_LIVE_PRIVATE_MAX_SCENARIOS + 2
    assert preflight["expected_model_tasks"] == preflight["scenario_count"] * 4
    assert preflight["generated_case_ids"] == ["generated-eval.expensive-context-loop"]
    assert any("cost cap" in blocker for blocker in preflight["blockers"])
    assert any("generated-eval" in blocker for blocker in preflight["blockers"])


def test_tessl_live_budget_preflight_passes_target_eight_non_generated_cases(tmp_path: Path) -> None:
    evals_root = tmp_path / "evals"
    for index in range(evals.TESSL_LIVE_PRIVATE_TARGET_SCENARIOS):
        case_root = evals_root / f"case-{index:02d}"
        case_root.mkdir(parents=True)
        (case_root / "task.md").write_text("Do the task.\n", encoding="utf-8")
        (case_root / "criteria.json").write_text("[]\n", encoding="utf-8")

    preflight = evals._tessl_live_budget_preflight(tmp_path)

    assert preflight["status"] == "pass"
    assert preflight["scenario_count"] == 8
    assert preflight["target_scenarios"] == 8
    assert preflight["expected_solution_runs"] == 16
    assert preflight["expected_score_runs"] == 16
    assert preflight["expected_model_tasks"] == 32


def test_tessl_live_budget_preflight_blocks_below_five(tmp_path: Path) -> None:
    evals_root = tmp_path / "evals"
    for index in range(evals.TESSL_LIVE_PRIVATE_MIN_SCENARIOS - 1):
        case_root = evals_root / f"case-{index:02d}"
        case_root.mkdir(parents=True)
        (case_root / "task.md").write_text("Do the task.\n", encoding="utf-8")
        (case_root / "criteria.json").write_text("[]\n", encoding="utf-8")

    preflight = evals._tessl_live_budget_preflight(tmp_path)

    assert preflight["status"] == "blocked"
    assert any("coverage floor" in blocker for blocker in preflight["blockers"])


def test_evals_live_private_uses_default_workspace(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_tessl_dry_run_admission", return_value={"ready_for_tessl_dry_run": True}),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_live_dry_run=True,
    )

    assert result.status == "success"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "pass"
    assert result.data["tessl_workspace_source"] == "default"
    assert tessl_eval["workspace"] == "jscraik"


def test_evals_live_private_rejects_invalid_workspace(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="bad/workspace",
            tessl_live_dry_run=True,
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "workspace" in tessl_eval["blocker"].lower()


def _completed_tessl_view() -> mock.Mock:
    return mock.Mock(returncode=0, stdout=json.dumps({"data": {"attributes": {
        "agent": "claude", "model": "deepseek-v4-flash", "scorerAgent": "glm", "scorerModel": "glm-5.1",
        "usage": {"meanTurns": 20, "p95Turns": 37, "totalTokens": 12345, "estimatedCostUsd": 0.0236},
        "scenarios": [{"solutions": [
            {"variant": "baseline", "assessmentResults": [{"score": 0, "max_score": 1}]},
            {"variant": "usage-spec", "assessmentResults": [{"score": 1, "max_score": 1}]},
        ]}],
    }}}), stderr="")


def _tessl_live_fake_run(completed_view: mock.Mock):
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(returncode=0, stdout='{"id":"019e6ac8-08eb-75fb-8fbb-e2346517f82d"}', stderr="")
    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(returncode=0, stdout='{"workspace":"jscraik","project":"example-skill","name":"jscraik/example-skill"}', stderr="", args=cmd)
        if cmd[1:3] == ["eval", "list"]:
            return mock.Mock(returncode=0, stdout="[]", stderr="", args=cmd)
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        return completed_view if cmd[1:3] == ["eval", "view"] else completed
    return fake_run


def _assert_tessl_commands(run: mock.Mock) -> Path:
    calls = [call.args[0] for call in run.call_args_list]
    tessl_cmd = next(call for call in calls if call[1:3] == ["eval", "run"])
    view_cmd = next(call for call in calls if call[1:3] == ["eval", "view"])
    assert not any(any("run_skill_evals.py" in str(part) for part in call) for call in calls)
    assert tessl_cmd[:6] == ["/usr/local/bin/tessl", "eval", "run", "--json", "--workspace", "jscraik"]
    assert not {"--yes", "publish", "install", "registry"}.intersection(tessl_cmd)
    assert view_cmd == ["/usr/local/bin/tessl", "eval", "view", "--json", "019e6ac8-08eb-75fb-8fbb-e2346517f82d"]
    return Path(tessl_cmd[6])


def _assert_tessl_stage(staged_source: Path) -> None:
    assert staged_source.is_dir()
    assert not (staged_source / "tile.json").exists()
    _assert_tessl_stage_manifest(staged_source)
    _assert_tessl_stage_files(staged_source)


def _assert_tessl_stage_manifest(staged_source: Path) -> None:
    manifest = json.loads((staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "jscraik/example-skill" and manifest["version"] == "1.2.3"
    assert manifest["description"] == "Private live eval plugin for example-skill."
    assert manifest["private"] is True and manifest["skills"] == "./skills/"
    assert json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))["name"] == "jscraik/example-skill"


def _assert_tessl_stage_files(staged_source: Path) -> None:
    staged_skill = _assert_plugin_shaped_stage(staged_source, "example-skill")
    assert (staged_skill / "SKILL.md").is_file() and (staged_skill / "references" / "evals.yaml").is_file()
    assert (staged_source / "evals" / "smoke-example" / "task.md").is_file()
    assert (staged_source / "evals" / "smoke-example" / "criteria.json").is_file()


def _assert_tessl_evidence(tmp_path: Path, result, completed_view: mock.Mock) -> None:
    tessl_eval = result.data["tessl_eval"]
    root = tmp_path / ".harness" / "evidence" / "tessl" / "example-skill" / "019e6ac8-08eb-75fb-8fbb-e2346517f82d"
    submission = json.loads((tmp_path / tessl_eval["submission_evidence_path"]).read_text(encoding="utf-8"))
    assert tmp_path / tessl_eval["submission_evidence_path"] == root / "tessl-eval-submission.json"
    assert submission["status"] == "submitted_pending_view"
    assert submission["run_id"] == "019e6ac8-08eb-75fb-8fbb-e2346517f82d"
    assert submission["workspace"] == "jscraik" and submission["skill_path"] == "Skills/example-skill"
    assert submission["next_action"].startswith("poll tessl eval view")
    assert tmp_path / tessl_eval["view_evidence_path"] == root / "tessl-eval-view.json"
    assert json.loads((tmp_path / tessl_eval["view_evidence_path"]).read_text(encoding="utf-8")) == json.loads(completed_view.stdout)


def _assert_tessl_summary(result) -> None:
    summary = result.data["tessl_eval"]["live_result_summary"]
    assert summary["meets_min_score"] is True and summary["beats_baseline"] is True
    assert summary["model_selection"] == {"agent": "claude", "model": "deepseek-v4-flash", "scorer_agent": "glm", "scorer_model": "glm-5.1", "quality_floor_before_cost": True, "cost_is_secondary_to_score": True}
    assert summary["comparative_quality"]["with_skill_score"] == 1
    assert summary["comparative_quality"]["without_skill_score"] == 0
    cost = summary["cost_observability"]
    assert cost["turn_metrics_available"] and cost["token_metrics_available"] and cost["cost_metrics_available"]
    assert cost["turn_metrics"] == {"usage.meanTurns": 20, "usage.p95Turns": 37}
    assert cost["token_metrics"] == {"usage.totalTokens": 12345}
    assert cost["cost_metrics"] == {"usage.estimatedCostUsd": 0.0236}


def test_evals_live_private_invokes_tessl_with_workspace_and_plugin_manifest(tmp_path: Path) -> None:
    completed_view = _completed_tessl_view()
    _write_example_skill(tmp_path)
    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals, "_tessl_live_handoff_readiness", return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []}),
        mock.patch.object(evals.subprocess, "run", side_effect=_tessl_live_fake_run(completed_view)) as run,
    ):
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke", tessl_live_private=True, tessl_workspace="jscraik")
    assert result.status == "success" and result.data["local_eval_status"] == "skipped_tessl_live_private"
    assert result.data["eval_closeout"]["status"] == "pass"
    assert result.data["eval_closeout_path"].startswith("Infrastructure/artifacts/evals/closeouts/")
    assert "separately before live scoring" in result.data["tessl_live_private_note"]
    _assert_tessl_stage(_assert_tessl_commands(run))
    _assert_tessl_evidence(tmp_path, result, completed_view)
    _assert_tessl_summary(result)


def test_tessl_live_evidence_rejects_unsafe_run_ids(tmp_path: Path) -> None:
    view_path = evals._write_tessl_live_view_evidence(
        tmp_path,
        "Skills/example-skill",
        "../outside",
        '{"status":"completed"}',
    )
    submission_path = evals._write_tessl_live_submission_evidence(
        tmp_path,
        "Skills/example-skill",
        run_id="run/with/slash",
        workspace="jscraik",
        staged_source=tmp_path / "stage",
        project_identity={"project": "jscraik/example-skill"},
    )

    assert view_path is None
    assert submission_path is None
    assert not (tmp_path / ".harness" / "evidence" / "outside").exists()


def test_tessl_live_evidence_records_compact_forensic_index(tmp_path: Path) -> None:
    view_path = evals._write_tessl_live_view_evidence(
        tmp_path,
        "Skills/example-skill",
        "019e6ac8-08eb-75fb-8fbb-e2346517f82d",
        json.dumps({"data": {"attributes": {"status": "completed", "scenarios": []}}}),
    )

    assert view_path is not None
    index_path = tmp_path / ".harness" / "evidence" / "tessl" / "index.jsonl"
    index_rows = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()]

    assert len(index_rows) == 1
    assert index_rows[0]["schema_version"] == "skills-sdk.tessl-live-evidence-index.v1"
    assert index_rows[0]["skill_handle"] == "example-skill"
    assert index_rows[0]["run_id"] == "019e6ac8-08eb-75fb-8fbb-e2346517f82d"
    assert index_rows[0]["artifact_type"] == "tessl-eval-view.json"
    assert index_rows[0]["raw_evidence_path"] == view_path
    assert index_rows[0]["status"] == "completed"
    assert index_rows[0]["raw_evidence_bytes"] > 0
    assert index_rows[0]["archived_previous_path"] is None
    assert "local forensic evidence" in index_rows[0]["retention_policy"]


def test_tessl_live_evidence_archives_prior_raw_file_before_overwrite(tmp_path: Path) -> None:
    first_path = evals._write_tessl_live_view_evidence(
        tmp_path,
        "Skills/example-skill",
        "019e6ac8-08eb-75fb-8fbb-e2346517f82d",
        '{"data":{"attributes":{"status":"running","scenarios":[]}}}',
    )
    second_path = evals._write_tessl_live_view_evidence(
        tmp_path,
        "Skills/example-skill",
        "019e6ac8-08eb-75fb-8fbb-e2346517f82d",
        '{"data":{"attributes":{"status":"completed","scenarios":[]}}}',
    )

    assert first_path == second_path
    raw_path = tmp_path / first_path
    assert json.loads(raw_path.read_text(encoding="utf-8"))["data"]["attributes"]["status"] == "completed"

    index_path = tmp_path / ".harness" / "evidence" / "tessl" / "index.jsonl"
    index_rows = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()]
    archived_previous_path = index_rows[-1]["archived_previous_path"]

    assert archived_previous_path is not None
    archived_payload = json.loads((tmp_path / archived_previous_path).read_text(encoding="utf-8"))
    assert archived_payload["data"]["attributes"]["status"] == "running"


def test_evals_live_private_blocks_before_submit_when_pending_run_exists(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    pending_payload = {
        "data": [
            {
                "id": "019edf73-3fdc-749d-b470-cc10e941715e",
                "type": "eval-run",
                "attributes": {
                    "status": "pending",
                    "metadata": {"tileName": "jscraik/example-skill"},
                },
            }
        ]
    }
    _write_example_skill(tmp_path)

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"workspace":"jscraik","project":"example-skill","name":"jscraik/example-skill"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:3] == ["eval", "list"]:
            return mock.Mock(returncode=0, stdout=json.dumps(pending_payload), stderr="", args=cmd)
        if cmd[1:3] == ["eval", "run"]:
            raise AssertionError("duplicate pending run guard must block before tessl eval run")
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_environment"
    assert tessl_eval["pending_run_preflight"]["pending_eval_run_ids"] == [
        "019edf73-3fdc-749d-b470-cc10e941715e"
    ]


def test_evals_live_private_fails_when_score_is_below_baseline(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(returncode=0, stdout='{"id":"019e6ac8-08eb-75fb-8fbb-e2346517f82d"}', stderr="")
    completed_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "scenarios": [
                        {
                            "shortDescription": "regressed handoff",
                            "solutions": [
                                {
                                    "variant": "baseline",
                                    "assessmentResults": [{"score": 1, "max_score": 1}],
                                },
                                {
                                    "variant": "usage-spec",
                                    "assessmentResults": [{"score": 0, "max_score": 1}],
                                },
                            ],
                        }
                    ]
                }
            }
        }),
        stderr="",
    )
    _write_example_skill(tmp_path)

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"workspace":"jscraik","project":"example-skill","name":"jscraik/example-skill"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:3] == ["eval", "list"]:
            return mock.Mock(returncode=0, stdout="[]", stderr="", args=cmd)
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        if cmd[1:3] == ["eval", "view"]:
            return completed_view
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "fail"
    assert "failed readiness" in tessl_eval["blocker"]
    assert tessl_eval["live_result_summary"]["score"] == 0
    assert tessl_eval["live_result_summary"]["baseline_score"] == 1
    assert tessl_eval["live_result_summary"]["regressions_count"] == 1


def test_evals_live_private_fails_when_skill_only_ties_baseline(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(returncode=0, stdout='{"id":"019e6ac8-08eb-75fb-8fbb-e2346517f82d"}', stderr="")
    completed_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "scenarios": [
                        {
                            "shortDescription": "non-discriminating perfect score",
                            "solutions": [
                                {
                                    "variant": "baseline",
                                    "assessmentResults": [{"score": 1, "max_score": 1}],
                                },
                                {
                                    "variant": "usage-spec",
                                    "assessmentResults": [{"score": 1, "max_score": 1}],
                                },
                            ],
                        }
                    ]
                }
            }
        }),
        stderr="",
    )
    _write_example_skill(tmp_path)

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"workspace":"jscraik","project":"example-skill","name":"jscraik/example-skill"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:3] == ["eval", "list"]:
            return mock.Mock(returncode=0, stdout="[]", stderr="", args=cmd)
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        if cmd[1:3] == ["eval", "view"]:
            return completed_view
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "fail"
    assert "score 100.0% vs baseline 100.0%" in tessl_eval["blocker"]
    summary = tessl_eval["live_result_summary"]
    assert summary["meets_min_score"] is True
    assert summary["beats_baseline"] is False
    assert summary["baseline_ties_count"] == 1
    assert summary["regressions_count"] == 0


def test_evals_live_private_polls_until_view_scores_are_complete(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(returncode=0, stdout='{"id":"019e6ac8-08eb-75fb-8fbb-e2346517f82d"}', stderr="")
    pending_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "status": "pending",
                    "scenarios": [{
                        "solutions": [
                            {"variant": "baseline", "assessmentResults": [{"score": 1, "max_score": 1}]},
                            {"variant": "usage-spec", "assessmentResults": None},
                        ],
                    }],
                }
            }
        }),
        stderr="",
    )
    completed_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "status": "completed",
                    "scenarios": [{
                            "solutions": [
                                {"variant": "baseline", "assessmentResults": [{"score": 0, "max_score": 1}]},
                                {"variant": "usage-spec", "assessmentResults": [{"score": 1, "max_score": 1}]},
                            ],
                    }],
                }
            }
        }),
        stderr="",
    )
    _write_example_skill(tmp_path)
    view_calls = 0

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        nonlocal view_calls
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"workspace":"jscraik","project":"example-skill","name":"jscraik/example-skill"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:3] == ["eval", "list"]:
            return mock.Mock(returncode=0, stdout="[]", stderr="", args=cmd)
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        if cmd[1:3] == ["eval", "view"]:
            view_calls += 1
            return pending_view if view_calls == 1 else completed_view
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run),
        mock.patch.object(evals.time, "sleep", return_value=None),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "success"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["view_attempts"] == 2
    assert tessl_eval["view_status"] == "completed"
    assert tessl_eval["live_result_summary"]["score"] == 1

__all__ = [name for name in globals() if not name.startswith("__")]
