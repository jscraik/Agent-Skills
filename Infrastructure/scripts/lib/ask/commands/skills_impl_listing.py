from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from .skills_impl_catalog import *  # noqa: F403

@dataclass(frozen=True)
class ListSkillsOptions:
    starter: bool = False
    archetype: str = "general"
    limit: int = 12
    advanced: bool = False
    visible_only: bool = False


@dataclass(frozen=True)
class SkillsHandlesOptions:
    check: bool = False
    include_handles: bool = True
    write_projection: bool = False
    check_projection: bool = False
    dry_run: bool = False


def _list_discovery_mode(category: Optional[str], starter: bool, visible_only: bool) -> tuple[str, bool]:
    category_token = category.lower().strip() if category else ""
    explicit_visible_only = bool(visible_only)
    return category_token, bool(
        (category_token and not explicit_visible_only) or (not explicit_visible_only and not starter)
    )


def _list_catalog_entries(
    repo_root: Path, *, discovery_advanced: bool, visible_only: bool, starter: bool, archetype: str, limit: int
) -> list[Any]:
    entries = [
        entry for entry in discover_catalog_entries(advanced=discovery_advanced)
        if entry.source_dir.is_relative_to(repo_root)
    ]
    if visible_only:
        entries = [entry for entry in entries if _entry_visible_for_picker(entry, repo_root)]
    return _starter_entries(entries, archetype=archetype, limit=limit) if starter else entries


def _list_skill_data(repo_root: Path, entries: list[Any], category_token: str) -> list[dict[str, str]]:
    owner_by_handle = _sdk_handle_owner_index(repo_root) if category_token else {}
    return [
        {
            "name": entry.name,
            "path": str(entry.source_dir.relative_to(repo_root)),
            "category": entry.category,
            "description": entry.description,
        }
        for entry in entries
        if not category_token or _entry_matches_category(entry, category_token, owner_by_handle, repo_root)
    ]


def _list_validation_arguments(
    category: Optional[str], *, starter: bool, archetype: str, limit: int, advanced: bool, visible_only: bool
) -> tuple[str, list[str]]:
    args = ["--category", category] if category else []
    if advanced and not starter and not visible_only:
        args.append("--advanced")
    if visible_only and not starter:
        args.append("--visible-only")
    if starter:
        args.extend(["--archetype", archetype, "--limit", str(max(1, int(limit)))])
    return ("starter" if starter else "list"), args


def _list_skills(
    repo_root: Path, category: Optional[str] = None, *, starter: bool = False, archetype: str = "general",
    limit: int = 12, advanced: bool = False, visible_only: bool = False,
) -> CallResult:
    """List catalog skills using the current picker and starter-selection policy."""
    category_token, discovery_advanced = _list_discovery_mode(category, starter, visible_only)
    entries = _list_catalog_entries(
        repo_root, discovery_advanced=discovery_advanced, visible_only=visible_only,
        starter=starter, archetype=archetype, limit=limit,
    )
    result = CallResult()
    result.data.update({
        "skills": _list_skill_data(repo_root, entries, category_token),
        "policy_identity": get_policy_identity(),
        "advanced_mode": discovery_advanced,
        "inventory_mode": "repo" if discovery_advanced else "visible",
        "visible_only": bool(visible_only),
    })
    action, args = _list_validation_arguments(
        category, starter=starter, archetype=archetype, limit=limit, advanced=advanced, visible_only=visible_only,
    )
    if starter:
        result.data.update({
            "starter_mode": True, "starter_archetype": archetype if archetype in STARTER_ARCHETYPES else "general",
            "starter_limit": max(1, int(limit)),
        })
    result.data["validation_commands"] = [_skills_validation_command(action, *args)]
    result.status = "success"
    return result

def list_skills(
    repo_root: Path,
    category: Optional[str] = None,
    options: ListSkillsOptions | None = None,
    **legacy_options: object,
) -> CallResult:
    """List skills from typed options, retaining legacy keyword arguments during migration."""
    if options is not None and legacy_options:
        raise TypeError("pass either ListSkillsOptions or legacy keyword arguments, not both")
    resolved = options or ListSkillsOptions(**legacy_options)
    return _list_skills(
        repo_root,
        category,
        starter=resolved.starter,
        archetype=resolved.archetype,
        limit=resolved.limit,
        advanced=resolved.advanced,
        visible_only=resolved.visible_only,
    )


