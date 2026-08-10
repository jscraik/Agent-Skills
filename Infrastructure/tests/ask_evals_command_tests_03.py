from ask_evals_command_tests_02 import *  # noqa: F403

def test_tessl_projection_shape_rejects_invalid_bundled_mcp(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    manifest_path = staged_source / ".tessl-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["mcpServers"] = ".mcp.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (staged_source / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"bad": {"type": "stdio"}}}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="stdio MCP servers must declare a command"):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_projection_shape_rejects_tesslignore_that_hides_entrypoints(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    (staged_source / ".tesslignore").write_text(
        "AGENTS.md\nCLAUDE.md\nGEMINI.md\n.harness/\n.agents/\n.codex/\ndist/\nskills/\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must not ignore manifest entrypoints"):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_projection_shape_rejects_wrong_project_marker_name(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    (staged_source / "tessl.json").write_text(
        json.dumps({"name": "jscraik/other-project", "mode": "managed", "dependencies": {}}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exact workspace/project name jscraik/example-skill"):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_live_private_requires_generated_scenarios_unless_structure_only(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "contract.yaml").write_text("version: 1\n", encoding="utf-8")

    try:
        evals._stage_tessl_live_private_source(tmp_path, "Skills/example-skill", "jscraik", temp_root=tmp_path / "stage")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected live Tessl staging to require generated scenarios")

    assert "require reviewed generated scenarios" in message
    assert "prepare-tessl-scenarios" in message


def test_tessl_structure_only_policy_only_reads_tessl_scenario_policy(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    contract_path = skill_root / "references" / "contract.yaml"
    contract_path.write_text(
        "version: 1\n"
        "unrelated_policy:\n"
        "  structure_only: true\n",
        encoding="utf-8",
    )

    assert evals._tessl_structure_only_scenario_policy(skill_root) is False

    contract_path.write_text(
        "version: 1\n"
        "tessl_scenario_policy:\n"
        "  structure_only: true\n",
        encoding="utf-8",
    )

    assert evals._tessl_structure_only_scenario_policy(skill_root) is True


def test_tessl_live_private_accepts_generated_yaml_cases(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "contract.yaml").write_text("version: 1\n", encoding="utf-8")
    cases = [
        {
            "id": "yaml-generated",
            "unit": "yaml generated scenario",
            "given": "A reviewed generated scenario was imported into references/evals.yaml.",
            "should": "Treat the YAML-imported scenario as generated scenario evidence.",
            "prompt": "Review the architecture handoff.",
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": "Recognizes the YAML-imported generated scenario as reviewed Tessl evidence.",
                }
            ],
            "tessl": {"generated": True, "source": "references/evals.yaml"},
        }
    ]

    merged, manifest = evals._merge_tessl_cases_with_generated_fixtures(
        skill_root,
        cases,
        require_generated=True,
    )

    assert merged == cases
    assert manifest["generated_yaml_cases"] == 1
    assert manifest["generated_fixture_cases"] == 0


def test_tessl_eval_cases_compat_reads_yaml_generated_tessl_metadata() -> None:
    cases = evals._parse_tessl_eval_cases_compat(
        """
cases:
  - id: yaml-generated
    unit: yaml generated scenario
    given: A reviewed generated scenario was imported into references/evals.yaml.
    should: Treat the YAML-imported scenario as generated scenario evidence.
    prompt: Review the architecture handoff.
    tessl:
      generated: true
      source: references/evals.yaml
"""
    )

    assert cases == [
        {
            "id": "yaml-generated",
            "unit": "yaml generated scenario",
            "given": "A reviewed generated scenario was imported into references/evals.yaml.",
            "should": "Treat the YAML-imported scenario as generated scenario evidence.",
            "prompt": "Review the architecture handoff.",
            "tessl": {
                "generated": True,
                "source": "references/evals.yaml",
            },
        }
    ]


def test_tessl_live_private_stages_generated_fixture_scenarios(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "contract.yaml").write_text(
        "version: 1\n"
        "tessl_scenario_policy:\n"
        "  structure_only: true\n",
        encoding="utf-8",
    )
    fixture_dir = skill_root / "references" / "evals"
    fixture_dir.mkdir()
    (fixture_dir / "eval.arch.boundary-proof.md").write_text(
        (
            "# eval.arch.boundary-proof: Boundary Proof\n\n"
            "Knowledge claim: The skill should block unsafe architecture claims without caller proof.\n"
            "Behavior under test: Architecture boundary proof classification.\n"
            "Expected agent move: Classifies the boundary as risky, names missing caller proof, and recommends a tracer.\n"
            "Failure mode: Treats tidy module names as sufficient proof.\n"
            "Given: A module boundary looks clean but has no caller evidence, characterization test, or tracer path.\n"
            "Should: Classify the boundary as risky and request proof before autonomous edits.\n"
            "Expected failure: Treats tidy module names as sufficient proof.\n"
        ),
        encoding="utf-8",
    )

    staged_source, copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )

    manifest = json.loads((staged_source / "scenario-sources.json").read_text(encoding="utf-8"))
    assert manifest["skill_owned_cases"] == 1
    assert manifest["generated_fixture_cases"] == 1
    assert manifest["structure_only_exception"] is True
    assert "scenario-sources.json" in copied
    assert "skills/example-skill/references/evals/eval.arch.boundary-proof.md" in copied
    generated_case = staged_source / "evals" / "generated-eval.arch.boundary-proof" / "task.md"
    assert generated_case.exists()
    generated_task = generated_case.read_text(encoding="utf-8")
    assert "Review the architecture situation" not in generated_task
    assert "Architecture situation:" not in generated_task
    assert "next action" in generated_task
    criteria = json.loads(
        (staged_source / "evals" / "generated-eval.arch.boundary-proof" / "criteria.json").read_text(
            encoding="utf-8"
        )
    )
    assert criteria["metadata"]["source"] == "references/evals/eval.arch.boundary-proof.md"
    descriptions = [item["description"] for item in criteria["checklist"]]
    assert any("Classifies the boundary as risky" in item for item in descriptions)


def test_tessl_live_private_caps_yaml_set_before_generated_fixtures(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "contract.yaml").write_text("version: 1\n", encoding="utf-8")
    cases_yaml = ["cases:"]
    for index in range(evals.TESSL_LIVE_PRIVATE_MAX_SCENARIOS + 1):
        cases_yaml.extend([
            f"  - id: yaml-case-{index:02d}",
            f"    unit: YAML case {index:02d}",
            "    given: A reviewed YAML scenario is ready for the default Tessl live confirmation set.",
            "    should: Keep the default live upload inside the cost-bounded confirmation set.",
            "    prompt: Check the handoff evidence.",
            "    acceptance:",
            "      - type: expected_signal",
            "        value: Confirms the bounded handoff evidence.",
        ])
    (skill_root / "references" / "evals.yaml").write_text("\n".join(cases_yaml) + "\n", encoding="utf-8")
    fixture_dir = skill_root / "references" / "evals"
    fixture_dir.mkdir()
    (fixture_dir / "eval.reviewed.generated-fixture.md").write_text(
        (
            "# eval.reviewed.generated-fixture: Generated Fixture\n\n"
            "Knowledge claim: Generated fixtures need explicit budgeted live lanes.\n"
            "Behavior under test: Default Tessl live budget selection.\n"
            "Expected agent move: Excludes generated fixtures from the default live upload.\n"
            "Failure mode: Uploads generated fixtures without explicit budget approval.\n"
            "Given: A reviewed generated fixture exists next to enough YAML scenarios.\n"
            "Should: Stage only the capped YAML confirmation set by default.\n"
            "Expected failure: Uploads generated fixtures without explicit budget approval.\n"
        ),
        encoding="utf-8",
    )

    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )

    staged_case_ids = evals._tessl_live_staged_case_ids(staged_source)
    manifest = json.loads((staged_source / "scenario-sources.json").read_text(encoding="utf-8"))
    assert len(staged_case_ids) == evals.TESSL_LIVE_PRIVATE_MAX_SCENARIOS
    assert "generated-eval.reviewed.generated-fixture" not in staged_case_ids
    excluded_id = f"yaml-case-{evals.TESSL_LIVE_PRIVATE_MAX_SCENARIOS:02d}"
    assert excluded_id not in staged_case_ids
    assert manifest["generated_fixture_cases"] == 1
    assert manifest["default_live_selection"]["excluded_generated_fixture_case_ids"] == [
        "generated-eval.reviewed.generated-fixture"
    ]
    assert manifest["default_live_selection"]["excluded_over_cap_case_ids"] == [excluded_id]
    assert evals._tessl_live_budget_preflight(staged_source)["status"] == "pass"


def test_tessl_live_private_selects_declared_release_set_before_cap() -> None:
    base_cases = [{"id": f"case-{index:02d}"} for index in range(12)]
    release_ids = {f"case-{index:02d}" for index in range(4, 12)}
    manifest: dict[str, object] = {}

    selected = evals._select_default_tessl_live_cases(
        base_cases,
        list(base_cases),
        manifest,
        release_ids,
    )

    assert [case["id"] for case in selected] == [f"case-{index:02d}" for index in range(4, 12)]
    assert manifest["default_live_selection"]["policy"] == "declared_release_set_capped_before_live_budget"


def test_tessl_live_private_staging_excludes_platform_junk_files(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / ".DS_Store").write_text("finder metadata\n", encoding="utf-8")
    apple_double = skill_root / "references" / ".AppleDouble"
    apple_double.mkdir()
    (apple_double / "metadata").write_text("finder metadata\n", encoding="utf-8")

    staged_source, copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )

    assert not any(".DS_Store" in path for path in copied)
    assert not any(".AppleDouble" in path for path in copied)
    assert not list(staged_source.rglob(".DS_Store"))
    assert not list(staged_source.rglob(".AppleDouble"))


