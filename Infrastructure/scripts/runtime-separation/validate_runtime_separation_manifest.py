#!/usr/bin/env python3
"""Validate runtime-separation slice manifest invariants."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

ALLOWED_ACTIVATION_STATES = {
    "declared",
    "pre_activation",
    "migrated",
    "rollback_pending",
    "rolled_back",
    "cleanup_complete",
}
ALLOWED_DISCOVERY_COMPATIBILITY = {"catalog_only", "dual_read"}
ALLOWED_PATH_COMPATIBILITY = {"resolver_only", "filesystem_forwarder", "combined"}
ALLOWED_FORWARDER_TYPES = {
    "resolver_alias",
    "directory_projection",
    "package_root_projection",
    "wrapper_index",
}
ALLOWED_OWNER_LANES = {"skills", "plugins"}
REQUIRED_SLICE_KEYS = {
    "id",
    "phase",
    "owner_lane",
    "activation_state",
    "discovery_compatibility",
    "path_compatibility",
    "discovery_precedence",
    "forwarder_type",
    "overlap_class",
    "authoritative_write_root",
    "inventory_selector",
    "path_consumer_inventory_ref",
    "path_consumer_inventory_digest",
    "reader_inventory_ref",
    "reader_inventory_digest",
    "policy_export_version",
    "canonical_paths",
    "legacy_paths",
    "planned_deltas",
    "representative_commands",
    "plugin_lifecycle_checks",
    "entry_checks",
    "exit_checks",
    "rollback_commands",
}
HEX64_LENGTH = 64


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="GOVERNANCE/runtime-separation/slices.yaml",
        help="Slice manifest path",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable stricter digest/reference checks",
    )
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"manifest root must be a mapping: {path}")
    return payload


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(value: Any, field: str, index: int) -> list[str]:
    if not isinstance(value, list) or not value:
        raise SystemExit(f"slice #{index} key {field} must be a non-empty list")
    cleaned: list[str] = []
    for item in value:
        if not _is_non_empty_str(item):
            raise SystemExit(f"slice #{index} key {field} must contain only non-empty strings")
        cleaned.append(str(item).strip())
    return cleaned


def _validate_path_compatibility(value: Any) -> list[str]:
    if isinstance(value, str):
        if value not in ALLOWED_PATH_COMPATIBILITY:
            raise SystemExit(
                f"path_compatibility {value!r} must be one of {sorted(ALLOWED_PATH_COMPATIBILITY)}"
            )
        return [value]
    if isinstance(value, list) and value:
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str) or item not in ALLOWED_PATH_COMPATIBILITY:
                raise SystemExit(
                    "path_compatibility list items must be one of "
                    f"{sorted(ALLOWED_PATH_COMPATIBILITY)}"
                )
            if item not in normalized:
                normalized.append(item)
        return normalized
    raise SystemExit("path_compatibility must be a string or non-empty list")


def _validate_hex_digest(value: Any, field: str, index: int) -> str:
    if not isinstance(value, str):
        raise SystemExit(f"slice #{index} key {field} must be a hex digest string")
    digest = value.strip().lower()
    if len(digest) != HEX64_LENGTH or any(ch not in "0123456789abcdef" for ch in digest):
        raise SystemExit(f"slice #{index} key {field} must be a 64-char lowercase hex digest")
    return digest


def _resolve_repo_path(repo_root: Path, candidate: Any, field: str, index: int) -> Path:
    if not _is_non_empty_str(candidate):
        raise SystemExit(f"slice #{index} key {field} must be a non-empty path string")
    value = str(candidate).strip()
    path = Path(value)
    resolved = path if path.is_absolute() else (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise SystemExit(f"slice #{index} key {field} must resolve under repo root: {value}") from exc
    return resolved


def _validate_representative_commands(value: Any, index: int) -> None:
    if not isinstance(value, list) or not value:
        raise SystemExit(f"slice #{index} key representative_commands must be a non-empty list")
    required = {
        "command",
        "comparison_mode",
        "args_legacy",
        "args_canonical",
        "expected_exit_code",
        "normalized_assertions",
        "expected_result_ref",
    }
    for command_index, entry in enumerate(value, start=1):
        if not isinstance(entry, dict):
            raise SystemExit(
                f"slice #{index} representative_commands[{command_index}] must be a mapping"
            )
        missing = sorted(required - set(entry))
        if missing:
            raise SystemExit(
                f"slice #{index} representative_commands[{command_index}] missing keys: "
                + ", ".join(missing)
            )
        if not _is_non_empty_str(entry.get("command")):
            raise SystemExit(
                f"slice #{index} representative_commands[{command_index}].command must be non-empty"
            )


def _validate_plugin_lifecycle_checks(value: Any, index: int) -> None:
    if not isinstance(value, list) or not value:
        raise SystemExit(f"slice #{index} key plugin_lifecycle_checks must be a non-empty list")
    for check_index, entry in enumerate(value, start=1):
        if not isinstance(entry, dict):
            raise SystemExit(
                f"slice #{index} plugin_lifecycle_checks[{check_index}] must be a mapping"
            )
        for key in ("id", "command"):
            if not _is_non_empty_str(entry.get(key)):
                raise SystemExit(
                    f"slice #{index} plugin_lifecycle_checks[{check_index}].{key} must be non-empty"
                )


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    repo_root = Path(__file__).resolve().parents[3]

    if not manifest_path.exists():
        raise SystemExit(f"runtime-separation manifest missing: {manifest_path}")

    payload = _load_yaml(manifest_path)
    for key in ("schema_version", "reader_min_version", "policy_export_version", "slices"):
        if key not in payload:
            raise SystemExit(f"manifest missing required top-level key: {key}")

    schema_version = payload.get("schema_version")
    reader_min_version = payload.get("reader_min_version")
    policy_export_version = payload.get("policy_export_version")
    slices = payload.get("slices")

    if not isinstance(schema_version, int) or schema_version < 1:
        raise SystemExit("manifest key schema_version must be an integer >= 1")
    if not isinstance(reader_min_version, int) or reader_min_version < 1:
        raise SystemExit("manifest key reader_min_version must be an integer >= 1")
    if not _is_non_empty_str(policy_export_version):
        raise SystemExit("manifest key policy_export_version must be a non-empty string")
    if not isinstance(slices, list):
        raise SystemExit("manifest key slices must be a list")
    if args.strict and not slices:
        raise SystemExit("strict mode requires at least one declared slice")

    slice_ids: set[str] = set()
    for index, slice_entry in enumerate(slices, start=1):
        if not isinstance(slice_entry, dict):
            raise SystemExit(f"slice #{index} is not a mapping")

        missing = sorted(REQUIRED_SLICE_KEYS - set(slice_entry))
        if missing:
            raise SystemExit(f"slice #{index} missing required keys: {', '.join(missing)}")

        slice_id = slice_entry.get("id")
        if not _is_non_empty_str(slice_id):
            raise SystemExit(f"slice #{index} key id must be a non-empty string")
        normalized_id = str(slice_id).strip()
        if normalized_id in slice_ids:
            raise SystemExit(f"duplicate slice id: {normalized_id}")
        slice_ids.add(normalized_id)

        owner_lane = slice_entry.get("owner_lane")
        if owner_lane not in ALLOWED_OWNER_LANES:
            raise SystemExit(
                f"slice #{index} owner_lane {owner_lane!r} must be one of {sorted(ALLOWED_OWNER_LANES)}"
            )

        activation_state = slice_entry.get("activation_state")
        if activation_state not in ALLOWED_ACTIVATION_STATES:
            raise SystemExit(
                f"slice #{index} activation_state {activation_state!r} must be one of "
                f"{sorted(ALLOWED_ACTIVATION_STATES)}"
            )

        discovery_compatibility = slice_entry.get("discovery_compatibility")
        if discovery_compatibility not in ALLOWED_DISCOVERY_COMPATIBILITY:
            raise SystemExit(
                f"slice #{index} discovery_compatibility {discovery_compatibility!r} must be one of "
                f"{sorted(ALLOWED_DISCOVERY_COMPATIBILITY)}"
            )

        _validate_path_compatibility(slice_entry.get("path_compatibility"))

        forwarder_type = slice_entry.get("forwarder_type")
        if forwarder_type not in ALLOWED_FORWARDER_TYPES:
            raise SystemExit(
                f"slice #{index} forwarder_type {forwarder_type!r} must be one of "
                f"{sorted(ALLOWED_FORWARDER_TYPES)}"
            )

        if not _is_non_empty_str(slice_entry.get("phase")):
            raise SystemExit(f"slice #{index} key phase must be a non-empty string")
        if not _is_non_empty_str(slice_entry.get("overlap_class")):
            raise SystemExit(f"slice #{index} key overlap_class must be a non-empty string")
        if not _is_non_empty_str(slice_entry.get("authoritative_write_root")):
            raise SystemExit(
                f"slice #{index} key authoritative_write_root must be a non-empty string"
            )

        discovery_precedence = _validate_string_list(
            slice_entry.get("discovery_precedence"), "discovery_precedence", index
        )
        canonical_paths = _validate_string_list(slice_entry.get("canonical_paths"), "canonical_paths", index)
        legacy_paths = _validate_string_list(slice_entry.get("legacy_paths"), "legacy_paths", index)
        _ = legacy_paths
        if len(set(discovery_precedence)) != len(discovery_precedence):
            raise SystemExit(f"slice #{index} discovery_precedence contains duplicate entries")

        inventory_selector = slice_entry.get("inventory_selector")
        if not isinstance(inventory_selector, dict):
            raise SystemExit(f"slice #{index} key inventory_selector must be a mapping")

        if slice_entry.get("policy_export_version") != policy_export_version:
            raise SystemExit(
                f"slice #{index} policy_export_version must match top-level policy_export_version"
            )

        for command_field in ("entry_checks", "exit_checks", "rollback_commands"):
            _validate_string_list(slice_entry.get(command_field), command_field, index)

        planned_deltas = slice_entry.get("planned_deltas")
        if not isinstance(planned_deltas, list):
            raise SystemExit(f"slice #{index} key planned_deltas must be a list")

        _validate_representative_commands(slice_entry.get("representative_commands"), index)
        _validate_plugin_lifecycle_checks(slice_entry.get("plugin_lifecycle_checks"), index)

        reader_ref = _resolve_repo_path(repo_root, slice_entry.get("reader_inventory_ref"), "reader_inventory_ref", index)
        path_ref = _resolve_repo_path(
            repo_root,
            slice_entry.get("path_consumer_inventory_ref"),
            "path_consumer_inventory_ref",
            index,
        )
        reader_digest = _validate_hex_digest(
            slice_entry.get("reader_inventory_digest"),
            "reader_inventory_digest",
            index,
        )
        path_digest = _validate_hex_digest(
            slice_entry.get("path_consumer_inventory_digest"),
            "path_consumer_inventory_digest",
            index,
        )

        if args.strict:
            for field_name, ref_path in (
                ("reader_inventory_ref", reader_ref),
                ("path_consumer_inventory_ref", path_ref),
            ):
                if not ref_path.exists():
                    raise SystemExit(
                        f"slice #{index} key {field_name} points to missing file: {ref_path}"
                    )
                if ref_path.suffix not in {".yaml", ".yml"}:
                    raise SystemExit(
                        f"slice #{index} key {field_name} must reference a YAML inventory file"
                    )

            actual_reader_digest = _file_digest(reader_ref)
            actual_path_digest = _file_digest(path_ref)
            if actual_reader_digest != reader_digest:
                raise SystemExit(
                    f"slice #{index} reader_inventory_digest mismatch "
                    f"(expected={reader_digest}, actual={actual_reader_digest})"
                )
            if actual_path_digest != path_digest:
                raise SystemExit(
                    f"slice #{index} path_consumer_inventory_digest mismatch "
                    f"(expected={path_digest}, actual={actual_path_digest})"
                )

        if canonical_paths[0] != str(canonical_paths[0]).strip():
            raise SystemExit(f"slice #{index} canonical_paths contains leading/trailing whitespace")

    print(
        "runtime-separation manifest validation passed "
        f"(schema_version={schema_version}, slices={len(slices)}, strict={args.strict})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
