"""Small JSON Schema subset validator used by contract tests."""

from __future__ import annotations

from typing import Any


SUPPORTED_SCHEMA_KEYS = {
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
    "maxItems",
    "minItems",
    "minLength",
    "minimum",
    "oneOf",
    "properties",
    "required",
    "then",
    "title",
    "type",
    "uniqueItems",
}


def _resolve_schema_ref(
    ref: str,
    schema: dict[str, Any],
    schemas: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if schemas and ref in schemas:
        return schemas[ref]
    if schemas and "#" in ref and not ref.startswith("#/"):
        schema_name, fragment = ref.split("#", 1)
        return _resolve_schema_ref("#" + fragment, schemas[schema_name], schemas)
    node: Any = schema
    for part in ref.removeprefix("#/").split("/"):
        if part:
            node = node[part]
    if not isinstance(node, dict):
        raise AssertionError(f"Schema ref {ref!r} did not resolve to an object")
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


def _validate_schema_ref(
    schema: dict[str, Any],
    value: object,
    schemas: dict[str, dict[str, Any]],
    path: str,
    root_schema: dict[str, Any],
) -> bool:
    if "$ref" not in schema:
        return False
    resolved_root = root_schema
    ref = schema["$ref"]
    if schemas and ref in schemas:
        resolved_root = schemas[ref]
    elif schemas and "#" in ref and not ref.startswith("#/"):
        schema_name, _fragment = ref.split("#", 1)
        resolved_root = schemas[schema_name]
    _validate_schema_subset(_resolve_schema_ref(ref, root_schema, schemas), value, schemas, path, resolved_root)
    return True


def _validate_schema_combinators(
    schema: dict[str, Any],
    value: object,
    schemas: dict[str, dict[str, Any]],
    path: str,
    root_schema: dict[str, Any],
) -> None:
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
        matches = sum(_schema_option_matches(option, value, schemas, path, root_schema) for option in schema["oneOf"])
        if matches != 1:
            raise AssertionError(f"{path} expected exactly one oneOf match, got {matches}")


def _schema_option_matches(
    schema: dict[str, Any],
    value: object,
    schemas: dict[str, dict[str, Any]],
    path: str,
    root_schema: dict[str, Any],
) -> bool:
    try:
        _validate_schema_subset(schema, value, schemas, path, root_schema)
    except AssertionError:
        return False
    return True


def _validate_type_constraint(schema: dict[str, Any], value: object, path: str) -> None:
    if "type" not in schema:
        return
    expected_types = schema["type"]
    if isinstance(expected_types, str):
        expected_types = [expected_types]
    if not any(_schema_type_matches(value, expected) for expected in expected_types):
        raise AssertionError(f"{path} expected {expected_types}, got {type(value).__name__}")


def _validate_scalar_constraints(schema: dict[str, Any], value: object, path: str) -> None:
    _validate_type_constraint(schema, value, path)
    if "const" in schema and value != schema["const"]:
        raise AssertionError(f"{path} expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise AssertionError(f"{path} expected one of {schema['enum']!r}, got {value!r}")
    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        raise AssertionError(f"{path} shorter than minLength {schema['minLength']}")
    if isinstance(value, int) and "minimum" in schema and value < schema["minimum"]:
        raise AssertionError(f"{path} smaller than minimum {schema['minimum']}")


def _validate_array_constraints(
    schema: dict[str, Any],
    value: list[object],
    schemas: dict[str, dict[str, Any]],
    path: str,
    root_schema: dict[str, Any],
) -> None:
    if "minItems" in schema and len(value) < schema["minItems"]:
        raise AssertionError(f"{path} shorter than minItems {schema['minItems']}")
    if "maxItems" in schema and len(value) > schema["maxItems"]:
        raise AssertionError(f"{path} longer than maxItems {schema['maxItems']}")
    if schema.get("uniqueItems") is True and len({repr(item) for item in value}) != len(value):
        raise AssertionError(f"{path} contains duplicate items")
    if "items" in schema:
        for index, item in enumerate(value):
            _validate_schema_subset(schema["items"], item, schemas, f"{path}[{index}]", root_schema)


def _validate_object_constraints(
    schema: dict[str, Any],
    value: dict[str, object],
    schemas: dict[str, dict[str, Any]],
    path: str,
    root_schema: dict[str, Any],
) -> None:
    for key in schema.get("required", []):
        if key not in value:
            raise AssertionError(f"{path} missing required key {key!r}")
    properties = schema.get("properties", {})
    for key, child in properties.items():
        if key in value:
            _validate_schema_subset(child, value[key], schemas, f"{path}.{key}", root_schema)
    additional = schema.get("additionalProperties", True)
    extra = set(value) - set(properties)
    if additional is False and extra:
        raise AssertionError(f"{path} unexpected keys {sorted(extra)}")
    if isinstance(additional, dict):
        for key in extra:
            _validate_schema_subset(additional, value[key], schemas, f"{path}.{key}", root_schema)


def _validate_schema_subset(
    schema: dict[str, Any],
    value: object,
    schemas: dict[str, dict[str, Any]],
    path: str = "$",
    root_schema: dict[str, Any] | None = None,
) -> None:
    if root_schema is None:
        root_schema = schema
    unsupported = set(schema) - SUPPORTED_SCHEMA_KEYS
    if unsupported:
        raise AssertionError(f"Unsupported schema keys at {path}: {sorted(unsupported)}")

    if _validate_schema_ref(schema, value, schemas, path, root_schema):
        return

    _validate_schema_combinators(schema, value, schemas, path, root_schema)
    _validate_scalar_constraints(schema, value, path)

    if isinstance(value, list):
        _validate_array_constraints(schema, value, schemas, path, root_schema)

    if isinstance(value, dict):
        _validate_object_constraints(schema, value, schemas, path, root_schema)
