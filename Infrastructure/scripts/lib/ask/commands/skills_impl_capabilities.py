from __future__ import annotations

from dataclasses import dataclass

from .skills_impl_profile_ops import *  # noqa: F403

def skills_capabilities(repo_root: Path, runtime_target: str = "codex") -> CallResult:
    """Report runtime proof-plane capability discovery for agents."""
    target = normalize_runtime_target(runtime_target)
    supported_targets = [runtime_target for runtime_target in ("any", "codex", "agents") if runtime_target in SUPPORTED_RUNTIME_TARGETS]
    result = CallResult()
    result.metadata["command"] = "skills capabilities"
    if target not in supported_targets:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid runtime target '{target}'.",
                fix_suggestion="Use --runtime-target any, --runtime-target codex, or --runtime-target agents.",
            )
        )
        return result
    preview = build_codex_load_preview(repo_root)
    proof_targets = [runtime_target for runtime_target in ("codex", "agents") if runtime_target in EVIDENCE_RUNTIME_TARGETS] if target == "any" else [target]
    live_runtime_parity = "not_applicable_discovery_only" if target == "any" else "not_claimed"
    blockers = list(preview.get("blocked_checks", []))
    readiness = "discovery_only" if target == "any" else ("partial" if blockers else "available")
    proof_commands = [_skills_validation_command("proof", "HANDLE", "--runtime-target", proof_target) for proof_target in proof_targets]
    artifact_paths = [
        f".harness/evidence/runtime-proof/<handle>/{proof_target}/{artifact_name}"
        for proof_target in proof_targets
        for artifact_name in ("runtime-card.json", "evidence-receipt.json", "artifact-record.json", "probe.json")
    ]
    result.data["capability_discovery"] = {
        "schema_version": "capability-discovery.v1",
        "command": "skills capabilities",
        "runtime_target": target,
        "status": readiness,
        "runtime_target_support": {
            "supported_targets": supported_targets,
            "selected": target,
            "evidence_targets": ["codex", "agents"],
        },
        "evidence_modes": [
            {
                "mode": "source_modeled",
                "status": "available",
                "commands": [
                    _skills_validation_command("codex-preview"),
                    _skills_validation_command("render-preview"),
                    _skills_validation_command("conformance", "run", "--suite", "codex-parity"),
                ],
            },
            {
                "mode": "runtime_evidence",
                "status": "available",
                "commands": [*proof_commands, _ask_validation_command("repo", "closeout", "--changed")],
            },
        ],
        "supported_commands": [
            {"name": f"skills proof ({proof_target})", "command": proof_command}
            for proof_target, proof_command in zip(proof_targets, proof_commands)
        ] + [
            {"name": "skills conformance run", "command": _skills_validation_command("conformance", "run", "--suite", "codex-parity")},
            {"name": "skills codex-preview", "command": _skills_validation_command("codex-preview")},
            {"name": "repo closeout", "command": _ask_validation_command("repo", "closeout", "--changed")},
        ],
        "required_artifacts": artifact_paths,
        "known_limitations": [
            {
                "class": "live_runtime_parity_not_claimed",
                "message": "Capability discovery reports available commands; it does not prove live runtime parity."
                if target == "any"
                else f"Capability discovery reports available commands; it does not prove live {target} runtime parity.",
            },
            {
                "class": "explicit_runtime_required_for_artifacts",
                "message": "Use an explicit runtime target before expecting runtime-card artifacts.",
            }
        ],
        "blocked_checks": blockers,
        "source_basis": preview.get("source_basis"),
        "next_actions": [
            _skills_validation_command("proof", "HANDLE", "--runtime-target", proof_targets[0]),
            _ask_validation_command("repo", "closeout", "--changed"),
        ],
        "truth_boundaries": {
            "capability_discovery": "checked",
            "live_runtime_parity": live_runtime_parity,
            "schema_validation": "not_run_use_validate_runtime_cards",
        },
    }
    return result


