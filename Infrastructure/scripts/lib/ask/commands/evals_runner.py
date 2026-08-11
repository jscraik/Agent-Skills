from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from ask.skill_review_dashboard import dashboard_not_requested_receipt, render_optional_dashboard

from .evals_closeout import *  # noqa: F403


def _attach_eval_closeout(
    result: CallResult,
    repo_root: Path,
    path: str,
    mode: str,
    runner: str,
    started_at: float,
    timeout_seconds: int | None,
    *,
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
) -> None:
    no_case_reason = _tessl_no_case_reason(result, tessl_live_private=tessl_live_private)
    closeout = _write_eval_closeout(
        repo_root, skill_path=path, mode=mode, runner=runner,
        raw_output=str(result.data.get("raw_output") or ""),
        raw_error=str(result.data.get("raw_error") or ""),
        eval_status=str(result.data.get("eval_status") or ("pass" if result.status == "success" else "fail")),
        blocker_class=result.data.get("blocker_class") if isinstance(result.data.get("blocker_class"), str) else None,
        started_at=started_at, timeout_seconds=timeout_seconds, no_case_reason=no_case_reason,
        tessl_live_private=tessl_live_private, tessl_workspace=tessl_workspace,
        tessl_live_dry_run=tessl_live_dry_run,
    )
    result.data["eval_closeout"] = closeout
    if closeout.get("path"):
        result.data["eval_closeout_path"] = closeout["path"]
    if not _closeout_blocks_result(closeout, result):
        return
    _apply_closeout_block(result, closeout, path, mode, runner)


def _tessl_no_case_reason(result: CallResult, *, tessl_live_private: bool) -> str | None:
    if tessl_live_private and isinstance(result.data.get("tessl_eval"), dict):
        return "Tessl live-private result evidence is retained in data.tessl_eval."
    return None


def _closeout_blocks_result(closeout: dict[str, object], result: CallResult) -> bool:
    return closeout.get("status") == "blocked" and result.status != "error"


def _apply_closeout_block(
    result: CallResult, closeout: dict[str, object], path: str, mode: str, runner: str,
) -> None:
    blocker_class = str(closeout.get("blocker_class") or "blocked_missing_artifact")
    result.status = "error"
    result.data.update(eval_status=blocker_class, blocker_class=blocker_class)
    lifecycle_events = result.data.setdefault("lifecycle_events", [])
    if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
        lifecycle_events.pop()
    _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status=blocker_class, blocker_class=blocker_class)
    result.errors.append(ErrorObject(
        code="ERR_VALIDATION",
        message=f"Evaluation run blocked by closeout contract: {blocker_class}.",
        fix_suggestion=str(closeout.get("next_reproduce_command") or result.data["validation_commands"][0]),
    ))


@dataclass(frozen=True)
class EvalRunRequest:
    """Explicit options for one Skills SDK evaluation request."""

    path: str
    mode: str = "smoke"
    dashboard: bool = True
    runner: str = "codex"
    skip_tessl: bool | None = None
    allow_tessl_project_save: bool = False
    tessl_live_private: bool = False
    tessl_workspace: str | None = None
    tessl_live_dry_run: bool = False
    handoff_readiness_path: str | None = None
    model: str | None = None
    codex_profile: str | None = None
    cases: list[str] | None = None
    timeout_seconds: int | None = None


@dataclass(frozen=True)
class _EvalRunContext:
    path: str
    mode: str
    runner: str
    dashboard: bool
    skip_tessl: bool | None
    effective_skip_tessl: bool
    tessl_live_private: bool
    tessl_live_dry_run: bool
    tessl_workspace: str | None
    handoff_readiness_path: Path | None
    codex_profile: str | None
    effective_codex_profile: str
    model: str | None
    cases: list[str] | None
    timeout_seconds: int | None


