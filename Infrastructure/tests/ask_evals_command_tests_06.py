from ask_evals_command_tests_05 import *  # noqa: F403


def test_eval_closeout_persistence_failure_returns_classified_blocker(tmp_path: Path) -> None:
    closeout = evals._eval_closeout_payload(
        tmp_path,
        "Skills/example-skill",
        "smoke",
        "codex",
        None,
        [],
        "fail",
        None,
        "RESULT: FAIL",
        "",
        missing_suite_artifacts=False,
        timeout_seconds=None,
        no_case_reason=None,
    )
    closeout_path = tmp_path / "blocked" / "workflow-closeout.json"

    with mock.patch.object(Path, "mkdir", side_effect=OSError("read-only evidence root")):
        persisted = evals._persist_eval_closeout(tmp_path, closeout, closeout_path)

    assert persisted["status"] == "blocked"
    assert persisted["blocker_class"] == "blocked_artifact_persistence"
    assert persisted["mutation_allowed"] is False
    assert persisted["registry_update_allowed"] is False
    assert persisted["persistence_error"] == {
        "operation": "create parent directory",
        "error": "read-only evidence root",
    }


def test_evals_live_private_reports_tessl_quota_blocker(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(
        returncode=0,
        stdout='[{"evalRunId":"019ecadc-9870-7323-8098-58145a211f26","scenariosCount":32}]',
        stderr="",
    )
    failed_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "status": "failed",
                    "failureReason": {
                        "code": "EVAL_QUOTA_EXCEEDED",
                        "message": "Your organisation has reached its daily eval limit.",
                    },
                    "scenarios": [{"solutions": []}],
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
            return failed_view
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
    assert "EVAL_QUOTA_EXCEEDED" in tessl_eval["blocker"]
    assert tessl_eval["eval_run_id"] == "019ecadc-9870-7323-8098-58145a211f26"


def test_prepare_tessl_scenario_generation_dry_run_stages_target_tile(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "evals").mkdir()
    (skill_root / "evals" / "old-case.txt").write_text(
        "do not stage generated evals\\n",
        encoding="utf-8",
    )

    result = evals.prepare_tessl_scenario_generation(
        tmp_path,
        "Skills/example-skill",
        workspace="jscraik",
        dry_run=True,
    )

    assert result.status == "success"
    assert result.data["status"] == "pass"
    assert result.data["command"] == (
        "tessl install tessl-labs/tessl-skill-eval-scenarios@0.1.0 --agent codex --yes"
    )
    target_tile = Path(result.data["target_tile"])
    tool_project = Path(result.data["tool_project"])
    assert target_tile.name == "target-tile"
    assert tool_project.name == "tool-project"
    assert (target_tile / "SKILL.md").is_file()
    assert (target_tile / "README.md").is_file()
    assert not (target_tile / "evals").exists()
    assert (tool_project / "tessl.json").is_file()
    assert Path(result.data["scenario_generation_brief"]).is_file()
    assert not (target_tile / "tile.json").exists()
    manifest = json.loads((target_tile / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "jscraik/example-skill"
    assert manifest["version"] == "1.2.3"
    assert manifest["private"] is True
    assert manifest["skills"] == "./skills/"
    assert result.data["target_plugin_manifest"].endswith("/.tessl-plugin/plugin.json")
    assert result.data["policy"]["no_repo_root_install"] is True
    assert result.data["policy"]["allowed_install_scope"] == "temp tool project only"


def test_prepare_tessl_scenario_generation_defaults_to_staging_only(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run") as run:
        result = evals.prepare_tessl_scenario_generation(
            tmp_path,
            "Skills/example-skill",
            workspace="jscraik",
        )

    assert result.status == "success"
    assert result.data["dry_run"] is True
    assert Path(result.data["scenario_generation_brief"]).is_file()
    run.assert_not_called()


def test_prepare_tessl_scenario_generation_archives_prior_temp_evidence(tmp_path: Path) -> None:
    skill_root = tmp_path / "Skills" / "example-skill-retention"
    references = skill_root / "references"
    references.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: example-skill-retention\nmetadata:\n  version: "1.2.3"\n---\n# Example Skill\n',
        encoding="utf-8",
    )
    (references / "evals.yaml").write_text(
        'cases:\n  - id: smoke-example\n    prompt: "Do the example task."\n',
        encoding="utf-8",
    )

    first = evals.prepare_tessl_scenario_generation(
        tmp_path,
        "Skills/example-skill-retention",
        workspace="jscraik",
        dry_run=True,
    )
    assert first.status == "success"
    staged_root = Path(first.data["staged_root"])
    prior_task = Path(first.data["target_tile"]) / "evals" / "scenario-0" / "task.md"
    prior_task.parent.mkdir(parents=True)
    prior_task.write_text("prior generated scenario evidence\n", encoding="utf-8")

    second = evals.prepare_tessl_scenario_generation(
        tmp_path,
        "Skills/example-skill-retention",
        workspace="jscraik",
        dry_run=True,
    )

    assert second.status == "success"
    archived_tasks = list((staged_root / "evidence-archive").glob("*/evals/scenario-0/task.md"))
    assert "prior generated scenario evidence\n" in [
        task.read_text(encoding="utf-8") for task in archived_tasks
    ]
    assert not (Path(second.data["target_tile"]) / "evals" / "scenario-0" / "task.md").exists()
    assert (Path(second.data["target_tile"]) / "SKILL.md").is_file()


def test_prepare_tessl_scenario_generation_installs_tool_in_temp_project(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="installed\\n", stderr="")
    _write_example_skill(tmp_path)

    def fake_install(cmd: list[str], **kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"] and "--relink" not in cmd:
            return mock.Mock(returncode=1, stdout='{"status":"error"}', stderr="", args=cmd)
        if cmd[1:3] == ["project", "repair"] and "--relink" in cmd:
            return mock.Mock(returncode=1, stdout='{"status":"error","message":"not found"}', stderr="", args=cmd)
        if cmd[1:3] == ["project", "create"]:
            return mock.Mock(returncode=0, stdout="Created project\n", stderr="", args=cmd)
        tool_project = Path(str(kwargs["cwd"]))
        scenario_root = (
            tool_project
            / ".tessl/plugins/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios"
        )
        (scenario_root / "references").mkdir(parents=True)
        (scenario_root / "SKILL.md").write_text("# Creating Eval Scenarios\n", encoding="utf-8")
        (scenario_root / "references/scenario-generation.md").write_text(
            "# Scenario Generation\n",
            encoding="utf-8",
        )
        completed.args = cmd
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_install) as run,
    ):
        result = evals.prepare_tessl_scenario_generation(
            tmp_path,
            "Skills/example-skill",
            workspace="jscraik",
            dry_run=False,
        )

    assert result.status == "success"
    assert result.data["workspace"] == "jscraik"
    cmd = run.call_args.args[0]
    assert cmd == [
        "/usr/local/bin/tessl",
        "install",
        "tessl-labs/tessl-skill-eval-scenarios@0.1.0",
        "--agent",
        "codex",
        "--yes",
    ]
    assert run.call_args.kwargs["cwd"] == result.data["tool_project"]
    assert "/ask-tessl-scenario-generation/" in result.data["tool_project"]
    assert "/.tessl/plugins/" in result.data["scenario_skill"]
    assert "/.tessl/plugins/" in result.data["scenario_reference"]
    assert result.data["generated_output"].endswith("/target-tile/evals")
    live_source = Path(result.data["live_staged_source"])
    assert "/ask-tessl-evals-live/" in str(live_source)
    assert result.data["project_link"]["staged_source"] == str(live_source)
    assert (live_source / "skills" / "example-skill" / "SKILL.md").is_file()
    project_receipt = Path(tmp_path) / ".harness" / "evidence" / "tessl-project-links" / "example-skill"
    receipt = next(project_receipt.glob("*.json"))
    assert json.loads(receipt.read_text(encoding="utf-8"))["staged_source"] == str(live_source)


def test_evals_stage_folded_yaml_prompts_for_tessl(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: folded-prompt\n"
            "    unit: folded prompt preservation proof\n"
            "    given: A serialized YAML prompt uses folded block syntax.\n"
            "    should: Preserve the whole prompt while keeping behavioural scoring criteria.\n"
            "    prompt: >-\n"
            "      Investigate the target workflow\n"
            "      and preserve the whole prompt.\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(workflow|prompt)\"\n"
            "      - type: expected_signal\n"
            "        value: Preserves the whole prompt while keeping behavioural scoring criteria.\n"
        ),
        encoding="utf-8",
    )
    staged_root = tmp_path / "staged"

    copied = evals._write_tessl_scenarios_from_evals(skill_root, staged_root)

    assert copied == [
        "scenario-sources.json",
        "scenarios/folded-prompt/task.md",
        "scenarios/folded-prompt/criteria.json",
    ]
    task_text = (staged_root / "scenarios" / "folded-prompt" / "task.md").read_text(encoding="utf-8")
    assert task_text.startswith("Unit: folded prompt preservation proof\n")
    assert task_text.endswith("Investigate the target workflow and preserve the whole prompt.\n")
    criteria = json.loads((staged_root / "scenarios" / "folded-prompt" / "criteria.json").read_text(encoding="utf-8"))
    assert criteria["type"] == "weighted_checklist"


def test_evals_fallback_parser_preserves_literal_block_relative_indent(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: literal-prompt\n"
            "    unit: literal prompt preservation proof\n"
            "    given: A serialized YAML prompt uses a literal code block.\n"
            "    should: Preserve literal indentation while keeping behavioural scoring criteria.\n"
            "    prompt: |\n"
            "        def example():\n"
            "            return 1\n"
            "      done\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(def example|done)\"\n"
            "      - type: expected_signal\n"
            "        value: Preserves literal indentation while keeping behavioural scoring criteria.\n"
        ),
        encoding="utf-8",
    )
    staged_root = tmp_path / "staged"

    copied = evals._write_tessl_scenarios_from_evals(skill_root, staged_root)

    assert copied == [
        "scenario-sources.json",
        "scenarios/literal-prompt/task.md",
        "scenarios/literal-prompt/criteria.json",
    ]
    task_text = (staged_root / "scenarios" / "literal-prompt" / "task.md").read_text(encoding="utf-8")
    assert task_text.startswith("Unit: literal prompt preservation proof\n")
    assert task_text.endswith("  def example():\n      return 1\ndone\n")


