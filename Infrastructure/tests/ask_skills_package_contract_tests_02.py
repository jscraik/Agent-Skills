import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from ask_skills_package_contract_tests_core import (
    REPO_ROOT,
    _AskSkillsPackageContractBase,
    _load_snapshot,
    _snapshot_projection,
    _validate_schema_subset,
)
from ask.commands.skills_impl import skills_package
from ask.skills_sdk import package_contracts
from ask.skills_sdk.contracts import read_skill_frontmatter_fields

class TestAskSkillsPackageContract(_AskSkillsPackageContractBase):
    def test_reference_inventory_blocks_generic_markdown_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'weak-reference-heading'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: weak-reference-heading\ndescription: Create reliable reference heading checks for package validation.\n---\n\n# Weak Reference Heading\n', encoding='utf-8')
            (references_dir / 'routing-boundary.md').write_text('# Details\n\nReference content.\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        references = contract['identity_and_assets']['reference_inventory']
        self.assertFalse(references['ready'])
        self.assertEqual(references['weak_headings'], ['Skills/agent-ops/weak-reference-heading/references/routing-boundary.md'])

    def test_reference_inventory_accepts_filename_aligned_markdown_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'strong-reference-heading'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: strong-reference-heading\ndescription: Create reliable reference heading checks for package validation.\n---\n\n# Strong Reference Heading\n', encoding='utf-8')
            (references_dir / 'routing-boundary.md').write_text('# Routing Boundary\n\nReference content.\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        references = contract['identity_and_assets']['reference_inventory']
        self.assertEqual(references['weak_headings'], [])
        self.assertEqual(references['missing_descriptions'], [])

    def test_reference_inventory_blocks_weak_top_level_capsule_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'weak-capsule-heading'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: weak-capsule-heading\ndescription: Create reliable capsule heading checks for package validation.\n---\n\n# Weak Capsule Heading\n\n## Progressive Disclosure\n\n- Read references/knowledge-capsule-routing.md before opening capsule files.\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule.manifest.yaml').write_text('schema_version: knowledge-os.knowledge-capsule-manifest.v1\ncapsules:\n  - target_path: references/spec-first-demo.md\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule-routing.md').write_text('# Knowledge Capsule Routing\n\n- references/spec-first-demo.md for spec-first demo coaching.\n', encoding='utf-8')
            (references_dir / 'spec-first-demo.md').write_text('# Reference\n\nCapsule content.\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        references = contract['identity_and_assets']['reference_inventory']
        self.assertFalse(references['ready'])
        self.assertEqual(references['weak_headings'], ['Skills/agent-ops/weak-capsule-heading/references/spec-first-demo.md'])

    def test_reference_inventory_accepts_invocable_top_level_capsule_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'strong-capsule-heading'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: strong-capsule-heading\ndescription: Create reliable capsule heading checks for package validation.\n---\n\n# Strong Capsule Heading\n\n## Progressive Disclosure\n\n- Read references/knowledge-capsule-routing.md before opening capsule files.\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule.manifest.yaml').write_text('schema_version: knowledge-os.knowledge-capsule-manifest.v1\ncapsules:\n  - target_path: references/spec-first-demo.md\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule-routing.md').write_text('# Knowledge Capsule Routing\n\n- references/spec-first-demo.md for spec-first demo coaching.\n', encoding='utf-8')
            (references_dir / 'spec-first-demo.md').write_text('# Spec First Demo\n\nCapsule content.\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        references = contract['identity_and_assets']['reference_inventory']
        self.assertEqual(references['weak_headings'], [])
        self.assertEqual(references['missing_descriptions'], [])

    def test_required_skillflow_missing_blocks_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'workflow-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: workflow-skill\ndescription: Workflow skill fixture.\nversion: "1.0.0"\nmetadata:\n  compatible_roles:\n    - worker\n  runtime_needs:\n    - filesystem\n  maturity: beta\n  provenance: internal\n  share_readiness: ready\n---\n\n# Workflow Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('schema_version: "1.0"\npurpose: "Exercise required skillflow blocking."\nexecution_mode: "deterministic_flow"\ninputs:\n  - name: task\noutputs:\n  - name: result\nworkflow:\n  path: "workflows/skillflow.json"\n  required: true\n  execution_mode: "deterministic_flow"\n', encoding='utf-8')
            package = skills_package(repo_root, 'Skills/agent-ops/workflow-skill', strict=True).data['skill_package']
        workflow_contract = package['package_contract']['sdk_contract']['values']['workflow_contract']
        self.assertEqual(workflow_contract['status'], 'blocked_validation')
        self.assertIn('workflow_contract:skillflow_required_file_missing', package['gate_summary']['blocked_reasons'])
        self.assertIn(package['package_contract']['readiness_level'], {'sdk_contract_incomplete', 'workflow_contract_incomplete'})

    def test_sdk_contract_accepts_valid_skill_optimization_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'optimizable-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: optimizable-skill\ndescription: Optimizable skill fixture.\n---\n\n# Optimizable Skill\n', encoding='utf-8')
            optimization_payload = {'schema_version': 'skill-optimization-contract.v1', 'enabled': True, 'target_artifact': 'SKILL.md', 'optimizer_mode': 'bounded_patch', 'roles': {'target_runner': {'may_edit': 'none', 'sees': ['current_target']}, 'optimizer': {'may_edit': 'candidate_patch_only', 'sees': ['train', 'selection']}, 'promoter': {'may_edit': 'canonical_source_after_review', 'sees': ['candidate', 'selection', 'test']}, 'auditor': {'may_edit': 'none', 'sees': ['diff', 'protected_paths']}}, 'splits': {'train': {'path': '.harness/evals/optimizable/train.jsonl', 'role': 'proposal_generation'}, 'selection': {'path': '.harness/evals/optimizable/selection.jsonl', 'role': 'candidate_acceptance'}, 'test': {'path': '.harness/evals/optimizable/test.jsonl', 'role': 'final_report_only'}, 'split_seed': 42}, 'edit_policy': {'mode': 'patch', 'operations': ['add', 'delete', 'replace'], 'max_edits': 4}, 'acceptance_gate': {'metric': 'score', 'direction': 'maximize', 'rule': 'strict_improvement', 'ties': 'reject', 'min_delta': 0.01, 'noise_runs': 3, 'guard_failure': 'discard', 'report_test_score_only_after_acceptance': True}, 'anti_cheat': {'protected_paths': ['references/evals.yaml', '.harness/evals/**'], 'checks': ['protected_path_diff_empty', 'held_out_not_visible_to_optimizer']}, 'evidence': {'root': '.harness/evidence/optimizable/<run_tag>', 'rollout_jsonl': 'rollouts.jsonl', 'rejected_buffer_jsonl': 'rejected-edits.jsonl', 'candidate_artifact': 'best_skill.md', 'promotion_manifest': 'promotion.json', 'selection_results': 'selection-results.json', 'test_results': 'test-results.json'}, 'promotion': {'canonical_edit_requires_review': True, 'required_checks': ['selection_gate_pass', 'held_out_test_report', 'anti_cheat_pass']}}
            (references_dir / 'contract.yaml').write_text('schema_version: "1.0"\npurpose: "Exercise valid bounded optimization contract support."\ninputs:\n  - name: task\noutputs:\n  - name: result\noptimization:\n  schema_version: "skill-optimization-contract.v1"\n  enabled: true\n  target_artifact: "SKILL.md"\n  optimizer_mode: "bounded_patch"\n  roles:\n    target_runner:\n      may_edit: "none"\n      sees:\n        - current_target\n    optimizer:\n      may_edit: "candidate_patch_only"\n      sees:\n        - train\n        - selection\n    promoter:\n      may_edit: "canonical_source_after_review"\n      sees:\n        - candidate\n        - selection\n        - test\n    auditor:\n      may_edit: "none"\n      sees:\n        - diff\n        - protected_paths\n  splits:\n    train:\n      path: ".harness/evals/optimizable/train.jsonl"\n      role: "proposal_generation"\n    selection:\n      path: ".harness/evals/optimizable/selection.jsonl"\n      role: "candidate_acceptance"\n    test:\n      path: ".harness/evals/optimizable/test.jsonl"\n      role: "final_report_only"\n    split_seed: 42\n  edit_policy:\n    mode: "patch"\n    operations:\n      - add\n      - delete\n      - replace\n    max_edits: 4\n  acceptance_gate:\n    metric: "score"\n    direction: "maximize"\n    rule: "strict_improvement"\n    ties: "reject"\n    min_delta: 0.01\n    noise_runs: 3\n    guard_failure: "discard"\n    report_test_score_only_after_acceptance: true\n  anti_cheat:\n    protected_paths:\n      - "references/evals.yaml"\n      - ".harness/evals/**"\n    checks:\n      - protected_path_diff_empty\n      - held_out_not_visible_to_optimizer\n  evidence:\n    root: ".harness/evidence/optimizable/<run_tag>"\n    rollout_jsonl: "rollouts.jsonl"\n    rejected_buffer_jsonl: "rejected-edits.jsonl"\n    candidate_artifact: "best_skill.md"\n    promotion_manifest: "promotion.json"\n    selection_results: "selection-results.json"\n    test_results: "test-results.json"\n  promotion:\n    canonical_edit_requires_review: true\n    required_checks:\n      - selection_gate_pass\n      - held_out_test_report\n      - anti_cheat_pass\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        optimization_contract = contract['values']['optimization_contract']
        _validate_schema_subset(self.schemas['skill-optimization-contract.v1.schema.json'], optimization_payload, self.schemas)
        min_delta_payload = json.loads(json.dumps(optimization_payload))
        min_delta_payload['acceptance_gate'] = {'metric': 'score', 'direction': 'maximize', 'rule': 'min_delta', 'ties': 'reject', 'guard_failure': 'discard'}
        with self.assertRaisesRegex(AssertionError, 'min_delta'):
            _validate_schema_subset(self.schemas['skill-optimization-contract.v1.schema.json'], min_delta_payload, self.schemas)
        negative_integer_payload = json.loads(json.dumps(optimization_payload))
        negative_integer_payload['edit_policy']['max_edits'] = -1
        with self.assertRaisesRegex(AssertionError, 'minimum'):
            _validate_schema_subset(self.schemas['skill-optimization-contract.v1.schema.json'], negative_integer_payload, self.schemas)
        self.assertEqual(optimization_contract['status'], 'pass')
        self.assertTrue(optimization_contract['enabled'])
        self.assertEqual(optimization_contract['optimizer_mode'], 'bounded_patch')
        self.assertEqual(optimization_contract['split_seed'], 42)
        self.assertFalse(optimization_contract['blockers'])
        self.assertTrue(contract['progressive_disclosure']['optimization_declared'])

    def test_incomplete_skill_optimization_contract_blocks_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'optimizable-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: optimizable-skill\ndescription: Optimizable skill fixture.\nversion: "1.0.0"\nmetadata:\n  compatible_roles:\n    - worker\n  runtime_needs:\n    - filesystem\n  maturity: beta\n  provenance: internal\n  share_readiness: ready\n---\n\n# Optimizable Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('schema_version: "1.0"\npurpose: "Exercise incomplete bounded optimization contract blocking."\ninputs:\n  - name: task\noutputs:\n  - name: result\noptimization:\n  enabled: true\n  target_artifact: "SKILL.md"\n', encoding='utf-8')
            package = skills_package(repo_root, 'Skills/agent-ops/optimizable-skill', strict=True).data['skill_package']
        optimization_contract = package['package_contract']['sdk_contract']['values']['optimization_contract']
        self.assertEqual(optimization_contract['status'], 'blocked_validation')
        self.assertIn('optimization_contract:optimization_optimizer_mode_invalid', package['gate_summary']['blocked_reasons'])
        self.assertIn(package['package_contract']['readiness_level'], {'sdk_contract_incomplete', 'optimization_contract_incomplete'})

    def test_incomplete_reference_quality_blocks_package_readiness(self) -> None:
        frontmatter = {'name': 'reference-blocked-skill', 'description': 'Reference blocked skill fixture.', 'metadata': {'version': '1.0.0', 'compatible_roles': ['worker'], 'runtime_needs': ['filesystem'], 'maturity': 'beta', 'provenance': 'internal', 'share_readiness': 'ready'}}
        sdk_contract = {'required_fields': {'missing': []}, 'values': {'workflow_contract': {'status': 'pass'}, 'optimization_contract': {'status': 'pass'}, 'reference_quality': {'status': 'blocked_validation', 'required_for_package_readiness': True, 'blockers': [{'rule_id': 'reference_contract_incomplete'}]}}}
        with patch.object(package_contracts, 'sdk_package_contract', return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)
        self.assertEqual(package['readiness_level'], 'reference_quality_incomplete')
        self.assertIn('reference_quality:reference_contract_incomplete', package['install_gate']['blocked_reasons'])

    def test_incomplete_writing_quality_blocks_package_readiness(self) -> None:
        frontmatter = {'name': 'writing-blocked-skill', 'description': 'Writing blocked skill fixture.', 'metadata': {'version': '1.0.0', 'compatible_roles': ['worker'], 'runtime_needs': ['filesystem'], 'maturity': 'beta', 'provenance': 'internal', 'share_readiness': 'ready'}}
        sdk_contract = {'required_fields': {'missing': []}, 'values': {'workflow_contract': {'status': 'pass'}, 'optimization_contract': {'status': 'pass'}, 'reference_quality': {'status': 'pass', 'required_for_package_readiness': True}, 'writing_quality': {'status': 'blocked_validation', 'required_for_package_readiness': True, 'blockers': [{'rule_id': 'scenario_alignment_gold_shape'}]}}}
        with patch.object(package_contracts, 'sdk_package_contract', return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)
        self.assertEqual(package['readiness_level'], 'writing_quality_incomplete')
        self.assertFalse(package['install_gate']['install_ready'])
        self.assertIn('writing_quality:scenario_alignment_gold_shape', package['install_gate']['blocked_reasons'])

    def test_incomplete_openai_platform_compat_blocks_package_readiness(self) -> None:
        frontmatter = {'name': 'openai-blocked-skill', 'description': 'OpenAI blocked skill fixture.', 'metadata': {'version': '1.0.0', 'compatible_roles': ['worker'], 'runtime_needs': ['filesystem'], 'maturity': 'beta', 'provenance': 'internal', 'share_readiness': 'ready'}}
        sdk_contract = {'required_fields': {'missing': []}, 'values': {'workflow_contract': {'status': 'pass'}, 'optimization_contract': {'status': 'pass'}, 'reference_quality': {'status': 'pass', 'required_for_package_readiness': True}, 'writing_quality': {'status': 'pass', 'required_for_package_readiness': True}, 'openai_platform_compat': {'status': 'blocked_validation', 'required_for_package_readiness': True, 'blockers': [{'rule_id': 'plugin_hooks_unsupported_type'}]}}}
        with patch.object(package_contracts, 'sdk_package_contract', return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)
        self.assertEqual(package['readiness_level'], 'openai_platform_compat_incomplete')
        self.assertFalse(package['install_gate']['install_ready'])
        self.assertIn('openai_platform_compat:plugin_hooks_unsupported_type', package['install_gate']['blocked_reasons'])

    def test_reference_quality_requires_capability_selector_for_multi_facet_capsules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'multi-facet-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: multi-facet-skill\ndescription: Multi facet fixture.\nversion: "1.0.0"\n---\n\n# Multi Facet Skill\n\n## Progressive Disclosure\n- references/knowledge-capsules/example-a.md\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test missing capability selector.\ninputs:\n  - user_request\noutputs:\n  - result\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule.manifest.yaml').write_text('schema_version: knowledge-os.knowledge-capsule-manifest.v1\nselected_facets:\n  - pack.example:alpha\n  - pack.example:beta\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        selector_check = next((check for check in contract['checks'] if check['name'] == 'capability_selector_contract'))
        self.assertEqual(selector_check['status'], 'blocked_validation')
        self.assertEqual(selector_check['missing'], ['knowledge-capsule-routing.md', 'capability_selection', 'progressive_disclosure_named_capsules'])
        self.assertIn('capability_selector_contract_missing', {blocker['rule_id'] for blocker in contract['blockers']})
        self.assertIn('basic_requirement_rubric_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_requires_basic_requirement_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'rubricless-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: rubricless-skill\ndescription: Rubricless fixture.\nversion: "1.0.0"\n---\n\n# Rubricless Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test missing rubric contract.\ninputs:\n  - user request\noutputs:\n  - result\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        rubric_check = next((check for check in contract['checks'] if check['name'] == 'basic_requirement_rubric'))
        self.assertEqual(rubric_check['status'], 'blocked_validation')
        self.assertEqual(rubric_check['missing'], ['quality_criteria', 'evidence_requirements'])
        self.assertIn('basic_requirement_rubric_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_requires_analytic_rubric_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'weak-rubric-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: weak-rubric-skill\ndescription: Weak rubric fixture.\nversion: "1.0.0"\n---\n\n# Weak Rubric Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test weak rubric contract.\ninputs:\n  - user request\noutputs:\n  - result\nquality_criteria:\n  result_quality:\n    observable: result contains useful evidence\n    scoring: malformed\nevidence_requirements:\n  - Result cites evidence.\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        analytic_check = next((check for check in contract['checks'] if check['name'] == 'analytic_rubric_quality'))
        self.assertEqual(analytic_check['status'], 'blocked_validation')
        self.assertIn('quality_criteria.result_quality.purpose', analytic_check['missing'])
        self.assertIn('quality_criteria.result_quality.why_it_matters', analytic_check['missing'])
        self.assertIn('quality_criteria.result_quality.observable_evidence', analytic_check['missing'])
        self.assertNotIn('quality_criteria.result_quality.scoring', analytic_check['missing'])
        self.assertIn('quality_criteria.result_quality.scoring:nonempty_mapping_required', analytic_check['missing'])
        self.assertIn('automatic_failure_conditions', analytic_check['missing'])
        self.assertNotIn('analytic_rubric_quality_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_blocks_analytic_rubric_shape_for_tessl_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'weak-tessl-rubric-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: weak-tessl-rubric-skill\ndescription: Weak Tessl rubric fixture.\nversion: "1.0.0"\n---\n\n# Weak Tessl Rubric Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test weak Tessl rubric contract.\ninputs:\n  - user request\noutputs:\n  - result\nquality_criteria:\n  result_quality:\n    observable: result contains useful evidence\nevidence_requirements:\n  - Result cites evidence.\ntessl_scenario_policy:\n  scenario_drift_review:\n    required_after_skill_change: true\n    review_decisions:\n      - keep\n      - update\n      - add\n      - remove\n    review_surfaces:\n      - references/evals.yaml\n      - references/evals/*.md\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        analytic_check = next((check for check in contract['checks'] if check['name'] == 'analytic_rubric_quality'))
        self.assertEqual(analytic_check['status'], 'blocked_validation')
        self.assertIn('analytic_rubric_quality_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_accepts_declared_capability_selector_for_multi_facet_capsules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'selector-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: selector-skill\ndescription: Selector fixture.\nversion: "1.0.0"\n---\n\n# Selector Skill\n\nSelect the task type before opening capsule bodies.\n\n## Progressive Disclosure\n- references/knowledge-capsule-routing.md\n- references/knowledge-capsule.manifest.yaml\n- references/knowledge-capsules/<capsule>.md\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test complete capability selector.\ninputs:\n  - user_request\n  - task_type\noutputs:\n  - result\n  - task_type\nquality_criteria:\n  task_type_selection:\n    alpha: alpha task\n    beta: beta task\n  result_quality:\n    purpose: Measures whether the skill returns the selected task result.\n    why_it_matters: Selector skills must prove that the selected capability changes the output.\n    observable_evidence:\n      - The result names the selected task type.\n      - The result cites selector evidence.\n    scoring:\n      5: Selects the task type, returns the matching result, and cites evidence.\n      4: Selects the task type and returns the matching result with minor evidence gaps.\n      3: Returns a plausible result but leaves selector evidence partly implicit.\n      2: Mentions a task type but does not use it to shape the result.\n      1: Does not select or apply a task type.\nautomatic_failure_conditions:\n  - Missing or contradictory task type selection.\nevidence_requirements:\n  - Selection decisions must cite the selected task type and evidence.\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule-routing.md').write_text('# Capsule Routing\n\nRoute through the smallest selected capsule.\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule.manifest.yaml').write_text('schema_version: knowledge-os.knowledge-capsule-manifest.v1\nselected_facets:\n  - pack.example:alpha\n  - pack.example:beta\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        selector_check = next((check for check in contract['checks'] if check['name'] == 'capability_selector_contract'))
        self.assertEqual(selector_check['status'], 'pass')
        self.assertEqual(selector_check['selectors'], ['task_type_selection'])
        rubric_check = next((check for check in contract['checks'] if check['name'] == 'basic_requirement_rubric'))
        self.assertEqual(rubric_check['status'], 'pass')
        analytic_check = next((check for check in contract['checks'] if check['name'] == 'analytic_rubric_quality'))
        self.assertEqual(analytic_check['status'], 'pass')
        self.assertNotIn('capability_selector_contract_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_blocks_orphaned_capsules_when_manifest_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'orphaned-capsule-skill'
            references_dir = skill_dir / 'references'
            capsules_dir = references_dir / 'knowledge-capsules'
            capsules_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: orphaned-capsule-skill\ndescription: Use when a user asks to test capsule routing.\nversion: "1.0.0"\n---\n\n# Orphaned Capsule Skill\n\nSelect the task type before opening capsule bodies.\n\n## Progressive Disclosure\n- Read references/knowledge-capsule-routing.md before opening capsule bodies.\n- Read references/knowledge-capsules/<capsule>.md only through the routing table.\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test complete capability selector.\ninputs:\n  - user_request\n  - task_type\noutputs:\n  - result\n  - task_type\nquality_criteria:\n  task_type_selection:\n    alpha: alpha task\n    beta: beta task\n  result_quality:\n    purpose: Measures whether the skill returns the selected task result.\n    why_it_matters: Selector skills must prove that the selected capability changes the output.\n    observable_evidence:\n      - The result names the selected task type.\n      - The result cites selector evidence.\n    scoring:\n      5: Selects the task type, returns the matching result, and cites evidence.\n      4: Selects the task type and returns the matching result with minor evidence gaps.\n      3: Returns a plausible result but leaves selector evidence partly implicit.\n      2: Mentions a task type but does not use it to shape the result.\n      1: Does not select or apply a task type.\nautomatic_failure_conditions:\n  - Missing or contradictory task type selection.\nevidence_requirements:\n  - Selection decisions must cite the selected task type and evidence.\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule-routing.md').write_text('# Capsule Routing\n\nUse references/knowledge-capsules/routed.md for alpha tasks.\n', encoding='utf-8')
            (references_dir / 'knowledge-capsule.manifest.yaml').write_text('schema_version: knowledge-os.knowledge-capsule-manifest.v1\nselected_facets:\n  - pack.example:alpha\n  - pack.example:beta\n', encoding='utf-8')
            (capsules_dir / 'routed.md').write_text('# Routed\n', encoding='utf-8')
            (capsules_dir / 'orphaned.md').write_text('# Orphaned\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        orphan_check = next((check for check in contract['checks'] if check['name'] == 'orphaned_bundle_reference'))
        self.assertEqual(orphan_check['status'], 'blocked_validation')
        self.assertEqual(orphan_check['orphaned_paths'], ['Skills/agent-ops/orphaned-capsule-skill/references/knowledge-capsules/orphaned.md'])
        self.assertIn('orphaned_bundle_reference', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_writing_quality_accepts_routed_eval_and_scorer_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'routed-eval-bundle-skill'
            references_dir = skill_dir / 'references'
            evals_dir = references_dir / 'evals'
            scorer_dir = references_dir / 'scorer-calibration'
            raw_dir = scorer_dir / 'raw'
            raw_dir.mkdir(parents=True)
            evals_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: routed-eval-bundle-skill\ndescription: Use when a user asks to validate routed eval bundle support files.\nmetadata:\n  skill-type: runbook\n  lifecycle_state: active\n  metadata_source: frontmatter\n---\n\n# Routed Eval Bundle Skill\n\nShort purpose paragraph.\n\n## When To Use\n\n- Use when testing eval bundle routing.\n\n## Inputs\n\n- Target path.\n\n## Outputs\n\n- Report.\n\n## Workflow\n\n1. Inspect the target.\n\n## Failure Mode\n\n- Stop with the blocker.\n\n## Validation\n\n- ./bin/ask sdk eval scenario-quality Skills/agent-ops/routed-eval-bundle-skill --preview --json --robot\n\n## References\n\n- references/evals.yaml\n- references/scorer-calibration/manifest.json\n', encoding='utf-8')
            (references_dir / 'evals.yaml').write_text('claims:\n  - id: routed-eval\ncases:\n  - id: routed-eval\n', encoding='utf-8')
            (evals_dir / 'eval.routed-eval.md').write_text('# Routed Eval\n', encoding='utf-8')
            (scorer_dir / 'manifest.json').write_text('{\n  "schema_version": "skills-sdk.scorer-calibration-bundle.v1",\n  "examples_path": "examples.jsonl",\n  "raw_artifacts_dir": "raw"\n}\n', encoding='utf-8')
            (scorer_dir / 'examples.jsonl').write_text('{}\n', encoding='utf-8')
            (raw_dir / 'example.json').write_text('{}\n', encoding='utf-8')
            progressive = package_contracts.progressive_disclosure_contract(repo_root, skill_md, skill_md.read_text(encoding='utf-8'))
            contract = package_contracts.writing_quality_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md), skill_md.read_text(encoding='utf-8'), progressive)
        advisory_ids = {advisory['rule_id'] for advisory in contract['advisories']}
        self.assertNotIn('orphaned_bundle_reference', advisory_ids)

    def test_reference_quality_accepts_centralized_gold_rubric_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            central_rubric = repo_root / 'Infrastructure' / 'config' / 'skills-sdk'
            central_rubric.mkdir(parents=True)
            (central_rubric / 'gold-standard-rubric.v1.json').write_text('{\n  "schema_version": "skills-sdk.gold-standard-rubric.v1",\n  "rubric_id": "skills-sdk.gold-standard.v1",\n  "quality_criteria": {\n    "trigger_boundary": {\n      "purpose": "Measures whether the skill selects the right work.",\n      "why_it_matters": "Incorrect routing makes later evidence meaningless.",\n      "observable_evidence": [\n        "The description names trigger and non-trigger cases."\n      ],\n      "scoring": {\n        "5": "Trigger and non-trigger behavior are explicit and covered.",\n        "4": "Trigger behavior is clear with minor edge ambiguity.",\n        "3": "Common cases route correctly but adjacent work can over-trigger.",\n        "2": "Triggering relies on broad keywords.",\n        "1": "The skill cannot be selected predictably."\n      }\n    }\n  },\n  "automatic_failure_conditions": [\n    "Missing package purpose, inputs, or outputs."\n  ]\n}\n', encoding='utf-8')
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'central-rubric-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: central-rubric-skill\ndescription: Use when a user asks to test centralized rubric profiles.\nversion: "1.0.0"\n---\n\n# Central Rubric Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('rubric_profile: skills-sdk.gold-standard.v1\npurpose: Test centralized rubric profiles.\ninputs:\n  - user_request\n  - capability\noutputs:\n  - result\n  - capability\ncapability_selection:\n  alpha: alpha task\nquality_criteria:\n  capability_selection:\n    alpha: alpha task\nevidence_requirements:\n  - Selection decisions must cite the selected capability.\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        basic_check = next((check for check in contract['checks'] if check['name'] == 'basic_requirement_rubric'))
        self.assertEqual(basic_check['status'], 'pass')
        self.assertEqual(basic_check['rubric_profiles'], ['skills-sdk.gold-standard.v1'])
        analytic_check = next((check for check in contract['checks'] if check['name'] == 'analytic_rubric_quality'))
        self.assertEqual(analytic_check['status'], 'pass')
        self.assertIn('trigger_boundary', analytic_check['criteria_checked'])
        self.assertNotIn('analytic_rubric_quality_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_scenario_case_fallback_ignores_nested_list_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evals_path = Path(temp_dir) / 'evals.yaml'
            evals_path.write_text('schema_version: "2.0"\ncases:\n- id: first-case\n  category: happy\n  eval_modes:\n  - smoke\n  prompt: First prompt.\n  task: First task.\n  given: First given.\n  should: First should.\n  acceptance:\n  - type: expected_signal\n    value: First evidence.\n  deterministic_checks:\n    forbidden_commands:\n    - curl\n- id: second-case\n  category: negative\n  eval_modes:\n  - release\n  prompt: Second prompt.\n  task: Second task.\n  given: Second given.\n  should: Second should.\n  acceptance:\n  - type: not_regex\n    value: "(?i)code"\n  deterministic_checks:\n    forbidden_commands:\n    - rm -rf\n', encoding='utf-8')
            cases = package_contracts._scenario_cases_from_reference(evals_path, {'cases': []})
        self.assertEqual([case['id'] for case in cases], ['first-case', 'second-case'])
        self.assertEqual(cases[0]['eval_modes'], ['smoke'])
        self.assertEqual(cases[1]['acceptance'][0], 'type: not_regex')

    def test_reference_quality_validates_scenario_drift_review_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'scenario-policy-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: scenario-policy-skill\ndescription: Scenario policy fixture.\nversion: "1.0.0"\n---\n\n# Scenario Policy Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test scenario drift metadata shape.\ninputs:\n  - skill changes\noutputs:\n  - scenario review decision\ntessl_scenario_policy:\n  structure_only: false\n  scenario_drift_review:\n    required_after_skill_change: "yes"\n    review_decisions: keep\n    review_surfaces:\n      - ""\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        drift_check = next((check for check in contract['checks'] if check['name'] == 'tessl_scenario_drift_review'))
        self.assertEqual(drift_check['status'], 'blocked_validation')
        self.assertEqual(drift_check['missing'], ['required_after_skill_change', 'review_decisions', 'review_surfaces'])
        self.assertIn('tessl_scenario_drift_review_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_requires_complete_scenario_drift_review_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'partial-scenario-policy-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: partial-scenario-policy-skill\ndescription: Partial scenario policy fixture.\nversion: "1.0.0"\n---\n\n# Partial Scenario Policy Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test complete scenario drift metadata semantics.\ninputs:\n  - skill changes\noutputs:\n  - scenario review decision\ntessl_scenario_policy:\n  structure_only: false\n  scenario_drift_review:\n    required_after_skill_change: true\n    review_decisions:\n      - keep\n    review_surfaces:\n      - SKILL.md\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        drift_check = next((check for check in contract['checks'] if check['name'] == 'tessl_scenario_drift_review'))
        self.assertEqual(drift_check['status'], 'blocked_validation')
        self.assertEqual(drift_check['missing'], ['review_decisions', 'review_surfaces'])

    def test_reference_quality_honors_structure_check_only_scenario_policy_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'structure-check-only-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: structure-check-only-skill\ndescription: Structure-only scenario policy fixture.\nversion: "1.0.0"\n---\n\n# Structure Check Only Skill\n', encoding='utf-8')
            (references_dir / 'contract.yaml').write_text('purpose: Test structure_check_only scenario policy alias.\ninputs:\n  - skill structure\noutputs:\n  - structure validation result\ntessl_scenario_policy:\n  structure_check_only: true\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        drift_checks = [check for check in contract['checks'] if check['name'] == 'tessl_scenario_drift_review']
        self.assertEqual(drift_checks, [])
        self.assertNotIn('tessl_scenario_drift_review_missing', {blocker['rule_id'] for blocker in contract['blockers']})

    def test_reference_quality_skips_hidden_platform_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'hidden-file-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: hidden-file-skill\ndescription: Hidden reference fixture.\n---\n\n# Hidden File Skill\n', encoding='utf-8')
            (references_dir / '.DS_Store').write_bytes(b'\xff\x00binary')
            (references_dir / 'details.md').write_text('# Hidden File Skill Details\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        paths = {check.get('path') for check in contract['checks']}
        self.assertNotIn('Skills/agent-ops/hidden-file-skill/references/.DS_Store', paths)
        self.assertIn('Skills/agent-ops/hidden-file-skill/references/details.md', paths)
        self.assertEqual(contract['status'], 'pass')

    def test_reference_quality_blocks_non_invocable_markdown_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'capsule-heading-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: capsule-heading-skill\ndescription: Capsule heading fixture.\n---\n\n# Capsule Heading Skill\n', encoding='utf-8')
            (references_dir / 'capsule-routing.md').write_text('# Details\n\nRoute this capsule for routing tasks.\n', encoding='utf-8')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        heading_check = next((check for check in contract['checks'] if check['name'] == 'reference_heading_invocable'))
        self.assertEqual(heading_check['status'], 'blocked_validation')
        self.assertEqual(heading_check['path'], 'Skills/agent-ops/capsule-heading-skill/references/capsule-routing.md')
        self.assertIn('reference_heading_not_invocable', {blocker['rule_id'] for blocker in contract['blockers']})
        self.assertEqual(contract['status'], 'blocked_validation')

    def test_reference_quality_blocks_non_utf8_reference_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'binary-reference-skill'
            references_dir = skill_dir / 'references'
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('---\nname: binary-reference-skill\ndescription: Binary reference fixture.\n---\n\n# Binary Reference Skill\n', encoding='utf-8')
            (references_dir / 'details.md').write_text('# Details\n', encoding='utf-8')
            (references_dir / 'bad.md').write_bytes(b'\xff\x00binary')
            contract = package_contracts.reference_quality_contract(repo_root, skill_md)
        blockers = {blocker['path']: blocker for blocker in contract['blockers']}
        self.assertIn('Skills/agent-ops/binary-reference-skill/references/bad.md', blockers)
        self.assertEqual(contract['status'], 'blocked_validation')

    def test_sdk_contract_missing_files_block_install_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'packaged-skill'
            skill_dir.mkdir(parents=True)
            (skill_dir / 'SKILL.md').write_text('---\nname: packaged-skill\ndescription: Packaged skill fixture.\nversion: "2.0.0"\nmetadata:\n  compatible_roles:\n    - worker\n  runtime_needs:\n    - filesystem\n  maturity: beta\n  provenance: internal\n  share_readiness: ready\n---\n\n# Packaged Skill\n', encoding='utf-8')
            package = skills_package(repo_root, 'Skills/agent-ops/packaged-skill', strict=True).data['skill_package']
        summary = package['readiness_summary']
        self.assertEqual(summary['missing_fields'], [])
        self.assertIn('agent_metadata', summary['sdk_contract_missing_fields'])
        self.assertIn('reference_contract', summary['sdk_contract_missing_fields'])
        self.assertIn('task_profile', summary['sdk_contract_missing_fields'])
        self.assertFalse(package['gate_summary']['install_ready'])
        self.assertIn('sdk_contract:agent_metadata', package['gate_summary']['blocked_reasons'])

    def test_package_readiness_schema_requires_sdk_contract(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        package['package_contract'].pop('sdk_contract')
        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(self.schemas['skill-package-readiness.v1.schema.json'], package, self.schemas)
        self.assertIn("missing required key 'sdk_contract'", str(context.exception))

    def test_reference_contract_fallback_supports_sdk_fields_without_pyyaml(self) -> None:
        skill_md = REPO_ROOT / 'Plugins' / 'skill-factory' / 'skills' / 'skill-factory-router' / 'SKILL.md'
        with patch.object(package_contracts, 'yaml', None):
            contract = package_contracts.sdk_package_contract(REPO_ROOT, skill_md, read_skill_frontmatter_fields(skill_md))
        self.assertEqual(contract['values']['purpose'], 'Route skill lifecycle requests to exactly one skill-factory lane before execution.')
        self.assertIn('inputs', contract['required_fields']['present'])
        self.assertIn('outputs', contract['required_fields']['present'])
        self.assertEqual(contract['values']['permission_profile']['filesystem']['write'], [])
        self.assertTrue(contract['progressive_disclosure']['references_contract_declared'])

    def test_knowledge_capsule_contract_requires_first_party_routing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'capsule-skill'
            references = skill_dir / 'references'
            references.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('# Capsule Skill\n\nLoad references/knowledge-capsule-routing.md before capsule bodies.\n', encoding='utf-8')
            (references / 'knowledge-capsule.manifest.yaml').write_text('capsules:\n  - target_path: references/knowledge-capsules/one.md\n    facet_id: one\n', encoding='utf-8')
            (references / 'knowledge-capsule-routing.md').write_text('# Knowledge Capsule Routing\n\n- references/knowledge-capsules/one.md\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        self.assertTrue(contract['knowledge_capsules']['manifest_declared'])
        self.assertTrue(contract['knowledge_capsules']['ready'])
        self.assertEqual(contract['knowledge_capsules']['capsule_paths'], ['references/knowledge-capsules/one.md'])

    def test_knowledge_capsule_contract_blocks_unsafe_target_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'capsule-skill'
            references = skill_dir / 'references'
            references.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('# Capsule Skill\n\nLoad references/knowledge-capsule-routing.md before capsule bodies.\n', encoding='utf-8')
            (references / 'knowledge-capsule.manifest.yaml').write_text('capsules:\n  - target_path: /tmp/outside.md\n    facet_id: outside\n', encoding='utf-8')
            (references / 'knowledge-capsule-routing.md').write_text('# Knowledge Capsule Routing\n\n- /tmp/outside.md\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        self.assertTrue(contract['knowledge_capsules']['manifest_declared'])
        self.assertFalse(contract['knowledge_capsules']['ready'])
        self.assertEqual(contract['knowledge_capsules']['unsafe_capsule_paths'], ['/tmp/outside.md'])

    def test_knowledge_capsule_contract_warns_when_routing_is_buried(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'capsule-skill'
            references = skill_dir / 'references'
            references.mkdir(parents=True)
            skill_md = skill_dir / 'SKILL.md'
            skill_md.write_text('# Capsule Skill\n\nLoad the manifest when needed.\n', encoding='utf-8')
            (references / 'knowledge-capsule.manifest.yaml').write_text('capsules:\n  - target_path: references/knowledge-capsules/one.md\n    facet_id: one\n', encoding='utf-8')
            contract = package_contracts.sdk_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
        self.assertEqual(contract['knowledge_capsules']['status'], 'advisory')
        self.assertTrue(contract['knowledge_capsules']['manifest_declared'])
        self.assertFalse(contract['knowledge_capsules']['ready'])

    def test_knowledge_capsules_block_package_readiness_when_declared_but_not_routed(self) -> None:
        frontmatter = {'name': 'capsule-blocked-skill', 'description': 'Capsule blocked skill fixture.', 'metadata': {'version': '1.0.0', 'compatible_roles': ['worker'], 'runtime_needs': ['filesystem'], 'maturity': 'beta', 'provenance': 'internal', 'share_readiness': 'ready'}}
        sdk_contract = {'required_fields': {'missing': []}, 'values': {'workflow_contract': {'status': 'pass'}, 'optimization_contract': {'status': 'pass'}, 'reference_quality': {'status': 'pass', 'required_for_package_readiness': True}}, 'knowledge_capsules': {'manifest_declared': True, 'ready': False}}
        with patch.object(package_contracts, 'sdk_package_contract', return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)
        self.assertEqual(package['readiness_level'], 'knowledge_capsules_incomplete')
        self.assertIn('knowledge_capsules:first_party_routing_incomplete', package['install_gate']['blocked_reasons'])

    def test_package_readiness_schema_rejects_payload_without_snapshot_identity(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        package.pop('compatibility_snapshot')
        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(self.schemas['skill-package-readiness.v1.schema.json'], package, self.schemas)
        self.assertIn("missing required key 'compatibility_snapshot'", str(context.exception))

    def test_package_readiness_schema_rejects_unknown_top_level_keys(self) -> None:
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        package['unexpected_contract_key'] = True
        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(self.schemas['skill-package-readiness.v1.schema.json'], package, self.schemas)
        self.assertIn('unexpected keys', str(context.exception))

    def test_package_public_output_matches_compatibility_snapshot(self) -> None:
        snapshots = _load_snapshot()
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'skill-factory-router', 'source_path': 'Plugins/skill-factory/skills/skill-factory-router/SKILL.md'}):
            valid_package = skills_package(REPO_ROOT, 'skill-factory-router').data['skill_package']
        with patch('ask.commands.skills_impl.resolve_skill_handle', return_value={'status': 'ok', 'handle': 'missing-skill', 'source_path': 'Skills/agent-ops/missing-skill/SKILL.md'}):
            missing_package = skills_package(REPO_ROOT, 'missing-skill').data['skill_package']
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / 'Skills' / 'agent-ops' / 'packaged-skill'
            skill_dir.mkdir(parents=True)
            (skill_dir / 'SKILL.md').write_text('---\nversion: "2.0.0"\nmetadata:\n  compatible_roles:\n    - worker\n  runtime_needs:\n    - filesystem\n  maturity: beta\n  provenance: internal\n  share_readiness: ready\n---\n\n# Packaged Skill\n', encoding='utf-8')
            strict_incomplete_package = skills_package(repo_root, 'Skills/agent-ops/packaged-skill', strict=True).data['skill_package']
        self.assertEqual({'valid_share_ready_package': _snapshot_projection(valid_package), 'missing_source_package': _snapshot_projection(missing_package), 'strict_incomplete_package': _snapshot_projection(strict_incomplete_package)}, snapshots)
