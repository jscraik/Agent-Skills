from __future__ import annotations

from dataclasses import dataclass

from .repo_impl_core import *  # noqa: F403
from .repo_impl_doctor import *  # noqa: F403

def _git_output_text(repo_root: Path, args: list[str]) -> str:
    command = ["git", *args]
    try:
        process = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git command timed out: {' '.join(command)}") from exc
    except OSError as exc:
        raise RuntimeError(
            f"git command could not start: {' '.join(command)} ({exc})"
        ) from exc
    if process.returncode != 0:
        detail = (process.stderr or process.stdout or "").strip()
        raise RuntimeError(
            f"git command failed: {' '.join(command)}"
            + (f" ({detail})" if detail else "")
        )
    return process.stdout


def _git_output_lines(repo_root: Path, args: list[str]) -> list[str]:
    return [line.strip() for line in _git_output_text(repo_root, args).splitlines() if line.strip()]


def _shape_baseline(repo_root: Path, baseline_path: str | None) -> dict[str, Any]:
    deleted = [
        path
        for path in _git_output_lines(repo_root, ["diff", "--name-only", "--diff-filter=D", "HEAD", "--"])
        if path.endswith(".py")
    ]
    siblings: list[str] = []
    if baseline_path:
        relative = Path(baseline_path).resolve().relative_to(repo_root.resolve()).as_posix()
        parent = Path(relative).parent.as_posix()
        siblings = [
            path
            for path in _git_output_lines(
                repo_root,
                ["ls-tree", "-r", "--name-only", "HEAD", "--", f"{parent}/*.py"],
            )
            if path.endswith(".py")
        ]
    paths = list(dict.fromkeys([*deleted, *siblings]))
    head_text = {path: _git_output_text(repo_root, ["show", f"HEAD:{path}"]) for path in paths}
    return {"deleted_python_paths": deleted, "sibling_python_paths": siblings, "head_text": head_text}


