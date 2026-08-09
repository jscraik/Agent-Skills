from .skills_impl_project_improve import *  # noqa: F403

def skills_sdk_project_conformance(
    repo_root: Path,
    project_root: str | None = None,
    mode: str = "status",
) -> CallResult:
    """
    Report Skills SDK project conformance for a given repository and project location.

    Parameters:
        repo_root (Path): Repository root containing skills metadata.
        project_root (str | None): Project directory to evaluate; when None the project root is inferred.
        mode (str): Conformance mode, either "status" (summary) or "doctor" (detailed diagnostics).

    Returns:
        result (CallResult): Contains `data["skills_sdk_project_conformance"]` with a `skills-sdk-project-conformance.v1` payload:
            - `status`: overall conformance status from the generated receipt.
            - `mode`: the requested mode.
            - `project_root`: the provided project_root value.
            - `receipt`: the full conformance receipt produced by the builder.
            - `validation_commands`: suggested CLI command(s) to re-run the check.
            - `agent_summary`: short human-readable summary.
        On invalid `mode`, the result has `status="error"` and an `ERR_VALIDATION` ErrorObject. If the underlying receipt builder fails, the result has `status="error"`, includes the error receipt in the payload, and adds an ErrorObject derived from the builder exception.
    """
    result = CallResult()
    result.metadata["command"] = f"sdk project {mode}"
    if mode not in {"status", "doctor"}:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skills SDK project conformance mode must be status or doctor.",
                fix_suggestion="ask sdk project status --project-root /path/to/project --json --robot",
            )
        )
        return result
    try:
        receipt = _build_project_conformance_receipt(
            repo_root,
            project_root=project_root,
            mode=mode,
        )
    except _ProjectConformanceError as exc:
        result.status = "error"
        validation_cmd_args = ["sdk", "project", mode]
        if project_root:
            validation_cmd_args.extend(["--project-root", project_root])
        result.data["skills_sdk_project_conformance"] = {
            "schema_version": "skills-sdk-project-conformance.v1",
            "status": exc.receipt.get("status", "blocked"),
            "mode": mode,
            "project_root": project_root,
            "receipt": exc.receipt,
            "validation_commands": [_ask_validation_command(*validation_cmd_args)],
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
    validation_cmd_args = ["sdk", "project", mode]
    if project_root:
        validation_cmd_args.extend(["--project-root", project_root])
    payload = {
        "schema_version": "skills-sdk-project-conformance.v1",
        "status": receipt["status"],
        "mode": mode,
        "project_root": project_root,
        "receipt": receipt,
        "validation_commands": [_ask_validation_command(*validation_cmd_args)],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_project_conformance"] = payload
    return result


def skills_sdk_placeholder_lifecycle(
    repo_root: Path,
    surface: str | None = None,
    risk_tier: str = "medium",
) -> CallResult:
    """Emit read-only placeholder lifecycle receipts for unavailable V1.0 surfaces."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk lifecycle"
    try:
        lifecycle = _build_placeholder_lifecycle_receipts(surface=surface, risk_tier=risk_tier)
    except (ValueError, KeyError, TypeError) as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Placeholder lifecycle builder validation failed: {e}",
                fix_suggestion="Check that surface and risk_tier arguments match the canonical SDK contract.",
            )
        )
        return result
    payload = {
        **lifecycle,
        "facade_command": "skills-sdk lifecycle",
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "lifecycle",
                *(("--surface", surface) if surface else ()),
                "--risk-tier",
                risk_tier,
            )
        ],
    }
    result.data["skills_sdk_placeholder_lifecycle"] = payload
    if lifecycle["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=lifecycle["agent_summary"],
                fix_suggestion="Use --risk-tier medium for optional placeholder reporting, or implement the missing adapter in a later approved slice.",
            )
        )
    return result


def skills_sdk_status(repo_root: Path) -> CallResult:
    """Report the canonical Skills SDK capability truth matrix."""
    result = CallResult()
    result.metadata["command"] = "sdk status"
    try:
        status = _build_capability_status(repo_root)
    except _CapabilityStatusError as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK capability matrix validation failed: {e}",
                fix_suggestion="Fix Infrastructure/config/skills-sdk/capability-matrix.v1.json and rerun ask sdk status.",
            )
        )
        return result
    result.data["skills_sdk_status"] = status
    return result


def skills_sdk_capability_evidence(repo_root: Path, scope: str) -> CallResult:
    """Verify capability matrix evidence refs without running command or external lanes."""
    result = CallResult()
    result.metadata["command"] = "sdk evidence verify"
    try:
        receipt = _build_capability_evidence_receipt(repo_root, scope=scope)
    except (ValueError, _CapabilityStatusError) as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK capability evidence verification failed: {e}",
                fix_suggestion="Fix the capability matrix or run ask sdk evidence verify --scope capability-matrix --json --robot.",
            )
        )
        return result
    result.data["skills_sdk_capability_evidence"] = {
        "status": receipt["status"],
        "receipt": receipt,
    }
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Inspect receipt.blockers and fix missing or unknown capability matrix evidence refs before "
                    "using ask sdk evidence verify as a validation gate."
                ),
            )
        )
    return result


def skills_prove(repo_root: Path, handle: str) -> CallResult:
    """Compose an agent-facing proof scorecard for one skill handle."""
    result = CallResult()
    result.metadata["command"] = "skills prove"
    query = handle.strip()
    goal_resolution: dict[str, Any] | None = None
    reachability_result = skills_proof(repo_root, query)
    command_proof = reachability_result.data.get("proof", {})
    initial_resolution = command_proof.get("resolution") if isinstance(command_proof, dict) else {}
    resolver_ok = isinstance(initial_resolution, dict) and initial_resolution.get("status") == "ok"
    if reachability_result.status != "success" and not resolver_ok:
        improvement_result = improve_skills(repo_root, goal_text=query)
        goal_resolution = improvement_result.data.get("improvement")
        candidate = (goal_resolution or {}).get("recommended_capability") or {}
        if candidate.get("handle"):
            reachability_result = skills_proof(repo_root, str(candidate["handle"]))
        else:
            result.status = "error"
            result.data["skill_proof"] = {
                "schema_version": "skill-proof-scorecard.v1",
                "query": query,
                "handle": None,
                "proof_status": "blocked_goal_resolution",
                "agent_summary": f"Could not resolve goal '{query}' to one skill handle.",
                "reachability": {"status": "not_checked", "source": "goal_resolution"},
                "structural_quality": {"status": "not_checked", "audit_command": None},
                "analytics": {
                    "status": "unavailable_or_legacy",
                    "evidence_class": "native_skill_invocation_projection",
                    "note": "No skill handle was available for analytics lookup.",
                },
                "outcome_proof": {"status": "not_checked", "workout_candidates": [], "evidence_class": "outcome_proof"},
                "goal_resolution": goal_resolution,
                "next_command": (goal_resolution or {}).get("next_command")
                or _skills_validation_command("improve", query),
            }
            result.data["skill_proof"]["validation_commands"] = [
                result.data["skill_proof"]["next_command"],
            ]
            result.errors.extend(improvement_result.errors)
            if not result.errors:
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message=f"Could not resolve goal '{query}' to one skill handle.",
                        fix_suggestion=result.data["skill_proof"]["next_command"],
                    )
                )
            return result
    command_proof = reachability_result.data.get("proof", {})
    resolution = command_proof.get("resolution") if isinstance(command_proof, dict) else {}
    if not isinstance(resolution, dict):
        resolution = {}
    normalized = str(command_proof.get("handle") or resolution.get("handle") or handle.lstrip("$"))
    reachability_status = command_proof.get("status") if isinstance(command_proof, dict) else "missing"

    audit_target = _skill_audit_target(repo_root, resolution)
    structural_detail: dict[str, Any] = {
        "status": "missing",
        "audit_level": "compat",
        "audit_command": None,
    }
    if audit_target:
        audit_result = audit_skill(repo_root, audit_target, level="compat", validation_scope="source")
        structural_detail = {
            "status": "pass" if audit_result.status == "success" else "fail",
            "audit_level": "compat",
            "audit_command": _skills_validation_command("audit", audit_target, "--level", "compat"),
            "strict_audit_command": _skills_validation_command("audit", audit_target, "--level", "strict"),
            "diagnostics_exit_code": audit_result.data.get("diagnostics", {}).get("exit_code"),
        }

    analytics = skill_invocation_analytics(repo_root, normalized)
    workouts = _skill_workout_candidates(repo_root, normalized)
    evaluation_proof = _eval_shard_outcome_proof(repo_root, normalized)
    outcome_status = "pass" if evaluation_proof["status"] == "pass" else "missing"
    next_command = _skills_validation_command("proof", normalized)
    if reachability_status != "pass":
        proof_status = "blocked_reachability"
        runtime_diagnostics = command_proof.get("runtime_diagnostics")
        recovery_commands = (
            runtime_diagnostics.get("recovery_commands")
            if isinstance(runtime_diagnostics, dict)
            else None
        )
        if isinstance(recovery_commands, list):
            preview = next(
                (
                    item.get("command")
                    for item in recovery_commands
                    if isinstance(item, dict)
                    and item.get("kind") == "preview_user_runtime_sync"
                    and isinstance(item.get("command"), str)
                ),
                None,
            )
            if preview:
                next_command = preview
    elif structural_detail["status"] != "pass":
        proof_status = "blocked_structural_quality"
        next_command = structural_detail.get("audit_command") or next_command
    elif evaluation_proof["status"] == "pass":
        proof_status = "proved_local"
        outcome_status = "pass"
        next_command = None
    elif workouts:
        proof_status = "reachable_without_outcome_proof"
        outcome_status = "available_not_run"
        next_command = _ask_validation_command("workouts", "run", workouts[0])
    else:
        proof_status = "reachable_without_outcome_proof"
        next_command = _outcome_proof_next_command(
            repo_root,
            normalized,
            structural_detail.get("strict_audit_command") or next_command,
        )

    scorecard = {
        "schema_version": "skill-proof-scorecard.v1",
        "query": query,
        "handle": normalized,
        "proof_status": proof_status,
        "agent_summary": (
            f"{normalized} is reachable and structurally valid, but outcome proof is not present."
            if proof_status == "reachable_without_outcome_proof"
            else f"{normalized} is structurally valid, reachable, and has current local outcome proof."
            if proof_status == "proved_local"
            else f"{normalized} proof is blocked at {proof_status.replace('blocked_', '').replace('_', ' ')}."
        ),
        "reachability": {
            "status": reachability_status,
            "source": "sdk_skill_proof",
            "command": _skills_validation_command("proof", normalized),
        },
        "structural_quality": structural_detail,
        "analytics": analytics,
        "outcome_proof": {
            "status": outcome_status,
            "workout_candidates": workouts,
            "evidence_class": "outcome_proof",
            **({key: value for key, value in evaluation_proof.items() if key != "status"} if outcome_status == "pass" else {}),
        },
        "next_command": next_command,
        "validation_commands": [next_command] if next_command else [],
    }
    if goal_resolution:
        scorecard["goal_resolution"] = goal_resolution
    result.data["skill_proof"] = scorecard
    result.data["sdk_skill_proof"] = command_proof
    if proof_status.startswith("blocked_"):
        result.status = "error"
        result.errors.extend(reachability_result.errors)
        if not result.errors:
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Skill proof scorecard is blocked for '{normalized}'.",
                    fix_suggestion=next_command,
                )
            )
    elif proof_status == "reachable_without_outcome_proof":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skill proof scorecard has no local outcome proof for '{normalized}'.",
                fix_suggestion=next_command,
            )
        )
    return result


def _skill_sections(path: Path) -> dict[str, list[str]]:
    """Return markdown section bodies keyed by heading text."""
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1).strip().lower()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return sections


def _section_items(sections: dict[str, list[str]], names: tuple[str, ...], limit: int = 4) -> list[str]:
    """Extract concise bullets or first paragraphs from named markdown sections."""
    items: list[str] = []
    for name in names:
        for raw in sections.get(name, []):
            line = raw.strip()
            if not line:
                continue
            line = re.sub(r"^[-*]\s+", "", line)
            line = re.sub(r"^\d+\.\s+", "", line)
            items.append(line)
            if len(items) >= limit:
                return items
    return items


def _skill_usage_items(sections: dict[str, list[str]], limit: int = 4) -> tuple[list[str], list[str]]:
    """Split positive and negative guidance from a skill's usage section."""
    when_to_use: list[str] = []
    when_not_to_use: list[str] = []
    for raw in sections.get("when to use", []):
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        if line.lower().startswith("avoid "):
            when_not_to_use.append(line)
        else:
            when_to_use.append(line)
        if len(when_to_use) >= limit and len(when_not_to_use) >= limit:
            break
    return when_to_use[:limit], when_not_to_use[:limit]


def _skill_validation_commands(source_path: Path, repo_root: Path) -> list[str]:
    """Return executable validation commands for a resolved skill source."""
    try:
        relative_source = source_path.relative_to(repo_root)
    except ValueError:
        return []
    audit_target = relative_source.parent if relative_source.name == "SKILL.md" else relative_source
    return [_skills_validation_command("audit", str(audit_target), "--level", "strict")]


def explain_skill(repo_root: Path, handle: str) -> CallResult:
    """Explain one SDK-visible skill handle for agent use."""
    result = CallResult()
    result.metadata["command"] = "skills explain"
    resolution = resolve_skill_handle(handle, repo_root_path=repo_root)
    normalized = resolution.get("handle", handle.lstrip("$"))
    if resolution.get("status") != "ok":
        result.status = "error"
        result.data["explanation"] = {
            "schema_version": "skill-explanation.v1",
            "status": "blocked",
            "handle": normalized,
            "agent_summary": f"Could not resolve skill handle '{normalized}'.",
            "next_command": _skills_validation_command("resolve", str(normalized)),
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not explain skill handle '{normalized}': {resolution.get('error_code')}",
                fix_suggestion=resolution.get("operator_action"),
            )
        )
        return result

    source_path_value = str(resolution.get("source_path") or "").strip()
    if not source_path_value:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skill handle '{normalized}' resolved without a canonical source path.",
                fix_suggestion="Run ./bin/ask skills sync --scope workspace --projection flat --json --robot and rerun ./bin/ask skills explain.",
            )
        )
        return result
    raw_source_path = Path(source_path_value)
    source_path = raw_source_path if raw_source_path.is_absolute() else repo_root / raw_source_path
    try:
        resolved_source = source_path.resolve()
        resolved_repo = repo_root.resolve()
        try:
            resolved_source.relative_to(resolved_repo)
        except ValueError:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_PATH_TRAVERSAL",
                    message=f"Skill handle '{normalized}' resolved outside the repository root.",
                    fix_suggestion="Fix the SDK skill registry source path and rerun ./bin/ask skills explain.",
                )
            )
            return result
    except (ValueError, OSError) as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Failed to validate source path: {e}",
                fix_suggestion="Ensure the source path is valid and accessible",
            )
        )
        return result
    if not resolved_source.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Resolved source for '{normalized}' is missing: {source_path}",
                fix_suggestion="Run ./bin/ask skills sync --scope workspace --projection flat --json --robot and rerun ./bin/ask skills explain.",
            )
        )
        return result
    try:
        sections = _skill_sections(source_path)
    except OSError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Resolved source for '{normalized}' could not be read: {source_path}",
                fix_suggestion=f"Fix source permissions or rerun `./bin/ask skills explain {shlex.quote(str(normalized))}` after syncing.",
            )
        )
        return result
    description = str(resolution.get("description") or "").strip()
    when_to_use, inline_when_not_to_use = _skill_usage_items(sections, limit=4)
    when_to_use = when_to_use or ([description] if description else [])
    when_not_to_use = inline_when_not_to_use or _section_items(sections, ("avoid",), limit=4)
    required_validation = _section_items(sections, ("validation",), limit=4)
    known_limitations = _section_items(sections, ("failure mode", "anti-patterns", "constraints"), limit=4)
    validation_commands = _skill_validation_commands(source_path, repo_root)
    proof_result = skills_proof(repo_root, str(normalized))
    proof = proof_result.data.get("proof", {})

    skills_explain = {
        "schema_version": "skills-explain.v1",
        "query": handle,
        "canonical_source": resolution.get("source_path"),
        "skill_handle": normalized,
        "handle_source": resolution.get("handle_source") or "sdk_flat_registry",
        "runtime_projection": (resolution.get("provenance") or {}).get("projection_mode"),
        "runtime_visibility": resolution.get("runtime_visibility"),
        "owner": resolution.get("owner"),
        "loaded_references": [],
        "when_to_use": when_to_use,
        "when_not_to_use": when_not_to_use,
        "validation": validation_commands,
        "overlaps": [],
        "ambiguity_notes": [],
    }
    # Determine runtime projection path - check if a file-backed projection exists
    runtime_projection_path = None
    projection_note = None
    canonical_source_path = resolution.get("source_path")

    if canonical_source_path:
        # Check for file-backed runtime projection in .agents/skills
        potential_projection = repo_root / ".agents" / "skills" / normalized / "SKILL.md"
        if potential_projection.is_file():
            try:
                runtime_projection_path = str(potential_projection.relative_to(repo_root))
            except ValueError:
                runtime_projection_path = None
                projection_note = "projection_outside_repo"
        else:
            projection_note = "projection_not_file_backed"

    runtime_projection_mode = (resolution.get("provenance") or {}).get("projection_mode")
    if runtime_projection_path and resolution.get("runtime_visibility") == "flat":
        runtime_projection_mode = "flat"
        if (resolution.get("provenance") or {}).get("projection_mode") not in {None, "flat"}:
            projection_note = "file_backed_flat_projection_overrides_stale_resolver_provenance"
    skills_explain["runtime_projection"] = runtime_projection_mode

    explanation = {
        "schema_version": "skill-explanation.v1",
        "status": "resolved",
        "handle": normalized,
        "agent_summary": f"{normalized} is for {description}" if description else f"{normalized} is resolved.",
        "what_it_is": description,
        "when_to_use": when_to_use,
        "when_not_to_use": when_not_to_use,
        "canonical_source_path": canonical_source_path,
        "runtime_projection_path": runtime_projection_path,
        "skill_handles": [
            {
                "handle": normalized,
                "path": runtime_projection_path,
                "projection_note": projection_note,
                "handle_source": resolution.get("handle_source") or "sdk_flat_registry",
            }
        ],
        "required_validation": required_validation,
        "validation_commands": validation_commands,
        "known_limitations": known_limitations,
        "overlaps": skills_explain["overlaps"],
        "ambiguity_notes": skills_explain["ambiguity_notes"],
        "reachability": {
            "status": proof.get("status") if isinstance(proof, dict) else "not_checked",
            "proof_command": _skills_validation_command("proof", str(normalized)),
        },
        "resolution": resolution,
        "next_command": _skills_validation_command("proof", str(normalized)),
    }
    result.data["skills_explain"] = skills_explain
    result.data["explanation"] = explanation
    return result