def _run_budget_command(
    repo_root: Path, command: List[str],
) -> tuple[Optional[subprocess.CompletedProcess[str]], Optional[OSError], Optional[CallResult]]:
    """Run one bounded runtime-budget command."""
    try:
        process, timeout_result = _run_bounded_subprocess(
            repo_root, command, "runtime_budget", "Skill runtime budget verifier timed out."
        )
        return process, None, timeout_result
    except OSError as exc:
        return None, exc, None


def _budget_process(
    repo_root: Path, command: List[str], script_args: list[str],
) -> tuple[Optional[subprocess.CompletedProcess[str]], Optional[OSError], Optional[CallResult]]:
    """Run the managed budget command, retrying only unavailable wrappers."""
    process, run_error, timeout_result = _run_budget_command(repo_root, command)
    wrapper = Path(command[0]).name.lower() if command else ""
    if timeout_result is not None or process is not None or wrapper not in {"uv", "mise"}:
        return process, run_error, timeout_result
    fallback, fallback_error, fallback_timeout = _run_budget_command(
        repo_root, [sys.executable, *script_args]
    )
    return (
        fallback,
        None if fallback is not None else fallback_error or run_error,
        fallback_timeout,
    )


def _budget_execution_error(run_error: Optional[OSError]) -> CallResult:
    """Return a stable runtime error when no budget process could start."""
    detail = (
        f"Failed to execute runtime budget verifier: {run_error}"
        if run_error is not None else "Failed to execute runtime budget verifier."
    )
    result = CallResult(status="error")
    result.errors.append(ErrorObject(
        code="ERR_RUNTIME",
        message=detail,
        fix_suggestion="Ensure Python is available and rerun `ask skills budget`.",
    ))
    return result


def _budget_report(process: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """Parse a runtime-budget report while retaining malformed process output."""
    try:
        parsed = json.loads(process.stdout)
    except json.JSONDecodeError:
        parsed = {"status": "fail", "raw_stdout": process.stdout, "raw_stderr": process.stderr}
    if isinstance(parsed, dict):
        return parsed
    return {
        "status": "fail", "raw_stdout": process.stdout, "raw_stderr": process.stderr,
        "parse_error": "verify_runtime_budget.py did not return a JSON object",
    }


def _budget_result(
    process: subprocess.CompletedProcess[str], report: dict[str, Any], default_max: int,
) -> CallResult:
    """Bind validation evidence and classify the parsed runtime-budget report."""
    validation_args = [] if default_max == 30 else ["--default-max", str(default_max)]
    report["validation_commands"] = [_skills_validation_command("budget", *validation_args)]
    passed = process.returncode == 0 and report.get("status") == "pass"
    result = CallResult(status="success" if passed else "error")
    result.data["runtime_budget"] = report
    if not passed:
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Skill runtime budget failed.",
            fix_suggestion="Reduce default-visible skills or hide bridge aliases under .system.",
        ))
    return result


def skills_budget(repo_root: Path, default_max: int = 30) -> CallResult:
    """Run the default skill runtime-budget audit and return its JSON report."""
    script_args = [
        "Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py",
        "--default-max", str(default_max), "--json",
    ]
    process, run_error, timeout_result = _budget_process(
        repo_root, _get_python_command() + script_args, script_args
    )
    if timeout_result is not None:
        return timeout_result
    if process is None:
        return _budget_execution_error(run_error)
    return _budget_result(process, _budget_report(process), default_max)


def _handles_validation_arguments(options: SkillsHandlesOptions) -> list[str]:
    flags = (
        (options.check, "--check"),
        (not options.include_handles, "--no-handles"),
        (options.write_projection, "--write-projection"),
        (options.check_projection, "--check-projection"),
        (options.dry_run, "--dry-run"),
    )
    return [flag for enabled, flag in flags if enabled]


def _handles_projection_error(result: CallResult) -> CallResult:
    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_INVALID_PROJECTION_MODE",
            message="Removed projection flags are not part of the SDK target registry path.",
            fix_suggestion="Use ./bin/ask skills sync --scope workspace --projection flat --json --robot, then rerun ./bin/ask skills list --json --robot.",
        )
    )
    return result


