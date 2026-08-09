from .evals_projection import *  # noqa: F403

def _tessl_auth_blocked(*texts: str) -> bool:
    combined = "\n".join(texts).lower()
    return "authenticate with tessl" in combined


def _run_tessl_project_command(
    tessl_path: str,
    args: list[str],
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [tessl_path, *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=TESSL_PROJECT_LINK_TIMEOUT_SECONDS,
        env=env,
    )


def _signal_name_for_returncode(returncode: int) -> str | None:
    if returncode >= 0:
        return None
    signal_number = abs(returncode)
    try:
        return signal.Signals(signal_number).name
    except ValueError:
        return f"signal {signal_number}"


def _tessl_signal_blocker(process: subprocess.CompletedProcess[str], *, lane: str) -> str | None:
    signal_name = _signal_name_for_returncode(process.returncode)
    if not signal_name:
        return None
    return (
        f"Tessl {lane} command was terminated by {signal_name} "
        f"(return code {process.returncode}) before completing. This is a local "
        "native CLI, sandbox, or OS runtime blocker, not a skill assessment result."
    )


def _tessl_project_link_matches(stdout: str, *, workspace: str, project: str) -> bool:
    parsed = _json_or_text(stdout.strip()) if stdout.strip() else None
    if not isinstance(parsed, dict):
        return False

    def values_for(key: str, obj: object) -> set[str]:
        values: set[str] = set()
        if isinstance(obj, dict):
            for item_key, item_value in obj.items():
                if item_key in {key, f"{key}Name", f"{key}_name"} and isinstance(item_value, str):
                    values.add(item_value)
                values.update(values_for(key, item_value))
        elif isinstance(obj, list):
            for item in obj:
                values.update(values_for(key, item))
        return values

    workspace_values = values_for("workspace", parsed)
    project_values = values_for("project", parsed)
    name_values = values_for("name", parsed)
    return (
        workspace in workspace_values
        and (project in project_values or f"{workspace}/{project}" in name_values)
    )


def _tessl_eval_list_count(stdout: str) -> int | None:
    parsed = _parse_json_value_from_text(stdout) if stdout.strip() else None
    if isinstance(parsed, list):
        return len(parsed)
    if not isinstance(parsed, dict):
        return None
    if parsed.get("status") == "error" or parsed.get("ok") is False:
        return None
    for key in ("evals", "runs", "items", "nodes", "data", "results"):
        value = parsed.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            nested = _tessl_eval_list_count(json.dumps(value))
            if nested is not None:
                return nested
    return None


def _tessl_eval_list_runs(stdout: str) -> list[dict[str, object]] | None:
    parsed = _parse_json_value_from_text(stdout) if stdout.strip() else None
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if not isinstance(parsed, dict):
        return None
    if parsed.get("status") == "error" or parsed.get("ok") is False:
        return None
    for key in ("evals", "runs", "items", "nodes", "data", "results"):
        value = parsed.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _tessl_eval_list_runs(json.dumps(value))
            if nested is not None:
                return nested
    return None


def _tessl_run_field(run: dict[str, object], *keys: str) -> object:
    for key in keys:
        value = run.get(key)
        if value is not None:
            return value
    attributes = run.get("attributes")
    if isinstance(attributes, dict):
        for key in keys:
            value = attributes.get(key)
            if value is not None:
                return value
    return None


def _tessl_run_metadata_field(run: dict[str, object], key: str) -> object:
    metadata = run.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get(key)
    attributes = run.get("attributes")
    if isinstance(attributes, dict):
        metadata = attributes.get("metadata")
        if isinstance(metadata, dict):
            return metadata.get(key)
    return None


def _tessl_pending_run_ids_for_project(stdout: str, *, project: str) -> list[str] | None:
    runs = _tessl_eval_list_runs(stdout)
    if runs is None:
        return None
    pending_ids: list[str] = []
    for run in runs:
        run_status = _tessl_run_field(run, "status")
        if not isinstance(run_status, str) or run_status.strip().lower() != "pending":
            continue
        tile_name = _tessl_run_metadata_field(run, "tileName")
        subject = _tessl_run_field(run, "subject")
        if not any(isinstance(value, str) and value.rsplit("/", 1)[-1] == project for value in (tile_name, subject)):
            continue
        run_id = _tessl_run_field(run, "id", "evalRunId", "runId")
        if isinstance(run_id, str) and run_id.strip():
            pending_ids.append(run_id.strip())
    return pending_ids


def _tessl_pending_run_preflight(
    tessl_path: str,
    workspace: str,
    project: str,
    staged_root: Path,
    env: dict[str, str],
) -> dict[str, object]:
    command_text = _tessl_eval_list_command_text(tessl_path, workspace)
    try:
        process, command_text = _run_tessl_eval_list_for_workspace(tessl_path, workspace, staged_root, env)
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": "Tessl pending-run preflight timed out before live scoring; refusing to submit another run.",
            "command": command_text,
            "raw_output": _as_text(exc.stdout),
            "raw_error": _as_text(exc.stderr),
        }
    except OSError as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": f"Failed to run Tessl pending-run preflight; refusing to submit another run: {exc}",
            "command": command_text,
            "raw_output": "",
            "raw_error": str(exc),
        }

    if blocker := _tessl_signal_blocker(process, lane="eval list pending-run preflight"):
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": blocker,
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if _tessl_auth_blocked(process.stdout, process.stderr):
        return {
            "status": "blocked",
            "blocker_class": "blocked_auth",
            "blocker": "Tessl authentication is required before pending-run preflight can protect live eval credits.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if process.returncode != 0:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": "Tessl pending-run preflight could not fetch run history; refusing to submit another live eval run.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }

    pending_ids = _tessl_pending_run_ids_for_project(process.stdout, project=project)
    if pending_ids is None:
        return {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "blocker": "Tessl pending-run preflight could not parse run history; refusing to submit another live eval run.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if pending_ids:
        return {
            "status": "blocked",
            "blocker_class": "blocked_environment",
            "blocker": "A pending Tessl eval run already exists for this workspace/project; inspect that run instead of spending another.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "pending_eval_run_ids": pending_ids,
        }
    return {
        "status": "pass",
        "blocker": None,
        "blocker_class": None,
        "command": command_text,
        "exit_code": process.returncode,
        "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
        "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        "pending_eval_run_ids": [],
    }


def _tessl_run_budget_preflight(
    tessl_path: str,
    workspace: str,
    staged_root: Path,
    env: dict[str, str],
) -> dict[str, object]:
    try:
        process, command_text = _run_tessl_eval_list_for_workspace(tessl_path, workspace, staged_root, env)
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": "Tessl workspace run-budget preflight timed out before live scoring.",
            "command": _tessl_eval_list_command_text(tessl_path, workspace),
            "raw_output": _as_text(exc.stdout),
            "raw_error": _as_text(exc.stderr),
        }
    except OSError as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": f"Failed to run Tessl workspace run-budget preflight: {exc}",
            "command": _tessl_eval_list_command_text(tessl_path, workspace),
            "raw_output": "",
            "raw_error": str(exc),
        }

    if blocker := _tessl_signal_blocker(process, lane="eval list run-budget preflight"):
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": blocker,
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if _tessl_auth_blocked(process.stdout, process.stderr):
        return {
            "status": "blocked",
            "blocker_class": "blocked_auth",
            "blocker": "Tessl CLI is installed locally, but authentication is required before run-budget preflight can run.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if process.returncode != 0:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": (
                "Tessl workspace run-budget preflight could not fetch run history; "
                "blocking live scoring because remaining workspace capacity could not "
                "be checked."
            ),
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
            "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
            "capacity_source": "unavailable_eval_list",
        }

    used_runs = _tessl_eval_list_count(process.stdout)
    if used_runs is None:
        return {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "blocker": (
                "Tessl workspace run-budget preflight could not determine remaining "
                "capacity; blocking live scoring because workspace reserve could not "
                "be enforced."
            ),
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
            "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
            "capacity_source": "unparseable_eval_list",
        }

    remaining_runs = max(TESSL_WORKSPACE_RUN_LIMIT - used_runs, 0)
    status = "pass" if remaining_runs > TESSL_WORKSPACE_RUN_RESERVE else "blocked"
    blocker = None
    blocker_class = None
    if status == "blocked":
        blocker = (
            f"Tessl workspace {workspace} has {remaining_runs} of "
            f"{TESSL_WORKSPACE_RUN_LIMIT} runs remaining, which is at or below the "
            f"{TESSL_WORKSPACE_RUN_RESERVE}-run reserve. Use dry-run/local evidence "
            "before spending another live eval run."
        )
        blocker_class = "blocked_environment"
    return {
        "status": status,
        "blocker": blocker,
        "blocker_class": blocker_class,
        "command": command_text,
        "exit_code": process.returncode,
        "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
        "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
        "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
        "used_runs": used_runs,
        "remaining_runs": remaining_runs,
    }


