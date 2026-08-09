from .skills_impl_sdk_eval import *  # noqa: F403

def skills_sdk_eval_scorer_calibration(repo_root: Path, target: str) -> CallResult:
    """Preview held-out scorer calibration evidence without mutating eval sources."""
    result = CallResult()
    result.metadata["command"] = "sdk eval scorer-calibration"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_scorer_calibration"] = {
            "schema_version": "skills-sdk-eval-scorer-calibration.v0",
            "status": "blocked",
            "query": query,
            "canonical_source_path": source_path_value,
            "receipt": None,
            "ready": False,
            "mutation_performed": False,
            "promotion_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-calibration", query, "--preview")],
            "agent_summary": f"skills-sdk eval scorer-calibration is blocked for {query}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK scorer calibration is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "scorer-calibration", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.scorer_calibration import build_scorer_calibration_receipt  # noqa: PLC0415

    receipt = build_scorer_calibration_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-eval-scorer-calibration.v0",
        "status": receipt["status"],
        "query": query,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk eval scorer-calibration",
        "receipt": receipt,
        "ready": receipt["ready"],
        "blocked_count": len(receipt["blockers"]),
        "mutation_performed": False,
        "promotion_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-calibration", query, "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_scorer_calibration"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command("sdk", "eval", "scorer-calibration", query, "--preview"),
            )
        )
    return result


def skills_sdk_eval_tessl_score(
    repo_root: Path,
    *,
    view_json: str,
    skill: str,
    run_id: str | None = None,
) -> CallResult:
    """Preview a Tessl score receipt from an explicit eval view JSON artifact."""
    result = CallResult()
    result.metadata["command"] = "sdk eval tessl-score"
    view_path = Path(view_json)
    if not view_path.is_absolute():
        view_path = repo_root / view_path

    from ask.skills_sdk.tessl_score_receipt import build_tessl_score_receipt  # noqa: PLC0415

    receipt = build_tessl_score_receipt(repo_root, view_json=view_path, skill=skill, run_id=run_id)
    payload = {
        "schema_version": "skills-sdk-eval-tessl-score.v0",
        "status": receipt["status"],
        "ready": receipt["ready"],
        "skill": skill,
        "run_id": receipt["run_id"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "eval", "tessl-score", "--view-json", view_json, "--skill", skill, "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_tessl_score"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command(
                    "sdk",
                    "eval",
                    "tessl-score",
                    "--view-json",
                    view_json,
                    "--skill",
                    skill,
                    "--preview",
                ),
            )
        )
    return result


def skills_sdk_eval_tessl_local_proof(
    repo_root: Path,
    *,
    skill: str,
    workspace: str,
    execute: bool = False,
    include_review: bool = False,
    review_threshold: int = TESSL_REVIEW_MIN_SCORE,
    timeout_seconds: int = 180,
) -> CallResult:
    """Preview or execute a temp-staged local Tessl package/install proof receipt."""
    result = CallResult()
    result.metadata["command"] = "sdk eval tessl-local-proof"
    from ask.commands import evals as eval_commands  # noqa: PLC0415

    receipt = eval_commands.run_tessl_local_proof(
        repo_root,
        skill,
        workspace=workspace,
        execute=execute,
        include_review=include_review,
        review_threshold=review_threshold,
        timeout_seconds=timeout_seconds,
    )
    command_parts = [
        "sdk",
        "eval",
        "tessl-local-proof",
        "--skill",
        skill,
        "--workspace",
        workspace,
    ]
    if execute:
        command_parts.append("--execute")
    else:
        command_parts.append("--preview")
    if include_review:
        command_parts.append("--include-review")
    if review_threshold != TESSL_REVIEW_MIN_SCORE:
        command_parts.extend(["--review-threshold", str(review_threshold)])
    if timeout_seconds != 180:
        command_parts.extend(["--timeout-seconds", str(timeout_seconds)])

    payload = {
        "schema_version": "skills-sdk-eval-tessl-local-proof.v0",
        "status": receipt.get("status"),
        "ready": receipt.get("status") == "pass",
        "skill": skill,
        "workspace": workspace,
        "receipt": receipt,
        "mutation_performed": execute,
        "validation_commands": [_ask_validation_command(*command_parts)],
        "agent_summary": (
            "Tessl local proof passed."
            if receipt.get("status") == "pass"
            else f"Tessl local proof is {receipt.get('status')} for {skill}."
        ),
    }
    result.data["skills_sdk_eval_tessl_local_proof"] = payload
    if receipt.get("status") in {"blocked", "fail"}:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION" if receipt.get("status") == "fail" else "ERR_RUNTIME",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command(
                    "sdk",
                    "eval",
                    "tessl-local-proof",
                    "--skill",
                    skill,
                    "--workspace",
                    workspace,
                    "--preview",
                ),
            )
        )
    return result


