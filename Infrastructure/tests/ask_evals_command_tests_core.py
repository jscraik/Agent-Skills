from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import evals  # noqa: E402
from ask.commands import sdk_eval  # noqa: E402
from ask.skills_sdk.handoff_readiness import build_candidate_identity  # noqa: E402
from ask.skill_review_dashboard import _parse_plugin_eval, _render_eval_cases, render_skill_review_dashboard  # noqa: E402


EXAMPLE_TESSL_EVAL_YAML = """cases:
  - id: smoke-example
    unit: example skill behavioural proof
    given: A user needs the example skill to guide a repository handoff.
    should: Produce a concrete handoff that separates evidence from readiness claims.
    prompt: "Do the example task."
    acceptance:
      - type: regex
        value: "(?is)(example|task)"
      - type: expected_signal
        value: Separates evidence from readiness claims while completing the example task.
      - type: text_field_equals
        field: status
        value: blocked
"""


def _completed_eval_with_report(tmp_path: Path, skill_name: str = "example-skill") -> mock.Mock:
    report_dir = tmp_path / "Infrastructure" / "artifacts" / "skills" / skill_name / "run-1"
    report_dir.mkdir(parents=True, exist_ok=True)
    case_dir = report_dir / "01-happy-path"
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "result.json").write_text(
        json.dumps({"id": "happy-path", "status": "pass"}),
        encoding="utf-8",
    )
    (report_dir / "summary.json").write_text(
        json.dumps({
            "cases": [
                {
                    "id": "happy-path",
                    "status": "pass",
                    "dir": f"Infrastructure/artifacts/skills/{skill_name}/run-1/01-happy-path",
                }
            ]
        }),
        encoding="utf-8",
    )
    return mock.Mock(
        returncode=0,
        stdout=f"Skill evals: {skill_name}\nReports: {report_dir}\nRESULT: PASS\n",
        stderr="",
    )


def _assert_plugin_shaped_stage(staged_source: Path, skill_name: str) -> Path:
    staged_skill = staged_source / "skills" / skill_name
    assert not (staged_source / "references").exists()
    assert not (staged_source / "assets").exists()
    assert not (staged_source / "SKILL.md").exists()
    return staged_skill


def test_tessl_run_id_parser_handles_prefixed_json() -> None:
    payload = 'tessl output\n{"id": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}'

    assert evals._parse_json_object_from_text(payload) == {
        "id": "019e7ab3-fda5-7071-8e47-9ea75386d53b"
    }
    assert evals._extract_tessl_eval_run_id(payload) == "019e7ab3-fda5-7071-8e47-9ea75386d53b"


def test_shard_aggregate_dispatch_selects_preview_or_write_artifact_mode() -> None:
    args = argparse.Namespace(
        target="Skills/agent-ops/demo",
        scenario_set="demo-release-5-v1",
        receipts=["Infrastructure/artifacts/skills/demo/run/sdk-eval-run-receipt.json"],
        codex_profile="oss-local",
        preview=False,
    )
    with mock.patch.object(sdk_eval.skills_commands, "skills_sdk_eval_shard_aggregate", return_value=mock.Mock()) as write_aggregate, mock.patch.object(
        sdk_eval.skills_commands,
        "skills_sdk_eval_shard_aggregate_preview",
        return_value=mock.Mock(),
    ) as preview_aggregate:
        sdk_eval._dispatch_shard_aggregate(REPO_ROOT, args)
        args.preview = True
        sdk_eval._dispatch_shard_aggregate(REPO_ROOT, args)

    expected_kwargs = {
        "target": args.target,
        "scenario_set": args.scenario_set,
        "receipts": args.receipts,
        "codex_profile": args.codex_profile,
    }
    write_aggregate.assert_called_once_with(REPO_ROOT, **expected_kwargs)
    preview_aggregate.assert_called_once_with(REPO_ROOT, **expected_kwargs)


def test_internal_skill_eval_subprocess_runs_in_isolated_session() -> None:
    completed = subprocess.CompletedProcess(
        args=["run_skill_evals.py"],
        returncode=2,
        stdout="",
        stderr="runner terminated",
    )

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run_mock:
        result = evals.run_evals(
            REPO_ROOT,
            "Skills/agent-ops/technical-writer",
            mode="release",
            runner="codex",
            dashboard=False,
            skip_tessl=True,
            codex_profile="oss-local",
            cases=["smoke-discovery", "happy-path"],
            timeout_seconds=90,
        )

    assert result.status == "error"
    assert run_mock.call_args.kwargs["start_new_session"] is True


def test_codex_release_profile_timeout_uses_selected_case_budget(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run_mock:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="release",
            runner="codex",
            dashboard=False,
            skip_tessl=True,
            codex_profile="oss-local",
            cases=["smoke-discovery", "happy-path"],
            timeout_seconds=90,
        )

    assert result.status == "success"
    assert run_mock.call_args.kwargs["timeout"] == 240


