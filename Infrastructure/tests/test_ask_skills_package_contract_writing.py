from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_writing_quality_blocks_near_threshold_reference_backed_sprawl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "near-threshold-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            filler = "\n".join(f"Filler line {index}." for index in range(205))
            skill_md.write_text(
                f"""---
name: near-threshold-skill
description: Use when a user asks to run a near-threshold package fixture.
---

# Near Threshold Skill

## Workflow

Run the narrow fixture path.

{filler}

## Output Contract

- Report the fixture result.

## Validation

- Command: fixture check -> pass

## Progressive Disclosure

- Read `references/details.md` for task-specific detail.
""",
                encoding="utf-8",
            )
            (references_dir / "details.md").write_text(
                "# Hidden File Skill Details\n",
                encoding="utf-8",
            )

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

        progressive_check = next(
            check for check in contract["checks"] if check["name"] == "progressive_disclosure_rubric"
        )
        self.assertEqual(progressive_check["status"], "blocked_validation")
        self.assertGreater(progressive_check["evidence"]["line_count"], 220)
        self.assertTrue(progressive_check["evidence"]["over_near_threshold"])
        self.assertIn(
            "near_threshold_entrypoint_sprawl",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_accepts_evidence_contract_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "evidence-contract-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: evidence-contract-skill
description: Use when a user asks to test evidence contract completion criteria.
---

# Evidence Contract Skill

## Workflow

Run the fixture path.

## Evidence Contract

Report the command evidence and blocker class.

## Progressive Disclosure

- Read `references/details.md` for task-specific detail.
""",
                encoding="utf-8",
            )
            (references_dir / "details.md").write_text("# Details\n", encoding="utf-8")

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

        completion_check = next(
            check for check in contract["checks"] if check["name"] == "procedural_completion_criteria"
        )
        self.assertEqual(completion_check["status"], "pass")
        self.assertTrue(completion_check["evidence"]["evidence_contract_declared"])
        self.assertNotIn(
            "missing_completion_criterion",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_accepts_routed_validation_output_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "routed-output-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: routed-output-skill
description: Use when a user asks to test routed validation output criteria.
---

# Routed Output Skill

## Workflow

Run the fixture path.

## Progressive Disclosure

- Read `references/validation-and-output.md` for output and evidence fields.
""",
                encoding="utf-8",
            )
            (references_dir / "validation-and-output.md").write_text(
                "# Validation And Output\n\nReport command evidence.\n",
                encoding="utf-8",
            )

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

        completion_check = next(
            check for check in contract["checks"] if check["name"] == "procedural_completion_criteria"
        )
        self.assertEqual(completion_check["status"], "pass")
        self.assertTrue(completion_check["evidence"]["completion_reference_declared"])
        self.assertNotIn(
            "missing_completion_criterion",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_blocks_generic_trigger_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "generic-trigger-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: generic-trigger-skill
description: Use when a user asks for help with anything.
---

# Generic Trigger Skill

## Workflow

Run the fixture path.

## Output Contract

- Report the fixture result.
""",
                encoding="utf-8",
            )

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

        trigger_check = next(
            check for check in contract["checks"] if check["name"] == "construction_trigger_boundary"
        )
        self.assertEqual(trigger_check["status"], "blocked_validation")
        self.assertEqual(trigger_check["dimension"], "invocation")
        self.assertEqual(trigger_check["evidence"]["glossary_axis"], "Invocation")
        self.assertIn("anything", trigger_check["evidence"]["generic_trigger_terms"])
        self.assertIn(
            "construction_trigger_boundary_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_blocks_missing_steps_reference_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "structureless-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: structureless-skill
description: Use when a user asks to validate structure checks.
---

# Structureless Skill

This skill contains background material but no executable workflow section.

## Output Contract

- Report the fixture result.

## Progressive Disclosure

- Read references/details.md for task-specific detail.
""",
                encoding="utf-8",
            )
            (references_dir / "details.md").write_text("# Details\n", encoding="utf-8")

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

        structure_check = next(
            check for check in contract["checks"] if check["name"] == "construction_steps_reference_structure"
        )
        self.assertEqual(structure_check["status"], "blocked_validation")
        self.assertEqual(structure_check["dimension"], "information_hierarchy")
        self.assertEqual(structure_check["evidence"]["glossary_axis"], "Information Hierarchy")
        self.assertFalse(structure_check["evidence"]["procedural_heading_declared"])
        self.assertIn(
            "construction_steps_reference_structure_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_blocks_phase_steps_without_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "ungated-phase-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: ungated-phase-skill
description: Use when a user asks to plan phase based skill work.
---

# Ungated Phase Skill

## Workflow

- Phase one: gather the request.
- Phase two: write the answer.

## Output Contract

- Report the fixture result.
""",
                encoding="utf-8",
            )

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

        steering_check = next(
            check for check in contract["checks"] if check["name"] == "construction_steering_phase_gate"
        )
        self.assertEqual(steering_check["status"], "blocked_validation")
        self.assertEqual(steering_check["dimension"], "steering")
        self.assertEqual(steering_check["evidence"]["glossary_axis"], "Steering")
        self.assertTrue(steering_check["evidence"]["phase_like"])
        self.assertIn(
            "construction_steering_phase_gate_missing",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_blocks_sediment_and_duplicate_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "sediment-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            sediment = " ".join(
                [
                    "This package represents a thoughtful and comprehensive perspective on collaboration"
                    for _ in range(12)
                ]
            )
            duplicate = (
                "- Read references/details.md before creating the final report for the operator.\n"
            )
            references_dir = skill_dir / "references"
            references_dir.mkdir()
            (references_dir / "details.md").write_text("# Details\n", encoding="utf-8")
            skill_md.write_text(
                f"""---
name: sediment-skill
description: Use when a user asks to validate pruning checks.
---

# Sediment Skill

{sediment}

## Workflow

- Run the fixture path.
{duplicate}{duplicate}

## Output Contract

- Report the fixture result.
""",
                encoding="utf-8",
            )

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

        pruning_check = next(
            check for check in contract["checks"] if check["name"] == "construction_pruning_sediment"
        )
        self.assertEqual(pruning_check["status"], "blocked_validation")
        self.assertEqual(pruning_check["dimension"], "pruning")
        self.assertEqual(pruning_check["evidence"]["glossary_axis"], "Pruning")
        self.assertTrue(pruning_check["evidence"]["long_paragraphs_without_behavior"])
        self.assertTrue(pruning_check["evidence"]["duplicate_instruction_lines"])
        blocker_ids = {blocker["rule_id"] for blocker in contract["blockers"]}
        self.assertIn("construction_sediment_paragraph", blocker_ids)
        self.assertIn("construction_duplicate_instruction", blocker_ids)

    def test_writing_quality_blocks_three_way_boundary_fragmentation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "fragmented-boundary-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: fragmented-boundary-skill
description: Use when a user asks to validate fragmented boundary checks.
---

# Fragmented Boundary Skill

## Workflow

1. Inspect the target and report command evidence.

## Constraints

- Keep the audit read-only.

## Execution Boundaries

- Use target repo commands as authority.

## Failure Mode

- Stop with the blocker.

## Validation

- Command: fixture check -> pass

""",
                encoding="utf-8",
            )

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

        fragmentation_check = next(
            check for check in contract["checks"] if check["name"] == "construction_boundary_fragmentation"
        )
        self.assertEqual(fragmentation_check["status"], "blocked_validation")
        self.assertEqual(fragmentation_check["dimension"], "pruning")
        self.assertEqual(
            fragmentation_check["evidence"]["fragmented_sections"],
            ["Constraints", "Execution Boundaries", "Validation"],
        )
        self.assertIn(
            "construction_boundary_fragmentation",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_blocks_extra_headers_for_sdk_managed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "extra-header-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: extra-header-skill
description: Use when a user asks to validate canonical skill headers.
metadata:
  skill-type: runbook
  lifecycle_state: active
  metadata_source: frontmatter
---

# Extra Header Skill

Short purpose paragraph.

## Principle

Keep the entrypoint small.

## When To Use

- Use when testing canonical headers.

## Inputs

- Target path.

## Outputs

- Report.

## Workflow

1. Inspect the target.

## Failure Mode

- Stop with the blocker.

## Validation

- Command: fixture check -> pass

## References

- No references.
""",
                encoding="utf-8",
            )

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

        header_check = next(
            check for check in contract["checks"] if check["name"] == "canonical_skill_headers"
        )
        self.assertEqual(header_check["status"], "blocked_validation")
        self.assertEqual(header_check["evidence"]["extra_h2_headings"], ["Principle"])
        self.assertIn(
            "canonical_skill_headers_required",
            {blocker["rule_id"] for blocker in contract["blockers"]},
        )

    def test_writing_quality_accepts_canonical_headers_for_sdk_managed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "canonical-header-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: canonical-header-skill
description: Use when a user asks to validate canonical skill headers.
metadata:
  skill-type: runbook
  lifecycle_state: active
  metadata_source: frontmatter
---

# Canonical Header Skill

Short purpose paragraph.

## When To Use

- Use when testing canonical headers.

## Inputs

- Target path.

## Outputs

- Report.

## Workflow

1. Inspect the target.

## Failure Mode

- Stop with the blocker.

## Validation

- Command: fixture check -> pass

## References

- No references.
""",
                encoding="utf-8",
            )

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

        header_check = next(
            check for check in contract["checks"] if check["name"] == "canonical_skill_headers"
        )
        self.assertEqual(header_check["status"], "pass")
        self.assertEqual(header_check["evidence"]["missing_headers"], [])
        self.assertEqual(header_check["evidence"]["extra_h2_headings"], [])