def _coerce_eval_run_request(
    request_or_path: EvalRunRequest | str | None,
    legacy_options: dict[str, object],
) -> EvalRunRequest:
    """Accept the value-object contract while preserving existing internal callers."""
    if request_or_path is None:
        request_or_path = legacy_options.pop("path", None)
    elif "path" in legacy_options:
        raise TypeError("run_evals received both a positional request and path keyword")
    if isinstance(request_or_path, EvalRunRequest):
        if legacy_options:
            unexpected = ", ".join(sorted(legacy_options))
            raise TypeError(f"EvalRunRequest does not accept legacy options: {unexpected}")
        return request_or_path
    if not isinstance(request_or_path, str):
        raise TypeError("run_evals expects an EvalRunRequest or skill path string")
    allowed = set(EvalRunRequest.__dataclass_fields__) - {"path"}
    unexpected = set(legacy_options) - allowed
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TypeError(f"run_evals received unexpected option(s): {names}")
    return EvalRunRequest(path=request_or_path, **legacy_options)


def run_evals(
    repo_root: Path,
    request_or_path: EvalRunRequest | str | None = None,
    **legacy_options: object,
) -> CallResult:
    """Runs evaluation cases for a skill."""
    request = _coerce_eval_run_request(request_or_path, legacy_options)
    result = CallResult()
    result.data["dashboard"] = (
        {"status": "not_run", "reason": "evaluation_not_completed", "tab": "evals"}
        if request.dashboard
        else dashboard_not_requested_receipt(tab="evals")
    )
    context = _prepare_eval_context(repo_root, request, result)
    if context is None or _invalid_tessl_flags(result, context):
        return result
    started_at = time.time()
    if context.tessl_live_private:
        return _run_tessl_private_eval(repo_root, context, result, started_at)
    return _run_local_eval(repo_root, context, result, started_at)


def _block_eval_validation(
    result: CallResult, message: str, *, workspace_source: str | None = None, fix_suggestion: str | None = None,
) -> None:
    result.status = "error"
    result.data.update(raw_output="", raw_error=message, eval_status="blocked_validation", blocker_class="blocked_validation")
    result.data["blocker_taxonomy"] = _eval_blocker_taxonomy()
    result.data["tessl_eval"] = {"status": "blocked", "blocker": message, "blocker_class": "blocked_validation"}
    if workspace_source:
        result.data["tessl_eval"]["workspace_source"] = workspace_source
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message, fix_suggestion=fix_suggestion))


def _resolve_tessl_workspace(request: EvalRunRequest, result: CallResult) -> tuple[str | None, str | None] | None:
    if not request.tessl_live_private:
        return None, None
    if request.tessl_workspace:
        try:
            return _validate_tessl_workspace(request.tessl_workspace), "argument"
        except ValueError as exc:
            _block_eval_validation(result, str(exc), workspace_source="argument")
            return None
    try:
        workspace, source = _default_tessl_workspace_from_env()
    except ValueError as exc:
        _block_eval_validation(result, str(exc), workspace_source="environment")
        return None
    if workspace:
        return workspace, source
    message = "Tessl live-private evals require --tessl-workspace <workspace> or an explicit Tessl workspace environment variable."
    _block_eval_validation(result, message, workspace_source="missing")
    return None


