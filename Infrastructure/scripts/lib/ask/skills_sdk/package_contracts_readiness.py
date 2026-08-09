from .package_contracts_core import *  # noqa: F403
from .package_contracts_rubric import *  # noqa: F403
from .package_contracts_support import *  # noqa: F403
from .package_contracts_optimization import *  # noqa: F403
from .package_contracts_writing_core import *  # noqa: F403
from .package_contracts_writing_checks import *  # noqa: F403
from .package_contracts_platform import *  # noqa: F403

def sdk_contract_field_present(field: str, value: Any) -> bool:
    """Return whether an SDK package contract field has real declared evidence."""
    if field == "evals" and isinstance(value, dict):
        return bool(value.get("declared"))
    if field in {"agent_metadata", "reference_contract", "task_profile"} and isinstance(value, dict):
        return bool(value.get("declared"))
    if field == "portability_profile" and isinstance(value, dict):
        return any(bool(item) for item in value.values())
    return bool(value)


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


def _required_sdk_contract_blockers(sdk_contract: dict[str, Any]) -> dict[str, list[str]]:
    values = sdk_contract.get("values")
    if not isinstance(values, dict):
        return {}
    blockers_by_field: dict[str, list[str]] = {}
    for field, contract in values.items():
        if not isinstance(contract, dict):
            continue
        if contract.get("required_for_package_readiness") is not True:
            continue
        if contract.get("status") != "blocked_validation":
            continue
        raw_blockers = contract.get("blockers")
        blocker_items = raw_blockers if isinstance(raw_blockers, list) else []
        blockers = [
            f"{field}:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in blocker_items
            if isinstance(blocker, dict)
        ] or [f"{field}:blocked_validation"]
        blockers_by_field[str(field)] = blockers
    return blockers_by_field


def skill_package_readiness(
    frontmatter: dict[str, Any],
    repo_root: Path | None = None,
    source_path: Path | None = None,
) -> dict[str, Any]:
    """Return version and role-aware package readiness for one skill."""
    values = package_field_values(frontmatter)
    sdk_contract = sdk_package_contract(repo_root, source_path, frontmatter)
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
    sdk_missing = [
        f"sdk_contract:{field}"
        for field in sdk_contract["required_fields"]["missing"]
    ]
    blocked_reasons.extend(sdk_missing)
    workflow_contract = sdk_contract["values"].get("workflow_contract")
    workflow_blockers: list[str] = []
    if isinstance(workflow_contract, dict) and workflow_contract.get("status") == "blocked_validation":
        workflow_blockers = [
            f"workflow_contract:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in workflow_contract.get("blockers", [])
            if isinstance(blocker, dict)
        ] or ["workflow_contract:blocked_validation"]
        blocked_reasons.extend(workflow_blockers)
    optimization_readiness = sdk_contract["values"].get("optimization_contract")
    optimization_blockers: list[str] = []
    if (
        isinstance(optimization_readiness, dict)
        and optimization_readiness.get("status") == "blocked_validation"
    ):
        optimization_blockers = [
            f"optimization_contract:{blocker.get('rule_id', 'blocked_validation')}"
            for blocker in optimization_readiness.get("blockers", [])
            if isinstance(blocker, dict)
        ] or ["optimization_contract:blocked_validation"]
        blocked_reasons.extend(optimization_blockers)
    required_contract_blockers = _required_sdk_contract_blockers(sdk_contract)
    reference_blockers = required_contract_blockers.pop("reference_quality", [])
    writing_quality_blockers = required_contract_blockers.pop("writing_quality", [])
    authoring_contract_blockers = required_contract_blockers.pop("authoring_contract", [])
    openai_platform_blockers = required_contract_blockers.pop("openai_platform_compat", [])
    other_required_contract_blockers = [
        blocker
        for blockers in required_contract_blockers.values()
        for blocker in blockers
    ]
    blocked_reasons.extend(reference_blockers)
    blocked_reasons.extend(writing_quality_blockers)
    blocked_reasons.extend(authoring_contract_blockers)
    blocked_reasons.extend(openai_platform_blockers)
    blocked_reasons.extend(other_required_contract_blockers)
    if sdk_missing and not missing_identity_fields and not missing:
        readiness_level = "sdk_contract_incomplete"
        share_ready = False
    if workflow_blockers and not missing_identity_fields and not missing and not sdk_missing:
        readiness_level = "workflow_contract_incomplete"
        share_ready = False
    if (
        optimization_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
    ):
        readiness_level = "optimization_contract_incomplete"
        share_ready = False
    if (
        reference_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
    ):
        readiness_level = "reference_quality_incomplete"
        share_ready = False
    if (
        writing_quality_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
    ):
        readiness_level = "writing_quality_incomplete"
        share_ready = False
    if (
        authoring_contract_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
    ):
        readiness_level = "authoring_contract_incomplete"
        share_ready = False
    if (
        openai_platform_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not authoring_contract_blockers
    ):
        readiness_level = "openai_platform_compat_incomplete"
        share_ready = False
    if (
        other_required_contract_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not authoring_contract_blockers
        and not openai_platform_blockers
    ):
        readiness_level = "sdk_required_contract_incomplete"
        share_ready = False
    knowledge_capsules = sdk_contract.get("knowledge_capsules")
    knowledge_blockers: list[str] = []
    if (
        isinstance(knowledge_capsules, dict)
        and knowledge_capsules.get("manifest_declared") is True
        and knowledge_capsules.get("ready") is not True
    ):
        knowledge_blockers = ["knowledge_capsules:first_party_routing_incomplete"]
        blocked_reasons.extend(knowledge_blockers)
    if (
        knowledge_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not authoring_contract_blockers
        and not openai_platform_blockers
        and not other_required_contract_blockers
    ):
        readiness_level = "knowledge_capsules_incomplete"
        share_ready = False
    progressive = sdk_contract.get("progressive_disclosure")
    progressive_blockers: list[str] = []
    if isinstance(progressive, dict):
        source_operating_model = progressive.get("source_operating_model")
        if (
            isinstance(source_operating_model, dict)
            and source_operating_model.get("status") == "blocked_validation"
        ):
            progressive_blockers = [
                "progressive_disclosure:source_operating_model_preservation"
            ]
            blocked_reasons.extend(progressive_blockers)
    if (
        progressive_blockers
        and not missing_identity_fields
        and not missing
        and not sdk_missing
        and not workflow_blockers
        and not optimization_blockers
        and not reference_blockers
        and not writing_quality_blockers
        and not authoring_contract_blockers
        and not openai_platform_blockers
        and not other_required_contract_blockers
        and not knowledge_blockers
    ):
        readiness_level = "progressive_disclosure_incomplete"
        share_ready = False
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
        "sdk_contract": sdk_contract,
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
    sdk_contract = package_contract.get("sdk_contract") or {}
    sdk_required_fields = sdk_contract.get("required_fields") or {}
    sdk_missing_fields = list(sdk_required_fields.get("missing") or [])
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
        "sdk_contract_missing_fields": sdk_missing_fields,
        "telemetry_confidence": (
            sdk_contract.get("evidence_providers", {}).get("telemetry_confidence")
            if isinstance(sdk_contract.get("evidence_providers"), dict)
            else None
        ),
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
        "sdk_contract": package_readiness.get("sdk_contract"),
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
__all__ = [name for name in globals() if not name.startswith("__")]
