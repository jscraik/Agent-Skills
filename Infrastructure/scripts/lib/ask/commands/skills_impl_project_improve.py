from .skills_impl_release_sets import *  # noqa: F403

def _sdk_improve_redact_sensitive_values(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if any(marker in lowered for marker in _SDK_IMPROVE_SENSITIVE_KEY_MARKERS):
                redacted[key_text] = "[redacted]"
            else:
                redacted[key_text] = _sdk_improve_redact_sensitive_values(item)
        return redacted
    if isinstance(value, list):
        return [_sdk_improve_redact_sensitive_values(item) for item in value]
    return value


def _sdk_improve_atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    safe_payload = _sdk_improve_redact_sensitive_values(payload)
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(safe_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)


def _sdk_improve_append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_event = _sdk_improve_redact_sensitive_values(event)
    with path.open("a", encoding="utf-8") as handle:
        json.dump(safe_event, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")


def _sdk_improve_error(
    *,
    result: CallResult,
    query: str,
    status: str,
    message: str,
    fix_suggestion: str,
    receipt: dict[str, Any],
) -> CallResult:
    result.status = "error"
    result.data["skills_sdk_project_improve"] = {
        "schema_version": "skills-sdk-project-improve.v0",
        "query": query,
        "status": status,
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": receipt.get("validation_commands", []),
        "agent_summary": message,
    }
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))
    return result