def _prepare_eval_context(repo_root: Path, request: EvalRunRequest, result: CallResult) -> _EvalRunContext | None:
    workspace = _resolve_tessl_workspace(request, result)
    if workspace is None:
        return None
    path = _resolve_eval_skill_path(repo_root, request.path)
    handoff_readiness_path, handoff_readiness_error = _resolve_handoff_readiness_path(
        repo_root,
        request.handoff_readiness_path,
    )
    if handoff_readiness_error:
        _block_eval_validation(result, handoff_readiness_error)
        return None
    if handoff_readiness_path is not None and not request.tessl_live_private:
        _block_eval_validation(result, "--handoff-readiness requires --tessl-live-private.")
        return None
    if path != request.path:
        result.data.update(requested_path=request.path, resolved_skill_path=path)
    context = _EvalRunContext(
        path=path, mode=request.mode, runner=request.runner, dashboard=request.dashboard, skip_tessl=request.skip_tessl,
        effective_skip_tessl=not request.tessl_live_private if request.skip_tessl is None else request.skip_tessl,
        tessl_live_private=request.tessl_live_private, tessl_live_dry_run=request.tessl_live_dry_run,
        tessl_workspace=workspace[0], handoff_readiness_path=handoff_readiness_path,
        codex_profile=request.codex_profile, effective_codex_profile=request.codex_profile or SMOKE_EVAL_PROFILE,
        model=request.model, cases=request.cases, timeout_seconds=request.timeout_seconds,
    )
    _set_eval_contract(result, context, workspace[1], repo_root)
    return context


def _set_eval_contract(
    result: CallResult,
    context: _EvalRunContext,
    workspace_source: str | None,
    repo_root: Path,
) -> None:
    profile_invoked = context.runner == "codex" and (context.mode == "smoke" or context.codex_profile is not None)
    result.data.update(tessl_workspace=context.tessl_workspace, tessl_workspace_source=workspace_source)
    result.data["validation_commands"] = [_evals_run_validation_command(
        context.path, mode=context.mode, runner=context.runner, dashboard=context.dashboard, codex_profile=context.codex_profile,
        tessl_live_private=context.tessl_live_private, tessl_workspace=context.tessl_workspace, tessl_live_dry_run=context.tessl_live_dry_run,
        handoff_readiness_path=_repo_relative_path(repo_root, context.handoff_readiness_path)
        if context.handoff_readiness_path is not None else None,
    )]
    result.data["profile_contract"] = {
        "codex_profile": context.effective_codex_profile if profile_invoked else None,
        "codex_profile_config": f"[profiles.{context.effective_codex_profile}]" if profile_invoked else None,
        "codex_profile_source": "argument" if context.codex_profile else "default",
        "codex_profile_required_for_smoke": context.mode == "smoke" and context.runner == "codex",
        "codex_exec_invoked": profile_invoked, "codex_exec_command_shape": ["codex", "exec", "--profile", context.effective_codex_profile] if profile_invoked else None,
        "codex_profile_proof_lane": context.effective_codex_profile if context.effective_codex_profile in {"oss-local", "oss-cloud"} else None,
        "tessl_policy": _tessl_policy(), "tessl_live_private_policy": _tessl_live_private_policy(context.tessl_workspace) if context.tessl_live_private else None,
    }


def _invalid_tessl_flags(result: CallResult, context: _EvalRunContext) -> bool:
    if context.tessl_live_dry_run and not context.tessl_live_private:
        _block_eval_validation(result, "--tessl-live-dry-run requires --tessl-live-private.")
        return True
    if context.effective_skip_tessl and context.tessl_live_private:
        _block_eval_validation(result, "--skip-tessl cannot be combined with --tessl-live-private.")
        return True
    if not context.effective_skip_tessl and not context.tessl_live_private:
        _block_eval_validation(
            result, "Direct Tessl eval submission is retired; use --tessl-live-private with the SDK handoff workflow.",
            fix_suggestion="./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot",
        )
        return True
    return False


def _resolve_handoff_readiness_path(
    repo_root: Path,
    raw_path: str | None,
) -> tuple[Path | None, str | None]:
    """Accept only a regular readiness manifest within the handoff evidence root."""
    if raw_path is None:
        return None, None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return None, "--handoff-readiness must be repo-relative beneath .harness/evidence/handoff"
    path = (repo_root / candidate).resolve(strict=False)
    evidence_root = (repo_root / ".harness" / "evidence" / "handoff").resolve()
    try:
        path.relative_to(evidence_root)
    except ValueError:
        return None, "--handoff-readiness must stay beneath .harness/evidence/handoff"
    if path.name != "eval-handoff-readiness.json":
        return None, "--handoff-readiness must name eval-handoff-readiness.json"
    if path.is_symlink() or not path.is_file():
        return None, "--handoff-readiness must be an existing regular file"
    return path, None


