from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from .skills_impl_listing import *  # noqa: F403


def _freeze_contract_mapping(
    value: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Mapping[str, Any]]:
    """Freeze module-level contract mappings while preserving list schema fields."""
    return MappingProxyType({key: MappingProxyType(dict(item)) for key, item in value.items()})


CAPABILITY_LIFECYCLE_EVENT_CONSUMERS: Mapping[str, Mapping[str, Any]] = _freeze_contract_mapping({
    "skill_loaded": {
        "profiles": ["authoring", "package-review", "eval"],
        "producer_commands": ["./bin/ask skills resolve <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "skill_loaded")],
    },
    "skill_doctor_completed": {
        "profiles": ["authoring", "package-review"],
        "producer_commands": ["./bin/ask skills doctor <handle-or-path> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "skill_doctor_completed")],
    },
    "package_readiness_checked": {
        "profiles": ["package-review", "plugin-share"],
        "producer_commands": ["./bin/ask skills package <handle-or-path> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "package_readiness_checked")],
    },
    "eval_started": {
        "profiles": ["eval"],
        "producer_commands": ["./bin/ask skills prove <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "eval_started")],
    },
    "eval_blocked": {
        "profiles": ["eval"],
        "producer_commands": ["./bin/ask skills prove <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "eval_blocked")],
    },
    "eval_completed": {
        "profiles": ["eval"],
        "producer_commands": ["./bin/ask skills prove <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "eval_completed")],
    },
    "projection_synced": {
        "profiles": ["authoring", "live-mutation"],
        "producer_commands": [_skills_validation_command("sync")],
        "observer_commands": [_skills_validation_command("list")],
    },
    "manifest_changed": {
        "profiles": ["authoring", "plugin-share", "live-mutation"],
        "producer_commands": [_skills_validation_command("sync", "--scope", "workspace", "--projection", "flat")],
        "observer_commands": [_skills_validation_command("list")],
    },
})


SKILL_OPERATION_PROFILES: Mapping[str, Mapping[str, Any]] = _freeze_contract_mapping({
    "authoring": {
        "intent": "Create or revise canonical skill sources.",
        "allowed_roots": ["Skills/**", "Plugins/*/skills/**", "Docs/**", "Infrastructure/tests/**"],
        "write_policy": "canonical_source_only",
        "permissions": ["repo_read", "repo_write_canonical_sources", "local_validation"],
        "required_evidence": ["nearest AGENTS.md", "UBIQUITOUS_LANGUAGE.md", "skill audit", "focused tests"],
        "stop_conditions": ["missing canonical owner", "strict audit failure", "runtime projection drift"],
    },
    "package-review": {
        "intent": "Check a skill or plugin package before promotion.",
        "allowed_roots": ["Skills/**", "Plugins/**", "Infrastructure/artifacts/skill-reviews/**"],
        "write_policy": "reports_only_unless_fix_requested",
        "permissions": ["repo_read", "local_validation", "artifact_write"],
        "required_evidence": [
            "compat or strict audit",
            "external review report",
            "Plugin Eval grade B+ or better",
            "Tessl review score >= 95",
            "metadata contract",
        ],
        "stop_conditions": ["blocked_validation", "blocked_missing_artifact", "blocked_missing_tool"],
    },
    "plugin-share": {
        "intent": "Prepare versioned skill/plugin sharing metadata and install readiness.",
        "allowed_roots": ["Plugins/**", "Skills/**", ".agents/Plugins/marketplace.json", "Docs/**"],
        "write_policy": "versioned_metadata_and_marketplace_only",
        "permissions": ["repo_read", "repo_write_metadata", "local_validation"],
        "required_evidence": ["version", "provenance", "compatible_roles", "runtime_needs", "share_readiness"],
        "stop_conditions": ["missing provenance", "untrusted source", "unpinned external ref"],
    },
    "eval": {
        "intent": "Run smoke, workout, or release evidence for one capability.",
        "allowed_roots": ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        "write_policy": "artifact_write_only",
        "permissions": ["repo_read", "local_validation", "artifact_write"],
        "required_evidence": [
            "eval_started event",
            "Codex smoke run uses [profiles.fast] via --profile fast",
            f"Tessl eval source staged under {os.path.join(tempfile.gettempdir(), 'ask-tessl-evals')}",
            "staged tessl.json project marker",
            "canonical references/evals.yaml copied into staged input",
            "eval_completed or eval_blocked event",
            "timeout classification",
        ],
        "stop_conditions": list(EVAL_BLOCKER_CLASSES),
    },
    "live-mutation": {
        "intent": "Perform externally visible mutation such as tracker, PR, or runtime sync changes.",
        "allowed_roots": ["Skills/**", "Plugins/**", ".agents/**", ".skillsets/**", "Docs/**"],
        "write_policy": "explicit_request_required",
        "permissions": ["repo_read", "repo_write", "external_write_after_confirmation"],
        "required_evidence": ["operator request", "target identity", "rollback path", "post-mutation validation"],
        "stop_conditions": ["unclear target", "auth mismatch", "unrelated dirty worktree", "rollback unavailable"],
    },
})


def _skill_memory_operation_context() -> dict[str, Any]:
    """Return profile and provenance context for the skill memory facade."""
    return {
        "primary_profile": "authoring",
        "consumer_profiles": ["authoring", "package-review", "eval"],
        "provider_model": "extension-like-read-only",
        "profiles": {
            profile_name: {
                "intent": SKILL_OPERATION_PROFILES[profile_name]["intent"],
                "write_policy": SKILL_OPERATION_PROFILES[profile_name]["write_policy"],
                "required_evidence": SKILL_OPERATION_PROFILES[profile_name]["required_evidence"],
            }
            for profile_name in ("authoring", "package-review", "eval")
        },
        "provider_contract": {
            "required_entry_fields": ["id", "source_id", "path", "title", "snippet", "provenance", "freshness"],
            "read_modes": ["list", "read", "search"],
            "mutation_policy": "read_only",
        },
        "follow_up_commands": [
            _skills_validation_command("memory", "list"),
            "./bin/ask skills memory search <query> --json --robot",
            "./bin/ask skills memory read <entry-id-or-path> --json --robot",
        ],
        "validation_commands": [
            _skills_validation_command("memory", "search", "projection"),
            _ask_validation_command("memory", "search", "projection"),
        ],
    }


def _skill_memory_source_summary(roots: list[dict[str, Any]]) -> dict[str, Any]:
    """Return compact source availability for the skill memory provider."""
    available = [root["provider"] for root in roots if root["exists"]]
    missing = [root["provider"] for root in roots if not root["exists"]]
    return {
        "source_count": len(roots),
        "available_sources": available,
        "missing_sources": missing,
    }


def _skill_memory_freshness_label(value: Any) -> str:
    """Return a stable bucket label for memory freshness metadata."""
    if isinstance(value, str) and value.strip():
        return value
    if isinstance(value, dict):
        status = value.get("status")
        if isinstance(status, str) and status.strip():
            return status
        if value.get("mtime") is not None:
            return "has_mtime"
        if value:
            return "metadata_present"
    return "unknown"


def _skill_memory_entry_summary(entries: list[dict[str, Any]], total_count: int | None = None) -> dict[str, Any]:
    """Return compact memory result counts grouped by provider and freshness."""
    by_source: dict[str, int] = {}
    by_freshness: dict[str, int] = {}
    for entry in entries:
        source_id = str(entry.get("source_id") or "unknown")
        freshness = _skill_memory_freshness_label(entry.get("freshness"))
        by_source[source_id] = by_source.get(source_id, 0) + 1
        by_freshness[freshness] = by_freshness.get(freshness, 0) + 1
    return {
        "returned_count": len(entries),
        "total_count": len(entries) if total_count is None else total_count,
        "by_source": by_source,
        "by_freshness": by_freshness,
    }


def skills_memory(
    repo_root: Path,
    mode: str,
    query: str | None = None,
    limit: int = 8,
    source_id: str | None = None,
) -> CallResult:
    """List, read, or search durable skill memory surfaces as a read-only provider."""
    result = CallResult()
    result.metadata["command"] = f"skills memory {mode}"
    provider_roots = [
        {
            "provider": source.source_id,
            "root": str(source.root),
            "description": source.label,
            "type": source.source_type,
            "exists": (repo_root / source.root).exists(),
        }
        for source in MEMORY_SOURCES
    ]
    mode_key = mode.strip().lower()
    capped_limit = min(limit, 50)
    payload: dict[str, Any] = {
        "schema_version": "skill-memory-provider.v1",
        "status": "pass",
        "mode": mode_key,
        "query": query,
        "provider_model": "extension-like-read-only",
        "contract_schemas": {
            "memory": "skill-memory-provider.v1",
            "provider": "memory-provider.v1",
            "profiles": "skill-operation-profiles.v1",
            "events": "skill-events.v1",
        },
        "operation_context": _skill_memory_operation_context(),
        "roots": provider_roots,
        "source_summary": _skill_memory_source_summary(provider_roots),
        "memory_provider_schema": "memory-provider.v1",
    }

    if mode_key == "list":
        provider_result = _memory_provider_list(repo_root, source_id=source_id, limit=capped_limit)
        memory_payload = provider_result.data.get("memory", {})
        if provider_result.status != "success":
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = memory_payload.get("agent_summary") or (
                provider_result.errors[0].message if provider_result.errors else "Memory list failed."
            )
            result.errors.extend(provider_result.errors)
            result.data["skill_memory"] = payload
            return result
        payload["entries"] = memory_payload.get("entries", [])
        payload["entry_count"] = memory_payload.get("count", len(payload["entries"]))
        payload["total_count"] = memory_payload.get("total_count", len(payload["entries"]))
        payload["entry_summary"] = _skill_memory_entry_summary(payload["entries"], payload["total_count"])
        payload["agent_summary"] = memory_payload.get("agent_summary", "Listed skill memory entries.")
    elif mode_key == "read":
        needle = (query or "").strip()
        if not needle:
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = "Memory read requires an entry id or repo-relative path."
            result.data["skill_memory"] = payload
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=payload["agent_summary"],
                    fix_suggestion="Run ./bin/ask skills memory list --json --robot and pass an entry id.",
                )
            )
            return result
        provider_result = _memory_provider_read(repo_root, needle)
        memory_payload = provider_result.data.get("memory", {})
        if provider_result.status != "success":
            result.status = "error"
            payload["status"] = "blocked"
            payload["requested"] = needle
            payload["agent_summary"] = memory_payload.get("agent_summary") or f"No skill memory entry matched '{needle}'."
            result.errors.extend(provider_result.errors)
            result.data["skill_memory"] = payload
            return result
        payload["entry"] = memory_payload.get("entry")
        payload["entry_summary"] = _skill_memory_entry_summary([payload["entry"]] if payload["entry"] else [], 1 if payload["entry"] else 0)
        payload["agent_summary"] = memory_payload.get("agent_summary", f"Read skill memory entry {needle}.")
    elif mode_key == "search":
        if not (query or "").strip():
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = "Memory search requires a non-empty query."
            result.data["skill_memory"] = payload
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=payload["agent_summary"],
                    fix_suggestion="Run ./bin/ask skills memory search '<keyword>' --json --robot.",
                )
            )
            return result
        provider_result = _memory_provider_search(repo_root, query or "", source_id=source_id, limit=capped_limit)
        memory_payload = provider_result.data.get("memory", {})
        if provider_result.status != "success":
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = memory_payload.get("agent_summary") or (
                provider_result.errors[0].message if provider_result.errors else "Memory search failed."
            )
            result.errors.extend(provider_result.errors)
            result.data["skill_memory"] = payload
            return result
        payload["entries"] = memory_payload.get("results", [])
        payload["entry_count"] = memory_payload.get("count", len(payload["entries"]))
        payload["total_count"] = memory_payload.get("total_count", len(payload["entries"]))
        payload["entry_summary"] = _skill_memory_entry_summary(payload["entries"], payload["total_count"])
        payload["agent_summary"] = memory_payload.get("agent_summary", f"Found skill memory entries matching '{query}'.")
    else:
        result.status = "error"
        payload["status"] = "blocked"
        payload["agent_summary"] = f"Unknown skill memory mode '{mode}'."
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use one of: list, read, search.",
            )
        )

    result.data["skill_memory"] = payload
    return result


