"""
Tests for JSC-351 Codex ABI Conformance schema contracts.

Covers the three new JSON Schema files introduced in the PR:
  - Infrastructure/config/schemas/skill-doctor.v1.schema.json
  - Infrastructure/config/schemas/skill-package.v1.schema.json
  - Infrastructure/config/schemas/skill-package-readiness.v1.schema.json

And the updated generated surface files:
  - .skillsets/command-surface.json
  - .skillsets/*/manifest.jsonl
"""
import json
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = REPO_ROOT / "Infrastructure" / "config" / "schemas"
SKILLSETS_DIR = REPO_ROOT / ".skillsets"

SKILL_DOCTOR_SCHEMA_PATH = SCHEMAS_DIR / "skill-doctor.v1.schema.json"
SKILL_PACKAGE_SCHEMA_PATH = SCHEMAS_DIR / "skill-package.v1.schema.json"
SKILL_PACKAGE_READINESS_SCHEMA_PATH = SCHEMAS_DIR / "skill-package-readiness.v1.schema.json"
SKILLS_SDK_PROJECT_SCHEMA_PATH = SCHEMAS_DIR / "skills-sdk.project.v1.schema.json"
COMMAND_SURFACE_PATH = SKILLSETS_DIR / "command-surface.json"
SYSTEM_BRIDGE_HANDLES = {
    "imagegen",
    "openai-docs",
    "plugin-creator",
    "plugin-installer",
    "skill-creator",
    "skill-installer",
}

# ---------------------------------------------------------------------------
# Minimal in-test JSON Schema subset validator (no external dependency)
# ---------------------------------------------------------------------------

_SUPPORTED_SCHEMA_KEYS = {
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "allOf",
    "const",
    "definitions",
    "enum",
    "if",
    "items",
    "minItems",
    "minLength",
    "minimum",
    "oneOf",
    "properties",
    "required",
    "then",
    "title",
    "type",
}


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def _resolve_schema_ref(ref: str, root_schema: dict, schemas: dict[str, dict] | None = None) -> dict:
    if schemas and ref in schemas:
        return schemas[ref]
    if schemas and "#" in ref and not ref.startswith("#/"):
        schema_name, fragment = ref.split("#", 1)
        base = schemas[schema_name]
        return _resolve_schema_ref("#" + fragment, base, schemas)
    node = root_schema
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
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise AssertionError(f"Unsupported schema type in test validator: {expected}")


