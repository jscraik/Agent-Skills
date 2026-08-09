from __future__ import annotations

from .repo_impl_core import *  # noqa: F403

def doctor_catalog(repo_root: Path, strict: bool = False) -> CallResult:
    """Run catalog parity diagnostics and expose the full report in a CallResult."""
    result = CallResult()
    report = compute_catalog_parity(repo_root, strict=strict)
    result.data["catalog_parity"] = report
    result.data["decision_status"] = report.get("decision_status")
    result.data["policy_identity"] = report.get("policy_identity")

    drift_detected = report.get("drift_detected")
    if drift_detected is False:
        result.status = "success"
        return result

    if drift_detected is True:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"doctor-catalog detected drift: {report.get('drift_class')}",
                fix_suggestion=report.get("operator_action")
                or "Run sync/projection tooling and rerun doctor-catalog.",
            )
        )
        return result

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_RUNTIME",
            message="doctor-catalog report missing required drift_detected boolean.",
            fix_suggestion="Regenerate catalog parity diagnostics and rerun doctor-catalog.",
        )
    )
    return result


def _error_summary(result: CallResult, fallback: str) -> str:
    if result.errors:
        return result.errors[0].message
    return fallback


def _repo_status_signal(status_result: CallResult) -> dict[str, Any]:
    if status_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(status_result, "Repository status check failed."),
            "source": "repo_status",
            "next_command": _repo_validation_command("status"),
        }
    if not status_result.data.get("is_git"):
        return {
            "state": "block",
            "severity": "blocker",
            "summary": "Repository root is not a git repository.",
            "source": "repo_status",
            "next_command": _repo_validation_command("status"),
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Repository status is readable.",
        "source": "repo_status",
        "details": {
            "repo_root": status_result.data.get("repo_root"),
            "is_git": status_result.data.get("is_git"),
        },
    }


def _projection_sync_signal(status_result: CallResult) -> dict[str, Any]:
    if status_result.status != "success":
        return {
            "state": "skipped",
            "severity": "warning",
            "summary": "Projection sync could not be checked because repo status failed.",
            "source": "repo_status",
            "next_command": _repo_validation_command("status"),
        }
    if not status_result.data.get("is_git"):
        return {
            "state": "skipped",
            "severity": "warning",
            "summary": "Projection sync not checked because the repository root is not a git repository.",
            "source": "repo_status",
            "next_command": _repo_validation_command("status"),
            "details": {"is_git": False},
        }
    return _workspace_projection_signal(
        status_result.data.get("skills_projection_state", "missing"),
        bool(status_result.data.get("skills_synced")),
    )


def _workspace_projection_signal(projection_state: str, skills_synced: bool) -> dict[str, Any]:
    """Render a projection verdict without treating an absent projection as healthy."""
    if skills_synced:
        return {
            "state": "pass", "severity": "info", "summary": "Workspace skill runtime appears synced.",
            "source": "repo_status", "details": {"skills_synced": True, "projection_state": projection_state},
        }
    unmaterialized = projection_state == "unmaterialized_linked_worktree"
    summaries = {
        "corrupt": "Workspace skill runtime projection is corrupted or unreadable.",
        "empty": "Workspace skill runtime projection is present but empty.",
        "unmaterialized_linked_worktree": "Workspace skill runtime is intentionally unmaterialized in this linked worktree.",
    }
    signal: dict[str, Any] = {
        "state": "warn" if unmaterialized else "block",
        "severity": "warning" if unmaterialized else "blocker",
        "summary": summaries.get(projection_state, "Workspace skill runtime does not appear synced."),
        "source": "repo_status",
        "details": {"skills_synced": False, "projection_state": projection_state},
    }
    if unmaterialized:
        signal["details"]["runtime_verification"] = "not_run"
        signal["next_command"] = SKILLS_SYNC_COMMAND
    else:
        signal["next_command"] = SKILLS_SYNC_COMMAND
    return signal


