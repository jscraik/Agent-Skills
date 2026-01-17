#!/usr/bin/env python3
import argparse
import json
import sys

try:
    import jsonschema
except Exception:
    sys.stderr.write("ERROR: jsonschema is required. Install with: python3 -m pip install jsonschema\n")
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate JSON against a JSON Schema.")
    parser.add_argument("--schema", required=True, help="Path to schema JSON")
    parser.add_argument("--data", required=True, help="Path to JSON data")
    args = parser.parse_args()

    with open(args.schema, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    jsonschema.validate(instance=data, schema=schema)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except jsonschema.ValidationError as e:
        sys.stderr.write(f"ValidationError: {e.message}\n")
        raise SystemExit(1)
