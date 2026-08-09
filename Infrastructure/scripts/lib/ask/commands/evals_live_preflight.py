from __future__ import annotations

from .evals_project import *  # noqa: F403

def _stage_tessl_eval_source(
    repo_root: Path,
    path: str,
    temp_root: Path | None = None,
    workspace: str | None = None,
) -> tuple[Path, list[str]]:
    repo_root_resolved = repo_root.resolve()
    source_root = (repo_root_resolved / path).resolve()
    if not source_root.is_relative_to(repo_root_resolved):
        raise FileNotFoundError("Tessl eval source must be inside repo_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl eval source is not a directory: {path}")

    staged_root = (temp_root / source_root.name) if temp_root else _stable_tessl_stage_parent(path)
    staged_root.mkdir(parents=True, exist_ok=True)
    _archive_stage_children(staged_root, "local-eval")

    copied: list[str] = []
    for relative_path in (
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "references/task-profile.json",
    ):
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
    copied.extend(_copy_tree_files_if_present(source_root, "references/evals", staged_root))
    copied.extend(_copy_tree_files_if_present(source_root, "assets", staged_root))
    copied.extend(_write_tessl_scenarios_from_evals(source_root, staged_root))
    copied.extend(_write_tessl_project_marker(source_root, staged_root, workspace))

    if not copied:
        raise FileNotFoundError(f"No Tessl eval staging files found under: {path}")
    return staged_root, copied


def _stage_tessl_live_private_source(
    repo_root: Path,
    path: str,
    workspace: str,
    temp_root: Path | None = None,
) -> tuple[Path, list[str]]:
    repo_root_resolved = repo_root.resolve()
    source_root = (repo_root_resolved / path).resolve()
    if not source_root.is_relative_to(repo_root_resolved):
        raise FileNotFoundError("Tessl live eval source must be inside repo_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl live eval source is not a directory: {path}")

    staged_root = (temp_root / source_root.name) if temp_root else _stable_tessl_live_stage_parent(path)
    staged_root.mkdir(parents=True, exist_ok=True)
    _archive_stage_children(staged_root, "live-private")

    copied: list[str] = []
    copied.extend(_write_tessl_live_plugin_manifest(source_root, staged_root, workspace))
    copied.extend(_write_tessl_registry_readme(source_root, staged_root, workspace))
    copied.extend(_write_tesslignore(staged_root))
    copied.extend(_copy_tessl_live_skill_package(source_root, staged_root))
    copied.extend(_write_tessl_live_evals_from_references(source_root, staged_root))
    _validate_tessl_projection_shape(
        staged_root,
        skill_name=source_root.name,
        workspace=workspace,
        project_slug=_tessl_project_slug(source_root),
        require_evals=True,
    )

    if f"skills/{source_root.name}/SKILL.md" not in copied:
        raise FileNotFoundError(f"No SKILL.md found under Tessl live eval source: {path}")
    return staged_root, copied


def _tessl_live_staged_case_ids(staged_source: Path) -> list[str]:
    """Return the exact scenario ids that would be submitted to Tessl live."""
    case_ids: set[str] = set()
    for dirname in ("evals", "scenarios"):
        root = staged_source / dirname
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if (child / "task.md").is_file() and (child / "criteria.json").is_file():
                case_ids.add(child.name)
    return sorted(case_ids)


def _case_ids_with_pass_status(payload: object) -> set[str]:
    """Collect case ids that carry direct pass evidence in SDK OSS receipts."""
    passed: set[str] = set()
    if isinstance(payload, dict):
        case_id = payload.get("case_id")
        status = payload.get("status")
        latest = payload.get("latest_evidence")
        latest_status = latest.get("status") if isinstance(latest, dict) else None
        if isinstance(case_id, str) and (status == "pass" or latest_status == "pass"):
            passed.add(case_id)
        for value in payload.values():
            passed.update(_case_ids_with_pass_status(value))
    elif isinstance(payload, list):
        for item in payload:
            passed.update(_case_ids_with_pass_status(item))
    return passed


def _tessl_live_readiness_lanes(repo_root: Path, source_path: str) -> dict[str, dict[str, object]]:
    readiness_path = default_handoff_readiness_path(repo_root, repo_root / source_path)
    readiness = _load_json_file(readiness_path)
    lanes = readiness.get("lanes")
    if not isinstance(lanes, list):
        return {}
    lane_map: dict[str, dict[str, object]] = {}
    for lane in lanes:
        if isinstance(lane, dict) and isinstance(lane.get("id"), str):
            lane_map[str(lane["id"])] = lane
    return lane_map