def test_tessl_local_proof_preview_records_lint_pack_install_and_review_commands(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run") as run:
        receipt = evals.run_tessl_local_proof(
            tmp_path,
            "Skills/example-skill",
            workspace="jscraik",
            execute=False,
            include_review=True,
        )

    assert receipt["status"] == "preview"
    assert receipt["execute"] is False
    assert receipt["policy"]["no_publish"] is True
    assert receipt["policy"]["install_scope"] == "temporary project workspace under /tmp/ask-tessl-local-install"
    assert receipt["staged_file_count"] > 0
    commands = receipt["planned_commands"]
    assert "tessl plugin lint" in commands["plugin_lint"]
    assert "tessl plugin pack --output" in commands["plugin_pack"]
    assert "tessl install file:" in commands["install_file"]
    assert "--agent codex" in commands["install_file"]
    assert "tessl review run" in commands["review_run"]
    assert "--workspace jscraik" in commands["review_run"]
    assert not any("publish" in command for command in commands.values())
    assert not any("npx" in command for command in commands.values())
    run.assert_not_called()


def test_tessl_local_proof_accepts_skill_md_path(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    receipt = evals.run_tessl_local_proof(
        tmp_path,
        "Skills/example-skill/SKILL.md",
        workspace="jscraik",
        execute=False,
    )

    assert receipt["status"] == "preview"
    assert receipt["source_path"] == "Skills/example-skill/SKILL.md"
    assert receipt["proof_path"] == "Skills/example-skill"
    assert receipt["dist_path"].endswith("/example-skill.tgz")
    assert "/skills/example-skill" in receipt["planned_commands"]["review_run"]


def test_tessl_local_proof_execute_uses_temp_install_workspace_and_no_publish(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")
    install_completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="Authenticated as operator@example.com\nInstalled jscraik/example-skill@0.1.0\n",
        stderr="",
    )

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=[completed, completed, install_completed, completed]) as run,
    ):
        receipt = evals.run_tessl_local_proof(
            tmp_path,
            "Skills/example-skill",
            workspace="jscraik",
            execute=True,
            include_review=True,
            timeout_seconds=17,
        )

    assert receipt["status"] == "pass"
    assert receipt["execute"] is True
    assert set(receipt["commands"]) == {"plugin_lint", "plugin_pack", "install_file", "review_run"}
    assert "operator@example.com" not in receipt["commands"]["install_file"]["stdout"]
    assert "<redacted-email>" in receipt["commands"]["install_file"]["stdout"]
    assert run.call_count == 4
    install_call = run.call_args_list[2]
    install_command = install_call.args[0]
    assert install_command[:2] == ["/usr/local/bin/tessl", "install"]
    assert install_command[2].startswith("file:")
    assert install_command[3:] == ["--agent", "codex", "--yes", "--strict"]
    assert "/ask-tessl-local-install/" in install_call.kwargs["cwd"]
    assert str(tmp_path) not in install_call.kwargs["cwd"]
    for call in run.call_args_list:
        command = call.args[0]
        assert "publish" not in command
        assert "npx" not in command
        assert call.kwargs["timeout"] == 17
        assert call.kwargs["env"]["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] == "0"


def test_tessl_local_proof_uses_canonical_blocked_validation_fallback(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_run_tessl_local_command",
            return_value={"status": "blocked", "blocker": "lint receipt was unavailable"},
        ),
    ):
        receipt = evals.run_tessl_local_proof(
            tmp_path,
            "Skills/example-skill",
            workspace="jscraik",
            execute=True,
        )

    assert receipt["status"] == "blocked"
    assert receipt["blocker_class"] == "blocked_validation"


