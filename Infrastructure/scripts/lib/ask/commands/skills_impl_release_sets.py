from __future__ import annotations

from .skills_impl_ab_receipts import *  # noqa: F403

def _skills_sdk_prepare_release_case_filters(
    repo_root: Path,
    *,
    target: str,
    target_path: str,
    mode: str,
    codex_profile: str | None,
    cases: list[str] | None,
    scenario_set: str | None,
    package_identity: dict[str, str] | None,
) -> tuple[list[str] | None, dict[str, Any] | None, CallResult | None]:
    if mode != "release":
        return cases, None, None
    source_path = _skills_sdk_eval_source_path(repo_root, target)
    if source_path is None:
        return cases, None, None
    skill_dir = source_path.parent
    evals_path = skill_dir / "references" / "evals.yaml"
    release_sets = _load_release_scenario_sets(evals_path)
    release_set = _select_release_scenario_set(release_sets, scenario_set)
    selected_case_ids = _flatten_case_filters(cases)
    if scenario_set and release_set is None:
        blocked = _skills_sdk_release_set_blocked_result(
            repo_root,
            target=target,
            target_path=target_path,
            evals_path=evals_path,
            package_identity=package_identity,
            mode=mode,
            codex_profile=codex_profile,
            cases=cases,
            scenario_set=scenario_set,
            selected_case_ids=selected_case_ids,
            release_set=None,
            blocker=f"release_scenario_set_unknown:{scenario_set}",
            message=f"Skills SDK release eval run is blocked: scenario set {scenario_set!r} is not declared.",
        )
        return cases, None, blocked
    if release_sets and release_set is None:
        default_count = sum(1 for item in release_sets if item.get("default") is True)
        blocked = _skills_sdk_release_set_blocked_result(
            repo_root,
            target=target,
            target_path=target_path,
            evals_path=evals_path,
            package_identity=package_identity,
            mode=mode,
            codex_profile=codex_profile,
            cases=cases,
            scenario_set=scenario_set,
            selected_case_ids=selected_case_ids,
            release_set=None,
            blocker=f"release_scenario_set_default_ambiguous:default_count:{default_count}",
            message=(
                "Skills SDK release eval run is blocked: release_scenario_sets must declare "
                "exactly one default or the run must specify --scenario-set."
            ),
        )
        return cases, None, blocked
    if release_set is None:
        return cases, None, None
    release_case_ids = list(release_set["case_ids"])
    minimum = int(release_set.get("minimum_scenarios") or RELEASE_SCENARIO_MINIMUM)
    release_metadata = {
        "scenario_set_id": release_set["id"],
        "scenario_set_case_ids": release_case_ids,
        "release_set_minimum": minimum,
        "lane_type": "release",
    }
    if len(release_case_ids) < minimum:
        blocked = _skills_sdk_release_set_blocked_result(
            repo_root,
            target=target,
            target_path=target_path,
            evals_path=evals_path,
            package_identity=package_identity,
            mode=mode,
            codex_profile=codex_profile,
            cases=cases,
            scenario_set=scenario_set,
            selected_case_ids=release_case_ids,
            release_set=release_set,
            blocker=f"release_scenario_set_under_minimum:{release_set['id']}:count:{len(release_case_ids)}:minimum:{minimum}",
            message=(
                "Skills SDK release eval run is blocked: the selected release scenario set "
                f"{release_set['id']!r} declares {len(release_case_ids)} cases, below the minimum {minimum}."
            ),
        )
        return cases, release_metadata, blocked
    if len(release_case_ids) > RELEASE_SCENARIO_MAXIMUM:
        blocked = _skills_sdk_release_set_blocked_result(
            repo_root,
            target=target,
            target_path=target_path,
            evals_path=evals_path,
            package_identity=package_identity,
            mode=mode,
            codex_profile=codex_profile,
            cases=cases,
            scenario_set=scenario_set,
            selected_case_ids=release_case_ids,
            release_set=release_set,
            blocker=(
                f"release_scenario_set_over_maximum:{release_set['id']}:"
                f"count:{len(release_case_ids)}:maximum:{RELEASE_SCENARIO_MAXIMUM}"
            ),
            message=(
                "Skills SDK release eval run is blocked: the selected release scenario set "
                f"exceeds the {RELEASE_SCENARIO_MAXIMUM}-scenario external-eval budget."
            ),
        )
        return cases, release_metadata, blocked
    if not selected_case_ids:
        return release_case_ids, release_metadata, None
    if len(selected_case_ids) == len(release_case_ids) and set(selected_case_ids) == set(release_case_ids):
        return selected_case_ids, release_metadata, None
    selected_are_unique_members = len(selected_case_ids) == len(set(selected_case_ids)) and set(selected_case_ids) <= set(release_case_ids)
    if codex_profile in {"oss-local", "oss-cloud"} and selected_are_unique_members and 0 < len(selected_case_ids) <= 2:
        release_metadata["lane_type"] = "release-shard"
        return selected_case_ids, release_metadata, None
    blocked = _skills_sdk_release_set_blocked_result(
        repo_root,
        target=target,
        target_path=target_path,
        evals_path=evals_path,
        package_identity=package_identity,
        mode=mode,
        codex_profile=codex_profile,
        cases=cases,
        scenario_set=scenario_set,
        selected_case_ids=selected_case_ids,
        release_set=release_set,
        blocker=(
            f"focused_debug_subset_not_release_evidence:selected:{len(selected_case_ids)}:"
            f"required:{len(release_case_ids)}:minimum:{minimum}"
        ),
        message=(
            "Skills SDK release eval run is blocked: explicit --case filters are a focused-debug subset, "
            f"not {codex_profile} release-lane evidence for scenario set {release_set['id']}."
        ),
    )
    return cases, release_metadata, blocked


