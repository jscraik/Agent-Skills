import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ask_skills_package_contract_tests_core import (
    REPO_ROOT,
    _AskSkillsPackageContractBase,
    _validate_schema_subset,
)
from ask.commands.skills_impl import skills_package
from ask.skills_sdk import package_contracts
from ask.skills_sdk.contracts import read_skill_frontmatter_fields


def _assert_sdk_package_contract(case, sdk_contract: dict[str, object]) -> None:
    values = sdk_contract['values']
    disclosure = sdk_contract['progressive_disclosure']
    required = {
        'agent_metadata', 'reference_contract', 'reference_quality', 'writing_quality',
        'openai_platform_compat', 'purpose', 'inputs', 'outputs', 'commands',
        'permission_profile', 'evals', 'task_profile', 'evidence_policy',
    }
    case.assertEqual(sdk_contract['schema_version'], 'skill-sdk-contract.v1')
    case.assertTrue(required <= set(sdk_contract['required_fields']['present']))
    case.assertEqual(values['agent_metadata']['path'], 'Plugins/skill-factory/skills/skill-factory-router/agents/openai.yaml')
    case.assertEqual(values['reference_contract']['path'], 'Plugins/skill-factory/skills/skill-factory-router/references/contract.yaml')
    for key in ('reference_quality', 'writing_quality', 'openai_platform_compat'):
        case.assertEqual(values[key]['status'], 'pass')
        case.assertTrue(values[key]['required_for_package_readiness'])
        case.assertFalse(values[key]['blockers'])
    case.assertEqual(disclosure['references_quality_status'], 'pass')
    case.assertEqual(disclosure['writing_quality_status'], 'pass')
    case.assertEqual(disclosure['openai_platform_compat_status'], 'pass')
    case.assertTrue(values['evals']['declared'])
    case.assertIn('Plugins/skill-factory/skills/skill-factory-router/references/evals.yaml', values['evals']['paths'])
    providers = sdk_contract['evidence_providers']
    case.assertEqual([item['name'] for item in providers['providers']], ['otel_collector', 'session_collector', 'observability_stack'])
    case.assertTrue(all(item['root'].startswith('~/.agents/') for item in providers['providers']))


