from .evals_closeout import *  # noqa: F403

def run_evals(
    repo_root: Path,
    path: str,
    mode: str = "smoke",
    dashboard: bool = True,
    runner: str = "codex",
    skip_tessl: bool | None = None,
    allow_tessl_project_save: bool = False,
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
    model: str | None = None,
    codex_profile: str | None = None,
    cases: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> CallResult:
    """Runs evaluation cases for a skill."""
    result = CallResult()
    effective_skip_tessl = not tessl_live_private if skip_tessl is None else skip_tessl
    requested_path = path
    path = _resolve_eval_skill_path(repo_root, path)
    if path != requested_path:
        result.data["requested_path"] = requested_path
        result.data["resolved_skill_path"] = path
    effective_tessl_workspace = None
    tessl_workspace_source = None
    if tessl_live_private:
        if tessl_workspace:
            try:
                effective_tessl_workspace = _validate_tessl_workspace(tessl_workspace)
                tessl_workspace_source = "argument"
            except ValueError as e:
                result.status = "error"
                result.data["raw_output"] = ""
                result.data["raw_error"] = str(e)
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": str(e),
                    "blocker_class": "blocked_validation",
                    "workspace_source": "argument",
                }
                result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(e)))
                return result
        if not effective_tessl_workspace:
            try:
                effective_tessl_workspace, tessl_workspace_source = _default_tessl_workspace_from_env()
            except ValueError as e:
                result.status = "error"
                result.data["raw_output"] = ""
                result.data["raw_error"] = str(e)
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": str(e),
                    "blocker_class": "blocked_validation",
                    "workspace_source": "environment",
                }
                result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(e)))
                return result
        if not effective_tessl_workspace:
            message = "Tessl live-private evals require --tessl-workspace <workspace> or an explicit Tessl workspace environment variable."
            result.status = "error"
            result.data["raw_output"] = ""
            result.data["raw_error"] = message
            result.data["eval_status"] = "blocked_validation"
            result.data["blocker_class"] = "blocked_validation"
            result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
            result.data["tessl_eval"] = {
                "status": "blocked",
                "blocker": message,
                "blocker_class": "blocked_validation",
                "workspace_source": "missing",
            }
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message))
            return result
    result.data["tessl_workspace"] = effective_tessl_workspace
    result.data["tessl_workspace_source"] = tessl_workspace_source
    result.data["validation_commands"] = [
        _evals_run_validation_command(
            path,
            mode=mode,
            runner=runner,
            dashboard=dashboard,
            codex_profile=codex_profile,
            tessl_live_private=tessl_live_private,
            tessl_workspace=effective_tessl_workspace,
            tessl_live_dry_run=tessl_live_dry_run,
        )
    ]
    effective_codex_profile = codex_profile or SMOKE_EVAL_PROFILE
    codex_profile_invoked = runner == "codex" and (mode == "smoke" or codex_profile is not None)
    codex_profile_config = f"[profiles.{effective_codex_profile}]" if codex_profile_invoked else None
    result.data["profile_contract"] = {
        "codex_profile": effective_codex_profile if codex_profile_invoked else None,
        "codex_profile_config": codex_profile_config,
        "codex_profile_source": "argument" if codex_profile else "default",
        "codex_profile_required_for_smoke": mode == "smoke" and runner == "codex",
        "codex_exec_invoked": codex_profile_invoked,
        "codex_exec_command_shape": ["codex", "exec", "--profile", effective_codex_profile] if codex_profile_invoked else None,
        "codex_profile_proof_lane": effective_codex_profile if effective_codex_profile in {"oss-local", "oss-cloud"} else None,
        "tessl_policy": _tessl_policy(),
        "tessl_live_private_policy": _tessl_live_private_policy(effective_tessl_workspace) if tessl_live_private else None,
    }

    if tessl_live_dry_run and not tessl_live_private:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = ""
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["tessl_eval"] = {
            "status": "blocked",
            "blocker": "--tessl-live-dry-run requires --tessl-live-private.",
            "blocker_class": "blocked_validation",
        }
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="--tessl-live-dry-run requires --tessl-live-private.",
        ))
        return result

    if effective_skip_tessl and tessl_live_private:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = ""
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["tessl_eval"] = {
            "status": "blocked",
            "blocker": "--skip-tessl cannot be combined with --tessl-live-private.",
            "blocker_class": "blocked_validation",
        }
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="--skip-tessl cannot be combined with --tessl-live-private.",
        ))
        return result

    if not effective_skip_tessl and not tessl_live_private:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = ""
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["tessl_eval"] = {
            "status": "blocked",
            "blocker": "Direct Tessl eval submission is retired; use --tessl-live-private with the SDK handoff workflow.",
            "blocker_class": "blocked_validation",
        }
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Direct Tessl eval submission is retired; use --tessl-live-private with the SDK handoff workflow.",
            fix_suggestion="./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot",
        ))
        return result

    if tessl_live_private:
        _start_eval_lifecycle(result, path=path, mode=mode, runner=runner)
        result.status = "success"
        result.data["raw_output"] = ""
        result.data["raw_error"] = ""
        result.data["eval_status"] = "pass"
        result.data["local_eval_status"] = (
            "skipped_tessl_live_dry_run" if tessl_live_dry_run else "skipped_tessl_live_private"
        )
        result.data["blocker_class"] = None
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        if tessl_live_dry_run:
            result.data["tessl_dry_run_note"] = (
                "Tessl live-private dry-run validates the staged private Tessl payload only. "
                "It is blocked until the current mechanical, security, scenario/scorer, deterministic, "
                "oss-local, oss-cloud, and Tessl-local receipts pass; a successful dry-run then becomes "
                "required evidence for live scoring."
            )
            dry_run_admission = _tessl_dry_run_admission(repo_root, path)
            result.data["tessl_dry_run_admission"] = dry_run_admission
            if not dry_run_admission.get("ready_for_tessl_dry_run"):
                result.status = "error"
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["tessl_eval_status"] = "blocked_validation"
                result.data["tessl_blocker_class"] = "blocked_validation"
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": dry_run_admission.get("agent_summary") or "Tessl dry-run admission is blocked",
                    "blocker_class": "blocked_validation",
                    "handoff_readiness_path": dry_run_admission.get("readiness_path"),
                    "handoff_readiness_blockers": dry_run_admission.get("blockers", []),
                    "required_next_actions": dry_run_admission.get("required_next_actions", []),
                }
                result.errors.append(ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Tessl live-private dry-run blocked: {result.data['tessl_eval']['blocker']}",
                    fix_suggestion="Complete SDK pre-Tessl lanes and record their receipts before --tessl-live-dry-run.",
                ))
                _finish_eval_lifecycle(
                    result,
                    path=path,
                    mode=mode,
                    runner=runner,
                    eval_status="blocked_validation",
                    blocker_class="blocked_validation",
                )
                return result
        else:
            result.data["tessl_live_private_note"] = (
                "Tessl live-private scoring uses the staged private Tessl payload directly. "
                "Run deterministic local gates, oss-local, oss-cloud, and Tessl dry-run separately before live scoring; "
                "live Tessl quota, auth, project-link, or external scoring blockers remain Tessl-lane blockers, "
                "and oss-local is rerun only for classified local skill regressions."
            )
            handoff_readiness = _tessl_live_handoff_readiness(repo_root, path)
            result.data["handoff_readiness"] = handoff_readiness
            if not handoff_readiness.get("ready_for_live_tessl"):
                result.status = "error"
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["tessl_eval_status"] = "blocked_validation"
                result.data["tessl_blocker_class"] = "blocked_validation"
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": handoff_readiness.get("agent_summary") or "handoff readiness is blocked",
                    "blocker_class": "blocked_validation",
                    "handoff_readiness_path": handoff_readiness.get("readiness_path"),
                    "handoff_readiness_blockers": handoff_readiness.get("blockers", []),
                    "required_next_actions": handoff_readiness.get("required_next_actions", []),
                }
                result.errors.append(ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Tessl live-private blocked: {result.data['tessl_eval']['blocker']}",
                    fix_suggestion="./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot",
                ))
                _finish_eval_lifecycle(
                    result,
                    path=path,
                    mode=mode,
                    runner=runner,
                    eval_status="blocked_validation",
                    blocker_class="blocked_validation",
                )
                return result
        tessl_eval = _run_tessl_live_private_eval(
            repo_root,
            path,
            workspace=effective_tessl_workspace,
            dry_run=tessl_live_dry_run,
        )
        result.data["tessl_eval"] = tessl_eval
        if tessl_eval.get("status") != "pass":
            blocker_class = tessl_eval.get("blocker_class") or "blocked_validation"
            result.status = "error"
            result.data["eval_status"] = blocker_class or str(tessl_eval.get("status") or "fail")
            result.data["blocker_class"] = blocker_class
            result.data["tessl_eval_status"] = result.data["eval_status"]
            result.data["tessl_blocker_class"] = blocker_class
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if tessl_eval.get("status") == "blocked" else "ERR_VALIDATION",
                    message=f"Tessl eval {tessl_eval.get('status')}: {tessl_eval.get('blocker') or 'see data.tessl_eval'}",
                ))
            _finish_eval_lifecycle(
                result,
                path=path,
                mode=mode,
                runner=runner,
                eval_status=result.data["eval_status"],
                blocker_class=blocker_class,
            )
        else:
            _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status="pass")
        return result

    selected_cases: list[str] = []
    for raw_case in cases or []:
        for case_part in raw_case.split(","):
            selected_case = case_part.strip()
            if selected_case:
                selected_cases.append(selected_case)

    qwen_batch_blocker = _qwen_oss_local_batch_blocker(
        mode=mode,
        runner=runner,
        codex_profile=codex_profile,
        selected_cases=selected_cases,
    )
    if qwen_batch_blocker is not None:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = json.dumps(qwen_batch_blocker, indent=2)
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["qwen_oss_local_smoke_batch"] = qwen_batch_blocker
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=(
                f"qwen oss-local {mode} selected {len(selected_cases)} cases; "
                f"maximum shard size is {QWEN_OSS_LOCAL_MAX_BATCH_CASES}."
            ),
            fix_suggestion=qwen_batch_blocker["expected"],
        ))
        return result

    cmd = [
        *_pyyaml_eval_python_command(),
        f"{SKILL_BUILDER_SCRIPTS}/run_skill_evals.py",
        path,
        "--eval-mode", mode,
        "--runner", runner,
    ]
    timeout = RELEASE_EVAL_TIMEOUT_SECONDS if mode == "release" else 300
    if runner == "codex" and (mode == "smoke" or codex_profile is not None):
        sandbox = "read-only" if codex_profile in {"oss-local", "oss-cloud", "codex-fast"} else "workspace-write"
        case_timeout = timeout_seconds or SMOKE_CASE_TIMEOUT_SECONDS
        cmd.extend([
            "--profile",
            effective_codex_profile,
            "--sandbox",
            sandbox,
            "--timeout-sec",
            str(case_timeout),
        ])
        if mode == "smoke" and (model or not codex_profile):
            cmd.extend(["--model", model or SMOKE_EVAL_MODEL])
        selected_case_count = max(len(selected_cases), 1)
        selected_case_timeout = int(case_timeout) * selected_case_count + 60
        if mode == "smoke":
            timeout = max(SMOKE_EVAL_TIMEOUT_SECONDS, selected_case_timeout)
        elif mode == "release":
            timeout = min(RELEASE_EVAL_TIMEOUT_SECONDS, selected_case_timeout)
        else:
            timeout = selected_case_timeout
    elif mode == "smoke":
        timeout = SMOKE_EVAL_TIMEOUT_SECONDS
    if timeout_seconds is not None and not (runner == "codex" and (mode == "smoke" or codex_profile is not None)):
        timeout = timeout_seconds

    for case in selected_cases:
        cmd.extend(["--case", case])

    _start_eval_lifecycle(result, path=path, mode=mode, runner=runner)
    eval_started_at = time.time()

    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_subprocess_env_with_uv_cache(),
            start_new_session=True,
        )
        result.data["raw_output"] = _repo_relative_text(repo_root, process.stdout)
        result.data["raw_error"] = _repo_relative_text(repo_root, process.stderr)
        result.data["eval_status"] = "pass" if process.returncode == 0 else "fail"
        result.data["blocker_class"] = None
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY

        if process.returncode == 0:
            result.status = "success"
            _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status="pass")
            if dashboard:
                try:
                    result.data.update(_render_eval_dashboard(repo_root, path, mode, process.stdout))
                except Exception as e:  # noqa: BLE001
                    result.errors.append(ErrorObject(
                        code="ERR_RUNTIME",
                        message=f"Evaluation passed, but dashboard rendering failed: {e}",
                        fix_suggestion="Inspect raw_output and rerun ./bin/ask skills external-review <skill> --dashboard if the dashboard report is malformed.",
                    ))
        else:
            blocker_class = _classify_eval_blocker(raw_output=process.stdout, raw_error=process.stderr)
            scorecard_path = _scorecard_path_from_output(repo_root, process.stdout)
            scorecard_blocker_class = _scorecard_blocker_class(_read_scorecard(scorecard_path))
            if blocker_class is None:
                blocker_class = scorecard_blocker_class
            if blocker_class is not None:
                result.data["eval_status"] = blocker_class
                result.data["blocker_class"] = blocker_class
            result.status = "error"
            _finish_eval_lifecycle(
                result,
                path=path,
                mode=mode,
                runner=runner,
                eval_status=result.data["eval_status"],
                blocker_class=blocker_class,
            )
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if blocker_class == "blocked_runtime" else "ERR_VALIDATION",
                message="Evaluation run blocked." if blocker_class is not None else "Evaluation run failed.",
            ))
            if dashboard and scorecard_path is not None:
                try:
                    result.data.update(_render_eval_dashboard(repo_root, path, mode, process.stdout))
                except Exception as e:  # noqa: BLE001
                    result.errors.append(ErrorObject(
                        code="ERR_RUNTIME",
                        message=f"Evaluation failed, and dashboard rendering also failed: {e}",
                        fix_suggestion="Inspect raw_output and raw_error; the scorecard path may be malformed or unreadable.",
                    ))
    except subprocess.TimeoutExpired as e:
        raw_output = _as_text(e.stdout)
        raw_error = _as_text(e.stderr)
        blocker_class = _classify_eval_blocker(raw_output=raw_output, raw_error=raw_error, timed_out=True)
        partial_artifact = _write_timeout_partial_artifact(
            repo_root,
            skill_path=path,
            mode=mode,
            runner=runner,
            raw_output=raw_output,
            raw_error=raw_error,
        )
        result.status = "error"
        result.data["raw_output"] = raw_output
        result.data["raw_error"] = raw_error
        result.data["eval_status"] = blocker_class
        result.data["blocker_class"] = blocker_class
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["timeout_classification"] = {
            "class": blocker_class,
            "partial_output_artifact": partial_artifact,
        }
        _finish_eval_lifecycle(
            result,
            path=path,
            mode=mode,
            runner=runner,
            eval_status=blocker_class or "timeout",
            blocker_class=blocker_class,
        )
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Evaluation timed out after {timeout} seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.data["eval_status"] = "blocked_runtime"
        result.data["blocker_class"] = "blocked_runtime"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        _finish_eval_lifecycle(
            result,
            path=path,
            mode=mode,
            runner=runner,
            eval_status="blocked_runtime",
            blocker_class="blocked_runtime",
        )
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run evaluation: {e}"))

    if effective_skip_tessl:
        result.data["tessl_eval"] = {
            "status": "skipped",
            "reason": "local_only_default" if skip_tessl is None else "--skip-tessl",
            "policy": _tessl_policy(),
        }
    else:
        tessl_eval = _run_tessl_live_private_eval(
            repo_root,
            path,
            workspace=effective_tessl_workspace,
            dry_run=tessl_live_dry_run,
        )
        result.data["tessl_eval"] = tessl_eval
        if tessl_eval.get("status") != "pass":
            tessl_status = str(tessl_eval.get("status") or "fail")
            blocker_class = tessl_eval.get("blocker_class")
            eval_status = blocker_class or tessl_status
            result.data["tessl_eval_status"] = eval_status
            result.data["tessl_blocker_class"] = blocker_class
            if result.status != "error":
                result.data["eval_status"] = eval_status
                result.data["blocker_class"] = blocker_class
                lifecycle_events = result.data.setdefault("lifecycle_events", [])
                if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
                    lifecycle_events.pop()
                _finish_eval_lifecycle(
                    result,
                    path=path,
                    mode=mode,
                    runner=runner,
                    eval_status=eval_status,
                    blocker_class=blocker_class,
                )
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if tessl_eval.get("status") == "blocked" else "ERR_VALIDATION",
                message=f"Tessl eval {tessl_eval.get('status')}: {tessl_eval.get('blocker') or 'see data.tessl_eval'}",
            ))
        elif (
            tessl_live_private
            and tessl_live_dry_run
            and result.status == "error"
            and runner == "discovery-smoke"
            and _is_discovery_smoke_filter_blocker(result.data.get("raw_error"))
        ):
            result.status = "success"
            result.data["local_eval_status"] = result.data.get("eval_status")
            result.data["eval_status"] = "pass"
            result.data["blocker_class"] = None
            result.data["tessl_dry_run_note"] = (
                "Tessl live-private dry-run staged successfully. The discovery-smoke "
                "runner had no smoke_mode cases, so it is recorded as local_eval_status "
                "instead of failing the Tessl staging lane."
            )
            result.errors = [
                error
                for error in result.errors
                if not (
                    error.code == "ERR_VALIDATION"
                    and error.message == "Evaluation run failed."
                )
            ]
            lifecycle_events = result.data.setdefault("lifecycle_events", [])
            if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
                lifecycle_events.pop()
            _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status="pass")

    closeout = _write_eval_closeout(
        repo_root,
        skill_path=path,
        mode=mode,
        runner=runner,
        raw_output=str(result.data.get("raw_output") or ""),
        raw_error=str(result.data.get("raw_error") or ""),
        eval_status=str(result.data.get("eval_status") or ("pass" if result.status == "success" else "fail")),
        blocker_class=result.data.get("blocker_class") if isinstance(result.data.get("blocker_class"), str) else None,
        started_at=eval_started_at,
        timeout_seconds=timeout_seconds,
    )
    result.data["eval_closeout"] = closeout
    if closeout.get("path"):
        result.data["eval_closeout_path"] = closeout["path"]
    if closeout.get("status") == "blocked" and result.status != "error":
        blocker_class = str(closeout.get("blocker_class") or "blocked_missing_artifact")
        result.status = "error"
        result.data["eval_status"] = blocker_class
        result.data["blocker_class"] = blocker_class
        lifecycle_events = result.data.setdefault("lifecycle_events", [])
        if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
            lifecycle_events.pop()
        _finish_eval_lifecycle(
            result,
            path=path,
            mode=mode,
            runner=runner,
            eval_status=blocker_class,
            blocker_class=blocker_class,
        )
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Evaluation run blocked by closeout contract: {blocker_class}.",
            fix_suggestion=str(closeout.get("next_reproduce_command") or result.data["validation_commands"][0]),
        ))

    return result

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