def _ask_bootstrap_signal(repo_root: Path) -> dict[str, Any]:
    proof = run_bootstrap_checks(repo_root, repair=False)
    entrypoint = proof["checks"]["entrypoint_executable"]
    fallback = proof["checks"]["fallback_command"]
    path_discovery = proof["checks"]["path_discovery"]
    shim = proof["checks"]["shim_smoke"]
    details = {
        "status": proof["status"],
        "entrypoint_status": entrypoint.get("status"),
        "entrypoint_path_type": entrypoint.get("path_type"),
        "safe_to_chmod": entrypoint.get("safe_to_chmod"),
        "fallback_status": fallback.get("status"),
        "fallback_defer_to": fallback.get("defer_to"),
        "path_discovery_status": path_discovery.get("status"),
        "resolved_path": path_discovery.get("resolved_path"),
        "shim_status": shim.get("status"),
        "shim_repo_identity_status": shim.get("repo_identity_status"),
        "manual_remediation": proof.get("remediation", {}).get("manual", []),
        "applied_remediation": proof.get("remediation", {}).get("applied", []),
    }
    if entrypoint.get("status") == "fail" or fallback.get("status") == "fail":
        return {
            "state": "block",
            "severity": "blocker",
            "summary": "Ask bootstrap entrypoint or fallback command is not ready.",
            "source": "ask_bootstrap",
            "next_command": "bash scripts/bootstrap-ask.sh --json",
            "details": details,
        }
    if path_discovery.get("status") != "pass" and shim.get("status") == "skipped":
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Ask bootstrap fallback is ready; PATH shim is not configured.",
            "source": "ask_bootstrap",
            "next_command": "bash scripts/bootstrap-ask.sh --json",
            "details": details,
        }
    if shim.get("status") != "pass":
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Ask bootstrap fallback works, but PATH discovery or shim identity is incomplete.",
            "source": "ask_bootstrap",
            "next_command": "bash scripts/bootstrap-ask.sh --json",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Ask bootstrap entrypoint, fallback, and PATH shim are ready.",
        "source": "ask_bootstrap",
        "details": details,
    }


def _catalog_parity_signal(catalog_result: CallResult) -> dict[str, Any]:
    report = catalog_result.data.get("catalog_parity", {})
    if catalog_result.status == "success" and report.get("drift_detected") is False:
        return {
            "state": "pass",
            "severity": "info",
            "summary": "Catalog parity is resolved.",
            "source": "doctor_catalog",
            "details": {
                "decision_status": report.get("decision_status"),
                "canonical_count": report.get("canonical_count"),
                "policy_identity": report.get("policy_identity"),
            },
        }
    if report.get("drift_detected") is True:
        return {
            "state": "block",
            "severity": "blocker",
            "summary": f"Catalog parity drift detected: {report.get('drift_class')}.",
            "source": "doctor_catalog",
            "next_command": _repo_validation_command("doctor-catalog"),
            "details": {
                "decision_status": report.get("decision_status"),
                "drift_class": report.get("drift_class"),
                "operator_action": report.get("operator_action"),
            },
        }
    return {
        "state": "error",
        "severity": "blocker",
        "summary": _error_summary(catalog_result, "Catalog parity check failed."),
        "source": "doctor_catalog",
        "next_command": _repo_validation_command("doctor-catalog"),
    }


def _runtime_budget_signal(runtime_result: CallResult) -> dict[str, Any]:
    report = runtime_result.data.get("runtime_budget", {})
    violations = report.get("violations") or []
    status = report.get("status")
    details = {
        "status": status,
        "default_visible_count": report.get("default_visible_count"),
        "estimated_description_tokens": report.get("estimated_description_tokens"),
        "violation_count": len(violations),
    }
    if runtime_result.status == "success" and status == "pass":
        return {
            "state": "pass",
            "severity": "info",
            "summary": "Runtime budget is within policy.",
            "source": "skills_budget",
            "details": details,
        }
    if violations:
        return {
            "state": "block",
            "severity": "blocker",
            "summary": f"Runtime budget has {len(violations)} policy violation(s).",
            "source": "skills_budget",
            "next_command": "./bin/ask runtime budget --json --robot",
            "details": details,
        }
    if runtime_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(runtime_result, "Runtime budget check failed."),
            "source": "skills_budget",
            "next_command": "./bin/ask runtime budget --json --robot",
            "details": details,
        }
    return {
        "state": "warn",
        "severity": "warning",
        "summary": "Runtime budget returned a non-passing advisory status.",
        "source": "skills_budget",
        "next_command": "./bin/ask runtime budget --json --robot",
        "details": details,
    }


