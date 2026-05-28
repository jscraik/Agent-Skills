from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import evals  # noqa: E402
from ask.skill_review_dashboard import _parse_plugin_eval, render_skill_review_dashboard  # noqa: E402


def test_smoke_evals_use_codex_spark_and_fast_profile_without_reasoning_level(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "gpt-5.3-codex-spark"
    assert "--profile" in cmd
    assert cmd[cmd.index("--profile") + 1] == "fast"
    assert result.data["profile_contract"]["codex_profile"] == "fast"
    assert result.data["profile_contract"]["codex_profile_config"] == "[profiles.fast]"
    assert result.data["profile_contract"]["tessl_policy"]["tessl_project_marker"] == "tessl.json"
    assert "--reasoning" not in cmd
    assert "--reasoning-effort" not in cmd
    assert "--codex-arg" not in cmd
    assert "--ignore-user-config" not in cmd


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


def test_tessl_criteria_recovers_compact_flow_map_acceptance() -> None:
    case = {
        "id": "compact-yaml",
        "prompt": "Create a package plan.",
        "expected_artifact": "A package plan naming SKILL.md and validation.",
        "acceptance": [
            {'{type': 'regex, value: "(?is)(SKILL\\.md|references/contract\\.yaml)"}'},
            {"{type": "skill_selected, expected_skill: skillify}"},
        ],
    }

    criteria = evals._tessl_criteria_from_case(case)

    assert criteria["checklist"][0]["name"] == "regex-1"
    assert "SKILL\\.md" in criteria["checklist"][0]["description"]
    assert criteria["checklist"][1]["name"] == "skill_selected-2"
    assert criteria["checklist"][1]["description"] == "skillify"


def test_tessl_compat_parser_keeps_inline_acceptance_detail() -> None:
    cases = evals._parse_tessl_eval_cases_compat(
        "cases:\n"
        "  - id: inline-acceptance\n"
        "    prompt: \"Handle the workflow.\"\n"
        "    acceptance: [{type: regex, value: \"(?i)(category|destination|blocked)\"}]\n"
    )

    assert cases[0]["acceptance"] == [
        {"type": "regex", "value": "(?i)(category|destination|blocked)"}
    ]
    criteria = evals._tessl_criteria_from_case(cases[0])
    assert criteria["checklist"][0]["name"] == "regex-1"
    assert criteria["checklist"][0]["description"] == "(?i)(category|destination|blocked)"


def test_benchmark_portfolio_exposes_validation_command(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="Benchmark OK\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.benchmark_portfolio(tmp_path)

    assert result.status == "success"
    assert result.data["validation_commands"] == ["./bin/ask evals benchmark --json --robot"]


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
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            runner="discovery-smoke",
            skip_tessl=True,
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
            skip_tessl=True,
        )

    assert result.status == "success"
    assert result.data["requested_path"] == ".agents/skills/evals-router"
    assert result.data["resolved_skill_path"] == "Skills/agent-ops/evals-router"
    assert run.call_args.args[0][2] == "Skills/agent-ops/evals-router"


def _write_example_skill(tmp_path: Path) -> Path:
    skill_root = tmp_path / "Skills" / "example-skill"
    references = skill_root / "references"
    references.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: example-skill\nmetadata:\n  version: "1.2.3"\n---\n# Example Skill\n',
        encoding="utf-8",
    )
    (references / "evals.yaml").write_text(
        'cases:\n  - id: smoke-example\n    prompt: "Do the example task."\n',
        encoding="utf-8",
    )
    (references / "contract.yaml").write_text("version: 1\n", encoding="utf-8")
    (skill_root / "secret-not-staged.txt").write_text("do not copy\n", encoding="utf-8")
    return skill_root


