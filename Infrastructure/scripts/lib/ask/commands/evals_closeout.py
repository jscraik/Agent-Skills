from __future__ import annotations

from .evals_macro import *  # noqa: F403
from .evals_shared import EvalArtifactReadError, _load_json_file
from ask.skills_sdk.tessl_acceptance_policy import (
    TESSL_ACCEPTANCE_SCORE,
    TESSL_TARGET_SCORE,
)

def _classify_eval_blocker(*, raw_output: str, raw_error: str, timed_out: bool = False) -> str | None:
    text = "\n".join([raw_output or "", raw_error or ""])
    low = text.lower()

    if timed_out:
        return "timeout_partial_output" if text.strip() else "timeout_no_output"

    runtime_markers = [
        "sandbox_apply: operation not permitted",
        "host_execution_untrusted",
        "sandbox-exec",
        "operation not permitted",
        "selected model is at capacity",
        "model is at capacity",
        "you've hit your usage limit",
        "you have hit your usage limit",
        "usage limit for",
        "switch to another model",
        "try again at",
        "context window",
        "start a new thread",
        "blocked_runtime",
    ]
    if any(marker in low for marker in runtime_markers):
        return "blocked_runtime"

    user_input_markers = [
        "user_input_requested_during_turn",
        "request_user_input",
        "requested user input",
        "waiting on user",
        "needs user input",
        "blocked_user_input",
    ]
    if any(marker in low for marker in user_input_markers):
        return "blocked_user_input"

    auth_markers = [
        "not logged in",
        "/login",
        "unauthenticated",
        "authentication required",
        "missing authenticated codex state",
        "blocked_auth",
    ]
    if any(marker in low for marker in auth_markers):
        return "blocked_auth"

    missing_tool_markers = [
        "command not found",
        "no such file or directory",
        "missing binary",
        "missing executable",
        "blocked_missing_tool",
    ]
    if any(marker in low for marker in missing_tool_markers):
        return "blocked_missing_tool"

    missing_artifact_markers = [
        "missing artifact",
        "expected artifact",
        "scorecard not found",
        "no scorecard",
        "blocked_missing_artifact",
    ]
    if any(marker in low for marker in missing_artifact_markers):
        return "blocked_missing_artifact"

    environment_markers = [
        "wrong cwd",
        "repo mismatch",
        "workspace root",
        "permission profile",
        "blocked_environment",
    ]
    if any(marker in low for marker in environment_markers):
        return "blocked_environment"

    validation_markers = [
        "blocked_validation",
        "validation failed",
        "strict audit failed",
        "policy validation",
        "no eval cases matched the selected filters",
        "selected case filters matched only smoke-only discovery contract cases",
        "requires eval cases",
        "none matched the selected filters",
        "add discovery-specific smoke_mode cases",
    ]
    if any(marker in low for marker in validation_markers):
        return "blocked_validation"

    return None


def _scorecard_path_from_output(repo_root: Path, raw_output: str) -> Path | None:
    for line in raw_output.splitlines():
        match = re.match(r"^Scorecard:\s+(.+?)\s*$", line)
        if not match:
            continue
        candidate = Path(match.group(1)).expanduser()
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.resolve()
    return None


def _reports_path_from_output(repo_root: Path, raw_output: str) -> Path | None:
    for line in raw_output.splitlines():
        match = re.match(r"^Reports:\s+(.+?)\s*$", line)
        if not match:
            continue
        candidate = Path(match.group(1)).expanduser()
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.resolve()
    return None


def _eval_skill_source_root(path: str) -> Path:
    source = Path(path).expanduser()
    if source.name == "SKILL.md":
        return source.parent
    return source


def _eval_skill_name_for_reports(path: str) -> str:
    source_root = _eval_skill_source_root(path)
    try:
        frontmatter = _read_skill_frontmatter(source_root)
    except OSError:
        frontmatter = {}
    name = str(frontmatter.get("name") or "").strip()
    return name or source_root.name