def _record_successful_tessl_dry_run(
    repo_root: Path,
    readiness_path: Path | None,
    tessl_eval: dict[str, object],
) -> str | None:
    """Persist dry-run proof only after a successful private Tessl dry-run."""
    if tessl_eval.get("status") != "pass" or not tessl_eval.get("dry_run"):
        return None
    receipt_readiness_path = readiness_path
    if receipt_readiness_path is None:
        source_path = str(tessl_eval.get("source_path") or "")
        if not source_path:
            return None
        receipt_readiness_path = default_handoff_readiness_path(
            repo_root,
            repo_root / source_path,
        )
    if receipt_readiness_path.is_symlink() or not receipt_readiness_path.is_file():
        return None
    try:
        from ask.skills_sdk.handoff_materialization import record_tessl_dry_run

        return record_tessl_dry_run(
            repo_root,
            readiness_path=receipt_readiness_path,
            tessl_eval=tessl_eval,
        )
    except ValueError as exc:
        tessl_eval.update(
            status="blocked",
            blocker=f"Failed to record Tessl dry-run evidence: {exc}",
            blocker_class="blocked_validation",
        )
        return None


def _run_tessl_private_eval(repo_root: Path, context: _EvalRunContext, result: CallResult, started_at: float) -> CallResult:
    _start_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner)
    result.status = "success"
    result.data.update(raw_output="", raw_error="", eval_status="pass", blocker_class=None)
    result.data["blocker_taxonomy"] = _eval_blocker_taxonomy()
    result.data["local_eval_status"] = "skipped_tessl_live_dry_run" if context.tessl_live_dry_run else "skipped_tessl_live_private"
    if not _admit_tessl_private_eval(repo_root, context, result):
        _attach_eval_closeout(
            result, repo_root, context.path, context.mode, context.runner, started_at,
            context.timeout_seconds, tessl_live_private=True,
            tessl_workspace=context.tessl_workspace,
            tessl_live_dry_run=context.tessl_live_dry_run,
        )
        return result
    tessl_eval = _run_tessl_live_private_eval(
        repo_root,
        context.path,
        workspace=context.tessl_workspace,
        dry_run=context.tessl_live_dry_run,
        handoff_readiness_path=context.handoff_readiness_path,
    )
    if tessl_live_dry_run_receipt := _record_successful_tessl_dry_run(
        repo_root,
        context.handoff_readiness_path,
        tessl_eval,
    ):
        tessl_eval["handoff_dry_run_receipt"] = tessl_live_dry_run_receipt
    result.data["tessl_eval"] = tessl_eval
    _finish_tessl_private_eval(result, context, tessl_eval)
    _attach_eval_closeout(
        result, repo_root, context.path, context.mode, context.runner, started_at,
        context.timeout_seconds, tessl_live_private=True,
        tessl_workspace=context.tessl_workspace,
        tessl_live_dry_run=context.tessl_live_dry_run,
    )
    return result


def _admit_tessl_private_eval(repo_root: Path, context: _EvalRunContext, result: CallResult) -> bool:
    if context.tessl_live_dry_run:
        result.data["tessl_dry_run_note"] = "Tessl live-private dry-run validates the staged private Tessl payload only; current pre-Tessl lane receipts must pass first."
        admission = _tessl_dry_run_admission(
            repo_root,
            context.path,
            context.handoff_readiness_path,
        )
        result.data["tessl_dry_run_admission"] = admission
        return _apply_tessl_admission(result, context, admission, "ready_for_tessl_dry_run", "Tessl live-private dry-run")
    result.data["tessl_live_private_note"] = (
        "Tessl live-private scoring uses the staged private Tessl payload directly. "
        "Run deterministic local gates, oss-local, oss-cloud, and Tessl dry-run separately before live scoring; "
        "live Tessl quota, auth, project-link, or external scoring blockers remain Tessl-lane blockers."
    )
    admission = _tessl_live_handoff_readiness(
        repo_root,
        context.path,
        context.handoff_readiness_path,
    )
    result.data["handoff_readiness"] = admission
    return _apply_tessl_admission(result, context, admission, "ready_for_live_tessl", "Tessl live-private")