def _resolve_tessl_live_evidence_path(repo_root: Path, raw_path: object) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def _oss_pass_case_ids_for_live(repo_root: Path, receipt_path: Path | None, seen: set[Path] | None = None) -> set[str]:
    if receipt_path is None:
        return set()
    resolved = receipt_path.resolve()
    if seen is None:
        seen = set()
    if resolved in seen:
        return set()
    seen.add(resolved)

    payload = _load_json_file(receipt_path)
    passed = _case_ids_with_pass_status(payload)
    source_receipt = payload.get("source_receipt") if isinstance(payload, dict) else None
    source_path = _resolve_tessl_live_evidence_path(repo_root, source_receipt)
    if source_path is not None and source_path.is_file():
        passed.update(_oss_pass_case_ids_for_live(repo_root, source_path, seen))
    return passed


def _tessl_live_oss_scenario_parity(
    repo_root: Path,
    source_path: str,
    staged_source: Path,
) -> dict[str, object]:
    """Block Tessl live when staged cases outrun OSS local/cloud pass evidence."""
    staged_case_ids = _tessl_live_staged_case_ids(staged_source)
    lanes = _tessl_live_readiness_lanes(repo_root, source_path)
    lane_case_ids: dict[str, list[str]] = {}
    missing_by_lane: dict[str, list[str]] = {}
    extra_by_lane: dict[str, list[str]] = {}
    lane_receipts: dict[str, dict[str, object]] = {}
    staged_case_set = set(staged_case_ids)
    for lane_id in ("oss-local", "oss-cloud"):
        lane = lanes.get(lane_id) or {}
        receipt_path = _resolve_tessl_live_evidence_path(repo_root, lane.get("receipt_path"))
        receipt_found = receipt_path is not None and receipt_path.is_file()
        passed = _oss_pass_case_ids_for_live(repo_root, receipt_path)
        lane_receipts[lane_id] = {
            "receipt_path": str(receipt_path.relative_to(repo_root)) if receipt_path and receipt_path.is_relative_to(repo_root) else str(receipt_path) if receipt_path else None,
            "receipt_found": receipt_found,
        }
        lane_case_ids[lane_id] = sorted(passed)
        missing_by_lane[lane_id] = sorted(staged_case_set - passed)
        extra_by_lane[lane_id] = sorted(passed - staged_case_set)

    unproven = sorted(set().union(*(set(items) for items in missing_by_lane.values())))
    extra = sorted(set().union(*(set(items) for items in extra_by_lane.values())))
    ok = bool(staged_case_ids) and not unproven and not extra
    return {
        "schema_version": "skills-sdk.tessl-live-oss-scenario-parity.v1",
        "status": "pass" if ok else "blocked",
        "staged_case_count": len(staged_case_ids),
        "staged_case_ids": staged_case_ids,
        "oss_local_pass_count": len(lane_case_ids.get("oss-local", [])),
        "oss_cloud_pass_count": len(lane_case_ids.get("oss-cloud", [])),
        "missing_by_lane": missing_by_lane,
        "extra_by_lane": extra_by_lane,
        "lane_receipts": lane_receipts,
        "unproven_case_count": len(unproven),
        "unproven_case_ids": unproven,
        "extra_case_count": len(extra),
        "extra_case_ids": extra,
        "rule": (
            "The Tessl live scenario set must exactly match both oss-local and "
            "oss-cloud pass evidence for the current live candidate."
        ),
    }


def _tessl_live_budget_preflight(staged_source: Path) -> dict[str, object]:
    """Return the paid-live Tessl scenario/cost-shape gate for staged input."""
    staged_case_ids = _tessl_live_staged_case_ids(staged_source)
    scenario_manifest = _load_json_file(staged_source / "scenario-sources.json")
    structure_only = bool(scenario_manifest.get("structure_only_exception"))
    generated_case_ids = sorted(case_id for case_id in staged_case_ids if case_id.startswith("generated-eval."))
    scenario_count = len(staged_case_ids)
    expected_solution_runs = scenario_count * TESSL_LIVE_PRIVATE_VARIANT_COUNT
    expected_score_runs = scenario_count * TESSL_LIVE_PRIVATE_VARIANT_COUNT
    expected_model_tasks = scenario_count * TESSL_LIVE_PRIVATE_VARIANT_COUNT * TESSL_LIVE_PRIVATE_MODEL_TASKS_PER_VARIANT
    blockers: list[str] = []
    if scenario_count > TESSL_LIVE_PRIVATE_MAX_SCENARIOS:
        blockers.append(
            f"scenario_count {scenario_count} exceeds the default {TESSL_LIVE_PRIVATE_MAX_SCENARIOS}-case Tessl live cost cap"
        )
    if not structure_only and scenario_count < TESSL_LIVE_PRIVATE_MIN_SCENARIOS:
        blockers.append(
            f"scenario_count {scenario_count} is below the {TESSL_LIVE_PRIVATE_MIN_SCENARIOS}-case Tessl live coverage floor"
        )
    if generated_case_ids:
        blockers.append("generated-eval.* scenarios require an explicit budgeted live lane before upload")

    return {
        "schema_version": "skills-sdk.tessl-live-budget-preflight.v1",
        "status": "pass" if not blockers else "blocked",
        "blocker_class": None if not blockers else "blocked_validation",
        "blockers": blockers,
        "scenario_count": scenario_count,
        "min_scenarios_required": TESSL_LIVE_PRIVATE_MIN_SCENARIOS,
        "target_scenarios": TESSL_LIVE_PRIVATE_TARGET_SCENARIOS,
        "max_scenarios_default": TESSL_LIVE_PRIVATE_MAX_SCENARIOS,
        "structure_only_exception": structure_only,
        "staged_case_ids": staged_case_ids,
        "generated_case_count": len(generated_case_ids),
        "generated_case_ids": generated_case_ids,
        "expected_variants": ["baseline", "usage-spec"],
        "expected_variant_count": TESSL_LIVE_PRIVATE_VARIANT_COUNT,
        "expected_solution_runs": expected_solution_runs,
        "expected_score_runs": expected_score_runs,
        "expected_model_tasks": expected_model_tasks,
        "rule": (
            "Tessl live accepts the same 5-to-10-case set proven by oss-local and oss-cloud, "
            "targets 8 high-value scenarios, and requires an explicit policy change for "
            "larger or generated scenario uploads."
        ),
    }


