from __future__ import annotations

from .skills_impl_install_improve import *  # noqa: F403

def _fallback_improvement_candidate(repo_root: Path, goal_text: str) -> dict[str, Any] | None:
    """Select one SDK skill handle when formal goal routing is too ambiguous."""
    request_tokens = _improve_tokens(goal_text)
    if not request_tokens:
        return None
    try:
        handles = [record.to_resolution() for record in build_sdk_skill_records(repo_root_path=repo_root, visibility="advanced")]
    except (OSError, RuntimeError, ValueError, KeyError, TypeError):
        return None
    handle_rows = {
        str(row.get("handle") or "").strip().lower().lstrip("$"): row
        for row in handles
        if isinstance(row, dict) and row.get("handle")
    }
    for required_tokens, hinted_handle, rationale in _IMPROVE_HANDLE_HINTS:
        normalized_hint = hinted_handle.strip().lower().lstrip("$")
        row = handle_rows.get(normalized_hint)
        if required_tokens.issubset(request_tokens) and row:
            return {
                "candidate_id": f"skill:{row.get('handle')}::{row.get('source_path')}",
                "candidate_type": row.get("kind", "skill"),
                "name": row.get("handle"),
                "path": row.get("source_path"),
                "confidence": 0.85,
                "rationale": [
                    rationale,
                    "matched terms=" + ",".join(sorted(required_tokens)),
                ],
                "scope_rank": 2,
            }
    scored: list[tuple[int, str, dict[str, Any], set[str]]] = []
    for row in handles:
        if not isinstance(row, dict):
            continue
        handle = str(row.get("handle") or "")
        searchable = " ".join(
            str(row.get(key) or "")
            for key in ("handle", "owner", "source_path", "description")
        )
        overlap = request_tokens & _improve_tokens(searchable)
        if overlap:
            scored.append((len(overlap), handle, row, overlap))
    if not scored:
        return None
    score, handle, row, overlap = max(scored, key=lambda item: (item[0], -len(item[1]), item[1]))
    normalized_handle = handle.strip().lower().lstrip("$")
    if score < 2 and normalized_handle not in request_tokens:
        return None
    return {
        "candidate_id": f"skill:{row.get('handle')}::{row.get('source_path')}",
        "candidate_type": row.get("kind", "skill"),
        "name": row.get("handle"),
        "path": row.get("source_path"),
        "confidence": round(min(0.95, 0.45 + (score * 0.1)), 2),
        "rationale": [
            "fallback SDK skill description match",
            "matched terms=" + ",".join(sorted(overlap)),
        ],
        "scope_rank": 2,
    }


def _improvement_route_state(route_decision_status: str | None, *, proof_failed: bool = False) -> tuple[str, str]:
    """Return the stable agent-facing route state for a skills improvement result."""
    if proof_failed:
        return "blocked_reachability", "selected capability failed reachability proof"
    if route_decision_status == "resolved":
        return "resolved", "goal routing selected one reachable capability"
    if route_decision_status == "unresolved_ambiguity":
        return "blocked_ambiguity", "goal routing could not select one capability"
    if route_decision_status in {"blocked_policy_drift", "blocked_catalog_parity", "degraded_no_candidates"}:
        return "blocked_dependency", f"goal routing returned {route_decision_status}"
    return "blocked_dependency", "goal routing did not produce a usable decision"


def _proof_missing_workspace_source(proof: dict[str, Any]) -> bool:
    if not isinstance(proof, dict):
        return False
    gates = proof.get("gates")
    if not isinstance(gates, dict):
        return False
    return gates.get("resolver") is False or gates.get("canonical_source_exists") is False


