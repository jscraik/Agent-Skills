from __future__ import annotations

from yaml import YAMLError

from .skills_impl_plugin_ab import *  # noqa: F403

def _ab_receipt_kwargs(repo_root: Path, request: AbEvalRequest) -> dict[str, object]:
    return {
        "repo_root": repo_root, "skill_a": request.skill_a, "skill_b": request.skill_b,
        "fixture": request.fixture,
        "skill_a_identity": _skills_sdk_eval_package_identity(repo_root, request.skill_a),
        "skill_b_identity": _skills_sdk_eval_package_identity(repo_root, request.skill_b),
        "execution_profile_id": request.execution_profile, "judge_profile_id": request.judge_profile,
        "execution_lane": request.execution_lane, "evidence_root": request.evidence_root,
    }


def _ab_validation_command(action: str, request: AbEvalRequest) -> str:
    args = ["sdk", "eval", action, "--skill-a", request.skill_a, "--skill-b", request.skill_b,
            "--fixture", request.fixture, "--execution-profile", request.execution_profile,
            "--judge-profile", request.judge_profile, "--execution-lane", request.execution_lane,
            "--evidence-root", request.evidence_root]
    args += ["--timeout-seconds", str(request.timeout_seconds), "--execute"] if action == "ab-run" else ["--preview"]
    return _ask_validation_command(*args)


def _ab_blocked_result(result: CallResult, receipt: dict[str, object], fix: str) -> None:
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=receipt["agent_summary"], fix_suggestion=fix))


def _ab_plan_payload(receipt: dict[str, object], request: AbEvalRequest) -> dict[str, object]:
    return {"schema_version": "skills-sdk-ab-plan.v0", "status": receipt["status"],
            "facade_command": "skills-sdk eval ab-plan", "receipt": receipt,
            "mutation_performed": False, "validation_commands": [_ab_validation_command("ab-plan", request)],
            "agent_summary": receipt["agent_summary"]}


def _ab_run_payload(repo_root: Path, receipt: dict[str, object], request: AbEvalRequest) -> dict[str, object]:
    payload = {"schema_version": "skills-sdk-ab-run.v0", "status": receipt["status"],
               "facade_command": "skills-sdk eval ab-run", "receipt": receipt,
               "mutation_performed": receipt["mutation_performed"],
               "validation_commands": [_ab_validation_command("ab-run", request)],
               "agent_summary": receipt["agent_summary"]}
    _attach_phoenix_eval_trace(payload, repo_root, receipt, command_name="sdk eval ab-run")
    return payload


def skills_sdk_eval_ab_plan(repo_root: Path, request: AbEvalRequest) -> CallResult:
    """Emit a non-mutating Codex-backed A/B eval execution plan."""
    from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt  # noqa: PLC0415

    result = CallResult()
    result.metadata["command"] = "sdk eval ab-plan --preview"
    receipt = build_ab_plan_receipt(**_ab_receipt_kwargs(repo_root, request))
    result.data["skills_sdk_eval_ab_plan"] = _ab_plan_payload(receipt, request)
    _ab_blocked_result(result, receipt, "Use canonical repo-local skill sources, fixture, and evidence root before ask sdk eval ab-plan.")
    return result


def skills_sdk_eval_ab_run(repo_root: Path, request: AbEvalRequest) -> CallResult:
    """Execute a Codex-backed A/B eval and emit bounded evidence receipts."""
    from ask.skills_sdk.eval_ab_run import build_ab_run_receipt  # noqa: PLC0415

    result = CallResult()
    result.metadata["command"] = "sdk eval ab-run --execute"
    kwargs = _ab_receipt_kwargs(repo_root, request)
    kwargs["timeout_seconds"] = request.timeout_seconds
    receipt = build_ab_run_receipt(**kwargs)
    result.data["skills_sdk_eval_ab_run"] = _ab_run_payload(repo_root, receipt, request)
    _ab_blocked_result(result, receipt, "Review per-variant blockers and Codex captures before rerunning ask sdk eval ab-run.")
    return result