def format_capabilities_human(discovery: dict[str, object]) -> list[str]:
    """
    Format a human-readable summary of a capability discovery payload.

    Parses the given discovery mapping for runtime target/status, truth boundaries (e.g. live_runtime_parity),
    available evidence modes, blocked fidelity checks count, and the first next action, then returns a short
    list of one-line summary strings suitable for display.

    Parameters:
        discovery (dict): Capability discovery payload containing keys such as
            'runtime_target', 'status', 'truth_boundaries', 'evidence_modes',
            'blocked_checks', and 'next_actions'.

    Returns:
        list[str]: One-line summary strings describing the capability discovery.
    """
    boundaries = discovery.get("truth_boundaries") if isinstance(discovery.get("truth_boundaries"), dict) else {}
    modes = discovery.get("evidence_modes") if isinstance(discovery.get("evidence_modes"), list) else []
    mode_names = [mode.get("mode") for mode in modes if isinstance(mode, dict) and mode.get("mode")]
    lines = [
        "Skills capabilities: "
        f"target={discovery.get('runtime_target')} status={discovery.get('status')}",
        f"Live runtime parity: {boundaries.get('live_runtime_parity')}",
        f"Evidence modes: {', '.join(mode_names) if mode_names else 'none'}",
    ]
    blocked_checks = discovery.get("blocked_checks") if isinstance(discovery.get("blocked_checks"), list) else []
    if blocked_checks:
        lines.append(f"Blocked fidelity checks: {len(blocked_checks)}")
    next_actions = discovery.get("next_actions") if isinstance(discovery.get("next_actions"), list) else []
    if next_actions:
        lines.append(f"Next: {next_actions[0]}")
    return lines


def format_codex_preview_human(preview: dict[str, object]) -> list[str]:
    """
    Format a Codex preview payload into a list of human-readable summary lines.

    Parameters:
        preview (dict[str, object]): A Codex preview dictionary containing optional keys:
            - "source_basis" (dict): source-derived metadata such as "live_runtime_parity".
            - "commands" (list): list of command descriptor dicts with "name" and "validation_command".
            - "blocked_checks" (list): list of blocked fidelity checks.
            - "status" (str): overall preview status.
            - "not_a_validation_result" (bool): when true, indicates the preview is source-modeled only.

    Returns:
        list[str]: Ordered summary lines including a commands/count/status header, notes about
        source-modeled vs runtime validation, live runtime parity when present, a blocked-checks
        summary when present, and one line per command in the form "- <name>: <validation_command>".
    """
    source_basis = preview.get("source_basis") if isinstance(preview.get("source_basis"), dict) else {}
    commands = preview.get("commands") if isinstance(preview.get("commands"), list) else []
    blocked_checks = preview.get("blocked_checks") if isinstance(preview.get("blocked_checks"), list) else []
    lines = [f"Codex preview commands: {len(commands)} command(s), status={preview.get('status')}"]
    if preview.get("not_a_validation_result"):
        lines.append("Preview basis: source-modeled only; not a runtime validation result")
    if source_basis.get("live_runtime_parity"):
        lines.append(f"Live runtime parity: {source_basis.get('live_runtime_parity')}")
    if blocked_checks:
        lines.append(f"Blocked fidelity checks: {len(blocked_checks)}")
    lines.extend(f"- {command.get('name')}: {command.get('validation_command')}" for command in commands if isinstance(command, dict))
    return lines


def skills_render_preview(repo_root: Path, context_window: int | None = None) -> CallResult:
    """
    Produce a Codex-based render preview payload for the repository.

    Parameters:
        repo_root (Path): Repository root used to discover and model skills.
        context_window (int | None): Optional maximum context window size to use when building the preview; when omitted the default sizing is applied.

    Returns:
        CallResult: A CallResult whose `data["codex_render_preview"]` contains the render preview payload.
    """
    result = CallResult()
    result.metadata["command"] = "skills render-preview"
    result.data["codex_render_preview"] = build_codex_render_preview(repo_root, context_window)
    return result


def skills_config_explain(repo_root: Path) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills config explain"
    result.data["codex_config_explain"] = build_codex_config_explain(repo_root)
    return result


def skills_inject_preview(repo_root: Path, text: str) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills inject-preview"
    result.data["codex_inject_preview"] = build_codex_inject_preview(repo_root, text)
    return result


