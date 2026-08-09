from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_reference_quality_requires_capability_selector_for_multi_facet_capsules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "multi-facet-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: multi-facet-skill
description: Multi facet fixture.
version: "1.0.0"
---

# Multi Facet Skill

## Progressive Disclosure
- references/knowledge-capsules/example-a.md
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test missing capability selector.
inputs:
  - user_request
outputs:
  - result
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule.manifest.yaml").write_text(
                """schema_version: knowledge-os.knowledge-capsule-manifest.v1
selected_facets:
  - pack.example:alpha
  - pack.example:beta
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        selector_check = next(
            check for check in contract["checks"] if check["name"] == "capability_selector_contract"
        )
        self.assertEqual(selector_check["status"], "blocked_validation")
        self.assertEqual(
            selector_check["missing"],
            [
                "knowledge-capsule-routing.md",
                "capability_selection",
                "progressive_disclosure_named_capsules",
            ],
        )
        self.assertIn(
            "capability_selector_contract_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )
        self.assertIn(
            "basic_requirement_rubric_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_requires_basic_requirement_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "rubricless-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: rubricless-skill
description: Rubricless fixture.
version: "1.0.0"
---

# Rubricless Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test missing rubric contract.
inputs:
  - user request
outputs:
  - result
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        rubric_check = next(
            check for check in contract["checks"] if check["name"] == "basic_requirement_rubric"
        )
        self.assertEqual(rubric_check["status"], "blocked_validation")
        self.assertEqual(
            rubric_check["missing"],
            ["quality_criteria", "evidence_requirements"],
        )
        self.assertIn(
            "basic_requirement_rubric_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_requires_analytic_rubric_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "weak-rubric-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: weak-rubric-skill
description: Weak rubric fixture.
version: "1.0.0"
---

# Weak Rubric Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test weak rubric contract.
inputs:
  - user request
outputs:
  - result
quality_criteria:
  result_quality:
    observable: result contains useful evidence
evidence_requirements:
  - Result cites evidence.
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        analytic_check = next(
            check for check in contract["checks"] if check["name"] == "analytic_rubric_quality"
        )
        self.assertEqual(analytic_check["status"], "blocked_validation")
        self.assertIn("quality_criteria.result_quality.purpose", analytic_check["missing"])
        self.assertIn("quality_criteria.result_quality.why_it_matters", analytic_check["missing"])
        self.assertIn("quality_criteria.result_quality.observable_evidence", analytic_check["missing"])
        self.assertIn("quality_criteria.result_quality.scoring", analytic_check["missing"])
        self.assertIn("automatic_failure_conditions", analytic_check["missing"])
        self.assertNotIn(
            "analytic_rubric_quality_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_blocks_analytic_rubric_shape_for_tessl_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "weak-tessl-rubric-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: weak-tessl-rubric-skill
description: Weak Tessl rubric fixture.
version: "1.0.0"
---

# Weak Tessl Rubric Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test weak Tessl rubric contract.
inputs:
  - user request
outputs:
  - result
quality_criteria:
  result_quality:
    observable: result contains useful evidence
evidence_requirements:
  - Result cites evidence.
tessl_scenario_policy:
  scenario_drift_review:
    required_after_skill_change: true
    review_decisions:
      - keep
      - update
      - add
      - remove
    review_surfaces:
      - references/evals.yaml
      - references/evals/*.md
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        analytic_check = next(
            check for check in contract["checks"] if check["name"] == "analytic_rubric_quality"
        )
        self.assertEqual(analytic_check["status"], "blocked_validation")
        self.assertIn(
            "analytic_rubric_quality_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_accepts_declared_capability_selector_for_multi_facet_capsules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "selector-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: selector-skill
description: Selector fixture.
version: "1.0.0"
---

# Selector Skill

Select the task type before opening capsule bodies.

## Progressive Disclosure
- references/knowledge-capsule-routing.md
- references/knowledge-capsule.manifest.yaml
- references/knowledge-capsules/<capsule>.md
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test complete capability selector.
inputs:
  - user_request
  - task_type
outputs:
  - result
  - task_type
quality_criteria:
  task_type_selection:
    alpha: alpha task
    beta: beta task
  result_quality:
    purpose: Measures whether the skill returns the selected task result.
    why_it_matters: Selector skills must prove that the selected capability changes the output.
    observable_evidence:
      - The result names the selected task type.
      - The result cites selector evidence.
    scoring:
      5: Selects the task type, returns the matching result, and cites evidence.
      4: Selects the task type and returns the matching result with minor evidence gaps.
      3: Returns a plausible result but leaves selector evidence partly implicit.
      2: Mentions a task type but does not use it to shape the result.
      1: Does not select or apply a task type.
automatic_failure_conditions:
  - Missing or contradictory task type selection.
evidence_requirements:
  - Selection decisions must cite the selected task type and evidence.
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule-routing.md").write_text(
                "# Capsule Routing\n\nRoute through the smallest selected capsule.\n",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule.manifest.yaml").write_text(
                """schema_version: knowledge-os.knowledge-capsule-manifest.v1
