from .skills_impl_improve_fallback import *  # noqa: F403

def _verify_user_runtime_relinks(
    plan: dict,
    repo_root: Path,
    home: Path,
    skills_dir: Path,
    *,
    dry_run: bool,
) -> list[ErrorObject]:
    """Verify home runtime skill links point at this checkout's projection after user sync."""
    checks: list[dict[str, Any]] = []
    errors: list[ErrorObject] = []
    if dry_run:
        plan["user_runtime_link_checks"] = {
            "status": "not_run",
            "reason": "dry_run",
            "expected_targets": [
                str(source)
                for _label, source, _link in _user_runtime_link_targets(repo_root, skills_dir, home)
            ],
            "checks": checks,
        }
        return errors

    for label, source, link in _user_runtime_link_targets(repo_root, skills_dir, home):
        expected_target = str(source)
        expected_resolved = source.resolve(strict=False)
        check: dict[str, Any] = {
            "label": label,
            "path": str(link),
            "expected_target": expected_target,
            "exists": link.exists(),
            "is_symlink": link.is_symlink(),
            "target": None,
            "resolved_target": None,
            "literal_target_matches": False,
            "resolved_target_matches": False,
            "status": "fail",
        }
        if link.is_symlink():
            try:
                target_text = os.readlink(link)
                resolved_target = link.resolve(strict=False)
            except OSError as exc:
                check["error"] = str(exc)
            else:
                check["target"] = target_text
                check["resolved_target"] = str(resolved_target)
                check["literal_target_matches"] = target_text == expected_target
                check["resolved_target_matches"] = resolved_target == expected_resolved
        if check["is_symlink"] and check["literal_target_matches"] and check["resolved_target_matches"]:
            check["status"] = "pass"
        else:
            errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"User runtime link {link} does not point at the active workspace projection.",
                    fix_suggestion=(
                        "Run ./bin/ask skills sync --scope user --projection flat --json --robot "
                        "from the intended checkout and verify the link target casing matches exactly."
                    ),
                )
            )
        checks.append(check)

    plan["user_runtime_link_checks"] = {
        "status": "pass" if not errors else "fail",
        "expected_targets": [
            str(source)
            for _label, source, _link in _user_runtime_link_targets(repo_root, skills_dir, home)
        ],
        "checks": checks,
    }
    return errors


def _clear_symlinked_personal_plugin_root(repo_root: Path, target: Path, *, dry_run: bool, plan: dict) -> str:
    """Remove only repo-backed personal plugin marketplace root symlinks before mirror sync."""
    if not target.exists() and not target.is_symlink():
        return f"Personal plugin marketplace root is absent: {target}"
    if not target.is_symlink():
        return f"Personal plugin marketplace root is already a directory: {target}"
    if not _is_repo_backed_plugin_root_symlink(repo_root, target):
        return f"Preserved personal plugin marketplace symlink: {target}"
    plan["deletes"].append(f"Remove symlinked personal plugin marketplace root: {target}")
    plan["writes"].append(str(target))
    if dry_run:
        return f"Would replace symlinked personal plugin marketplace root with directory: {target}"
    else:
        target.unlink()
        target.mkdir(parents=True, exist_ok=True)
    return f"Replaced symlinked personal plugin marketplace root with directory: {target}"


def _is_repo_backed_plugin_root_symlink(repo_root: Path, target: Path) -> bool:
    try:
        resolved = target.resolve(strict=False)
    except OSError:
        return False
    canonical_plugins = (repo_root / "Plugins").resolve(strict=False)
    if resolved == canonical_plugins:
        return True
    if resolved.name != "Plugins":
        return False
    repo_markers = (".git", "AGENTS.md", "UBIQUITOUS_LANGUAGE.md")
    return any((resolved.parent / marker).exists() for marker in repo_markers)


def _codex_profile_homes(home: Path) -> list[Path]:
    """Return Codex profile homes that can contribute plugin picker entries."""
    candidates = [home / ".codex"]
    try:
        candidates.extend(sorted(home.glob(".codex-*")))
    except OSError:
        pass
    return [path for path in candidates if path.exists() and path.is_dir()]


def _ensure_real_plugin_mirror_root(target: Path, canonical_plugins_dir: Path, dry_run: bool) -> str:
    """Ensure a home plugin mirror root is a real directory, not a symlink."""
    if target.is_symlink():
        if not dry_run:
            target.unlink()
            target.mkdir(parents=True, exist_ok=True)
        return f"Replaced symlinked plugin mirror root with directory: {target}"
    if target.exists() and not target.is_dir():
        return f"Skipped non-directory plugin mirror path: {target}"
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    return f"Ensured plugin mirror directory: {target}"