def skills_implicit_preview(repo_root: Path, command: str, workdir: str | None = None) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills implicit-preview"
    result.data["codex_implicit_preview"] = build_codex_implicit_preview(repo_root, command, workdir)
    return result


def _skill_package_operation_context() -> dict[str, Any]:
    """Return profile and event routing context for package readiness checks."""
    return {
        "primary_profile": "package-review",
        "promotion_profile": "plugin-share",
        "profiles": {
            profile_name: {
                "intent": SKILL_OPERATION_PROFILES[profile_name]["intent"],
                "write_policy": SKILL_OPERATION_PROFILES[profile_name]["write_policy"],
                "required_evidence": SKILL_OPERATION_PROFILES[profile_name]["required_evidence"],
            }
            for profile_name in ("package-review", "plugin-share")
        },
        "events": {
            "package_readiness_checked": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["package_readiness_checked"],
        },
        "validation_commands": [
            "./bin/ask skills package <handle-or-path> --json --robot",
            _skills_validation_command("events", "package_readiness_checked"),
        ],
    }


def _skill_doctor_operation_context() -> dict[str, Any]:
    """Return profile and event routing context for capability doctor checks."""
    return {
        "primary_profile": "authoring",
        "review_profile": "package-review",
        "next_profiles": ["package-review", "eval"],
        "profiles": {
            profile_name: {
                "intent": SKILL_OPERATION_PROFILES[profile_name]["intent"],
                "write_policy": SKILL_OPERATION_PROFILES[profile_name]["write_policy"],
                "required_evidence": SKILL_OPERATION_PROFILES[profile_name]["required_evidence"],
            }
            for profile_name in ("authoring", "package-review", "eval")
        },
        "events": {
            "skill_doctor_completed": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["skill_doctor_completed"],
            "eval_blocked": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["eval_blocked"],
            "eval_completed": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["eval_completed"],
        },
        "follow_up_commands": [
            "./bin/ask skills package <handle-or-path> --json --robot",
            "./bin/ask skills prove <handle> --json --robot",
            _skills_validation_command("events"),
        ],
        "validation_commands": [
            "./bin/ask skills doctor <handle-or-path> --json --robot",
            "./bin/ask skills audit <handle-or-path> --level strict --json --robot",
            _skills_validation_command("events", "skill_doctor_completed"),
        ],
    }


def _resolve_doctor_target(repo_root: Path, target: str) -> tuple[dict[str, Any], str | None]:
    """Resolve a doctor target as either an SDK skill handle or a repo-owned path."""
    query = target.strip()
    looks_like_path = "/" in query or query.endswith(".md") or query.startswith(".")
    if looks_like_path:
        project_target, project_audit_target = _project_local_skill_target(repo_root, query)
        if project_target is not None:
            return project_target, project_audit_target
        target_path, target_path_value = _normalize_skill_target_path(query)
        requested_path_value = Path(query).as_posix()
        resolved_path, path_error = _validate_repo_relative_skill_path(repo_root, query)
        if path_error:
            return {
                "target_kind": "invalid_path",
                "path_error": [error.__dict__ for error in path_error.errors],
            }, None
        assert resolved_path is not None
        source = resolved_path if resolved_path.name == "SKILL.md" else resolved_path / "SKILL.md"
        source_rel = _repo_relative_path(repo_root, source)
        return {
            "target_kind": "canonical_source_path",
            "handle": None,
            "source_path": source_rel,
            "target_path": target_path_value,
            "requested_path": requested_path_value,
            "source_exists": source.is_file(),
            "resolution": None,
        }, Path(source_rel).parent.as_posix() if source_rel else target_path.as_posix()

    resolution = resolve_skill_handle(query.casefold(), repo_root_path=repo_root)
    audit_target = _skill_audit_target(repo_root, resolution) if resolution.get("status") == "ok" else None
    return {
        "target_kind": "command_handle",
        "handle": resolution.get("handle", query.lstrip("$")),
        "source_path": resolution.get("source_path"),
        "source_exists": bool(audit_target and (repo_root / audit_target / "SKILL.md").is_file()),
        "resolution": resolution,
    }, audit_target


