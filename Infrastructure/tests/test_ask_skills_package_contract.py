from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_package_contract_logic_lives_in_skills_sdk_service(self) -> None:
        command_source = (
            REPO_ROOT / "Infrastructure/scripts/lib/ask/commands/skills_impl.py"
        ).read_text(encoding="utf-8")
        service_source = (
            REPO_ROOT / "Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            package_contracts.skill_package_contract.__module__,
            "ask.skills_sdk.package_contracts",
        )
        self.assertNotIn("def _skill_package_contract", command_source)
        self.assertNotIn("ask.commands", service_source)
        self.assertNotIn("CallResult", service_source)
        self.assertNotIn("ErrorObject", service_source)
        self.assertIn("def skill_package_contract", service_source)

    def test_skill_package_schema_accepts_codex_metadata_contract(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]

        contract = package["skill_package_contract"]
        _validate_schema_subset(self.schemas["skill-package.v1.schema.json"], contract, self.schemas)
        self.assertEqual(contract["schema_version"], "skill-package.v1")
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["compatibility_status"], "compatible")
        self.assertEqual(contract["metadata"]["name"], "skill-factory-router")
        self.assertEqual(
            contract["codex_abi_source"]["path"],
            "codex-rs/core-skills/src/model.rs",
        )
        self.assertFalse(Path(contract["codex_abi_source"]["path"]).is_absolute())
        self.assertIn("interface", contract["optional_fields"]["present"])
        self.assertEqual(
            contract["metadata"]["interface"]["display_name"],
            "Skill Factory Router",
        )

    def test_skill_package_contract_merges_agents_openai_policy_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "codex-package"
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: codex-package
description: Codex package metadata fixture.
dependencies:
  frontmatter_tool: required
policy:
  frontmatter_policy: strict
---

# Codex Package
""",
                encoding="utf-8",
            )
            (agents_dir / "openai.yaml").write_text(
                """interface:
  short_description: OpenAI package fixture.
dependencies:
  openai_tool: required
  required_skills:
    - skill-factory-router
  tools:
    - type: mcp
      name: browser
policy:
  openai_policy: strict
""",
                encoding="utf-8",
            )

            contract = skills_package(
                repo_root,
                "Skills/agent-ops/codex-package",
            ).data["skill_package"]["skill_package_contract"]

        self.assertEqual(
            contract["metadata"]["dependencies"],
            {
                "frontmatter_tool": "required",
                "openai_tool": "required",
                "required_skills": [
                    "skill-factory-router",
                ],
                "tools": [
                    {
                        "type": "mcp",
                        "name": "browser",
                    },
                ],
            },
        )
        self.assertEqual(
            contract["metadata"]["policy"],
            {
                "frontmatter_policy": "strict",
                "openai_policy": "strict",
            },
        )
        self.assertEqual(
            contract["metadata"]["short_description"],
            "OpenAI package fixture.",
        )
        self.assertIn("dependencies", contract["optional_fields"]["present"])
        self.assertIn("policy", contract["optional_fields"]["present"])

    def test_skill_frontmatter_parser_preserves_nested_contract_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = Path(temp_dir) / "SKILL.md"
            skill_md.write_text(
                """---
name: codex-package
description: Codex package metadata fixture.
dependencies:
  required_skills:
    - skill-factory-router
  tools:
    - browser
policy:
  permissions:
    - network
---