def improve_skills(
    repo_root: Path,
    goal_text: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """Route a user goal into one capability recommendation with proof status."""
    result = CallResult()
    result.metadata["command"] = "skills improve"
    goal_result = goal_skills(
        repo_root,
        intent_text=goal_text,
        top_k=top_k,
        considered_limit=considered_limit,
    )
    goal_decision = goal_result.data.get("goal_decision", {})
    route_decision_status = goal_result.data.get("route_decision_status")
    recommended = goal_decision.get("recommended_candidate")
    initial_route_state, initial_route_state_reason = _improvement_route_state(route_decision_status)

    improvement: dict[str, Any] = {
        "schema_version": "skill-improvement-recommendation.v1",
        "goal": goal_text,
        "status": "resolved" if goal_result.status == "success" and recommended else "blocked",
        "route_state": initial_route_state,
        "route_state_reason": initial_route_state_reason,
        "agent_summary": "",
        "recommended_capability": None,
        "why": [],
        "reachability": {
            "status": "not_checked",
            "proof_status": None,
            "required_gates_passed": None,
            "user_runtime_ready": None,
        },
        "proof": None,
        "alternatives": goal_decision.get("alternative_candidates", []),
        "next_command": None,
        "validation_commands": [_skills_validation_command("goal", goal_text)],
        "goal_decision_status": goal_decision.get("decision_status"),
        "goal_decision": goal_decision,
    }

    fallback_used = False
    fallback_allowed = route_decision_status == "unresolved_ambiguity"
    if not isinstance(recommended, dict) and fallback_allowed:
        recommended = _fallback_improvement_candidate(repo_root, goal_text)
        fallback_used = recommended is not None

    if not isinstance(recommended, dict):
        prompts = goal_decision.get("disambiguation_prompts") or []
        summary = goal_decision.get("operator_action") or "Goal did not resolve to one capability."
        improvement["agent_summary"] = summary
        improvement["disambiguation_prompts"] = prompts
        improvement["next_command"] = _skills_validation_command("goal", goal_text)
        improvement["validation_commands"] = [improvement["next_command"]]
        result.status = "error"
        result.data["improvement"] = improvement
        result.data["goal_decision"] = goal_decision
        result.errors.extend(goal_result.errors)
        if not result.errors:
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="skills improve could not resolve one recommended capability.",
                    fix_suggestion=summary,
                )
            )
        return result

    handle = _candidate_handle(recommended)
    proof_result = skills_proof(repo_root, handle=handle) if handle else CallResult(status="error")
    proof = proof_result.data.get("proof", {})
    gates = proof.get("gates", {}) if isinstance(proof, dict) else {}
    required = proof.get("gate_policy", {}).get("required", []) if isinstance(proof, dict) else []
    required_gates_passed = all(bool(gates.get(gate)) for gate in required)
    user_runtime_ready = bool(
        gates.get("user_runtime_ready")
    )
    rationale = recommended.get("rationale") or []
    capability = {
        "handle": handle,
        "name": recommended.get("name"),
        "path": recommended.get("path"),
        "candidate_id": recommended.get("candidate_id"),
        "candidate_type": recommended.get("candidate_type"),
        "confidence": recommended.get("confidence"),
    }

    improvement["recommended_capability"] = capability
    improvement["why"] = rationale
    if fallback_used:
        improvement["status"] = "resolved_with_fallback"
        improvement["route_state"] = "resolved_with_fallback"
        improvement["route_state_reason"] = "fallback SDK description match selected one reachable capability"
    improvement["reachability"] = {
        "status": "pass" if proof_result.status == "success" else "fail",
        "proof_status": proof.get("status") if isinstance(proof, dict) else "fail",
        "required_gates_passed": required_gates_passed,
        "user_runtime_ready": user_runtime_ready,
    }
    improvement["proof"] = proof
    improvement["agent_summary"] = (
        f"Recommended {handle} for this goal."
        if proof_result.status == "success"
        else f"Recommended {handle}, but reachability proof failed."
    )
    improvement["next_command"] = _skills_validation_command("proof", handle)
    improvement["validation_commands"] = [improvement["next_command"]]

    result.data["improvement"] = improvement
    result.data["goal_decision"] = goal_decision
    if proof_result.status == "success":
        return result

    proof_has_gates = isinstance(gates, dict) and bool(gates)
    fallback_after_unreachable_route = (
        not fallback_used
        and route_decision_status == "resolved"
        and proof_has_gates
        and _proof_missing_workspace_source(proof)
    )
    if fallback_after_unreachable_route:
        fallback = _fallback_improvement_candidate(repo_root, goal_text)
        fallback_handle = _candidate_handle(fallback or {})
        if fallback and fallback_handle and fallback_handle != handle:
            fallback_proof_result = skills_proof(repo_root, handle=fallback_handle)
            fallback_proof = fallback_proof_result.data.get("proof", {})
            improvement["fallback_attempt"] = {
                "handle": fallback_handle,
                "accepted": fallback_proof_result.status == "success",
                "proof_status": fallback_proof.get("status") if isinstance(fallback_proof, dict) else None,
            }
            if fallback_proof_result.status == "success":
                fallback_gates = fallback_proof.get("gates", {}) if isinstance(fallback_proof, dict) else {}
                fallback_required = (
                    fallback_proof.get("gate_policy", {}).get("required", [])
                    if isinstance(fallback_proof, dict)
                    else []
                )
                fallback_required_gates_passed = all(bool(fallback_gates.get(gate)) for gate in fallback_required)
                fallback_user_runtime_ready = bool(fallback_gates.get("user_runtime_ready"))
                improvement["status"] = "resolved_with_fallback"
                improvement["route_state"] = "resolved_with_fallback"
                improvement["route_state_reason"] = (
                    "fallback SDK description match replaced an unreachable routed capability"
                )
                improvement["recommended_capability"] = {
                    "handle": fallback_handle,
                    "name": fallback.get("name"),
                    "path": fallback.get("path"),
                    "candidate_id": fallback.get("candidate_id"),
                    "candidate_type": fallback.get("candidate_type"),
                    "confidence": fallback.get("confidence"),
                }
                improvement["why"] = [
                    *list(fallback.get("rationale") or []),
                    f"initial routed capability unreachable={handle}",
                ]
                improvement["reachability"] = {
                    "status": "pass",
                    "proof_status": fallback_proof.get("status") if isinstance(fallback_proof, dict) else "pass",
                    "required_gates_passed": fallback_required_gates_passed,
                    "user_runtime_ready": fallback_user_runtime_ready,
                }
                improvement["proof"] = fallback_proof
                improvement["agent_summary"] = (
                    f"Recommended {fallback_handle} after routed {handle} failed reachability."
                )
                improvement["next_command"] = _skills_validation_command("proof", fallback_handle)
                improvement["validation_commands"] = [improvement["next_command"]]
                return result
    improvement["status"] = "blocked"
    improvement["route_state"], improvement["route_state_reason"] = _improvement_route_state(
        route_decision_status,
        proof_failed=True,
    )
    result.status = "error"
    result.errors.extend(proof_result.errors)
    if not result.errors:
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"skills improve selected '{handle}', but reachability proof failed.",
                fix_suggestion=improvement["next_command"],
            )
        )
    return result


