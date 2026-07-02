from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import evals  # noqa: E402
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
            cases=["smoke-discovery"],
            timeout_seconds=5,
        )

    assert result.status == "error"
    assert run_mock.call_args.kwargs["start_new_session"] is True


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


def test_tessl_compat_parser_preserves_wrapped_plain_scalars() -> None:
    cases = evals._parse_tessl_eval_cases_compat(
        "cases:\n"
        "- id: wrapped-context\n"
        "  unit: repo readiness proof\n"
        "  given: A repo has scattered docs, validation entrypoints,\n"
        "    and proof loops.\n"
        "  should: Return a bounded scorecard that names exact files,\n"
        "    separates local proof from merge readiness, and recommends next fixes.\n"
        "  prompt: Assess the repository for agent-native readiness,\n"
        "    then produce a concise action queue.\n"
        "  acceptance:\n"
        "  - type: expected_signal\n"
        "    value: Names exact files and separates local proof from merge readiness\n"
        "      before recommending next fixes.\n"
    )

    assert cases[0]["given"] == (
        "A repo has scattered docs, validation entrypoints, and proof loops."
    )
    assert cases[0]["should"] == (
        "Return a bounded scorecard that names exact files, separates local proof "
        "from merge readiness, and recommends next fixes."
    )
    assert cases[0]["prompt"] == (
        "Assess the repository for agent-native readiness, then produce a concise action queue."
    )
    assert cases[0]["acceptance"] == [
        {
            "type": "expected_signal",
            "value": (
                "Names exact files and separates local proof from merge readiness before "
                "recommending next fixes."
            ),
        }
    ]


