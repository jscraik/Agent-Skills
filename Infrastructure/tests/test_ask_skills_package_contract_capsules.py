from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_sdk_contract_missing_files_block_install_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Packaged skill fixture.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            package = skills_package(
                repo_root,
                "Skills/agent-ops/packaged-skill",
                strict=True,
            ).data["skill_package"]

        summary = package["readiness_summary"]
        self.assertEqual(summary["missing_fields"], [])
        self.assertIn("agent_metadata", summary["sdk_contract_missing_fields"])
        self.assertIn("reference_contract", summary["sdk_contract_missing_fields"])
        self.assertIn("task_profile", summary["sdk_contract_missing_fields"])
        self.assertFalse(package["gate_summary"]["install_ready"])
        self.assertIn("sdk_contract:agent_metadata", package["gate_summary"]["blocked_reasons"])

    def test_package_readiness_schema_requires_sdk_contract(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]

        package["package_contract"].pop("sdk_contract")

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(
                self.schemas["skill-package-readiness.v1.schema.json"],
                package,
                self.schemas,
            )

        self.assertIn("missing required key 'sdk_contract'", str(context.exception))

    def test_reference_contract_fallback_supports_sdk_fields_without_pyyaml(self) -> None:
        skill_md = (
            REPO_ROOT
            / "Plugins"
            / "skill-factory"
            / "skills"
            / "skill-factory-router"
            / "SKILL.md"
        )
        with patch.object(package_contracts, "yaml", None):
            contract = package_contracts.sdk_package_contract(
                REPO_ROOT,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        self.assertEqual(
            contract["values"]["purpose"],
            "Route skill lifecycle requests to exactly one skill-factory lane before execution.",
        )
        self.assertIn("inputs", contract["required_fields"]["present"])
        self.assertIn("outputs", contract["required_fields"]["present"])
        self.assertEqual(
            contract["values"]["permission_profile"]["filesystem"]["write"],
            [],
        )
        self.assertTrue(contract["progressive_disclosure"]["references_contract_declared"])

    def test_knowledge_capsule_contract_requires_first_party_routing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "capsule-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "# Capsule Skill\n\nLoad references/knowledge-capsule-routing.md before capsule bodies.\n",
                encoding="utf-8",
            )
            (references / "knowledge-capsule.manifest.yaml").write_text(
                "capsules:\n"
                "  - target_path: references/knowledge-capsules/one.md\n"
                "    facet_id: one\n",
                encoding="utf-8",
            )
            (references / "knowledge-capsule-routing.md").write_text(
                "# Knowledge Capsule Routing\n\n- references/knowledge-capsules/one.md\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        self.assertTrue(contract["knowledge_capsules"]["manifest_declared"])
        self.assertTrue(contract["knowledge_capsules"]["ready"])
        self.assertEqual(contract["knowledge_capsules"]["capsule_paths"], ["references/knowledge-capsules/one.md"])

    def test_knowledge_capsule_contract_blocks_unsafe_target_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "capsule-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "# Capsule Skill\n\nLoad references/knowledge-capsule-routing.md before capsule bodies.\n",
                encoding="utf-8",
            )
            (references / "knowledge-capsule.manifest.yaml").write_text(
                "capsules:\n"
                "  - target_path: /tmp/outside.md\n"
                "    facet_id: outside\n",
                encoding="utf-8",
            )
            (references / "knowledge-capsule-routing.md").write_text(
                "# Knowledge Capsule Routing\n\n- /tmp/outside.md\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        self.assertTrue(contract["knowledge_capsules"]["manifest_declared"])
        self.assertFalse(contract["knowledge_capsules"]["ready"])
        self.assertEqual(contract["knowledge_capsules"]["unsafe_capsule_paths"], ["/tmp/outside.md"])

    def test_knowledge_capsule_contract_warns_when_routing_is_buried(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "capsule-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("# Capsule Skill\n\nLoad the manifest when needed.\n", encoding="utf-8")
            (references / "knowledge-capsule.manifest.yaml").write_text(
                "capsules:\n"
                "  - target_path: references/knowledge-capsules/one.md\n"
                "    facet_id: one\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        self.assertEqual(contract["knowledge_capsules"]["status"], "advisory")
        self.assertTrue(contract["knowledge_capsules"]["manifest_declared"])
        self.assertFalse(contract["knowledge_capsules"]["ready"])

    def test_knowledge_capsules_block_package_readiness_when_declared_but_not_routed(self) -> None:
        frontmatter = {
            "name": "capsule-blocked-skill",
            "description": "Capsule blocked skill fixture.",
            "metadata": {
                "version": "1.0.0",
                "compatible_roles": ["worker"],
                "runtime_needs": ["filesystem"],
                "maturity": "beta",
                "provenance": "internal",
                "share_readiness": "ready",
            },
        }
        sdk_contract = {
            "required_fields": {"missing": []},
            "values": {
                "workflow_contract": {"status": "pass"},
                "optimization_contract": {"status": "pass"},
                "reference_quality": {"status": "pass", "required_for_package_readiness": True},
            },
            "knowledge_capsules": {
                "manifest_declared": True,
                "ready": False,
            },
        }

        with patch.object(package_contracts, "sdk_package_contract", return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)

        self.assertEqual(package["readiness_level"], "knowledge_capsules_incomplete")
        self.assertIn(
            "knowledge_capsules:first_party_routing_incomplete",
            package["install_gate"]["blocked_reasons"],
        )

    def test_package_readiness_schema_rejects_payload_without_snapshot_identity(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]

        package.pop("compatibility_snapshot")

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(
                self.schemas["skill-package-readiness.v1.schema.json"],
                package,
                self.schemas,
            )

        self.assertIn("missing required key 'compatibility_snapshot'", str(context.exception))

    def test_package_readiness_schema_rejects_unknown_top_level_keys(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]
        package["unexpected_contract_key"] = True

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(
                self.schemas["skill-package-readiness.v1.schema.json"],
                package,
                self.schemas,
            )

        self.assertIn("unexpected keys", str(context.exception))

    def test_package_public_output_matches_compatibility_snapshot(self) -> None:
        snapshots = _load_snapshot()
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            valid_package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            missing_package = skills_package(REPO_ROOT, "missing-skill").data["skill_package"]
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )
            strict_incomplete_package = skills_package(
                repo_root,
                "Skills/agent-ops/packaged-skill",
                strict=True,
            ).data["skill_package"]

        self.assertEqual(
            {
                "valid_share_ready_package": _snapshot_projection(valid_package),
                "missing_source_package": _snapshot_projection(missing_package),
                "strict_incomplete_package": _snapshot_projection(strict_incomplete_package),
            },
            snapshots,
        )