def _create_symlink(source: Path, target: Path, dry_run: bool = False, *, replace_existing: bool = False) -> str:
    """
    Create or update a filesystem symbolic link at `target` that points to `source`.

    Ensures `target.parent` exists before creating the link. Existing non-symlink paths are preserved by default so user-owned directories like `~/plugins` are not deleted during relink.

    Parameters:
        source (Path): Destination path that the symlink should reference.
        target (Path): Filesystem path where the symlink will be created or updated.
        dry_run (bool): If True, do not perform filesystem mutations; only simulate the action.
        replace_existing (bool): If True, replace an existing non-symlink target before creating the symlink.

    Returns:
        action (str): Human-readable summary, e.g. "Created symlink: <target> -> <source>", "Updated symlink: <target> -> <source>", or "Skipped existing non-symlink path: <target>".
    """
    if target.is_symlink() and target.readlink() == source:
        return f"Symlink already current: {target} -> {source}"
    if target.exists() and not target.is_symlink() and not replace_existing:
        return f"Skipped existing non-symlink path: {target}"
    action = "Created" if not target.exists() else "Updated"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.symlink_to(source)
    return f"{action} symlink: {target} -> {source}"

def _prune_first_level_symlinks(target_dir: Path, keep_names: set[str], dry_run: bool = False) -> list[str]:
    """
    Remove stale first-level symlinks in target_dir while preserving regular files, directories, hidden names, and any names listed in keep_names.

    Parameters:
        target_dir (Path): Directory whose immediate entries will be inspected.
        keep_names (set[str]): Entry names to skip (preserve) even if they are symlinks.
        dry_run (bool): If true, do not modify the filesystem; only report planned removals.

    Returns:
        list[str]: Log lines describing each removed (or planned-to-remove when dry_run) symlink in the form "Removed stale symlink: <path> -> <target>".
    """
    logs: list[str] = []
    if not target_dir.exists():
        return logs
    for item in sorted(target_dir.iterdir()):
        # Preserve hidden control links (for example ".system") and managed links.
        if not item.is_symlink() or item.name in keep_names or item.name.startswith("."):
            continue
        logs.append(f"Removed stale symlink: {item} -> {os.readlink(item)}")
        if not dry_run:
            item.unlink()
    return logs