def _sdk_plugin_first_principles_gate(kind: str, action: str) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.first-principles-factory-gate.v1",
        "desired_outcome": "Create, review, install, or register a single skill or plugin through one SDK lifecycle front door.",
        "user_specific_constraints": [
            "Single skills and plugins must share an SDK orchestration lane.",
            "Factory behavior must reuse existing skill/plugin commands instead of duplicating scaffold logic.",
            "Registry save is local registry or marketplace persistence, not remote publication.",
        ],
        "copied_assumption_rejected": "Do not create a second plugin factory or treat marketplace save as public registry publish.",
        "fundamental_constraints": [
            f"artifact_kind={kind}",
            f"lifecycle_action={action}",
            "external registry publication requires a separate future authority lane",
            "apply mode may only delegate to existing bounded commands or write local registry files",
        ],
        "smallest_effective_mechanism": "Add an SDK facade receipt that delegates to existing skill and plugin lifecycle commands.",
        "artifact_decision": "IMPROVE_EXISTING",
        "rejected_alternatives": [
            {
                "alternative": "BUILD_PLUGIN",
                "reason": "The capability already belongs to the SDK and factory command surfaces.",
            },
            {
                "alternative": "ADD_HOOK",
                "reason": "The missing behavior is orchestration and receipts, not runtime hook execution.",
            },
            {
                "alternative": "REMOTE_PUBLISH",
                "reason": "Remote registry publish is explicitly outside the current local SDK authority boundary.",
            },
        ],
        "evidence_required": [
            "SDK command route exists for create, review, install, and save-registry.",
            "Preview receipts expose lower-level commands before mutation.",
            "Apply receipts show the delegated command result or local registry write.",
        ],
        "validation_proof": [
            "Focused SDK plugin lifecycle tests",
            "CLI help smoke for ask sdk plugin",
            "py_compile for edited command modules",
        ],
        "stop_or_pivot_condition": "Stop before remote registry publication, external writes, or ambiguous plugin ownership.",
    }


def _sdk_plugin_mode_status(apply: bool) -> str:
    return "applied" if apply else "preview"


def _sdk_plugin_result(
    *,
    command: str,
    payload_key: str,
    payload: dict[str, Any],
    error_message: str | None = None,
    fix_suggestion: str | None = None,
) -> CallResult:
    result = CallResult()
    result.metadata["command"] = command
    result.data[payload_key] = payload
    if error_message:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=error_message,
                fix_suggestion=fix_suggestion,
            )
        )
    return result