def _newest_report_dir_for_skill(repo_root: Path, *, skill_name: str, started_at: float) -> Path | None:
    reports_root = repo_root / "Infrastructure" / "artifacts" / "skills" / skill_name
    if not reports_root.is_dir():
        return None
    candidates = [
        path
        for path in reports_root.iterdir()
        if path.is_dir() and path.stat().st_mtime >= started_at - 1
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _eval_report_dir(
    repo_root: Path,
    *,
    skill_path: str,
    raw_output: str,
    started_at: float,
) -> Path | None:
    reports_path = _reports_path_from_output(repo_root, raw_output)
    if reports_path is not None and reports_path.is_dir():
        return reports_path
    scorecard_path = _scorecard_path_from_output(repo_root, raw_output)
    if scorecard_path is not None:
        return scorecard_path.parent
    skill_name = _eval_skill_name_for_reports(skill_path)
    return _newest_report_dir_for_skill(repo_root, skill_name=skill_name, started_at=started_at)


def _eval_closeout_status(eval_status: str, blocker_class: str | None) -> str:
    if blocker_class:
        return "blocked"
    normalized = str(eval_status or "").strip().lower()
    if normalized == "pass":
        return "pass"
    if normalized.startswith("blocked") or normalized.startswith("timeout"):
        return "blocked"
    return "fail"


def _case_status_from_record(case: dict) -> str:
    if case.get("blocked") is True:
        return "blocked"
    if case.get("passed") is True:
        return "pass"
    return "fail"


def _case_closeout_from_record(case: dict) -> dict[str, object]:
    case_id = str(case.get("id") or case.get("name") or "unknown")
    status = _case_status_from_record(case)
    result = {
        "id": case_id,
        "status": status,
    }
    if case.get("dir"):
        result["result_path"] = str(case.get("dir"))
    blocker_classes = case.get("blocker_classes")
    if status == "blocked" and isinstance(blocker_classes, list) and blocker_classes:
        result["blocker_class"] = str(blocker_classes[0])
    if status != "pass":
        failures = case.get("tier1_failures")
        if isinstance(failures, list) and failures:
            result["failures"] = [str(item) for item in failures]
        blocked_reasons = case.get("blocked_reasons")
        if isinstance(blocked_reasons, list) and blocked_reasons:
            result["blocked_reasons"] = [str(item) for item in blocked_reasons]
    return result


def _case_closeout_from_partial_dir(case_dir: Path, repo_root: Path) -> dict[str, object]:
    case_id = re.sub(r"^\d+-", "", case_dir.name)
    result_path = case_dir / "result.json"
    if result_path.is_file():
        try:
            case = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            case = {}
        if isinstance(case, dict):
            return _case_closeout_from_record(case)
    actual_artifacts = [
        path.relative_to(case_dir).as_posix()
        for path in sorted(case_dir.rglob("*"))
        if path.is_file()
    ]
    return {
        "id": case_id,
        "status": "blocked",
        "blocker_class": "blocked_missing_artifact",
        "expected_artifacts": ["result.json"],
        "actual_artifacts": actual_artifacts,
        "result_path": _repo_relative_path(repo_root, case_dir),
    }


def _load_eval_summary(report_dir: Path) -> dict:
    for name in ("summary.json", "scorecard.json"):
        path = report_dir / name
        if not path.is_file():
            continue
        return _load_json_file(path)
    return {}


def _eval_closeout_validation_checks(closeout: dict[str, object]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    missing = sorted(field for field in EVAL_CLOSEOUT_REQUIRED_FIELDS if field not in closeout)
    checks.append({
        "id": "required_fields_present",
        "status": "blocker" if missing else "pass",
        "message": "workflow-closeout/v1 receipts must include required contract fields.",
        "evidence": missing,
    })
    schema_version = closeout.get("schema_version")
    checks.append({
        "id": "schema_version_valid",
        "status": "pass" if schema_version == EVAL_CLOSEOUT_SCHEMA_VERSION else "blocker",
        "message": "workflow-closeout receipt must use skills-sdk.eval-closeout.v1.",
        "evidence": [] if schema_version == EVAL_CLOSEOUT_SCHEMA_VERSION else [str(schema_version)],
    })
    status = str(closeout.get("status") or "")
    cases = closeout.get("cases")
    case_list = cases if isinstance(cases, list) else []
    checks.append({
        "id": "cases_array_valid",
        "status": "pass" if isinstance(cases, list) else "blocker",
        "message": "workflow-closeout receipt must carry cases as an array.",
        "evidence": [] if isinstance(cases, list) else [type(cases).__name__],
    })
    blocked_cases = [
        str(case.get("id") or index)
        for index, case in enumerate(case_list, start=1)
        if isinstance(case, dict) and str(case.get("status") or "") == "blocked"
    ]
    checks.append({
        "id": "blocked_cases_block_suite",
        "status": "blocker" if blocked_cases and status != "blocked" else "pass",
        "message": "Any blocked case must make the suite closeout status blocked.",
        "evidence": blocked_cases if blocked_cases and status != "blocked" else [],
    })
    non_pass_status = status != "pass"
    mutation_allowed = closeout.get("mutation_allowed")
    registry_update_allowed = closeout.get("registry_update_allowed")
    checks.append({
        "id": "non_pass_blocks_source_mutation",
        "status": "blocker" if non_pass_status and mutation_allowed is not False else "pass",
        "message": "Non-pass closeouts must set mutation_allowed=false.",
        "evidence": [f"mutation_allowed={mutation_allowed!r}"] if non_pass_status and mutation_allowed is not False else [],
    })
    checks.append({
        "id": "non_pass_blocks_registry_promotion",
        "status": "blocker" if non_pass_status and registry_update_allowed is not False else "pass",
        "message": "Non-pass closeouts must set registry_update_allowed=false.",
        "evidence": [f"registry_update_allowed={registry_update_allowed!r}"] if non_pass_status and registry_update_allowed is not False else [],
    })
    missing_suite_artifacts = closeout.get("missing_suite_artifacts") is True
    blocker_class = closeout.get("blocker_class")
    checks.append({
        "id": "missing_artifacts_have_blocker_class",
        "status": "blocker" if missing_suite_artifacts and not blocker_class else "pass",
        "message": "Closeouts with missing suite artifacts must include blocker_class.",
        "evidence": ["missing_suite_artifacts=true"] if missing_suite_artifacts and not blocker_class else [],
    })
    no_case_reason = closeout.get("no_case_reason")
    checks.append({
        "id": "pass_has_case_evidence",
        "status": "blocker" if status == "pass" and not case_list and not no_case_reason else "pass",
        "message": "Pass closeouts must include complete case evidence or an explicit no_case_reason.",
        "evidence": ["cases=[]"] if status == "pass" and not case_list and not no_case_reason else [],
    })
    return checks


def validate_eval_closeout_payload(closeout: dict[str, object]) -> dict[str, object]:
    checks = _eval_closeout_validation_checks(closeout)
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": "skills-sdk.eval-closeout-validation.v1",
        "status": "blocked" if blockers else "pass",
        "checks": checks,
        "blockers": blockers,
    }


def _load_eval_closeout(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc}"
    if not isinstance(payload, dict):
        return None, "closeout_json_not_object"
    return payload, None


def _closeout_path_for_doctor(path: Path) -> Path:
    return path / "workflow-closeout.json" if path.is_dir() else path


def eval_closeout_doctor(repo_root: Path, path: str) -> CallResult:
    result = CallResult()
    requested = Path(path).expanduser()
    if not requested.is_absolute():
        requested = repo_root / requested
    closeout_path = _closeout_path_for_doctor(requested)
    result.data["validation_commands"] = [
        " ".join(shlex.quote(part) for part in ["./bin/ask", "evals", "closeout", "doctor", path, "--json", "--robot"])
    ]
    closeout, load_error = _load_eval_closeout(closeout_path)
    report_dir = closeout_path.parent
    case_dirs = [
        item
        for item in sorted(report_dir.iterdir())
        if report_dir.is_dir() and item.is_dir() and re.match(r"^\d+-", item.name)
    ] if report_dir.is_dir() else []
    missing_result_cases = [
        re.sub(r"^\d+-", "", item.name)
        for item in case_dirs
        if not (item / "result.json").is_file()
    ]
    summary_present = (report_dir / "summary.json").is_file()
    scorecard_present = (report_dir / "scorecard.json").is_file()
    validation = (
        validate_eval_closeout_payload(closeout)
        if closeout is not None
        else {
            "schema_version": "skills-sdk.eval-closeout-validation.v1",
            "status": "blocked",
            "checks": [],
            "blockers": [{"id": "closeout_load", "status": "blocker", "message": load_error or "missing closeout", "evidence": [str(closeout_path)]}],
        }
    )
    doctor = {
        "schema_version": "skills-sdk.eval-closeout-doctor.v1",
        "status": "blocked" if validation["status"] != "pass" or missing_result_cases else "pass",
        "requested_path": path,
        "closeout_path": _repo_relative_path(repo_root, closeout_path),
        "report_dir": _repo_relative_path(repo_root, report_dir),
        "summary_present": summary_present,
        "scorecard_present": scorecard_present,
        "case_count": len(case_dirs),
        "missing_result_cases": missing_result_cases,
        "closeout_validation": validation,
        "next_reproduce_command": closeout.get("next_reproduce_command") if isinstance(closeout, dict) else None,
    }
    result.data["eval_closeout_doctor"] = doctor
    if doctor["status"] != "pass":
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Eval closeout doctor detected blocked or incomplete closeout evidence.",
            fix_suggestion=str(doctor.get("next_reproduce_command") or result.data["validation_commands"][0]),
        ))
    return result