def _find_symlink_entries(source: Path) -> list[Path]:
    """
    Find symlinked filesystem entries at or below the given source path.

    If `source` is a symlink, returns a list containing only `source`. If `source`
    does not exist or is not a directory, returns an empty list. Otherwise walks
    the directory tree (without following symlinks) and returns any symlink paths
    found. Top-level traversal skips the `.git`, `node_modules`, and `__pycache__`
    subdirectories.

    Parameters:
        source (Path): Directory or path to inspect for symlink entries.

    Returns:
        list[Path]: A list of Path objects pointing to symlink entries; may be empty.
    """
    symlinks: list[Path] = []
    if source.is_symlink():
        symlinks.append(source)
        return symlinks
    if not source.exists() or not source.is_dir():
        return symlinks

    for root, dirs, files in os.walk(source, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for name in dirs + files:
            candidate = Path(root) / name
            if candidate.is_symlink():
                symlinks.append(candidate)
    return symlinks

def _sync_dir_copy(source: Path, target: Path, dry_run: bool = False) -> str:
    """
    Copy-sync a directory tree into a target directory while disallowing any symlinks in the source.

    Skips top-level entries named ".git", "node_modules", and "__pycache__". If any symlink is present anywhere under the source, raises ValueError. When not a dry run, ensures the target directory exists, replaces existing directories at the destination with fresh copies, and copies files preserving file metadata.

    Parameters:
        source (Path): Source directory to copy from. Must not contain symlinks.
        target (Path): Destination directory to copy into; will be created if missing.
        dry_run (bool): If True, perform no filesystem changes and only simulate the action.

    Returns:
        str: A human-readable message describing the completed sync and the target path.
    """
    symlink_entries = _find_symlink_entries(source)
    if symlink_entries:
        rel = symlink_entries[0]
        rel_text = str(rel.relative_to(source)) if rel != source else "."
        raise ValueError(f"Symlinks are not allowed in sync source: {source} (first: {rel_text})")

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            if item.name in ('.git', 'node_modules', '__pycache__'):
                continue
            dest = target / item.name
            if item.is_symlink():
                raise ValueError(f"Symlink entries are not allowed in sync source: {item}")
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                # Preserve symlink objects defensively if one appears mid-copy.
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest, follow_symlinks=False)
    return f"Synced directory: {target} (copy)"


def _refresh_system_lane_link(
    skills_dir: Path,
    system_skills_dir: Path,
    dry_run: bool = False,
) -> list[str]:
    """
    Preserve or create the reserved `.system` symlink in the skills lane when a managed system store exists.

    Parameters:
        skills_dir (Path): Path to the repository skills directory where `.system` should exist.
        system_skills_dir (Path): Path to the managed system skills store; if not a directory, no action is taken.
        dry_run (bool): If true, no filesystem changes are made; actions are returned as planned-log strings.

    Returns:
        list[str]: Log lines describing the action taken (created/updated) or skipped; empty list if no managed system store is present.
    """
    if not system_skills_dir.is_dir():
        return []

    target_link = skills_dir / ".system"
    if target_link.exists() and not target_link.is_symlink():
        return [f"Skipped existing non-symlink system lane: {target_link}"]

    return [_create_symlink(Path("../../skills-system"), target_link, dry_run)]


def _is_generated_root_skill_dir(path: Path) -> bool:
    """Return whether a first-level runtime directory was generated by rooted projection."""
    skill_md = path / "SKILL.md"
    if not path.is_dir() or path.is_symlink() or not skill_md.is_file():
        return False
    try:
        head = skill_md.read_text(encoding="utf-8", errors="ignore")[:600]
    except OSError:
        return False
    return "skill-type: root-skill-set" in head and "projection-mode: rooted" in head