def _sdk_plugin_relpath(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _sdk_plugin_registry_path(repo_root: Path, kind: str, registry: str | None) -> Path:
    if registry:
        path = Path(registry)
        return path if path.is_absolute() else repo_root / path
    if kind == "plugin":
        return repo_root / "Plugins" / "marketplace.json"
    return repo_root / ".harness" / "skills" / "registry.json"


def _sdk_plugin_read_json_object(path: Path, default_payload: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default_payload
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Registry JSON must be an object at {path}.")
    return payload


def _sdk_plugin_atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    _sdk_improve_atomic_write_json(path, payload)


def _sdk_plugin_save_skill_registry_receipt(
    repo_root: Path,
    *,
    target: str,
    registry: str | None,
    name: str | None,
    apply: bool,
) -> dict[str, Any]:
    registry_path = _sdk_plugin_registry_path(repo_root, "skill", registry)
    target_info, _audit_target = _resolve_doctor_target(repo_root, target)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    if not source_path_value:
        raise ValueError(f"Skill registry target did not resolve to a canonical source: {target}.")
    source_path = Path(str(source_path_value))
    if not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path.is_file():
        raise ValueError(f"Skill registry target source does not exist: {target}.")
    handle = (name or source_path.parent.name).strip()
    source_rel = _sdk_plugin_relpath(repo_root, source_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = {
        "skill_id": f"local:{handle}",
        "handle": handle,
        "scope": "local",
        "source": {
            "path": source_rel,
            "root": _sdk_plugin_relpath(repo_root, source_path.parent),
            "kind": "canonical_skill_source",
        },
        "lifecycle": {
            "state": "registered",
            "decision": "sdk_plugin_save_registry",
            "updated_at": timestamp,
        },
        "evidence": {
            "last_registry_save_command": _ask_validation_command(
                "sdk",
                "plugin",
                "save-registry",
                "--kind",
                "skill",
                "--target",
                target,
                "--apply" if apply else "--preview",
            ),
        },
    }
    receipt = {
        "schema_version": "skills-sdk.plugin-registry-save.v1",
        "kind": "skill",
        "target": target,
        "name": handle,
        "status": _sdk_plugin_mode_status(apply),
        "registry_path": _sdk_plugin_relpath(repo_root, registry_path),
        "entry": entry,
        "mutation_performed": apply,
    }
    if not apply:
        return receipt
    registry_payload = _sdk_plugin_read_json_object(
        registry_path,
        {
            "schema_version": "skills-sdk.project-skill-registry.v1",
            "project": {"id": "agent-skills-local", "manifest": "local"},
            "summary": {},
            "skills": [],
        },
    )
    skills = registry_payload.setdefault("skills", [])
    if not isinstance(skills, list):
        raise ValueError(f"Registry field 'skills' must be a list at {registry_path}.")
    replaced = False
    for index, item in enumerate(skills):
        if isinstance(item, dict) and (item.get("skill_id") == entry["skill_id"] or item.get("handle") == handle):
            skills[index] = entry
            replaced = True
            break
    if not replaced:
        skills.append(entry)
    summary = registry_payload.setdefault("summary", {})
    if isinstance(summary, dict):
        summary["skill_count"] = len([item for item in skills if isinstance(item, dict)])
        summary["last_registry_save_at"] = timestamp
        summary["last_registry_save_handle"] = handle
    _sdk_plugin_atomic_write_json(registry_path, registry_payload)
    receipt["registry_written"] = True
    return receipt


def _sdk_plugin_save_plugin_registry_receipt(
    repo_root: Path,
    *,
    target: str,
    registry: str | None,
    name: str | None,
    apply: bool,
) -> dict[str, Any]:
    registry_path = _sdk_plugin_registry_path(repo_root, "plugin", registry)
    target_path, target_rel = _sdk_plugin_validated_plugin_source(repo_root, target)
    plugin_name = (name or target_path.name).strip()
    entry = _sdk_plugin_marketplace_entry(plugin_name, target_rel)
    receipt = {
        "schema_version": "skills-sdk.plugin-registry-save.v1",
        "kind": "plugin",
        "target": target,
        "name": plugin_name,
        "status": _sdk_plugin_mode_status(apply),
        "registry_path": _sdk_plugin_relpath(repo_root, registry_path),
        "entry": entry,
        "mutation_performed": apply,
    }
    if not apply:
        return receipt
    _sdk_plugin_write_marketplace_entry(registry_path, plugin_name, entry)
    receipt["registry_written"] = True
    return receipt


def _sdk_plugin_validated_plugin_source(repo_root: Path, target: str) -> tuple[Path, str]:
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = repo_root / target_path
    try:
        target_rel = target_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"Plugin registry target must stay inside the repository: {target}.") from exc
    if not target_path.is_dir():
        raise ValueError(f"Plugin registry target does not exist: {target}.")
    if not (target_path / ".codex-plugin" / "plugin.json").is_file():
        raise ValueError(f"Plugin registry target is missing .codex-plugin/plugin.json: {target}.")
    return target_path, target_rel


def _sdk_plugin_marketplace_entry(plugin_name: str, target_rel: str) -> dict[str, Any]:
    return {
        "name": plugin_name,
        "category": "Productivity",
        "policy": {
            "authentication": "ON_INSTALL",
            "installation": "AVAILABLE",
            "products": ["CODEX"],
        },
        "source": {"source": "local", "path": f"./{target_rel}"},
    }


def _sdk_plugin_write_marketplace_entry(registry_path: Path, plugin_name: str, entry: dict[str, Any]) -> None:
    registry_payload = _sdk_plugin_read_json_object(
        registry_path,
        {
            "name": "agent-skills-local",
            "interface": {"displayName": "Local Plugins"},
            "plugins": [],
        },
    )
    plugins = registry_payload.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError(f"Registry field 'plugins' must be a list at {registry_path}.")
    replaced = False
    for index, item in enumerate(plugins):
        if isinstance(item, dict) and item.get("name") == plugin_name:
            plugins[index] = entry
            replaced = True
            break
    if not replaced:
        plugins.append(entry)
    plugins.sort(key=lambda item: str(item.get("name", "")) if isinstance(item, dict) else "")
    _sdk_plugin_atomic_write_json(registry_path, registry_payload)


def _sdk_command_extend(args: list[str], *pairs: tuple[str, str | None]) -> None:
    for flag, value in pairs:
        if value:
            args.extend([flag, value])


def _sdk_plugin_install_validation_command(
    *,
    kind: str,
    apply: bool,
    target: str | None = None,
    project_root: str | None = None,
    scope: str = "project",
    url: str | None = None,
    plugin_path: str | None = None,
    name: str | None = None,
    ref: str | None = None,
    dest: str = "Plugins/third-party",
    validation_level: str = "compat",
    allow_untrusted_source: bool = False,
    allow_unpinned_ref: bool = False,
    sync_profile: bool = False,
    require_desktop_loadable: bool = False,
) -> str:
    args = ["sdk", "plugin", "install", "--kind", kind]
    if kind == "skill":
        _sdk_command_extend(args, ("--target", target), ("--project-root", project_root))
        if scope != "project":
            args.extend(["--scope", scope])
    else:
        _sdk_command_extend(args, ("--url", url), ("--path", plugin_path), ("--name", name), ("--ref", ref))
        if dest != "Plugins/third-party":
            args.extend(["--dest", dest])
        if validation_level != "compat":
            args.extend(["--validation-level", validation_level])
        for enabled, flag in (
            (allow_untrusted_source, "--allow-untrusted-source"),
            (allow_unpinned_ref, "--allow-unpinned-ref"),
            (sync_profile, "--sync-profile"),
            (require_desktop_loadable, "--require-desktop-loadable"),
        ):
            if enabled:
                args.append(flag)
    args.append("--apply" if apply else "--preview")
    return _ask_validation_command(*args)


def skills_sdk_plugin_create(
    repo_root: Path,
    *,
    kind: str,
    name: str,
    category: str,
    description: str | None = None,
    with_registry: bool = False,
    companion_folders: list[str] | None = None,
    apply: bool = False,
) -> CallResult:
    """Create or preview creation of a single skill or plugin through the SDK facade."""
    command = _ask_validation_command(
        "sdk",
        "plugin",
        "create",
        name,
        "--kind",
        kind,
        "--category",
        category,
        "--apply" if apply else "--preview",
    )
    if kind == "skill" and not description:
        payload = {
            "schema_version": "skills-sdk-plugin-create.v0",
            "status": "blocked",
            "kind": kind,
            "name": name,
            "mutation_performed": False,
            "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "create"),
            "validation_commands": [command],
            "agent_summary": "Skill creation requires --description so the routing contract is not blank.",
        }
        return _sdk_plugin_result(
            command="sdk plugin create",
            payload_key="skills_sdk_plugin_create",
            payload=payload,
            error_message=payload["agent_summary"],
            fix_suggestion="Add --description before applying or previewing a skill scaffold.",
        )

    if not apply:
        lower_command = (
            _skills_validation_command("init", name, "--category", category, "--description", description or "")
            if kind == "skill"
            else _ask_validation_command("plugins", "create", name, "--category", category)
        )
        if kind == "plugin" and with_registry:
            lower_command = f"{lower_command} --with-marketplace"
        payload = {
            "schema_version": "skills-sdk-plugin-create.v0",
            "status": "preview",
            "kind": kind,
            "name": name,
            "category": category,
            "with_registry": with_registry,
            "planned_commands": [lower_command, command],
            "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "create"),
            "mutation_performed": False,
            "agent_summary": f"SDK plugin create preview planned {kind} creation without writes.",
        }
        return _sdk_plugin_result(command="sdk plugin create", payload_key="skills_sdk_plugin_create", payload=payload)

    if kind == "skill":
        delegated = init_skill(repo_root, name=name, category=category, description=description or "")
        artifact_target = f"Skills/{category}/{name}" if not category.startswith("Skills/") else f"{category}/{name}"
    else:
        from ask.commands.plugins import init_plugin  # noqa: PLC0415

        delegated = init_plugin(
            repo_root,
            name=name,
            category=category,
            with_marketplace=with_registry,
            companion_folders=companion_folders or [],
            action="create",
        )
        artifact_target = str(delegated.data.get("plugin_root") or f"Plugins/{category}/{name}")
    registry_receipt = None
    if with_registry and delegated.status == "success":
        try:
            registry_receipt = (
                _sdk_plugin_save_skill_registry_receipt(
                    repo_root,
                    target=f"{artifact_target}/SKILL.md",
                    registry=None,
                    name=name,
                    apply=True,
                )
                if kind == "skill"
                else _sdk_plugin_save_plugin_registry_receipt(
                    repo_root,
                    target=artifact_target,
                    registry=None,
                    name=name,
                    apply=True,
                )
            )
        except ValueError as exc:
            delegated.status = "error"
            delegated.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion="Fix the local registry JSON before retrying registry save.",
                )
            )
    payload = {
        "schema_version": "skills-sdk-plugin-create.v0",
        "status": "applied" if delegated.status == "success" else "blocked",
        "kind": kind,
        "name": name,
        "category": category,
        "with_registry": with_registry,
        "delegated_command_status": delegated.status,
        "delegated_data": delegated.data,
        "registry_receipt": registry_receipt,
        "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "create"),
        "mutation_performed": True,
        "validation_commands": [command],
        "agent_summary": f"SDK plugin create delegated {kind} creation through the bounded factory command.",
    }
    result = _sdk_plugin_result(command="sdk plugin create", payload_key="skills_sdk_plugin_create", payload=payload)
    result.status = delegated.status
    result.errors.extend(delegated.errors)
    return result


