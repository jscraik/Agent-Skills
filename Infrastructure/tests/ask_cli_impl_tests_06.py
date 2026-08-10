from ask_cli_impl_tests_05 import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_runtime_missing_action_human_output_exposes_validation(self):
        """Verify incomplete runtime commands render the recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'runtime', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'runtime output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'runtime'", result.stdout)
        self.assertIn('Validation: ./bin/ask runtime surface --json --robot', result.stdout)

    def test_runtime_missing_action_json_contract_exposes_validation(self):
        """Verify incomplete runtime commands expose the surface recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'runtime', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'runtime output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask runtime surface --json --robot'])

    def test_repo_surface_json_contract_exposes_validation(self):
        """Verify repo surface exposes its replay command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'surface', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'repo surface output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('repo_surface', output['data'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask repo surface --json --robot'])

    def test_repo_surface_human_output_exposes_validation(self):
        """Verify repo surface human output names its replay command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'surface', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'repo surface output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Repo surface:', result.stdout)
        self.assertIn('Validation: ./bin/ask repo surface --json --robot', result.stdout)

    def test_runtime_budget_json_contract(self):
        """Verify ask runtime budget remains a first-class budget gate command."""
        saved_projection_mode = os.environ.get('SYNC_SKILLS_PROJECTION_MODE')
        try:
            os.environ['SYNC_SKILLS_PROJECTION_MODE'] = 'flat'
            cmd = ['python3', 'Infrastructure/bin/ask', 'runtime', 'budget', '--json']
            result = _run_cli(cmd)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output['status'], 'success')
            self.assertEqual(output['data']['runtime_budget']['status'], 'pass')
            self.assertEqual(output['data']['runtime_surface']['status'], 'pass')
            self.assertEqual(output['data']['validation_commands'], ['./bin/ask runtime budget --json --robot'])
        finally:
            if saved_projection_mode is None:
                os.environ.pop('SYNC_SKILLS_PROJECTION_MODE', None)
            else:
                os.environ['SYNC_SKILLS_PROJECTION_MODE'] = saved_projection_mode

    def test_runtime_budget_human_output_exposes_validation(self):
        """Verify ask runtime budget renders its runtime replay command."""
        saved_projection_mode = os.environ.get('SYNC_SKILLS_PROJECTION_MODE')
        try:
            os.environ['SYNC_SKILLS_PROJECTION_MODE'] = 'flat'
            cmd = ['python3', 'Infrastructure/bin/ask', 'runtime', 'budget', '--robot']
            result = _run_cli(cmd)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Runtime budget:', result.stdout)
            self.assertIn('Validation: ./bin/ask runtime budget --json --robot', result.stdout)
        finally:
            if saved_projection_mode is None:
                os.environ.pop('SYNC_SKILLS_PROJECTION_MODE', None)
            else:
                os.environ['SYNC_SKILLS_PROJECTION_MODE'] = saved_projection_mode

    def test_graph_list_json_contract_exposes_validation(self):
        """Verify graph list exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'list', '--topic-filter', 'agent-ops', '--tier', 'experimental', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph list output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph list --topic-filter agent-ops --tier experimental --json --robot'])

    def test_graph_list_human_output_exposes_validation(self):
        """Verify graph list human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'list', '--topic-filter', 'agent-ops', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph list output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Skills [topic=agent-ops]', result.stdout)
        self.assertIn('Validation: ./bin/ask graph list --topic-filter agent-ops --json --robot', result.stdout)

    def test_graph_topics_json_contract_exposes_validation(self):
        """Verify graph topics exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'topics', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph topics output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph topics --json --robot'])

    def test_graph_topics_human_output_exposes_validation(self):
        """Verify graph topics human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'topics', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph topics output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Topic Clusters', result.stdout)
        self.assertIn('Validation: ./bin/ask graph topics --json --robot', result.stdout)

    def test_graph_missing_action_exposes_validation(self):
        """Verify incomplete graph commands expose the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'graph output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph list --json --robot'])

    def test_graph_missing_action_human_output_exposes_validation(self):
        """Verify incomplete graph commands render the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'graph output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'graph'", result.stdout)
        self.assertIn('Validation: ./bin/ask graph list --json --robot', result.stdout)

    def test_graph_related_json_contract_exposes_validation(self):
        """Verify graph related exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'related', 'agents-md', '--depth', '2', '--reverse', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph related output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph related agents-md --depth 2 --reverse --json --robot'])

    def test_graph_related_human_output_exposes_validation(self):
        """Verify graph related human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'related', 'agents-md', '--depth', '2', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph related output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('agents-md [out-links, depth=2]', result.stdout)
        self.assertIn('Validation: ./bin/ask graph related agents-md --depth 2 --json --robot', result.stdout)

    def test_graph_find_json_contract_exposes_validation(self):
        """Verify graph find exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'find', 'agent', '--topic-filter', 'agent-ops', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph find output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph find agent --topic-filter agent-ops --json --robot'])

    def test_graph_find_human_output_exposes_validation(self):
        """Verify graph find human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'find', 'agent', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph find output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("Search: 'agent'", result.stdout)
        self.assertIn('Validation: ./bin/ask graph find agent --json --robot', result.stdout)

    def test_graph_info_json_contract_exposes_validation(self):
        """Verify graph info exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'info', 'agents-md', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph info output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph info agents-md --json --robot'])

    def test_graph_info_unknown_skill_exposes_recovery_commands(self):
        """Verify an unknown graph skill points agents to inspect valid ids."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'info', 'definitely-missing', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'graph info output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertEqual(output['errors'][0]['fix_suggestion'], 'Search available skill ids with: ./bin/ask graph find definitely-missing --json --robot; if no matches are returned, run ./bin/ask graph list --json --robot')

    def test_graph_info_human_output_exposes_validation(self):
        """Verify graph info human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'info', 'agents-md', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph info output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('agents-md', result.stdout)
        self.assertIn('Validation: ./bin/ask graph info agents-md --json --robot', result.stdout)

    def test_graph_chain_json_contract_exposes_validation(self):
        """Verify graph chain exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'chain', 'agents-md', 'verification-before-completion', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph chain output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data']['reachable'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask graph chain agents-md verification-before-completion --json --robot'])

    def test_graph_chain_human_output_exposes_validation(self):
        """Verify graph chain human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'graph', 'chain', 'agents-md', 'verification-before-completion', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'graph chain output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Chain (', result.stdout)
        self.assertIn('Validation: ./bin/ask graph chain agents-md verification-before-completion --json --robot', result.stdout)

    def test_skills_sync_projection_reaches_engine(self):
        """Verify --projection is dispatched and cannot be silently ignored."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'workspace', '--projection', 'flat', '--dry-run', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['projection_mode'], 'flat')
        self.assertEqual(output['data']['projection']['engine'], 'projection_engine.py')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills sync --dry-run --projection flat --json --robot'])

    def test_skills_sync_rejects_removed_rooted_projection(self):
        """Rooted mode is removed from the SDK-flat sync contract."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'workspace', '--projection', 'rooted', '--dry-run', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIsNone(output['data']['projection_mode'])
        self.assertEqual(output['data']['requested_projection_mode'], 'rooted')
        self.assertEqual(output['errors'][0]['code'], 'ERR_INVALID_PROJECTION_MODE')

    def test_skills_sync_rejects_removed_skill_tree_alias(self):
        """Rooted aliases are removed with rooted mode."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'workspace', '--projection', 'skill-tree', '--dry-run', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIsNone(output['data']['projection_mode'])
        self.assertEqual(output['data']['requested_projection_mode'], 'skill-tree')
        self.assertEqual(output['errors'][0]['code'], 'ERR_INVALID_PROJECTION_MODE')

    def test_skills_sync_rejects_deferred_hybrid_projection(self):
        """Hybrid remains out of mutating scope until a named consumer exists."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'workspace', '--projection', 'hybrid', '--dry-run', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIsNone(output['data']['projection_mode'])
        self.assertEqual(output['data']['requested_projection_mode'], 'hybrid')
        self.assertEqual(output['errors'][0]['code'], 'ERR_DEFERRED_PROJECTION_MODE')

    def test_skills_install_dry_run(self):
        """CA2: Verify ask skills install --dry-run returns a plan without making changes."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'install', 'https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication', '--dry-run', '--json']
        result = _run_cli(cmd)
        output = json.loads(result.stdout)
        self.assertIn(output['status'], ['success', 'error'])
        if output['status'] == 'success':
            self.assertIn('skill_name', output['data'])
            self.assertTrue(output['data'].get('dry_run', False), 'Expected dry_run to be True')
            intake = output['data'].get('intake_decision')
            self.assertIsInstance(intake, dict)
            self.assertEqual(intake.get('schema_version'), 'skill-install-intake.v1')
            self.assertIn(intake.get('outcome'), intake.get('allowed_outcomes', []))
            self.assertIn('post_install_gates', intake)
            readiness = output['data'].get('readiness_policy')
            self.assertTrue(readiness.get('full_evals_required_before_promotion'))
            self.assertTrue(readiness.get('external_skill_install_is_intake_not_copy'))
            self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills install https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication --dest Skills/github --dry-run --json --robot'])

    def test_skills_install_dry_run_human_output_exposes_validation(self):
        """Verify ask skills install --dry-run renders its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'install', 'https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Dry run - would install:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills install https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication --dest Skills/github --dry-run --json --robot', result.stdout)

    def test_skills_external_review_skip_tools_json_contract(self):
        """Verify ask skills external-review exposes a replayable local-only contract."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'external-review', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--skip-plugin-eval', '--skip-tessl', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['plugin_eval']['status'], 'skipped')
        self.assertEqual(output['data']['tessl_lint']['status'], 'skipped')
        self.assertEqual(output['data']['policy']['plugin_eval_min_acceptable_grade'], 'B+')
        self.assertEqual(output['data']['policy']['tessl_review_min_score'], 95)
        self.assertEqual(output['data']['policy']['tessl_review_target_score'], 95)
        self.assertEqual(output['data']['policy']['tessl_project_marker'], 'tessl.json')
        self.assertIn(os.path.join(tempfile.gettempdir(), 'ask-tessl-reviews'), output['data']['policy']['tessl_staging_root'])
        self.assertEqual(output['data']['review_mode_details']['tessl_review']['minimum_score'], 95)
        self.assertEqual(output['data']['review_mode_details']['tessl_review']['target_score'], 95)
        self.assertIn('--threshold 95', output['data']['review_mode_details']['tessl_review']['command'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills external-review Plugins/skill-factory/skills/code_quality_review/skill-builder --skip-plugin-eval --skip-tessl --json --robot'])

    def test_skills_external_review_skip_tools_human_output_exposes_validation(self):
        """Verify ask skills external-review renders local-only status and validation."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'external-review', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--skip-plugin-eval', '--skip-tessl', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('External review:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills external-review Plugins/skill-factory/skills/code_quality_review/skill-builder --skip-plugin-eval --skip-tessl --json --robot', result.stdout)

    def test_skills_fold_dependency_error_exposes_validation(self):
        """Verify ask skills fold dependency blockers remain replayable."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'fold', 'simplify', 'imagegen', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_DEPENDENCY')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills fold simplify imagegen --json --robot'])
        self.assertIn(output['data']['dependency_status']['skill_catalog'], {'load_failed', 'missing'})

    def test_skills_fold_dependency_error_human_output_exposes_validation(self):
        """Verify ask skills fold dependency blockers render their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'fold', 'simplify', 'imagegen', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Skill router or builder catalog not available.', result.stdout)
        self.assertIn('Validation: ./bin/ask skills fold simplify imagegen --json --robot', result.stdout)

    def test_trace_id_from_env(self):
        """CA2: ASK_TRACE_ID environment variable propagates to output."""
        env = os.environ.copy()
        env['ASK_TRACE_ID'] = 'test-trace-123'
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'status', '--json']
        result = _run_cli(cmd, env=env)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['trace_id'], 'test-trace-123')

    def test_trace_id_flag_overrides_env(self):
        """CA2: --trace-id flag overrides ASK_TRACE_ID environment variable."""
        env = os.environ.copy()
        env['ASK_TRACE_ID'] = 'env-trace-456'
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'status', '--json', '--trace-id', 'flag-trace-789']
        result = _run_cli(cmd, env=env)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['trace_id'], 'flag-trace-789')

    def test_robot_mode_recovers_swapped_topic_action(self):
        """Robot mode should recover clear intent when topic/action are swapped."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'list', 'skills', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'Expected success, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertIn('skills', output.get('data', {}))
        self.assertIn('correction_note', output.get('metadata', {}))

    def test_robot_mode_recovers_action_after_flags(self):
        """Robot mode should recover when action token is after option flags."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', '--advanced', 'ls', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'Expected success, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data'].get('advanced_mode'))
        self.assertIn('correction_note', output.get('metadata', {}))

    def test_robot_mode_returns_detailed_error_for_ambiguous_intent(self):
        """Robot mode should return rich guidance when intent cannot be resolved."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'status', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        message = output['errors'][0]['message']
        self.assertIn('Guidance', message)
        self.assertIn('Try one of these', message)
        self.assertIn('repo status', message)

    def test_robot_mode_returns_argument_guidance_when_intent_clear(self):
        """Robot mode should explain missing arguments with command-specific examples."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'audit', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        message = output['errors'][0]['message']
        self.assertIn('Command intent was understood', message)
        self.assertIn('ask skills audit --help', message)
        self.assertIn('Valid examples', message)
        self.assertIn('skills audit', message)

    def test_skills_audit_json_contract(self):
        """Verify ask skills audit exposes its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'audit', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['diagnostics']['exit_code'], 0)
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills audit Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot'])

    def test_skills_audit_accepts_explicit_external_project_skill(self):
        """Verify Skill Factory audit can inspect project-local skills outside the foundry."""
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / 'x-writer' / '.codex' / 'skills' / 'draft-helper'
            skill_dir.mkdir(parents=True)
            (skill_dir / 'SKILL.md').write_text('---\nname: draft-helper\ndescription: Use when improving a project-local writing workflow.\n---\n\n# Draft Helper\n', encoding='utf-8')
            cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / 'bin' / 'ask'), 'skills', 'audit', str(skill_dir), '--json', '--robot']
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['audit_scope']['classification'], 'external_project_skill')
        self.assertFalse(output['data']['audit_scope']['repo_coupled_gates'])
        diagnostics = output['data']['diagnostics']
        self.assertEqual(diagnostics['exit_code'], 0)
        self.assertIn('external project skill', diagnostics['stdout'])

    def test_skills_audit_accepts_explicit_external_project_skill_root(self):
        """Verify Skill Factory audit can inspect a project-local .codex/skills root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / 'x-writer' / '.codex' / 'skills'
            for name in ('draft-helper', 'style-check'):
                skill_dir = skills_root / name
                skill_dir.mkdir(parents=True)
                (skill_dir / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Use when improving a project-local writing workflow.\n---\n\n# {name}\n', encoding='utf-8')
            cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / 'bin' / 'ask'), 'skills', 'audit', str(skills_root), '--json', '--robot']
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['audit_scope']['classification'], 'external_project_skill_root')
        self.assertEqual(output['data']['audit_scope']['child_count'], 2)
        self.assertEqual([child['status'] for child in output['data']['children']], ['success', 'success'])

    def test_skills_audit_human_output_exposes_validation(self):
        """Verify ask skills audit renders its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'audit', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Audit passed:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills audit Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot', result.stdout)

    def test_skills_validate_openai_format_json_contract(self):
        """Verify ask exposes OpenAI skill format as a first-class validation surface."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'validate-openai-format', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        gate = output['data']['openai_skill_format']
        self.assertEqual(gate['exit_code'], 0)
        self.assertIn('lint_openai_skill_format.sh', ' '.join(gate['command']))
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills validate-openai-format Plugins/skill-factory/skills/code_quality_review/skill-builder --mode strict --json --robot'])

    def test_skills_validate_openai_format_human_output_exposes_validation(self):
        """Verify ask skills validate-openai-format renders its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'validate-openai-format', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('OpenAI skill format passed:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills validate-openai-format Plugins/skill-factory/skills/code_quality_review/skill-builder --mode strict --json --robot', result.stdout)

    def test_skills_validate_skill_gate_json_contract(self):
        """Verify ask exposes skill gate as a first-class validation surface."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'validate-skill-gate', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        gate = output['data']['skill_gate']
        self.assertEqual(gate['exit_code'], 0)
        self.assertTrue(any(('skill_gate.py' in part for part in gate['command'])))
        self.assertNotIn('SEC_CANONICAL_HEADER_ORDER', gate['stdout'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills validate-skill-gate Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot'])

    def test_skills_validate_skill_gate_human_output_exposes_validation(self):
        """Verify ask skills validate-skill-gate renders its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'validate-skill-gate', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Skill gate passed:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills validate-skill-gate Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot', result.stdout)

    def test_skills_validate_boundaries_json_contract(self):
        """Verify ask exposes canonical-versus-projection ownership as a first-class check."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'validate-boundaries', 'Skills/agent-ops/autofix', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        boundary = output['data']['boundary_check']
        self.assertEqual(boundary['status'], 'pass')
        self.assertEqual(boundary['handle'], 'autofix')
        self.assertEqual(boundary['canonical_skill_path'], 'Skills/agent-ops/autofix/SKILL.md')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills validate-boundaries Skills/agent-ops/autofix --json --robot'])

    def test_skills_validate_boundaries_human_output_exposes_validation(self):
        """Verify ask skills validate-boundaries renders its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'validate-boundaries', 'Skills/agent-ops/autofix', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Skill boundaries passed: $autofix', result.stdout)
        self.assertIn('Canonical source:', result.stdout)
        self.assertIn('Note: Edit the canonical source path', result.stdout)
        self.assertIn('Validation: ./bin/ask skills validate-boundaries Skills/agent-ops/autofix --json --robot', result.stdout)

    def test_skills_init_validation_error_exposes_validation(self):
        """Verify ask skills init validation errors remain replayable without writing files."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'init', 'example-skill', '--category', '/tmp/not-repo-relative', '--description', 'Example description', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertEqual(output['data']['validation_commands'], ["./bin/ask skills init example-skill --category /tmp/not-repo-relative --description 'Example description' --json --robot"])

    def test_skills_init_validation_error_human_output_exposes_validation(self):
        """Verify ask skills init validation errors render their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'init', 'example-skill', '--category', '/tmp/not-repo-relative', '--description', 'Example description', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Skill category must be repo-relative.', result.stdout)
        self.assertIn("Validation: ./bin/ask skills init example-skill --category /tmp/not-repo-relative --description 'Example description' --json --robot", result.stdout)

    def test_workouts_list_json_contract_exposes_validation(self):
        """Verify ask workouts list exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'workouts', 'list', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertIn('workouts', output['data'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask workouts list --json --robot'])

    def test_workouts_list_human_output_exposes_validation(self):
        """Verify ask workouts list renders its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'workouts', 'list', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Workout list: success', result.stdout)
        self.assertIn('Validation: ./bin/ask workouts list --json --robot', result.stdout)

    def test_workouts_missing_action_exposes_validation(self):
        """Verify incomplete workout commands expose the list recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'workouts', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'workouts output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask workouts list --json --robot'])

    def test_workouts_missing_action_human_output_exposes_validation(self):
        """Verify incomplete workout commands render the list recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'workouts', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'workouts output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'workouts'", result.stdout)
        self.assertIn('Validation: ./bin/ask workouts list --json --robot', result.stdout)

    def test_workouts_score_error_json_contract_exposes_validation(self):
        """Verify ask workouts score validation errors remain replayable."""
        workout_id = 'agent-ops/not-a-real-workout'
        cmd = ['python3', 'Infrastructure/bin/ask', 'workouts', 'score', workout_id, '--json', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['data']['validation_commands'], [f'./bin/ask workouts score {workout_id} --json --robot'])

    def test_workouts_score_error_human_output_exposes_validation(self):
        """Verify ask workouts score validation errors render their replay command."""
        workout_id = 'agent-ops/not-a-real-workout'
        cmd = ['python3', 'Infrastructure/bin/ask', 'workouts', 'score', workout_id, '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f'No scorecard found for workout {workout_id}.', result.stdout)
        self.assertIn(f'Validation: ./bin/ask workouts score {workout_id} --json --robot', result.stdout)

    def test_plugins_init_validation_error_exposes_validation(self):
        """Verify plugins init validation errors expose a replay command without writing."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'init', 'example-plugin', '--category', '/tmp/not-a-plugin-category', '--with-marketplace', '--with-scripts', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins init example-plugin --category /tmp/not-a-plugin-category --with-marketplace --with-scripts --json --robot'])

__all__ = [name for name in globals() if not name.startswith("__")]
