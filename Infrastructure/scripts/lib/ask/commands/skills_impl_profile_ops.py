from __future__ import annotations

from .skills_impl_memory_profiles import *  # noqa: F403

def _skill_profile_event_coverage(
    profiles: dict[str, dict[str, Any]],
    event_consumers: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return lifecycle event coverage grouped by operation profile."""
    events_by_profile = {profile_name: [] for profile_name in profiles}
    for event_name, consumer in event_consumers.items():
        for profile_name in consumer.get("profiles", []):
            if profile_name in events_by_profile:
                events_by_profile[profile_name].append(event_name)
    profiles_missing_events = sorted(
        profile_name
        for profile_name, event_names in events_by_profile.items()
        if not event_names
    )
    profiles_with_events = sorted(
        profile_name
        for profile_name, event_names in events_by_profile.items()
        if event_names
    )
    event_coverage_gaps = profiles_missing_events
    return {
        "profile_count": len(profiles),
        "profile_names": sorted(profiles),
        "events_by_profile": {
            profile_name: sorted(event_names)
            for profile_name, event_names in events_by_profile.items()
        },
        "event_count_by_profile": {
            profile_name: len(event_names)
            for profile_name, event_names in events_by_profile.items()
        },
        "event_reference_count": sum(len(event_names) for event_names in events_by_profile.values()),
        "profiles_with_events": profiles_with_events,
        "profiles_with_event_count": len(profiles_with_events),
        "profiles_missing_events": profiles_missing_events,
        "profiles_missing_event_count": len(profiles_missing_events),
        "has_profiles_missing_events": bool(profiles_missing_events),
        "all_profiles_have_events": bool(profiles) and not profiles_missing_events,
        "profiles_with_event_gaps": event_coverage_gaps,
        "profiles_with_event_gap_count": len(event_coverage_gaps),
        **_contract_readiness(bool(profiles), event_coverage_gaps),
    }


def _skill_profiles_operation_context() -> dict[str, Any]:
    """Return command surfaces that consume operation profiles."""
    return {
        "profile_model": "profile-v2-inspired",
        "contract_schemas": {
            "profiles": "skill-operation-profiles.v1",
            "events": "skill-events.v1",
            "lifecycle_event": "capability-lifecycle-event.v1",
            "doctor": "skill-doctor.v1",
            "package": "skill-package-readiness.v1",
            "memory": "skill-memory-provider.v1",
        },
        "consumer_commands": {
            "doctor": "./bin/ask skills doctor <handle-or-path> --json --robot",
            "package": "./bin/ask skills package <handle-or-path> --json --robot",
            "events": _skills_validation_command("events"),
            "memory": "./bin/ask skills memory search <query> --json --robot",
        },
        "routing_contracts": {
            "doctor": ["authoring", "package-review", "eval"],
            "package": ["package-review", "plugin-share"],
            "memory": ["authoring", "package-review", "eval"],
            "events": ["authoring", "package-review", "plugin-share", "eval", "live-mutation"],
        },
        "validation_commands": [
            _skills_validation_command("list"),
            _skills_validation_command("events"),
        ],
    }


def _skill_profile_summary(profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return compact profile coverage counts for automation consumers."""
    by_write_policy: dict[str, int] = {}
    by_permission: dict[str, int] = {}
    root_count = 0
    stop_condition_count = 0
    required_evidence_count = 0
    profiles_missing_write_policy: list[str] = []
    profiles_missing_allowed_roots: list[str] = []
    profiles_missing_permissions: list[str] = []
    profiles_missing_stop_conditions: list[str] = []
    profiles_missing_required_evidence: list[str] = []
    taxonomy_stop_conditions_by_profile: dict[str, list[str]] = {}
    profiles_without_taxonomy_stop_conditions: list[str] = []
    required_evidence_by_profile: dict[str, list[str]] = {}
    permissions_by_profile: dict[str, list[str]] = {}
    allowed_roots_by_profile: dict[str, list[str]] = {}
    write_policy_by_profile: dict[str, str] = {}
    stop_conditions_by_profile: dict[str, list[str]] = {}
    for profile_name, profile in profiles.items():
        write_policy_value = profile.get("write_policy")
        write_policy = str(write_policy_value or "unknown")
        if not write_policy_value:
            profiles_missing_write_policy.append(profile_name)
        write_policy_by_profile[profile_name] = write_policy
        by_write_policy[write_policy] = by_write_policy.get(write_policy, 0) + 1
        roots = profile.get("allowed_roots", [])
        profile_root_count = len(roots) if isinstance(roots, list) else 0
        root_count += profile_root_count
        if profile_root_count == 0:
            profiles_missing_allowed_roots.append(profile_name)
        if isinstance(roots, list):
            allowed_roots_by_profile[profile_name] = sorted(str(root) for root in roots)
        stop_conditions = profile.get("stop_conditions", [])
        profile_stop_condition_count = len(stop_conditions) if isinstance(stop_conditions, list) else 0
        stop_condition_count += profile_stop_condition_count
        if profile_stop_condition_count == 0:
            profiles_missing_stop_conditions.append(profile_name)
        if isinstance(stop_conditions, list):
            stop_conditions_by_profile[profile_name] = sorted(str(condition) for condition in stop_conditions)
        taxonomy_stop_conditions = sorted(
            str(condition)
            for condition in (stop_conditions if isinstance(stop_conditions, list) else [])
            if isinstance(condition, str) and condition in DOCTOR_BLOCKER_TAXONOMY
        )
        if taxonomy_stop_conditions:
            taxonomy_stop_conditions_by_profile[profile_name] = taxonomy_stop_conditions
        else:
            profiles_without_taxonomy_stop_conditions.append(profile_name)
        required_evidence = profile.get("required_evidence", [])
        profile_required_evidence_count = len(required_evidence) if isinstance(required_evidence, list) else 0
        required_evidence_count += profile_required_evidence_count
        if profile_required_evidence_count == 0:
            profiles_missing_required_evidence.append(profile_name)
        if isinstance(required_evidence, list):
            required_evidence_by_profile[profile_name] = sorted(str(item) for item in required_evidence)
        permissions = profile.get("permissions", [])
        profile_permission_count = len(permissions) if isinstance(permissions, list) else 0
        if profile_permission_count == 0:
            profiles_missing_permissions.append(profile_name)
        if isinstance(permissions, list):
            permissions_by_profile[profile_name] = sorted(str(permission) for permission in permissions)
            for permission in permissions:
                key = str(permission)
                by_permission[key] = by_permission.get(key, 0) + 1
    profiles_with_contract_gaps = sorted(
        set(
            profiles_missing_write_policy
            + profiles_missing_allowed_roots
            + profiles_missing_permissions
            + profiles_missing_stop_conditions
            + profiles_missing_required_evidence
        )
    )
    missing_by_contract_dimension = {
        "write_policy": sorted(profiles_missing_write_policy),
        "permissions": sorted(profiles_missing_permissions),
        "allowed_roots": sorted(profiles_missing_allowed_roots),
        "stop_conditions": sorted(profiles_missing_stop_conditions),
        "required_evidence": sorted(profiles_missing_required_evidence),
    }
    return {
        "profile_count": len(profiles),
        "profile_names": sorted(profiles),
        "has_profiles": bool(profiles),
        "contract_dimensions": sorted(missing_by_contract_dimension),
        "contract_dimension_count": len(missing_by_contract_dimension),
        "contract_dimension_status": {
            dimension: _contract_status(bool(profiles), missing_profiles)
            for dimension, missing_profiles in missing_by_contract_dimension.items()
        },
        "missing_profiles_by_contract_dimension": missing_by_contract_dimension,
        "missing_profile_count_by_contract_dimension": {
            dimension: len(missing_profiles)
            for dimension, missing_profiles in missing_by_contract_dimension.items()
        },
        "by_write_policy": by_write_policy,
        "write_policy_count": len(by_write_policy),
        "write_policy_by_profile": write_policy_by_profile,
        "profiles_missing_write_policy": sorted(profiles_missing_write_policy),
        "profiles_missing_write_policy_count": len(profiles_missing_write_policy),
        "has_profiles_missing_write_policy": bool(profiles_missing_write_policy),
        "all_profiles_have_write_policy": bool(profiles) and not profiles_missing_write_policy,
        "by_permission": by_permission,
        "permission_count": len(by_permission),
        "permissions_by_profile": permissions_by_profile,
        "permission_count_by_profile": {
            profile_name: len(permission_items)
            for profile_name, permission_items in permissions_by_profile.items()
        },
        "profiles_missing_permissions": sorted(profiles_missing_permissions),
        "profiles_missing_permission_count": len(profiles_missing_permissions),
        "has_profiles_missing_permissions": bool(profiles_missing_permissions),
        "all_profiles_have_permissions": bool(profiles) and not profiles_missing_permissions,
        "allowed_root_count": root_count,
        "allowed_roots_by_profile": allowed_roots_by_profile,
        "allowed_root_count_by_profile": {
            profile_name: len(root_items)
            for profile_name, root_items in allowed_roots_by_profile.items()
        },
        "profiles_missing_allowed_roots": sorted(profiles_missing_allowed_roots),
        "profiles_missing_allowed_root_count": len(profiles_missing_allowed_roots),
        "has_profiles_missing_allowed_roots": bool(profiles_missing_allowed_roots),
        "all_profiles_have_allowed_roots": bool(profiles) and not profiles_missing_allowed_roots,
        "stop_condition_count": stop_condition_count,
        "has_stop_conditions": stop_condition_count > 0,
        "stop_conditions_by_profile": stop_conditions_by_profile,
        "stop_condition_count_by_profile": {
            profile_name: len(condition_items)
            for profile_name, condition_items in stop_conditions_by_profile.items()
        },
        "profiles_missing_stop_conditions": sorted(profiles_missing_stop_conditions),
        "profiles_missing_stop_condition_count": len(profiles_missing_stop_conditions),
        "has_profiles_missing_stop_conditions": bool(profiles_missing_stop_conditions),
        "all_profiles_have_stop_conditions": bool(profiles) and not profiles_missing_stop_conditions,
        "taxonomy_stop_conditions_by_profile": taxonomy_stop_conditions_by_profile,
        "taxonomy_stop_condition_count": sum(
            len(conditions) for conditions in taxonomy_stop_conditions_by_profile.values()
        ),
        "profiles_with_taxonomy_stop_conditions": sorted(taxonomy_stop_conditions_by_profile),
        "profiles_with_taxonomy_stop_condition_count": len(taxonomy_stop_conditions_by_profile),
        "profiles_without_taxonomy_stop_conditions": sorted(profiles_without_taxonomy_stop_conditions),
        "profiles_without_taxonomy_stop_condition_count": len(profiles_without_taxonomy_stop_conditions),
        "has_profiles_without_taxonomy_stop_conditions": bool(profiles_without_taxonomy_stop_conditions),
        "all_profiles_have_taxonomy_stop_conditions": bool(profiles) and not profiles_without_taxonomy_stop_conditions,
        "has_taxonomy_stop_conditions": bool(taxonomy_stop_conditions_by_profile),
        "required_evidence_count": required_evidence_count,
        "has_required_evidence": required_evidence_count > 0,
        "required_evidence_by_profile": required_evidence_by_profile,
        "required_evidence_count_by_profile": {
            profile_name: len(evidence_items)
            for profile_name, evidence_items in required_evidence_by_profile.items()
        },
        "profiles_missing_required_evidence": sorted(profiles_missing_required_evidence),
        "profiles_missing_required_evidence_count": len(profiles_missing_required_evidence),
        "has_profiles_missing_required_evidence": bool(profiles_missing_required_evidence),
        "all_profiles_have_required_evidence": bool(profiles) and not profiles_missing_required_evidence,
        "profiles_with_contract_gaps": profiles_with_contract_gaps,
        **_contract_readiness(bool(profiles), profiles_with_contract_gaps),
    }


def _skill_profiles_readiness_overview(
    profile_summary: dict[str, Any],
    event_coverage: dict[str, Any],
) -> dict[str, Any]:
    """Return a compact cross-contract readiness summary for profile consumers."""
    return _contract_sections_overview({
        "profile_contracts": {
            "status": profile_summary["contract_status"],
            "ready": profile_summary["contract_ready"],
            "gap_count": profile_summary["contract_gap_count"],
        },
        "lifecycle_event_coverage": {
            "status": event_coverage["contract_status"],
            "ready": event_coverage["contract_ready"],
            "gap_count": event_coverage["contract_gap_count"],
        },
    })


def skills_profiles(repo_root: Path, profile: str | None = None) -> CallResult:
    """Return profile-v2-style operation modes for skill lifecycle work."""
    result = CallResult()
    result.metadata["command"] = "skills profiles"
    profile_key = profile.strip() if profile else None
    profiles = SKILL_OPERATION_PROFILES
    if profile_key:
        if profile_key not in profiles:
            result.status = "error"
            result.data["skill_profiles"] = {
                "schema_version": "skill-operation-profiles.v1",
                "status": "blocked",
                "selected_profile": None,
                "requested_profile": profile_key,
                "available_profiles": sorted(profiles),
            }
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Unknown skill operation profile '{profile_key}'.",
                    fix_suggestion=f"Use one of: {', '.join(sorted(profiles))}",
                )
            )
            return result
        selected_profiles = {profile_key: profiles[profile_key]}
    else:
        selected_profiles = profiles

    profile_summary = _skill_profile_summary(selected_profiles)
    event_coverage = _skill_profile_event_coverage(selected_profiles, CAPABILITY_LIFECYCLE_EVENT_CONSUMERS)

    result.data["skill_profiles"] = {
        "schema_version": "skill-operation-profiles.v1",
        "status": "pass",
        "repo_root": str(repo_root),
        "workspace_roots": _skill_profile_workspace_roots(repo_root),
        "profile_model": "profile-v2-inspired",
        "operation_context": _skill_profiles_operation_context(),
        "selected_profile": profile_key,
        "profile_names": list(selected_profiles),
        "available_profiles": sorted(profiles),
        "readiness_overview": _skill_profiles_readiness_overview(profile_summary, event_coverage),
        "profile_summary": profile_summary,
        "event_coverage": event_coverage,
        "eval_blocker_classes": {
            blocker_class: DOCTOR_BLOCKER_TAXONOMY[blocker_class]
            for blocker_class in EVAL_BLOCKER_CLASSES
        },
        "blocker_taxonomy": DOCTOR_BLOCKER_TAXONOMY,
        "warning_taxonomy": DOCTOR_WARNING_TAXONOMY,
        "profiles": _profiles_with_effective_roots(selected_profiles),
        "profile_order": ["authoring", "package-review", "plugin-share", "eval", "live-mutation"],
        "agent_summary": (
            f"Profile '{profile_key}' is declared."
            if profile_key
            else f"{len(profiles)} skill operation profiles are declared."
        ),
    }
    return result