def _apply_tessl_admission(
    result: CallResult, context: _EvalRunContext, admission: dict[str, object], ready_key: str, label: str,
) -> bool:
    if admission.get(ready_key):
        return True
    blocker = str(admission.get("agent_summary") or f"{label} admission is blocked")
    result.status = "error"
    result.data.update(eval_status="blocked_validation", blocker_class="blocked_validation", tessl_eval_status="blocked_validation", tessl_blocker_class="blocked_validation")
    result.data["tessl_eval"] = {"status": "blocked", "blocker": blocker, "blocker_class": "blocked_validation", "handoff_readiness_path": admission.get("readiness_path"), "handoff_readiness_blockers": admission.get("blockers", []), "required_next_actions": admission.get("required_next_actions", [])}
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=f"{label} blocked: {blocker}", fix_suggestion="./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot"))
    _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status="blocked_validation", blocker_class="blocked_validation")
    return False


def _finish_tessl_private_eval(result: CallResult, context: _EvalRunContext, tessl_eval: dict[str, object]) -> None:
    if tessl_eval.get("status") == "pass":
        _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status="pass")
        return
    blocker_class = str(tessl_eval.get("blocker_class") or "blocked_validation")
    result.status = "error"
    result.data.update(eval_status=blocker_class, blocker_class=blocker_class, tessl_eval_status=blocker_class, tessl_blocker_class=blocker_class)
    result.errors.append(ErrorObject(code="ERR_RUNTIME" if tessl_eval.get("status") == "blocked" else "ERR_VALIDATION", message=f"Tessl eval {tessl_eval.get('status')}: {tessl_eval.get('blocker') or 'see data.tessl_eval'}"))
    _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status=blocker_class, blocker_class=blocker_class)


def _selected_eval_cases(cases: list[str] | None) -> list[str]:
    return [part.strip() for raw_case in cases or [] for part in raw_case.split(",") if part.strip()]


def _qwen_batch_is_blocked(result: CallResult, context: _EvalRunContext, selected_cases: list[str]) -> bool:
    blocker = _qwen_oss_local_batch_blocker(mode=context.mode, runner=context.runner, codex_profile=context.codex_profile, selected_cases=selected_cases)
    if blocker is None:
        return False
    result.status = "error"
    result.data.update(raw_output="", raw_error=json.dumps(blocker, indent=2), eval_status="blocked_validation", blocker_class="blocked_validation")
    result.data["blocker_taxonomy"] = _eval_blocker_taxonomy()
    result.data["qwen_oss_local_smoke_batch"] = blocker
    result.errors.append(ErrorObject(code="ERR_VALIDATION", message=f"qwen oss-local {context.mode} selected {len(selected_cases)} cases; maximum shard size is {QWEN_OSS_LOCAL_MAX_BATCH_CASES}.", fix_suggestion=blocker["expected"]))
    return True


def _eval_command(context: _EvalRunContext, selected_cases: list[str]) -> tuple[list[str], int]:
    cmd = [*_pyyaml_eval_python_command(), f"{SKILL_BUILDER_SCRIPTS}/run_skill_evals.py", context.path, "--eval-mode", context.mode, "--runner", context.runner]
    is_codex = context.runner == "codex" and (context.mode == "smoke" or context.codex_profile is not None)
    if is_codex:
        timeout = _add_codex_eval_options(cmd, context, selected_cases)
    else:
        timeout = _non_codex_eval_timeout(context)
    return [*cmd, *[item for case in selected_cases for item in ("--case", case)]], timeout


