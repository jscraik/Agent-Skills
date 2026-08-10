from __future__ import annotations

from dataclasses import dataclass

from .skills_impl_capabilities import *  # noqa: F403

@dataclass(frozen=True)
class SkillsDoctorOptions:
    strict: bool = False
    codex_parity: bool = False
    validation_scope: Literal["runtime", "source"] = "runtime"


@dataclass
class _DoctorState:
    """Mutable diagnostic state shared by the small doctor check helpers."""
    query: str
    target_info: dict[str, Any]
    audit_target: str | None
    target_kind: str
    normalized_handle: Any
    source_path_value: Any
    source_path: Path | None
    checks: dict[str, Any]
    blockers: list[dict[str, str]]
    warnings: list[dict[str, str]]


def _new_doctor_state(repo_root: Path, target: str) -> _DoctorState:
    """Resolve the target once and initialise its doctor result collections."""
    query = target.strip()
    target_info, audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path")
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    return _DoctorState(
        query, target_info, audit_target, str(target_info.get("target_kind") or "unknown"),
        target_info.get("handle"), source_path_value, source_path, {}, [], [],
    )


def _doctor_add_resolver_check(state: _DoctorState) -> bool:
    """Record command-handle resolution and return whether it is usable."""
    resolution = state.target_info.get("resolution")
    resolver_pass = isinstance(resolution, dict) and resolution.get("status") == "ok"
    state.checks["resolver"] = _doctor_check(
        _status_from_bool(resolver_pass), check_name="resolver", handle=state.normalized_handle,
        error_code=(resolution or {}).get("error_code") if isinstance(resolution, dict) else None,
        operator_action=(resolution or {}).get("operator_action") if isinstance(resolution, dict) else None,
    )
    if not resolver_pass:
        state.blockers.append(_doctor_blocker(
            "blocked_resolution", f"Could not resolve skill handle '{state.normalized_handle}'.",
        ))
    return resolver_pass


