from __future__ import annotations

from dataclasses import dataclass

from .skills_impl_external_review import *  # noqa: F403

@dataclass(frozen=True)
class InstallSkillOptions:
    remediate: bool = False
    dest: str = "Skills/github"
    dry_run: bool = False


def _install_dry_run_result(
    repo_root: Path,
    url: str,
    remediate: bool,
    dest_rel: str,
    skill_name: str,
    target_path: Path,
    intake_decision: dict,
) -> CallResult:
    """Build the non-mutating install preview with its canonical next command."""
    result = CallResult(status="success")
    try:
        display_path = str(target_path.relative_to(repo_root))
    except ValueError:
        display_path = str(target_path)
    validation_args = [url, "--dest", dest_rel]
    if remediate:
        validation_args.append("--remediate")
    validation_args.append("--dry-run")
    result.data.update({
        "dry_run": True, "skill_name": skill_name, "target_path": display_path,
        "url": url, "remediate": remediate, "canonical_dest": dest_rel,
        "intake_decision": intake_decision,
        "readiness_policy": {
            "full_evals_required_before_promotion": True,
            "external_skill_install_is_intake_not_copy": True,
            "preserve_operating_model_docs_as_references": True,
            "promotion_rule": intake_decision["promotion_rule"],
        },
        "validation_commands": [_skills_validation_command("install", *validation_args)],
    })
    result.metadata["next_steps"] = [
        "Review data.intake_decision.outcome before writing canonical source.",
        f"ask skills install {url} --dest {dest_rel}" + (" --remediate" if remediate else ""),
    ]
    return result


def _install_conflict_result(
    repo_root: Path, dest_rel: str, skill_name: str, target_path: Path, intake_decision: dict,
) -> CallResult:
    """Return the explicit duplicate or ownership-choice result before mutation."""
    try:
        display_path = str(target_path.relative_to(repo_root))
    except ValueError:
        display_path = str(target_path)
    duplicate = intake_decision["outcome"] == "reject_duplicate"
    result = CallResult(status="error")
    result.errors.append(ErrorObject(
        code="ERR_CONFLICT" if duplicate else "ERR_REQUIRES_HUMAN_CHOICE",
        message=(f"Skill '{skill_name}' already exists at '{display_path}'." if duplicate else f"Skill '{skill_name}' is similar to existing local skills; choose install_new, blend_into_existing, keep_separate, or reject_duplicate before writing."),
        fix_suggestion=("Remove the existing skill or choose a different destination with --dest." if duplicate else "Inspect data.intake_decision.local_overlap_candidates and rerun only after the ownership decision is explicit."),
    ))
    result.data.update({
        "skill_name": skill_name, "canonical_dest": dest_rel,
        "existing_path": display_path, "intake_decision": intake_decision,
    })
    return result


def _install_command(
    repo_root: Path, url: str, dest_path: Path, remediate: bool, result: CallResult,
) -> list[str] | None:
    """Build the installer invocation after checking its advertised optional flags."""
    python_cmd = _get_python_command(["pyyaml"])
    flags = _install_script_supported_flags(repo_root, python_cmd)
    cmd = python_cmd + [
        _resolve_skill_installer_script(repo_root), "--url", url, "--dest", str(dest_path),
    ]
    if "--validation-level" in flags:
        cmd.extend(["--validation-level", "compat"])
        result.data["validation_level"] = "compat"
    else:
        result.data["validation_level"] = "compat_skipped_unsupported"
    if not remediate or "--remediate" in flags:
        return [*cmd, *( ["--remediate"] if remediate else [])]
    result.status = "error"
    result.errors.append(ErrorObject(
        code="ERR_VALIDATION", message="Installed skill installer does not support --remediate.",
        fix_suggestion="Re-run without --remediate, or update the installer to a version that supports remediation.",
    ))
    return None