# Codex Package
""",
                encoding="utf-8",
            )

            frontmatter = read_skill_frontmatter_fields(skill_md)

        self.assertEqual(frontmatter["dependencies"]["required_skills"], ["skill-factory-router"])
        self.assertEqual(frontmatter["dependencies"]["tools"], ["browser"])
        self.assertEqual(frontmatter["policy"]["permissions"], ["network"])

    def test_normalized_list_sorts_sets_without_reordering_lists(self) -> None:
        self.assertEqual(package_contracts.normalized_list({"beta", "alpha"}), ["alpha", "beta"])
        self.assertEqual(package_contracts.normalized_list(("beta", "alpha")), ["beta", "alpha"])

    def test_package_contract_manual_yaml_fallback_preserves_openai_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "codex-package"
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: codex-package
description: Codex package metadata fixture.
---

# Codex Package
""",
                encoding="utf-8",
            )
            (agents_dir / "openai.yaml").write_text(
                """interface:
  short_description: OpenAI package fixture.
dependencies:
  required_skills:
    - skill-factory-router
  tools:
    - type: mcp
      name: browser
policy:
  openai_policy: strict
""",
                encoding="utf-8",
            )

            frontmatter = read_skill_frontmatter_fields(skill_md)
            with patch.object(package_contracts, "yaml", None):
                contract = package_contracts.skill_package_contract(
                    repo_root,
                    skill_md,
                    frontmatter,
                )

        self.assertEqual(contract["metadata"]["short_description"], "OpenAI package fixture.")
        self.assertEqual(contract["metadata"]["dependencies"]["required_skills"], ["skill-factory-router"])
        self.assertEqual(
            contract["metadata"]["dependencies"]["tools"],
            [{"type": "mcp", "name": "browser"}],
        )
        self.assertEqual(contract["metadata"]["policy"], {"openai_policy": "strict"})

    def test_json_shaped_reference_contract_survives_without_pyyaml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "Skills" / "agent-ops" / "json-contract"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("# Json Contract\n", encoding="utf-8")
            (references / "contract.yaml").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "skill": "json-contract",
                        "purpose": "Keep JSON-shaped YAML readable.",
                        "inputs": ["input"],
                        "outputs": ["output"],
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(package_contracts, "yaml", None):
                contract = package_contracts.read_reference_contract(skill_md)

        self.assertEqual(contract["purpose"], "Keep JSON-shaped YAML readable.")
        self.assertEqual(contract["inputs"], ["input"])
        self.assertEqual(contract["outputs"], ["output"])

    def test_package_contract_malformed_yaml_falls_back_to_empty_openai_fields(self) -> None:
        class BrokenYaml:
            class YAMLError(Exception):
                pass

            @staticmethod
            def safe_load(_text: str) -> object:
                raise BrokenYaml.YAMLError("malformed")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "codex-package"
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: codex-package
description: Codex package metadata fixture.
dependencies:
  frontmatter_tool: required
policy:
  frontmatter_policy: strict
---