def _prune_generated_root_skill_dirs(
    target_dir: Path,
    keep_names: set[str],
    *,
    dry_run: bool = False,
    preserve_keep_names: bool = True,
) -> list[str]:
    """Remove generated rooted runtime directories that do not belong to the requested projection."""
    logs: list[str] = []
    if not target_dir.exists():
        return logs
    for item in sorted(target_dir.iterdir()):
        if item.name.startswith(".") or (preserve_keep_names and item.name in keep_names):
            continue
        if not _is_generated_root_skill_dir(item):
            continue
        logs.append(f"Removed generated root skill set: {item}")
        if not dry_run:
            shutil.rmtree(item)
    return logs


def _generated_root_skill_dir_names(target_dir: Path) -> list[str]:
    """Return generated rooted projection entries still present in the flat runtime lane."""
    if not target_dir.exists():
        return []
    return sorted(item.name for item in target_dir.iterdir() if _is_generated_root_skill_dir(item))


SYSTEM_BRIDGE_ALIAS_MARKER = ".agent-skills-system-bridge-alias.json"


def _is_generated_system_bridge_alias(item: Path, system_source: Path) -> bool:
    if item.is_symlink():
        raw_target = Path(os.readlink(item))
        if raw_target == Path(".system") / item.name or raw_target.parts[-2:] == (".system", item.name):
            return True
        try:
            return item.resolve(strict=True) == system_source.resolve(strict=True)
        except OSError:
            return False

    marker = (
        item / SYSTEM_BRIDGE_ALIAS_MARKER
        if item.is_dir()
        else item.parent / f".{item.name}-{SYSTEM_BRIDGE_ALIAS_MARKER}"
    )
    if not marker.is_file():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if payload.get("kind") != "system_bridge_alias":
        return False
    try:
        target = system_source.parent / str(payload.get("target", ""))
        return target.resolve(strict=True) == system_source.resolve(strict=True)
    except OSError:
        return False