def _post_install_readiness_policy(installed_path: str, intake_decision: dict) -> dict:
    """Return the required post-install gates for an admitted source package."""
    return {
        "full_evals_required_before_promotion": True,
        "external_skill_install_is_intake_not_copy": True,
        "preserve_operating_model_docs_as_references": True,
        "promotion_rule": intake_decision["promotion_rule"],
        "post_install_gates": [
            f"ask skills audit {installed_path} --level strict --json --robot",
            f"ask sdk eval scenario-quality {installed_path} --preview --json --robot",
            f"ask sdk eval scorer-quality {installed_path} --preview --json --robot",
            f"ask sdk eval scorer-calibration {installed_path} --preview --json --robot",
            f"ask sdk eval run {installed_path} --runner internal --mode smoke --codex-profile oss-local --json --robot",
            f"ask sdk eval run {installed_path} --runner internal --mode smoke --codex-profile oss-cloud --json --robot",
            f"ask sdk eval tessl-local-proof --skill {installed_path} --workspace jscraik --execute --json --robot",
            f"ask evals run {installed_path} --mode smoke --runner discovery-smoke --tessl-live-private --tessl-workspace jscraik --tessl-live-dry-run --json --robot once scenario-quality passes",
            f"ask sdk eval handoff-readiness --skill {installed_path} --preview --json --robot",
            f"ask skills external-review {installed_path} --json --robot",
            f"ask evals run {installed_path} --mode release --json --robot only after SDK handoff gates are current",
        ],
    }


def _record_install_process(
    result: CallResult, process: subprocess.CompletedProcess[str], dest_rel: str, intake_decision: dict,
) -> None:
    """Attach the installer process evidence before classifying its outcome."""
    result.data.update({
        "raw_output": process.stdout,
        "raw_error": process.stderr,
        "canonical_dest": dest_rel,
        "intake_decision": intake_decision,
    })


def _complete_installation(
    result: CallResult, repo_root: Path, dest_rel: str, fallback_name: str, intake_decision: dict,
) -> None:
    """Synchronise a successful install and attach its post-install gate list."""
    match = re.search(r"Installed (.*?) to", result.data["raw_output"])
    installed_name = match.group(1) if match else fallback_name
    result.status = "success"
    result.data["skill_name"] = installed_name
    sync_result = sync_skills(repo_root, scope="workspace", dry_run=False)
    result.data["workspace_sync"] = {
        "status": sync_result.status,
        "logs": sync_result.data.get("logs", []),
    }
    if sync_result.status != "success":
        sync_error = sync_result.errors[0].message if sync_result.errors else "Unknown sync failure."
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_RUNTIME",
            message=f"Skill installed to '{dest_rel}', but workspace sync failed: {sync_error}",
            fix_suggestion="Run `ask skills sync --scope workspace` after resolving the sync error.",
        ))
        return
    policy = _post_install_readiness_policy(f"{dest_rel}/{installed_name}", intake_decision)
    result.data["readiness_policy"] = policy
    result.metadata["next_steps"] = policy["post_install_gates"]


def _record_install_failure(result: CallResult) -> None:
    """Classify a non-zero installer process without changing its captured evidence."""
    result.status = "error"
    result.errors.append(ErrorObject(
        code="ERR_RUNTIME", message=result.data["raw_error"].strip() or "Installation failed.",
    ))


