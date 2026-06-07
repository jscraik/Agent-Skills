from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from ask.envelope import ErrorObject
from ask.services.plugin_sources import (
    copy_directory_contents,
    load_local_marketplace,
    materialize_first_level_skill_aliases,
)

SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
LIFECYCLE_SYNC_ROOT = SCRIPTS_ROOT / "lifecycle-and-sync"
if str(LIFECYCLE_SYNC_ROOT) not in sys.path:
    sys.path.append(str(LIFECYCLE_SYNC_ROOT))

from command_surface import (
    FOLDED_SKILL_HANDLE_ALIASES,
    HIDDEN_COMPATIBILITY_COMMAND_HANDLES,
    handles_report,
)

RUNTIME_CACHE_RELATIVE_ROOT = Path(".agents/plugins-runtime/cache")
PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED = "PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED"
PLUGIN_CACHE_PERMISSION_RERUN = "rerun with write access to .agents/plugins-runtime/cache."
PICKER_INTERNAL_SKILL_DIRS = {
    "code_quality_review",
    "data_fetch_analysis",
    "examples",
    "fixtures",
    "infrastructure_ops",
    "references",
    "scaffolding_templates",
    "scripts",
    "shared",
    "team_automation",
    "templates",
}
PICKER_INTERNAL_PLUGIN_ROOT_DIRS = {
    "fixtures",
}


@dataclass
class PluginCacheRefreshReport:
    """Mutation report for repo-local plugin cache refreshes."""

    writes: list[str]
    deletes: list[str]
    logs: list[str]


class PluginCacheRefreshError(RuntimeError):
    """Raised when command-handle pruning cannot safely complete."""


def _manifest_declares_skills_root(plugin_root: Path, skills_root: Path) -> bool:
    plugin_json = plugin_root / ".codex-plugin" / "plugin.json"
    try:
        payload = json.loads(plugin_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    raw_path = str(payload.get("skills") or "").strip()
    if not raw_path:
        return False
    declared = (plugin_root / raw_path.removeprefix("./")).resolve()
    return declared == skills_root.resolve()


def plugin_cache_permission_declaration(repo_root: Path, *, mode: str = "auto") -> dict[str, str]:
    """Return the write declaration required to refresh repo-local plugin runtime caches."""
    runtime_cache_root = repo_root / RUNTIME_CACHE_RELATIVE_ROOT
    return {
        "mode": mode,
        "status": "not_run",
        "runtime_cache_root": str(runtime_cache_root),
        "runtime_cache_root_relative": str(RUNTIME_CACHE_RELATIVE_ROOT),
        "permission_requirement": "write access to .agents/plugins-runtime/cache",
        "rerun": PLUGIN_CACHE_PERMISSION_RERUN,
    }


def _codex_marketplace_entry(entry: dict[str, object], source_path: str) -> dict[str, object]:
    marketplace_entry: dict[str, object] = {
        "name": entry["name"],
        "source": {"source": "local", "path": source_path},
    }
    for key in ("policy", "category"):
        if key in entry:
            marketplace_entry[key] = entry[key]
    return marketplace_entry


def _write_codex_marketplace_root(
    *,
    marketplace_root: Path,
    marketplace_name: str,
    entries: list[dict[str, object]],
    source_paths: dict[str, str],
    dry_run: bool,
) -> list[str]:
    """Write a Codex-supported marketplace manifest under a plugin cache root."""
    marketplace_manifest = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    payload = {
        "name": marketplace_name,
        "plugins": [
            _codex_marketplace_entry(entry, source_paths[str(entry["name"])])
            for entry in entries
            if str(entry.get("name") or "") in source_paths
        ],
    }
    if dry_run:
        return [f"Would write Codex marketplace manifest: {marketplace_manifest}"]

    marketplace_manifest.parent.mkdir(parents=True, exist_ok=True)
    marketplace_manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return [f"Wrote Codex marketplace manifest: {marketplace_manifest}"]


def prune_command_handle_skill_entries(
    repo_root: Path,
    plugin_name: str,
    plugin_root: Path,
) -> tuple[list[str], list[str]]:
    """Remove plugin skill entries that are already exposed by generated command handles."""
    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        return [], []
    try:
        report = handles_report(repo_root_path=repo_root, include_handles=True)
    except Exception as exc:  # noqa: BLE001 - convert command-surface failures into sync errors.
        raise PluginCacheRefreshError(
            f"Failed to discover command handles for plugin cache pruning "
            f"(plugin={plugin_name}, root={plugin_root}): {exc}"
        ) from exc
    public_handles = report.get("handles", []) if isinstance(report, dict) else []
    hidden_handles = report.get("hidden_handles", []) if isinstance(report, dict) else []
    if not isinstance(public_handles, list) or not isinstance(hidden_handles, list):
        return [], []
    handles = [*public_handles, *hidden_handles]

    handles_to_prune: set[str] = set()
    owner_handles: set[str] = set()
    for row in handles:
        if not isinstance(row, dict):
            continue
        if row.get("owner") != plugin_name:
            continue
        command_handle_path = str(row.get("command_handle_path") or "")
        if not command_handle_path.startswith(".agents/skills/"):
            continue
        command_handle_file = repo_root / command_handle_path
        if not (command_handle_file.exists() or command_handle_file.is_symlink()):
            continue
        handle = str(row.get("handle") or "").strip()
        if not handle or "/" in handle or ".." in handle:
            continue
        owner_handles.add(handle)
        handles_to_prune.add(handle)
    for alias, target in FOLDED_SKILL_HANDLE_ALIASES.items():
        if alias not in HIDDEN_COMPATIBILITY_COMMAND_HANDLES:
            continue
        if target in owner_handles and "/" not in alias and ".." not in alias:
            handles_to_prune.add(alias)
    for hidden_handle in HIDDEN_COMPATIBILITY_COMMAND_HANDLES:
        if hidden_handle in owner_handles and "/" not in hidden_handle and ".." not in hidden_handle:
            handles_to_prune.add(hidden_handle)

    logs: list[str] = []
    deletes: list[str] = []
    for handle in sorted(handles_to_prune):
        targets = [skills_root / handle]
        targets.extend(
            skill_md.parent
            for skill_md in skills_root.rglob("SKILL.md")
            if skill_md.parent.name == handle
        )
        for target in sorted(set(targets)):
            if not (target.exists() or target.is_symlink()):
                continue
            try:
                if target.is_symlink() or target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)
            except OSError as exc:
                logs.append(f"Skipped protected command-handle duplicate plugin skill entry: {target}: {exc}")
                continue
            deletes.append(str(target))
            logs.append(f"Removed command-handle duplicate plugin skill entry: {target}")
    return logs, deletes


