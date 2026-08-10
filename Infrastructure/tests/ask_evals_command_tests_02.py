from ask_evals_command_tests_01 import *  # noqa: F403

def test_macro_eval_report_exports_case_level_events(tmp_path: Path) -> None:
    report_dir = tmp_path / "Infrastructure" / "artifacts" / "skills" / "demo-skill" / "run-1"
    report_dir.mkdir(parents=True)
    (report_dir / "summary.json").write_text(
        json.dumps(
            {
                "schema_version": "2.1",
                "generated_at": "2026-05-25T10:00:00Z",
                "skill": "demo-skill",
                "run_id": "run-1",
                "eval_mode": "release",
                "runner_mode": "codex",
                "decision": "fail",
                "claim_to_evidence": {"passed": True, "blocking_gaps": []},
                "cases": [
                    {
                        "id": "pricing-exception",
                        "name": "Pricing exception",
                        "category": "pricing",
                        "passed": False,
                        "baseline_type": "neutral_repo_baseline",
                        "baseline_id": "pricing-neutral",
                        "comparison_inputs": {"control": "without-skill"},
                        "baseline_comparisons": {
                            "codex": {
                                "status": "compared",
                                "skill_lift": 1,
                                "is_beneficial": True,
                                "regression": False,
                            }
                        },
                        "skill_lift": 1,
                        "is_beneficial": True,
                        "baseline_regression": False,
                        "readiness_state": "comparison_incomplete",
                        "metric_availability": "available",
                        "evidence_surfaces": ["deterministic_checks", "expected_signals"],
                        "check_evidence": True,
                        "hard_gates": ["no_false_completion"],
                        "expected_evidence": ["acceptance"],
                        "tier1_failed": True,
                        "tier1_failures": ["expected margin guardrail evidence"],
                        "runners": {
                            "codex": {
                                "metrics": {
                                    "trace": {"tool_calls": 2},
                                    "expected_signals": {"score": 75},
                                },
                            },
                        },
                    },
                    {
                        "id": "clean-path",
                        "category": "clean",
                        "passed": True,
                        "runners": {},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (report_dir / "release_manifest.json").write_text('{"schema_version":"1.0"}\n', encoding="utf-8")
    component_source = tmp_path / "Infrastructure" / "templates" / "components"
    component_source.mkdir(parents=True)
    (component_source / "eval-report.tsx").write_text("export function MacroEvalTotals() { return null; }\n", encoding="utf-8")

    result = evals.macro_eval_report(tmp_path)

    assert result.status == "success"
    assert result.data["totals"]["summaries_scanned"] == 1
    assert result.data["totals"]["events"] == 2
    assert result.data["totals"]["behavior_patterns"] == 2
    events_path = tmp_path / result.data["artifacts"]["events_jsonl"]
    rows = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["case_type"] == "pricing"
    assert rows[0]["run_outcome"] == "failed"
    assert rows[0]["eval_finding"] == "expected margin guardrail evidence"
    assert rows[0]["behavior_pattern"] == "pricing:failed:expected-margin-guardrail-evidence"
    assert rows[0]["baseline_status"] == "executed_compared"
    assert rows[0]["baseline_type"] == "neutral_repo_baseline"
    assert rows[0]["skill_lift"] == 1
    assert rows[0]["is_beneficial"] is True
    assert rows[0]["baseline_regression"] is False
    assert rows[0]["readiness_state"] == "comparison_incomplete"
    assert rows[0]["metric_availability"] == "available"
    assert rows[0]["check_evidence"] is True
    assert rows[0]["verification_strategy"] == "executed_deterministic"
    assert rows[0]["verifier_types"] == [
        "deterministic_checks",
        "executed_check_evidence",
        "expected_evidence",
        "expected_signals",
        "hard_gates",
        "trace_metrics",
    ]
    assert rows[0]["summary_path"] == "Infrastructure/artifacts/skills/demo-skill/run-1/summary.json"
    assert rows[0]["release_manifest_path"] == "Infrastructure/artifacts/skills/demo-skill/run-1/release_manifest.json"
    assert rows[1]["case_type"] == "clean"
    assert rows[1]["run_outcome"] == "passed"
    assert rows[1]["eval_finding"] == "none"
    assert rows[1]["baseline_status"] == "none_declared"
    assert rows[1]["verification_strategy"] == "acceptance_only"
    assert (tmp_path / result.data["artifacts"]["report_json"]).is_file()
    assert result.data["groups"]["by_skill_behavior_pattern"] == [
        {
            "skill": "demo-skill",
            "behavior_pattern": "clean:passed:none",
            "trace_count": 1,
        },
        {
            "skill": "demo-skill",
            "behavior_pattern": "pricing:failed:expected-margin-guardrail-evidence",
            "trace_count": 1,
        },
    ]
    assert result.data["groups"]["by_verification_strategy"] == [
        {"verification_strategy": "acceptance_only", "trace_count": 1},
        {"verification_strategy": "executed_deterministic", "trace_count": 1},
    ]
    assert result.data["groups"]["by_baseline_status"] == [
        {"baseline_status": "executed_compared", "trace_count": 1},
        {"baseline_status": "none_declared", "trace_count": 1},
    ]
    assert {"verifier_type": "trace_metrics", "trace_count": 1} in result.data["groups"]["by_verifier_type"]
    assert (tmp_path / result.data["artifacts"]["report_components"]).is_file()
    mdx_text = (tmp_path / result.data["artifacts"]["report_mdx"]).read_text(encoding="utf-8")
    assert "schema_version: skill-macro-eval-report.mdx.v1" in mdx_text
    assert "MacroEvalTotals" in mdx_text
    assert "MacroEvalFlowTable rows={macroReport.groups.by_skill_behavior_pattern}" in mdx_text
    assert "export const macroReport = {" in mdx_text


def test_macro_eval_report_uses_claim_gap_when_case_has_no_finding(tmp_path: Path) -> None:
    report_dir = tmp_path / "Infrastructure" / "artifacts" / "skills" / "demo-skill" / "run-2"
    report_dir.mkdir(parents=True)
    (report_dir / "summary.json").write_text(
        json.dumps(
            {
                "skill": "demo-skill",
                "run_id": "run-2",
                "decision": "blocked",
                "claim_to_evidence": {
                    "passed": False,
                    "blocking_gaps": [{"type": "claim_without_case", "claim_id": "demo.claim"}],
                },
                "cases": [{"id": "governance-case", "passed": False, "runners": {}}],
            }
        ),
        encoding="utf-8",
    )

    result = evals.macro_eval_report(tmp_path, output_dir="macro-out")

    assert result.status == "success"
    events_path = tmp_path / "macro-out" / "macro-eval-events.jsonl"
    row = json.loads(events_path.read_text(encoding="utf-8").splitlines()[0])
    assert row["case_type"] == "governance"
    assert row["run_outcome"] == "blocked"
    assert row["eval_finding"] == "claim_without_case"
    assert result.data["groups"]["by_eval_finding"] == [
        {"eval_finding": "claim_without_case", "trace_count": 1}
    ]


def test_smoke_evals_can_use_discovery_smoke_without_codex_args(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with (
        mock.patch.object(evals, "_pyyaml_eval_python_command", return_value=["managed-python"]),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            runner="discovery-smoke",
            skip_tessl=True,
        )

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert cmd[:2] == ["managed-python", "Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py"]
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
    completed = _completed_eval_with_report(tmp_path, "evals-router")

    with (
        mock.patch.object(evals, "_pyyaml_eval_python_command", return_value=["managed-python"]),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
    ):
        result = evals.run_evals(
            tmp_path,
            ".agents/skills/evals-router",
            mode="smoke",
            runner="discovery-smoke",
            dashboard=False,
            skip_tessl=True,
        )

    assert result.status == "success"
    assert result.data["requested_path"] == ".agents/skills/evals-router"
    assert result.data["resolved_skill_path"] == "Skills/agent-ops/evals-router"
    cmd = run.call_args.args[0]
    assert cmd[cmd.index("Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py") + 1] == "Skills/agent-ops/evals-router"


def test_evals_run_defaults_to_local_only_without_project_mutation(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            allow_tessl_project_save=False,
    )

    assert result.status == "success"
    commands = [call.args[0] for call in run.call_args_list]
    tessl_eval_runs = [cmd for cmd in commands if cmd[1:3] == ["eval", "run"]]
    assert tessl_eval_runs == []
    assert not any(cmd[1:3] == ["project", "create"] for cmd in commands)
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "skipped"
    assert tessl_eval["reason"] == "local_only_default"
    assert tessl_eval["policy"]["no_registry_upload"] is True


def test_eval_only_review_report_uses_stable_tessl_staging_template(tmp_path: Path) -> None:
    report_path = evals._write_eval_only_review_report(tmp_path, "example-skill", "Skills/example-skill")
    report = json.loads(report_path.read_text(encoding="utf-8"))

    expected_staging_root = os.path.join(tempfile.gettempdir(), "ask-tessl-evals")
    policy = report["data"]["policy"]
    assert policy["tessl_eval_staging_root"].startswith(expected_staging_root)
    assert policy["tessl_eval_staging_root"].endswith("<skill-path>-<sha12>")
    assert report["data"]["review_mode_details"]["local_evals"]["tessl_evidence"].startswith(
        f"stages copied eval inputs under {expected_staging_root}"
    )


def test_tessl_live_private_sanitizer_preserves_staged_evidence_root() -> None:
    payload = {
        "staged_source": "/tmp/ask-tessl-evals/example-skill-abc123",
        "path": "/private/tmp/ask-tessl-evals/example-skill-abc123/scenarios/smoke/task.md",
        "user": "Jamie",
        "stdout": "contact user@example.com and inspect /Users/jamiecraik/private.txt",
    }

    sanitized = evals._sanitize_tessl_live_private_payload(payload)

    assert sanitized["staged_source"] == "/tmp/ask-tessl-evals/example-skill-abc123"
    assert sanitized["path"] == "/private/tmp/ask-tessl-evals/example-skill-abc123/scenarios/smoke/task.md"
    assert sanitized["user"] == "<redacted-actor>"
    assert sanitized["stdout"] == "contact <redacted-email> and inspect <user-path>"


def test_tessl_live_private_sanitizer_redacts_cross_platform_home_paths() -> None:
    payload = {
        "stdout": (
            "linux /home/runner/private.txt, root /root/private.txt, "
            "windows C:\\Users\\Jamie\\private.txt, and windows C:/users/Jamie/private.txt"
        ),
    }

    sanitized = evals._sanitize_tessl_live_private_payload(payload)

    assert sanitized["stdout"] == (
        "linux <user-path>, root <user-path>, windows <user-path>, and windows <user-path>"
    )


def test_macro_eval_report_blocks_on_malformed_existing_summary(tmp_path: Path) -> None:
    report_dir = tmp_path / "Infrastructure" / "artifacts" / "skills" / "demo-skill" / "run-1"
    report_dir.mkdir(parents=True)
    (report_dir / "summary.json").write_text("{ not valid json", encoding="utf-8")

    result = evals.macro_eval_report(tmp_path)

    assert result.status == "error"
    assert result.errors[0].code == "ERR_VALIDATION"
    assert result.data["artifact_errors"] == [{
        "path": "Infrastructure/artifacts/skills/demo-skill/run-1/summary.json",
        "message": "Could not parse JSON evidence artifact: " + str(report_dir / "summary.json"),
    }]


def test_macro_eval_report_blocks_on_non_object_existing_summary(tmp_path: Path) -> None:
    report_dir = tmp_path / "Infrastructure" / "artifacts" / "skills" / "demo-skill" / "run-1"
    report_dir.mkdir(parents=True)
    (report_dir / "summary.json").write_text("[]", encoding="utf-8")

    result = evals.macro_eval_report(tmp_path)

    assert result.status == "error"
    assert result.errors[0].code == "ERR_VALIDATION"
    assert result.data["artifact_errors"] == [{
        "path": "Infrastructure/artifacts/skills/demo-skill/run-1/summary.json",
        "message": "JSON evidence artifact must be an object: " + str(report_dir / "summary.json"),
    }]


def test_evals_run_default_does_not_stage_or_submit_tessl_source(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "assets").mkdir()
    (skill_root / "assets" / "example.png").write_bytes(b"png")

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
            "Skills/example-skill",
            mode="smoke",
            allow_tessl_project_save=True,
    )

    assert result.status == "success"
    commands = [call.args[0] for call in run.call_args_list]
    tessl_eval_runs = [cmd for cmd in commands if cmd[1:3] == ["eval", "run"]]
    assert tessl_eval_runs == []
    assert result.data["tessl_eval"]["status"] == "skipped"
    assert result.data["tessl_eval"]["reason"] == "local_only_default"


def test_tessl_live_private_dry_run_blocks_before_staging_without_security_receipt(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    readiness_path = tmp_path / ".harness" / "evidence" / "handoff" / skill_root.name / "eval-handoff-readiness.json"
    payload = json.loads(readiness_path.read_text(encoding="utf-8"))
    payload["lanes"] = [lane for lane in payload["lanes"] if lane["id"] != "security_risk_modes"]
    readiness_path.write_text(json.dumps(payload), encoding="utf-8")

    with mock.patch.object(evals, "_run_tessl_live_private_eval") as run_tessl:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
            tessl_live_dry_run=True,
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["tessl_dry_run_admission"]["ready_for_tessl_dry_run"] is False
    assert "lane_present" in {item["id"] for item in result.data["tessl_dry_run_admission"]["blockers"]}
    run_tessl.assert_not_called()


def test_evals_live_private_dry_run_stages_private_plugin_shape(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path, "skill-factory-router")
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "SKILL.md").write_text(
        '---\nname: example-skill\nmetadata:\n  version: "2.3.4"\n---\n'
        "# Example Skill\n\nSee references/runtime-boundary.md for runtime details.\n",
        encoding="utf-8",
    )
    (skill_root / "references" / "runtime-boundary.md").write_text(
        "Runtime boundary details.\n",
        encoding="utf-8",
    )
    (skill_root / "assets").mkdir()
    (skill_root / "assets" / "example.png").write_bytes(b"png")
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: smoke-example\n"
            "    unit: example private plugin proof\n"
            "    given: A private Tessl dry-run stages a skill package for assessment.\n"
            "    should: Preserve package shape and prove the skill-specific eval can be scored.\n"
            "    prompt: \"Do the example task.\"\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(example|task)\"\n"
            "      - type: expected_signal\n"
            "        value: Preserves package shape and proves the skill-specific eval can be scored.\n"
        ),
        encoding="utf-8",
    )

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
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
    assert run.call_count == 0
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "pass"
    assert tessl_eval["dry_run"] is True
    assert tessl_eval["live_private"] is True
    assert "ask-tessl-evals" in tessl_eval["staged_source"]
    assert tessl_eval["visibility"] == "private"
    assert tessl_eval["workspace"] == "jscraik"
    assert tessl_eval["policy"]["no_publish"] is True
    assert tessl_eval["policy"]["no_install"] is True
    assert tessl_eval["policy"]["no_registry_upload"] is True
    assert tessl_eval["policy"]["plugin_private_required"] is True
    feedback_loop = tessl_eval["policy"]["pre_tessl_feedback_loop"]
    assert feedback_loop["required_order"] == [
        "mechanical_validation",
        "security_risk_modes",
        "scenario_quality",
        "scorer_quality",
        "scorer_calibration",
        "deterministic_local_gates",
        "oss_local_internal_judge",
        "patch_oss_local_failures",
        "oss_cloud_internal_judge",
        "patch_oss_cloud_failures",
        "tessl_local_proof",
        "tessl_live_dry_run",
        "tessl_live_run",
        "patch_tessl_failures",
    ]
    assert [stage["profile"] for stage in feedback_loop["internal_judge_sequence"]] == [
        "oss-local",
        "oss-cloud",
    ]
    assert "rerun oss-local only for classified local skill regressions" in feedback_loop["failure_loop"]
    assert "oss-cloud" in feedback_loop["live_blocked_until"]
    assert tessl_eval["tessl_project_marker"].endswith("/tessl.json")
    assert tessl_eval["plugin_version"] == "2.3.4"

    staged_source = Path(tessl_eval["staged_source"])
    assert not (staged_source / "tile.json").exists()
    readme_text = (staged_source / "README.md").read_text(encoding="utf-8")
    assert "Registry presentation" in readme_text
    assert "should not be treated as agent context" in readme_text
    assert "GitHub Badge" in readme_text
    assert "tessl skill review --optimize" in readme_text
    assert "tessl review run" in readme_text
    plugin_manifest = json.loads((staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert plugin_manifest["name"] == "jscraik/example-skill"
    assert plugin_manifest["version"] == "2.3.4"
    assert plugin_manifest["private"] is True
    assert plugin_manifest["skills"] == "./skills/"
    assert (staged_source / "skills" / "example-skill" / "SKILL.md").is_file()
    assert (staged_source / "skills" / "example-skill" / "agents" / "openai.yaml").is_file()
    tesslignore = (staged_source / ".tesslignore").read_text(encoding="utf-8")
    assert "AGENTS.md" in tesslignore
    assert ".harness/" in tesslignore
    assert "skills/" not in {line.strip() for line in tesslignore.splitlines()}
    task_text = (staged_source / "evals" / "smoke-example" / "task.md").read_text(encoding="utf-8")
    assert task_text.startswith("Unit: example private plugin proof\n")
    assert task_text.endswith("Do the example task.\n")
    criteria = json.loads((staged_source / "evals" / "smoke-example" / "criteria.json").read_text(encoding="utf-8"))
    assert criteria["type"] == "weighted_checklist"
    descriptions = [item["description"] for item in criteria["checklist"]]
    assert "(?is)(example|task)" in descriptions
    assert "Preserves package shape and proves the skill-specific eval can be scored." in descriptions
    staged_skill = _assert_plugin_shaped_stage(staged_source, "example-skill")
    assert (staged_skill / "references" / "runtime-boundary.md").read_text(encoding="utf-8") == "Runtime boundary details.\n"
    assert (staged_skill / "assets" / "example.png").read_bytes() == b"png"
    assert (staged_source / "tessl.json").exists()
    assert not (staged_source / "secret-not-staged.txt").exists()


def test_tessl_projection_shape_rejects_root_rules_for_skill_references(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    rules_dir = staged_source / "rules"
    rules_dir.mkdir()
    (rules_dir / "support.md").write_text("# Wrong support location\n", encoding="utf-8")

    with pytest.raises(ValueError, match="use references"):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_projection_shape_rejects_manifest_skills_outside_staged_root(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    manifest_path = staged_source / ".tessl-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["skills"] = "./not-skills/"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match='skills must be "\\./skills/"'):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_projection_shape_rejects_manifest_skills_without_exact_staged_root(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    manifest_path = staged_source / ".tessl-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["skills"] = "skills/"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match='skills must be "\\./skills/"'):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_projection_shape_augments_existing_readme_with_registry_guidance(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "README.md").write_text("# Example Skill\n\nExisting project README.\n", encoding="utf-8")

    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )

    readme_text = (staged_source / "README.md").read_text(encoding="utf-8")
    assert "Existing project README." in readme_text
    assert "GitHub Badge" in readme_text
    assert "tessl skill review --optimize" in readme_text
    assert "tessl review run" in readme_text


def test_tessl_projection_shape_rejects_readme_without_badge_and_review_guidance(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    (staged_source / "README.md").write_text("# Example Skill\n\nRegistry presentation.\n", encoding="utf-8")

    with pytest.raises(ValueError, match="GitHub Badge"):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )


def test_tessl_projection_shape_rejects_incomplete_eval_case_files(tmp_path: Path) -> None:
    _write_example_skill(tmp_path)
    staged_source, _copied = evals._stage_tessl_live_private_source(
        tmp_path,
        "Skills/example-skill",
        "jscraik",
        temp_root=tmp_path / "stage",
    )
    (staged_source / "evals" / "smoke-example" / "criteria.json").unlink()

    with pytest.raises(ValueError, match="criteria.json"):
        evals._validate_tessl_projection_shape(
            staged_source,
            skill_name="example-skill",
            workspace="jscraik",
            project_slug="example-skill",
            require_evals=True,
        )

__all__ = [name for name in globals() if not name.startswith("__")]