def skills_sdk_plugin_review(
    repo_root: Path,
    *,
    kind: str,
    target: str,
    strict: bool = False,
    execute: bool = False,
) -> CallResult:
    """Review or preview review of a single skill or plugin through SDK guardrails."""
    command = _ask_validation_command(
        "sdk",
        "plugin",
        "review",
        target,
        "--kind",
        kind,
        "--execute" if execute else "--preview",
    )
    planned = (
        [_ask_validation_command("sdk", "check", target, "--strict" if strict else "")]
        if kind == "skill"
        else [_ask_validation_command("plugins", "harden", target)]
    )
    planned = [item.strip() for item in planned]
    if not execute:
        payload = {
            "schema_version": "skills-sdk-plugin-review.v0",
            "status": "preview",
            "kind": kind,
            "target": target,
            "planned_commands": planned,
            "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "review"),
            "mutation_performed": False,
            "agent_summary": f"SDK plugin review preview planned {kind} guardrails without running checks.",
        }
        return _sdk_plugin_result(command="sdk plugin review", payload_key="skills_sdk_plugin_review", payload=payload)
    if kind == "skill":
        delegated = skills_sdk_check(repo_root, target=target, strict=strict, codex_parity=False)
    else:
        from ask.commands.plugins import harden_plugin  # noqa: PLC0415

        delegated = harden_plugin(repo_root, plugin_path=target, require_marketplace=strict)
    payload = {
        "schema_version": "skills-sdk-plugin-review.v0",
        "status": "passed" if delegated.status == "success" else "blocked",
        "kind": kind,
        "target": target,
        "delegated_command_status": delegated.status,
        "delegated_data": delegated.data,
        "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "review"),
        "mutation_performed": False,
        "validation_commands": [command],
        "agent_summary": f"SDK plugin review executed bounded {kind} checks.",
    }
    result = _sdk_plugin_result(command="sdk plugin review", payload_key="skills_sdk_plugin_review", payload=payload)
    result.status = delegated.status
    result.errors.extend(delegated.errors)
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