@dataclass(frozen=True)
class SkillsPackageOptions:
    strict: bool = False
    checkout_test: bool = False


@dataclass
class _PackageReadinessState:
    query: str
    target_info: dict[str, object]
    audit_target: str | None
    source_path_value: object | None
    source_path: Path | None
    blockers: list[dict[str, str]]
    warnings: list[dict[str, str]]
    package_contract: dict[str, object]
    skill_package_contract: dict[str, object]


def _missing_source_package_contract(repo_root: Path) -> dict[str, object]:
    return {
        "readiness_level": "blocked_missing_source",
        "required_fields": {"present": [], "missing": list(PACKAGE_CONTRACT_FIELDS)},
        "values": {},
        "role_compatibility": {"declared": False, "roles": []},
        "runtime_contract": {"declared": False, "needs": []},
        "install_gate": {
            "install_ready": False,
            "required_checks": list(PACKAGE_CONTRACT_FIELDS),
            "blocked_reasons": list(PACKAGE_CONTRACT_FIELDS),
            "checkout_test": {"required": True, "status": "not_run", "evidence": []},
        },
        "promotion_gate": {
            "status": "blocked_missing_source",
            "promotion_ready": False,
            "share_ready": False,
            "share_readiness": None,
            "checkout_test_status": "not_run",
            "blocked_reasons": list(PACKAGE_CONTRACT_FIELDS),
            "recommended_next_fields": list(PACKAGE_CONTRACT_FIELDS),
        },
        "sdk_contract": _sdk_package_contract(repo_root, None, {}),
    }


def _package_source_path(repo_root: Path, source_path_value: object | None) -> Path | None:
    if not source_path_value:
        return None
    source_path = Path(str(source_path_value))
    return source_path if source_path.is_absolute() else repo_root / source_path


def _missing_source_package_state(
    repo_root: Path,
    query: str,
    target_info: dict[str, object],
    audit_target: str | None,
    source_path_value: object | None,
    source_path: Path | None,
) -> _PackageReadinessState:
    blockers = [_doctor_blocker("blocked_missing_source", f"Canonical source is missing for '{query}'.")]
    return _PackageReadinessState(
        query=query,
        target_info=target_info,
        audit_target=audit_target,
        source_path_value=source_path_value,
        source_path=source_path,
        blockers=blockers,
        warnings=[],
        package_contract=_missing_source_package_contract(repo_root),
        skill_package_contract=_empty_skill_package_contract(),
    )


def _package_source_contracts(
    repo_root: Path,
    source_path: Path,
    strict: bool,
) -> tuple[dict[str, object], dict[str, object], list[dict[str, str]], list[dict[str, str]]]:
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    try:
        frontmatter = _read_skill_frontmatter_fields(source_path)
    except OSError:
        frontmatter = {}
    skill_package_contract = _skill_package_contract(repo_root, source_path, frontmatter)
    package_contract = _skill_package_readiness(frontmatter, repo_root, source_path)
    missing_fields = package_contract["required_fields"]["missing"]
    gate_blockers = package_contract["install_gate"]["blocked_reasons"]
    if gate_blockers:
        warnings.append(
            _doctor_warning(
                "capability_contract_incomplete",
                "Package readiness metadata is incomplete."
                if missing_fields
                else "Package promotion gate is blocked.",
            )
        )
        if strict:
            blocker_message = (
                "Strict package readiness failed; missing package metadata: "
                f"{', '.join(missing_fields)}."
                if missing_fields
                else (
                    "Strict package readiness failed; package gate blockers: "
                    f"{', '.join(gate_blockers)}."
                )
            )
            blockers.append(_doctor_blocker("blocked_validation", blocker_message))
    return package_contract, skill_package_contract, blockers, warnings


def _package_readiness_state(repo_root: Path, target: str, strict: bool) -> _PackageReadinessState:
    query = target.strip()
    target_info, audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path")
    source_path = _package_source_path(repo_root, source_path_value)
    if not source_path or not source_path.is_file():
        return _missing_source_package_state(
            repo_root,
            query,
            target_info,
            audit_target,
            source_path_value,
            source_path,
        )
    package_contract, skill_package_contract, blockers, warnings = _package_source_contracts(
        repo_root,
        source_path,
        strict,
    )
    return _PackageReadinessState(
        query=query,
        target_info=target_info,
        audit_target=audit_target,
        source_path_value=source_path_value,
        source_path=source_path,
        blockers=blockers,
        warnings=warnings,
        package_contract=package_contract,
        skill_package_contract=skill_package_contract,
    )


