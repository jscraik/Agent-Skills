from __future__ import annotations

from .skills_impl_capabilities import *  # noqa: F403

def skills_doctor(
    repo_root: Path,
    target: str,
    strict: bool = False,
    codex_parity: bool = False,
    validation_scope: Literal["runtime", "source"] = "runtime",
) -> CallResult:
    """Run a compact per-capability diagnostic for a skill handle or source path."""
    result = CallResult()
    result.metadata["command"] = "skills doctor"
    query = target.strip()
    target_info, audit_target = _resolve_doctor_target(repo_root, query)
    target_kind = str(target_info.get("target_kind") or "unknown")
    normalized_handle = target_info.get("handle")
    source_path_value = target_info.get("source_path")
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    checks: dict[str, Any] = {}
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    resolution = target_info.get("resolution")
    if target_kind == "command_handle":
        resolver_pass = isinstance(resolution, dict) and resolution.get("status") == "ok"
        checks["resolver"] = _doctor_check(
            _status_from_bool(resolver_pass),
            check_name="resolver",
            handle=normalized_handle,
            error_code=(resolution or {}).get("error_code") if isinstance(resolution, dict) else None,
            operator_action=(resolution or {}).get("operator_action") if isinstance(resolution, dict) else None,
        )
        if not resolver_pass:
            blockers.append(
                _doctor_blocker(
                    "blocked_resolution",
                    f"Could not resolve skill handle '{normalized_handle}'.",
                )
            )

        proof_runtime_target = "codex" if codex_parity else "any"
        proof_result = skills_proof(repo_root, str(normalized_handle), runtime_target=proof_runtime_target)
        proof = proof_result.data.get("proof", {})
        runtime_failure = (
            proof.get("runtime_failure")
            if isinstance(proof, dict) and isinstance(proof.get("runtime_failure"), dict)
            else proof_result.data.get("runtime_failure")
        )
        proof_command_args = [str(normalized_handle)]
        if codex_parity:
            proof_command_args.extend(["--runtime-target", "codex"])
        checks["runtime_reachability"] = _doctor_check(
            proof.get("status", "fail") if isinstance(proof, dict) else "fail",
            check_name="runtime_reachability",
            command=_skills_validation_command("proof", *proof_command_args),
            codex_parity=codex_parity,
            runtime_target=proof_runtime_target,
            gate_policy=proof.get("gate_policy", {}) if isinstance(proof, dict) else {},
            gates=proof.get("gates", {}) if isinstance(proof, dict) else {},
            runtime_failure=runtime_failure if isinstance(runtime_failure, dict) else None,
            error_code=runtime_failure.get("error_code") if isinstance(runtime_failure, dict) else None,
            failed_check_id=runtime_failure.get("failed_check_id") if isinstance(runtime_failure, dict) else None,
            path=runtime_failure.get("path") if isinstance(runtime_failure, dict) else None,
            recovery_guidance=runtime_failure.get("recovery_guidance") if isinstance(runtime_failure, dict) else None,
        )
        if proof_result.status != "success":
            blockers.append(
                _doctor_blocker(
                    "blocked_runtime",
                    f"Runtime reachability proof failed for '{normalized_handle}'.",
                )
            )
    else:
        checks["resolver"] = _doctor_check(
            "skipped",
            check_name="resolver",
            reason="Path targets are audited as canonical source; runtime proof requires a handle.",
        )
        if codex_parity:
            checks["runtime_reachability"] = _doctor_check(
                "fail",
                check_name="runtime_reachability",
                codex_parity=True,
                runtime_target="codex",
                reason="Codex parity requires an SDK skill handle so Codex runtime proof can run.",
            )
            blockers.append(
                _doctor_blocker(
                    "blocked_runtime",
                    "Codex parity requires an SDK skill handle.",
                )
            )

    source_exists = bool(target_info.get("source_exists"))
    checks["canonical_source"] = _doctor_check(
        _status_from_bool(source_exists),
        check_name="canonical_source",
        source_path=source_path_value,
    )
    if not source_exists:
        blockers.append(
            _doctor_blocker(
                "blocked_missing_source",
                f"Canonical source is missing for '{query}'.",
            )
        )

    projection_path_value = None
    target_path_value = target_info.get("requested_path") or target_info.get("target_path")
    ownership_source_path = target_path_value if target_kind != "command_handle" else source_path_value
    source_ownership = _skill_root_ownership_for_path(
        str(ownership_source_path) if ownership_source_path else None,
        repo_root=repo_root,
    )
    target_ownership = (
        _skill_root_ownership_for_path(str(target_path_value), repo_root=repo_root)
        if target_kind != "command_handle" and target_path_value
        else source_ownership
    )
    if (
        target_kind != "command_handle"
        and target_ownership.get("classification")
        in {
            "generated_runtime_projection",
            "client_runtime_config",
        }
    ):
        projection_path_value = str(target_path_value)
    projection_ownership = _skill_root_ownership_for_path(
        str(projection_path_value) if projection_path_value else None,
        repo_root=repo_root,
    )
    manifest_evaluation = _evaluate_project_skills_sdk_manifest(repo_root)
    manifest_state = _manifest_state_summary(manifest_evaluation)
    ownership_status = "pass"
    if manifest_evaluation.state == "invalid":
        ownership_status = "fail"
        first_blocker = manifest_evaluation.blockers[0]
        blockers.append(
            _doctor_blocker(
                "blocked_validation",
                (
                    "Owner-repo skills-sdk.json is present but invalid and cannot be treated as absent: "
                    f"{first_blocker.message} Resolve the manifest blockers before ownership is trusted."
                ),
            )
        )
    elif target_ownership.get("classification") in {
        "generated_runtime_projection",
        "client_runtime_config",
    }:
        ownership_status = "fail"
        blockers.append(
            _doctor_blocker(
                "blocked_validation",
                (
                    f"Doctor target '{query}' resolves to {target_ownership['classification']}; "
                    "edit canonical source or declare the root as canonical_project_source in an owner-repo "
                    "skills-sdk.json manifest."
                ),
            )
        )
    elif not source_exists:
        ownership_status = "skipped"
    checks["projection_ownership"] = _doctor_check(
        ownership_status,
        check_name="projection_ownership",
        source=source_ownership,
        target=target_ownership,
        target_path=target_path_value,
        projection=projection_ownership,
        projection_path=projection_path_value,
        projection_editable=bool(projection_ownership.get("editable_source")),
        owner_manifest_schema=PROJECT_SKILLS_SDK_SCHEMA,
        owner_manifest_state=manifest_state,
    )

    audit_level = "strict" if strict else "compat"
    if audit_target and source_exists:
        audit_result = audit_skill(
            repo_root,
            audit_target,
            level=audit_level,
            validation_scope=validation_scope,
        )
        diagnostics = audit_result.data.get("diagnostics", {})
        checks["structural_audit"] = _doctor_check(
            "pass" if audit_result.status == "success" else "fail",
            check_name="structural_audit",
            level=audit_level,
            command=_skills_validation_command("audit", audit_target, "--level", audit_level),
            diagnostics_exit_code=diagnostics.get("exit_code"),
        )
        if audit_result.status != "success":
            blockers.append(
                _doctor_blocker(
                    "blocked_validation",
                    f"{audit_level} skill audit failed for '{audit_target}'.",
                )
            )
    else:
        checks["structural_audit"] = _doctor_check(
            "skipped",
            check_name="structural_audit",
            level=audit_level,
            reason="No canonical source target available.",
        )

    frontmatter: dict[str, Any] = {}
    source_body = ""
    if source_path and source_path.is_file():
        try:
            frontmatter = _read_skill_frontmatter_fields(source_path)
            source_body = source_path.read_text(encoding="utf-8")
        except OSError:
            frontmatter = {}
            source_body = ""
    risk_classification = _build_risk_classification(
        source_path if source_path and source_path.exists() else None,
        frontmatter,
        source_body,
    )
    checks["risk_classification"] = _doctor_check(
        "pass",
        check_name="risk_classification",
        classification=risk_classification,
        sensor_ids=risk_classification["sensor_ids"],
        risk_tier=risk_classification["risk_tier"],
        source_kind=risk_classification["source_kind"],
        blocking_behavior=risk_classification["blocking_behavior"],
        receipt_required=risk_classification["receipt_required"],
    )
    metadata_status = _capability_metadata_status(frontmatter)
    metadata_status.setdefault("sdk_layer", _doctor_sdk_layer_for("check", "capability_metadata"))
    checks["capability_metadata"] = metadata_status
    if metadata_status["status"] == "warning":
        warnings.append(
            _doctor_warning(
                "metadata_incomplete",
                "Recommended frontmatter fields are incomplete.",
            )
        )
    package_readiness = metadata_status.get("package_readiness", {})
    package_status = "pass"
    if isinstance(package_readiness, dict) and package_readiness.get("required_fields", {}).get("missing"):
        package_status = "warning"
        warnings.append(
            _doctor_warning(
                "capability_contract_incomplete",
                "Package/share readiness metadata is incomplete.",
            )
        )
    checks["package_readiness"] = _doctor_check(
        package_status,
        check_name="package_readiness",
        package_readiness=package_readiness,
        required_fields=package_readiness.get("required_fields", {}) if isinstance(package_readiness, dict) else {},
        install_gate=package_readiness.get("install_gate", {}) if isinstance(package_readiness, dict) else {},
        promotion_gate=package_readiness.get("promotion_gate", {}) if isinstance(package_readiness, dict) else {},
    )

    workout_handle = str(normalized_handle or (Path(audit_target).name if audit_target else "")).strip()
    workouts = _skill_workout_candidates(repo_root, workout_handle) if workout_handle else []
    evaluation_proof = _eval_shard_outcome_proof(repo_root, workout_handle) if workout_handle else {
        "status": "missing",
        "evidence_class": "outcome_proof",
    }
    outcome_proof_status = str(evaluation_proof.get("status") or "missing")
    if outcome_proof_status == "pass":
        doctor_outcome_status = "pass"
    elif workouts:
        doctor_outcome_status = "available_not_run"
    else:
        doctor_outcome_status = "missing"
    checks["outcome_proof"] = _doctor_check(
        doctor_outcome_status,
        check_name="outcome_proof",
        workout_candidates=workouts,
        evidence_class=evaluation_proof.get("evidence_class", "outcome_proof"),
        evidence_ref=evaluation_proof.get("evidence_ref"),
        evidence_digest=evaluation_proof.get("evidence_digest"),
        scenario_set=evaluation_proof.get("scenario_set"),
        case_count=evaluation_proof.get("case_count"),
    )
    if outcome_proof_status != "pass" and not workouts:
        warnings.append(
            _doctor_warning(
                "outcome_proof_missing",
                "No matching workout was found for this capability.",
            )
        )
    doctor_status = "blocked" if blockers else ("warning" if warnings else "pass")
    next_command_decision = _skill_doctor_next_command_decision(
        blockers=blockers,
        warnings=warnings,
        checks=checks,
        normalized_handle=normalized_handle,
        query=query,
        audit_target=audit_target,
        strict=strict,
    )
    next_command = str(next_command_decision["command"])

    handle_label = str(normalized_handle) if normalized_handle else query
    lifecycle_event = _capability_lifecycle_event(
        event_type="skill_doctor_completed",
        query=query,
        target_kind=target_kind,
        handle=normalized_handle,
        source_path=source_path_value,
        audit_target=audit_target,
        status=doctor_status,
        blockers=blockers,
        warnings=warnings,
    )
    result.data["skill_doctor"] = {
        "schema_version": "skill-doctor.v1",
        "query": query,
        "target_kind": target_kind,
        "handle": normalized_handle,
        "canonical_source_path": source_path_value,
        "audit_target": audit_target,
        "target_summary": _skill_target_summary(
            query=query,
            target_kind=target_kind,
            handle=normalized_handle,
            source_path=source_path_value,
            audit_target=audit_target,
        ),
        "status": doctor_status,
        "blockers": blockers,
        "warnings": warnings,
        "readiness_taxonomy": {
            "blockers": DOCTOR_BLOCKER_TAXONOMY,
            "warnings": DOCTOR_WARNING_TAXONOMY,
        },
        "sdk_layers": list(DOCTOR_SDK_LAYERS),
        "contract_schemas": _doctor_contract_schema_refs(),
        "contract_schema_versions": _doctor_contract_schema_versions(),
        "operation_context": _skill_doctor_operation_context(),
        "lifecycle_event": lifecycle_event,
        "lifecycle_event_types": CAPABILITY_LIFECYCLE_EVENT_TYPES,
        "checks": checks,
        "check_summary": _skill_doctor_check_summary(checks),
        "agent_summary": (
            f"{handle_label} is blocked: {blockers[0]['message']}"
            if blockers
            else (
                f"{handle_label} is usable with {len(warnings)} readiness warning(s)."
                if warnings
                else f"{handle_label} passed capability doctor checks."
            )
        ),
        "next_command": next_command,
        "next_command_decision": next_command_decision,
    }
    if blockers:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=result.data["skill_doctor"]["agent_summary"],
                fix_suggestion=next_command,
            )
        )
    return result