def test_tessl_eval_quality_rejects_keyword_only_cases() -> None:
    cases = [{
        "id": "weak-keywords",
        "prompt": "Audit this repository.",
        "acceptance": [
            {"type": "regex", "value": "(?is)(audit|repo|proof)"},
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert {finding["code"] for finding in findings} == {
        "missing_scenario_context",
        "missing_behavioral_acceptance",
        "keyword_only_acceptance",
    }


def test_tessl_eval_quality_rejects_shallow_routing_oracle() -> None:
    cases = [{
        "id": "shallow-teach-routing",
        "unit": "teach routing",
        "given": "A learner asks for a multi-session study plan.",
        "should": "Choose the teaching workflow and preserve the learning mission.",
        "prompt": "Teach SQL joins over four weeks.",
        "acceptance": [
            {"type": "skill_selected", "expected_skill": "teach"},
            {"type": "expected_signal", "value": "mission-grounded next step"},
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert [finding["code"] for finding in findings] == ["shallow_routing_oracle"]


def test_tessl_eval_quality_rejects_mixed_case_shallow_routing_oracle() -> None:
    cases = [{
        "id": "shallow-teach-routing",
        "unit": "teach routing",
        "given": "A learner asks for a multi-session study plan.",
        "should": "Choose the teaching workflow and preserve the learning mission.",
        "prompt": "Teach SQL joins over four weeks.",
        "acceptance": [
            {"type": "Skill_Selected", "expected_skill": "teach"},
            {"type": "Expected_Signal", "value": "mission-grounded next step"},
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert [finding["code"] for finding in findings] == ["shallow_routing_oracle"]


def test_ordinary_tessl_staging_allows_legacy_keyword_cases(tmp_path: Path) -> None:
    skill_root = _write_example_skill(tmp_path)
    (skill_root / "references" / "evals.yaml").write_text(
        (
            "cases:\n"
            "  - id: legacy-regex\n"
            "    prompt: Audit this repository.\n"
            "    acceptance:\n"
            "      - type: regex\n"
            "        value: \"(?is)(audit|repository)\"\n"
        ),
        encoding="utf-8",
    )
    staged_root = tmp_path / "staged"

    copied = evals._write_tessl_scenarios_from_evals(skill_root, staged_root)

    assert copied == [
        "scenario-sources.json",
        "scenarios/legacy-regex/task.md",
        "scenarios/legacy-regex/criteria.json",
    ]
    assert (staged_root / "scenarios" / "legacy-regex" / "task.md").exists()
    assert (staged_root / "scenarios" / "legacy-regex" / "criteria.json").exists()


def test_tessl_eval_quality_rejects_provenance_only_knowledgeos_signal() -> None:
    cases = [{
        "id": "eval.harness.seed-only",
        "unit": "seed only",
        "given": "A KnowledgeOS seed scenario was imported.",
        "should": "Convert the seed into a skill-specific behavioural eval.",
        "prompt": "Assess the repository and produce an evidence-backed answer.",
        "acceptance": [
            {"type": "regex", "value": "(?is)(evidence|repo)"},
            {
                "type": "expected_signal",
                "value": (
                    "Names the skill-local KnowledgeOS eval fixture path "
                    "references/evals/eval.harness.seed-only.md as part of the evidence boundary."
                ),
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert [finding["code"] for finding in findings] == [
        "missing_skill_lift_acceptance",
        "fixture_path_acceptance",
    ]


def test_tessl_eval_quality_rejects_broader_provenance_only_signal() -> None:
    cases = [{
        "id": "eval.harness.seed-only",
        "unit": "seed only",
        "given": "A KnowledgeOS seed scenario was imported.",
        "should": "Convert the seed into a skill-specific behavioural eval.",
        "prompt": "Assess the repository and produce an evidence-backed answer.",
        "acceptance": [
            {"type": "regex", "value": "(?is)(evidence|repo)"},
            {
                "type": "expected_signal",
                "value": "Cites references/evals/eval.harness.seed-only.md as evidence.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert [finding["code"] for finding in findings] == [
        "missing_skill_lift_acceptance",
        "fixture_path_acceptance",
    ]


def test_tessl_eval_quality_rejects_empty_case_set(tmp_path: Path) -> None:
    source = tmp_path / "references" / "evals.yaml"

    try:
        evals._assert_tessl_eval_quality([], source=source)
    except ValueError as exc:
        assert "no Tessl eval cases were selected" in str(exc)
    else:
        raise AssertionError("empty Tessl case set should fail quality gate")


def test_tessl_eval_quality_rejects_generic_should_contract_signal() -> None:
    cases = [{
        "id": "generic-should-contract",
        "unit": "generic expected signal",
        "given": "A seed eval has been converted from a knowledge capsule.",
        "should": "Separate evidence from readiness claims.",
        "prompt": "Assess the repository handoff.",
        "acceptance": [
            {"type": "regex", "value": "(?is)(evidence|readiness)"},
            {
                "type": "expected_signal",
                "value": (
                    "Demonstrates the skill-specific behavior in this case Should contract: "
                    "Separate evidence from readiness claims."
                ),
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert [finding["code"] for finding in findings] == ["missing_skill_lift_acceptance"]


def test_tessl_eval_quality_rejects_answer_leakage() -> None:
    leaked_answer = (
        "Classifies the boundary as risky, names missing caller proof, requests a "
        "tracer, and blocks autonomous edits until regression evidence exists."
    )
    cases = [{
        "id": "leaked-answer",
        "unit": "boundary proof",
        "given": "A module boundary looks clean but lacks caller proof.",
        "should": leaked_answer,
        "prompt": "Review the boundary before agents edit it.",
        "acceptance": [
            {
                "type": "expected_signal",
                "value": leaked_answer,
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert [finding["code"] for finding in findings] == ["answer_leakage"]


def test_tessl_eval_quality_flags_unstaged_repo_paths() -> None:
    cases = [{
        "id": "unstaged-path",
        "unit": "architecture review",
        "given": "A repo-root module is named directly.",
        "should": "Review the target from available evidence.",
        "prompt": "Review Infrastructure/scripts/lifecycle-and-sync/command_surface.py before changing it.",
        "acceptance": [
            {
                "type": "expected_signal",
                "value": "Names source-of-truth and caller proof.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "unstaged_repo_path_reference" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_flags_unstaged_repo_paths_in_acceptance() -> None:
    cases = [{
        "id": "unstaged-acceptance-path",
        "unit": "architecture review",
        "given": "A remote Tessl scenario refers to a repo-local proof artifact.",
        "should": "Use staged package context only.",
        "prompt": "Review the staged package context.",
        "acceptance": [
            {
                "type": "expected_signal",
                "value": "Cites .harness/artifacts/pu-020-adversarial-review/proof.md.",
            },
            {
                "type": "skill_selected",
                "expected_skill": "Mentions Docs/agents/24-tessl-live-skill-eval-workflow.md.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "unstaged_repo_path_reference" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_allows_package_relative_paths() -> None:
    cases = [{
        "id": "package-path",
        "unit": "architecture review",
        "given": "A package-local contract file is available in the staged Tessl tile.",
        "should": "Review the package contract from available evidence.",
        "prompt": "Review SKILL.md and references/contract.yaml before changing this package.",
        "acceptance": [
            {
                "type": "expected_signal",
                "value": "Names source-of-truth and caller proof.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "unstaged_repo_path_reference" not in {finding["code"] for finding in findings}


def _calibrated_guardrail_case(**overrides: object) -> dict[str, object]:
    case: dict[str, object] = {
        "id": "calibrated-hallucination-guardrail",
        "unit": "hallucination guardrail",
        "given": "A support-agent answer must stay grounded in a source-of-truth policy.",
        "should": (
            "Evaluate each sentence against source-of-truth evidence using factual accuracy, "
            "relevance, policy compliance, and contextual coherence."
        ),
        "prompt": (
            "Design a hallucination guardrail judge with labeled pass/fail examples, ordinary "
            "and adversarial cases, machine-readable JSON output, precision/recall calibration, "
            "and first-class outcomes judge_parse_error, judge_schema_error, "
            "judge_semantic_fail, and judge_pass."
        ),
        "raw_response_artifact": "references/evals/artifacts/judge-raw-output.json",
        "judge_raw_output_artifact": "references/evals/artifacts/judge-raw-output.json",
        "judge_parse_error_artifact": "references/evals/artifacts/judge-parse-error.json",
        "judge_schema_error_artifact": "references/evals/artifacts/judge-schema-error.json",
        "positive_example_artifact": "references/evals/examples/guardrail-pass.json",
        "negative_example_artifact": "references/evals/examples/guardrail-fail.json",
        "synthetic": True,
        "label": "pass",
        "risk_dimension": "policy-grounding",
        "source_policy_artifact": "references/evals/policies/source-of-truth.md",
        "judge_temperature": 0.2,
        "judge_runs": 3,
        "sample_count": 40,
        "pass_rate_threshold": 0.95,
        "acceptance": [
            {
                "type": "expected_signal",
                "value": (
                    "Requires labeled ordinary and adversarial examples plus precision and "
                    "recall calibration before the guardrail becomes release evidence."
                ),
            },
            {
                "type": "output_schema",
                "value": (
                    "Returns structured JSON with sentence_results[], overall_verdict, "
                    "failure_reason, and source_references[]. Unsupported factual claim "
                    "aggregation is fail-closed. A pass decision requires exact supporting "
                    "source_references, while a fail decision records a separate rationale."
                ),
            },
        ],
    }
    case.update(overrides)
    return case


def test_tessl_eval_quality_rejects_vague_hallucination_guardrail() -> None:
    cases = [{
        "id": "vague-hallucination-guardrail",
        "unit": "hallucination guardrail",
        "given": "A user wants a guardrail for hallucinations.",
        "should": "Check truthfulness and relevance.",
        "prompt": "Build a hallucination guardrail for this skill eval.",
        "acceptance": [
            {
                "type": "expected_signal",
                "value": "Says whether the answer is truthful and relevant.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "guardrail_missing_calibration_shape" in {finding["code"] for finding in findings}
    assert "guardrail_missing_paired_examples" in {finding["code"] for finding in findings}
    assert "guardrail_missing_judge_outcomes" in {finding["code"] for finding in findings}
    assert "guardrail_missing_response_schema" in {finding["code"] for finding in findings}
    assert "guardrail_missing_source_reference_quality" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_rejects_mixed_guardrail_terminology() -> None:
    cases = [{
        "id": "mixed-guardrail-terms",
        "unit": "hallucination guardrail",
        "given": "A support assistant answer must stay grounded in a knowledge base policy.",
        "should": (
            "Evaluate each sentence against source-of-truth evidence using factual accuracy, "
            "relevance, policy compliance, and contextual coherence."
        ),
        "prompt": (
            "Design a hallucination guardrail for the agent with labeled pass/fail examples, "
            "ordinary and adversarial cases, machine-readable JSON output, and precision/recall "
            "calibration."
        ),
        "positive_example_artifact": "references/evals/examples/guardrail-pass.json",
        "negative_example_artifact": "references/evals/examples/guardrail-fail.json",
        "judge_raw_output_artifact": "references/evals/artifacts/judge-raw-output.json",
        "judge_parse_error_artifact": "references/evals/artifacts/judge-parse-error.json",
        "judge_schema_error_artifact": "references/evals/artifacts/judge-schema-error.json",
        "acceptance": [
            {
                "type": "output_schema",
                "value": (
                    "Returns structured JSON with sentence_results[], overall_verdict, "
                    "failure_reason, and source_references[]. Unsupported factual claim "
                    "aggregation is fail-closed. A pass decision requires exact supporting "
                    "source_references, while a fail decision records a separate rationale."
                ),
            },
            {
                "type": "expected_signal",
                "value": (
                    "Requires precision and recall calibration before release evidence and "
                    "uses outcomes judge_parse_error, judge_schema_error, "
                    "judge_semantic_fail, and judge_pass."
                ),
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "guardrail_mixed_terminology" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_accepts_calibrated_hallucination_guardrail() -> None:
    cases = [_calibrated_guardrail_case()]

    assert evals._tessl_eval_quality_findings(cases) == []


def test_tessl_eval_quality_rejects_guardrail_without_failure_outcomes() -> None:
    case = _calibrated_guardrail_case(
        prompt=(
            "Design a hallucination guardrail judge with labeled pass/fail examples, ordinary "
            "and adversarial cases, machine-readable JSON output, and precision/recall calibration."
        ),
        judge_raw_output_artifact=None,
    )

    findings = evals._tessl_eval_quality_findings([case])

    assert "guardrail_missing_judge_outcomes" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_rejects_guardrail_without_whole_response_schema() -> None:
    case = _calibrated_guardrail_case(
        acceptance=[
            {
                "type": "expected_signal",
                "value": "Requires labeled examples and precision/recall calibration.",
            },
            {
                "type": "output_schema",
                "value": "Returns structured JSON with per-sentence factual accuracy evidence.",
            },
        ],
    )

    findings = evals._tessl_eval_quality_findings([case])

    assert "guardrail_missing_response_schema" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_rejects_missing_source_reference_quality() -> None:
    case = _calibrated_guardrail_case(
        acceptance=[
            {
                "type": "expected_signal",
                "value": (
                    "Requires labeled ordinary and adversarial examples plus precision and "
                    "recall calibration before the guardrail becomes release evidence."
                ),
            },
            {
                "type": "output_schema",
                "value": (
                    "Returns structured JSON with sentence_results[], overall_verdict, "
                    "failure_reason, and source_references[]. Unsupported factual claim "
                    "aggregation is fail-closed."
                ),
            },
        ],
    )

    findings = evals._tessl_eval_quality_findings([case])

    assert "guardrail_missing_source_reference_quality" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_flags_synthetic_guardrail_label_imbalance() -> None:
    cases = [
        _calibrated_guardrail_case(id="synthetic-pass-one", label="pass"),
        _calibrated_guardrail_case(id="synthetic-pass-two", label="pass"),
    ]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "guardrail_synthetic_label_imbalance" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_accepts_balanced_synthetic_guardrail_labels() -> None:
    cases = [
        _calibrated_guardrail_case(id="synthetic-pass", label="pass"),
        _calibrated_guardrail_case(id="synthetic-fail", label="fail"),
    ]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "guardrail_synthetic_label_imbalance" not in {finding["code"] for finding in findings}


def test_tessl_eval_quality_rejects_temperature_without_sample_count() -> None:
    case = _calibrated_guardrail_case(judge_runs=None, sample_count=None)

    findings = evals._tessl_eval_quality_findings([case])

    assert "judge_sampling_missing_repeat_count" in {finding["code"] for finding in findings}


def test_tessl_criteria_preserves_guardrail_calibration_examples() -> None:
    case = _calibrated_guardrail_case()

    criteria = evals._tessl_criteria_from_case(case)

    assert criteria["metadata"]["calibration_examples"] == {
        "positive": "references/evals/examples/guardrail-pass.json",
        "negative": "references/evals/examples/guardrail-fail.json",
    }


def test_tessl_criteria_preserves_guardrail_extended_metadata() -> None:
    case = _calibrated_guardrail_case()

    criteria = evals._tessl_criteria_from_case(case)
    metadata = criteria["metadata"]

    assert metadata["agent_eval_artifacts"] == {
        "raw_response": "references/evals/artifacts/judge-raw-output.json",
        "judge_details": None,
        "judge_raw_output": "references/evals/artifacts/judge-raw-output.json",
        "judge_parse_error": "references/evals/artifacts/judge-parse-error.json",
        "judge_schema_error": "references/evals/artifacts/judge-schema-error.json",
    }
    assert metadata["judge_failure_outcomes"] == {
        "parse_error": "judge_parse_error",
        "schema_error": "judge_schema_error",
        "semantic_fail": "judge_semantic_fail",
        "pass": "judge_pass",
    }
    assert metadata["guardrail_output_contract"] == {
        "sentence_results": "required",
        "overall_verdict": "required",
        "failure_reason": "required",
        "source_references": "required_for_pass_decisions",
        "unsupported_factual_claim": "fail_closed",
        "fail_rationale": "separate_from_pass_reference",
    }
    assert metadata["synthetic_case"] == {
        "enabled": True,
        "label": "pass",
        "risk_dimension": "policy-grounding",
        "source_policy_artifact": "references/evals/policies/source-of-truth.md",
    }
    assert metadata["judge_sampling"] == {
        "temperature": 0.2,
        "runs": 3,
        "sample_count": 40,
    }
    assert metadata["pass_rate_policy"] == {
        "threshold": 0.95,
        "calibration_artifact": None,
        "gate_status": "advisory",
    }


def test_tessl_eval_quality_accepts_behavioral_scenario() -> None:
    cases = [{
        "id": "useful-scenario",
        "unit": "repo validation proof boundary",
        "given": "A user asks whether a PR is ready after local tests ran but CI has not been checked.",
        "should": "Separate local validation truth from remote CI and merge-readiness truth.",
        "prompt": "Advise the next action for the repository handoff.",
        "acceptance": [
            {"type": "regex", "value": "(?is)(local|CI|merge)"},
            {
                "type": "expected_signal",
                "value": "Separates local test evidence from CI and merge-readiness claims before recommending next action.",
            },
        ],
    }]

    assert evals._tessl_eval_quality_findings(cases) == []


def test_tessl_eval_quality_rejects_skill_name_as_primary_proof() -> None:
    cases = [{
        "id": "skill-selection-oracle",
        "unit": "technical writing boundary",
        "given": "A user asks for a docs audit.",
        "should": "Demonstrate a useful docs-audit behavior, not just select the expected skill.",
        "prompt": "Review the staged docs package.",
        "acceptance": [
            {"type": "skill_selected", "value": "technical-writer"},
            {"type": "regex", "value": "(?i)technical-writer"},
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "skill_name_primary_proof" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_rejects_missing_concrete_output_artifact() -> None:
    cases = [{
        "id": "release-case-without-output",
        "mode": "release",
        "unit": "technical writing reader review",
        "given": "A migration guide omits rollback evidence.",
        "should": "Identify missing reader and recovery evidence.",
        "prompt": "Review the staged migration guide and report the issue.",
        "acceptance": [
            {
                "type": "expected_signal",
                "value": "Names missing rollback evidence and asks the writer for the source of truth before editing.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "missing_concrete_output_artifact" in {finding["code"] for finding in findings}


def test_tessl_eval_quality_rejects_hidden_reference_dependency() -> None:
    cases = [{
        "id": "hidden-discovery-reference",
        "mode": "smoke",
        "unit": "underspecified documentation request",
        "given": "A user asks for docs help without naming the editable surface.",
        "should": "Ask one discovery question before editing.",
        "prompt": (
            "Use references/discovery-interview.md to decide the smallest useful "
            "question for this underspecified request."
        ),
        "acceptance": [
            {
                "type": "expected_signal",
                "value": "Asks which documentation path or surface to inspect first before making changes.",
            },
        ],
    }]

    findings = evals._tessl_eval_quality_findings(cases)

    assert "hidden_reference_dependency" in {finding["code"] for finding in findings}


def test_extract_tessl_eval_run_id_accepts_array_json_response() -> None:
    output = (
        "- Running 32 scenarios...\n"
        '[{"evalRunId":"019ecad5-c50c-75ab-91d4-50209e9f3d8a","scenariosCount":32}]\n'
    )

    assert evals._extract_tessl_eval_run_id(output) == "019ecad5-c50c-75ab-91d4-50209e9f3d8a"


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


def _write_example_skill(tmp_path: Path) -> Path:
    skill_root = tmp_path / "Skills" / "example-skill"
    references = skill_root / "references"
    references.mkdir(parents=True)
    agents = skill_root / "agents"
    agents.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        '---\nname: example-skill\nmetadata:\n  version: "1.2.3"\n---\n# Example Skill\n',
        encoding="utf-8",
    )
    (agents / "openai.yaml").write_text(
        "schema_version: openai.skill.v1\nname: example-skill\n",
        encoding="utf-8",
    )
    (references / "evals.yaml").write_text(
        EXAMPLE_TESSL_EVAL_YAML,
        encoding="utf-8",
    )
    (references / "contract.yaml").write_text(
        "version: 1\ntessl_scenario_policy:\n  structure_only: true\n",
        encoding="utf-8",
    )
    (skill_root / "secret-not-staged.txt").write_text("do not copy\n", encoding="utf-8")
    _write_handoff_readiness(tmp_path, "example-skill")
    return skill_root


def _write_handoff_readiness(tmp_path: Path, skill_name: str) -> Path:
    evidence_root = tmp_path / ".harness" / "evidence" / "handoff" / skill_name
    evidence_root.mkdir(parents=True, exist_ok=True)
    lanes = []
    lane_commands = {
        "deterministic_local_gates": "./bin/ask sdk eval local-gates Skills/example-skill --json --robot",
        "oss-local": "./bin/ask sdk eval run Skills/example-skill --codex-profile oss-local --json --robot",
        "oss-cloud": "./bin/ask sdk eval run Skills/example-skill --codex-profile oss-cloud --json --robot",
        "tessl-local-proof": "./bin/ask sdk eval tessl-local-proof Skills/example-skill --execute --json --robot",
        "tessl-live-dry-run": (
            "./bin/ask evals run Skills/example-skill --tessl-live-private "
            "--tessl-live-dry-run --json --robot"
        ),
    }
    for lane_id, command in lane_commands.items():
        receipt_path = evidence_root / f"{lane_id}.json"
        receipt_payload: dict[str, object] = {"status": "pass", "lane": lane_id}
        if lane_id in {"oss-local", "oss-cloud"}:
            receipt_payload["profile"] = lane_id
            receipt_payload["codex_profile"] = lane_id
            receipt_payload["codex_exec_invoked"] = True
        if lane_id == "tessl-local-proof":
            receipt_payload["receipt"] = {
                "schema_version": "jscraik.tessl-local-proof.v1",
                "status": "pass",
                "execute": True,
            }
        if lane_id == "tessl-live-dry-run":
            receipt_payload["tessl_eval"] = {
                "status": "pass",
                "live_private": True,
                "dry_run": True,
            }
        receipt_path.write_text(json.dumps(receipt_payload) + "\n", encoding="utf-8")
        lanes.append({
            "id": lane_id,
            "status": "pass",
            "command": command,
            "receipt_path": receipt_path.relative_to(tmp_path).as_posix(),
        })
    readiness_path = evidence_root / "eval-handoff-readiness.json"
    readiness_path.write_text(
        json.dumps({
            "schema_version": "jscraik.eval-handoff-readiness-input.v1",
            "candidate_id": skill_name,
            "lanes": lanes,
        }) + "\n",
        encoding="utf-8",
    )
    return readiness_path


def test_evals_run_native_tessl_without_project_save_approval_flag(tmp_path: Path) -> None:
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
    assert len(tessl_eval_runs) == 1
    assert not any(cmd[1:3] == ["project", "create"] for cmd in commands)
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


def test_evals_run_native_tessl_by_default_with_temp_staged_source(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)
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
        task_text = (staged_source / "scenarios" / "smoke-example" / "task.md").read_text(encoding="utf-8")
        assert task_text.startswith("Unit: example skill behavioural proof\n")
        assert task_text.endswith("Do the example task.\n")
        assert not (staged_source / "secret-not-staged.txt").exists()
        return completed

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(
            evals,
            "_tessl_live_handoff_readiness",
            return_value={"ready_for_live_tessl": True, "blockers": [], "required_next_actions": []},
        ),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run) as run,
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
    assert len(tessl_eval_runs) == 1
    tessl_cmd = tessl_eval_runs[0]
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
        "scenario-sources.json",
        "scenarios/smoke-example/task.md",
        "scenarios/smoke-example/criteria.json",
        "tessl.json",
    ]
    assert result.data["tessl_eval"]["policy"]["no_registry_upload"] is True
    assert result.data["tessl_eval"]["policy"]["temp_staged_project_input_only"] is True
    assert result.data["tessl_eval"]["policy"]["network_permission_required_by_repo"] is False
    assert result.data["tessl_eval"]["policy"]["project_save_default"] == "compatibility_flag_not_required"


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
    assert "Help with this situation:" in generated_task
    criteria = json.loads(
        (staged_source / "evals" / "generated-eval.arch.boundary-proof" / "criteria.json").read_text(
            encoding="utf-8"
        )
    )
    assert criteria["metadata"]["source"] == "references/evals/eval.arch.boundary-proof.md"
    descriptions = [item["description"] for item in criteria["checklist"]]
    assert any("Classifies the boundary as risky" in item for item in descriptions)


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


def test_tessl_live_private_requires_twenty_behavioral_scenarios(tmp_path: Path) -> None:
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
        raise AssertionError("expected behavioral live staging to require 20 scenarios")

    assert "require at least 20 gold-standard structured scenarios" in message
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

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
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

    with mock.patch.object(
        evals,
        "_run_tessl_live_private_eval",
        return_value={
            "status": "blocked",
            "blocker": "Tessl workspace is required.",
            "blocker_class": "blocked_validation",
        },
    ) as run_live_private:
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


def test_tessl_live_private_policy_names_tessl_local_proof_gate() -> None:
    policy = evals._tessl_live_private_policy("jscraik")
    feedback_loop = policy["pre_tessl_feedback_loop"]

    assert "tessl_local_proof" in feedback_loop["required_order"]
    assert any(step["stage"] == "tessl_local_proof" for step in feedback_loop["tessl_sequence"])
    assert "Tessl local-proof" in feedback_loop["failure_loop"]
    assert "Tessl local-proof" in feedback_loop["live_blocked_until"]


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

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
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

    with mock.patch.object(evals.subprocess, "run", return_value=completed):
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


def test_evals_run_uses_plugin_project_identity_when_workspace_is_set(tmp_path: Path) -> None:
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

    def fake_run(cmd: list[str], **kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["project", "repair"]:
            staged_source = Path(str(kwargs["cwd"]))
            marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
            assert marker["name"] == "jscraik/skill-factory"
            return mock.Mock(
                returncode=0,
                stdout='{"workspace":"jscraik","project":"skill-factory","name":"jscraik/skill-factory"}',
                stderr="",
                args=cmd,
            )
        if cmd[1:4] == ["eval", "run", "--json"]:
            staged_source = Path(cmd[4])
            marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
            assert marker["name"] == "jscraik/skill-factory"
            return mock.Mock(returncode=0, stdout="{}", stderr="", args=cmd)
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
            "Plugins/skill-factory/skills/skill-factory-router",
            mode="smoke",
            tessl_workspace="jscraik",
        )

    tessl_eval = result.data["tessl_eval"]
    assert result.status == "success"
    assert tessl_eval["project_identity"]["owner_type"] == "plugin"
    assert tessl_eval["project_identity"]["project"] == "skill-factory"
    assert tessl_eval["project_link"]["action"] == "already_linked"


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
    assert archive_dir.parent == tmp_path / "staged-evidence-archive"
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
    external_archive_root = tmp_path / "staged-evidence-archive"

    assert archive_dir is not None
    assert not (staged_root / "evidence-archive").exists()
    assert (
        next(external_archive_root.glob("*legacy-evidence-archive/old-run/archived-scenarios/old-case/task.md"))
    ).read_text(encoding="utf-8") == "stale scenario evidence\n"
    assert not (archive_dir / "scenarios").exists()
    assert (archive_dir / "archived-scenarios" / "current-case" / "task.md").read_text(encoding="utf-8") == (
        "current scenario evidence\n"
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


def test_evals_live_private_uses_default_workspace(tmp_path: Path) -> None:
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


def test_evals_live_private_invokes_tessl_with_workspace_and_plugin_manifest(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")
    completed_eval = mock.Mock(returncode=0, stdout='{"id":"019e6ac8-08eb-75fb-8fbb-e2346517f82d"}', stderr="")
    completed_view = mock.Mock(
        returncode=0,
        stdout=json.dumps({
            "data": {
                "attributes": {
                    "agent": "claude",
                    "model": "deepseek-v4-flash",
                    "scorerAgent": "glm",
                    "scorerModel": "glm-5.1",
                    "usage": {
                        "meanTurns": 20,
                        "p95Turns": 37,
                        "totalTokens": 12345,
                        "estimatedCostUsd": 0.0236,
                    },
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
    assert result.data["local_eval_status"] == "skipped_tessl_live_private"
    assert "separately before live scoring" in result.data["tessl_live_private_note"]
    eval_run_calls = [
        call.args[0] for call in run.call_args_list
        if call.args[0][1:3] == ["eval", "run"]
    ]
    local_eval_calls = [
        call.args[0] for call in run.call_args_list
        if any("run_skill_evals.py" in str(part) for part in call.args[0])
    ]
    eval_view_calls = [
        call.args[0] for call in run.call_args_list
        if call.args[0][1:3] == ["eval", "view"]
    ]
    assert local_eval_calls == []
    assert len(eval_run_calls) == 1
    assert len(eval_view_calls) == 1
    tessl_cmd = eval_run_calls[0]
    assert tessl_cmd[:4] == ["/usr/local/bin/tessl", "eval", "run", "--json"]
    assert tessl_cmd[4:6] == ["--workspace", "jscraik"]
    assert "--yes" not in tessl_cmd
    staged_source = Path(tessl_cmd[6])
    assert staged_source.is_dir()
    view_cmd = eval_view_calls[0]
    assert view_cmd == [
        "/usr/local/bin/tessl",
        "eval",
        "view",
        "--json",
        "019e6ac8-08eb-75fb-8fbb-e2346517f82d",
    ]
    assert not (staged_source / "tile.json").exists()
    staged_manifest = json.loads(
        (staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert staged_manifest["name"] == "jscraik/example-skill"
    assert staged_manifest["version"] == "1.2.3"
    assert staged_manifest["description"] == "Private live eval plugin for example-skill."
    assert staged_manifest["private"] is True
    assert staged_manifest["skills"] == "./skills/"
    project_marker = json.loads((staged_source / "tessl.json").read_text(encoding="utf-8"))
    assert project_marker["name"] == "jscraik/example-skill"
    staged_skill = _assert_plugin_shaped_stage(staged_source, "example-skill")
    assert (staged_skill / "SKILL.md").is_file()
    assert (staged_skill / "references" / "evals.yaml").is_file()
    assert (staged_source / "evals" / "smoke-example" / "task.md").is_file()
    assert (staged_source / "evals" / "smoke-example" / "criteria.json").is_file()
    assert "publish" not in tessl_cmd
    assert "install" not in tessl_cmd
    assert "registry" not in tessl_cmd
    assert result.data["tessl_eval"]["policy"]["command_shape"] == (
        "tessl eval run --json --workspace <workspace> <staged-plugin-dir>"
    )
    assert result.data["tessl_eval"]["policy"]["duplicate_run_guard"].startswith("before live scoring")
    submission_evidence_path = tmp_path / result.data["tessl_eval"]["submission_evidence_path"]
    assert submission_evidence_path == (
        tmp_path
        / ".harness"
        / "evidence"
        / "tessl"
        / "example-skill"
        / "019e6ac8-08eb-75fb-8fbb-e2346517f82d"
        / "tessl-eval-submission.json"
    )
    submission_evidence = json.loads(submission_evidence_path.read_text(encoding="utf-8"))
    assert submission_evidence["status"] == "submitted_pending_view"
    assert submission_evidence["run_id"] == "019e6ac8-08eb-75fb-8fbb-e2346517f82d"
    assert submission_evidence["workspace"] == "jscraik"
    assert submission_evidence["skill_path"] == "Skills/example-skill"
    assert submission_evidence["next_action"].startswith("poll tessl eval view")
    view_evidence_path = tmp_path / result.data["tessl_eval"]["view_evidence_path"]
    assert view_evidence_path == (
        tmp_path
        / ".harness"
        / "evidence"
        / "tessl"
        / "example-skill"
        / "019e6ac8-08eb-75fb-8fbb-e2346517f82d"
        / "tessl-eval-view.json"
    )
    assert json.loads(view_evidence_path.read_text(encoding="utf-8")) == json.loads(completed_view.stdout)
    summary = result.data["tessl_eval"]["live_result_summary"]
    assert summary["meets_min_score"] is True
    assert summary["beats_baseline"] is True
    assert summary["model_selection"] == {
        "agent": "claude",
        "model": "deepseek-v4-flash",
        "scorer_agent": "glm",
        "scorer_model": "glm-5.1",
        "quality_floor_before_cost": True,
        "cost_is_secondary_to_score": True,
    }
    assert summary["comparative_quality"]["with_skill_score"] == 1
    assert summary["comparative_quality"]["without_skill_score"] == 0
    assert summary["cost_observability"]["turn_metrics_available"] is True
    assert summary["cost_observability"]["token_metrics_available"] is True
    assert summary["cost_observability"]["cost_metrics_available"] is True
    assert summary["cost_observability"]["turn_metrics"]["usage.meanTurns"] == 20
    assert summary["cost_observability"]["turn_metrics"]["usage.p95Turns"] == 37
    assert summary["cost_observability"]["token_metrics"]["usage.totalTokens"] == 12345
    assert summary["cost_observability"]["cost_metrics"]["usage.estimatedCostUsd"] == 0.0236


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


def test_evals_skip_tessl_escape_hatch(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path)

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Skills/example-skill", mode="smoke", skip_tessl=True)

    assert result.status == "success"
    commands = [call.args[0] for call in run.call_args_list]
    assert not any(cmd[1:3] == ["eval", "run"] for cmd in commands)
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

    def fake_run(cmd: list[str], **_kwargs: object) -> mock.Mock:
        if cmd[1:3] == ["eval", "run"]:
            return completed_tessl
        return completed_eval

    with (
        mock.patch.object(evals.shutil, "which", return_value="/usr/local/bin/tessl"),
        mock.patch.object(evals.subprocess, "run", side_effect=fake_run),
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

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_run_tessl_eval", return_value={"status": "pass"}) as run_tessl,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] == "jscraik"
    assert result.data["tessl_workspace_source"] == "ASK_TESSL_WORKSPACE"
    assert run_tessl.call_args.kwargs["workspace"] == "jscraik"


def test_run_evals_without_workspace_uses_jscraik_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ASK_TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE_NAME", raising=False)
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_run_tessl_eval", return_value={"status": "pass"}) as run_tessl,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] == "jscraik"
    assert result.data["tessl_workspace_source"] == "default"
    assert run_tessl.call_args.kwargs["workspace"] == "jscraik"


def test_run_evals_preserves_jscraik_tessl_workspace_argument(tmp_path: Path) -> None:
    completed = _completed_eval_with_report(tmp_path, "autoreview")

    with (
        mock.patch.object(evals.subprocess, "run", return_value=completed),
        mock.patch.object(evals, "_run_tessl_eval", return_value={"status": "pass"}) as run_tessl,
    ):
        result = evals.run_evals(
            tmp_path,
            "Skills/agent-ops/autoreview",
            mode="smoke",
            dashboard=False,
            tessl_workspace="jscraik",
        )

    assert result.status == "success"
    assert result.data["tessl_workspace"] == "jscraik"
    assert result.data["tessl_workspace_source"] == "argument"
    assert "--tessl-workspace jscraik" in result.data["validation_commands"][0]
    assert run_tessl.call_args.kwargs["workspace"] == "jscraik"


def test_run_evals_blocks_stale_tessl_workspace_argument(tmp_path: Path) -> None:
    result = evals.run_evals(
        tmp_path,
        "Skills/agent-ops/autoreview",
        mode="smoke",
        dashboard=False,
        tessl_workspace="not-jscraik",
    )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["tessl_eval"]["status"] == "blocked"
    assert result.data["tessl_eval"]["workspace_source"] == "argument"
    assert "must use workspace jscraik" in result.data["tessl_eval"]["blocker"]


def test_run_evals_live_private_uses_jscraik_default_workspace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ASK_TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE", raising=False)
    monkeypatch.delenv("TESSL_WORKSPACE_NAME", raising=False)
    _write_example_skill(tmp_path)

    result = evals.run_evals(
        tmp_path,
        "Skills/example-skill",
        mode="smoke",
        dashboard=False,
        tessl_live_private=True,
    )

    assert result.status == "error"
    assert result.data["tessl_workspace"] == "jscraik"
    assert result.data["tessl_workspace_source"] == "default"
    assert result.errors[0].message.startswith("Tessl live-private blocked")
    assert "Handoff readiness" in result.errors[0].message


def test_run_evals_blocks_invalid_default_tessl_workspace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("ASK_TESSL_WORKSPACE", "skills-sdk")

    result = evals.run_evals(
        tmp_path,
        "Skills/agent-ops/autoreview",
        mode="smoke",
        dashboard=False,
    )

    assert result.status == "error"
    assert result.data["eval_status"] == "blocked_validation"
    assert result.data["tessl_eval"]["status"] == "blocked"
    assert "must use workspace jscraik" in result.data["tessl_eval"]["blocker"]
    assert result.errors[0].code == "ERR_VALIDATION"


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
    skill = tmp_path / "Skills" / "agent-ops" / "autoresearch"
    skill.mkdir(parents=True)
    absolute_report = tmp_path / "Infrastructure" / "artifacts" / "skills" / "scorecard.json"
    absolute_report.parent.mkdir(parents=True)
    absolute_report.write_text(
        json.dumps({
            "status": "pass",
            "cases": [],
            "no_case_reason": "path sanitization fixture",
        }),
        encoding="utf-8",
    )
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
                        "command": "tessl plugin lint <temporary-plugin-wrapper>",
                        "role": "disposable .tessl-plugin/plugin.json package-shape check",
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
    assert "disposable .tessl-plugin/plugin.json package-shape check" in html_text
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


def test_tessl_live_evidence_rejects_symlinked_repo_evidence_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    external = tmp_path / "external-evidence"
    external.mkdir()
    evidence_parent = repo_root / ".harness" / "evidence"
    evidence_parent.mkdir(parents=True)
    os.symlink(external, evidence_parent / "tessl")

    path = evals._tessl_live_evidence_file(repo_root, "Skills/example/SKILL.md", "run-123", "view.json")

    assert path is None
