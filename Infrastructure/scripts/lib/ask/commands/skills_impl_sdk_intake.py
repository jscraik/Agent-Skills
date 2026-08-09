from .skills_impl_doctor_intake import *  # noqa: F403

def skills_sdk_intake_review(
    repo_root: Path,
    *,
    source: str,
    source_kind: str = "directory",
) -> CallResult:
    """
    Generate an intake review receipt for a skill source without mutating the workspace.

    Parameters:
        source (str): The external skill directory path to review.
        source_kind (str): Type of source. Defaults to "directory"; archive input remains blocked in this slice.

    Returns:
        CallResult: Result with `data["skills_sdk_intake_review"]` containing the receipt payload. Status is set to "error" if the receipt status is "blocked".
    """
    result = CallResult()
    result.metadata["command"] = "sdk intake review --preview"
    query = source.strip()
    receipt = _build_skill_intake_review_receipt(repo_root, source=query, source_kind=source_kind)
    payload = {
        "schema_version": "skills-sdk-intake-review.v0",
        "query": query,
        "status": receipt["status"],
        "facade_command": "skills-sdk intake review --preview",
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "intake",
                "review",
                query,
                "--preview",
                "--source-kind",
                source_kind,
            ),
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_intake_review"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion="Inspect data.skills_sdk_intake_review.receipt.intake_receipt.blockers before rerunning review.",
            )
        )
    return result


def skills_sdk_ir_build(
    repo_root: Path,
    target: str,
) -> CallResult:
    """
    Build a read-only SkillIR.v0 payload for a canonical skill target.

    Resolves the target to its canonical source location and generates a SkillIR
    representation if the source file exists. Returns a blocked IR payload if the
    canonical source cannot be located.

    Parameters:
        repo_root (Path): Repository root directory.
        target (str): Skill target identifier or query.

    Returns:
        CallResult: Result object with `data["skills_sdk_ir"]` containing a built or
        blocked SkillIR payload. Status is "error" if canonical source validation fails.
    """
    result = CallResult()
    result.metadata["command"] = "sdk ir build"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK IR build is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "check", query),
            )
        )
        result.data["skills_sdk_ir"] = {
            "schema_version": "skills-sdk-ir-build.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "ir", "build", query)],
            "agent_summary": f"skills-sdk ir build is blocked for {query}: canonical source is missing.",
        }
        return result

    ir = _build_skill_ir(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-ir-build.v0",
        "query": query,
        "status": "built",
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk ir build",
        "ir": ir,
        "receipt": {
            "command": "skills-sdk ir build",
            "status": "built",
            "mutation_performed": False,
            "schema_version": ir["schema_version"],
            "source_path": ir["source"]["skill_md"],
        },
        "validation_commands": [
            _ask_validation_command("sdk", "ir", "build", query),
        ],
        "agent_summary": f"skills-sdk ir build produced SkillIR.v0 for {query} without writes.",
    }
    result.data["skills_sdk_ir"] = payload
    return result


def skills_sdk_docs_verify(
    repo_root: Path,
    artifact: str | None = None,
) -> CallResult:
    """Verify static SDK docs projections against executable capability truth."""
    result = CallResult()
    result.metadata["command"] = "sdk docs verify"
    artifact_path = Path(artifact) if artifact else None
    payload = _verify_capability_docs_projection(repo_root, artifact_path=artifact_path)
    payload["validation_commands"] = [
        _ask_validation_command("sdk", "docs", "verify")
        if not artifact
        else _ask_validation_command("sdk", "docs", "verify", "--artifact", artifact)
    ]
    result.data["skills_sdk_docs_verify"] = payload
    if payload["status"] != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Regenerate or patch the capability projection from Infrastructure/config/skills-sdk/capability-matrix.v1.json.",
            )
        )
    return result


def skills_sdk_package_build(
    repo_root: Path,
    target: str,
) -> CallResult:
    """Build a non-mutating package identity receipt for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk package build"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK package build is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "ir", "build", query),
            )
        )
        result.data["skills_sdk_package_build"] = {
            "schema_version": "skills-sdk-package-build.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "package", "build", query)],
            "agent_summary": f"skills-sdk package build is blocked for {query}: canonical source is missing.",
        }
        return result

    receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-package-build.v0",
        "query": query,
        "status": receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk package build",
        "package_id": receipt["package_id"],
        "version": receipt["version"],
        "source_digest": receipt["source_digest"],
        "manifest_digest": receipt["manifest_digest"],
        "package_digest": receipt["package_digest"],
        "included_files": receipt["included_files"],
        "excluded_files": receipt["excluded_files"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "package", "build", query),
        ],
        "agent_summary": f"skills-sdk package build produced digest identity for {query} without writes.",
    }
    result.data["skills_sdk_package_build"] = payload
    return result


def skills_sdk_package_harden(
    repo_root: Path,
    target: str,
) -> CallResult:
    """Build a read-only package hardening receipt for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk package harden"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK package harden is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "harden", query),
            )
        )
        result.data["skills_sdk_package_harden"] = {
            "schema_version": "skills-sdk-package-harden.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "package", "harden", query)],
            "agent_summary": f"skills-sdk package harden is blocked for {query}: canonical source is missing.",
        }
        return result

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    payload = {
        "schema_version": "skills-sdk-package-harden.v0",
        "query": query,
        "status": hardening_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk package harden",
        "package_id": hardening_receipt["package_id"],
        "version": hardening_receipt["version"],
        "package_digest": hardening_receipt["package_digest"],
        "receipt": hardening_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "package", "harden", query),
        ],
        "agent_summary": f"skills-sdk package harden {hardening_receipt['status']} for {query} without writes.",
    }
    result.data["skills_sdk_package_harden"] = payload
    if hardening_receipt["status"] != "pass":
        result.status = "error"
        message = "Skills SDK package hardening blocked package emission."
        if hardening_receipt["blockers"]:
            message = hardening_receipt["blockers"][0]["message"]
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion="Remove forbidden package paths or restore canonical SkillIR/package provenance before hardening.",
            )
        )
    return result


