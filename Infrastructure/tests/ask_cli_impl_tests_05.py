from ask_cli_impl_tests_04 import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_skills_memory_list_source_filter_limits_entries(self):
        """Verify ask skills memory list preserves provider source filtering."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'list', '--source', 'harness-solutions', '--limit', '2', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills memory list output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        memory = output['data']['skill_memory']
        self.assertEqual(memory['entry_count'], 2)
        self.assertGreaterEqual(memory['total_count'], 2)
        self.assertIn('./bin/ask skills memory search <query> --json --robot', memory['operation_context']['follow_up_commands'])
        self.assertTrue(all((entry['source_id'] == 'harness-solutions' for entry in memory['entries'])))

    def test_skills_memory_read_command_returns_content_and_provenance(self):
        """Verify ask skills memory read exposes durable content with provenance."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'read', '.harness/memory/LEARNINGS.md', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'skills memory read output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        memory = output['data']['skill_memory']
        self.assertEqual(memory['mode'], 'read')
        entry = memory['entry']
        self.assertEqual(entry['path'], '.harness/memory/LEARNINGS.md')
        self.assertEqual(entry['provenance']['provider'], 'harness-memory')
        self.assertIn('# Learnings', entry['content'])

    def test_skills_memory_read_command_blocks_missing_identifier(self):
        """Verify ask skills memory read fails closed without an entry id."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'memory', 'read', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'skills memory read output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        memory = output['data']['skill_memory']
        self.assertEqual(memory['status'], 'blocked')
        self.assertEqual(memory['mode'], 'read')
        self.assertIn('requires an entry id', memory['agent_summary'])

    def test_evals_missing_action_exposes_validation(self):
        """Verify incomplete eval commands expose the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'evals', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'evals output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask evals dashboard --json --robot'])

    def test_evals_missing_action_human_output_exposes_validation(self):
        """Verify incomplete eval commands render the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'evals', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'evals output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'evals'", result.stdout)
        self.assertIn('Validation: ./bin/ask evals dashboard --json --robot', result.stdout)

    def test_evals_closeout_doctor_human_output_renders_result(self):
        """Verify evals closeout doctor prints its non-JSON result."""
        with tempfile.TemporaryDirectory() as tmp:
            closeout_path = _write_pass_closeout(tmp)
            cmd = ['python3', 'Infrastructure/bin/ask', 'evals', 'closeout', 'doctor', str(closeout_path), '--robot']
            result = _run_cli(cmd, cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 0, f'closeout doctor output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Eval closeout doctor: pass', result.stdout)
        self.assertIn('Validation: pass', result.stdout)
        self.assertIn('Validation: ./bin/ask evals closeout doctor', result.stdout)

    def test_mcp_sync_dry_run_json_contract_exposes_validation(self):
        """Verify MCP sync dry-run exposes its replay command without writing config."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'mcp', 'sync', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'mcp sync output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data']['dry_run'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask mcp sync --dry-run --json --robot'])

    def test_mcp_sync_dry_run_human_output_exposes_validation(self):
        """Verify MCP sync dry-run human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'mcp', 'sync', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'mcp sync output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Dry run - would sync', result.stdout)
        self.assertIn('Validation: ./bin/ask mcp sync --dry-run --json --robot', result.stdout)

    def test_mcp_missing_action_exposes_validation(self):
        """Verify incomplete MCP commands expose the safe dry-run recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'mcp', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'mcp output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask mcp sync --dry-run --json --robot'])

    def test_mcp_missing_action_human_output_exposes_validation(self):
        """Verify incomplete MCP commands render the safe recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'mcp', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'mcp output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'mcp'", result.stdout)
        self.assertIn('Validation: ./bin/ask mcp sync --dry-run --json --robot', result.stdout)

    def test_wiki_lint_json_contract_exposes_validation(self):
        """Verify wiki lint exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'lint', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'wiki lint output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask wiki lint --wiki-root Wiki/wiki --max-age-days 60 --json --robot'])

    def test_wiki_lint_human_output_exposes_validation(self):
        """Verify wiki lint human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'lint', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'wiki lint output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Wiki lint passed.', result.stdout)
        self.assertIn('Validation: ./bin/ask wiki lint --wiki-root Wiki/wiki --max-age-days 60 --json --robot', result.stdout)

    def test_wiki_query_json_contract_exposes_validation(self):
        """Verify wiki query exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'query', 'skill', '--limit', '1', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'wiki query output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['query'], 'skill')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask wiki query skill --wiki-root Wiki/wiki --limit 1 --json --robot'])

    def test_wiki_query_human_output_exposes_validation(self):
        """Verify wiki query human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'query', 'skill', '--limit', '1', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'wiki query output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Found 1 matching wiki page(s).', result.stdout)
        self.assertIn('Validation: ./bin/ask wiki query skill --wiki-root Wiki/wiki --limit 1 --json --robot', result.stdout)

    def test_wiki_ingest_dry_run_json_contract_exposes_validation(self):
        """Verify wiki ingest dry-run exposes its replay command without writing."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'ingest', 'Capability Readiness Note', '--source', 'heartbeat:test', '--summary', 'Dry-run readiness evidence for wiki ingest.', '--tag', 'readiness', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'wiki ingest output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data']['dry_run'])
        self.assertEqual(output['data']['validation_commands'], ["./bin/ask wiki ingest 'Capability Readiness Note' --source heartbeat:test --summary 'Dry-run readiness evidence for wiki ingest.' --tag readiness --dry-run --json --robot"])

    def test_wiki_ingest_dry_run_human_output_exposes_validation(self):
        """Verify wiki ingest dry-run human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'ingest', 'Capability Readiness Note', '--source', 'heartbeat:test', '--summary', 'Dry-run readiness evidence for wiki ingest.', '--tag', 'readiness', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'wiki ingest output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Dry run - would ingest:', result.stdout)
        self.assertIn("Validation: ./bin/ask wiki ingest 'Capability Readiness Note' --source heartbeat:test --summary 'Dry-run readiness evidence for wiki ingest.' --tag readiness --dry-run --json --robot", result.stdout)

    def test_wiki_add_json_contract_exposes_validation(self):
        """Verify wiki add exposes its replay command even when dependencies block."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add', 'Capability Readiness Finding', '--summary', 'Dry-run readiness evidence for wiki add.', '--source', 'heartbeat:test', '--intent', 'finding', '--status', 'needs-verification', '--destination', 'failures', '--tag', 'readiness', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'wiki add output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['data']['validation_commands'], ["./bin/ask wiki add 'Capability Readiness Finding' --summary 'Dry-run readiness evidence for wiki add.' --source heartbeat:test --intent finding --status needs-verification --destination failures --tag readiness --dry-run --json --robot"])

    def test_wiki_add_human_output_exposes_validation(self):
        """Verify wiki add human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add', 'Capability Readiness Finding', '--summary', 'Dry-run readiness evidence for wiki add.', '--source', 'heartbeat:test', '--intent', 'finding', '--status', 'needs-verification', '--destination', 'failures', '--tag', 'readiness', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'wiki add output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("Validation: ./bin/ask wiki add 'Capability Readiness Finding' --summary 'Dry-run readiness evidence for wiki add.' --source heartbeat:test --intent finding --status needs-verification --destination failures --tag readiness --dry-run --json --robot", result.stdout)

    def test_wiki_add_asset_json_contract_exposes_validation(self):
        """Verify wiki add-asset exposes its replay command even when dependencies block."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add-asset', 'Wiki/wiki/playbooks/code-scanning-remediation.md', '--title', 'Capability Readiness Asset', '--summary', 'Dry-run readiness evidence for wiki asset add.', '--source', 'heartbeat:test', '--status', 'verified', '--destination', 'assets/ui', '--tag', 'readiness', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'wiki add-asset output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['data']['validation_commands'], ["./bin/ask wiki add-asset Wiki/wiki/playbooks/code-scanning-remediation.md --title 'Capability Readiness Asset' --summary 'Dry-run readiness evidence for wiki asset add.' --source heartbeat:test --status verified --destination assets/ui --tag readiness --dry-run --json --robot"])

    def test_wiki_add_asset_human_output_exposes_validation(self):
        """Verify wiki add-asset human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add-asset', 'Wiki/wiki/playbooks/code-scanning-remediation.md', '--title', 'Capability Readiness Asset', '--summary', 'Dry-run readiness evidence for wiki asset add.', '--source', 'heartbeat:test', '--status', 'verified', '--destination', 'assets/ui', '--tag', 'readiness', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'wiki add-asset output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("Validation: ./bin/ask wiki add-asset Wiki/wiki/playbooks/code-scanning-remediation.md --title 'Capability Readiness Asset' --summary 'Dry-run readiness evidence for wiki asset add.' --source heartbeat:test --status verified --destination assets/ui --tag readiness --dry-run --json --robot", result.stdout)

    def test_wiki_add_missing_fields_json_contract_exposes_validation(self):
        """Verify wiki add missing-field errors expose their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'wiki add output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIn('Missing required fields for wiki add', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask wiki add --json --robot'])

    def test_wiki_add_missing_fields_human_output_exposes_validation(self):
        """Verify wiki add missing-field human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'wiki add output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Missing required fields for wiki add', result.stdout)
        self.assertIn('Validation: ./bin/ask wiki add --json --robot', result.stdout)

    def test_wiki_add_asset_missing_fields_json_contract_exposes_validation(self):
        """Verify wiki add-asset missing-field errors expose their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add-asset', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'wiki add-asset output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertIn('Missing required fields for wiki add-asset', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask wiki add-asset --status verified --destination assets/ui --json --robot'])

    def test_wiki_add_asset_missing_fields_human_output_exposes_validation(self):
        """Verify wiki add-asset missing-field human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', 'add-asset', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'wiki add-asset output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Missing required fields for wiki add-asset', result.stdout)
        self.assertIn('Validation: ./bin/ask wiki add-asset --status verified --destination assets/ui --json --robot', result.stdout)

    def test_wiki_missing_action_exposes_validation(self):
        """Verify incomplete wiki commands expose the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'wiki output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask wiki lint --json --robot'])

    def test_wiki_missing_action_human_output_exposes_validation(self):
        """Verify incomplete wiki commands render the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'wiki', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'wiki output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'wiki'", result.stdout)
        self.assertIn('Validation: ./bin/ask wiki lint --json --robot', result.stdout)

    def test_memory_search_command_returns_provider_entries(self):
        """Verify ask memory search exposes the same provenance-bearing provider entries."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', 'search', 'projection', '--limit', '1', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'memory search failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        memory = output['data']['memory']
        self.assertEqual(memory['schema_version'], 'memory-provider.v1')
        self.assertEqual(memory['count'], 1)
        entry = memory['results'][0]
        self.assertEqual(entry['provenance']['provider'], entry['source_id'])
        self.assertEqual(entry['provenance']['repo_relative_path'], entry['path'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask memory search projection --limit 1 --json --robot'])

    def test_memory_search_human_output_lists_entry_paths(self):
        """Verify ask memory search has a useful non-JSON provider render."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', 'search', 'projection', '--limit', '1', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'memory output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn('Found 1 memory entry.', result.stdout)
        self.assertIn('docs-agent-guidance:docs-agents-04-validation-md', result.stdout)
        self.assertIn('Docs/agents/04-validation.md', result.stdout)
        self.assertIn('Validation: ./bin/ask memory search projection --limit 1 --json --robot', result.stdout)

    def test_memory_list_source_filter_limits_entries(self):
        """Verify ask memory list honors source filtering from the CLI path."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', 'list', '--source', 'harness-solutions', '--limit', '2', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'memory list output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        memory = output['data']['memory']
        self.assertEqual(memory['count'], 2)
        self.assertGreaterEqual(memory['total_count'], 2)
        self.assertTrue(all((entry['source_id'] == 'harness-solutions' for entry in memory['entries'])))
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask memory list --source harness-solutions --limit 2 --json --robot'])

    def test_memory_list_command_blocks_negative_limit(self):
        """Verify ask memory list rejects negative limits."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', 'list', '--limit', '-1', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'memory list output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('limit must be non-negative', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask memory list --limit -1 --json --robot'])

    def test_memory_read_command_returns_content_and_provenance(self):
        """Verify ask memory read exposes durable content with provenance."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', 'read', '.harness/memory/LEARNINGS.md', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'memory read output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        memory = output['data']['memory']
        entry = memory['entry']
        self.assertEqual(entry['path'], '.harness/memory/LEARNINGS.md')
        self.assertEqual(entry['provenance']['provider'], 'harness-memory')
        self.assertIn('# Learnings', entry['content'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask memory read .harness/memory/LEARNINGS.md --json --robot'])

    def test_memory_read_command_blocks_missing_identifier(self):
        """Verify ask memory read parser reports the missing identifier clearly."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', 'read', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'memory read output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('arguments are required: identifier', output['errors'][0]['message'])
        self.assertIn('ask memory read .harness/memory/LEARNINGS.md --json', output['errors'][0]['message'])

    def test_memory_command_blocks_missing_action(self):
        """Verify ask memory fails closed when no provider mode is selected."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'memory output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask memory list --json --robot'])

    def test_memory_missing_action_human_output_exposes_validation(self):
        """Verify incomplete memory commands render the recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'memory', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'memory output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'memory'", result.stdout)
        self.assertIn('Validation: ./bin/ask memory list --json --robot', result.stdout)

    def test_plugins_list_state(self):
        """CA1: Verify ask plugins list returns lifecycle state groups."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'list', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins list failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertIn('installed_state', output['data'])
        self.assertIn('activation_state', output['data'])
        self.assertIn('health_state', output['data'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins list --json --robot'])

    def test_plugins_list_human_output_exposes_validation(self):
        """Verify plugins list human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'list', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins list failed: {result.stderr}')
        self.assertIn('Plugins installed:', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins list --json --robot', result.stdout)

    def test_plugins_missing_action_exposes_validation(self):
        """Verify incomplete plugin commands expose the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'plugins output: {result.stdout}\nstderr: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertIn('missing action', output['errors'][0]['message'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins list --json --robot'])

    def test_plugins_missing_action_human_output_exposes_validation(self):
        """Verify incomplete plugin commands render the read-only recovery command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, f'plugins output: {result.stdout}\nstderr: {result.stderr}')
        self.assertIn("missing action for topic 'plugins'", result.stdout)
        self.assertIn('Validation: ./bin/ask plugins list --json --robot', result.stdout)

    def test_plugins_status_json_contract_exposes_validation(self):
        """Verify plugin status exposes its scoped replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'status', 'harness-engineering', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins status failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins status harness-engineering --json --robot'])

    def test_plugins_doctor_json_contract_exposes_validation(self):
        """Verify plugin doctor exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'doctor', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertIn(result.returncode, {0, 2}, f'plugins doctor failed: {result.stderr}')
        output = json.loads(result.stdout)
        if result.returncode == 0:
            self.assertEqual(output['status'], 'success')
            self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins doctor --json --robot'])
        else:
            self.assertEqual(output['status'], 'error')

    def test_plugins_sync_local_runtime_dry_run_exposes_validation(self):
        """Verify plugin runtime sync dry-run exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'sync-local-runtime', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins sync-local-runtime failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data']['dry_run'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins sync-local-runtime --dry-run --json --robot'])

    def test_plugins_sync_local_runtime_human_output_exposes_validation(self):
        """Verify plugin runtime sync dry-run human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'sync-local-runtime', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins sync-local-runtime failed: {result.stderr}')
        self.assertIn('Dry run - would replace local-plugin runtime mirrors', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins sync-local-runtime --dry-run --json --robot', result.stdout)

    def test_plugins_harden_success_human_output_exposes_validation(self):
        """Verify plugin harden success output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'harden', 'Plugins/harness-engineering', '--skip-compat', '--skip-marketplace-audit', '--no-require-marketplace', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins harden failed: {result.stderr}')
        self.assertIn("Hardened plugin 'harness-engineering'", result.stdout)
        self.assertIn('Checks run:', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins harden Plugins/harness-engineering --skip-compat --skip-marketplace-audit --no-require-marketplace --json --robot', result.stdout)

    def test_plugins_install_dry_run_human_output_exposes_validation(self):
        """Verify plugin install dry-run human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'install', 'https://github.com/example/repo', '--path', 'Plugins/demo-plugin', '--name', 'demo-plugin', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins install dry-run failed: {result.stderr}')
        self.assertIn('Dry run - would install plugin', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins install https://github.com/example/repo --path Plugins/demo-plugin --name demo-plugin --dry-run --json --robot', result.stdout)

    def test_plugins_install_validation_error_exposes_validation(self):
        """Verify plugin install validation errors expose a replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'install', 'https://github.com/example/repo', '--path', 'Plugins/demo-plugin', '--dest', '/tmp/not-a-plugin-dest', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins install https://github.com/example/repo --path Plugins/demo-plugin --dest /tmp/not-a-plugin-dest --json --robot'])

    def test_plugins_install_validation_error_human_output_exposes_validation(self):
        """Verify plugin install validation errors render their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'install', 'https://github.com/example/repo', '--path', 'Plugins/demo-plugin', '--dest', '/tmp/not-a-plugin-dest', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Invalid plugin destination', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins install https://github.com/example/repo --path Plugins/demo-plugin --dest /tmp/not-a-plugin-dest --json --robot', result.stdout)

    def test_plugins_uninstall_dry_run_json_contract_exposes_validation(self):
        """Verify plugin uninstall dry-run exposes its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'uninstall', 'harness-engineering', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins uninstall dry-run failed: {result.stderr}')
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertTrue(output['data']['dry_run'])
        self.assertEqual(output['data']['plugin_name'], 'harness-engineering')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins uninstall harness-engineering --dry-run --json --robot'])

    def test_plugins_uninstall_dry_run_human_output_exposes_validation(self):
        """Verify plugin uninstall dry-run human output names its replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'uninstall', 'harness-engineering', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f'plugins uninstall dry-run failed: {result.stderr}')
        self.assertIn('Dry run - would uninstall plugin', result.stdout)
        self.assertIn('Name: harness-engineering', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins uninstall harness-engineering --dry-run --json --robot', result.stdout)

    def test_plugins_uninstall_missing_plugin_exposes_validation(self):
        """Verify plugin uninstall missing-plugin errors expose a replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'uninstall', 'not-a-real-plugin', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins uninstall not-a-real-plugin --dry-run --json --robot'])

    def test_plugins_uninstall_missing_plugin_human_output_exposes_validation(self):
        """Verify plugin uninstall missing-plugin errors render their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'uninstall', 'not-a-real-plugin', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Plugin 'not-a-real-plugin' not found under Plugins/.", result.stdout)
        self.assertIn('Validation: ./bin/ask plugins uninstall not-a-real-plugin --dry-run --json --robot', result.stdout)

    def test_skills_sync_dry_run(self):
        """CA2: Verify ask skills sync --dry-run returns a plan without changes."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'sync', '--dry-run', '--json']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'success')
        self.assertIn('plan', output['data'])
        self.assertIn('symlinks', output['data']['plan'])
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills sync --dry-run --json --robot'])

    def test_skills_user_sync_defaults_to_links_only(self):
        """User sync must not refresh plugin mirrors without an explicit full mode."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'user', '--dry-run', '--json', '--robot']
        with tempfile.TemporaryDirectory() as home:
            result = _run_cli(cmd, env={**os.environ, 'HOME': home})
            self.assertFalse((Path(home) / '.agents').exists())
            self.assertFalse((Path(home) / '.codex').exists())
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        plan = output['data']['plan']
        self.assertEqual(plan['user_sync_mode'], 'links-only')
        self.assertNotIn('runtime_plugin_mirrors', plan)
        self.assertEqual(plan['mutation_counts']['writes'], 0)
        self.assertEqual(plan['mutation_counts']['deletes'], 0)
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills sync --scope user --dry-run --user-sync-mode links-only --json --robot'])

    def test_skills_user_sync_full_mode_keeps_plugin_mirror_route_explicit(self):
        """The legacy plugin-mirror route remains available only with explicit full mode."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'user', '--user-sync-mode', 'full', '--dry-run', '--json', '--robot']
        with tempfile.TemporaryDirectory() as home:
            result = _run_cli(cmd, env={**os.environ, 'HOME': home})
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        plan = output['data']['plan']
        self.assertEqual(plan['user_sync_mode'], 'full')
        self.assertIn('runtime_plugin_mirrors', plan)
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills sync --scope user --dry-run --user-sync-mode full --json --robot'])

    def test_skills_workspace_sync_preserves_full_sync_contract(self):
        """Workspace sync must not inherit the user-only links-only default."""
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'workspace', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['data']['plan']['user_sync_mode'], 'full')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask skills sync --dry-run --json --robot'])

    def test_skills_workspace_sync_rejects_user_only_links_mode(self):
        cmd = [sys.executable, 'Infrastructure/bin/ask', 'skills', 'sync', '--scope', 'workspace', '--user-sync-mode', 'links-only', '--dry-run', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['errors'][0]['code'], 'ERR_INVALID_SCOPE')
        self.assertIn('only with --scope user', output['errors'][0]['message'])

    def test_skills_sync_human_output_exposes_validation(self):
        """Verify ask skills sync renders its validation command in dry-run mode."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'skills', 'sync', '--dry-run', '--robot']
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Planned sync:', result.stdout)
        self.assertIn('Validation: ./bin/ask skills sync --dry-run --json --robot', result.stdout)

    def test_runtime_surface_json_contract(self):
        """Verify ask runtime surface exposes the runtime report under an obvious topic."""
        saved_projection_mode = os.environ.get('SYNC_SKILLS_PROJECTION_MODE')
        try:
            os.environ['SYNC_SKILLS_PROJECTION_MODE'] = 'flat'
            cmd = ['python3', 'Infrastructure/bin/ask', 'runtime', 'surface', '--json']
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output['status'], 'success')
            report = output['data']['runtime_surface']
            self.assertIn(report['projection_mode'], {'flat', 'rooted'})
            self.assertIn('first_level_default_entries', report)
            self.assertIn('hidden_system_entries', report)
            self.assertIn('estimated_description_tokens', report)
            self.assertEqual(output['data']['validation_commands'], ['./bin/ask runtime surface --json --robot'])
        finally:
            if saved_projection_mode is None:
                os.environ.pop('SYNC_SKILLS_PROJECTION_MODE', None)
            else:
                os.environ['SYNC_SKILLS_PROJECTION_MODE'] = saved_projection_mode

    def test_runtime_surface_human_output_exposes_validation(self):
        """Verify ask runtime surface renders its runtime replay command."""
        saved_projection_mode = os.environ.get('SYNC_SKILLS_PROJECTION_MODE')
        try:
            os.environ['SYNC_SKILLS_PROJECTION_MODE'] = 'flat'
            cmd = ['python3', 'Infrastructure/bin/ask', 'runtime', 'surface', '--robot']
            result = _run_cli(cmd)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Runtime surface:', result.stdout)
            self.assertIn('Validation: ./bin/ask runtime surface --json --robot', result.stdout)
        finally:
            if saved_projection_mode is None:
                os.environ.pop('SYNC_SKILLS_PROJECTION_MODE', None)
            else:
                os.environ['SYNC_SKILLS_PROJECTION_MODE'] = saved_projection_mode

__all__ = [name for name in globals() if not name.startswith("__")]
