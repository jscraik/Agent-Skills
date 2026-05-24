from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any


CODEX_SKILL_PACKAGE_FIELDS: tuple[tuple[str, bool], ...] = (
    ("name", True),
    ("description", True),
    ("short_description", False),
    ("interface", False),
    ("dependencies", False),
    ("policy", False),
    ("scope", False),
    ("plugin_id", False),
)
CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS: tuple[str, ...] = tuple(
    field for field, _required in CODEX_SKILL_PACKAGE_FIELDS
)

PACKAGE_CONTRACT_FIELDS: tuple[str, ...] = (
    "version",
    "compatible_roles",
    "runtime_needs",
    "maturity",
    "provenance",
    "share_readiness",
)

DOCTOR_BLOCKER_TAXONOMY: dict[str, str] = {
    "blocked_resolution": "The requested handle or path cannot be resolved to a repo-owned capability.",
    "blocked_runtime": "The capability source exists, but the generated runtime handle is not reachable.",
    "blocked_missing_source": "The resolved capability no longer has a canonical SKILL.md source file.",
    "blocked_validation": "A structural or policy validation gate failed for the canonical capability source.",
    "blocked_user_input": "The run requested user input and should not be classified as a hang.",
    "blocked_auth": "A required credential, token, account, or OAuth grant is unavailable.",
    "timeout_no_output": "A bounded run exceeded its timeout without producing usable output.",
    "timeout_partial_output": "A bounded run exceeded its timeout after producing incomplete output.",
    "blocked_missing_tool": "A required local command, runtime, package, or validator is unavailable.",
    "blocked_missing_artifact": "An expected report, transcript, workout, or generated artifact is absent.",
    "blocked_environment": "The selected workspace, sandbox, cwd, or permission profile cannot run the check.",
}

DOCTOR_WARNING_TAXONOMY: dict[str, str] = {
    "metadata_incomplete": "Recommended capability metadata is absent or only partially declared.",
    "capability_contract_incomplete": "The richer capability contract is not fully declared yet.",
    "outcome_proof_missing": "No matching workout or proof artifact was found for outcome-level evidence.",
    "strict_audit_not_run": "The doctor used compatibility audit mode; strict audit remains available.",
}

DOCTOR_SDK_LAYERS: tuple[str, ...] = (
    "Contracts",
    "Catalog",
    "Authoring",
    "Validation",
    "Packaging",
    "Runtime Adapters",
    "Evidence",
    "Memory",
)

DOCTOR_CHECK_SDK_LAYERS: dict[str, str] = {
    "resolver": "Catalog",
    "runtime_reachability": "Runtime Adapters",
    "canonical_source": "Authoring",
    "structural_audit": "Validation",
    "capability_metadata": "Catalog",
    "package_readiness": "Packaging",
    "outcome_proof": "Evidence",
}

DOCTOR_BLOCKER_SDK_LAYERS: dict[str, str] = {
    "blocked_resolution": "Catalog",
    "blocked_runtime": "Runtime Adapters",
    "blocked_missing_source": "Authoring",
    "blocked_validation": "Validation",
    "blocked_user_input": "Runtime Adapters",
    "blocked_auth": "Runtime Adapters",
    "timeout_no_output": "Runtime Adapters",
    "timeout_partial_output": "Runtime Adapters",
    "blocked_missing_tool": "Validation",
    "blocked_missing_artifact": "Evidence",
    "blocked_environment": "Runtime Adapters",
}

DOCTOR_WARNING_SDK_LAYERS: dict[str, str] = {
    "metadata_incomplete": "Catalog",
    "capability_contract_incomplete": "Packaging",
    "outcome_proof_missing": "Evidence",
    "strict_audit_not_run": "Validation",
}

DOCTOR_CONTRACT_SCHEMA_VERSIONS: dict[str, str] = {
    "doctor": "skill-doctor.v1",
    "events": "skill-events.v1",
    "lifecycle_event": "capability-lifecycle-event.v1",
    "profiles": "skill-operation-profiles.v1",
    "package": "skill-package-readiness.v1",
    "memory": "skill-memory-provider.v1",
}

EVAL_BLOCKER_CLASSES: list[str] = [
    "blocked_user_input",
    "blocked_auth",
    "blocked_runtime",
    "timeout_no_output",
    "timeout_partial_output",
    "blocked_missing_tool",
    "blocked_missing_artifact",
    "blocked_environment",
    "blocked_validation",
]


def ask_validation_command(*args: str) -> str:
    parts = ["./bin/ask"]
    parts.extend(args)
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def skills_validation_command(action: str, *args: str) -> str:
    return ask_validation_command("skills", action, *args)


def parse_frontmatter_scalar(value: str) -> Any:
    """Parse a conservative subset of YAML frontmatter scalar values."""
    cleaned = value.strip().strip("\"'")
    if cleaned.startswith("[") and cleaned.endswith("]"):
        return [
            item.strip().strip("\"'")
            for item in cleaned[1:-1].split(",")
            if item.strip()
        ]
    if cleaned.lower() in {"true", "false"}:
        return cleaned.lower() == "true"
    return cleaned


