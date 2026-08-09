from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_sdk_contract_reports_missing_progressive_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "missing-ref-skill"
            skill_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: missing-ref-skill
description: Missing reference fixture.
---

# Missing Reference Skill

## Progressive Disclosure

- Read `references/missing.md` for task-specific detail.
""",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        progressive = contract["progressive_disclosure"]
        self.assertEqual(
            progressive["progressive_disclosure_missing_references"],
            ["references/missing.md"],
        )
        self.assertFalse(progressive["progressive_disclosure_ready"])

    def test_sdk_contract_requires_format_docs_for_operating_model_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "github" / "teach-like"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: teach-like
description: Teaching fixture.
---

# Teach Like

## Inputs

- Workspace files: MISSION.md, RESOURCES.md, GLOSSARY.md, and learning-records/*.md.

## Progressive Disclosure

- Read `references/templates.md` for compact artifact shapes.
""",
                encoding="utf-8",
            )
            (references_dir / "templates.md").write_text("# Templates\n", encoding="utf-8")

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

            progressive = contract["progressive_disclosure"]
            formats = progressive["operating_model_formats"]
            self.assertEqual(
                formats["missing_format_references"],
                [
                    "references/mission-format.md",
                    "references/resources-format.md",
                    "references/glossary-format.md",
                    "references/learning-record-format.md",
                ],
            )
            self.assertFalse(formats["format_references_ready"])
            self.assertFalse(progressive["progressive_disclosure_ready"])

            for filename in (
                "mission-format.md",
                "resources-format.md",
                "glossary-format.md",
                "learning-record-format.md",
            ):
                (references_dir / filename).write_text(f"# {filename}\n", encoding="utf-8")

            fixed = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        fixed_formats = fixed["progressive_disclosure"]["operating_model_formats"]
        self.assertEqual(fixed_formats["missing_format_references"], [])
        self.assertTrue(fixed_formats["format_references_ready"])
        self.assertTrue(fixed["progressive_disclosure"]["progressive_disclosure_ready"])

    def test_sdk_contract_rejects_progressive_paths_outside_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "escape-ref-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: escape-ref-skill
description: Escape reference fixture.
---

# Escape Reference Skill

## Progressive Disclosure