def test_evals_classify_malformed_yaml_as_blocked_validation(tmp_path: Path) -> None:
    class FakeYAMLError(Exception):
        pass

    class FakeYaml:
        YAMLError = FakeYAMLError

        @staticmethod
        def safe_load(_text: str) -> object:
            raise FakeYAMLError("bad yaml")

    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    _write_example_skill(tmp_path)

    with (
        mock.patch.dict(sys.modules, {"yaml": FakeYaml}),
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals, "_pyyaml_eval_python_command", return_value=["managed-python"]),
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_tessl_dry_run_admission", return_value={"ready_for_tessl_dry_run": True}),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
            tessl_live_dry_run=True,
        )

    tessl_eval = result.data["tessl_eval"]
    assert result.status == "error"
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "Failed to parse Tessl eval cases" in tessl_eval["blocker"]


def test_evals_staging_rejects_symlinked_support_files(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    outside = tmp_path / "outside-secret.md"
    outside.write_text("secret\n", encoding="utf-8")
    link = skill_root / "references" / "evals" / "leak.md"
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ValueError, match="symlinked support path"):
        evals._stage_tessl_eval_source(tmp_path, "Skills/example-skill", tmp_path / "staged")


def test_tessl_live_staging_rejects_symlinked_support_files(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    outside = tmp_path / "outside-secret.md"
    outside.write_text("secret\n", encoding="utf-8")
    link = skill_root / "assets" / "leak.md"
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ValueError, match="symlinked support path"):
        evals._stage_tessl_live_private_source(
            tmp_path,
            "Skills/example-skill",
            "jscraik",
            tmp_path / "staged",
        )