def test_evals_run_native_tessl_without_project_save_approval_flag(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
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
    assert run.call_count == 2
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "pass"
    assert "ask-tessl-evals" in tessl_eval["staged_source"]
    assert tessl_eval["staging_policy"] == "stable_tmp_evidence"
    assert tessl_eval["tessl_project_marker"].endswith("/tessl.json")
    expected_staging_root = os.path.join(tempfile.gettempdir(), "ask-tessl-evals")
    assert tessl_eval["policy"]["stable_staging_root"].startswith(expected_staging_root)
    assert tessl_eval["policy"]["no_registry_upload"] is True
    assert tessl_eval["policy"]["network_permission_required_by_repo"] is False


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


def test_evals_run_native_tessl_by_default_with_temp_staged_source(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "assets").mkdir()
    (skill_root / "assets" / "example.png").write_bytes(b"png")

    def fake_run(cmd: list[str], **kwargs: object) -> mock.Mock:
        if cmd[1:4] != ["eval", "run", "--json"]:
            return completed

        staged_source = Path(cmd[4])
        assert cmd[:4] == ["/usr/local/bin/tessl", "eval", "run", "--json"]
        assert staged_source != skill_root
        assert staged_source.exists()
        assert "ask-tessl-evals" in str(staged_source)
        assert staged_source.is_relative_to(Path(str(kwargs["cwd"])))
        assert "HOME" in kwargs["env"]
        assert "ask-tessl-evals" not in str(kwargs["env"]["HOME"])
        assert kwargs["env"]["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] == "0"
        assert (staged_source / "SKILL.md").read_text(encoding="utf-8") == (
            '---\nname: example-skill\nmetadata:\n  version: "1.2.3"\n---\n# Example Skill\n'
        )
        assert (staged_source / "references" / "evals.yaml").exists()
        assert (staged_source / "references" / "contract.yaml").exists()
        assert (staged_source / "assets" / "example.png").read_bytes() == b"png"
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
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            allow_tessl_project_save=True,
        )

    assert result.status == "success"
    assert run.call_count == 2
    tessl_cmd = run.call_args_list[-1].args[0]
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
        "assets/example.png",
        "scenarios/smoke-example/task.md",
        "tessl.json",
    ]
    assert result.data["tessl_eval"]["policy"]["no_registry_upload"] is True
    assert result.data["tessl_eval"]["policy"]["temp_staged_project_input_only"] is True
    assert result.data["tessl_eval"]["policy"]["network_permission_required_by_repo"] is False
    assert result.data["tessl_eval"]["policy"]["project_save_default"] == "compatibility_flag_not_required"


def test_evals_live_private_dry_run_stages_private_tile_shape(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
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
            "    prompt: \"Do the example task.\"\n"
            "    acceptance:\n"
            "      - type: expected_signal\n"
            "        value: Uses the example skill.\n"
        ),
        encoding="utf-8",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
            tessl_live_dry_run=True,
        )

    assert result.status == "success"
    assert run.call_count == 1
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "pass"
    assert tessl_eval["dry_run"] is True
    assert tessl_eval["live_private"] is True
    assert "ask-tessl-live" in tessl_eval["staged_source"]
    assert tessl_eval["visibility"] == "private"
    assert tessl_eval["workspace"] == "jscraik"
    assert tessl_eval["policy"]["no_publish"] is True
    assert tessl_eval["policy"]["no_install"] is True
    assert tessl_eval["policy"]["no_registry_upload"] is True
    assert tessl_eval["policy"]["tile_private_required"] is True
    assert tessl_eval["tessl_project_marker"].endswith("/tessl.json")
    assert tessl_eval["tile_version"] == "2.3.4"

    staged_source = Path(tessl_eval["staged_source"])
    tile_manifest = json.loads((staged_source / "tile.json").read_text(encoding="utf-8"))
    assert tile_manifest["name"] == "jscraik/example-skill"
    assert tile_manifest["version"] == "2.3.4"
    assert tile_manifest["private"] is True
    assert tile_manifest["skills"]["example-skill"]["path"] == "SKILL.md"
    assert (staged_source / "evals" / "smoke-example" / "task.md").read_text(encoding="utf-8") == (
        "Do the example task.\n"
    )
    criteria = json.loads((staged_source / "evals" / "smoke-example" / "criteria.json").read_text(encoding="utf-8"))
    assert criteria["type"] == "weighted_checklist"
    assert criteria["checklist"][0]["description"] == "Uses the example skill."
    assert (staged_source / "references" / "runtime-boundary.md").read_text(encoding="utf-8") == (
        "Runtime boundary details.\n"
    )
    assert (staged_source / "assets" / "example.png").read_bytes() == b"png"
    assert (staged_source / "tessl.json").exists()
    assert not (staged_source / "secret-not-staged.txt").exists()


