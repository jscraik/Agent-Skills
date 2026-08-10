from ask_evals_command_tests_03 import *  # noqa: F403

def test_evals_live_private_requires_oss_lanes_to_match_tessl_case_set(tmp_path: Path) -> None:
    _write_handoff_readiness(tmp_path, "example-skill")
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: smoke-example\n"
            "    unit: exact live case-set rehearsal\n"
            "    given: A live Tessl candidate has one selected case.\n"
            "    should: Block when oss-cloud evidence contains a different wider case set.\n"
            "    prompt: Do the example task.\n"
            "    acceptance:\n"
            "      - type: expected_signal\n"
            "        value: Produces the expected example behavior.\n"
        ),
        encoding="utf-8",
    )
    evidence_root = tmp_path / ".harness" / "evidence" / "handoff" / "example-skill"
    for lane_id in ("oss-local", "oss-cloud"):
        receipt_path = evidence_root / f"{lane_id}.json"
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload["cases"].append({"case_id": "extra-not-in-live-upload", "status": "pass"})
        receipt_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
            mock.patch.object(
                evals,
                "_tessl_live_handoff_readiness",
                return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
            ),
            mock.patch.object(
                evals,
                "_tessl_dry_run_admission",
                return_value={"ready_for_tessl_dry_run": True, "blockers": [], "required_next_actions": []},
            ),
            mock.patch.object(evals.subprocess, "run") as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="release",
            tessl_live_private=True,
            tessl_live_dry_run=True,
            tessl_workspace="jscraik",
            dashboard=False,
        )

    assert result.status == "error"
    parity = result.data["tessl_eval"]["oss_scenario_parity"]
    assert parity["status"] == "blocked"
    assert parity["missing_by_lane"] == {"oss-local": [], "oss-cloud": []}
    assert parity["extra_by_lane"]["oss-local"] == ["extra-not-in-live-upload"]
    assert parity["extra_by_lane"]["oss-cloud"] == ["extra-not-in-live-upload"]
    assert parity["extra_case_ids"] == ["extra-not-in-live-upload"]
    run.assert_not_called()


def test_tessl_live_private_policy_names_tessl_local_proof_gate() -> None:
    policy = evals._tessl_live_private_policy("jscraik")
    feedback_loop = policy["pre_tessl_feedback_loop"]

    assert "tessl_local_proof" in feedback_loop["required_order"]
    assert any(step["stage"] == "tessl_local_proof" for step in feedback_loop["tessl_sequence"])
    assert "Tessl local-proof" in feedback_loop["failure_loop"]
    assert "Tessl local-proof" in feedback_loop["live_blocked_until"]


def test_tessl_live_private_rejects_denied_external_effects(monkeypatch) -> None:
    monkeypatch.setenv("ASK_EXTERNAL_EFFECTS", "deny")

    result = evals._tessl_live_effects_block(
        "ask evals run", "Skills/example-skill", "jscraik", dry_run=False,
    )

    assert result is not None
    assert result["status"] == "blocked"
    assert result["blocker_class"] == "blocked_validation"
    assert "external-effect policy" in result["blocker"]


def test_tessl_live_private_requires_explicit_external_effect_permission(monkeypatch) -> None:
    monkeypatch.delenv("ASK_EXTERNAL_EFFECTS", raising=False)

    blocked = evals._tessl_live_effects_block(
        "ask evals run", "Skills/example-skill", "jscraik", dry_run=False,
    )

    assert blocked is not None
    assert blocked["status"] == "blocked"
    assert "ASK_EXTERNAL_EFFECTS=allow" in blocked["blocker"]