def prune_picker_internal_skill_dirs(plugin_root: Path) -> tuple[list[str], list[str]]:
    """Remove copied implementation and archive folders that broad picker scans can see."""
    logs: list[str] = []
    deletes: list[str] = []
    for name in sorted(PICKER_INTERNAL_PLUGIN_ROOT_DIRS):
        target = plugin_root / name
        if not (target.exists() or target.is_symlink()):
            continue
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
        deletes.append(str(target))
        logs.append(f"Removed picker-internal plugin archive: {target}")

    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        return logs, deletes
    if _manifest_declares_skills_root(plugin_root, skills_root):
        logs.append(f"Preserved manifest-declared plugin skills root: {skills_root}")
        return logs, deletes

    for name in sorted(PICKER_INTERNAL_SKILL_DIRS):
        target = skills_root / name
        if not (target.exists() or target.is_symlink()):
            continue
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
        deletes.append(str(target))
        logs.append(f"Removed picker-internal plugin skill category: {target}")
    return logs, deletes


def plugin_version(source_dir: Path) -> str:
    """Return the declared plugin version, falling back to the local-dev version."""
    plugin_json = source_dir / ".codex-plugin" / "plugin.json"
    try:
        payload = json.loads(plugin_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "0.1.0"
    version = str(payload.get("version") or "0.1.0").strip()
    if not version or "/" in version or ".." in version:
        return "0.1.0"
    return version


def replace_plugin_cache_copy(
    repo_root: Path,
    plugin_name: str,
    source_dir: Path,
    target_dir: Path,
) -> PluginCacheRefreshReport:
    """Replace one local plugin cache copy while preserving loader-declared skill content."""
    deletes: list[str] = []
    if target_dir.is_symlink() or target_dir.is_file():
        deletes.append(str(target_dir))
        target_dir.unlink()
    elif target_dir.exists():
        deletes.extend(str(child) for child in target_dir.iterdir())
    copy_directory_contents(source_dir, target_dir)
    materialize_first_level_skill_aliases(target_dir)
    logs, internal_deletes = prune_picker_internal_skill_dirs(target_dir)
    deletes.extend(path for path in internal_deletes if path not in deletes)
    logs.append(f"Replaced local plugin cache: {target_dir} <- {source_dir}")
    return PluginCacheRefreshReport(writes=[str(target_dir)], deletes=deletes, logs=logs)


def refresh_workspace_plugin_caches(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    *,
    dry_run: bool,
) -> ErrorObject | None:
    """Refresh repo-local plugin caches that Codex picker paths may scan."""
    refresh_state = plan.setdefault(
        "plugin_cache_refresh",
        plugin_cache_permission_declaration(repo_root),
    )
    refresh_state["status"] = "running"
    try:
        marketplace_path, entries = load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        refresh_state["status"] = "skipped"
        logs.append(f"Skipped workspace plugin cache refresh: {exc}")
        return None

    try:
        marketplace_name = json.loads(marketplace_path.read_text(encoding="utf-8")).get("name") or "agent-skills-local"
    except (OSError, json.JSONDecodeError):
        marketplace_name = "agent-skills-local"
    marketplace_name = str(marketplace_name).strip() or "agent-skills-local"
    if "/" in marketplace_name or ".." in marketplace_name:
        marketplace_name = "agent-skills-local"

    runtime_cache_root = repo_root / RUNTIME_CACHE_RELATIVE_ROOT / marketplace_name
    versioned_cache_root = repo_root / "Plugins" / "cache" / marketplace_name
    plan.setdefault("plugin_cache_writes", [])
    plan.setdefault("writes", [])
    plan.setdefault("deletes", [])
    plan.setdefault("warnings", [])

    keep_plugin_names = {entry["name"] for entry in entries}
    runtime_source_paths: dict[str, str] = {}
    versioned_source_paths: dict[str, str] = {}
    try:
        for entry in entries:
            plugin_name = entry["name"]
            if "/" in plugin_name or ".." in plugin_name:
                logs.append(f"Skipped unsafe plugin cache name: {plugin_name}")
                continue
            source_dir = repo_root / entry["path"].removeprefix("./")
            if not source_dir.is_dir():
                logs.append(f"Skipped missing plugin cache source: {source_dir}")
                continue
            version = plugin_version(source_dir)
            runtime_target = runtime_cache_root / plugin_name
            versioned_target = versioned_cache_root / plugin_name / version
            planned_writes = [str(runtime_target), str(versioned_target)]
            plan["plugin_cache_writes"].extend(planned_writes)
            plan["writes"].extend(planned_writes)
            runtime_source_paths[plugin_name] = f"./{plugin_name}"
            versioned_source_paths[plugin_name] = f"./{plugin_name}/{version}"
            if dry_run:
                refresh_state["status"] = "planned"
                logs.append(f"Would replace local plugin cache: {runtime_target} <- {source_dir}")
                logs.append(f"Would replace local plugin cache: {versioned_target} <- {source_dir}")
                for target in (runtime_target, versioned_target):
                    if target.exists() or target.is_symlink():
                        plan["deletes"].append(str(target))
                plugin_version_root = versioned_cache_root / plugin_name
                for child in sorted(plugin_version_root.iterdir()) if plugin_version_root.is_dir() else []:
                    if child == versioned_target or not child.is_dir():
                        continue
                    plan["deletes"].append(str(child))
                    logs.append(f"Would remove stale versioned local plugin cache variant: {child}")
                continue
            for target in (runtime_target, versioned_target):
                report = replace_plugin_cache_copy(repo_root, plugin_name, source_dir, target)
                logs.extend(report.logs)
                plan["deletes"].extend(report.deletes)
            plugin_version_root = versioned_cache_root / plugin_name
            for child in sorted(plugin_version_root.iterdir()) if plugin_version_root.is_dir() else []:
                if child == versioned_target or not child.is_dir():
                    continue
                plan["deletes"].append(str(child))
                shutil.rmtree(child)
                logs.append(f"Removed stale versioned local plugin cache variant: {child}")

        for cache_root in (runtime_cache_root, versioned_cache_root):
            if not cache_root.is_dir():
                continue
            for child in sorted(cache_root.iterdir()):
                if child.name in {".agents", ".claude-plugin"} or child.name in keep_plugin_names or not child.is_dir():
                    continue
                plan["deletes"].append(str(child))
                if dry_run:
                    logs.append(f"Would remove stale local plugin cache: {child}")
                    continue
                shutil.rmtree(child)
                logs.append(f"Removed stale local plugin cache: {child}")

        marketplace_writes = [
            str(runtime_cache_root / ".agents" / "plugins" / "marketplace.json"),
            str(versioned_cache_root / ".agents" / "plugins" / "marketplace.json"),
        ]
        plan["plugin_cache_writes"].extend(marketplace_writes)
        plan["writes"].extend(marketplace_writes)
        logs.extend(
            _write_codex_marketplace_root(
                marketplace_root=runtime_cache_root,
                marketplace_name=marketplace_name,
                entries=entries,
                source_paths=runtime_source_paths,
                dry_run=dry_run,
            )
        )
        logs.extend(
            _write_codex_marketplace_root(
                marketplace_root=versioned_cache_root,
                marketplace_name=marketplace_name,
                entries=entries,
                source_paths=versioned_source_paths,
                dry_run=dry_run,
            )
        )
    except PermissionError as exc:
        refresh_state["status"] = "blocked"
        refresh_state["warning"] = PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED
        plan["warnings"].append(PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED)
        logs.append(
            "Skipped workspace plugin cache refresh after permission failure: "
            f"{exc}. Rooted skill projections and manifests may still be current; "
            f"{PLUGIN_CACHE_PERMISSION_RERUN}"
        )
        return ErrorObject(
            code="ERR_RUNTIME",
            message=f"Workspace plugin cache refresh blocked by permissions: {exc}",
            fix_suggestion=PLUGIN_CACHE_PERMISSION_RERUN,
        )
    except (OSError, ValueError, PluginCacheRefreshError) as exc:
        return ErrorObject(
            code="ERR_RUNTIME",
            message=f"Workspace plugin cache refresh failed: {exc}",
            fix_suggestion="Check local plugin cache permissions and rerun `./bin/ask skills sync --scope workspace --robot --json`.",
        )
    refresh_state["status"] = "planned" if dry_run else "refreshed"
    return None