def _capability_lifecycle_event(
    *,
    event_type: str,
    query: str,
    target_kind: str,
    handle: Any,
    source_path: Any,
    audit_target: Any,
    status: str,
    blockers: list[dict[str, str]],
    warnings: list[dict[str, str]],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured lifecycle event for capability diagnostics."""
    subject_key = str(handle or audit_target or source_path or query)
    event_consumer = CAPABILITY_LIFECYCLE_EVENT_CONSUMERS.get(event_type, {})
    producer_commands = event_consumer.get("producer_commands", [])
    observer_commands = event_consumer.get("observer_commands", [])
    event = {
        "schema_version": "capability-lifecycle-event.v1",
        "event_type": event_type,
        "event_definition": CAPABILITY_LIFECYCLE_EVENT_TYPES.get(event_type),
        "contract_schemas": {
            "lifecycle_event": "capability-lifecycle-event.v1",
            "events": "skill-events.v1",
            "profiles": "skill-operation-profiles.v1",
        },
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "event_identity": {
            "event_type": event_type,
            "subject_key": subject_key,
            "target_kind": target_kind,
            "status": status,
        },
        "producer_command": producer_commands[0] if producer_commands else None,
        "observer_command": observer_commands[0] if observer_commands else None,
        "subject": {
            "query": query,
            "target_kind": target_kind,
            "handle": handle,
            "canonical_source_path": source_path,
            "audit_target": audit_target,
        },
        "outcome": {
            "status": status,
            "blocker_classes": [blocker["class"] for blocker in blockers],
            "warning_classes": [warning["class"] for warning in warnings],
        },
    }
    if details:
        event["details"] = details
    return event


def _contract_status(has_items: bool, contract_gaps: list[str]) -> str:
    """Return the stable readiness label for a summarized contract."""
    if not has_items:
        return "empty"
    if contract_gaps:
        return "has_gaps"
    return "ready"


def _contract_readiness(has_items: bool, contract_gaps: list[str]) -> dict[str, Any]:
    """Return shared readiness fields for summarized contracts."""
    return {
        "contract_gap_count": len(contract_gaps),
        "has_contract_gaps": bool(contract_gaps),
        "contract_status": _contract_status(has_items, contract_gaps),
        "contract_ready": has_items and not contract_gaps,
    }


def _contract_sections_overview(contract_sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return shared readiness fields for named contract sections."""
    gap_count = sum(int(section["gap_count"]) for section in contract_sections.values())
    contract_ready = bool(contract_sections) and all(section["ready"] for section in contract_sections.values())
    section_statuses = {str(section["status"]) for section in contract_sections.values()}
    if contract_ready:
        contract_status = "ready"
    elif "has_gaps" in section_statuses or gap_count > 0:
        contract_status = "has_gaps"
    else:
        contract_status = "empty"
    return {
        "contract_sections": contract_sections,
        "contract_status_by_section": {
            section_name: section["status"]
            for section_name, section in contract_sections.items()
        },
        "contract_gap_count_by_section": {
            section_name: section["gap_count"]
            for section_name, section in contract_sections.items()
        },
        "contract_section_count": len(contract_sections),
        "ready_contract_sections": sorted(
            section_name
            for section_name, section in contract_sections.items()
            if section["ready"]
        ),
        "blocked_contract_sections": sorted(
            section_name
            for section_name, section in contract_sections.items()
            if not section["ready"]
        ),
        "contract_gap_count": gap_count,
        "has_contract_gaps": gap_count > 0,
        "contract_ready": contract_ready,
        "contract_status": contract_status,
    }


def _skill_event_summary(
    event_consumers: dict[str, dict[str, Any]],
    known_profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return compact event coverage counts for automation consumers."""
    by_profile: dict[str, int] = {}
    events_by_profile: dict[str, list[str]] = {}
    profiles_by_event: dict[str, list[str]] = {}
    producer_count = 0
    observer_count = 0
    producer_command_count_by_event: dict[str, int] = {}
    observer_command_count_by_event: dict[str, int] = {}
    events_missing_producers: list[str] = []
    events_missing_observers: list[str] = []
    events_missing_profiles: list[str] = []
    events_with_unknown_profiles: dict[str, list[str]] = {}
    known_profile_names = set(known_profiles)
    for event_name, consumer in event_consumers.items():
        producer_commands = consumer.get("producer_commands", [])
        observer_commands = consumer.get("observer_commands", [])
        profiles = consumer.get("profiles", [])
        profiles_by_event[event_name] = sorted(str(profile) for profile in profiles)
        producer_command_count_by_event[event_name] = len(producer_commands)
        observer_command_count_by_event[event_name] = len(observer_commands)
        if not producer_commands:
            events_missing_producers.append(event_name)
        if not observer_commands:
            events_missing_observers.append(event_name)
        if not profiles:
            events_missing_profiles.append(event_name)
        producer_count += len(producer_commands)
        observer_count += len(observer_commands)
        for profile in profiles:
            if profile not in known_profile_names:
                events_with_unknown_profiles.setdefault(event_name, []).append(profile)
            by_profile[profile] = by_profile.get(profile, 0) + 1
            events_by_profile.setdefault(profile, []).append(event_name)
    events_with_contract_gaps = sorted(
        set(
            events_missing_producers
            + events_missing_observers
            + events_missing_profiles
            + list(events_with_unknown_profiles)
        )
    )
    missing_by_contract_dimension = {
        "known_profiles": sorted(events_with_unknown_profiles),
        "observer_commands": sorted(events_missing_observers),
        "producer_commands": sorted(events_missing_producers),
        "profiles": sorted(events_missing_profiles),
    }
    referenced_profile_names = set(by_profile)
    known_profiles_without_events = sorted(known_profile_names - referenced_profile_names)
    known_profiles_with_events = sorted(known_profile_names & referenced_profile_names)
    known_events_by_profile = {
        profile_name: sorted(events_by_profile.get(profile_name, []))
        for profile_name in sorted(known_profiles)
    }
    unknown_profile_reference_count = sum(
        len(profile_names) for profile_names in events_with_unknown_profiles.values()
    )
    return {
        "event_count": len(event_consumers),
        "contract_dimensions": sorted(missing_by_contract_dimension),
        "contract_dimension_count": len(missing_by_contract_dimension),
        "contract_dimension_status": {
            dimension: _contract_status(bool(event_consumers), missing_events)
            for dimension, missing_events in missing_by_contract_dimension.items()
        },
        "missing_events_by_contract_dimension": missing_by_contract_dimension,
        "missing_event_count_by_contract_dimension": {
            dimension: len(missing_events)
            for dimension, missing_events in missing_by_contract_dimension.items()
        },
        "producer_command_count": producer_count,
        "observer_command_count": observer_count,
        "producer_command_count_by_event": dict(sorted(producer_command_count_by_event.items())),
        "observer_command_count_by_event": dict(sorted(observer_command_count_by_event.items())),
        "events_missing_producers": sorted(events_missing_producers),
        "events_missing_observers": sorted(events_missing_observers),
        "events_missing_profiles": sorted(events_missing_profiles),
        "events_missing_profile_count": len(events_missing_profiles),
        "has_missing_producers": bool(events_missing_producers),
        "has_missing_observers": bool(events_missing_observers),
        "has_missing_profiles": bool(events_missing_profiles),
        "events_with_unknown_profile_count": len(events_with_unknown_profiles),
        "unknown_profile_reference_count": unknown_profile_reference_count,
        "events_with_unknown_profiles": {
            event_name: sorted(profile_names)
            for event_name, profile_names in sorted(events_with_unknown_profiles.items())
        },
        "profiles_unknown_to_registry": sorted(
            {
                profile_name
                for profile_names in events_with_unknown_profiles.values()
                for profile_name in profile_names
            }
        ),
        "has_unknown_profiles": bool(events_with_unknown_profiles),
        "known_profile_count": len(known_profiles),
        "known_profile_names": sorted(known_profiles),
        "referenced_profile_count": len(referenced_profile_names),
        "referenced_profile_names": sorted(referenced_profile_names),
        "known_profiles_with_events": known_profiles_with_events,
        "known_profile_event_coverage_count": len(known_profiles_with_events),
        "all_known_profiles_have_events": len(known_profiles_with_events) == len(known_profile_names),
        "known_profiles_without_events": known_profiles_without_events,
        "has_known_profiles_without_events": bool(known_profiles_without_events),
        "known_events_by_profile": known_events_by_profile,
        "known_event_count_by_profile": {
            profile_name: len(event_names)
            for profile_name, event_names in known_events_by_profile.items()
        },
        "events_with_contract_gaps": events_with_contract_gaps,
        **_contract_readiness(bool(event_consumers), events_with_contract_gaps),
        "by_profile": by_profile,
        "events_by_profile": {
            profile_name: sorted(event_names)
            for profile_name, event_names in sorted(events_by_profile.items())
        },
        "event_count_by_profile": {
            profile_name: len(event_names)
            for profile_name, event_names in sorted(events_by_profile.items())
        },
        "profiles_by_event": dict(sorted(profiles_by_event.items())),
        "profile_count_by_event": {
            event_name: len(profile_names)
            for event_name, profile_names in sorted(profiles_by_event.items())
        },
        "profile_count": len(by_profile),
        "profile_names": sorted(by_profile),
        "has_profiles": bool(by_profile),
    }


def _skill_events_readiness_overview(event_summary: dict[str, Any]) -> dict[str, Any]:
    """Return a compact readiness summary for lifecycle event consumers."""
    return _contract_sections_overview({
        "lifecycle_event_contract": {
            "status": event_summary["contract_status"],
            "ready": event_summary["contract_ready"],
            "gap_count": event_summary["contract_gap_count"],
        }
    })


def _unknown_skill_event_result(selected: str) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills events"
    result.status = "error"
    result.data["skill_events"] = {
        "schema_version": "skill-events.v1",
        "status": "blocked",
        "requested_event_type": selected,
        "available_event_types": sorted(CAPABILITY_LIFECYCLE_EVENT_TYPES),
    }
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=f"Unknown skill lifecycle event type '{selected}'.",
            fix_suggestion=f"Use one of: {', '.join(sorted(CAPABILITY_LIFECYCLE_EVENT_TYPES))}",
        )
    )
    return result


def _selected_skill_event_contract(selected: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    selected_event_types = (
        {selected: CAPABILITY_LIFECYCLE_EVENT_TYPES[selected]}
        if selected
        else CAPABILITY_LIFECYCLE_EVENT_TYPES
    )
    selected_event_consumers = (
        {selected: CAPABILITY_LIFECYCLE_EVENT_CONSUMERS[selected]}
        if selected
        else CAPABILITY_LIFECYCLE_EVENT_CONSUMERS
    )
    event_types = dict(selected_event_types)
    event_consumers = {
        event_type: dict(consumer)
        for event_type, consumer in selected_event_consumers.items()
    }
    return event_types, event_consumers


def _skill_events_contract_schemas() -> dict[str, str]:
    return {
        "events": "skill-events.v1",
        "lifecycle_event": "capability-lifecycle-event.v1",
        "profiles": "skill-operation-profiles.v1",
        "doctor": "skill-doctor.v1",
        "package": "skill-package-readiness.v1",
        "memory": "skill-memory-provider.v1",
    }


def _skill_events_payload(
    repo_root: Path,
    selected: str | None,
    event_types: dict[str, Any],
    event_consumers: dict[str, Any],
) -> dict[str, Any]:
    event_summary = _skill_event_summary(event_consumers, SKILL_OPERATION_PROFILES)
    return {
        "schema_version": "skill-events.v1",
        "status": "pass",
        "repo_root": str(repo_root),
        "selected_event_type": selected,
        "event_schema": "capability-lifecycle-event.v1",
        "event_names": list(event_types),
        "available_event_types": sorted(CAPABILITY_LIFECYCLE_EVENT_TYPES),
        "contract_schemas": _skill_events_contract_schemas(),
        "event_types": event_types,
        "event_consumers": event_consumers,
        "readiness_overview": _skill_events_readiness_overview(event_summary),
        "event_summary": event_summary,
        "validation_commands": [
            _skills_validation_command("events"),
            "./bin/ask skills events <event-type> --json --robot",
            _skills_validation_command("list"),
        ],
        "eval_blocker_classes": {
            blocker_class: DOCTOR_BLOCKER_TAXONOMY[blocker_class]
            for blocker_class in EVAL_BLOCKER_CLASSES
        },
        "blocker_taxonomy": DOCTOR_BLOCKER_TAXONOMY,
        "warning_taxonomy": DOCTOR_WARNING_TAXONOMY,
        "event_order": list(CAPABILITY_LIFECYCLE_EVENT_TYPES),
        "event_count": len(event_types),
        "agent_summary": (
            f"Lifecycle event '{selected}' is declared."
            if selected
            else f"{len(CAPABILITY_LIFECYCLE_EVENT_TYPES)} capability lifecycle event types are declared."
        ),
    }


def skills_events(repo_root: Path, event_type: str | None = None) -> CallResult:
    """Return the declared capability lifecycle event contract."""
    selected = event_type.strip() if event_type else None
    if selected and selected not in CAPABILITY_LIFECYCLE_EVENT_TYPES:
        return _unknown_skill_event_result(selected)
    event_types, event_consumers = _selected_skill_event_contract(selected)
    result = CallResult()
    result.metadata["command"] = "skills events"
    result.data["skill_events"] = _skill_events_payload(
        repo_root, selected, event_types, event_consumers
    )
    return result


def _skill_profile_workspace_roots(repo_root: Path) -> dict[str, Any]:
    return {
        "repo_root": str(repo_root),
        "canonical_skill_roots": ["Skills", "Plugins"],
        "runtime_projection_roots": [".agents/skills", ".skillsets"],
        "artifact_roots": ["Infrastructure/artifacts", "Infrastructure/workouts"],
        "memory_roots": [".harness/memory", "Wiki/wiki/learnings", "Docs/solutions"],
    }


def _profiles_with_effective_roots(profiles: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    enriched: dict[str, dict[str, Any]] = {}
    for name, profile in profiles.items():
        stop_conditions = list(profile.get("stop_conditions", []))
        enriched_profile = {
            **profile,
            "effective_roots": list(profile.get("allowed_roots", [])),
        }
        blocker_definitions = {
            condition: DOCTOR_BLOCKER_TAXONOMY[condition]
            for condition in stop_conditions
            if condition in DOCTOR_BLOCKER_TAXONOMY
        }
        if blocker_definitions:
            enriched_profile["stop_condition_definitions"] = blocker_definitions
        if name == "eval":
            enriched_profile["eval_blocker_classes"] = {
                blocker_class: DOCTOR_BLOCKER_TAXONOMY[blocker_class]
                for blocker_class in EVAL_BLOCKER_CLASSES
            }
            enriched_profile["eval_profile_contract"] = {
                "codex_profile": "fast",
                "codex_profile_config": "[profiles.fast]",
                "codex_runner_args": ["--profile", "fast"],
                "tessl_eval_staging_root": f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-evals')}/<skill-path>-<sha12>",
                "tessl_project_marker": "tessl.json",
                "staged_inputs": [
                    "SKILL.md",
                    "references/evals.yaml",
                    "references/contract.yaml",
                    "references/task-profile.json",
                    "evals/<case-id>/task.md",
                    "evals/<case-id>/criteria.json",
                ],
                "evidence_retention": "stable tmp staging is intentionally left for post-run inspection",
            }
        if name == "package-review":
            enriched_profile["external_review_contract"] = {
                "plugin_eval_min_acceptable_grade": PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE,
                "plugin_eval_b_plus_is_acceptable": True,
                "tessl_review_min_score": TESSL_REVIEW_MIN_SCORE,
                "tessl_review_target_score": TESSL_REVIEW_TARGET_SCORE,
                "tessl_review_args": ["skill", "review", "--json", "--threshold", str(TESSL_REVIEW_MIN_SCORE)],
                "tessl_review_staging_root": f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-reviews')}/<skill-path>-<sha12>",
                "tessl_project_marker": "tessl.json",
                "evidence_retention": "stable tmp wrapper is intentionally left for post-run inspection",
            }
        enriched[name] = enriched_profile
    return enriched

__all__ = [name for name in globals() if not name.startswith("__")]