def test_evals_live_private_skips_local_only_cases(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path, "skill-factory-router")
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: local-negative\n"
            "    prompt: \"Write a poem instead of auditing.\"\n"
            "    tessl_live_private: false\n"
            "    acceptance:\n"
            "      - type: not_contains\n"
            "        value: example-skill\n"
            "  - id: live-pressure\n"
            "    unit: example live pressure proof\n"
            "    given: A user asks for an agent-readiness audit.\n"
            "    should: Produce a concrete audit finding instead of generic readiness language.\n"
            "    prompt: \"Audit the repository for agent readiness.\"\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(audit|readiness)\"\n"
            "      - type: expected_signal\n"
            "        value: Produces a concrete audit finding instead of generic readiness language.\n"
        ),
        encoding="utf-8",
    )
    (skill_root / "references" / "contract.yaml").write_text(
        "version: 1\ntessl_scenario_policy:\n  structure_only: true\n",
        encoding="utf-8",
    )
    evidence_root = tmp_path / ".harness" / "evidence" / "handoff" / "example-skill"
    for lane_id in ("oss-local", "oss-cloud"):
        receipt_path = evidence_root / f"{lane_id}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["cases"] = [{"case_id": "live-pressure", "status": "pass"}]
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    with (
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

    assert result.status == "success"
    tessl_eval = result.data["tessl_eval"]
    staged_files = tessl_eval["staged_files"]
    staged_source = Path(tessl_eval["staged_source"])
    assert "evals/live-pressure/task.md" in staged_files
    assert "evals/live-pressure/criteria.json" in staged_files
    assert not any("local-negative" in path for path in staged_files)
    assert not (staged_source / "evals" / "local-negative").exists()
    assert (staged_source / "evals" / "live-pressure" / "task.md").exists()


def test_evals_live_private_uses_plugin_project_identity(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    skill_root = tmp_path / "Plugins" / "skill-factory" / "skills" / "skill-factory-router"
    (skill_root / "references").mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: skill-factory-router\nmetadata:\n  version: "1.2.3"\n---\n'
        "# Skill Builder\n\nBuild and improve skills.\n",
        encoding="utf-8",
    )
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: plugin-scope\n"
            "    unit: plugin project identity proof\n"
            "    given: A plugin-owned skill is staged for a private Tessl assessment.\n"
            "    should: Preserve plugin project identity rather than using the nested skill name as the project.\n"
            "    prompt: \"Improve the plugin-owned skill.\"\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(plugin|project)\"\n"
            "      - type: expected_signal\n"
            "        value: Preserves plugin project identity rather than using the nested skill name as the project.\n"
        ),
        encoding="utf-8",
    )
    (skill_root / "references" / "contract.yaml").write_text(
        "version: 1\ntessl_scenario_policy:\n  structure_only: true\n",
        encoding="utf-8",
    )

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(
            evals,
            "_tessl_dry_run_admission",
            return_value={"ready_for_tessl_dry_run": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(
            evals,
            "_tessl_live_oss_scenario_parity",
            return_value={"status": "pass", "rule": "project-identity fixture"},
        ),
    ):
        result = evals.run_evals(
            tmp_path,
            "Plugins/skill-factory/skills/skill-factory-router",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
            tessl_live_dry_run=True,
        )

    assert result.status == "success"
    tessl_eval = result.data["tessl_eval"]
    staged_source = Path(tessl_eval["staged_source"])
    plugin_manifest = json.loads((staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
    project_marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
    assert not (staged_source / "tile.json").exists()
    assert plugin_manifest["name"] == "jscraik/skill-factory"
    assert plugin_manifest["skills"] == "./skills/"
    assert (staged_source / "skills" / "skill-factory-router" / "SKILL.md").is_file()
    assert project_marker["name"] == "jscraik/skill-factory"


def test_evals_run_ignores_workspace_without_live_private_opt_in(tmp_path: Path) -> None:
    skill_root = tmp_path / "Plugins" / "skill-factory" / "skills" / "skill-factory-router"
    (skill_root / "references").mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: skill-factory-router\nmetadata:\n  version: "1.2.3"\n---\n# Skill Builder\n',
        encoding="utf-8",
    )
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: plugin-scope\n"
            "    unit: plugin project identity proof\n"
            "    given: A plugin-owned skill is staged for Tessl.\n"
            "    should: Preserve plugin project identity when workspace is set.\n"
            "    prompt: \"Improve the plugin skill.\"\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(plugin|skill)\"\n"
            "      - type: expected_signal\n"
            "        value: Preserves plugin project identity when workspace is set.\n"
        ),
        encoding="utf-8",
    )

    completed = _completed_eval_with_report(tmp_path, "skill-factory-router")

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Plugins/skill-factory/skills/skill-factory-router",
            mode="smoke",
            tessl_workspace="jscraik",
        )

    tessl_eval = result.data["tessl_eval"]
    assert result.status == "success"
    assert tessl_eval["status"] == "skipped"
    assert result.data["tessl_workspace"] is None
    assert all(call.args[0][0] != "/usr/local/bin/tessl" for call in run.call_args_list)