def skills_sdk_eval_ab_judge_preview(
    repo_root: Path,
    *,
    run_receipt: str,
) -> CallResult:
    """Emit a non-mutating sanitized A/B judge input receipt."""
    from ask.skills_sdk.eval_ab_judge import build_ab_judge_preview_receipt  # noqa: PLC0415

    result = CallResult()
    result.metadata["command"] = "sdk eval ab-judge-preview --preview"
    receipt = build_ab_judge_preview_receipt(repo_root, run_receipt=run_receipt)
    payload = {
        "schema_version": "skills-sdk-ab-judge-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-judge-preview",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-judge-preview",
                "--run-receipt",
                run_receipt,
                "--preview",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_judge_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Provide a repo-local completed ab-run receipt before previewing judge input."
                ),
            )
        )
    return result


def skills_sdk_eval_ab_judge_score(
    repo_root: Path,
    *,
    run_receipt: str,
    evidence_root: str = ".harness/artifacts/sdk-ab-judges",
    judge_profile: str = "oss-local",
    timeout_seconds: int = 300,
) -> CallResult:
    """Invoke Codex-backed A/B judge scoring and emit advisory decision evidence."""
    from ask.skills_sdk.eval_ab_judge import build_ab_judge_score_receipt  # noqa: PLC0415

    result = CallResult()
    result.metadata["command"] = "sdk eval ab-judge-score --execute"
    receipt = build_ab_judge_score_receipt(
        repo_root,
        run_receipt=run_receipt,
        evidence_root=evidence_root,
        judge_profile_id=judge_profile,
        timeout_seconds=timeout_seconds,
    )
    payload = {
        "schema_version": "skills-sdk-ab-judge-score.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-judge-score",
        "receipt": receipt,
        "mutation_performed": receipt["mutation_performed"],
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-judge-score",
                "--run-receipt",
                run_receipt,
                "--evidence-root",
                evidence_root,
                "--judge-profile",
                judge_profile,
                "--timeout-seconds",
                str(timeout_seconds),
                "--execute",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    _attach_phoenix_eval_trace(
        payload,
        repo_root,
        receipt,
        command_name="sdk eval ab-judge-score",
    )
    result.data["skills_sdk_eval_ab_judge_score"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Provide a completed ab-run receipt and the selected Codex judge profile before "
                    "running ask sdk eval ab-judge-score."
                ),
            )
        )
    return result