def test_evals_generic_smoke_defaults_to_local_only(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke")

    assert result.status == "success"
    commands = [call.args[0] for call in run.call_args_list]
    assert not any(cmd[0] == "tessl" for cmd in commands)
    assert result.data["tessl_eval"]["status"] == "skipped"
    assert result.data["tessl_eval"]["reason"] == "local_only_default"


def test_legacy_direct_tessl_submission_helper_is_not_available() -> None:
    assert not hasattr(evals, "_run_tessl_eval")


def test_evals_generic_smoke_does_not_require_tessl_cli(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value=None),
        mock.patch.object(evals.subprocess, "run", return_value=completed),
    ):
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke")

    assert result.status == "success"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "skipped"
    assert tessl_eval["reason"] == "local_only_default"
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_completed",
    ]


def test_evals_generic_smoke_preserves_primary_failure_without_tessl(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=1, stdout="primary regression", stderr="assertion failed")
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value=None),
        mock.patch.object(evals.subprocess, "run", return_value=completed),
    ):
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke")

    assert result.status == "error"
    assert result.data["eval_status"] == "fail"
    assert result.data["blocker_class"] is None
    assert result.data["tessl_eval"]["status"] == "skipped"
    assert "tessl_eval_status" not in result.data
    assert "tessl_blocker_class" not in result.data
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_completed",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "fail"
    assert result.data["lifecycle_event"]["outcome"]["blocker_classes"] == []


