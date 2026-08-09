from .skills_impl_sdk_calibration import *  # noqa: F403

def skills_sdk_plugin_install(
    repo_root: Path,
    *,
    kind: str,
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
    apply: bool = False,
) -> CallResult:
    """Install or preview install of a single skill or plugin through SDK guardrails."""
    command_args = {
        "kind": kind,
        "target": target,
        "project_root": project_root,
        "scope": scope,
        "url": url,
        "plugin_path": plugin_path,
        "name": name,
        "ref": ref,
        "dest": dest,
        "validation_level": validation_level,
        "allow_untrusted_source": allow_untrusted_source,
        "allow_unpinned_ref": allow_unpinned_ref,
        "sync_profile": sync_profile,
        "require_desktop_loadable": require_desktop_loadable,
        "apply": apply,
    }
    command = _sdk_plugin_install_validation_command(**command_args)
    if kind == "skill":
        if not target:
            return _sdk_plugin_install_blocked(kind, command, "Skill install requires --target.", "Pass --target <skill-handle-or-path>.")
        delegated = (
            skills_sdk_project_install(repo_root, target=target, project_root=project_root, scope=scope)
            if apply
            else skills_sdk_install_preview(repo_root, target=target, scope=scope)
        )
    else:
        if not url or not plugin_path:
            return _sdk_plugin_install_blocked(kind, command, "Plugin install requires --url and --path.", "Pass --url <repo-url> --path <plugin-path>.")
        delegated = _sdk_plugin_install_delegated(repo_root, command_args)
    payload = _sdk_plugin_install_payload(kind, target, apply, command, delegated)
    result = _sdk_plugin_result(command="sdk plugin install", payload_key="skills_sdk_plugin_install", payload=payload)
    result.status = delegated.status
    result.errors.extend(delegated.errors)
    return result


def _sdk_plugin_install_blocked(kind: str, command: str, message: str, fix_suggestion: str) -> CallResult:
    payload = {
        "schema_version": "skills-sdk-plugin-install.v0",
        "status": "blocked",
        "kind": kind,
        "mutation_performed": False,
        "validation_commands": [command],
        "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "install"),
        "agent_summary": message,
    }
    return _sdk_plugin_result(
        command="sdk plugin install",
        payload_key="skills_sdk_plugin_install",
        payload=payload,
        error_message=message,
        fix_suggestion=fix_suggestion,
    )


def _sdk_plugin_install_delegated(repo_root: Path, args: dict[str, Any]) -> CallResult:
    from ask.commands.plugins import install_plugin  # noqa: PLC0415

    return install_plugin(
        repo_root,
        url=args["url"],
        plugin_path=args["plugin_path"],
        name=args["name"],
        ref=args["ref"],
        dest=args["dest"],
        validation_level=args["validation_level"],
        allow_untrusted_source=args["allow_untrusted_source"],
        allow_unpinned_ref=args["allow_unpinned_ref"],
        sync_profile=args["sync_profile"],
        require_desktop_loadable=args["require_desktop_loadable"],
        dry_run=not args["apply"],
        action="install",
    )


def _sdk_plugin_install_payload(
    kind: str,
    target: str | None,
    apply: bool,
    command: str,
    delegated: CallResult,
) -> dict[str, Any]:
    status = "applied" if apply and delegated.status == "success" else ("preview" if not apply else "blocked")
    return {
        "schema_version": "skills-sdk-plugin-install.v0",
        "status": status,
        "kind": kind,
        "target": target,
        "delegated_command_status": delegated.status,
        "delegated_data": delegated.data,
        "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "install"),
        "mutation_performed": apply,
        "validation_commands": [command],
        "agent_summary": f"SDK plugin install {'applied' if apply else 'previewed'} {kind} install through bounded lifecycle commands.",
    }


