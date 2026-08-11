from skills_sdk_ab_judge_score_tests_core import *  # noqa: F403

class TestSkillsSdkAbJudgeScore(_SkillsSdkAbJudgeScoreBase):
    @unittest.skipIf(not hasattr(os, 'mkfifo'), 'fifo support unavailable')
    def test_cloud_judge_rejects_fifo_outside_actual_codex_home(self) -> None:
        profile = {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}
        with tempfile.TemporaryDirectory() as directory:
            actual_home = Path(directory) / 'actual-home'
            other_home = Path(directory) / 'other-home'
            unapproved_stream = other_home / '.codex' / '.env'
            unapproved_stream.parent.mkdir(parents=True)
            os.mkfifo(unapproved_stream)
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(unapproved_stream)}, clear=False), patch('ask.skills_sdk.ab_transport_contracts.operator_account_home', return_value=actual_home):
                self.assertIsNone(codex_judge._codex_auth_env_file_path(profile))
                with self.assertRaisesRegex(codex_judge.CodexProfileConfigError, 'Configs auth-backed wrapper boundary'):
                    codex_judge._codex_judge_command(profile, Path(directory) / 'work', Path(directory) / 'last-message.json')

    def test_cloud_judge_rejects_receipt_only_stream_marker(self) -> None:
        profile = {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}
        with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': '<operator-approved-opaque-env-stream>'}, clear=False):
            self.assertIsNone(codex_judge._codex_auth_env_file_path(profile))
            with self.assertRaisesRegex(codex_judge.CodexProfileConfigError, 'Configs auth-backed wrapper boundary'):
                codex_judge._codex_judge_command(profile, Path('/private/tmp/work'), Path('/private/tmp/last-message.json'))

    @unittest.skipIf(not hasattr(os, 'mkfifo'), 'fifo support unavailable')
    def test_judge_execution_argv_requires_a_real_opaque_fifo(self) -> None:
        command_tail = ['--require-env', 'OLLAMA_API_KEY', '--', 'bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh', '--profile', 'oss-cloud', '--model', 'deepseek-v4-flash:0731-cloud', '--strict-config', '-c', 'approval_policy="on-request"', '--sandbox', 'read-only', '--ephemeral', '-']
        with tempfile.TemporaryDirectory() as directory, patch('ask.skills_sdk.ab_transport_contracts.operator_account_home', return_value=Path(directory)):
            env_dir = Path(directory) / '.codex'
            env_dir.mkdir()
            env_file = env_dir / '.env'
            regular = ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh', '--env-file', str(env_file), *command_tail]
            env_file.write_text('opaque reference only', encoding='utf-8')
            blockers: list[str] = []
            result = CodexJudgeResult(0, '', '', executed_argv=regular)
            evidence = {'command_argv': regular, 'codex_profile': 'oss-cloud'}
            self.assertIsNone(_validate_judge_execution_argv(evidence, result, blockers))
            self.assertEqual(blockers, ['judge_command_profile_missing_or_invalid'])
            env_file.unlink()
            os.mkfifo(env_file)
            fifo_argv = ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh', '--env-file', str(env_file), *command_tail]
            blockers = []
            result = CodexJudgeResult(0, '', '', executed_argv=fifo_argv)
            evidence = {'command_argv': fifo_argv, 'codex_profile': 'oss-cloud'}
            self.assertEqual(_validate_judge_execution_argv(evidence, result, blockers), 'oss-cloud')
            self.assertEqual(blockers, [])
            receipt_marker = ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh', '--env-file', '<operator-approved-opaque-env-stream>', *command_tail]
            blockers = []
            result = CodexJudgeResult(0, '', '', executed_argv=receipt_marker)
            evidence = {'command_argv': receipt_marker, 'codex_profile': 'oss-cloud'}
            self.assertIsNone(_validate_judge_execution_argv(evidence, result, blockers))
            self.assertEqual(blockers, ['judge_command_profile_missing_or_invalid'])
            relative = ['bash', 'evil/run-auth-backed.sh', '--env-file', str(env_file), *command_tail]
            blockers = []
            result = CodexJudgeResult(0, '', '', executed_argv=relative)
            evidence = {'command_argv': relative, 'codex_profile': 'oss-cloud'}
            self.assertIsNone(_validate_judge_execution_argv(evidence, result, blockers))
            self.assertEqual(blockers, ['judge_command_profile_missing_or_invalid'])

    def test_builder_scores_with_injected_local_judge(self) -> None:
        calls: list[tuple[str, str, int]] = []

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            calls.append((prompt, str(judge_profile['model']), timeout_seconds))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(_decision(run_receipt['experiment_id'])))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, timeout_seconds=12, runner=fake_runner)
        self.assertEqual(receipt['status'], 'scored')
        self.assertEqual(receipt['operation'], 'ab_judge_score')
        self.assertEqual(receipt['judge_profile']['id'], 'oss-local')
        self.assertEqual(receipt['judge_profile']['model'], 'qwen3.5:9b-mlx')
        self.assertEqual(receipt['judge_profile']['model_role'], 'local_sandbox_eval_default')
        self.assertEqual(receipt['judge_profile']['model_settings']['num_ctx'], 8192)
        self.assertEqual(receipt['decision']['winner'], 'skill_b')
        self.assertEqual(receipt['decision']['confidence'], 'medium')
        self.assertTrue(receipt['provider_invoked'])
        self.assertTrue(receipt['network_accessed'])
        self.assertTrue(receipt['mutation_performed'])
        self.assertTrue(receipt['advisory_only'])
        self.assertTrue(receipt['calibration_required'])
        self.assertEqual(receipt['blockers'], [])
        self.assertEqual(len(calls), 1)
        self.assertIn('qwen3.5:9b-mlx', calls[0])
        self.assertTrue((REPO_ROOT / receipt['judge_output_path']).is_file())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_scores_with_code_heavy_local_judge_profile(self) -> None:
        calls: list[str] = []

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            calls.append(str(judge_profile['codex_profile']))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(_decision(run_receipt['experiment_id'])))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, judge_profile_id='oss-local-code', runner=fake_runner)
        self.assertEqual(receipt['status'], 'scored')
        self.assertEqual(receipt['blockers'], [])
        self.assertEqual(receipt['judge_profile']['id'], 'oss-local-code')
        self.assertEqual(receipt['judge_profile']['codex_profile'], 'oss-local-code')
        self.assertEqual(receipt['judge_profile']['model'], 'qwen3-coder:30b')
        self.assertEqual(receipt['judge_profile']['model_role'], 'code_heavy_specialist')
        self.assertEqual(receipt['codex_profile'], 'oss-local-code')
        self.assertEqual(calls, ['oss-local-code'])
        self.assertIn('--profile', receipt['judge_command_argv'])
        self.assertIn('oss-local-code', receipt['judge_command_argv'])
        validate_ab_judge_score_receipt(receipt)

    def test_judge_metadata_alone_cannot_prove_executed_profile(self) -> None:
        invalid_argvs = [['codex', 'exec', '--sandbox', 'read-only', '--json', '-'], ['codex', 'exec', '--sandbox', 'read-only', '--profile', 'oss-local']]
        for invalid_argv in invalid_argvs:
            with self.subTest(invalid_argv=invalid_argv), patch('ask.skills_sdk.eval_ab_judge._codex_judge_command', return_value=invalid_argv):
                receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, judge_profile_id='oss-local')
            self.assertEqual(receipt['status'], 'blocked')
            self.assertIn('judge_command_profile_missing_or_invalid', receipt['blockers'])
            self.assertIsNone(receipt['codex_profile'])

    def test_codex_command_uses_large_transcript_model_settings(self) -> None:
        judge_profile = {'id': 'oss-local-large-transcript', 'codex_profile': 'oss-local', 'model': 'qwen3.5:9b-mlx', 'model_settings': {'num_ctx': 16384, 'temperature': 0.1, 'top_p': 0.9}}
        result, command, _env, _profile_text, _op_env_file = _run_codex_with_captured_subprocess('oss-local', 'model = "qwen3.5:9b-mlx"\n', judge_profile)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(command[:4], ['codex', 'exec', '--profile', 'oss-local'])
        self.assertIn('--profile', command)
        self.assertEqual(command[command.index('--profile') + 1], 'oss-local')
        self.assertIn('model_settings.num_ctx=16384', command)

    def test_codex_model_settings_skip_non_string_keys_before_sorting(self) -> None:
        overrides = codex_judge._codex_model_setting_overrides({'id': 'mixed-settings', 'model_settings': {1: 16384, 'num_ctx': 8192, 'temperature': 0.1, 'bad': object()}})
        self.assertEqual(overrides, ['model_settings.num_ctx=8192', 'model_settings.temperature=0.1'])

    def test_builder_scores_with_injected_cloud_judge_profile(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            calls.append((prompt, str(judge_profile['id'])))
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(_decision(run_receipt['experiment_id'])))
        with tempfile.TemporaryDirectory() as profile_dir:
            env_dir = Path(profile_dir) / '.codex'
            env_dir.mkdir()
            auth_env_file = env_dir / '.env'
            os.mkfifo(auth_env_file)
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(auth_env_file)}), patch('ask.skills_sdk.ab_transport_contracts.operator_account_home', return_value=Path(profile_dir)):
                receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, judge_profile_id='oss-cloud', runner=fake_runner)
        self.assertEqual(receipt['status'], 'scored')
        self.assertEqual(receipt['blockers'], [])
        self.assertEqual(receipt['judge_profile']['id'], 'oss-cloud')
        self.assertEqual(receipt['codex_profile'], 'oss-cloud')
        self.assertTrue(receipt['provider_invoked'])
        self.assertTrue(receipt['mutation_performed'])
        self.assertEqual(calls[0][1], 'oss-cloud')
        validate_ab_judge_score_receipt(receipt)

    def test_cli_accepts_cloud_judge_profile_before_execute_gate(self) -> None:
        proc = subprocess.run([str(REPO_ROOT / 'bin/ask'), 'sdk', 'eval', 'ab-judge-score', '--run-receipt', RUN_RECEIPT, '--judge-profile', 'oss-cloud', '--json', '--robot'], cwd=REPO_ROOT, check=False, text=True, capture_output=True)
        payload = json.loads(proc.stdout)
        _assert_robot_cli_stderr(self, proc.stderr)
        self.assertEqual(payload['status'], 'error')

    def test_cli_accepts_declared_local_code_judge_profile_before_execute_gate(self) -> None:
        proc = subprocess.run([str(REPO_ROOT / 'bin/ask'), 'sdk', 'eval', 'ab-judge-score', '--run-receipt', RUN_RECEIPT, '--judge-profile', 'oss-local-code', '--json', '--robot'], cwd=REPO_ROOT, check=False, text=True, capture_output=True)
        payload = json.loads(proc.stdout)
        _assert_robot_cli_stderr(self, proc.stderr)
        self.assertEqual(payload['status'], 'error')
        self.assertIn('requires --execute', payload['errors'][0]['message'])
        self.assertEqual(payload['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('requires --execute', payload['errors'][0]['message'])

    def test_ab_judge_score_cli_choices_exclude_codex_fast(self) -> None:
        self.assertIn('oss-local-code', _AB_SCORE_PROFILE_CHOICES)
        self.assertIn('oss-local-fallback', _AB_SCORE_PROFILE_CHOICES)
        self.assertNotIn('codex-fast', _AB_SCORE_PROFILE_CHOICES)

    def test_builder_blocks_invalid_judge_output(self) -> None:

        def invalid_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            return _judge_result(judge_profile, output_file=output_file, stdout='not json')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=invalid_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_output_invalid_json', receipt['blockers'])
        self.assertTrue(receipt['provider_invoked'])
        self.assertTrue((REPO_ROOT / receipt['judge_output_path']).is_file())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_codex_metadata_fallback_before_scoring(self) -> None:

        def fallback_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(_decision(run_receipt['experiment_id'])), stderr='warning: Model metadata for qwen3.5:9b-mlx not found. Defaulting to fallback metadata.')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=fallback_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('codex_runtime_metadata_fallback', receipt['blockers'])
        self.assertIsNone(receipt['decision'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_visible_thinking_before_scoring(self) -> None:

        def thinking_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout='<think>hidden chain should not leak</think>\n' + json.dumps(_decision(run_receipt['experiment_id'])))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=thinking_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('codex_runtime_visible_thinking', receipt['blockers'])
        self.assertIsNone(receipt['decision'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_allows_codex_jsonl_reasoning_telemetry_when_guard_allows_it(self) -> None:

        def telemetry_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            reasoning_event = json.dumps({'type': 'item.completed', 'item': {'id': 'item_1', 'type': 'reasoning', 'text': 'structured telemetry'}})
            output_file.write_text(json.dumps(_decision(run_receipt['experiment_id'])), encoding='utf-8')
            return _judge_result(judge_profile, output_file=output_file, stdout=reasoning_event)
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=telemetry_runner)
        self.assertEqual(receipt['status'], 'scored')
        self.assertEqual(receipt['blockers'], [])
        self.assertIsNotNone(receipt['decision'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_codex_token_budget_blowout_before_scoring(self) -> None:

        def costly_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            usage_event = json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 8231, 'output_tokens': 53, 'reasoning_output_tokens': 0}})
            stdout = json.dumps(_decision(run_receipt['experiment_id'])) + '\n' + usage_event + '\n'
            return _judge_result(judge_profile, output_file=output_file, stdout=stdout)
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=costly_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('codex_runtime_token_budget_exceeded', receipt['blockers'])
        self.assertIsNone(receipt['decision'])
        validate_ab_judge_score_receipt(receipt)

    def test_parse_judge_decision_accepts_fenced_json_and_derives_normalized_scores(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
        comparison_payload = _comparison_payload_for_decision_test(run_receipt['experiment_id'])
        model_payload = _decision(run_receipt['experiment_id'])
        model_payload['dimension_scores'][-1]['skill_a_score'] = 4.5
        model_payload['dimension_scores'][-1]['skill_b_score'] = 4.5
        model_payload['normalized_score_a'] = 0.97
        model_payload['normalized_score_b'] = 0.97
        raw_output = '```json\n' + json.dumps(model_payload) + '\n```'
        decision, blocker = _parse_judge_decision(raw_output, comparison_payload)
        self.assertIsNone(blocker)
        self.assertIsNotNone(decision)
        self.assertAlmostEqual(decision['normalized_score_a'], 0.63)
        self.assertAlmostEqual(decision['normalized_score_b'], 0.81)
        malformed_output = raw_output.replace('}], "normalized_score_a"', ']}, "normalized_score_a"')
        repaired_decision, repaired_blocker = _parse_judge_decision(malformed_output, comparison_payload)
        self.assertIsNone(repaired_blocker)
        self.assertIsNotNone(repaired_decision)
        self.assertAlmostEqual(repaired_decision['normalized_score_a'], 0.63)
        missing_comma_output = raw_output.replace('", "evidence_refs"', '"\n\n"evidence_refs"', 1)
        comma_repaired_decision, comma_repaired_blocker = _parse_judge_decision(missing_comma_output, comparison_payload)
        self.assertIsNone(comma_repaired_blocker)
        self.assertIsNotNone(comma_repaired_decision)
        self.assertAlmostEqual(comma_repaired_decision['normalized_score_b'], 0.81)

    def test_judge_prompt_requires_string_evidence_references(self) -> None:
        prompt = _judge_prompt(_comparison_payload_for_decision_test('ex_0123456789abcdef'))

        self.assertIn('every evidence_refs member must be a non-empty string', prompt)
        self.assertIn('never a numeric index', prompt)
        self.assertIn('must be reported as 1.0, never 5.0', prompt)

    def test_builder_blocks_unavailable_local_judge(self) -> None:

        def missing_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            raise FileNotFoundError('codex')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=missing_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_provider_unavailable', receipt['blockers'])
        self.assertFalse(receipt['provider_invoked'])
        self.assertTrue(receipt['mutation_performed'])
        self.assertTrue((REPO_ROOT / receipt['judge_output_path']).parent.is_dir())
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_local_judge_startup_oserror(self) -> None:

        def permission_denied_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            raise PermissionError('codex')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=permission_denied_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_provider_unavailable', receipt['blockers'])
        self.assertFalse(receipt['provider_invoked'])
        self.assertTrue(receipt['mutation_performed'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_clears_stale_output_when_local_judge_unavailable(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
        stale_output = REPO_ROOT / self.evidence_root / run_receipt['experiment_id'] / 'judge' / 'codex-last-message.json'
        stale_output.parent.mkdir(parents=True, exist_ok=True)
        stale_output.write_text('{"stale": true}', encoding='utf-8')

        def missing_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            raise FileNotFoundError('codex')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=missing_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_provider_unavailable', receipt['blockers'])
        self.assertFalse(stale_output.exists())
        self.assertIsNone(receipt['judge_output_digest'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_schema_extra_judge_keys(self) -> None:

        def extra_key_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            decision = _decision(run_receipt['experiment_id'])
            decision['unexpected'] = 'blocked'
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(decision))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=extra_key_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_decision_keys_invalid', receipt['blockers'])
        validate_ab_judge_score_receipt(receipt)

    def test_typed_contract_rejects_decision_for_different_experiment(self) -> None:

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(_decision(run_receipt['experiment_id'])))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=fake_runner)
        receipt['decision']['experiment_id'] = '0000000000000000'
        with self.assertRaises(ValidationError):
            validate_ab_judge_score_receipt(receipt)

    def test_typed_contract_rejects_persisted_score_arithmetic_mismatch(self) -> None:

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(_decision(run_receipt['experiment_id'])))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=fake_runner)
        receipt['decision']['dimension_scores'] = [{**row, 'skill_a_score': 5.0, 'skill_b_score': 1.0, 'reason': 'skill_a has stronger evidence'} for row in receipt['decision']['dimension_scores']]
        receipt['decision']['normalized_score_a'] = 0.2
        receipt['decision']['normalized_score_b'] = 0.9
        receipt['decision']['winner'] = 'skill_b'
        with self.assertRaises(ValidationError):
            validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_winner_mismatched_to_scores(self) -> None:

        def mismatched_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            decision = _decision(run_receipt['experiment_id'])
            decision['winner'] = 'skill_a'
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(decision))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=mismatched_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_decision_winner_mismatch', receipt['blockers'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_low_confidence_directional_winner(self) -> None:

        def low_confidence_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            decision = _decision(run_receipt['experiment_id'])
            decision['confidence'] = 'low'
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(decision))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=low_confidence_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_decision_winner_mismatch', receipt['blockers'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_normalized_scores_mismatched_to_dimension_rows(self) -> None:

        def mismatched_score_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            decision = _decision(run_receipt['experiment_id'])
            decision['dimension_scores'] = [{**row, 'skill_a_score': 5.0, 'skill_b_score': 1.0, 'reason': 'skill_a has stronger evidence'} for row in decision['dimension_scores']]
            decision['normalized_score_a'] = 0.2
            decision['normalized_score_b'] = 0.9
            decision['winner'] = 'skill_b'
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(decision))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=mismatched_score_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_decision_winner_mismatch', receipt['blockers'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_non_finite_judge_scores(self) -> None:

        def non_finite_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding='utf-8'))
            decision = _decision(run_receipt['experiment_id'])
            decision['normalized_score_a'] = math.nan
            return _judge_result(judge_profile, output_file=output_file, stdout=json.dumps(decision))
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=non_finite_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('judge_output_invalid_json', receipt['blockers'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_file_evidence_root_before_writing(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        evidence_root.parent.mkdir(parents=True, exist_ok=True)
        evidence_root.write_text('not a directory', encoding='utf-8')

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            self.fail('runner should not be invoked when evidence root is a file')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root=self.evidence_root, runner=fake_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('evidence_root_not_directory', receipt['blockers'])
        self.assertFalse(receipt['provider_invoked'])
        self.assertFalse(receipt['mutation_performed'])
        validate_ab_judge_score_receipt(receipt)

    def test_builder_blocks_file_ancestor_evidence_root_before_writing(self) -> None:

        def fake_runner(prompt: str, judge_profile: dict[str, object], timeout_seconds: int, repo_root: Path, output_file: Path) -> CodexJudgeResult:
            self.fail('runner should not be invoked when an evidence root ancestor is a file')
        receipt = build_ab_judge_score_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT, evidence_root='AGENTS.md/judges', runner=fake_runner)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertIn('evidence_root_not_directory', receipt['blockers'])
        self.assertFalse(receipt['mutation_performed'])
        validate_ab_judge_score_receipt(receipt)

    def test_cli_requires_execute_gate(self) -> None:
        proc = subprocess.run([str(REPO_ROOT / 'bin/ask'), 'sdk', 'eval', 'ab-judge-score', '--run-receipt', RUN_RECEIPT, '--json', '--robot'], cwd=REPO_ROOT, check=False, text=True, capture_output=True)
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload['status'], 'error')
        self.assertIn('requires --execute', payload['errors'][0]['message'])

    def test_evidence_preflight_rejects_paths_outside_repo(self) -> None:
        evidence = _score_evidence_paths(REPO_ROOT, '../sdk-ab-judge-escape', '1234567890abcdef')
        self.assertEqual(evidence['blocker'], 'evidence_root_outside_repo')
        self.assertFalse((REPO_ROOT.parent / 'sdk-ab-judge-escape.txt').exists())

    def test_evidence_preflight_rejects_malformed_experiment_id(self) -> None:
        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '../../../scratch')
        self.assertEqual(evidence['blocker'], 'experiment_id_invalid')
        self.assertIsNone(evidence['prompt_path'])
        self.assertIsNone(evidence['output_path'])

    @unittest.skipIf(not hasattr(Path, 'symlink_to'), 'symlink support unavailable')
    def test_evidence_preflight_rejects_symlinked_experiment_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        experiment_root = evidence_root / '1234567890abcdef'
        with tempfile.TemporaryDirectory(prefix='sdk-ab-judge-outside-') as outside_dir:
            outside = Path(outside_dir)
            evidence_root.mkdir(parents=True, exist_ok=True)
            experiment_root.symlink_to(outside, target_is_directory=True)
            evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '1234567890abcdef')
            self.assertEqual(evidence['blocker'], 'score_evidence_path_outside_repo')
            self.assertIsNone(evidence['prompt_path'])
            self.assertIsNone(evidence['output_path'])
            if experiment_root.is_symlink():
                experiment_root.unlink()

    @unittest.skipIf(not hasattr(Path, 'symlink_to'), 'symlink support unavailable')
    def test_evidence_preflight_rejects_symlinked_evidence_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        target_root = REPO_ROOT / '.harness/test-sdk-ab-judge-score-target'
        shutil.rmtree(target_root, ignore_errors=True)
        try:
            target_root.mkdir(parents=True, exist_ok=True)
            evidence_root.symlink_to(target_root, target_is_directory=True)
            evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '1234567890abcdef')
            self.assertEqual(evidence['blocker'], 'score_evidence_path_outside_repo')
            self.assertIsNone(evidence['prompt_path'])
            self.assertIsNone(evidence['output_path'])
        finally:
            if evidence_root.is_symlink():
                evidence_root.unlink()
            shutil.rmtree(target_root, ignore_errors=True)

    @unittest.skipIf(not hasattr(Path, 'symlink_to'), 'symlink support unavailable')
    def test_evidence_preflight_rejects_symlinked_score_file(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / '1234567890abcdef' / 'judge'
        with tempfile.TemporaryDirectory(prefix='sdk-ab-judge-outside-') as outside_dir:
            outside = Path(outside_dir) / 'prompt.txt'
            outside.write_text('outside', encoding='utf-8')
            score_dir.mkdir(parents=True, exist_ok=True)
            (score_dir / 'prompt.txt').symlink_to(outside)
            evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '1234567890abcdef')
            self.assertEqual(evidence['blocker'], 'score_evidence_path_outside_repo')
            self.assertIsNone(evidence['prompt_path'])
            self.assertIsNone(evidence['output_path'])

    @unittest.skipIf(not hasattr(Path, 'symlink_to'), 'symlink support unavailable')
    def test_evidence_preflight_rejects_repo_internal_symlinked_experiment_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        experiment_root = evidence_root / '1234567890abcdef'
        target_root = evidence_root / 'alternate-target'
        evidence_root.mkdir(parents=True, exist_ok=True)
        target_root.mkdir(parents=True, exist_ok=True)
        experiment_root.symlink_to(target_root, target_is_directory=True)
        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '1234567890abcdef')
        self.assertEqual(evidence['blocker'], 'score_evidence_path_outside_repo')
        self.assertIsNone(evidence['prompt_path'])
        self.assertIsNone(evidence['output_path'])

    def test_evidence_preflight_rejects_directory_score_file_leaf(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / '1234567890abcdef' / 'judge'
        (score_dir / 'prompt.txt').mkdir(parents=True, exist_ok=True)
        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '1234567890abcdef')
        self.assertEqual(evidence['blocker'], 'score_evidence_path_outside_repo')
        self.assertIsNone(evidence['prompt_path'])
        self.assertIsNone(evidence['output_path'])

    @unittest.skipIf(not hasattr(Path, 'symlink_to'), 'symlink support unavailable')
    def test_clear_text_evidence_unlinks_leaf_symlink_not_target(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / '1234567890abcdef' / 'judge'
        with tempfile.TemporaryDirectory(prefix='sdk-ab-judge-target-') as target_dir:
            target = Path(target_dir) / 'codex-last-message.json'
            target.write_text('old-output', encoding='utf-8')
            score_dir.mkdir(parents=True, exist_ok=True)
            symlink = score_dir / 'codex-last-message.json'
            symlink.symlink_to(target)
            _clear_text_evidence(REPO_ROOT, symlink)
            self.assertFalse(symlink.exists())
            self.assertEqual(target.read_text(encoding='utf-8'), 'old-output')

    @unittest.skipIf(not hasattr(Path, 'symlink_to'), 'symlink support unavailable')
    def test_write_text_evidence_rejects_leaf_symlink(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / '1234567890abcdef' / 'judge'
        with tempfile.TemporaryDirectory(prefix='sdk-ab-judge-target-') as target_dir:
            target = Path(target_dir) / 'prompt.txt'
            target.write_text('original', encoding='utf-8')
            score_dir.mkdir(parents=True, exist_ok=True)
            symlink = score_dir / 'prompt.txt'
            symlink.symlink_to(target)
            _write_text_evidence(REPO_ROOT, symlink, 'new prompt')
            self.assertTrue(symlink.is_symlink())
            self.assertEqual(target.read_text(encoding='utf-8'), 'original')

    def test_write_text_evidence_resets_existing_file_permissions(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        score_dir = evidence_root / '1234567890abcdef' / 'judge'
        prompt_file = score_dir / 'prompt.txt'
        score_dir.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text('old prompt', encoding='utf-8')
        prompt_file.chmod(0o644)
        _write_text_evidence(REPO_ROOT, prompt_file, 'new prompt')
        self.assertEqual(prompt_file.read_text(encoding='utf-8'), 'new prompt')
        self.assertEqual(prompt_file.stat().st_mode & 0o777, 0o600)

    def test_evidence_preflight_rejects_existing_file_experiment_root(self) -> None:
        evidence_root = REPO_ROOT / self.evidence_root
        evidence_root.mkdir(parents=True, exist_ok=True)
        (evidence_root / '1234567890abcdef').write_text('not a directory', encoding='utf-8')
        evidence = _score_evidence_paths(REPO_ROOT, self.evidence_root, '1234567890abcdef')
        self.assertEqual(evidence['blocker'], 'evidence_root_not_directory')
        self.assertIsNone(evidence['prompt_path'])
        self.assertIsNone(evidence['output_path'])

    def test_local_codex_runner_uses_oss_local_profile(self) -> None:
        result, captured_command, captured_env, captured_profile_text, _op_env_file = _run_codex_with_captured_subprocess('oss-local', 'model = "qwen3.5:9b-mlx"\nmodel_provider = "ollama"\nsandbox_mode = "read-only"\n', {'id': 'oss-local', 'codex_profile': 'oss-local', 'model': 'qwen3.5:9b-mlx'})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:4], ['codex', 'exec', '--profile', 'oss-local'])
        self.assertIn('--sandbox', captured_command)
        self.assertIn('read-only', captured_command)
        self.assertIn('--ephemeral', captured_command)
        self.assertIn('--skip-git-repo-check', captured_command)
        self.assertIn('--output-last-message', captured_command)
        self.assertIn('--cd', captured_command)
        self.assertNotEqual(captured_command[captured_command.index('--cd') + 1], str(REPO_ROOT))
        self.assertEqual(result.output_text, '{}')
        self.assertIn('CODEX_HOME', captured_env)
        self.assertIn('CODEX_SQLITE_HOME', captured_env)
        self.assertIn('model = "qwen3.5:9b-mlx"', captured_profile_text)
        self.assertIn('model_catalog_json = "', captured_profile_text)
        self.assertIn('model_context_window = 262144', captured_profile_text)
        self.assertIn('hide_agent_reasoning = true', captured_profile_text)
        self.assertNotIn('OPENAI_API_KEY', captured_env)
        self.assertNotIn('OLLAMA_API_KEY', captured_env)
        self.assertNotIn('GITHUB_TOKEN', captured_env)

    def test_code_heavy_codex_runner_uses_dedicated_local_profile(self) -> None:
        result, captured_command, _captured_env, captured_profile_text, _op_env_file = _run_codex_with_captured_subprocess('oss-local-code', 'model = "qwen3-coder:30b"\nmodel_provider = "ollama"\nsandbox_mode = "read-only"\n', {'id': 'oss-local-code', 'codex_profile': 'oss-local-code', 'model': 'qwen3-coder:30b'})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:4], ['codex', 'exec', '--profile', 'oss-local-code'])
        self.assertIn('model = "qwen3-coder:30b"', captured_profile_text)

    def test_fallback_codex_runner_uses_dedicated_local_profile(self) -> None:
        result, captured_command, _captured_env, captured_profile_text, _op_env_file = _run_codex_with_captured_subprocess('oss-local-fallback', 'model = "qwen3.5:latest"\nmodel_provider = "ollama"\nsandbox_mode = "read-only"\n', {'id': 'oss-local-fallback', 'codex_profile': 'oss-local-fallback', 'model': 'qwen3.5:latest'})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:4], ['codex', 'exec', '--profile', 'oss-local-fallback'])
        self.assertIn('model = "qwen3.5:latest"', captured_profile_text)

    def test_cloud_codex_runner_uses_configs_auth_and_execution_wrappers(self) -> None:
        result, captured_command, captured_env, captured_profile_text, auth_env_file = _run_codex_with_captured_subprocess('oss-cloud', 'model = "deepseek-v4-flash:0731-cloud"\nmodel_provider = "ollama-cloud"\nsandbox_mode = "read-only"\n', {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}, {'OPENAI_API_KEY': 'other-token', 'GITHUB_TOKEN': 'repo-token'})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(captured_command[:7], ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh', '--env-file', str(auth_env_file), '--require-env', 'OLLAMA_API_KEY', '--'])
        self.assertEqual(captured_command[7:11], ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh', '--profile', 'oss-cloud'])
        self.assertIn('--strict-config', captured_command)
        self.assertIn('--model', captured_command)
        self.assertIn('deepseek-v4-flash:0731-cloud', captured_command)
        self.assertNotIn('op', captured_command)
        self.assertNotIn('OLLAMA_API_KEY', captured_env)
        self.assertIn('model = "deepseek-v4-flash:0731-cloud"', captured_profile_text)
        self.assertNotIn('OPENAI_API_KEY', captured_env)
        self.assertNotIn('GITHUB_TOKEN', captured_env)

__all__ = [name for name in globals() if not name.startswith("__")]
