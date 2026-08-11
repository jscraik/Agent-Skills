from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from ask.skill_review_dashboard import dashboard_not_requested_receipt, render_optional_dashboard

from .skills_impl_audit_validation import *  # noqa: F403


@dataclass(frozen=True)
class ExternalReviewRequest:
    """Explicit policy inputs for one local external-review invocation."""

    skill_path: str
    audit_level: str = "strict"
    skip_plugin_eval: bool = False
    skip_tessl: bool = False
    with_tessl_review: bool = False
    skip_tessl_review: bool = False
    include_snyk: bool = False
    timeout_seconds: int = 180
    report_path: str | None = None
    dashboard: bool = False
    dashboard_path: str | None = None


@dataclass
class _ExternalReviewState:
    repo_root: Path
    request: ExternalReviewRequest
    result: CallResult
    audit_target: str = ""
    audit_target_path: str = ""
    target_abs: Path | None = None

    def error(self, code: str, message: str, suggestion: str) -> None:
        self.result.status = "error"
        self.result.errors.append(ErrorObject(code=code, message=message, fix_suggestion=suggestion))


_POLICY = MappingProxyType({
    "mode": "local_internal_only", "no_publish": True, "no_registry_upload": True,
    "uses_npx": False, "publish_policy": "never publish, register, upload, or invoke npx from this lane",
    "tessl_review_default": "disabled_requires_explicit_opt_in", "primary_gate": "local_eval_ask_audit",
    "external_quality_judge": "tessl_review_opt_in", "tessl_project_marker": "tessl.json",
    "tessl_evidence_retention": "stable tmp wrapper is intentionally left for inspection and copied-input evidence",
    "tessl_lint_role": "stable_plugin_packaging_shape_check", "tessl_lint_shape": "Tessl plugin lint expects a .tessl-plugin/plugin.json package. Canonical repo skills are SKILL.md-first, so this command builds a stable local plugin wrapper under /tmp before linting.",
    "tessl_review_role": "local_best_practice_content_review",
    "plugin_eval_role": "budget_and_ergonomics_guardrail", "snyk_role": "opt_in_local_dependency_security_screening",
    "snyk_default": "disabled_until_requested", "snyk_release_requirement": "release_required_for_manifest_backed_candidates",
    "plugin_eval_context_policy": "Plugin Eval scores the agent-loaded context view. SDK workbench files remain package-validated but are excluded from static context-budget scoring.",
    "snyk_when_to_use": ["when a skill or plugin candidate has dependency manifests", "when claiming release readiness for a manifest-backed skill or plugin package", "when dependency files, installer scripts, generated package surfaces, or plugin runtime dependencies changed", "when matching the CircleCI/Snyk security screening lane locally before or after CI", "when the user explicitly asks for Snyk, dependency vulnerability screening, or external security advisory evidence"],
    "snyk_when_not_to_use": ["pure SKILL.md-first instruction-only candidates with no supported dependency manifest, unless the user explicitly asks", "routine local iteration where external networked security analysis is not needed"],
    "snyk_privacy_basis": "Snyk CLI security analysis may contact Snyk services. It is never run by default in this local-first review lane; pass --include-snyk when external Snyk advisory analysis is wanted.",
})


def _coerce_external_review_request(
    request_or_skill_path: ExternalReviewRequest | str | None,
    legacy_options: dict[str, object],
) -> ExternalReviewRequest:
    """Accept the value-object contract while preserving existing callers."""
    if request_or_skill_path is None:
        request_or_skill_path = legacy_options.pop("skill_path", None)
    elif "skill_path" in legacy_options:
        raise TypeError("external_review_skill received both a positional request and skill_path keyword")
    if isinstance(request_or_skill_path, ExternalReviewRequest):
        if legacy_options:
            raise TypeError(f"ExternalReviewRequest does not accept legacy options: {', '.join(sorted(legacy_options))}")
        return request_or_skill_path
    if not isinstance(request_or_skill_path, str):
        raise TypeError("external_review_skill expects an ExternalReviewRequest or skill path string")
    allowed = set(ExternalReviewRequest.__dataclass_fields__) - {"skill_path"}
    unexpected = set(legacy_options) - allowed
    if unexpected:
        raise TypeError(f"external_review_skill received unexpected option(s): {', '.join(sorted(unexpected))}")
    return ExternalReviewRequest(skill_path=request_or_skill_path, **legacy_options)


