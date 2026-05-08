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

from command_surface import handles_report


@dataclass
class PluginCacheRefreshReport:
    """Mutation report for repo-local plugin cache refreshes."""

    writes: list[str]
    deletes: list[str]
    logs: list[str]


class PluginCacheRefreshError(RuntimeError):
    """Raised when command-handle pruning cannot safely complete."""


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
    handles = report.get("handles") if isinstance(report, dict) else []
    if not isinstance(handles, list):
        return [], []

    logs: list[str] = []
    deletes: list[str] = []
    for row in handles:
        if not isinstance(row, dict):
            continue
        if row.get("owner") != plugin_name:
            continue
        command_handle_path = str(row.get("command_handle_path") or "")
        if not command_handle_path.startswith(".agents/skills/"):
            continue
        handle = str(row.get("handle") or "").strip()
        if not handle or "/" in handle or ".." in handle:
            continue
        targets = [skills_root / handle]
        targets.extend(
            skill_md.parent
            for skill_md in skills_root.rglob("SKILL.md")
            if skill_md.parent.name == handle
        )
        for target in sorted(set(targets)):
            if not (target.exists() or target.is_symlink()):
                continue
            if target.is_symlink() or target.is_file():
                target.unlink()
            else:
                shutil.rmtree(target)
            deletes.append(str(target))
            logs.append(f"Removed command-handle duplicate plugin skill entry: {target}")
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
    """Replace one local plugin cache copy and prune command-handle duplicate entries."""
    deletes: list[str] = []
    if target_dir.is_symlink() or target_dir.is_file():
        deletes.append(str(target_dir))
        target_dir.unlink()
    elif target_dir.exists():
        deletes.append(str(target_dir))
        shutil.rmtree(target_dir)
    copy_directory_contents(source_dir, target_dir)
    materialize_first_level_skill_aliases(target_dir)
    logs, prune_deletes = prune_command_handle_skill_entries(repo_root, plugin_name, target_dir)
    deletes.extend(prune_deletes)
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
    try:
        marketplace_path, entries = load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        logs.append(f"Skipped workspace plugin cache refresh: {exc}")
        return None

    try:
        marketplace_name = json.loads(marketplace_path.read_text(encoding="utf-8")).get("name") or "agent-skills-local"
    except (OSError, json.JSONDecodeError):
        marketplace_name = "agent-skills-local"
    marketplace_name = str(marketplace_name).strip() or "agent-skills-local"
    if "/" in marketplace_name or ".." in marketplace_name:
        marketplace_name = "agent-skills-local"

    runtime_cache_root = repo_root / ".agents" / "plugins-runtime" / "cache" / marketplace_name
    versioned_cache_root = repo_root / "Plugins" / "cache" / marketplace_name
    plan.setdefault("plugin_cache_writes", [])
    plan.setdefault("writes", [])
    plan.setdefault("deletes", [])

    keep_plugin_names = {entry["name"] for entry in entries}
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
            if dry_run:
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
                if child.name in keep_plugin_names or not child.is_dir():
                    continue
                plan["deletes"].append(str(child))
                if dry_run:
                    logs.append(f"Would remove stale local plugin cache: {child}")
                    continue
                shutil.rmtree(child)
                logs.append(f"Removed stale local plugin cache: {child}")
    except (OSError, ValueError, PluginCacheRefreshError) as exc:
        return ErrorObject(
            code="ERR_RUNTIME",
            message=f"Workspace plugin cache refresh failed: {exc}",
            fix_suggestion="Check local plugin cache permissions and rerun `./bin/ask skills sync --scope workspace --robot --json`.",
        )
    return None