def test_evals_live_private_uses_plugin_project_identity(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    skill_root = tmp_path / "Plugins" / "skill-factory" / "skills" / "code_quality_review" / "skill-builder"
    (skill_root / "references").mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: skill-builder\nmetadata:\n  version: "1.2.3"\n---\n'
        "# Skill Builder\n\nBuild and improve skills.\n",
        encoding="utf-8",
    )
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: plugin-scope\n"
            "    prompt: \"Improve the plugin-owned skill.\"\n"
            "    acceptance:\n"
            "      - type: expected_signal\n"
            "        value: Preserves plugin project identity.\n"
        ),
        encoding="utf-8",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="skills-sdk",
            tessl_live_dry_run=True,
        )

    assert result.status == "success"
    tessl_eval = result.data["tessl_eval"]
    staged_source = Path(tessl_eval["staged_source"])
    tile_manifest = json.loads((staged_source / "tile.json").read_text(encoding="utf-8"))
    project_marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
    assert tile_manifest["name"] == "skills-sdk/skill-factory"
    assert tile_manifest["skills"]["skill-builder"]["path"] == "SKILL.md"
    assert project_marker["name"] == "skills-sdk/skill-factory"


def test_evals_run_uses_plugin_project_identity_when_workspace_is_set(tmp_path: Path) -> None:
    skill_root = tmp_path / "Plugins" / "skill-factory" / "skills" / "code_quality_review" / "skill-builder"
    (skill_root / "references").mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: skill-builder\nmetadata:\n  version: "1.2.3"\n---\n# Skill Builder\n',
        encoding="utf-8",
    )
    (skill_root / "references" / "evals.yaml").write_text(
        'cases:\n  - id: plugin-scope\n    prompt: "Improve the plugin skill."\n',
        encoding="utf-8",
    )

    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    def fake_run(cmd: list[str], **kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"]:
            staged_source = Path(str(kwargs["cwd"]))
            marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
            assert marker["name"] == "skills-sdk/skill-factory"
            return mock.Mock(returncode=0, stdout="{}", stderr="", args=cmd)
        if cmd[1:4] == ["eval", "run", "--json"]:
            staged_source = Path(cmd[4])
            marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
            assert marker["name"] == "skills-sdk/skill-factory"
            return mock.Mock(returncode=0, stdout="{}", stderr="", args=cmd)
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run),
    ):
        result = evals.run_evals(
            tmp_path,
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            mode="smoke",
            tessl_workspace="skills-sdk",
        )

    tessl_eval = result.data["tessl_eval"]
    assert result.status == "success"
    assert tessl_eval["project_identity"]["owner_type"] == "plugin"
    assert tessl_eval["project_identity"]["project"] == "skill-factory"
    assert tessl_eval["project_link"]["action"] == "already_linked"


def test_tessl_project_link_creates_after_missing_existing_project(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        if cmd[1:4] == ["project", "repair", "--json"]:
            return mock.Mock(returncode=1, stdout='{"status":"needs_repair"}', stderr="", args=cmd)
        if "--relink" in cmd:
            return mock.Mock(returncode=1, stdout="", stderr="Project not found", args=cmd)
        if cmd[1:3] == ["project", "create"]:
            return mock.Mock(returncode=0, stdout="created\n", stderr="", args=cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "plugin",
                "workspace": "skills-sdk",
                "project": "skill-factory",
                "name": "skills-sdk/skill-factory",
            },
        )

    assert link["status"] == "pass"
    assert link["action"] == "created_project"
    assert calls[-1] == ["/usr/local/bin/tessl", "project", "create", "skill-factory", "--workspace", "skills-sdk"]


