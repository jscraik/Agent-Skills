import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills_impl import skills_package  # noqa: E402
from ask.skills_sdk.contracts import read_skill_frontmatter_fields  # noqa: E402
from ask.skills_sdk import package_contracts  # noqa: E402


SUPPORTED_SCHEMA_KEYS = {
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "allOf",
    "const",
    "definitions",
    "description",
    "enum",
    "if",
    "items",
    "exclusiveMinimum",
    "minimum",
    "minItems",
    "minLength",
    "oneOf",
    "properties",
    "required",
    "then",
    "title",
    "type",
}


def _load_schema(name: str) -> dict:
    return json.loads((REPO_ROOT / "Infrastructure" / "config" / "schemas" / name).read_text(encoding="utf-8"))


def _load_snapshot() -> dict:
    return json.loads(
        (
            REPO_ROOT
            / "Infrastructure"
            / "tests"
            / "fixtures"
            / "skill_package_snapshots"
            / "skill-package-readiness-public-output.v1.json"
        ).read_text(encoding="utf-8")
    )


def _resolve_schema_ref(ref: str, schema: dict, schemas: dict[str, dict]) -> dict:
    if ref in schemas:
        return schemas[ref]
    if "#" in ref and not ref.startswith("#/"):
        schema_name, fragment = ref.split("#", 1)
        base = schemas[schema_name]
        return _resolve_schema_ref("#" + fragment, base, schemas)
    node = schema
    for part in ref.removeprefix("#/").split("/"):
        if not part:
            continue
        node = node[part]
    return node