def _configured_codex_cli_path() -> str | None:
    """Return the projected immutable Codex executable only when safe to invoke."""
    configured = os.environ.get("CODEX_CLI_PATH", "").strip()
    if not configured:
        return None
    path = Path(configured)
    if not path.is_absolute() or path.is_symlink() or not path.is_file() or not os.access(path, os.X_OK):
        return None
    return str(path)


def _add_codex_eval_options(cmd: list[str], context: _EvalRunContext, selected_cases: list[str]) -> int:
    sandbox = "read-only" if context.codex_profile in {"oss-local", "oss-cloud", "codex-fast"} else "workspace-write"
    case_timeout = context.timeout_seconds or SMOKE_CASE_TIMEOUT_SECONDS
    cmd.extend(["--profile", context.effective_codex_profile, "--sandbox", sandbox, "--timeout-sec", str(case_timeout)])
    if context.mode == "smoke" and (context.model or not context.codex_profile):
        cmd.extend(["--model", context.model or SMOKE_EVAL_MODEL])
    if codex_cli_path := _configured_codex_cli_path():
        cmd.extend(["--codex-bin", codex_cli_path])
    return _eval_timeout(context.mode, int(case_timeout), len(selected_cases))


def _non_codex_eval_timeout(context: _EvalRunContext) -> int:
    if context.timeout_seconds is not None:
        return context.timeout_seconds
    if context.mode == "smoke":
        return SMOKE_EVAL_TIMEOUT_SECONDS
    return RELEASE_EVAL_TIMEOUT_SECONDS if context.mode == "release" else 300


def _eval_timeout(mode: str, case_timeout: int, case_count: int) -> int:
    selected_timeout = case_timeout * max(case_count, 1) + 60
    if mode == "smoke":
        return max(SMOKE_EVAL_TIMEOUT_SECONDS, selected_timeout)
    if mode == "release":
        return min(RELEASE_EVAL_TIMEOUT_SECONDS, selected_timeout)
    return selected_timeout


def _run_local_eval(repo_root: Path, context: _EvalRunContext, result: CallResult, started_at: float) -> CallResult:
    selected_cases = _selected_eval_cases(context.cases)
    if _qwen_batch_is_blocked(result, context, selected_cases):
        return result
    cmd, timeout = _eval_command(context, selected_cases)
    _start_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner)
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=timeout, env=_subprocess_env_with_uv_cache(), start_new_session=True)
        _apply_eval_process_result(repo_root, context, result, process)
    except subprocess.TimeoutExpired as exc:
        _apply_eval_timeout(repo_root, context, result, exc, timeout)
    except OSError as exc:
        _apply_eval_oserror(context, result, exc)
    _mark_tessl_skipped(result, context)
    _attach_eval_closeout(result, repo_root, context.path, context.mode, context.runner, started_at, context.timeout_seconds)
    return result


def _apply_eval_process_result(repo_root: Path, context: _EvalRunContext, result: CallResult, process: subprocess.CompletedProcess[str]) -> None:
    result.data.update(raw_output=_repo_relative_text(repo_root, process.stdout), raw_error=_repo_relative_text(repo_root, process.stderr), eval_status="pass" if process.returncode == 0 else "fail", blocker_class=None)
    result.data["blocker_taxonomy"] = _eval_blocker_taxonomy()
    if process.returncode == 0:
        result.status = "success"
        _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status="pass")
        _render_eval_dashboard_if_requested(repo_root, context, result, process.stdout, succeeded=True)
        return
    blocker = _classify_eval_blocker(raw_output=process.stdout, raw_error=process.stderr) or _scorecard_blocker_class(_read_scorecard(_scorecard_path_from_output(repo_root, process.stdout)))
    if blocker:
        result.data.update(eval_status=blocker, blocker_class=blocker)
    result.status = "error"
    _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status=result.data["eval_status"], blocker_class=blocker)
    result.errors.append(ErrorObject(code="ERR_RUNTIME" if blocker == "blocked_runtime" else "ERR_VALIDATION", message="Evaluation run blocked." if blocker else "Evaluation run failed."))
    _render_eval_dashboard_if_requested(repo_root, context, result, process.stdout, succeeded=False)


