from skills_sdk_scenario_quality_tests_core import *  # noqa: F403
from skills_sdk_scenario_quality_tests_core import (
    _SkillsSdkScenarioQualityBase,
    _command_env,
    _mixed_pinned_and_text_registry_source_evals_yaml,
    _nested_registry_reference_evals_yaml,
    _nested_registry_source_evals_yaml,
    _plain_evals_yaml,
    _registry_reference_evals_yaml,
    _registry_source_evals_yaml,
    _release_set_8_evals_yaml,
    _run_ask,
    _write_adaptation_receipt,
    _write_skill_with_evals,
    _yaml_safe_load,
)

class TestSkillsSdkScenarioQuality(_SkillsSdkScenarioQualityBase):
    def test_scenario_quality_command_builds_preview(self) -> None:
        process = _run_ask('sdk', 'eval', 'scenario-quality', FIXTURE_SKILL, '--preview', '--json', '--robot')
        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope['data']['skills_sdk_eval_scenario_quality']
        receipt = payload['receipt']
        self.assertEqual(payload['status'], 'preview')
        self.assertEqual(receipt['scenario_count'], 1)
        self.assertEqual(receipt['promotion_ready_count'], 1)
        self.assertFalse(receipt['mutation_performed'])
        self.assertFalse(receipt['promotion_performed'])

    def test_scenario_quality_requires_preview_flag(self) -> None:
        process = _run_ask('sdk', 'eval', 'scenario-quality', FIXTURE_SKILL, '--json', '--robot')
        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope['status'], 'error')
        self.assertIn('requires --preview', envelope['errors'][0]['message'])

    def test_builder_blocks_missing_evals_yaml(self) -> None:
        with self.assertRaises(ScenarioQualityError) as raised:
            build_scenario_quality_receipt(REPO_ROOT, source_path=REPO_ROOT / INVALID_SKILL / 'SKILL.md', query=INVALID_SKILL)
        receipt = raised.exception.receipt
        self.assertEqual(receipt['status'], 'blocked')
        self.assertEqual(receipt['scenario_count'], 0)
        self.assertTrue(any((check['id'] == 'evals_yaml_present' for check in receipt['blockers'])))

    def test_builder_blocks_direct_registry_reference_in_evals_without_adaptation_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml())
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        self.assertEqual(receipt['status'], 'blocked')
        self.assertTrue(any((check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for check in receipt['blockers'])))

    def test_builder_allows_registry_reference_after_sdk_adaptation_receipt(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id)
            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        self.assertEqual(receipt['status'], 'preview')
        self.assertEqual(receipt['blocked_count'], 0)
        quality_check_ids = {check['id']: check['status'] for check in receipt['quality_checks']}
        self.assertEqual(quality_check_ids['registry_reference_requires_sdk_adaptation_receipt'], 'pass')

    def test_builder_allows_repo_relative_target_skill_path_in_adaptation_receipt(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            target_path = skill_dir.relative_to(REPO_ROOT).as_posix()
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, target_path=target_path)
            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        self.assertEqual(receipt['status'], 'preview')
        self.assertEqual(receipt['blocked_count'], 0)

    def test_builder_blocks_basename_only_target_skill_path_in_adaptation_receipt(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, target_path=skill_dir.name)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('target_skill_mismatch', evidence)

    def test_builder_blocks_wrong_package_id_in_adaptation_receipt(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, package_id='other-skill')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('target_skill_mismatch', evidence)

    def test_builder_allows_nested_registry_reference_after_sdk_adaptation_receipt(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id)
            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        self.assertEqual(receipt['status'], 'preview')
        self.assertEqual(receipt['blocked_count'], 0)

    def test_builder_allows_nested_registry_source_after_sdk_adaptation_receipt(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_source_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id)
            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        self.assertEqual(receipt['status'], 'preview')
        self.assertEqual(receipt['blocked_count'], 0)

    def test_builder_blocks_registry_source_digest_mismatch(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_source_evals_yaml(registry_id, digest='sha256:expected'))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, digest='sha256:stale')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('registry_source_mismatch', evidence)

    def test_builder_blocks_nested_registry_source_version_mismatch(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_source_evals_yaml(registry_id, version='0.2.0'))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, version='0.1.0')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('registry_source_mismatch', evidence)

    def test_builder_blocks_nested_registry_source_digest_mismatch(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_source_evals_yaml(registry_id, digest='sha256:expected'))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, digest='sha256:stale')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('registry_source_mismatch', evidence)

    def test_builder_blocks_pass_adaptation_receipt_with_failed_validation_row(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, validation_status='fail')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('schema_invalid', evidence)
        self.assertIn('validation[0].status:const', evidence)

    def test_builder_blocks_registry_source_id_prefix_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_reference_evals_yaml('registry://shared/proof-boundary-v2'))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id='registry://shared/proof-boundary')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('registry_source_mismatch', evidence)

    def test_builder_blocks_partial_adaptation_receipt_missing_schema_required_fields(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, include_full_schema_fields=False)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        evidence = '\n'.join((evidence for check in receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('receipt_missing_required_fields', evidence)
        self.assertIn('operation', evidence)

    def test_builder_blocks_adaptation_receipt_missing_full_schema_fields(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            receipt_path = _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id)
            payload = json.loads(receipt_path.read_text(encoding='utf-8'))
            payload.pop('validation')
            payload.pop('mutation_manifest')
            receipt_path.write_text(json.dumps(payload), encoding='utf-8')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        evidence = '\n'.join((evidence for check in raised.exception.receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('receipt_missing_required_fields', evidence)
        self.assertIn('validation', evidence)
        self.assertIn('mutation_manifest', evidence)

    def test_builder_blocks_text_duplicate_when_pinned_registry_source_digest_mismatches(self) -> None:
        registry_id = 'registry://shared/proof-boundary'
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _mixed_pinned_and_text_registry_source_evals_yaml(registry_id, digest='sha256:expected'))
            _write_adaptation_receipt(skill_dir, case_id='proof-boundary', registry_id=registry_id, digest='sha256:stale')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        evidence = '\n'.join((evidence for check in raised.exception.receipt['blockers'] if check['id'] == 'registry_reference_requires_sdk_adaptation_receipt' for evidence in check['evidence']))
        self.assertIn('registry_source_mismatch', evidence)

    def test_builder_blocks_direct_registry_reference_in_skill_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _plain_evals_yaml())
            (skill_dir / 'SKILL.md').write_text('---\nname: sample\n---\n# Sample\nLoad registry://shared/proof-boundary directly.\n', encoding='utf-8')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())
        receipt = raised.exception.receipt
        self.assertTrue(any((check['id'] == 'registry_reference_not_in_skill_entrypoint' for check in receipt['blockers'])))

    def test_no_direct_registry_validator_blocks_unauthenticated_ad_hoc_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml())
            process = subprocess.run([sys.executable, 'Infrastructure/scripts/validation-and-linting/validate_no_direct_registry_scenario_use.py', skill_dir.as_posix(), '--json'], cwd=REPO_ROOT, env=_command_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(process.returncode, 1)
        payload = json.loads(process.stdout)
        self.assertEqual(payload['status'], 'blocked')
        self.assertEqual(payload['blockers'][0]['id'], 'registry_reference_requires_sdk_adaptation_receipt')

    def test_yaml_fallback_parses_fixture_without_subprocess(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == 'yaml':
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)
        evals_text = (REPO_ROOT / FIXTURE_SKILL / 'references/evals.yaml').read_text(encoding='utf-8')
        with mock.patch('builtins.__import__', side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)
        self.assertEqual(payload['cases'][0]['id'], 'happy-scenario-quality')
        self.assertEqual(payload['cases'][0]['eval_modes'], ['smoke'])
        self.assertIsInstance(payload['cases'][0]['deterministic_checks'], dict)

    def test_yaml_fallback_ignores_claims_and_parses_root_aligned_cases(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == 'yaml':
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)
        evals_text = "schema_version: '2.0'\nskill_name: sample\nclaims:\n- id: sample.claim\n  statement: ignored by fallback\ncases:\n- id: root-aligned-case\n  category: pressure\n  realistic: true\n  eval_modes:\n  - smoke\n  prompt: Check the root-aligned case parser.\n  acceptance:\n  - type: expected_signal\n    value: parsed\n      continuation\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n"
        with mock.patch('builtins.__import__', side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)
        self.assertEqual(payload['cases'][0]['id'], 'root-aligned-case')
        self.assertEqual(payload['cases'][0]['eval_modes'], ['smoke'])
        self.assertEqual(payload['cases'][0]['acceptance'][0]['value'], 'parsed continuation')
        self.assertEqual(payload['cases'][0]['claim_ids'], ['sample.claim'])
        self.assertIsInstance(payload['cases'][0]['deterministic_checks'], dict)

    def test_yaml_fallback_parses_legacy_expect_lists(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == 'yaml':
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)
        evals_text = 'schema_version: 1\nskill: sample\nclaims:\n- id: sample.claim\n  statement: ignored by fallback\ncases:\n- id: x-writer-style-case\n  claim_ids:\n  - sample.claim\n  input: |-\n    Turn this brief into an X launch thread.\n  expect:\n  - Includes two hook variants.\n  - Keeps publication status draft-only when request_user_input\n    is unavailable.\n  - Keeps implementation ownership clear: Codex writes code; Jamie validates.\n  prompt: |-\n    Can you turn this brief into an X launch thread?\n  acceptance:\n  - type: regex\n    value: "(?is)(claim_authority.*limited to supplied brief|no external factual claims)"\n  eval_modes:\n  - smoke\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n'
        with mock.patch('builtins.__import__', side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)
        case = payload['cases'][0]
        self.assertEqual(case['id'], 'x-writer-style-case')
        self.assertEqual(case['expect'][0], 'Includes two hook variants.')
        self.assertEqual(case['expect'][1], 'Keeps publication status draft-only when request_user_input is unavailable.')
        self.assertEqual(case['expect'][2], 'Keeps implementation ownership clear: Codex writes code; Jamie validates.')
        self.assertEqual(case['eval_modes'], ['smoke'])
        self.assertEqual(case['claim_ids'], ['sample.claim'])
        self.assertIsInstance(case['deterministic_checks'], dict)

    def test_yaml_fallback_rejects_invalid_scalar_continuation(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == 'yaml':
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)
        evals_text = "schema_version: '2.0'\ncases:\n- id: invalid-continuation\n  realistic: true\n    continuation\n"
        with mock.patch('builtins.__import__', side_effect=import_without_yaml), mock.patch('ask.skills_sdk.scenario_quality.subprocess.run', side_effect=FileNotFoundError()):
            with self.assertRaises(ValueError):
                _yaml_safe_load(evals_text)

    def test_builder_blocks_pyyaml_parse_errors(self) -> None:

        class FakeYAMLError(Exception):
            pass

        class FakeYaml:
            YAMLError = FakeYAMLError

            @staticmethod
            def safe_load(_text: str) -> object:
                raise FakeYAMLError('bad yaml')
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), 'cases:\n- id: malformed\n  prompt: [unterminated\n')
            with mock.patch.dict(sys.modules, {'yaml': FakeYaml}), self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        receipt = raised.exception.receipt
        self.assertEqual(receipt['status'], 'blocked')
        blocker_ids = {check['id'] for check in receipt['blockers']}
        self.assertIn('evals_yaml_parse', blocker_ids)

    def test_builder_blocks_malformed_text_field_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), 'schema_version: 1\ncases:\n- id: malformed-text-field\n  eval_modes:\n  - smoke\n  prompt: Check structured output.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: text_field_in\n    value: draft_only\n')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('typed_text_field_assertions_valid', blocker_ids)

    def test_builder_blocks_typed_field_assertions_with_empty_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), 'schema_version: 1\ncases:\n- id: malformed-empty-values\n  eval_modes:\n  - smoke\n  prompt: Check structured output.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: text_field_in\n    field: status\n    values: []\n')
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('typed_text_field_assertions_valid', blocker_ids)

    def test_builder_blocks_regex_against_known_structured_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: 1\ncases:\n- id: regex-structured-field\n  eval_modes:\n  - smoke\n  prompt: Check structured output.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: regex\n    value: 'publication_gate_status:\\s*draft_only'\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('structured_fields_use_typed_assertions', blocker_ids)

    def test_builder_blocks_tessl_quality_mismatch_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: keyword-only-mismatch\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  prompt: Ask for an evidence-backed validation summary.\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: regex\n    value: '(?is)(evidence|validation)'\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:keyword_only_acceptance', blocker_ids)
        self.assertIn('platform_tessl_quality:missing_scenario_context', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_tessl_semantic_answer_leakage_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: leaked-scorecard\n  category: happy\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Maintainers ask for repository readiness reviews before release.\n  unit: repo readiness scorecard\n  given: A user needs a repository readiness audit for routing, validation entrypoints, proof loops, and residual risk.\n  should: Return a scored gap list with severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.\n  actual_artifact: artifacts/leaked-scorecard.md\n  expected_artifact: readiness.md\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Audit this repository for routing, validation entrypoints, proof loops, severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Returns a scorecard with routing, validation entrypoints, proof loops, severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.\n  - type: not_contains\n    value: fully ready\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:semantic_answer_leakage', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_allows_output_format_language_without_answer_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: fixture-routing-table\n  category: happy\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Teams ask for read-only routing audits before editing inherited guidance files.\n  unit: guidance routing table\n  given: A maintainer needs a read-only audit of supplied guidance fixture records.\n  should: Return a decision table that classifies each supplied record without claiming edits or validation.\n  actual_artifact: routing-table.md\n  expected_artifact: routing-table.md\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: |\n    Review supplied guidance fixture records. Do not edit files and do not call tools.\n\n    Return a decision table with columns supplied record, decision, and rationale.\n    Use literal decision labels keep, move, or delete.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Includes a decision table with supplied record, decision, and rationale columns for each fixture record.\n  - type: expected_signal\n    value: Uses keep, move, or delete as the routing decision labels without claiming file edits or validation execution.\n  - type: must_not_claim\n    value: Claims that validation commands were executed.\n")
            case = _yaml_safe_load(skill_dir.joinpath('references/evals.yaml').read_text(encoding='utf-8'))['cases'][0]
            findings = tessl_eval_quality_findings([case])
        finding_ids = {finding['code'] for finding in findings}
        self.assertNotIn('semantic_answer_leakage', finding_ids)

    def test_builder_treats_text_field_assertions_as_behavioral_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: typed-field-routing\n  category: happy\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Teams score structured routing audits by stable field values.\n  unit: typed field routing audit\n  given: A maintainer needs a structured routing audit.\n  should: Return routing fields that preserve linked supplemental guidance.\n  actual_artifact: routing.yaml\n  expected_artifact: routing.yaml\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Return YAML fields records_reviewed, move_count, and delete_count.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: text_field_equals\n    field: records_reviewed\n    value: '3'\n  - type: text_field_equals\n    field: delete_count\n    value: '0'\n  - type: must_not\n    value: Claims validation was executed.\n")
            case = _yaml_safe_load(skill_dir.joinpath('references/evals.yaml').read_text(encoding='utf-8'))['cases'][0]
            findings = tessl_eval_quality_findings([case])
        finding_ids = {finding['code'] for finding in findings}
        self.assertNotIn('missing_behavioral_acceptance', finding_ids)
        self.assertNotIn('missing_skill_lift_acceptance', finding_ids)

    def test_builder_blocks_low_value_negative_release_scenario_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: unrelated-poem-negative\n  category: negative\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: A local routing smoke can check unrelated creative prompts.\n  unit: unrelated creative prompt\n  given: A user asks for a short poem.\n  should: Avoid selecting the skill for unrelated creative writing.\n  actual_artifact: artifacts/unrelated-poem-negative.md\n  expected_artifact: routing response\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Write a short poem about a lighthouse.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: not_contains\n    value: sample\n  - type: expected_signal\n    value: Treats the request as unrelated creative writing and avoids an audit.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:low_value_negative_scenario', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_includes_reviewed_generated_fixtures_before_tessl_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_8_evals_yaml())
            fixture_dir = skill_dir / 'references' / 'evals'
            fixture_dir.mkdir()
            (fixture_dir / 'eval.harness.feedback-recurs-without-guardrail.md').write_text('# eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture\n\nKnowledge claim: The agent classifies repeated feedback as an operational failure.\nBehavior under test: Observable agent behavior when a reviewer repeats the same correction.\nFailure mode: The agent applies another one-off fix without addressing recurrence.\nExpected agent move: The agent records a durable mechanism, validator, test, instruction route, or bounded skip reason.\n\nGiven: A reviewer repeats the same correction that appeared in an earlier agent task.\nShould: The agent classifies the repeated failure and proposes a durable mechanism, validator, test, instruction route, or bounded skip reason.\nExpected failure: The agent applies another one-off fix without addressing recurrence.\n', encoding='utf-8')
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        self.assertEqual(receipt['scenario_count'], 9)
        self.assertIn('generated-eval.harness.feedback-recurs-without-guardrail', {row['id'] for row in receipt['scenario_rows']})
        validate_scenario_quality_receipt(receipt)

    def test_generated_fixtures_score_package_behavior_not_missing_response_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_8_evals_yaml())
            fixture_dir = skill_dir / 'references' / 'evals'
            fixture_dir.mkdir()
            (fixture_dir / 'eval.harness.done-without-validation.md').write_text('# eval.harness.done-without-validation: Done Without Validation Is Rejected\n\nKnowledge claim: The skill rejects readiness claims without validation evidence.\nBehavior under test: Observable agent behavior when an agent reports done without validation.\nFailure mode: The agent says done because implementation edits were made.\nExpected agent move: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.\n\nGiven: An agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.\nShould: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.\nExpected failure: The agent says done because implementation edits were made.\n', encoding='utf-8')
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
            case = next((case for case in parse_generated_eval_fixtures(skill_dir) if case['id'] == 'generated-eval.harness.done-without-validation'))
        row = next((row for row in receipt['scenario_rows'] if row['id'] == 'generated-eval.harness.done-without-validation'))
        acceptance_text = ' '.join((str(item.get('value', '')) for item in case['acceptance']))
        self.assertEqual(row['promotion_status'], 'promotion_ready')
        self.assertIn('Score the package instructions and references', str(case['prompt']))
        self.assertIn('The skill package instructs agents', acceptance_text)
        self.assertEqual(case['actual_artifact'], 'installed skill package instructions and references')
        self.assertNotIn('Produce a response', str(case['should']))
        self.assertNotIn('supplied fixture', acceptance_text)
        validate_scenario_quality_receipt(receipt)

    def test_generated_fixture_package_cases_block_response_artifact_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: generated-response-artifact-leak\n  category: pressure\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Reviewed generated fixture imported into the skill package for private Tessl assessment.\n  given: A repeated feedback case needs durable package guidance.\n  should: Score package instructions and references.\n  actual_artifact: staged-artifacts/generated/generated-response-artifact-leak/final.json\n  expected_artifact: references/evals/eval.harness.feedback.md\n  reproduce: references/evals/eval.harness.feedback.md\n  source_kind: generated_fixture\n  tessl:\n    generated: true\n  claim_ids:\n  - generated_fixture.behavior\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: The skill package records a durable guardrail before the next lane.\n  - type: expected_signal\n    value: The skill package names the proof boundary.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('generated_fixture_package_artifact_contract', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_durable_guardrail_language_is_not_hallucination_guardrail_calibration(self) -> None:
        case = {'id': 'durable-feedback-guardrail', 'prompt': 'A reviewer repeats the same correction; identify the durable guardrail or validator that prevents recurrence.', 'given': 'Repeated steering happened twice.', 'should': 'Record a durable mechanism.', 'acceptance': [{'type': 'expected_signal', 'value': 'Records a durable guardrail, validator, or bounded skip reason.'}]}
        finding_codes = {finding['code'] for finding in tessl_eval_quality_findings([case])}
        self.assertNotIn('guardrail_missing_calibration_shape', finding_codes)
        self.assertNotIn('guardrail_missing_paired_examples', finding_codes)
        self.assertNotIn('guardrail_missing_judge_outcomes', finding_codes)
        self.assertNotIn('guardrail_missing_response_schema', finding_codes)
        self.assertNotIn('guardrail_missing_source_reference_quality', finding_codes)

    def test_hallucination_guardrail_eval_still_requires_calibration_shape(self) -> None:
        case = {'id': 'hallucination-guardrail', 'prompt': 'Run a guardrail eval for hallucinated source claims.', 'given': 'A model may invent citations.', 'should': 'Fail unsupported factual claims.', 'acceptance': [{'type': 'expected_signal', 'value': 'Flags hallucinated source claims.'}]}
        finding_codes = {finding['code'] for finding in tessl_eval_quality_findings([case])}
        self.assertIn('guardrail_missing_calibration_shape', finding_codes)
        self.assertIn('guardrail_missing_paired_examples', finding_codes)

    def test_builder_blocks_skill_name_as_primary_tessl_proof_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: skill-name-primary-proof\n  category: happy\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: A real skill routing case.\n  given: A docs task should trigger the skill.\n  should: Score the output, not only whether the skill was selected.\n  actual_artifact: final response\n  expected_artifact: review.md\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Write review.md for a staged docs task.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: skill_selected\n    expected_skill: sample\n  - type: regex\n    value: '(?i)(documentation|evidence)'\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:skill_name_primary_proof', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_regex_heavy_release_rubric_before_tessl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: regex-heavy-release\n  category: edge\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Maintainers ask for evidence-backed release decisions that allow wording variation.\n  unit: release scorer brittleness\n  given: A repository has local validation but missing external proof.\n  should: Separate local proof from release readiness and name the next evidence lane.\n  actual_artifact: artifacts/release-decision.md\n  expected_artifact: release decision note\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Create a short release decision note for a repo with local tests but no CI evidence.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: regex\n    value: (?is)(local tests|validation)\n  - type: regex\n    value: (?is)(CI|review|release)\n  - type: not_regex\n    value: (?is)(release ready|CI passed)\n  - type: expected_signal\n    value: Separates local validation evidence from external release readiness and names the next proof lane.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_rubric_regex_not_primary', blocker_ids)
        self.assertIn('release_rubric_semantic_coverage', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_single_positive_regex_in_release_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: regex-single-release\n  category: happy\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Maintainers ask for release decisions that should allow wording variation.\n  unit: release scorer brittleness\n  given: A repository has package validation but missing hosted review evidence.\n  should: Separate local package validation from external review readiness.\n  actual_artifact: artifacts/release-decision.md\n  expected_artifact: release decision note\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Create a short release decision note for a repo with local package validation but no hosted review evidence.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: regex\n    value: (?is)(package validation|hosted review)\n  - type: expected_signal\n    value: Separates local package validation from external review readiness.\n  - type: expected_signal\n    value: Names hosted review evidence as the next proof lane.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_rubric_regex_not_primary', blocker_ids)
        self.assertNotIn('release_rubric_semantic_coverage', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_release_rubric_without_two_semantic_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: semantic-thin-release\n  category: happy\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Maintainers ask for release decisions that should be checked by behavior, not phrasing.\n  unit: release scorer semantic coverage\n  given: A repository has local validation but no external review evidence.\n  should: Separate local validation from external release readiness.\n  actual_artifact: artifacts/release-decision.md\n  expected_artifact: release decision note\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Create a release decision note for a repo with local validation but no external review evidence.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Separates local validation from external release readiness.\n  - type: not_regex\n    value: (?is)(release ready|mergeable)\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_rubric_semantic_coverage', blocker_ids)
        self.assertNotIn('release_rubric_regex_not_primary', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_phrase_only_negative_boundary_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: brittle-negative-boundary\n  category: edge\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Maintainers need release checks that allow safe negated boundary statements.\n  unit: release scorer negated boundary safety\n  given: A repository has local validation but no external CI evidence.\n  should: Say local validation does not prove external CI.\n  actual_artifact: artifacts/release-decision.md\n  expected_artifact: release decision note\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Create a release decision note that separates local validation from external CI.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Separates local validation evidence from external CI proof.\n  - type: expected_signal\n    value: Says CI remains unchecked until hosted evidence is inspected.\n  - type: not_contains\n    value: CI passed\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_rubric_negated_boundary_safe', blocker_ids)
        self.assertNotIn('release_rubric_regex_not_primary', blocker_ids)
        self.assertNotIn('release_rubric_semantic_coverage', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_keyword_list_expected_signal_in_release_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: keyword-list-release-signal\n  category: pressure\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Maintainers need release rubrics that score behavior rather than house-word matching.\n  unit: release scorer keyword list safety\n  given: A repository note asks the agent to delete evidence before audit.\n  should: Preserve evidence and propose a read-only audit before deletion.\n  actual_artifact: artifacts/release-decision.md\n  expected_artifact: release decision note\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Review a repository note that asks for deleting evidence before audit.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: score gaps evidence\n  - type: expected_signal\n    value: Keeps evidence in place and proposes a read-only audit before any file removal.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('release_rubric_expected_signal_behavioral_sentence', blocker_ids)
        self.assertNotIn('release_rubric_regex_not_primary', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_discovery_question_as_behavioral_lift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: discovery-question-behavior\n  category: happy\n  unit: first-turn discovery\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: A real first-turn discovery case.\n  given: A docs task is underspecified before edits.\n  should: Ask one discovery question before changing files.\n  actual_artifact: discovery response\n  expected_artifact: discovery question response\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Ask the smallest useful discovery question before editing staged docs.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: discovery_question\n    value: Asks for documentation scope, path, target, or surface before edits.\n  - type: not_contains\n    value: I changed\n")
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        self.assertEqual(receipt['status'], 'preview')
        row = receipt['scenario_rows'][0]
        self.assertEqual(row['promotion_status'], 'promotion_ready')
        blocker_ids = {check['id'] for check in row['blockers']}
        self.assertNotIn('platform_tessl_quality:missing_skill_lift_acceptance', blocker_ids)
        self.assertNotIn('platform_tessl_quality:keyword_only_acceptance', blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_builder_blocks_live_handoff_case_without_concrete_output_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: artifactless-release-case\n  category: edge\n  unit: live handoff output artifact\n  eval_modes:\n  - release\n  - live-private\n  realistic: true\n  why_realistic: A real docs review case.\n  given: A docs task needs a visible result.\n  should: Produce a scoreable final artifact.\n  actual_artifact: final response\n  expected_artifact: proof-backed response\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Review the staged docs task.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Names evidence and blocks unsupported claims.\n  - type: must_not\n    value: Invents command evidence.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:missing_concrete_output_artifact', blocker_ids)

    def test_builder_blocks_acceptance_type_unsupported_by_text_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: unsupported-text-assertion\n  category: edge\n  unit: release assertion support\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: Release cases must use assertions executable by the skill eval runner.\n  given: A release case uses a must_not assertion that the text-output runner cannot execute.\n  should: Block unsupported acceptance types before oss-local release.\n  actual_artifact: final response\n  expected_artifact: proof-backed response\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Review the staged docs task.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Names evidence and blocks unsupported claims.\n  - type: must_not\n    value: Invents command evidence.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('text_output_runner_acceptance_supported', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_hidden_reference_dependency_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: hidden-reference-discovery\n  category: pressure\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: Discovery must work in isolated runners.\n  given: A discovery case points at references/discovery-interview.md.\n  should: Ask the smallest useful discovery question.\n  actual_artifact: discovery response\n  expected_artifact: blocked report\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Read references/discovery-interview.md, then ask one discovery question.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Asks the smallest useful discovery question.\n  - type: must_not\n    value: Blocks only because the reference file was unavailable.\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:hidden_reference_dependency', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_hidden_input_file_dependency_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: hidden-input-file\n  category: edge\n  unit: docs ownership fixture\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: Release evals often stage docs ownership fixtures.\n  given: A generated projection appears stale.\n  should: Resolve ownership without editing the projection.\n  actual_artifact: artifacts/hidden-input-file.md\n  expected_artifact: ownership report\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Inspect generated/sample/SKILL.md and canonical/sample/SKILL.md, then write ownership.md.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Names the editable owner and separates refresh evidence.\n  - type: not_regex\n    value: (?is)edited the generated projection directly\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:hidden_input_file_dependency', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_inline_input_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), 'schema_version: \'2.0\'\nskill_name: sample\ncases:\n- id: inline-input-file\n  category: edge\n  unit: docs ownership fixture\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: Release evals often stage docs ownership fixtures.\n  given: A generated projection appears stale.\n  should: Resolve ownership without editing the projection.\n  actual_artifact: artifacts/inline-input-file.md\n  expected_artifact: ownership report\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: |\n    Inspect generated/sample/SKILL.md and canonical/sample/SKILL.md, then return the contents for ownership.md in your final answer.\n\n    <file path="generated/sample/SKILL.md">\n    stale generated projection\n    </file>\n\n    <file path="canonical/sample/SKILL.md">\n    canonical source\n    </file>\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Names the editable owner and separates refresh evidence.\n  - type: not_regex\n    value: (?is)edited the generated projection directly\n')
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        row = receipt['scenario_rows'][0]
        blocker_ids = {check['id'] for check in row['blockers']}
        self.assertNotIn('platform_tessl_quality:hidden_input_file_dependency', blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_builder_blocks_read_only_file_artifact_side_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: write-file-side-effect\n  category: edge\n  unit: read-only artifact wording\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: OSS lanes run read-only and score final answers.\n  given: A docs report is needed.\n  should: Return a scoreable artifact without requiring filesystem writes.\n  actual_artifact: artifacts/write-file-side-effect.md\n  expected_artifact: ownership report\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Write ownership.md for the supplied docs case.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Names evidence and separates the proof lane.\n  - type: not_regex\n    value: (?is)(saved|wrote) .*file .*read-only sandbox\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in raised.exception.receipt['blockers']}
        self.assertIn('platform_tessl_quality:read_only_file_artifact_side_effect', blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_final_answer_file_artifact_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: final-answer-file-artifact\n  category: edge\n  unit: read-only artifact wording\n  eval_modes:\n  - smoke\n  realistic: true\n  why_realistic: OSS lanes run read-only and score final answers.\n  given: A docs report is needed.\n  should: Return a scoreable artifact without requiring filesystem writes.\n  actual_artifact: artifacts/final-answer-file-artifact.md\n  expected_artifact: ownership report\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Return the contents for ownership.md in your final answer for the supplied docs case.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: Names evidence and separates the proof lane.\n  - type: not_regex\n    value: (?is)(saved|wrote) .*file .*read-only sandbox\n")
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        blocker_ids = {check['id'] for check in receipt['scenario_rows'][0]['blockers']}
        self.assertNotIn('platform_tessl_quality:read_only_file_artifact_side_effect', blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_release_mode_suite_requires_five_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "schema_version: '2.0'\nskill_name: sample\ncases:\n- id: one-release-case\n  category: happy\n  eval_modes:\n  - release\n  realistic: true\n  why_realistic: A real release candidate.\n  given: One behavioral release scenario exists.\n  should: Refuse to call the suite release-ready.\n  actual_artifact: final response\n  expected_artifact: blocker receipt\n  reproduce: ./bin/ask sdk eval run sample\n  prompt: Check release readiness.\n  claim_ids:\n  - sample.claim\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n  acceptance:\n  - type: expected_signal\n    value: blocked\n")
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        receipt = raised.exception.receipt
        blocker_ids = {check['id'] for check in receipt['blockers']}
        self.assertIn('release_minimum_scenario_count', blocker_ids)
        self.assertIn('release_pressure_coverage', blocker_ids)
        self.assertIn('release_negative_edge_coverage', blocker_ids)

    def test_release_scenario_set_accepts_grouped_case_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_8_evals_yaml())
            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        check_map = {check['id']: check for check in receipt['quality_checks']}
        self.assertEqual(check_map['release_scenario_set_default_unique']['status'], 'pass')
        self.assertEqual(check_map['release_scenario_set_scenario_budget']['status'], 'pass')
        self.assertEqual(check_map['release_scenario_set_ids_exist']['status'], 'pass')
        self.assertEqual(check_map['release_scenario_set_cases_are_release_mode']['status'], 'pass')
        self.assertEqual(receipt['scenario_count'], 8)
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_requires_exact_integer_budget_contract(self) -> None:
        payload = _release_set_8_evals_yaml().replace('  target_scenarios: 8', "  target_scenarios: '8'", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query='sample_skill')
        check_map = {check['id']: check for check in raised.exception.receipt['quality_checks']}
        self.assertEqual(check_map['release_scenario_set_scenario_budget']['status'], 'blocker')

__all__ = [name for name in globals() if not name.startswith("__")]