def _schema_type_matches(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise AssertionError(f"Unsupported schema type in test validator: {expected}")


def _validate_schema_subset(
    schema: dict,
    value: object,
    schemas: dict[str, dict],
    path: str = "$",
    root_schema: dict | None = None,
) -> None:
    if root_schema is None:
        root_schema = schema
    unsupported = set(schema) - SUPPORTED_SCHEMA_KEYS
    if unsupported:
        raise AssertionError(f"Unsupported schema keys at {path}: {sorted(unsupported)}")

    if "$ref" in schema:
        _validate_schema_subset(
            _resolve_schema_ref(schema["$ref"], root_schema, schemas),
            value,
            schemas,
            path,
            root_schema,
        )
        return

    for subschema in schema.get("allOf", []):
        _validate_schema_subset(subschema, value, schemas, path, root_schema)

    if "if" in schema:
        try:
            _validate_schema_subset(schema["if"], value, schemas, path, root_schema)
        except AssertionError:
            pass
        else:
            if "then" in schema:
                _validate_schema_subset(schema["then"], value, schemas, path, root_schema)

    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                _validate_schema_subset(option, value, schemas, path, root_schema)
            except AssertionError:
                continue
            matches += 1
        if matches != 1:
            raise AssertionError(f"{path} expected exactly one oneOf match, got {matches}")

    if "type" in schema:
        expected_types = schema["type"]
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_schema_type_matches(value, expected) for expected in expected_types):
            raise AssertionError(f"{path} expected {expected_types}, got {type(value).__name__}")

    if "const" in schema and value != schema["const"]:
        raise AssertionError(f"{path} expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise AssertionError(f"{path} expected one of {schema['enum']!r}, got {value!r}")

    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        raise AssertionError(f"{path} shorter than minLength {schema['minLength']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise AssertionError(f"{path} lower than minimum {schema['minimum']}")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            raise AssertionError(f"{path} lower than or equal to exclusiveMinimum {schema['exclusiveMinimum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise AssertionError(f"{path} shorter than minItems {schema['minItems']}")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_schema_subset(schema["items"], item, schemas, f"{path}[{index}]", root_schema)

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise AssertionError(f"{path} missing required key {key!r}")
        properties = schema.get("properties", {})
        for key, child in properties.items():
            if key in value:
                _validate_schema_subset(child, value[key], schemas, f"{path}.{key}", root_schema)
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(properties)
            if extra:
                raise AssertionError(f"{path} unexpected keys {sorted(extra)}")


def _snapshot_projection(package: dict) -> dict:
    contract = package["package_contract"]
    skill_contract = package["skill_package_contract"]
    return {
        "schema_version": package["schema_version"],
        "compatibility_snapshot": package["compatibility_snapshot"],
        "package_schema": package["package_schema"],
        "package_readiness_schema": package["package_readiness_schema"],
        "status": package["status"],
        "strict": package["strict"],
        "target_kind": package["target_kind"],
        "gate_summary": package["gate_summary"],
        "readiness_summary": {
            "readiness_level": package["readiness_summary"]["readiness_level"],
            "missing_fields": package["readiness_summary"]["missing_fields"],
            "missing_field_count": package["readiness_summary"]["missing_field_count"],
            "promotion_status": package["readiness_summary"]["promotion_status"],
        },
        "skill_package_contract": {
            "schema_version": skill_contract["schema_version"],
            "source_files": skill_contract["source_files"],
            "codex_abi_source": skill_contract["codex_abi_source"],
            "metadata": {
                "name": skill_contract["metadata"]["name"],
                "description": skill_contract["metadata"]["description"],
                "short_description": skill_contract["metadata"]["short_description"],
                "interface": skill_contract["metadata"]["interface"],
                "dependencies": skill_contract["metadata"]["dependencies"],
                "policy": skill_contract["metadata"]["policy"],
                "scope": skill_contract["metadata"]["scope"],
                "plugin_id": skill_contract["metadata"]["plugin_id"],
            },
            "required_fields": skill_contract["required_fields"],
            "optional_fields": skill_contract["optional_fields"],
            "compatibility_status": skill_contract["compatibility_status"],
        },
        "package_contract": {
            "readiness_level": contract["readiness_level"],
            "required_fields": contract["required_fields"],
            "values": contract["values"],
            "install_gate": {
                "install_ready": contract["install_gate"]["install_ready"],
                "blocked_reasons": contract["install_gate"]["blocked_reasons"],
                "checkout_test_status": contract["install_gate"]["checkout_test"]["status"],
            },
            "promotion_gate": {
                "status": contract["promotion_gate"]["status"],
                "promotion_ready": contract["promotion_gate"]["promotion_ready"],
                "share_ready": contract["promotion_gate"]["share_ready"],
                "blocked_reasons": contract["promotion_gate"]["blocked_reasons"],
            },
        },
        "blocker_classes": [blocker["class"] for blocker in package["blockers"]],
        "warning_classes": [warning["class"] for warning in package["warnings"]],
    }


class TestAskSkillsPackageContract(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas = {
            "skill-package.v1.schema.json": _load_schema("skill-package.v1.schema.json"),
            "skill-package-readiness.v1.schema.json": _load_schema(
                "skill-package-readiness.v1.schema.json"
            ),
            "skillflow.v1.schema.json": _load_schema("skillflow.v1.schema.json"),
            "skill-optimization-contract.v1.schema.json": _load_schema(
                "skill-optimization-contract.v1.schema.json"
            ),
        }

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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]

        contract = package["skill_package_contract"]
        _validate_schema_subset(self.schemas["skill-package.v1.schema.json"], contract, self.schemas)
        self.assertEqual(contract["schema_version"], "skill-package.v1")
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["compatibility_status"], "compatible")
        self.assertEqual(contract["metadata"]["name"], "skill-builder")
        self.assertEqual(
            contract["codex_abi_source"]["path"],
            "codex-rs/core-skills/src/model.rs",
        )
        self.assertFalse(Path(contract["codex_abi_source"]["path"]).is_absolute())
        self.assertIn("interface", contract["optional_fields"]["present"])
        self.assertEqual(
            contract["metadata"]["interface"]["display_name"],
            "Skill Builder",
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
    - skill-builder
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
                    "skill-builder",
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
    - skill-builder
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

        self.assertEqual(frontmatter["dependencies"]["required_skills"], ["skill-builder"])
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
    - skill-builder
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
        self.assertEqual(contract["metadata"]["dependencies"]["required_skills"], ["skill-builder"])
        self.assertEqual(
            contract["metadata"]["dependencies"]["tools"],
            [{"type": "mcp", "name": "browser"}],
        )
        self.assertEqual(contract["metadata"]["policy"], {"openai_policy": "strict"})

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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            contract = skills_package(REPO_ROOT, "skill-builder").data["skill_package"][
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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            contract = skills_package(REPO_ROOT, "skill-builder").data["skill_package"][
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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]

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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]

        sdk_contract = package["package_contract"]["sdk_contract"]
        self.assertEqual(sdk_contract["schema_version"], "skill-sdk-contract.v1")
        self.assertIn("agent_metadata", sdk_contract["required_fields"]["present"])
        self.assertIn("reference_contract", sdk_contract["required_fields"]["present"])
        self.assertIn("reference_quality", sdk_contract["required_fields"]["present"])
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
            "Plugins/skill-factory/skills/code_quality_review/skill-builder/agents/openai.yaml",
        )
        self.assertEqual(
            sdk_contract["values"]["reference_contract"]["path"],
            "Plugins/skill-factory/skills/code_quality_review/skill-builder/references/contract.yaml",
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
            sdk_contract["progressive_disclosure"]["references_quality_status"],
            "pass",
        )
        self.assertEqual(
            sdk_contract["values"]["task_profile"]["path"],
            "Plugins/skill-factory/skills/code_quality_review/skill-builder/references/task-profile.json",
        )
        self.assertEqual(
            sdk_contract["values"]["permission_profile"]["filesystem"]["read"],
            [
                "target skill package",
                "repo validation scripts",
                "optional ~/.agents evidence provider summaries",
            ],
        )
        self.assertTrue(sdk_contract["progressive_disclosure"]["skill_md_under_500_lines"])
        self.assertTrue(sdk_contract["progressive_disclosure"]["agent_metadata_declared"])
        self.assertTrue(sdk_contract["progressive_disclosure"]["references_contract_declared"])
        self.assertTrue(sdk_contract["values"]["evals"]["declared"])
        self.assertTrue(sdk_contract["progressive_disclosure"]["task_profile_declared"])
        self.assertFalse(sdk_contract["progressive_disclosure"]["agent_tomls_declared"])
        self.assertIn(
            "Plugins/skill-factory/skills/code_quality_review/skill-builder/references/evals.yaml",
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
            "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
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

    def test_required_skillflow_missing_blocks_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "workflow-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: workflow-skill
description: Workflow skill fixture.
version: "1.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Workflow Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise required skillflow blocking."
execution_mode: "deterministic_flow"
inputs:
  - name: task
outputs:
  - name: result
workflow:
  path: "workflows/skillflow.json"
  required: true
  execution_mode: "deterministic_flow"
""",
                encoding="utf-8",
            )

            package = skills_package(
                repo_root,
                "Skills/agent-ops/workflow-skill",
                strict=True,
            ).data["skill_package"]

        workflow_contract = package["package_contract"]["sdk_contract"]["values"]["workflow_contract"]
        self.assertEqual(workflow_contract["status"], "blocked_validation")
        self.assertIn(
            "workflow_contract:skillflow_required_file_missing",
            package["gate_summary"]["blocked_reasons"],
        )
        self.assertIn(
            package["package_contract"]["readiness_level"],
            {"sdk_contract_incomplete", "workflow_contract_incomplete"},
        )

    def test_sdk_contract_accepts_valid_skill_optimization_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "optimizable-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: optimizable-skill
description: Optimizable skill fixture.
---

# Optimizable Skill
""",
                encoding="utf-8",
            )
            optimization_payload = {
                "schema_version": "skill-optimization-contract.v1",
                "enabled": True,
                "target_artifact": "SKILL.md",
                "optimizer_mode": "bounded_patch",
                "roles": {
                    "target_runner": {
                        "may_edit": "none",
                        "sees": ["current_target"],
                    },
                    "optimizer": {
                        "may_edit": "candidate_patch_only",
                        "sees": ["train", "selection"],
                    },
                    "promoter": {
                        "may_edit": "canonical_source_after_review",
                        "sees": ["candidate", "selection", "test"],
                    },
                    "auditor": {
                        "may_edit": "none",
                        "sees": ["diff", "protected_paths"],
                    },
                },
                "splits": {
                    "train": {
                        "path": ".harness/evals/optimizable/train.jsonl",
                        "role": "proposal_generation",
                    },
                    "selection": {
                        "path": ".harness/evals/optimizable/selection.jsonl",
                        "role": "candidate_acceptance",
                    },
                    "test": {
                        "path": ".harness/evals/optimizable/test.jsonl",
                        "role": "final_report_only",
                    },
                    "split_seed": 42,
                },
                "edit_policy": {
                    "mode": "patch",
                    "operations": ["add", "delete", "replace"],
                    "max_edits": 4,
                },
                "acceptance_gate": {
                    "metric": "score",
                    "direction": "maximize",
                    "rule": "strict_improvement",
                    "ties": "reject",
                    "min_delta": 0.01,
                    "noise_runs": 3,
                    "guard_failure": "discard",
                    "report_test_score_only_after_acceptance": True,
                },
                "anti_cheat": {
                    "protected_paths": ["references/evals.yaml", ".harness/evals/**"],
                    "checks": ["protected_path_diff_empty", "held_out_not_visible_to_optimizer"],
                },
                "evidence": {
                    "root": ".harness/evidence/optimizable/<run_tag>",
                    "rollout_jsonl": "rollouts.jsonl",
                    "rejected_buffer_jsonl": "rejected-edits.jsonl",
                    "candidate_artifact": "best_skill.md",
                    "promotion_manifest": "promotion.json",
                    "selection_results": "selection-results.json",
                    "test_results": "test-results.json",
                },
                "promotion": {
                    "canonical_edit_requires_review": True,
                    "required_checks": [
                        "selection_gate_pass",
                        "held_out_test_report",
                        "anti_cheat_pass",
                    ],
                },
            }
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise valid bounded optimization contract support."
inputs:
  - name: task
outputs:
  - name: result
optimization:
  schema_version: "skill-optimization-contract.v1"
  enabled: true
  target_artifact: "SKILL.md"
  optimizer_mode: "bounded_patch"
  roles:
    target_runner:
      may_edit: "none"
      sees:
        - current_target
    optimizer:
      may_edit: "candidate_patch_only"
      sees:
        - train
        - selection
    promoter:
      may_edit: "canonical_source_after_review"
      sees:
        - candidate
        - selection
        - test
    auditor:
      may_edit: "none"
      sees:
        - diff
        - protected_paths
  splits:
    train:
      path: ".harness/evals/optimizable/train.jsonl"
      role: "proposal_generation"
    selection:
      path: ".harness/evals/optimizable/selection.jsonl"
      role: "candidate_acceptance"
    test:
      path: ".harness/evals/optimizable/test.jsonl"
      role: "final_report_only"
    split_seed: 42
  edit_policy:
    mode: "patch"
    operations:
      - add
      - delete
      - replace
    max_edits: 4
  acceptance_gate:
    metric: "score"
    direction: "maximize"
    rule: "strict_improvement"
    ties: "reject"
    min_delta: 0.01
    noise_runs: 3
    guard_failure: "discard"
    report_test_score_only_after_acceptance: true
  anti_cheat:
    protected_paths:
      - "references/evals.yaml"
      - ".harness/evals/**"
    checks:
      - protected_path_diff_empty
      - held_out_not_visible_to_optimizer
  evidence:
    root: ".harness/evidence/optimizable/<run_tag>"
    rollout_jsonl: "rollouts.jsonl"
    rejected_buffer_jsonl: "rejected-edits.jsonl"
    candidate_artifact: "best_skill.md"
    promotion_manifest: "promotion.json"
    selection_results: "selection-results.json"
    test_results: "test-results.json"
  promotion:
    canonical_edit_requires_review: true
    required_checks:
      - selection_gate_pass
      - held_out_test_report
      - anti_cheat_pass
""",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        optimization_contract = contract["values"]["optimization_contract"]
        _validate_schema_subset(
            self.schemas["skill-optimization-contract.v1.schema.json"],
            optimization_payload,
            self.schemas,
        )
        min_delta_payload = json.loads(json.dumps(optimization_payload))
        min_delta_payload["acceptance_gate"] = {
            "metric": "score",
            "direction": "maximize",
            "rule": "min_delta",
            "ties": "reject",
            "guard_failure": "discard",
        }
        with self.assertRaisesRegex(AssertionError, "min_delta"):
            _validate_schema_subset(
                self.schemas["skill-optimization-contract.v1.schema.json"],
                min_delta_payload,
                self.schemas,
            )
        negative_integer_payload = json.loads(json.dumps(optimization_payload))
        negative_integer_payload["edit_policy"]["max_edits"] = -1
        with self.assertRaisesRegex(AssertionError, "minimum"):
            _validate_schema_subset(
                self.schemas["skill-optimization-contract.v1.schema.json"],
                negative_integer_payload,
                self.schemas,
            )
        self.assertEqual(optimization_contract["status"], "pass")
        self.assertTrue(optimization_contract["enabled"])
        self.assertEqual(optimization_contract["optimizer_mode"], "bounded_patch")
        self.assertEqual(optimization_contract["split_seed"], 42)
        self.assertFalse(optimization_contract["blockers"])
        self.assertTrue(contract["progressive_disclosure"]["optimization_declared"])

    def test_incomplete_skill_optimization_contract_blocks_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "optimizable-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: optimizable-skill
description: Optimizable skill fixture.
version: "1.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Optimizable Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise incomplete bounded optimization contract blocking."
inputs:
  - name: task
outputs:
  - name: result
optimization:
  enabled: true
  target_artifact: "SKILL.md"
""",
                encoding="utf-8",
            )

            package = skills_package(
                repo_root,
                "Skills/agent-ops/optimizable-skill",
                strict=True,
            ).data["skill_package"]

        optimization_contract = package["package_contract"]["sdk_contract"]["values"][
            "optimization_contract"
        ]
        self.assertEqual(optimization_contract["status"], "blocked_validation")
        self.assertIn(
            "optimization_contract:optimization_optimizer_mode_invalid",
            package["gate_summary"]["blocked_reasons"],
        )
        self.assertIn(
            package["package_contract"]["readiness_level"],
            {"sdk_contract_incomplete", "optimization_contract_incomplete"},
        )

    def test_incomplete_reference_quality_blocks_package_readiness(self) -> None:
        frontmatter = {
            "name": "reference-blocked-skill",
            "description": "Reference blocked skill fixture.",
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
                "reference_quality": {
                    "status": "blocked_validation",
                    "required_for_package_readiness": True,
                    "blockers": [{"rule_id": "reference_contract_incomplete"}],
                },
            },
        }

        with patch.object(package_contracts, "sdk_package_contract", return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)

        self.assertEqual(
            package["readiness_level"],
            "reference_quality_incomplete",
        )
        self.assertIn(
            "reference_quality:reference_contract_incomplete",
            package["install_gate"]["blocked_reasons"],
        )

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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]

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
            / "code_quality_review"
            / "skill-builder"
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
            "Operational contract for skill-builder routing and execution boundaries.",
        )
        self.assertIn("inputs", contract["required_fields"]["present"])
        self.assertIn("outputs", contract["required_fields"]["present"])
        self.assertEqual(
            contract["values"]["permission_profile"]["filesystem"]["write"],
            ["canonical target skill package", "repo-local validation artifacts"],
        )
        self.assertTrue(contract["progressive_disclosure"]["references_contract_declared"])

    def test_package_readiness_schema_rejects_payload_without_snapshot_identity(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]

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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]
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
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            valid_package = skills_package(REPO_ROOT, "skill-builder").data["skill_package"]
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


if __name__ == "__main__":
    unittest.main()
