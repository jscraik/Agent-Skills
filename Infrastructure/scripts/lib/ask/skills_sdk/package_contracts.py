from __future__ import annotations

from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import (
    CODEX_SKILL_PACKAGE_FIELDS,
    CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS,
    PACKAGE_CONTRACT_FIELDS,
    parse_frontmatter_scalar,
)

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None


SKILL_PACKAGE_SCHEMA_VERSION = "skill-package.v1"
SKILL_PACKAGE_READINESS_SCHEMA_VERSION = "skill-package-readiness.v1"
SKILL_PACKAGE_COMPATIBILITY_SNAPSHOT_ID = "skill-package-readiness.v1.public-output.2026-05-23"
SKILL_PACKAGE_SCHEMA_PATH = "Infrastructure/config/schemas/skill-package.v1.schema.json"
SKILL_PACKAGE_READINESS_SCHEMA_PATH = "Infrastructure/config/schemas/skill-package-readiness.v1.schema.json"
SKILL_PACKAGE_SNAPSHOT_PATH = (
    "Infrastructure/tests/fixtures/skill_package_snapshots/"
    "skill-package-readiness-public-output.v1.json"
)
CODEX_SKILL_PACKAGE_ABI_SOURCE_PATH = "codex-rs/core-skills/src/model.rs"
CODEX_SKILL_PACKAGE_ABI_EVIDENCE_FIELDS: tuple[str, ...] = CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS
CODEX_SKILL_PACKAGE_REQUIRED_FIELDS: tuple[str, ...] = tuple(
    field for field, required in CODEX_SKILL_PACKAGE_FIELDS if required
)
CODEX_SKILL_PACKAGE_OPTIONAL_FIELDS: tuple[str, ...] = tuple(
    field for field, required in CODEX_SKILL_PACKAGE_FIELDS if not required
)