def skills_sdk_plugin_save_registry(
    repo_root: Path,
    *,
    kind: str,
    target: str,
    registry: str | None = None,
    name: str | None = None,
    apply: bool = False,
) -> CallResult:
    """Save or preview saving a single skill or plugin in the local SDK registry/marketplace."""
    command = _ask_validation_command(
        "sdk",
        "plugin",
        "save-registry",
        "--kind",
        kind,
        "--target",
        target,
        "--apply" if apply else "--preview",
    )
    try:
        receipt = (
            _sdk_plugin_save_skill_registry_receipt(
                repo_root,
                target=target,
                registry=registry,
                name=name,
                apply=apply,
            )
            if kind == "skill"
            else _sdk_plugin_save_plugin_registry_receipt(
                repo_root,
                target=target,
                registry=registry,
                name=name,
                apply=apply,
            )
        )
    except (OSError, ValueError) as exc:
        payload = {
            "schema_version": "skills-sdk-plugin-save-registry.v0",
            "status": "blocked",
            "kind": kind,
            "target": target,
            "receipt": None,
            "mutation_performed": False,
            "validation_commands": [command],
            "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "save-registry"),
            "agent_summary": f"SDK plugin registry save is blocked: {exc}",
        }
        return _sdk_plugin_result(
            command="sdk plugin save-registry",
            payload_key="skills_sdk_plugin_save_registry",
            payload=payload,
            error_message=payload["agent_summary"],
            fix_suggestion="Fix the local registry path or JSON shape before retrying.",
        )
    payload = {
        "schema_version": "skills-sdk-plugin-save-registry.v0",
        "status": receipt["status"],
        "kind": kind,
        "target": target,
        "receipt": receipt,
        "remote_publish_performed": False,
        "mutation_performed": apply,
        "validation_commands": [command],
        "first_principles_gate": _sdk_plugin_first_principles_gate(kind, "save-registry"),
        "agent_summary": (
            f"SDK plugin registry save {'wrote' if apply else 'previewed'} local {kind} registry state; remote publish was not performed."
        ),
    }
    return _sdk_plugin_result(command="sdk plugin save-registry", payload_key="skills_sdk_plugin_save_registry", payload=payload)


def skills_sdk_eval_regression_plan(
    repo_root: Path,
    *,
    view_json: str,
    skill: str,
    run_id: str | None = None,
    plan_json: str | None = None,
) -> CallResult:
    """Preview an owner-classified regression plan from Tessl score evidence."""
    result = CallResult()
    result.metadata["command"] = "sdk eval regression-plan"
    view_path = Path(view_json)
    if not view_path.is_absolute():
        view_path = repo_root / view_path
    plan_path = Path(plan_json) if plan_json else None
    if plan_path and not plan_path.is_absolute():
        plan_path = repo_root / plan_path

    query = skill.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_regression_plan"] = {
            "schema_version": "skills-sdk-eval-regression-plan.v0",
            "status": "blocked",
            "ready_for_live_rerun": False,
            "skill": skill,
            "run_id": run_id or "",
            "receipt": None,
            "mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "eval", "regression-plan", "--view-json", view_json, "--skill", skill, "--preview")
            ],
            "agent_summary": f"skills-sdk eval regression-plan is blocked for {skill}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK regression plan is missing a canonical SKILL.md source for '{skill}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "regression-plan", "--view-json", "<view-json>", "--skill", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.regression_plan import build_regression_plan_receipt  # noqa: PLC0415

    receipt = build_regression_plan_receipt(
        repo_root,
        view_json=view_path,
        source_path=source_path,
        query=skill,
        run_id=run_id,
        plan_path=plan_path,
    )
    payload = {
        "schema_version": "skills-sdk-eval-regression-plan.v0",
        "status": receipt["status"],
        "ready_for_live_rerun": receipt["ready_for_live_rerun"],
        "skill": skill,
        "run_id": receipt["run_id"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "eval", "regression-plan", "--view-json", view_json, "--skill", skill, "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_regression_plan"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command(
                    "sdk",
                    "eval",
                    "regression-plan",
                    "--view-json",
                    view_json,
                    "--skill",
                    skill,
                    "--preview",
                ),
            )
        )
    return result


def skills_sdk_eval_handoff_readiness(
    repo_root: Path,
    *,
    skill: str,
    receipt_json: str | None = None,
    tessl_score: str | None = None,
) -> CallResult:
    """Preview whether the required local/internal evidence lanes are ready for live Tessl."""
    result = CallResult()
    result.metadata["command"] = "sdk eval handoff-readiness"
    readiness_path = Path(receipt_json) if receipt_json else None
    if readiness_path and not readiness_path.is_absolute():
        readiness_path = repo_root / readiness_path
    tessl_score_path = Path(tessl_score) if tessl_score else None
    if tessl_score_path and not tessl_score_path.is_absolute():
        tessl_score_path = repo_root / tessl_score_path

    query = skill.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_handoff_readiness"] = {
            "schema_version": "skills-sdk-eval-handoff-readiness.v0",
            "status": "blocked",
            "ready_for_live_tessl": False,
            "skill": skill,
            "receipt": None,
            "mutation_performed": False,
            "validation_commands": [
                _ask_validation_command("sdk", "eval", "handoff-readiness", "--skill", skill, "--preview")
            ],
            "agent_summary": f"skills-sdk eval handoff-readiness is blocked for {skill}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK handoff readiness is missing a canonical SKILL.md source for '{skill}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "handoff-readiness", "--skill", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.handoff_readiness import build_handoff_readiness_receipt  # noqa: PLC0415

    receipt = build_handoff_readiness_receipt(
        repo_root,
        source_path=source_path,
        query=skill,
        readiness_path=readiness_path,
        tessl_score_path=tessl_score_path,
    )
    payload = {
        "schema_version": "skills-sdk-eval-handoff-readiness.v0",
        "status": receipt["status"],
        "ready_for_live_tessl": receipt["ready_for_live_tessl"],
        "skill": skill,
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "handoff-readiness",
                "--skill",
                skill,
                *("--tessl-score", tessl_score) if tessl_score else (),
                "--preview",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_handoff_readiness"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command("sdk", "eval", "handoff-readiness", "--skill", skill, "--preview"),
            )
        )
    return result