def read_skill_frontmatter_fields(skill_md: Path) -> dict[str, Any]:
    """Extract conservative scalar and one-level metadata fields from SKILL.md frontmatter."""
    fields: dict[str, Any] = {}
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return fields
    current_map: str | None = None
    current_list_key: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip(" "))
        if stripped.startswith("- "):
            item = parse_frontmatter_scalar(stripped[2:])
            if current_map == "metadata" and current_list_key:
                nested = fields.setdefault(current_map, {})
                if isinstance(nested, dict):
                    values = nested.setdefault(current_list_key, [])
                    if isinstance(values, list):
                        values.append(item)
                continue
            if current_map and current_map != "metadata":
                values = fields.setdefault(current_map, [])
                if isinstance(values, list):
                    values.append(item)
                continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent > 0 and current_map:
            nested = fields.setdefault(current_map, {})
            if isinstance(nested, dict):
                if value:
                    nested[key] = parse_frontmatter_scalar(value)
                    current_list_key = None
                else:
                    nested[key] = []
                    current_list_key = key
            continue
        current_map = None
        current_list_key = None
        if not value:
            fields[key] = [] if key in PACKAGE_CONTRACT_FIELDS else {}
            current_map = key
            continue
        parsed_value = parse_frontmatter_scalar(value)
        if key in {
            *CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS,
            "metadata",
            *PACKAGE_CONTRACT_FIELDS,
        } and parsed_value:
            fields[key] = parsed_value
    return fields


def status_from_bool(value: bool) -> str:
    return "pass" if value else "fail"


def runtime_failure_payload(
    *,
    command: str,
    error_code: str,
    failed_check_id: str,
    path: str,
    message: str,
    recovery_guidance: str,
    validation_commands: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "skill-runtime-failure.v1",
        "command": command,
        "error_code": error_code,
        "failed_check_id": failed_check_id,
        "path": path,
        "message": message,
        "recovery_guidance": recovery_guidance,
        "validation_commands": validation_commands,
    }


def doctor_sdk_layer_for(kind: str, name: str) -> str:
    """Return the public Skills SDK layer for a doctor contract object."""
    layer_maps = {
        "check": DOCTOR_CHECK_SDK_LAYERS,
        "blocker": DOCTOR_BLOCKER_SDK_LAYERS,
        "warning": DOCTOR_WARNING_SDK_LAYERS,
    }
    return layer_maps.get(kind, {}).get(name, "Contracts")


def doctor_contract_schema_refs() -> dict[str, dict[str, str]]:
    """Return consumer-usable schema references for doctor payload surfaces."""
    missing_schema_reason = (
        "Governed inline contract; concrete schema file is deferred until "
        "external consumers require it."
    )
    refs = {
        schema_name: {
            "name": schema_name,
            "version": version,
            "owner": "Agent Skills Kit",
            "stability": "experimental",
            "missing_schema_reason": missing_schema_reason,
        }
        for schema_name, version in DOCTOR_CONTRACT_SCHEMA_VERSIONS.items()
    }
    refs["doctor"].pop("missing_schema_reason", None)
    refs["doctor"]["path"] = "Infrastructure/config/schemas/skill-doctor.v1.schema.json"
    return refs


def doctor_contract_schema_versions() -> dict[str, str]:
    """Return legacy scalar schema versions for existing doctor consumers."""
    return dict(DOCTOR_CONTRACT_SCHEMA_VERSIONS)


def doctor_blocker(blocker_class: str, message: str) -> dict[str, str]:
    return {
        "class": blocker_class,
        "sdk_layer": doctor_sdk_layer_for("blocker", blocker_class),
        "message": message,
        "definition": DOCTOR_BLOCKER_TAXONOMY.get(blocker_class, "Unclassified doctor blocker."),
    }


def doctor_warning(warning_class: str, message: str) -> dict[str, str]:
    return {
        "class": warning_class,
        "sdk_layer": doctor_sdk_layer_for("warning", warning_class),
        "message": message,
        "definition": DOCTOR_WARNING_TAXONOMY.get(warning_class, "Unclassified doctor warning."),
    }


def skill_target_summary(
    *,
    query: str,
    target_kind: Any,
    handle: Any,
    source_path: Any,
    audit_target: Any,
) -> dict[str, Any]:
    """Return compact target identity for readiness payload consumers."""
    return {
        "query": query,
        "target_kind": target_kind,
        "handle": handle,
        "canonical_source_path": source_path,
        "audit_target": audit_target,
    }


def skill_doctor_check_summary(checks: dict[str, Any]) -> dict[str, Any]:
    """Return compact doctor check counts for automation consumers."""
    status_counts: dict[str, int] = {}
    failed_checks: list[str] = []
    warning_checks: list[str] = []
    for name, check in checks.items():
        status = str(check.get("status", "unknown")) if isinstance(check, dict) else "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        if status == "fail":
            failed_checks.append(name)
        elif status == "warning":
            warning_checks.append(name)
    return {
        "check_names": list(checks),
        "check_count": len(checks),
        "status_counts": status_counts,
        "failed_checks": failed_checks,
        "warning_checks": warning_checks,
    }
