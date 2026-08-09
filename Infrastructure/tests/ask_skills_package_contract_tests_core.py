import json
import os
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

class _AskSkillsPackageContractBase(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas = {'skill-package.v1.schema.json': _load_schema('skill-package.v1.schema.json'), 'skill-package-readiness.v1.schema.json': _load_schema('skill-package-readiness.v1.schema.json'), 'skillflow.v1.schema.json': _load_schema('skillflow.v1.schema.json'), 'skill-optimization-contract.v1.schema.json': _load_schema('skill-optimization-contract.v1.schema.json')}

__all__ = [name for name in globals() if not name.startswith("__")]