def repo_relative_path(repo_root: Path, path: Path) -> str | None:
    """Return a repo-relative POSIX path when *path* is inside *repo_root*."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def codex_skill_package_abi_source() -> dict[str, Any]:
    """Return repo-neutral provenance for the Codex SkillMetadata ABI shape."""
    return {
        "path": CODEX_SKILL_PACKAGE_ABI_SOURCE_PATH,
        "struct": "SkillMetadata",
        "evidence_fields": list(CODEX_SKILL_PACKAGE_ABI_EVIDENCE_FIELDS),
    }


def metadata_value(frontmatter: dict[str, Any], field: str) -> Any:
    """Return a package field from top-level frontmatter or nested metadata."""
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    if field == "version":
        return frontmatter.get("version") or metadata.get("version")
    return metadata.get(field) or frontmatter.get(field)


def normalized_list(value: Any) -> list[str]:
    """Normalize package metadata values into a stable string list."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, set):
        return sorted(str(item) for item in value if str(item).strip())
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def package_field_values(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Extract package readiness metadata from skill frontmatter."""
    values = {field: metadata_value(frontmatter, field) for field in PACKAGE_CONTRACT_FIELDS}
    return {
        "version": values.get("version"),
        "compatible_roles": normalized_list(values.get("compatible_roles")),
        "runtime_needs": normalized_list(values.get("runtime_needs")),
        "maturity": values.get("maturity"),
        "provenance": values.get("provenance"),
        "share_readiness": values.get("share_readiness"),
    }


def read_agents_openai_yaml_fields(skill_md: Path | None) -> dict[str, Any]:
    """Extract a conservative agents/openai.yaml contract view."""
    if not skill_md:
        return {}
    agents_openai = skill_md.parent / "agents" / "openai.yaml"
    if not agents_openai.is_file():
        return {}
    try:
        text = agents_openai.read_text(encoding="utf-8")
    except OSError:
        return {}
    if yaml is not None:
        try:
            loaded = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            loaded = {}
        if isinstance(loaded, dict):
            return {str(key): value for key, value in loaded.items()}
    fields: dict[str, Any] = {}
    current_map: str | None = None
    current_nested_key: str | None = None
    current_list_item: dict[str, Any] | None = None
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if current_map and stripped.startswith("- "):
            nested = fields.setdefault(current_map, {})
            if not isinstance(nested, dict):
                continue
            item_text = stripped[2:].strip()
            if not current_nested_key:
                continue
            values = nested.setdefault(current_nested_key, [])
            if not isinstance(values, list):
                values = []
                nested[current_nested_key] = values
            if ":" in item_text:
                item_key, item_value = item_text.split(":", 1)
                current_list_item = {
                    item_key.strip(): parse_frontmatter_scalar(item_value.strip())
                }
                values.append(current_list_item)
            else:
                values.append(parse_frontmatter_scalar(item_text))
                current_list_item = None
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent == 0:
            if value:
                fields[key] = parse_frontmatter_scalar(value)
                current_map = None
                current_nested_key = None
                current_list_item = None
            else:
                fields[key] = {}
                current_map = key
                current_nested_key = None
                current_list_item = None
            continue
        if current_map:
            nested = fields.setdefault(current_map, {})
            if not isinstance(nested, dict):
                continue
            if current_list_item is not None and indent >= 4 and value:
                current_list_item[key] = parse_frontmatter_scalar(value)
                continue
            if value:
                nested[key] = parse_frontmatter_scalar(value)
                current_nested_key = None
                current_list_item = None
            else:
                nested[key] = []
                current_nested_key = key
                current_list_item = None
    return fields


def skill_package_contract(
    repo_root: Path,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return the Codex-native package contract for SKILL.md plus agents/openai.yaml."""
    openai_fields = read_agents_openai_yaml_fields(source_path)
    interface = frontmatter.get("interface")
    if not isinstance(interface, dict):
        interface = {}
    openai_interface = openai_fields.get("interface")
    if isinstance(openai_interface, dict):
        interface = {**interface, **openai_interface}

    dependencies = frontmatter.get("dependencies")
    if not isinstance(dependencies, dict):
        dependencies = {}
    openai_dependencies = openai_fields.get("dependencies")
    if isinstance(openai_dependencies, dict):
        dependencies = {**dependencies, **openai_dependencies}
    policy = frontmatter.get("policy")
    if not isinstance(policy, dict):
        policy = {}
    openai_policy = openai_fields.get("policy")
    if isinstance(openai_policy, dict):
        policy = {**policy, **openai_policy}

    codex_metadata = {
        "name": frontmatter.get("name"),
        "description": frontmatter.get("description"),
        "short_description": frontmatter.get("short_description")
        or interface.get("short_description"),
        "interface": interface or None,
        "dependencies": dependencies or None,
        "policy": policy or None,
        "scope": frontmatter.get("scope"),
        "plugin_id": frontmatter.get("plugin_id"),
    }
    required_present = sorted(
        field for field in CODEX_SKILL_PACKAGE_REQUIRED_FIELDS if codex_metadata.get(field)
    )
    required_missing = sorted(
        field for field in CODEX_SKILL_PACKAGE_REQUIRED_FIELDS if not codex_metadata.get(field)
    )
    optional_present = sorted(
        field for field in CODEX_SKILL_PACKAGE_OPTIONAL_FIELDS if codex_metadata.get(field)
    )
    source_rel = repo_relative_path(repo_root, source_path) if source_path else None
    openai_rel = None
    if source_path:
        openai_path = source_path.parent / "agents" / "openai.yaml"
        if openai_path.is_file():
            openai_rel = repo_relative_path(repo_root, openai_path)
    return {
        "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
        "source_files": {
            "skill_md": source_rel,
            "agents_openai_yaml": openai_rel,
        },
        "codex_abi_source": codex_skill_package_abi_source(),
        "metadata": codex_metadata,
        "required_fields": {
            "present": required_present,
            "missing": required_missing,
        },
        "optional_fields": {
            "present": optional_present,
        },
        "compatibility_status": "blocked_validation" if required_missing else "compatible",
    }


def empty_skill_package_contract() -> dict[str, Any]:
    """Return a package contract for unresolved or missing source paths."""
    return {
        "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
        "source_files": {
            "skill_md": None,
            "agents_openai_yaml": None,
        },
        "codex_abi_source": codex_skill_package_abi_source(),
        "metadata": {
            "name": None,
            "description": None,
            "short_description": None,
            "interface": None,
            "dependencies": None,
            "policy": None,
            "scope": None,
            "plugin_id": None,
        },
        "required_fields": {
            "present": [],
            "missing": list(CODEX_SKILL_PACKAGE_REQUIRED_FIELDS),
        },
        "optional_fields": {
            "present": [],
        },
        "compatibility_status": "blocked_missing_source",
    }


def skill_package_compatibility_snapshot() -> dict[str, Any]:
    """Return the public package-output snapshot identity for drift tests."""
    return {
        "id": SKILL_PACKAGE_COMPATIBILITY_SNAPSHOT_ID,
        "schema_version": SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
        "path": SKILL_PACKAGE_SNAPSHOT_PATH,
        "covers": [
            "valid_share_ready_package",
            "missing_source_package",
            "strict_incomplete_package",
        ],
    }


def skill_package_readiness(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Return version and role-aware package readiness for one skill."""
    values = package_field_values(frontmatter)
    present = sorted(field for field, value in values.items() if bool(value))
    missing = sorted(field for field in PACKAGE_CONTRACT_FIELDS if field not in present)
    share_readiness = str(values.get("share_readiness") or "").strip().lower()
    share_readiness_ready = share_readiness == "ready"
    share_ready = False
    missing_identity_fields = [
        field
        for field in ("name", "description")
        if not str(frontmatter.get(field) or "").strip()
    ]

    if missing_identity_fields:
        readiness_level = "incomplete_identity"
    elif not values.get("version"):
        readiness_level = "legacy_capability"
    elif missing:
        readiness_level = "versioned_capability"
    elif not share_readiness_ready:
        readiness_level = "share_readiness_blocked"
    else:
        readiness_level = "share_ready"
        share_ready = True

    blocked_reasons = list(missing)
    if missing_identity_fields:
        blocked_reasons.append("identity_incomplete")
    if not missing and not share_readiness_ready:
        blocked_reasons.append("share_readiness_not_ready")
    recommended_next_fields = [
        field
        for field in ("compatible_roles", "runtime_needs", "provenance", "share_readiness")
        if field in missing
    ]
    if not missing and not share_readiness_ready:
        recommended_next_fields.append("share_readiness")
    if "version" in missing:
        recommended_next_fields.insert(0, "version")
    recommended_next_fields = [*missing_identity_fields, *recommended_next_fields]
    promotion_status = "ready_pending_checkout" if share_ready else "blocked_validation"

    return {
        "readiness_level": readiness_level,
        "required_fields": {
            "present": present,
            "missing": missing,
        },
        "values": values,
        "role_compatibility": {
            "declared": bool(values["compatible_roles"]),
            "roles": values["compatible_roles"],
        },
        "runtime_contract": {
            "declared": bool(values["runtime_needs"]),
            "needs": values["runtime_needs"],
        },
        "install_gate": {
            "install_ready": share_ready,
            "required_checks": list(PACKAGE_CONTRACT_FIELDS),
            "blocked_reasons": blocked_reasons,
            "checkout_test": {
                "required": True,
                "status": "not_run",
                "evidence": [],
            },
        },
        "promotion_gate": {
            "status": promotion_status,
            "promotion_ready": False,
            "share_ready": share_ready,
            "share_readiness": values["share_readiness"],
            "checkout_test_status": "not_run",
            "blocked_reasons": blocked_reasons,
            "recommended_next_fields": recommended_next_fields,
        },
    }


def refresh_package_promotion_gate(package_contract: dict[str, Any]) -> None:
    """Keep promotion readiness tied to metadata and checkout evidence."""
    promotion_gate = package_contract["promotion_gate"]
    checkout_status = package_contract["install_gate"]["checkout_test"]["status"]
    promotion_gate["checkout_test_status"] = checkout_status

    if promotion_gate["status"] == "blocked_missing_source":
        promotion_gate["promotion_ready"] = False
        return
    if promotion_gate["blocked_reasons"]:
        promotion_gate["status"] = "blocked_validation"
        promotion_gate["promotion_ready"] = False
        return
    if not promotion_gate["share_ready"]:
        promotion_gate["status"] = "blocked_validation"
        promotion_gate["promotion_ready"] = False
        return
    if checkout_status == "pass":
        promotion_gate["status"] = "ready"
        promotion_gate["promotion_ready"] = True
        return
    if checkout_status == "not_run":
        promotion_gate["status"] = "ready_pending_checkout"
    else:
        promotion_gate["status"] = checkout_status
    promotion_gate["promotion_ready"] = False


def skill_package_gate_summary(package_contract: dict[str, Any]) -> dict[str, Any]:
    """Return automation-facing package gate status without nested traversal."""
    install_gate = package_contract["install_gate"]
    promotion_gate = package_contract["promotion_gate"]
    return {
        "install_ready": install_gate["install_ready"],
        "checkout_test_status": install_gate["checkout_test"]["status"],
        "promotion_status": promotion_gate["status"],
        "promotion_ready": promotion_gate["promotion_ready"],
        "blocked_reasons": promotion_gate["blocked_reasons"],
    }


def skill_package_readiness_summary(package_contract: dict[str, Any]) -> dict[str, Any]:
    """Return a compact readiness summary for routing and dashboards."""
    required_fields = package_contract["required_fields"]
    present_fields = list(required_fields["present"])
    missing_fields = list(required_fields["missing"])
    return {
        "readiness_level": package_contract["readiness_level"],
        "present_fields": present_fields,
        "missing_fields": missing_fields,
        "present_field_count": len(present_fields),
        "missing_field_count": len(missing_fields),
        "role_compatible": package_contract["role_compatibility"]["declared"],
        "runtime_contract_declared": package_contract["runtime_contract"]["declared"],
        "share_ready": package_contract["promotion_gate"]["share_ready"],
        "promotion_status": package_contract["promotion_gate"]["status"],
        "recommended_next_fields": list(package_contract["promotion_gate"]["recommended_next_fields"]),
    }


def skill_package_contract_summary(package_readiness: dict[str, Any]) -> dict[str, Any]:
    """Return the doctor-facing package contract view from package readiness."""
    package_fields = package_readiness["required_fields"]
    return {
        "present": package_fields["present"],
        "missing": package_fields["missing"],
        "values": package_readiness["values"],
        "role_compatibility": package_readiness["role_compatibility"],
        "runtime_contract": package_readiness["runtime_contract"],
        "install_gate": package_readiness["install_gate"],
        "promotion_gate": package_readiness["promotion_gate"],
    }


def skill_package_checkout_test(
    repo_root: Path,
    source_path: Path | None,
    audit_target: str | None,
    package_contract: dict[str, Any],
) -> dict[str, Any]:
    """Return read-only local checkout evidence for a package candidate."""
    evidence: list[str] = []
    if not source_path or not source_path.is_file():
        return {
            "required": True,
            "status": "blocked_missing_source",
            "evidence": evidence,
        }

    source_rel = repo_relative_path(repo_root, source_path) or source_path.as_posix()
    evidence.append(f"source_path:{source_rel}")
    try:
        source_path.read_text(encoding="utf-8")
    except OSError as exc:
        evidence.append("source_readable:false")
        evidence.append(f"source_read_error:{exc.__class__.__name__}")
        return {
            "required": True,
            "status": "blocked_missing_source",
            "evidence": evidence,
        }
    evidence.append("source_readable:true")
    if audit_target:
        evidence.append(f"audit_target:{audit_target}")

    missing_fields = package_contract["required_fields"]["missing"]
    blocked_reasons = package_contract["install_gate"]["blocked_reasons"]
    if blocked_reasons:
        if missing_fields:
            evidence.append(f"missing_package_metadata:{','.join(missing_fields)}")
        else:
            evidence.append(f"promotion_gate_blocked:{','.join(blocked_reasons)}")
        return {
            "required": True,
            "status": "blocked_validation",
            "evidence": evidence,
        }

    evidence.append("package_metadata_complete:true")
    return {
        "required": True,
        "status": "pass",
        "evidence": evidence,
    }


def capability_metadata_status(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Return a non-blocking metadata readiness summary for one skill source."""
    required_fields = ("name", "description")
    capability_fields = (
        "skill-type",
        "lifecycle_state",
        "maturity",
        "owner",
        "metadata_source",
    )
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    present_required = sorted(field for field in required_fields if frontmatter.get(field))
    missing_required = sorted(field for field in required_fields if not frontmatter.get(field))
    present_capability = sorted(field for field in capability_fields if metadata.get(field))
    missing_capability = sorted(field for field in capability_fields if not metadata.get(field))

    package_readiness = skill_package_readiness(frontmatter)
    package_fields = package_readiness["required_fields"]
    missing_package = package_fields["missing"]

    readiness_level = "package_ready" if not missing_package else "capability_declared"
    if missing_capability:
        readiness_level = "legacy_frontmatter"
    if missing_required:
        readiness_level = "incomplete"

    return {
        "status": "pass" if not missing_required else "warning",
        "readiness_level": readiness_level,
        "required_fields": {
            "present": present_required,
            "missing": missing_required,
        },
        "capability_contract": {
            "present": present_capability,
            "missing": missing_capability,
            "values": {field: metadata.get(field) for field in present_capability},
        },
        "package_contract": skill_package_contract_summary(package_readiness),
        "package_readiness": package_readiness,
        "note": "Package/share metadata gaps are reported as contract gaps, not current blockers.",
    }