def _sdk_handles_signal(handles_result: CallResult) -> dict[str, Any]:
    report = handles_result.data.get("sdk_handles") or handles_result.data.get("command_surface", {})
    violations = report.get("violations") or []
    details = {
        "status": report.get("status"),
        "handle_count": report.get("handle_count"),
        "violation_count": len(violations),
    }
    if report.get("status") == "pass" and not violations:
        return {
            "state": "pass",
            "severity": "info",
            "summary": "SDK skill handles validate cleanly.",
            "source": "skills_handles",
            "details": details,
        }
    if violations:
        summary = f"SDK handle validation found {len(violations)} violation(s)."
    else:
        summary = _error_summary(handles_result, "SDK handle validation failed.")
    details["failure_code"] = "sdk_handle_validation_failed"
    return {
        "state": "block",
        "severity": "blocker",
        "summary": summary,
        "source": "skills_handles",
        "next_command": SDK_HANDLE_CHECK_COMMAND,
        "details": details,
    }


def _capability_readiness_signal(
    profiles_result: CallResult,
    events_result: CallResult,
) -> dict[str, Any]:
    profiles = profiles_result.data.get("skill_profiles", {})
    events = events_result.data.get("skill_events", {})
    profile_overview = profiles.get("readiness_overview", {})
    event_overview = events.get("readiness_overview", {})
    eval_blocker_classes = sorted(
        set(profiles.get("eval_blocker_classes", {})) | set(events.get("eval_blocker_classes", {}))
    )
    profile_gaps = int(profile_overview.get("contract_gap_count") or 0)
    event_gaps = int(event_overview.get("contract_gap_count") or 0)
    details = {
        "profile_status": profiles.get("status"),
        "profile_contract_status": profile_overview.get("contract_status"),
        "profile_contract_gap_count": profile_gaps,
        "profile_ready_sections": profile_overview.get("ready_contract_sections", []),
        "profile_blocked_sections": profile_overview.get("blocked_contract_sections", []),
        "event_status": events.get("status"),
        "event_contract_status": event_overview.get("contract_status"),
        "event_contract_gap_count": event_gaps,
        "event_ready_sections": event_overview.get("ready_contract_sections", []),
        "event_blocked_sections": event_overview.get("blocked_contract_sections", []),
        "eval_blocker_classes": eval_blocker_classes,
        "eval_blocker_class_count": len(eval_blocker_classes),
    }
    if profiles_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(profiles_result, "Skill profile readiness failed."),
            "source": "skills_profiles",
            "next_command": "./bin/ask skills profiles --json --robot",
            "details": details,
        }
    if events_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(events_result, "Skill lifecycle event readiness failed."),
            "source": "skills_events",
            "next_command": "./bin/ask skills events --json --robot",
            "details": details,
        }
    gap_count = profile_gaps + event_gaps
    if gap_count:
        return {
            "state": "block",
            "severity": "blocker",
            "summary": f"Skill capability readiness has {gap_count} contract gap(s).",
            "source": "skills_profiles+skills_events",
            "next_command": "./bin/ask skills profiles --json --robot",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Skill capability readiness contracts are ready.",
        "source": "skills_profiles+skills_events",
        "details": details,
    }