def _install_skill(repo_root: Path, url: str, remediate: bool = False, dest: str = "Skills/github", dry_run: bool = False) -> CallResult:
    result = CallResult()
    try:
        dest_path, dest_rel = _resolve_canonical_install_dest(repo_root, dest)
    except ValueError as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid install destination '{dest}': {exc}",
                fix_suggestion="Use a category under Skills/ such as 'Skills/github' or shorthand 'github'.",
            )
        )
        return result

    # Parse skill name from URL for preview
    skill_name = (url.split("/")[-1] if "/" in url else url).removesuffix(".git")
    target_path = dest_path / skill_name
    intake_decision = _skill_install_intake_decision(repo_root, skill_name, target_path)

    if dry_run:
        return _install_dry_run_result(repo_root, url, remediate, dest_rel, skill_name, target_path, intake_decision)

    if intake_decision["outcome"] in {"reject_duplicate", "needs_human_choice"}:
        return _install_conflict_result(repo_root, dest_rel, skill_name, target_path, intake_decision)

    cmd = _install_command(repo_root, url, dest_path, remediate, result)
    if cmd is None:
        return result

    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=INSTALL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        result.status = "error"
        result.data.update({
            "raw_output": _decode_stream(exc.stdout),
            "raw_error": _decode_stream(exc.stderr),
            "canonical_dest": dest_rel,
            "intake_decision": intake_decision,
        })
        result.errors.append(ErrorObject(
            code="ERR_TIMEOUT",
            message=f"ask skills install: installer timed out after {INSTALL_TIMEOUT_SECONDS} seconds.",
            fix_suggestion="Check network access to the source URL, then rerun the install.",
        ))
        return result
    _record_install_process(result, process, dest_rel, intake_decision)
    _record_install_process(result, process, dest_rel, intake_decision)

    if process.returncode == 0:
        _complete_installation(result, repo_root, dest_rel, skill_name, intake_decision)
    else:
        _record_install_failure(result)

    return result


def install_skill(
    repo_root: Path,
    url: str,
    options: InstallSkillOptions | None = None,
    **legacy_options: object,
) -> CallResult:
    """Install from typed options, retaining legacy keywords during migration."""
    if options is not None and legacy_options:
        raise TypeError("pass either InstallSkillOptions or legacy keyword arguments, not both")
    resolved = options or InstallSkillOptions(**legacy_options)
    return _install_skill(repo_root, url, remediate=resolved.remediate, dest=resolved.dest, dry_run=resolved.dry_run)


def _install_script_supported_flags(repo_root: Path, python_cmd: List[str]) -> set[str]:
    """
    Identify which optional flags the installer script advertises in its help text.

    Parameters:
        repo_root (Path): Repository root used as the subprocess working directory.
        python_cmd (List[str]): Tokenised Python command to invoke the script (e.g. ["python3"] or a wrapper tool chain).

    Returns:
        supported (set[str]): Set containing any of `"--validation-level"` and `"--remediate"` that appear in the script's help output.
    """
    installer_script = _resolve_skill_installer_script(repo_root)
    help_cmd = python_cmd + [
        installer_script,
        "--help",
    ]
    try:
        process = subprocess.run(help_cmd, cwd=str(repo_root), capture_output=True, text=True)
    except OSError:
        return set()

    help_text = "\n".join([process.stdout or "", process.stderr or ""])
    supported = set()
    for flag in ("--validation-level", "--remediate"):
        if flag in help_text:
            supported.add(flag)
    return supported