def _finalize_skill_sync_result(
    result: CallResult,
    plan: dict,
    logs: list[str],
    projection_decision: ProjectionModeDecision,
    *,
    scope: str,
    dry_run: bool,
    status: str,
    plugin_cache_refresh: str = "auto",
) -> CallResult:
    """Populate common sync result data after all mutations have been planned."""
    plan["mutation_counts"] = {
        "writes": len(plan["writes"]),
        "deletes": len(plan["deletes"]),
        "symlinks": len(plan["symlinks"]),
    }
    result.data["plan"] = plan
    result.data["logs"] = logs
    result.data["policy_identity"] = get_policy_identity()
    result.data["projection_mode"] = projection_decision.projection_mode
    result.data["projection"] = build_projection_plan_metadata(
        projection_decision,
        scope=scope,
        dry_run=dry_run,
        warnings=plan["warnings"],
    )
    validation_args: list[str] = []
    if scope != "workspace":
        validation_args.extend(["--scope", scope])
    if dry_run:
        validation_args.append("--dry-run")
    if projection_decision.mode_source in {"cli", "env"}:
        validation_args.extend(["--projection", projection_decision.requested_mode])
    if scope == "user":
        validation_args.extend(["--user-sync-mode", str(plan.get("user_sync_mode", "full"))])
    if plugin_cache_refresh != "auto":
        validation_args.extend(["--plugin-cache-refresh", plugin_cache_refresh])
    result.data["validation_commands"] = [_skills_validation_command("sync", *validation_args)]
    result.status = status
    return result


def _refresh_home_plugin_mirrors(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    home_plugins_dir: Path,
    *,
    dry_run: bool,
    prune_command_surface_duplicates: bool = False,
) -> None:
    """
    Replace the user's home plugin mirror copies from the repository's canonical Plugins/ sources.

    When run, ensure the home plugins mirror root is a real directory (not a repository-backed symlink), then for each plugin listed in Plugins/marketplace.json replace the corresponding directory under home_plugins_dir with a copy of the repository source, materialize first-level skill aliases, prune duplicate SDK entries, and write a marker file recording the repository source. In dry-run mode, only record planned actions in logs and the provided plan structure.

    Parameters:
        plan (dict): Operation plan that will be mutated with a mirror plan and per-plugin entries.
        logs (list[str]): Mutable log list to append human-readable action messages.
        repo_root (Path): Repository root containing the Plugins/ directory and marketplace.json.
        home_plugins_dir (Path): Target directory under the user's home where plugin mirrors are maintained.
        dry_run (bool): If True, do not perform filesystem mutations; only record intended actions in logs.
    """
    plugins_dir = repo_root / "Plugins"
    mirror_plan = {
        "from": str(plugins_dir),
        "to": str(home_plugins_dir),
        "mode": "copy-replace",
        "trigger": "refresh after canonical Plugins/ or Plugins/marketplace.json changes",
        "plugins": [],
    }
    plan.setdefault("runtime_plugin_mirrors", []).append(mirror_plan)
    root_log = _ensure_real_plugin_mirror_root(home_plugins_dir, plugins_dir, dry_run)
    logs.append(root_log)
    if root_log.startswith("Skipped"):
        return

    try:
        _marketplace_path, entries = _load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        logs.append(f"Skipped home plugin mirror refresh: {exc}")
        return

    marker_name = ".codex-repo-plugin-source"
    keep_names = {entry["name"] for entry in entries}
    for entry in entries:
        plugin_name = entry["name"]
        relative = entry["path"]
        source_dir = repo_root / relative.removeprefix("./")
        target_dir = home_plugins_dir / plugin_name
        mirror_plan["plugins"].append({
            "name": plugin_name,
            "source": str(source_dir),
            "target": str(target_dir),
        })
        if not source_dir.is_dir():
            logs.append(f"Skipped missing home plugin mirror source: {source_dir}")
            continue
        if dry_run:
            logs.append(f"Would replace home plugin mirror: {target_dir} <- {source_dir}")
            continue
        try:
            if target_dir.is_symlink() or target_dir.is_file():
                target_dir.unlink()
            elif target_dir.exists():
                shutil.rmtree(target_dir)
        except OSError as exc:
            logs.append(f"Skipped replacing protected home plugin mirror: {target_dir}: {exc}")
            if prune_command_surface_duplicates:
                prune_logs, _prune_deletes = prune_command_surface_duplicate_skill_entries(repo_root, plugin_name, target_dir)
                logs.extend(prune_logs)
            continue
        _copy_directory_contents(source_dir, target_dir)
        _materialize_first_level_skill_aliases(target_dir)
        if prune_command_surface_duplicates:
            prune_logs, _prune_deletes = prune_command_surface_duplicate_skill_entries(repo_root, plugin_name, target_dir)
            logs.extend(prune_logs)
        (target_dir / marker_name).write_text(str(source_dir.resolve()) + "\n", encoding="utf-8")
        logs.append(f"Replaced home plugin mirror: {target_dir} <- {source_dir}")

    # Prune stale home plugin mirrors that are no longer declared in the marketplace.
    reserved = {"marketplace.json", "cache"}
    if home_plugins_dir.is_dir():
        for child in home_plugins_dir.iterdir():
            if child.name in keep_names or child.name in reserved:
                continue
            if not child.is_dir():
                continue
            marker_file = child / marker_name
            if not marker_file.is_file():
                continue
            if dry_run:
                logs.append(f"Would remove stale home plugin mirror: {child}")
                continue
            try:
                if child.is_symlink():
                    child.unlink()
                else:
                    shutil.rmtree(child)
            except OSError as exc:
                logs.append(f"Skipped removing protected stale home plugin mirror: {child}: {exc}")
                continue
            logs.append(f"Removed stale home plugin mirror: {child}")