def skills_sdk_project_improve(
    repo_root: Path,
    target: str,
    project_root: str | None = None,
    run_evals: bool = False,
    mode: str = "smoke",
    codex_profile: str | None = None,
    apply: bool = False,
) -> CallResult:
    """Run a project-local skill improvement lifecycle gate and record owner-repo evidence."""
    result = CallResult()
    result.metadata["command"] = "sdk improve --apply" if apply else "sdk improve --preview"
    query = target.strip()
    timestamp = _sdk_improve_timestamp()
    resolved_project_root = _sdk_improve_project_root(project_root)
    if resolved_project_root is None:
        receipt = {
            "schema_version": "skills-sdk.project-improvement-receipt.v0",
            "status": "blocked",
            "operation": "project_skill_improve",
            "target": query,
            "project_root": project_root,
            "blockers": ["invalid_project_root"],
            "mutation_performed": False,
            "source_mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "improve", query, "--project-root", project_root or "<project-root>", "--preview"),
            ],
        }
        return _sdk_improve_error(
            result=result,
            query=query,
            status="blocked",
            message="Skills SDK improve requires an existing absolute --project-root.",
            fix_suggestion="Pass an absolute project root containing skills-sdk.json.",
            receipt=receipt,
        )

    manifest_path, manifest_evaluation = _sdk_improve_load_manifest(resolved_project_root)
    if not manifest_evaluation.is_valid:
        if manifest_evaluation.state == "absent":
            blocker_codes = ["missing_skills_sdk_manifest"]
            message = "Skills SDK improve requires an owner repo skills-sdk.json manifest that is absent."
            fix_suggestion = "Create skills-sdk.json with a canonical_project_source skill_roots entry."
        else:
            blocker_codes = ["invalid_skills_sdk_manifest", *manifest_evaluation.blocker_codes()]
            message = (
                "Skills SDK improve found a skills-sdk.json manifest that is invalid and cannot be "
                "treated as absent."
            )
            fix_suggestion = "Resolve the manifest blockers so it matches the skills-sdk.project.v1 contract."
        receipt = {
            "schema_version": "skills-sdk.project-improvement-receipt.v0",
            "status": "blocked",
            "operation": "project_skill_improve",
            "target": query,
            "project_root": str(resolved_project_root),
            "manifest_path": _sdk_improve_project_relative(resolved_project_root, manifest_path),
            "manifest_state": manifest_evaluation.state,
            "manifest_blockers": manifest_evaluation.blocker_dicts(),
            "manifest_compatibility_note": manifest_evaluation.compatibility_note(),
            "blockers": blocker_codes,
            "mutation_performed": False,
            "source_mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "improve", query, "--project-root", str(resolved_project_root), "--preview"),
            ],
        }
        return _sdk_improve_error(
            result=result,
            query=query,
            status="blocked",
            message=message,
            fix_suggestion=fix_suggestion,
            receipt=receipt,
        )
    manifest = manifest_evaluation.manifest

    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path or not source_path.is_file() or not _is_path_relative_to(source_path, resolved_project_root):
        receipt = {
            "schema_version": "skills-sdk.project-improvement-receipt.v0",
            "status": "blocked",
            "operation": "project_skill_improve",
            "target": query,
            "project_root": str(resolved_project_root),
            "canonical_source_path": str(source_path) if source_path else None,
            "blockers": ["target_not_project_local_source"],
            "mutation_performed": False,
            "source_mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "ir", "build", query),
            ],
        }
        return _sdk_improve_error(
            result=result,
            query=query,
            status="blocked",
            message="Skills SDK improve only edits manifest-declared project-local skill source.",
            fix_suggestion="Pass a SKILL.md path under the owner repo's canonical_project_source root.",
            receipt=receipt,
        )
    declared_root = _declared_project_skill_source(resolved_project_root, manifest_path, source_path)
    if not declared_root:
        receipt = {
            "schema_version": "skills-sdk.project-improvement-receipt.v0",
            "status": "blocked",
            "operation": "project_skill_improve",
            "target": query,
            "project_root": str(resolved_project_root),
            "canonical_source_path": str(source_path),
            "blockers": ["source_root_not_manifest_declared"],
            "mutation_performed": False,
            "source_mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "project", "doctor", "--project-root", str(resolved_project_root)),
            ],
        }
        return _sdk_improve_error(
            result=result,
            query=query,
            status="blocked",
            message="Project-local skill source is not declared as canonical_project_source.",
            fix_suggestion="Declare the skill root in skills-sdk.json before running sdk improve.",
            receipt=receipt,
        )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    eval_payload: dict[str, Any] | None = None
    eval_receipt: dict[str, Any] | None = None
    eval_closeout: dict[str, Any] | None = None
    if run_evals:
        eval_result = skills_sdk_eval_run(
            repo_root,
            target=str(source_path),
            mode=mode,
            runner="internal",
            skip_tessl=True,
            codex_profile=codex_profile,
        )
        eval_payload = eval_result.data.get("skills_sdk_eval_run") if isinstance(eval_result.data, dict) else None
        if isinstance(eval_payload, dict) and isinstance(eval_payload.get("receipt"), dict):
            eval_receipt = eval_payload["receipt"]
            internal_eval = eval_payload.get("internal_eval")
            if isinstance(internal_eval, dict) and isinstance(internal_eval.get("eval_closeout"), dict):
                eval_closeout = internal_eval["eval_closeout"]

    blockers: list[str] = []
    if hardening_receipt.get("status") != "pass":
        blockers.append(f"package_hardening:{hardening_receipt.get('status')}")
    if run_evals and (not eval_receipt or eval_receipt.get("status") != "pass"):
        blockers.append(f"evals:{eval_receipt.get('status') if eval_receipt else 'missing_receipt'}")
    if run_evals and eval_closeout:
        if eval_closeout.get("mutation_allowed") is not True:
            blockers.append("eval_closeout:mutation_not_allowed")
        if eval_closeout.get("registry_update_allowed") is not True:
            blockers.append("eval_closeout:registry_promotion_not_allowed")
        closeout_validation = eval_closeout.get("closeout_validation")
        if isinstance(closeout_validation, dict) and closeout_validation.get("status") != "pass":
            blockers.append("eval_closeout:validation_blocked")
    status = "blocked" if blockers else "pass"
    project_id = _sdk_improve_project_id(manifest, resolved_project_root)
    package_id = str(package_receipt.get("package_id") or source_path.parent.name)
    slug = _sdk_improve_receipt_slug(package_id, timestamp)
    try:
        paths = _sdk_improve_evidence_paths(resolved_project_root, manifest, slug)
    except ValueError as exc:
        receipt = {
            "schema_version": "skills-sdk.project-improvement-receipt.v0",
            "status": "blocked",
            "operation": "project_skill_improve",
            "target": query,
            "project_root": str(resolved_project_root),
            "canonical_source_path": str(source_path),
            "blockers": ["invalid_project_evidence_paths"],
            "mutation_performed": False,
            "source_mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "project", "doctor", "--project-root", str(resolved_project_root)),
            ],
        }
        return _sdk_improve_error(
            result=result,
            query=query,
            status="blocked",
            message=str(exc),
            fix_suggestion="Use project-relative evidence paths that stay inside project_root.",
            receipt=receipt,
        )
    receipt_relative = _sdk_improve_project_relative(resolved_project_root, paths["receipt"])
    registry_relative = _sdk_improve_project_relative(resolved_project_root, paths["registry"])
    events_relative = _sdk_improve_project_relative(resolved_project_root, paths["events"])
    source_relative = _sdk_improve_project_relative(resolved_project_root, source_path)
    source_edit = {
        "status": "not_requested",
        "reason": "sdk improve currently records package/eval-backed owner-repo evidence; no deterministic source patch was supplied.",
        "files_changed": [],
        "mutation_performed": False,
    }
    validation_commands = [
        _ask_validation_command("sdk", "package", "harden", str(source_path)),
    ]
    if run_evals:
        validation_commands.append(
            _ask_validation_command(
                "sdk",
                "eval",
                "run",
                str(source_path),
                "--runner",
                "internal",
                "--mode",
                mode,
                *(("--codex-profile", codex_profile) if codex_profile else ()),
            )
        )
    validation_commands.append(
        _ask_validation_command(
            "sdk",
            "improve",
            str(source_path),
            "--project-root",
            str(resolved_project_root),
            "--evals" if run_evals else "",
            *(("--codex-profile", codex_profile) if codex_profile else ()),
            "--apply" if apply else "--preview",
        ).replace("  ", " ")
    )
    receipt = {
        "schema_version": "skills-sdk.project-improvement-receipt.v0",
        "status": status,
        "operation": "project_skill_improve",
        "target": query,
        "project_root": str(resolved_project_root),
        "project_id": project_id,
        "manifest_path": _sdk_improve_project_relative(resolved_project_root, manifest_path),
        "canonical_source_path": str(source_path),
        "source": {
            "path": source_relative,
            "root": declared_root,
            "kind": "canonical_project_source",
        },
        "source_edit": source_edit,
        "package": {
            "status": hardening_receipt.get("status"),
            "package_id": package_id,
            "package_digest": hardening_receipt.get("package_digest"),
            "receipt": hardening_receipt,
        },
        "evals": {
            "requested": run_evals,
            "status": eval_receipt.get("status") if eval_receipt else "not_run",
            "mode": mode if run_evals else None,
            "receipt": eval_receipt,
            "closeout": eval_closeout,
        },
        "promotion": {
            "allowed": status == "pass",
            "missing": [
                blocker
                for blocker in blockers
                if blocker.startswith(("package_hardening:", "evals:", "eval_closeout:"))
            ],
        },
        "blockers": blockers,
        "registry_path": registry_relative,
        "events_path": events_relative,
        "receipt_path": receipt_relative,
        "mutation_performed": False,
        "source_mutation_performed": False,
        "validation_commands": validation_commands,
        "created_at": timestamp,
    }

    if apply:
        registry_before_digest = _skills_sdk_digest_file(paths["registry"]) if paths["registry"].is_file() else None
        try:
            registry = _sdk_improve_load_registry(
                paths["registry"],
                project_id,
                _sdk_improve_project_relative(resolved_project_root, manifest_path),
            )
        except ValueError as exc:
            receipt["status"] = "blocked"
            receipt["blockers"] = [*blockers, "invalid_project_registry"]
            receipt["mutation_performed"] = False
            return _sdk_improve_error(
                result=result,
                query=query,
                status="blocked",
                message=str(exc),
                fix_suggestion="Repair or move the existing project skill registry before applying SDK improve evidence.",
                receipt=receipt,
            )
        _sdk_improve_update_registry(
            registry,
            project_id=project_id,
            handle=package_id,
            source_path=source_relative,
            source_root=declared_root,
            hardening_receipt=hardening_receipt,
            eval_receipt=eval_receipt,
            improvement_status=status,
            receipt_path=receipt_relative,
            timestamp=timestamp,
            source_edit_status=source_edit["status"],
        )
        event = {
            "schema_version": "skills-sdk.project-skill-event.v1",
            "timestamp": timestamp,
            "event": "project_skill_improvement_validated" if status == "pass" else "project_skill_improvement_blocked",
            "project": project_id,
            "skill": package_id,
            "source": source_relative,
            "receipt": receipt_relative,
            "package_status": hardening_receipt.get("status"),
            "eval_status": eval_receipt.get("status") if eval_receipt else "not_run",
            "source_edit_status": source_edit["status"],
            "runtime_claim": "not_run",
        }
        _sdk_improve_atomic_write_json(paths["receipt"], receipt)
        _sdk_improve_atomic_write_json(paths["registry"], registry)
        _sdk_improve_append_event(paths["events"], event)
        receipt["registry_before_digest"] = registry_before_digest
        receipt["registry_after_digest"] = _skills_sdk_digest_file(paths["registry"])
        receipt["event"] = event
        receipt["mutation_performed"] = True
        _sdk_improve_atomic_write_json(paths["receipt"], receipt)

    payload = {
        "schema_version": "skills-sdk-project-improve.v0",
        "query": query,
        "status": status,
        "project_root": str(resolved_project_root),
        "canonical_source_path": str(source_path),
        "facade_command": "skills-sdk improve",
        "receipt": receipt,
        "mutation_performed": apply,
        "source_mutation_performed": False,
        "validation_commands": validation_commands,
        "agent_summary": (
            f"skills-sdk project improve {status} for {package_id}; "
            f"source edit {source_edit['status']}, owner evidence {'written' if apply else 'previewed'}."
        ),
    }
    result.data["skills_sdk_project_improve"] = payload
    if status != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK project improve blocked for {package_id}: {', '.join(blockers)}",
                fix_suggestion="Fix the blocked package or eval gate, then rerun sdk improve.",
            )
        )
    return result


