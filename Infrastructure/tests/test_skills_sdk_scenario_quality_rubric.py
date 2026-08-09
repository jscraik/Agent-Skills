from scenario_quality_test_support import *  # noqa: F403


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_builder_blocks_tessl_semantic_answer_leakage_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: leaked-scorecard
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for repository readiness reviews before release.
  unit: repo readiness scorecard
  given: A user needs a repository readiness audit for routing, validation entrypoints, proof loops, and residual risk.
  should: Return a scored gap list with severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.
  actual_artifact: artifacts/leaked-scorecard.md
  expected_artifact: readiness.md
  reproduce: ./bin/ask sdk eval run sample
  prompt: Audit this repository for routing, validation entrypoints, proof loops, severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns a scorecard with routing, validation entrypoints, proof loops, severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.
  - type: not_contains
    value: fully ready
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:semantic_answer_leakage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_allows_output_format_language_without_answer_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: fixture-routing-table
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Teams ask for read-only routing audits before editing inherited guidance files.
  unit: guidance routing table
  given: A maintainer needs a read-only audit of supplied guidance fixture records.
  should: Return a decision table that classifies each supplied record without claiming edits or validation.
  actual_artifact: routing-table.md
  expected_artifact: routing-table.md
  reproduce: ./bin/ask sdk eval run sample
  prompt: |
    Review supplied guidance fixture records. Do not edit files and do not call tools.

    Return a decision table with columns supplied record, decision, and rationale.
    Use literal decision labels keep, move, or delete.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Includes a decision table with supplied record, decision, and rationale columns for each fixture record.
  - type: expected_signal
    value: Uses keep, move, or delete as the routing decision labels without claiming file edits or validation execution.
  - type: must_not_claim
    value: Claims that validation commands were executed.
