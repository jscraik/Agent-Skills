from scenario_quality_test_support import *  # noqa: F403


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_scenario_set_parity_accepts_canonical_and_reviewed_fixture_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: canonical-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK, staged Tessl, and Tessl score scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the scenario parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            reviewed_dir = skill_dir / "references" / "evals"
            reviewed_dir.mkdir()
            (reviewed_dir / "eval.visual-evidence-decision.md").write_text("# Visual evidence decision\n", encoding="utf-8")
            ids = ["canonical-case", "generated-eval.visual-evidence-decision"]
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ids)
            score_json = _write_tessl_score_json(temp_path / "score.json", ids)

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_staged_json=staged_json,
                tessl_score_json=score_json,
            )

        self.assertEqual(receipt["scenario_set_parity"]["canonical_count"], 1)
        self.assertEqual(receipt["scenario_set_parity"]["reviewed_fixture_count"], 1)
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_normalizes_tessl_staged_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: docs/foo
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A scenario id contains characters that Tessl staging normalizes.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the scenario parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ["docs-foo"])
            score_json = _write_tessl_score_json(temp_path / "score.json", ["docs/foo"])

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_staged_json=staged_json,
                tessl_score_json=score_json,
            )

        self.assertEqual(receipt["scenario_set_parity"]["missing_from_staged"], [])
        self.assertEqual(receipt["scenario_set_parity"]["extra_in_staged"], [])
        self.assertEqual(receipt["scenario_set_parity"]["missing_from_score_receipt"], [])
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_uses_selected_release_set_universe(self) -> None:
        payload = _release_set_8_evals_yaml() + """
- id: non-release-doc-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A non-release documentation scenario belongs to the full suite but not the selected release set.
  should: Return non-release-doc-case.md content with source-backed validation claims.
  actual_artifact: non-release-doc-case.md
  expected_artifact: non-release-doc-case.md
  prompt: Return the non-release-doc-case.md content.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns non-release-doc-case.md content with source-backed validation claims.
"""
        release_ids = [f"foundation-{index}" for index in range(1, 3)] + [f"behavioral-{index}" for index in range(1, 7)]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, payload)
            reviewed_dir = skill_dir / "references" / "evals"
            reviewed_dir.mkdir()
            (reviewed_dir / "eval.visual-evidence-decision.md").write_text("# Visual evidence decision\n", encoding="utf-8")
            ids = [*release_ids, "generated-eval.visual-evidence-decision"]
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ids)
            score_json = _write_tessl_score_json(temp_path / "score.json", ids)

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_staged_json=staged_json,
                tessl_score_json=score_json,
                scenario_set="sample-release-8-v1",
            )

        self.assertEqual(receipt["scenario_count"], 8)
        self.assertEqual(receipt["scenario_set_parity"]["canonical_count"], 8)
        self.assertEqual(receipt["scenario_set_parity"]["reviewed_fixture_count"], 1)
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_unknown_selected_release_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, _release_set_8_evals_yaml())
            release_ids = [f"foundation-{index}" for index in range(1, 3)] + [f"behavioral-{index}" for index in range(1, 7)]
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", release_ids)

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_staged_json=staged_json,
                    scenario_set="missing-release-set",
                )

        blockers = {check["id"]: check for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_scenario_set_selector_valid", blockers)
        self.assertEqual(
            blockers["release_scenario_set_selector_valid"]["evidence"],
            ["scenario_set:missing-release-set:not_found_or_empty"],
        )
        self.assertEqual(raised.exception.receipt["scenario_set_parity"]["canonical_count"], 0)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_scenario_set_parity_blocks_tessl_case_id_collisions(self) -> None:
        evals_text = """schema_version: '2.0'
skill_name: sample
cases:
- id: docs/foo
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs slash scenario
  given: A docs scenario id contains a slash.
  should: Return docs-slash.md content with evidence-backed documentation behavior.
  actual_artifact: docs-slash.md
  expected_artifact: docs-slash.md
  prompt: Return docs-slash.md content.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-slash.md content with evidence-backed documentation behavior.
- id: docs-foo
  category: edge
  eval_modes:
  - smoke
  realistic: true
  unit: docs dash scenario
  given: A docs scenario id already contains the Tessl-safe dash form.
  should: Return docs-dash.md content with evidence-backed documentation behavior.
  actual_artifact: docs-dash.md
  expected_artifact: docs-dash.md
  prompt: Return docs-dash.md content.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-dash.md content with evidence-backed documentation behavior.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, evals_text)
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ["docs-foo"])

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_staged_json=staged_json,
                )

        check_map = {check["id"]: check for check in raised.exception.receipt["quality_checks"]}
        self.assertEqual(check_map["scenario_set_tessl_case_ids_unique"]["status"], "blocker")
        self.assertEqual(check_map["scenario_set_tessl_case_ids_unique"]["evidence"], ["docs-foo:docs-foo,docs/foo"])
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_scenario_set_parity_counts_tessl_score_wins_as_covered_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                _two_case_score_parity_evals_yaml(),
            )
            score_json = _write_tessl_score_json(temp_path / "score.json", ["tied-case"], wins=["usage-win-case"])

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_score_json=score_json,
            )

        self.assertEqual(receipt["scenario_set_parity"]["score_receipt_path_count"], 2)
        self.assertEqual(receipt["scenario_set_parity"]["score_receipt_declared_count"], 2)
        self.assertEqual(receipt["scenario_set_parity"]["missing_from_score_receipt"], [])
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_missing_tessl_score_win_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                _two_case_score_parity_evals_yaml(),
            )
            score_json = _write_tessl_score_json(temp_path / "score.json", ["tied-case"], scenario_count=2)

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_score_json=score_json,
                )

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("scenario_set_score_receipt_matches_sdk", blockers)
        self.assertEqual(receipt["scenario_set_parity"]["score_receipt_path_count"], 1)
        self.assertEqual(receipt["scenario_set_parity"]["missing_from_score_receipt"], ["usage-win-case"])
        self.assertIn("missing:usage-win-case", blockers["scenario_set_score_receipt_matches_sdk"]["evidence"])
        validate_scenario_quality_receipt(receipt)

    def test_minimal_yaml_loader_preserves_quoted_regex_hashes(self) -> None:
        payload = _load_minimal_evals_yaml(
            """schema_version: '2.0'
skill_name: sample
cases:
- id: quoted-regex
  category: edge
  eval_modes:
  - release
  realistic: true
  unit: no invention
  given: A staged excerpt lacks command evidence.
  should: Do not invent setup commands or validation commands.
  prompt: Use only the supplied excerpt. Do not invent setup commands or validation commands.
  actual_artifact: artifacts/quoted-regex.md
  expected_artifact: artifacts/quoted-regex.md
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: not_regex
    value: '(?i)(#[a-z0-9_-]+|Slack channel|pytest|uv|mise|\\./bin/ask|setup command|validation command)'
"""
        )

        acceptance = payload["cases"][0]["acceptance"]
        self.assertEqual(acceptance[0]["type"], "not_regex")
        self.assertIn("#[a-z0-9_-]+", acceptance[0]["value"])
        self.assertIn("\\./bin/ask", acceptance[0]["value"])

    def test_scenario_set_parity_blocks_staged_tessl_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: canonical-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK and staged Tessl scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the staged scenario parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ["canonical-case", "unexpected-extra"])

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_staged_json=staged_json,
                )

        receipt = raised.exception.receipt
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("scenario_set_staged_tessl_matches_sdk", blocker_ids)
        self.assertEqual(receipt["scenario_set_parity"]["extra_in_staged"], ["unexpected-extra"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_tessl_score_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: canonical-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK and Tessl score receipt scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the Tessl score parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            score_json = _write_tessl_score_json(temp_path / "score.json", ["canonical-case"], scenario_count=32)

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_score_json=score_json,
                )

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("scenario_set_score_receipt_matches_sdk", blockers)
        self.assertIn("declared_count:32:expected:1", blockers["scenario_set_score_receipt_matches_sdk"]["evidence"])
        validate_scenario_quality_receipt(receipt)