def test_tessl_project_link_relinks_mismatched_existing_project(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        if "--relink" in cmd:
            return mock.Mock(returncode=0, stdout='{"status":"relinked"}', stderr="", args=cmd)
        if "--update-source" in cmd:
            return mock.Mock(returncode=0, stdout='{"status":"updated"}', stderr="", args=cmd)
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"workspace":"old-workspace","project":"old-project","name":"old-workspace/old-project"}',
                stderr="",
                args=cmd,
            )
        raise AssertionError(f"unexpected command: {cmd}")

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "plugin",
                "workspace": "jscraik",
                "project": "skill-factory",
                "name": "jscraik/skill-factory",
            },
        )

    assert link["status"] == "pass"
    assert link["action"] == "relinked_existing_project_updated_source"
    assert any("--relink" in call for call in calls)


def test_tessl_project_link_creates_after_missing_existing_project(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        if "--relink" in cmd:
            return mock.Mock(returncode=1, stdout="", stderr="Project not found", args=cmd)
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(returncode=1, stdout='{"status":"needs_repair"}', stderr="", args=cmd)
        if cmd[1:3] == ["project", "create"]:
            return mock.Mock(returncode=0, stdout="created\n", stderr="", args=cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "plugin",
                "workspace": "jscraik",
                "project": "skill-factory",
                "name": "jscraik/skill-factory",
            },
        )

    assert link["status"] == "pass"
    assert link["action"] == "created_project"
    assert calls[-1] == [
        "/usr/local/bin/tessl",
        "project",
        "create",
        "--new",
        "--workspace",
        "jscraik",
        "skill-factory",
    ]