def _tessl_eval_list_command(tessl_path: str, workspace: str) -> list[str]:
    return [tessl_path, "eval", "list", "--json", "--workspace", workspace]


def _tessl_eval_list_command_text(tessl_path: str, workspace: str) -> str:
    return " ".join(shlex.quote(_portable_command_part(str(part))) for part in _tessl_eval_list_command(tessl_path, workspace))


def _run_tessl_eval_list_for_workspace(
    tessl_path: str,
    workspace: str,
    staged_root: Path,
    env: dict[str, str],
) -> tuple[subprocess.CompletedProcess[str], str]:
    command = _tessl_eval_list_command(tessl_path, workspace)
    process = subprocess.run(
        command,
        cwd=str(staged_root),
        capture_output=True,
        text=True,
        timeout=TESSL_PROJECT_LINK_TIMEOUT_SECONDS,
        env=env,
    )
    return process, " ".join(shlex.quote(str(part)) for part in command)


def _tessl_live_private_eval_run_command(
    tessl_path: str,
    workspace: str,
    staged_source: Path,
) -> list[str]:
    return [
        tessl_path,
        "eval",
        "run",
        "--json",
        "--workspace",
        workspace,
        str(staged_source),
    ]


def _ensure_tessl_project_link(
    tessl_path: str,
    staged_root: Path,
    identity: dict[str, str | None],
) -> dict[str, object]:
    workspace = identity.get("workspace")
    project = identity.get("project")
    common = {
        "identity": identity,
        "staged_source": str(staged_root),
        "checked": True,
    }
    if not workspace or not project:
        return {
            **common,
            "status": "skipped",
            "action": "workspace_not_provided",
            "blocker": None,
            "blocker_class": None,
            "commands": [],
        }

    tessl_env = dict(os.environ)
    tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    commands: list[dict[str, object]] = []

    def record(action: str, process: subprocess.CompletedProcess[str]) -> None:
        process_args = getattr(process, "args", [])
        if not isinstance(process_args, (list, tuple)):
            process_args = []
        signal_name = _signal_name_for_returncode(process.returncode)
        commands.append({
            "action": action,
            "command": " ".join(shlex.quote(_portable_command_part(str(part))) for part in process_args),
            "exit_code": process.returncode,
            "signal": signal_name,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "parsed_output": (
                _sanitize_tessl_live_private_payload(_json_or_text(process.stdout.strip()))
                if process.stdout.strip()
                else None
            ),
        })

    try:
        check = _run_tessl_project_command(tessl_path, ["project", "repair", "--json", "--yes"], staged_root, tessl_env)
        record("check", check)
        if blocker := _tessl_signal_blocker(check, lane="project repair check"):
            return {
                **common,
                "status": "blocked",
                "action": "check",
                "blocker": blocker,
                "blocker_class": "blocked_runtime",
                "commands": commands,
            }
        if _tessl_auth_blocked(check.stdout, check.stderr):
            return {
                **common,
                "status": "blocked",
                "action": "check",
                "blocker": "Tessl CLI is installed locally, but authentication is required before project link checks can run.",
                "blocker_class": "blocked_auth",
                "commands": commands,
            }
        if check.returncode == 0 and _tessl_project_link_matches(check.stdout, workspace=workspace, project=project):
            return {
                **common,
                "status": "pass",
                "action": "already_linked",
                "blocker": None,
                "blocker_class": None,
                "commands": commands,
            }

        relink = _run_tessl_project_command(
            tessl_path,
            ["project", "repair", "--relink", "--workspace", workspace, "--project", project, "--yes", "--json"],
            staged_root,
            tessl_env,
        )
        record("relink", relink)
        if blocker := _tessl_signal_blocker(relink, lane="project relink"):
            return {
                **common,
                "status": "blocked",
                "action": "relink",
                "blocker": blocker,
                "blocker_class": "blocked_runtime",
                "commands": commands,
            }
        if _tessl_auth_blocked(relink.stdout, relink.stderr):
            return {
                **common,
                "status": "blocked",
                "action": "relink",
                "blocker": "Tessl CLI is installed locally, but authentication is required before project relink can run.",
                "blocker_class": "blocked_auth",
                "commands": commands,
            }
        if _tessl_process_succeeded(relink):
            update_source = _run_tessl_project_command(
                tessl_path,
                ["project", "repair", "--update-source", "--yes", "--json"],
                staged_root,
                tessl_env,
            )
            record("update_source", update_source)
            if blocker := _tessl_signal_blocker(update_source, lane="project source repair"):
                return {
                    **common,
                    "status": "blocked",
                    "action": "update_source",
                    "blocker": blocker,
                    "blocker_class": "blocked_runtime",
                    "commands": commands,
                }
            if _tessl_auth_blocked(update_source.stdout, update_source.stderr):
                return {
                    **common,
                    "status": "blocked",
                    "action": "update_source",
                    "blocker": "Tessl CLI is installed locally, but authentication is required before project source repair can run.",
                    "blocker_class": "blocked_auth",
                    "commands": commands,
                }
            if update_source.returncode != 0:
                return {
                    **common,
                    "status": "blocked",
                    "action": "update_source",
                    "blocker": (
                        f"Relinked Tessl project {workspace}/{project}, but failed to update "
                        "the recorded source for the temp-staged eval directory."
                    ),
                    "blocker_class": "blocked_validation",
                    "commands": commands,
                }
            return {
                **common,
                "status": "pass",
                "action": "relinked_existing_project_updated_source",
                "blocker": None,
                "blocker_class": None,
                "commands": commands,
            }

        create = _run_tessl_project_command(
            tessl_path,
            ["project", "create", "--new", "--workspace", workspace, project],
            staged_root,
            tessl_env,
        )
        record("create", create)
        if blocker := _tessl_signal_blocker(create, lane="project create"):
            return {
                **common,
                "status": "blocked",
                "action": "create",
                "blocker": blocker,
                "blocker_class": "blocked_runtime",
                "commands": commands,
            }
        if _tessl_auth_blocked(create.stdout, create.stderr):
            return {
                **common,
                "status": "blocked",
                "action": "create",
                "blocker": "Tessl CLI is installed locally, but authentication is required before project create can run.",
                "blocker_class": "blocked_auth",
                "commands": commands,
            }
        if _tessl_process_succeeded(create):
            return {
                **common,
                "status": "pass",
                "action": "created_project",
                "blocker": None,
                "blocker_class": None,
                "commands": commands,
            }
        return {
            **common,
            "status": "blocked",
            "action": "create",
            "blocker": (
                f"Unable to relink or create Tessl project {workspace}/{project} "
                "for the temp-staged eval directory."
            ),
            "blocker_class": "blocked_validation",
            "commands": commands,
        }
    except subprocess.TimeoutExpired as e:
        return {
            **common,
            "status": "blocked",
            "action": "project_link",
            "blocker": f"Tessl project link check timed out after {TESSL_PROJECT_LINK_TIMEOUT_SECONDS} seconds.",
            "blocker_class": "blocked_runtime",
            "commands": commands,
            "raw_output": _as_text(e.stdout),
            "raw_error": _as_text(e.stderr),
        }
    except OSError as e:
        return {
            **common,
            "status": "blocked",
            "action": "project_link",
            "blocker": f"Failed to run Tessl project link check: {e}",
            "blocker_class": "blocked_runtime",
            "commands": commands,
        }

__all__ = [name for name in globals() if not name.startswith("__")]