def _handles_report(repo_root: Path, options: SkillsHandlesOptions) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidates = build_sdk_skill_record_candidates(repo_root_path=repo_root, visibility="advanced")
    records = build_sdk_skill_records(repo_root_path=repo_root, visibility="advanced")
    handles = [record.to_resolution() for record in records] if options.include_handles else []
    violations = sdk_duplicate_handle_violations(candidates)
    report = {
        "schema_version": "sdk-skill-handles.v1",
        "status": "fail" if violations else "pass",
        "generated_from": "sdk_flat_registry",
        "handle_count": len(records),
        "handles": handles,
        "violations": violations,
        "validation_commands": [_skills_validation_command("handles", *_handles_validation_arguments(options))],
    }
    return report, violations


def _skills_handles(repo_root: Path, options: SkillsHandlesOptions) -> CallResult:
    """Return or validate SDK-visible skill handles from one typed options value."""
    result = CallResult()
    result.metadata["command"] = "skills handles"
    if options.write_projection or options.check_projection:
        return _handles_projection_error(result)
    report, violations = _handles_report(repo_root, options)
    result.data.update({
        "sdk_handles": report,
        "command_surface": {
            **report, "schema_version": "command-surface.v1", "generated_from": "sdk_flat_registry_compat_alias",
        },
        "handles": report["handles"],
        "violations": violations,
        "policy_identity": get_policy_identity(),
    })
    if options.check and violations:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="SDK skill target validation failed.",
                fix_suggestion="Inspect data.violations, fix SDK skill metadata, and rerun ./bin/ask skills list --json --robot.",
            )
        )
    return result

def skills_handles(
    repo_root: Path,
    options: SkillsHandlesOptions | None = None,
    **legacy_options: object,
) -> CallResult:
    """Return skill handles from typed options, retaining legacy keyword arguments during migration."""
    if options is not None and legacy_options:
        raise TypeError("pass either SkillsHandlesOptions or legacy keyword arguments, not both")
    resolved = options or SkillsHandlesOptions(**legacy_options)
    return _skills_handles(repo_root, resolved)




def skills_resolve(repo_root: Path, handle: str) -> CallResult:
    """Resolve one SDK-visible skill handle to its canonical source."""
    result = CallResult()
    result.metadata["command"] = "skills resolve"
    payload = resolve_skill_handle(handle, repo_root_path=repo_root)
    normalized = str(payload.get("handle") or handle).lstrip("$")
    payload["validation_commands"] = [
        _skills_validation_command("resolve", normalized),
    ]
    result.data["resolution"] = payload
    if payload.get("status") != "ok":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not resolve skill handle '{payload.get('handle', handle)}': {payload.get('error_code')}",
                fix_suggestion=payload.get("operator_action"),
            )
        )
    return result


def skills_parse(repo_root: Path, request_text: str) -> CallResult:
    """Parse a prompt for SDK skill mentions and reviewer roles, then resolve them."""
    result = CallResult()
    result.metadata["command"] = "skills parse"
    payload = parse_sdk_references(request_text, repo_root_path=repo_root)
    payload["validation_commands"] = [
        _skills_validation_command("parse", request_text),
    ]
    result.data["parse"] = payload
    if payload.get("status") != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="One or more SDK skill handles in the prompt could not be resolved.",
                fix_suggestion="Inspect data.parse.unresolved, then rerun with valid $ skill and @ reviewer handles.",
            )
        )
    return result