def test_tessl_project_link_updates_source_after_relink(tmp_path: Path) -> None:
    staged_root = tmp_path / "staged"
    staged_root.mkdir()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        calls.append(cmd)
        if cmd[1:4] == ["project", "repair", "--json"]:
            return mock.Mock(returncode=1, stdout='{"status":"needs_repair","allowedActions":["relink","update_source"]}', stderr="", args=cmd)
        if "--relink" in cmd:
            return mock.Mock(returncode=0, stdout='{"status":"relinked"}', stderr="", args=cmd)
        if "--update-source" in cmd:
            return mock.Mock(returncode=0, stdout='{"status":"updated"}', stderr="", args=cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    with mock.patch.object(evals.subprocess, "run", side_effect=fake_run):
        link = evals._ensure_tessl_project_link(
            "/usr/local/bin/tessl",
            staged_root,
            {
                "owner_type": "plugin",
                "workspace": "skills-sdk",
                "project": "skill-factory",
                "name": "skills-sdk/skill-factory",
            },
        )

    assert link["status"] == "pass"
    assert link["action"] == "relinked_existing_project_updated_source"
    assert calls[-1] == ["/usr/local/bin/tessl", "project", "repair", "--update-source", "--yes", "--json"]


def test_evals_live_private_requires_workspace(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    _write_example_skill(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_live_dry_run=True,
        )

    assert result.status == "error"
    assert run.call_count == 1
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "--tessl-workspace" in tessl_eval["blocker"]


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


def test_evals_live_private_invokes_tessl_with_workspace_and_tile_manifest(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(returncode=0, stdout='{"id":"019e6ac8-08eb-75fb-8fbb-e2346517f82d"}', stderr="")
    completed_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "scenarios": [
                        {
                            "solutions": [
                                {
                                    "variant": "baseline",
                                    "assessmentResults": [{"score": 0, "max_score": 1}],
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
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        if cmd[1:3] == ["eval", "view"]:
            return completed_view
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run) as run,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            tessl_live_private=True,
            tessl_workspace="jscraik",
        )

    assert result.status == "success"
    assert run.call_count == 4
    tessl_cmd = run.call_args_list[-2].args[0]
    assert tessl_cmd[:4] == ["/usr/local/bin/tessl", "eval", "run", "--json"]
    assert tessl_cmd[4].endswith("/tile.json")
    view_cmd = run.call_args_list[-1].args[0]
    assert view_cmd == [
        "/usr/local/bin/tessl",
        "eval",
        "view",
        "--json",
        "019e6ac8-08eb-75fb-8fbb-e2346517f82d",
    ]
    staged_manifest = json.loads(Path(tessl_cmd[4]).read_text(encoding="utf-8"))
    assert staged_manifest["name"] == "jscraik/example-skill"
    assert staged_manifest["private"] is True
    assert "publish" not in tessl_cmd
    assert "install" not in tessl_cmd
    assert "registry" not in tessl_cmd
    assert result.data["tessl_eval"]["policy"]["command_shape"] == (
        "tessl eval run --json <staged-tile-json>"
    )
    assert result.data["tessl_eval"]["live_result_summary"]["meets_min_score"] is True
    assert result.data["tessl_eval"]["live_result_summary"]["beats_baseline"] is True


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
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        if cmd[1:3] == ["eval", "view"]:
            return completed_view
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
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
                            {"variant": "baseline", "assessmentResults": [{"score": 1, "max_score": 1}]},
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
        if cmd[1:3] == ["eval", "run"]:
            return completed_eval
        if cmd[1:3] == ["eval", "view"]:
            view_calls += 1
            return pending_view if view_calls == 1 else completed_view
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
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
        workspace="skills-sdk",
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
    assert not (target_tile / "evals").exists()
    assert (tool_project / "tessl.json").is_file()
    assert Path(result.data["scenario_generation_brief"]).is_file()
    manifest = json.loads((target_tile / "tile.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "skills-sdk/example-skill"
    assert manifest["version"] == "1.2.3"
    assert manifest["private"] is True
    assert result.data["policy"]["no_repo_root_install"] is True
    assert result.data["policy"]["allowed_install_scope"] == "temp tool project only"


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
        workspace="skills-sdk",
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
        workspace="skills-sdk",
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

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
    ):
        result = evals.prepare_tessl_scenario_generation(
            tmp_path,
            "Skills/example-skill",
            workspace="skills-sdk",
        )

    assert result.status == "success"
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
    assert result.data["generated_output"].endswith("/target-tile/evals")


def test_evals_stage_folded_yaml_prompts_for_tessl(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: folded-prompt\n"
            "    prompt: >-\n"
            "      Investigate the target workflow\n"
            "      and preserve the whole prompt.\n"
        ),
        encoding="utf-8",
    )
    staged_root = tmp_path / "staged"

    copied = evals._write_tessl_scenarios_from_evals(skill_root, staged_root)

    assert copied == ["scenarios/folded-prompt/task.md"]
    assert (
        staged_root / "scenarios" / "folded-prompt" / "task.md"
    ).read_text(encoding="utf-8") == "Investigate the target workflow and preserve the whole prompt.\n"


def test_evals_fallback_parser_preserves_literal_block_relative_indent(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: literal-prompt\n"
            "    prompt: |\n"
            "        def example():\n"
            "            return 1\n"
            "      done\n"
        ),
        encoding="utf-8",
    )
    staged_root = tmp_path / "staged"

    copied = evals._write_tessl_scenarios_from_evals(skill_root, staged_root)

    assert copied == ["scenarios/literal-prompt/task.md"]
    assert (
        staged_root / "scenarios" / "literal-prompt" / "task.md"
    ).read_text(encoding="utf-8") == "  def example():\n      return 1\ndone\n"


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
        mock.patch.object(evals.subprocess, "run", return_value=completed),
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            allow_tessl_project_save=True,
        )

    tessl_eval = result.data["tessl_eval"]
    assert result.status == "error"
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "Failed to parse Tessl eval cases" in tessl_eval["blocker"]


def test_evals_skip_tessl_escape_hatch(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    assert run.call_count == 1
    assert result.data["tessl_eval"]["status"] == "skipped"


def test_evals_classify_missing_tessl_cli_as_blocked_runtime(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    _write_example_skill(tmp_path)

    with (
        mock.patch.object(evals.shutil, "which", return_value=None),
        mock.patch.object(evals.subprocess, "run", return_value=completed),
    ):
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke")

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_runtime"
    assert result.data["eval_status"] == "blocked_runtime"
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_blocked",
    ]
    assert result.data["lifecycle_event"]["outcome"]["blocker_classes"] == ["blocked_runtime"]


def test_evals_preserve_primary_failure_when_tessl_also_fails(tmp_path: Path) -> None:
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
    assert result.data["tessl_eval"]["status"] == "blocked"
    assert result.data["tessl_eval_status"] == "blocked_runtime"
    assert result.data["tessl_blocker_class"] == "blocked_runtime"
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_completed",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "fail"
    assert result.data["lifecycle_event"]["outcome"]["blocker_classes"] == []


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
        result = evals.run_evals(
            tmp_path,
            "Skills/example-skill",
            mode="smoke",
            allow_tessl_project_save=True,
        )

    assert result.status == "error"
    tessl_eval = result.data["tessl_eval"]
    assert tessl_eval["status"] == "blocked"
    assert tessl_eval["blocker_class"] == "blocked_validation"
    assert "project/workspace is linked" in tessl_eval["blocker"]
    assert "tessl.json" in tessl_eval["staged_files"]
    assert [event["event_type"] for event in result.data["lifecycle_events"]] == [
        "eval_started",
        "eval_blocked",
    ]
    assert result.data["lifecycle_event"]["outcome"]["status"] == "blocked_validation"
    assert result.data["lifecycle_event"]["outcome"]["blocker_classes"] == ["blocked_validation"]


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
    skill = tmp_path / "Skills" / "agent-ops" / "autoresearch"
    skill.mkdir(parents=True)
    absolute_report = tmp_path / "Infrastructure" / "artifacts" / "skills" / "scorecard.json"
    completed = mock.Mock(
        returncode=0,
        stdout=f"Scorecard: {absolute_report}\n",
        stderr=f"checked {skill}\n",
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

    assert result.status == "success"
    assert str(tmp_path) not in result.data["raw_output"]
    assert str(tmp_path) not in result.data["raw_error"]
    assert "Infrastructure/artifacts/skills/scorecard.json" in result.data["raw_output"]


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
    completed = mock.Mock(returncode=0, stdout="Skill evals: example-skill\n", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            dashboard=False,
            skip_tessl=True,
        )

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
    cmd = run.call_args.args[0]
    assert cmd[1] == "Plugins/skill-factory/scripts/skill-builder/build_skill_eval_dashboard.py"
