from ask_cli_impl_tests_02 import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_sdk_unknown_action_keeps_expert_routes_out_of_default_recovery(self):
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'sdk', 'unsupported-action', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        error = output['errors'][0]
        self.assertEqual(error['fix_suggestion'], 'Valid actions: start, check')
        self.assertIn('choose from start, check', error['message'])
        self.assertNotIn('score', error['message'])
        self.assertNotIn('lifecycle', error['message'])
        self.assertEqual(output['data']['candidate_commands'], ['ask sdk start Skills/agent-ops/simplify --json --robot', 'ask sdk check Skills/agent-ops/simplify --json --robot'])

    def test_ambiguous_action_first_error_exposes_candidate_commands(self):
        """Verify ambiguous action-first parser errors expose machine-readable candidates."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'list', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('ambiguous', output['errors'][0]['message'])
        self.assertEqual(output['data']['candidate_commands'], ['ask skills list', 'ask plugins list', 'ask graph list'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask sdk start <skill> --json --robot', './bin/ask plugins list --json --robot', './bin/ask graph list --json --robot'])

    def test_argument_error_exposes_candidate_commands(self):
        """
            Verify that missing required arguments in known commands expose candidate command examples.

            Tests that when a required argument is omitted (e.g., `skills resolve --json --robot` without a skill identifier), the error response includes candidate commands matching the expected argument pattern.
            """
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'resolve', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('argument syntax is invalid', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills resolve --help'])
        self.assertEqual(len(output['data']['candidate_commands']), 1)
        self.assertRegex(output['data']['candidate_commands'][0], '^ask skills resolve Skills/agent-ops/[a-z0-9-]+ --json$')

    def test_skills_missing_action_exposes_validation(self):
        """Verify incomplete skills commands expose the read-only recovery command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask sdk start <skill> --json --robot'])

    def test_skills_missing_action_human_output_exposes_validation(self):
        """Verify incomplete skills commands render the read-only recovery command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("missing action for topic 'skills'", result.stdout)
        self.assertIn('Validation: ./bin/ask sdk start <skill> --json --robot', result.stdout)

    def test_skills_goal_json_contract(self):
        """
            Ensure the `ask skills goal create` CLI returns a JSON envelope containing a `goal_decision` with required fields.

            Asserts the top-level `status` and `data` keys exist and that `data.goal_decision` includes `schema_version`, `decision_status`, `policy_identity`, `recommended_candidate`, and `alternative_candidates`.
            """
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'goal', 'create auth integration', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('status', output)
        self.assertIn('data', output)
        self.assertIn('goal_decision', output['data'])
        goal = output['data']['goal_decision']
        self.assertEqual(goal.get('schema_version'), 'goal-decision.v1')
        self.assertIn('decision_status', goal)
        self.assertIn('policy_identity', goal)
        self.assertIn('recommended_candidate', goal)
        self.assertIn('alternative_candidates', goal)
        self.assertEqual(goal.get('validation_commands'), ["./bin/ask skills goal 'create auth integration' --json --robot"])

    def test_skills_goal_human_output_exposes_validation(self):
        """Verify ambiguous goal output renders the goal validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'goal', 'help me', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('🎯 Goal decision:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills goal', result.stdout)
        self.assertIn('--json --robot', result.stdout)

    def test_skills_improve_json_contract(self):
        """Verify `ask skills improve` returns an agent-facing recommendation envelope."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'skills', 'improve', 'autofix', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        improvement = output.get('data', {}).get('improvement', {})
        self.assertEqual(improvement.get('schema_version'), 'skill-improvement-recommendation.v1')
        self.assertIn(improvement.get('route_state'), {'blocked_reachability', 'resolved', 'resolved_with_fallback'})
        self.assertIn('route_state_reason', improvement)
        self.assertIn('goal_decision_status', improvement)
        self.assertIn('agent_summary', improvement)
        self.assertIn('recommended_capability', improvement)
        self.assertIn('why', improvement)
        self.assertIn('reachability', improvement)
        self.assertIn('proof', improvement)
        self.assertIn('why', improvement)
        self.assertIn('next_command', improvement)
        self.assertEqual(improvement['validation_commands'], [improvement['next_command']])

    def test_skills_improve_human_output_exposes_validation(self):
        """Verify ask skills improve renders the recommendation validation command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'skills', 'improve', 'autofix', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'skills improve output: {result.stdout}\nstderr: {result.stderr}')
        if result.returncode == 0:
            self.assertIn('🎯 Skill improvement:', result.stdout)
            self.assertIn('Recommended:', result.stdout)
            self.assertIn('Reachability: pass', result.stdout)
            self.assertIn('Validation: ./bin/ask skills proof', result.stdout)
            self.assertIn('Next: ./bin/ask skills proof', result.stdout)
        else:
            self.assertIn("SDK skill proof failed for 'autofix'", result.stdout)
            self.assertIn('skills sync --scope user --projection flat --dry-run', result.stdout)

    def test_repo_doctor_catalog_json_contract(self):
        """
            Verify `ask repo doctor-catalog --json` returns a catalog parity payload with required fields.

            Asserts the CLI emits non-empty JSON and that `data.catalog_parity` contains `schema_version`, `drift_detected` and `surfaces`.
            """
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'doctor-catalog', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('status', output)
        self.assertIn('catalog_parity', output.get('data', {}))
        report = output['data']['catalog_parity']
        self.assertEqual(report.get('schema_version'), 'catalog-parity.v1')
        self.assertIn('drift_detected', report)
        self.assertIn('surfaces', report)

    def test_repo_doctor_json_contract(self):
        """Verify `ask repo doctor --json` exposes the golden-path payload."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'doctor', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        doctor = output.get('data', {}).get('doctor', {})
        self.assertIn('agent_summary', doctor)
        self.assertIn('blocking', doctor)
        self.assertIn('blockers', doctor)
        self.assertIn('next_command', doctor)
        self.assertIn('signals', doctor)
        self.assertIn('diagnostic_debt', doctor)
        capability = doctor['signals'].get('capability_readiness', {})
        projection = doctor['signals'].get('projection_sync', {})
        if projection.get('state') == 'warn':
            self.assertEqual(capability.get('state'), 'skipped')
            self.assertEqual(capability.get('source'), 'repo_status')
            self.assertIn('intentionally has no runtime projection', capability.get('summary', ''))
        else:
            self.assertEqual(capability.get('state'), 'pass')
            self.assertEqual(capability.get('source'), 'skills_profiles+skills_events')
        memory = doctor['signals'].get('memory_readiness', {})
        self.assertEqual(memory.get('state'), 'skipped' if projection.get('state') == 'warn' else 'pass')
        package = doctor['signals'].get('package_readiness', {})
        self.assertEqual(package.get('state'), 'skipped' if projection.get('state') == 'warn' else 'pass')

    def test_repo_doctor_human_output_includes_readiness_signals(self):
        """Verify repo doctor --robot prints capability-readiness signals."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'doctor', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Repo doctor:', result.stdout)
        self.assertIn('Usable with diagnostic debt', result.stdout)
        if 'Capability readiness:' not in result.stdout:
            self.assertIn('intentionally unmaterialized', result.stdout)
        self.assertIn('Next:', result.stdout)

    def test_repo_doctor_help_mentions_agent_health_entrypoint(self):
        """Verify `ask repo doctor --help` exposes the agent health wording."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'doctor', '--help']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Agent-facing repository health entrypoint', result.stdout)

    def test_repo_provider_audit_json_contract_exposes_validation(self):
        """Verify provider audit exposes its replay command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'provider-audit', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'provider audit output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('provider_policy', output['data'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask repo provider-audit --json --robot'])

    def test_repo_provider_audit_human_output_exposes_validation(self):
        """Verify provider audit human output names its replay command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'provider-audit', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'provider audit output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Provider policy:', result.stdout)
        self.assertIn('Validation: ./bin/ask repo provider-audit --json --robot', result.stdout)

    def test_repo_check_stability_json_contract_exposes_validation(self):
        """Verify check-stability exposes its replay command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'check-stability', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'check-stability output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('stable_skills', output['data'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask repo check-stability --json --robot'])

    def test_repo_check_stability_human_output_exposes_validation(self):
        """Verify check-stability human output names its replay command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'check-stability', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'check-stability output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Stability check passed', result.stdout)
        self.assertIn('Validation: ./bin/ask repo check-stability --json --robot', result.stdout)

    def test_repo_closeout_json_contract(self):
        """Verify `ask repo closeout --changed --json` exposes readiness fields."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'closeout', '--changed', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        closeout = output.get('data', {}).get('repo_closeout', {})
        self.assertIn('changed_files', closeout)
        self.assertIn('sync', closeout)
        self.assertIn('runtime_budget', closeout)
        self.assertIn('capability_readiness', closeout)
        self.assertIn('memory_readiness', closeout)
        self.assertIn('package_readiness', closeout)
        self.assertIn('surface_policy', closeout)
        self.assertIn('runtime_evidence', closeout)
        self.assertIn('focused_validation', closeout)
        self.assertIn('commit_readiness', closeout)
        self.assertIn('next_command', closeout)
        capability = closeout['capability_readiness']
        if capability['status'] == 'skipped':
            self.assertIn('intentionally has no runtime projection', capability['summary'])
        else:
            self.assertEqual(capability['status'], 'pass')
            self.assertIn(capability['profile_contract_status'], {'ready', None})
            self.assertEqual(capability['profile_contract_gap_count'], 0)
            self.assertIn(capability['event_contract_status'], {'ready', None})
            self.assertEqual(capability['event_contract_gap_count'], 0)
            self.assertIsInstance(capability['eval_blocker_classes'], list)
            self.assertEqual(capability['eval_blocker_class_count'], len(capability['eval_blocker_classes']))
            self.assertEqual(capability['contract_gap_count'], 0)
        memory = closeout['memory_readiness']
        if memory['status'] == 'skipped':
            self.assertIn('intentionally has no runtime projection', memory['summary'])
        else:
            self.assertEqual(memory['status'], 'pass')
            self.assertIn(memory['provider_model'], {'extension-like-read-only', None})
            self.assertGreaterEqual(memory['entry_count'], 0)
            self.assertIn('available_sources', memory)
            self.assertIsInstance(memory['by_freshness'], dict)
        package = closeout['package_readiness']
        if package['status'] == 'skipped':
            self.assertIn('intentionally has no runtime projection', package['summary'])
        else:
            self.assertEqual(package['status'], 'pass')
            self.assertIsInstance(package['target'], str)
        runtime_evidence = closeout['runtime_evidence']
        self.assertIn(runtime_evidence['status'], {'not_applicable', 'missing', 'present', 'invalid', 'deleted'})
        self.assertEqual(runtime_evidence['evidence_root'], '.harness/evidence/runtime-proof')
        self.assertIn('changed_scope', runtime_evidence)
        self.assertIn('workspace_scope', runtime_evidence)
        self.assertEqual(runtime_evidence['truth_boundaries']['command_proof'], 'workspace_runtime_evidence')
        if runtime_evidence['status'] == 'not_applicable':
            self.assertEqual(runtime_evidence['schema_validation']['status'], 'not_run')
            self.assertEqual(runtime_evidence['truth_boundaries']['schema_proof'], 'not_run_by_closeout_use_schema_validation_command')
        else:
            self.assertEqual(runtime_evidence['schema_validation']['status'], 'pass')
            self.assertEqual(runtime_evidence['truth_boundaries']['schema_proof'], 'checked_by_repo_closeout')
        self.assertEqual(runtime_evidence['truth_boundaries']['pr_truth'], 'not_checked_by_repo_closeout')
        self.assertEqual(runtime_evidence['truth_boundaries']['tracker_truth'], 'not_checked_by_repo_closeout')
        self.assertEqual(runtime_evidence['truth_boundaries']['docs_truth'], 'not_checked_by_repo_closeout')
        validation_ids = [command['id'] for command in closeout['focused_validation']]
        self.assertIn('skill_profiles_readiness', validation_ids)
        self.assertIn('skill_events_readiness', validation_ids)
        self.assertIn('skill_memory_readiness', validation_ids)
        self.assertIn('skill_package_readiness', validation_ids)
        package_validation = next((command for command in closeout['focused_validation'] if command['id'] == 'skill_package_readiness'))
        self.assertIn('--checkout-test', package_validation['command'])

    def test_repo_closeout_help_mentions_completion_readiness(self):
        """Verify `ask repo closeout --help` exposes completion-readiness wording."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'closeout', '--help']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('commit readiness', result.stdout)

    def test_repo_closeout_human_output_mentions_capability_readiness(self):
        """Verify non-JSON repo closeout output exposes readiness and validation cues."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'repo', 'closeout', '--changed', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'repo closeout output: {result.stdout}\nstderr: {result.stderr}')
        if result.returncode == 0:
            self.assertIn('Repo closeout: Ready: no closeout blockers detected.', result.stdout)
            self.assertIn('Commit ready: True', result.stdout)
        else:
            self.assertIn('Blocked: closeout has', result.stdout)
            json_result = _run_cli([*cmd, '--json'])
            self.assertEqual(json_result.returncode, result.returncode, json_result.stderr)
            closeout = json.loads(json_result.stdout)['data']['repo_closeout']
            next_command = closeout['next_command']
            self.assertIsInstance(next_command, str)
            self.assertTrue(next_command.startswith('./bin/ask '))
            self.assertIn(f'💡 {next_command}', result.stdout)
            return
        self.assertIn('Capability readiness:', result.stdout)
        self.assertIn('Memory readiness:', result.stdout)
        self.assertIn('Package readiness:', result.stdout)
        self.assertIn('Runtime evidence:', result.stdout)
        self.assertIn('command=workspace_runtime_evidence', result.stdout)
        self.assertTrue('schema=checked_by_repo_closeout' in result.stdout or 'schema=not_run_by_closeout_use_schema_validation_command' in result.stdout)
        self.assertIn('PR=not_checked_by_repo_closeout', result.stdout)
        self.assertIn('skill_profiles_readiness', result.stdout)
        self.assertIn('skill_events_readiness', result.stdout)
        self.assertIn('skill_memory_readiness', result.stdout)
        self.assertIn('skill_package_readiness', result.stdout)

    def test_goal_alias_normalization(self):
        """
            Ensure the `goal create` CLI alias returns a skills-style goal decision in the JSON envelope.

            Runs `bin/ask goal create auth integration --json`, asserts stdout contains JSON and that `data.goal_decision` exists.
            """
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'goal', 'create auth integration', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('goal_decision', output.get('data', {}))

    def test_goal_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json goal alias maps to ask skills goal."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', '--json', 'goal', 'create auth integration']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('goal_decision', output.get('data', {}))

    def test_doctor_catalog_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json doctor catalog alias maps to repo doctor-catalog."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', '--json', 'doctor', 'catalog']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('catalog_parity', output.get('data', {}))

    def test_skills_starter_mode(self):
        """
            Verify the CLI `skills starter` command returns starter-mode catalogue metadata for the chosen archetype.

            Runs `bin/ask skills starter --archetype delivery --limit 5 --json` and asserts the process exits with code 0, the JSON envelope `status` is `"success"`, `data.starter_mode` is truthy, `data.starter_archetype` equals `"delivery"`, and `data.skills` is a list.
            """
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'skills', 'starter', '--archetype', 'delivery', '--limit', '5', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills starter failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data'].get('starter_mode'))
        self.assertEqual(output['data'].get('starter_archetype'), 'delivery')
        self.assertIsInstance(output['data'].get('skills'), list)
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills starter --archetype delivery --limit 5 --json --robot'])

    def test_skills_starter_human_output_exposes_validation(self):
        """Verify ask skills starter renders its validation command."""
        cmd = [__import__('sys').executable, 'Infrastructure/bin/ask', 'skills', 'starter', '--archetype', 'delivery', '--limit', '5', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Starter skills (5) [delivery]', result.stdout)
        self.assertIn('Validation: ./bin/ask skills starter --archetype delivery --limit 5 --json --robot', result.stdout)

    def test_skills_package_command(self):
        """Verify ask skills package exposes package readiness metadata."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills package failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        package = output['data']['skill_package']
        self.assertEqual(package['schema_version'], 'skill-package-readiness.v1')
        self.assertIsNone(package['target_summary']['handle'])
        self.assertEqual(package['target_summary']['canonical_source_path'], 'Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md')
        self.assertEqual(package['target_summary']['target_kind'], package['target_kind'])
        self.assertIn('version', package['package_contract']['required_fields']['present'])
        self.assertEqual(package['readiness_summary']['readiness_level'], package['package_contract']['readiness_level'])
        self.assertIn('version', package['readiness_summary']['present_fields'])
        self.assertEqual(package['readiness_summary']['missing_field_count'], len(package['package_contract']['required_fields']['missing']))
        self.assertEqual(package['gate_summary']['promotion_status'], 'ready_pending_checkout')
        self.assertFalse(package['gate_summary']['promotion_ready'])
        self.assertTrue(package['package_contract']['install_gate']['install_ready'])
        self.assertEqual(package['package_contract']['install_gate']['checkout_test']['status'], 'not_run')
        self.assertEqual(package['package_contract']['promotion_gate']['status'], 'ready_pending_checkout')
        self.assertFalse(package['package_contract']['promotion_gate']['promotion_ready'])
        self.assertEqual(package['package_contract']['required_fields']['missing'], [])
        self.assertEqual(package['package_contract']['install_gate']['blocked_reasons'], [])
        self.assertEqual(package['package_contract']['promotion_gate']['blocked_reasons'], [])
        self.assertEqual(package['contract_schemas']['package'], 'skill-package-readiness.v1')
        self.assertEqual(package['contract_schemas']['profiles'], 'skill-operation-profiles.v1')
        self.assertEqual(package['operation_context']['primary_profile'], 'package-review')
        self.assertEqual(package['operation_context']['promotion_profile'], 'plugin-share')
        self.assertIn('metadata contract', package['operation_context']['profiles']['package-review']['required_evidence'])
        self.assertIn('./bin/ask skills package <handle-or-path> --json --robot', package['operation_context']['events']['package_readiness_checked']['producer_commands'])
        self.assertIn('./bin/ask skills events package_readiness_checked --json --robot', package['operation_context']['validation_commands'])
        self.assertEqual(package['lifecycle_events'][1]['details']['gate_summary'], package['gate_summary'])
        self.assertEqual(package['lifecycle_event'], package['lifecycle_events'][1])
        self.assertEqual(package['lifecycle_events'][1]['event_identity']['event_type'], 'package_readiness_checked')
        self.assertEqual(package['lifecycle_events'][1]['event_identity']['subject_key'], 'Plugins/skill-factory/skills/code_quality_review/skill-builder')
        self.assertEqual(package['lifecycle_events'][1]['contract_schemas']['lifecycle_event'], 'capability-lifecycle-event.v1')
        self.assertEqual(package['lifecycle_events'][1]['producer_command'], './bin/ask skills package <handle-or-path> --json --robot')
        self.assertEqual(package['lifecycle_events'][1]['observer_command'], './bin/ask skills events package_readiness_checked --json --robot')
        self.assertIn('package_readiness_checked', [event['event_type'] for event in package['lifecycle_events']])

    def test_skills_package_rejects_missing_target(self):
        """Verify ask skills package preserves the required target contract."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIn('the following arguments are required: target', output['errors'][0]['message'])

    def test_skills_package_rejects_extra_non_verify_target(self):
        """Verify ask skills package does not ignore unexpected positional input."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', 'extra', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIn('unexpected verify-only arguments', output['errors'][0]['message'])

    def test_skills_package_rejects_verify_flags_without_verify_mode(self):
        """Verify verify-only flags cannot silently alter package readiness."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--expected-sha256', '0' * 64, '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIn('unexpected verify-only arguments', output['errors'][0]['message'])

    def test_skills_package_verify_strict_enforces_target_readiness_with_compact_json(self):
        """Verify strict verification uses the requested target's readiness gate."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'verify', 'simplify', '--strict', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(len(result.stdout.encode('utf-8')), 10 * 1024)
        output = json.loads(result.stdout)
        verification = output['data']['skill_package_verification']
        self.assertTrue(verification['strict'])
        self.assertEqual(verification['status'], 'pass')
        self.assertEqual(verification['next_command'], './bin/ask skills prove simplify --json --robot')
        self.assertEqual(verification['strict_package_readiness']['missing_fields'], [])
        self.assertEqual(output['errors'], [])

    def test_skills_package_human_output(self):
        """Verify ask skills package has a useful non-JSON readiness render."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills package output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Skill package: Plugins/skill-factory/skills/code_quality_review/skill-builder', result.stdout)
        self.assertIn('Event: package_readiness_checked', result.stdout)
        self.assertIn('Readiness level: share_ready', result.stdout)
        self.assertIn('Compatible roles: default, worker, skill-inspector', result.stdout)
        self.assertIn('Runtime needs: 3 declared', result.stdout)
        self.assertIn('Provenance: frontmatter:Agent Skills Team:2026-05-15:canonical-source', result.stdout)
        self.assertIn('Install ready:', result.stdout)
        self.assertIn('Checkout test:', result.stdout)
        self.assertIn('Promotion:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills package <handle-or-path> --json --robot', result.stdout)
        self.assertIn('Next:', result.stdout)

    def test_skills_package_checkout_test_command_records_evidence(self):
        """Verify ask skills package --checkout-test records local install-gate evidence."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--checkout-test', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills package checkout output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        package = output['data']['skill_package']
        checkout = package['package_contract']['install_gate']['checkout_test']
        self.assertEqual(checkout['status'], 'pass')
        self.assertEqual(package['gate_summary']['checkout_test_status'], 'pass')
        self.assertEqual(package['gate_summary']['promotion_status'], 'ready')
        self.assertTrue(package['gate_summary']['promotion_ready'])
        self.assertIn('source_readable:true', checkout['evidence'])
        self.assertIn('package_metadata_complete:true', checkout['evidence'])

    def test_skills_package_strict_command_accepts_complete_metadata(self):
        """Verify ask skills package --strict accepts complete package metadata."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--strict', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills package strict output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        package = output['data']['skill_package']
        self.assertTrue(package['strict'])
        self.assertEqual(package['status'], 'pass')
        self.assertEqual(package['blockers'], [])
        self.assertEqual(package['package_contract']['required_fields']['missing'], [])
        self.assertEqual(package['package_contract']['install_gate']['blocked_reasons'], [])
        self.assertIn('package_readiness_checked', [event['event_type'] for event in package['lifecycle_events']])

    def test_skills_package_verify_strict_reaches_directory_verification(self):
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'package', 'verify', 'Infrastructure/tests/fixtures/skills_sdk/valid_skill', '--strict', '--json', '--robot']
        result = _run_cli(cmd)
        output = json.loads(result.stdout)
        self.assertIn('skill_package_verification', output['data'])
        self.assertTrue(output['data']['skill_package_verification']['strict'])

    def test_skills_doctor_command_exposes_lifecycle_and_readiness(self):
        """Verify ask skills doctor exposes lifecycle and readiness contracts."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'doctor', 'Skills/agent-ops/autofix', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills doctor failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        doctor = output['data']['skill_doctor']
        self.assertEqual(doctor['schema_version'], 'skill-doctor.v1')
        self.assertEqual(doctor['target_kind'], 'canonical_source_path')
        self.assertEqual(doctor['target_summary']['query'], 'Skills/agent-ops/autofix')
        self.assertEqual(doctor['target_summary']['canonical_source_path'], doctor['canonical_source_path'])
        self.assertIn('canonical_source', doctor['check_summary']['check_names'])
        self.assertEqual(doctor['check_summary']['check_count'], len(doctor['checks']))
        self.assertIn('missing', doctor['check_summary']['status_counts'])
        self.assertEqual(doctor['lifecycle_event']['schema_version'], 'capability-lifecycle-event.v1')
        self.assertEqual(doctor['lifecycle_event']['event_type'], 'skill_doctor_completed')
        self.assertEqual(doctor['lifecycle_event']['contract_schemas']['events'], 'skill-events.v1')
        self.assertEqual(doctor['lifecycle_event']['event_identity']['target_kind'], 'canonical_source_path')
        self.assertEqual(doctor['lifecycle_event']['event_identity']['subject_key'], 'Skills/agent-ops/autofix')
        self.assertEqual(doctor['lifecycle_event']['producer_command'], './bin/ask skills doctor <handle-or-path> --json --robot')
        self.assertEqual(doctor['lifecycle_event']['observer_command'], './bin/ask skills events skill_doctor_completed --json --robot')
        self.assertIn('blocked_user_input', doctor['readiness_taxonomy']['blockers'])
        self.assertEqual(doctor['contract_schemas']['doctor']['version'], 'skill-doctor.v1')
        self.assertEqual(doctor['contract_schemas']['doctor']['owner'], 'Agent Skills Kit')
        self.assertTrue(doctor['contract_schemas']['doctor'].get('path') or doctor['contract_schemas']['doctor'].get('missing_schema_reason'))
        self.assertEqual(doctor['contract_schemas']['events']['version'], 'skill-events.v1')
        self.assertEqual(doctor['contract_schema_versions']['doctor'], 'skill-doctor.v1')
        self.assertEqual(doctor['contract_schema_versions']['events'], 'skill-events.v1')
        self.assertEqual(doctor['operation_context']['primary_profile'], 'authoring')
        self.assertIn('package-review', doctor['operation_context']['next_profiles'])
        self.assertIn('skill audit', doctor['operation_context']['profiles']['authoring']['required_evidence'])
        self.assertIn('./bin/ask skills doctor <handle-or-path> --json --robot', doctor['operation_context']['events']['skill_doctor_completed']['producer_commands'])
        self.assertIn('./bin/ask skills events skill_doctor_completed --json --robot', doctor['operation_context']['validation_commands'])
        self.assertIn('eval_blocked', doctor['lifecycle_event_types'])
        self.assertIn('Packaging', doctor['sdk_layers'])
        projection_ownership = doctor['checks']['projection_ownership']
        self.assertEqual(projection_ownership['sdk_layer'], 'Runtime Adapters')
        self.assertEqual(projection_ownership['source']['classification'], 'canonical_project_source')
        self.assertTrue(projection_ownership['source']['editable_source'])
        self.assertFalse(projection_ownership['projection_editable'])
        self.assertEqual(projection_ownership['owner_manifest_schema'], 'Infrastructure/config/schemas/skills-sdk.project.v1.schema.json')
        self.assertEqual(doctor['checks']['package_readiness']['sdk_layer'], 'Packaging')
        package_readiness = doctor['checks']['capability_metadata']['package_readiness']
        self.assertIn('version', package_readiness['required_fields']['present'])
        self.assertFalse(package_readiness['promotion_gate']['share_ready'])
        package_contract = doctor['checks']['capability_metadata']['package_contract']
        self.assertEqual(package_contract['role_compatibility'], package_readiness['role_compatibility'])
        self.assertEqual(package_contract['runtime_contract'], package_readiness['runtime_contract'])
        self.assertEqual(package_contract['install_gate'], package_readiness['install_gate'])
        self.assertEqual(package_contract['promotion_gate'], package_readiness['promotion_gate'])

    def test_skills_doctor_blocks_generated_projection_path_as_source(self):
        """Verify doctor refuses to treat generated .agents skill projections as source."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'doctor', '.agents/skills/1password', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills doctor output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        doctor = output['data']['skill_doctor']
        self.assertEqual(doctor['checks']['projection_ownership']['status'], 'fail')
        self.assertEqual(doctor['checks']['projection_ownership']['source']['classification'], 'generated_runtime_projection')
        self.assertFalse(doctor['checks']['projection_ownership']['source']['editable_source'])
        self.assertIn('blocked_validation', [blocker['class'] for blocker in doctor['blockers']])

    def test_skills_doctor_blocks_runtime_symlink_target_path(self):
        """Verify path-mode doctor classifies the queried path before dereferencing symlinks."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            source = repo_root / 'Skills' / 'agent-ops' / 'autofix' / 'SKILL.md'
            source.parent.mkdir(parents=True)
            source.write_text('---\nname: autofix\ndescription: Fix a known issue\nversion: 0.1.0\n---\n# Autofix\n', encoding='utf-8')
            projection = repo_root / '.agents' / 'skills' / 'autofix'
            projection.parent.mkdir(parents=True)
            try:
                projection.symlink_to(source.parent)
            except OSError as exc:
                self.skipTest(f'symlinks unavailable: {exc}')
            with mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=['autofix proof']):
                result = skills_commands.skills_doctor(repo_root, '.agents/skills/autofix')
        doctor = result.data['skill_doctor']
        projection_ownership = doctor['checks']['projection_ownership']
        self.assertEqual(result.status, 'error')
        self.assertEqual(projection_ownership['status'], 'fail')
        self.assertEqual(projection_ownership['source']['classification'], 'generated_runtime_projection')
        self.assertEqual(projection_ownership['projection']['classification'], 'generated_runtime_projection')
        self.assertFalse(projection_ownership['projection_editable'])
        self.assertIn('blocked_validation', [blocker['class'] for blocker in doctor['blockers']])

__all__ = [name for name in globals() if not name.startswith("__")]