def external_review_skill(
    repo_root: Path,
    request_or_skill_path: ExternalReviewRequest | str | None = None,
    **legacy_options: object,
) -> CallResult:
    """Run the local-only second-review lane for one skill."""
    state = _new_external_review_state(repo_root, request_or_skill_path, legacy_options)
    early_result = _prepare_external_review(state)
    if early_result is not None:
        return early_result
    _run_audit_lane(state)
    _run_plugin_eval_lane(state)
    _run_tessl_lane(state)
    _run_snyk_lane(state)
    return _persist_external_review(state)


def _new_external_review_state(
    repo_root: Path, request_or_skill_path: ExternalReviewRequest | str | None, legacy_options: dict[str, object],
) -> _ExternalReviewState:
    request = _coerce_external_review_request(request_or_skill_path, legacy_options)
    result = CallResult(status="success")
    result.data["dashboard"] = _initial_dashboard_receipt(request.dashboard)
    return _ExternalReviewState(repo_root=repo_root, request=request, result=result)


def _initial_dashboard_receipt(dashboard: bool) -> dict[str, str]:
    if dashboard:
        return {"status": "not_run", "reason": "review_not_completed", "tab": "quality"}
    return dashboard_not_requested_receipt(tab="quality")


def _prepare_external_review(state: _ExternalReviewState) -> CallResult | None:
    blocker = _review_flag_blocker(state)
    if blocker is not None:
        return blocker
    _, path_error = _validate_repo_relative_skill_path(state.repo_root, state.request.skill_path)
    if path_error:
        return path_error
    return _resolve_external_review_target(state)


def _review_flag_blocker(state: _ExternalReviewState) -> CallResult | None:
    request = state.request
    if not request.with_tessl_review or not (request.skip_tessl_review or request.skip_tessl):
        return None
    flag = "--skip-tessl-review" if request.skip_tessl_review else "--skip-tessl"
    message = f"--with-tessl-review cannot be combined with {flag}."
    state.result.data["external_review"] = {"status": "blocked", "blocker_class": "blocked_validation", "blocker": message}
    state.error("ERR_VALIDATION", message, "Remove one conflicting Tessl review flag and rerun.")
    return state.result


def _resolve_external_review_target(state: _ExternalReviewState) -> CallResult | None:
    state.audit_target, state.audit_target_path = _normalize_skill_target_path(state.request.skill_path)
    state.target_abs = (state.repo_root / state.audit_target).resolve()
    if state.target_abs.is_dir() and (state.target_abs / "SKILL.md").is_file():
        _set_external_review_metadata(state)
        return None
    state.error("ERR_VALIDATION", "Skill path must resolve to a directory containing SKILL.md.", f"Check the path and rerun against a canonical skill directory: {state.audit_target_path}")
    return state.result


def _set_external_review_metadata(state: _ExternalReviewState) -> None:
    state.result.data["policy"] = _external_review_policy()
    state.result.data["review_mode_details"] = _review_mode_details()
    state.result.data["target"] = state.audit_target_path
    state.result.data["validation_commands"] = [_skills_validation_command("external-review", *_external_review_args(state.request))]