# Codex Package
""",
                encoding="utf-8",
            )
            (agents_dir / "openai.yaml").write_text("interface: [malformed\n", encoding="utf-8")

            frontmatter = read_skill_frontmatter_fields(skill_md)
            with patch.object(package_contracts, "yaml", BrokenYaml):
                contract = package_contracts.skill_package_contract(
                    repo_root,
                    skill_md,
                    frontmatter,
                )

        self.assertIsNone(contract["metadata"]["short_description"])
        self.assertEqual(contract["metadata"]["dependencies"], {"frontmatter_tool": "required"})
        self.assertEqual(contract["metadata"]["policy"], {"frontmatter_policy": "strict"})

    def test_skill_package_schema_rejects_missing_identity_contract(self) -> None:
        schema = self.schemas["skill-package.v1.schema.json"]
        invalid_contract = {
            "schema_version": "skill-package.v1",
            "metadata": {
                "short_description": "Missing required identity fields."
            },
            "required_fields": {
                "present": [],
                "missing": ["name", "description"],
            },
            "compatibility_status": "blocked_validation",
        }

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(schema, invalid_contract, self.schemas)

        self.assertIn("missing required key", str(context.exception))

    def test_skill_package_schema_rejects_unknown_contract_keys(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            contract = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"][
                "skill_package_contract"
            ]
        contract["unexpected_contract_key"] = True

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(
                self.schemas["skill-package.v1.schema.json"],
                contract,
                self.schemas,
            )

        self.assertIn("unexpected keys", str(context.exception))

    def test_skill_package_schema_rejects_unknown_metadata_keys(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            contract = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"][
                "skill_package_contract"
            ]
        contract["metadata"]["unexpected_metadata_key"] = True

        with self.assertRaises(AssertionError) as context:
            _validate_schema_subset(
                self.schemas["skill-package.v1.schema.json"],
                contract,
                self.schemas,
            )

        self.assertIn("unexpected keys", str(context.exception))

    def test_package_readiness_schema_accepts_public_package_payload(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]

        _validate_schema_subset(
            self.schemas["skill-package-readiness.v1.schema.json"],
            package,
            self.schemas,
        )
        self.assertEqual(package["package_schema"]["schema_version"], "skill-package.v1")
        self.assertEqual(
            package["package_readiness_schema"]["schema_version"],
            "skill-package-readiness.v1",
        )
        self.assertEqual(
            package["optimization_schema"]["schema_version"],
            "skill-optimization-contract.v1",
        )
        self.assertEqual(
            package["compatibility_snapshot"]["id"],
            "skill-package-readiness.v1.public-output.2026-05-23",
        )
        self.assertEqual(package["contract_schemas"]["skill_package"], "skill-package.v1")

    def test_package_payload_exposes_sdk_contract_and_optional_observability(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-factory-router").data["skill_package"]

        sdk_contract = package["package_contract"]["sdk_contract"]
        self.assertEqual(sdk_contract["schema_version"], "skill-sdk-contract.v1")
        self.assertIn("agent_metadata", sdk_contract["required_fields"]["present"])
        self.assertIn("reference_contract", sdk_contract["required_fields"]["present"])
        self.assertIn("reference_quality", sdk_contract["required_fields"]["present"])
        self.assertIn("writing_quality", sdk_contract["required_fields"]["present"])
        self.assertIn("openai_platform_compat", sdk_contract["required_fields"]["present"])
        self.assertIn("purpose", sdk_contract["required_fields"]["present"])
        self.assertIn("inputs", sdk_contract["required_fields"]["present"])
        self.assertIn("outputs", sdk_contract["required_fields"]["present"])
        self.assertIn("commands", sdk_contract["required_fields"]["present"])
        self.assertIn("permission_profile", sdk_contract["required_fields"]["present"])
        self.assertIn("evals", sdk_contract["required_fields"]["present"])
        self.assertIn("task_profile", sdk_contract["required_fields"]["present"])
        self.assertIn("evidence_policy", sdk_contract["required_fields"]["present"])
        self.assertEqual(
            sdk_contract["values"]["agent_metadata"]["path"],
            "Plugins/skill-factory/skills/skill-factory-router/agents/openai.yaml",
        )
        self.assertEqual(
            sdk_contract["values"]["reference_contract"]["path"],
            "Plugins/skill-factory/skills/skill-factory-router/references/contract.yaml",
        )
        self.assertEqual(
            sdk_contract["values"]["reference_quality"]["policy"],
            "references_are_package_contract",
        )
        self.assertEqual(sdk_contract["values"]["reference_quality"]["status"], "pass")
        self.assertTrue(
            sdk_contract["values"]["reference_quality"]["required_for_package_readiness"]
        )
        self.assertFalse(sdk_contract["values"]["reference_quality"]["blockers"])
        self.assertEqual(
            sdk_contract["values"]["writing_quality"]["schema_version"],
            "skills-sdk.skill-writing-quality.v1",
        )
        self.assertEqual(sdk_contract["values"]["writing_quality"]["status"], "pass")
        self.assertTrue(
            sdk_contract["values"]["writing_quality"]["required_for_package_readiness"]
        )
        self.assertFalse(sdk_contract["values"]["writing_quality"]["blockers"])
        self.assertEqual(
            sdk_contract["values"]["openai_platform_compat"]["schema_version"],
            "skills-sdk.openai-platform-compat.v1",
        )
        self.assertEqual(
            sdk_contract["values"]["openai_platform_compat"]["status"],
            "pass",
        )
        self.assertTrue(
            sdk_contract["values"]["openai_platform_compat"]["required_for_package_readiness"]
        )
        self.assertFalse(sdk_contract["values"]["openai_platform_compat"]["blockers"])
        self.assertEqual(
            sdk_contract["progressive_disclosure"]["references_quality_status"],
            "pass",
        )
        self.assertEqual(
            sdk_contract["progressive_disclosure"]["writing_quality_status"],
            "pass",
        )
        self.assertEqual(
            sdk_contract["progressive_disclosure"]["openai_platform_compat_status"],
            "pass",
        )
        self.assertEqual(
            sdk_contract["values"]["task_profile"]["path"],
            "Plugins/skill-factory/skills/skill-factory-router/references/task-profile.json",
        )
        self.assertEqual(
            sdk_contract["values"]["permission_profile"]["filesystem"]["read"],
            [
                "user request and declared target skill path",
                "Skill Factory skill inventory",
                "Skill Factory references needed for the selected lane",
                "repo validation scripts and package-readiness schemas",
            ],
        )
        self.assertTrue(sdk_contract["progressive_disclosure"]["skill_md_under_500_lines"])

        self.assertTrue(sdk_contract["progressive_disclosure"]["agent_metadata_declared"])
        self.assertTrue(sdk_contract["progressive_disclosure"]["references_contract_declared"])
        self.assertTrue(sdk_contract["values"]["evals"]["declared"])
        self.assertTrue(sdk_contract["progressive_disclosure"]["task_profile_declared"])
        self.assertFalse(sdk_contract["progressive_disclosure"]["agent_tomls_declared"])
        self.assertIn(
            "Plugins/skill-factory/skills/skill-factory-router/references/evals.yaml",
            sdk_contract["values"]["evals"]["paths"],
        )
        self.assertFalse(
            any(
                command.startswith("Tessl content below 95")
                for command in sdk_contract["values"]["commands"]
            )
        )
        self.assertEqual(
            sdk_contract["agent_contract"]["source_of_truth"],
            "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        )
        self.assertIn(
            "claim_eval_pass_as_runtime_proof",
            sdk_contract["agent_contract"]["forbidden_actions"],
        )
        self.assertIn("optional_per_skill_runtime_profiles", sdk_contract["agent_contract"]["agent_toml_policy"])
        self.assertEqual(
            sdk_contract["values"]["workflow_contract"]["schema_version"],
            "skillflow-contract.v1",
        )
        self.assertEqual(
            sdk_contract["values"]["workflow_contract"]["skillflow_schema_version"],
            "skillflow.v1",
        )
        self.assertEqual(
            sdk_contract["values"]["optimization_contract"]["schema_version"],
            "skill-optimization-readiness.v1",
        )
        self.assertEqual(
            sdk_contract["values"]["optimization_contract"]["optimization_schema_version"],
            "skill-optimization-contract.v1",
        )
        self.assertEqual(
            sdk_contract["progressive_disclosure"]["execution_mode"],
            sdk_contract["values"]["workflow_contract"]["execution_mode"],
        )
        self.assertEqual(
            sdk_contract["progressive_disclosure"]["optimization_status"],
            sdk_contract["values"]["optimization_contract"]["status"],
        )
        self.assertIn(
            "workflows/skillflow.json",
            sdk_contract["agent_contract"]["workflow_policy"],
        )
        self.assertIn(
            "bounded candidate artifacts",
            sdk_contract["agent_contract"]["optimization_policy"],
        )

        providers = sdk_contract["evidence_providers"]
        self.assertEqual(providers["schema_version"], "skill-evidence-providers.v1")
        self.assertEqual(providers["authority"], "artifacts_decide_telemetry_explains")
        self.assertFalse(providers["required_for_package_readiness"])
        self.assertIn(
            providers["telemetry_confidence"],
            {"enriched", "partial", "not_available"},
        )
        self.assertEqual(
            [provider["name"] for provider in providers["providers"]],
            ["otel_collector", "session_collector", "observability_stack"],
        )

    def test_structured_reference_fallback_preserves_top_level_lists(self) -> None:
        text = """---