selected_facets:
  - pack.example:alpha
  - pack.example:beta
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        selector_check = next(
            check for check in contract["checks"] if check["name"] == "capability_selector_contract"
        )
        self.assertEqual(selector_check["status"], "pass")
        self.assertEqual(selector_check["selectors"], ["task_type_selection"])
        rubric_check = next(
            check for check in contract["checks"] if check["name"] == "basic_requirement_rubric"
        )
        self.assertEqual(rubric_check["status"], "pass")
        analytic_check = next(
            check for check in contract["checks"] if check["name"] == "analytic_rubric_quality"
        )
        self.assertEqual(analytic_check["status"], "pass")
        self.assertNotIn(
            "capability_selector_contract_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_blocks_orphaned_capsules_when_manifest_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "orphaned-capsule-skill"
            references_dir = skill_dir / "references"
            capsules_dir = references_dir / "knowledge-capsules"
            capsules_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: orphaned-capsule-skill
description: Use when a user asks to test capsule routing.
version: "1.0.0"
---

# Orphaned Capsule Skill

Select the task type before opening capsule bodies.

## Progressive Disclosure
- Read references/knowledge-capsule-routing.md before opening capsule bodies.
- Read references/knowledge-capsules/<capsule>.md only through the routing table.
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test complete capability selector.
inputs:
  - user_request
  - task_type
outputs:
  - result
  - task_type
quality_criteria:
  task_type_selection:
    alpha: alpha task
    beta: beta task
  result_quality:
    purpose: Measures whether the skill returns the selected task result.
    why_it_matters: Selector skills must prove that the selected capability changes the output.
    observable_evidence:
      - The result names the selected task type.
      - The result cites selector evidence.
    scoring:
      5: Selects the task type, returns the matching result, and cites evidence.
      4: Selects the task type and returns the matching result with minor evidence gaps.
      3: Returns a plausible result but leaves selector evidence partly implicit.
      2: Mentions a task type but does not use it to shape the result.
      1: Does not select or apply a task type.
automatic_failure_conditions:
  - Missing or contradictory task type selection.
evidence_requirements:
  - Selection decisions must cite the selected task type and evidence.
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule-routing.md").write_text(
                "# Capsule Routing\n\nUse references/knowledge-capsules/routed.md for alpha tasks.\n",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule.manifest.yaml").write_text(
                """schema_version: knowledge-os.knowledge-capsule-manifest.v1
selected_facets:
  - pack.example:alpha
  - pack.example:beta
""",
                encoding="utf-8",
            )
            (capsules_dir / "routed.md").write_text("# Routed\n", encoding="utf-8")
            (capsules_dir / "orphaned.md").write_text("# Orphaned\n", encoding="utf-8")

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        orphan_check = next(
            check for check in contract["checks"] if check["name"] == "orphaned_bundle_reference"
        )
        self.assertEqual(orphan_check["status"], "blocked_validation")
        self.assertEqual(
            orphan_check["orphaned_paths"],
            ["Skills/agent-ops/orphaned-capsule-skill/references/knowledge-capsules/orphaned.md"],
        )
        self.assertIn(
            "orphaned_bundle_reference",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_accepts_routed_eval_and_scorer_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "routed-eval-bundle-skill"
            references_dir = skill_dir / "references"
            evals_dir = references_dir / "evals"
            scorer_dir = references_dir / "scorer-calibration"
            raw_dir = scorer_dir / "raw"
            raw_dir.mkdir(parents=True)
            evals_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: routed-eval-bundle-skill
description: Use when a user asks to validate routed eval bundle support files.
metadata:
  skill-type: runbook
  lifecycle_state: active
  metadata_source: frontmatter
---

# Routed Eval Bundle Skill

Short purpose paragraph.

## When To Use

- Use when testing eval bundle routing.

## Inputs

- Target path.

## Outputs

- Report.

## Workflow

1. Inspect the target.

## Failure Mode

- Stop with the blocker.

## Validation

- ./bin/ask sdk eval scenario-quality Skills/agent-ops/routed-eval-bundle-skill --preview --json --robot

## References

- references/evals.yaml
- references/scorer-calibration/manifest.json
""",
                encoding="utf-8",
            )
            (references_dir / "evals.yaml").write_text(
                "claims:\n  - id: routed-eval\ncases:\n  - id: routed-eval\n",
                encoding="utf-8",
            )
            (evals_dir / "eval.routed-eval.md").write_text("# Routed Eval\n", encoding="utf-8")
            (scorer_dir / "manifest.json").write_text(
                """{
  "schema_version": "skills-sdk.scorer-calibration-bundle.v1",
  "examples_path": "examples.jsonl",
  "raw_artifacts_dir": "raw"
}
""",
                encoding="utf-8",
            )
            (scorer_dir / "examples.jsonl").write_text("{}\n", encoding="utf-8")
            (raw_dir / "example.json").write_text("{}\n", encoding="utf-8")

            progressive = package_contracts.progressive_disclosure_contract(
                repo_root,
                skill_md,
                skill_md.read_text(encoding="utf-8"),
            )
            contract = package_contracts.writing_quality_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
                skill_md.read_text(encoding="utf-8"),
                progressive,
            )

        advisory_ids = {advisory["rule_id"] for advisory in contract["advisories"]}
        self.assertNotIn("orphaned_bundle_reference", advisory_ids)