def test_tessl_live_private_requires_five_behavioral_scenarios(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "contract.yaml").write_text("version: 1\n", encoding="utf-8")
    fixture_dir = skill_root / "references" / "evals"
    fixture_dir.mkdir()
    (fixture_dir / "eval.arch.boundary-proof.md").write_text(
        (
            "# eval.arch.boundary-proof: Boundary Proof\n\n"
            "Expected agent move: Classifies the boundary as risky, names missing caller proof, and recommends a tracer.\n"
            "Given: A module boundary looks clean but has no caller evidence, characterization test, or tracer path.\n"
            "Should: Classify the boundary as risky and request proof before autonomous edits.\n"
        ),
        encoding="utf-8",
    )

    try:
        evals._stage_tessl_live_private_source(
            tmp_path,
            "Skills/example-skill",
            "jscraik",
            temp_root=tmp_path / "stage",
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected behavioral live staging to require 5 scenarios")

    assert "require at least 5 gold-standard structured scenarios" in message
    assert "Found 2" in message


def test_evals_live_private_dry_run_is_not_failed_by_discovery_smoke_filter(tmp_path: Path) -> None:
    completed = mock.Mock(
        returncode=1,
        stdout="",
        stderr=(
            "ERROR: discovery-smoke runner requires eval cases with `smoke_mode`; "
            "none matched the selected filters. Use a live runner such as `codex` "
            "for behavior evals, or add discovery-specific smoke_mode cases.\n"
        ),
    )
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_tessl_dry_run_admission", return_value={"ready_for_tessl_dry_run": True}),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="release",
            runner="discovery-smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
            tessl_live_dry_run=True,
            dashboard=False,
        )

    assert result.status == "success"
    assert result.errors == []
    assert result.data["local_eval_status"] == "skipped_tessl_live_dry_run"
    assert result.data["eval_status"] == "pass"
    assert result.data["blocker_class"] is None
    assert result.data["tessl_eval"]["status"] == "pass"
    assert result.data["tessl_eval"]["dry_run"] is True
    assert "staged private Tessl payload" in result.data["tessl_dry_run_note"]
    assert result.data["lifecycle_event"]["event_type"] == "eval_completed"
    assert result.data["lifecycle_event"]["outcome"]["status"] == "pass"


