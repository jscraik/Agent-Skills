from __future__ import annotations

from ask.skill_review_dashboard import dashboard_not_requested_receipt, render_optional_dashboard

from .skills_impl_audit_validation import *  # noqa: F403

def external_review_skill(
    repo_root: Path,
    skill_path: str,
    *,
    audit_level: str = "strict",
    skip_plugin_eval: bool = False,
    skip_tessl: bool = False,
    with_tessl_review: bool = False,
    skip_tessl_review: bool = False,
    include_snyk: bool = False,
    timeout_seconds: int = 180,
    report_path: Optional[str] = None,
    dashboard: bool = False,
    dashboard_path: Optional[str] = None,
) -> CallResult:
    """Run the local-only second-review lane for one skill.

    This command intentionally never publishes or registers a skill. Tessl is
    used only as an installed local CLI, never through npx. Content review is
    opt-in because it can invoke an external model-backed review service; the
    default lane keeps the deterministic local audit and package lint only.
    """
    result = CallResult()
    result.status = "success"
    result.data["dashboard"] = (
        {"status": "not_run", "reason": "review_not_completed", "tab": "quality"}
        if dashboard
        else dashboard_not_requested_receipt(tab="quality")
    )

    if with_tessl_review and (skip_tessl_review or skip_tessl):
        result.status = "error"
        blocker_flag = "--skip-tessl-review" if skip_tessl_review else "--skip-tessl"
        blocker_message = f"--with-tessl-review cannot be combined with {blocker_flag}."
        result.data["external_review"] = {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "blocker": blocker_message,
        }
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=blocker_message,
        ))
        return result

    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    audit_target, audit_target_path = _normalize_skill_target_path(skill_path)
    target_abs = (repo_root / audit_target).resolve()
    if not target_abs.is_dir() or not (target_abs / "SKILL.md").is_file():
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Skill path must resolve to a directory containing SKILL.md.",
            fix_suggestion=f"Check the path and rerun against a canonical skill directory: {audit_target_path}",
        ))
        return result

    result.data["policy"] = {
        "mode": "local_internal_only",
        "no_publish": True,
        "no_registry_upload": True,
        "uses_npx": False,
        "publish_policy": "never publish, register, upload, or invoke npx from this lane",
        "tessl_review_default": "disabled_requires_explicit_opt_in",
        "tessl_review_privacy_basis": "Tessl content review may use an external model-backed service; invoke it only with --with-tessl-review.",
        "primary_gate": "local_eval_ask_audit",
        "external_quality_judge": "tessl_review_opt_in",
        "tessl_review_min_score": TESSL_REVIEW_MIN_SCORE,
        "tessl_review_target_score": TESSL_REVIEW_TARGET_SCORE,
        "tessl_review_threshold_policy": (
            f"Tessl review must return reviewScore >= {TESSL_REVIEW_MIN_SCORE}; "
            f"{TESSL_REVIEW_TARGET_SCORE}+ remains the improvement target."
        ),
        "tessl_staging_root": f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-reviews')}/<skill-path>-<sha12>",
        "tessl_project_marker": "tessl.json",
        "tessl_evidence_retention": "stable tmp wrapper is intentionally left for inspection and copied-input evidence",
        "tessl_lint_role": "stable_plugin_packaging_shape_check",
        "tessl_lint_shape": (
            "Tessl plugin lint expects a .tessl-plugin/plugin.json package. Canonical repo skills are "
            f"SKILL.md-first, so this command builds a stable local plugin wrapper under {tempfile.gettempdir()} before linting."
        ),
        "tessl_review_role": "local_best_practice_content_review",
        "plugin_eval_role": "budget_and_ergonomics_guardrail",
        "plugin_eval_context_policy": (
            "Plugin Eval scores the agent-loaded context view. SDK workbench files "
            "remain package-validated but are excluded from static context-budget scoring."
        ),
        "plugin_eval_excluded_package_surfaces": list(PLUGIN_EVAL_EXCLUDED_PACKAGE_SURFACES),
        "plugin_eval_min_acceptable_grade": PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE,
        "plugin_eval_warning_policy": (
            "Plugin Eval warnings are visible follow-up work, but they are not release blockers when "
            "there are zero Plugin Eval failures, the grade is B+ or better, and local/Tessl gates pass."
        ),
        "snyk_role": "opt_in_local_dependency_security_screening",
        "snyk_default": "disabled_until_requested",
        "snyk_release_requirement": "release_required_for_manifest_backed_candidates",
        "snyk_when_to_use": [
            "when a skill or plugin candidate has dependency manifests such as package.json, pyproject.toml, requirements.txt, Gemfile, go.mod, or lockfiles",
            "when claiming release readiness for a manifest-backed skill or plugin package",
            "when dependency files, installer scripts, generated package surfaces, or plugin runtime dependencies changed",
            "when matching the CircleCI/Snyk security screening lane locally before or after CI",
            "when the user explicitly asks for Snyk, dependency vulnerability screening, or external security advisory evidence",
        ],
        "snyk_when_not_to_use": [
            "pure SKILL.md-first instruction-only candidates with no supported dependency manifest, unless the user explicitly asks",
            "routine local iteration where external networked security analysis is not needed",
        ],
        "snyk_privacy_basis": (
            "Snyk CLI security analysis may contact Snyk services. It is never run by default in this "
            "local-first review lane; pass --include-snyk when external Snyk advisory analysis is wanted."
        ),
    }
    result.data["review_mode_details"] = {
        "local_evals": {
            "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
            "role": "dynamic run-trace behavior checks for skill selection, commands, artifacts, and release gates",
        },
        "plugin_eval": {
            "command": "plugin-eval analyze <path> --format markdown",
            "role": "static budget, ergonomics, and reviewability guardrail; not a substitute for local evals",
        },
        "tessl_lint": {
            "command": "tessl plugin lint <stable-plugin-directory>",
            "role": "stable .tessl-plugin/plugin.json package-shape check, not a direct content finding",
            "canonical_source_shape": "SKILL.md-first",
        },
        "tessl_review": {
            "command": f"tessl skill review --json --threshold {TESSL_REVIEW_MIN_SCORE} <stable-skill-directory>",
            "role": "explicitly requested external content review for private or work-in-progress skills",
            "default": "disabled_requires_--with-tessl-review",
            "minimum_score": TESSL_REVIEW_MIN_SCORE,
            "target_score": TESSL_REVIEW_TARGET_SCORE,
            "publishes": False,
        },
        "snyk": {
            "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>",
            "role": "opt-in local dependency security screening; release-required for manifest-backed candidates",
            "default": "disabled_until_requested",
            "release_required": "manifest-backed candidates",
            "use_when": [
                "candidate has supported dependency manifests",
                "release-readiness is claimed for a manifest-backed package",
                "dependency/runtime package surfaces changed",
                "local evidence must match CircleCI/Snyk screening",
                "user explicitly requests Snyk or dependency vulnerability evidence",
            ],
        },
    }
    result.data["target"] = audit_target_path
    validation_args = [skill_path]
    if audit_level != "strict":
        validation_args.extend(["--audit-level", audit_level])
    if skip_plugin_eval:
        validation_args.append("--skip-plugin-eval")
    if skip_tessl:
        validation_args.append("--skip-tessl")
    if with_tessl_review:
        validation_args.append("--with-tessl-review")
    if skip_tessl_review:
        validation_args.append("--skip-tessl-review")
    if include_snyk:
        validation_args.append("--include-snyk")
    if timeout_seconds != 180:
        validation_args.extend(["--timeout-seconds", str(timeout_seconds)])
    if report_path:
        validation_args.extend(["--report-path", report_path])
    if dashboard:
        validation_args.append("--dashboard")
    if dashboard_path:
        validation_args.extend(["--dashboard-path", dashboard_path])
    result.data["validation_commands"] = [_skills_validation_command("external-review", *validation_args)]

    audit_result = audit_skill(repo_root, audit_target_path, level=audit_level)
    result.data["ask_audit"] = {
        "status": audit_result.status,
        "data": audit_result.data,
        "errors": [getattr(error, "__dict__", error) for error in audit_result.errors],
    }
    if audit_result.status != "success":
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Internal ask skill audit failed during external-review lane.",
            fix_suggestion="Inspect data.ask_audit for the exact failing gate.",
        ))

    if not skip_plugin_eval:
        plugin_eval_bin = shutil.which("plugin-eval")
        if not plugin_eval_bin:
            result.status = "error"
            result.data["plugin_eval"] = {"status": "blocked_missing_binary", "command": "plugin-eval analyze"}
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message="plugin-eval is not installed or not on PATH.",
                fix_suggestion="Install or expose plugin-eval, then rerun this local-only review lane.",
            ))
        else:
            plugin_eval_target, plugin_eval_context = _stage_plugin_eval_agent_context(
                repo_root,
                target_abs,
                audit_target,
            )
            result.data["plugin_eval_context"] = plugin_eval_context
            command = [plugin_eval_bin, "analyze", plugin_eval_target.as_posix(), "--format", "markdown"]
            try:
                proc = _run_captured_tool(repo_root=repo_root, command=command, timeout_seconds=timeout_seconds)
                payload = _completed_process_payload(proc)
                payload["status"] = "success" if proc.returncode == 0 else "error"
                plugin_summary = _parse_plugin_eval(payload.get("stdout", ""), payload["status"])
                payload["summary"] = plugin_summary
                result.data["plugin_eval"] = payload
                if proc.returncode != 0:
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message="plugin-eval analysis failed during external-review lane.",
                        fix_suggestion="Inspect data.plugin_eval for full output.",
                    ))
                elif plugin_summary.get("blocking_fail_count", plugin_summary.get("fail_count", 0)) or not plugin_summary.get("grade_acceptable", False):
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message=(
                            "Plugin Eval did not meet the local acceptance floor "
                            f"({PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE} with zero failures)."
                        ),
                        fix_suggestion="Inspect data.plugin_eval.summary for grade, fail count, and follow-up findings.",
                    ))
            except subprocess.TimeoutExpired:
                result.status = "error"
                result.data["plugin_eval"] = {"status": "timeout", "command": command, "timeout_seconds": timeout_seconds}
                result.errors.append(ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"plugin-eval timed out after {timeout_seconds} seconds.",
                    fix_suggestion="Rerun with a higher --timeout-seconds value if the target is intentionally large.",
                ))
    else:
        result.data["plugin_eval"] = {"status": "skipped"}

    if not skip_tessl:
        tessl_bin = shutil.which("tessl")
        if not tessl_bin:
            result.status = "error"
            result.data["tessl_lint"] = {"status": "blocked_missing_binary", "command": "tessl plugin lint"}
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message="Tessl CLI is not installed or not on PATH; Tessl local lint in the Second-Review Lane could not run.",
                fix_suggestion="Install Tessl as a local machine tool and rerun. This command will not invoke npx or publish anything.",
            ))
        else:
            tessl_tmp_path = _stable_tessl_review_root(audit_target_path)
            try:
                staging_root, plugin_info = _write_tessl_plugin_wrapper(repo_root, audit_target_path, tessl_tmp_path)
            except ValueError as exc:
                result.status = "error"
                result.data["tessl_plugin"] = {"status": "blocked_validation", "message": str(exc)}
                result.errors.append(ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion="Replace symlinked skill review inputs with regular files or directories before Tessl staging.",
                ))
                return result
            tessl_env: dict[str, str] = {}
            result.data["tessl_plugin"] = {
                **plugin_info,
                "mode": "stable_tmp_wrapper",
                "reason": (
                    "Tessl plugin lint validates .tessl-plugin/plugin.json packages. Canonical repo skills remain "
                    "SKILL.md-first, so this command stages a local plugin-shaped wrapper under /tmp."
                ),
                "auth_home": "process_home",
                "support_refs_included": True,
            }

            lint_command = [tessl_bin, "plugin", "lint", str(staging_root)]
            try:
                lint_proc = _run_captured_tool(
                    repo_root=repo_root,
                    command=lint_command,
                    timeout_seconds=timeout_seconds,
                    env_overrides=tessl_env,
                )
                lint_payload = _completed_process_payload(lint_proc)
                lint_payload["status"] = "success" if lint_proc.returncode == 0 else "error"
                result.data["tessl_lint"] = lint_payload
                if lint_proc.returncode != 0:
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message="Tessl skill lint failed during local-only external review.",
                        fix_suggestion="Inspect data.tessl_lint for Tessl's validation output.",
                    ))
            except subprocess.TimeoutExpired:
                result.status = "error"
                result.data["tessl_lint"] = {"status": "timeout", "command": lint_command, "timeout_seconds": timeout_seconds}
                result.errors.append(ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Tessl skill lint timed out after {timeout_seconds} seconds.",
                    fix_suggestion="Check the local Tessl installation and rerun once it responds normally.",
                ))

            if with_tessl_review:
                review_command = [
                    tessl_bin,
                    "skill",
                    "review",
                    "--json",
                    "--threshold",
                    str(TESSL_REVIEW_MIN_SCORE),
                    plugin_info["review_path"],
                ]
                try:
                    review_proc = _run_captured_tool(
                        repo_root=repo_root,
                        command=review_command,
                        timeout_seconds=timeout_seconds,
                        env_overrides=tessl_env,
                    )
                    review_payload = _completed_process_payload(review_proc)
                    review_payload["status"] = "success" if review_proc.returncode == 0 else "error"
                    review_summary = _parse_tessl_review_output(review_payload.get("stdout", ""), review_payload["status"])
                    review_payload["summary"] = review_summary
                    review_payload["minimum_score"] = TESSL_REVIEW_MIN_SCORE
                    review_payload["target_score"] = TESSL_REVIEW_TARGET_SCORE
                    result.data["tessl_review"] = review_payload
                    if review_proc.returncode != 0:
                        result.status = "error"
                        result.errors.append(ErrorObject(
                            code="ERR_VALIDATION",
                            message=f"Tessl skill review did not meet the >= {TESSL_REVIEW_MIN_SCORE} threshold.",
                            fix_suggestion="Inspect data.tessl_review for full output and the staged wrapper path.",
                        ))
                except subprocess.TimeoutExpired:
                    result.status = "error"
                    result.data["tessl_review"] = {"status": "timeout", "command": review_command, "timeout_seconds": timeout_seconds}
                    result.errors.append(ErrorObject(
                        code="ERR_RUNTIME",
                        message=f"Tessl skill review timed out after {timeout_seconds} seconds.",
                        fix_suggestion="Check the local Tessl installation and rerun once it responds normally.",
                    ))
            else:
                result.data["tessl_review"] = {
                    "status": "skipped",
                    "reason": "Disabled by default; pass --with-tessl-review to run model-backed Tessl content review.",
                    "minimum_score": TESSL_REVIEW_MIN_SCORE,
                    "target_score": TESSL_REVIEW_TARGET_SCORE,
                }
    else:
        result.data["tessl_lint"] = {"status": "skipped"}
        result.data["tessl_review"] = {
            "status": "skipped",
            "minimum_score": TESSL_REVIEW_MIN_SCORE,
            "target_score": TESSL_REVIEW_TARGET_SCORE,
        }

    if include_snyk:
        snyk_bin = shutil.which("snyk")
        if not snyk_bin:
            result.status = "error"
            result.data["snyk"] = {
                "status": "blocked_missing_binary",
                "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>",
            }
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message="Snyk CLI is not installed or not on PATH.",
                fix_suggestion="Install or expose the Snyk CLI, authenticate it if required, then rerun with --include-snyk.",
            ))
        else:
            snyk_command = [
                snyk_bin,
                "test",
                "--all-projects",
                "--detection-depth=6",
                "--severity-threshold=high",
                "--json",
                audit_target_path,
            ]
            try:
                snyk_proc = _run_captured_tool(
                    repo_root=repo_root,
                    command=snyk_command,
                    timeout_seconds=timeout_seconds,
                )
                snyk_payload = _completed_process_payload(snyk_proc)
                snyk_text = f"{snyk_proc.stdout}\n{snyk_proc.stderr}".lower()
                if snyk_proc.returncode == 0:
                    snyk_payload["status"] = "success"
                elif "could not detect supported target files" in snyk_text or "no supported files" in snyk_text:
                    snyk_payload["status"] = "not_applicable"
                    snyk_payload["reason"] = (
                        "Snyk found no supported dependency manifest under this skill. "
                        "SKILL.md-first skills are still covered by the internal audit, "
                        "security evals, and OpenClaw guard."
                    )
                elif (
                    "use snyk auth" in snyk_text
                    or "not authenticated" in snyk_text
                    or "authentication required" in snyk_text
                    or "snyk_token" in snyk_text
                ):
                    snyk_payload["status"] = "blocked_auth"
                    snyk_payload["reason"] = (
                        "Snyk CLI authentication is unavailable. Run snyk auth locally or provide "
                        "SNYK_TOKEN in CI before rerunning --include-snyk."
                    )
                elif snyk_proc.returncode == 1:
                    snyk_payload["status"] = "advisory"
                else:
                    snyk_payload["status"] = "error"
                result.data["snyk"] = snyk_payload
                if snyk_payload["status"] == "blocked_auth":
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_AUTH",
                        message="Snyk authentication is required for the external security lane.",
                        fix_suggestion="Run snyk auth locally or set SNYK_TOKEN in CI, then rerun with --include-snyk.",
                    ))
                elif snyk_payload["status"] in {"advisory", "error"}:
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message="Snyk reported an advisory or failed during the external security lane.",
                        fix_suggestion="Inspect data.snyk for vulnerability details, unsupported-project output, or authentication errors.",
                    ))
            except subprocess.TimeoutExpired:
                result.status = "error"
                result.data["snyk"] = {
                    "status": "timeout",
                    "command": snyk_command,
                    "timeout_seconds": timeout_seconds,
                }
                result.errors.append(ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Snyk timed out after {timeout_seconds} seconds.",
                    fix_suggestion="Check the local Snyk CLI/auth state and rerun with a higher --timeout-seconds value if needed.",
                ))
    else:
        result.data["snyk"] = {
            "status": "skipped",
            "reason": "Snyk is disabled by default. Use --include-snyk when external Snyk advisory analysis is wanted.",
        }

    report_target: Optional[Path] = None
    if report_path:
        report_target, report_error = _validate_repo_relative_skill_path(repo_root, report_path)
        if report_error:
            return report_error
        assert report_target is not None
    elif dashboard:
        default_report = Path("Infrastructure") / "artifacts" / "skill-reviews" / f"{target_abs.name}.json"
        report_target = (repo_root / default_report).resolve()

    def write_report() -> None:
        assert report_target is not None
        report_target.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "status": result.status,
            "data": result.data,
            "errors": [getattr(error, "__dict__", error) for error in result.errors],
        }
        report_target.write_text(json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def record_report_path() -> None:
        assert report_target is not None
        result.data["report_path"] = report_target.relative_to(repo_root.resolve()).as_posix()

    if report_target is not None and not dashboard:
        write_report()
        record_report_path()

    if dashboard:
        assert report_target is not None

        if dashboard_path:
            dashboard_target, dashboard_error = _validate_repo_relative_skill_path(repo_root, dashboard_path)
            if dashboard_error:
                return dashboard_error
            assert dashboard_target is not None
        else:
            dashboard_target = report_target.with_suffix(".html")

        def render_dashboard() -> Path:
            write_report()
            record_report_path()
            rendered = render_skill_review_dashboard(
                report_path=report_target,
                output_path=dashboard_target,
                repo_root=repo_root,
            )
            dashboard_rel_path = rendered.relative_to(repo_root.resolve()).as_posix()
            result.data["dashboard"] = {"status": "rendered", "tab": "quality"}
            result.data["dashboard_path"] = dashboard_rel_path
            result.data["dashboard_url"] = dashboard_rel_path
            write_report()
            return rendered

        rendered_dashboard, dashboard_receipt = render_optional_dashboard(render_dashboard, tab="quality")
        result.data["dashboard"] = dashboard_receipt
        if rendered_dashboard is not None:
            dashboard_rel_path = rendered_dashboard.relative_to(repo_root.resolve()).as_posix()
            result.data["dashboard_path"] = dashboard_rel_path
            result.data["dashboard_url"] = dashboard_rel_path
        else:
            result.data.pop("dashboard_path", None)
            result.data.pop("dashboard_url", None)
            if "report_path" in result.data:
                try:
                    write_report()
                except (OSError, UnicodeError, ValueError, KeyError, TypeError):
                    pass

    return result


def validate_skill_boundaries(repo_root: Path, handle: str) -> CallResult:
    """Resolve a handle and expose canonical-versus-projection ownership boundaries."""
    resolved = skills_explain_boundary(repo_root, handle)
    if resolved.status != "success":
        return resolved
    resolved.data["validation_commands"] = [
        _skills_validation_command("validate-boundaries", handle)
    ]
    return resolved


def skills_explain_boundary(repo_root: Path, handle: str) -> CallResult:
    """Return compact SDK source/projection ownership for one skill handle."""
    result = skills_resolve(repo_root, handle=handle)
    if result.status != "success":
        return result

    resolution = result.data.get("resolution", {})
    canonical_path = resolution.get("canonical_skill_path") or resolution.get("source_path")
    projection_risks: list[str] = []
    if canonical_path:
        projection_risks.append("Edit the canonical source path and regenerate or verify projections after changes.")

    boundary = {
        "handle": resolution.get("handle", handle.lstrip("$")),
        "status": "pass",
        "canonical_skill_path": canonical_path,
        "runtime_projection_path": resolution.get("runtime_projection_path"),
        "runtime_visibility": resolution.get("runtime_visibility"),
        "handle_source": resolution.get("handle_source"),
        "projection_mode": resolution.get("projection_mode"),
        "notes": projection_risks,
    }
    result.data = {"boundary_check": boundary}
    return result

def _resolve_canonical_install_dest(repo_root: Path, dest: str) -> tuple[Path, str]:
    """
    Resolve an install destination into an absolute repo path and a canonical repo-relative string.

    Parameters:
        repo_root (Path): Repository root directory against which `dest` is resolved.
        dest (str): User-supplied destination token (e.g. "github" or "backend"); empty values default to "github".

    Returns:
        tuple[Path, str]: A pair where the first element is the absolute resolved destination path inside `repo_root`
        and the second is the normalized repo-relative destination string.

    Raises:
        ValueError: If `dest` is an absolute path, if the resolved destination escapes the repository root,
        or if the repo-relative destination is empty or "." (must include a category directory).
    """
    dest_token = (dest or "Skills/github").strip() or "Skills/github"
    raw_dest = Path(dest_token)
    if raw_dest.is_absolute():
        raise ValueError("Destination must be repo-relative (for example: Skills/github or Skills/backend).")

    resolved_root = repo_root.resolve()
    resolved_dest = (repo_root / raw_dest).resolve()
    try:
        rel_dest = resolved_dest.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Destination escapes repository root.") from exc

    rel_parts = rel_dest.parts
    if len(rel_parts) == 1:
        rel_dest = Path("Skills") / rel_dest
        resolved_dest = (repo_root / rel_dest).resolve()
        rel_parts = rel_dest.parts
    rel_text = rel_dest.as_posix()
    if len(rel_parts) != 2 or rel_parts[0] != "Skills":
        raise ValueError("Destination must be under Skills/<category>.")
    if resolved_dest.exists() and not resolved_dest.is_dir():
        raise ValueError("Destination must resolve to a directory under repository root.")
    return resolved_dest, rel_text


def _skill_install_intake_decision(repo_root: Path, skill_name: str, target_path: Path) -> dict[str, Any]:
    """
    Analyze existing repository skills for naming/path conflicts and determine installation compatibility.

    Scans the canonical catalog for existing skills with similar names or directory names, determines an installation
    outcome based on conflict severity (install_new, keep_separate, needs_human_choice, reject_duplicate),
    and returns a comprehensive intake decision payload with overlapping candidates, pre-install checks,
    compatibility requirements, and post-install gates.

    Returns:
        Intake decision dictionary (schema: skill-install-intake.v1) containing outcome determination, matched
        candidates, policy requirements, and operational gates for pre-install validation and post-install promotion.
    """
    normalized_name = skill_name.lower().strip()
    matches: list[dict[str, Any]] = []
    catalog_entries = sorted(
        (
            entry
            for entry in discover_catalog_entries(advanced=True)
            if entry.source_dir.is_relative_to(repo_root)
        ),
        key=lambda entry: entry.source_dir.relative_to(repo_root).as_posix(),
    )
    for entry in catalog_entries:
        skill_dir = entry.source_dir
        skill_md = skill_dir / "SKILL.md"
        try:
            frontmatter = _read_skill_frontmatter_fields(skill_md)
        except OSError:
            frontmatter = {}
        local_name = str(frontmatter.get("name") or entry.name or skill_dir.name)
        local_description = str(frontmatter.get("description") or entry.description or "")
        name_ratio = difflib.SequenceMatcher(None, normalized_name, local_name.lower()).ratio()
        path_ratio = difflib.SequenceMatcher(None, normalized_name, skill_dir.name.lower()).ratio()
        score = max(name_ratio, path_ratio)
        if normalized_name in {local_name.lower(), skill_dir.name.lower()} or score >= 0.72:
            matches.append({
                "name": local_name,
                "path": skill_dir.relative_to(repo_root).as_posix(),
                "description": local_description,
                "similarity": round(score, 3),
            })
    matches.sort(key=lambda item: (-float(item["similarity"]), item["path"]))

    target_exists = target_path.exists()
    if target_exists:
        outcome = "reject_duplicate"
        reason = "target_path_exists"
    elif matches and float(matches[0]["similarity"]) >= 0.86:
        outcome = "needs_human_choice"
        reason = "high_similarity_local_skill"
    elif matches:
        outcome = "keep_separate"
        reason = "nearby_skill_exists_but_not_blocking"
    else:
        outcome = "install_new"
        reason = "no_close_local_match"

    return {
        "schema_version": "skill-install-intake.v1",
        "canonical_term": "External Skill Intake",
        "candidate": skill_name,
        "outcome": outcome,
        "reason": reason,
        "target_exists": target_exists,
        "local_overlap_candidates": matches[:8],
        "allowed_outcomes": [
            "install_new",
            "blend_into_existing",
            "keep_separate",
            "reject_duplicate",
            "needs_human_choice",
        ],
        "pre_install_checks": [
            "inventory existing skills with ./bin/ask skills list --json --robot",
            "search Skills/**, Plugins/**/skills/**, and skills-system/** for overlap",
            "compare intent, trigger wording, scripts/assets, safety boundaries, and closeout contract",
            "return an Intake Decision before writing canonical source",
        ],
        "compatibility_checks": [
            "OpenAI skill format and SKILL.md frontmatter",
            "progressive disclosure shape, preserved operating-model references, and required local safety sections",
            "repo path, network, secret, package-manager, and external-tool assumptions",
            "dependency manifest presence for Snyk applicability",
        ],
        "post_install_gates": [
            "./bin/ask skills audit <skill-path> --level strict --json --robot",
            "./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot",
            "./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot",
            "./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot",
            "./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-local --json --robot",
            "./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-cloud --json --robot",
            "./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace jscraik --execute --json --robot",
            "./bin/ask evals run <skill-path> --mode smoke --runner discovery-smoke --tessl-live-private --tessl-workspace jscraik --tessl-live-dry-run --json --robot once scenario-quality passes",
            "./bin/ask sdk eval handoff-readiness --skill <skill-path> --preview --json --robot",
            "./bin/ask skills external-review <skill-path> --json --robot",
            "./bin/ask evals run <skill-path> --mode release --json --robot only after SDK handoff gates are current",
        ],
        "snyk_policy": {
            "required_when": "manifest-backed candidate is promoted or release readiness is claimed",
            "not_applicable_when": "pure SKILL.md-first instruction-only candidate has no supported dependency manifest",
        },
        "promotion_rule": "Do not add a skill handle, route as canonical, blend into an owner skill, or make a Release-Readiness Claim until required gates pass.",
    }

__all__ = [name for name in globals() if not name.startswith("__")]