def skills_sdk_check(
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
    doctor_status = doctor.get("status") if isinstance(doctor, dict) else None
    blockers = doctor.get("blockers", []) if isinstance(doctor, dict) else []
    first_blocker = blockers[0] if blockers and isinstance(blockers[0], dict) else {}
    status = "blocked" if doctor_status == "blocked" else "pass"
    if doctor_status not in {"pass", "warning", "blocked"}:
        status = "degraded"
    failure_class = "none"
    if status in {"blocked", "degraded"}:
        failure_class = "validation_failed"

    doctor_command_args = [target]
    if strict:
        doctor_command_args.append("--strict")
    if codex_parity:
        doctor_command_args.append("--codex-parity")
    doctor_command = _skills_validation_command("doctor", *doctor_command_args)
    facade_command_parts = ["sdk", "check", target]
    if strict:
        facade_command_parts.append("--strict")
    if codex_parity:
        facade_command_parts.append("--codex-parity")
    facade_replay_command = _ask_validation_command(*facade_command_parts)
    facade_command = "skills-sdk check"
    next_command = (
        str(doctor.get("next_command") or doctor_command)
        if status in {"blocked", "degraded"} and isinstance(doctor, dict)
        else _ask_validation_command("skills", "package", "verify", target, "--strict")
    )
    result.metadata["command"] = "sdk check"
    receipt = {
        "schema_version": "skills-sdk.check-receipt.v1",
        "schema_uri": "https://agent-skills.local/schemas/skills-sdk/check-receipt.v1.schema.json",
        "command": facade_command,
        "command_version": "skills-sdk.v1",
        "status": status,
        "failure_class": failure_class,
        "exit_code": 0 if result.status == "success" else 2,
        "work_mode": "computational",
        "proof": {
            "type": "command_output",
            "evidence_kind": "receipt",
            "evidence_ref": facade_replay_command,
        },
        "sensor": {
            "id": "skills-sdk.check.facade",
            "placement": "preflight",
            "required": True,
        },
        "actor": {"role": "agent"},
        "approval_decision": "not_required",
        "redaction": "not_applicable",
        "acceptance_trace": ["FR-008", "FR-009", "SA-004", "SA-005", "VP-002"],
    }
    payload = {
        "schema_version": "skills-sdk-check.v1",
        "query": target,
        "status": status,
        "failure_class": failure_class,
        "doctor_status": doctor_status,
        "canonical_source_path": doctor.get("canonical_source_path") if isinstance(doctor, dict) else None,
        "canonical_command": facade_replay_command,
        "facade_command": facade_command,
        "receipt": receipt,
        "agent_summary": (
            f"skills-sdk check blocked for {target}: {first_blocker.get('message')}"
            if status == "blocked"
            else (
                f"skills-sdk check is degraded for {target}: doctor status '{doctor_status}' is not a recognized verdict."
                if status == "degraded"
                else f"skills-sdk check passed for {target}."
            )
        ),
        "validation_commands": [
            facade_replay_command,
            doctor_command,
        ],
        "next_command": next_command,
        "claims_boundary": (
            "This checks local source readiness; it does not prove package readiness, runtime reachability, "
            "task outcome, publication, or release readiness."
        ),
    }
    result.data["skills_sdk_check"] = payload
    return result


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