def _skills_sdk_eval_codex_profile_proof(
    internal: CallResult,
    *,
    codex_profile: str | None,
) -> dict[str, object]:
    profile_contract = internal.data.get("profile_contract")
    if not isinstance(profile_contract, dict):
        profile_contract = {}
    invoked = profile_contract.get("codex_exec_invoked") is True
    observed_profile = profile_contract.get("codex_profile")
    command_shape = profile_contract.get("codex_exec_command_shape")
    return {
        "codex_profile": observed_profile if isinstance(observed_profile, str) else None,
        "codex_exec_invoked": invoked,
        "codex_exec_command_shape": command_shape if isinstance(command_shape, list) else None,
        "matches_requested_profile": bool(codex_profile) and invoked and observed_profile == codex_profile,
    }


def _attach_phoenix_eval_trace(
    payload: dict[str, Any],
    repo_root: Path,
    receipt: dict[str, Any],
    *,
    command_name: str = "sdk eval run",
    profile: str | None = None,
) -> None:
    schema_version = "skills-sdk.phoenix-eval-trace-receipt.v1"
    try:
        from ask.skills_sdk.phoenix_observability import (  # noqa: PLC0415
            PHOENIX_EVAL_TRACE_SCHEMA_VERSION,
            build_phoenix_eval_trace_receipt,
        )

        schema_version = PHOENIX_EVAL_TRACE_SCHEMA_VERSION
        payload["phoenix_eval_trace"] = build_phoenix_eval_trace_receipt(
            repo_root,
            eval_receipt=receipt,
            command_name=command_name,
            profile=profile,
        )
    except (ImportError, KeyError, OSError, TypeError, ValueError) as exc:
        payload["phoenix_eval_trace"] = {
            "schema_version": schema_version,
            "schema_uri": "https://agent-skills.local/schemas/skills-sdk/phoenix-eval-trace-receipt.v1.schema.json",
            "status": "blocked",
            "operation": "phoenix_eval_trace",
            "source_receipt_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
            "source_kind": "unsupported_receipt",
            "eval_status": receipt.get("status"),
            "observability_status": "blocked",
            "runner": receipt.get("runner"),
            "mode": receipt.get("mode"),
            "profile": None,
            "profile_evidence": [],
            "target_path": None,
            "package_id": receipt.get("package_id"),
            "package_digest": receipt.get("package_digest"),
            "case_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "project_name": "agent-skills-skills-sdk-evals",
            "trace_id": "00000000000000000000000000000000",
            "root_span_id": "0000000000000000",
            "span_plan": [],
            "planned_span_count": 0,
            "emitted_span_count": 0,
            "case_span_trace_enabled": False,
            "case_span_limit": 0,
            "case_span_count": 0,
            "enabled": False,
            "emitted_spans": [],
            "checks": [],
            "blockers": [
                {
                    "id": "phoenix_eval_trace_unexpected_error",
                    "status": "blocker",
                    "severity": "blocker",
                    "message": "Phoenix eval trace emission raised an unexpected error.",
                    "evidence": [f"error_class:{type(exc).__name__}"],
                }
            ],
            "mutation_performed": False,
            "acceptance_trace": ["phoenix-oss-eval-observability-workflow-2026-07-08", "PU-026"],
            "agent_summary": f"Phoenix eval trace blocked due to unexpected error: {type(exc).__name__}",
        }


