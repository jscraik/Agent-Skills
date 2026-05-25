#!/usr/bin/env python3
"""Validate JSC-364 runtime proof evidence artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_FILES = {
    "runtime_card": "runtime-card.v1.schema.json",
    "evidence_receipt": "evidence-receipt.v1.schema.json",
    "artifact_record": "artifact-record.v1.schema.json",
    "runtime_session_summary": "runtime-session-summary.v1.schema.json",
    "recovery_plan_summary": "recovery-plan-summary.v1.schema.json",
}
WORKSPACE_ROOT_MARKERS = {"${WORKSPACE_ROOT}"}


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str
    field: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "kind": self.kind,
            "field": self.field,
            "message": self.message,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate runtime proof evidence JSON files.")
    parser.add_argument("paths", nargs="*", type=Path, help="Runtime evidence JSON files or directories.")
    parser.add_argument("--evidence-dir", type=Path, help="Directory containing runtime evidence JSON files.")
    parser.add_argument(
        "--require-shared-workspace",
        action="store_true",
        help="Require closeout-eligible RuntimeCard and ArtifactRecord visibility to be user_observable.",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.cwd(),
        help="Expected shared workspace root when --require-shared-workspace is set. Defaults to the current directory.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable validation output.")
    return parser.parse_args()


def _schema_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "schemas"


def _load_schema(schema_name: str) -> dict[str, Any]:
    try:
        payload = json.loads((_schema_dir() / schema_name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _schema_definition_enum(schema_name: str, definition_name: str) -> set[str]:
    schema = _load_schema(schema_name)
    values = schema.get("definitions", {}).get(definition_name, {}).get("enum", [])
    return set(values) if isinstance(values, list) else set()


def _schema_property_enum(schema_name: str, property_name: str) -> set[str]:
    schema = _load_schema(schema_name)
    values = schema.get("properties", {}).get(property_name, {}).get("enum", [])
    return set(values) if isinstance(values, list) else set()


def _schema_required(schema_name: str) -> list[str]:
    schema = _load_schema(schema_name)
    values = schema.get("required", [])
    return list(values) if isinstance(values, list) else []


def _schema_definition_required(schema_name: str, definition_name: str) -> list[str]:
    schema = _load_schema(schema_name)
    values = schema.get("definitions", {}).get(definition_name, {}).get("required", [])
    return list(values) if isinstance(values, list) else []


def _marker_values(marker: object) -> set[object]:
    if isinstance(marker, (list, tuple, set, frozenset)):
        return set(marker)
    return {marker}


def _schema_conditional_required(schema_name: str, field_name: str, marker: object) -> list[str]:
    schema = _load_schema(schema_name)
    for rule in schema.get("allOf", []):
        if not isinstance(rule, dict):
            continue
        properties = rule.get("if", {}).get("properties", {})
        if field_name not in properties:
            continue
        condition = properties[field_name]
        if not isinstance(condition, dict):
            continue
        matches = condition.get("const") == marker if "const" in condition else set(condition.get("enum", [])) == _marker_values(marker)
        if matches:
            values = rule.get("then", {}).get("required", [])
            return list(values) if isinstance(values, list) else []
    return []


def _runtime_targets() -> set[str]:
    return _schema_definition_enum(SCHEMA_FILES["runtime_card"], "runtimeTarget")


def _runtime_statuses() -> set[str]:
    return _schema_definition_enum(SCHEMA_FILES["runtime_card"], "runtimeStatus")


def _claim_statuses() -> set[str]:
    return _schema_definition_enum(SCHEMA_FILES["evidence_receipt"], "claimStatus")


def _evidence_types() -> set[str]:
    return _schema_property_enum(SCHEMA_FILES["evidence_receipt"], "evidence_type")


def _actor_types() -> set[str]:
    return _schema_definition_enum(SCHEMA_FILES["runtime_card"], "actorType")


def _mutation_scopes() -> set[str]:
    return _schema_definition_enum(SCHEMA_FILES["runtime_card"], "mutationScope")


def _visibility_statuses() -> set[str]:
    return _schema_definition_enum(SCHEMA_FILES["runtime_card"], "visibilityStatus")


def _artifact_types() -> set[str]:
    return _schema_property_enum(SCHEMA_FILES["artifact_record"], "artifact_type")


def _collect_paths(paths: list[Path], evidence_dir: Path | None) -> list[tuple[Path, bool]]:
    candidates: list[tuple[Path, bool]] = []
    if evidence_dir is not None:
        candidates.append((evidence_dir, True))
    candidates.extend((path, path.is_dir()) for path in paths)

    json_paths: list[tuple[Path, bool]] = []
    for candidate, from_directory in candidates:
        if candidate.is_dir():
            json_paths.extend((path, True) for path in sorted(candidate.rglob("*.json")) if path.is_file())
        else:
            json_paths.append((candidate, from_directory))
    return json_paths


def _load_json(path: Path) -> tuple[object | None, list[Finding]]:
    if not path.exists():
        return None, [Finding(str(path), "unknown", "$", "file does not exist")]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [Finding(str(path), "unknown", "$", f"invalid JSON: {exc}")]


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_object(value: object, path: Path, kind: str) -> list[Finding]:
    if isinstance(value, dict):
        return []
    return [Finding(str(path), kind, "$", "payload must be an object")]


def _require_fields(payload: dict[str, Any], required: list[str], path: Path, kind: str) -> list[Finding]:
    findings: list[Finding] = []
    for field in required:
        if field not in payload:
            findings.append(Finding(str(path), kind, field, "missing required field"))
    return findings


def _require_non_empty_string(
    payload: dict[str, Any],
    fields: list[str],
    path: Path,
    kind: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for field in fields:
        if field in payload and not _is_non_empty_string(payload[field]):
            findings.append(Finding(str(path), kind, field, "must be a non-empty string"))
    return findings


def _require_enum(
    payload: dict[str, Any],
    field: str,
    allowed: set[str],
    path: Path,
    kind: str,
) -> list[Finding]:
    if field not in payload:
        return []
    value = payload[field]
    if value not in allowed:
        return [Finding(str(path), kind, field, f"must be one of {sorted(allowed)}")]
    return []


def _require_list(payload: dict[str, Any], fields: list[str], path: Path, kind: str) -> list[Finding]:
    findings: list[Finding] = []
    for field in fields:
        if field in payload and not isinstance(payload[field], list):
            findings.append(Finding(str(path), kind, field, "must be an array"))
    return findings


def _require_object_fields(payload: dict[str, Any], fields: list[str], path: Path, kind: str) -> list[Finding]:
    findings: list[Finding] = []
    for field in fields:
        if field in payload and not isinstance(payload[field], dict):
            findings.append(Finding(str(path), kind, field, "must be an object"))
    return findings


def _expected_workspace_finding(
    payload: dict[str, Any],
    path: Path,
    kind: str,
    *,
    expected_workspace_root: str,
) -> list[Finding]:
    workspace_root = payload.get("workspace_root")
    if workspace_root in WORKSPACE_ROOT_MARKERS:
        return []
    if workspace_root != expected_workspace_root:
        return [
            Finding(
                str(path),
                kind,
                "workspace_root",
                f"must match expected workspace root {expected_workspace_root}",
            )
        ]
    return []


def _infer_kind(payload: dict[str, Any]) -> str:
    if "card_id" in payload and "runtime_session" in payload:
        return "runtime_card"
    if "receipt_id" in payload and "claim" in payload:
        return "evidence_receipt"
    if "artifact_id" in payload and "artifact_type" in payload:
        return "artifact_record"
    if "session_id" in payload and "runtime_target" in payload:
        return "runtime_session_summary"
    if "recovery_status" in payload and "next_commands" in payload:
        return "recovery_plan_summary"
    return "unknown"


def _validate_recovery_plan(payload: dict[str, Any], path: Path) -> list[Finding]:
    kind = "recovery_plan_summary"
    findings = _require_fields(payload, _schema_required(SCHEMA_FILES[kind]), path, kind)
    findings.extend(_require_enum(payload, "recovery_status", _runtime_statuses(), path, kind))
    findings.extend(_require_non_empty_string(payload, ["reason", "expected_outcome"], path, kind))
    findings.extend(_require_list(payload, ["next_commands", "preconditions"], path, kind))
    findings.extend(_require_object_fields(payload, ["permission_profile"], path, kind))
    for index, command in enumerate(payload.get("next_commands", [])):
        if not isinstance(command, dict):
            findings.append(Finding(str(path), kind, f"next_commands[{index}]", "must be an object"))
            continue
        findings.extend(
            _require_fields(
                command,
                _schema_definition_required(SCHEMA_FILES[kind], "commandDescriptor"),
                path,
                kind,
            )
        )
        findings.extend(
            _require_non_empty_string(command, ["command", "expected_outcome"], path, kind)
        )
        findings.extend(_require_list(command, ["preconditions"], path, kind))
        findings.extend(_require_object_fields(command, ["permission_profile"], path, kind))
    return findings


def _validate_runtime_session(
    payload: dict[str, Any],
    path: Path,
    *,
    require_shared_workspace: bool = False,
    expected_workspace_root: str = "",
) -> list[Finding]:
    kind = "runtime_session_summary"
    findings = _require_fields(payload, _schema_required(SCHEMA_FILES[kind]), path, kind)
    findings.extend(_require_non_empty_string(payload, ["session_id", "created_at", "workspace_root"], path, kind))
    findings.extend(_require_enum(payload, "runtime_target", _runtime_targets(), path, kind))
    findings.extend(_require_enum(payload, "runtime_status", _runtime_statuses(), path, kind))
    findings.extend(_require_enum(payload, "actor_type", _actor_types(), path, kind))
    findings.extend(_require_enum(payload, "visibility_status", _visibility_statuses(), path, kind))
    if require_shared_workspace:
        findings.extend(_expected_workspace_finding(payload, path, kind, expected_workspace_root=expected_workspace_root))
    return findings


def _validate_artifact_record(
    payload: dict[str, Any],
    path: Path,
    *,
    require_shared_workspace: bool,
    expected_workspace_root: str,
) -> list[Finding]:
    kind = "artifact_record"
    findings = _require_fields(payload, _schema_required(SCHEMA_FILES[kind]), path, kind)
    findings.extend(
        _require_non_empty_string(
            payload,
            ["artifact_id", "path", "workspace_root", "generated_by", "consumer_contract"],
            path,
            kind,
        )
    )
    findings.extend(_require_enum(payload, "artifact_type", _artifact_types(), path, kind))
    findings.extend(_require_enum(payload, "actor_type", _actor_types(), path, kind))
    findings.extend(_require_enum(payload, "mutation_scope", _mutation_scopes(), path, kind))
    findings.extend(_require_enum(payload, "visibility_status", _visibility_statuses(), path, kind))
    findings.extend(_require_enum(payload, "validation_status", _claim_statuses(), path, kind))
    findings.extend(_require_object_fields(payload, ["source_identity"], path, kind))
    source_identity = payload.get("source_identity")
    if isinstance(source_identity, dict):
        source_paths = source_identity.get("source_paths")
        if not isinstance(source_paths, list) or not all(_is_non_empty_string(item) for item in source_paths):
            findings.append(Finding(str(path), kind, "source_identity.source_paths", "must be a non-empty string array"))
    if require_shared_workspace and payload.get("visibility_status") != "user_observable":
        findings.append(Finding(str(path), kind, "visibility_status", "must be user_observable for shared workspace evidence"))
    if require_shared_workspace:
        findings.extend(_expected_workspace_finding(payload, path, kind, expected_workspace_root=expected_workspace_root))
    return findings


def _validate_evidence_receipt(payload: dict[str, Any], path: Path) -> list[Finding]:
    kind = "evidence_receipt"
    findings = _require_fields(payload, _schema_required(SCHEMA_FILES[kind]), path, kind)
    findings.extend(_require_non_empty_string(payload, ["receipt_id", "claim", "verifier", "observed_at"], path, kind))
    findings.extend(_require_enum(payload, "claim_status", _claim_statuses(), path, kind))
    findings.extend(_require_enum(payload, "runtime_target", _runtime_targets(), path, kind))
    findings.extend(_require_enum(payload, "runtime_status", _runtime_statuses(), path, kind))
    findings.extend(_require_enum(payload, "evidence_type", _evidence_types(), path, kind))
    findings.extend(_require_list(payload, ["source_paths"], path, kind))
    source_paths = payload.get("source_paths")
    if isinstance(source_paths, list) and not all(_is_non_empty_string(item) for item in source_paths):
        findings.append(Finding(str(path), kind, "source_paths", "must contain only non-empty strings"))
    if payload.get("evidence_type") == "command":
        findings.extend(
            _require_fields(
                payload,
                _schema_conditional_required(SCHEMA_FILES[kind], "evidence_type", "command"),
                path,
                kind,
            )
        )
        findings.extend(_require_non_empty_string(payload, ["command"], path, kind))
        if "exit_code" in payload and not _is_integer(payload["exit_code"]):
            findings.append(Finding(str(path), kind, "exit_code", "must be an integer"))
    if payload.get("runtime_status") == "blocked_runtime":
        findings.extend(
            _require_fields(
                payload,
                _schema_conditional_required(SCHEMA_FILES[kind], "runtime_status", "blocked_runtime"),
                path,
                kind,
            )
        )
        findings.extend(_require_non_empty_string(payload, ["probe_command", "probe_artifact_path", "blocker_class"], path, kind))
        if "probe_exit_code" in payload and not _is_integer(payload["probe_exit_code"]):
            findings.append(Finding(str(path), kind, "probe_exit_code", "must be an integer"))
    if payload.get("claim_status") in {"blocked", "partial"}:
        findings.extend(
            _require_fields(
                payload,
                _schema_conditional_required(SCHEMA_FILES[kind], "claim_status", ("blocked", "partial")),
                path,
                kind,
            )
        )
        findings.extend(_require_non_empty_string(payload, ["blocker"], path, kind))
    return findings


def _validate_runtime_card(
    payload: dict[str, Any],
    path: Path,
    *,
    require_shared_workspace: bool,
    expected_workspace_root: str,
) -> list[Finding]:
    kind = "runtime_card"
    findings = _require_fields(payload, _schema_required(SCHEMA_FILES[kind]), path, kind)
    if "schema_version" in payload and payload["schema_version"] != 1:
        findings.append(Finding(str(path), kind, "schema_version", "must be integer 1"))
    findings.extend(_require_non_empty_string(payload, ["card_id", "created_at", "skill_handle", "workspace_root"], path, kind))
    findings.extend(_require_enum(payload, "runtime_target", _runtime_targets(), path, kind))
    findings.extend(_require_enum(payload, "runtime_status", _runtime_statuses(), path, kind))
    findings.extend(_require_enum(payload, "actor_type", _actor_types(), path, kind))
    findings.extend(_require_enum(payload, "mutation_scope", _mutation_scopes(), path, kind))
    findings.extend(_require_enum(payload, "visibility_status", _visibility_statuses(), path, kind))
    findings.extend(_require_list(payload, ["thread_runs", "turn_events", "artifacts", "evidence_receipts", "verifier_results", "limitations"], path, kind))
    findings.extend(_require_object_fields(payload, ["runtime_session", "permission_profile", "recovery_plan"], path, kind))
    if require_shared_workspace and payload.get("visibility_status") != "user_observable":
        findings.append(Finding(str(path), kind, "visibility_status", "must be user_observable for shared workspace evidence"))
    if require_shared_workspace:
        findings.extend(_expected_workspace_finding(payload, path, kind, expected_workspace_root=expected_workspace_root))

    runtime_session = payload.get("runtime_session")
    if isinstance(runtime_session, dict):
        findings.extend(
            _validate_runtime_session(
                runtime_session,
                path,
                require_shared_workspace=require_shared_workspace,
                expected_workspace_root=expected_workspace_root,
            )
        )
    recovery_plan = payload.get("recovery_plan")
    if isinstance(recovery_plan, dict):
        findings.extend(_validate_recovery_plan(recovery_plan, path))
    for index, artifact in enumerate(payload.get("artifacts", [])):
        if isinstance(artifact, dict):
            findings.extend(
                _validate_artifact_record(
                    artifact,
                    path,
                    require_shared_workspace=require_shared_workspace,
                    expected_workspace_root=expected_workspace_root,
                )
            )
        else:
            findings.append(Finding(str(path), kind, f"artifacts[{index}]", "must be an object"))
    for index, receipt in enumerate(payload.get("evidence_receipts", [])):
        if isinstance(receipt, dict):
            findings.extend(_validate_evidence_receipt(receipt, path))
        else:
            findings.append(Finding(str(path), kind, f"evidence_receipts[{index}]", "must be an object"))
    return findings


def _validate_payload(
    payload: object,
    path: Path,
    *,
    require_shared_workspace: bool,
    expected_workspace_root: str,
) -> tuple[str, list[Finding]]:
    object_findings = _require_object(payload, path, "unknown")
    if object_findings:
        return "unknown", object_findings
    assert isinstance(payload, dict)
    kind = _infer_kind(payload)
    if kind == "runtime_card":
        return kind, _validate_runtime_card(
            payload,
            path,
            require_shared_workspace=require_shared_workspace,
            expected_workspace_root=expected_workspace_root,
        )
    if kind == "evidence_receipt":
        return kind, _validate_evidence_receipt(payload, path)
    if kind == "artifact_record":
        return kind, _validate_artifact_record(
            payload,
            path,
            require_shared_workspace=require_shared_workspace,
            expected_workspace_root=expected_workspace_root,
        )
    if kind == "runtime_session_summary":
        return kind, _validate_runtime_session(
            payload,
            path,
            require_shared_workspace=require_shared_workspace,
            expected_workspace_root=expected_workspace_root,
        )
    if kind == "recovery_plan_summary":
        return kind, _validate_recovery_plan(payload, path)
    return kind, [Finding(str(path), kind, "$", "could not infer runtime proof artifact kind")]


def _schema_findings() -> list[Finding]:
    findings: list[Finding] = []
    schema_dir = _schema_dir()
    for kind, schema_name in SCHEMA_FILES.items():
        schema_path = schema_dir / schema_name
        if not schema_path.exists():
            findings.append(Finding(str(schema_path), kind, "$", "schema file missing"))
            continue
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(Finding(str(schema_path), kind, "$", f"schema JSON is invalid: {exc}"))
    return findings


def main() -> int:
    args = parse_args()
    paths = _collect_paths(args.paths, args.evidence_dir)
    findings = _schema_findings()
    checked: list[dict[str, str]] = []
    expected_workspace_root = str(args.workspace_root.resolve())

    if not paths:
        findings.append(Finding(".", "unknown", "$", "no evidence paths provided"))

    for path, from_directory in paths:
        payload, load_findings = _load_json(path)
        findings.extend(load_findings)
        if load_findings:
            continue
        if from_directory and isinstance(payload, dict) and _infer_kind(payload) == "unknown":
            continue
        kind, payload_findings = _validate_payload(
            payload,
            path,
            require_shared_workspace=args.require_shared_workspace,
            expected_workspace_root=expected_workspace_root,
        )
        checked.append({"path": str(path), "kind": kind})
        findings.extend(payload_findings)

    if paths and not checked:
        findings.append(Finding(".", "unknown", "$", "no runtime proof artifacts found"))

    status = "fail" if findings else "pass"
    result = {
        "schema_version": "runtime-proof-validation.v1",
        "status": status,
        "checked_count": len(checked),
        "checked": checked,
        "schema_files": {kind: str(_schema_dir() / schema_name) for kind, schema_name in SCHEMA_FILES.items()},
        "require_shared_workspace": args.require_shared_workspace,
        "expected_workspace_root": expected_workspace_root if args.require_shared_workspace else None,
        "findings": [finding.as_dict() for finding in findings],
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"runtime proof validation: {status}")
        for finding in findings:
            print(f"- {finding.path} [{finding.kind}] {finding.field}: {finding.message}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