""",
            )

            case = _yaml_safe_load(skill_dir.joinpath("references/evals.yaml").read_text(encoding="utf-8"))["cases"][0]
            findings = tessl_eval_quality_findings([case])

        finding_ids = {finding["code"] for finding in findings}
        self.assertNotIn("semantic_answer_leakage", finding_ids)

    def test_builder_treats_text_field_assertions_as_behavioral_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: typed-field-routing
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Teams score structured routing audits by stable field values.
  unit: typed field routing audit
  given: A maintainer needs a structured routing audit.
  should: Return routing fields that preserve linked supplemental guidance.
  actual_artifact: routing.yaml
  expected_artifact: routing.yaml
  reproduce: ./bin/ask sdk eval run sample
  prompt: Return YAML fields records_reviewed, move_count, and delete_count.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: text_field_equals
    field: records_reviewed
    value: '3'
  - type: text_field_equals
    field: delete_count
    value: '0'
  - type: must_not
    value: Claims validation was executed.
""",
            )

            case = _yaml_safe_load(skill_dir.joinpath("references/evals.yaml").read_text(encoding="utf-8"))["cases"][0]
            findings = tessl_eval_quality_findings([case])

        finding_ids = {finding["code"] for finding in findings}
        self.assertNotIn("missing_behavioral_acceptance", finding_ids)
        self.assertNotIn("missing_skill_lift_acceptance", finding_ids)

    def test_builder_blocks_low_value_negative_release_scenario_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: unrelated-poem-negative
  category: negative
  eval_modes:
  - release
  realistic: true
  why_realistic: A local routing smoke can check unrelated creative prompts.
  unit: unrelated creative prompt
  given: A user asks for a short poem.
  should: Avoid selecting the skill for unrelated creative writing.
  actual_artifact: artifacts/unrelated-poem-negative.md
  expected_artifact: routing response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Write a short poem about a lighthouse.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: not_contains
    value: sample
  - type: expected_signal
    value: Treats the request as unrelated creative writing and avoids an audit.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:low_value_negative_scenario", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_includes_reviewed_generated_fixtures_before_tessl_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_8_evals_yaml())
            fixture_dir = skill_dir / "references" / "evals"
            fixture_dir.mkdir()
            (fixture_dir / "eval.harness.feedback-recurs-without-guardrail.md").write_text(
                """# eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture

Knowledge claim: The agent classifies repeated feedback as an operational failure.
Behavior under test: Observable agent behavior when a reviewer repeats the same correction.
Failure mode: The agent applies another one-off fix without addressing recurrence.
Expected agent move: The agent records a durable mechanism, validator, test, instruction route, or bounded skip reason.

Given: A reviewer repeats the same correction that appeared in an earlier agent task.
Should: The agent classifies the repeated failure and proposes a durable mechanism, validator, test, instruction route, or bounded skip reason.
Expected failure: The agent applies another one-off fix without addressing recurrence.
""",
                encoding="utf-8",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        self.assertEqual(receipt["scenario_count"], 9)
        self.assertIn(
            "generated-eval.harness.feedback-recurs-without-guardrail",
            {row["id"] for row in receipt["scenario_rows"]},
        )
        validate_scenario_quality_receipt(receipt)

    def test_generated_fixtures_score_package_behavior_not_missing_response_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_8_evals_yaml())
            fixture_dir = skill_dir / "references" / "evals"
            fixture_dir.mkdir()
            (fixture_dir / "eval.harness.done-without-validation.md").write_text(
                """# eval.harness.done-without-validation: Done Without Validation Is Rejected

Knowledge claim: The skill rejects readiness claims without validation evidence.
Behavior under test: Observable agent behavior when an agent reports done without validation.
Failure mode: The agent says done because implementation edits were made.
Expected agent move: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.

Given: An agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Should: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Expected failure: The agent says done because implementation edits were made.
""",
                encoding="utf-8",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")
            case = next(
                case
                for case in parse_generated_eval_fixtures(skill_dir)
                if case["id"] == "generated-eval.harness.done-without-validation"
            )

        row = next(
            row
            for row in receipt["scenario_rows"]
            if row["id"] == "generated-eval.harness.done-without-validation"
        )
        acceptance_text = " ".join(str(item.get("value", "")) for item in case["acceptance"])
        self.assertEqual(row["promotion_status"], "promotion_ready")
        self.assertIn("Score the package instructions and references", str(case["prompt"]))
        self.assertIn("The skill package instructs agents", acceptance_text)
        self.assertEqual(case["actual_artifact"], "installed skill package instructions and references")
        self.assertNotIn("Produce a response", str(case["should"]))
        self.assertNotIn("supplied fixture", acceptance_text)
        validate_scenario_quality_receipt(receipt)

    def test_generated_fixture_package_cases_block_response_artifact_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: generated-response-artifact-leak
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: Reviewed generated fixture imported into the skill package for private Tessl assessment.
  given: A repeated feedback case needs durable package guidance.
  should: Score package instructions and references.
  actual_artifact: staged-artifacts/generated/generated-response-artifact-leak/final.json
  expected_artifact: references/evals/eval.harness.feedback.md
  reproduce: references/evals/eval.harness.feedback.md
  source_kind: generated_fixture
  tessl:
    generated: true
  claim_ids:
  - generated_fixture.behavior
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: The skill package records a durable guardrail before the next lane.
  - type: expected_signal
    value: The skill package names the proof boundary.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("generated_fixture_package_artifact_contract", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_durable_guardrail_language_is_not_hallucination_guardrail_calibration(self) -> None:
        case = {
            "id": "durable-feedback-guardrail",
            "prompt": "A reviewer repeats the same correction; identify the durable guardrail or validator that prevents recurrence.",
            "given": "Repeated steering happened twice.",
            "should": "Record a durable mechanism.",
            "acceptance": [
                {"type": "expected_signal", "value": "Records a durable guardrail, validator, or bounded skip reason."}
            ],
        }

        finding_codes = {finding["code"] for finding in tessl_eval_quality_findings([case])}

        self.assertNotIn("guardrail_missing_calibration_shape", finding_codes)
        self.assertNotIn("guardrail_missing_paired_examples", finding_codes)
        self.assertNotIn("guardrail_missing_judge_outcomes", finding_codes)
        self.assertNotIn("guardrail_missing_response_schema", finding_codes)
        self.assertNotIn("guardrail_missing_source_reference_quality", finding_codes)

    def test_hallucination_guardrail_eval_still_requires_calibration_shape(self) -> None:
        case = {
            "id": "hallucination-guardrail",
            "prompt": "Run a guardrail eval for hallucinated source claims.",
            "given": "A model may invent citations.",
            "should": "Fail unsupported factual claims.",
            "acceptance": [
                {"type": "expected_signal", "value": "Flags hallucinated source claims."}
            ],
        }

        finding_codes = {finding["code"] for finding in tessl_eval_quality_findings([case])}

        self.assertIn("guardrail_missing_calibration_shape", finding_codes)
        self.assertIn("guardrail_missing_paired_examples", finding_codes)

    def test_builder_blocks_skill_name_as_primary_tessl_proof_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: skill-name-primary-proof
  category: happy
  eval_modes:
  - smoke
  realistic: true
  why_realistic: A real skill routing case.
  given: A docs task should trigger the skill.
  should: Score the output, not only whether the skill was selected.
  actual_artifact: final response
  expected_artifact: review.md
  reproduce: ./bin/ask sdk eval run sample
  prompt: Write review.md for a staged docs task.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: skill_selected
    expected_skill: sample
  - type: regex
    value: '(?i)(documentation|evidence)'
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:skill_name_primary_proof", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_regex_heavy_release_rubric_before_tessl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: regex-heavy-release
  category: edge
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for evidence-backed release decisions that allow wording variation.
  unit: release scorer brittleness
  given: A repository has local validation but missing external proof.
  should: Separate local proof from release readiness and name the next evidence lane.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a short release decision note for a repo with local tests but no CI evidence.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: (?is)(local tests|validation)
  - type: regex
    value: (?is)(CI|review|release)
  - type: not_regex
    value: (?is)(release ready|CI passed)
  - type: expected_signal
    value: Separates local validation evidence from external release readiness and names the next proof lane.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_regex_not_primary", blocker_ids)
        self.assertIn("release_rubric_semantic_coverage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_single_positive_regex_in_release_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: regex-single-release
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for release decisions that should allow wording variation.
  unit: release scorer brittleness
  given: A repository has package validation but missing hosted review evidence.
  should: Separate local package validation from external review readiness.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a short release decision note for a repo with local package validation but no hosted review evidence.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: (?is)(package validation|hosted review)
  - type: expected_signal
    value: Separates local package validation from external review readiness.
  - type: expected_signal
    value: Names hosted review evidence as the next proof lane.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_regex_not_primary", blocker_ids)
        self.assertNotIn("release_rubric_semantic_coverage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_release_rubric_without_two_semantic_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: semantic-thin-release
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for release decisions that should be checked by behavior, not phrasing.
  unit: release scorer semantic coverage
  given: A repository has local validation but no external review evidence.
  should: Separate local validation from external release readiness.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a release decision note for a repo with local validation but no external review evidence.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Separates local validation from external release readiness.
  - type: not_regex
    value: (?is)(release ready|mergeable)
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_semantic_coverage", blocker_ids)
        self.assertNotIn("release_rubric_regex_not_primary", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_phrase_only_negative_boundary_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: brittle-negative-boundary
  category: edge
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers need release checks that allow safe negated boundary statements.
  unit: release scorer negated boundary safety
  given: A repository has local validation but no external CI evidence.
  should: Say local validation does not prove external CI.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a release decision note that separates local validation from external CI.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Separates local validation evidence from external CI proof.
  - type: expected_signal
    value: Says CI remains unchecked until hosted evidence is inspected.
  - type: not_contains
    value: CI passed
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_negated_boundary_safe", blocker_ids)
        self.assertNotIn("release_rubric_regex_not_primary", blocker_ids)
        self.assertNotIn("release_rubric_semantic_coverage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_keyword_list_expected_signal_in_release_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: keyword-list-release-signal
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers need release rubrics that score behavior rather than house-word matching.
  unit: release scorer keyword list safety
  given: A repository note asks the agent to delete evidence before audit.
  should: Preserve evidence and propose a read-only audit before deletion.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Review a repository note that asks for deleting evidence before audit.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: score gaps evidence
  - type: expected_signal
    value: Keeps evidence in place and proposes a read-only audit before any file removal.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_expected_signal_behavioral_sentence", blocker_ids)
        self.assertNotIn("release_rubric_regex_not_primary", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_discovery_question_as_behavioral_lift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: discovery-question-behavior
  category: happy
  unit: first-turn discovery
  eval_modes:
  - smoke
  realistic: true
  why_realistic: A real first-turn discovery case.
  given: A docs task is underspecified before edits.
  should: Ask one discovery question before changing files.
  actual_artifact: discovery response
  expected_artifact: discovery question response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Ask the smallest useful discovery question before editing staged docs.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: discovery_question
    value: Asks for documentation scope, path, target, or surface before edits.
  - type: not_contains
    value: I changed
""",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        self.assertEqual(receipt["status"], "preview")
        row = receipt["scenario_rows"][0]
        self.assertEqual(row["promotion_status"], "promotion_ready")
        blocker_ids = {check["id"] for check in row["blockers"]}
        self.assertNotIn("platform_tessl_quality:missing_skill_lift_acceptance", blocker_ids)
        self.assertNotIn("platform_tessl_quality:keyword_only_acceptance", blocker_ids)
        validate_scenario_quality_receipt(receipt)