def _external_review_policy() -> dict[str, object]:
    policy = dict(_POLICY)
    policy["tessl_review_min_score"] = TESSL_REVIEW_MIN_SCORE
    policy["tessl_review_target_score"] = TESSL_REVIEW_TARGET_SCORE
    policy["tessl_review_threshold_policy"] = f"Tessl review must return reviewScore >= {TESSL_REVIEW_MIN_SCORE}; {TESSL_REVIEW_TARGET_SCORE}+ remains the improvement target."
    policy["tessl_staging_root"] = f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-reviews')}/<skill-path>-<sha12>"
    policy["plugin_eval_excluded_package_surfaces"] = list(PLUGIN_EVAL_EXCLUDED_PACKAGE_SURFACES)
    policy["plugin_eval_min_acceptable_grade"] = PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE
    policy["plugin_eval_warning_policy"] = "Plugin Eval warnings are visible follow-up work, but they are not release blockers when there are zero Plugin Eval failures, the grade is B+ or better, and local/Tessl gates pass."
    policy["tessl_review_privacy_basis"] = "Tessl content review may use an external model-backed service; invoke it only with --with-tessl-review."
    return policy


def _review_mode_details() -> dict[str, object]:
    return {
        "local_evals": {"command": "./bin/ask evals run <path> --mode smoke|release --json --robot", "role": "dynamic run-trace behavior checks for skill selection, commands, artifacts, and release gates"},
        "plugin_eval": {"command": "plugin-eval analyze <path> --format markdown", "role": "static budget, ergonomics, and reviewability guardrail; not a substitute for local evals"},
        "tessl_lint": {"command": "tessl plugin lint <stable-plugin-directory>", "role": "stable .tessl-plugin/plugin.json package-shape check, not a direct content finding", "canonical_source_shape": "SKILL.md-first"},
        "tessl_review": {"command": f"tessl skill review --json --threshold {TESSL_REVIEW_MIN_SCORE} <stable-skill-directory>", "role": "explicitly requested external content review for private or work-in-progress skills", "default": "disabled_requires_--with-tessl-review", "minimum_score": TESSL_REVIEW_MIN_SCORE, "target_score": TESSL_REVIEW_TARGET_SCORE, "publishes": False},
        "snyk": {"command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>", "role": "opt-in local dependency security screening; release-required for manifest-backed candidates", "default": "disabled_until_requested", "release_required": "manifest-backed candidates", "use_when": ["candidate has supported dependency manifests", "release-readiness is claimed for a manifest-backed package", "dependency/runtime package surfaces changed", "local evidence must match CircleCI/Snyk screening", "user explicitly requests Snyk or dependency vulnerability evidence"]},
    }


def _external_review_args(request: ExternalReviewRequest) -> list[str]:
    args = [request.skill_path]
    options = ((request.audit_level != "strict", ["--audit-level", request.audit_level]), (request.skip_plugin_eval, ["--skip-plugin-eval"]), (request.skip_tessl, ["--skip-tessl"]), (request.with_tessl_review, ["--with-tessl-review"]), (request.skip_tessl_review, ["--skip-tessl-review"]), (request.include_snyk, ["--include-snyk"]), (request.timeout_seconds != 180, ["--timeout-seconds", str(request.timeout_seconds)]), (bool(request.report_path), ["--report-path", request.report_path]), (request.dashboard, ["--dashboard"]), (bool(request.dashboard_path), ["--dashboard-path", request.dashboard_path]))
    for enabled, option in options:
        if enabled:
            args.extend(option)
    return args


def _run_audit_lane(state: _ExternalReviewState) -> None:
    audit = audit_skill(state.repo_root, state.audit_target_path, level=state.request.audit_level)
    state.result.data["ask_audit"] = {"status": audit.status, "data": audit.data, "errors": [getattr(error, "__dict__", error) for error in audit.errors]}
    if audit.status != "success":
        state.error("ERR_VALIDATION", "Internal ask skill audit failed during external-review lane.", "Inspect data.ask_audit for the exact failing gate.")