def skills_sdk_observability_promote(
    repo_root: Path,
    *,
    feedback_receipt: str,
    package_receipt: str,
    eval_run_receipt: str,
) -> CallResult:
    """Preview whether observability feedback candidates can advance after package and eval proof."""
    result = CallResult()
    result.metadata["command"] = "sdk observability promote"
    from ask.skills_sdk.observability_promotion import build_observability_promotion_receipt  # noqa: PLC0415

    promotion_receipt = build_observability_promotion_receipt(
        repo_root,
        feedback_receipt_path=feedback_receipt,
        package_receipt_path=package_receipt,
        eval_run_receipt_path=eval_run_receipt,
    )
    payload = {
        "schema_version": "skills-sdk-observability-promotion.v0",
        "status": promotion_receipt["status"],
        "facade_command": "skills-sdk observability promote",
        "package_id": promotion_receipt["package_id"],
        "package_digest": promotion_receipt["package_digest"],
        "receipt": promotion_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "observability",
                "promote",
                "--feedback-receipt",
                feedback_receipt,
                "--package-receipt",
                package_receipt,
                "--eval-run-receipt",
                eval_run_receipt,
                "--preview",
            )
        ],
        "agent_summary": promotion_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_promote"] = payload
    if promotion_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=(
                    "Provide matching observability feedback, package digest, and passing eval-run receipts "
                    "for the same package id and digest."
                ),
            )
        )
    return result


def skills_sdk_observability_phoenix_status(
    repo_root: Path,
    *,
    base_url: str,
    timeout_seconds: float,
) -> CallResult:
    """Check that the configured Phoenix OSS endpoint is reachable."""
    result = CallResult()
    result.metadata["command"] = "sdk observability phoenix-status"
    from ask.skills_sdk.phoenix_observability import build_phoenix_status_receipt  # noqa: PLC0415

    status_receipt = build_phoenix_status_receipt(
        repo_root,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )
    payload = {
        "schema_version": "skills-sdk-observability-phoenix-status.v0",
        "status": status_receipt["status"],
        "facade_command": "skills-sdk observability phoenix-status",
        "receipt": status_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "observability",
                "phoenix-status",
                "--base-url",
                base_url,
            )
        ],
        "agent_summary": status_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_phoenix_status"] = payload
    if status_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message=payload["agent_summary"],
                fix_suggestion="Start Phoenix OSS with Docker and rerun the status check.",
            )
        )
    return result


def skills_sdk_observability_phoenix_smoke(
    repo_root: Path,
    *,
    base_url: str,
    profile: str,
    timeout_seconds: float,
    otel_python_path: str | None,
    model_name: str | None,
    provider: str | None,
    prompt_tokens: int,
    completion_tokens: int,
) -> CallResult:
    """Emit a deterministic smoke trace to the configured Phoenix OSS endpoint."""
    result = CallResult()
    result.metadata["command"] = "sdk observability phoenix-smoke"
    from ask.skills_sdk.phoenix_observability import build_phoenix_smoke_receipt  # noqa: PLC0415

    smoke_receipt = build_phoenix_smoke_receipt(
        repo_root,
        base_url=base_url,
        profile=profile,
        timeout_seconds=timeout_seconds,
        otel_python_path=otel_python_path,
        model_name=model_name,
        provider=provider,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )
    payload = {
        "schema_version": "skills-sdk-observability-phoenix-smoke.v0",
        "status": smoke_receipt["status"],
        "facade_command": "skills-sdk observability phoenix-smoke",
        "receipt": smoke_receipt,
        "mutation_performed": smoke_receipt["mutation_performed"],
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "observability",
                "phoenix-smoke",
                "--base-url",
                base_url,
                "--profile",
                profile,
                *("--otel-python", otel_python_path) if otel_python_path else (),
                *("--model", model_name) if model_name else (),
                *("--provider", provider) if provider else (),
                "--prompt-tokens",
                str(prompt_tokens),
                "--completion-tokens",
                str(completion_tokens),
            )
        ],
        "agent_summary": smoke_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_phoenix_smoke"] = payload
    if smoke_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message=payload["agent_summary"],
                fix_suggestion="Start Phoenix OSS and ensure ~/.agents/otel-collector has opentelemetry-proto available.",
            )
        )
    return result