schema_version: '2.0'
skill_name: example
claims:
- id: global-target-repository
  statement: Uses active repository.
cases:
- id: smoke-discovery
  name: Discovery
"""

        with tempfile.NamedTemporaryFile("w", suffix=".yaml", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            with patch.object(package_contracts, "yaml", None):
                process = package_contracts.subprocess.CompletedProcess(
                    args=["ruby"],
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "schema_version": "2.0",
                            "skill_name": "example",
                            "claims": [
                                {
                                    "id": "global-target-repository",
                                    "statement": "Uses active repository.",
                                }
                            ],
                            "cases": [{"id": "smoke-discovery", "name": "Discovery"}],
                        }
                    ),
                    stderr="",
                )
                with patch.object(package_contracts.subprocess, "run", return_value=process):
                    loaded, error = package_contracts.read_structured_reference(Path(handle.name))

        self.assertIsNone(error)
        self.assertIsInstance(loaded, dict)
        if not isinstance(loaded, dict):
            self.fail("expected structured reference fallback to return a dict")
        self.assertIsInstance(loaded.get("claims"), list)
        self.assertIsInstance(loaded.get("cases"), list)
        self.assertTrue(loaded["claims"])
        self.assertTrue(loaded["cases"])

    def test_structured_reference_fallback_preserves_nested_rubric_scoring(self) -> None:
        text = """schema_version: 1