def _run_plugin_eval_lane(state: _ExternalReviewState) -> None:
    if state.request.skip_plugin_eval:
        state.result.data["plugin_eval"] = {"status": "skipped"}
        return
    plugin_eval_bin = shutil.which("plugin-eval")
    if not plugin_eval_bin:
        state.result.data["plugin_eval"] = {"status": "blocked_missing_binary", "command": "plugin-eval analyze"}
        state.error("ERR_DEPENDENCY", "plugin-eval is not installed or not on PATH.", "Install or expose plugin-eval, then rerun this local-only review lane.")
        return
    assert state.target_abs is not None
    target, context = _stage_plugin_eval_agent_context(state.repo_root, state.target_abs, state.audit_target)
    state.result.data["plugin_eval_context"] = context
    _capture_plugin_eval(state, [plugin_eval_bin, "analyze", target.as_posix(), "--format", "markdown"])


def _capture_plugin_eval(state: _ExternalReviewState, command: list[str]) -> None:
    try:
        proc = _run_captured_tool(repo_root=state.repo_root, command=command, timeout_seconds=state.request.timeout_seconds)
    except subprocess.TimeoutExpired:
        state.result.data["plugin_eval"] = {"status": "timeout", "command": command, "timeout_seconds": state.request.timeout_seconds}
        state.error("ERR_RUNTIME", f"plugin-eval timed out after {state.request.timeout_seconds} seconds.", "Rerun with a higher --timeout-seconds value if the target is intentionally large.")
        return
    payload = _completed_process_payload(proc)
    payload["status"] = "success" if proc.returncode == 0 else "error"
    payload["summary"] = _parse_plugin_eval(payload.get("stdout", ""), payload["status"])
    state.result.data["plugin_eval"] = payload
    _apply_plugin_eval_outcome(state, proc.returncode, payload["summary"])


def _apply_plugin_eval_outcome(state: _ExternalReviewState, returncode: int, summary: dict[str, object]) -> None:
    if returncode:
        state.error("ERR_VALIDATION", "plugin-eval analysis failed during external-review lane.", "Inspect data.plugin_eval for full output.")
        return
    failed = summary.get("blocking_fail_count", summary.get("fail_count", 0))
    if failed or not summary.get("grade_acceptable", False):
        state.error("ERR_VALIDATION", f"Plugin Eval did not meet the local acceptance floor ({PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE} with zero failures).", "Inspect data.plugin_eval.summary for grade, fail count, and follow-up findings.")


def _run_tessl_lane(state: _ExternalReviewState) -> None:
    if state.request.skip_tessl:
        _record_skipped_tessl(state)
        return
    tessl_bin = shutil.which("tessl")
    if not tessl_bin:
        state.result.data["tessl_lint"] = {"status": "blocked_missing_binary", "command": "tessl plugin lint"}
        state.error("ERR_DEPENDENCY", "Tessl CLI is not installed or not on PATH; Tessl local lint in the Second-Review Lane could not run.", "Install Tessl as a local machine tool and rerun. This command will not invoke npx or publish anything.")
        return
    wrapper = _prepare_tessl_wrapper(state)
    if wrapper is None:
        return
    staging_root, plugin_info = wrapper
    _capture_tessl_lint(state, tessl_bin, staging_root)
    _capture_tessl_review(state, tessl_bin, plugin_info)


def _record_skipped_tessl(state: _ExternalReviewState) -> None:
    state.result.data["tessl_lint"] = {"status": "skipped"}
    state.result.data["tessl_review"] = {"status": "skipped", "minimum_score": TESSL_REVIEW_MIN_SCORE, "target_score": TESSL_REVIEW_TARGET_SCORE}


def _prepare_tessl_wrapper(state: _ExternalReviewState) -> tuple[Path, dict[str, object]] | None:
    try:
        staging_root, plugin_info = _write_tessl_plugin_wrapper(state.repo_root, state.audit_target_path, _stable_tessl_review_root(state.audit_target_path))
    except ValueError as exc:
        state.result.data["tessl_plugin"] = {"status": "blocked_validation", "message": str(exc)}
        state.error("ERR_VALIDATION", str(exc), "Replace symlinked skill review inputs with regular files or directories before Tessl staging.")
        return None
    state.result.data["tessl_plugin"] = {**plugin_info, "mode": "stable_tmp_wrapper", "reason": "Tessl plugin lint validates .tessl-plugin/plugin.json packages. Canonical repo skills remain SKILL.md-first, so this command stages a local plugin-shaped wrapper under /tmp.", "auth_home": "process_home", "support_refs_included": True}
    return staging_root, plugin_info