- Read `references/../outside.md` for task-specific detail.
""",
                encoding="utf-8",
            )
            (skill_dir / "outside.md").write_text("# Outside\n", encoding="utf-8")

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        progressive = contract["progressive_disclosure"]
        self.assertEqual(
            progressive["progressive_disclosure_missing_references"],
            ["references/../outside.md"],
        )
        self.assertFalse(progressive["progressive_disclosure_ready"])

    def test_sdk_contract_requires_source_operating_model_progressive_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "github" / "sourceful-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: sourceful-skill
description: Preserve source operating model fixture.
metadata:
  version: "1.0.0"
  compatible_roles:
    - default
  runtime_needs:
    - local files
  maturity: stable
  provenance: test fixture
  share_readiness: ready
---

# Sourceful Skill

## Progressive Disclosure

- Read `references/templates.md` for compact artifact shapes.
""",
                encoding="utf-8",
            )
            (references_dir / "templates.md").write_text("# Templates\n", encoding="utf-8")
            (references_dir / "teaching-operating-model.md").write_text(
                "# Teaching Operating Model\n",
                encoding="utf-8",
            )
            (references_dir / "source-context.yaml").write_text(
                """schema_version: 1
references:
  - path: references/teaching-operating-model.md
    kind: source_operating_model
    provenance: upstream source
    load_when: creating lessons
""",
                encoding="utf-8",
            )

            contract = package_contracts.skill_package_readiness(
                read_skill_frontmatter_fields(skill_md),
                repo_root,
                skill_md,
            )

            source_model = contract["sdk_contract"]["progressive_disclosure"][
                "source_operating_model"
            ]
            self.assertEqual(source_model["status"], "blocked_validation")
            self.assertEqual(
                source_model["missing_progressive_routes"],
                ["references/teaching-operating-model.md"],
            )
            self.assertIn(
                "progressive_disclosure:source_operating_model_preservation",
                contract["install_gate"]["blocked_reasons"],
            )

            skill_md.write_text(
                skill_md.read_text(encoding="utf-8")
                + "- Read `references/teaching-operating-model.md` before creating lessons.\n",
                encoding="utf-8",
            )

            fixed = package_contracts.skill_package_readiness(
                read_skill_frontmatter_fields(skill_md),
                repo_root,
                skill_md,
            )

        fixed_source_model = fixed["sdk_contract"]["progressive_disclosure"][
            "source_operating_model"
        ]
        self.assertEqual(fixed_source_model["status"], "pass")
        self.assertEqual(fixed_source_model["missing_progressive_routes"], [])
        self.assertNotIn(
            "progressive_disclosure:source_operating_model_preservation",
            fixed["install_gate"]["blocked_reasons"],
        )

    def test_sdk_contract_reports_identity_and_asset_browseability(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "identity-skill"
            references_dir = skill_dir / "references"
            scripts_dir = skill_dir / "scripts"
            references_dir.mkdir(parents=True)
            scripts_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: identity-skill
description: Create reliable package identity checks when validating skill assets.
short_description: Check skill package identity
---

# Identity Skill
""",
                encoding="utf-8",
            )
            (references_dir / "gold-contract.md").write_text(
                "# Gold Contract\n\nPurposeful reference detail.\n",
                encoding="utf-8",
            )
            (references_dir / "held-out-examples.jsonl").write_text(
                '{"description":"Purpose: held-out scorer calibration example.","id":"case-1"}\n',
                encoding="utf-8",
            )
            (scripts_dir / "run-checks.py").write_text(
                "\"\"\"Purpose: run the package identity fixture check.\"\"\"\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        identity = contract["identity_and_assets"]
        self.assertTrue(identity["ready"])
        self.assertTrue(identity["skill_identity"]["name_kebab_case"])
        self.assertTrue(identity["skill_identity"]["name_matches_directory"])
        self.assertTrue(identity["skill_identity"]["description_has_action_term"])
        self.assertTrue(identity["reference_inventory"]["ready"])
        self.assertTrue(identity["script_inventory"]["ready"])

    def test_sdk_contract_accepts_multiline_script_docstring_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "script-docstring-skill"
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: script-docstring-skill
description: Create reliable script description checks for package validation.
---

# Script Docstring Skill
""",
                encoding="utf-8",
            )
            (scripts_dir / "run-checks.py").write_text(
                "\"\"\"\nPurpose: run the package script fixture check.\n\"\"\"\nprint('ok')\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        scripts = contract["identity_and_assets"]["script_inventory"]
        self.assertTrue(scripts["ready"])
        self.assertEqual(scripts["missing_descriptions"], [])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_sdk_contract_blocks_symlinked_support_files_without_reading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "symlink-support-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            outside = repo_root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            try:
                (references_dir / "outside-link.md").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: symlink-support-skill
description: Create reliable symlink blocking checks for package validation.
---

# Symlink Support Skill
""",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        references = contract["identity_and_assets"]["reference_inventory"]
        self.assertFalse(references["ready"])
        self.assertEqual(references["count"], 0)
        self.assertIn(
            "Skills/agent-ops/symlink-support-skill/references/outside-link.md",
            references["unsafe_paths"],
        )

    def test_sdk_contract_reports_identity_and_asset_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "bad-skill"
            references_dir = skill_dir / "references"
            scripts_dir = skill_dir / "scripts"
            references_dir.mkdir(parents=True)
            scripts_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: Bad Skill
description: sample
---

# Bad Skill
""",
                encoding="utf-8",
            )
            (references_dir / "details.md").write_text(
                "No title here.\n",
                encoding="utf-8",
            )
            (references_dir / "undocumented-examples.jsonl").write_text(
                '{"id":"case-1"}\n',
                encoding="utf-8",
            )
            (scripts_dir / "RunChecks.py").write_text(
                "print('missing purpose metadata')\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        identity = contract["identity_and_assets"]
        self.assertFalse(identity["ready"])
        self.assertFalse(identity["skill_identity"]["name_kebab_case"])
        self.assertFalse(identity["skill_identity"]["name_matches_directory"])
        self.assertFalse(identity["skill_identity"]["description_length_ok"])
        self.assertFalse(identity["skill_identity"]["description_has_action_term"])
        self.assertIn(
            "Skills/agent-ops/bad-skill/references/details.md",
            identity["reference_inventory"]["generic_names"],
        )
        self.assertIn(
            "Skills/agent-ops/bad-skill/references/details.md",
            identity["reference_inventory"]["missing_descriptions"],
        )
        self.assertIn(
            "Skills/agent-ops/bad-skill/references/details.md",
            identity["reference_inventory"]["weak_headings"],
        )
        self.assertIn(
            "Skills/agent-ops/bad-skill/references/undocumented-examples.jsonl",
            identity["reference_inventory"]["missing_descriptions"],
        )
        self.assertIn(
            "Skills/agent-ops/bad-skill/scripts/RunChecks.py",
            identity["script_inventory"]["bad_names"],
        )
        self.assertIn(
            "Skills/agent-ops/bad-skill/scripts/RunChecks.py",
            identity["script_inventory"]["missing_descriptions"],
        )

    def test_reference_inventory_blocks_generic_markdown_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "weak-reference-heading"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: weak-reference-heading
description: Create reliable reference heading checks for package validation.
---

# Weak Reference Heading
""",
                encoding="utf-8",
            )
            (references_dir / "routing-boundary.md").write_text(
                "# Details\n\nReference content.\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        references = contract["identity_and_assets"]["reference_inventory"]
        self.assertFalse(references["ready"])
        self.assertEqual(
            references["weak_headings"],
            ["Skills/agent-ops/weak-reference-heading/references/routing-boundary.md"],
        )

    def test_reference_inventory_accepts_filename_aligned_markdown_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "strong-reference-heading"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: strong-reference-heading
description: Create reliable reference heading checks for package validation.
---

# Strong Reference Heading
""",
                encoding="utf-8",
            )
            (references_dir / "routing-boundary.md").write_text(
                "# Routing Boundary\n\nReference content.\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        references = contract["identity_and_assets"]["reference_inventory"]
        self.assertEqual(references["weak_headings"], [])
        self.assertEqual(references["missing_descriptions"], [])

    def test_reference_inventory_blocks_weak_top_level_capsule_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "weak-capsule-heading"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: weak-capsule-heading
description: Create reliable capsule heading checks for package validation.
---

# Weak Capsule Heading

## Progressive Disclosure

- Read references/knowledge-capsule-routing.md before opening capsule files.
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule.manifest.yaml").write_text(
                """schema_version: knowledge-os.knowledge-capsule-manifest.v1
capsules:
  - target_path: references/spec-first-demo.md
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule-routing.md").write_text(
                "# Knowledge Capsule Routing\n\n- references/spec-first-demo.md for spec-first demo coaching.\n",
                encoding="utf-8",
            )
            (references_dir / "spec-first-demo.md").write_text(
                "# Reference\n\nCapsule content.\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        references = contract["identity_and_assets"]["reference_inventory"]
        self.assertFalse(references["ready"])
        self.assertEqual(
            references["weak_headings"],
            ["Skills/agent-ops/weak-capsule-heading/references/spec-first-demo.md"],
        )

    def test_reference_inventory_accepts_invocable_top_level_capsule_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "strong-capsule-heading"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: strong-capsule-heading
description: Create reliable capsule heading checks for package validation.
---

# Strong Capsule Heading

## Progressive Disclosure

- Read references/knowledge-capsule-routing.md before opening capsule files.
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule.manifest.yaml").write_text(
                """schema_version: knowledge-os.knowledge-capsule-manifest.v1
capsules:
  - target_path: references/spec-first-demo.md
""",
                encoding="utf-8",
            )
            (references_dir / "knowledge-capsule-routing.md").write_text(
                "# Knowledge Capsule Routing\n\n- references/spec-first-demo.md for spec-first demo coaching.\n",
                encoding="utf-8",
            )
            (references_dir / "spec-first-demo.md").write_text(
                "# Spec First Demo\n\nCapsule content.\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        references = contract["identity_and_assets"]["reference_inventory"]
        self.assertEqual(references["weak_headings"], [])
        self.assertEqual(references["missing_descriptions"], [])