def skills_proof(repo_root: Path, handle: str, runtime_target: str = "any") -> CallResult:
    """
    Prove that an SDK skill handle is reachable from the workspace and user runtime targets.

    Parameters:
        repo_root (Path): Repository root used to resolve skill sources and workspace context.
        handle (str): Command-visible handle to prove (e.g., "$skill do something").
        runtime_target (str): Runtime target to validate against; normalized values include `"any"` and `"codex"`.

    Returns:
        CallResult: Result of the proof operation. On success `status` will be `"success"` and `data["proof"]`
        contains the proof payload produced by `build_sdk_skill_proof`. `data["runtime_evidence"]` will
        contain emitted runtime evidence. If the proof fails `status` will be `"error"`, `errors` will include an
        `ErrorObject` with `code="ERR_VALIDATION"`, and `data["runtime_failure"]` will contain failure details.
    """
    result = CallResult()
    result.metadata["command"] = "skills proof"
    runtime_target = normalize_runtime_target(runtime_target)
    proof = build_sdk_skill_proof(
        repo_root=repo_root,
        handle=handle,
        runtime_target=runtime_target,
        resolve_skill_handle_fn=resolve_skill_handle,
        home_path=Path.home(),
    )
    normalized = proof["handle"]
    runtime_evidence = emit_sdk_skill_runtime_evidence(repo_root=repo_root, proof=proof)
    result.data["runtime_evidence"] = runtime_evidence
    proof["runtime_evidence"] = runtime_evidence
    runtime_evidence_blocks = (
        runtime_target in {"codex", "agents"}
        and runtime_evidence.get("claim_status") in {"blocked", "partial"}
    )
    result.data["proof"] = proof
    if proof["status"] != "pass" or runtime_evidence_blocks:
        failure = (
            proof.get("runtime_failure")
            if isinstance(proof.get("runtime_failure"), dict)
            else _runtime_failure_payload(
                command="skills proof",
                error_code="ERR_RUNTIME",
                failed_check_id=str(runtime_evidence.get("failed_check_id") or "runtime_observation_quality"),
                path="runtime_evidence.claim_status",
                message=str(runtime_evidence.get("blocker") or "Runtime evidence quality is incomplete."),
                recovery_guidance="Rerun the explicit runtime proof after collecting current runtime evidence.",
                validation_commands=[_skills_validation_command("proof", normalized, "--runtime-target", runtime_target)],
            )
        )
        if runtime_evidence_blocks and proof.get("status") == "pass":
            proof["status"] = "fail"
        proof["runtime_failure"] = failure
        result.data["runtime_failure"] = failure
        message = (
            f"Invalid runtime target '{runtime_target}'."
            if failure.get("failed_check_id") == "runtime_target"
            else f"SDK skill proof failed for '{normalized}'."
        )
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=failure["recovery_guidance"],
            )
        )
    return result


def _skill_audit_target(repo_root: Path, resolution: dict[str, Any]) -> str | None:
    source = resolution.get("source_path")
    if not source:
        return None
    target = Path(str(source))
    if not target.is_absolute():
        target = repo_root / target
    if target.name == "SKILL.md":
        target = target.parent
    try:
        return target.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _skills_sdk_digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _skills_sdk_repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _skills_sdk_eval_package_identity(repo_root: Path, target: str) -> dict[str, str] | None:
    query = target.strip()
    if not query:
        return None
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    if not isinstance(target_info, dict) or target_info.get("target_kind") == "invalid_path":
        return None
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    if not source_path_value:
        return None
    source_path = Path(str(source_path_value))
    if not source_path.is_absolute():
        source_path = repo_root / source_path
    if source_path.is_dir():
        source_path = source_path / "SKILL.md"
    if not source_path.is_file():
        return None
    receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    return {
        "skill_ir_schema_version": str(receipt["manifest"]["skill_ir_schema_version"]),
        "package_id": str(receipt["package_id"]),
        "package_digest": str(receipt["package_digest"]),
    }


def _skills_sdk_eval_source_path(repo_root: Path, target: str) -> Path | None:
    query = target.strip()
    if not query:
        return None
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    if not isinstance(target_info, dict) or target_info.get("target_kind") == "invalid_path":
        return None
    source_path_value = target_info.get("source_path")
    if not source_path_value:
        return None
    source_path = Path(str(source_path_value))
    if not source_path.is_absolute():
        source_path = repo_root / source_path
    if source_path.is_dir():
        source_path = source_path / "SKILL.md"
    return source_path if source_path.is_file() else None


def _flatten_case_filters(cases: list[str] | None) -> list[str]:
    selected: list[str] = []
    for raw_case in cases or []:
        for case_id in raw_case.split(","):
            normalized = case_id.strip()
            if normalized and normalized not in selected:
                selected.append(normalized)
    return selected


def _skill_workout_candidates(repo_root: Path, handle: str) -> list[str]:
    workouts_root = repo_root / ".workouts"
    if not workouts_root.is_dir():
        return []
    normalized = handle.strip().lower().replace("_", "-")

    def _normalized_metadata_values(value: Any) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            return {value.strip().lower().replace("_", "-")}
        if isinstance(value, dict):
            result: set[str] = set()
            for nested in value.values():
                result.update(_normalized_metadata_values(nested))
            return result
        if isinstance(value, (list, tuple, set)):
            result: set[str] = set()
            for nested in value:
                result.update(_normalized_metadata_values(nested))
            return result
        return {str(value).strip().lower().replace("_", "-")}

    candidates: list[str] = []
    for workout in sorted(workouts_root.glob("**/workout.yaml")):
        workout_id = workout.parent.relative_to(workouts_root).as_posix()
        try:
            from ask.commands.workouts import _load_structured_file

            metadata = _load_structured_file(workout)
        except (OSError, ValueError):
            continue
        explicit_values: set[str] = set()
        for key in (
            "skills",
            "handles",
            "target_skills",
            "target_handles",
            "skill",
            "handle",
            "skill_id",
            "id",
            "target_module",
            "target_skill",
            "target_handle",
        ):
            explicit_values.update(_normalized_metadata_values(metadata.get(key)))
        for value in _normalized_metadata_values(metadata.get("target_source_path")):
            path = Path(value)
            explicit_values.add(path.stem)
            if path.parent.name:
                explicit_values.add(path.parent.name)
        if normalized in explicit_values:
            candidates.append(workout_id)
    return candidates