def _capture_tessl_lint(state: _ExternalReviewState, tessl_bin: str, staging_root: Path) -> None:
    command = [tessl_bin, "plugin", "lint", str(staging_root)]
    try:
        proc = _run_captured_tool(repo_root=state.repo_root, command=command, timeout_seconds=state.request.timeout_seconds, env_overrides={})
    except subprocess.TimeoutExpired:
        state.result.data["tessl_lint"] = {"status": "timeout", "command": command, "timeout_seconds": state.request.timeout_seconds}
        state.error("ERR_RUNTIME", f"Tessl skill lint timed out after {state.request.timeout_seconds} seconds.", "Check the local Tessl installation and rerun once it responds normally.")
        return
    payload = _completed_process_payload(proc)
    payload["status"] = "success" if proc.returncode == 0 else "error"
    state.result.data["tessl_lint"] = payload
    if proc.returncode:
        state.error("ERR_VALIDATION", "Tessl skill lint failed during local-only external review.", "Inspect data.tessl_lint for Tessl's validation output.")


def _capture_tessl_review(state: _ExternalReviewState, tessl_bin: str, plugin_info: dict[str, object]) -> None:
    if not state.request.with_tessl_review:
        state.result.data["tessl_review"] = {"status": "skipped", "reason": "Disabled by default; pass --with-tessl-review to run model-backed Tessl content review.", "minimum_score": TESSL_REVIEW_MIN_SCORE, "target_score": TESSL_REVIEW_TARGET_SCORE}
        return
    command = [tessl_bin, "skill", "review", "--json", "--threshold", str(TESSL_REVIEW_MIN_SCORE), str(plugin_info["review_path"])]
    try:
        proc = _run_captured_tool(repo_root=state.repo_root, command=command, timeout_seconds=state.request.timeout_seconds, env_overrides={})
    except subprocess.TimeoutExpired:
        state.result.data["tessl_review"] = {"status": "timeout", "command": command, "timeout_seconds": state.request.timeout_seconds}
        state.error("ERR_RUNTIME", f"Tessl skill review timed out after {state.request.timeout_seconds} seconds.", "Check the local Tessl installation and rerun once it responds normally.")
        return
    payload = _completed_process_payload(proc)
    payload["status"] = "success" if proc.returncode == 0 else "error"
    payload["summary"] = _parse_tessl_review_output(payload.get("stdout", ""), payload["status"])
    payload["minimum_score"], payload["target_score"] = TESSL_REVIEW_MIN_SCORE, TESSL_REVIEW_TARGET_SCORE
    state.result.data["tessl_review"] = payload
    if proc.returncode:
        state.error("ERR_VALIDATION", f"Tessl skill review did not meet the >= {TESSL_REVIEW_MIN_SCORE} threshold.", "Inspect data.tessl_review for full output and the staged wrapper path.")


def _run_snyk_lane(state: _ExternalReviewState) -> None:
    if not state.request.include_snyk:
        state.result.data["snyk"] = {"status": "skipped", "reason": "Snyk is disabled by default. Use --include-snyk when external Snyk advisory analysis is wanted."}
        return
    snyk_bin = shutil.which("snyk")
    if not snyk_bin:
        state.result.data["snyk"] = {"status": "blocked_missing_binary", "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>"}
        state.error("ERR_DEPENDENCY", "Snyk CLI is not installed or not on PATH.", "Install or expose the Snyk CLI, authenticate it if required, then rerun with --include-snyk.")
        return
    command = [snyk_bin, "test", "--all-projects", "--detection-depth=6", "--severity-threshold=high", "--json", state.audit_target_path]
    _capture_snyk(state, command)