def skills_sdk_package_signing_intent(
    repo_root: Path,
    target: str,
    policy: str,
) -> CallResult:
    """Build a non-mutating signing intent receipt for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk package signing-intent"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    policy_path = Path(policy)
    if not policy_path.is_absolute():
        policy_path = repo_root / policy_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK package signing intent is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        result.data["skills_sdk_package_signing_intent"] = {
            "schema_version": "skills-sdk-package-signing-intent.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "signing_performed": False,
            "key_material_accessed": False,
            "artifact_emitted": False,
            "validation_commands": [
                _ask_validation_command("sdk", "package", "signing-intent", query, "--policy", policy)
            ],
            "agent_summary": f"skills-sdk package signing intent is blocked for {query}: canonical source is missing.",
        }
        return result

    from ask.skills_sdk.signing_intent import (  # noqa: PLC0415
        SigningIntentError,
        build_signing_intent_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    try:
        signing_receipt = build_signing_intent_receipt(
            repo_root=repo_root,
            policy_path=policy_path,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
        )
    except SigningIntentError as exc:
        signing_receipt = exc.receipt

    payload = {
        "schema_version": "skills-sdk-package-signing-intent.v0",
        "query": query,
        "status": signing_receipt["status"],
        "canonical_source_path": source_path_value,
        "policy_path": policy,
        "facade_command": "skills-sdk package signing-intent",
        "package_id": signing_receipt["package_id"],
        "version": signing_receipt["version"],
        "package_digest": signing_receipt["package_digest"],
        "receipt": signing_receipt,
        "mutation_performed": False,
        "signing_performed": False,
        "key_material_accessed": False,
        "artifact_emitted": False,
        "validation_commands": [
            _ask_validation_command("sdk", "package", "signing-intent", query, "--policy", policy),
        ],
        "agent_summary": signing_receipt["agent_summary"],
    }
    result.data["skills_sdk_package_signing_intent"] = payload
    if signing_receipt["status"] != "ready":
        result.status = "error"
        message = signing_receipt["blockers"][0]["message"] if signing_receipt["blockers"] else payload["agent_summary"]
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=(
                    "Use a v0 signing policy that pins the package id and digest, requires hardening, "
                    "keeps key material external, and does not require archive emission."
                ),
            )
        )
    return result


def skills_sdk_sandbox_validate(
    repo_root: Path,
    profile: str,
) -> CallResult:
    """Validate a sandbox boundary profile without invoking an execution provider."""
    result = CallResult()
    result.metadata["command"] = "sdk sandbox validate"
    try:
        receipt = _build_sandbox_profile_receipt(repo_root, profile_path=profile)
    except _SandboxProfileError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-sandbox-validate.v0",
        "status": receipt["status"],
        "profile": profile,
        "facade_command": "skills-sdk sandbox validate",
        "receipt": receipt,
        "mutation_performed": False,
        "execution_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "sandbox", "validate", "--profile", profile),
        ],
        "agent_summary": (
            f"skills-sdk sandbox validate passed for {receipt['profile_path']} without executing a sandbox."
            if receipt["status"] == "pass"
            else f"skills-sdk sandbox validate blocked {receipt['profile_path']} with {len(receipt['blockers'])} blocker(s)."
        ),
    }
    result.data["skills_sdk_sandbox_validate"] = payload
    if receipt["status"] != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use a deny-by-default profile with no persistent writes, no network egress, no ambient environment, and no selected adapter.",
            )
        )
    return result


def skills_sdk_trust_decide(
    repo_root: Path,
    target: str,
    decision: str,
    reason: str,
    owner: str,
    *,
    preview: bool,
    apply: bool,
    ledger: str | None = None,
    expires_at: str | None = None,
    revoked_package_digest: str | None = None,
) -> CallResult:
    """Preview or append a local trust ledger decision for one skill package."""
    result = CallResult()
    result.metadata["command"] = "sdk trust decide"
    preview_mode = preview and not apply
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK trust decision is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        result.data["skills_sdk_trust_decide"] = {
            "schema_version": "skills-sdk-trust-decide.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "trust_store_mutated": False,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "trust",
                    "decide",
                    query,
                    "--decision",
                    decision,
                    "--reason",
                    reason,
                    "--owner",
                    owner,
                    "--preview",
                )
            ],
            "agent_summary": f"skills-sdk trust decide is blocked for {query}: canonical source is missing.",
        }
        return result

    from ask.skills_sdk.trust_ledger import (  # noqa: PLC0415
        TrustLedgerError,
        build_trust_decision_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    try:
        trust_receipt = build_trust_decision_receipt(
            repo_root,
            package_receipt=package_receipt,
            decision=decision,
            reason=reason,
            owner=owner,
            apply=apply,
            ledger_path=ledger,
            expires_at=expires_at,
            revoked_package_digest=revoked_package_digest,
        )
    except TrustLedgerError as exc:
        trust_receipt = exc.receipt

    command_args = ["sdk", "trust", "decide", query, "--decision", decision, "--reason", reason, "--owner", owner]
    if expires_at:
        command_args.extend(["--expires-at", expires_at])
    if revoked_package_digest:
        command_args.extend(["--revoked-package-digest", revoked_package_digest])
    if ledger:
        command_args.extend(["--ledger", ledger])
    command_args.append("--apply" if apply else "--preview")

    payload = {
        "schema_version": "skills-sdk-trust-decide.v0",
        "query": query,
        "status": trust_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk trust decide",
        "package_id": trust_receipt["package_id"],
        "version": trust_receipt["version"],
        "package_digest": trust_receipt["package_digest"],
        "ledger_path": trust_receipt["ledger_path"],
        "decision": trust_receipt["decision"],
        "preview": preview_mode,
        "receipt": trust_receipt,
        "mutation_performed": trust_receipt["mutation_performed"],
        "trust_store_mutated": False,
        "validation_commands": [_ask_validation_command(*command_args)],
        "agent_summary": trust_receipt["agent_summary"],
    }
    result.data["skills_sdk_trust_decide"] = payload
    if trust_receipt["status"] == "blocked":
        result.status = "error"
        message = trust_receipt["blockers"][0]["message"] if trust_receipt["blockers"] else payload["agent_summary"]
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion="Provide a valid decision, reason, owner, ledger path, and revocation digest when decision is revoke.",
            )
        )
    return result


def skills_sdk_observability_feedback(
    repo_root: Path,
    target: str,
    events: str,
) -> CallResult:
    """Mine redacted runtime events into non-mutating feedback candidates."""
    result = CallResult()
    result.metadata["command"] = "sdk observability feedback"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK observability feedback is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        return result

    from ask.skills_sdk.observability_feedback import (  # noqa: PLC0415
        ObservabilityFeedbackError,
        build_observability_feedback_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    try:
        feedback_receipt = build_observability_feedback_receipt(
            repo_root,
            package_receipt=package_receipt,
            events_path=events,
        )
    except ObservabilityFeedbackError as exc:
        feedback_receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-observability-feedback.v0",
        "query": query,
        "status": feedback_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk observability feedback",
        "package_id": feedback_receipt["package_id"],
        "package_digest": feedback_receipt["package_digest"],
        "receipt": feedback_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "observability", "feedback", "--skill", query, "--events", events, "--preview")
        ],
        "agent_summary": feedback_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_feedback"] = payload
    if feedback_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use redacted JSONL event records with digest references and no raw prompt/output fields.",
            )
        )
    return result


def skills_sdk_emitter_preview(
    repo_root: Path,
    target: str,
    projection: str,
    target_root: str,
) -> CallResult:
    """Preview a generated-output write plan without emitting files."""
    result = CallResult()
    result.metadata["command"] = "sdk emitter preview"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK emitter preview is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        return result

    from ask.skills_sdk.emitter_preview import (  # noqa: PLC0415
        EmitterPreviewError,
        build_emitter_preview_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    try:
        emitter_receipt = build_emitter_preview_receipt(
            repo_root,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
            projection=projection,
            target_root=target_root,
        )
    except EmitterPreviewError as exc:
        emitter_receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-emitter-preview.v0",
        "query": query,
        "status": emitter_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk emitter preview",
        "package_id": emitter_receipt["package_id"],
        "package_digest": emitter_receipt["package_digest"],
        "projection": emitter_receipt["projection"],
        "target_root": emitter_receipt["target_root"],
        "receipt": emitter_receipt,
        "mutation_performed": False,
        "artifact_emitted": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "emitter",
                "preview",
                "--skill",
                query,
                "--projection",
                projection,
                "--target-root",
                target_root,
                "--preview",
            )
        ],
        "agent_summary": emitter_receipt["agent_summary"],
    }
    result.data["skills_sdk_emitter_preview"] = payload
    if emitter_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use --projection runtime-skill with --target-root .agents/skills and a hardened local package.",
            )
        )
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