def _package_readiness_events(
    state: _PackageReadinessState,
    status: str,
    gate_summary: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    event_kwargs = {
        "query": state.query, "target_kind": str(state.target_info.get("target_kind") or "unknown"),
        "handle": state.target_info.get("handle"), "source_path": state.source_path_value,
        "audit_target": state.audit_target, "status": status, "blockers": state.blockers, "warnings": state.warnings,
    }
    lifecycle_event = _capability_lifecycle_event(event_type="skill_loaded", **event_kwargs)
    readiness_event = _capability_lifecycle_event(
        event_type="package_readiness_checked",
        details={"gate_summary": gate_summary},
        **event_kwargs,
    )
    return lifecycle_event, readiness_event


def _package_agent_summary(state: _PackageReadinessState) -> str:
    if state.blockers:
        return f"{state.query} is blocked: {state.blockers[0]['message']}"
    if state.warnings:
        blockers = state.package_contract["install_gate"]["blocked_reasons"]
        if not blockers:
            return f"{state.query} has package gate warnings: {state.warnings[0]['message']}"
        return f"{state.query} has package gate blockers: {', '.join(blockers)}."
    promotion_status = state.package_contract["promotion_gate"]["status"]
    if promotion_status == "ready_pending_checkout":
        return f"{state.query} is package/share ready; run --checkout-test before promotion."
    return f"{state.query} is package/share ready with checkout evidence."


def _package_payload_identity(state: _PackageReadinessState, strict: bool, status: str) -> dict[str, object]:
    target_info = state.target_info
    return {
        "schema_version": SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
        "query": state.query,
        "target_kind": target_info.get("target_kind"),
        "handle": target_info.get("handle"),
        "canonical_source_path": state.source_path_value,
        "audit_target": state.audit_target,
        "target_summary": _skill_target_summary(
            query=state.query,
            target_kind=target_info.get("target_kind"),
            handle=target_info.get("handle"),
            source_path=state.source_path_value,
            audit_target=state.audit_target,
        ),
        "status": status,
        "strict": strict,
    }


def _package_payload_contract_schemas() -> dict[str, object]:
    return {
        "package_schema": {"schema_version": SKILL_PACKAGE_SCHEMA_VERSION, "path": SKILL_PACKAGE_SCHEMA_PATH},
        "package_readiness_schema": {"schema_version": SKILL_PACKAGE_READINESS_SCHEMA_VERSION, "path": SKILL_PACKAGE_READINESS_SCHEMA_PATH},
        "contract_schemas": {
            "package": SKILL_PACKAGE_READINESS_SCHEMA_VERSION, "skill_package": SKILL_PACKAGE_SCHEMA_VERSION,
            "skillflow": SKILLFLOW_SCHEMA_VERSION, "optimization": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
            "events": "skill-events.v1", "lifecycle_event": "capability-lifecycle-event.v1",
            "profiles": "skill-operation-profiles.v1", "doctor": "skill-doctor.v1", "memory": "skill-memory-provider.v1",
        },
        "workflow_schema": {"schema_version": SKILLFLOW_SCHEMA_VERSION, "path": SKILLFLOW_SCHEMA_PATH},
        "optimization_schema": {"schema_version": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION, "path": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH},
    }


def _package_payload_contracts(
    state: _PackageReadinessState,
    gate_summary: dict[str, object],
    readiness_summary: dict[str, object],
) -> dict[str, object]:
    return {
        "compatibility_snapshot": _skill_package_compatibility_snapshot(),
        "skill_package_contract": state.skill_package_contract,
        "package_contract": state.package_contract,
        "gate_summary": gate_summary,
        "readiness_summary": readiness_summary,
        "operation_context": _skill_package_operation_context(),
    }


def _package_readiness_payload(
    state: _PackageReadinessState,
    strict: bool,
    status: str,
    gate_summary: dict[str, object],
    readiness_summary: dict[str, object],
    lifecycle_event: dict[str, object],
    readiness_event: dict[str, object],
) -> dict[str, object]:
    payload = _package_payload_identity(state, strict, status)
    payload.update(_package_payload_contract_schemas())
    payload.update(_package_payload_contracts(state, gate_summary, readiness_summary))
    payload.update({
        "blockers": state.blockers,
        "warnings": state.warnings,
        "lifecycle_event": readiness_event,
        "lifecycle_events": [lifecycle_event, readiness_event],
        "agent_summary": _package_agent_summary(state),
        "next_command": (
            _skills_validation_command("doctor", state.query)
            if state.blockers
            else _skills_validation_command("doctor", state.query, "--strict")
        ),
    })
    return payload


def _apply_package_result(
    result: CallResult,
    payload: dict[str, object],
    state: _PackageReadinessState,
    strict: bool,
) -> None:
    result.data["skill_package"] = payload
    if state.blockers or (strict and state.warnings):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=payload["next_command"],
            )
        )