def skills_sdk_eval_run(
    repo_root: Path,
    dataset: str | None = None,
    target: str | None = None,
    mode: str = "smoke",
    runner: str = "auto",
    skip_tessl: bool = True,
    codex_profile: str | None = None,
    cases: list[str] | None = None,
    scenario_set: str | None = None,
    timeout_seconds: int | None = None,
) -> CallResult:
    """Run SDK evals through deterministic JSONL or the internal skill-builder backend."""
    result = CallResult()
    result.metadata["command"] = "sdk eval run"
    if not skip_tessl:
        result.status = "error"
        result.data["skills_sdk_eval_run"] = {
            "schema_version": "skills-sdk-eval-run.v0",
            "status": "blocked",
            "dataset": dataset,
            "target": target,
            "runner": runner,
            "receipt": None,
            "mutation_performed": False,
            "validation_commands": [
                "./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot",
                "./bin/ask evals run <skill> --tessl-live-private --tessl-workspace <workspace> --json --robot",
            ],
            "agent_summary": "sdk eval run is local-only; direct Tessl continuation is retired in favor of the guarded live-private handoff route.",
        }
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="sdk eval run does not submit Tessl evals; use the guarded live-private handoff route.",
            fix_suggestion="./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot",
        ))
        return result
    resolved_runner = "deterministic-jsonl" if runner == "auto" and dataset else runner
    if resolved_runner == "auto":
        resolved_runner = "internal"
    if resolved_runner == "internal":
        if not target:
            result.status = "error"
            result.data["skills_sdk_eval_run"] = {
                "schema_version": "skills-sdk-eval-run.v0",
                "status": "blocked",
                "dataset": dataset,
                "target": target,
                "runner": "internal_skill_builder_v0",
                "receipt": None,
                "mutation_performed": False,
                "validation_commands": [_ask_validation_command("sdk", "eval", "run", "<skill>", "--runner", "internal")],
                "agent_summary": "skills-sdk eval run is blocked: internal runner requires a skill target.",
            }
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK internal eval run requires a skill target.",
                    fix_suggestion="Run ask sdk eval run <skill> --runner internal --mode smoke --json --robot.",
                )
            )
            return result
        from ask.commands import evals as _eval_commands  # noqa: PLC0415

        target_path = str(_skills_sdk_eval_source_path(repo_root, target) or target)
        package_identity = _skills_sdk_eval_package_identity(repo_root, target_path)
        cases, release_set_metadata, release_set_blocked = _skills_sdk_prepare_release_case_filters(
            repo_root,
            target=target,
            target_path=target_path,
            mode=mode,
            codex_profile=codex_profile,
            cases=cases,
            scenario_set=scenario_set,
            package_identity=package_identity,
        )
        if release_set_blocked is not None:
            return release_set_blocked

        internal = _eval_commands.run_evals(
            repo_root,
            target,
            mode=mode,
            runner="codex",
            dashboard=False,
            skip_tessl=skip_tessl,
            codex_profile=codex_profile,
            cases=cases,
            timeout_seconds=timeout_seconds,
        )
        raw_status = str(internal.data.get("eval_status") or ("pass" if internal.status == "success" else "fail"))
        blockers = []
        if internal.status != "success":
            blockers = [error.message for error in internal.errors] or [raw_status]
        status = "pass" if internal.status == "success" else "blocked" if raw_status.startswith("blocked") else "fail"
        target_path = str(internal.data.get("resolved_skill_path") or target_path)
        if package_identity is None:
            package_identity = _skills_sdk_eval_package_identity(repo_root, target_path)
        receipt_counts = _skills_sdk_internal_eval_receipt_counts(
            repo_root,
            internal,
            status=status,
            fallback_blockers=blockers,
            eval_commands=_eval_commands,
        )
        profile_proof = _skills_sdk_eval_codex_profile_proof(internal, codex_profile=codex_profile)
        identity_source_path = _skills_sdk_eval_source_path(repo_root, target)
        eval_lane = _skills_sdk_eval_receipt_lane(mode, codex_profile)
        execution_identity = _skills_sdk_eval_execution_identity(
            identity_source_path.parent / "references" / "evals.yaml"
            if identity_source_path is not None
            else Path(""),
            eval_lane,
        )
        if execution_identity is None:
            execution_identity = _skills_sdk_eval_profile_execution_identity(codex_profile)
        profile_blockers: list[str] = []
        if codex_profile in {"oss-local", "oss-cloud"} and not profile_proof["matches_requested_profile"]:
            profile_blockers.append(f"blocked_missing_artifact:codex_profile_exec_receipt_missing:{codex_profile}")
        identity_blockers: list[str] = []
        if eval_lane in {"oss-local", "oss-cloud"} and execution_identity is None:
            identity_blockers.append(f"blocked_missing_artifact:execution_identity_missing:{eval_lane}")
        proof_blockers = [*profile_blockers, *identity_blockers]
        receipt = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "schema_uri": "https://agent-skills.local/schemas/skills-sdk/eval-run-receipt.v0.schema.json",
            "status": "blocked" if proof_blockers and receipt_counts["status"] == "pass" else receipt_counts["status"],
            "runner": "internal_skill_builder_v0",
            "dataset_path": receipt_counts["dataset_path"],
            "dataset_digest": receipt_counts["dataset_digest"],
            "skill_ir_schema_version": package_identity["skill_ir_schema_version"] if package_identity else None,
            "package_id": package_identity["package_id"] if package_identity else None,
            "package_digest": package_identity["package_digest"] if package_identity else None,
            "rubric_digest": _skills_sdk_digest_file(repo_root / "Infrastructure/config/skills-sdk/gold-standard-rubric.v1.json"),
            "target_path": target_path,
            "mode": mode,
            "lane": eval_lane,
            "lane_type": release_set_metadata["lane_type"] if release_set_metadata else mode,
            "profile": codex_profile,
            "codex_profile": profile_proof["codex_profile"],
            "codex_exec_invoked": profile_proof["codex_exec_invoked"],
            "codex_exec_command_shape": profile_proof["codex_exec_command_shape"],
            **_skills_sdk_eval_identity_fields(execution_identity),
            "scenario_set_id": release_set_metadata["scenario_set_id"] if release_set_metadata else scenario_set,
            "scenario_set_case_ids": release_set_metadata["scenario_set_case_ids"] if release_set_metadata else None,
            "selected_case_ids": _flatten_case_filters(cases),
            "release_set_minimum": release_set_metadata["release_set_minimum"] if release_set_metadata else None,
            "case_count": receipt_counts["case_count"],
            "passed_count": receipt_counts["passed_count"],
            "failed_count": max(1, receipt_counts["failed_count"]) if proof_blockers else receipt_counts["failed_count"],
            "quality_gates": receipt_counts["quality_gates"],
            "closeout_validation": receipt_counts.get("closeout_validation"),
            "cases": receipt_counts["cases"],
            "blockers": sorted(set([*receipt_counts["blockers"], *proof_blockers])),
            "mutation_performed": False,
            "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"],
        }
        status = receipt["status"]
        receipt_path = _skills_sdk_persist_eval_run_receipt(repo_root, receipt)
        payload = {
            "schema_version": "skills-sdk-eval-run.v0",
            "status": status,
            "dataset": dataset,
            "target": target,
            "runner": "internal_skill_builder_v0",
            "mode": mode,
            "receipt": receipt,
            "receipt_path": receipt_path,
            "internal_eval": internal.data,
            "mutation_performed": False,
            "validation_commands": [
                _skills_sdk_eval_run_validation_command(
                    target,
                    mode=mode,
                    codex_profile=codex_profile,
                    cases=cases,
                    scenario_set=scenario_set,
                    timeout_seconds=timeout_seconds,
                )
            ],
            "agent_summary": f"skills-sdk internal eval run {status} for {target} in {mode} mode.",
        }
        _attach_phoenix_eval_trace(payload, repo_root, receipt, profile=codex_profile)
        result.data["skills_sdk_eval_run"] = payload
        if status != "pass":
            result.status = "error"
            result.errors.extend(internal.errors)
            if not result.errors:
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message=f"Skills SDK internal eval run did not pass for {target}.",
                        fix_suggestion=_ask_validation_command("sdk", "eval", "run", target, "--runner", "internal", "--mode", mode),
                    )
                )
        return result

    if resolved_runner != "deterministic-jsonl":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Unsupported Skills SDK eval runner: {runner}.",
                fix_suggestion="Use --runner internal or --runner deterministic-jsonl.",
            )
        )
        return result
    if not dataset:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skills SDK deterministic eval run requires --dataset.",
                fix_suggestion="Run ask sdk eval run --runner deterministic-jsonl --dataset <cases.jsonl> --json --robot.",
            )
        )
        return result
    package_identity: dict[str, str] | None = None
    if target:
        query = target.strip()
        package_identity = _skills_sdk_eval_package_identity(repo_root, query)
        if package_identity is None:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Skills SDK eval run is missing a canonical SKILL.md source for '{query}'.",
                    fix_suggestion=_ask_validation_command("sdk", "ir", "build", query),
                )
            )
            result.data["skills_sdk_eval_run"] = {
                "schema_version": "skills-sdk-eval-run.v0",
                "status": "blocked",
                "dataset": dataset,
                "target": query,
                "receipt": None,
                "mutation_performed": False,
                "validation_commands": [_ask_validation_command("sdk", "eval", "run", "--dataset", dataset, "--skill", query)],
                "agent_summary": f"skills-sdk eval run is blocked for {query}: canonical source is missing.",
            }
            return result

    receipt = _run_deterministic_eval(
        repo_root,
        dataset=dataset,
        skill_ir_schema_version=package_identity["skill_ir_schema_version"] if package_identity else None,
        package_id=package_identity["package_id"] if package_identity else None,
        package_digest=package_identity["package_digest"] if package_identity else None,
    )
    payload = {
        "schema_version": "skills-sdk-eval-run.v0",
        "status": receipt["status"],
        "dataset": dataset,
        "target": target,
        "runner": receipt["runner"],
        "case_count": receipt["case_count"],
        "passed_count": receipt["passed_count"],
        "failed_count": receipt["failed_count"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "run", "--dataset", dataset)],
        "agent_summary": (
            f"skills-sdk eval run {receipt['status']} with "
            f"{receipt['passed_count']}/{receipt['case_count']} deterministic JSONL case(s) passing."
        ),
    }
    _attach_phoenix_eval_trace(payload, repo_root, receipt, profile=codex_profile)
    if target:
        payload["validation_commands"] = [
            _ask_validation_command("sdk", "eval", "run", "--dataset", dataset, "--skill", target)
        ]
    result.data["skills_sdk_eval_run"] = payload
    if receipt["status"] != "pass":
        result.status = "error"
        message = "Skills SDK deterministic eval run did not pass."
        if receipt["status"] == "blocked" and receipt["blockers"]:
            message = f"Skills SDK deterministic eval run blocked: {receipt['blockers'][0]}"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion="Fix the JSONL eval dataset or expected/actual exact-match values and rerun ask sdk eval run.",
            )
        )
    return result