def test_codex_release_profile_timeout_caps_scaled_case_budget(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run_mock:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="release",
            runner="codex",
            dashboard=False,
            skip_tessl=True,
            codex_profile="codex-fast",
            cases=[f"case-{index}" for index in range(40)],
            timeout_seconds=600,
        )

    assert result.status == "success"
    assert run_mock.call_args.kwargs["timeout"] == evals.RELEASE_EVAL_TIMEOUT_SECONDS


def test_codex_smoke_without_case_filter_preserves_suite_timeout_floor(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run_mock:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            runner="codex",
            dashboard=False,
            skip_tessl=True,
            timeout_seconds=90,
        )

    assert result.status == "success"
    assert run_mock.call_args.kwargs["timeout"] == evals.SMOKE_EVAL_TIMEOUT_SECONDS


def test_codex_oss_local_blocks_unfiltered_batch(tmp_path: Path) -> None:
    with mock.patch.object(evals.subprocess, "run") as run_mock:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            runner="codex",
            dashboard=False,
            skip_tessl=True,
            codex_profile="oss-local",
        )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["qwen_oss_local_smoke_batch"]["actual"] == "no --case filter supplied"
    assert "no --case filter supplied" in result.data["raw_error"]
    run_mock.assert_not_called()


def test_eval_blocker_classifies_no_matching_eval_cases_as_validation() -> None:
    blocker = evals._classify_eval_blocker(
        raw_output="",
        raw_error="ERROR: No eval cases matched the selected filters and eval mode 'smoke'.",
    )

    assert blocker == "blocked_validation"


def test_eval_blocker_classifies_smoke_only_case_live_runner_skip_as_validation() -> None:
    blocker = evals._classify_eval_blocker(
        raw_output="",
        raw_error=(
            "ERROR: selected case filters matched only smoke-only discovery contract cases, "
            "which live/model runners skip."
        ),
    )

    assert blocker == "blocked_validation"


def test_eval_closeout_blocks_no_case_evidence_from_filter_error(tmp_path: Path) -> None:
    raw_error = "ERROR: No eval cases matched the selected filters and eval mode 'smoke'."
    blocker = evals._classify_eval_blocker(raw_output="", raw_error=raw_error)

    closeout = evals._write_eval_closeout(
        tmp_path,
        skill_path="Skills/agent-ops/improve-agent-native",
        mode="smoke",
        runner="codex",
        raw_output="",
        raw_error=raw_error,
        eval_status="fail",
        blocker_class=blocker,
        started_at=0,
        timeout_seconds=120,
    )

    assert closeout["status"] == "blocked"
    assert closeout["blocker_class"] == "blocked_validation"
    assert closeout["cases"] == []
    assert closeout["case_evidence_present"] is False
    assert closeout["mutation_allowed"] is False
    assert closeout["registry_update_allowed"] is False
    assert closeout["closeout_validation"]["status"] == "pass"


def test_tessl_json_parser_skips_bracketed_log_prefix_and_trailing_text() -> None:
    assert evals._parse_json_value_from_text(
        '[info] preparing eval\n[{"evalRunId": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}]'
    ) == [{"evalRunId": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}]
    assert evals._parse_json_value_from_text(
        '{"id": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}\ntrailing log text'
    ) == {"id": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}


def test_tessl_run_id_parser_handles_alternate_json_keys() -> None:
    assert (
        evals._extract_tessl_eval_run_id('{"evalRunId": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}')
        == "019e7ab3-fda5-7071-8e47-9ea75386d53b"
    )
    assert (
        evals._extract_tessl_eval_run_id(
            '{"data": {"runId": "019e7ab3-fda5-7071-8e47-9ea75386d53b"}}'
        )
        == "019e7ab3-fda5-7071-8e47-9ea75386d53b"
    )


def test_tessl_run_id_parser_falls_back_to_plain_text_uuid() -> None:
    assert (
        evals._extract_tessl_eval_run_id(
            "created run 019e7ab3-fda5-7071-8e47-9ea75386d53b; view it after completion"
        )
        == "019e7ab3-fda5-7071-8e47-9ea75386d53b"
    )


def test_tessl_eval_view_incomplete_when_assessment_results_empty() -> None:
    payload = {
        "data": {
            "attributes": {
                "scenarios": [
                    {
                        "solutions": [
                            {"variant": "baseline", "assessmentResults": []},
                            {"variant": "usage-spec", "assessmentResults": [{"score": 1, "max_score": 1}]},
                        ]
                    }
                ]
            }
        }
    }

    assert evals._tessl_eval_view_has_complete_scores(payload) is False