def skills_sdk_project_install(
    repo_root: Path,
    target: str,
    project_root: str | None = None,
    scope: str = "project",
) -> CallResult:
    """Install one local skill into an explicit project root."""
    result = CallResult()
    result.metadata["command"] = "sdk install --apply"
    query = target.strip()
    if scope != "project":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Real Skills SDK installs are bounded to --scope project in PU-009.",
                fix_suggestion="ask sdk install <target> --apply --scope project --project-root /path/to/project --json --robot",
            )
        )
        return result
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    try:
        receipt = _install_project_skill(
            repo_root,
            query=query,
            source_path=source_path,
            target_info=target_info,
            project_root=project_root,
        )
    except _ProjectInstallError as exc:
        result.status = "error"
        result.data["skills_sdk_project_install"] = {
            "schema_version": "skills-sdk-project-install.v1",
            "query": query,
            "status": str(exc.receipt.get("status") or "blocked"),
            "scope": "project",
            "canonical_source_path": str(source_path) if source_path else None,
            "facade_command": "skills-sdk install --apply",
            "receipt": exc.receipt,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "install",
                    query,
                    "--apply",
                    "--project-root",
                    project_root or "<project-root>",
                ),
            ],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result

    payload = {
        "schema_version": "skills-sdk-project-install.v1",
        "query": query,
        "status": receipt["status"],
        "scope": "project",
        "canonical_source_path": str(source_path) if source_path else None,
        "facade_command": "skills-sdk install --apply",
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "install",
                query,
                "--apply",
                "--project-root",
                project_root or "<project-root>",
            ),
        ],
        "agent_summary": (
            f"skills-sdk installed {len(receipt['files_written'])} file(s) for {query} into {receipt['target_root']}."
        ),
    }
    result.data["skills_sdk_project_install"] = payload
    return result


