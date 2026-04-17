#!/usr/bin/env python3
"""Refresh runtime-separation consumer inventory digests and validate inventory shape."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml


INVENTORIES = {
    "readers": (
        Path("GOVERNANCE/runtime-separation/readers.yaml"),
        Path("GOVERNANCE/runtime-separation/readers.sha256"),
    ),
    "path-consumers": (
        Path("GOVERNANCE/runtime-separation/path-consumers.yaml"),
        Path("GOVERNANCE/runtime-separation/path-consumers.sha256"),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-readers", action="store_true")
    parser.add_argument("--emit-path-consumers", action="store_true")
    parser.add_argument("--emit-digests", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"inventory root must be a mapping: {path}")
    return payload


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_inventory(name: str, payload: dict[str, Any]) -> int:
    if "rows" not in payload:
        raise SystemExit(f"{name}: missing rows")
    if not isinstance(payload["rows"], list):
        raise SystemExit(f"{name}: rows must be a list")
    row_count = payload.get("row_count")
    if not isinstance(row_count, int):
        raise SystemExit(f"{name}: row_count must be an integer")
    actual = len(payload["rows"])
    if row_count != actual:
        raise SystemExit(f"{name}: row_count mismatch (declared={row_count}, actual={actual})")
    return actual


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]

    targets: list[str] = []
    if args.emit_readers:
        targets.append("readers")
    if args.emit_path_consumers:
        targets.append("path-consumers")
    if not targets:
        targets = ["readers", "path-consumers"]

    summary: dict[str, dict[str, Any]] = {}
    for name in targets:
        inventory_rel, digest_rel = INVENTORIES[name]
        inventory_path = repo_root / inventory_rel
        digest_path = repo_root / digest_rel
        if not inventory_path.exists():
            raise SystemExit(f"{name}: missing inventory file {inventory_path}")

        payload = _load_yaml(inventory_path)
        row_count = _validate_inventory(name, payload)

        digest = _digest(inventory_path)
        if args.emit_digests:
            digest_path.write_text(digest + "\n", encoding="utf-8")
        elif args.strict:
            expected = digest_path.read_text(encoding="utf-8").strip() if digest_path.exists() else ""
            if expected != digest:
                raise SystemExit(
                    f"{name}: digest mismatch (expected={expected or 'missing'}, actual={digest})"
                )

        summary[name] = {
            "rows": row_count,
            "digest": digest,
            "inventory": str(inventory_rel),
            "digest_file": str(digest_rel),
        }

    for name in targets:
        info = summary[name]
        print(
            f"{name}: rows={info['rows']} digest={info['digest']} "
            f"inventory={info['inventory']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
