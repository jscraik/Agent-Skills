#!/usr/bin/env python3
"""Verify runtime-separation reader compatibility across schema versions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema-current", required=True)
    parser.add_argument("--schema-prev", required=True)
    parser.add_argument(
        "--readers",
        default="GOVERNANCE/runtime-separation/readers.yaml",
        help="Reader inventory path",
    )
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return payload


def _manifest_signature(payload: dict[str, Any]) -> dict[str, Any]:
    slices = payload.get("slices") if isinstance(payload.get("slices"), list) else []
    return {
        "schema_version": payload.get("schema_version"),
        "reader_min_version": payload.get("reader_min_version"),
        "policy_export_version": payload.get("policy_export_version"),
        "slice_count": len(slices),
        "required_slice_keys": sorted(list(slices[0].keys())) if slices and isinstance(slices[0], dict) else [],
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    current_path = Path(args.schema_current)
    if not current_path.is_absolute():
        current_path = (repo_root / current_path).resolve()
    prev_path = Path(args.schema_prev)
    if not prev_path.is_absolute():
        prev_path = (repo_root / prev_path).resolve()
    readers_path = Path(args.readers)
    if not readers_path.is_absolute():
        readers_path = (repo_root / readers_path).resolve()

    if not current_path.exists():
        raise SystemExit(f"current schema file missing: {current_path}")
    if not prev_path.exists():
        raise SystemExit(f"previous schema fixture missing: {prev_path}")
    if not readers_path.exists():
        raise SystemExit(f"readers inventory missing: {readers_path}")

    current_manifest = _load_yaml(current_path)
    prev_manifest = _load_yaml(prev_path)
    readers = _load_yaml(readers_path)

    if "rows" not in readers or not isinstance(readers["rows"], list):
        raise SystemExit(f"readers inventory missing rows list: {readers_path}")

    current_schema = current_manifest.get("schema_version")
    prev_schema = prev_manifest.get("schema_version")
    if not isinstance(current_schema, int):
        raise SystemExit("current manifest schema_version must be an integer")
    if not isinstance(prev_schema, int):
        raise SystemExit("previous manifest schema_version must be an integer")
    if prev_schema > current_schema:
        raise SystemExit(
            f"previous schema fixture must be <= current schema ({prev_schema} > {current_schema})"
        )

    signatures = {
        "current": _manifest_signature(current_manifest),
        "previous": _manifest_signature(prev_manifest),
        "readers_row_count": len(readers["rows"]),
    }

    print(json.dumps(signatures, indent=2, sort_keys=True))
    print("runtime-separation reader compatibility check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