quality_criteria:
  current_state_before_action:
    purpose: Uses live PR state.
    why_it_matters: Prevents stale merge claims.
    observable_evidence:
      - latest_head_sha
      - required_checks
    scoring:
      "5": Latest-head proof is complete.
      "4": Minor evidence detail is missing.
      "3": Evidence is present but incomplete.
      "2": Evidence is stale or partial.
      "1": No live PR evidence is provided.
automatic_failure_conditions:
  - Claims waived external CI as green.
"""
        mock_stdout = '{"schema_version":1,"quality_criteria":{"current_state_before_action":{"purpose":"Uses live PR state.","why_it_matters":"Prevents stale merge claims.","observable_evidence":["latest_head_sha","required_checks"],"scoring":{"5":"Latest-head proof is complete.","4":"Minor evidence detail is missing.","3":"Evidence is present but incomplete.","2":"Evidence is stale or partial.","1":"No live PR evidence is provided."}}},"automatic_failure_conditions":["Claims waived external CI as green."]}'
        mock_process = package_contracts.subprocess.CompletedProcess(
            args=["ruby"],
            returncode=0,
            stdout=mock_stdout,
            stderr="",
        )

        with tempfile.NamedTemporaryFile("w", suffix=".yaml", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            with (
                patch.object(package_contracts, "yaml", None),
                patch.object(package_contracts.subprocess, "run", return_value=mock_process),
            ):
                loaded, error = package_contracts.read_structured_reference(Path(handle.name))

        self.assertIsNone(error)
        self.assertIsInstance(loaded, dict)
        if not isinstance(loaded, dict):
            self.fail("expected structured reference fallback to return a dict")
        criterion = loaded["quality_criteria"]["current_state_before_action"]
        self.assertEqual(criterion["observable_evidence"], ["latest_head_sha", "required_checks"])
        self.assertEqual(criterion["scoring"]["5"], "Latest-head proof is complete.")

    def test_sdk_contract_accepts_optional_valid_skillflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "workflow-skill"
            references_dir = skill_dir / "references"
            workflows_dir = skill_dir / "workflows"
            references_dir.mkdir(parents=True)
            workflows_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: workflow-skill
description: Workflow skill fixture.
---

# Workflow Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise optional skillflow contract support."
execution_mode: "hybrid"
inputs:
  - name: task
outputs:
  - name: result
workflow:
  path: "workflows/skillflow.json"
  required: true
  execution_mode: "hybrid"
""",
                encoding="utf-8",
            )
            skillflow_payload = {
                "schema_version": "skillflow.v1",
                "name": "workflow-skill",
                "inputs": {"task": {"type": "string"}},
                "outputs": {"result": {"type": "string"}},
                "nodes": [
                    {
                        "id": "classify",
                        "type": "llm",
                        "out": "classification",
                    },
                    {
                        "id": "validate",
                        "type": "validator",
                        "out": "result",
                    },
                ],
            }
            (workflows_dir / "skillflow.json").write_text(
                json.dumps(skillflow_payload),
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        workflow_contract = contract["values"]["workflow_contract"]
        _validate_schema_subset(
            self.schemas["skillflow.v1.schema.json"],
            skillflow_payload,
            self.schemas,
        )
        self.assertEqual(workflow_contract["status"], "pass")
        self.assertTrue(workflow_contract["declared"])
        self.assertTrue(workflow_contract["required"])
        self.assertEqual(workflow_contract["execution_mode"], "hybrid")
        self.assertEqual(workflow_contract["node_count"], 2)
        self.assertEqual(workflow_contract["human_gate_count"], 0)
        self.assertFalse(workflow_contract["blockers"])
        self.assertTrue(contract["progressive_disclosure"]["workflow_declared"])

    def test_sdk_contract_reports_progressive_disclosure_compaction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "compact-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: compact-skill
description: Compact skill fixture.
---

# Compact Skill

## Workflow

Keep the entrypoint small.

## Progressive Disclosure

- Read `references/details.md` for task-specific detail.
""",
                encoding="utf-8",
            )
            (references_dir / "details.md").write_text(
                "# Hidden File Skill Details\n",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        progressive = contract["progressive_disclosure"]
        self.assertTrue(progressive["skill_md_under_250_lines"])
        self.assertTrue(progressive["progressive_disclosure_declared"])
        self.assertEqual(progressive["progressive_disclosure_reference_count"], 1)
        self.assertEqual(progressive["progressive_disclosure_missing_references"], [])
        self.assertTrue(progressive["progressive_disclosure_ready"])
