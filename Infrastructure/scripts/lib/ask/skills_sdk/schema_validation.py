from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


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
    "anyOf",
    "default",
    "additionalProperties",
    "allOf",
    "const",
    "definitions",
    "enum",
    "exclusiveMinimum",
    "if",
    "items",
    "minItems",
    "minLength",
    "minimum",
    "maximum",
    "maxItems",
    "oneOf",
    "pattern",
    "prefixItems",
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
        _validate_schema_reference(ref, value, root_schema, schemas, path)
        return
    _validate_schema_combinators(schema, value, schemas, path, root_schema)
    _validate_schema_scalars(schema, value, path)
    if isinstance(value, list):
        _validate_schema_array(schema, value, schemas, path, root_schema)
    elif isinstance(value, dict):
        _validate_schema_object(schema, value, schemas, path, root_schema)


def _validate_schema_reference(
    ref: str, value: object, root_schema: dict[str, object],
    schemas: dict[str, dict[str, object]], path: str,
) -> None:
    resolved_root = schemas.get(ref, root_schema)
    if "#" in ref and not ref.startswith("#/"):
        resolved_root = schemas[ref.split("#", 1)[0]]
    _validate_schema_subset(_resolve_schema_ref(ref, root_schema, schemas), value, schemas, path, resolved_root)


def _validate_schema_combinators(
    schema: dict[str, object], value: object, schemas: dict[str, dict[str, object]],
    path: str, root_schema: dict[str, object],
) -> None:
    for subschema in _list_of_dicts(schema.get("allOf")):
        _validate_schema_subset(subschema, value, schemas, path, root_schema)
    _validate_if_then(schema, value, schemas, path, root_schema)
    _validate_schema_choice(schema.get("oneOf"), value, schemas, path, root_schema, exact=True)
    _validate_schema_choice(schema.get("anyOf"), value, schemas, path, root_schema, exact=False)


def _validate_if_then(
    schema: dict[str, object], value: object, schemas: dict[str, dict[str, object]],
    path: str, root_schema: dict[str, object],
) -> None:
    condition = schema.get("if")
    if not isinstance(condition, dict):
        return
    try:
        _validate_schema_subset(condition, value, schemas, path, root_schema)
    except AssertionError:
        return
    consequence = schema.get("then")
    if isinstance(consequence, dict):
        _validate_schema_subset(consequence, value, schemas, path, root_schema)


def _validate_schema_choice(
    choices: object, value: object, schemas: dict[str, dict[str, object]],
    path: str, root_schema: dict[str, object], *, exact: bool,
) -> None:
    options = _list_of_dicts(choices)
    if not options:
        return
    matches = sum(_schema_option_matches(option, value, schemas, path, root_schema) for option in options)
    if (exact and matches != 1) or (not exact and matches == 0):
        qualifier = "exactly one" if exact else "at least one"
        raise AssertionError(f"{path} expected {qualifier} choice match, got {matches}")


def _schema_option_matches(
    schema: dict[str, object], value: object, schemas: dict[str, dict[str, object]],
    path: str, root_schema: dict[str, object],
) -> bool:
    try:
        _validate_schema_subset(schema, value, schemas, path, root_schema)
    except AssertionError:
        return False
    return True


def _validate_schema_scalars(schema: dict[str, object], value: object, path: str) -> None:
    expected_types = _schema_types(schema.get("type"))
    if expected_types and not any(_schema_type_matches(value, expected) for expected in expected_types):
        raise AssertionError(f"{path} expected {expected_types}, got {type(value).__name__}")
    if "const" in schema and value != schema["const"]:
        raise AssertionError(f"{path} expected const {schema['const']!r}, got {value!r}")
    enum = schema.get("enum")
    if isinstance(enum, list) and value not in enum:
        raise AssertionError(f"{path} expected one of {enum!r}, got {value!r}")
    _validate_string_limits(schema, value, path)
    _validate_number_limits(schema, value, path)


def _schema_types(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def _validate_string_limits(schema: dict[str, object], value: object, path: str) -> None:
    if not isinstance(value, str):
        return
    minimum = schema.get("minLength")
    if isinstance(minimum, int) and len(value) < minimum:
        raise AssertionError(f"{path} shorter than minLength {minimum}")
    pattern = schema.get("pattern")
    if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
        raise AssertionError(f"{path} does not match pattern {pattern!r}")


def _validate_number_limits(schema: dict[str, object], value: object, path: str) -> None:
    minimum = schema.get("minimum")
    if isinstance(value, int) and not isinstance(value, bool) and isinstance(minimum, int) and value < minimum:
        raise AssertionError(f"{path} smaller than minimum {minimum}")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return
    exclusive = schema.get("exclusiveMinimum")
    if isinstance(exclusive, (int, float)) and value <= exclusive:
        raise AssertionError(f"{path} not greater than exclusiveMinimum {exclusive}")
    maximum = schema.get("maximum")
    if isinstance(maximum, (int, float)) and value > maximum:
        raise AssertionError(f"{path} greater than maximum {maximum}")


def _validate_schema_array(
    schema: dict[str, object], value: list[object], schemas: dict[str, dict[str, object]],
    path: str, root_schema: dict[str, object],
) -> None:
    _validate_array_limits(schema, value, path)
    prefix_items = schema.get("prefixItems")
    if isinstance(prefix_items, list):
        for index, item_schema in enumerate(prefix_items):
            if index >= len(value):
                break
            if isinstance(item_schema, dict):
                _validate_schema_subset(item_schema, value[index], schemas, f"{path}[{index}]", root_schema)
    item_schema = schema.get("items")
    if isinstance(item_schema, dict):
        for index, item in enumerate(value):
            _validate_schema_subset(item_schema, item, schemas, f"{path}[{index}]", root_schema)


def _validate_array_limits(schema: dict[str, object], value: list[object], path: str) -> None:
    minimum = schema.get("minItems")
    if isinstance(minimum, int) and len(value) < minimum:
        raise AssertionError(f"{path} shorter than minItems {minimum}")
    maximum = schema.get("maxItems")
    if isinstance(maximum, int) and len(value) > maximum:
        raise AssertionError(f"{path} longer than maxItems {maximum}")


def _validate_schema_object(
    schema: dict[str, object], value: dict[str, object], schemas: dict[str, dict[str, object]],
    path: str, root_schema: dict[str, object],
) -> None:
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