def skills_sdk_project_rollback(
    repo_root: Path,
    receipt_path: str,
    project_root: str | None = None,
    apply: bool = False,
) -> CallResult:
    """Preview or apply receipt-proven cleanup for one project install receipt."""
    result = CallResult()
    mode = "--apply" if apply else "--preview"
    result.metadata["command"] = f"sdk rollback {mode}"
    try:
        receipt = _rollback_project_install(
            repo_root,
            receipt_path=receipt_path,
            project_root=project_root,
            apply=apply,
        )
    except _ProjectCleanupError as exc:
        result.status = "error"
        result.data["skills_sdk_project_rollback"] = {
            "schema_version": "skills-sdk-project-cleanup.v1",
            "operation": "rollback",
            "status": exc.receipt.get("status", "blocked"),
            "mode": "apply" if apply else "preview",
            "receipt": exc.receipt,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "rollback",
                    "--receipt",
                    receipt_path,
                    mode,
                    *(("--project-root", project_root) if project_root else ()),
                )
            ],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result
    payload = {
        "schema_version": "skills-sdk-project-cleanup.v1",
        "operation": "rollback",
        "status": receipt["status"],
        "mode": "apply" if apply else "preview",
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "rollback",
                "--receipt",
                receipt_path,
                mode,
                *(("--project-root", project_root) if project_root else ()),
            )
        ],
        "agent_summary": (
            f"skills-sdk rollback {receipt['status']} for {len(receipt.get('files_applied') if 'files_applied' in receipt else receipt.get('files_cleaned_up') if 'files_cleaned_up' in receipt else receipt['files_planned'])} {'applied' if receipt.get('mode') == 'apply' else 'planned'} file(s)."
            if receipt.get('mode') == 'apply'
            else f"skills-sdk rollback {receipt['status']} for {len(receipt['files_planned'])} planned file(s)."
        ),
    }
    result.data["skills_sdk_project_rollback"] = payload
    return result