def _memory_readiness_signal(memory_result: CallResult) -> dict[str, Any]:
    memory = memory_result.data.get("skill_memory", {})
    source_summary = memory.get("source_summary", {})
    entry_summary = memory.get("entry_summary", {})
    entry_count = int(memory.get("entry_count") or 0)
    available_sources = source_summary.get("available_sources", [])
    details = {
        "status": memory.get("status"),
        "schema_version": memory.get("schema_version"),
        "provider_model": memory.get("provider_model"),
        "mode": memory.get("mode"),
        "query": memory.get("query"),
        "entry_count": entry_count,
        "total_count": int(memory.get("total_count") or entry_count),
        "source_count": source_summary.get("source_count", 0),
        "available_sources": available_sources,
        "missing_sources": source_summary.get("missing_sources", []),
        "by_source": entry_summary.get("by_source", {}),
        "by_freshness": entry_summary.get("by_freshness", {}),
        "validation_command": "./bin/ask skills memory search projection --json --robot",
    }
    if memory_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(memory_result, "Skill memory readiness failed."),
            "source": "skills_memory",
            "next_command": "./bin/ask skills memory search projection --json --robot",
            "details": details,
        }
    if not available_sources:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Skill memory provider has no available source roots.",
            "source": "skills_memory",
            "next_command": "./bin/ask skills memory list --json --robot",
            "details": details,
        }
    if entry_count == 0:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Skill memory provider is available but returned no projection evidence.",
            "source": "skills_memory",
            "next_command": "./bin/ask skills memory search projection --json --robot",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Skill memory provider returned searchable readiness evidence.",
        "source": "skills_memory",
        "details": details,
    }


def _package_readiness_signal(package_result: CallResult) -> dict[str, Any]:
    package = package_result.data.get("skill_package", {})
    package_contract = package.get("package_contract", {})
    required_fields = package_contract.get("required_fields", {})
    gate_summary = package.get("gate_summary", {})
    promotion_gate = package_contract.get("promotion_gate", {})
    install_gate = package_contract.get("install_gate", {})
    details = {
        "status": package.get("status"),
        "schema_version": package.get("schema_version"),
        "target": package.get("query"),
        "handle": package.get("handle"),
        "readiness_level": package_contract.get("readiness_level"),
        "present_fields": required_fields.get("present", []),
        "missing_fields": required_fields.get("missing", []),
        "missing_field_count": len(required_fields.get("missing", [])),
        "install_ready": gate_summary.get("install_ready"),
        "promotion_status": gate_summary.get("promotion_status"),
        "promotion_ready": gate_summary.get("promotion_ready"),
        "checkout_test_status": gate_summary.get("checkout_test_status"),
        "blocked_reasons": gate_summary.get("blocked_reasons", []),
        "share_ready": promotion_gate.get("share_ready"),
        "compatible_roles_declared": package_contract.get("role_compatibility", {}).get("declared"),
        "runtime_contract_declared": package_contract.get("runtime_contract", {}).get("declared"),
        "checkout_test_required": install_gate.get("checkout_test", {}).get("required"),
        "validation_command": (
            f"./bin/ask skills package {PACKAGE_READINESS_SENTINEL} "
            "--checkout-test --json --robot"
        ),
    }
    if package_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(package_result, "Skill package readiness failed."),
            "source": "skills_package",
            "next_command": details["validation_command"],
            "details": details,
        }
    if package.get("status") == "blocked":
        return {
            "state": "block",
            "severity": "blocker",
            "summary": package.get("agent_summary") or "Skill package readiness is blocked.",
            "source": "skills_package",
            "next_command": details["validation_command"],
            "details": details,
        }
    if package.get("status") == "warning" or details["blocked_reasons"]:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": package.get("agent_summary") or "Skill package readiness has metadata gaps.",
            "source": "skills_package",
            "next_command": details["validation_command"],
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Skill package readiness contract is ready.",
        "source": "skills_package",
        "details": details,
    }