def _skills_package(
    repo_root: Path,
    target: str,
    strict: bool = False,
    checkout_test: bool = False,
) -> CallResult:
    """Report version and role-aware package readiness for one skill."""
    result = CallResult()
    result.metadata["command"] = "skills package"
    state = _package_readiness_state(repo_root, target, strict)
    if checkout_test:
        state.package_contract["install_gate"]["checkout_test"] = _skill_package_checkout_test(
            repo_root,
            state.source_path,
            state.audit_target,
            state.package_contract,
        )
    _refresh_package_promotion_gate(state.package_contract)
    gate_summary = _skill_package_gate_summary(state.package_contract)
    readiness_summary = _skill_package_readiness_summary(state.package_contract)
    status = "blocked" if state.blockers else ("warning" if state.warnings else "pass")
    lifecycle_event, readiness_event = _package_readiness_events(state, status, gate_summary)
    payload = _package_readiness_payload(
        state,
        strict,
        status,
        gate_summary,
        readiness_summary,
        lifecycle_event,
        readiness_event,
    )
    _apply_package_result(result, payload, state, strict)
    return result


def skills_package(
    repo_root: Path,
    target: str,
    options: SkillsPackageOptions | None = None,
    **legacy_options: object,
) -> CallResult:
    """Report package readiness from typed options, retaining legacy keywords during migration."""
    if options is not None and legacy_options:
        raise TypeError("pass either SkillsPackageOptions or legacy keyword arguments, not both")
    resolved = options or SkillsPackageOptions(**legacy_options)
    return _skills_package(repo_root, target, strict=resolved.strict, checkout_test=resolved.checkout_test)