def test_evals_rejects_legacy_direct_tessl_continuation(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run") as run:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            skip_tessl=False,
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "Direct Tessl eval submission is retired" in tessl_eval["blocker"]
    run.assert_not_called()


def test_evals_rejects_conflicting_local_only_and_live_tessl_flags(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run") as run:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            skip_tessl=True,
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "error"
    assert result.data["tessl_eval"]["status"] == "blocked"
    assert result.data["tessl_eval"]["blocker_class"] == "blocked_validation"
    assert "cannot be combined" in result.data["tessl_eval"]["blocker"]
    run.assert_not_called()


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
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    assert result.data["dashboard_path"] == "Infrastructure/artifacts/skill-reviews/example-skill-dashboard-smoke.html"
    assert result.data["dashboard_tab"] == "evals"
    assert result.data["scorecard_path"] == "Infrastructure/artifacts/skills/example-skill/run-1/scorecard.json"
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
    assert "disposable .tessl-plugin/plugin.json package-shape check" in html_text
    assert "opt-in local dependency security screening" in html_text


def test_run_evals_writes_blocked_closeout_for_partial_report_dir(tmp_path: Path) -> None:
    report_dir = tmp_path / "Infrastructure/artifacts/skills/example-skill/run-partial"
    case_dir = report_dir / "01-edge-case"
    case_dir.mkdir(parents=True)
    (case_dir / "prompt.txt").write_text("Task: sparse brief\n", encoding="utf-8")
    completed = mock.Mock(
        returncode=0,
        stdout=f"Skill evals: example-skill\nReports: {report_dir}\nRESULT: PASS\n",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_missing_artifact"
    closeout = result.data["eval_closeout"]
    assert closeout["schema_version"] == "skills-sdk.eval-closeout.v1"
    assert closeout["status"] == "blocked"
    assert closeout["blocker_class"] == "blocked_missing_artifact"
    assert closeout["cases"] == [
        {
            "id": "edge-case",
            "status": "blocked",
            "blocker_class": "blocked_missing_artifact",
            "expected_artifacts": ["result.json"],
            "actual_artifacts": ["prompt.txt"],
            "result_path": "Infrastructure/artifacts/skills/example-skill/run-partial/01-edge-case",
        }
    ]
    closeout_path = tmp_path / result.data["eval_closeout_path"]
    assert closeout_path.is_file()
    assert closeout["closeout_validation"]["status"] == "pass"


def test_run_evals_blocks_success_without_report_directory(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=0,
        stdout="Skill evals: example-skill\nRESULT: PASS\n",
        stderr="",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_missing_artifact"
    closeout = result.data["eval_closeout"]
    assert closeout["status"] == "blocked"
    assert closeout["blocker_class"] == "blocked_missing_artifact"
    assert closeout["report_dir"] is None
    assert closeout["missing_suite_artifacts"] is True
    assert closeout["mutation_allowed"] is False
    assert closeout["registry_update_allowed"] is False
    assert closeout["closeout_validation"]["status"] == "pass"
    assert result.data["eval_closeout_path"].startswith(
        "Infrastructure/artifacts/evals/closeouts/"
    )


def test_eval_closeout_validation_blocks_non_pass_mutation() -> None:
    closeout = {
        "schema_version": "jscraik.eval-closeout.v1",
        "status": "blocked",
        "skill_path": "Skills/example/SKILL.md",
        "mode": "smoke",
        "runner": "codex",
        "cases": [{"id": "edge", "status": "blocked", "blocker_class": "blocked_missing_artifact"}],
        "blocker_class": "blocked_missing_artifact",
        "mutation_allowed": True,
        "registry_update_allowed": True,
        "next_reproduce_command": "./bin/ask evals run Skills/example --mode smoke --runner codex",
    }

    validation = evals.validate_eval_closeout_payload(closeout)

    assert validation["status"] == "blocked"
    blocker_ids = {blocker["id"] for blocker in validation["blockers"]}
    assert "non_pass_blocks_source_mutation" in blocker_ids
    assert "non_pass_blocks_registry_promotion" in blocker_ids


def test_evals_run_validation_command_preserves_timeout_seconds() -> None:
    command = evals._evals_run_validation_command(
        "Skills/example",
        mode="smoke",
        runner="codex",
        dashboard=True,
        timeout_seconds=17,
    )

    assert command == "./bin/ask evals run Skills/example --mode smoke --runner codex --timeout-seconds 17 --json --robot"


def test_eval_closeout_doctor_reports_missing_case_result(tmp_path: Path) -> None:
    report_dir = tmp_path / "Infrastructure/artifacts/skills/example-skill/run-partial"
    case_dir = report_dir / "01-edge-case"
    case_dir.mkdir(parents=True)
    (case_dir / "prompt.txt").write_text("Task: sparse brief\n", encoding="utf-8")
    closeout = {
        "schema_version": "jscraik.eval-closeout.v1",
        "status": "blocked",
        "skill_path": "Skills/example/SKILL.md",
        "mode": "smoke",
        "runner": "codex",
        "cases": [{"id": "edge-case", "status": "blocked", "blocker_class": "blocked_missing_artifact"}],
        "blocker_class": "blocked_missing_artifact",
        "mutation_allowed": False,
        "registry_update_allowed": False,
        "missing_suite_artifacts": True,
        "next_reproduce_command": "./bin/ask evals run Skills/example --mode smoke --runner codex",
    }
    (report_dir / "workflow-closeout.json").write_text(json.dumps(closeout), encoding="utf-8")

    result = evals.eval_closeout_doctor(tmp_path, str(report_dir))

    assert result.status == "error"
    doctor = result.data["eval_closeout_doctor"]
    assert doctor["status"] == "blocked"
    assert doctor["missing_result_cases"] == ["edge-case"]

__all__ = [name for name in globals() if not name.startswith("__")]