def _sdk_improve_timestamp() -> str:
    value = os.environ.get("ASK_SKILLS_SDK_IMPROVE_TIMESTAMP")
    if value:
        return value
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sdk_improve_receipt_slug(package_id: str, timestamp: str) -> str:
    safe_time = re.sub(r"[^0-9A-Za-z_.-]+", "-", timestamp).strip("-")
    safe_package = re.sub(r"[^0-9A-Za-z_.-]+", "-", package_id).strip("-") or "unknown"
    return f"{safe_package}-{safe_time}"


def _sdk_improve_project_root(project_root: str | None) -> Path | None:
    if not project_root:
        return None
    candidate = Path(project_root).expanduser()
    if not candidate.is_absolute():
        return None
    try:
        return candidate.resolve(strict=True)
    except OSError:
        return None


def _sdk_improve_load_manifest(project_root: Path) -> tuple[Path, _ManifestEvaluation]:
    manifest_path = project_root / PROJECT_SKILLS_SDK_MANIFEST
    evaluation = _evaluate_manifest_file(manifest_path, display_path=PROJECT_SKILLS_SDK_MANIFEST)
    return manifest_path, evaluation


def _sdk_improve_project_id(manifest: dict[str, Any] | None, project_root: Path) -> str:
    if isinstance(manifest, dict):
        project = manifest.get("project")
        if isinstance(project, dict) and isinstance(project.get("id"), str) and project["id"].strip():
            return project["id"].strip()
        if isinstance(manifest.get("project_id"), str) and manifest["project_id"].strip():
            return manifest["project_id"].strip()
    return project_root.name