def _eval_closeout_cases(repo_root: Path, report_dir: Path | None, summary: dict) -> list[dict[str, object]]:
    if isinstance(summary.get("cases"), list):
        return [_case_closeout_from_record(case) for case in summary["cases"] if isinstance(case, dict)]
    if report_dir is None or not report_dir.is_dir():
        return []
    case_dirs = [path for path in sorted(report_dir.iterdir()) if path.is_dir() and re.match(r"^\d+-", path.name)]
    return [_case_closeout_from_partial_dir(path, repo_root) for path in case_dirs]


def _eval_closeout_state(
    eval_status: str,
    blocker_class: str | None,
    report_dir: Path | None,
    summary: dict,
    cases: list[dict[str, object]],
    no_case_reason: str | None,
) -> tuple[str, str | None, bool]:
    status = _eval_closeout_status(eval_status, blocker_class)
    missing_suite_artifacts = _missing_suite_artifacts(report_dir, summary, no_case_reason)
    if missing_suite_artifacts or _missing_case_evidence(cases, no_case_reason):
        return "blocked", blocker_class or "blocked_missing_artifact", missing_suite_artifacts
    if any(case.get("status") == "blocked" for case in cases):
        return "blocked", blocker_class or "blocked_missing_artifact", missing_suite_artifacts
    if status == "pass" and any(case.get("status") == "fail" for case in cases):
        status = "fail"
    return status, blocker_class, missing_suite_artifacts