def _doctor_check(status: str, **details: Any) -> dict[str, Any]:
    check_name = str(details.pop("check_name", "") or "")
    payload = {
        "status": status,
        "sdk_layer": _doctor_sdk_layer_for("check", check_name),
    }
    payload.update(details)
    return payload


PROJECT_SKILLS_SDK_MANIFEST = "skills-sdk.json"
PROJECT_SKILLS_SDK_SCHEMA = "Infrastructure/config/schemas/skills-sdk.project.v1.schema.json"
PROJECT_SKILLS_SDK_SCHEMA_VERSION = "skills-sdk.project.v1"
PROJECT_SKILL_ROOT_CLASSIFICATIONS = frozenset({
    "canonical_project_source",
    "generated_runtime_projection",
    "client_runtime_config",
    "unknown",
})


def _repo_relative_path_parts(path: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in Path(path.strip().strip("/")).parts)


def _path_is_under_declared_skill_root(path: str, root: str) -> bool:
    path_parts = _repo_relative_path_parts(path)
    root_parts = _repo_relative_path_parts(root)
    return bool(root_parts) and path_parts[: len(root_parts)] == root_parts


def _evaluate_project_skills_sdk_manifest(repo_root: Path | None) -> _ManifestEvaluation:
    """Return the explicit absent/valid/invalid state for the owner-repo manifest.

    An invalid manifest is never collapsed into ``absent``: it carries
    deterministic, machine-readable blockers so ownership and lifecycle callers
    can refuse to trust it instead of silently falling back to path heuristics.
    """
    return _evaluate_repo_manifest(repo_root)