def _validate_schema(
    schema: dict,
    value: object,
    root_schema: dict,
    schemas: dict[str, dict] | None = None,
    path: str = "$",
) -> None:
    if "$ref" in schema:
        _validate_schema(
            _resolve_schema_ref(schema["$ref"], root_schema, schemas),
            value,
            root_schema,
            schemas,
            path,
        )
        return

    for subschema in schema.get("allOf", []):
        _validate_schema(subschema, value, root_schema, schemas, path)

    if "if" in schema:
        try:
            _validate_schema(schema["if"], value, root_schema, schemas, path)
        except AssertionError:
            pass
        else:
            if "then" in schema:
                _validate_schema(schema["then"], value, root_schema, schemas, path)

    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                _validate_schema(option, value, root_schema, schemas, path)
            except AssertionError:
                continue
            matches += 1
        if matches != 1:
            raise AssertionError(f"{path}: expected exactly one oneOf match, got {matches}")

    if "type" in schema:
        expected_types = schema["type"]
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_schema_type_matches(value, t) for t in expected_types):
            raise AssertionError(f"{path}: expected {expected_types}, got {type(value).__name__}")

    if "const" in schema and value != schema["const"]:
        raise AssertionError(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise AssertionError(f"{path}: expected one of {schema['enum']!r}, got {value!r}")

    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        raise AssertionError(f"{path}: shorter than minLength {schema['minLength']}")

    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema:
        if value < schema["minimum"]:
            raise AssertionError(f"{path}: smaller than minimum {schema['minimum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise AssertionError(f"{path}: fewer items than minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                _validate_schema(schema["items"], item, root_schema, schemas, f"{path}[{i}]")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise AssertionError(f"{path} missing required key {key!r}")
        props = schema.get("properties", {})
        for key, child in props.items():
            if key in value:
                _validate_schema(child, value[key], root_schema, schemas, f"{path}.{key}")
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(props)
            if extra:
                raise AssertionError(f"{path} unexpected keys {sorted(extra)}")


# ---------------------------------------------------------------------------
# Schema file structural validity tests
# ---------------------------------------------------------------------------

class TestSchemaFilesExistAndAreValidJson(unittest.TestCase):
    """The three schema files introduced by JSC-351 must exist and be valid JSON."""

    def _assert_schema_file(self, path: Path) -> dict:
        self.assertTrue(path.exists(), f"Schema file missing: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, f"Schema is not a JSON object: {path}")
        return data

    def test_skill_doctor_schema_file_exists_and_is_valid_json(self) -> None:
        self._assert_schema_file(SKILL_DOCTOR_SCHEMA_PATH)

    def test_skill_package_schema_file_exists_and_is_valid_json(self) -> None:
        self._assert_schema_file(SKILL_PACKAGE_SCHEMA_PATH)

    def test_skill_package_readiness_schema_file_exists_and_is_valid_json(self) -> None:
        self._assert_schema_file(SKILL_PACKAGE_READINESS_SCHEMA_PATH)

    def test_skills_sdk_project_schema_file_exists_and_is_valid_json(self) -> None:
        self._assert_schema_file(SKILLS_SDK_PROJECT_SCHEMA_PATH)

    def test_skill_doctor_schema_has_draft07_declaration(self) -> None:
        schema = _load_schema("skill-doctor.v1.schema.json")
        self.assertIn("$schema", schema)
        self.assertIn("draft-07", schema["$schema"])

    def test_skill_package_schema_has_draft07_declaration(self) -> None:
        schema = _load_schema("skill-package.v1.schema.json")
        self.assertIn("$schema", schema)
        self.assertIn("draft-07", schema["$schema"])

    def test_skill_package_readiness_schema_has_draft07_declaration(self) -> None:
        schema = _load_schema("skill-package-readiness.v1.schema.json")
        self.assertIn("$schema", schema)
        self.assertIn("draft-07", schema["$schema"])

    def test_skills_sdk_project_schema_has_draft07_declaration(self) -> None:
        schema = _load_schema("skills-sdk.project.v1.schema.json")
        self.assertIn("$schema", schema)
        self.assertIn("draft-07", schema["$schema"])


# ---------------------------------------------------------------------------
# skill-doctor.v1.schema.json contract tests
# ---------------------------------------------------------------------------

class TestSkillDoctorSchemaStructure(unittest.TestCase):
    """skill-doctor.v1.schema.json must enforce the JSC-351 ABI contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-doctor.v1.schema.json")

    def test_schema_version_const_is_skill_doctor_v1(self) -> None:
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"],
            "skill-doctor.v1",
        )

    def test_top_level_disallows_additional_properties(self) -> None:
        self.assertFalse(
            self.schema.get("additionalProperties"),
            "skill-doctor.v1 must set additionalProperties: false at the top level",
        )

    def test_next_command_decision_is_optional_for_v1_compatibility(self) -> None:
        """next_command_decision is emitted by JSC-351 but optional in the v1 schema."""
        required = self.schema.get("required", [])
        self.assertNotIn("next_command_decision", required)

    def test_next_command_decision_has_precedence_enum(self) -> None:
        """next_command_decision.precedence must be one of: blocker, warning, default."""
        ncd = self.schema["properties"]["next_command_decision"]
        precedence_prop = ncd["properties"]["precedence"]
        self.assertEqual(
            sorted(precedence_prop["enum"]),
            ["blocker", "default", "warning"],
        )

    def test_next_command_decision_requires_command_precedence_reason(self) -> None:
        ncd = self.schema["properties"]["next_command_decision"]
        required = ncd.get("required", [])
        for field in ("command", "precedence", "reason"):
            self.assertIn(field, required, f"next_command_decision missing required field '{field}'")

    def test_status_enum_values(self) -> None:
        status_prop = self.schema["properties"]["status"]
        self.assertEqual(sorted(status_prop["enum"]), ["blocked", "pass", "warning"])

    def test_target_kind_enum_values(self) -> None:
        target_kind_prop = self.schema["properties"]["target_kind"]
        self.assertIn("command_handle", target_kind_prop["enum"])
        self.assertIn("canonical_source_path", target_kind_prop["enum"])

    def test_sdk_layers_enum_contains_all_required_layers(self) -> None:
        sdk_layers_prop = self.schema["properties"]["sdk_layers"]
        self.assertEqual(sdk_layers_prop["minItems"], 1)
        layer_enum = sdk_layers_prop["items"]["enum"]
        for expected_layer in (
            "Contracts",
            "Catalog",
            "Authoring",
            "Validation",
            "Packaging",
            "Runtime Adapters",
            "Evidence",
            "Memory",
        ):
            self.assertIn(expected_layer, layer_enum, f"Missing SDK layer: {expected_layer}")

    def test_checks_object_requires_core_checks(self) -> None:
        checks = self.schema["properties"]["checks"]
        required = checks.get("required", [])
        for check_name in (
            "resolver",
            "canonical_source",
            "structural_audit",
            "capability_metadata",
            "package_readiness",
            "outcome_proof",
        ):
            self.assertIn(check_name, required, f"checks missing required check '{check_name}'")
        self.assertIn(
            "projection_ownership",
            checks.get("properties", {}),
            "checks must still document optional projection_ownership payloads",
        )
        self.assertNotIn(
            "projection_ownership",
            required,
            "skill-doctor.v1 cannot require newly added checks from older producers",
        )

    def test_checks_disallows_additional_properties(self) -> None:
        checks = self.schema["properties"]["checks"]
        self.assertFalse(
            checks.get("additionalProperties"),
            "checks must set additionalProperties: false",
        )

    def test_check_definition_requires_status_and_sdk_layer(self) -> None:
        check_def = self.schema["definitions"]["check"]
        required = check_def.get("required", [])
        self.assertIn("status", required)
        self.assertIn("sdk_layer", required)

    def test_check_status_enum_includes_blocked(self) -> None:
        check_def = self.schema["definitions"]["check"]
        status_enum = check_def["properties"]["status"]["enum"]
        self.assertIn("blocked", status_enum)

    def test_diagnostic_definition_disallows_additional_properties(self) -> None:
        diagnostic = self.schema["definitions"]["diagnostic"]
        self.assertFalse(
            diagnostic.get("additionalProperties"),
            "diagnostic definition must set additionalProperties: false",
        )

    def test_schema_ref_definition_requires_owner_const(self) -> None:
        schema_ref = self.schema["definitions"]["schemaRef"]
        owner_prop = schema_ref["properties"]["owner"]
        self.assertEqual(owner_prop["const"], "Agent Skills Kit")

    def test_lifecycle_event_requires_skill_doctor_completed_event_type(self) -> None:
        lc_event = self.schema["properties"]["lifecycle_event"]
        event_type_const = lc_event["properties"]["event_type"]["const"]
        self.assertEqual(event_type_const, "skill_doctor_completed")

    def test_contract_schemas_object_requires_six_named_schemas(self) -> None:
        contract_schemas = self.schema["properties"]["contract_schemas"]
        required = contract_schemas.get("required", [])
        for name in ("doctor", "events", "lifecycle_event", "profiles", "package", "memory"):
            self.assertIn(name, required, f"contract_schemas missing required schema '{name}'")


class TestSkillDoctorSchemaAcceptsValidPayload(unittest.TestCase):
    """The skill-doctor.v1.schema.json must accept a minimal valid payload."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-doctor.v1.schema.json")

    def _make_minimal_valid_payload(self) -> dict:
        return {
            "schema_version": "skill-doctor.v1",
            "query": "autofix",
            "target_kind": "command_handle",
            "target_summary": {"query": "autofix", "target_kind": "command_handle"},
            "status": "pass",
            "blockers": [],
            "warnings": [],
            "readiness_taxonomy": {"blockers": {}, "warnings": {}},
            "sdk_layers": ["Catalog"],
            "contract_schemas": {
                "doctor": {
                    "name": "doctor",
                    "version": "skill-doctor.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "path": "Infrastructure/config/schemas/skill-doctor.v1.schema.json",
                },
                "events": {
                    "name": "events",
                    "version": "events.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
                "lifecycle_event": {
                    "name": "lifecycle_event",
                    "version": "capability-lifecycle-event.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
                "profiles": {
                    "name": "profiles",
                    "version": "profiles.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
                "package": {
                    "name": "package",
                    "version": "skill-package-readiness.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "path": "Infrastructure/config/schemas/skill-package-readiness.v1.schema.json",
                },
                "memory": {
                    "name": "memory",
                    "version": "memory.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
            },
            "contract_schema_versions": {"doctor": "skill-doctor.v1"},
            "operation_context": {
                "primary_profile": "default",
                "profiles": {},
                "events": {},
                "validation_commands": [],
            },
            "lifecycle_event": {
                "schema_version": "capability-lifecycle-event.v1",
                "event_type": "skill_doctor_completed",
                "event_identity": {},
                "outcome": {
                    "status": "pass",
                    "blocker_classes": [],
                    "warning_classes": [],
                },
            },
            "lifecycle_event_types": {"eval_blocked": "eval_blocked_description"},
            "checks": {
                "resolver": {"status": "pass", "sdk_layer": "Catalog"},
                "canonical_source": {"status": "pass", "sdk_layer": "Catalog"},
                "projection_ownership": {"status": "pass", "sdk_layer": "Runtime Adapters"},
                "structural_audit": {"status": "pass", "sdk_layer": "Validation"},
                "capability_metadata": {"status": "pass", "sdk_layer": "Contracts"},
                "package_readiness": {"status": "pass", "sdk_layer": "Packaging"},
                "outcome_proof": {"status": "available_not_run", "sdk_layer": "Evidence"},
            },
            "check_summary": {
                "check_names": ["resolver"],
                "check_count": 1,
                "status_counts": {"pass": 1},
                "failed_checks": [],
                "warning_checks": [],
            },
            "agent_summary": "Skill autofix passed doctor.",
            "next_command": None,
            "next_command_decision": {
                "command": None,
                "precedence": "default",
                "reason": "no blockers or warnings",
            },
        }

    def test_valid_payload_passes_schema(self) -> None:
        payload = self._make_minimal_valid_payload()
        try:
            _validate_schema(self.schema, payload, self.schema)
        except AssertionError as exc:
            self.fail(f"Valid payload rejected by skill-doctor.v1 schema: {exc}")

    def test_payload_with_blocked_status_passes_schema(self) -> None:
        payload = self._make_minimal_valid_payload()
        payload["status"] = "blocked"
        payload["blockers"] = [
            {
                "class": "blocked_runtime",
                "sdk_layer": "Runtime Adapters",
                "message": "Runtime proof failed.",
                "definition": "Codex user runtime is not ready.",
            }
        ]
        payload["lifecycle_event"]["outcome"]["status"] = "blocked"
        payload["lifecycle_event"]["outcome"]["blocker_classes"] = ["blocked_runtime"]
        payload["next_command"] = "./bin/ask skills proof autofix --runtime-target codex --json --robot"
        payload["next_command_decision"] = {
            "command": "./bin/ask skills proof autofix --runtime-target codex --json --robot",
            "precedence": "blocker",
            "source_class": "blocked_runtime",
            "source_check": "runtime_reachability",
            "reason": "blocked_runtime class from runtime_reachability check",
        }
        try:
            _validate_schema(self.schema, payload, self.schema)
        except AssertionError as exc:
            self.fail(f"Blocked-status payload rejected by skill-doctor.v1 schema: {exc}")

    def test_payload_without_projection_ownership_preserves_v1_compatibility(self) -> None:
        payload = self._make_minimal_valid_payload()
        del payload["checks"]["projection_ownership"]
        try:
            _validate_schema(self.schema, payload, self.schema)
        except AssertionError as exc:
            self.fail(f"Legacy skill-doctor.v1 payload rejected without projection_ownership: {exc}")


class TestSkillDoctorSchemaRejectsInvalidPayloads(unittest.TestCase):
    """The skill-doctor.v1.schema.json must reject non-conforming payloads."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-doctor.v1.schema.json")

    def _make_base_payload(self) -> dict:
        return {
            "schema_version": "skill-doctor.v1",
            "query": "autofix",
            "target_kind": "command_handle",
            "target_summary": {"query": "autofix", "target_kind": "command_handle"},
            "status": "pass",
            "blockers": [],
            "warnings": [],
            "readiness_taxonomy": {"blockers": {}, "warnings": {}},
            "sdk_layers": ["Catalog"],
            "contract_schemas": {
                "doctor": {
                    "name": "doctor",
                    "version": "skill-doctor.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "path": "Infrastructure/config/schemas/skill-doctor.v1.schema.json",
                },
                "events": {
                    "name": "events",
                    "version": "events.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
                "lifecycle_event": {
                    "name": "lifecycle_event",
                    "version": "capability-lifecycle-event.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
                "profiles": {
                    "name": "profiles",
                    "version": "profiles.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
                "package": {
                    "name": "package",
                    "version": "skill-package-readiness.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "path": "Infrastructure/config/schemas/skill-package-readiness.v1.schema.json",
                },
                "memory": {
                    "name": "memory",
                    "version": "memory.v1",
                    "owner": "Agent Skills Kit",
                    "stability": "experimental",
                    "missing_schema_reason": "not yet defined",
                },
            },
            "contract_schema_versions": {"doctor": "skill-doctor.v1"},
            "operation_context": {
                "primary_profile": "default",
                "profiles": {},
                "events": {},
                "validation_commands": [],
            },
            "lifecycle_event": {
                "schema_version": "capability-lifecycle-event.v1",
                "event_type": "skill_doctor_completed",
                "event_identity": {},
                "outcome": {
                    "status": "pass",
                    "blocker_classes": [],
                    "warning_classes": [],
                },
            },
            "lifecycle_event_types": {"eval_blocked": "eval_blocked_description"},
            "checks": {
                "resolver": {"status": "pass", "sdk_layer": "Catalog"},
                "canonical_source": {"status": "pass", "sdk_layer": "Catalog"},
                "projection_ownership": {"status": "pass", "sdk_layer": "Runtime Adapters"},
                "structural_audit": {"status": "pass", "sdk_layer": "Validation"},
                "capability_metadata": {"status": "pass", "sdk_layer": "Contracts"},
                "package_readiness": {"status": "pass", "sdk_layer": "Packaging"},
                "outcome_proof": {"status": "available_not_run", "sdk_layer": "Evidence"},
            },
            "check_summary": {
                "check_names": ["resolver"],
                "check_count": 1,
                "status_counts": {"pass": 1},
                "failed_checks": [],
                "warning_checks": [],
            },
            "agent_summary": "Skill autofix passed doctor.",
            "next_command": None,
            "next_command_decision": {
                "command": None,
                "precedence": "default",
                "reason": "no blockers or warnings",
            },
        }

    def test_rejects_missing_schema_version(self) -> None:
        payload = self._make_base_payload()
        del payload["schema_version"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("missing required key", str(ctx.exception))

    def test_accepts_missing_next_command_decision_for_v1_compatibility(self) -> None:
        payload = self._make_base_payload()
        del payload["next_command_decision"]
        _validate_schema(self.schema, payload, self.schema)

    def test_rejects_invalid_status_value(self) -> None:
        payload = self._make_base_payload()
        payload["status"] = "unknown_status"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("expected one of", str(ctx.exception))

    def test_rejects_invalid_next_command_decision_precedence(self) -> None:
        payload = self._make_base_payload()
        payload["next_command_decision"]["precedence"] = "critical"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("expected one of", str(ctx.exception))

    def test_rejects_unknown_top_level_keys(self) -> None:
        payload = self._make_base_payload()
        payload["jsc351_extra_field"] = "should_not_be_here"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_invalid_target_kind_value(self) -> None:
        payload = self._make_base_payload()
        payload["target_kind"] = "not_a_valid_kind"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("expected one of", str(ctx.exception))

    def test_rejects_unknown_sdk_layer(self) -> None:
        payload = self._make_base_payload()
        payload["sdk_layers"] = ["UnknownLayer"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("expected one of", str(ctx.exception))

    def test_rejects_empty_sdk_layers(self) -> None:
        payload = self._make_base_payload()
        payload["sdk_layers"] = []
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("minItems", str(ctx.exception))

    def test_rejects_check_with_unknown_keys_when_strict(self) -> None:
        payload = self._make_base_payload()
        # checks object itself has additionalProperties: false
        payload["checks"]["extra_check"] = {"status": "pass", "sdk_layer": "Catalog"}
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_diagnostic_with_unknown_fields(self) -> None:
        payload = self._make_base_payload()
        payload["status"] = "blocked"
        payload["blockers"] = [
            {
                "class": "blocked_runtime",
                "sdk_layer": "Runtime Adapters",
                "message": "Runtime proof failed.",
                "definition": "Codex user runtime is not ready.",
                "unknown_field": "reject_this",
            }
        ]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_wrong_schema_version_const(self) -> None:
        payload = self._make_base_payload()
        payload["schema_version"] = "skill-doctor.v2"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("expected const", str(ctx.exception))

    def test_rejects_lifecycle_event_wrong_event_type(self) -> None:
        payload = self._make_base_payload()
        payload["lifecycle_event"]["event_type"] = "wrong_event"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema)
        self.assertIn("expected const", str(ctx.exception))


# ---------------------------------------------------------------------------
# skills-sdk.project.v1.schema.json contract tests
# ---------------------------------------------------------------------------

class TestSkillsSdkProjectSchemaStructure(unittest.TestCase):
    """skills-sdk.project.v1.schema.json must define owner-repo source boundaries."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skills-sdk.project.v1.schema.json")

    def _make_valid_manifest(self) -> dict:
        return {
            "schema_version": "skills-sdk.project.v1",
            "project_id": "example-owner-repo",
            "skill_roots": [
                {
                    "path": ".agents/skills",
                    "classification": "canonical_project_source",
                    "default_for_create": True,
                    "default_for_install": True,
                    "default_for_update": True,
                }
            ],
            "eval_suite": {"path": ".harness/evals/skills"},
            "evidence": {"output_path": ".harness/session-evidence/skills"},
            "trust_policy": "local_owner",
            "precedence_policy": "project_over_user_after_trust",
        }

    def test_schema_version_const_is_skills_sdk_project_v1(self) -> None:
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"],
            "skills-sdk.project.v1",
        )

    def test_root_classification_enum_matches_sdk_contract(self) -> None:
        classification_enum = self.schema["definitions"]["skillRoot"]["properties"]["classification"]["enum"]
        self.assertEqual(
            sorted(classification_enum),
            [
                "canonical_project_source",
                "client_runtime_config",
                "generated_runtime_projection",
                "unknown",
            ],
        )

    def test_skill_roots_document_unique_path_requirement(self) -> None:
        description = self.schema["properties"]["skill_roots"].get("description", "")
        self.assertIn("unique", description.lower())
        self.assertIn("path", description.lower())

    def test_skill_root_properties_have_descriptions(self) -> None:
        skill_root = self.schema["definitions"]["skillRoot"]
        self.assertIn("description", skill_root)
        for property_name in (
            "path",
            "classification",
            "default_for_create",
            "default_for_install",
            "default_for_update",
        ):
            with self.subTest(property_name=property_name):
                self.assertIn(
                    "description",
                    skill_root["properties"][property_name],
                )

    def test_valid_project_manifest_passes_schema(self) -> None:
        try:
            _validate_schema(self.schema, self._make_valid_manifest(), self.schema)
        except AssertionError as exc:
            self.fail(f"Valid skills-sdk.project.v1 manifest rejected: {exc}")

    def test_manifest_requires_skill_roots(self) -> None:
        manifest = self._make_valid_manifest()
        manifest.pop("skill_roots")
        with self.assertRaises(AssertionError):
            _validate_schema(self.schema, manifest, self.schema)

    def test_manifest_requires_default_operation_flags(self) -> None:
        manifest = self._make_valid_manifest()
        manifest["skill_roots"][0].pop("default_for_update")
        with self.assertRaises(AssertionError):
            _validate_schema(self.schema, manifest, self.schema)

    def test_manifest_rejects_unknown_root_classification(self) -> None:
        manifest = self._make_valid_manifest()
        manifest["skill_roots"][0]["classification"] = "editable_runtime_projection"
        with self.assertRaises(AssertionError):
            _validate_schema(self.schema, manifest, self.schema)


# ---------------------------------------------------------------------------
# skill-package.v1.schema.json contract tests
# ---------------------------------------------------------------------------

class TestSkillPackageSchemaStructure(unittest.TestCase):
    """skill-package.v1.schema.json must enforce the JSC-351 SkillPackage v1 contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-package.v1.schema.json")

    def test_schema_version_const_is_skill_package_v1(self) -> None:
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"],
            "skill-package.v1",
        )

    def test_top_level_disallows_additional_properties(self) -> None:
        self.assertFalse(
            self.schema.get("additionalProperties"),
            "skill-package.v1 must set additionalProperties: false at the top level",
        )

    def test_required_fields(self) -> None:
        required = self.schema.get("required", [])
        for field in ("schema_version", "metadata", "required_fields", "compatibility_status"):
            self.assertIn(field, required)

    def test_metadata_disallows_additional_properties(self) -> None:
        metadata = self.schema["properties"]["metadata"]
        self.assertFalse(
            metadata.get("additionalProperties"),
            "skill-package.v1 metadata must set additionalProperties: false",
        )

    def test_metadata_requires_name_and_description(self) -> None:
        metadata = self.schema["properties"]["metadata"]
        required = metadata.get("required", [])
        self.assertIn("name", required)
        self.assertIn("description", required)

    def test_compatibility_status_enum(self) -> None:
        compat = self.schema["properties"]["compatibility_status"]
        self.assertEqual(
            sorted(compat["enum"]),
            ["blocked_missing_source", "blocked_validation", "compatible"],
        )

    def test_codex_abi_source_requires_path_struct_evidence_fields(self) -> None:
        abi_source = self.schema["properties"]["codex_abi_source"]
        required = abi_source.get("required", [])
        for field in ("path", "struct", "evidence_fields"):
            self.assertIn(field, required)

    def test_codex_abi_source_struct_const_is_skill_metadata(self) -> None:
        struct_prop = self.schema["properties"]["codex_abi_source"]["properties"]["struct"]
        self.assertEqual(struct_prop["const"], "SkillMetadata")

    def test_required_fields_object_disallows_additional_properties(self) -> None:
        req_fields = self.schema["properties"]["required_fields"]
        self.assertFalse(
            req_fields.get("additionalProperties"),
            "required_fields must set additionalProperties: false",
        )

    def test_source_files_disallows_additional_properties(self) -> None:
        src_files = self.schema["properties"]["source_files"]
        self.assertFalse(
            src_files.get("additionalProperties"),
            "source_files must set additionalProperties: false",
        )


class TestSkillPackageSchemaAcceptsValidPayload(unittest.TestCase):
    """skill-package.v1.schema.json must accept minimal valid Codex package contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-package.v1.schema.json")

    def _make_minimal_valid_contract(self) -> dict:
        return {
            "schema_version": "skill-package.v1",
            "metadata": {
                "name": "test-skill",
                "description": "A test skill.",
            },
            "source_files": {
                "skill_md": "Skills/example/SKILL.md",
                "agents_openai_yaml": "Skills/example/agents/openai.yaml",
            },
            "codex_abi_source": {
                "path": "codex-rs/core-skills/src/model.rs",
                "struct": "SkillMetadata",
                "evidence_fields": ["name", "description"],
            },
            "required_fields": {
                "present": ["name", "description"],
                "missing": [],
            },
            "compatibility_status": "compatible",
        }

    def test_minimal_contract_passes_schema(self) -> None:
        contract = self._make_minimal_valid_contract()
        try:
            _validate_schema(self.schema, contract, self.schema)
        except AssertionError as exc:
            self.fail(f"Valid minimal contract rejected by skill-package.v1 schema: {exc}")

    def test_contract_with_codex_abi_source_passes_schema(self) -> None:
        contract = self._make_minimal_valid_contract()
        contract["codex_abi_source"] = {
            "path": "codex-rs/core-skills/src/model.rs",
            "struct": "SkillMetadata",
            "evidence_fields": ["name", "description", "interface"],
        }
        try:
            _validate_schema(self.schema, contract, self.schema)
        except AssertionError as exc:
            self.fail(f"Contract with codex_abi_source rejected: {exc}")

    def test_contract_with_all_optional_metadata_passes_schema(self) -> None:
        contract = self._make_minimal_valid_contract()
        contract["metadata"]["short_description"] = "Short."
        contract["metadata"]["scope"] = "global"
        contract["metadata"]["plugin_id"] = "plugin-abc"
        contract["metadata"]["interface"] = {"display_name": "Test Skill"}
        try:
            _validate_schema(self.schema, contract, self.schema)
        except AssertionError as exc:
            self.fail(f"Contract with full metadata rejected: {exc}")

    def test_blocked_missing_source_status_passes_schema(self) -> None:
        contract = self._make_minimal_valid_contract()
        contract["compatibility_status"] = "blocked_missing_source"
        contract["metadata"]["name"] = None
        contract["metadata"]["description"] = None
        del contract["source_files"]
        del contract["codex_abi_source"]
        contract["required_fields"]["present"] = []
        contract["required_fields"]["missing"] = ["name", "description"]
        try:
            _validate_schema(self.schema, contract, self.schema)
        except AssertionError as exc:
            self.fail(f"blocked_missing_source contract rejected: {exc}")


class TestSkillPackageSchemaRejectsInvalidPayloads(unittest.TestCase):
    """skill-package.v1.schema.json must reject non-conforming contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-package.v1.schema.json")

    def _make_base_contract(self) -> dict:
        return {
            "schema_version": "skill-package.v1",
            "metadata": {"name": "test-skill", "description": "A test skill."},
            "source_files": {
                "skill_md": "Skills/example/SKILL.md",
                "agents_openai_yaml": "Skills/example/agents/openai.yaml",
            },
            "codex_abi_source": {
                "path": "codex-rs/core-skills/src/model.rs",
                "struct": "SkillMetadata",
                "evidence_fields": ["name", "description"],
            },
            "required_fields": {"present": ["name", "description"], "missing": []},
            "compatibility_status": "compatible",
        }

    def test_rejects_missing_metadata(self) -> None:
        contract = self._make_base_contract()
        del contract["metadata"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("missing required key 'metadata'", str(ctx.exception))

    def test_rejects_missing_compatibility_status(self) -> None:
        contract = self._make_base_contract()
        del contract["compatibility_status"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("missing required key 'compatibility_status'", str(ctx.exception))

    def test_rejects_invalid_compatibility_status(self) -> None:
        contract = self._make_base_contract()
        contract["compatibility_status"] = "valid_but_wrong"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("expected one of", str(ctx.exception))

    def test_rejects_compatible_contract_with_null_core_metadata(self) -> None:
        contract = self._make_base_contract()
        contract["metadata"]["name"] = None
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("$.metadata.name", str(ctx.exception))

    def test_rejects_unknown_top_level_key(self) -> None:
        contract = self._make_base_contract()
        contract["extra_key"] = "should_fail"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_unknown_metadata_key(self) -> None:
        contract = self._make_base_contract()
        contract["metadata"]["unknown_field"] = "reject_this"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_metadata_missing_name(self) -> None:
        contract = self._make_base_contract()
        del contract["metadata"]["name"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("missing required key 'name'", str(ctx.exception))

    def test_rejects_wrong_schema_version(self) -> None:
        contract = self._make_base_contract()
        contract["schema_version"] = "skill-package.v2"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("expected const", str(ctx.exception))

    def test_rejects_required_fields_with_unknown_keys(self) -> None:
        contract = self._make_base_contract()
        contract["required_fields"]["extra"] = []
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_codex_abi_source_with_wrong_struct(self) -> None:
        contract = self._make_base_contract()
        contract["codex_abi_source"] = {
            "path": "codex-rs/core-skills/src/model.rs",
            "struct": "WrongStruct",
            "evidence_fields": ["name"],
        }
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, contract, self.schema)
        self.assertIn("expected const", str(ctx.exception))


# ---------------------------------------------------------------------------
# skill-package-readiness.v1.schema.json contract tests
# ---------------------------------------------------------------------------

class TestSkillPackageReadinessSchemaStructure(unittest.TestCase):
    """skill-package-readiness.v1.schema.json must enforce the JSC-351 payload contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-package-readiness.v1.schema.json")

    def test_schema_version_const_is_skill_package_readiness_v1(self) -> None:
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"],
            "skill-package-readiness.v1",
        )

    def test_top_level_disallows_additional_properties(self) -> None:
        self.assertFalse(
            self.schema.get("additionalProperties"),
            "skill-package-readiness.v1 must set additionalProperties: false",
        )

    def test_required_fields_include_compatibility_snapshot(self) -> None:
        required = self.schema.get("required", [])
        self.assertIn("compatibility_snapshot", required)

    def test_required_fields_include_skill_package_contract(self) -> None:
        required = self.schema.get("required", [])
        self.assertIn("skill_package_contract", required)

    def test_compatibility_snapshot_requires_four_fields(self) -> None:
        snapshot = self.schema["properties"]["compatibility_snapshot"]
        required = snapshot.get("required", [])
        for field in ("id", "schema_version", "path", "covers"):
            self.assertIn(field, required, f"compatibility_snapshot missing required '{field}'")

    def test_compatibility_snapshot_schema_version_const(self) -> None:
        snapshot = self.schema["properties"]["compatibility_snapshot"]
        schema_version_prop = snapshot["properties"]["schema_version"]
        self.assertEqual(schema_version_prop["const"], "skill-package-readiness.v1")

    def test_compatibility_snapshot_disallows_additional_properties(self) -> None:
        snapshot = self.schema["properties"]["compatibility_snapshot"]
        self.assertFalse(
            snapshot.get("additionalProperties"),
            "compatibility_snapshot must set additionalProperties: false",
        )

    def test_status_enum_values(self) -> None:
        status_prop = self.schema["properties"]["status"]
        self.assertEqual(sorted(status_prop["enum"]), ["blocked", "pass", "warning"])

    def test_skill_package_contract_references_skill_package_schema(self) -> None:
        skill_pkg = self.schema["properties"]["skill_package_contract"]
        self.assertIn("$ref", skill_pkg)
        self.assertIn("skill-package.v1.schema.json", skill_pkg["$ref"])

    def test_package_contract_requires_core_gate_fields(self) -> None:
        pkg_contract = self.schema["properties"]["package_contract"]
        required = pkg_contract.get("required", [])
        for field in ("readiness_level", "required_fields", "values", "install_gate", "promotion_gate"):
            self.assertIn(field, required, f"package_contract missing required '{field}'")

    def test_gate_summary_requires_core_fields(self) -> None:
        gate_summary = self.schema["properties"]["gate_summary"]
        required = gate_summary.get("required", [])
        for field in ("install_ready", "checkout_test_status", "promotion_status", "blocked_reasons"):
            self.assertIn(field, required, f"gate_summary missing required '{field}'")

    def test_schema_pointer_definition_requires_schema_version_and_path(self) -> None:
        schema_pointer = self.schema["definitions"]["schemaPointer"]
        required = schema_pointer.get("required", [])
        self.assertIn("schema_version", required)
        self.assertIn("path", required)

    def test_schema_pointer_definition_disallows_additional_properties(self) -> None:
        schema_pointer = self.schema["definitions"]["schemaPointer"]
        self.assertFalse(
            schema_pointer.get("additionalProperties"),
            "schemaPointer must set additionalProperties: false",
        )


class TestSkillPackageReadinessSchemaRejectsInvalidPayloads(unittest.TestCase):
    """skill-package-readiness.v1.schema.json must reject non-conforming payloads."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema("skill-package-readiness.v1.schema.json")
        cls.schemas = {
            "skill-package.v1.schema.json": _load_schema("skill-package.v1.schema.json"),
            "skill-package-readiness.v1.schema.json": cls.schema,
        }

    def _make_base_payload(self) -> dict:
        return {
            "schema_version": "skill-package-readiness.v1",
            "query": "test-skill",
            "target_kind": "command_handle",
            "status": "pass",
            "package_schema": {"schema_version": "skill-package.v1", "path": "schemas/skill-package.v1.schema.json"},
            "package_readiness_schema": {"schema_version": "skill-package-readiness.v1", "path": "schemas/skill-package-readiness.v1.schema.json"},
            "compatibility_snapshot": {
                "id": "skill-package-readiness.v1.public-output.2026-05-23",
                "schema_version": "skill-package-readiness.v1",
                "path": "tests/fixtures/skill_package_snapshots/skill-package-readiness-public-output.v1.json",
                "covers": ["valid_share_ready_package"],
            },
            "skill_package_contract": {
                "schema_version": "skill-package.v1",
                "metadata": {"name": "test-skill", "description": "A test skill."},
                "source_files": {
                    "skill_md": "Skills/example/SKILL.md",
                    "agents_openai_yaml": "Skills/example/agents/openai.yaml",
                },
                "codex_abi_source": {
                    "path": "codex-rs/core-skills/src/model.rs",
                    "struct": "SkillMetadata",
                    "evidence_fields": ["name", "description"],
                },
                "required_fields": {"present": ["name", "description"], "missing": []},
                "compatibility_status": "compatible",
            },
            "package_contract": {
                "readiness_level": "share_ready",
                "required_fields": ["name", "description"],
                "values": {},
                "role_compatibility": {},
                "runtime_contract": {},
                "install_gate": {"install_ready": True, "checkout_test_status": "pass", "blocked_reasons": []},
                "promotion_gate": {"status": "pass", "promotion_ready": True, "share_ready": True, "blocked_reasons": []},
            },
            "gate_summary": {
                "install_ready": True,
                "checkout_test_status": "pass",
                "promotion_status": "pass",
                "promotion_ready": True,
                "blocked_reasons": [],
            },
            "readiness_summary": {
                "readiness_level": "share_ready",
                "present_fields": ["name", "description"],
                "missing_fields": [],
                "missing_field_count": 0,
                "promotion_status": "pass",
            },
            "contract_schemas": {"package": "skill-package.v1", "skill_package": "skill-package.v1"},
            "blockers": [],
            "warnings": [],
            "lifecycle_event": {
                "schema_version": "capability-lifecycle-event.v1",
                "event_type": "skill_package_completed",
                "event_identity": {},
                "outcome": {"status": "pass"},
            },
            "lifecycle_events": [],
            "agent_summary": "Package test-skill is ready.",
            "next_command": "./bin/ask skills doctor test-skill --json --robot",
        }

    def test_rejects_missing_compatibility_snapshot(self) -> None:
        payload = self._make_base_payload()
        del payload["compatibility_snapshot"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema, self.schemas)
        self.assertIn("missing required key 'compatibility_snapshot'", str(ctx.exception))

    def test_rejects_unknown_top_level_key(self) -> None:
        payload = self._make_base_payload()
        payload["extra_key"] = "should_fail"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema, self.schemas)
        self.assertIn("unexpected keys", str(ctx.exception))

    def test_rejects_invalid_status(self) -> None:
        payload = self._make_base_payload()
        payload["status"] = "unknown"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema, self.schemas)
        self.assertIn("expected one of", str(ctx.exception))

    def test_rejects_missing_skill_package_contract(self) -> None:
        payload = self._make_base_payload()
        del payload["skill_package_contract"]
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema, self.schemas)
        self.assertIn("missing required key 'skill_package_contract'", str(ctx.exception))

    def test_rejects_wrong_compatibility_snapshot_schema_version(self) -> None:
        payload = self._make_base_payload()
        payload["compatibility_snapshot"]["schema_version"] = "wrong-version"
        with self.assertRaises(AssertionError) as ctx:
            _validate_schema(self.schema, payload, self.schema, self.schemas)
        self.assertIn("expected const", str(ctx.exception))


# ---------------------------------------------------------------------------
# command-surface.json JSC-351 contract tests
# ---------------------------------------------------------------------------

class TestCommandSurfaceJsonJsc351Contract(unittest.TestCase):
    """Validate JSC-351 specific contracts in the updated command-surface.json."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))
        cls.handles: list[dict] = cls.data.get("handles", [])

    def test_generated_command_handle_count_is_absent(self) -> None:
        """The command surface is metadata only and has no generated wrapper count."""
        self.assertNotIn("generated_command_handle_count", self.data)

    def test_handles_do_not_include_command_handle_path(self) -> None:
        """No command-surface handle may point at a generated wrapper file."""
        for handle in self.handles:
            with self.subTest(handle=handle.get("handle")):
                self.assertNotIn("command_handle_path", handle)

    def test_handles_count_matches_handles_array_length(self) -> None:
        self.assertEqual(
            self.data["handle_count"],
            len(self.handles),
            "handle_count must equal length of handles array",
        )

    def test_generated_from_is_rooted_manifests(self) -> None:
        """JSC-351 establishes rooted manifest projection as the canonical mode."""
        self.assertEqual(
            self.data.get("generated_from"),
            "rooted_manifests",
        )

    def test_handles_from_skills_tree_resolve_to_canonical_skill_md(self) -> None:
        """Command-surface metadata resolves directly to canonical SKILL.md source."""
        for handle in self.handles:
            src = handle.get("source_path", "")
            if src.startswith("Skills/"):
                with self.subTest(handle=handle.get("handle")):
                    self.assertTrue(src.endswith("/SKILL.md"), src)


# ---------------------------------------------------------------------------
# Manifest JSONL cross-skillset consistency tests (JSC-351 specific)
# ---------------------------------------------------------------------------

class TestManifestJsc351Consistency(unittest.TestCase):
    """Validate that all skillset manifests are consistent after JSC-351 updates."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_paths = sorted(SKILLSETS_DIR.glob("*/manifest.jsonl"))
        cls.all_rows: list[dict[str, Any]] = []
        for path in cls.manifest_paths:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    cls.all_rows.append({"file": path, "row": json.loads(line)})

    def test_all_skillset_directories_have_manifest(self) -> None:
        """Every skillset subdirectory must contain a manifest.jsonl file."""
        for subdir in sorted(SKILLSETS_DIR.iterdir()):
            if subdir.is_dir():
                with self.subTest(skillset=subdir.name):
                    self.assertTrue(
                        (subdir / "manifest.jsonl").exists(),
                        f"Missing manifest.jsonl in .skillsets/{subdir.name}",
                    )

    def test_all_manifests_have_non_zero_entries(self) -> None:
        """Each manifest file must contain at least one skill entry."""
        for path in self.manifest_paths:
            rows = [
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            with self.subTest(manifest=path.name):
                self.assertGreater(len(rows), 0, f"Empty manifest: {path}")

    def test_all_manifests_use_rooted_projection_mode(self) -> None:
        """All manifests must use the rooted projection mode established in JSC-351."""
        for entry in self.all_rows:
            prov = entry["row"].get("provenance", {})
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertEqual(
                    prov.get("projection_mode"),
                    "rooted",
                    f"'{entry['row'].get('id')}' in {entry['file'].name} has wrong projection_mode",
                )

    def test_manifest_ids_are_unique_within_each_skillset(self) -> None:
        """Skill IDs must be unique within each skillset's manifest."""
        by_file: dict[Path, list[str]] = {}
        for entry in self.all_rows:
            by_file.setdefault(entry["file"], []).append(entry["row"].get("id", ""))
        for manifest_file, ids in by_file.items():
            with self.subTest(manifest=manifest_file.name):
                self.assertEqual(
                    len(ids),
                    len(set(ids)),
                    f"Duplicate IDs in {manifest_file.name}: {[x for x in ids if ids.count(x) > 1]}",
                )

    def test_manifest_skill_set_field_matches_parent_directory(self) -> None:
        """The skill_set field in each entry must match the containing directory name."""
        for entry in self.all_rows:
            expected = entry["file"].parent.name
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertEqual(
                    entry["row"].get("skill_set"),
                    expected,
                    f"skill_set mismatch in {entry['file'].name}: "
                    f"expected '{expected}', got '{entry['row'].get('skill_set')}'",
                )

    def test_manifest_source_paths_use_canonical_prefix(self) -> None:
        """source_path in manifests must start with Skills/, Plugins/, or skills-system/.

        skills-system/ is allowed for system bridge skills (e.g., imagegen, openai-docs,
        skill-creator, skill-installer) which are sourced from the system lane.
        """
        for entry in self.all_rows:
            src = entry["row"].get("source_path", "")
            with self.subTest(id=entry["row"].get("id"), file=entry["file"].name):
                self.assertTrue(
                    src.startswith("Skills/")
                    or src.startswith("Plugins/")
                    or src.startswith("skills-system/"),
                    f"'{entry['row'].get('id')}' in {entry['file'].name} has non-canonical source_path: {src}",
                )


# ---------------------------------------------------------------------------
# Schema cross-reference integrity tests
# ---------------------------------------------------------------------------

class TestSchemasCrossReferenceIntegrity(unittest.TestCase):
    """The new schema files must correctly cross-reference each other."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            "skill-doctor.v1.schema.json": _load_schema("skill-doctor.v1.schema.json"),
            "skill-package.v1.schema.json": _load_schema("skill-package.v1.schema.json"),
            "skill-package-readiness.v1.schema.json": _load_schema("skill-package-readiness.v1.schema.json"),
        }

    def test_skill_package_readiness_references_skill_package_schema(self) -> None:
        """skill-package-readiness.v1 must $ref skill-package.v1 for the contract field."""
        readiness_schema = self.schemas["skill-package-readiness.v1.schema.json"]
        skill_pkg_ref = readiness_schema["properties"]["skill_package_contract"]["$ref"]
        self.assertIn("skill-package.v1.schema.json", skill_pkg_ref)

    def test_skill_package_schema_referenced_file_exists(self) -> None:
        """The cross-referenced skill-package.v1.schema.json file must exist on disk."""
        self.assertTrue(
            SKILL_PACKAGE_SCHEMA_PATH.exists(),
            "skill-package.v1.schema.json referenced by skill-package-readiness.v1 must exist",
        )

    def test_all_internal_refs_in_skill_doctor_schema_resolve(self) -> None:
        """All $ref pointers in skill-doctor.v1.schema.json must resolve within the same file."""
        schema = self.schemas["skill-doctor.v1.schema.json"]

        def collect_refs(node: Any, path: str) -> list[tuple[str, str]]:
            refs = []
            if isinstance(node, dict):
                if "$ref" in node:
                    refs.append((node["$ref"], path))
                for key, value in node.items():
                    if key != "$ref":
                        refs.extend(collect_refs(value, f"{path}.{key}"))
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    refs.extend(collect_refs(item, f"{path}[{i}]"))
            return refs

        all_refs = collect_refs(schema, "$")
        for ref, ref_path in all_refs:
            with self.subTest(ref=ref, at=ref_path):
                self.assertTrue(
                    ref.startswith("#/"),
                    f"Expected internal $ref at {ref_path}, got external: {ref}",
                )
                try:
                    _resolve_schema_ref(ref, schema)
                except (KeyError, TypeError) as exc:
                    self.fail(f"$ref '{ref}' at {ref_path} failed to resolve: {exc}")

    def test_skill_doctor_schema_definitions_are_used(self) -> None:
        """All definitions in skill-doctor.v1.schema.json should be referenced."""
        schema = self.schemas["skill-doctor.v1.schema.json"]
        defined_names = set(schema.get("definitions", {}).keys())

        def collect_ref_targets(node: Any) -> set[str]:
            refs = set()
            if isinstance(node, dict):
                if "$ref" in node:
                    ref = node["$ref"]
                    if ref.startswith("#/definitions/"):
                        refs.add(ref.removeprefix("#/definitions/"))
                for key, value in node.items():
                    if key not in ("definitions",):
                        refs.update(collect_ref_targets(value))
            elif isinstance(node, list):
                for item in node:
                    refs.update(collect_ref_targets(item))
            return refs

        used_names = collect_ref_targets(schema)
        for name in defined_names:
            self.assertIn(
                name,
                used_names,
                f"Definition '{name}' in skill-doctor.v1.schema.json is never referenced",
            )


if __name__ == "__main__":
    unittest.main()
