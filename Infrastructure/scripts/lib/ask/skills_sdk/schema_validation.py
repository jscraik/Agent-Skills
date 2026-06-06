from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SchemaDiagnostic:
    schema_path: str
    payload_source: str
    json_path: str
    message: str
    status: str
    truth_lane: str


@dataclass(frozen=True)
class SchemaValidationResult:
    status: str
    diagnostics: tuple[SchemaDiagnostic, ...]


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


def validate_payload_against_schema(
    payload: object,
    schema: dict[str, object],
    schemas: dict[str, dict[str, object]],
    *,
    schema_path: Path | str,
    payload_source: str,
    truth_lane: str,
) -> SchemaValidationResult:
    try:
        _validate_schema_subset(schema, payload, schemas)
    except AssertionError as exc:
        return SchemaValidationResult(
            status="fail",
            diagnostics=(
                SchemaDiagnostic(
                    schema_path=str(schema_path),
                    payload_source=payload_source,
                    json_path=_diagnostic_path(str(exc)),
                    message=str(exc),
                    status="fail",
                    truth_lane=truth_lane,
                ),
            ),
        )
    return SchemaValidationResult(status="pass", diagnostics=())


def _diagnostic_path(message: str) -> str:
    if message.startswith("$"):
        return message.split(" ", 1)[0]
    return "$"


def _resolve_schema_ref(
    ref: str,
    schema: dict[str, object],
    schemas: dict[str, dict[str, object]],
) -> dict[str, object]:
    if ref in schemas:
        return schemas[ref]
    if "#" in ref and not ref.startswith("#/"):
        schema_name, fragment = ref.split("#", 1)
        return _resolve_schema_ref("#" + fragment, schemas[schema_name], schemas)
    node: object = schema
    for part in ref.removeprefix("#/").split("/"):
        if not part:
            continue
        if not isinstance(node, dict):
            raise AssertionError(f"Schema ref {ref!r} crossed a non-object node")
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
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise AssertionError(f"Unsupported schema type in SDK validator: {expected}")


def _validate_schema_subset(
    schema: dict[str, object],
    value: object,
    schemas: dict[str, dict[str, object]],
    path: str = "$",
    root_schema: dict[str, object] | None = None,
) -> None:
    if root_schema is None:
        root_schema = schema
    unsupported = set(schema) - SUPPORTED_SCHEMA_KEYS
    if unsupported:
        raise AssertionError(f"{path} has unsupported schema keys: {sorted(unsupported)}")

    ref = schema.get("$ref")
    if isinstance(ref, str):
        resolved_root = root_schema
        if ref in schemas:
            resolved_root = schemas[ref]
        elif "#" in ref and not ref.startswith("#/"):
            schema_name, _fragment = ref.split("#", 1)
            resolved_root = schemas[schema_name]
        _validate_schema_subset(
            _resolve_schema_ref(ref, root_schema, schemas),
            value,
            schemas,
            path,
            resolved_root,
        )
        return

    for subschema in _list_of_dicts(schema.get("allOf")):
        _validate_schema_subset(subschema, value, schemas, path, root_schema)

    if isinstance(schema.get("if"), dict):
        try:
            _validate_schema_subset(_dict_value(schema, "if"), value, schemas, path, root_schema)
        except AssertionError:
            pass
        else:
            if isinstance(schema.get("then"), dict):
                _validate_schema_subset(_dict_value(schema, "then"), value, schemas, path, root_schema)

    one_of = _list_of_dicts(schema.get("oneOf"))
    if one_of:
        matches = 0
        for option in one_of:
            try:
                _validate_schema_subset(option, value, schemas, path, root_schema)
            except AssertionError:
                continue
            matches += 1
        if matches != 1:
            raise AssertionError(f"{path} expected exactly one oneOf match, got {matches}")

    schema_type = schema.get("type")
    if isinstance(schema_type, str):
        expected_types = [schema_type]
    elif isinstance(schema_type, list) and all(isinstance(item, str) for item in schema_type):
        expected_types = schema_type
    else:
        expected_types = []
    if expected_types and not any(_schema_type_matches(value, expected) for expected in expected_types):
        raise AssertionError(f"{path} expected {expected_types}, got {type(value).__name__}")

    if "const" in schema and value != schema["const"]:
        raise AssertionError(f"{path} expected const {schema['const']!r}, got {value!r}")

    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        raise AssertionError(f"{path} expected one of {enum!r}, got {value!r}")

    min_length = schema.get("minLength")
    if isinstance(value, str) and isinstance(min_length, int) and len(value) < min_length:
        raise AssertionError(f"{path} shorter than minLength {min_length}")

    minimum = schema.get("minimum")
    if isinstance(value, int) and isinstance(minimum, int) and value < minimum:
        raise AssertionError(f"{path} smaller than minimum {minimum}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            raise AssertionError(f"{path} shorter than minItems {min_items}")
        items = schema.get("items")
        if isinstance(items, dict):
            item_schema = _dict_value(schema, "items")
            for index, item in enumerate(value):
                _validate_schema_subset(item_schema, item, schemas, f"{path}[{index}]", root_schema)

    if isinstance(value, dict):
        properties = _dict_of_dicts(schema.get("properties"))
        required = schema.get("required")
        if isinstance(required, list):
            for key in required:
                if isinstance(key, str) and key not in value:
                    raise AssertionError(f"{path}.{key} missing required property")
        additional = schema.get("additionalProperties")
        if additional is False:
            extra = set(value) - set(properties)
            if extra:
                raise AssertionError(f"{path} has additional properties: {sorted(extra)}")
        for key, subschema in properties.items():
            if key in value:
                _validate_schema_subset(subschema, value[key], schemas, f"{path}.{key}", root_schema)


def _dict_value(mapping: dict[str, object], key: str) -> dict[str, object]:
    value = mapping[key]
    if not isinstance(value, dict):
        raise AssertionError(f"Expected {key} to contain an object schema")
    return value


def _list_of_dicts(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            raise AssertionError("Expected schema list to contain object schemas")
        result.append(item)
    return result


def _dict_of_dicts(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, dict[str, object]] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise AssertionError("Expected schema property names to be strings")
        if not isinstance(item, dict):
            raise AssertionError(f"Expected schema property {key!r} to contain an object schema")
        result[key] = item
    return result