def test_evals_live_private_dry_run_failure_records_blocked_lifecycle(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(
            evals,
            "_run_tessl_live_private_eval",
            return_value={
                "status": "blocked",
                "blocker": "Tessl workspace is required.",
                "blocker_class": "blocked_validation",
            },
        ) as run_live_private,
        mock.patch.object(evals, "_tessl_dry_run_admission", return_value={"ready_for_tessl_dry_run": True}),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="release",
            runner="discovery-smoke",
            tessl_live_private=True,
            tessl_live_dry_run=True,
            tessl_workspace="jscraik",
            dashboard=False,
        )

    run_live_private.assert_called_once()
    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["lifecycle_event"]["event_type"] == "eval_blocked"
    assert result.data["lifecycle_event"]["outcome"]["status"] == "blocked_validation"
    assert result.data["lifecycle_events"][-1]["event_type"] == "eval_blocked"


def test_evals_rejects_dry_run_without_live_private(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run") as run:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="release",
            runner="discovery-smoke",
            tessl_live_dry_run=True,
            dashboard=False,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["blocker_class"] == "blocked_validation"
    assert result.data["tessl_eval"]["blocker"] == "--tessl-live-dry-run requires --tessl-live-private."
    assert result.errors[0].code == "ERR_VALIDATION"
    run.assert_not_called()


def test_evals_live_private_blocks_without_handoff_readiness(tmp_path: Path) -> None:
    readiness_path = _write_handoff_readiness(tmp_path, "example-skill")
    _write_example_skill(tmp_path)
    readiness_path.unlink()

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run") as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["handoff_readiness"]["ready_for_live_tessl"] is False
    assert result.data["tessl_eval"]["status"] == "blocked"
    assert result.data["tessl_eval"]["blocker_class"] == "blocked_validation"
    assert "Handoff readiness" in result.data["tessl_eval"]["blocker"]
    run.assert_not_called()


def test_evals_live_private_blocks_unproven_oss_scenarios_before_tessl(tmp_path: Path) -> None:
    _write_handoff_readiness(tmp_path, "example-skill")
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: smoke-example\n"
            "    unit: example skill behavioural proof\n"
            "    given: A user asks for the proven example behavior.\n"
            "    should: Produce the expected example behavior.\n"
            "    prompt: Do the example task.\n"
            "    acceptance:\n"
            "      - type: expected_signal\n"
            "        value: Produces the expected example behavior.\n"
            "  - id: unproven-live-only\n"
            "    unit: unproven live upload guard\n"
            "    given: A scenario lacks OSS local and cloud pass evidence.\n"
            "    should: Block before Tessl live submission.\n"
            "    prompt: Do another example task.\n"
            "    acceptance:\n"
            "      - type: expected_signal\n"
            "        value: Blocks before Tessl live submission.\n"
        ),
        encoding="utf-8",
    )

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run") as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="release",
            tessl_live_private=True,
            tessl_workspace="jscraik",
            dashboard=False,
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "without both oss-local and oss-cloud pass evidence" in tessl_eval["blocker"]
    parity = tessl_eval["oss_scenario_parity"]
    assert parity["status"] == "blocked"
    assert parity["staged_case_count"] == 2
    assert parity["unproven_case_ids"] == ["unproven-live-only"]
    assert parity["missing_by_lane"]["oss-local"] == ["unproven-live-only"]
    assert parity["missing_by_lane"]["oss-cloud"] == ["unproven-live-only"]
    assert parity["lane_receipts"]["oss-local"]["receipt_found"] is True
    assert parity["lane_receipts"]["oss-cloud"]["receipt_found"] is True
    run.assert_not_called()


def test_evals_live_private_proceeds_when_oss_lanes_match_tessl_case_set(tmp_path: Path) -> None:
    _write_handoff_readiness(tmp_path, "example-skill")
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: smoke-example\n"
            "    unit: proven live upload guard\n"
            "    given: A scenario has OSS local and cloud pass evidence.\n"
            "    should: Proceed to Tessl live submission.\n"
            "    prompt: Do the example task.\n"
            "    acceptance:\n"
            "      - type: expected_signal\n"
            "        value: Produces the expected example behavior.\n"
        ),
        encoding="utf-8",
    )

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
            mock.patch.object(evals.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="{}", stderr="")) as run,
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

    assert result.status == "success"
    parity = result.data["tessl_eval"]["oss_scenario_parity"]
    assert parity["status"] == "pass"
    assert parity["missing_by_lane"] == {"oss-local": [], "oss-cloud": []}
    assert parity["extra_by_lane"] == {"oss-local": [], "oss-cloud": []}
    assert parity["lane_receipts"]["oss-local"]["receipt_found"] is True
    assert parity["lane_receipts"]["oss-cloud"]["receipt_found"] is True
    run.assert_not_called()

__all__ = [name for name in globals() if not name.startswith("__")]