def skills_sdk_project_uninstall(
    repo_root: Path,
    skill_id: str,
    project_root: str | None = None,
    apply: bool = False,
) -> CallResult:
    """
    Generate a project uninstallation receipt for a lockfile-resolved skill and optionally apply the cleanup.

    Parameters:
        repo_root (Path): Repository root path used to resolve and operate on the project.
        skill_id (str): Lockfile-resolved skill identifier to uninstall.
        project_root (str | None): Optional project root path to target; when omitted the repo-level project is used.
        apply (bool): When True, perform the uninstall changes; when False, produce a preview-only receipt.

    Returns:
        CallResult: Result with `data["skills_sdk_project_uninstall"]` containing a `skills-sdk-project-cleanup.v1` receipt payload
        with keys: `schema_version`, `operation`, `status`, `mode`, `skill_id`, `receipt`, `validation_commands`, and `agent_summary`.
        On failure (internal project cleanup error) the result has `status="error"` and `errors` contains an `ErrorObject`
        derived from the cleanup exception; the corresponding receipt is included in the data payload.
    """
    result = CallResult()
    mode = "--apply" if apply else "--preview"
    result.metadata["command"] = f"sdk uninstall {mode}"
    try:
        receipt = _uninstall_project_skill(
            repo_root,
            skill_id=skill_id,
            project_root=project_root,
            apply=apply,
        )
    except _ProjectCleanupError as exc:
        result.status = "error"
        result.data["skills_sdk_project_uninstall"] = {
            "schema_version": "skills-sdk-project-cleanup.v1",
            "operation": "uninstall",
            "status": exc.receipt.get("status", "blocked"),
            "mode": "apply" if apply else "preview",
            "skill_id": skill_id,
            "receipt": exc.receipt,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "uninstall",
                    skill_id,
                    mode,
                    *(("--project-root", project_root) if project_root else ()),
                )
            ],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result
    payload = {
        "schema_version": "skills-sdk-project-cleanup.v1",
        "operation": "uninstall",
        "status": receipt["status"],
        "mode": "apply" if apply else "preview",
        "skill_id": skill_id,
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "uninstall",
                skill_id,
                mode,
                *(("--project-root", project_root) if project_root else ()),
            )
        ],
        "agent_summary": (
            f"skills-sdk uninstall {receipt['status']} for {skill_id} with {len(receipt.get('files_applied') if 'files_applied' in receipt else receipt.get('files_cleaned_up') if 'files_cleaned_up' in receipt else receipt['files_planned'])} {'applied' if receipt.get('mode') == 'apply' else 'planned'} file(s)."
            if receipt.get('mode') == 'apply'
            else f"skills-sdk uninstall {receipt['status']} for {skill_id} with {len(receipt['files_planned'])} planned file(s)."
        ),
    }
    result.data["skills_sdk_project_uninstall"] = payload
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