def _eval_shard_outcome_proof(repo_root: Path, handle: str) -> dict[str, Any]:
    """Return one current, identity-bound local shard aggregate when available."""
    identity = _skills_sdk_eval_package_identity(repo_root, handle)
    package_id = str((identity or {}).get("package_id") or "").strip()
    package_digest = str((identity or {}).get("package_digest") or "").strip()
    if not package_id or not package_digest or Path(package_id).name != package_id:
        return {"status": "missing", "evidence_class": "outcome_proof"}

    artifacts_root = repo_root / "Infrastructure" / "artifacts" / "skills" / package_id
    current_rubric_digest = _skills_sdk_current_rubric_digest(repo_root)
    accepted: list[tuple[int, dict[str, Any]]] = []
    for candidate in artifacts_root.glob("**/aggregate.json"):
        relative_path = _repo_relative_path(repo_root, candidate)
        if relative_path is None:
            continue
        try:
            envelope = json.loads(candidate.read_text(encoding="utf-8"))
            aggregate = envelope["data"]["skills_sdk_eval_shard_aggregate"]
            receipt = aggregate["receipt"]
        except (KeyError, OSError, TypeError, json.JSONDecodeError):
            continue
        if not isinstance(receipt, dict):
            continue
        checks = receipt.get("checks")
        check_statuses = {
            str(check.get("id")): check.get("status")
            for check in checks
            if isinstance(check, dict)
        } if isinstance(checks, list) else {}
        if (
            envelope.get("status") == "success"
            and aggregate.get("status") == "pass"
            and receipt.get("status") == "pass"
            and receipt.get("lane") == "oss-local"
            and receipt.get("profile") == "oss-local"
            and receipt.get("codex_profile") == "oss-local"
            and current_rubric_digest is not None
            and receipt.get("rubric_digest") == current_rubric_digest
            and receipt.get("package_id") == package_id
            and receipt.get("package_digest") == package_digest
            and check_statuses.get("shards_match_current_package") == "pass"
            and check_statuses.get("all_case_results_pass") == "pass"
        ):
            accepted.append(
                (
                    candidate.stat().st_mtime_ns,
                    {
                        "status": "pass",
                        "evidence_class": "oss_local_release_aggregate",
                        "evidence_ref": relative_path,
                        "evidence_digest": _skills_sdk_digest_file(candidate),
                        "scenario_set": receipt.get("scenario_set_id"),
                        "case_count": receipt.get("case_count"),
                    },
                )
            )
    return max(accepted, key=lambda item: item[0])[1] if accepted else {"status": "missing", "evidence_class": "outcome_proof"}


def _current_release_shard_receipts(
    repo_root: Path,
    *,
    package_id: str,
    package_digest: str,
    scenario_set_id: str,
) -> list[tuple[Path, list[str]]]:
    """Return current, non-overlapping OSS-local release shard receipts and their cases."""
    current_rubric_digest = _skills_sdk_current_rubric_digest(repo_root)
    if current_rubric_digest is None or not package_id or Path(package_id).name != package_id:
        return []
    candidates: list[tuple[int, Path, list[str]]] = []
    receipts_root = repo_root / "Infrastructure" / "artifacts" / "skills" / package_id
    for receipt_path in sorted(receipts_root.glob("**/sdk-eval-run-receipt.json")):
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, TypeError, json.JSONDecodeError):
            continue
        selected = receipt.get("selected_case_ids") if isinstance(receipt, dict) else None
        if (
            not isinstance(selected, list)
            or not selected
            or not all(isinstance(case_id, str) for case_id in selected)
            or len(set(selected)) != len(selected)
        ):
            continue
        if not (
            receipt.get("status") == "pass"
            and receipt.get("lane") == receipt.get("profile") == receipt.get("codex_profile") == "oss-local"
            and receipt.get("lane_type") == "release-shard"
            and receipt.get("rubric_digest") == current_rubric_digest
            and receipt.get("scenario_set_id") == scenario_set_id
            and receipt.get("package_id") == package_id
            and receipt.get("package_digest") == package_digest
            and receipt.get("case_count") == receipt.get("passed_count") == len(selected)
            and receipt.get("failed_count") == 0
        ):
            continue
        candidates.append((receipt_path.stat().st_mtime_ns, receipt_path, selected))

    completed_case_ids: set[str] = set()
    completed: list[tuple[Path, list[str]]] = []
    for _mtime_ns, receipt_path, selected in sorted(candidates, key=lambda item: (item[0], str(item[1])), reverse=True):
        if completed_case_ids.isdisjoint(selected):
            completed.append((receipt_path, selected))
            completed_case_ids.update(selected)
    return sorted(completed, key=lambda item: str(item[0]))


