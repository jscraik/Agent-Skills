from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_reference_quality_accepts_centralized_gold_rubric_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            central_rubric = repo_root / "Infrastructure" / "config" / "skills-sdk"
            central_rubric.mkdir(parents=True)
            (central_rubric / "gold-standard-rubric.v1.json").write_text(
                """{
  "schema_version": "skills-sdk.gold-standard-rubric.v1",
  "rubric_id": "skills-sdk.gold-standard.v1",
  "quality_criteria": {
    "trigger_boundary": {
      "purpose": "Measures whether the skill selects the right work.",
      "why_it_matters": "Incorrect routing makes later evidence meaningless.",
      "observable_evidence": [
        "The description names trigger and non-trigger cases."
      ],
      "scoring": {
        "5": "Trigger and non-trigger behavior are explicit and covered.",
        "4": "Trigger behavior is clear with minor edge ambiguity.",
        "3": "Common cases route correctly but adjacent work can over-trigger.",
        "2": "Triggering relies on broad keywords.",
        "1": "The skill cannot be selected predictably."
      }
    }
  },
  "automatic_failure_conditions": [
    "Missing package purpose, inputs, or outputs."
  ]
}
""",
                encoding="utf-8",
            )
            skill_dir = repo_root / "Skills" / "agent-ops" / "central-rubric-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: central-rubric-skill
description: Use when a user asks to test centralized rubric profiles.
version: "1.0.0"
---

# Central Rubric Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """rubric_profile: skills-sdk.gold-standard.v1
purpose: Test centralized rubric profiles.
inputs:
  - user_request
  - capability
outputs:
  - result
  - capability
capability_selection:
  alpha: alpha task
quality_criteria:
  capability_selection:
    alpha: alpha task