def test_tessl_live_summary_flags_missing_observable_output_regressions() -> None:
    payload = {
        "data": {
            "attributes": {
                "scenarios": [
                    {
                        "id": "scenario-1",
                        "path": "interface-contract-migration",
                        "shortDescription": "Unit: public interface",
                        "solutions": [
                            {
                                "variant": "baseline",
                                "assessmentResults": [
                                    {
                                        "name": "expected_signal-1",
                                        "score": 1,
                                        "max_score": 1,
                                        "reasoning": "The response created a migration decision artifact.",
                                    }
                                ],
                            },
                            {
                                "variant": "usage-spec",
                                "assessmentResults": [
                                    {
                                        "name": "expected_signal-1",
                                        "score": 0,
                                        "max_score": 1,
                                        "reasoning": (
                                            "No agent response artifact is present in the solution; "
                                            "only the fixture/skill package files are included."
                                        ),
                                    }
                                ],
                            },
                        ],
                    }
                ]
            }
        }
    }

    summary = evals._summarize_tessl_live_eval_view(payload)

    assert summary["score"] == 0
    assert summary["baseline_score"] == 1
    assert summary["regressions_count"] == 1
    assert summary["evidence_shape_regressions_count"] == 1
    regression = summary["evidence_shape_regressions"][0]
    assert regression["path"] == "interface-contract-migration"
    assert regression["usage_missing_observable_output"] is True
    assert regression["baseline_missing_observable_output"] is False
    assert regression["usage_failed_criteria"][0]["name"] == "expected_signal-1"