def reviewers_resolve(repo_root: Path, handle: str) -> CallResult:
    """Resolve one reviewer/subagent handle from the reviewer namespace."""
    result = CallResult()
    result.metadata["command"] = "reviewers resolve"
    payload = resolve_reviewer_handle(handle)
    normalized = str(payload.get("canonical_handle") or payload.get("handle") or handle).lstrip("@")
    payload["validation_commands"] = [
        _ask_validation_command("reviewers", "resolve", normalized),
    ]
    result.data["resolution"] = payload
    if payload.get("status") != "ok":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not resolve reviewer handle '{payload.get('handle', handle)}': {payload.get('error_code')}",
                fix_suggestion=payload.get("operator_action"),
            )
        )
    return result


def init_skill(repo_root: Path, name: str, category: str, description: str) -> CallResult:
    """Initializes a new skill scaffold using the repo template logic."""
    result = CallResult()
    result.data["validation_commands"] = [
        _skills_validation_command(
            "init",
            name,
            "--category",
            category,
            "--description",
            description,
        )
    ]
    category_token = (category or "").strip()
    if not category_token:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill category cannot be empty.",
                fix_suggestion="Use a category such as 'ui' or 'code_quality_review'.",
            )
        )
        return result
    if Path(category_token).is_absolute():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill category must be repo-relative.",
                fix_suggestion="Use a category token such as 'ui' (not an absolute path).",
            )
        )
        return result

    if category_token.startswith("Skills/"):
        out_dir = repo_root / category_token
        category_rel = category_token
    else:
        out_dir = repo_root / "Skills" / category_token
        category_rel = f"Skills/{category_token}"
    try:
        out_dir.resolve().relative_to(repo_root.resolve())
    except ValueError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_PATH_TRAVERSAL",
                message=f"Category '{category}' escapes repository root.",
                fix_suggestion="Use a category path under Skills/.",
            )
        )
        return result

    init_skill_script = _resolve_skill_builder_script(repo_root, "init_skill")
    cmd = _get_python_command(["pyyaml"]) + [
        init_skill_script,
        name,
        "--path",
        str(out_dir),
        "--description", description,
        "--owner", "Agent Skills Kit",
        "--review-cadence", "quarterly",
        "--maturity", "experimental",
        "--lifecycle-state", "incubating"
    ]

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)

    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Initialized skill '{name}' in '{category_rel}'"
        result.data["canonical_dest"] = category_rel
        result.metadata["next_steps"] = [f"ask skills audit {category_rel}/{name} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip()))

    return result

__all__ = [name for name in globals() if not name.startswith("__")]