def fold_skills(repo_root: Path, source: str, target: str, sensitivity: float = 0.2) -> CallResult:
    """
    Determine whether the source skill should be folded into the target skill based on description similarity.

    Parameters:
        repo_root (Path): Repository root used to load builder modules and the skill catalog.
        source (str): Name or trailing path segment identifying the source skill to evaluate.
        target (str): Name or trailing path segment identifying the target skill to compare against.
        sensitivity (float): Confidence threshold in the range 0-1 above which overlap is considered high (default 0.2).

    Returns:
        CallResult: Result object containing:
            - On success: `status == "success"`, `data["overlap_score"]` (float), and `data["recommendation"]`
              set to either a "KEEP" message or a "KEEP: No significant overlap found." message.
            - On redundancy detection: `status == "error"`, an `ERR_REDUNDANCY` error with a `fix_suggestion`,
              and `data["overlap_score"]`, `data["rationale"]`, and `data["recommendation"]` describing the overlap.
            - On missing dependencies: `status == "error"` with `ERR_DEPENDENCY`.
            - On missing skills: `status == "error"` with `ERR_VALIDATION`.
            - `data["rationale"]`, when present, contains the router's textual rationale for the match.
    """
    result = CallResult()
    validation_args = [source, target]
    if sensitivity != 0.2:
        validation_args.extend(["--sensitivity", str(sensitivity)])
    result.data["validation_commands"] = [_skills_validation_command("fold", *validation_args)]

    builder_catalog = _load_builder_module(repo_root, "skill_catalog")
    router_mod = _load_builder_module(repo_root, "skill_router")

    if not builder_catalog or not router_mod:
        result.status = "error"
        result.data["dependency_status"] = {
            "skill_catalog": "available" if builder_catalog else "missing",
            "skill_router": "available" if router_mod else "missing",
        }
        result.errors.append(ErrorObject(
            code="ERR_DEPENDENCY",
            message="Skill router or builder catalog not available.",
            fix_suggestion="Restore the Skill Factory script namespace or use skills route for current routing checks.",
        ))
        return result

    try:
        catalog = builder_catalog.load_catalog(repo_root)
    except (ImportError, OSError, TypeError, ValueError) as exc:
        result.status = "error"
        result.data["dependency_status"] = {
            "skill_catalog": "load_failed",
            "skill_router": "available",
            "error": str(exc),
        }
        result.errors.append(ErrorObject(
            code="ERR_DEPENDENCY",
            message="Skill router or builder catalog not available.",
            fix_suggestion="Inspect data.dependency_status.error or use skills route for current routing checks.",
        ))
        return result
    source_skill = next((s for s in catalog.skills if s.name == source or str(s.skill_path).endswith(source)), None)
    target_skill = next((s for s in catalog.skills if s.name == target or str(s.skill_path).endswith(target)), None)

    if not source_skill or not target_skill:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Source or target skill not found."))
        return result

    # Run router check
    query = source_skill.description
    candidates, _ = router_mod.route(query, [target_skill], top_k=1)

    if candidates:
        match = candidates[0]
        result.data["overlap_score"] = match.confidence
        result.data["rationale"] = match.rationale

        if match.confidence >= sensitivity:
            # High overlap - emit CONFLICT to indicate redundancy issue
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_REDUNDANCY",
                message=f"High overlap ({int(match.confidence * 100)}%) detected between '{source}' and '{target}'.",
                fix_suggestion=f"Consider folding '{source}' into '{target}' to reduce redundancy."
            ))
            result.data["recommendation"] = f"FOLD: High overlap ({int(match.confidence * 100)}%) detected."
        else:
            result.status = "success"
            result.data["recommendation"] = f"KEEP: Low overlap ({int(match.confidence * 100)}%) detected."
    else:
        result.status = "success"
        result.data["overlap_score"] = 0
        result.data["recommendation"] = "KEEP: No significant overlap found."

    return result


def _scope_rank_for_path(repo_root: Path, skill_path: str) -> int:
    scope = classify_skill_scope(repo_root / skill_path, repo_root=repo_root)
    max_precedence = max(USER_SKILL_SCOPE_PRECEDENCE.values())
    scope_precedence = USER_SKILL_SCOPE_PRECEDENCE.get(scope)
    if scope_precedence is not None:
        return max_precedence - scope_precedence + 1
    if scope == "system":
        return max_precedence + 1
    root = skill_path.split("/", 1)[0].strip()
    if root in REPO_SCAN_ROOTS:
        return max_precedence + REPO_SCAN_ROOTS.index(root) + 2
    return max_precedence + len(REPO_SCAN_ROOTS) + 2


def _canonical_repo_relative_path(path: str) -> str:
    parts = Path(path).parts
    if parts and parts[0] == "plugins":
        return Path("Plugins", *parts[1:]).as_posix()
    return path


def _exact_handle_sort_key(candidate: EligibleCandidate) -> tuple[int, int, str]:
    path = candidate.path.removeprefix("./")
    bridge_rank = 1 if path.startswith(".agents/") else 0
    return bridge_rank, candidate.scope_rank, canonical_sort_key(candidate)