def collect_changed_files(repo_root: Path) -> list[str]:
    """Return repo-relative staged, unstaged, and untracked file paths."""
    changed = set()
    for args in (
        ["diff", "--name-only", "--diff-filter=ACMRD", "--"],
        ["diff", "--cached", "--name-only", "--diff-filter=ACMRD", "--"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        changed.update(_git_output_lines(repo_root, args))
    return sorted(changed)


def _validation_command_for_changed_files(changed_files: list[str]) -> str:
    if not changed_files:
        return _repo_validation_command("validate")
    return _repo_validation_command("validate", "--changed-files", *changed_files)


def _closeout_sync_report(changed_files: list[str]) -> dict[str, Any]:
    generated_changed = [
        path for path in changed_files
        if path.startswith(GENERATED_SURFACE_PREFIXES)
    ]
    canonical_skill_changed = [
        path for path in changed_files
        if _is_canonical_skill_path(path)
    ]
    commands = []
    validation_commands = []
    if canonical_skill_changed and not generated_changed:
        commands.append(SKILLS_SYNC_COMMAND)
    flat_source_projection_present = False
    projection_update_present = bool(canonical_skill_changed and generated_changed)
    if canonical_skill_changed or generated_changed:
        validation_commands.append(SDK_HANDLE_CHECK_COMMAND)
    return {
        "needed": bool(commands),
        "commands": commands,
        "validation_commands": validation_commands,
        "generated_changed_files": generated_changed,
        "canonical_skill_changed_files": canonical_skill_changed,
        "projection_update_present": projection_update_present,
        "flat_source_projection_present": flat_source_projection_present,
    }


def _is_canonical_skill_path(path: str) -> bool:
    if path.startswith(CANONICAL_SKILL_PREFIXES):
        return True
    parts = path.split("/")
    return (
        len(parts) >= 4
        and parts[0] == "Plugins"
        and parts[1] != "cache"
        and parts[2] in {"skills", "Skills"}
    )


def _closeout_runtime_budget(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    details = (
        doctor_payload.get("signals", {})
        .get("runtime_budget", {})
        .get("details", {})
    )
    return {
        "status": details.get("status"),
        "default_visible_count": details.get("default_visible_count"),
        "estimated_description_tokens": details.get("estimated_description_tokens"),
        "violation_count": details.get("violation_count", 0),
    }


def _closeout_surface_policy(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    details = (
        doctor_payload.get("signals", {})
        .get("repo_surface", {})
        .get("details", {})
    )
    return {
        "status": details.get("status"),
        "blocking_findings": details.get("blocking_findings", 0),
        "total_paths": details.get("total_paths"),
        "counts_by_code": details.get("counts_by_code", {}),
        "blocking_counts_by_code": details.get("blocking_counts_by_code", {}),
        "blocking_counts_by_classification": details.get("blocking_counts_by_classification", {}),
        "diagnostic_summary": details.get("diagnostic_summary", {}),
    }


def _closeout_capability_readiness(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    signal = doctor_payload.get("signals", {}).get("capability_readiness", {})
    details = signal.get("details", {})
    profile_gap_count = int(details.get("profile_contract_gap_count") or 0)
    event_gap_count = int(details.get("event_contract_gap_count") or 0)
    return {
        "status": signal.get("state"),
        "summary": signal.get("summary"),
        "profile_contract_status": details.get("profile_contract_status"),
        "profile_contract_gap_count": profile_gap_count,
        "profile_ready_sections": details.get("profile_ready_sections", []),
        "profile_blocked_sections": details.get("profile_blocked_sections", []),
        "event_contract_status": details.get("event_contract_status"),
        "event_contract_gap_count": event_gap_count,
        "event_ready_sections": details.get("event_ready_sections", []),
        "event_blocked_sections": details.get("event_blocked_sections", []),
        "eval_blocker_classes": details.get("eval_blocker_classes", []),
        "eval_blocker_class_count": int(details.get("eval_blocker_class_count") or 0),
        "contract_gap_count": profile_gap_count + event_gap_count,
    }


def _closeout_memory_readiness(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    signal = doctor_payload.get("signals", {}).get("memory_readiness", {})
    details = signal.get("details", {})
    return {
        "status": signal.get("state"),
        "summary": signal.get("summary"),
        "provider_model": details.get("provider_model"),
        "schema_version": details.get("schema_version"),
        "entry_count": int(details.get("entry_count") or 0),
        "total_count": int(details.get("total_count") or 0),
        "available_sources": details.get("available_sources", []),
        "missing_sources": details.get("missing_sources", []),
        "by_source": details.get("by_source", {}),
        "by_freshness": details.get("by_freshness", {}),
        "validation_command": details.get("validation_command"),
    }


def _closeout_package_readiness(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract package readiness information from a doctor payload into a normalized closeout report.

    Parameters:
        doctor_payload (dict[str, Any]): The payload returned by `repo_doctor` (typically `result.data`), expected to contain `signals.package_readiness`.

    Returns:
        dict[str, Any]: A mapping with the following keys:
            - status: The signal state (`"pass"`, `"warning"`, `"block"`, `"skipped"`, etc.).
            - summary: Short human-readable summary of package readiness.
            - target: The package target identifier or path the readiness report refers to.
            - schema_version: Declared package schema/version when present.
            - readiness_level: Contract-readiness classification from the package report.
            - missing_fields: List of contract fields that are missing.
            - missing_field_count: Integer count of missing contract fields (0 when absent).
            - install_ready: Boolean indicating whether the package is installable.
            - promotion_status: Current promotion classification or status string.
            - promotion_ready: Boolean indicating whether the package is ready for promotion.
            - checkout_test_status: Result of any checkout/test performed for the package.
            - blocked_reasons: List of strings explaining why the package is blocked.
            - validation_command: A recommended command string to run package readiness validation.
    """
    signal = doctor_payload.get("signals", {}).get("package_readiness", {})
    details = signal.get("details", {})
    return {
        "status": signal.get("state"),
        "summary": signal.get("summary"),
        "target": details.get("target"),
        "schema_version": details.get("schema_version"),
        "readiness_level": details.get("readiness_level"),
        "missing_fields": details.get("missing_fields", []),
        "missing_field_count": int(details.get("missing_field_count") or 0),
        "install_ready": details.get("install_ready"),
        "promotion_status": details.get("promotion_status"),
        "promotion_ready": details.get("promotion_ready"),
        "checkout_test_status": details.get("checkout_test_status"),
        "blocked_reasons": details.get("blocked_reasons", []),
        "validation_command": details.get("validation_command"),
    }


def _closeout_focused_validation(repo_root: Path, changed_files: list[str]) -> list[dict[str, Any]]:
    """
    Builds a prioritized list of validation commands to run for a focused closeout.

    Includes a core set of readiness checks (doctor, profiles, events, memory, package) and conditionally appends:
    - an SDK handle check when any changed path is within generated surface prefixes,
    - a runtime-evidence schema validation when any changed path points under the repository's runtime evidence root,
    - a scoped `repo validate` invocation when changed files are present, or a `repo status` check when none are present.

    Parameters:
        repo_root (Path): Repository root used to normalize and evaluate runtime-evidence paths.
        changed_files (list[str]): Changed-file paths (absolute or repo-relative) used to determine which conditional checks to include.

    Returns:
        list[dict[str, Any]]: Ordered list of validation command descriptors, each containing `id`, `reason`, and `command`.
    """
    commands = [
        {
            "id": "repo_doctor",
            "reason": "Confirm golden-path health before claiming completion.",
            "command": _repo_validation_command("doctor"),
        },
        {
            "id": "skill_profiles_readiness",
            "reason": "Validate skill operation-profile readiness contracts directly.",
            "command": "./bin/ask skills profiles --json --robot",
        },
        {
            "id": "skill_events_readiness",
            "reason": "Validate skill lifecycle-event readiness contracts directly.",
            "command": "./bin/ask skills events --json --robot",
        },
        {
            "id": "skill_memory_readiness",
            "reason": "Validate searchable skill memory provider evidence directly.",
            "command": "./bin/ask skills memory search projection --json --robot",
        },
        {
            "id": "skill_package_readiness",
            "reason": "Validate version and role-aware package readiness directly.",
            "command": (
                f"./bin/ask skills package {PACKAGE_READINESS_SENTINEL} "
                "--checkout-test --json --robot"
            ),
        }
    ]
    if any(path.startswith(GENERATED_SURFACE_PREFIXES) for path in changed_files):
        commands.append(
            {
                "id": "skill_handles",
                "reason": "Validate SDK handle projection for changed projection files.",
                "command": SDK_HANDLE_CHECK_COMMAND,
            }
        )
    if any(_is_runtime_evidence_path(repo_root, path) for path in changed_files):
        commands.append(
            {
                "id": "runtime_evidence_cards",
                "reason": "Validate changed shared-workspace runtime evidence artifacts.",
                "command": _runtime_evidence_validation_command(repo_root),
            }
        )
    if changed_files:
        commands.append(
            {
                "id": "changed_validation",
                "reason": "Run validation scoped to the files currently changed.",
                "command": _validation_command_for_changed_files(changed_files),
            }
        )
    else:
        commands.append(
            {
                "id": "repo_status",
                "reason": "No changed files were detected; confirm clean repository state.",
                "command": _repo_validation_command("status"),
            }
        )
    return commands


def _runtime_evidence_validation_command(repo_root: Path, card_paths: list[Path] | None = None) -> str:
    """
    Builds the shell command to validate runtime evidence cards for the given repository.

    Parameters:
        repo_root (Path): Repository root used as the workspace root argument in the command; it will be resolved to an absolute path.

    Returns:
        command (str): A single shell command string that invokes validate_runtime_cards.py with the evidence directory, `--require-shared-workspace`, the resolved workspace root, and `--json`. The command tokens are shell-quoted where appropriate.
    """
    validator_path = RUNTIME_EVIDENCE_VALIDATOR
    if not (repo_root / validator_path).exists():
        validator_path = Path(__file__).resolve().parents[4] / "scripts" / "validation-and-linting" / "validate_runtime_cards.py"
    parts = ["python3", str(validator_path)]
    if card_paths:
        for card_path in card_paths:
            try:
                parts.append(str(card_path.relative_to(repo_root)))
            except ValueError:
                parts.append(str(card_path))
    else:
        parts.extend(["--evidence-dir", RUNTIME_EVIDENCE_ROOT])
    parts.extend(["--require-shared-workspace", "--workspace-root", str(repo_root.resolve()), "--json"])
    return " ".join(shlex.quote(part) for part in parts)


def _runtime_evidence_schema_validation(repo_root: Path, card_paths: list[Path]) -> dict[str, Any]:
    command = _runtime_evidence_validation_command(repo_root, card_paths)
    existing_cards = [path for path in card_paths if path.exists() and not path.is_symlink()]
    if not existing_cards:
        return {
            "status": "not_run",
            "command": command,
            "reason": "No existing changed RuntimeCard files to schema-validate.",
        }
    try:
        process = subprocess.run(
            shlex.split(command),
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "status": "fail",
            "command": command,
            "returncode": None,
            "findings": [],
            "checked": [],
            "stderr": f"Runtime evidence validator could not complete: {exc}",
        }
    try:
        payload = json.loads(process.stdout) if process.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": process.stdout}
    return {
        "status": "pass" if process.returncode == 0 else "fail",
        "command": command,
        "returncode": process.returncode,
        "findings": payload.get("findings", []) if isinstance(payload, dict) else [],
        "checked": payload.get("checked", []) if isinstance(payload, dict) else [],
        "stderr": process.stderr.strip(),
    }


def _normalize_changed_path(repo_root: Path, path: str) -> str:
    """
    Normalize a changed-file path to a repository-relative POSIX path when possible.

    Parameters:
        repo_root (Path): Repository root used to compute a relative path.
        path (str): File path to normalize; may be absolute or relative.

    Returns:
        str: If `path` is inside `repo_root`, a repository-relative POSIX path is returned.
             If `path` is an absolute path not under `repo_root`, the original absolute path string is returned.
             For relative inputs, a leading "./" is removed if present.
    """
    path_obj = Path(path)
    if path_obj.is_absolute():
        try:
            return path_obj.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return str(path_obj)
    return path.removeprefix("./")


def _is_runtime_evidence_path(repo_root: Path, path: str) -> bool:
    """
    Determine whether a changed-file path falls under the runtime evidence root.

    Parameters:
        repo_root (Path): Repository root used to normalize absolute paths.
        path (str): Changed-file path (absolute or relative) to normalize and test.

    Returns:
        True if the normalized repo-relative path starts with '.harness/evidence/runtime-proof/', False otherwise.
    """
    return _normalize_changed_path(repo_root, path).startswith(RUNTIME_EVIDENCE_ROOT + "/")


def _changed_runtime_card_paths(repo_root: Path, changed_files: list[str]) -> list[Path]:
    """
    Return the list of runtime-card.json file paths that are affected by a set of changed files under the runtime evidence root.

    Parameters:
        repo_root (Path): Repository root used to resolve relative changed-file paths.
        changed_files (list[str]): Changed file paths (absolute or relative) to inspect.

    Returns:
        list[Path]: Sorted, unique Paths for changed files whose normalized repo-relative path starts with
        RUNTIME_EVIDENCE_ROOT + "/" and ends with "/runtime-card.json".
    """
    paths = []
    for changed_file in changed_files:
        normalized = _normalize_changed_path(repo_root, changed_file)
        if normalized.startswith(RUNTIME_EVIDENCE_ROOT + "/") and normalized.endswith("/runtime-card.json"):
            paths.append(repo_root / normalized)
    return sorted(set(paths))


def _runtime_card_summary(repo_root: Path, path: Path) -> dict[str, Any]:
    """
    Summarizes a runtime-card.json file located under the repository root.

    Reads and parses the JSON file at `path` (relative to `repo_root`) and classifies its read status. Handles these cases:
    - If `path` is a symlink: marks the card as invalid with an explanatory error.
    - If the file cannot be read because it no longer exists: marks the card as deleted.
    - If the file cannot be read for other I/O reasons or contains invalid JSON or is not a JSON object: marks the card as invalid and includes an error message.
    - Otherwise extracts common card fields and counts `evidence_receipts`.

    Parameters:
        repo_root (Path): Repository root used to produce a repo-relative `path` string in the summary.
        path (Path): Absolute or resolved path to a runtime-card.json file.

    Returns:
        dict: A summary dictionary containing at least:
            - "path" (str): Repo-relative path to the file.
            - "read_status" (str): One of "readable", "deleted", or "invalid".
            - If "invalid" or "deleted": may include "error" (str) with a human-readable message.
            - If "readable": may include the extracted card fields:
                - "card_id"
                - "created_at"
                - "skill_handle"
                - "sdk_skill_name"
                - "runtime_target"
                - "runtime_status"
                - "workspace_root"
                - "receipt_count" (int): number of items in `evidence_receipts` when present.
    """
    relative_path = str(path.relative_to(repo_root))
    if path.is_symlink():
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": "RuntimeCard path must not be a symlink.",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        if not path.exists():
            return {
                "path": relative_path,
                "read_status": "deleted",
                "error": "RuntimeCard path no longer exists.",
            }
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": f"RuntimeCard read failed: {exc}",
        }
    except json.JSONDecodeError as exc:
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": f"invalid JSON: {exc}",
        }
    if not isinstance(payload, dict):
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": "RuntimeCard payload is not a JSON object.",
        }
    receipts = payload.get("evidence_receipts")
    receipt_count = len(receipts) if isinstance(receipts, list) else 0
    return {
        "path": relative_path,
        "read_status": "readable",
        "card_id": payload.get("card_id"),
        "created_at": payload.get("created_at"),
        "skill_handle": payload.get("skill_handle"),
        "sdk_skill_name": payload.get("sdk_skill_name") or payload.get("skill_handle"),
        "runtime_target": payload.get("runtime_target"),
        "runtime_status": payload.get("runtime_status"),
        "workspace_root": payload.get("workspace_root"),
        "receipt_count": receipt_count,
    }


def _runtime_card_scope_summary(runtime_cards: list[dict[str, Any]], *, empty_status: str) -> dict[str, Any]:
    """
    Builds an aggregate summary of a collection of runtime card summaries and classifies their overall scope status.

    Parameters:
        runtime_cards (list[dict[str, Any]]): Per-card summaries each containing at least a `read_status` key.
        empty_status (str): Status to use when `runtime_cards` is empty.

    Returns:
        dict[str, Any]: Summary containing:
            - `status` (str): One of `empty_status` (when no cards), `invalid` (any card not `readable` or `deleted`), `deleted` (all cards are `deleted`), or `present` (at least one readable card).
            - `runtime_card_count` (int): Total number of cards examined.
            - `invalid_runtime_card_count` (int): Number of cards whose `read_status` is neither `readable` nor `deleted`.
            - `deleted_runtime_card_count` (int): Number of cards with `read_status == "deleted"`.
            - `runtime_cards` (list[dict[str, Any]]): The original list of card summaries.
    """
    invalid_cards = [
        card for card in runtime_cards if card.get("read_status") not in {"readable", "deleted"}
    ]
    deleted_cards = [card for card in runtime_cards if card.get("read_status") == "deleted"]
    status = empty_status
    if runtime_cards:
        if invalid_cards:
            status = "invalid"
        elif len(deleted_cards) == len(runtime_cards):
            status = "deleted"
        else:
            status = "present"
    return {
        "status": status,
        "runtime_card_count": len(runtime_cards),
        "invalid_runtime_card_count": len(invalid_cards),
        "deleted_runtime_card_count": len(deleted_cards),
        "runtime_cards": runtime_cards,
    }


def _closeout_runtime_evidence(repo_root: Path, *, include_cards: bool, changed_files: list[str]) -> dict[str, Any]:
    """
    Summarize runtime-evidence ("runtime-card.json") files for closeout and optionally report only the changed subset.

    Parameters:
        repo_root (Path): Repository root used to locate the runtime evidence directory.
        include_cards (bool): When True, discover and summarize runtime-card files; when False, skip discovery and return a skipped report.
        changed_files (list[str]): List of changed paths used to determine the changed-scope subset.

    Returns:
        dict: A closeout report containing:
            - status (str): One of "present", "invalid", "deleted", "not_applicable", or "skipped" describing the changed-scope outcome.
            - evidence_root (str): Relative evidence root path constant used for discovery.
            - runtime_card_count (int): Number of runtime cards in the reported (changed) scope.
            - invalid_runtime_card_count (int): Number of runtime cards in the reported scope with invalid read/parse status.
            - deleted_runtime_card_count (int): Number of runtime cards in the reported scope marked deleted.
            - runtime_cards (list[dict]): List of per-card summaries for the reported (changed) scope.
            - changed_scope (dict): Scope summary for changed cards (counts, status, and the `runtime_cards` list).
            - workspace_scope (dict): Scope summary for all workspace cards discovered under the evidence root.
            - schema_validation (dict): Contains `status` ("not_run") and the `command` string to validate runtime card schema.
            - truth_boundaries (dict): Indicators describing which proofs are considered by closeout (e.g., command_proof, schema_proof, pr_truth, tracker_truth, docs_truth).
    """
    evidence_root = repo_root / RUNTIME_EVIDENCE_ROOT
    validation_command = _runtime_evidence_validation_command(repo_root)
    if not include_cards:
        skipped_scope = _runtime_card_scope_summary([], empty_status="skipped")
        return {
            "status": "skipped",
            "reason": "Runtime evidence discovery runs only for changed closeout.",
            "evidence_root": RUNTIME_EVIDENCE_ROOT,
            "runtime_card_count": 0,
            "invalid_runtime_card_count": 0,
            "deleted_runtime_card_count": 0,
            "runtime_cards": [],
            "changed_scope": skipped_scope,
            "workspace_scope": skipped_scope,
            "schema_validation": {
                "status": "not_run",
                "command": validation_command,
            },
            "truth_boundaries": {
                "command_proof": "not_checked_by_repo_closeout",
                "schema_proof": "not_run_by_closeout_use_schema_validation_command",
                "pr_truth": "not_checked_by_repo_closeout",
                "tracker_truth": "not_checked_by_repo_closeout",
                "docs_truth": "not_checked_by_repo_closeout",
            },
        }
    workspace_cards = (
        [_runtime_card_summary(repo_root, path) for path in sorted(evidence_root.rglob("runtime-card.json"))]
        if evidence_root.exists()
        else []
    )
    changed_card_paths = _changed_runtime_card_paths(repo_root, changed_files)
    changed_cards = [_runtime_card_summary(repo_root, path) for path in changed_card_paths]
    changed_scope = _runtime_card_scope_summary(changed_cards, empty_status="not_applicable")
    schema_validation = _runtime_evidence_schema_validation(repo_root, changed_card_paths)
    if changed_scope["status"] == "present" and schema_validation["status"] == "fail":
        changed_scope = {
            **changed_scope,
            "status": "invalid",
            "invalid_runtime_card_count": changed_scope["runtime_card_count"],
        }
    workspace_scope = _runtime_card_scope_summary(workspace_cards, empty_status="missing")
    return {
        "status": changed_scope["status"],
        "evidence_root": RUNTIME_EVIDENCE_ROOT,
        "runtime_card_count": changed_scope["runtime_card_count"],
        "invalid_runtime_card_count": changed_scope["invalid_runtime_card_count"],
        "deleted_runtime_card_count": changed_scope["deleted_runtime_card_count"],
        "runtime_cards": changed_scope["runtime_cards"],
        "changed_scope": changed_scope,
        "workspace_scope": workspace_scope,
        "schema_validation": schema_validation,
        "truth_boundaries": {
            "command_proof": "workspace_runtime_evidence",
            "schema_proof": "checked_by_repo_closeout" if schema_validation["status"] in {"pass", "fail"} else "not_run_by_closeout_use_schema_validation_command",
            "pr_truth": "not_checked_by_repo_closeout",
            "tracker_truth": "not_checked_by_repo_closeout",
            "docs_truth": "not_checked_by_repo_closeout",
        },
    }


def _diagnostic_debt_next_command(diagnostic_debt: list[dict[str, Any]]) -> str | None:
    """
    Select the first non-empty `next_command` from a diagnostic-debt list.

    Parameters:
        diagnostic_debt (list[dict[str, Any]]): Ordered diagnostic-debt entries; each entry may include a `next_command` string.

    Returns:
        str | None: The first `next_command` that is a non-empty string, or `None` if none are present.
    """
    for debt in diagnostic_debt:
        next_command = debt.get("next_command") if isinstance(debt, dict) else None
        if isinstance(next_command, str) and next_command.strip():
            return next_command
    return None


@dataclass(frozen=True)
class RepoCloseoutOptions:
    """Explicit switches for closeout readiness collection."""

    changed: bool = False
    strict: bool = False


def _coerce_repo_closeout_options(
    options: RepoCloseoutOptions | None,
    legacy_options: dict[str, object],
) -> RepoCloseoutOptions:
    """Accept explicit options while retaining the established keyword callers."""
    if options is not None:
        if not isinstance(options, RepoCloseoutOptions):
            raise TypeError("repo_closeout options must be RepoCloseoutOptions")
        if legacy_options:
            names = ", ".join(sorted(legacy_options))
            raise TypeError(f"RepoCloseoutOptions does not accept legacy options: {names}")
        return options
    allowed = set(RepoCloseoutOptions.__dataclass_fields__)
    unexpected = set(legacy_options) - allowed
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TypeError(f"repo_closeout received unexpected option(s): {names}")
    return RepoCloseoutOptions(**legacy_options)


def _closeout_changed_files(repo_root: Path, changed: bool) -> tuple[list[str], str | None]:
    if not changed:
        return [], None
    try:
        return collect_changed_files(repo_root), None
    except RuntimeError as exc:
        return [], str(exc)


def _closeout_blockers(
    doctor_payload: dict[str, Any], sync_report: dict[str, Any], diagnostic_debt: list[dict[str, Any]],
    runtime_evidence: dict[str, Any], changed_files_error: str | None, strict: bool,
) -> list[str]:
    blockers = [
        name for name, active in (
            ("changed_file_detection_failed", bool(changed_files_error)),
            ("repo_doctor_blocking", bool(doctor_payload.get("blocking"))),
            ("sync_required", bool(sync_report["needed"])),
            ("strict_diagnostic_debt", strict and bool(diagnostic_debt)),
        ) if active
    ]
    runtime_status = runtime_evidence.get("changed_scope", {}).get("status")
    if runtime_status in {"invalid", "deleted"}:
        blockers.append(f"runtime_evidence_{runtime_status}")
    return blockers


def _closeout_next_command(
    doctor_payload: dict[str, Any], sync_report: dict[str, Any], diagnostic_debt: list[dict[str, Any]],
    runtime_evidence: dict[str, Any], changed_files: list[str], changed_files_error: str | None, strict: bool,
) -> str:
    if changed_files_error:
        return _repo_validation_command("status")
    if doctor_payload.get("blocking"):
        return doctor_payload.get("next_command") or _repo_validation_command("doctor")
    if sync_report["needed"]:
        return sync_report["commands"][0]
    if strict and diagnostic_debt:
        return _diagnostic_debt_next_command(diagnostic_debt) or doctor_payload.get("next_command") or _repo_validation_command("doctor")
    if runtime_evidence.get("changed_scope", {}).get("status") in {"invalid", "deleted"}:
        return runtime_evidence["schema_validation"]["command"]
    if sync_report["validation_commands"]:
        return sync_report["validation_commands"][0]
    return _validation_command_for_changed_files(changed_files) if changed_files else _repo_validation_command("status")


def _closeout_payload(
    doctor_payload: dict[str, Any], changed_files: list[str], changed_files_error: str | None,
    sync_report: dict[str, Any], runtime_evidence: dict[str, Any], diagnostic_debt: list[dict[str, Any]],
    focused_validation: list[str], blockers: list[str], changed: bool, strict: bool, next_command: str,
) -> dict[str, Any]:
    ready = not blockers
    return {
        "agent_summary": "Ready: no closeout blockers detected." if ready else f"Blocked: closeout has {len(blockers)} blocker(s).",
        "changed_files": changed_files, "changed_file_count": len(changed_files), "changed_mode_requested": changed,
        "changed_files_error": changed_files_error, "sync": sync_report,
        "runtime_budget": _closeout_runtime_budget(doctor_payload),
        "capability_readiness": _closeout_capability_readiness(doctor_payload),
        "memory_readiness": _closeout_memory_readiness(doctor_payload),
        "package_readiness": _closeout_package_readiness(doctor_payload), "surface_policy": _closeout_surface_policy(doctor_payload),
        "runtime_evidence": runtime_evidence, "focused_validation": focused_validation,
        "diagnostic_debt": diagnostic_debt, "commit_readiness": {"ready": ready, "blockers": blockers, "strict": strict},
        "doctor": doctor_payload, "next_command": next_command,
    }


def repo_closeout(repo_root: Path, options: RepoCloseoutOptions | None = None, **legacy_options: object) -> CallResult:
    """Build a closeout readiness report for the selected repository scope."""
    selected = _coerce_repo_closeout_options(options, legacy_options)
    result = CallResult()
    doctor_payload = repo_doctor(repo_root).data.get("doctor", {})
    changed_files, changed_files_error = _closeout_changed_files(repo_root, selected.changed)
    sync_report = _closeout_sync_report(changed_files)
    diagnostic_debt = doctor_payload.get("diagnostic_debt", [])
    runtime_evidence = _closeout_runtime_evidence(repo_root, include_cards=selected.changed, changed_files=changed_files)
    blockers = _closeout_blockers(doctor_payload, sync_report, diagnostic_debt, runtime_evidence, changed_files_error, selected.strict)
    next_command = _closeout_next_command(doctor_payload, sync_report, diagnostic_debt, runtime_evidence, changed_files, changed_files_error, selected.strict)
    payload = _closeout_payload(doctor_payload, changed_files, changed_files_error, sync_report, runtime_evidence, diagnostic_debt, _closeout_focused_validation(repo_root, changed_files), blockers, selected.changed, selected.strict, next_command)
    result.data["repo_closeout"] = payload
    result.data.update(payload)
    result.status = "success" if not blockers else "error"
    if blockers:
        result.errors.append(ErrorObject(code=ErrorCode.ERR_VALIDATION, message=payload["agent_summary"], fix_suggestion=next_command))
    return result
__all__ = [name for name in globals() if not name.startswith("__")]
