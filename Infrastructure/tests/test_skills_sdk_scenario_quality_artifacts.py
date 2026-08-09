from scenario_quality_test_support import *  # noqa: F403


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_builder_blocks_live_handoff_case_without_concrete_output_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: artifactless-release-case
  category: edge
  unit: live handoff output artifact
  eval_modes:
  - release
  - live-private
  realistic: true
  why_realistic: A real docs review case.
  given: A docs task needs a visible result.
  should: Produce a scoreable final artifact.
  actual_artifact: final response
  expected_artifact: proof-backed response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Review the staged docs task.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and blocks unsupported claims.
  - type: must_not
    value: Invents command evidence.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:missing_concrete_output_artifact", blocker_ids)

    def test_builder_blocks_acceptance_type_unsupported_by_text_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: unsupported-text-assertion
  category: edge
  unit: release assertion support
  eval_modes:
  - release
  realistic: true
  why_realistic: Release cases must use assertions executable by the skill eval runner.
  given: A release case uses a must_not assertion that the text-output runner cannot execute.
  should: Block unsupported acceptance types before oss-local release.
  actual_artifact: final response
  expected_artifact: proof-backed response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Review the staged docs task.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and blocks unsupported claims.
  - type: must_not
    value: Invents command evidence.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("text_output_runner_acceptance_supported", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_hidden_reference_dependency_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: hidden-reference-discovery
  category: pressure
  eval_modes:
  - smoke
  realistic: true
  why_realistic: Discovery must work in isolated runners.
  given: A discovery case points at references/discovery-interview.md.
  should: Ask the smallest useful discovery question.
  actual_artifact: discovery response
  expected_artifact: blocked report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Read references/discovery-interview.md, then ask one discovery question.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Asks the smallest useful discovery question.
  - type: must_not
    value: Blocks only because the reference file was unavailable.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:hidden_reference_dependency", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_hidden_input_file_dependency_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: hidden-input-file
  category: edge
  unit: docs ownership fixture
  eval_modes:
  - smoke
  realistic: true
  why_realistic: Release evals often stage docs ownership fixtures.
  given: A generated projection appears stale.
  should: Resolve ownership without editing the projection.
  actual_artifact: artifacts/hidden-input-file.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Inspect generated/sample/SKILL.md and canonical/sample/SKILL.md, then write ownership.md.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names the editable owner and separates refresh evidence.
  - type: not_regex
    value: (?is)edited the generated projection directly
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:hidden_input_file_dependency", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_inline_input_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: inline-input-file
  category: edge
  unit: docs ownership fixture
  eval_modes:
  - smoke
  realistic: true
  why_realistic: Release evals often stage docs ownership fixtures.
  given: A generated projection appears stale.
  should: Resolve ownership without editing the projection.
  actual_artifact: artifacts/inline-input-file.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: |
    Inspect generated/sample/SKILL.md and canonical/sample/SKILL.md, then return the contents for ownership.md in your final answer.

    <file path="generated/sample/SKILL.md">
    stale generated projection
    </file>

    <file path="canonical/sample/SKILL.md">
    canonical source
    </file>
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names the editable owner and separates refresh evidence.
  - type: not_regex
    value: (?is)edited the generated projection directly
""",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        row = receipt["scenario_rows"][0]
        blocker_ids = {check["id"] for check in row["blockers"]}
        self.assertNotIn("platform_tessl_quality:hidden_input_file_dependency", blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_builder_blocks_read_only_file_artifact_side_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: write-file-side-effect
  category: edge
  unit: read-only artifact wording
  eval_modes:
  - smoke
  realistic: true
  why_realistic: OSS lanes run read-only and score final answers.
  given: A docs report is needed.
  should: Return a scoreable artifact without requiring filesystem writes.
  actual_artifact: artifacts/write-file-side-effect.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Write ownership.md for the supplied docs case.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and separates the proof lane.
  - type: not_regex
    value: (?is)(saved|wrote) .*file .*read-only sandbox
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:read_only_file_artifact_side_effect", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_final_answer_file_artifact_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: final-answer-file-artifact
  category: edge
  unit: read-only artifact wording
  eval_modes:
  - smoke
  realistic: true
  why_realistic: OSS lanes run read-only and score final answers.
  given: A docs report is needed.
  should: Return a scoreable artifact without requiring filesystem writes.
  actual_artifact: artifacts/final-answer-file-artifact.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Return the contents for ownership.md in your final answer for the supplied docs case.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and separates the proof lane.
  - type: not_regex
    value: (?is)(saved|wrote) .*file .*read-only sandbox
""",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["scenario_rows"][0]["blockers"]}
        self.assertNotIn("platform_tessl_quality:read_only_file_artifact_side_effect", blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_release_mode_suite_requires_five_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: one-release-case
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: A real release candidate.
  given: One behavioral release scenario exists.
  should: Refuse to call the suite release-ready.
  actual_artifact: final response
  expected_artifact: blocker receipt
  reproduce: ./bin/ask sdk eval run sample
  prompt: Check release readiness.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: blocked
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("release_minimum_scenario_count", blocker_ids)
        self.assertIn("release_pressure_coverage", blocker_ids)
        self.assertIn("release_negative_edge_coverage", blocker_ids)

    def test_release_scenario_set_accepts_grouped_case_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_8_evals_yaml())

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_default_unique"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_scenario_budget"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_ids_exist"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_cases_are_release_mode"]["status"], "pass")
        self.assertEqual(receipt["scenario_count"], 8)
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_requires_exact_integer_budget_contract(self) -> None:
        payload = _release_set_8_evals_yaml().replace("  target_scenarios: 8", "  target_scenarios: '8'", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in raised.exception.receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_scenario_budget"]["status"], "blocker")

    def test_release_scenario_set_accepts_flat_case_lists(self) -> None:
        payload = _release_set_8_evals_yaml()
        flat_cases = "\n".join(
            [
                "release_scenario_sets:",
                "- id: sample-release-8-v1",
                "  default: true",
                "  minimum_scenarios: 5",
                "  target_scenarios: 8",
                "  maximum_scenarios: 10",
                "  cases:",
                *[f"  - foundation-{index}" for index in range(1, 3)],
                *[f"  - behavioral-{index}" for index in range(1, 7)],
                "cases:",
            ]
        )
        start = payload.index("release_scenario_sets:")
        end = payload.index("cases:", start)
        payload = payload[:start] + flat_cases + payload[end + len("cases:") :]
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_scenario_budget"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_ids_exist"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_cases_are_release_mode"]["status"], "pass")
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_rejects_more_than_ten(self) -> None:
        payload = _release_set_8_evals_yaml()
        flat_cases = "\n".join(
            [
                "release_scenario_sets:",
                "- id: sample-release-11-v1",
                "  default: true",
                "  minimum_scenarios: 5",
                "  target_scenarios: 8",
                "  maximum_scenarios: 10",
                "  cases:",
                *[f"  - foundation-{index}" for index in range(1, 3)],
                *[f"  - behavioral-{index}" for index in range(1, 10)],
                "cases:",
            ]
        )
        start = payload.index("release_scenario_sets:")
        end = payload.index("cases:", start)
        payload = payload[:start] + flat_cases + payload[end + len("cases:") :]
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in raised.exception.receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_scenario_budget"]["status"], "blocker")
        self.assertIn(
            "sample-release-11-v1:count:11:minimum:5:target:8:maximum:10",
            check_map["release_scenario_set_scenario_budget"]["evidence"],
        )
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_release_scenario_set_rejects_duplicate_ids(self) -> None:
        duplicate_set = "\n".join(
            [
                "- id: sample-release-8-v1",
                "  default: false",
                "  minimum_scenarios: 5",
                "  target_scenarios: 8",
                "  maximum_scenarios: 10",
                "  groups:",
                "    foundation_smoke:",
                "    - foundation-1",
                "    - foundation-2",
                "    behavioral_release:",
                *[f"    - behavioral-{index}" for index in range(1, 7)],
            ]
        )
        payload = _release_set_8_evals_yaml().replace("cases:", f"{duplicate_set}\ncases:", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_scenario_set_ids_unique", blocker_ids)

    def test_release_rubric_requires_binary_evidence_and_failure_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: weak-release-rubric
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: A real release candidate.
  given: A pressure scenario has a vague one-line oracle.
  should: Refuse the vague rubric before release.
  actual_artifact: final response
  expected_artifact: blocker receipt
  reproduce: ./bin/ask sdk eval run sample
  prompt: Check release rubric readiness.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Handles it well.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_binary_items", blocker_ids)
        self.assertIn("release_rubric_evidence_anchored", blocker_ids)
        self.assertIn("release_rubric_failure_guard", blocker_ids)

    def test_registry_dependency_claim_requires_separate_trust_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: weak-registry-case
  category: pressure
  eval_modes:
  - smoke
  realistic: true
  prompt: A Registry tile has a high review score. Decide whether to use it.
  claim_ids:
  - sdk-scenario-generator.registry-dependency
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Uses the review score.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("registry_dependency_intake_complete", blockers)
        self.assertIn("registry_security_warning_blocks_use", blockers)
        self.assertIn("weak-registry-case:security", blockers["registry_dependency_intake_complete"]["evidence"])
        self.assertIn("weak-registry-case:version_or_pin", blockers["registry_dependency_intake_complete"]["evidence"])
        self.assertIn("weak-registry-case:local_validation", blockers["registry_dependency_intake_complete"]["evidence"])