def route_skills(
    repo_root: Path,
    request: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """
    Route a textual request to candidate skills and produce a decision payload.

    Builds a set of eligible skills from the repository, ranks the best matches for the trimmed request using the skill router, evaluates catalog parity, and returns a CallResult containing the routing decision and related metadata.

    Parameters:
        repo_root (Path): Repository root used to discover canonical skill entries.
        request (str): Textual request to route; must be non-empty after trimming.
        top_k (int): Maximum number of top-ranked skills to return; values less than 1 are coerced to 1.
        considered_limit (int): Maximum number of candidate skills to consider when routing; values less than 1 are coerced to 1.

    Returns:
        CallResult: Result object whose `data` includes:
            - `decision`: decision payload produced by the routing logic.
            - `catalog_parity`: parity information comparing catalog and routing considerations.
            - `policy_identity`: policy identity used for the decision.
            - `decision_status`: the decision's status string.
        On error the CallResult will have `status == "error"` and `errors` will include one or more ErrorObject entries describing validation, dependency or runtime issues.
    """
    result = CallResult()
    query = request.strip()
    if not query:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Request cannot be empty for skills route.",
                fix_suggestion="Provide request text, for example: ask skills route \"review this PR\"",
            )
        )
        return result

    default_candidates: list[EligibleCandidate] = []
    default_candidate_ids: set[str] = set()
    for entry in discover_catalog_entries():
        if not entry.source_dir.is_relative_to(repo_root):
            continue
        rel_path = _canonical_repo_relative_path(entry.source_dir.relative_to(repo_root).as_posix())
        candidate = EligibleCandidate(
            name=entry.name,
            path=rel_path,
            description=entry.description,
            scope_rank=_scope_rank_for_path(repo_root, rel_path),
        )
        default_candidates.append(candidate)
        default_candidate_ids.add(candidate_id(candidate))

    advanced_only_candidates: list[EligibleCandidate] = []
    for entry in discover_catalog_entries(advanced=True):
        if not entry.source_dir.is_relative_to(repo_root):
            continue
        rel_path = _canonical_repo_relative_path(entry.source_dir.relative_to(repo_root).as_posix())
        candidate = EligibleCandidate(
            name=entry.name,
            path=rel_path,
            description=entry.description,
            scope_rank=_scope_rank_for_path(repo_root, rel_path),
        )
        if candidate_id(candidate) in default_candidate_ids:
            continue
        advanced_only_candidates.append(candidate)

    ordered_default_candidates = sorted(default_candidates, key=canonical_sort_key)
    all_candidates = list(ordered_default_candidates)
    all_candidate_ids = {candidate_id(candidate) for candidate in all_candidates}
    for candidate in sorted(advanced_only_candidates, key=canonical_sort_key):
        cid = candidate_id(candidate)
        if cid in all_candidate_ids:
            continue
        all_candidates.append(candidate)
        all_candidate_ids.add(cid)

    normalized_handle_query = query.removeprefix("$").strip().lower()
    if normalized_handle_query and " " not in normalized_handle_query:
        for entry in discover_catalog_entries(advanced=True, source="repo"):
            if entry.name.lower() != normalized_handle_query:
                continue
            if not entry.source_dir.is_relative_to(repo_root):
                continue
            rel_path = _canonical_repo_relative_path(entry.source_dir.relative_to(repo_root).as_posix())
            candidate = EligibleCandidate(
                name=entry.name,
                path=rel_path,
                description=entry.description,
                scope_rank=_scope_rank_for_path(repo_root, rel_path),
            )
            cid = candidate_id(candidate)
            if cid in all_candidate_ids:
                continue
            all_candidates.append(candidate)
            all_candidate_ids.add(cid)

    exact_candidates = [
        candidate
        for candidate in all_candidates
        if candidate.name.lower() == normalized_handle_query
    ]
    exact_candidate = min(exact_candidates, key=_exact_handle_sort_key) if exact_candidates else None
    if exact_candidate is not None and normalized_handle_query and " " not in normalized_handle_query:
        ranked_payload = [
            {
                "skill_name": exact_candidate.name,
                "skill_path": exact_candidate.path,
                "confidence": 1.0,
                "rationale": ["exact SDK skill handle match"],
                "risk_tier": "low",
            }
        ]
        catalog_parity = compute_catalog_parity(repo_root, strict=False)
        decision = build_decision_payload(
            request=query,
            policy_identity=get_policy_identity(),
            considered_limit=len(all_candidates),
            top_k=1,
            eligible_candidates=all_candidates,
            ranked_candidates=ranked_payload,
            uncertainty_reasons=[],
            catalog_parity_ok=not bool(catalog_parity.get("drift_detected")),
        )
        result.data["decision"] = decision
        result.data["catalog_parity"] = catalog_parity
        result.data["policy_identity"] = decision["policy_identity"]
        result.data["decision_status"] = decision["decision_status"]
        decision["validation_commands"] = [_skills_validation_command("route", query)]
        if decision["decision_status"] == "resolved":
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"skills route returned {decision['decision_status']}",
                    fix_suggestion=decision.get("operator_action"),
                )
            )
        return result

    bounded_limit = max(1, int(considered_limit))
    considered_candidates = ordered_default_candidates[:bounded_limit]
    considered_candidate_ids = {candidate_id(candidate) for candidate in considered_candidates}
    for candidate in sorted(advanced_only_candidates, key=canonical_sort_key):
        cid = candidate_id(candidate)
        if cid in considered_candidate_ids:
            continue
        considered_candidates.append(candidate)
        considered_candidate_ids.add(cid)

    router_mod = _load_builder_module(repo_root, "skill_router")
    if not router_mod:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_DEPENDENCY",
                message="Skill router module is not available.",
                fix_suggestion=(
                    "Ensure Plugins/skill-factory/scripts/skill-builder/skill_router.py "
                    "exists and rerun."
                ),
            )
        )
        return result
    router_skills = [
        _RouterSkill(name=item.name, description=item.description, skill_path=item.path)
        for item in considered_candidates
    ]

    ranked, uncertainty_reasons = router_mod.route(query, router_skills, top_k=max(1, int(top_k)))
    ranked_payload = [
        {
            "skill_name": candidate.skill_name,
            "skill_path": candidate.skill_path,
            "confidence": float(candidate.confidence),
            "rationale": list(candidate.rationale),
            "risk_tier": candidate.risk_tier,
        }
        for candidate in ranked
    ]

    catalog_parity = compute_catalog_parity(
        repo_root,
        strict=False,
    )

    decision = build_decision_payload(
        request=query,
        policy_identity=get_policy_identity(),
        considered_limit=len(considered_candidates),
        top_k=max(1, int(top_k)),
        eligible_candidates=considered_candidates,
        ranked_candidates=ranked_payload,
        uncertainty_reasons=list(uncertainty_reasons),
        catalog_parity_ok=not bool(catalog_parity.get("drift_detected")),
    )
    decision["validation_commands"] = [_skills_validation_command("route", query)]

    decision_status = decision["decision_status"]
    result.data["decision"] = decision
    result.data["catalog_parity"] = catalog_parity
    result.data["policy_identity"] = decision["policy_identity"]
    result.data["decision_status"] = decision_status

    if decision_status == "resolved":
        result.status = "success"
        return result

    failure_class = decision.get("failure_class")
    code = "ERR_VALIDATION"
    if failure_class == "AMBIGUITY_UNRESOLVED":
        code = "ERR_CONFLICT"
    elif failure_class == "DISCOVERY_POLICY_DRIFT":
        code = "ERR_DEPENDENCY"
    elif failure_class == "CATALOG_PARITY_DRIFT":
        code = "ERR_VALIDATION"

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code=code,
            message=f"skills route returned {decision_status}",
            fix_suggestion=decision.get("operator_action"),
        )
    )
    return result