def _stable_tessl_scenario_generation_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-scenario-generation" / f"{safe_name}-{digest}"


def _tessl_local_proof_policy(workspace: str | None = None) -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.tessl-local-proof-policy.v1",
        "workspace": workspace,
        "stage": "Tessl Distribution -> Local Runtime Truth bridge",
        "proves": [
            "controlled Tessl plugin package shape",
            "local Tessl plugin lint compatibility",
            "temporary plugin archive packability",
            "file: install command compatibility inside a temporary project workspace",
            "optional Tessl review threshold command result when explicitly requested",
        ],
        "does_not_prove": [
            "live Tessl eval score",
            "public registry publication",
            "persistent user runtime activation",
            "oss-local or oss-cloud behavioral proof",
        ],
        "no_publish": True,
        "no_registry_upload": True,
        "no_live_repo_source": True,
        "install_scope": "temporary project workspace under /tmp/ask-tessl-local-install",
    }


def _tessl_local_command_payload(
    command: list[str],
    process: subprocess.CompletedProcess[str],
    *,
    cwd: Path,
) -> dict[str, object]:
    def redact(value: str) -> str:
        return re.sub(r"[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}", "<redacted-email>", value)

    return {
        "status": "success" if process.returncode == 0 else "error",
        "command": " ".join(shlex.quote(_portable_command_part(part)) for part in command),
        "cwd": str(cwd),
        "exit_code": process.returncode,
        "stdout": redact(process.stdout),
        "stderr": redact(process.stderr),
    }


def _portable_command_part(part: str) -> str:
    if Path(part).is_absolute():
        return Path(part).name
    return part


def _sanitize_tessl_live_private_payload(value: object) -> object:
    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key, item in value.items():
            if key in {"createdBy", "user", "userId", "firstName", "lastName"}:
                sanitized[key] = "<redacted-actor>"
            elif key in {"command", "cliInvocation", "cwd", "path", "staged_source"}:
                sanitized[key] = _sanitize_tessl_live_private_payload(item)
            else:
                sanitized[key] = _sanitize_tessl_live_private_payload(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_tessl_live_private_payload(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, (dict, list)):
                return json.dumps(_sanitize_tessl_live_private_payload(parsed), indent=2, sort_keys=True)
        redacted = re.sub(r"/Users/[^\s\"']+", "<user-path>", value)
        redacted = re.sub(r"[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}", "<redacted-email>", redacted)
        return redacted
    return value


def _run_tessl_local_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: int,
) -> dict[str, object]:
    try:
        process = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
    except subprocess.TimeoutExpired as e:
        return {
            "status": "blocked",
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
            "timeout_seconds": timeout_seconds,
            "stdout": _as_text(e.stdout),
            "stderr": _as_text(e.stderr),
            "blocker": f"Tessl local proof command timed out after {timeout_seconds} seconds.",
            "blocker_class": "blocked_runtime",
        }
    except OSError as e:
        return {
            "status": "blocked",
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
            "stdout": "",
            "stderr": str(e),
            "blocker": f"Failed to run Tessl local proof command: {e}",
            "blocker_class": "blocked_runtime",
        }

    payload = _tessl_local_command_payload(command, process, cwd=cwd)
    if signal_blocker := _tessl_signal_blocker(process, lane="local proof"):
        payload["status"] = "blocked"
        payload["blocker"] = signal_blocker
        payload["blocker_class"] = "blocked_runtime"
    elif process.returncode != 0 and _tessl_auth_blocked(process.stdout, process.stderr):
        payload["status"] = "blocked"
        payload["blocker"] = "Tessl CLI is installed locally, but authentication is required before this local proof can run."
        payload["blocker_class"] = "blocked_auth"
    return payload

__all__ = [name for name in globals() if not name.startswith("__")]
