from .evals_local_scenario import *  # noqa: F403

def _tessl_eval_result_common(
    *,
    command: str,
    source_path: str,
    staged_source: Path,
    copied_files: list[str],
    workspace: str,
    project_identity: dict[str, str | None],
    dry_run: bool,
) -> dict:
    plugin_version = None
    try:
        manifest = json.loads((staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
        raw_version = manifest.get("version") if isinstance(manifest, dict) else None
        if isinstance(raw_version, str):
            plugin_version = raw_version
    except (OSError, json.JSONDecodeError):
        plugin_version = None
    return {
        "command": command,
        "source_path": source_path,
        "staged_source": str(staged_source),
        "plugin_manifest": str(staged_source / ".tessl-plugin" / "plugin.json"),
        "plugin_version": plugin_version,
        "tessl_project_marker": str(staged_source / "tessl.json") if (staged_source / "tessl.json").exists() else None,
        "staged_files": copied_files,
        "staging_policy": "stable_tmp_private_plugin_evidence",
        "workspace": workspace,
        "project_identity": project_identity,
        "visibility": "private",
        "dry_run": dry_run,
        "live_private": True,
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
        "policy": _tessl_live_private_policy(workspace),
    }


def _run_tessl_live_private_eval(
    repo_root: Path,
    path: str,
    *,
    workspace: str | None,
    dry_run: bool = False,
) -> dict:
    """Run or preview the opt-in private Tessl plugin eval lane."""
    command_display = "tessl eval run --json --workspace <workspace> <staged-plugin-dir>"
    test_process_without_mock = (
        os.environ.get("PYTEST_CURRENT_TEST")
        and type(subprocess.run).__module__ != "unittest.mock"
    )
    if not dry_run and (test_process_without_mock or os.environ.get("ASK_EXTERNAL_EFFECTS") == "deny"):
        return {
            "status": "blocked",
            "command": command_display,
            "source_path": path,
            "raw_output": "",
            "raw_error": "",
            "blocker": "Tessl live evaluation is blocked by the hermetic test effect policy; pytest requires an in-process subprocess mock and provider submission requires a separately authorised operator process.",
            "blocker_class": "blocked_validation",
            "policy": _tessl_live_private_policy(workspace),
            "live_private": True,
            "dry_run": dry_run,
        }
    try:
        normalized_workspace = _validate_tessl_workspace(workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(repo_root, path, normalized_workspace)
        command_display = f"tessl eval run --json --workspace {normalized_workspace} {staged_source}"
    except (OSError, ValueError) as e:
        return {
            "status": "blocked",
            "command": command_display,
            "source_path": path,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to stage private Tessl plugin eval source: {e}",
            "blocker_class": "blocked_validation",
            "policy": _tessl_live_private_policy(workspace),
            "live_private": True,
            "dry_run": dry_run,
        }

    common = _tessl_eval_result_common(
        command=command_display,
        source_path=path,
        staged_source=staged_source,
        copied_files=copied_files,
        workspace=normalized_workspace,
        project_identity=_tessl_project_identity((repo_root / path).resolve(), normalized_workspace),
        dry_run=dry_run,
    )
    parity = _tessl_live_oss_scenario_parity(repo_root, path, staged_source)
    budget_preflight = _tessl_live_budget_preflight(staged_source)
    common["oss_scenario_parity"] = parity
    common["budget_preflight"] = budget_preflight
    if parity.get("status") != "pass":
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": (
                "Tessl live scenario set includes scenarios without both oss-local "
                "and oss-cloud pass evidence."
            ),
            "blocker_class": "blocked_validation",
        }
    if budget_preflight.get("status") != "pass":
        blockers = budget_preflight.get("blockers")
        blocker_text = "; ".join(str(item) for item in blockers) if isinstance(blockers, list) else None
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": blocker_text or "Tessl live budget preflight blocked the staged scenario set.",
            "blocker_class": budget_preflight.get("blocker_class") or "blocked_validation",
        }
    if dry_run:
        return {
            "status": "pass",
            **common,
            "raw_output": "",
            "raw_error": "",
            "exit_code": 0,
            "blocker": None,
            "blocker_class": None,
        }

    tessl_path = shutil.which("tessl")
    if not tessl_path:
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": "Installed native tessl CLI was not found on PATH.",
            "blocker_class": "blocked_runtime",
        }

    project_link = _validate_tessl_project_link_receipt(
        repo_root,
        path,
        normalized_workspace,
        common["project_identity"],
    )
    common["project_link"] = project_link
    if project_link.get("status") == "blocked":
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": project_link.get("blocker"),
            "blocker_class": project_link.get("blocker_class"),
        }

    tessl_env = dict(os.environ)
    tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    project_name = str(common["project_identity"].get("project") or _tessl_live_tile_slug(repo_root / path))
    pending_run_preflight = _tessl_pending_run_preflight(
        tessl_path,
        normalized_workspace,
        project_name,
        staged_source,
        tessl_env,
    )
    common["pending_run_preflight"] = pending_run_preflight
    if pending_run_preflight.get("status") == "blocked":
        return {
            "status": "blocked",
            **common,
            "raw_output": str(pending_run_preflight.get("raw_output") or ""),
            "raw_error": str(pending_run_preflight.get("raw_error") or ""),
            "blocker": pending_run_preflight.get("blocker"),
            "blocker_class": pending_run_preflight.get("blocker_class"),
        }
    run_budget_preflight = _tessl_run_budget_preflight(
        tessl_path,
        normalized_workspace,
        staged_source,
        tessl_env,
    )
    common["run_budget_preflight"] = run_budget_preflight
    if run_budget_preflight.get("status") == "blocked":
        return {
            "status": "blocked",
            **common,
            "raw_output": str(run_budget_preflight.get("raw_output") or ""),
            "raw_error": str(run_budget_preflight.get("raw_error") or ""),
            "blocker": run_budget_preflight.get("blocker"),
            "blocker_class": run_budget_preflight.get("blocker_class"),
        }

    cmd = _tessl_live_private_eval_run_command(tessl_path, normalized_workspace, staged_source)
    try:
        process = subprocess.run(
            cmd,
            cwd=str(staged_source),
            capture_output=True,
            text=True,
            timeout=600,
            env=tessl_env,
        )
    except subprocess.TimeoutExpired as e:
        return {
            "status": "blocked",
            **common,
            "raw_output": _as_text(e.stdout),
            "raw_error": _as_text(e.stderr),
            "blocker": "Tessl private plugin eval timed out after 600 seconds.",
            "blocker_class": "blocked_runtime",
        }
    except OSError as e:
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to run Tessl private plugin eval: {e}",
            "blocker_class": "blocked_runtime",
        }

    raw_output = process.stdout
    raw_error = process.stderr
    auth_text = f"{raw_output}\n{raw_error}".lower()
    if process.returncode != 0 and "authenticate with tessl" in auth_text:
        status = "blocked"
        blocker = "Tessl CLI is installed locally, but authentication is required before private plugin evals can run."
        blocker_class = "blocked_auth"
    elif process.returncode != 0 and "no existing project safely matches this directory" in auth_text:
        status = "blocked"
        blocker = (
            "Tessl CLI is authenticated, but no Tessl project/workspace is linked for the "
            "temp-staged private plugin eval directory. Run tessl project create/link/repair for a live project lane."
        )
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "no tessl project found" in auth_text:
        status = "blocked"
        blocker = "Tessl CLI could not find a tessl.json project marker in the staged private plugin eval directory."
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "project that was not found or is not accessible" in auth_text:
        status = "blocked"
        blocker = (
            f"Tessl project {normalized_workspace}/{_tessl_live_tile_slug(repo_root / path)} "
            f"was not found or is not accessible. Create, link, or repair that project "
            f"in workspace {normalized_workspace} before running live evals."
        )
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "points at a different repository or directory path" in auth_text:
        status = "blocked"
        blocker = (
            "Tessl project binding points at a different source directory than the "
            "temp-staged private eval directory."
        )
        blocker_class = "blocked_validation"
    else:
        status = "pass" if process.returncode == 0 else "fail"
        blocker = None
        blocker_class = None

    eval_run_id = _extract_tessl_eval_run_id(raw_output)
    submission_evidence_path = _write_tessl_live_submission_evidence(
        repo_root,
        path,
        run_id=eval_run_id,
        workspace=normalized_workspace,
        staged_source=staged_source,
        project_identity=common["project_identity"],
    )
    live_result_summary = None
    view_raw_output = ""
    view_raw_error = ""
    view_evidence_path = None
    view_attempts = 0
    view_status = None
    if status == "pass":
        if not eval_run_id:
            status = "blocked"
            blocker = "Tessl private plugin eval completed but did not return an eval run id for score/baseline verification."
            blocker_class = "blocked_validation"
        else:
            view_cmd = [tessl_path, "eval", "view", "--json", eval_run_id]
            try:
                deadline = time.monotonic() + TESSL_LIVE_PRIVATE_VIEW_TIMEOUT_SECONDS
                view_payload = None
                while True:
                    view_attempts += 1
                    view_process = subprocess.run(
                        view_cmd,
                        cwd=str(staged_source),
                        capture_output=True,
                        text=True,
                        timeout=600,
                        env=tessl_env,
                    )
                    view_raw_output = view_process.stdout
                    view_raw_error = view_process.stderr
                    if view_process.returncode != 0:
                        break
                    view_payload = _parse_json_object_from_text(view_raw_output)
                    if view_payload is None:
                        break
                    view_status = _tessl_eval_view_status(view_payload)
                    if _tessl_eval_view_has_complete_scores(view_payload):
                        break
                    if view_status in {"failed", "error", "cancelled", "canceled"}:
                        break
                    if time.monotonic() >= deadline:
                        break
                    time.sleep(TESSL_LIVE_PRIVATE_VIEW_POLL_SECONDS)
            except subprocess.TimeoutExpired as e:
                status = "blocked"
                blocker = "Tessl private plugin eval view timed out while waiting for scored results."
                blocker_class = "blocked_runtime"
                view_raw_output = _as_text(e.stdout)
                view_raw_error = _as_text(e.stderr)
            except OSError as e:
                status = "blocked"
                blocker = f"Failed to inspect Tessl private plugin eval results: {e}"
                blocker_class = "blocked_runtime"
                view_raw_error = str(e)
            else:
                if view_process.returncode != 0:
                    status = "blocked"
                    blocker = "Tessl private plugin eval completed but result inspection failed."
                    blocker_class = "blocked_validation"
                else:
                    try:
                        if view_payload is None:
                            raise ValueError("No JSON object found in Tessl eval view output.")
                        if not _tessl_eval_view_has_complete_scores(view_payload):
                            failure_reason = _tessl_eval_view_failure_reason(view_payload)
                            if failure_reason:
                                failure_code, failure_message = failure_reason
                                if failure_code == "EVAL_QUOTA_EXCEEDED":
                                    blocker_class = "blocked_environment"
                                else:
                                    blocker_class = "blocked_validation"
                                raise ValueError(
                                    f"Tessl eval run failed before scoring: {failure_code}: {failure_message}"
                                )
                            if time.monotonic() >= deadline:
                                raise ValueError("Tessl eval view did not reach complete scored results before timeout.")
                            raise ValueError(f"Tessl eval view is not scored yet (status={view_status or 'unknown'}).")
                        live_result_summary = _summarize_tessl_live_eval_view(view_payload)
                    except ValueError as e:
                        status = "blocked"
                        blocker = f"Failed to parse Tessl private plugin eval score summary: {e}"
                        blocker_class = blocker_class or "blocked_validation"
                    else:
                        if not live_result_summary["meets_min_score"] or not live_result_summary["beats_baseline"]:
                            status = "fail"
                            score_pct = round(float(live_result_summary["score"]) * 100, 2)
                            baseline_pct = round(float(live_result_summary["baseline_score"]) * 100, 2)
                            blocker = (
                                "Tessl private plugin eval completed but failed readiness: "
                                f"score {score_pct}% vs baseline {baseline_pct}%."
                            )
                            blocker_class = None

    view_evidence_path = _write_tessl_live_view_evidence(repo_root, path, eval_run_id, view_raw_output)

    return {
        "status": status,
        **common,
        "exit_code": process.returncode,
        "eval_run_id": eval_run_id,
        "submission_evidence_path": submission_evidence_path,
        "live_result_summary": live_result_summary,
        "view_attempts": view_attempts,
        "view_status": view_status,
        "view_evidence_path": view_evidence_path,
        "view_raw_output": _sanitize_tessl_live_private_payload(view_raw_output),
        "view_raw_error": _sanitize_tessl_live_private_payload(view_raw_error),
        "raw_output": _sanitize_tessl_live_private_payload(raw_output),
        "raw_error": _sanitize_tessl_live_private_payload(raw_error),
        "blocker": blocker,
        "blocker_class": blocker_class,
    }

__all__ = [name for name in globals() if not name.startswith("__")]