def _prune_first_level_system_bridge_aliases(
    target_dir: Path,
    system_skills_dir: Path,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Remove stale first-level aliases for skills that belong in the hidden system lane."""
    logs: list[str] = []
    if not target_dir.exists() or not system_skills_dir.is_dir():
        return logs

    for bridge_skill in sorted(SYSTEM_BRIDGE_SKILL_NAMES):
        item = target_dir / bridge_skill
        system_source = system_skills_dir / bridge_skill
        if not (item.exists() or item.is_symlink()):
            continue
        if not (system_source / "SKILL.md").exists():
            continue

        if not _is_generated_system_bridge_alias(item, system_source):
            logs.append(f"Skipped first-level system bridge alias without generated provenance: {item}")
            continue

        logs.append(f"Removed first-level system bridge alias: {item}")
        if dry_run:
            continue
        if item.is_symlink() or item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)
    return logs


def _is_system_bridge_entry(entry: Any, system_skills_dir: Path) -> bool:
    """Return whether a discovered entry is owned by the hidden system lane."""
    if entry.name not in SYSTEM_BRIDGE_SKILL_NAMES:
        return False
    try:
        entry_source = entry.source_dir.resolve(strict=False)
        system_root = system_skills_dir.resolve(strict=False)
        entry_source.relative_to(system_root)
    except (OSError, ValueError):
        return False
    return True


def _public_root_report(report: dict) -> dict:
    return {
        **report,
        "roots": [
            {key: value for key, value in root.items() if key != "content"}
            for root in report.get("roots", [])
        ],
    }


def _public_manifest_report(report: dict) -> dict:
    return {
        **report,
        "manifests": [
            {key: value for key, value in manifest.items() if key != "rows"}
            for manifest in report.get("manifests", [])
        ],
    }


def _append_user_runtime_relinks(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    skills_dir: Path,
    *,
    dry_run: bool,
    include_plugin_mirrors: bool = True,
    replace_runtime_links: bool = False,
) -> None:
    home = Path.home()
    for _label, src, dst in _user_runtime_link_targets(repo_root, skills_dir, home):
        plan["symlinks"].append({"from": str(dst), "to": str(src)})
        logs.append(_create_symlink(src, dst, dry_run, replace_existing=replace_runtime_links))
    if not include_plugin_mirrors:
        logs.append("Skipped home plugin mirror refresh for links-only user sync.")
        return
    user_plugins = home / ".agents" / "plugins"
    personal_plugins_action = _clear_symlinked_personal_plugin_root(
        repo_root,
        user_plugins,
        dry_run=dry_run,
        plan=plan,
    )
    logs.append(personal_plugins_action)
    if user_plugins.is_symlink() and not personal_plugins_action.startswith(("Would replace", "Replaced")):
        logs.append(f"Skipped home plugin mirror refresh for preserved personal plugin marketplace symlink: {user_plugins}")
    elif personal_plugins_action.startswith(("Would replace", "Replaced")) or user_plugins.exists():
        _refresh_home_plugin_mirrors(plan, logs, repo_root, user_plugins, dry_run=dry_run)
    _refresh_home_plugin_mirrors(plan, logs, repo_root, home / "plugins", dry_run=dry_run)
    for profile_home in _codex_profile_homes(home):
        _refresh_home_plugin_mirrors(
            plan, logs, repo_root, profile_home / "plugins", dry_run=dry_run, prune_command_surface_duplicates=True
        )
        _refresh_home_plugin_mirrors(
            plan, logs, repo_root, profile_home / "Plugins", dry_run=dry_run, prune_command_surface_duplicates=True
        )
        _refresh_home_plugin_mirrors(
            plan, logs, repo_root, profile_home / ".agents" / "plugins", dry_run=dry_run, prune_command_surface_duplicates=True
        )


def _user_runtime_link_targets(repo_root: Path, skills_dir: Path, home: Path) -> tuple[tuple[str, Path, Path], ...]:
    """Return the exact user-runtime links owned by a links-only projection."""
    return (
        ("agents_user_runtime", skills_dir, home / ".agents" / "skills"),
        ("codex_user_runtime", skills_dir, home / ".codex" / "skills"),
        ("agents_repository_root", repo_root, home / ".agents" / "agent-skills"),
    )


def _runtime_link_preflight_error(link: Path, classification: str) -> ErrorObject:
    messages = {
        "foreign_or_stale": f"User runtime link {link} is foreign or stale and will not be replaced.",
        "uninspectable": f"User runtime link {link} could not be inspected and will not be replaced.",
        "non_symlink": f"User runtime link destination {link} is occupied by a non-symlink path.",
    }
    return ErrorObject(
        code="ERR_RUNTIME",
        message=messages[classification],
        fix_suggestion=f"Inspect and reconcile {link} before applying a links-only user sync.",
    )


def _inspect_user_runtime_link(source: Path, link: Path, label: str) -> tuple[dict[str, Any], ErrorObject | None]:
    expected_target = str(source)
    check: dict[str, Any] = {
        "label": label,
        "path": str(link),
        "expected_target": expected_target,
        "classification": "absent",
        "status": "pass",
    }
    if not link.exists() and not link.is_symlink():
        return check, None
    if not link.is_symlink():
        check.update({"classification": "non_symlink", "status": "fail"})
        return check, _runtime_link_preflight_error(link, "non_symlink")
    try:
        target_text = os.readlink(link)
        resolved_target = link.resolve(strict=False)
    except OSError as exc:
        check.update({"classification": "uninspectable", "status": "fail", "error": str(exc)})
        return check, _runtime_link_preflight_error(link, "uninspectable")
    expected_resolved = source.resolve(strict=False)
    check.update({"target": target_text, "resolved_target": str(resolved_target)})
    if target_text == expected_target and resolved_target == expected_resolved:
        check["classification"] = "current"
        return check, None
    check.update({"classification": "foreign_or_stale", "status": "fail"})
    return check, _runtime_link_preflight_error(link, "foreign_or_stale")


def _preflight_user_runtime_relinks(plan: dict, repo_root: Path, skills_dir: Path, home: Path) -> list[ErrorObject]:
    """Reject occupied user-runtime destinations before a links-only projection mutates home."""
    checks: list[dict[str, Any]] = []
    errors: list[ErrorObject] = []
    for label, source, link in _user_runtime_link_targets(repo_root, skills_dir, home):
        check, error = _inspect_user_runtime_link(source, link, label)
        checks.append(check)
        if error is not None:
            errors.append(error)
    plan["user_runtime_link_preflight"] = {
        "status": "pass" if not errors else "fail",
        "checks": checks,
    }
    return errors

__all__ = [name for name in globals() if not name.startswith("__")]