def test_tessl_project_link_creates_when_relink_json_status_is_error(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        if "--relink" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"status":"error","message":"Project not found in workspace jscraik: improve-agent-native"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(
                returncode=0,
                stdout='{"status":"match","workspaceName":"old-workspace","projectName":"old-project"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:3] == ["project", "create"]:
            return mock.Mock(returncode=0, stdout="created\n", stderr="", args=cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "standalone_skill",
                "workspace": "jscraik",
                "project": "improve-agent-native",
                "name": "jscraik/improve-agent-native",
            },
        )

    assert link["status"] == "pass"
    assert link["action"] == "created_project"
    assert calls[-1] == [
        "/usr/local/bin/tessl",
        "project",
        "create",
        "--new",
        "--workspace",
        "jscraik",
        "improve-agent-native",
    ]
    assert not any("--update-source" in call for call in calls)


def test_tessl_project_link_classifies_signal_kill_as_runtime_blocker(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        return mock.Mock(returncode=-9, stdout="", stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "standalone_skill",
                "workspace": "jscraik",
                "project": "improve-agent-native",
                "name": "jscraik/improve-agent-native",
            },
        )

    assert link["status"] == "blocked"
    assert link["action"] == "check"
    assert link["blocker_class"] == "blocked_runtime"
    assert "SIGKILL" in link["blocker"]
    assert "not a skill assessment result" in link["blocker"]
    assert link["commands"][0]["exit_code"] == -9
    assert link["commands"][0]["signal"] == "SIGKILL"


def test_tessl_project_link_updates_source_after_relink(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        if "--relink" in cmd:
            return mock.Mock(returncode=0, stdout='{"status":"relinked"}', stderr="", args=cmd)
        if "--update-source" in cmd:
            return mock.Mock(returncode=0, stdout='{"status":"updated"}', stderr="", args=cmd)
        if cmd[1:3] == ["project", "repair"] and "--json" in cmd:
            return mock.Mock(returncode=1, stdout='{"status":"needs_repair","allowedActions":["relink","update_source"]}', stderr="", args=cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "plugin",
                "workspace": "jscraik",
                "project": "skill-factory",
                "name": "jscraik/skill-factory",
            },
        )

    assert link["status"] == "pass"
    assert link["action"] == "relinked_existing_project_updated_source"
    assert calls[-1] == ["/usr/local/bin/tessl", "project", "repair", "--update-source", "--yes", "--json"]


def test_tessl_archive_retains_prior_scenarios_without_ingestable_path(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    prior_task = staged_root / "scenarios" / "old-case" / "task.md"
    prior_task.parent.mkdir(parents=True)
    prior_task.write_text("prior scenario evidence\n", encoding="utf-8")

    archive_dir = evals._archive_stage_children(staged_root, "local-eval")

    assert archive_dir is not None
    assert archive_dir.parent == tmp_path / "evidence-archive"
    assert not (archive_dir / "scenarios").exists()
    assert (archive_dir / "archived-scenarios" / "old-case" / "task.md").read_text(encoding="utf-8") == (
        "prior scenario evidence\n"
    )


def test_tessl_archive_sanitizes_existing_ingestable_archive_paths(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    stale_task = staged_root / "evidence-archive" / "old-run" / "scenarios" / "old-case" / "task.md"
    stale_task.parent.mkdir(parents=True)
    stale_task.write_text("stale scenario evidence\n", encoding="utf-8")
    current_task = staged_root / "scenarios" / "current-case" / "task.md"
    current_task.parent.mkdir(parents=True)
    current_task.write_text("current scenario evidence\n", encoding="utf-8")

    archive_dir = evals._archive_stage_children(staged_root, "local-eval")
    external_archive_root = tmp_path / "evidence-archive"

    assert archive_dir is not None
    assert not (staged_root / "evidence-archive").exists()
    assert (
        next(external_archive_root.glob("*legacy-evidence-archive/old-run/archived-scenarios/old-case/task.md"))
    ).read_text(encoding="utf-8") == "stale scenario evidence\n"
    assert not (archive_dir / "scenarios").exists()
    assert (archive_dir / "archived-scenarios" / "current-case" / "task.md").read_text(encoding="utf-8") == (
        "current scenario evidence\n"
    )


def test_tessl_local_and_live_staging_use_separate_stable_roots() -> None:
    local_root = evals._stable_tessl_stage_parent("Skills/example-skill")
    live_root = evals._stable_tessl_live_stage_parent("Skills/example-skill")

    assert local_root.parent.name == "ask-tessl-evals"
    assert live_root.parent.name == "ask-tessl-evals-live"
    assert local_root != live_root
    assert evals._tessl_live_private_policy("jscraik")["stable_staging_root"].startswith(
        str(live_root.parent)
    )


def test_timeout_partial_artifact_sanitizes_repo_paths(tmp_path: Path) -> None:
    skill_dir = tmp_path / "Skills" / "example"
    skill_dir.mkdir(parents=True)

    artifact = evals._write_timeout_partial_artifact(
        tmp_path,
        skill_path="Skills/example",
        mode="smoke",
        runner="codex",
        raw_output=f"wrote {tmp_path}/Skills/example/output.txt",
        raw_error=f"failed under {tmp_path}",
    )

    assert artifact is not None
    payload = (tmp_path / artifact).read_text(encoding="utf-8")
    assert str(tmp_path) not in payload
    assert "Skills/example/output.txt" in payload


def test_tessl_run_budget_preflight_blocks_when_capacity_unknown(tmp_path: Path) -> None:
    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        assert cmd[1:3] == ["eval", "list"]
        return mock.Mock(returncode=0, stdout='{"unexpected":"shape"}', stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_run_budget_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            tmp_path,
            {},
        )

    assert preflight["status"] == "blocked"
    assert preflight["blocker_class"] == "blocked_validation"
    assert "could not determine remaining capacity" in preflight["blocker"]
    assert preflight["capacity_source"] == "unparseable_eval_list"


def test_tessl_run_budget_preflight_blocks_when_eval_list_unavailable(tmp_path: Path) -> None:
    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        assert cmd[1:3] == ["eval", "list"]
        return mock.Mock(
            returncode=1,
            stdout="",
            stderr="- Fetching eval runs...\n✖ Failed to fetch eval runs\n",
            args=cmd,
        )

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_run_budget_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            tmp_path,
            {},
        )

    assert preflight["status"] == "blocked"
    assert preflight["blocker_class"] == "blocked_runtime"
    assert "could not fetch run history" in preflight["blocker"]
    assert preflight["capacity_source"] == "unavailable_eval_list"


def test_tessl_run_budget_preflight_uses_unbounded_eval_list(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        assert "--limit" not in cmd
        return mock.Mock(returncode=0, stdout=json.dumps({"data": [{"id": "run-1"}]}), stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_run_budget_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            tmp_path,
            {},
        )

    assert preflight["status"] == "pass"
    assert len(calls) == 1
    assert calls[0] == ["/usr/local/bin/tessl", "eval", "list", "--json", "--workspace", "jscraik"]
    assert preflight["used_runs"] == 1


def test_tessl_eval_list_count_rejects_error_payload_lists() -> None:
    payload = {
        "status": "error",
        "errors": [
            {"message": "workspace quota is unavailable"},
            {"message": "retry later"},
        ],
    }

    assert evals._tessl_eval_list_count(json.dumps(payload)) is None


def test_tessl_eval_list_count_rejects_unknown_nested_lists() -> None:
    payload = {
        "status": "ok",
        "metadata": {
            "warnings": [{"message": "not a run"}],
            "workspace": {"limits": [1, 2, 3]},
        },
    }

    assert evals._tessl_eval_list_count(json.dumps(payload)) is None


def test_tessl_eval_list_count_accepts_prefixed_json_output() -> None:
    stdout = (
        "Fetching workspace eval runs...\n"
        + json.dumps({
            "status": "ok",
            "runs": [
                {"id": "eval-run-1"},
                {"id": "eval-run-2"},
            ],
        })
    )

    assert evals._tessl_eval_list_count(stdout) == 2


def test_tessl_pending_run_preflight_blocks_existing_project_run(tmp_path: Path) -> None:
    payload = {
        "data": [
            {
                "id": "019edf73-3fdc-749d-b470-cc10e941715e",
                "type": "eval-run",
                "attributes": {
                    "status": "pending",
                    "metadata": {
                        "tileName": "jscraik/autoreview",
                        "tileVersion": "0.1.0",
                    },
                },
            }
        ]
    }

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        assert cmd[1:3] == ["eval", "list"]
        assert "--status" not in cmd
        assert "--tile" not in cmd
        return mock.Mock(returncode=0, stdout=json.dumps(payload), stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_pending_run_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            "autoreview",
            tmp_path,
            {},
        )

    assert preflight["status"] == "blocked"
    assert preflight["blocker_class"] == "blocked_environment"
    assert preflight["pending_eval_run_ids"] == ["019edf73-3fdc-749d-b470-cc10e941715e"]
    assert "inspect that run instead" in preflight["blocker"]


def test_tessl_pending_run_preflight_blocks_unparseable_history(tmp_path: Path) -> None:
    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        assert cmd[1:3] == ["eval", "list"]
        return mock.Mock(returncode=0, stdout='{"unexpected":"shape"}', stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_pending_run_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            "autoreview",
            tmp_path,
            {},
        )

    assert preflight["status"] == "blocked"
    assert preflight["blocker_class"] == "blocked_validation"
    assert "could not parse run history" in preflight["blocker"]


def test_tessl_pending_run_preflight_uses_unbounded_eval_list(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        assert "--limit" not in cmd
        return mock.Mock(returncode=0, stdout=json.dumps({"data": []}), stderr="", args=cmd)

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        preflight = evals._tessl_pending_run_preflight(
            "/usr/local/bin/tessl",
            "jscraik",
            "teach",
            tmp_path,
            {},
        )

    assert preflight["status"] == "pass"
    assert len(calls) == 1
    assert calls[0] == ["/usr/local/bin/tessl", "eval", "list", "--json", "--workspace", "jscraik"]
    assert preflight["pending_eval_run_ids"] == []

__all__ = [name for name in globals() if not name.startswith("__")]