def _load_project_skills_sdk_manifest(repo_root: Path | None) -> dict[str, Any] | None:
    """Return the manifest payload only when it evaluates to a trusted valid state."""
    evaluation = _evaluate_project_skills_sdk_manifest(repo_root)
    return evaluation.manifest if evaluation.is_valid else None


def _manifest_state_summary(evaluation: _ManifestEvaluation) -> dict[str, Any]:
    """Expose owner-manifest state for machine-readable doctor/ownership output."""
    return {
        "state": evaluation.state,
        "path": evaluation.path,
        "schema": PROJECT_SKILLS_SDK_SCHEMA,
        "schema_version": PROJECT_SKILLS_SDK_SCHEMA_VERSION,
        "legacy_compat": evaluation.legacy_compat,
        "missing_contract_fields": list(evaluation.missing_contract_fields),
        "blockers": evaluation.blocker_dicts(),
        "compatibility_note": evaluation.compatibility_note(),
    }


def _manifest_skill_root_ownership(repo_root: Path | None, path: str) -> dict[str, Any] | None:
    manifest = _load_project_skills_sdk_manifest(repo_root)
    if not manifest:
        return None
    matches: list[tuple[int, str, str]] = []
    for root in manifest.get("skill_roots", []):
        if not isinstance(root, dict):
            continue
        root_path = str(root.get("path") or "").strip().strip("/")
        if not root_path or not _path_is_under_declared_skill_root(path, root_path):
            continue
        classification = str(root.get("classification") or "unknown")
        if classification not in PROJECT_SKILL_ROOT_CLASSIFICATIONS:
            continue
        matches.append((len(_repo_relative_path_parts(root_path)), root_path, classification))
    if not matches:
        return None
    _, root_path, classification = max(matches, key=lambda item: item[0])
    editable_source = classification == "canonical_project_source"
    return {
        "path": path,
        "root": root_path,
        "classification": classification,
        "editable_source": editable_source,
        "owner_manifest_required_for_edit": not editable_source,
        "manifest_schema": PROJECT_SKILLS_SDK_SCHEMA,
        "manifest_declared": True,
        "owner_manifest_path": PROJECT_SKILLS_SDK_MANIFEST,
        "owner_manifest_project_id": manifest.get("project_id"),
    }