def _skills_sdk_internal_case_results(scorecard: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    cases: list[dict[str, str]] = []
    blockers: list[str] = []
    raw_cases = scorecard.get("cases")
    if not isinstance(raw_cases, list):
        return cases, blockers

    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            continue
        case_id = str(raw_case.get("id") or raw_case.get("name") or f"case-{index}").strip()
        if not case_id:
            case_id = f"case-{index}"
        passed = raw_case.get("passed") is True
        blocked = raw_case.get("blocked") is True
        status = "pass" if passed else "fail"
        raw_blockers = raw_case.get("blocked_reasons")
        if isinstance(raw_blockers, list):
            blockers.extend(str(reason) for reason in raw_blockers if str(reason).strip())
        raw_blocker_classes = raw_case.get("blocker_classes")
        if isinstance(raw_blocker_classes, list):
            blockers.extend(str(reason) for reason in raw_blocker_classes if str(reason).strip())
        tier1_failures = raw_case.get("tier1_failures")
        if not passed and isinstance(tier1_failures, list):
            blockers.extend(str(reason) for reason in tier1_failures if str(reason).strip())
        actual = "blocked" if blocked else status
        cases.append(
            {
                "case_id": case_id,
                "status": status,
                "oracle": "exact_match",
                "expected": "pass",
                "actual": actual,
            }
        )
    return cases, sorted(set(blockers))


def _skills_sdk_internal_eval_receipt_counts(
    repo_root: Path,
    internal: CallResult,
    *,
    status: str,
    fallback_blockers: list[str],
    eval_commands: _EvalCommandsProtocol,
) -> dict[str, Any]:
    raw_output = str(internal.data.get("raw_output") or "")
    scorecard_path = eval_commands._scorecard_path_from_output(repo_root, raw_output)  # noqa: SLF001
    scorecard = eval_commands._read_scorecard(scorecard_path)  # noqa: SLF001
    quality_gates = _internal_scorecard_quality_gates(scorecard)
    closeout = internal.data.get("eval_closeout")
    closeout_validation = (
        eval_commands.validate_eval_closeout_payload(closeout)
        if isinstance(closeout, dict) and hasattr(eval_commands, "validate_eval_closeout_payload")
        else None
    )
    quality_blockers = (
        [f"quality_gate_failed:{item}" for item in quality_gates["failed_assertions"]]
        if quality_gates and quality_gates["failed_assertions"]
        else []
    )
    cases, case_blockers = _skills_sdk_internal_case_results(scorecard)
    if cases:
        failed_count = sum(1 for item in cases if item["status"] == "fail")
        receipt_status = status if status != "pass" else "fail" if failed_count or quality_blockers else "pass"
        blockers = sorted(set(fallback_blockers + case_blockers + quality_blockers)) if receipt_status != "pass" else []
        dataset_path = (
            _skills_sdk_repo_relative(repo_root, scorecard_path)
            if scorecard_path is not None and scorecard_path.is_file()
            else "internal:skill-builder"
        )
        dataset_digest = (
            _skills_sdk_digest_file(scorecard_path)
            if scorecard_path is not None and scorecard_path.is_file()
            else None
        )
        return {
            "status": receipt_status,
            "dataset_path": dataset_path,
            "dataset_digest": dataset_digest,
            "case_count": len(cases),
            "passed_count": len(cases) - failed_count,
            "failed_count": failed_count,
            "quality_gates": quality_gates,
            "closeout_validation": closeout_validation,
            "cases": cases,
            "blockers": blockers,
        }

    if isinstance(closeout, dict):
        closeout_status = str(closeout.get("status") or status)
        closeout_cases = closeout.get("cases")
        cases = []
        if isinstance(closeout_cases, list):
            for index, raw_case in enumerate(closeout_cases, start=1):
                if not isinstance(raw_case, dict):
                    continue
                case_id = str(raw_case.get("id") or f"case-{index}")
                case_status = str(raw_case.get("status") or "blocked")
                actual = case_status
                cases.append(
                    {
                        "case_id": case_id,
                        "status": "pass" if case_status == "pass" else "fail",
                        "oracle": "eval_closeout",
                        "expected": "pass",
                        "actual": actual,
                    }
                )
        closeout_blockers = list(fallback_blockers + quality_blockers)
        if isinstance(closeout_validation, dict) and closeout_validation.get("status") != "pass":
            for blocker in closeout_validation.get("blockers") or []:
                if isinstance(blocker, dict):
                    closeout_blockers.append(f"closeout_validation:{blocker.get('id')}")
        blocker_class = closeout.get("blocker_class")
        if blocker_class:
            closeout_blockers.append(str(blocker_class))
        for raw_case in closeout_cases if isinstance(closeout_cases, list) else []:
            if not isinstance(raw_case, dict):
                continue
            if raw_case.get("blocker_class"):
                closeout_blockers.append(str(raw_case["blocker_class"]))
            for reason in raw_case.get("blocked_reasons") or []:
                closeout_blockers.append(str(reason))
            for failure in raw_case.get("failures") or []:
                closeout_blockers.append(str(failure))
        if closeout_blockers and closeout_status == "pass":
            closeout_status = "blocked"
        closeout_path = closeout.get("path")
        dataset_path = str(closeout_path or "internal:skill-builder-closeout")
        digest_path = repo_root / dataset_path if closeout_path and not Path(str(closeout_path)).is_absolute() else Path(str(closeout_path or ""))
        dataset_digest = (
            _skills_sdk_digest_file(digest_path)
            if closeout_path and digest_path.is_file()
            else None
        )
        failed_count = sum(1 for item in cases if item["status"] == "fail")
        return {
            "status": closeout_status,
            "dataset_path": dataset_path,
            "dataset_digest": dataset_digest,
            "case_count": len(cases),
            "passed_count": len(cases) - failed_count,
            "failed_count": failed_count,
            "quality_gates": quality_gates,
            "closeout_validation": closeout_validation,
            "cases": cases,
            "blockers": sorted(set(closeout_blockers)) if closeout_status != "pass" else [],
        }

    synthetic_blockers = list(fallback_blockers + quality_blockers)
    if status == "pass":
        synthetic_blockers.append("blocked_missing_artifact:no_scorecard_or_closeout")
    internal_case_count = 0 if status == "blocked" else 1
    if status == "pass":
        receipt_status = "blocked"
    elif quality_blockers:
        receipt_status = "fail"
    else:
        receipt_status = status
    missing_artifact_check = {
        "id": "blocked_missing_artifact:no_scorecard_or_closeout",
        "status": "blocker",
        "message": "Internal eval runner did not emit a scorecard or workflow closeout receipt.",
        "evidence": ["raw_output"],
    }
    return {
        "status": receipt_status,
        "dataset_path": "internal:skill-builder",
        "dataset_digest": None,
        "case_count": internal_case_count,
        "passed_count": 0,
        "failed_count": 1 if receipt_status in {"fail", "blocked"} else 0,
        "quality_gates": quality_gates,
        "closeout_validation": {
            "schema_version": "skills-sdk.eval-closeout-validation.v1",
            "status": "blocked",
            "checks": [missing_artifact_check],
            "blockers": [missing_artifact_check],
        } if status == "pass" else {},
        "cases": [],
        "blockers": sorted(set(synthetic_blockers)),
    }


def _skills_sdk_persist_eval_run_receipt(repo_root: Path, receipt: dict[str, Any]) -> str | None:
    """Persist an existing eval receipt only beside a repository-owned report."""
    dataset_path = str(receipt.get("dataset_path") or "")
    if not dataset_path or dataset_path.startswith("internal:"):
        return None
    candidate = Path(dataset_path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    try:
        report_path = candidate.resolve(strict=True)
        report_path.relative_to((repo_root / "Infrastructure" / "artifacts").resolve(strict=True))
    except (OSError, ValueError):
        return None
    receipt_path = report_path.parent / "sdk-eval-run-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _skills_sdk_repo_relative(repo_root, receipt_path)


def _skills_sdk_eval_run_validation_command(
    target: str,
    *,
    mode: str,
    codex_profile: str | None,
    cases: list[str] | None,
    scenario_set: str | None = None,
    timeout_seconds: int | None,
) -> str:
    args = [
        "sdk",
        "eval",
        "run",
        target,
        "--runner",
        "internal",
        "--mode",
        mode,
    ]
    if codex_profile:
        args.extend(["--codex-profile", codex_profile])
    if scenario_set:
        args.extend(["--scenario-set", scenario_set])
    for case in cases or []:
        args.extend(["--case", case])
    if timeout_seconds:
        args.extend(["--timeout-seconds", str(timeout_seconds)])
    return _ask_validation_command(*args)


def _skills_sdk_eval_receipt_lane(mode: str, codex_profile: str | None) -> str:
    if codex_profile in {"oss-local", "oss-cloud"}:
        return codex_profile
    if codex_profile in {"fast", "codex-fast"}:
        return "codex-fast-smoke"
    return mode


def _skills_sdk_eval_execution_identity(evals_path: Path, lane: str | None) -> dict[str, str] | None:
    if not evals_path.is_file():
        return None
    try:
        from ask.skills_sdk.eval_lane_policy import eval_lane_execution_identity  # noqa: PLC0415
        from ask.skills_sdk.scenario_quality import _yaml_safe_load  # noqa: PLC0415

        payload = _yaml_safe_load(evals_path.read_text(encoding="utf-8")) or {}
    except (OSError, RuntimeError, TypeError, ValueError):
        return None
    return eval_lane_execution_identity(payload, lane)


def _skills_sdk_eval_profile_execution_identity(codex_profile: str | None) -> dict[str, str] | None:
    """Read the executed OSS profile identity when a skill has no lane-policy override."""
    if codex_profile not in {"oss-local", "oss-cloud"}:
        return None
    profile_path = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / f"{codex_profile}.config.toml"
    try:
        profile = tomllib.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    model = profile.get("model")
    provider = profile.get("model_provider")
    if not isinstance(model, str) or not model.strip() or not isinstance(provider, str) or not provider.strip():
        return None
    return {
        "model": model.strip(),
        "model_family": model.split(":", 1)[0].strip(),
        "provider": provider.strip(),
        "identity_source": "codex-profile-config",
    }


def _skills_sdk_eval_identity_fields(identity: dict[str, str] | None) -> dict[str, str | None]:
    return {
        "execution_model": identity.get("model") if identity else None,
        "execution_model_family": identity.get("model_family") if identity else None,
        "execution_model_provider": identity.get("provider") if identity else None,
        "execution_identity_source": identity.get("identity_source") if identity else None,
    }


def _load_release_scenario_sets(evals_path: Path) -> list[dict[str, Any]]:
    if not evals_path.is_file():
        return []
    text = evals_path.read_text(encoding="utf-8")
    try:
        from ask.skills_sdk.scenario_quality import _yaml_safe_load  # noqa: PLC0415

        payload = _yaml_safe_load(text) or {}
    except (ImportError, OSError, RuntimeError, TypeError, ValueError, YAMLError):
        payload = {}
    raw_sets = payload.get("release_scenario_sets") if isinstance(payload, dict) else None
    if not isinstance(raw_sets, list):
        raw_sets = _load_minimal_release_scenario_sets(text)
    if not isinstance(raw_sets, list):
        return []
    sets: list[dict[str, Any]] = []
    for raw_set in raw_sets:
        if not isinstance(raw_set, dict):
            continue
        set_id = str(raw_set.get("id") or "").strip()
        if not set_id:
            continue
        case_ids: list[str] = []
        groups = raw_set.get("groups")
        if isinstance(groups, dict):
            for group_ids in groups.values():
                if not isinstance(group_ids, list):
                    continue
                for raw_case_id in group_ids:
                    case_id = str(raw_case_id or "").strip()
                    if case_id and case_id not in case_ids:
                        case_ids.append(case_id)
        raw_cases = raw_set.get("cases")
        if isinstance(raw_cases, list):
            for raw_case_id in raw_cases:
                case_id = str(raw_case_id or "").strip()
                if case_id and case_id not in case_ids:
                    case_ids.append(case_id)
        minimum = raw_set.get("minimum_scenarios")
        minimum_value = (
            max(RELEASE_SCENARIO_MINIMUM, minimum)
            if isinstance(minimum, int) and not isinstance(minimum, bool)
            else RELEASE_SCENARIO_MINIMUM
        )
        sets.append(
            {
                "id": set_id,
                "default": raw_set.get("default") is True,
                "minimum_scenarios": minimum_value,
                "case_ids": case_ids,
            }
        )
    return sets


def _load_minimal_release_scenario_sets(text: str) -> list[dict[str, Any]]:
    release_sets: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_group: str | None = None
    current_set_indent: int | None = None
    in_release_sets = False
    in_groups = False
    in_cases = False
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0 and stripped == "release_scenario_sets:":
            in_release_sets = True
            current = None
            current_group = None
            current_set_indent = None
            in_groups = False
            in_cases = False
            continue
        if in_release_sets and indent == 0 and not stripped.startswith("- "):
            break
        if not in_release_sets:
            continue
        if stripped.startswith("- ") and (current is None or current_set_indent is None or indent <= current_set_indent):
            current = {"groups": {}}
            release_sets.append(current)
            current_group = None
            current_set_indent = indent
            in_groups = False
            in_cases = False
            _minimal_release_set_assign(current, stripped[2:])
            continue
        if current is None:
            continue
        property_indent = (current_set_indent or 0) + 2
        item_indent = property_indent + 2
        if indent == property_indent and stripped == "groups:":
            in_groups = True
            in_cases = False
            current_group = None
            continue
        if indent == property_indent and stripped == "cases:":
            in_groups = False
            in_cases = True
            current_group = None
            current["cases"] = []
            continue
        if in_cases and indent == item_indent and stripped.startswith("- "):
            cases = current.setdefault("cases", [])
            if isinstance(cases, list):
                cases.append(stripped[2:].strip().strip("'\""))
            continue
        if indent == property_indent and ":" in stripped:
            in_groups = False
            in_cases = False
            current_group = None
            _minimal_release_set_assign(current, stripped)
            continue
        if in_groups and indent == item_indent and stripped.endswith(":"):
            current_group = stripped[:-1].strip()
            groups = current.setdefault("groups", {})
            if isinstance(groups, dict):
                groups[current_group] = []
            continue
        if in_groups and indent == item_indent + 2 and stripped.startswith("- ") and current_group:
            groups = current.setdefault("groups", {})
            if isinstance(groups, dict):
                group_values = groups.setdefault(current_group, [])
                if isinstance(group_values, list):
                    group_values.append(stripped[2:].strip().strip("'\""))
    return release_sets


def _minimal_release_set_assign(target: dict[str, Any], pair: str) -> None:
    if ":" not in pair:
        return
    key, value = pair.split(":", 1)
    value = value.strip().strip("'\"")
    if value in {"true", "false"}:
        target[key.strip()] = value == "true"
        return
    if value.isdigit():
        target[key.strip()] = int(value)
        return
    target[key.strip()] = value


def _select_release_scenario_set(release_sets: list[dict[str, Any]], scenario_set: str | None) -> dict[str, Any] | None:
    if not release_sets:
        return None
    if scenario_set:
        for release_set in release_sets:
            if release_set["id"] == scenario_set:
                return release_set
        return None
    defaults = [release_set for release_set in release_sets if release_set.get("default") is True]
    return defaults[0] if len(defaults) == 1 else None


def _skills_sdk_release_set_blocked_result(
    repo_root: Path,
    *,
    target: str,
    target_path: str,
    evals_path: Path,
    package_identity: dict[str, str] | None,
    mode: str,
    codex_profile: str | None,
    cases: list[str] | None,
    scenario_set: str | None,
    selected_case_ids: list[str],
    release_set: dict[str, Any] | None,
    blocker: str,
    message: str,
) -> CallResult:
    result = CallResult(status="error")
    release_case_ids = list(release_set.get("case_ids") or []) if release_set else []
    execution_identity = _skills_sdk_eval_execution_identity(
        evals_path, _skills_sdk_eval_receipt_lane(mode, codex_profile)
    )
    receipt = {
        "schema_version": "skills-sdk.eval-run-receipt.v0",
        "schema_uri": "https://agent-skills.local/schemas/skills-sdk/eval-run-receipt.v0.schema.json",
        "status": "blocked",
        "runner": "internal_skill_builder_v0",
        "dataset_path": _skills_sdk_repo_relative(repo_root, evals_path),
        "dataset_digest": _skills_sdk_digest_file(evals_path) if evals_path.is_file() else None,
        "skill_ir_schema_version": package_identity["skill_ir_schema_version"] if package_identity else None,
        "package_id": package_identity["package_id"] if package_identity else None,
        "package_digest": package_identity["package_digest"] if package_identity else None,
        "target_path": target_path,
        "mode": mode,
        "lane": _skills_sdk_eval_receipt_lane(mode, codex_profile),
        "lane_type": "focused-debug",
        "profile": codex_profile,
        "codex_profile": codex_profile,
        "codex_exec_invoked": False,
        "codex_exec_command_shape": None,
        **_skills_sdk_eval_identity_fields(execution_identity),
        "scenario_set_id": release_set.get("id") if release_set else scenario_set,
        "scenario_set_case_ids": release_case_ids,
        "selected_case_ids": selected_case_ids,
        "release_set_minimum": release_set.get("minimum_scenarios") if release_set else RELEASE_SCENARIO_MINIMUM,
        "case_count": len(selected_case_ids),
        "passed_count": 0,
        "failed_count": 0,
        "quality_gates": None,
        "closeout_validation": None,
        "cases": [],
        "blockers": [blocker],
        "mutation_performed": False,
        "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"],
    }
    result.data["skills_sdk_eval_run"] = {
        "schema_version": "skills-sdk-eval-run.v0",
        "status": "blocked",
        "dataset": None,
        "target": target,
        "runner": "internal_skill_builder_v0",
        "mode": mode,
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _skills_sdk_eval_run_validation_command(
                target,
                mode=mode,
                codex_profile=codex_profile,
                cases=cases,
                scenario_set=scenario_set,
                timeout_seconds=None,
            )
        ],
        "agent_summary": message,
    }
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=message,
            fix_suggestion=(
                f"Run the declared release set with --scenario-set {release_set['id']} "
                if release_set
                else "Define release_scenario_sets in references/evals.yaml before OSS release proof. "
            )
            + "or use --mode smoke for focused debug subsets.",
        )
    )
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