def skills_sdk_observability_phoenix_mirror(
    repo_root: Path,
    *,
    receipt_path: str,
    out_path: str | None,
    write: bool,
) -> CallResult:
    """Build or write a redacted Phoenix-ready JSONL mirror from a repo receipt."""
    result = CallResult()
    result.metadata["command"] = "sdk observability phoenix-mirror"
    from ask.skills_sdk.phoenix_observability import (  # noqa: PLC0415
        PhoenixObservabilityError,
        build_phoenix_mirror_receipt,
    )

    try:
        mirror_receipt = build_phoenix_mirror_receipt(
            repo_root,
            receipt_path=receipt_path,
            out_path=out_path,
            write=write,
        )
    except PhoenixObservabilityError as exc:
        mirror_receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-observability-phoenix-mirror.v0",
        "status": mirror_receipt["status"],
        "facade_command": "skills-sdk observability phoenix-mirror",
        "receipt": mirror_receipt,
        "mutation_performed": mirror_receipt["mutation_performed"],
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "observability",
                "phoenix-mirror",
                "--receipt",
                receipt_path,
                *("--out", out_path) if out_path else (),
                "--write" if write else "--preview",
            )
        ],
        "agent_summary": mirror_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_phoenix_mirror"] = payload
    if mirror_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Provide a JSON receipt in the repo or /tmp, and use --out when writing a mirror artifact.",
            )
        )
    return result


def skills_sdk_eval_profiles_preview(repo_root: Path) -> CallResult:
    """Emit the non-mutating Codex execution and judge profile contract."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk eval profiles --preview"
    receipt = _build_eval_profile_preview_receipt()
    payload = {
        "schema_version": "skills-sdk-eval-profile-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval profiles",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "profiles", "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_profiles"] = payload
    return result


def skills_sdk_eval_ab_rubric_preview(repo_root: Path) -> CallResult:
    """Emit the non-mutating canonical A/B scoring rubric contract."""
    from ask.skills_sdk.eval_ab_rubric import (  # noqa: PLC0415
        build_ab_rubric_preview_receipt,
    )

    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-rubric --preview"
    receipt = build_ab_rubric_preview_receipt()
    payload = {
        "schema_version": "skills-sdk-ab-rubric.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-rubric",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "ab-rubric", "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_rubric"] = payload
    return result


def skills_sdk_eval_ab_preview(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    execution_profile: str = "codex-read-only",
    judge_profile: str = "oss-local",
) -> CallResult:
    """Emit a non-mutating Codex-backed A/B eval experiment contract."""
    from ask.skills_sdk.eval_ab_preview import build_ab_preview_receipt  # noqa: PLC0415

    result = CallResult()
    result.metadata["command"] = "sdk eval ab-preview --preview"
    skill_a_identity = _skills_sdk_eval_package_identity(repo_root, skill_a)
    skill_b_identity = _skills_sdk_eval_package_identity(repo_root, skill_b)
    receipt = build_ab_preview_receipt(
        repo_root,
        skill_a=skill_a,
        skill_b=skill_b,
        fixture=fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile,
        judge_profile_id=judge_profile,
    )
    payload = {
        "schema_version": "skills-sdk-ab-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-preview",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-preview",
                "--skill-a",
                skill_a,
                "--skill-b",
                skill_b,
                "--fixture",
                fixture,
                "--execution-profile",
                execution_profile,
                "--judge-profile",
                judge_profile,
                "--preview",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Use canonical repo-local skill sources and a repo-local fixture before running "
                    "ask sdk eval ab-preview."
                ),
            )
        )
    return result


@dataclass(frozen=True)
class AbEvalRequest:
    skill_a: str
    skill_b: str
    fixture: str
    execution_profile: str = "codex-read-only"
    judge_profile: str = "oss-local"
    execution_lane: str = "all"
    evidence_root: str = ".harness/artifacts/sdk-ab-evals"
    timeout_seconds: int = 1800

__all__ = [name for name in globals() if not name.startswith("__")]