def _capture_snyk(state: _ExternalReviewState, command: list[str]) -> None:
    try:
        proc = _run_captured_tool(repo_root=state.repo_root, command=command, timeout_seconds=state.request.timeout_seconds)
    except subprocess.TimeoutExpired:
        state.result.data["snyk"] = {"status": "timeout", "command": command, "timeout_seconds": state.request.timeout_seconds}
        state.error("ERR_RUNTIME", f"Snyk timed out after {state.request.timeout_seconds} seconds.", "Check the local Snyk CLI/auth state and rerun with a higher --timeout-seconds value if needed.")
        return
    payload = _completed_process_payload(proc)
    payload["status"] = _snyk_status(proc)
    if payload["status"] == "not_applicable":
        payload["reason"] = "Snyk found no supported dependency manifest under this skill. SKILL.md-first skills are still covered by the internal audit, security evals, and OpenClaw guard."
    state.result.data["snyk"] = payload
    _apply_snyk_outcome(state, payload["status"])


def _snyk_status(proc: subprocess.CompletedProcess[str]) -> str:
    text = f"{proc.stdout}\n{proc.stderr}".lower()
    if proc.returncode == 0:
        return "success"
    if "could not detect supported target files" in text or "no supported files" in text:
        return "not_applicable"
    if any(marker in text for marker in ("use snyk auth", "not authenticated", "authentication required", "snyk_token")):
        return "blocked_auth"
    return "advisory" if proc.returncode == 1 else "error"


def _apply_snyk_outcome(state: _ExternalReviewState, status: str) -> None:
    if status == "blocked_auth":
        state.error("ERR_AUTH", "Snyk authentication is required for the external security lane.", "Run snyk auth locally or set SNYK_TOKEN in CI, then rerun with --include-snyk.")
    elif status in {"advisory", "error"}:
        state.error("ERR_VALIDATION", "Snyk reported an advisory or failed during the external security lane.", "Inspect data.snyk for vulnerability details, unsupported-project output, or authentication errors.")


def _persist_external_review(state: _ExternalReviewState) -> CallResult:
    target, path_error = _external_review_report_target(state)
    if path_error:
        return path_error
    if target is None:
        return state.result
    if not state.request.dashboard:
        _write_external_review_report(state, target)
        _record_report_path(state, target)
        return state.result
    return _render_external_review_dashboard(state, target)


def _external_review_report_target(state: _ExternalReviewState) -> tuple[Path | None, CallResult | None]:
    if state.request.report_path:
        target, error = _validate_repo_relative_skill_path(state.repo_root, state.request.report_path)
        return target, error
    if state.request.dashboard:
        assert state.target_abs is not None
        return (state.repo_root / "Infrastructure" / "artifacts" / "skill-reviews" / f"{state.target_abs.name}.json").resolve(), None
    return None, None


