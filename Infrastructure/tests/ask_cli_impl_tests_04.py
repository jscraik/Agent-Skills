from ask_cli_impl_tests_03 import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_skill_root_ownership_classifies_generated_roots_case_insensitively(self):
        """Verify generated-root guards survive mixed-case paths on case-insensitive filesystems."""
        from ask.commands import skills_impl as skills_commands
        agents_ownership = skills_commands._skill_root_ownership_for_path('.Agents/skills/1password')
        codex_ownership = skills_commands._skill_root_ownership_for_path('.CoDeX/skills/1password')
        self.assertEqual(agents_ownership['classification'], 'generated_runtime_projection')
        self.assertFalse(agents_ownership['editable_source'])
        self.assertTrue(agents_ownership['owner_manifest_required_for_edit'])
        self.assertEqual(codex_ownership['classification'], 'client_runtime_config')
        self.assertFalse(codex_ownership['editable_source'])
        self.assertTrue(codex_ownership['owner_manifest_required_for_edit'])

    def test_skills_doctor_allows_manifest_declared_project_skill_source(self):
        """Verify owner repo manifests can declare .agents/skills as canonical project source."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / '.agents' / 'skills' / 'local-demo' / 'SKILL.md'
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text('---\nname: local-demo\ndescription: Local owner skill\nversion: 0.1.0\n---\n# Local Demo\n', encoding='utf-8')
            (repo_root / 'skills-sdk.json').write_text(json.dumps({'schema_version': 'skills-sdk.project.v1', 'project_id': 'owner-repo', 'skill_roots': [{'path': '.agents/skills', 'classification': 'canonical_project_source', 'default_for_create': True, 'default_for_install': True, 'default_for_update': True}], 'eval_suite': {'path': '.harness/evals/skills'}, 'evidence': {'output_path': '.harness/session-evidence/skills'}, 'trust_policy': 'local_owner', 'precedence_policy': 'project_over_user_after_trust'}), encoding='utf-8')
            with mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=['local-demo proof']):
                result = skills_commands.skills_doctor(repo_root, '.agents/skills/local-demo')
        doctor = result.data['skill_doctor']
        source = doctor['checks']['projection_ownership']['source']
        self.assertNotEqual(result.status, 'error')
        self.assertEqual(doctor['checks']['projection_ownership']['status'], 'pass')
        self.assertEqual(source['classification'], 'canonical_project_source')
        self.assertTrue(source['editable_source'])
        self.assertTrue(source['manifest_declared'])
        self.assertEqual(source['owner_manifest_path'], 'skills-sdk.json')
        self.assertNotIn('blocked_validation', [blocker['class'] for blocker in doctor['blockers']])

    def test_skill_root_ownership_prefers_most_specific_manifest_root(self):
        """Verify nested generated roots are not masked by broader manifest roots."""
        from ask.commands import skills_impl as skills_commands
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / 'skills-sdk.json').write_text(json.dumps({'schema_version': 'skills-sdk.project.v1', 'project_id': 'owner-repo', 'skill_roots': [{'path': '.agents/skills', 'classification': 'canonical_project_source', 'default_for_create': True, 'default_for_install': True, 'default_for_update': True}, {'path': '.agents/skills/generated', 'classification': 'generated_runtime_projection', 'default_for_create': False, 'default_for_install': False, 'default_for_update': False}], 'eval_suite': {'path': '.harness/evals/skills'}, 'evidence': {'output_path': '.harness/session-evidence/skills'}, 'trust_policy': 'local_owner', 'precedence_policy': 'project_over_user_after_trust'}), encoding='utf-8')
            ownership = skills_commands._skill_root_ownership_for_path('.agents/skills/generated/demo', repo_root=repo_root)
        self.assertEqual(ownership['root'], '.agents/skills/generated')
        self.assertEqual(ownership['classification'], 'generated_runtime_projection')
        self.assertFalse(ownership['editable_source'])
        self.assertTrue(ownership['owner_manifest_required_for_edit'])

    def test_skills_doctor_rejects_duplicate_manifest_root_paths(self):
        """Verify duplicate manifest paths cannot grant canonical edit authority."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / '.agents' / 'skills' / 'local-demo' / 'SKILL.md'
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text('---\nname: local-demo\ndescription: Local owner skill\nversion: 0.1.0\n---\n# Local Demo\n', encoding='utf-8')
            (repo_root / 'skills-sdk.json').write_text(json.dumps({'schema_version': 'skills-sdk.project.v1', 'project_id': 'owner-repo', 'skill_roots': [{'path': '.agents/skills', 'classification': 'canonical_project_source', 'default_for_create': True, 'default_for_install': True, 'default_for_update': True}, {'path': '/.agents/skills/', 'classification': 'canonical_project_source', 'default_for_create': False, 'default_for_install': False, 'default_for_update': False}], 'eval_suite': {'path': '.harness/evals/skills'}, 'evidence': {'output_path': '.harness/session-evidence/skills'}, 'trust_policy': 'local_owner', 'precedence_policy': 'project_over_user_after_trust'}), encoding='utf-8')
            with mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=['local-demo proof']):
                result = skills_commands.skills_doctor(repo_root, '.agents/skills/local-demo')
        doctor = result.data['skill_doctor']
        source = doctor['checks']['projection_ownership']['source']
        self.assertEqual(result.status, 'error')
        self.assertEqual(source['classification'], 'generated_runtime_projection')
        self.assertFalse(source['manifest_declared'])
        self.assertIn('blocked_validation', [blocker['class'] for blocker in doctor['blockers']])

    def test_skills_doctor_exposes_valid_manifest_state(self):
        """Verify doctor projection_ownership surfaces a valid owner-manifest state."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / '.agents' / 'skills' / 'local-demo' / 'SKILL.md'
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text('---\nname: local-demo\ndescription: Local owner skill\nversion: 0.1.0\n---\n# Local Demo\n', encoding='utf-8')
            (repo_root / 'skills-sdk.json').write_text(json.dumps({'schema_version': 'skills-sdk.project.v1', 'project_id': 'owner-repo', 'skill_roots': [{'path': '.agents/skills', 'classification': 'canonical_project_source', 'default_for_create': True, 'default_for_install': True, 'default_for_update': True}], 'eval_suite': {'path': '.harness/evals/skills'}, 'evidence': {'output_path': '.harness/session-evidence/skills'}, 'trust_policy': 'local_owner', 'precedence_policy': 'project_over_user_after_trust'}), encoding='utf-8')
            with mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=['local-demo proof']):
                result = skills_commands.skills_doctor(repo_root, '.agents/skills/local-demo')
        doctor = result.data['skill_doctor']
        manifest_state = doctor['checks']['projection_ownership']['owner_manifest_state']
        self.assertEqual(manifest_state['state'], 'valid')
        self.assertFalse(manifest_state['legacy_compat'])
        self.assertEqual(manifest_state['blockers'], [])

    def test_skills_doctor_blocks_invalid_manifest_and_exposes_state(self):
        """Verify an invalid owner manifest is blocked, not silently treated as absent."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / '.agents' / 'skills' / 'local-demo' / 'SKILL.md'
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text('---\nname: local-demo\ndescription: Local owner skill\nversion: 0.1.0\n---\n# Local Demo\n', encoding='utf-8')
            (repo_root / 'skills-sdk.json').write_text(json.dumps({'schema_version': 'skills-sdk.project.v2', 'project_id': 'owner-repo', 'skill_roots': [{'path': '.agents/skills', 'classification': 'canonical_project_source'}]}), encoding='utf-8')
            with mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=['local-demo proof']):
                result = skills_commands.skills_doctor(repo_root, '.agents/skills/local-demo')
        doctor = result.data['skill_doctor']
        manifest_state = doctor['checks']['projection_ownership']['owner_manifest_state']
        self.assertEqual(result.status, 'error')
        self.assertEqual(manifest_state['state'], 'invalid')
        self.assertIn('manifest_schema_version_unsupported', [blocker['class'] for blocker in manifest_state['blockers']])
        self.assertIn('blocked_validation', [blocker['class'] for blocker in doctor['blockers']])

    def test_skills_doctor_human_output_exposes_lifecycle_event(self):
        """Verify ask skills doctor exposes the primary lifecycle event in human output."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'doctor', 'Plugins/skill-factory/skills/code_quality_review/skill-builder', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills doctor output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Skill doctor: Plugins/skill-factory/skills/code_quality_review/skill-builder', result.stdout)
        self.assertIn('Event: skill_doctor_completed', result.stdout)
        self.assertNotIn('Warning classes:', result.stdout)
        self.assertIn('Checks: available_not_run=1, pass=6, skipped=1', result.stdout)
        self.assertIn('Validation: ./bin/ask skills doctor <handle-or-path> --json --robot', result.stdout)
        self.assertIn('Next:', result.stdout)

    def test_skills_profiles_command_returns_selected_profile(self):
        """Verify ask skills profiles exposes one operation-mode contract."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'profiles', 'eval', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills profiles failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        profiles = output['data']['skill_profiles']
        self.assertEqual(profiles['schema_version'], 'skill-operation-profiles.v1')
        self.assertEqual(profiles['selected_profile'], 'eval')
        self.assertEqual(profiles['profile_names'], ['eval'])
        self.assertIn('package-review', profiles['available_profiles'])
        self.assertEqual(profiles['profile_summary']['profile_count'], 1)
        self.assertEqual(profiles['profile_summary']['profile_names'], ['eval'])
        self.assertTrue(profiles['profile_summary']['has_profiles'])
        _assert_readiness_overview_ready(self, profiles['readiness_overview'], ['lifecycle_event_coverage', 'profile_contracts'])
        self.assertEqual(profiles['readiness_overview']['contract_sections'], {'lifecycle_event_coverage': {'gap_count': 0, 'ready': True, 'status': 'ready'}, 'profile_contracts': {'gap_count': 0, 'ready': True, 'status': 'ready'}})
        self.assertEqual(profiles['profile_summary']['contract_dimensions'], ['allowed_roots', 'permissions', 'required_evidence', 'stop_conditions', 'write_policy'])
        self.assertEqual(profiles['profile_summary']['contract_dimension_count'], 5)
        self.assertEqual(profiles['profile_summary']['contract_dimension_status'], {'allowed_roots': 'ready', 'permissions': 'ready', 'required_evidence': 'ready', 'stop_conditions': 'ready', 'write_policy': 'ready'})
        self.assertEqual(profiles['profile_summary']['missing_profiles_by_contract_dimension'], {'allowed_roots': [], 'permissions': [], 'required_evidence': [], 'stop_conditions': [], 'write_policy': []})
        self.assertEqual(profiles['profile_summary']['missing_profile_count_by_contract_dimension'], {'allowed_roots': 0, 'permissions': 0, 'required_evidence': 0, 'stop_conditions': 0, 'write_policy': 0})
        self.assertEqual(profiles['profile_summary']['required_evidence_count'], len(profiles['profiles']['eval']['required_evidence']))
        self.assertEqual(profiles['profile_summary']['required_evidence_by_profile']['eval'], sorted(profiles['profiles']['eval']['required_evidence']))
        self.assertEqual(profiles['profile_summary']['required_evidence_count_by_profile']['eval'], len(profiles['profiles']['eval']['required_evidence']))
        self.assertTrue(profiles['profile_summary']['has_required_evidence'])
        self.assertTrue(profiles['profile_summary']['has_stop_conditions'])
        self.assertEqual(profiles['profile_summary']['stop_conditions_by_profile']['eval'], sorted(profiles['profiles']['eval']['stop_conditions']))
        self.assertEqual(profiles['profile_summary']['stop_condition_count_by_profile']['eval'], len(profiles['profiles']['eval']['stop_conditions']))
        self.assertEqual(profiles['profile_summary']['profiles_missing_allowed_roots'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_allowed_root_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_allowed_roots'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_allowed_roots'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_permissions'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_permission_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_permissions'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_permissions'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_required_evidence'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_required_evidence_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_required_evidence'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_required_evidence'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_stop_conditions'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_stop_condition_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_stop_conditions'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_stop_conditions'])
        self.assertEqual(profiles['profile_summary']['profiles_without_taxonomy_stop_conditions'], [])
        self.assertEqual(profiles['profile_summary']['profiles_with_taxonomy_stop_conditions'], ['eval'])
        self.assertEqual(profiles['profile_summary']['profiles_with_taxonomy_stop_condition_count'], 1)
        self.assertEqual(profiles['profile_summary']['profiles_without_taxonomy_stop_condition_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_without_taxonomy_stop_conditions'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_taxonomy_stop_conditions'])
        self.assertTrue(profiles['profile_summary']['has_taxonomy_stop_conditions'])
        self.assertIn('blocked_runtime', profiles['profile_summary']['taxonomy_stop_conditions_by_profile']['eval'])
        self.assertIn('timeout_no_output', profiles['profile_summary']['taxonomy_stop_conditions_by_profile']['eval'])
        self.assertEqual(profiles['profile_summary']['taxonomy_stop_condition_count'], len(profiles['profile_summary']['taxonomy_stop_conditions_by_profile']['eval']))
        self.assertEqual(profiles['profile_summary']['profiles_missing_write_policy'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_write_policy_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_write_policy'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_write_policy'])
        self.assertEqual(profiles['profile_summary']['profiles_with_contract_gaps'], [])
        _assert_contract_ready(self, profiles['profile_summary'])
        self.assertIn('artifact_write_only', profiles['profile_summary']['by_write_policy'])
        self.assertEqual(profiles['profile_summary']['write_policy_count'], 1)
        self.assertEqual(profiles['profile_summary']['write_policy_by_profile']['eval'], profiles['profiles']['eval']['write_policy'])
        self.assertIn('repo_read', profiles['profile_summary']['by_permission'])
        self.assertEqual(profiles['profile_summary']['permission_count'], len(profiles['profile_summary']['by_permission']))
        self.assertEqual(profiles['profile_summary']['permissions_by_profile']['eval'], sorted(profiles['profiles']['eval']['permissions']))
        self.assertEqual(profiles['profile_summary']['permission_count_by_profile']['eval'], len(profiles['profiles']['eval']['permissions']))
        self.assertEqual(profiles['profile_summary']['allowed_roots_by_profile']['eval'], sorted(profiles['profiles']['eval']['allowed_roots']))
        self.assertEqual(profiles['profile_summary']['allowed_root_count_by_profile']['eval'], len(profiles['profiles']['eval']['allowed_roots']))
        self.assertEqual(list(profiles['profiles']), ['eval'])
        eval_contract = profiles['profiles']['eval']['eval_profile_contract']
        self.assertEqual(eval_contract['codex_profile'], 'fast')
        self.assertEqual(eval_contract['codex_profile_config'], '[profiles.fast]')
        self.assertEqual(eval_contract['tessl_project_marker'], 'tessl.json')
        self.assertIn(os.path.join(tempfile.gettempdir(), 'ask-tessl-evals'), eval_contract['tessl_eval_staging_root'])
        self.assertEqual(profiles['operation_context']['profile_model'], 'profile-v2-inspired')
        self.assertEqual(profiles['operation_context']['contract_schemas']['doctor'], 'skill-doctor.v1')
        self.assertEqual(profiles['operation_context']['contract_schemas']['memory'], 'skill-memory-provider.v1')
        self.assertIn('eval', profiles['operation_context']['routing_contracts']['events'])
        self.assertEqual(profiles['event_coverage']['profile_count'], 1)
        self.assertEqual(profiles['event_coverage']['profile_names'], ['eval'])
        self.assertIn('eval_blocked', profiles['event_coverage']['events_by_profile']['eval'])
        self.assertIn('eval_completed', profiles['event_coverage']['events_by_profile']['eval'])
        self.assertEqual(profiles['event_coverage']['event_count_by_profile']['eval'], len(profiles['event_coverage']['events_by_profile']['eval']))
        self.assertEqual(profiles['event_coverage']['event_reference_count'], profiles['event_coverage']['event_count_by_profile']['eval'])
        self.assertEqual(profiles['event_coverage']['profiles_with_events'], ['eval'])
        self.assertEqual(profiles['event_coverage']['profiles_with_event_count'], 1)
        self.assertEqual(profiles['event_coverage']['profiles_missing_events'], [])
        self.assertEqual(profiles['event_coverage']['profiles_missing_event_count'], 0)
        self.assertFalse(profiles['event_coverage']['has_profiles_missing_events'])
        self.assertTrue(profiles['event_coverage']['all_profiles_have_events'])
        self.assertEqual(profiles['event_coverage']['profiles_with_event_gaps'], [])
        self.assertEqual(profiles['event_coverage']['profiles_with_event_gap_count'], 0)
        _assert_contract_ready(self, profiles['event_coverage'])
        self.assertEqual(profiles['operation_context']['consumer_commands']['events'], './bin/ask skills events --json --robot')
        self.assertIn('Skills', profiles['workspace_roots']['canonical_skill_roots'])
        self.assertIn('.agents/skills', profiles['workspace_roots']['runtime_projection_roots'])
        self.assertIn('blocked_runtime', profiles['eval_blocker_classes'])
        self.assertEqual(profiles['blocker_taxonomy']['blocked_runtime'], profiles['eval_blocker_classes']['blocked_runtime'])
        self.assertIn('strict_audit_not_run', profiles['warning_taxonomy'])
        self.assertIn('blocked_runtime', profiles['profiles']['eval']['stop_conditions'])
        self.assertIn('timeout_no_output', profiles['profiles']['eval']['stop_conditions'])
        self.assertIn('blocked_runtime', profiles['profiles']['eval']['stop_condition_definitions'])
        self.assertIn('timeout_no_output', profiles['profiles']['eval']['stop_condition_definitions'])
        self.assertIn('blocked_user_input', profiles['profiles']['eval']['eval_blocker_classes'])
        self.assertEqual(profiles['profiles']['eval']['effective_roots'], ['Skills/**', 'Infrastructure/workouts/**', 'Infrastructure/artifacts/**'])

    def test_skills_profiles_command_returns_aggregate_contract_readiness(self):
        """Verify ask skills profiles summarizes all operation-mode contracts."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'profiles', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills profiles failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        profiles = output['data']['skill_profiles']
        self.assertEqual(profiles['selected_profile'], None)
        _assert_readiness_overview_ready(self, profiles['readiness_overview'], ['lifecycle_event_coverage', 'profile_contracts'])
        self.assertEqual(profiles['readiness_overview']['contract_sections']['profile_contracts']['status'], profiles['profile_summary']['contract_status'])
        self.assertEqual(profiles['readiness_overview']['contract_sections']['lifecycle_event_coverage']['status'], profiles['event_coverage']['contract_status'])
        self.assertEqual(profiles['profile_summary']['profile_count'], len(profiles['profiles']))
        self.assertEqual(profiles['profile_summary']['profile_names'], sorted(profiles['profiles']))
        self.assertEqual(profiles['profile_summary']['contract_dimensions'], ['allowed_roots', 'permissions', 'required_evidence', 'stop_conditions', 'write_policy'])
        self.assertEqual(profiles['profile_summary']['contract_dimension_count'], 5)
        self.assertEqual(set(profiles['profile_summary']['contract_dimension_status']), set(profiles['profile_summary']['contract_dimensions']))
        self.assertTrue(all((status == 'ready' for status in profiles['profile_summary']['contract_dimension_status'].values())))
        self.assertTrue(all((count == 0 for count in profiles['profile_summary']['missing_profile_count_by_contract_dimension'].values())))
        self.assertEqual(set(profiles['profile_summary']['missing_profiles_by_contract_dimension']), set(profiles['profile_summary']['contract_dimensions']))
        self.assertEqual(profiles['profile_summary']['profiles_with_contract_gaps'], [])
        _assert_contract_ready(self, profiles['profile_summary'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_allowed_roots'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_allowed_root_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_allowed_roots'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_allowed_roots'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_permissions'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_permission_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_permissions'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_permissions'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_required_evidence'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_required_evidence_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_required_evidence'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_required_evidence'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_stop_conditions'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_stop_condition_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_stop_conditions'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_stop_conditions'])
        self.assertEqual(profiles['profile_summary']['profiles_missing_write_policy'], [])
        self.assertEqual(profiles['profile_summary']['profiles_missing_write_policy_count'], 0)
        self.assertFalse(profiles['profile_summary']['has_profiles_missing_write_policy'])
        self.assertTrue(profiles['profile_summary']['all_profiles_have_write_policy'])
        self.assertEqual(profiles['profile_summary']['required_evidence_count'], sum(profiles['profile_summary']['required_evidence_count_by_profile'].values()))
        self.assertEqual(sorted(profiles['profile_summary']['write_policy_by_profile']), sorted(profiles['profiles']))
        self.assertEqual(profiles['profile_summary']['write_policy_by_profile']['live-mutation'], 'explicit_request_required')
        self.assertEqual(sorted(profiles['profile_summary']['stop_conditions_by_profile']), sorted(profiles['profiles']))
        self.assertEqual(sum(profiles['profile_summary']['stop_condition_count_by_profile'].values()), profiles['profile_summary']['stop_condition_count'])
        self.assertIn('unrelated dirty worktree', profiles['profile_summary']['stop_conditions_by_profile']['live-mutation'])
        self.assertEqual(sorted(profiles['profile_summary']['required_evidence_by_profile']), sorted(profiles['profiles']))
        self.assertIn('post-mutation validation', profiles['profile_summary']['required_evidence_by_profile']['live-mutation'])
        self.assertTrue(profiles['profile_summary']['has_taxonomy_stop_conditions'])
        self.assertIn('eval', profiles['profile_summary']['profiles_with_taxonomy_stop_conditions'])
        self.assertIn('package-review', profiles['profile_summary']['profiles_with_taxonomy_stop_conditions'])
        self.assertIn('authoring', profiles['profile_summary']['profiles_without_taxonomy_stop_conditions'])
        self.assertEqual(profiles['profile_summary']['profiles_with_taxonomy_stop_condition_count'], len(profiles['profile_summary']['profiles_with_taxonomy_stop_conditions']))
        self.assertEqual(profiles['profile_summary']['profiles_without_taxonomy_stop_condition_count'], len(profiles['profile_summary']['profiles_without_taxonomy_stop_conditions']))
        self.assertTrue(profiles['profile_summary']['has_profiles_without_taxonomy_stop_conditions'])
        self.assertFalse(profiles['profile_summary']['all_profiles_have_taxonomy_stop_conditions'])
        self.assertIn('blocked_user_input', profiles['profile_summary']['taxonomy_stop_conditions_by_profile']['eval'])
        self.assertIn('live-mutation', profiles['profile_names'])
        self.assertIn('external_write_after_confirmation', profiles['profile_summary']['by_permission'])
        self.assertEqual(sorted(profiles['profile_summary']['permissions_by_profile']), sorted(profiles['profiles']))
        self.assertEqual(sum(profiles['profile_summary']['permission_count_by_profile'].values()), sum((len(profile['permissions']) for profile in profiles['profiles'].values())))
        self.assertIn('external_write_after_confirmation', profiles['profile_summary']['permissions_by_profile']['live-mutation'])
        self.assertEqual(sorted(profiles['profile_summary']['allowed_roots_by_profile']), sorted(profiles['profiles']))
        self.assertEqual(sum(profiles['profile_summary']['allowed_root_count_by_profile'].values()), profiles['profile_summary']['allowed_root_count'])
        self.assertIn('Infrastructure/artifacts/skill-reviews/**', profiles['profile_summary']['allowed_roots_by_profile']['package-review'])
        self.assertEqual(sorted(profiles['event_coverage']['events_by_profile']), sorted(profiles['profiles']))
        self.assertEqual(profiles['event_coverage']['profile_count'], len(profiles['profiles']))
        self.assertEqual(profiles['event_coverage']['profile_names'], sorted(profiles['profiles']))
        self.assertFalse(profiles['event_coverage']['has_profiles_missing_events'])
        self.assertEqual(profiles['event_coverage']['profiles_missing_events'], [])
        self.assertEqual(profiles['event_coverage']['profiles_missing_event_count'], 0)
        self.assertTrue(profiles['event_coverage']['all_profiles_have_events'])
        self.assertEqual(profiles['event_coverage']['event_reference_count'], sum(profiles['event_coverage']['event_count_by_profile'].values()))
        self.assertEqual(profiles['event_coverage']['profiles_with_events'], sorted(profiles['profiles']))
        self.assertEqual(profiles['event_coverage']['profiles_with_event_count'], len(profiles['profiles']))
        self.assertGreaterEqual(profiles['event_coverage']['event_count_by_profile']['authoring'], 1)
        self.assertIn('projection_synced', profiles['event_coverage']['events_by_profile']['live-mutation'])
        self.assertEqual(profiles['event_coverage']['profiles_with_event_gaps'], [])
        self.assertEqual(profiles['event_coverage']['profiles_with_event_gap_count'], 0)
        _assert_contract_ready(self, profiles['event_coverage'])

    def test_skills_profiles_human_output(self):
        """Verify ask skills profiles has a useful non-JSON selected-profile render."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'profiles', 'package-review', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills profiles output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Skill profiles: pass', result.stdout)
        self.assertIn('Readiness: ready (0 gaps)', result.stdout)
        self.assertIn('Ready sections: lifecycle_event_coverage, profile_contracts', result.stdout)
        self.assertIn('Validation: ./bin/ask skills list --json --robot', result.stdout)
        self.assertIn('Profile: package-review', result.stdout)
        self.assertIn('Intent: Check a skill or plugin package before promotion.', result.stdout)
        self.assertIn('Write policy: reports_only_unless_fix_requested', result.stdout)

    def test_skills_profiles_command_blocks_unknown_profile(self):
        """Verify ask skills profiles fails closed for unknown operation modes."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'profiles', 'unsafe-live-linear', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills profiles output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        profiles = output['data']['skill_profiles']
        self.assertEqual(profiles['status'], 'blocked')
        self.assertEqual(profiles['requested_profile'], 'unsafe-live-linear')
        self.assertIn('live-mutation', profiles['available_profiles'])

    def test_skills_events_command_returns_lifecycle_contract(self):
        """Verify ask skills events exposes the lifecycle event contract."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'events', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills events failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        events = output['data']['skill_events']
        self.assertEqual(events['schema_version'], 'skill-events.v1')
        self.assertEqual(events['event_schema'], 'capability-lifecycle-event.v1')
        self.assertEqual(events['contract_schemas']['profiles'], 'skill-operation-profiles.v1')
        self.assertEqual(events['contract_schemas']['package'], 'skill-package-readiness.v1')
        self.assertGreaterEqual(events['event_count'], 8)
        self.assertIn('eval_blocked', events['event_names'])
        self.assertIn('skill_loaded', events['available_event_types'])
        _assert_readiness_overview_ready(self, events['readiness_overview'], ['lifecycle_event_contract'])
        self.assertEqual(events['readiness_overview']['contract_sections'], {'lifecycle_event_contract': {'gap_count': 0, 'ready': True, 'status': 'ready'}})
        self.assertEqual(events['event_summary']['event_count'], events['event_count'])
        self.assertEqual(events['event_summary']['contract_dimensions'], ['known_profiles', 'observer_commands', 'producer_commands', 'profiles'])
        self.assertEqual(events['event_summary']['contract_dimension_count'], 4)
        self.assertEqual(events['event_summary']['contract_dimension_status'], {'known_profiles': 'ready', 'observer_commands': 'ready', 'producer_commands': 'ready', 'profiles': 'ready'})
        self.assertEqual(events['event_summary']['missing_events_by_contract_dimension'], {'known_profiles': [], 'observer_commands': [], 'producer_commands': [], 'profiles': []})
        self.assertEqual(events['event_summary']['missing_event_count_by_contract_dimension'], {'known_profiles': 0, 'observer_commands': 0, 'producer_commands': 0, 'profiles': 0})
        self.assertGreaterEqual(events['event_summary']['producer_command_count'], events['event_count'])
        self.assertGreaterEqual(events['event_summary']['observer_command_count'], events['event_count'])
        self.assertEqual(sorted(events['event_summary']['producer_command_count_by_event']), sorted(events['event_consumers']))
        self.assertEqual(events['event_summary']['producer_command_count_by_event']['eval_completed'], len(events['event_consumers']['eval_completed']['producer_commands']))
        self.assertEqual(events['event_summary']['observer_command_count_by_event']['projection_synced'], len(events['event_consumers']['projection_synced']['observer_commands']))
        self.assertGreaterEqual(events['event_summary']['by_profile']['eval'], 1)
        self.assertIn('eval_blocked', events['event_summary']['events_by_profile']['eval'])
        self.assertIn('projection_synced', events['event_summary']['events_by_profile']['live-mutation'])
        self.assertEqual(events['event_summary']['event_count_by_profile']['eval'], len(events['event_summary']['events_by_profile']['eval']))
        self.assertEqual(events['event_summary']['profiles_by_event']['eval_blocked'], events['event_consumers']['eval_blocked']['profiles'])
        self.assertEqual(events['event_summary']['profile_count_by_event']['manifest_changed'], len(events['event_consumers']['manifest_changed']['profiles']))
        self.assertEqual(events['event_summary']['profile_count'], len(events['event_summary']['by_profile']))
        self.assertEqual(events['event_summary']['profile_names'], sorted(events['event_summary']['by_profile']))
        self.assertIn('eval', events['event_summary']['profile_names'])
        self.assertTrue(events['event_summary']['has_profiles'])
        self.assertFalse(events['event_summary']['has_missing_producers'])
        self.assertFalse(events['event_summary']['has_missing_observers'])
        self.assertFalse(events['event_summary']['has_missing_profiles'])
        self.assertFalse(events['event_summary']['has_unknown_profiles'])
        self.assertEqual(events['event_summary']['events_missing_producers'], [])
        self.assertEqual(events['event_summary']['events_missing_observers'], [])
        self.assertEqual(events['event_summary']['events_missing_profiles'], [])
        self.assertEqual(events['event_summary']['events_missing_profile_count'], 0)
        self.assertEqual(events['event_summary']['events_with_unknown_profile_count'], 0)
        self.assertEqual(events['event_summary']['unknown_profile_reference_count'], 0)
        self.assertEqual(events['event_summary']['events_with_unknown_profiles'], {})
        self.assertEqual(events['event_summary']['profiles_unknown_to_registry'], [])
        self.assertEqual(events['event_summary']['known_profile_count'], len(events['event_summary']['known_profile_names']))
        self.assertEqual(events['event_summary']['referenced_profile_count'], len(events['event_summary']['referenced_profile_names']))
        self.assertEqual(sorted(events['event_summary']['known_events_by_profile']), events['event_summary']['known_profile_names'])
        self.assertEqual(events['event_summary']['known_event_count_by_profile']['eval'], len(events['event_summary']['known_events_by_profile']['eval']))
        self.assertEqual(events['event_summary']['known_profiles_with_events'], events['event_summary']['known_profile_names'])
        self.assertEqual(events['event_summary']['known_profile_event_coverage_count'], events['event_summary']['known_profile_count'])
        self.assertTrue(events['event_summary']['all_known_profiles_have_events'])
        self.assertEqual(events['event_summary']['known_profiles_without_events'], [])
        self.assertFalse(events['event_summary']['has_known_profiles_without_events'])
        self.assertIn('live-mutation', events['event_summary']['known_profile_names'])
        self.assertIn('live-mutation', events['event_summary']['referenced_profile_names'])
        self.assertEqual(events['event_summary']['events_with_contract_gaps'], [])
        _assert_contract_ready(self, events['event_summary'])
        self.assertIn('./bin/ask skills events --json --robot', events['validation_commands'])
        self.assertIn('eval_blocked', events['event_types'])
        self.assertIn('eval', events['event_consumers']['eval_blocked']['profiles'])
        self.assertIn('./bin/ask skills prove <handle> --json --robot', events['event_consumers']['eval_completed']['producer_commands'])
        self.assertEqual(events['event_consumers']['projection_synced']['producer_commands'], ['./bin/ask skills sync --json --robot'])
        self.assertEqual(events['event_consumers']['manifest_changed']['producer_commands'], ['./bin/ask skills sync --scope workspace --projection flat --json --robot'])
        self.assertEqual(events['event_consumers']['projection_synced']['observer_commands'], ['./bin/ask skills list --json --robot'])
        self.assertIn('blocked_user_input', events['eval_blocker_classes'])
        self.assertIn('blocked_runtime', events['eval_blocker_classes'])
        self.assertIn('timeout_partial_output', events['eval_blocker_classes'])
        self.assertEqual(events['blocker_taxonomy']['blocked_auth'], events['eval_blocker_classes']['blocked_auth'])
        self.assertIn('strict_audit_not_run', events['warning_taxonomy'])
        self.assertIn('skill_doctor_completed', events['event_order'])
        self.assertEqual(events['selected_event_type'], None)

    def test_skills_events_command_returns_selected_event(self):
        """Verify ask skills events can narrow to a single event type."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'events', 'eval_blocked', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills events failed: {result.stderr}')
        output = json.loads(result.stdout)
        events = output['data']['skill_events']
        self.assertEqual(events['selected_event_type'], 'eval_blocked')
        self.assertEqual(events['event_names'], ['eval_blocked'])
        self.assertIn('eval_completed', events['available_event_types'])
        _assert_readiness_overview_ready(self, events['readiness_overview'], ['lifecycle_event_contract'])
        self.assertEqual(events['readiness_overview']['contract_sections']['lifecycle_event_contract']['status'], events['event_summary']['contract_status'])
        self.assertEqual(events['event_summary']['event_count'], 1)
        self.assertEqual(events['event_summary']['contract_dimensions'], ['known_profiles', 'observer_commands', 'producer_commands', 'profiles'])
        self.assertEqual(events['event_summary']['contract_dimension_count'], 4)
        self.assertEqual(events['event_summary']['contract_dimension_status'], {'known_profiles': 'ready', 'observer_commands': 'ready', 'producer_commands': 'ready', 'profiles': 'ready'})
        self.assertEqual(events['event_summary']['missing_events_by_contract_dimension'], {'known_profiles': [], 'observer_commands': [], 'producer_commands': [], 'profiles': []})
        self.assertEqual(events['event_summary']['missing_event_count_by_contract_dimension'], {'known_profiles': 0, 'observer_commands': 0, 'producer_commands': 0, 'profiles': 0})
        self.assertEqual(events['event_summary']['producer_command_count'], 1)
        self.assertEqual(events['event_summary']['observer_command_count'], 1)
        self.assertEqual(events['event_summary']['producer_command_count_by_event'], {'eval_blocked': 1})
        self.assertEqual(events['event_summary']['observer_command_count_by_event'], {'eval_blocked': 1})
        self.assertEqual(events['event_summary']['profile_names'], ['eval'])
        self.assertEqual(events['event_summary']['profile_count'], 1)
        self.assertEqual(events['event_summary']['events_by_profile'], {'eval': ['eval_blocked']})
        self.assertEqual(events['event_summary']['event_count_by_profile'], {'eval': 1})
        self.assertEqual(events['event_summary']['profiles_by_event'], {'eval_blocked': ['eval']})
        self.assertEqual(events['event_summary']['profile_count_by_event'], {'eval_blocked': 1})
        self.assertFalse(events['event_summary']['has_missing_producers'])
        self.assertFalse(events['event_summary']['has_missing_observers'])
        self.assertFalse(events['event_summary']['has_missing_profiles'])
        self.assertFalse(events['event_summary']['has_unknown_profiles'])
        self.assertEqual(events['event_summary']['events_missing_profile_count'], 0)
        self.assertEqual(events['event_summary']['events_with_unknown_profile_count'], 0)
        self.assertEqual(events['event_summary']['unknown_profile_reference_count'], 0)
        self.assertEqual(events['event_summary']['events_with_unknown_profiles'], {})
        self.assertEqual(events['event_summary']['profiles_unknown_to_registry'], [])
        self.assertEqual(events['event_summary']['known_profile_count'], 5)
        self.assertIn('live-mutation', events['event_summary']['known_profile_names'])
        self.assertEqual(events['event_summary']['known_events_by_profile']['eval'], ['eval_blocked'])
        self.assertEqual(events['event_summary']['known_events_by_profile']['live-mutation'], [])
        self.assertEqual(events['event_summary']['known_event_count_by_profile']['live-mutation'], 0)
        self.assertEqual(events['event_summary']['known_profiles_with_events'], ['eval'])
        self.assertEqual(events['event_summary']['known_profile_event_coverage_count'], 1)
        self.assertFalse(events['event_summary']['all_known_profiles_have_events'])
        self.assertEqual(events['event_summary']['referenced_profile_names'], ['eval'])
        self.assertIn('live-mutation', events['event_summary']['known_profiles_without_events'])
        self.assertTrue(events['event_summary']['has_known_profiles_without_events'])
        self.assertEqual(events['event_summary']['events_with_contract_gaps'], [])
        _assert_contract_ready(self, events['event_summary'])
        self.assertEqual(list(events['event_types']), ['eval_blocked'])
        self.assertEqual(list(events['event_consumers']), ['eval_blocked'])
        self.assertEqual(events['contract_schemas']['events'], 'skill-events.v1')
        self.assertIn('blocker', events['event_types']['eval_blocked'])
        self.assertIn('eval', events['event_consumers']['eval_blocked']['profiles'])
        self.assertIn('blocked_auth', events['eval_blocker_classes'])

    def test_skills_events_summary_flags_unknown_profiles(self):
        """Verify event summaries fail closed on undeclared profile references."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills_impl import _skill_event_summary
            summary = _skill_event_summary({'unsafe_event': {'profiles': ['ghost-profile'], 'producer_commands': ['ask unsafe'], 'observer_commands': ['ask events unsafe_event']}}, {'eval': {'intent': 'Run evidence.'}})
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(summary['events_with_unknown_profiles'], {'unsafe_event': ['ghost-profile']})
        self.assertEqual(summary['contract_dimensions'], ['known_profiles', 'observer_commands', 'producer_commands', 'profiles'])
        self.assertEqual(summary['contract_dimension_count'], 4)
        self.assertEqual(summary['contract_dimension_status'], {'known_profiles': 'has_gaps', 'observer_commands': 'ready', 'producer_commands': 'ready', 'profiles': 'ready'})
        self.assertEqual(summary['missing_events_by_contract_dimension'], {'known_profiles': ['unsafe_event'], 'observer_commands': [], 'producer_commands': [], 'profiles': []})
        self.assertEqual(summary['missing_event_count_by_contract_dimension'], {'known_profiles': 1, 'observer_commands': 0, 'producer_commands': 0, 'profiles': 0})
        self.assertEqual(summary['profiles_unknown_to_registry'], ['ghost-profile'])
        self.assertTrue(summary['has_unknown_profiles'])
        self.assertEqual(summary['events_missing_profile_count'], 0)
        self.assertEqual(summary['events_with_unknown_profile_count'], 1)
        self.assertEqual(summary['unknown_profile_reference_count'], 1)
        self.assertEqual(summary['known_profile_names'], ['eval'])
        self.assertEqual(summary['referenced_profile_names'], ['ghost-profile'])
        self.assertEqual(summary['known_events_by_profile'], {'eval': []})
        self.assertEqual(summary['known_event_count_by_profile'], {'eval': 0})
        self.assertEqual(summary['known_profiles_with_events'], [])
        self.assertEqual(summary['known_profile_event_coverage_count'], 0)
        self.assertFalse(summary['all_known_profiles_have_events'])
        self.assertEqual(summary['producer_command_count_by_event'], {'unsafe_event': 1})
        self.assertEqual(summary['observer_command_count_by_event'], {'unsafe_event': 1})
        self.assertEqual(summary['events_by_profile'], {'ghost-profile': ['unsafe_event']})
        self.assertEqual(summary['event_count_by_profile'], {'ghost-profile': 1})
        self.assertEqual(summary['profiles_by_event'], {'unsafe_event': ['ghost-profile']})
        self.assertEqual(summary['profile_count_by_event'], {'unsafe_event': 1})
        self.assertEqual(summary['known_profiles_without_events'], ['eval'])
        self.assertTrue(summary['has_known_profiles_without_events'])
        self.assertEqual(summary['events_with_contract_gaps'], ['unsafe_event'])
        self.assertEqual(summary['contract_gap_count'], 1)
        self.assertTrue(summary['has_contract_gaps'])
        self.assertEqual(summary['contract_status'], 'has_gaps')
        self.assertFalse(summary['contract_ready'])

    def test_skills_readiness_overviews_flag_blocked_sections(self):
        """Verify readiness overview helpers expose blocked sections directly."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills_impl import _skill_events_readiness_overview, _skill_profiles_readiness_overview
            profile_overview = _skill_profiles_readiness_overview({'contract_status': 'ready', 'contract_ready': True, 'contract_gap_count': 0}, {'contract_status': 'has_gaps', 'contract_ready': False, 'contract_gap_count': 2})
            event_overview = _skill_events_readiness_overview({'contract_status': 'has_gaps', 'contract_ready': False, 'contract_gap_count': 1, 'has_contract_gaps': True})
            empty_event_overview = _skill_events_readiness_overview({'contract_status': 'empty', 'contract_ready': False, 'contract_gap_count': 0, 'has_contract_gaps': False})
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(profile_overview['contract_status'], 'has_gaps')
        self.assertFalse(profile_overview['contract_ready'])
        self.assertTrue(profile_overview['has_contract_gaps'])
        self.assertEqual(profile_overview['contract_gap_count'], 2)
        self.assertEqual(profile_overview['ready_contract_sections'], ['profile_contracts'])
        self.assertEqual(profile_overview['blocked_contract_sections'], ['lifecycle_event_coverage'])
        self.assertEqual(profile_overview['contract_status_by_section'], {'lifecycle_event_coverage': 'has_gaps', 'profile_contracts': 'ready'})
        self.assertEqual(profile_overview['contract_gap_count_by_section'], {'lifecycle_event_coverage': 2, 'profile_contracts': 0})
        self.assertEqual(event_overview['contract_status'], 'has_gaps')
        self.assertFalse(event_overview['contract_ready'])
        self.assertTrue(event_overview['has_contract_gaps'])
        self.assertEqual(event_overview['contract_gap_count'], 1)
        self.assertEqual(event_overview['ready_contract_sections'], [])
        self.assertEqual(event_overview['blocked_contract_sections'], ['lifecycle_event_contract'])
        self.assertEqual(event_overview['contract_status_by_section'], {'lifecycle_event_contract': 'has_gaps'})
        self.assertEqual(event_overview['contract_gap_count_by_section'], {'lifecycle_event_contract': 1})
        self.assertEqual(empty_event_overview['contract_status'], 'empty')
        self.assertFalse(empty_event_overview['contract_ready'])
        self.assertFalse(empty_event_overview['has_contract_gaps'])
        self.assertEqual(empty_event_overview['contract_gap_count'], 0)
        self.assertEqual(empty_event_overview['ready_contract_sections'], [])
        self.assertEqual(empty_event_overview['blocked_contract_sections'], ['lifecycle_event_contract'])

    def test_skills_events_human_output(self):
        """Verify ask skills events has a useful non-JSON selected-event render."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'events', 'eval_blocked', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills events output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Skill events: pass', result.stdout)
        self.assertIn('Readiness: ready (0 gaps)', result.stdout)
        self.assertIn('Ready sections: lifecycle_event_contract', result.stdout)
        self.assertIn('Validation: ./bin/ask skills events --json --robot', result.stdout)
        self.assertIn('Event: eval_blocked', result.stdout)
        self.assertIn('Definition:', result.stdout)

    def test_skills_events_command_blocks_unknown_event(self):
        """Verify ask skills events fails closed for unknown event types."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'events', 'made_up_event', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills events output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        events = output['data']['skill_events']
        self.assertEqual(events['status'], 'blocked')
        self.assertEqual(events['requested_event_type'], 'made_up_event')
        self.assertIn('eval_blocked', events['available_event_types'])

    def test_skills_memory_search_command_returns_provider_entries(self):
        """Verify ask skills memory search exposes provenance-bearing entries."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'search', 'projection', '--limit', '3', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills memory search failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        memory = output['data']['skill_memory']
        self.assertEqual(memory['schema_version'], 'skill-memory-provider.v1')
        self.assertEqual(memory['provider_model'], 'extension-like-read-only')
        self.assertEqual(memory['contract_schemas']['memory'], 'skill-memory-provider.v1')
        self.assertEqual(memory['contract_schemas']['profiles'], 'skill-operation-profiles.v1')
        self.assertEqual(memory['operation_context']['provider_model'], 'extension-like-read-only')
        self.assertEqual(memory['operation_context']['provider_contract']['mutation_policy'], 'read_only')
        self.assertIn('provenance', memory['operation_context']['provider_contract']['required_entry_fields'])
        self.assertIn('eval', memory['operation_context']['consumer_profiles'])
        self.assertIn('./bin/ask memory search projection --json --robot', memory['operation_context']['validation_commands'])
        self.assertGreaterEqual(memory['source_summary']['source_count'], 1)
        self.assertEqual(memory['mode'], 'search')
        self.assertGreaterEqual(memory['entry_count'], 1)
        self.assertEqual(memory['entry_summary']['returned_count'], memory['entry_count'])
        self.assertGreaterEqual(memory['entry_summary']['total_count'], memory['entry_count'])
        self.assertIn('provenance', memory['entries'][0])
        self.assertIn('freshness', memory['entries'][0])

    def test_skills_memory_human_output_exposes_provider_contract(self):
        """Verify ask skills memory human output names the provider model and sources."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'search', 'projection', '--limit', '3', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills memory output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Skill memory: search (pass)', result.stdout)
        self.assertIn('Provider: extension-like-read-only', result.stdout)
        self.assertIn('Validation: ./bin/ask skills memory search projection --json --robot', result.stdout)
        self.assertIn('Sources:', result.stdout)
        self.assertIn('docs-agent-guidance', result.stdout)

    def test_skills_memory_search_command_blocks_missing_query(self):
        """Verify ask skills memory search requires a query from the CLI path."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'search', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills memory output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        memory = output['data']['skill_memory']
        self.assertEqual(memory['status'], 'blocked')
        self.assertEqual(memory['mode'], 'search')
        self.assertIn('requires a non-empty query', memory['agent_summary'])

    def test_skills_memory_search_command_blocks_negative_limit(self):
        """Verify ask skills memory search rejects negative limits."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'search', 'projection', '--limit', '-1', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills memory output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        memory = output['data']['skill_memory']
        self.assertEqual(memory['status'], 'blocked')
        self.assertEqual(memory['mode'], 'search')
        self.assertIn('limit must be non-negative', memory['agent_summary'])

__all__ = [name for name in globals() if not name.startswith("__")]