def _sdk_improve_evidence_paths(project_root: Path, manifest: dict[str, Any] | None, slug: str) -> dict[str, Path]:
    evidence = manifest.get("evidence") if isinstance(manifest, dict) else None
    evidence = evidence if isinstance(evidence, dict) else {}
    registry = _resolve_project_relative_config_path(
        project_root,
        str(evidence.get("registry") or ".harness/skills/registry.json"),
    )
    events = _resolve_project_relative_config_path(
        project_root,
        str(evidence.get("events") or ".harness/skills/events.jsonl"),
    )
    receipts_root = _resolve_project_relative_config_path(
        project_root,
        str(evidence.get("receipts") or ".harness/skills/receipts"),
    )
    if registry is None or events is None or receipts_root is None:
        raise ValueError("Project evidence paths must be relative paths inside project_root.")
    return {
        "registry": registry,
        "events": events,
        "receipt": receipts_root / "improvements" / f"{slug}.json",
    }


def _sdk_improve_project_relative(project_root: Path, path: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def _sdk_improve_load_registry(path: Path, project_id: str, manifest_path: str) -> dict[str, Any]:
    if not path.exists():
        payload = {}
    else:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid skills registry JSON at {path}: {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Unable to read skills registry at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Skills registry JSON must be an object at {path}.")
    payload.setdefault("schema_version", "skills-sdk.project-skill-registry.v1")
    payload.setdefault("project", {"id": project_id, "manifest": manifest_path})
    payload.setdefault("summary", {})
    payload.setdefault("skills", [])
    if not isinstance(payload["skills"], list):
        raise ValueError(f"Skills registry JSON field 'skills' must be a list at {path}.")
    return payload


def _sdk_improve_update_registry(
    registry: dict[str, Any],
    *,
    project_id: str,
    handle: str,
    source_path: str,
    source_root: str,
    hardening_receipt: dict[str, Any],
    eval_receipt: dict[str, Any] | None,
    improvement_status: str,
    receipt_path: str,
    timestamp: str,
    source_edit_status: str,
) -> None:
    skill_id = f"{project_id}:{handle}"
    skills = registry.setdefault("skills", [])
    if not isinstance(skills, list):
        skills = []
        registry["skills"] = skills
    entry = None
    for item in skills:
        if not isinstance(item, dict):
            continue
        if item.get("skill_id") == skill_id or item.get("handle") == handle:
            entry = item
            break
    if entry is None:
        entry = {
            "skill_id": skill_id,
            "handle": handle,
            "scope": "project",
            "source": {
                "path": source_path,
                "root": source_root,
                "kind": "canonical_project_source",
            },
            "runtime": {
                "workspace_projection": "not_run",
                "user_projection": "not_run",
                "invocation": "not_run",
            },
        }
        skills.append(entry)
    entry["skill_id"] = skill_id
    entry["handle"] = handle
    entry["scope"] = "project"
    entry["source"] = {
        "path": source_path,
        "root": source_root,
        "kind": "canonical_project_source",
    }
    entry["lifecycle"] = {
        "state": "validated" if improvement_status == "pass" else "blocked",
        "decision": (
            "improve_validated_no_source_patch"
            if improvement_status == "pass" and source_edit_status == "not_requested"
            else "improve_blocked"
        ),
        "updated_at": timestamp,
    }
    entry["package"] = {
        "hardening_status": hardening_receipt.get("status"),
        "package_digest": hardening_receipt.get("package_digest"),
        "file_count": hardening_receipt.get("file_count"),
        "blockers": hardening_receipt.get("blockers", []),
        "warnings": hardening_receipt.get("warnings", []),
    }
    entry["evals"] = {
        "status": eval_receipt.get("status") if eval_receipt else "not_run",
        "runner": eval_receipt.get("runner") if eval_receipt else None,
        "lane": eval_receipt.get("lane") if eval_receipt else None,
        "profile": eval_receipt.get("profile") if eval_receipt else None,
        "case_count": eval_receipt.get("case_count") if eval_receipt else 0,
        "passed_count": eval_receipt.get("passed_count") if eval_receipt else 0,
        "failed_count": eval_receipt.get("failed_count") if eval_receipt else 0,
    }
    missing_promotion_evidence: list[str] = []
    if hardening_receipt.get("status") != "pass":
        missing_promotion_evidence.append("package hardening pass")
    if not eval_receipt:
        missing_promotion_evidence.append("eval run receipt")
    elif eval_receipt.get("status") != "pass":
        missing_promotion_evidence.append(f"eval pass receipt ({eval_receipt.get('status')})")
    closeout_validation = eval_receipt.get("closeout_validation") if eval_receipt else None
    if isinstance(closeout_validation, dict) and closeout_validation.get("status") != "pass":
        missing_promotion_evidence.append("workflow-closeout/v1 validation pass")
    entry["promotion"] = {
        "allowed": improvement_status == "pass" and not missing_promotion_evidence,
        "state": "promoted" if improvement_status == "pass" and not missing_promotion_evidence else "blocked",
        "missing": missing_promotion_evidence,
        "updated_at": timestamp,
    }
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
    evidence["last_improvement_receipt"] = receipt_path
    evidence["last_improvement_at"] = timestamp
    entry["evidence"] = evidence
    summary = registry.setdefault("summary", {})
    if isinstance(summary, dict):
        summary["skill_count"] = len([item for item in skills if isinstance(item, dict)])
        summary["last_improvement_receipt"] = receipt_path
        summary["last_improvement_at"] = timestamp


_SDK_IMPROVE_SENSITIVE_KEY_MARKERS = (
    "api_key",
    "apikey",
    "auth",
    "cookie",
    "credential",
    "password",
    "secret",
    "token",
)

__all__ = [name for name in globals() if not name.startswith("__")]