def _repo_surface_signal(surface_result: CallResult) -> dict[str, Any]:
    report = surface_result.data.get("repo_surface", {})
    summary = report.get("summary", {})
    blocking_findings = summary.get("blocking_findings", 0)
    diagnostic_summary = _repo_surface_diagnostic_summary(summary)
    details = {
        "status": report.get("status"),
        "total_paths": summary.get("total_paths"),
        "blocking_findings": blocking_findings,
        "counts_by_code": summary.get("counts_by_code", {}),
        "blocking_counts_by_code": summary.get("blocking_counts_by_code", {}),
        "blocking_counts_by_classification": summary.get("blocking_counts_by_classification", {}),
        "diagnostic_summary": diagnostic_summary,
    }
    if surface_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(surface_result, "Repo surface inventory failed."),
            "source": "repo_surface",
            "next_command": _repo_validation_command("surface"),
            "details": details,
        }
    if report.get("status") == "warning" or blocking_findings:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": _repo_surface_warning_summary(blocking_findings, diagnostic_summary),
            "source": "repo_surface",
            "next_command": _repo_validation_command("surface"),
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Repo surface inventory has no diagnostic debt.",
        "source": "repo_surface",
        "details": details,
    }


def _top_count_items(counts: dict[str, Any], *, limit: int = 3) -> list[dict[str, int]]:
    normalized: list[dict[str, int]] = []
    for code, count in counts.items():
        if isinstance(code, str) and isinstance(count, int) and count > 0:
            normalized.append({"code": code, "count": count})
    return sorted(normalized, key=lambda item: (-item["count"], item["code"]))[:limit]


def _repo_surface_diagnostic_summary(summary: dict[str, Any]) -> dict[str, Any]:
    blocking_counts = summary.get("blocking_counts_by_code", {})
    if not isinstance(blocking_counts, dict) or not blocking_counts:
        blocking_counts = summary.get("counts_by_code", {})
    if not isinstance(blocking_counts, dict):
        blocking_counts = {}
    top_codes = _top_count_items(blocking_counts)
    return {
        "diagnostic_class": "repo_surface_ownership_debt",
        "top_blocking_codes": top_codes,
        "next_action": "classify_allowlist_or_cleanup_tracked_surface",
        "operator_rule": (
            "Do not flatten high-count repo-surface findings into generic "
            "nonblocking debt; report dominant categories, owner decision, "
            "and the next classification command."
        ),
    }


def _repo_surface_warning_summary(blocking_findings: int, diagnostic_summary: dict[str, Any]) -> str:
    top_codes = diagnostic_summary.get("top_blocking_codes", [])
    if isinstance(top_codes, list) and top_codes:
        formatted = ", ".join(
            f"{item['code']}={item['count']}"
            for item in top_codes
            if isinstance(item, dict) and item.get("code") and item.get("count")
        )
        if formatted:
            return (
                f"Repo surface has {blocking_findings} ownership diagnostic finding(s); "
                f"top categories: {formatted}."
            )
    return f"Repo surface has {blocking_findings} ownership diagnostic finding(s)."


def _unknown_signal_error_signal(exc: Exception) -> dict[str, Any]:
    return {
        "state": "error",
        "severity": "blocker",
        "summary": f"Repo doctor failed while composing signals: {type(exc).__name__}.",
        "source": "repo_doctor",
        "next_command": _repo_validation_command("status"),
        "details": {
            "error_type": type(exc).__name__,
        },
    }


def _skipped_signal(summary: str, source: str) -> dict[str, Any]:
    return {
        "state": "skipped",
        "severity": "info",
        "summary": summary,
        "source": source,
    }


def _repo_status_skipped_downstream_signals(reason: str) -> dict[str, dict[str, Any]]:
    sdk_handles = _skipped_signal(
        f"SDK handle validation skipped {reason}.",
        "repo_status",
    )
    return {
        "catalog_parity": _skipped_signal(
            f"Catalog parity skipped {reason}.",
            "repo_status",
        ),
        "runtime_budget": _skipped_signal(
            f"Runtime budget skipped {reason}.",
            "repo_status",
        ),
        "sdk_handles": sdk_handles,
        "command_handles": sdk_handles,
        "capability_readiness": _skipped_signal(
            f"Capability readiness skipped {reason}.",
            "repo_status",
        ),
        "memory_readiness": _skipped_signal(
            f"Memory readiness skipped {reason}.",
            "repo_status",
        ),
        "package_readiness": _skipped_signal(
            f"Package readiness skipped {reason}.",
            "repo_status",
        ),
        "repo_surface": _skipped_signal(
            f"Repo surface inventory skipped {reason}.",
            "repo_status",
        ),
    }


