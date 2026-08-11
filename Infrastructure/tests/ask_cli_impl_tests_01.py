from ask_cli_impl_tests_core import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_json_envelope_format(self):
        """CA1: Verify ask --json returns a valid CallResult envelope."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'CLI failed with stderr: {result.stderr}')
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail('CLI output was not valid JSON')
        self.assertIn('status', output)
        self.assertIn('trace_id', output)
        self.assertIn('metadata', output)
        self.assertEqual(output['status'], 'success')
        self.assertIn('version', output['metadata'])

    def test_repo_status_discovery(self):
        """CA1: Verify ask repo status correctly identifies the repo root."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'status', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertIn('repo_root', output['data'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask repo status --json --robot'])
        repo_root = output['data']['repo_root']
        if '<USER_HOME>' in repo_root:
            repo_root = repo_root.replace('<USER_HOME>', os.path.expanduser('~'))
        self.assertTrue(os.path.isdir(repo_root), f'repo_root is not a directory: {repo_root}')

    def test_repo_status_human_output_exposes_validation(self):
        """Verify repo status human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'status', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Success:', result.stdout)
        self.assertIn('Validation: ./bin/ask repo status --json --robot', result.stdout)

    def test_repo_yaml_inspect_cli_uses_managed_pyyaml(self):
        """Verify YAML inspection works through ask instead of bare system python."""
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp_dir:
            yaml_path = Path(tmp_dir) / 'fixture.yaml'
            yaml_path.write_text('cases:\n  - id: package-fixture\n', encoding='utf-8')
            cmd = ['python3', './bin/ask', 'repo', 'yaml-inspect', str(yaml_path.relative_to(REPO_ROOT)), '--query', 'cases.0.id', '--json', '--robot']
            result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'yaml-inspect output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['yaml']['query_value'], 'package-fixture')
        self.assertTrue(output['data']['python_command'].endswith(' -'))
        self.assertNotIn('mise exec', output['data']['python_command'])
        self.assertNotIn('mise', output['data']['python_command'])

    def test_repo_yaml_inspect_serializes_yaml_dates(self):
        """Verify YAML inspection emits JSON-safe values for YAML scalar types."""
        repo_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmp_dir:
            yaml_path = Path(tmp_dir) / 'dates.yaml'
            yaml_path.write_text('released_on: 2026-06-16\n', encoding='utf-8')
            relative_path = yaml_path.relative_to(repo_root)
            cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'yaml-inspect', str(relative_path), '--query', 'released_on', '--json', '--robot']
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])
        self.assertEqual(result.returncode, 0, f'yaml-inspect output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['yaml']['query_type'], 'date')
        self.assertEqual(output['data']['yaml']['query_value'], '2026-06-16')

    def test_repo_yaml_inspect_human_output_renders_result(self):
        """Verify YAML inspection has a visible non-JSON success output."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'yaml-inspect', 'Skills/agent-ops/improve-agent-native/references/evals.yaml', '--query', 'cases.0.id', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'yaml-inspect output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('YAML inspect: Skills/agent-ops/improve-agent-native/references/evals.yaml', result.stdout)
        self.assertIn('query=cases.0.id', result.stdout)
        self.assertIn("value='smoke-discovery-target'", result.stdout)

    def test_repo_yaml_inspect_human_output_renders_summary_without_query(self):
        """Verify root YAML inspection renders summary metadata without a query."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', 'yaml-inspect', 'Skills/agent-ops/improve-agent-native/references/evals.yaml', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'yaml-inspect output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('root_type=dict', result.stdout)
        self.assertIn('top_level_keys=', result.stdout)
        self.assertNotIn('item_count=None', result.stdout)

    def test_repo_missing_action_exposes_validation(self):
        """Verify incomplete repo commands expose the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'repo output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask repo status --json --robot'])

    def test_repo_missing_action_human_output_exposes_validation(self):
        """Verify incomplete repo commands render the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'repo', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'repo output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'repo'", result.stdout)
        self.assertIn('Validation: ./bin/ask repo status --json --robot', result.stdout)

    def test_skills_list(self):
        """
            Validate that `ask skills list --json` returns a skills catalogue with required envelope, mode settings, and skill fields.

            Checks:
            - Exit code 0 and `status` equals "success".
            - `data.skills` is present as a list.
            - `advanced_mode` is true and `inventory_mode` equals "repo".
            - `validation_commands` contains the expected replay command.
            - If non-empty, first skill contains `name` and `path`.
            """
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'list', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertIn('skills', output['data'])
        self.assertIsInstance(output['data']['skills'], list)
        self.assertTrue(output['data'].get('advanced_mode'))
        self.assertEqual(output['data'].get('inventory_mode'), 'repo')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills list --json --robot'])
        if len(output['data']['skills']) > 0:
            skill = output['data']['skills'][0]
            self.assertIn('name', skill)
            self.assertIn('path', skill)

    def test_skills_list_human_output_exposes_validation(self):
        """
            Verify that the human-readable skills list output includes discovery confirmation and a validation replay command.
            """
        cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / 'bin' / 'ask'), 'skills', 'list', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Discovered', result.stdout)
        self.assertIn('Validation: ./bin/ask skills list --json --robot', result.stdout)

    def test_skills_list_advanced_flag(self):
        """CA1: Verify ask skills list --advanced remains a full-inventory compatibility alias."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'list', '--advanced', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data'].get('advanced_mode'))
        self.assertEqual(output['data'].get('inventory_mode'), 'repo')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills list --advanced --json --robot'])

    def test_skills_list_visible_only_flag(self):
        """Verify ask skills list --visible-only exposes the narrower visible inventory."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'list', '--visible-only', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertFalse(output['data'].get('advanced_mode'))
        self.assertEqual(output['data'].get('inventory_mode'), 'visible')
        self.assertTrue(output['data'].get('visible_only'))
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills list --visible-only --json --robot'])

    def test_skills_list_visible_only_wins_over_advanced_alias(self):
        """Verify mixed compatibility flags report one coherent visible inventory."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'list', '--advanced', '--visible-only', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertFalse(output['data'].get('advanced_mode'))
        self.assertEqual(output['data'].get('inventory_mode'), 'visible')
        self.assertTrue(output['data'].get('visible_only'))
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills list --visible-only --json --robot'])

    def test_skills_budget_json_contract(self):
        """Verify ask skills budget exposes the runtime-budget validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'budget', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        budget = output['data']['runtime_budget']
        self.assertEqual(budget['status'], 'pass')
        self.assertEqual(budget['validation_commands'], ['./bin/ask skills budget --json --robot'])

    def test_skills_budget_human_output_exposes_validation(self):
        """Verify ask skills budget renders its validation command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'budget', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Runtime budget:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills budget --json --robot', result.stdout)

    def test_skills_route_json_contract(self):
        """CA1: Verify ask skills route exposes selection-decision fields."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'route', 'create-auth', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f'Expected JSON output, stderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertIn('status', output)
        self.assertIn('data', output)
        self.assertIn('decision', output['data'])
        decision = output['data']['decision']
        self.assertIn('decision_status', decision)
        self.assertIn('policy_identity', decision)
        self.assertIn('considered_limit', decision)
        self.assertIn('selected_candidates', decision)
        self.assertEqual(decision.get('validation_commands'), ['./bin/ask skills route create-auth --json --robot'])

    def test_skills_route_human_output_exposes_validation(self):
        """Verify ambiguous route output renders the route validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'route', 'help me', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('🧭 Route decision:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills route', result.stdout)
        self.assertIn('--json --robot', result.stdout)

    def test_skills_list_json_contract(self):
        """Verify ask skills list exposes the SDK target inventory contract."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'list', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        skills = output['data']['skills']
        self.assertGreater(len(skills), 0)
        self.assertIn('name', skills[0])
        self.assertIn('path', skills[0])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills list --json --robot'])

    def test_skills_list_human_output_includes_inventory_entries(self):
        """Verify ask skills list renders inventory entries."""
        cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / 'bin' / 'ask'), 'skills', 'list', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Discovered', result.stdout)
        self.assertIn('autofix', result.stdout)

    def test_skills_removed_projection_flags_fail_closed(self):
        """Verify removed projection flags direct callers to current skill sync/list surfaces."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'handles', '--write-projection', '--dry-run', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_INVALID_PROJECTION_MODE')
        self.assertIn('skills sync --scope workspace --projection flat', output['errors'][0]['fix_suggestion'])
        self.assertIn('skills list --json --robot', output['errors'][0]['fix_suggestion'])

    def test_skills_resolve_json_contract(self):
        """Verify ask skills resolve returns the canonical source for a source-path target."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'resolve', 'Skills/agent-ops/autofix', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output['data']['resolution']
        self.assertEqual(resolution['status'], 'ok')
        self.assertEqual(resolution['handle'], 'autofix')
        self.assertEqual(resolution['source_path'], 'Skills/agent-ops/autofix/SKILL.md')
        self.assertEqual(resolution['requested_handle'], 'Skills/agent-ops/autofix')
        self.assertEqual(resolution['alias_resolution'], 'autofix')
        self.assertEqual(resolution['validation_commands'], ['./bin/ask skills resolve autofix --json --robot'])

    def test_skills_resolve_human_output_exposes_validation(self):
        """Verify ask skills resolve renders its validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'resolve', 'Skills/agent-ops/autofix', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Skill target: autofix', result.stdout)
        self.assertIn('Validation: ./bin/ask skills resolve autofix --json --robot', result.stdout)

    def test_skills_parse_json_contract(self):
        """Verify ask skills parse reports resolved mentions and its validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'parse', 'use $simplify and $autofix', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        parsed = output['data']['parse']
        self.assertEqual(parsed['status'], 'pass')
        self.assertEqual(parsed['mention_counts']['skills'], 2)
        self.assertEqual(parsed['validation_commands'], ["./bin/ask skills parse 'use $simplify and $autofix' --json --robot"])

    def test_skills_parse_human_output_exposes_validation(self):
        """Verify ask skills parse renders its validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'parse', 'use $simplify and $autofix', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Parse succeeded: pass', result.stdout)
        self.assertIn('Skill mentions: 2', result.stdout)
        self.assertIn('Validation: ./bin/ask skills parse', result.stdout)
        self.assertIn('--json --robot', result.stdout)

    def test_skills_proof_json_contract(self):
        """Verify ask skills proof separates resolver, canonical source, and runtime-link gates."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'proof', 'Skills/agent-ops/autofix', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        proof = output['data']['proof']
        self.assertEqual(proof['schema_version'], 'sdk-skill-proof.v1')
        self.assertEqual(proof['handle'], 'autofix')
        self.assertIn('resolver', proof['gates'])
        self.assertIn('canonical_source_exists', proof['gates'])
        self.assertIn('codex_user_link', proof['gates'])
        self.assertIn('user_runtime_ready', proof['gates'])
        self.assertIn('user_runtime_ready', proof['gate_policy']['required'])
        self.assertIn('either supported user runtime link', proof['gate_policy']['required_semantics'])
        self.assertIn('codex_user_link', proof['gate_policy']['supporting_runtime_diagnostics'])
        self.assertIn('agents_user_link', proof['gate_policy']['supporting_runtime_diagnostics'])
        self.assertEqual(proof['validation_commands'], ['./bin/ask skills proof autofix --json --robot'])
        if proof.get('status') == 'pass':
            self.assertEqual(proof['live_runtime_invocation']['status'], 'manual_session_gate')
        else:
            self.assertNotIn('live_runtime_invocation', proof)

    def test_skills_proof_human_output(self):
        """Verify ask skills proof has a useful non-JSON success render."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'proof', 'Skills/agent-ops/autofix']
        result = _run_cli(cmd)
        if result.returncode == 0:
            self.assertIn('Skill target proof: autofix', result.stdout)
            self.assertIn('required gates: resolver, canonical_source_exists, direct_runtime_projection, user_runtime_ready', result.stdout)
            self.assertIn('Validation: ./bin/ask skills proof autofix --json --robot', result.stdout)
            if 'runtime satisfied by:' in result.stdout:
                self.assertRegex(result.stdout, 'runtime satisfied by: (codex_user_runtime|agents_user_runtime)')
            if 'live invocation:' in result.stdout:
                self.assertIn('live invocation: manual_session_gate', result.stdout)
        elif result.returncode == 2:
            self.assertRegex(result.stdout, "SDK skill proof failed for 'autofix'")
        else:
            self.fail(f'Unexpected return code {result.returncode}, stderr: {result.stderr}')

    def test_skills_prove_json_contract(self):
        """Verify ask skills prove keeps its three user-facing truths compact."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'Skills/agent-ops/autofix', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), result.stderr)
        self.assertLess(len(result.stdout.encode('utf-8')), 10 * 1024)
        output = json.loads(result.stdout)
        skill_proof = output['data']['skill_proof']
        self.assertEqual(skill_proof['schema_version'], 'skill-proof-scorecard.v1')
        self.assertEqual(skill_proof['handle'], 'autofix')
        self.assertIn('runtime_reachability', skill_proof)
        self.assertIn('structural_quality', skill_proof)
        self.assertIn('outcome_proof', skill_proof)
        self.assertIn('claims_boundary', skill_proof)
        self.assertNotIn('sdk_skill_proof', output['data'])

    def test_skills_prove_reachability_blocker_names_a_non_repeating_preview(self):
        """Verify a blocked proof points to the prerequisite instead of itself."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'simplify', '--json', '--robot']
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env['HOME'] = temp_dir
            result = _run_cli(cmd, env=env)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output['data']['skill_proof']
        self.assertEqual(skill_proof['proof_status'], 'blocked_reachability')
        self.assertEqual(skill_proof['next_command'], './bin/ask skills sync --scope user --projection flat --dry-run --json --robot')

    def test_skills_prove_human_output(self):
        """Verify ask skills prove renders the scorecard in non-JSON mode."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'Skills/agent-ops/autofix', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, result.stderr)
        if result.returncode == 0:
            self.assertIn('Skill proof scorecard: $autofix', result.stdout)
            self.assertRegex(result.stdout, 'reachability: (pass|fail)')
            self.assertIn('structural_quality: pass', result.stdout)
            self.assertIn('analytics: unavailable_or_legacy', result.stdout)
            self.assertIn('outcome_proof: missing', result.stdout)
            self.assertIn('Next:', result.stdout)
        else:
            self.assertIn("SDK skill proof failed for 'autofix'.", result.stdout)
            self.assertIn('skills sync --scope user --projection flat --dry-run', result.stdout)

    def test_skills_prove_maps_golden_path_taxonomy_for_current_target(self):
        """Verify prove exposes the stable proof taxonomy without adding schemas."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'Skills/agent-ops/autofix', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output['data']['skill_proof']
        self.assertEqual(skill_proof['schema_version'], 'skill-proof-scorecard.v1')
        self.assertEqual(skill_proof['handle'], 'autofix')
        self.assertIn(skill_proof['runtime_reachability']['status'], {'pass', 'fail'})
        self.assertEqual(skill_proof['structural_quality']['status'], 'pass')
        self.assertEqual(skill_proof['outcome_proof']['evidence_class'], 'outcome_proof')
        self.assertIn(skill_proof['proof_status'], {'blocked_reachability', 'reachable_without_outcome_proof', 'pass'})
        self.assertNotIn('sdk_skill_proof', output['data'])

    def test_skills_prove_keeps_compact_invocation_summary(self):
        """Verify compact prove output keeps the bounded analytics summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, 'telemetry')
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, 'skill-invocations.jsonl'), 'w', encoding='utf-8') as handle:
                handle.write(json.dumps({'skill_id': 'autofix', 'plugin_id': 'harness-engineering', 'turn_id_hash': 'turn_123', 'thread_id_hash': 'thread_123', 'invoke_type': 'skill', 'scope': 'workspace', 'model_slug': 'gpt-5.3-codex', 'product_client_id_hash': 'client_123', 'repository_hash': 'repo_123', 'timestamp': '2026-05-07T10:00:00Z'}, sort_keys=True) + '\n')
            env = os.environ.copy()
            env['SKILL_TELEMETRY_DIR'] = telemetry_dir
            cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'autofix', '--json']
            result = _run_cli(cmd, env=env)
        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        analytics = output['data']['skill_proof']['analytics']
        self.assertEqual(analytics['status'], 'available')
        self.assertEqual(analytics['matching_invocation_count'], 1)

    def test_skills_prove_reports_projection_parse_warning(self):
        """Verify ask skills prove preserves valid projection rows with parse warnings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, 'telemetry')
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, 'skill-invocations.jsonl'), 'w', encoding='utf-8') as handle:
                handle.write('{not-json\n')
                handle.write(json.dumps({'skill_id': 'other-skill', 'timestamp': '2026-05-07T10:00:00Z'}) + '\n')
            with mock.patch.dict(os.environ, {'SKILL_TELEMETRY_DIR': telemetry_dir}):
                lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
                sys.path.insert(0, lib_path)
                try:
                    from ask.skill_analytics import skill_invocation_analytics
                    analytics = skill_invocation_analytics(Path.cwd(), 'autofix')
                finally:
                    sys.path.remove(lib_path)
        self.assertEqual(analytics['status'], 'parse_warning')
        self.assertEqual(analytics['invocation_count'], 1)
        self.assertEqual(analytics['matching_invocation_count'], 0)
        self.assertEqual(analytics['parse_error_count'], 1)

    def test_skills_prove_keeps_compact_parse_warning_summary(self):
        """Verify compact prove output preserves the parse-warning classification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, 'telemetry')
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, 'skill-invocations.jsonl'), 'w', encoding='utf-8') as handle:
                handle.write('{not-json\n')
                handle.write(json.dumps({'skill_id': 'autofix', 'timestamp': '2026-05-07T10:00:00Z'}) + '\n')
            env = os.environ.copy()
            env['SKILL_TELEMETRY_DIR'] = telemetry_dir
            cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'autofix', '--json']
            result = _run_cli(cmd, env=env)
        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        analytics = output['data']['skill_proof']['analytics']
        self.assertEqual(analytics['status'], 'parse_warning')
        self.assertEqual(analytics['parse_error_count'], 1)

    def test_skill_invocation_analytics_relative_override_uses_repo_root(self):
        """Verify relative telemetry overrides are anchored to the repository root."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask import skill_analytics
            repo_root = Path('/tmp/agent-skills-repo')
            with mock.patch.dict(os.environ, {'SKILL_TELEMETRY_DIR': 'generated/telemetry'}):
                telemetry_dir = skill_analytics.skill_telemetry_dir(repo_root)
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(telemetry_dir, repo_root / 'generated' / 'telemetry')

    def test_skill_invocation_analytics_handles_projection_read_errors(self):
        """Verify projection read errors return an unavailable summary."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask import skill_analytics
            with tempfile.TemporaryDirectory() as temp_dir:
                telemetry_dir = Path(temp_dir) / 'telemetry'
                telemetry_dir.mkdir(parents=True)
                projection = telemetry_dir / 'skill-invocations.jsonl'
                projection.write_text('', encoding='utf-8')
                original_open = Path.open

                def selective_open(path_self, *args, **kwargs):
                    if path_self == projection:
                        raise PermissionError('permission denied')
                    return original_open(path_self, *args, **kwargs)
                with mock.patch.dict(os.environ, {'SKILL_TELEMETRY_DIR': str(telemetry_dir)}), mock.patch.object(Path, 'open', selective_open):
                    analytics = skill_analytics.skill_invocation_analytics(Path.cwd(), 'autofix')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(analytics['status'], 'unavailable_or_legacy')
        self.assertEqual(analytics['parse_error_count'], 1)
        self.assertIn('permission denied', analytics['parse_errors'][0]['message'])

    def test_skills_prove_goal_fallback_json_contract(self):
        """Verify ask skills prove routes or clearly blocks a goal query."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'fix', 'PR', 'review', 'comments', '--json']
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output['data']['skill_proof']
        self.assertEqual(skill_proof['schema_version'], 'skill-proof-scorecard.v1')
        self.assertEqual(skill_proof['query'], 'fix PR review comments')
        self.assertIn(skill_proof['proof_status'], ('blocked_goal_resolution', 'blocked_reachability', 'reachable_without_outcome_proof'))
        self.assertIn('goal_resolution', skill_proof)
        self.assertIn('recommended_capability', skill_proof['goal_resolution'])
        self.assertEqual(skill_proof['validation_commands'], [skill_proof['next_command']])

    def test_skills_prove_single_token_goal_uses_improve_fallback(self):
        """Verify one-word goals use the same improvement route as phrase goals."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            failed_reachability = CallResult(status='error')
            goal_result = CallResult()
            goal_result.data['improvement'] = {'recommended_capability': {'handle': 'security-reviewer'}, 'next_command': './bin/ask skills proof security-reviewer --json --robot'}
            reachable_result = CallResult()
            reachable_result.data['proof'] = {'status': 'pass', 'handle': 'security-reviewer', 'resolution': {'handle': 'security-reviewer', 'source_path': 'Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md'}}
            with mock.patch.object(skills_commands, 'skills_proof', side_effect=[failed_reachability, reachable_result]), mock.patch.object(skills_commands, 'improve_skills', return_value=goal_result) as improve_mock, mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()):
                result = skills_commands.skills_prove(Path.cwd(), 'security')
        finally:
            sys.path.remove(lib_path)
        improve_mock.assert_called_once()
        self.assertEqual(result.data['skill_proof']['handle'], 'security-reviewer')
        self.assertIn('goal_resolution', result.data['skill_proof'])
        self.assertEqual(result.data['skill_proof']['validation_commands'], [result.data['skill_proof']['next_command']])

    def test_skills_prove_goal_resolution_without_candidate_uses_improve_command(self):
        """Verify unresolved goals point back to the improve command."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult
            failed_reachability = CallResult(status='error')
            goal_result = CallResult()
            goal_result.data['improvement'] = {'recommended_capability': {}}
            with mock.patch.object(skills_commands, 'skills_proof', return_value=failed_reachability), mock.patch.object(skills_commands, 'improve_skills', return_value=goal_result):
                result = skills_commands.skills_prove(Path.cwd(), 'unknown goal')
        finally:
            sys.path.remove(lib_path)
        skill_proof = result.data['skill_proof']
        self.assertEqual(result.status, 'error')
        self.assertEqual(skill_proof['proof_status'], 'blocked_goal_resolution')
        self.assertEqual(skill_proof['next_command'], "./bin/ask skills improve 'unknown goal' --json --robot")
        self.assertEqual(skill_proof['validation_commands'], [skill_proof['next_command']])

    def test_skills_prove_resolved_handle_failure_does_not_use_goal_fallback(self):
        """Verify a resolved handle with broken reachability stays on the requested handle."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult, ErrorObject
            failed_reachability = CallResult(status='error')
            failed_reachability.data['proof'] = {'status': 'fail', 'handle': 'autofix', 'resolution': {'status': 'ok', 'handle': 'autofix', 'source_path': 'Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md'}}
            failed_reachability.errors.append(ErrorObject(code='ERR_VALIDATION', message='reachability failed'))
            with mock.patch.object(skills_commands, 'skills_proof', return_value=failed_reachability), mock.patch.object(skills_commands, 'improve_skills') as improve_mock, mock.patch.object(skills_commands, 'audit_skill', return_value=CallResult()), mock.patch.object(skills_commands, 'skill_invocation_analytics', return_value={'status': 'unavailable_or_legacy'}):
                result = skills_commands.skills_prove(Path.cwd(), 'autofix')
        finally:
            sys.path.remove(lib_path)
        improve_mock.assert_not_called()
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.data['skill_proof']['handle'], 'autofix')
        self.assertEqual(result.data['skill_proof']['proof_status'], 'blocked_reachability')
        self.assertEqual(result.data['skill_proof']['validation_commands'], [result.data['skill_proof']['next_command']])

    def test_skills_prove_human_output_exposes_validation(self):
        """Verify ask skills prove renders its scorecard validation command."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'prove', 'autofix', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills prove output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("SDK skill proof failed for 'autofix'.", result.stdout)
        self.assertIn('skills sync --scope user --projection flat --dry-run', result.stdout)

    def test_skills_prove_workout_candidates_require_explicit_metadata_match(self):
        """Verify workout outcome candidates are not inferred from directory names."""
        lib_path = str(Path.cwd() / 'Infrastructure' / 'scripts' / 'lib')
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills import _skill_workout_candidates
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                false_positive = repo_root / '.workouts' / 'autofix-but-not-referenced'
                false_positive.mkdir(parents=True)
                false_positive.joinpath('workout.yaml').write_text('id: unrelated\nskills:\n  - other-skill\n', encoding='utf-8')
                explicit_match = repo_root / '.workouts' / 'explicit-outcome'
                explicit_match.mkdir(parents=True)
                explicit_match.joinpath('workout.yaml').write_text('id: outcome\nskills:\n  - autofix\n', encoding='utf-8')
                target_module_match = repo_root / '.workouts' / 'target-module-outcome'
                target_module_match.mkdir(parents=True)
                target_module_match.joinpath('workout.yaml').write_text('id: outcome-target\ntarget_module: autofix\n', encoding='utf-8')
                candidates = _skill_workout_candidates(repo_root, 'autofix')
        finally:
            sys.path.remove(lib_path)
        self.assertEqual(candidates, ['explicit-outcome', 'target-module-outcome'])

__all__ = [name for name in globals() if not name.startswith("__")]