def _skill_root_ownership_for_path(
    repo_relative_path: str | None,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Classify whether a repo-relative skill path is editable source or projection."""
    if not repo_relative_path:
        return {
            "path": None,
            "root": None,
            "classification": "unknown",
            "editable_source": False,
            "owner_manifest_required_for_edit": False,
        }

    path = repo_relative_path.strip().strip("/")
    parts = Path(path).parts
    normalized_parts = _repo_relative_path_parts(path)
    manifest_ownership = _manifest_skill_root_ownership(repo_root, path)
    if manifest_ownership:
        return manifest_ownership
    if normalized_parts[:2] == (".agents", "skills"):
        return {
            "path": path,
            "root": ".agents/skills",
            "classification": "generated_runtime_projection",
            "editable_source": False,
            "owner_manifest_required_for_edit": True,
            "manifest_schema": PROJECT_SKILLS_SDK_SCHEMA,
            "manifest_declared": False,
        }
    if normalized_parts[:2] == (".codex", "skills"):
        return {
            "path": path,
            "root": ".codex/skills",
            "classification": "client_runtime_config",
            "editable_source": False,
            "owner_manifest_required_for_edit": True,
            "manifest_schema": PROJECT_SKILLS_SDK_SCHEMA,
            "manifest_declared": False,
        }
    if path.startswith("Skills/") or path == "Skills":
        return {
            "path": path,
            "root": "Skills/**",
            "classification": "canonical_project_source",
            "editable_source": True,
            "owner_manifest_required_for_edit": False,
            "owner_kind": "repo_skills",
        }
    if len(parts) >= 3 and parts[0] == "Plugins" and parts[2] == "skills":
        return {
            "path": path,
            "root": "Plugins/*/skills/**",
            "classification": "canonical_project_source",
            "editable_source": True,
            "owner_manifest_required_for_edit": False,
            "owner_kind": "plugin_skills",
        }
    return {
        "path": path,
        "root": None,
        "classification": "unknown",
        "editable_source": False,
        "owner_manifest_required_for_edit": False,
    }


def _skill_doctor_next_command_decision(
    *,
    blockers: list[dict[str, str]],
    warnings: list[dict[str, str]],
    checks: dict[str, Any],
    normalized_handle: Any,
    query: str,
    audit_target: str | None,
    strict: bool,
) -> dict[str, str | None]:
    """Select the most actionable follow-up command from classified doctor evidence."""
    blocker_classes = [blocker.get("class") for blocker in blockers]
    if "blocked_validation" in blocker_classes:
        command = checks.get("structural_audit", {}).get("command")
        if command:
            return {
                "command": str(command),
                "precedence": "blocker",
                "source_class": "blocked_validation",
                "source_check": "structural_audit",
                "reason": "blocked_validation takes precedence; rerun the structural audit that failed.",
            }
        if audit_target:
            return {
                "command": _skills_validation_command("audit", audit_target, "--level", "compat"),
                "precedence": "blocker",
                "source_class": "blocked_validation",
                "source_check": "structural_audit",
                "reason": "blocked_validation takes precedence; no check command was present, so use the compatibility audit fallback.",
            }
    if "blocked_runtime" in blocker_classes:
        command = checks.get("runtime_reachability", {}).get("command")
        if command:
            return {
                "command": str(command),
                "precedence": "blocker",
                "source_class": "blocked_runtime",
                "source_check": "runtime_reachability",
                "reason": "blocked_runtime takes precedence after validation blockers; rerun the runtime reachability proof.",
            }
    if "blocked_missing_source" in blocker_classes:
        return {
            "command": _skills_validation_command("resolve", str(normalized_handle or query)),
            "precedence": "blocker",
            "source_class": "blocked_missing_source",
            "source_check": "canonical_source",
            "reason": "blocked_missing_source requires resolving the target before any runtime or package proof.",
        }
    if "blocked_resolution" in blocker_classes:
        return {
            "command": _skills_validation_command("resolve", str(normalized_handle or query)),
            "precedence": "blocker",
            "source_class": "blocked_resolution",
            "source_check": "resolver",
            "reason": "blocked_resolution requires resolving the requested handle before follow-up checks.",
        }
    if blockers:
        return {
            "command": _skills_validation_command("doctor", str(normalized_handle or query)),
            "precedence": "blocker",
            "source_class": str(blocker_classes[0] or "unclassified_blocker"),
            "source_check": None,
            "reason": "An unclassified blocker remains; rerun doctor to preserve the full diagnostic payload.",
        }

    warning_classes = {warning.get("class") for warning in warnings}
    package_or_metadata_warning = bool(
        {"metadata_incomplete", "capability_contract_incomplete"} & warning_classes
    )
    if package_or_metadata_warning and audit_target and not strict:
        return {
            "command": _skills_validation_command("audit", audit_target, "--level", "strict"),
            "precedence": "warning",
            "source_class": "metadata_incomplete" if "metadata_incomplete" in warning_classes else "capability_contract_incomplete",
            "source_check": "capability_metadata",
            "reason": "Package or metadata warnings should be tightened by strict audit before package proof.",
        }
    if "capability_contract_incomplete" in warning_classes:
        return {
            "command": _skills_validation_command("package", str(normalized_handle or query)),
            "precedence": "warning",
            "source_class": "capability_contract_incomplete",
            "source_check": "package_readiness",
            "reason": "Capability package metadata is incomplete; run the package readiness command.",
        }
    if "outcome_proof_missing" in warning_classes:
        return {
            "command": _skills_validation_command("prove", str(normalized_handle or query)),
            "precedence": "warning",
            "source_class": "outcome_proof_missing",
            "source_check": "outcome_proof",
            "reason": "Outcome proof is missing; run the proof scorecard command.",
        }
    if warnings and audit_target and not strict:
        return {
            "command": _skills_validation_command("audit", audit_target, "--level", "strict"),
            "precedence": "warning",
            "source_class": str(next(iter(warning_classes), "unclassified_warning")),
            "source_check": None,
            "reason": "A warning remains and strict audit has not run; run strict audit before claiming readiness.",
        }
    if normalized_handle:
        return {
            "command": _skills_validation_command("prove", str(normalized_handle)),
            "precedence": "default",
            "source_class": None,
            "source_check": "outcome_proof",
            "reason": "No blockers or warnings remain; run the proof scorecard as the next evidence command.",
        }
    if not audit_target:
        return {
            "command": _skills_validation_command("resolve", query),
            "precedence": "default",
            "source_class": None,
            "source_check": "canonical_source",
            "reason": "No handle and no audit target are available; resolve the target first.",
        }
    return {
        "command": _skills_validation_command("audit", str(audit_target), "--level", "strict"),
        "precedence": "default",
        "source_class": None,
        "source_check": "structural_audit",
        "reason": "No handle is available; strict audit is the safest remaining source-path evidence command.",
    }


def skills_load_preview(repo_root: Path) -> CallResult:
    """
    Builds a Codex load preview for the repository.

    Parameters:
        repo_root (Path): Path to the repository root used to generate the preview.

    Returns:
        result (CallResult): A CallResult whose `data["codex_load_preview"]` contains the preview payload. The result.metadata includes `command = "skills load-preview"`.
    """
    result = CallResult()
    result.metadata["command"] = "skills load-preview"
    result.data["codex_load_preview"] = build_codex_load_preview(repo_root)
    return result


def skills_codex_preview(repo_root: Path) -> CallResult:
    """
    Builds a Codex-mode preview payload summarizing source-modeled skill discovery and available preview commands.

    The returned CallResult contains a `codex_preview` payload with keys such as `schema_version`, `command`, `status`, `source_identity`, `source_basis`, `blocked_checks`, `modeled_rule_version`, `source_files`, `commands` (each with `name`, `purpose`, and `validation_command`), and an `agent_summary`. The CallResult metadata will include `command = "skills codex-preview"`.

    Returns:
        CallResult: A result whose `data["codex_preview"]` holds the structured Codex preview payload.
    """
    load_preview = build_codex_load_preview(repo_root)
    result = CallResult()
    result.metadata["command"] = "skills codex-preview"
    result.data["codex_preview"] = {
        "schema_version": CODEX_PREVIEW_SCHEMA_VERSION,
        "command": "skills codex-preview",
        "status": load_preview.get("status"),
        "not_a_validation_result": True,
        "source_identity": load_preview.get("source_identity"),
        "source_basis": load_preview.get("source_basis"),
        "blocked_checks": load_preview.get("blocked_checks", []),
        "modeled_rule_version": CODEX_PREVIEW_MODELED_RULE_VERSION,
        "source_files": list(CODEX_PREVIEW_SOURCE_FILES),
        "commands": [
            {
                "name": "load-preview",
                "purpose": "Model Codex skill-root loading and scan visible SKILL.md metadata.",
                "validation_command": _skills_validation_command("load-preview"),
            },
            {
                "name": "render-preview",
                "purpose": "Model available-skill rendering, source basis, budget, and truncation status.",
                "validation_command": _skills_validation_command("render-preview"),
            },
            {
                "name": "config explain",
                "purpose": "Explain source-backed Codex skills.config rule semantics and blocked live layers.",
                "validation_command": _skills_validation_command("config", "explain"),
            },
            {
                "name": "inject-preview",
                "purpose": "Model explicit skill mention selection from prompt text.",
                "validation_command": _skills_validation_command("inject-preview", "$skill"),
            },
            {
                "name": "implicit-preview",
                "purpose": "Model implicit invocation attribution from a shell command.",
                "validation_command": _skills_validation_command("implicit-preview", "--command", "cat SKILL.md"),
            },
        ],
        "agent_summary": "Use the listed public skills preview commands for source-modeled Codex preview evidence; they do not claim live runtime parity.",
    }
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
