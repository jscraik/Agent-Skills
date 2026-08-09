from ask_evals_command_tests_core import *  # noqa: F403

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
            "Evaluate each sentence against source-of-truth evidence and return a fail-closed judgement."
        ),
        "prompt": "Assess whether a support-agent response is grounded in its source policy.",
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
                "type": "expected_signal",
                "value": (
                    "Records judge_parse_error, judge_schema_error, judge_semantic_fail, "
                    "and judge_pass while preserving the raw judge output."
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
        prompt="Assess whether the support-agent response is grounded in its source policy.",
        judge_raw_output_artifact=None,
        raw_response_artifact=None,
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

__all__ = [name for name in globals() if not name.startswith("__")]