evidence_requirements:
  - Selection decisions must cite the selected capability.
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        basic_check = next(
            check for check in contract["checks"] if check["name"] == "basic_requirement_rubric"
        )
        self.assertEqual(basic_check["status"], "pass")
        self.assertEqual(basic_check["rubric_profiles"], ["skills-sdk.gold-standard.v1"])
        analytic_check = next(
            check for check in contract["checks"] if check["name"] == "analytic_rubric_quality"
        )
        self.assertEqual(analytic_check["status"], "pass")
        self.assertIn("trigger_boundary", analytic_check["criteria_checked"])
        self.assertNotIn(
            "analytic_rubric_quality_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_scenario_case_fallback_ignores_nested_list_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            evals_path = Path(temp_dir) / "evals.yaml"
            evals_path.write_text(
                """schema_version: "2.0"
cases:
- id: first-case
  category: happy
  eval_modes:
  - smoke
  prompt: First prompt.
  task: First task.
  given: First given.
  should: First should.
  acceptance:
  - type: expected_signal
    value: First evidence.
  deterministic_checks:
    forbidden_commands:
    - curl
- id: second-case
  category: negative
  eval_modes:
  - release
  prompt: Second prompt.
  task: Second task.
  given: Second given.
  should: Second should.
  acceptance:
  - type: not_regex
    value: "(?i)code"
  deterministic_checks:
    forbidden_commands:
    - rm -rf
""",
                encoding="utf-8",
            )

            cases = package_contracts._scenario_cases_from_reference(evals_path, {"cases": []})

        self.assertEqual([case["id"] for case in cases], ["first-case", "second-case"])
        self.assertEqual(cases[0]["eval_modes"], ["smoke"])
        self.assertEqual(cases[1]["acceptance"][0], "type: not_regex")

    def test_reference_quality_validates_scenario_drift_review_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "scenario-policy-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: scenario-policy-skill
description: Scenario policy fixture.
version: "1.0.0"
---

# Scenario Policy Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test scenario drift metadata shape.
inputs:
  - skill changes
outputs:
  - scenario review decision
tessl_scenario_policy:
  structure_only: false
  scenario_drift_review:
    required_after_skill_change: "yes"
    review_decisions: keep
    review_surfaces:
      - ""
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        drift_check = next(
            check for check in contract["checks"] if check["name"] == "tessl_scenario_drift_review"
        )
        self.assertEqual(drift_check["status"], "blocked_validation")
        self.assertEqual(
            drift_check["missing"],
            ["required_after_skill_change", "review_decisions", "review_surfaces"],
        )
        self.assertIn(
            "tessl_scenario_drift_review_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_requires_complete_scenario_drift_review_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "partial-scenario-policy-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: partial-scenario-policy-skill
description: Partial scenario policy fixture.
version: "1.0.0"
---

# Partial Scenario Policy Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test complete scenario drift metadata semantics.
inputs:
  - skill changes
outputs:
  - scenario review decision
tessl_scenario_policy:
  structure_only: false
  scenario_drift_review:
    required_after_skill_change: true
    review_decisions:
      - keep
    review_surfaces:
      - SKILL.md
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        drift_check = next(
            check for check in contract["checks"] if check["name"] == "tessl_scenario_drift_review"
        )
        self.assertEqual(drift_check["status"], "blocked_validation")
        self.assertEqual(drift_check["missing"], ["review_decisions", "review_surfaces"])

    def test_reference_quality_honors_structure_check_only_scenario_policy_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "structure-check-only-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: structure-check-only-skill
description: Structure-only scenario policy fixture.
version: "1.0.0"
---

# Structure Check Only Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """purpose: Test structure_check_only scenario policy alias.
inputs:
  - skill structure
outputs:
  - structure validation result
tessl_scenario_policy:
  structure_check_only: true
""",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        drift_checks = [
            check for check in contract["checks"] if check["name"] == "tessl_scenario_drift_review"
        ]
        self.assertEqual(drift_checks, [])
        self.assertNotIn(
            "tessl_scenario_drift_review_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_reference_quality_skips_hidden_platform_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "hidden-file-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: hidden-file-skill
description: Hidden reference fixture.
---

# Hidden File Skill
""",
                encoding="utf-8",
            )
            (references_dir / ".DS_Store").write_bytes(b"\xff\x00binary")
            (references_dir / "details.md").write_text(
                "# Hidden File Skill Details\n",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        paths = {check.get("path") for check in contract["checks"]}
        self.assertNotIn("Skills/agent-ops/hidden-file-skill/references/.DS_Store", paths)
        self.assertIn("Skills/agent-ops/hidden-file-skill/references/details.md", paths)
        self.assertEqual(contract["status"], "pass")

    def test_reference_quality_blocks_non_invocable_markdown_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "capsule-heading-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: capsule-heading-skill
description: Capsule heading fixture.
---

# Capsule Heading Skill
""",
                encoding="utf-8",
            )
            (references_dir / "capsule-routing.md").write_text(
                "# Details\n\nRoute this capsule for routing tasks.\n",
                encoding="utf-8",
            )

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        heading_check = next(
            check for check in contract["checks"] if check["name"] == "reference_heading_invocable"
        )
        self.assertEqual(heading_check["status"], "blocked_validation")
        self.assertEqual(
            heading_check["path"],
            "Skills/agent-ops/capsule-heading-skill/references/capsule-routing.md",
        )
        self.assertIn(
            "reference_heading_not_invocable",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )
        self.assertEqual(contract["status"], "blocked_validation")

    def test_reference_quality_blocks_non_utf8_reference_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "binary-reference-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: binary-reference-skill
description: Binary reference fixture.
---

# Binary Reference Skill
""",
                encoding="utf-8",
            )
            (references_dir / "details.md").write_text("# Details\n", encoding="utf-8")
            (references_dir / "bad.md").write_bytes(b"\xff\x00binary")

            contract = package_contracts.reference_quality_contract(repo_root, skill_md)

        blockers = {blocker["path"]: blocker for blocker in contract["blockers"]}
        self.assertIn("Skills/agent-ops/binary-reference-skill/references/bad.md", blockers)
        self.assertEqual(contract["status"], "blocked_validation")