def _missing_suite_artifacts(report_dir: Path | None, summary: dict, no_case_reason: str | None) -> bool:
    return (report_dir is None or not summary) and not no_case_reason


def _missing_case_evidence(cases: list[dict[str, object]], no_case_reason: str | None) -> bool:
    return not cases and not no_case_reason


def _eval_closeout_path(
    repo_root: Path, report_dir: Path | None, skill_path: str, mode: str, runner: str,
    raw_output: str, raw_error: str, no_case_reason: str | None,
) -> Path | None:
    if report_dir is not None:
        return report_dir / "workflow-closeout.json"
    if not (raw_output.strip() or raw_error.strip() or no_case_reason):
        return None
    closeout_root = repo_root / "Infrastructure" / "artifacts" / "evals" / "closeouts"
    stamp = _utc_now_iso().replace(":", "").replace("-", "")
    return closeout_root / f"{stamp}-{_safe_slug(skill_path)}-{_safe_slug(mode)}-{_safe_slug(runner)}.json"


def _eval_closeout_payload(
    repo_root: Path, skill_path: str, mode: str, runner: str, report_dir: Path | None,
    cases: list[dict[str, object]], status: str, blocker_class: str | None,
    raw_output: str, raw_error: str, missing_suite_artifacts: bool,
    timeout_seconds: int | None, no_case_reason: str | None, artifact_read_error: str | None = None,
    *, tessl_live_private: bool = False, tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
) -> dict[str, object]:
    return {
        "schema_version": EVAL_CLOSEOUT_SCHEMA_VERSION, "status": status, "skill_path": skill_path,
        "mode": mode, "runner": runner,
        "report_dir": _repo_relative_path(repo_root, report_dir) if report_dir is not None else None,
        "cases_expected": [str(case.get("id")) for case in cases], "cases": cases,
        "blocker_class": blocker_class, "mutation_allowed": status == "pass",
        "registry_update_allowed": status == "pass" and mode == "release",
        "raw_output_present": bool(raw_output.strip()), "raw_error_present": bool(raw_error.strip()),
        "missing_suite_artifacts": missing_suite_artifacts, "case_evidence_present": bool(cases),
        "no_case_reason": no_case_reason, "artifact_read_error": artifact_read_error,
        "next_reproduce_command": _evals_run_validation_command(
            skill_path, mode=mode, runner=runner, dashboard=True,
            tessl_live_private=tessl_live_private, tessl_workspace=tessl_workspace,
            tessl_live_dry_run=tessl_live_dry_run, timeout_seconds=timeout_seconds,
        ),
    }