def goal_skills(
    repo_root: Path,
    intent_text: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """
    Builds a goal-oriented decision from an intent by routing the intent to skills and converting the resulting route decision into a goal decision.

    Parameters:
        repo_root (Path): Repository root used to discover and route against skills.
        intent_text (str): Natural-language intent to resolve into a goal decision.
        top_k (int): Maximum number of top candidate skills to return from routing.
        considered_limit (int): Number of skills to consider during routing.

    Returns:
        CallResult: Contains:
            - `data["goal_decision"]` (dict): The constructed goal decision payload.
            - `data["decision_status"]` (str): Final goal decision status.
            - `data["policy_identity"]` (dict): Policy identity associated with the decision.
            - `data["route_decision_status"]` (optional[str]): Status of the underlying route decision.
            On success (`decision_status == "resolved"`) the result.status is `"success"`. On failure the result.status is `"error"` and result.errors includes an ErrorObject with `code="ERR_VALIDATION"` and a `fix_suggestion` when available. If the routing step did not produce a decision payload the result.error contains an ErrorObject with `code="ERR_RUNTIME"`.
    """
    result = CallResult()
    route_result = route_skills(
        repo_root,
        request=intent_text,
        top_k=max(1, int(top_k)),
        considered_limit=max(1, int(considered_limit)),
    )
    route_decision = route_result.data.get("decision") if isinstance(route_result.data, dict) else None
    if not isinstance(route_decision, dict):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message="Route decision payload missing while building goal decision.",
                fix_suggestion="Retry `ask skills goal` after restoring route command health.",
            )
        )
        return result

    goal_decision = build_goal_decision(route_decision)
    goal_decision["validation_commands"] = [_skills_validation_command("goal", intent_text)]
    result.data["goal_decision"] = goal_decision
    result.data["decision_status"] = goal_decision["decision_status"]
    result.data["policy_identity"] = goal_decision["policy_identity"]
    result.data["route_decision_status"] = route_decision.get("decision_status")

    if goal_decision["decision_status"] == "resolved":
        result.status = "success"
        return result

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=f"skills goal returned {goal_decision['decision_status']}",
            fix_suggestion=goal_decision.get("operator_action"),
        )
    )
    return result


