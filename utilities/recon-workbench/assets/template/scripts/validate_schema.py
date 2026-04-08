#!/usr/bin/env python3
import argparse
import json
import sys


def _load_jsonschema():
    try:
        import jsonschema  # type: ignore
    except ModuleNotFoundError:
        sys.stderr.write("ERROR: jsonschema is required. Install with: uv pip install jsonschema\n")
        return None
    return jsonschema


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate JSON against a JSON Schema.")
    parser.add_argument("--schema", required=True, help="Path to schema JSON")
    parser.add_argument("--data", required=True, help="Path to JSON data")
    args = parser.parse_args()
    jsonschema = _load_jsonschema()
    if jsonschema is None:
        return 2

    with open(args.schema, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        sys.stderr.write(f"ValidationError: {e.message}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
