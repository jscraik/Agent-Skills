from __future__ import annotations

from .skills_impl_sdk_intake import *  # noqa: F403

def skills_sdk_ci_policy_preview(
    repo_root: Path,
    risk_tier: str,
) -> CallResult:
    """Preview required CI checks without inspecting or mutating hosted CI."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk ci policy"
    from ask.skills_sdk.ci_policy_preview import (  # noqa: PLC0415
        CiPolicyPreviewError,
        build_ci_policy_preview_receipt,
    )

    try:
        receipt = build_ci_policy_preview_receipt(risk_tier=risk_tier)
    except CiPolicyPreviewError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-ci-policy-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk ci policy",
        "risk_tier": receipt["risk_tier"],
        "required_checks": receipt["required_checks"],
        "receipt": receipt,
        "live_ci_evidence_attached": False,
        "branch_protection_mutated": False,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "ci", "policy", "--risk-tier", risk_tier, "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_ci_policy_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use a supported SDK risk tier and attach live CI evidence in a separate hosted-check lane.",
            )
        )
    return result


def skills_sdk_security_adapters_preview(repo_root: Path) -> CallResult:
    """Discover configured local security adapters without executing scanners."""
    result = CallResult()
    result.metadata["command"] = "sdk security adapters"
    from ask.skills_sdk.security_adapter_discovery import (  # noqa: PLC0415
        SecurityAdapterDiscoveryError,
        build_security_adapter_discovery_receipt,
    )

    try:
        receipt = build_security_adapter_discovery_receipt(repo_root)
    except SecurityAdapterDiscoveryError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-security-adapter-discovery-receipt.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk security adapters",
        "adapter_count": receipt["adapter_count"],
        "adapter_candidates": receipt["adapter_candidates"],
        "receipt": receipt,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "security", "adapters", "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_security_adapter_discovery"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=(
                    "Add local scanner workflow or config evidence before approving any scanner execution adapter."
                ),
            )
        )
    return result


def _skills_sdk_resolve_security_source(repo_root: Path, query: str) -> tuple[object, Path | None]:
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    return source_path_value, source_path


def _skills_sdk_blocked_security_preview(
    *,
    result: CallResult,
    data_key: str,
    schema_version: str,
    query: str,
    source_path_value: object,
    validation_command: str,
    command_label: str,
) -> CallResult:
    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=f"Skills SDK {command_label} is missing a canonical SKILL.md source for '{query}'.",
            fix_suggestion=validation_command,
        )
    )
    result.data[data_key] = {
        "schema_version": schema_version,
        "query": query,
        "status": "blocked",
        "canonical_source_path": source_path_value,
        "receipt": None,
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "validation_commands": [validation_command],
        "agent_summary": f"{command_label} is blocked for {query}: canonical source is missing.",
    }
    return result


def skills_sdk_security_package_signature_preview(repo_root: Path, target: str) -> CallResult:
    """Build a package security signature without executing source content."""
    result = CallResult()
    result.metadata["command"] = "sdk security package-signature"
    query = target.strip()
    source_path_value, source_path = _skills_sdk_resolve_security_source(repo_root, query)
    validation_command = _ask_validation_command("sdk", "security", "package-signature", query, "--preview")

    if not source_path or not source_path.is_file():
        return _skills_sdk_blocked_security_preview(
            result=result,
            data_key="skills_sdk_package_security_signature",
            schema_version="skills-sdk-package-security-signature-preview.v0",
            query=query,
            source_path_value=source_path_value,
            validation_command=validation_command,
            command_label="package security signature",
        )

    from ask.skills_sdk.package_security_signature import build_package_security_signature_receipt  # noqa: PLC0415

    receipt = build_package_security_signature_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-package-security-signature-preview.v0",
        "query": query,
        "status": receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk security package-signature",
        "package_id": receipt["package_id"],
        "package_digest": receipt["package_digest"],
        "package_security_signature_digest": receipt["package_security_signature_digest"],
        "indicator_summary": receipt["indicator_summary"],
        "indicators": receipt["indicators"],
        "receipt": receipt,
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "validation_commands": [validation_command],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_package_security_signature"] = payload
    return result


def skills_sdk_security_risk_modes_preview(repo_root: Path, target: str) -> CallResult:
    """
    Generate a security risk-mode taxonomy for a skill without executing it.

    Parameters:
        target: A skill path or SDK handle.

    Returns:
        CallResult containing risk-mode taxonomy analysis under data["skills_sdk_risk_mode_taxonomy"].
        Status is "error" if the canonical source is missing.
    """
    result = CallResult()
    result.metadata["command"] = "sdk security risk-modes"
    query = target.strip()
    source_path_value, source_path = _skills_sdk_resolve_security_source(repo_root, query)
    validation_command = _ask_validation_command("sdk", "security", "risk-modes", query, "--preview")

    if not source_path or not source_path.is_file():
        return _skills_sdk_blocked_security_preview(
            result=result,
            data_key="skills_sdk_risk_mode_taxonomy",
            schema_version="skills-sdk-risk-mode-taxonomy-preview.v0",
            query=query,
            source_path_value=source_path_value,
            validation_command=validation_command,
            command_label="risk-mode taxonomy",
        )

    from ask.skills_sdk.risk_modes import build_risk_mode_taxonomy_receipt  # noqa: PLC0415

    receipt = build_risk_mode_taxonomy_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-risk-mode-taxonomy-preview.v0",
        "query": query,
        "status": receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk security risk-modes",
        "package_id": receipt["package_id"],
        "package_digest": receipt["package_digest"],
        "primary_mode": receipt["primary_mode"],
        "detected_modes": receipt["detected_modes"],
        "receipt": receipt,
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "validation_commands": [validation_command],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_risk_mode_taxonomy"] = payload
    return result


def skills_sdk_security_run_lane_preview(
    repo_root: Path,
    target: str,
    *,
    profile: str | None = None,
    require_review: bool = False,
) -> CallResult:
    """Build the deterministic SDK security lane receipt without executing source content."""
    result = CallResult()
    result.metadata["command"] = "sdk security run-lane"
    query = target.strip()
    source_path_value, source_path = _skills_sdk_resolve_security_source(repo_root, query)

    validation_command_parts = ["sdk", "security", "run-lane", query, "--preview"]
    if profile:
        validation_command_parts.extend(["--profile", profile])
    if require_review:
        validation_command_parts.append("--require-review")
    validation_command = _ask_validation_command(*validation_command_parts)

    if not source_path or not source_path.is_file():
        return _skills_sdk_blocked_security_preview(
            result=result,
            data_key="skills_sdk_security_lane",
            schema_version="skills-sdk-security-lane-preview.v0",
            query=query,
            source_path_value=source_path_value,
            validation_command=validation_command,
            command_label="security lane",
        )

    from ask.skills_sdk.security_lane import build_security_lane_receipt  # noqa: PLC0415

    receipt = build_security_lane_receipt(
        repo_root,
        source_path=source_path,
        query=query,
        profile=profile,
        require_review=require_review,
    )
    payload = {
        "schema_version": "skills-sdk-security-lane-preview.v0",
        "query": query,
        "status": receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk security run-lane",
        "package_id": receipt["package_id"],
        "package_digest": receipt["package_digest"],
        "security_lane_digest": receipt["security_lane_digest"],
        "package_security_signature_digest": receipt["package_security_signature_digest"],
        "risk_mode_taxonomy_digest": receipt["risk_mode_taxonomy_digest"],
        "profile_review": receipt["profile_review"],
        "receipt": receipt,
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "validation_commands": [validation_command],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_security_lane"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=validation_command,
            )
        )
    return result


def skills_sdk_static_explorer_preview(repo_root: Path) -> CallResult:
    """
    Generate a JSON-only static explorer index preview without rendering or publishing HTML.

    Returns:
        `CallResult` with `data["skills_sdk_static_explorer_preview"]` containing a structured preview payload including capability and skill counts, projection inputs, and explorer metadata. Sets status to `error` if the receipt status is `blocked`.
    """
    result = CallResult()
    result.metadata["command"] = "sdk explorer static"
    from ask.skills_sdk.static_explorer import (  # noqa: PLC0415
        StaticExplorerError,
        build_static_explorer_receipt,
    )

    try:
        receipt = build_static_explorer_receipt(repo_root)
    except StaticExplorerError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-static-explorer-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk explorer static",
        "capability_count": receipt["capability_count"],
        "skill_count": receipt["skill_count"],
        "projection_inputs": receipt["projection_inputs"],
        "receipt": receipt,
        "html_rendered": False,
        "hosted_publish_requested": False,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "explorer", "static", "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_static_explorer_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Fix capability status JSON or rooted .skillsets manifest JSONL before previewing explorer indexes.",
            )
        )
    return result


def skills_sdk_eval_scenario_quality(
    repo_root: Path,
    target: str,
    *,
    tessl_staged_json: str | None = None,
    tessl_score: str | None = None,
    scenario_set: str | None = None,
) -> CallResult:
    """Preview eval scenario quality without promoting or mutating scenario sources."""
    result = CallResult()
    result.metadata["command"] = "sdk eval scenario-quality"
    query = target.strip()
    tessl_staged_path = Path(tessl_staged_json) if tessl_staged_json else None
    if tessl_staged_path and not tessl_staged_path.is_absolute():
        tessl_staged_path = repo_root / tessl_staged_path
    tessl_score_path = Path(tessl_score) if tessl_score else None
    if tessl_score_path and not tessl_score_path.is_absolute():
        tessl_score_path = repo_root / tessl_score_path
    validation_command_parts = ["sdk", "eval", "scenario-quality", query, "--preview"]
    if scenario_set:
        validation_command_parts.extend(["--scenario-set", scenario_set])
    if tessl_staged_json:
        validation_command_parts.extend(["--tessl-staged-json", tessl_staged_json])
    if tessl_score:
        validation_command_parts.extend(["--tessl-score", tessl_score])
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_scenario_quality"] = {
            "schema_version": "skills-sdk-eval-scenario-quality.v0",
            "status": "blocked",
            "query": query,
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "promotion_performed": False,
            "validation_commands": [_ask_validation_command(*validation_command_parts)],
            "agent_summary": f"skills-sdk eval scenario-quality is blocked for {query}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK scenario quality is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "scenario-quality", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.scenario_quality import (  # noqa: PLC0415
        ScenarioQualityError,
        build_scenario_quality_receipt,
    )

    try:
        receipt = build_scenario_quality_receipt(
            repo_root,
            source_path=source_path,
            query=query,
            tessl_staged_json=tessl_staged_path,
            tessl_score_json=tessl_score_path,
            scenario_set=scenario_set,
        )
    except ScenarioQualityError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-eval-scenario-quality.v0",
        "status": receipt["status"],
        "query": query,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk eval scenario-quality",
        "receipt": receipt,
        "scenario_count": receipt["scenario_count"],
        "promotion_ready_count": receipt["promotion_ready_count"],
        "blocked_count": receipt["blocked_count"],
        "mutation_performed": False,
        "promotion_performed": False,
        "validation_commands": [_ask_validation_command(*validation_command_parts)],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_scenario_quality"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Add or repair references/evals.yaml with ids, prompts, acceptance checks, eval modes, and deterministic safety checks.",
            )
        )
    return result


def _blocked_eval_shard_aggregate_receipt(
    *,
    profile: str,
    scenario_set: str,
    message: str,
) -> dict[str, Any]:
    """Return a schema-complete blocked aggregate receipt for early input failures."""
    blocker = {"id": "aggregate_input_invalid", "status": "blocker", "evidence": [message]}
    return {
        "schema_version": "skills-sdk.eval-shard-aggregate-receipt.v0",
        "schema_uri": "https://agent-skills.local/schemas/skills-sdk/eval-shard-aggregate-receipt.v0.schema.json",
        "status": "blocked",
        "lane": profile,
        "profile": profile,
        "package_id": None,
        "package_digest": None,
        "execution_model": None,
        "execution_model_family": None,
        "execution_model_provider": None,
        "execution_identity_source": None,
        "codex_exec_invoked": False,
        "codex_profile": None,
        "shard_dataset_digests": [],
        "rubric_digest": None,
        "scenario_set_id": scenario_set,
        "scenario_set_case_ids": [],
        "shard_receipts": [],
        "shard_count": 0,
        "case_count": 0,
        "passed_count": 0,
        "failed_count": 0,
        "cases": [],
        "checks": [blocker],
        "blockers": [blocker],
        "mutation_performed": False,
        "claims_boundary": "This blocked receipt proves only that shard aggregation input validation failed before aggregation.",
        "agent_summary": f"{profile} shard aggregation input is invalid: {message}",
    }


def _skills_sdk_persist_eval_shard_aggregate(
    repo_root: Path,
    package_id: str,
    payload: dict[str, Any],
) -> str | None:
    """Persist passing aggregate evidence in the existing repository-local artifact lane."""
    if package_id in {"", ".", ".."} or Path(package_id).name != package_id:
        return None
    artifact_dir = (
        repo_root
        / "Infrastructure"
        / "artifacts"
        / "skills"
        / package_id
        / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    )
    try:
        artifact_dir.mkdir(parents=True, exist_ok=False)
        artifact_path = artifact_dir / "aggregate.json"
        artifact_ref = _repo_relative_path(repo_root, artifact_path)
        if artifact_ref is None:
            return None
        envelope = {
            "status": "success",
            "data": {
                "skills_sdk_eval_shard_aggregate": {
                    **payload,
                    "artifact_path": artifact_ref,
                    "mutation_performed": True,
                }
            },
        }
        artifact_path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        return None
    payload["artifact_path"] = artifact_ref
    payload["mutation_performed"] = True
    return artifact_ref


def _skills_sdk_eval_shard_aggregate_payload(
    *,
    target: str,
    scenario_set: str,
    receipts: list[str],
    codex_profile: str,
    receipt: dict[str, Any],
    artifact_mode: Literal["preview", "write"],
) -> dict[str, Any]:
    """Build the existing aggregate envelope for the requested artifact mode."""
    command_parts = [
        "sdk", "eval", "aggregate-shards", target, "--scenario-set", scenario_set,
        "--codex-profile", codex_profile,
    ]
    command_parts.extend(part for receipt_path in receipts for part in ("--receipt", receipt_path))
    if artifact_mode == "preview":
        command_parts.append("--preview")
    return {
        "schema_version": "skills-sdk-eval-shard-aggregate.v0",
        "status": receipt["status"],
        "target": target,
        "scenario_set": scenario_set,
        "codex_profile": codex_profile,
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command(*command_parts)],
        "agent_summary": receipt["agent_summary"],
    }


def skills_sdk_eval_shard_aggregate(
    repo_root: Path,
    *,
    target: str,
    scenario_set: str,
    receipts: list[str],
    codex_profile: str = "oss-local",
) -> CallResult:
    """Aggregate bounded OSS release shards and persist a passing local aggregate."""
    return _skills_sdk_eval_shard_aggregate(
        repo_root,
        target=target,
        scenario_set=scenario_set,
        receipts=receipts,
        codex_profile=codex_profile,
        artifact_mode="write",
    )


def skills_sdk_eval_shard_aggregate_preview(
    repo_root: Path,
    *,
    target: str,
    scenario_set: str,
    receipts: list[str],
    codex_profile: str = "oss-local",
) -> CallResult:
    """Aggregate bounded OSS release shards without writing local evidence."""
    return _skills_sdk_eval_shard_aggregate(
        repo_root,
        target=target,
        scenario_set=scenario_set,
        receipts=receipts,
        codex_profile=codex_profile,
        artifact_mode="preview",
    )


def _skills_sdk_eval_shard_aggregate(
    repo_root: Path,
    *,
    target: str,
    scenario_set: str,
    receipts: list[str],
    codex_profile: str,
    artifact_mode: Literal["preview", "write"],
) -> CallResult:
    """Build an aggregate result in the selected explicit artifact mode."""
    from ask.skills_sdk.eval_shard_aggregate import (  # noqa: PLC0415
        EvalShardAggregateError,
        build_eval_shard_aggregate_receipt,
    )

    result = CallResult()
    result.metadata["command"] = "sdk eval aggregate-shards"
    if artifact_mode not in {"preview", "write"}:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=f"unsupported aggregate artifact mode: {artifact_mode}"))
        return result
    target_path = Path(target) if Path(target).is_absolute() else repo_root / target
    try:
        package_identity = _skills_sdk_eval_package_identity(repo_root, target)
        if package_identity is None:
            raise ValueError(f"unable to compute current package identity for {target}")
        receipt = build_eval_shard_aggregate_receipt(
            repo_root,
            skill_path=target_path,
            scenario_set=scenario_set,
            receipt_paths=[Path(path) for path in receipts],
            profile=codex_profile,
            expected_package_digest=package_identity["package_digest"],
        )
    except (EvalShardAggregateError, OSError, ValueError) as exc:
        if isinstance(exc, EvalShardAggregateError):
            receipt = exc.receipt
        else:
            receipt = _blocked_eval_shard_aggregate_receipt(
                profile=codex_profile,
                scenario_set=scenario_set,
                message=str(exc),
            )
        package_identity = None
    payload = _skills_sdk_eval_shard_aggregate_payload(
        target=target,
        scenario_set=scenario_set,
        receipts=receipts,
        codex_profile=codex_profile,
        receipt=receipt,
        artifact_mode=artifact_mode,
    )
    if receipt["status"] == "pass" and artifact_mode == "write":
        package_id = str((package_identity or {}).get("package_id") or "")
        if not _skills_sdk_persist_eval_shard_aggregate(repo_root, package_id, payload):
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="unable to persist local aggregate outcome evidence"))
    result.data["skills_sdk_eval_shard_aggregate"] = payload
    if receipt["status"] != "pass":
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=receipt["agent_summary"]))
    return result


def skills_sdk_eval_scorer_quality(repo_root: Path, target: str) -> CallResult:
    """Preview scorer calibration quality without promoting or mutating eval sources."""
    result = CallResult()
    result.metadata["command"] = "sdk eval scorer-quality"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_scorer_quality"] = {
            "schema_version": "skills-sdk-eval-scorer-quality.v0",
            "status": "blocked",
            "query": query,
            "canonical_source_path": source_path_value,
            "receipt": None,
            "ready": False,
            "mutation_performed": False,
            "promotion_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-quality", query, "--preview")],
            "agent_summary": f"skills-sdk eval scorer-quality is blocked for {query}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK scorer quality is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "scorer-quality", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.scorer_quality import build_scorer_quality_receipt  # noqa: PLC0415

    receipt = build_scorer_quality_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-eval-scorer-quality.v0",
        "status": receipt["status"],
        "query": query,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk eval scorer-quality",
        "receipt": receipt,
        "ready": receipt["ready"],
        "blocked_count": len(receipt["blockers"]),
        "mutation_performed": False,
        "promotion_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-quality", query, "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_scorer_quality"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command("sdk", "eval", "scorer-quality", query, "--preview"),
            )
        )
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
