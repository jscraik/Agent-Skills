from skills_sdk_ab_judge_score_tests_01 import *  # noqa: F403

class TestSkillsSdkAbJudgeScore(_SkillsSdkAbJudgeScoreBase):
    def test_cloud_codex_command_uses_oss_cloud_profile(self) -> None:
        output_file = REPO_ROOT / self.evidence_root / 'judge' / 'codex-last-message.json'
        with tempfile.TemporaryDirectory() as profile_dir:
            env_dir = Path(profile_dir) / '.codex'
            env_dir.mkdir()
            auth_env_file = env_dir / '.env'
            os.mkfifo(auth_env_file)
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(auth_env_file)}), patch('ask.skills_sdk.ab_transport_contracts.operator_account_home', return_value=Path(profile_dir)):
                command = _codex_judge_command({'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}, codex_judge._codex_judge_work_dir(output_file), output_file)
        self.assertEqual(command[:11], ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh', '--env-file', str(auth_env_file), '--require-env', 'OLLAMA_API_KEY', '--', 'bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh', '--profile', 'oss-cloud'])
        self.assertIn('--model', command)
        self.assertIn('deepseek-v4-flash:0731-cloud', command)
        self.assertIn('--strict-config', command)
        self.assertIn('--skip-git-repo-check', command)
        self.assertIn('--cd', command)
        self.assertNotIn(str(REPO_ROOT), command)
        shape = _codex_judge_command_shape({'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}, codex_judge._codex_judge_work_dir(output_file), output_file)
        self.assertEqual(shape[:4], ['codex', 'exec', '--profile', 'oss-cloud'])
        self.assertNotIn(str(output_file), shape)
        self.assertNotIn(str(codex_judge._codex_judge_work_dir(output_file)), shape)

    def test_cloud_auth_env_file_requires_a_desktop_fifo(self) -> None:
        profile = {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}
        with tempfile.TemporaryDirectory() as profile_dir:
            env_file = Path(profile_dir) / 'codex.env'
            env_file.write_text('', encoding='utf-8')
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(env_file)}):
                self.assertIsNone(codex_judge._codex_auth_env_file_path(profile))

    def test_cloud_judge_rejects_direct_codex_when_configs_boundary_is_missing(self) -> None:
        output_file = REPO_ROOT / self.evidence_root / 'judge' / 'codex-last-message.json'
        profile = {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}
        with tempfile.TemporaryDirectory() as profile_dir:
            env_file = Path(profile_dir) / 'codex.env'
            env_file.write_text('not a FIFO\n', encoding='utf-8')
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(env_file)}, clear=True):
                with self.assertRaises(codex_judge.CodexProfileConfigError):
                    _codex_judge_command(profile, codex_judge._codex_judge_work_dir(output_file), output_file)
            env_file.write_text('not a FIFO\n', encoding='utf-8')
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(env_file)}):
                self.assertIsNone(codex_judge._codex_auth_env_file_path(profile))

    @unittest.skipIf(not hasattr(os, 'mkfifo'), 'fifo support unavailable')
    def test_cloud_codex_command_accepts_desktop_fifo(self) -> None:
        output_file = REPO_ROOT / self.evidence_root / 'judge' / 'codex-last-message.json'
        profile = {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}
        with tempfile.TemporaryDirectory() as profile_dir:
            env_dir = Path(profile_dir) / '.codex'
            env_dir.mkdir()
            auth_env_file = env_dir / '.env'
            os.mkfifo(auth_env_file)
            env_patch = patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(auth_env_file)})
            with env_patch, patch('ask.skills_sdk.ab_transport_contracts.operator_account_home', return_value=Path(profile_dir)):
                command = _codex_judge_command(profile, codex_judge._codex_judge_work_dir(output_file), output_file)
                shape = _codex_judge_command_shape(profile, codex_judge._codex_judge_work_dir(output_file), output_file)
        self.assertEqual(command[2:7], ['--env-file', str(auth_env_file), '--require-env', 'OLLAMA_API_KEY', '--'])
        self.assertEqual(command[7:11], ['bash', '/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh', '--profile', 'oss-cloud'])
        self.assertEqual(shape[:4], ['codex', 'exec', '--profile', 'oss-cloud'])

    @unittest.skipIf(not hasattr(os, 'mkfifo'), 'fifo support unavailable')
    def test_cloud_judge_contains_runtime_output_and_copies_receipt(self) -> None:
        profile = {'id': 'oss-cloud', 'model': 'deepseek-v4-flash:0731-cloud', 'secret_env_names': ['OLLAMA_API_KEY']}
        with tempfile.TemporaryDirectory() as profile_dir, tempfile.TemporaryDirectory() as evidence_dir:
            profile_root = Path(profile_dir)
            env_file = profile_root / '.codex' / '.env'
            env_file.parent.mkdir()
            os.mkfifo(env_file)
            output_file = Path(evidence_dir) / 'judge' / 'codex-last-message.json'
            captured: dict[str, object] = {}

            def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                captured['cwd'] = kwargs['cwd']
                output_path = Path(args[args.index('--output-last-message') + 1])
                self.assertFalse(output_path.is_absolute())
                runtime_output = Path(kwargs['cwd']) / output_path
                runtime_output.write_text('{"winner":"skill_b"}', encoding='utf-8')
                return subprocess.CompletedProcess(args=args, returncode=0, stdout='events', stderr='')
            with patch.dict(os.environ, {'SKILLS_SDK_OSS_CLOUD_ENV_FILE': str(env_file)}, clear=False), patch('ask.skills_sdk.ab_transport_contracts.operator_account_home', return_value=profile_root), patch('ask.skills_sdk.eval_ab_judge_codex.subprocess.run', side_effect=fake_run):
                result = _run_codex_judge('prompt', profile, 5, REPO_ROOT, output_file)
            expected_work_dir = codex_judge._codex_judge_work_dir(output_file)
            self.assertEqual(captured['cwd'], expected_work_dir)
            self.assertEqual(result.output_text, '{"winner":"skill_b"}')
            self.assertEqual(output_file.read_text(encoding='utf-8'), '{"winner":"skill_b"}')
            self.assertEqual(result.executed_argv[result.executed_argv.index('--output-last-message') + 1], 'codex-last-message.json')
            shutil.rmtree(expected_work_dir, ignore_errors=True)

__all__ = [name for name in globals() if not name.startswith("__")]