def _outcome_proof_next_command(repo_root: Path, handle: str, fallback: str) -> str:
    """Return the first missing bounded OSS release shard when a valid set is declared."""
    source_path = _skills_sdk_eval_source_path(repo_root, handle)
    if source_path is None:
        return fallback
    release_set = _select_release_scenario_set(
        _load_release_scenario_sets(source_path.parent / "references" / "evals.yaml"),
        scenario_set=None,
    )
    if release_set is None:
        return fallback
    case_ids = list(release_set.get("case_ids") or [])
    try:
        minimum = int(release_set.get("minimum_scenarios") or RELEASE_SCENARIO_MINIMUM)
    except (TypeError, ValueError):
        return fallback
    if not RELEASE_SCENARIO_MINIMUM <= minimum <= len(case_ids) <= RELEASE_SCENARIO_MAXIMUM:
        return fallback
    package_identity = _skills_sdk_eval_package_identity(repo_root, handle)
    if package_identity is None:
        return fallback
    current_receipts = _current_release_shard_receipts(
        repo_root,
        package_id=package_identity["package_id"],
        package_digest=package_identity["package_digest"],
        scenario_set_id=str(release_set["id"]),
    )
    completed_case_ids = {case_id for _receipt_path, selected_case_ids in current_receipts for case_id in selected_case_ids}
    missing_case_ids = [case_id for case_id in case_ids if case_id not in completed_case_ids]
    target = _repo_relative_path(repo_root, source_path.parent) or handle
    if not missing_case_ids:
        aggregate_command = _release_shard_aggregate_command(repo_root, target, str(release_set["id"]), current_receipts)
        return aggregate_command or fallback
    return _skills_sdk_eval_run_validation_command(
        target,
        mode="release",
        codex_profile="oss-local",
        cases=missing_case_ids[:2],
        scenario_set=str(release_set["id"]),
        timeout_seconds=None,
    )


def _release_shard_aggregate_command(
    repo_root: Path,
    target: str,
    scenario_set: str,
    receipts: list[tuple[Path, list[str]]],
) -> str | None:
    """Build the existing aggregate command from current repository-owned receipts."""
    receipt_paths = [_repo_relative_path(repo_root, receipt_path) for receipt_path, _case_ids in receipts]
    if not receipt_paths or not all(receipt_paths):
        return None
    return _ask_validation_command(
        "sdk",
        "eval",
        "aggregate-shards",
        target,
        "--scenario-set",
        scenario_set,
        "--codex-profile",
        "oss-local",
        *[part for receipt_path in receipt_paths for part in ("--receipt", receipt_path)],
    )


def _repo_relative_path(repo_root: Path, path: Path) -> str | None:
    """Return a repo-relative POSIX path when *path* is inside *repo_root*."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


CAPABILITY_LIFECYCLE_EVENT_TYPES = MappingProxyType({
    "skill_loaded": "A skill source or handle was loaded for inspection or execution.",
    "skill_doctor_completed": "A capability doctor run completed with pass, warning, or blocked status.",
    "package_readiness_checked": "A skill package readiness gate completed with pass, warning, or blocked status.",
    "eval_started": "A workout, smoke eval, or proof run started for a capability.",
    "eval_blocked": "A workout, smoke eval, or proof run stopped on a classified blocker.",
    "eval_completed": "A workout, smoke eval, or proof run completed with pass or fail status.",
    "projection_synced": "A canonical skill source was projected into runtime handles or manifests.",
    "manifest_changed": "A skill or skillset manifest changed and may need validation.",
})

__all__ = [name for name in globals() if not name.startswith("__")]
