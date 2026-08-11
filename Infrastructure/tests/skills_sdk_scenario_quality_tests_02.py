from skills_sdk_scenario_quality_tests_01 import *  # noqa: F403

class TestSkillsSdkScenarioQuality(_SkillsSdkScenarioQualityBase):
    def test_release_scenario_set_accepts_flat_case_lists(self) -> None:
        payload = _release_set_8_evals_yaml()
        flat_cases = '\n'.join(['release_scenario_sets:', '- id: sample-release-8-v1', '  default: true', '  minimum_scenarios: 5', '  target_scenarios: 8', '  maximum_scenarios: 10', '  cases:', *[f'  - foundation-{index}' for index in range(1, 3)], *[f'  - behavioral-{index}' for index in range(1, 7)], 'cases:'])
        start = payload.index('release_scenario_sets:')
        end = payload.index('cases:', start)
        payload = payload[:start] + flat_cases + payload[end + len('cases:'):]
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        check_map = {check['id']: check for check in receipt['quality_checks']}
        self.assertEqual(check_map['release_scenario_set_scenario_budget']['status'], 'pass')
        self.assertEqual(check_map['release_scenario_set_ids_exist']['status'], 'pass')
        self.assertEqual(check_map['release_scenario_set_cases_are_release_mode']['status'], 'pass')
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_rejects_more_than_ten(self) -> None:
        payload = _release_set_8_evals_yaml()
        flat_cases = '\n'.join(['release_scenario_sets:', '- id: sample-release-11-v1', '  default: true', '  minimum_scenarios: 5', '  target_scenarios: 8', '  maximum_scenarios: 10', '  cases:', *[f'  - foundation-{index}' for index in range(1, 3)], *[f'  - behavioral-{index}' for index in range(1, 10)], 'cases:'])
        start = payload.index('release_scenario_sets:')
        end = payload.index('cases:', start)
        payload = payload[:start] + flat_cases + payload[end + len('cases:'):]
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        check_map = {check['id']: check for check in raised.exception.receipt['quality_checks']}
        self.assertEqual(check_map['release_scenario_set_scenario_budget']['status'], 'blocker')
        self.assertIn('sample-release-11-v1:count:11:minimum:5:target:8:maximum:10', check_map['release_scenario_set_scenario_budget']['evidence'])
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_release_scenario_set_rejects_duplicate_ids(self) -> None:
        duplicate_set = '\n'.join(['- id: sample-release-8-v1', '  default: false', '  minimum_scenarios: 5', '  target_scenarios: 8', '  maximum_scenarios: 10', '  groups:', '    foundation_smoke:', '    - foundation-1', '    - foundation-2', '    behavioral_release:', *[f'    - behavioral-{index}' for index in range(1, 7)]])
        payload = _release_set_8_evals_yaml().replace('cases:', f'{duplicate_set}\ncases:', 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_scenario_set_ids_unique', blocker_ids)

    def test_release_rubric_requires_binary_evidence_and_failure_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: weak-release-rubric\n  category: pressure\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: A real release candidate.\n  given: A pressure scenario has a vague one-line oracle.\n  should: Refuse the vague rubric before release.\n  actual_artifact: final response\n  expected_artifact: blocker receipt\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Check release rubric readiness.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Handles it well.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_rubric_binary_items', blocker_ids)
        self.assertIn('release_rubric_evidence_anchored', blocker_ids)
        self.assertIn('release_rubric_failure_guard', blocker_ids)

    def test_registry_dependency_claim_requires_separate_trust_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: weak-registry-case\n  category: pressure\n  eval_modes:\n  - smoke\n  realistic: true\n  prompt: A Registry tile has a high review score. Decide whether to use it.\n  claim_ids:\n  - sdk-scenario-generator.registry-dependency\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Uses the review score.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        receipt = raised.exception.receipt
        blockers = {check['id']: check for check in receipt['blockers']}
        self.assertIn('registry_dependency_intake_complete', blockers)
        self.assertIn('registry_security_warning_blocks_use', blockers)
        self.assertIn('weak-registry-case:security', blockers['registry_dependency_intake_complete']['evidence'])
        self.assertIn('weak-registry-case:version_or_pin', blockers['registry_dependency_intake_complete']['evidence'])
        self.assertIn('weak-registry-case:local_validation', blockers['registry_dependency_intake_complete']['evidence'])

    def test_scenario_set_parity_accepts_canonical_and_reviewed_fixture_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: canonical-case\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs scenario parity\n  given: A release fixture needs proof that SDK, staged Tessl, and Tessl score scenarios are the same set.\n  should: Return docs-output.md content with source-backed validation claims and no invented command proof.\n  actual_artifact: docs-output.md\n  expected_artifact: docs-output.md\n  prompt: Return the docs-output.md content as a proof-backed docs note for the scenario parity review.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.\n")
            reviewed_dir = skill_dir / 'references' / 'evals'
            reviewed_dir.mkdir()
            (reviewed_dir / 'eval.visual-evidence-decision.md').write_text('# Visual evidence decision\n', encoding='utf-8')
            ids = ['canonical-case', 'generated-eval.visual-evidence-decision']
            staged_json = _write_staged_tessl_json(temp_path / 'staged.json', ids)
            score_json = _write_tessl_score_json(temp_path / 'score.json', ids)
            receipt = build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_staged_json=staged_json, tessl_score_json=score_json)
        self.assertEqual(receipt['scenario_set_parity']['canonical_count'], 1)
        self.assertEqual(receipt['scenario_set_parity']['reviewed_fixture_count'], 1)
        self.assertFalse(receipt['blockers'])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_normalizes_tessl_staged_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: docs/foo\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs scenario parity\n  given: A scenario id contains characters that Tessl staging normalizes.\n  should: Return docs-output.md content with source-backed validation claims and no invented command proof.\n  actual_artifact: docs-output.md\n  expected_artifact: docs-output.md\n  prompt: Return the docs-output.md content as a proof-backed docs note for the scenario parity review.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.\n")
            staged_json = _write_staged_tessl_json(temp_path / 'staged.json', ['docs-foo'])
            score_json = _write_tessl_score_json(temp_path / 'score.json', ['docs/foo'])
            receipt = build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_staged_json=staged_json, tessl_score_json=score_json)
        self.assertEqual(receipt['scenario_set_parity']['missing_from_staged'], [])
        self.assertEqual(receipt['scenario_set_parity']['extra_in_staged'], [])
        self.assertEqual(receipt['scenario_set_parity']['missing_from_score_receipt'], [])
        self.assertFalse(receipt['blockers'])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_uses_selected_release_set_universe(self) -> None:
        payload = _release_set_8_evals_yaml() + '\n- id: non-release-doc-case\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs scenario parity\n  given: A non-release documentation scenario belongs to the full suite but not the selected release set.\n  should: Return non-release-doc-case.md content with source-backed validation claims.\n  actual_artifact: non-release-doc-case.md\n  expected_artifact: non-release-doc-case.md\n  prompt: Return the non-release-doc-case.md content.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns non-release-doc-case.md content with source-backed validation claims.\n'
        release_ids = [f'foundation-{index}' for index in range(1, 3)] + [f'behavioral-{index}' for index in range(1, 7)]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, payload)
            reviewed_dir = skill_dir / 'references' / 'evals'
            reviewed_dir.mkdir()
            (reviewed_dir / 'eval.visual-evidence-decision.md').write_text('# Visual evidence decision\n', encoding='utf-8')
            ids = [*release_ids, 'generated-eval.visual-evidence-decision']
            staged_json = _write_staged_tessl_json(temp_path / 'staged.json', ids)
            score_json = _write_tessl_score_json(temp_path / 'score.json', ids)
            receipt = build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_staged_json=staged_json, tessl_score_json=score_json, scenario_set='sample-release-8-v1')
        self.assertEqual(receipt['scenario_count'], 8)
        self.assertEqual(receipt['scenario_set_parity']['canonical_count'], 8)
        self.assertEqual(receipt['scenario_set_parity']['reviewed_fixture_count'], 1)
        self.assertFalse(receipt['blockers'])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_unknown_selected_release_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, _release_set_8_evals_yaml())
            release_ids = [f'foundation-{index}' for index in range(1, 3)] + [f'behavioral-{index}' for index in range(1, 7)]
            staged_json = _write_staged_tessl_json(temp_path / 'staged.json', release_ids)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_staged_json=staged_json, scenario_set='missing-release-set')
        blockers = {check['id']: check for check in raised.exception.receipt['blockers']}
        self.assertIn('release_scenario_set_selector_valid', blockers)
        self.assertEqual(blockers['release_scenario_set_selector_valid']['evidence'], ['scenario_set:missing-release-set:not_found_or_empty'])
        self.assertEqual(raised.exception.receipt['scenario_set_parity']['canonical_count'], 0)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_scenario_set_parity_blocks_tessl_case_id_collisions(self) -> None:
        evals_text = "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: docs/foo\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs slash scenario\n  given: A docs scenario id contains a slash.\n  should: Return docs-slash.md content with evidence-backed documentation behavior.\n  actual_artifact: docs-slash.md\n  expected_artifact: docs-slash.md\n  prompt: Return docs-slash.md content.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns docs-slash.md content with evidence-backed documentation behavior.\n- id: docs-foo\n  category: edge\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs dash scenario\n  given: A docs scenario id already contains the Tessl-safe dash form.\n  should: Return docs-dash.md content with evidence-backed documentation behavior.\n  actual_artifact: docs-dash.md\n  expected_artifact: docs-dash.md\n  prompt: Return docs-dash.md content.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns docs-dash.md content with evidence-backed documentation behavior.\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, evals_text)
            staged_json = _write_staged_tessl_json(temp_path / 'staged.json', ['docs-foo'])
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_staged_json=staged_json)
        check_map = {check['id']: check for check in raised.exception.receipt['quality_checks']}
        self.assertEqual(check_map['scenario_set_tessl_case_ids_unique']['status'], 'blocker')
        self.assertEqual(check_map['scenario_set_tessl_case_ids_unique']['evidence'], ['docs-foo:docs-foo,docs/foo'])
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_scenario_set_parity_counts_tessl_score_wins_as_covered_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, _two_case_score_parity_evals_yaml())
            score_json = _write_tessl_score_json(temp_path / 'score.json', ['tied-case'], wins=['usage-win-case'])
            receipt = build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_score_json=score_json)
        self.assertEqual(receipt['scenario_set_parity']['score_receipt_path_count'], 2)
        self.assertEqual(receipt['scenario_set_parity']['score_receipt_declared_count'], 2)
        self.assertEqual(receipt['scenario_set_parity']['missing_from_score_receipt'], [])
        self.assertFalse(receipt['blockers'])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_missing_tessl_score_win_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, _two_case_score_parity_evals_yaml())
            score_json = _write_tessl_score_json(temp_path / 'score.json', ['tied-case'], scenario_count=2)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_score_json=score_json)
        receipt = raised.exception.receipt
        blockers = {check['id']: check for check in receipt['blockers']}
        self.assertIn('scenario_set_score_receipt_matches_sdk', blockers)
        self.assertEqual(receipt['scenario_set_parity']['score_receipt_path_count'], 1)
        self.assertEqual(receipt['scenario_set_parity']['missing_from_score_receipt'], ['usage-win-case'])
        self.assertIn('missing:usage-win-case', blockers['scenario_set_score_receipt_matches_sdk']['evidence'])
        validate_scenario_quality_receipt(receipt)

    def test_minimal_yaml_loader_preserves_quoted_regex_hashes(self) -> None:
        payload = _load_minimal_evals_yaml("schema_version: '2.0'\nskill_name: sample\ncases:\n- id: quoted-regex\n  category: edge\n  eval_modes:\n  - release\n  realistic: true\n  unit: no invention\n  given: A staged excerpt lacks command evidence.\n  should: Do not invent setup commands or validation commands.\n  prompt: Use only the supplied excerpt. Do not invent setup commands or validation commands.\n  actual_artifact: artifacts/quoted-regex.md\n  expected_artifact: artifacts/quoted-regex.md\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: not_regex\n    value: '(?i)(#[a-z0-9_-]+|Slack channel|pytest|uv|mise|\\./bin/ask|setup command|validation command)'\n")
        acceptance = payload['cases'][0]['acceptance']
        self.assertEqual(acceptance[0]['type'], 'not_regex')
        self.assertIn('#[a-z0-9_-]+', acceptance[0]['value'])
        self.assertIn('\\./bin/ask', acceptance[0]['value'])

    def test_scenario_set_parity_blocks_staged_tessl_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: canonical-case\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs scenario parity\n  given: A release fixture needs proof that SDK and staged Tessl scenarios are the same set.\n  should: Return docs-output.md content with source-backed validation claims and no invented command proof.\n  actual_artifact: docs-output.md\n  expected_artifact: docs-output.md\n  prompt: Return the docs-output.md content as a proof-backed docs note for the staged scenario parity review.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.\n")
            staged_json = _write_staged_tessl_json(temp_path / 'staged.json', ['canonical-case', 'unexpected-extra'])
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_staged_json=staged_json)
        receipt = raised.exception.receipt
        blocker_ids = {check['id'] for check in receipt['blockers']}
        self.assertIn('scenario_set_staged_tessl_matches_sdk', blocker_ids)
        self.assertEqual(receipt['scenario_set_parity']['extra_in_staged'], ['unexpected-extra'])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_tessl_score_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: canonical-case\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  unit: docs scenario parity\n  given: A release fixture needs proof that SDK and Tessl score receipt scenarios are the same set.\n  should: Return docs-output.md content with source-backed validation claims and no invented command proof.\n  actual_artifact: docs-output.md\n  expected_artifact: docs-output.md\n  prompt: Return the docs-output.md content as a proof-backed docs note for the Tessl score parity review.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.\n")
            score_json = _write_tessl_score_json(temp_path / 'score.json', ['canonical-case'], scenario_count=32)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(temp_path, source_path=skill_dir, query='sample_skill', tessl_score_json=score_json)
        receipt = raised.exception.receipt
        blockers = {check['id']: check for check in receipt['blockers']}
        self.assertIn('scenario_set_score_receipt_matches_sdk', blockers)
        self.assertIn('declared_count:32:expected:1', blockers['scenario_set_score_receipt_matches_sdk']['evidence'])
        validate_scenario_quality_receipt(receipt)

__all__ = [name for name in globals() if not name.startswith("__")]