def _render_eval_dashboard_if_requested(repo_root: Path, context: _EvalRunContext, result: CallResult, output: str, *, succeeded: bool) -> None:
    if not context.dashboard or (not succeeded and _scorecard_path_from_output(repo_root, output) is None):
        return
    dashboard_data, dashboard_receipt = render_optional_dashboard(
        lambda: _render_eval_dashboard(repo_root, context.path, context.mode, output),
        tab="evals",
    )
    result.data["dashboard"] = dashboard_receipt
    if dashboard_data is not None:
        result.data.update(dashboard_data)


def _apply_eval_timeout(repo_root: Path, context: _EvalRunContext, result: CallResult, exc: subprocess.TimeoutExpired, timeout: int) -> None:
    raw_output, raw_error = _as_text(exc.stdout), _as_text(exc.stderr)
    blocker = _classify_eval_blocker(raw_output=raw_output, raw_error=raw_error, timed_out=True)
    partial = _write_timeout_partial_artifact(repo_root, skill_path=context.path, mode=context.mode, runner=context.runner, raw_output=raw_output, raw_error=raw_error)
    result.status = "error"
    result.data.update(raw_output=raw_output, raw_error=raw_error, eval_status=blocker, blocker_class=blocker)
    result.data["blocker_taxonomy"] = _eval_blocker_taxonomy()
    result.data["timeout_classification"] = {"class": blocker, "partial_output_artifact": partial}
    _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status=blocker or "timeout", blocker_class=blocker)
    result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Evaluation timed out after {timeout} seconds."))


def _apply_eval_oserror(context: _EvalRunContext, result: CallResult, exc: OSError) -> None:
    result.status = "error"
    result.data.update(raw_output="", raw_error=str(exc), eval_status="blocked_runtime", blocker_class="blocked_runtime")
    result.data["blocker_taxonomy"] = _eval_blocker_taxonomy()
    _finish_eval_lifecycle(result, path=context.path, mode=context.mode, runner=context.runner, eval_status="blocked_runtime", blocker_class="blocked_runtime")
    result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run evaluation: {exc}"))


def _mark_tessl_skipped(result: CallResult, context: _EvalRunContext) -> None:
    result.data["tessl_eval"] = {"status": "skipped", "reason": "local_only_default" if context.skip_tessl is None else "--skip-tessl", "policy": _tessl_policy()}

def benchmark_portfolio(repo_root: Path) -> CallResult:
    """Runs the full repository skill benchmark suite."""
    result = CallResult()
    result.data["validation_commands"] = [_evals_validation_command("benchmark")]

    cmd = [sys.executable, f"{SKILL_BUILDER_SCRIPTS}/benchmark_skill_portfolio.py"]
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr
        if process.returncode == 0:
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark suite failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run benchmark: {e}"))

    return result

def dashboard_report(repo_root: Path) -> CallResult:
    """Generates the skill evaluation dashboard."""
    result = CallResult()
    result.data["validation_commands"] = [_evals_validation_command("dashboard")]

    cmd = [sys.executable, f"{SKILL_BUILDER_SCRIPTS}/build_skill_eval_dashboard.py"]
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr
        if process.returncode == 0:
            result.status = "success"
            result.data["message"] = "Dashboard generated successfully."
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run dashboard generation: {e}"))

    return result

__all__ = [name for name in globals() if not name.startswith("__")]