@dataclass(frozen=True)
class SkillSyncOptions:
    """Optional user-sync behavior while preserving the existing sync call shape."""

    plugin_cache_refresh: str = "auto"
    user_sync_mode: str = "full"


def sync_skills(
    repo_root: Path,
    scope: str = "workspace",
    dry_run: bool = False,
    projection: Optional[str] = None,
    plugin_cache_refresh: str | SkillSyncOptions = "auto",
) -> CallResult:
    """
    Synchronizes derived skill views for either the repository workspace or the user environment.

    For scope="workspace" this prunes stale first-level symlinks under .agents/skills, recreates symlinks for repository-owned skills, preserves a .system bridge when present, and refreshes catalog projections (SKILL.md and README.md). For scope="user" this creates user-facing symlinks from the repo workspace.

    Parameters:
        repo_root (Path): Root path of the repository containing skills directories.
        scope (str): Either "workspace" to sync repository-derived views or "user" to populate user-local locations.
        dry_run (bool): If True, no filesystem mutations are performed; actions are reported only.
        projection (Optional[str]): Explicit runtime projection mode. When omitted,
            SYNC_SKILLS_PROJECTION_MODE is honored before the flat default.
        plugin_cache_refresh (str | SkillSyncOptions): Plugin runtime cache refresh mode:
            "auto" refreshes best-effort during workspace sync, "skip" runs
            normal projection sync without cache mutation, and "only" refreshes
            plugin runtime caches without changing skill projections. The typed
            form can additionally select links-only user sync.

    Returns:
        CallResult: Success result contains a `data` object with:
          - plan: dict with lists for "writes", "deletes", and "symlinks" describing intended changes,
          - logs: list of human-readable action logs,
          - policy_identity: identity info from get_policy_identity().
        On error, the result will have status "error" and one or more ErrorObject entries:
          - ERR_INVALID_SCOPE when `scope` is not "workspace" or "user".
          - ERR_VALIDATION when inputs contain disallowed symlinks or other validation failures.
          - Other errors may be returned for copy/sync failures (e.g., when `_sync_dir_copy` detects symlinks).
    """
    result = CallResult()
    sync_options = (
        plugin_cache_refresh
        if isinstance(plugin_cache_refresh, SkillSyncOptions)
        else SkillSyncOptions(plugin_cache_refresh=str(plugin_cache_refresh))
    )
    plugin_cache_refresh = sync_options.plugin_cache_refresh
    user_sync_mode = sync_options.user_sync_mode
    try:
        projection_decision = normalize_projection_mode(projection)
    except ProjectionModeError as exc:
        resolved_mode = getattr(exc, "resolved_mode", None)
        fix_suggestions = {
            "ERR_INVALID_PROJECTION_MODE": "Choose the supported SDK projection mode: --projection flat.",
            "ERR_DEFERRED_PROJECTION_MODE": "Use --projection flat until the deferred projection mode is available.",
        }
        result.status = "error"
        result.errors.append(ErrorObject(
            code=exc.code,
            message=exc.message,
            fix_suggestion=fix_suggestions.get(exc.code, "Choose a supported projection mode or rerun with --dry-run."),
        ))
        result.data["projection_mode"] = resolved_mode
        result.data["requested_projection_mode"] = getattr(exc, "requested_mode", projection or "")
        return result

    if plugin_cache_refresh not in {"auto", "skip", "only"}:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Invalid plugin cache refresh mode: '{plugin_cache_refresh}'.",
            fix_suggestion="Use --plugin-cache-refresh auto, skip, or only.",
        ))
        return result

    if user_sync_mode not in {"full", "links-only"}:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Invalid user sync mode: '{user_sync_mode}'.",
            fix_suggestion="Use --user-sync-mode links-only or full.",
        ))
        return result

    if scope not in {"workspace", "user"}:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_INVALID_SCOPE",
            message=f"Invalid scope: '{scope}'. Must be 'workspace' or 'user'.",
            fix_suggestion="Use --scope workspace or --scope user"
        ))
        return result

    if scope != "user" and user_sync_mode != "full":
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_INVALID_SCOPE",
            message="User sync mode is available only with --scope user.",
            fix_suggestion="Use --scope user --user-sync-mode links-only.",
        ))
        return result

    plan = {
        "writes": [],
        "deletes": [],
        "symlinks": [],
        "system_bridge_skill_names": sorted(SYSTEM_BRIDGE_SKILL_NAMES),
        "preserved_bridge_lane_entries": [],
        "preserved_system_lane_entries": [],
        "validation_status": "not_run",
        "unmapped_entries": [],
        "violations": [],
        "mutation_counts": {
            "writes": 0,
            "deletes": 0,
            "symlinks": 0,
        },
        "warnings": [],
        "user_sync_mode": user_sync_mode,
        "plugin_cache_refresh": plugin_cache_permission_declaration(repo_root, mode=plugin_cache_refresh),
    }
    logs = []
    skills_dir = repo_root / ".agents" / "skills"
    system_skills_dir = repo_root / "skills-system"

    if plugin_cache_refresh == "only":
        if scope != "workspace":
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_INVALID_SCOPE",
                message="Plugin runtime cache refresh is workspace-scoped.",
                fix_suggestion="Use `./bin/ask skills sync --scope workspace --plugin-cache-refresh only`.",
            ))
            return result
        logs.append(
            "Running plugin runtime cache refresh only; normal SDK-flat projection sync skipped. "
            f"If the cache path is blocked, {PLUGIN_CACHE_PERMISSION_RERUN}"
        )
        cache_error = refresh_workspace_plugin_caches(plan, logs, repo_root, dry_run=dry_run)
        if cache_error:
            result.errors.append(cache_error)
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
        plan["validation_status"] = "pass"
        return _finalize_skill_sync_result(
            result,
            plan,
            logs,
            projection_decision,
            scope=scope,
            dry_run=dry_run,
            status="success",
            plugin_cache_refresh=plugin_cache_refresh,
        )

    if system_skills_dir.is_dir():
        plan["preserved_system_lane_entries"] = sorted(
            item.name
            for item in system_skills_dir.iterdir()
            if item.is_dir() and (item / "SKILL.md").exists()
        )


    entries = discover_skill_entries(source="repo")
    if scope == "workspace":
        try:
            plan["preserved_bridge_lane_entries"] = sorted(SYSTEM_BRIDGE_SKILL_NAMES)
            keep_names = {entry.name for entry in entries if entry.source_dir.is_relative_to(repo_root)}
            if system_skills_dir.is_dir():
                keep_names.add(".system")
            for log in _prune_first_level_symlinks(skills_dir, keep_names, dry_run):
                plan["deletes"].append(log)
                logs.append(log)
            if not dry_run:
                for log in _prune_first_level_system_bridge_aliases(
                    skills_dir,
                    system_skills_dir,
                    dry_run=False,
                ):
                    plan["deletes"].append(log)
                    logs.append(log)
            for log in _prune_generated_root_skill_dirs(
                skills_dir,
                keep_names,
                dry_run=dry_run,
                preserve_keep_names=False,
            ):
                plan["deletes"].append(log)
                logs.append(log)
            for entry in entries:
                if _is_system_bridge_entry(entry, system_skills_dir):
                    logs.append(f"Skipped hidden system bridge from flat projection: {entry.name}")
                    continue
                skill_name = entry.name
                target_link = skills_dir / skill_name
                if not entry.source_dir.is_relative_to(repo_root):
                    continue
                rel_to_root = entry.source_dir.relative_to(repo_root)
                source_rel = os.path.join("../..", str(rel_to_root))
                plan["symlinks"].append({"from": str(target_link), "to": source_rel})
                logs.append(_create_symlink(Path(source_rel), target_link, dry_run))
            system_lane_logs = _refresh_system_lane_link(skills_dir, system_skills_dir, dry_run)
            if system_lane_logs:
                plan["symlinks"].append({"from": str(skills_dir / ".system"), "to": "../../skills-system"})
                logs.extend(system_lane_logs)
            for log in _prune_first_level_system_bridge_aliases(
                skills_dir,
                system_skills_dir,
                dry_run=dry_run,
            ):
                plan["deletes"].append(log)
                logs.append(log)
            projection_logs = _refresh_catalog_projections(repo_root, dry_run)
            plan["writes"].extend([str(repo_root / "SKILL.md"), str(repo_root / "README.md")])
            logs.extend(projection_logs)
        except OSError as exc:
            plan["validation_status"] = "fail"
            plan["warnings"].append("RUNTIME_PROJECTION_MUTATION_FAILED")
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Skill runtime projection sync failed: {exc}",
                    fix_suggestion=(
                        "Check write permissions on .agents/skills and rerun "
                        "./bin/ask skills sync --scope workspace --json --robot."
                    ),
                )
            )
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
        cache_error = None
        if plugin_cache_refresh == "skip":
            plan["plugin_cache_refresh"]["status"] = "skipped"
            logs.append(
                "Skipped plugin runtime cache refresh (--plugin-cache-refresh skip); "
                f"{PLUGIN_CACHE_PERMISSION_RERUN}"
            )
        else:
            cache_error = refresh_workspace_plugin_caches(plan, logs, repo_root, dry_run=dry_run)
        if cache_error:
            result.errors.append(cache_error)
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
    elif scope == "user":
        try:
            rooted_entries = _generated_root_skill_dir_names(skills_dir)
            if rooted_entries:
                plan["validation_status"] = "fail"
                plan["warnings"].append("ROOTED_WORKSPACE_RESIDUE")
                plan["rooted_workspace_entries"] = rooted_entries
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message=(
                            "Workspace runtime still contains generated rooted skill-set entries: "
                            + ", ".join(rooted_entries)
                        ),
                        fix_suggestion=(
                            "Run ./bin/ask skills sync --scope workspace --projection flat --json --robot "
                            "before relinking user runtime skills."
                        ),
                    )
                )
                return _finalize_skill_sync_result(
                    result,
                    plan,
                    logs,
                    projection_decision,
                    scope=scope,
                    dry_run=dry_run,
                    status="error",
                    plugin_cache_refresh=plugin_cache_refresh,
                )
            home = Path.home()
            if user_sync_mode == "links-only":
                preflight_errors = _preflight_user_runtime_relinks(plan, repo_root, skills_dir, home)
                if preflight_errors:
                    plan["validation_status"] = "fail"
                    plan["warnings"].append("USER_RUNTIME_LINK_PREFLIGHT_FAILED")
                    result.errors.extend(preflight_errors)
                    return _finalize_skill_sync_result(
                        result,
                        plan,
                        logs,
                        projection_decision,
                        scope=scope,
                        dry_run=dry_run,
                        status="error",
                        plugin_cache_refresh=plugin_cache_refresh,
                    )
            _append_user_runtime_relinks(
                plan,
                logs,
                repo_root,
                skills_dir,
                dry_run=dry_run,
                include_plugin_mirrors=user_sync_mode == "full",
                replace_runtime_links=user_sync_mode == "full",
            )
            relink_errors = _verify_user_runtime_relinks(
                plan,
                repo_root,
                home,
                skills_dir,
                dry_run=dry_run,
            )
            if relink_errors:
                plan["validation_status"] = "fail"
                plan["warnings"].append("USER_RUNTIME_LINK_POSTCONDITION_FAILED")
                result.errors.extend(relink_errors)
                return _finalize_skill_sync_result(
                    result,
                    plan,
                    logs,
                    projection_decision,
                    scope=scope,
                    dry_run=dry_run,
                    status="error",
                    plugin_cache_refresh=plugin_cache_refresh,
                )
        except OSError as exc:
            plan["validation_status"] = "fail"
            plan["warnings"].append("USER_RUNTIME_LINK_SYNC_FAILED")
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"User runtime link sync failed: {exc}",
                    fix_suggestion=(
                        "Grant write access to ~/.agents and ~/.codex, then rerun "
                        "./bin/ask skills sync --scope user --json --robot."
                    ),
                )
            )
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
    plan["validation_status"] = "pass"
    return _finalize_skill_sync_result(
        result,
        plan,
        logs,
        projection_decision,
        scope=scope,
        dry_run=dry_run,
        status="success",
        plugin_cache_refresh=plugin_cache_refresh,
    )

__all__ = [name for name in globals() if not name.startswith("__")]