def _write_external_review_report(state: _ExternalReviewState, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": state.result.status, "data": state.result.data, "errors": [getattr(error, "__dict__", error) for error in state.result.errors]}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _record_report_path(state: _ExternalReviewState, target: Path) -> None:
    state.result.data["report_path"] = target.relative_to(state.repo_root.resolve()).as_posix()


def _render_external_review_dashboard(state: _ExternalReviewState, report_target: Path) -> CallResult:
    dashboard_target, path_error = _external_dashboard_target(state, report_target)
    if path_error:
        return path_error
    assert dashboard_target is not None
    rendered, receipt = render_optional_dashboard(lambda: _render_dashboard_file(state, report_target, dashboard_target), tab="quality")
    state.result.data["dashboard"] = receipt
    if rendered is None:
        state.result.data.pop("dashboard_path", None)
        state.result.data.pop("dashboard_url", None)
        return state.result
    relative = rendered.relative_to(state.repo_root.resolve()).as_posix()
    state.result.data["dashboard_path"] = relative
    state.result.data["dashboard_url"] = relative
    return state.result


def _external_dashboard_target(state: _ExternalReviewState, report_target: Path) -> tuple[Path | None, CallResult | None]:
    if state.request.dashboard_path:
        return _validate_repo_relative_skill_path(state.repo_root, state.request.dashboard_path)
    return report_target.with_suffix(".html"), None


def _render_dashboard_file(state: _ExternalReviewState, report_target: Path, dashboard_target: Path) -> Path:
    _write_external_review_report(state, report_target)
    _record_report_path(state, report_target)
    rendered = render_skill_review_dashboard(report_path=report_target, output_path=dashboard_target, repo_root=state.repo_root)
    relative = rendered.relative_to(state.repo_root.resolve()).as_posix()
    state.result.data["dashboard"] = {"status": "rendered", "tab": "quality"}
    state.result.data["dashboard_path"] = relative
    state.result.data["dashboard_url"] = relative
    _write_external_review_report(state, report_target)
    return rendered


def validate_skill_boundaries(repo_root: Path, handle: str) -> CallResult:
    """Resolve a handle and expose canonical-versus-projection ownership boundaries."""
    resolved = skills_explain_boundary(repo_root, handle)
    if resolved.status != "success":
        return resolved
    resolved.data["validation_commands"] = [_skills_validation_command("validate-boundaries", handle)]
    return resolved


def skills_explain_boundary(repo_root: Path, handle: str) -> CallResult:
    """Return compact SDK source/projection ownership for one skill handle."""
    result = skills_resolve(repo_root, handle=handle)
    if result.status != "success":
        return result
    resolution = result.data.get("resolution", {})
    canonical_path = resolution.get("canonical_skill_path") or resolution.get("source_path")
    notes = ["Edit the canonical source path and regenerate or verify projections after changes."] if canonical_path else []
    result.data = {"boundary_check": {"handle": resolution.get("handle", handle.lstrip("$")), "status": "pass", "canonical_skill_path": canonical_path, "runtime_projection_path": resolution.get("runtime_projection_path"), "runtime_visibility": resolution.get("runtime_visibility"), "handle_source": resolution.get("handle_source"), "projection_mode": resolution.get("projection_mode"), "notes": notes}}
    return result


def _resolve_canonical_install_dest(repo_root: Path, dest: str) -> tuple[Path, str]:
    """Resolve a category token to a canonical repository-relative install destination."""
    raw_dest = Path((dest or "Skills/github").strip() or "Skills/github")
    if raw_dest.is_absolute():
        raise ValueError("Destination must be repo-relative (for example: Skills/github or Skills/backend).")
    resolved_root = repo_root.resolve()
    resolved_dest = (repo_root / raw_dest).resolve()
    try:
        rel_dest = resolved_dest.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Destination escapes repository root.") from exc
    if len(rel_dest.parts) == 1:
        rel_dest = Path("Skills") / rel_dest
        resolved_dest = (repo_root / rel_dest).resolve()
    if len(rel_dest.parts) != 2 or rel_dest.parts[0] != "Skills":
        raise ValueError("Destination must be under Skills/<category>.")
    if resolved_dest.exists() and not resolved_dest.is_dir():
        raise ValueError("Destination must resolve to a directory under repository root.")
    return resolved_dest, rel_dest.as_posix()


def _skill_install_intake_decision(repo_root: Path, skill_name: str, target_path: Path) -> dict[str, Any]:
    """Return the installation conflict decision for one candidate skill."""
    matches = _matching_install_skills(repo_root, skill_name)
    outcome, reason = _install_intake_outcome(target_path.exists(), matches)
    return _install_intake_payload(skill_name, target_path.exists(), outcome, reason, matches)


def _matching_install_skills(repo_root: Path, skill_name: str) -> list[dict[str, Any]]:
    normalized = skill_name.lower().strip()
    entries = sorted((entry for entry in discover_catalog_entries(advanced=True) if entry.source_dir.is_relative_to(repo_root)), key=lambda entry: entry.source_dir.relative_to(repo_root).as_posix())
    matches = [_install_match(repo_root, entry, normalized) for entry in entries]
    return sorted((match for match in matches if match), key=lambda item: (-float(item["similarity"]), item["path"]))


def _install_match(repo_root: Path, entry: Any, normalized: str) -> dict[str, Any] | None:
    try:
        fields = _read_skill_frontmatter_fields(entry.source_dir / "SKILL.md")
    except OSError:
        fields = {}
    name = str(fields.get("name") or entry.name or entry.source_dir.name)
    score = max(difflib.SequenceMatcher(None, normalized, name.lower()).ratio(), difflib.SequenceMatcher(None, normalized, entry.source_dir.name.lower()).ratio())
    if normalized not in {name.lower(), entry.source_dir.name.lower()} and score < 0.72:
        return None
    return {"name": name, "path": entry.source_dir.relative_to(repo_root).as_posix(), "description": str(fields.get("description") or entry.description or ""), "similarity": round(score, 3)}


def _install_intake_outcome(target_exists: bool, matches: list[dict[str, Any]]) -> tuple[str, str]:
    if target_exists:
        return "reject_duplicate", "target_path_exists"
    if matches and float(matches[0]["similarity"]) >= 0.86:
        return "needs_human_choice", "high_similarity_local_skill"
    if matches:
        return "keep_separate", "nearby_skill_exists_but_not_blocking"
    return "install_new", "no_close_local_match"


def _install_intake_payload(skill_name: str, target_exists: bool, outcome: str, reason: str, matches: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema_version": "skill-install-intake.v1", "canonical_term": "External Skill Intake", "candidate": skill_name, "outcome": outcome, "reason": reason, "target_exists": target_exists, "local_overlap_candidates": matches[:8], "allowed_outcomes": ["install_new", "blend_into_existing", "keep_separate", "reject_duplicate", "needs_human_choice"], "pre_install_checks": _install_prechecks(), "compatibility_checks": _install_compatibility_checks(), "post_install_gates": _install_post_gates(), "snyk_policy": {"required_when": "manifest-backed candidate is promoted or release readiness is claimed", "not_applicable_when": "pure SKILL.md-first instruction-only candidate has no supported dependency manifest"}, "promotion_rule": "Do not add a skill handle, route as canonical, blend into an owner skill, or make a Release-Readiness Claim until required gates pass."}


def _install_prechecks() -> list[str]:
    return ["inventory existing skills with ./bin/ask skills list --json --robot", "search Skills/**, Plugins/**/skills/**, and skills-system/** for overlap", "compare intent, trigger wording, scripts/assets, safety boundaries, and closeout contract", "return an Intake Decision before writing canonical source"]


def _install_compatibility_checks() -> list[str]:
    return ["OpenAI skill format and SKILL.md frontmatter", "progressive disclosure shape, preserved operating-model references, and required local safety sections", "repo path, network, secret, package-manager, and external-tool assumptions", "dependency manifest presence for Snyk applicability"]


def _install_post_gates() -> list[str]:
    return ["./bin/ask skills audit <skill-path> --level strict --json --robot", "./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot", "./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot", "./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot", "./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-local --json --robot", "./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-cloud --json --robot", "./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace jscraik --execute --json --robot", "./bin/ask evals run <skill-path> --mode smoke --runner discovery-smoke --tessl-live-private --tessl-workspace jscraik --tessl-live-dry-run --json --robot once scenario-quality passes", "./bin/ask sdk eval handoff-readiness --skill <skill-path> --preview --json --robot", "./bin/ask skills external-review <skill-path> --json --robot", "./bin/ask evals run <skill-path> --mode release --json --robot only after SDK handoff gates are current"]


__all__ = [name for name in globals() if not name.startswith("__")]