def _candidate_handle(candidate: dict[str, Any]) -> str:
    """Return the best SDK skill handle spelling for a routed candidate."""
    name = str(candidate.get("name") or "").strip().lstrip("$")
    if name:
        return name
    path = str(candidate.get("path") or "").strip().rstrip("/")
    if path:
        return Path(path).name
    candidate_id_value = str(candidate.get("candidate_id") or "").strip()
    if candidate_id_value:
        return candidate_id_value.rsplit(":", 1)[-1].strip().lstrip("$")
    return ""


_IMPROVE_STOPWORDS = frozenset({
    "a",
    "an",
    "and",
    "against",
    "at",
    "better",
    "for",
    "make",
    "of",
    "this",
    "the",
    "to",
})

_IMPROVE_HANDLE_HINTS = (
    (
        frozenset({"validation", "blockers", "fix"}),
        "autofix",
        "fallback validation-blocker intent hint",
    ),
    (
        frozenset({"review", "implementation", "spec"}),
        "he-code-review",
        "fallback implementation-review intent hint",
    ),
    (
        frozenset({"monitor", "long", "running", "phase"}),
        "pr-green-sweep",
        "fallback PR sweep and long-running validation intent hint",
    ),
    (
        frozenset({"linear", "backed", "spec"}),
        "cli-spec",
        "fallback spec intent hint",
    ),
)


def _improve_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in _IMPROVE_STOPWORDS
    }

__all__ = [name for name in globals() if not name.startswith("__")]