def _persist_eval_closeout(repo_root: Path, closeout: dict[str, object], closeout_path: Path | None) -> dict[str, object]:
    if closeout_path is not None:
        try:
            closeout_path.parent.mkdir(parents=True, exist_ok=True)
            closeout["path"] = _repo_relative_path(repo_root, closeout_path)
        except OSError as exc:
            return _closeout_persistence_block(closeout, exc, "create parent directory")
    closeout["closeout_validation"] = validate_eval_closeout_payload(closeout)
    if closeout_path is not None:
        try:
            closeout_path.write_text(json.dumps(closeout, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as exc:
            return _closeout_persistence_block(closeout, exc, "write receipt")
    return closeout


def _closeout_persistence_block(closeout: dict[str, object], exc: OSError, operation: str) -> dict[str, object]:
    """Return a classified closeout when its required receipt cannot be persisted."""
    closeout.update(
        status="blocked",
        blocker_class="blocked_artifact_persistence",
        mutation_allowed=False,
        registry_update_allowed=False,
        persistence_error={"operation": operation, "error": str(exc)},
    )
    closeout["closeout_validation"] = validate_eval_closeout_payload(closeout)
    return closeout


def _write_eval_closeout(
    repo_root: Path,
    *,
    skill_path: str,
    mode: str,
    runner: str,
    raw_output: str,
    raw_error: str,
    eval_status: str,
    blocker_class: str | None,
    started_at: float,
    timeout_seconds: int | None = None,
    no_case_reason: str | None = None,
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None, tessl_live_dry_run: bool = False,
) -> dict[str, object]:
    report_dir = _eval_report_dir(repo_root, skill_path=skill_path, raw_output=raw_output, started_at=started_at)
    artifact_read_error = None
    try:
        summary = _load_eval_summary(report_dir) if report_dir is not None else {}
    except EvalArtifactReadError as exc:
        summary = {}
        artifact_read_error = str(exc)
    cases = _eval_closeout_cases(repo_root, report_dir, summary)
    if artifact_read_error:
        status, closeout_blocker, missing_suite_artifacts = "blocked", "blocked_validation", False
    else:
        status, closeout_blocker, missing_suite_artifacts = _eval_closeout_state(
            eval_status, blocker_class, report_dir, summary, cases, no_case_reason,
        )
    closeout = _eval_closeout_payload(
        repo_root, skill_path, mode, runner, report_dir, cases, status, closeout_blocker,
        raw_output, raw_error, missing_suite_artifacts, timeout_seconds, no_case_reason,
        artifact_read_error, tessl_live_private=tessl_live_private,
        tessl_workspace=tessl_workspace, tessl_live_dry_run=tessl_live_dry_run,
    )
    closeout_path = _eval_closeout_path(
        repo_root, report_dir, skill_path, mode, runner, raw_output, raw_error, no_case_reason,
    )
    return _persist_eval_closeout(repo_root, closeout, closeout_path)


def _write_timeout_partial_artifact(
    repo_root: Path,
    *,
    skill_path: str,
    mode: str,
    runner: str,
    raw_output: str,
    raw_error: str,
) -> str | None:
    if not (raw_output.strip() or raw_error.strip()):
        return None
    artifact_root = repo_root / "Infrastructure" / "artifacts" / "evals" / "timeouts"
    artifact_root.mkdir(parents=True, exist_ok=True)
    stamp = _utc_now_iso().replace(":", "").replace("-", "")
    artifact_path = artifact_root / f"{stamp}-{_safe_slug(skill_path)}-{_safe_slug(mode)}-{_safe_slug(runner)}.txt"
    sanitized_output = _repo_relative_text(repo_root, raw_output)
    sanitized_error = _repo_relative_text(repo_root, raw_error)
    artifact_path.write_text(
        "timeout_classification: timeout_partial_output\n\n"
        "stdout:\n"
        f"{sanitized_output}\n\n"
        "stderr:\n"
        f"{sanitized_error}\n",
        encoding="utf-8",
    )
    return _repo_relative_path(repo_root, artifact_path)


def _read_scorecard(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {}
    try:
        return _load_json_file(path)
    except EvalArtifactReadError as exc:
        return {"artifact_read_error": str(exc)}


def _scorecard_summary_blocker_class(scorecard: dict) -> str | None:
    summary = scorecard.get("blocked_class_summary")
    if isinstance(summary, dict):
        for blocker_class, count in summary.items():
            if blocker_class in _eval_blocker_taxonomy() and isinstance(count, int) and count > 0:
                return str(blocker_class)
    return None


def _scorecard_case_blocker_class(scorecard: dict) -> str | None:
    for case in scorecard.get("cases") or []:
        if not isinstance(case, dict):
            continue
        for blocker_class in case.get("blocker_classes") or []:
            if blocker_class in _eval_blocker_taxonomy():
                return str(blocker_class)
        runners = case.get("runners")
        if isinstance(runners, dict):
            for runner in runners.values():
                if not isinstance(runner, dict):
                    continue
                blocker_class = runner.get("blocker_class")
                if blocker_class in _eval_blocker_taxonomy():
                    return str(blocker_class)
    return None


def _scorecard_blocker_class(scorecard: dict) -> str | None:
    if scorecard.get("artifact_read_error"):
        return "blocked_validation"
    if str(scorecard.get("decision") or "").strip().lower() != "blocked":
        return None
    return _scorecard_summary_blocker_class(scorecard) or _scorecard_case_blocker_class(scorecard) or "blocked_validation"


def _latest_review_report(repo_root: Path, skill_identifier: str) -> Path | None:
    review_root = repo_root / "Infrastructure" / "artifacts" / "skill-reviews"
    if not review_root.exists():
        return None
    candidates: list[Path] = []
    fallback_candidates: list[Path] = []
    skill_name = Path(skill_identifier).name
    for report_path in review_root.rglob("*.json"):
        if report_path.name.endswith("-eval-latest.json"):
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data = report.get("data") if isinstance(report, dict) else None
        if not isinstance(data, dict):
            continue
        target = str(data.get("target") or "")
        if not target:
            continue
        target_identifier = _canonical_skill_identifier(repo_root, target)
        if target_identifier == skill_identifier:
            candidates.append(report_path)
        elif Path(target_identifier).name == skill_name:
            fallback_candidates.append(report_path)
    if not candidates:
        candidates = fallback_candidates
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _write_eval_only_review_report(repo_root: Path, skill_name: str, skill_path: str) -> Path:
    review_root = repo_root / "Infrastructure" / "artifacts" / "skill-reviews"
    review_root.mkdir(parents=True, exist_ok=True)
    report_path = review_root / f"{_safe_slug(skill_name)}-eval-latest.json"
    tessl_staging_root = _tessl_staging_root_template()
    report = {
        "status": "success",
        "data": {
            "target": skill_path,
            "generated_at": _utc_now_iso(),
            "review_mode": "eval_only",
            "policy": {
                "mode": "local_internal_only",
                "primary_gate": "local_eval_ask_audit",
                "plugin_eval_min_acceptable_grade": "B+",
                "tessl_review_min_score": TESSL_ACCEPTANCE_SCORE,
                "tessl_review_target_score": TESSL_TARGET_SCORE,
                "codex_smoke_profile": "[profiles.fast]",
                "tessl_eval_staging_root": tessl_staging_root,
                "tessl_project_marker": "tessl.json",
                "snyk_default": "disabled_until_requested",
                "snyk_release_requirement": "release_required_for_manifest_backed_candidates",
            },
            "review_mode_details": {
                "local_evals": {
                    "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
                    "role": "dynamic run-trace behavior checks for skill selection, commands, artifacts, and release gates",
                    "profile": "[profiles.fast] for Codex smoke runs",
                    "tessl_evidence": f"stages copied eval inputs under {tessl_staging_root} with tessl.json",
                    "status": "run_for_this_dashboard",
                },
                "plugin_eval": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "static budget and ergonomics guardrail; not a substitute for local evals",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "tessl_lint": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "disposable .tessl-plugin/plugin.json package-shape check, not a direct content finding",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "tessl_review": {
                    "command": "./bin/ask skills external-review <path> --with-tessl-review --json --robot",
                    "role": "explicitly requested model-backed content review for private or work-in-progress skills",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "snyk": {
                    "command": "./bin/ask skills external-review <path> --include-snyk --json --robot",
                    "role": "opt-in local dependency security screening; release-required for manifest-backed candidates",
                    "status": "not_run_by_default",
                },
            },
            "ask_audit": {
                "data": {
                    "openclaw": {
                        "status": "not_run",
                        "stdout": "Summary: 0 critical · 0 warn",
                    }
                }
            },
            "plugin_eval": {
                "status": "not_run",
                "stdout": (
                    "Plugin Eval was not run for this eval-only dashboard. "
                    "Run ./bin/ask skills external-review <path> --json --robot for the static budget and ergonomics lane."
                ),
            },
            "tessl_review": {
                "status": "not_run",
                "stdout": (
                    "Tessl review was not run for this eval-only dashboard. "
                    "Run ./bin/ask skills external-review <path> --with-tessl-review --json --robot "
                    "for the explicit content-review lane."
                ),
            },
        },
        "errors": [],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path


def _render_eval_dashboard(repo_root: Path, skill_path: str, mode: str, raw_output: str) -> dict:
    scorecard_path = _scorecard_path_from_output(repo_root, raw_output)
    scorecard = _read_scorecard(scorecard_path)
    source_skill_path = str(scorecard.get("skill_path") or skill_path)
    skill_identifier = _canonical_skill_identifier(repo_root, source_skill_path)
    skill_name = str(scorecard.get("skill") or Path(skill_identifier).name)
    report_path = _latest_review_report(repo_root, skill_identifier)
    if report_path is None:
        report_path = _write_eval_only_review_report(repo_root, skill_name, source_skill_path)

    dashboard_path = repo_root / "Infrastructure" / "artifacts" / "skill-reviews" / f"{_safe_slug(skill_name)}-dashboard-{mode}.html"
    rendered = render_skill_review_dashboard(report_path=report_path, output_path=dashboard_path, repo_root=repo_root)
    relative_dashboard = rendered.relative_to(repo_root).as_posix() if rendered.is_relative_to(repo_root) else str(rendered)
    return {
        "dashboard_path": relative_dashboard,
        "dashboard_url": rendered.resolve().as_uri(),
        "dashboard_tab": "evals",
        "dashboard_source_report": report_path.relative_to(repo_root).as_posix() if report_path.is_relative_to(repo_root) else str(report_path),
        "scorecard_path": scorecard_path.relative_to(repo_root).as_posix() if scorecard_path and scorecard_path.is_relative_to(repo_root) else (str(scorecard_path) if scorecard_path else None),
        "browser_instruction": "Open dashboard_url in the Codex in-app browser after evals complete.",
    }

__all__ = [name for name in globals() if not name.startswith("__")]