class TestAskSkillsPackageContract(_AskSkillsPackageContractBase):
    def test_source_operating_model_parser_resets_incomplete_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_context = Path(temp_dir) / 'source-context.yaml'
            source_context.write_text(
                'references:\n  - path: references/incomplete.md\n'
                '  - kind: source_operating_model\n', encoding='utf-8'
            )
            paths = package_contracts._source_operating_model_paths_from_text(source_context)
        self.assertEqual(paths, [])

    def test_package_contract_logic_lives_in_skills_sdk_service(self) -> None:
        command_source = (REPO_ROOT / 'Infrastructure/scripts/lib/ask/commands/skills_impl.py').read_text(encoding='utf-8')
        service_source = (REPO_ROOT / 'Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py').read_text(encoding='utf-8')
        self.assertEqual(package_contracts.skill_package_contract.__module__, 'ask.skills_sdk.package_contracts')
        self.assertNotIn('def _skill_package_contract', command_source)
        self.assertNotIn('ask.commands', service_source)
        self.assertNotIn('CallResult', service_source)
        self.assertNotIn('ErrorObject', service_source)
        self.assertIn('def skill_package_contract', service_source)

    def test_skill_package_schema_accepts_codex_metadata_contract(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        contract = package['skill_package_contract']
        _validate_schema_subset(self.schemas['skill-package.v1.schema.json'], contract, self.schemas)
        self.assertEqual(contract['schema_version'], 'skill-package.v1')
        self.assertEqual(contract['required_fields']['missing'], [])
        self.assertEqual(contract['compatibility_status'], 'compatible')
        self.assertEqual(contract['metadata']['name'], 'skill-factory-router')
        self.assertEqual(contract['codex_abi_source']['path'], 'codex-rs/core-skills/src/model.rs')
        self.assertFalse(Path(contract['codex_abi_source']['path']).is_absolute())
        self.assertIn('interface', contract['optional_fields']['present'])
        self.assertEqual(contract['metadata']['interface']['display_name'], 'Skill Factory Router')

    def test_skill_package_contract_merges_agents_openai_policy_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'codex-package'
            agents_dir = skill_dir / 'agents'
            agents_dir.mkdir(parents=True)
            (skill_dir / 'SKILL.md').write_text('---\nname: codex-package\ndescription: Codex package metadata fixture.\ndependencies:\n  frontmatter_tool: required\npolicy:\n  frontmatter_policy: strict\n---\n\n# Codex Package\n', encoding='utf-8')
            (agents_dir / 'openai.yaml').write_text('interface:\n  short_description: OpenAI package fixture.\ndependencies:\n  openai_tool: required\n  required_skills:\n    - skill-factory-router\n  tools:\n    - type: mcp\n      name: browser\npolicy:\n  openai_policy: strict\n', encoding='utf-8')
            contract = skills_package(repo_root, 'Skills/agent-ops/codex-package').data['skill_package']['skill_package_contract']
        self.assertEqual(contract['metadata']['dependencies'], {'frontmatter_tool': 'required', 'openai_tool': 'required', 'required_skills': ['skill-factory-router'], 'tools': [{'type': 'mcp', 'name': 'browser'}]})
        self.assertEqual(contract['metadata']['policy'], {'frontmatter_policy': 'strict', 'openai_policy': 'strict'})
        self.assertEqual(contract['metadata']['short_description'], 'OpenAI package fixture.')
        self.assertIn('dependencies', contract['optional_fields']['present'])
        self.assertIn('policy', contract['optional_fields']['present'])

    def test_skill_frontmatter_parser_preserves_nested_contract_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = Path(temp_dir) / 'SKILL.md'
            skill_md.write_text('---\nname: codex-package\ndescription: Codex package metadata fixture.\ndependencies:\n  required_skills:\n    - skill-factory-router\n  tools:\n    - browser\npolicy:\n  permissions:\n    - network\n---\n\n# Codex Package\n', encoding='utf-8')
            frontmatter = read_skill_frontmatter_fields(skill_md)
        self.assertEqual(frontmatter['dependencies']['required_skills'], ['skill-factory-router'])
        self.assertEqual(frontmatter['dependencies']['tools'], ['browser'])
        self.assertEqual(frontmatter['policy']['permissions'], ['network'])

    def test_normalized_list_sorts_sets_without_reordering_lists(self) -> None:
        self.assertEqual(package_contracts.normalized_list({'beta', 'alpha'}), ['alpha', 'beta'])
        self.assertEqual(package_contracts.normalized_list(('beta', 'alpha')), ['beta', 'alpha'])

    def test_package_contract_manual_yaml_fallback_preserves_openai_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'codex-package'
            agents_dir = skill_dir / 'agents'
            agents_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: codex-package\ndescription: Codex package metadata fixture.\n---\n\n# Codex Package\n', encoding='utf-8')
            (agents_dir / 'openai.yaml').write_text('interface:\n  short_description: OpenAI package fixture.\ndependencies:\n  required_skills:\n    - skill-factory-router\n  tools:\n    - type: mcp\n      name: browser\npolicy:\n  openai_policy: strict\n', encoding='utf-8')
            frontmatter = read_skill_frontmatter_fields(skill_md)
            with patch.object(package_contracts, 'yaml', None):
                contract = package_contracts.skill_package_contract(repo_root, skill_md, frontmatter)
        self.assertEqual(contract['metadata']['short_description'], 'OpenAI package fixture.')
        self.assertEqual(contract['metadata']['dependencies']['required_skills'], ['skill-factory-router'])
        self.assertEqual(contract['metadata']['dependencies']['tools'], [{'type': 'mcp', 'name': 'browser'}])
        self.assertEqual(contract['metadata']['policy'], {'openai_policy': 'strict'})

    def test_json_shaped_reference_contract_survives_without_pyyaml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / 'Skills' / 'agent-ops' / 'json-contract'
            references = skill_dir / 'references'
            references.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('# Json Contract\n', encoding='utf-8')
            (references / 'contract.yaml').write_text(json.dumps({'schema_version': 1, 'skill': 'json-contract', 'purpose': 'Keep JSON-shaped YAML readable.', 'inputs': ['input'], 'outputs': ['output']}), encoding='utf-8')
            with patch.object(package_contracts, 'yaml', None):
                contract = package_contracts.read_reference_contract(skill_md)
        self.assertEqual(contract['purpose'], 'Keep JSON-shaped YAML readable.')
        self.assertEqual(contract['inputs'], ['input'])
        self.assertEqual(contract['outputs'], ['output'])

    def test_package_contract_malformed_yaml_falls_back_to_empty_openai_fields(self) -> None:

        class BrokenYaml:

            class YAMLError(Exception):
                pass

            @staticmethod
            def safe_load(_text: str) -> object:
                raise BrokenYaml.YAMLError('malformed')
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'codex-package'
            agents_dir = skill_dir / 'agents'
            agents_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: codex-package\ndescription: Codex package metadata fixture.\ndependencies:\n  frontmatter_tool: required\npolicy:\n  frontmatter_policy: strict\n---\n\n# Codex Package\n', encoding='utf-8')
            (agents_dir / 'openai.yaml').write_text('interface: [malformed\n', encoding='utf-8')
            frontmatter = read_skill_frontmatter_fields(skill_md)
            with patch.object(package_contracts, 'yaml', BrokenYaml):
                contract = package_contracts.skill_package_contract(repo_root, skill_md, frontmatter)
        self.assertIsNone(contract['metadata']['short_description'])
        self.assertEqual(contract['metadata']['dependencies'], {'frontmatter_tool': 'required'})
        self.assertEqual(contract['metadata']['policy'], {'frontmatter_policy': 'strict'})

    def test_skill_package_schema_rejects_missing_identity_contract(self) -> None:
        schema = self.schemas['skill-package.v1.schema.json']
        invalid_contract = {'schema_version': 'skill-package.v1', 'metadata': {'short_description': 'Missing required identity fields.'}, 'required_fields': {'present': [], 'missing': ['name', 'description']}, 'compatibility_status': 'blocked_validation'}
        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(schema, invalid_contract, self.schemas)
        self.assertIn('missing required key', str(context.exception))

    def test_skill_package_schema_rejects_unknown_contract_keys(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            contract = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']['skill_package_contract']
        contract['unexpected_contract_key'] = True
        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(self.schemas['skill-package.v1.schema.json'], contract, self.schemas)
        self.assertIn('unexpected keys', str(context.exception))

    def test_skill_package_schema_rejects_unknown_metadata_keys(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            contract = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']['skill_package_contract']
        contract['metadata']['unexpected_metadata_key'] = True
        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(self.schemas['skill-package.v1.schema.json'], contract, self.schemas)
        self.assertIn('unexpected keys', str(context.exception))

    def test_package_readiness_schema_accepts_public_package_payload(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        _validate_schema_subset(self.schemas['skill-package-readiness.v1.schema.json'], package, self.schemas)
        self.assertEqual(package['package_schema']['schema_version'], 'skill-package.v1')
        self.assertEqual(package['package_readiness_schema']['schema_version'], 'skill-package-readiness.v1')
        self.assertEqual(package['optimization_schema']['schema_version'], 'skill-optimization-contract.v1')
        self.assertEqual(package['compatibility_snapshot']['id'], 'skill-package-readiness.v1.public-output.2026-05-23')
        self.assertEqual(package['contract_schemas']['skill_package'], 'skill-package.v1')

    def test_package_payload_exposes_sdk_contract_and_optional_observability(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        _assert_sdk_package_contract(self, package['package_contract']['sdk_contract'])

    def test_structured_reference_fallback_preserves_top_level_lists(self) -> None:
        text = "---\nschema_version: '2.0'\nskill_name: example\nclaims:\n- id: global-target-repository\n  statement: Uses active repository.\ncases:\n- id: smoke-discovery\n  name: Discovery\n"
        with tempfile.NamedTemporaryFile('w', suffix='.yaml', encoding='utf-8') as handle:
            handle.write(text)
            handle.flush()
            with patch.object(package_contracts, 'yaml', None):
                process = package_contracts.subprocess.CompletedProcess(args=['ruby'], returncode=0, stdout=json.dumps({'schema_version': '2.0', 'skill_name': 'example', 'claims': [{'id': 'global-target-repository', 'statement': 'Uses active repository.'}], 'cases': [{'id': 'smoke-discovery', 'name': 'Discovery'}]}), stderr='')
                with patch.object(package_contracts.subprocess, 'run', return_value=process):
                    loaded, error = package_contracts.read_structured_reference(Path(handle.name))
        self.assertIsNone(error)
        self.assertIsInstance(loaded, dict)
        if not isinstance(loaded, dict):
            self.fail('expected structured reference fallback to return a dict')
        self.assertIsInstance(loaded.get('claims'), list)
        self.assertIsInstance(loaded.get('cases'), list)
        self.assertTrue(loaded['claims'])
        self.assertTrue(loaded['cases'])

    def test_structured_reference_fallback_preserves_nested_rubric_scoring(self) -> None:
        text = 'schema_version: 1\nquality_criteria:\n  current_state_before_action:\n    purpose: Uses live PR state.\n    why_it_matters: Prevents stale merge claims.\n    observable_evidence:\n      - latest_head_sha\n      - required_checks\n    scoring:\n      "5": Latest-head proof is complete.\n      "4": Minor evidence detail is missing.\n      "3": Evidence is present but incomplete.\n      "2": Evidence is stale or partial.\n      "1": No live PR evidence is provided.\nautomatic_failure_conditions:\n  - Claims blocked external CI as green.\n'
        mock_stdout = '{"schema_version":1,"quality_criteria":{"current_state_before_action":{"purpose":"Uses live PR state.","why_it_matters":"Prevents stale merge claims.","observable_evidence":["latest_head_sha","required_checks"],"scoring":{"5":"Latest-head proof is complete.","4":"Minor evidence detail is missing.","3":"Evidence is present but incomplete.","2":"Evidence is stale or partial.","1":"No live PR evidence is provided."}}},"automatic_failure_conditions":["Claims blocked external CI as green."]}'
        mock_process = package_contracts.subprocess.CompletedProcess(args=['ruby'], returncode=0, stdout=mock_stdout, stderr='')
        with tempfile.NamedTemporaryFile('w', suffix='.yaml', encoding='utf-8') as handle:
            handle.write(text)
            handle.flush()
            with patch.object(package_contracts, 'yaml', None), patch.object(package_contracts.subprocess, 'run', return_value=mock_process):
                loaded, error = package_contracts.read_structured_reference(Path(handle.name))
        self.assertIsNone(error)
        self.assertIsInstance(loaded, dict)
        if not isinstance(loaded, dict):
            self.fail('expected structured reference fallback to return a dict')
        criterion = loaded['quality_criteria']['current_state_before_action']
        self.assertEqual(criterion['observable_evidence'], ['latest_head_sha', 'required_checks'])
        self.assertEqual(criterion['scoring']['5'], 'Latest-head proof is complete.')
        self.assertEqual(
            loaded['automatic_failure_conditions'],
            ['Claims blocked external CI as green.'],
        )

    def test_sdk_contract_accepts_optional_valid_skillflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'workflow-skill'
            references_dir = skill_dir / 'references'
            workflows_dir = skill_dir / 'workflows'
            references_dir.mkdir(parents=True)
            workflows_dir.mkdir()
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: workflow-skill\ndescription: Workflow skill fixture.\n---\n\n# Workflow Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('schema_version: "1.0"\npurpose: "Exercise optional skillflow contract support."\nexecution_mode: "hybrid"\ninputs:\n  - name: task\noutputs:\n  - name: result\nworkflow:\n  path: "workflows/skillflow.json"\n  required: true\n  execution_mode: "hybrid"\n', encoding='utf-8')
            skillflow_payload = {'schema_version': 'skillflow.v1', 'name': 'workflow-skill', 'inputs': {'task': {'type': 'string'}}, 'outputs': {'result': {'type': 'string'}}, 'nodes': [{'id': 'classify', 'type': 'llm', 'out': 'classification'}, {'id': 'validate', 'type': 'validator', 'out': 'result'}]}
            (workflows_dir / 'skillflow.json').write_text(json.dumps(skillflow_payload), encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        workflow_contract = contract['values']['workflow_contract']
        _validate_schema_subset(self.schemas['skillflow.v1.schema.json'], skillflow_payload, self.schemas)
        self.assertEqual(workflow_contract['status'], 'pass')
        self.assertTrue(workflow_contract['declared'])
        self.assertTrue(workflow_contract['required'])
        self.assertEqual(workflow_contract['execution_mode'], 'hybrid')
        self.assertEqual(workflow_contract['node_count'], 2)
        self.assertEqual(workflow_contract['human_gate_count'], 0)
        self.assertFalse(workflow_contract['blockers'])
        self.assertTrue(contract['progressive_disclosure']['workflow_declared'])

    def test_sdk_contract_reports_progressive_disclosure_compaction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'compact-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: compact-skill\ndescription: Compact skill fixture.\n---\n\n# Compact Skill\n\n## Workflow\n\nKeep the entrypoint small.\n\n## Progressive Disclosure\n\n- Read `references/details.md` for task-specific detail.\n', encoding='utf-8')
            (references_dir / 'details.md').write_text('# Hidden File Skill Details\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        progressive = contract['progressive_disclosure']
        self.assertTrue(progressive['skill_md_under_250_lines'])
        self.assertTrue(progressive['progressive_disclosure_declared'])
        self.assertEqual(progressive['progressive_disclosure_reference_count'], 1)
        self.assertEqual(progressive['progressive_disclosure_missing_references'], [])
        self.assertTrue(progressive['progressive_disclosure_ready'])

    def test_writing_quality_blocks_near_threshold_reference_backed_sprawl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'near-threshold-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            filler = '\n'.join((f'Filler line {index}.' for index in range(205)))
            skill_md.write_text(f'---\nname: near-threshold-skill\ndescription: Use when a user asks to run a near-threshold package fixture.\n---\n\n# Near Threshold Skill\n\n## Workflow\n\nRun the narrow fixture path.\n\n{filler}\n\n## Output Contract\n\n- Report the fixture result.\n\n## Validation\n\n- Command: fixture check -> pass\n\n## Progressive Disclosure\n\n- Read `references/details.md` for task-specific detail.\n', encoding='utf-8')
            (references_dir / 'details.md').write_text('# Hidden File Skill Details\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        progressive_check = next((check for check in contract['checks'] if check['name'] == 'progressive_disclosure_rubric'))
        self.assertEqual(progressive_check['status'], 'blocked_validation')
        self.assertGreater(progressive_check['evidence']['line_count'], 220)
        self.assertTrue(progressive_check['evidence']['over_near_threshold'])
        self.assertIn('near_threshold_entrypoint_sprawl', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_accepts_evidence_contract_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'evidence-contract-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: evidence-contract-skill\ndescription: Use when a user asks to test evidence contract completion criteria.\n---\n\n# Evidence Contract Skill\n\n## Workflow\n\nRun the fixture path.\n\n## Evidence Contract\n\nReport the command evidence and blocker class.\n\n## Progressive Disclosure\n\n- Read `references/details.md` for task-specific detail.\n', encoding='utf-8')
            (references_dir / 'details.md').write_text('# Details\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        completion_check = next((check for check in contract['checks'] if check['name'] == 'procedural_completion_criteria'))
        self.assertEqual(completion_check['status'], 'pass')
        self.assertTrue(completion_check['evidence']['evidence_contract_declared'])
        self.assertNotIn('missing_completion_criterion', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_accepts_routed_validation_output_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'routed-output-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: routed-output-skill\ndescription: Use when a user asks to test routed validation output criteria.\n---\n\n# Routed Output Skill\n\n## Workflow\n\nRun the fixture path.\n\n## Progressive Disclosure\n\n- Read `references/validation-and-output.md` for output and evidence fields.\n', encoding='utf-8')
            (references_dir / 'validation-and-output.md').write_text('# Validation And Output\n\nReport command evidence.\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        completion_check = next((check for check in contract['checks'] if check['name'] == 'procedural_completion_criteria'))
        self.assertEqual(completion_check['status'], 'pass')
        self.assertTrue(completion_check['evidence']['completion_reference_declared'])
        self.assertNotIn('missing_completion_criterion', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_blocks_generic_trigger_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'generic-trigger-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: generic-trigger-skill\ndescription: Use when a user asks for help with anything.\n---\n\n# Generic Trigger Skill\n\n## Workflow\n\nRun the fixture path.\n\n## Output Contract\n\n- Report the fixture result.\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        trigger_check = next((check for check in contract['checks'] if check['name'] == 'construction_trigger_boundary'))
        self.assertEqual(trigger_check['status'], 'blocked_validation')
        self.assertEqual(trigger_check['dimension'], 'invocation')
        self.assertEqual(trigger_check['evidence']['glossary_axis'], 'Invocation')
        self.assertIn('anything', trigger_check['evidence']['generic_trigger_terms'])
        self.assertIn('construction_trigger_boundary_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_blocks_missing_steps_reference_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'structureless-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: structureless-skill\ndescription: Use when a user asks to validate structure checks.\n---\n\n# Structureless Skill\n\nThis skill contains background material but no executable workflow section.\n\n## Output Contract\n\n- Report the fixture result.\n\n## Progressive Disclosure\n\n- Read references/details.md for task-specific detail.\n', encoding='utf-8')
            (references_dir / 'details.md').write_text('# Details\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        structure_check = next((check for check in contract['checks'] if check['name'] == 'construction_steps_reference_structure'))
        self.assertEqual(structure_check['status'], 'blocked_validation')
        self.assertEqual(structure_check['dimension'], 'information_hierarchy')
        self.assertEqual(structure_check['evidence']['glossary_axis'], 'Information Hierarchy')
        self.assertFalse(structure_check['evidence']['procedural_heading_declared'])
        self.assertIn('construction_steps_reference_structure_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_blocks_phase_steps_without_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'ungated-phase-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: ungated-phase-skill\ndescription: Use when a user asks to plan phase based skill work.\n---\n\n# Ungated Phase Skill\n\n## Workflow\n\n- Phase one: gather the request.\n- Phase two: write the answer.\n\n## Output Contract\n\n- Report the fixture result.\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        steering_check = next((check for check in contract['checks'] if check['name'] == 'construction_steering_phase_gate'))
        self.assertEqual(steering_check['status'], 'blocked_validation')
        self.assertEqual(steering_check['dimension'], 'steering')
        self.assertEqual(steering_check['evidence']['glossary_axis'], 'Steering')
        self.assertTrue(steering_check['evidence']['phase_like'])
        self.assertIn('construction_steering_phase_gate_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_blocks_sediment_and_duplicate_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'sediment-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            sediment = ' '.join(['This package represents a thoughtful and comprehensive perspective on collaboration' for _ in range(12)])
            duplicate = '- Read references/details.md before creating the final report for the operator.\n'
            references_dir = skill_dir / 'references'
            references_dir.mkdir()
            (references_dir / 'details.md').write_text('# Details\n', encoding='utf-8')
            skill_md.write_text(f'---\nname: sediment-skill\ndescription: Use when a user asks to validate pruning checks.\n---\n\n# Sediment Skill\n\n{sediment}\n\n## Workflow\n\n- Run the fixture path.\n{duplicate}{duplicate}\n\n## Output Contract\n\n- Report the fixture result.\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        pruning_check = next((check for check in contract['checks'] if check['name'] == 'construction_pruning_sediment'))
        self.assertEqual(pruning_check['status'], 'blocked_validation')
        self.assertEqual(pruning_check['dimension'], 'pruning')
        self.assertEqual(pruning_check['evidence']['glossary_axis'], 'Pruning')
        self.assertTrue(pruning_check['evidence']['long_paragraphs_without_behavior'])
        self.assertTrue(pruning_check['evidence']['duplicate_instruction_lines'])
        blocker_ids = {blocker['rule_id'] for blocker in contract['blockers']}
        self.assertIn('construction_sediment_paragraph', blocker_ids)
        self.assertIn('construction_duplicate_instruction', blocker_ids)

    def test_writing_quality_blocks_three_way_boundary_fragmentation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'fragmented-boundary-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: fragmented-boundary-skill\ndescription: Use when a user asks to validate fragmented boundary checks.\n---\n\n# Fragmented Boundary Skill\n\n## Workflow\n\n1. Inspect the target and report command evidence.\n\n## Constraints\n\n- Keep the audit read-only.\n\n## Execution Boundaries\n\n- Use target repo commands as authority.\n\n## Failure Mode\n\n- Stop with the blocker.\n\n## Validation\n\n- Command: fixture check -> pass\n\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        fragmentation_check = next((check for check in contract['checks'] if check['name'] == 'construction_boundary_fragmentation'))
        self.assertEqual(fragmentation_check['status'], 'blocked_validation')
        self.assertEqual(fragmentation_check['dimension'], 'pruning')
        self.assertEqual(fragmentation_check['evidence']['fragmented_sections'], ['Constraints', 'Execution Boundaries', 'Validation'])
        self.assertIn('construction_boundary_fragmentation', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_blocks_extra_headers_for_sdk_managed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'extra-header-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: extra-header-skill\ndescription: Use when a user asks to validate canonical skill headers.\nmetadata:\n  skill-type: runbook\n  lifecycle_state: active\n  metadata_source: frontmatter\n---\n\n# Extra Header Skill\n\nShort purpose paragraph.\n\n## Principle\n\nKeep the entrypoint small.\n\n## When To Use\n\n- Use when testing canonical headers.\n\n## Inputs\n\n- Target path.\n\n## Outputs\n\n- Report.\n\n## Workflow\n\n1. Inspect the target.\n\n## Failure Mode\n\n- Stop with the blocker.\n\n## Validation\n\n- Command: fixture check -> pass\n\n## References\n\n- No references.\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        header_check = next((check for check in contract['checks'] if check['name'] == 'canonical_skill_headers'))
        self.assertEqual(header_check['status'], 'blocked_validation')
        self.assertEqual(header_check['evidence']['extra_h2_headings'], ['Principle'])
        self.assertIn('canonical_skill_headers_required', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_accepts_canonical_headers_for_sdk_managed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'canonical-header-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: canonical-header-skill\ndescription: Use when a user asks to validate canonical skill headers.\nmetadata:\n  skill-type: runbook\n  lifecycle_state: active\n  metadata_source: frontmatter\n---\n\n# Canonical Header Skill\n\nShort purpose paragraph.\n\n## When To Use\n\n- Use when testing canonical headers.\n\n## Inputs\n\n- Target path.\n\n## Outputs\n\n- Report.\n\n## Workflow\n\n1. Inspect the target.\n\n## Failure Mode\n\n- Stop with the blocker.\n\n## Validation\n\n- Command: fixture check -> pass\n\n## References\n\n- No references.\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        header_check = next((check for check in contract['checks'] if check['name'] == 'canonical_skill_headers'))
        self.assertEqual(header_check['status'], 'pass')
        self.assertEqual(header_check['evidence']['missing_headers'], [])
        self.assertEqual(header_check['evidence']['extra_h2_headings'], [])

    def test_sdk_contract_reports_missing_progressive_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'missing-ref-skill'
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: missing-ref-skill\ndescription: Missing reference fixture.\n---\n\n# Missing Reference Skill\n\n## Progressive Disclosure\n\n- Read `references/missing.md` for task-specific detail.\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        progressive = contract['progressive_disclosure']
        self.assertEqual(progressive['progressive_disclosure_missing_references'], ['references/missing.md'])
        self.assertFalse(progressive['progressive_disclosure_ready'])

    def test_sdk_contract_requires_format_docs_for_operating_model_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'github' / 'teach-like'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: teach-like\ndescription: Teaching fixture.\n---\n\n# Teach Like\n\n## Inputs\n\n- Workspace files: MISSION.md, RESOURCES.md, GLOSSARY.md, and learning-records/*.md.\n\n## Progressive Disclosure\n\n- Read `references/templates.md` for compact artifact shapes.\n', encoding='utf-8')
            (references_dir / 'templates.md').write_text('# Templates\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
            progressive = contract['progressive_disclosure']
            formats = progressive['operating_model_formats']
            self.assertEqual(formats['missing_format_references'], ['references/mission-format.md', 'references/resources-format.md', 'references/glossary-format.md', 'references/learning-record-format.md'])
            self.assertFalse(formats['format_references_ready'])
            self.assertFalse(progressive['progressive_disclosure_ready'])
            for filename in ('mission-format.md', 'resources-format.md', 'glossary-format.md', 'learning-record-format.md'):
                (references_dir / filename).write_text(f'# {filename}\n', encoding='utf-8')
            fixed = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        fixed_formats = fixed['progressive_disclosure']['operating_model_formats']
        self.assertEqual(fixed_formats['missing_format_references'], [])
        self.assertTrue(fixed_formats['format_references_ready'])
        self.assertTrue(fixed['progressive_disclosure']['progressive_disclosure_ready'])

    def test_sdk_contract_rejects_progressive_paths_outside_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'escape-ref-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: escape-ref-skill\ndescription: Escape reference fixture.\n---\n\n# Escape Reference Skill\n\n## Progressive Disclosure\n\n- Read `references/../outside.md` for task-specific detail.\n', encoding='utf-8')
            (skill_dir / 'outside.md').write_text('# Outside\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        progressive = contract['progressive_disclosure']
        self.assertEqual(progressive['progressive_disclosure_missing_references'], ['references/../outside.md'])
        self.assertFalse(progressive['progressive_disclosure_ready'])

    def test_sdk_contract_requires_source_operating_model_progressive_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'github' / 'sourceful-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: sourceful-skill\ndescription: Preserve source operating model fixture.\nmetadata:\n  version: "1.0.0"\n  compatible_roles:\n    - default\n  runtime_needs:\n    - local files\n  maturity: stable\n  provenance: test fixture\n  share_readiness: ready\n---\n\n# Sourceful Skill\n\n## Progressive Disclosure\n\n- Read `references/templates.md` for compact artifact shapes.\n', encoding='utf-8')
            (references_dir / 'templates.md').write_text('# Templates\n', encoding='utf-8')
            (references_dir / 'teaching-operating-model.md').write_text('# Teaching Operating Model\n', encoding='utf-8')
            (references_dir / 'source-context.yaml').write_text('schema_version: 1\nreferences:\n  - path: references/teaching-operating-model.md\n    kind: source_operating_model\n    provenance: upstream source\n    load_when: creating lessons\n', encoding='utf-8')
            contract = package_contracts.skill_package_readiness(read_skill_frontmatter_fields(skill_md), repo_root, skill_md)
            source_model = contract['sdk_contract']['progressive_disclosure']['source_operating_model']
            self.assertEqual(source_model['status'], 'blocked_validation')
            self.assertEqual(source_model['missing_progressive_routes'], ['references/teaching-operating-model.md'])
            self.assertIn('progressive_disclosure:source_operating_model_preservation', contract['install_gate']['blocked_reasons'])
            skill_md.write_text(skill_md.read_text(encoding='utf-8') + '- Read `references/teaching-operating-model.md` before creating lessons.\n', encoding='utf-8')
            fixed = package_contracts.skill_package_readiness(read_skill_frontmatter_fields(skill_md), repo_root, skill_md)
        fixed_source_model = fixed['sdk_contract']['progressive_disclosure']['source_operating_model']
        self.assertEqual(fixed_source_model['status'], 'pass')
        self.assertEqual(fixed_source_model['missing_progressive_routes'], [])
        self.assertNotIn('progressive_disclosure:source_operating_model_preservation', fixed['install_gate']['blocked_reasons'])

    def test_sdk_contract_reports_identity_and_asset_browseability(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'identity-skill'
            references_dir = skill_dir / 'references'
            scripts_dir = skill_dir / 'scripts'
            references_dir.mkdir(parents=True)
            scripts_dir.mkdir()
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: identity-skill\ndescription: Create reliable package identity checks when validating skill assets.\nshort_description: Check skill package identity\n---\n\n# Identity Skill\n', encoding='utf-8')
            (references_dir / 'gold-contract.md').write_text('# Gold Contract\n\nPurposeful reference detail.\n', encoding='utf-8')
            (references_dir / 'held-out-examples.jsonl').write_text('{"description":"Purpose: held-out scorer calibration example.","id":"case-1"}\n', encoding='utf-8')
            (scripts_dir / 'run-checks.py').write_text('"""Purpose: run the package identity fixture check."""\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        identity = contract['identity_and_assets']
        self.assertTrue(identity['ready'])
        self.assertTrue(identity['skill_identity']['name_kebab_case'])
        self.assertTrue(identity['skill_identity']['name_matches_directory'])
        self.assertTrue(identity['skill_identity']['description_has_action_term'])
        self.assertTrue(identity['reference_inventory']['ready'])
        self.assertTrue(identity['script_inventory']['ready'])

    def test_sdk_contract_accepts_multiline_script_docstring_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'script-docstring-skill'
            scripts_dir = skill_dir / 'scripts'
            scripts_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: script-docstring-skill\ndescription: Create reliable script description checks for package validation.\n---\n\n# Script Docstring Skill\n', encoding='utf-8')
            (scripts_dir / 'run-checks.py').write_text('"""\nPurpose: run the package script fixture check.\n"""\nprint(\'ok\')\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        scripts = contract['identity_and_assets']['script_inventory']
        self.assertTrue(scripts['ready'])
        self.assertEqual(scripts['missing_descriptions'], [])

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symlink support required')
    def test_sdk_contract_blocks_symlinked_support_files_without_reading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'symlink-support-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            outside = repo_root / 'outside.md'
            outside.write_text('# Outside\n', encoding='utf-8')
            try:
                (references_dir / 'outside-link.md').symlink_to(outside)
            except OSError as exc:
                self.skipTest(f'symlink creation unavailable: {exc}')
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: symlink-support-skill\ndescription: Create reliable symlink blocking checks for package validation.\n---\n\n# Symlink Support Skill\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        references = contract['identity_and_assets']['reference_inventory']
        self.assertFalse(references['ready'])
        self.assertEqual(references['count'], 0)
        self.assertIn('Skills/agent-ops/symlink-support-skill/references/outside-link.md', references['unsafe_paths'])

    def test_sdk_contract_reports_identity_and_asset_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'bad-skill'
            references_dir = skill_dir / 'references'
            scripts_dir = skill_dir / 'scripts'
            references_dir.mkdir(parents=True)
            scripts_dir.mkdir()
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: Bad Skill\ndescription: sample\n---\n\n# Bad Skill\n', encoding='utf-8')
            (references_dir / 'details.md').write_text('No title here.\n', encoding='utf-8')
            (references_dir / 'undocumented-examples.jsonl').write_text('{"id":"case-1"}\n', encoding='utf-8')
            (scripts_dir / 'RunChecks.py').write_text("print('missing purpose metadata')\n", encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        identity = contract['identity_and_assets']
        self.assertFalse(identity['ready'])
        self.assertFalse(identity['skill_identity']['name_kebab_case'])
        self.assertFalse(identity['skill_identity']['name_matches_directory'])
        self.assertFalse(identity['skill_identity']['description_length_ok'])
        self.assertFalse(identity['skill_identity']['description_has_action_term'])
        self.assertIn('Skills/agent-ops/bad-skill/references/details.md', identity['reference_inventory']['generic_names'])
        self.assertIn('Skills/agent-ops/bad-skill/references/details.md', identity['reference_inventory']['missing_descriptions'])
        self.assertIn('Skills/agent-ops/bad-skill/references/details.md', identity['reference_inventory']['weak_headings'])
        self.assertIn('Skills/agent-ops/bad-skill/references/undocumented-examples.jsonl', identity['reference_inventory']['missing_descriptions'])
        self.assertIn('Skills/agent-ops/bad-skill/scripts/RunChecks.py', identity['script_inventory']['bad_names'])
        self.assertIn('Skills/agent-ops/bad-skill/scripts/RunChecks.py', identity['script_inventory']['missing_descriptions'])
