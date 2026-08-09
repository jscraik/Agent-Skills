from ask_cli_impl_tests_01 import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_skills_prove_workout_next_command_uses_ask_helper(self):
        """Verify workout proof replay commands use the shared ask command builder."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_source = repo_root / 'Skills' / 'agent-ops' / 'demo' / 'SKILL.md'
                skill_source.parent.mkdir(parents=True)
                skill_source.write_text('---\nname: demo\n---\n', encoding='utf-8')
                reachable_result = CallResult()
                reachable_result.data['proof'] = {'status': 'pass', 'handle': 'demo', 'resolution': {'status': 'ok', 'handle': 'demo', 'source_path': skill_source.relative_to(repo_root).as_posix()}}
                with mock.patch.object(skills_commands, 'skills_proof', return_value=reachable_result), mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, 'skill_invocation_analytics', return_value={'status': 'unavailable_or_legacy'}), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=['outcome proof']):
                    result = skills_commands.skills_prove(repo_root, 'demo')
        finally:
            sys.path.remove(lib_path)
        skill_proof = result.data['skill_proof']
        self.assertEqual(result.status, 'error')
        self.assertEqual(skill_proof['proof_status'], 'reachable_without_outcome_proof')
        self.assertEqual(skill_proof['next_command'], "./bin/ask workouts run 'outcome proof' --json --robot")
        self.assertEqual(skill_proof['validation_commands'], [skill_proof['next_command']])

    def test_skills_prove_accepts_current_identity_bound_shard_aggregate(self):
        """A current local aggregate is outcome proof rather than a legacy workout."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                source = repo_root / 'Skills' / 'agent-ops' / 'demo' / 'SKILL.md'
                source.parent.mkdir(parents=True)
                source.write_text('---\nname: demo\n---\n', encoding='utf-8')
                rubric_path = repo_root / 'Infrastructure' / 'config' / 'skills-sdk' / 'gold-standard-rubric.v1.json'
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding='utf-8')
                rubric_digest = 'sha256:' + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                aggregate_path = repo_root / 'Infrastructure' / 'artifacts' / 'skills' / 'demo' / 'proof' / 'aggregate.json'
                aggregate_path.parent.mkdir(parents=True)
                aggregate_path.write_text(json.dumps({'status': 'success', 'data': {'skills_sdk_eval_shard_aggregate': {'status': 'pass', 'receipt': {'status': 'pass', 'lane': 'oss-local', 'profile': 'oss-local', 'codex_profile': 'oss-local', 'package_id': 'demo', 'package_digest': 'sha256:current', 'rubric_digest': rubric_digest, 'scenario_set_id': 'demo-release-8-v1', 'case_count': 8, 'checks': [{'id': 'shards_match_current_package', 'status': 'pass'}, {'id': 'all_case_results_pass', 'status': 'pass'}]}}}}), encoding='utf-8')
                reachable = CallResult()
                reachable.data['proof'] = {'status': 'pass', 'handle': 'demo', 'resolution': {'status': 'ok', 'handle': 'demo', 'source_path': source.relative_to(repo_root).as_posix()}}
                with mock.patch.object(skills_commands, 'skills_proof', return_value=reachable), mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, 'skill_invocation_analytics', return_value={'status': 'unavailable_or_legacy'}), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=[]), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    result = skills_commands.skills_prove(repo_root, 'demo')
        finally:
            sys.path.remove(lib_path)
        proof = result.data['skill_proof']
        self.assertEqual(proof['proof_status'], 'proved_local')
        self.assertEqual(proof['outcome_proof']['status'], 'pass')
        self.assertEqual(proof['outcome_proof']['evidence_ref'], 'Infrastructure/artifacts/skills/demo/proof/aggregate.json')
        self.assertEqual(proof['next_command'], None)
        self.assertEqual(proof['validation_commands'], [])

    def test_skills_prove_keeps_outcome_proof_when_runtime_is_blocked(self):
        """Runtime reachability must not hide current local outcome evidence."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                source = repo_root / 'Skills' / 'agent-ops' / 'demo' / 'SKILL.md'
                source.parent.mkdir(parents=True)
                source.write_text('---\nname: demo\n---\n', encoding='utf-8')
                blocked = CallResult(status='error')
                blocked.data['proof'] = {'status': 'fail', 'handle': 'demo', 'resolution': {'status': 'ok', 'handle': 'demo', 'source_path': source.relative_to(repo_root).as_posix()}, 'runtime_diagnostics': {'recovery_commands': [{'kind': 'preview_user_runtime_sync', 'command': './bin/ask skills sync --scope user --projection flat --dry-run --json --robot'}]}}
                outcome_proof = {'status': 'pass', 'evidence_class': 'oss_local_release_aggregate', 'evidence_ref': 'Infrastructure/artifacts/skills/demo/proof/aggregate.json', 'evidence_digest': 'sha256:current', 'scenario_set': 'demo-release-8-v1', 'case_count': 8}
                with mock.patch.object(skills_commands, 'skills_proof', return_value=blocked), mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()) as audit_mock, mock.patch.object(skills_commands, 'skill_invocation_analytics', return_value={'status': 'unavailable_or_legacy'}), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=[]), mock.patch.object(skills_commands._impl, '_eval_shard_outcome_proof', return_value=outcome_proof):
                    result = skills_commands.skills_prove(repo_root, 'demo')
        finally:
            sys.path.remove(lib_path)
        proof = result.data['skill_proof']
        self.assertEqual(result.status, 'error')
        self.assertEqual(proof['proof_status'], 'blocked_reachability')
        self.assertEqual(proof['outcome_proof']['status'], 'pass')
        self.assertEqual(proof['outcome_proof']['workout_candidates'], [])
        for key, value in outcome_proof.items():
            self.assertEqual(proof['outcome_proof'][key], value)
        self.assertEqual(proof['next_command'], './bin/ask skills sync --scope user --projection flat --dry-run --json --robot')
        audit_mock.assert_called_once_with(repo_root, 'Skills/agent-ops/demo', level='compat', validation_scope='source')

    def test_skills_prove_rejects_stale_shard_aggregate_package_digest(self):
        """A passing aggregate for an earlier package must not prove the current source."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                source = repo_root / 'Skills' / 'agent-ops' / 'demo' / 'SKILL.md'
                source.parent.mkdir(parents=True)
                source.write_text('---\nname: demo\n---\n', encoding='utf-8')
                aggregate_path = repo_root / 'Infrastructure' / 'artifacts' / 'skills' / 'demo' / 'proof' / 'aggregate.json'
                aggregate_path.parent.mkdir(parents=True)
                aggregate_path.write_text(json.dumps({'status': 'success', 'data': {'skills_sdk_eval_shard_aggregate': {'status': 'pass', 'receipt': {'status': 'pass', 'package_id': 'demo', 'package_digest': 'sha256:stale', 'checks': [{'id': 'shards_match_current_package', 'status': 'pass'}, {'id': 'all_case_results_pass', 'status': 'pass'}]}}}}), encoding='utf-8')
                reachable = CallResult()
                reachable.data['proof'] = {'status': 'pass', 'handle': 'demo', 'resolution': {'status': 'ok', 'handle': 'demo', 'source_path': source.relative_to(repo_root).as_posix()}}
                with mock.patch.object(skills_commands, 'skills_proof', return_value=reachable), mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, 'skill_invocation_analytics', return_value={'status': 'unavailable_or_legacy'}), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=[]), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    result = skills_commands.skills_prove(repo_root, 'demo')
        finally:
            sys.path.remove(lib_path)
        proof = result.data['skill_proof']
        self.assertEqual(result.status, 'error')
        self.assertEqual(proof['proof_status'], 'reachable_without_outcome_proof')
        self.assertEqual(proof['outcome_proof']['status'], 'missing')

    def test_skills_prove_names_first_bounded_release_shard_when_outcome_is_missing(self):
        """A missing aggregate must advance through a bounded declared release shard."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                skill_dir.mkdir(parents=True)
                skill_dir.joinpath('SKILL.md').write_text('---\nname: demo\n---\n', encoding='utf-8')
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir()
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-8-v1\n    default: true\n    minimum_scenarios: 5\n    groups:\n      core: [case-one, case-two, case-three, case-four, case-five]\n', encoding='utf-8')
                reachable = CallResult()
                reachable.data['proof'] = {'status': 'pass', 'handle': 'demo', 'resolution': {'status': 'ok', 'handle': 'demo', 'source_path': 'Skills/agent-ops/demo/SKILL.md'}}
                with mock.patch.object(skills_commands, 'skills_proof', return_value=reachable), mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, 'skill_invocation_analytics', return_value={'status': 'unavailable_or_legacy'}), mock.patch.object(skills_commands, '_skill_workout_candidates', return_value=[]), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    result = skills_commands.skills_prove(repo_root, 'demo')
        finally:
            sys.path.remove(lib_path)
        proof = result.data['skill_proof']
        self.assertEqual(result.status, 'error')
        self.assertEqual(proof['proof_status'], 'reachable_without_outcome_proof')
        self.assertEqual(proof['next_command'], './bin/ask sdk eval run Skills/agent-ops/demo --runner internal --mode release --codex-profile oss-local --scenario-set demo-release-8-v1 --case case-one --case case-two --json --robot')

    def test_outcome_proof_next_command_rejects_undersized_release_set(self):
        """An invalid release set must not replace the existing safe repair action."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-invalid-v1\n    default: true\n    minimum_scenarios: 5\n    groups:\n      core: [case-one, case-two]\n', encoding='utf-8')
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_source_path', return_value=skill_dir / 'SKILL.md'):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, 'demo', './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(command, './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot')

    def test_outcome_proof_next_command_skips_current_passing_shard_cases(self):
        """A current shard receipt advances the next action to missing release cases."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-8-v1\n    default: true\n    minimum_scenarios: 5\n    groups:\n      core: [case-one, case-two, case-three, case-four, case-five]\n', encoding='utf-8')
                rubric_path = repo_root / 'Infrastructure' / 'config' / 'skills-sdk' / 'gold-standard-rubric.v1.json'
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding='utf-8')
                rubric_digest = 'sha256:' + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                receipt_path = repo_root / 'Infrastructure' / 'artifacts' / 'skills' / 'demo' / 'run' / 'sdk-eval-run-receipt.json'
                receipt_path.parent.mkdir(parents=True)
                receipt_path.write_text(json.dumps({'status': 'pass', 'lane': 'oss-local', 'lane_type': 'release-shard', 'profile': 'oss-local', 'codex_profile': 'oss-local', 'rubric_digest': rubric_digest, 'scenario_set_id': 'demo-release-8-v1', 'package_id': 'demo', 'package_digest': 'sha256:current', 'selected_case_ids': ['case-one', 'case-two'], 'case_count': 2, 'passed_count': 2, 'failed_count': 0}), encoding='utf-8')
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_source_path', return_value=skill_dir / 'SKILL.md'), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, 'demo', './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot')
        finally:
            sys.path.remove(lib_path)
        self.assertIn('--case case-three --case case-four', command)

    def test_outcome_proof_next_command_aggregates_complete_current_release_shards(self):
        """Complete current shards advance to the existing aggregate command."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-5-v1\n    default: true\n    minimum_scenarios: 5\n    groups:\n      core: [case-one, case-two, case-three, case-four, case-five]\n', encoding='utf-8')
                rubric_path = repo_root / 'Infrastructure' / 'config' / 'skills-sdk' / 'gold-standard-rubric.v1.json'
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding='utf-8')
                rubric_digest = 'sha256:' + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                receipts_root = repo_root / 'Infrastructure' / 'artifacts' / 'skills' / 'demo'
                for index, selected_case_ids in enumerate((['case-one', 'case-two'], ['case-three', 'case-four'], ['case-five'])):
                    receipt_path = receipts_root / f'run-{index}' / 'sdk-eval-run-receipt.json'
                    receipt_path.parent.mkdir(parents=True)
                    receipt_path.write_text(json.dumps({'status': 'pass', 'lane': 'oss-local', 'lane_type': 'release-shard', 'profile': 'oss-local', 'codex_profile': 'oss-local', 'rubric_digest': rubric_digest, 'scenario_set_id': 'demo-release-5-v1', 'package_id': 'demo', 'package_digest': 'sha256:current', 'selected_case_ids': selected_case_ids, 'case_count': len(selected_case_ids), 'passed_count': len(selected_case_ids), 'failed_count': 0}), encoding='utf-8')
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_source_path', return_value=skill_dir / 'SKILL.md'), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, 'demo', './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(command, './bin/ask sdk eval aggregate-shards Skills/agent-ops/demo --scenario-set demo-release-5-v1 --codex-profile oss-local --receipt Infrastructure/artifacts/skills/demo/run-0/sdk-eval-run-receipt.json --receipt Infrastructure/artifacts/skills/demo/run-1/sdk-eval-run-receipt.json --receipt Infrastructure/artifacts/skills/demo/run-2/sdk-eval-run-receipt.json --json --robot')

    def test_outcome_proof_next_command_ignores_stale_and_non_shard_receipts(self):
        """Only current release-shard receipts may advance an OSS-local release set."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-5-v1\n    default: true\n    minimum_scenarios: 5\n    groups:\n      core: [case-one, case-two, case-three, case-four, case-five]\n', encoding='utf-8')
                rubric_path = repo_root / 'Infrastructure' / 'config' / 'skills-sdk' / 'gold-standard-rubric.v1.json'
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding='utf-8')
                receipts_root = repo_root / 'Infrastructure' / 'artifacts' / 'skills' / 'demo'
                for run_name, lane_type, rubric_digest in (('full-release', 'release', 'sha256:' + hashlib.sha256(rubric_path.read_bytes()).hexdigest()), ('stale-shard', 'release-shard', 'sha256:stale')):
                    receipt_path = receipts_root / run_name / 'sdk-eval-run-receipt.json'
                    receipt_path.parent.mkdir(parents=True)
                    receipt_path.write_text(json.dumps({'status': 'pass', 'lane': 'oss-local', 'lane_type': lane_type, 'profile': 'oss-local', 'codex_profile': 'oss-local', 'rubric_digest': rubric_digest, 'scenario_set_id': 'demo-release-5-v1', 'package_id': 'demo', 'package_digest': 'sha256:current', 'selected_case_ids': ['case-one', 'case-two'], 'case_count': 2, 'passed_count': 2, 'failed_count': 0}), encoding='utf-8')
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_source_path', return_value=skill_dir / 'SKILL.md'), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, 'demo', './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot')
        finally:
            sys.path.remove(lib_path)
        self.assertIn('--case case-one --case case-two', command)
        self.assertNotIn('aggregate-shards', command)

    def test_outcome_proof_next_command_uses_latest_disjoint_release_shards(self):
        """A rerun replaces its earlier shard instead of duplicating aggregate cases."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-5-v1\n    default: true\n    minimum_scenarios: 5\n    groups:\n      core: [case-one, case-two, case-three, case-four, case-five]\n', encoding='utf-8')
                rubric_path = repo_root / 'Infrastructure' / 'config' / 'skills-sdk' / 'gold-standard-rubric.v1.json'
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding='utf-8')
                rubric_digest = 'sha256:' + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                receipts_root = repo_root / 'Infrastructure' / 'artifacts' / 'skills' / 'demo'
                for index, (run_name, selected_case_ids) in enumerate((('rerun-old', ['case-one', 'case-two']), ('rerun-new', ['case-one', 'case-two']), ('run-one', ['case-three', 'case-four']), ('run-two', ['case-five']))):
                    receipt_path = receipts_root / run_name / 'sdk-eval-run-receipt.json'
                    receipt_path.parent.mkdir(parents=True)
                    receipt_path.write_text(json.dumps({'status': 'pass', 'lane': 'oss-local', 'lane_type': 'release-shard', 'profile': 'oss-local', 'codex_profile': 'oss-local', 'rubric_digest': rubric_digest, 'scenario_set_id': 'demo-release-5-v1', 'package_id': 'demo', 'package_digest': 'sha256:current', 'selected_case_ids': selected_case_ids, 'case_count': len(selected_case_ids), 'passed_count': len(selected_case_ids), 'failed_count': 0}), encoding='utf-8')
                    os.utime(receipt_path, ns=(1000000000 + index, 1000000000 + index))
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_source_path', return_value=skill_dir / 'SKILL.md'), mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, 'demo', './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot')
        finally:
            sys.path.remove(lib_path)
        self.assertIn('rerun-new', command)
        self.assertIn('run-one', command)
        self.assertIn('run-two', command)
        self.assertNotIn('rerun-old', command)

    def test_outcome_proof_next_command_falls_back_for_non_numeric_minimum(self):
        """Malformed release-set thresholds cannot escape the compact proof facade."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / 'Skills' / 'agent-ops' / 'demo'
                evals_path = skill_dir / 'references' / 'evals.yaml'
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text('release_scenario_sets:\n  - id: demo-release-invalid-v1\n    default: true\n    minimum_scenarios: not-a-number\n    groups:\n      core: [case-one, case-two, case-three, case-four, case-five]\n', encoding='utf-8')
                fallback = './bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot'
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_source_path', return_value=skill_dir / 'SKILL.md'):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, 'demo', fallback)
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(command, fallback)

    def test_current_release_shard_receipts_reject_path_traversal_package_id(self):
        """Receipt discovery remains contained in the package artifact lane."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                rubric_path = repo_root / 'Infrastructure' / 'config' / 'skills-sdk' / 'gold-standard-rubric.v1.json'
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding='utf-8')
                escaped_receipt = repo_root / 'Infrastructure' / 'artifacts' / 'outside' / 'run' / 'sdk-eval-run-receipt.json'
                escaped_receipt.parent.mkdir(parents=True)
                escaped_receipt.write_text(json.dumps({'status': 'pass', 'lane': 'oss-local', 'lane_type': 'release-shard', 'profile': 'oss-local', 'codex_profile': 'oss-local', 'rubric_digest': 'sha256:' + hashlib.sha256(rubric_path.read_bytes()).hexdigest(), 'scenario_set_id': 'demo-release-5-v1', 'package_id': '../outside', 'package_digest': 'sha256:current', 'selected_case_ids': ['case-one'], 'case_count': 1, 'passed_count': 1, 'failed_count': 0}), encoding='utf-8')
                receipts = skills_commands._impl._current_release_shard_receipts(repo_root, package_id='../outside', package_digest='sha256:current', scenario_set_id='demo-release-5-v1')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(receipts, [])

    def test_persist_eval_shard_aggregate_does_not_claim_failed_write(self):
        """A failed aggregate write cannot leave persisted-evidence fields on the payload."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                payload = {'mutation_performed': False}
                with mock.patch.object(Path, 'write_text', side_effect=OSError('disk full')):
                    artifact_ref = skills_commands._impl._skills_sdk_persist_eval_shard_aggregate(Path(temp_dir), 'demo', payload)
        finally:
            sys.path.remove(lib_path)
        self.assertIsNone(artifact_ref)
        self.assertNotIn('artifact_path', payload)
        self.assertFalse(payload['mutation_performed'])

    def test_persist_eval_shard_aggregate_rejects_dot_package_ids(self):
        """Aggregate evidence never escapes its per-package artifact lane."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                for package_id in ('.', '..'):
                    with self.subTest(package_id=package_id):
                        payload = {'mutation_performed': False}
                        artifact_ref = skills_commands._impl._skills_sdk_persist_eval_shard_aggregate(repo_root, package_id, payload)
                        self.assertIsNone(artifact_ref)
                        self.assertEqual(payload, {'mutation_performed': False})
                        self.assertFalse((repo_root / 'Infrastructure' / 'artifacts').exists())
        finally:
            sys.path.remove(lib_path)

    def test_shard_aggregate_writes_evidence_only_outside_preview(self):
        """The normal aggregate route persists evidence while preview remains non-mutating."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                receipt = {'status': 'pass', 'agent_summary': 'All bounded release shards passed.'}
                with mock.patch.object(skills_commands._impl, '_skills_sdk_eval_package_identity', return_value={'package_id': 'demo', 'package_digest': 'sha256:current'}), mock.patch('ask.skills_sdk.eval_shard_aggregate.build_eval_shard_aggregate_receipt', return_value=receipt):
                    written = skills_commands.skills_sdk_eval_shard_aggregate(repo_root, target='Skills/agent-ops/demo', scenario_set='demo-release-5-v1', receipts=['Infrastructure/artifacts/skills/demo/run-0/sdk-eval-run-receipt.json'])
                    preview = skills_commands.skills_sdk_eval_shard_aggregate_preview(repo_root, target='Skills/agent-ops/demo', scenario_set='demo-release-5-v1', receipts=['Infrastructure/artifacts/skills/demo/run-0/sdk-eval-run-receipt.json'])
                    written_payload = written.data['skills_sdk_eval_shard_aggregate']
                    artifact_path = repo_root / written_payload['artifact_path']
                    self.assertTrue(written_payload['mutation_performed'])
                    self.assertTrue(artifact_path.is_file())
                    self.assertEqual(json.loads(artifact_path.read_text(encoding='utf-8'))['data']['skills_sdk_eval_shard_aggregate']['receipt'], receipt)
                    preview_payload = preview.data['skills_sdk_eval_shard_aggregate']
                    self.assertFalse(preview_payload['mutation_performed'])
                    self.assertNotIn('artifact_path', preview_payload)
        finally:
            sys.path.remove(lib_path)

    def test_compact_skill_prove_payload_keeps_local_outcome_evidence(self):
        """The compact proof facade retains the identity-bound outcome reference."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.cli_output import compact_skill_prove_payload
        finally:
            sys.path.remove(lib_path)
        payload = {'skill_proof': {'schema_version': 'skill-proof-scorecard.v1', 'query': 'demo', 'handle': 'demo', 'proof_status': 'proved_local', 'agent_summary': 'demo has current local outcome proof.', 'reachability': {'status': 'pass', 'command': './bin/ask skills proof demo --json --robot'}, 'structural_quality': {'status': 'pass', 'audit_level': 'compat', 'audit_command': 'audit demo'}, 'outcome_proof': {'status': 'pass', 'evidence_class': 'oss_local_release_aggregate', 'evidence_ref': 'Infrastructure/artifacts/skills/demo/proof/aggregate.json', 'evidence_digest': 'sha256:current', 'scenario_set': 'demo-release-8-v1', 'case_count': 8}, 'next_command': None, 'validation_commands': []}}
        compact_skill_prove_payload(payload)
        self.assertEqual(payload['skill_proof']['outcome_proof'], {'status': 'pass', 'evidence_class': 'oss_local_release_aggregate', 'evidence_ref': 'Infrastructure/artifacts/skills/demo/proof/aggregate.json', 'evidence_digest': 'sha256:current', 'scenario_set': 'demo-release-8-v1', 'case_count': 8})

    def test_skill_invocation_analytics_resolves_relative_telemetry_dir_from_repo_root(self):
        """Verify relative SKILL_TELEMETRY_DIR overrides are repo-root relative."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.skill_analytics import skill_invocation_analytics
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                telemetry_dir = repo_root / 'telemetry'
                telemetry_dir.mkdir(parents=True)
                telemetry_dir.joinpath('skill-invocations.jsonl').write_text(json.dumps({'skill_id': 'autofix', 'timestamp': '2026-05-07T10:00:00Z'}) + '\n', encoding='utf-8')
                with mock.patch.dict(os.environ, {'SKILL_TELEMETRY_DIR': 'telemetry'}):
                    analytics = skill_invocation_analytics(repo_root, 'autofix')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(analytics['status'], 'available')
        self.assertEqual(analytics['matching_invocation_count'], 1)

    def test_skills_explain_json_contract(self):
        """Verify ask skills explain returns concise agent-facing skill guidance."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'explain', 'autofix', '--robot', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        skills_explain = output['data']['skills_explain']
        self.assertEqual(skills_explain['schema_version'], 'skills-explain.v1')
        self.assertEqual(skills_explain['query'], 'autofix')
        self.assertEqual(skills_explain['canonical_source'], 'Skills/agent-ops/autofix/SKILL.md')
        self.assertEqual(skills_explain['skill_handle'], 'autofix')
        self.assertEqual(skills_explain['handle_source'], 'sdk_flat_registry')
        self.assertIn('validation', skills_explain)
        self.assertIn('when_not_to_use', skills_explain)
        explanation = output['data']['explanation']
        self.assertEqual(explanation['schema_version'], 'skill-explanation.v1')
        self.assertEqual(explanation['handle'], 'autofix')
        self.assertEqual(explanation['status'], 'resolved')
        for field in ('agent_summary', 'canonical_source_path', 'runtime_projection_path', 'skill_handles', 'required_validation', 'validation_commands', 'known_limitations', 'reachability', 'next_command'):
            self.assertIn(field, explanation)
        self.assertIsInstance(explanation['reachability'], dict)

    def test_skills_explain_human_output_exposes_validation(self):
        """Verify ask skills explain renders its primary validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'explain', 'Skills/agent-ops/autofix', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills explain output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('ℹ️  Skill: $autofix (resolved)', result.stdout)
        self.assertIn('Source: Skills/agent-ops/autofix/SKILL.md', result.stdout)
        self.assertIn('Validation: ./bin/ask skills audit Skills/agent-ops/autofix --level strict --json --robot', result.stdout)
        self.assertIn('Next: ./bin/ask skills proof autofix --json --robot', result.stdout)

    def test_skills_explain_golden_path_fields_for_flat_handles(self):
        """Verify explain exposes source, runtime, validation, and proof handoff."""
        for handle, canonical_source, owner in (('agents-md', 'Skills/agent-ops/agents-md/SKILL.md', 'agent-ops'), ('simplify', 'Skills/agent-ops/simplify/SKILL.md', 'Agent Skills Team')):
            with self.subTest(handle=handle):
                cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'explain', handle, '--json', '--robot']
                result = _run_cli(cmd)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                skills_explain = output['data']['skills_explain']
                self.assertEqual(skills_explain['query'], handle)
                self.assertEqual(skills_explain['canonical_source'], canonical_source)
                self.assertEqual(skills_explain['skill_handle'], handle)
                self.assertEqual(skills_explain['handle_source'], 'sdk_flat_registry')
                self.assertIn(skills_explain['runtime_projection'], {'flat', 'source'})
                self.assertIn(skills_explain['runtime_visibility'], {'flat', 'source'})
                self.assertEqual(skills_explain['owner'], owner)
                self.assertIn('validation', skills_explain)
                self.assertIn('ambiguity_notes', skills_explain)
                explanation = output['data']['explanation']
                self.assertEqual(explanation['canonical_source_path'], canonical_source)
                if skills_explain['runtime_projection'] == 'flat':
                    self.assertEqual(explanation['runtime_projection_path'], f'.agents/skills/{handle}/SKILL.md')
                else:
                    self.assertIsNone(explanation['runtime_projection_path'])
                self.assertEqual(explanation['skill_handles'], [{'handle': handle, 'path': explanation['runtime_projection_path'], 'projection_note': None if explanation['runtime_projection_path'] else 'projection_not_file_backed', 'handle_source': 'sdk_flat_registry'}])
                self.assertTrue(explanation['validation_commands'])
                self.assertIn('known_limitations', explanation)
                self.assertIn(explanation['reachability']['status'], {'pass', 'fail'})
                self.assertEqual(explanation['reachability']['proof_command'], f'./bin/ask skills proof {handle} --json --robot')
                self.assertEqual(explanation['next_command'], f'./bin/ask skills proof {handle} --json --robot')

    def test_skills_explain_rejects_out_of_repo_source_path(self):
        """Verify explain validates resolved skill paths before reading skill files."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with mock.patch.object(skills_commands, 'resolve_skill_handle', return_value={'status': 'ok', 'handle': 'escaped', 'source_path': '../outside/SKILL.md', 'description': 'outside repo'}):
                result = skills_commands.explain_skill(Path.cwd(), 'escaped')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.errors[0].code, 'ERR_PATH_TRAVERSAL')

    def test_skills_explain_rejects_missing_source_path(self):
        """Verify explain rejects resolved handles that omit the source path."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with mock.patch.object(skills_commands, 'resolve_skill_handle', return_value={'status': 'ok', 'handle': 'missing-source', 'description': 'missing source'}):
                result = skills_commands.explain_skill(Path.cwd(), 'missing-source')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.errors[0].code, 'ERR_VALIDATION')
        self.assertIn('without a canonical source path', result.errors[0].message)

    def test_skills_explain_rejects_nonexistent_source_file(self):
        """Verify explain rejects stale handles before reading source sections."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with mock.patch.object(skills_commands, 'resolve_skill_handle', return_value={'status': 'ok', 'handle': 'stale-source', 'source_path': 'Skills/agent-ops/nope/SKILL.md', 'description': 'stale source'}):
                result = skills_commands.explain_skill(Path.cwd(), 'stale-source')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.errors[0].code, 'ERR_VALIDATION')
        self.assertIn('is missing', result.errors[0].message)

    def test_skills_explain_rejects_unreadable_source_file(self):
        """Verify explain rejects source files that cannot be read."""
        lib_path = str(REPO_ROOT / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            with mock.patch.object(skills_commands, 'resolve_skill_handle', return_value={'status': 'ok', 'handle': 'autofix', 'source_path': 'Skills/agent-ops/autofix/SKILL.md', 'description': 'autofix'}), mock.patch.object(skills_commands, '_skill_sections', side_effect=PermissionError('permission denied')):
                result = skills_commands.explain_skill(REPO_ROOT, 'autofix')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.errors[0].code, 'ERR_VALIDATION')
        self.assertIn('could not be read', result.errors[0].message)

    def test_reviewers_resolve_json_contract(self):
        """Verify ask reviewers resolve exposes the reviewer handle namespace."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'reviewers', 'resolve', 'skillinspector', '--json']
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / 'agents.json'
            manifest.write_text(json.dumps([{'role': 'skill-inspector', 'source': 'test', 'output': 'agents/skill-inspector.toml'}]), encoding='utf-8')
            env = os.environ.copy()
            env['CODEX_AGENTS_MANIFEST'] = str(manifest)
            result = _run_cli(cmd, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output['data']['resolution']
        self.assertEqual(resolution['status'], 'ok')
        self.assertEqual(resolution['kind'], 'reviewer')
        self.assertEqual(resolution['command_visibility'], 'reviewer')
        self.assertEqual(resolution['canonical_handle'], 'skill-inspector')
        self.assertEqual(resolution['validation_commands'], ['./bin/ask reviewers resolve skill-inspector --json --robot'])

    def test_reviewers_resolve_human_output(self):
        """Verify ask reviewers resolve has a useful non-JSON success render."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'reviewers', 'resolve', 'skillinspector']
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / 'agents.json'
            manifest.write_text(json.dumps([{'role': 'skill-inspector', 'source': 'test', 'output': 'agents/skill-inspector.toml'}]), encoding='utf-8')
            env = os.environ.copy()
            env['CODEX_AGENTS_MANIFEST'] = str(manifest)
            result = _run_cli(cmd, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Reviewer handle: @skill-inspector', result.stdout)
        self.assertIn('Source: test', result.stdout)
        self.assertIn('Validation: ./bin/ask reviewers resolve skill-inspector --json --robot', result.stdout)

    def test_reviewers_missing_action_exposes_validation(self):
        """Verify ask reviewers missing action returns a concrete recovery command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'reviewers', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask reviewers resolve skill-inspector --json --robot'])

    def test_reviewers_missing_action_human_output_exposes_validation(self):
        """Verify ask reviewers missing action prints the recovery command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'reviewers', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("missing action for topic 'reviewers'", result.stdout)
        self.assertIn('Validation: ./bin/ask reviewers resolve skill-inspector --json --robot', result.stdout)

    def test_skills_invalid_action_mentions_prove(self):
        """Verify invalid skill-action guidance includes the public prove command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'nonsense', '--json']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        suggestion = output['errors'][0]['fix_suggestion']
        self.assertIn('prove', suggestion)

    def test_unknown_action_helpers_share_valid_actions_fix_suggestion(self):
        """Verify unknown-action helpers format valid actions from one source."""
        unknown_result = build_unknown_action_result('repo', 'nonsense')
        helpful_result = build_helpful_error('repo', 'nonsense', ['repo', 'nonsense'])
        expected_suggestion = f"Valid actions: {', '.join(VALID_ACTIONS['repo'])}"
        self.assertEqual(unknown_result.errors[0].fix_suggestion, expected_suggestion)
        self.assertEqual(helpful_result.errors[0].fix_suggestion, expected_suggestion)
        self.assertEqual(unknown_result.data['validation_commands'], ['./bin/ask repo status --json --robot'])
        self.assertEqual(unknown_result.data['candidate_commands'], ['ask repo doctor --json --robot', 'ask repo closeout --changed --json --robot', 'ask repo validate --ephemeral'])

    def test_skills_unknown_action_exposes_parser_recovery_validation(self):
        """Verify parser-level unknown skill actions expose the recovery command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'nonsense', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('Unknown action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask sdk start <skill> --json --robot'])
        self.assertEqual(output['data']['candidate_commands'], ['ask skills package verify Skills/agent-ops/simplify --strict --json --robot', 'ask skills prove Skills/agent-ops/simplify --json --robot'])

    def test_skills_unknown_action_human_output_exposes_parser_recovery_validation(self):
        """Verify parser-level unknown skill actions render the recovery command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'nonsense', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('Unknown action', result.stdout)
        self.assertIn('Validation: ./bin/ask sdk start <skill> --json --robot', result.stdout)

    def test_skills_default_help_hides_expert_routes_but_sync_remains_callable(self):
        help_result = _run_cli([sys.executable, 'Infrastructure/bin/ask', 'skills', '--help'])
        sync_result = _run_cli([sys.executable, 'Infrastructure/bin/ask', 'skills', 'sync', '--help'])
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn('{package,prove}', help_result.stdout)
        self.assertNotIn('Synchronize skill symlinks', help_result.stdout)
        self.assertEqual(sync_result.returncode, 0, sync_result.stderr)
        self.assertIn('--user-sync-mode {full,links-only}', sync_result.stdout)

__all__ = [name for name in globals() if not name.startswith("__")]