def test_smoke_evals_use_codex_spark_and_fast_profile_without_reasoning_level(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with (
        mock.patch.object(evals, "_pyyaml_eval_python_command", return_value=["managed-python"]),
        mock.patch.object(evals.subprocess, "run", return_value=completed) as run,
    ):
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert cmd[:2] == ["managed-python", "Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py"]
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "gpt-5.3-codex-spark"
    assert "--profile" in cmd
    assert cmd[cmd.index("--profile") + 1] == "fast"
    assert "--sandbox" in cmd
    assert cmd[cmd.index("--sandbox") + 1] == "workspace-write"
    assert result.data["profile_contract"]["codex_profile"] == "fast"
    assert result.data["profile_contract"]["codex_profile_config"] == "[profiles.fast]"
    assert result.data["profile_contract"]["codex_exec_invoked"] is True
    assert result.data["profile_contract"]["codex_exec_command_shape"][:4] == ["codex", "exec", "--profile", "fast"]
    assert result.data["profile_contract"]["tessl_policy"]["tessl_project_marker"] == "tessl.json"
    assert "--reasoning" not in cmd
    assert "--reasoning-effort" not in cmd
    assert "--codex-arg" not in cmd
    assert "--ignore-user-config" not in cmd
    assert run.call_args.kwargs["env"]["PYTHONDONTWRITEBYTECODE"] == "1"


def test_evals_pyyaml_runner_bypasses_mise_project_resolution(monkeypatch) -> None:
    monkeypatch.delenv("PYTHON_BIN", raising=False)
    monkeypatch.setattr(evals, "sys", mock.Mock(executable="/system/python"))
    monkeypatch.setattr(evals.Path, "home", staticmethod(lambda: Path("/missing-home")))
    monkeypatch.setattr(evals.shutil, "which", lambda name: "/usr/bin/python3" if name == "python3" else None)
    supports = mock.Mock(return_value=False)
    monkeypatch.setattr(evals, "_python_command_supports_packages", supports)

    command = evals._pyyaml_eval_python_command()

    assert command == ["uv", "run", "--no-project", "--with", "PyYAML", "python"]
    assert command[0] != "mise"
    assert "--no-project" in command
    assert supports.call_args_list == [
        mock.call(["/system/python"], ["pyyaml"]),
        mock.call(["/usr/bin/python3"], ["pyyaml"]),
    ]


def test_smoke_evals_accept_model_override_for_quota_recovery(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

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


def test_smoke_evals_accept_profile_override_for_oss_cloud(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="smoke",
            skip_tessl=True,
            codex_profile="oss-cloud",
        )

    assert result.status == "success"
    assert result.data["profile_contract"]["codex_profile"] == "oss-cloud"
    assert result.data["profile_contract"]["codex_profile_config"] == "[profiles.oss-cloud]"
    assert result.data["profile_contract"]["codex_profile_source"] == "argument"
    cmd = run.call_args.args[0]
    assert "--profile" in cmd
    assert cmd[cmd.index("--profile") + 1] == "oss-cloud"
    assert "--sandbox" in cmd
    assert cmd[cmd.index("--sandbox") + 1] == "read-only"
    assert "--model" not in cmd
    assert result.data["profile_contract"]["codex_exec_invoked"] is True
    assert result.data["profile_contract"]["codex_profile_proof_lane"] == "oss-cloud"


def test_release_evals_accept_profile_override_for_oss_local_proof(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(
            tmp_path,
            "Plugins/example-skill",
            mode="release",
            skip_tessl=True,
            codex_profile="oss-local",
            cases=["happy-path"],
        )

    assert result.status == "success"
    assert result.data["profile_contract"]["codex_profile"] == "oss-local"
    assert result.data["profile_contract"]["codex_exec_invoked"] is True
    assert result.data["profile_contract"]["codex_exec_command_shape"][:4] == ["codex", "exec", "--profile", "oss-local"]
    cmd = run.call_args.args[0]
    assert "--profile" in cmd
    assert cmd[cmd.index("--profile") + 1] == "oss-local"
    assert "--sandbox" in cmd
    assert cmd[cmd.index("--sandbox") + 1] == "read-only"
    assert "--model" not in cmd


def test_smoke_evals_pass_case_filters_to_skill_runner(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

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
    completed = _completed_eval_with_report(tmp_path)

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
    completed = _completed_eval_with_report(tmp_path)

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


def test_tessl_criteria_describes_semantic_requirements() -> None:
    case = {
        "id": "semantic-boundary",
        "expected_artifact": "SKILL.md",
        "acceptance": [
            {
                "type": "semantic_requirements",
                "requirements": [
                    {
                        "id": "injection_is_untrusted",
                        "all_of": ["comment"],
                        "any_of": ["untrusted text", "not authoritative"],
                    }
                ],
            }
        ],
    }

    criteria = evals._tessl_criteria_from_case(case)

    description = criteria["checklist"][0]["description"]
    assert description.startswith("semantic_requirements:")
    assert "injection_is_untrusted" in description
    assert "all_of=comment" in description
    assert "any_of=untrusted text, not authoritative" in description
    assert description != "SKILL.md"


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


def test_tessl_compat_parser_keeps_inline_acceptance_regex_quantifier_braces() -> None:
    cases = evals._parse_tessl_eval_cases_compat(
        "cases:\n"
        "  - id: inline-regex-braces\n"
        "    prompt: \"Handle repeated evidence.\"\n"
        "    acceptance: [{type: regex, value: \"(?i)item{2,}\"}]\n"
    )

    assert cases[0]["acceptance"] == [{"type": "regex", "value": "(?i)item{2,}"}]
    criteria = evals._tessl_criteria_from_case(cases[0])
    assert criteria["checklist"][0]["name"] == "regex-1"
    assert criteria["checklist"][0]["description"] == "(?i)item{2,}"


def test_tessl_compat_parser_accepts_serializer_style_case_lists() -> None:
    cases = evals._parse_tessl_eval_cases_compat(
        "---\n"
        "schema_version: '2.0'\n"
        "cases:\n"
        "- id: serialized-case\n"
        "  eval_modes:\n"
        "  - smoke\n"
        "  - release\n"
        "  prompt: |-\n"
        "    Assess repeated steering.\n"
        "  acceptance:\n"
        "  - type: regex\n"
        "    value: '(?is)(durable|guardrail)'\n"
        "  - type: expected_signal\n"
        "    value: Names references/evals/eval.example.md.\n"
    )

    assert len(cases) == 1
    assert cases[0]["id"] == "serialized-case"
    assert cases[0]["prompt"] == "Assess repeated steering."
    assert cases[0]["acceptance"] == [
        {"type": "regex", "value": "(?is)(durable|guardrail)"},
        {"type": "expected_signal", "value": "Names references/evals/eval.example.md."},
    ]


def test_tessl_compat_parser_stops_acceptance_before_sibling_context_fields() -> None:
    cases = evals._parse_tessl_eval_cases_compat(
        "cases:\n"
        "- id: serialized-context-after-acceptance\n"
        "  prompt: Assess repo readiness.\n"
        "  acceptance:\n"
        "  - type: regex\n"
        "    value: (?is)(repo|readiness)\n"
        "  - type: expected_signal\n"
        "    value: Separates local evidence from readiness claims.\n"
        "  unit: repo readiness proof\n"
        "  given: A user asks whether the repo is ready.\n"
        "  should: Separate local evidence from readiness claims.\n"
    )

    assert cases[0]["unit"] == "repo readiness proof"
    assert cases[0]["given"] == "A user asks whether the repo is ready."
    assert cases[0]["should"] == "Separate local evidence from readiness claims."
    assert cases[0]["acceptance"] == [
        {"type": "regex", "value": "(?is)(repo|readiness)"},
        {"type": "expected_signal", "value": "Separates local evidence from readiness claims."},
    ]

__all__ = [name for name in globals() if not name.startswith("__")]