def _doctor_proof_details(proof_result: CallResult) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Normalise the proof and optional runtime-failure fields for doctor output."""
    proof = proof_result.data.get("proof", {})
    proof_data = proof if isinstance(proof, dict) else {}
    failure = proof_data.get("runtime_failure") or proof_result.data.get("runtime_failure")
    return proof_data, failure if isinstance(failure, dict) else None


def _doctor_runtime_reachability_check(
    proof: dict[str, Any], runtime_failure: dict[str, Any] | None, command: str,
    codex_parity: bool, runtime_target: str,
) -> dict[str, Any]:
    """Build the runtime-reachability check payload from normalised proof data."""
    return _doctor_check(
        proof.get("status", "fail"), check_name="runtime_reachability", command=command,
        codex_parity=codex_parity, runtime_target=runtime_target,
        gate_policy=proof.get("gate_policy", {}), gates=proof.get("gates", {}),
        runtime_failure=runtime_failure, error_code=runtime_failure.get("error_code") if runtime_failure else None,
        failed_check_id=runtime_failure.get("failed_check_id") if runtime_failure else None,
        path=runtime_failure.get("path") if runtime_failure else None,
        recovery_guidance=runtime_failure.get("recovery_guidance") if runtime_failure else None,
    )


def _doctor_add_runtime_proof(state: _DoctorState, repo_root: Path, codex_parity: bool) -> None:
    """Run the handle-based runtime proof and record its detailed failure data."""
    runtime_target = "codex" if codex_parity else "any"
    proof_result = skills_proof(repo_root, str(state.normalized_handle), runtime_target=runtime_target)
    proof, runtime_failure = _doctor_proof_details(proof_result)
    command_args = [str(state.normalized_handle), *(["--runtime-target", "codex"] if codex_parity else [])]
    state.checks["runtime_reachability"] = _doctor_runtime_reachability_check(
        proof, runtime_failure, _skills_validation_command("proof", *command_args), codex_parity, runtime_target,
    )
    if proof_result.status != "success":
        state.blockers.append(_doctor_blocker("blocked_runtime", f"Runtime reachability proof failed for '{state.normalized_handle}'."))


def _doctor_add_path_runtime_check(state: _DoctorState, codex_parity: bool) -> None:
    """Record the explicit no-handle boundary for source-path doctor targets."""
    state.checks["resolver"] = _doctor_check(
        "skipped", check_name="resolver", reason="Path targets are audited as canonical source; runtime proof requires a handle.",
    )
    if codex_parity:
        state.checks["runtime_reachability"] = _doctor_check(
            "fail", check_name="runtime_reachability", codex_parity=True, runtime_target="codex",
            reason="Codex parity requires an SDK skill handle so Codex runtime proof can run.",
        )
        state.blockers.append(_doctor_blocker("blocked_runtime", "Codex parity requires an SDK skill handle."))


def _doctor_add_runtime_checks(state: _DoctorState, repo_root: Path, codex_parity: bool) -> None:
    """Dispatch the mutually exclusive runtime checks by resolved target kind."""
    if state.target_kind == "command_handle":
        _doctor_add_resolver_check(state)
        _doctor_add_runtime_proof(state, repo_root, codex_parity)
        return
    _doctor_add_path_runtime_check(state, codex_parity)


def _doctor_add_canonical_source_check(state: _DoctorState) -> bool:
    """Record canonical-source existence and the corresponding missing-source blocker."""
    source_exists = bool(state.target_info.get("source_exists"))
    state.checks["canonical_source"] = _doctor_check(
        _status_from_bool(source_exists), check_name="canonical_source", source_path=state.source_path_value,
    )
    if not source_exists:
        state.blockers.append(_doctor_blocker(
            "blocked_missing_source", f"Canonical source is missing for '{state.query}'.",
        ))
    return source_exists


def _doctor_ownership_paths(state: _DoctorState, repo_root: Path) -> tuple[Any, Any, Any, Any]:
    """Resolve source, target, and projection ownership without applying a verdict."""
    target_path = state.target_info.get("requested_path") or state.target_info.get("target_path")
    owner_path = target_path if state.target_kind != "command_handle" else state.source_path_value
    source = _skill_root_ownership_for_path(str(owner_path) if owner_path else None, repo_root=repo_root)
    target = _skill_root_ownership_for_path(str(target_path), repo_root=repo_root) if target_path and state.target_kind != "command_handle" else source
    projection_path = str(target_path) if target.get("classification") in {"generated_runtime_projection", "client_runtime_config"} else None
    projection = _skill_root_ownership_for_path(projection_path, repo_root=repo_root)
    return target_path, source, target, (projection_path, projection)


def _doctor_ownership_status(state: _DoctorState, target: dict[str, Any], manifest: Any) -> str:
    """Return the ownership check status while adding actionable validation blockers."""
    if manifest.state == "invalid":
        blocker = manifest.blockers[0]
        state.blockers.append(_doctor_blocker(
            "blocked_validation", "Owner-repo skills-sdk.json is present but invalid and cannot be treated as absent: "
            f"{blocker.message} Resolve the manifest blockers before ownership is trusted.",
        ))
        return "fail"
    if target.get("classification") in {"generated_runtime_projection", "client_runtime_config"}:
        state.blockers.append(_doctor_blocker(
            "blocked_validation", f"Doctor target '{state.query}' resolves to {target['classification']}; "
            "edit canonical source or declare the root as canonical_project_source in an owner-repo skills-sdk.json manifest.",
        ))
        return "fail"
    return "pass" if state.target_info.get("source_exists") else "skipped"


def _doctor_add_projection_ownership_check(state: _DoctorState, repo_root: Path) -> None:
    """Record source/projection ownership and enforce project-manifest validity."""
    target_path, source, target, projection_values = _doctor_ownership_paths(state, repo_root)
    projection_path, projection = projection_values
    manifest = _evaluate_project_skills_sdk_manifest(repo_root)
    status = _doctor_ownership_status(state, target, manifest)
    state.checks["projection_ownership"] = _doctor_check(
        status, check_name="projection_ownership", source=source, target=target, target_path=target_path,
        projection=projection, projection_path=projection_path,
        projection_editable=bool(projection.get("editable_source")), owner_manifest_schema=PROJECT_SKILLS_SDK_SCHEMA,
        owner_manifest_state=_manifest_state_summary(manifest),
    )


def _doctor_add_structural_audit(
    state: _DoctorState, repo_root: Path, strict: bool, validation_scope: Literal["runtime", "source"],
) -> None:
    """Run the selected structural audit when a canonical source is available."""
    level = "strict" if strict else "compat"
    if not state.audit_target or not state.target_info.get("source_exists"):
        state.checks["structural_audit"] = _doctor_check(
            "skipped", check_name="structural_audit", level=level, reason="No canonical source target available.",
        )
        return
    audit = audit_skill(repo_root, state.audit_target, level=level, validation_scope=validation_scope)
    diagnostics = audit.data.get("diagnostics", {})
    state.checks["structural_audit"] = _doctor_check(
        "pass" if audit.status == "success" else "fail", check_name="structural_audit", level=level,
        command=_skills_validation_command("audit", state.audit_target, "--level", level),
        diagnostics_exit_code=diagnostics.get("exit_code"),
    )
    if audit.status != "success":
        state.blockers.append(_doctor_blocker(
            "blocked_validation", f"{level} skill audit failed for '{state.audit_target}'.",
        ))


def _doctor_source_material(state: _DoctorState) -> tuple[dict[str, Any], str]:
    """Read available canonical source material for local risk and metadata checks."""
    if not state.source_path or not state.source_path.is_file():
        return {}, ""
    try:
        return _read_skill_frontmatter_fields(state.source_path), state.source_path.read_text(encoding="utf-8")
    except OSError:
        return {}, ""


def _doctor_add_risk_check(state: _DoctorState, frontmatter: dict[str, Any], source_body: str) -> None:
    """Attach the risk classifier result derived from the canonical source."""
    classification = _build_risk_classification(
        state.source_path if state.source_path and state.source_path.exists() else None, frontmatter, source_body,
    )
    state.checks["risk_classification"] = _doctor_check(
        "pass", check_name="risk_classification", classification=classification,
        sensor_ids=classification["sensor_ids"], risk_tier=classification["risk_tier"],
        source_kind=classification["source_kind"], blocking_behavior=classification["blocking_behavior"],
        receipt_required=classification["receipt_required"],
    )


def _doctor_add_metadata_check(state: _DoctorState, frontmatter: dict[str, Any]) -> None:
    """Attach capability and package-metadata readiness checks and warnings."""
    metadata = _capability_metadata_status(frontmatter)
    metadata.setdefault("sdk_layer", _doctor_sdk_layer_for("check", "capability_metadata"))
    state.checks["capability_metadata"] = metadata
    if metadata["status"] == "warning":
        state.warnings.append(_doctor_warning("metadata_incomplete", "Recommended frontmatter fields are incomplete."))
    package = metadata.get("package_readiness", {})
    missing = package.get("required_fields", {}).get("missing") if isinstance(package, dict) else None
    status = "warning" if missing else "pass"
    if missing:
        state.warnings.append(_doctor_warning("capability_contract_incomplete", "Package/share readiness metadata is incomplete."))
    state.checks["package_readiness"] = _doctor_check(
        status, check_name="package_readiness", package_readiness=package,
        required_fields=package.get("required_fields", {}) if isinstance(package, dict) else {},
        install_gate=package.get("install_gate", {}) if isinstance(package, dict) else {},
        promotion_gate=package.get("promotion_gate", {}) if isinstance(package, dict) else {},
    )


def _doctor_add_outcome_proof(state: _DoctorState, repo_root: Path) -> None:
    """Attach available outcome-proof evidence and its missing-evidence warning."""
    handle = str(state.normalized_handle or (Path(state.audit_target).name if state.audit_target else "")).strip()
    workouts = _skill_workout_candidates(repo_root, handle) if handle else []
    proof = _eval_shard_outcome_proof(repo_root, handle) if handle else {"status": "missing", "evidence_class": "outcome_proof"}
    proof_status = str(proof.get("status") or "missing")
    status = "pass" if proof_status == "pass" else ("available_not_run" if workouts else "missing")
    state.checks["outcome_proof"] = _doctor_check(
        status, check_name="outcome_proof", workout_candidates=workouts,
        evidence_class=proof.get("evidence_class", "outcome_proof"), evidence_ref=proof.get("evidence_ref"),
        evidence_digest=proof.get("evidence_digest"), scenario_set=proof.get("scenario_set"), case_count=proof.get("case_count"),
    )
    if proof_status != "pass" and not workouts:
        state.warnings.append(_doctor_warning("outcome_proof_missing", "No matching workout was found for this capability."))


def _doctor_status(state: _DoctorState) -> str:
    """Derive the single doctor verdict from accumulated blockers and warnings."""
    return "blocked" if state.blockers else ("warning" if state.warnings else "pass")


def _doctor_next_command_decision(state: _DoctorState, strict: bool) -> dict[str, Any]:
    """Select the next canonical command after the completed doctor checks."""
    return _skill_doctor_next_command_decision(
        blockers=state.blockers, warnings=state.warnings, checks=state.checks,
        normalized_handle=state.normalized_handle, query=state.query, audit_target=state.audit_target, strict=strict,
    )


def _doctor_agent_summary(state: _DoctorState, status: str) -> str:
    """Render a compact human outcome from the collected doctor state."""
    label = str(state.normalized_handle) if state.normalized_handle else state.query
    if status == "blocked":
        return f"{label} is blocked: {state.blockers[0]['message']}"
    if status == "warning":
        return f"{label} is usable with {len(state.warnings)} readiness warning(s)."
    return f"{label} passed capability doctor checks."


def _doctor_result_payload(state: _DoctorState, status: str, decision: dict[str, Any]) -> dict[str, Any]:
    """Build the stable doctor payload from completed checks and selected next action."""
    lifecycle_event = _capability_lifecycle_event(
        event_type="skill_doctor_completed", query=state.query, target_kind=state.target_kind,
        handle=state.normalized_handle, source_path=state.source_path_value, audit_target=state.audit_target,
        status=status, blockers=state.blockers, warnings=state.warnings,
    )
    return {
        "schema_version": "skill-doctor.v1", "query": state.query, "target_kind": state.target_kind,
        "handle": state.normalized_handle, "canonical_source_path": state.source_path_value,
        "audit_target": state.audit_target,
        "target_summary": _skill_target_summary(query=state.query, target_kind=state.target_kind, handle=state.normalized_handle, source_path=state.source_path_value, audit_target=state.audit_target),
        "status": status, "blockers": state.blockers, "warnings": state.warnings,
        "readiness_taxonomy": {"blockers": DOCTOR_BLOCKER_TAXONOMY, "warnings": DOCTOR_WARNING_TAXONOMY},
        "sdk_layers": list(DOCTOR_SDK_LAYERS), "contract_schemas": _doctor_contract_schema_refs(),
        "contract_schema_versions": _doctor_contract_schema_versions(),
        "operation_context": _skill_doctor_operation_context(), "lifecycle_event": lifecycle_event,
        "lifecycle_event_types": dict(CAPABILITY_LIFECYCLE_EVENT_TYPES), "checks": state.checks,
        "check_summary": _skill_doctor_check_summary(state.checks), "agent_summary": _doctor_agent_summary(state, status),
        "next_command": str(decision["command"]), "next_command_decision": decision,
    }


def _apply_doctor_result(result: CallResult, payload: dict[str, Any]) -> None:
    """Attach the doctor payload and preserve its blocker result contract."""
    result.data["skill_doctor"] = payload
    if payload["blockers"]:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION", message=payload["agent_summary"], fix_suggestion=payload["next_command"],
        ))


def _skills_doctor(
    repo_root: Path,
    target: str,
    strict: bool = False,
    codex_parity: bool = False,
    validation_scope: Literal["runtime", "source"] = "runtime",
) -> CallResult:
    """Run a compact per-capability diagnostic for a skill handle or source path."""
    result = CallResult()
    result.metadata["command"] = "skills doctor"
    state = _new_doctor_state(repo_root, target)
    _doctor_add_runtime_checks(state, repo_root, codex_parity)
    _doctor_add_canonical_source_check(state)
    _doctor_add_projection_ownership_check(state, repo_root)
    _doctor_add_structural_audit(state, repo_root, strict, validation_scope)
    frontmatter, source_body = _doctor_source_material(state)
    _doctor_add_risk_check(state, frontmatter, source_body)
    _doctor_add_metadata_check(state, frontmatter)
    _doctor_add_outcome_proof(state, repo_root)
    status = _doctor_status(state)
    decision = _doctor_next_command_decision(state, strict)
    _apply_doctor_result(result, _doctor_result_payload(state, status, decision))
    return result


def skills_doctor(
    repo_root: Path,
    target: str,
    options: SkillsDoctorOptions | None = None,
    **legacy_options: object,
) -> CallResult:
    """Run skill doctor from typed options, retaining legacy keywords during migration."""
    if options is not None and legacy_options:
        raise TypeError("pass either SkillsDoctorOptions or legacy keyword arguments, not both")
    resolved = options or SkillsDoctorOptions(**legacy_options)
    return _skills_doctor(
        repo_root,
        target,
        strict=resolved.strict,
        codex_parity=resolved.codex_parity,
        validation_scope=resolved.validation_scope,
    )


def _skills_sdk_check_status(doctor: object) -> tuple[str | None, dict[str, Any], str, str]:
    """Classify the doctor result for the SDK-check receipt without changing it."""
    doctor_data = doctor if isinstance(doctor, dict) else {}
    doctor_status = doctor_data.get("status")
    blockers = doctor_data.get("blockers", [])
    first_blocker = blockers[0] if blockers and isinstance(blockers[0], dict) else {}
    status = "blocked" if doctor_status == "blocked" else "pass"
    if doctor_status not in {"pass", "warning", "blocked"}:
        status = "degraded"
    failure_class = "validation_failed" if status in {"blocked", "degraded"} else "none"
    return doctor_status, first_blocker, status, failure_class


def _skills_sdk_check_commands(target: str, strict: bool, codex_parity: bool) -> tuple[str, str]:
    """Return doctor and public-facade replay commands for the selected options."""
    suffixes = (["--strict"] if strict else []) + (["--codex-parity"] if codex_parity else [])
    return (
        _skills_validation_command("doctor", target, *suffixes),
        _ask_validation_command("sdk", "check", target, *suffixes),
    )


def _skills_sdk_check_receipt(status: str, result_status: str, replay_command: str) -> dict[str, Any]:
    """Build the immutable receipt portion of an SDK-check response."""
    return {
        "schema_version": "skills-sdk.check-receipt.v1",
        "schema_uri": "https://agent-skills.local/schemas/skills-sdk/check-receipt.v1.schema.json",
        "command": "skills-sdk check", "command_version": "skills-sdk.v1", "status": status,
        "failure_class": "validation_failed" if status in {"blocked", "degraded"} else "none",
        "exit_code": 0 if result_status == "success" else 2, "work_mode": "computational",
        "proof": {"type": "command_output", "evidence_kind": "receipt", "evidence_ref": replay_command},
        "sensor": {"id": "skills-sdk.check.facade", "placement": "preflight", "required": True},
        "actor": {"role": "agent"}, "approval_decision": "not_required", "redaction": "not_applicable",
        "acceptance_trace": ["FR-008", "FR-009", "SA-004", "SA-005", "VP-002"],
    }


def _skills_sdk_check_payload(
    target: str, doctor: object, status: str, failure_class: str, first_blocker: dict[str, Any],
    doctor_command: str, replay_command: str, result_status: str,
) -> dict[str, Any]:
    """Build the public SDK-check report from the canonical doctor result."""
    doctor_data = doctor if isinstance(doctor, dict) else {}
    doctor_status = doctor_data.get("status")
    next_command = (
        str(doctor_data.get("next_command") or doctor_command)
        if status in {"blocked", "degraded"}
        else _ask_validation_command("skills", "package", "verify", target, "--strict")
    )
    summary = _skills_sdk_check_summary(target, status, doctor_status, first_blocker)
    return {
        "schema_version": "skills-sdk-check.v1", "query": target, "status": status,
        "failure_class": failure_class, "doctor_status": doctor_status,
        "canonical_source_path": doctor_data.get("canonical_source_path"),
        "canonical_command": replay_command, "facade_command": "skills-sdk check",
        "receipt": _skills_sdk_check_receipt(status, result_status, replay_command),
        "agent_summary": summary, "validation_commands": [replay_command, doctor_command],
        "next_command": next_command,
        "claims_boundary": "This checks local source readiness; it does not prove package readiness, runtime reachability, task outcome, publication, or release readiness.",
    }


def _skills_sdk_check_summary(
    target: str, status: str, doctor_status: object, first_blocker: dict[str, Any],
) -> str:
    """Render the status-specific SDK-check summary without changing its payload fields."""
    if status == "blocked":
        return f"skills-sdk check blocked for {target}: {first_blocker.get('message')}"
    if status == "degraded":
        return f"skills-sdk check is degraded for {target}: doctor status '{doctor_status}' is not a recognized verdict."
    return f"skills-sdk check passed for {target}."


def _skills_sdk_check(
    repo_root: Path,
    target: str,
    strict: bool = False,
    codex_parity: bool = False,
) -> CallResult:
    """Run the Skills SDK check facade through the canonical skills doctor."""
    result = skills_doctor(
        repo_root,
        target=target,
        strict=strict,
        codex_parity=codex_parity,
        validation_scope="source",
    )
    doctor = result.data.pop("skill_doctor", {})
    doctor_status, first_blocker, status, failure_class = _skills_sdk_check_status(doctor)
    doctor_command, replay_command = _skills_sdk_check_commands(target, strict, codex_parity)
    result.metadata["command"] = "sdk check"
    result.data["skills_sdk_check"] = _skills_sdk_check_payload(
        target, doctor, status, failure_class, first_blocker, doctor_command, replay_command, result.status,
    )
    return result


def skills_sdk_check(
    repo_root: Path,
    target: str,
    options: SkillsDoctorOptions | None = None,
    **legacy_options: object,
) -> CallResult:
    """Run the SDK check using the same typed options as doctor."""
    if options is not None and legacy_options:
        raise TypeError("pass either SkillsDoctorOptions or legacy keyword arguments, not both")
    resolved = options or SkillsDoctorOptions(**legacy_options)
    return _skills_sdk_check(
        repo_root,
        target,
        strict=resolved.strict,
        codex_parity=resolved.codex_parity,
    )


SDK_PIPELINE_START_SCHEMA_VERSION = "skills-sdk.pipeline-start.v1"
SDK_PIPELINE_START_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/pipeline-start.v1.schema.json"
def _sdk_start_target_class(target_info: dict[str, Any], ownership: dict[str, Any]) -> str:
    if target_info.get("target_kind") == "project_local_source_path":
        return "project_local_skill"
    if ownership.get("owner_kind") == "plugin_skills":
        return "plugin_owned_skill"
    if ownership.get("owner_kind") == "repo_skills":
        return "global_skill"
    if ownership.get("classification") in {"generated_runtime_projection", "client_runtime_config"}:
        return "runtime_projection"
    if target_info.get("target_kind") == "command_handle":
        return "global_skill"
    return "unknown"


def _sdk_start_repo_relative_source(repo_root: Path, source_path_value: Any) -> str | None:
    if not isinstance(source_path_value, str) or not source_path_value.strip():
        return None
    source_path = Path(source_path_value)
    if not source_path.is_absolute():
        return source_path.as_posix()
    return _repo_relative_path(repo_root, source_path)


def _sdk_start_status(source_exists: bool, target_class: str) -> tuple[str, list[str]]:
    allowed = {"project_local_skill", "plugin_owned_skill", "global_skill"}
    if source_exists and target_class in allowed:
        return "pass", []
    blocker = "runtime_projection_not_canonical_source" if target_class == "runtime_projection" else "missing_or_unclassified_skill_source"
    return "blocked", [blocker]


def _sdk_start_local_receipt(
    query: str,
    source_path: str | None,
    target_class: str,
    status: str,
    blockers: list[str],
) -> dict[str, Any]:
    """Build the compact default result for the local author journey."""
    next_command = _ask_validation_command("sdk", "check", query)
    return {
        "schema_version": SDK_PIPELINE_START_SCHEMA_VERSION,
        "schema_uri": SDK_PIPELINE_START_SCHEMA_URI,
        "status": status,
        "target": query,
        "target_class": target_class,
        "source_path": source_path,
        "current_lane": "local_check" if status == "pass" else "target_classification",
        "lanes": [
            {
                "id": "local_check",
                "status": "required_not_run",
                "command": next_command,
            }
        ],
        "next_action": {
            "lane": "local_check",
            "command": next_command,
            "why": "Check the resolved local source before package verification or proof.",
        },
        "blocked_downstream_lanes": [],
        "blockers": blockers,
        "what_this_proves": (
            "The named target resolves to a canonical local skill source."
            if status == "pass"
            else "The named target could not be resolved to a canonical local skill source."
        ),
        "what_this_does_not_prove": "Structural validity, package readiness, runtime reachability, and outcome proof have not run.",
    }


def skills_sdk_start(repo_root: Path, target: str, project_root: str | None = None) -> CallResult:
    """Emit the first SDK lifecycle receipt and next required command."""
    result = CallResult()
    result.metadata["command"] = "sdk start"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_rel = _sdk_start_repo_relative_source(repo_root, source_path_value)
    ownership = _skill_root_ownership_for_path(source_rel, repo_root=repo_root)
    target_class = _sdk_start_target_class(target_info, ownership)
    source_exists = bool(target_info.get("source_exists")) if isinstance(target_info, dict) else False
    status, blockers = _sdk_start_status(source_exists, target_class)
    display_source = source_rel or (str(source_path_value) if source_path_value else None)
    receipt = _sdk_start_local_receipt(query, display_source, target_class, status, blockers)
    result.data["skills_sdk_start"] = {
        "status": status,
        "receipt": receipt,
        "agent_summary": (
            (
                f"{query}: {display_source}; next action: {receipt['next_action']['command']}. "
                "This does not prove structural validity, package readiness, runtime reachability, or outcome proof."
            )
            if status == "pass"
            else (
                f"{query}: source unavailable; blocked before local source resolution. "
                f"Next action: {receipt['next_action']['command']}."
            )
        ),
    }
    if status != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skills SDK start could not classify the target skill source.",
                fix_suggestion=receipt["next_action"]["command"],
            )
        )
    return result


def skills_sdk_install_preview(
    repo_root: Path,
    target: str,
    scope: str = "project",
) -> CallResult:
    """Build a read-only Skills SDK install preview for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk install --preview"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    preview = _build_install_preview(
        repo_root,
        query=query,
        scope=scope,
        source_path=source_path,
        target_info=target_info,
    )
    status = "blocked" if preview["trust_state"] == "blocked" else "preview"
    payload = {
        "schema_version": "skills-sdk-install-preview.v1",
        "query": query,
        "status": status,
        "scope": scope,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk install --preview",
        "preview": preview,
        "receipt": {
            "command": "skills-sdk install --preview",
            "status": status,
            "mutation_performed": False,
            "receipt_ref": preview["receipt_ref"],
        },
        "validation_commands": [
            _ask_validation_command("sdk", "install", query, "--preview", "--scope", scope),
        ],
        "agent_summary": (
            f"skills-sdk install preview is blocked for {query}: canonical source is missing."
            if status == "blocked"
            else f"skills-sdk install preview planned {len(preview['target_paths'])} path(s) for {query} without writes."
        ),
    }
    result.data["skills_sdk_install_preview"] = payload
    if status == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command("sdk", "check", query),
            )
        )
    return result


def skills_sdk_intake_inspect(
    repo_root: Path,
    *,
    source: str,
    source_kind: str = "directory",
) -> CallResult:
    """
    Build a non-mutating intake inspection receipt for an external skill source.

    Parameters:
        source_kind (str): The type of source; defaults to "directory" (also supports "archive").

    Returns:
        CallResult: Contains the intake inspection receipt payload under data["skills_sdk_intake_inspect"]. Status is set to "error" if the receipt status is "blocked".
    """
    result = CallResult()
    result.metadata["command"] = "sdk intake inspect --preview"
    query = source.strip()
    receipt = _build_skill_intake_receipt(repo_root, source=query, source_kind=source_kind)
    payload = {
        "schema_version": "skills-sdk-intake-inspect.v0",
        "query": query,
        "status": receipt["status"],
        "facade_command": "skills-sdk intake inspect --preview",
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "intake",
                "inspect",
                query,
                "--preview",
                "--source-kind",
                source_kind,
            ),
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_intake_inspect"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion="Inspect data.skills_sdk_intake_inspect.receipt.blockers for specific details about path, symlink, or validation issues.",
            )
        )
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