def skills_package_verify(
    repo_root: Path,
    target: str,
    expected_sha256: str | None = None,
    trusted_provenance: str | None = None,
    rollback_journal: str | None = None,
) -> CallResult:
    """Verify a package candidate without installing, extracting, or mutating runtime roots."""
    result = CallResult()
    result.metadata["command"] = "skills package verify"
    query = target.strip()
    validation_args = ["verify", query]
    if expected_sha256:
        validation_args.extend(["--expected-sha256", expected_sha256])
    if trusted_provenance:
        validation_args.extend(["--trusted-provenance", trusted_provenance])
    if rollback_journal:
        validation_args.extend(["--rollback-journal", rollback_journal])
    validation_command = _skills_validation_command("package", *validation_args)
    target_path = Path(query)
    candidate_path = target_path if target_path.is_absolute() else repo_root / target_path

    trusted_sources = {
        source.strip()
        for source in (trusted_provenance or "").split(",")
        if source.strip()
    } or None
    is_archive_target = candidate_path.name != "SKILL.md" and (
        candidate_path.is_file() or candidate_path.suffix.lower() == ".zip"
    )

    if is_archive_target:
        journal_path = Path(rollback_journal) if rollback_journal else None
        if journal_path and not journal_path.is_absolute():
            journal_path = repo_root / journal_path
        verification = _verify_archive_package(
            candidate_path,
            expected_sha256=expected_sha256,
            trusted_sources=trusted_sources,
            rollback_journal_path=journal_path,
            repo_root=repo_root,
        )
    else:
        source_path: Path | None = None
        if candidate_path.is_dir():
            source_path = candidate_path / "SKILL.md"
        elif candidate_path.is_file() and candidate_path.name == "SKILL.md":
            source_path = candidate_path
        else:
            target_info, _audit_target = _resolve_doctor_target(repo_root, query)
            source_path_value = target_info.get("source_path")
            if source_path_value:
                source_path = Path(str(source_path_value))
                if not source_path.is_absolute():
                    source_path = repo_root / source_path
        if source_path and source_path.is_file():
            verification = _verify_skill_directory(repo_root, source_path, query, trusted_sources=trusted_sources)
        else:
            missing_path = (source_path or candidate_path).as_posix()
            verification = {
                "schema_version": PACKAGE_VERIFY_SCHEMA_VERSION,
                "target_kind": "missing",
                "target_path": missing_path,
                "archive_identity": None,
                "provenance_identity": {"trusted": False, "values": []},
                "rule_results": [
                    {
                        "rule_id": "blocked_missing_artifact",
                        "status": "blocked",
                        "message": "Package verification target did not resolve to a skill source or archive.",
                        "path": missing_path,
                    }
                ],
                "mutation_status": "not_mutated",
                "rollback_hint": "No rollback is required because verification did not install, extract, or mutate runtime roots.",
                "status": "blocked",
            }
    verification = _normalize_package_verification(
        query=query,
        validation_command=validation_command,
        verification=verification,
        strict=False,
    )

    result.data["skill_package_verification"] = verification
    if verification["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=verification["agent_summary"],
                fix_suggestion=verification["next_command"],
            )
        )
    return result


def skills_package_verify_strict(
    repo_root: Path,
    target: str,
    expected_sha256: str | None = None,
    trusted_provenance: str | None = None,
    rollback_journal: str | None = None,
) -> CallResult:
    """Verify a package candidate and enforce strict package readiness."""
    result = skills_package_verify(
        repo_root,
        target,
        expected_sha256=expected_sha256,
        trusted_provenance=trusted_provenance,
        rollback_journal=rollback_journal,
    )
    query = target.strip()
    verification = result.data.get("skill_package_verification")
    if not isinstance(verification, dict):
        return result
    if verification.get("target_kind") == "skill_directory":
        verification = _apply_strict_package_readiness(repo_root, query, verification)
    else:
        verification = {
            **verification,
            "strict_package_readiness": {
                "status": "not_applicable",
                "reason": (
                    "Strict package readiness is skill-directory scoped; it did not run for "
                    f"target_kind '{verification.get('target_kind')}'."
                ),
            },
        }
    verification = _normalize_package_verification(
        query=query,
        validation_command=_skills_validation_command("package", "verify", query, "--strict"),
        verification=verification,
        strict=True,
    )
    result.data["skill_package_verification"] = verification
    result.errors = []
    result.status = "success"
    if verification["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=verification["agent_summary"],
                fix_suggestion=verification["next_command"],
            )
        )
    return result


def skills_conformance_run(
    repo_root: Path,
    *,
    suite: str,
    evidence_dir: str,
) -> CallResult:
    """Run deterministic Codex parity conformance checks and write replayable evidence."""
    result = CallResult()
    result.metadata["command"] = "skills conformance run"
    validation_command = _skills_validation_command(
        "conformance",
        "run",
        "--suite",
        suite,
        "--evidence-dir",
        evidence_dir,
    )
    payload = _run_skills_conformance(repo_root, suite=suite, evidence_dir=evidence_dir)
    payload["validation_commands"] = [validation_command]
    payload["agent_summary"] = (
        f"Conformance suite {suite} blocked: {payload['blockers'][0]['message']}"
        if payload.get("blockers")
        else f"Conformance suite {suite} passed with {payload.get('case_count', 0)} fixture cases."
    )
    payload["next_command"] = validation_command
    result.data["skills_conformance"] = payload
    if payload.get("blockers"):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=validation_command,
            )
        )
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