def _safe_signal(builder: Any, *args: Any) -> dict[str, Any]:
    try:
        return builder(*args)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
        return _unknown_signal_error_signal(exc)


def _projection_skip_reason(signal_state: str | None, projection_state: str | None) -> str | None:
    if signal_state == "block":
        return "until workspace skill runtime projection is synced"
    if projection_state == "unmaterialized_linked_worktree":
        return "because this linked worktree intentionally has no runtime projection"
    return None


def repo_doctor(repo_root: Path) -> CallResult:
    """Compose repo health checks into one compact agent-facing doctor payload."""
    result = CallResult()
    try:
        status_result = repo_status(repo_root)
    except Exception as exc:
        signals = {
            "repo_status": _unknown_signal_error_signal(exc),
            "ask_bootstrap": _skipped_signal(
                "Ask bootstrap skipped because repository status failed.",
                "repo_status",
            ),
            "projection_sync": _skipped_signal(
                "Projection sync skipped because repository status failed.",
                "repo_status",
            ),
            **_repo_status_skipped_downstream_signals(
                "because repository status failed"
            ),
        }
    else:
        repo_status_signal = _safe_signal(_repo_status_signal, status_result)
        projection_sync_signal = _safe_signal(_projection_sync_signal, status_result)
        ask_bootstrap_signal = _safe_signal(_ask_bootstrap_signal, repo_root)
        signals = {
            "repo_status": repo_status_signal,
            "ask_bootstrap": ask_bootstrap_signal,
            "projection_sync": projection_sync_signal,
        }
        if repo_status_signal.get("state") in {"block", "error"}:
            signals.update(
                _repo_status_skipped_downstream_signals(
                    "until repository status is ready"
                )
            )
        elif skip_reason := _projection_skip_reason(
            projection_sync_signal.get("state"), status_result.data.get("skills_projection_state")
        ):
            signals.update(_repo_status_skipped_downstream_signals(skip_reason))
        else:
            sdk_handles_signal = _safe_signal(
                lambda: _sdk_handles_signal(
                    skills_handles(
                        repo_root,
                        check=True,
                        include_handles=False,
                    )
                )
            )
            signals.update(
                {
                    "catalog_parity": _safe_signal(
                        lambda: _catalog_parity_signal(doctor_catalog(repo_root))
                    ),
                    "runtime_budget": _safe_signal(
                        lambda: _runtime_budget_signal(skills_budget(repo_root))
                    ),
                    "sdk_handles": sdk_handles_signal,
                    "command_handles": sdk_handles_signal,
                    "capability_readiness": _safe_signal(
                        lambda: _capability_readiness_signal(
                            skills_profiles(repo_root),
                            skills_events(repo_root),
                        )
                    ),
                    "memory_readiness": _safe_signal(
                        lambda: _memory_readiness_signal(
                            skills_memory(repo_root, "search", query="projection", limit=3)
                        )
                    ),
                    "package_readiness": _safe_signal(
                        lambda: _package_readiness_signal(
                            skills_package(
                                repo_root,
                                PACKAGE_READINESS_SENTINEL,
                                checkout_test=True,
                            )
                        )
                    ),
                    "repo_surface": _safe_signal(
                        lambda: _repo_surface_signal(repo_surface(repo_root))
                    ),
                }
            )
    golden_path_signals = dict(signals)
    if "command_handles" in golden_path_signals:
        golden_path_signals.pop("sdk_handles", None)
    payload = build_golden_path_payload(
        signals=golden_path_signals,
        normal_next_command=_repo_validation_command("status"),
        signal_priorities=DOCTOR_SIGNAL_PRIORITY,
    )
    payload["signals"] = signals
    result.data["doctor"] = payload
    result.data.update(payload)
    result.status = "error" if payload["blocking"] else "success"
    if payload["blocking"]:
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=payload["agent_summary"],
                fix_suggestion=payload.get("next_command"),
            )
        )
    return result
__all__ = [name for name in globals() if not name.startswith("__")]
