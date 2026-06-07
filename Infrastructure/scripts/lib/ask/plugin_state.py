"""Read-only plugin state snapshots for ask plugin lifecycle commands."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT))
if str(SCRIPTS_ROOT / "lifecycle-and-sync") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "lifecycle-and-sync"))

from selection_policy import policy_identity  # noqa: E402


_LOCAL_PLUGIN_MARKETPLACE_ROOTS = ("Plugins", "plugins", ".agents/plugins")


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"missing file: {path}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"failed to parse {path}: {exc}"
    if not isinstance(payload, dict):
        return None, f"invalid object payload in {path}"
    return payload, None


def _plugin_root_content_status(plugin_root: Path) -> tuple[bool, list[str]]:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest_payload, manifest_error = _load_json(manifest_path)
    if manifest_payload is None:
        return False, [f"{plugin_root.as_posix()}: {manifest_error}"]
    skills_ref = manifest_payload.get("skills")
    if isinstance(skills_ref, str) and skills_ref.strip():
        skills_root = (plugin_root / skills_ref.strip()).resolve()
        try:
            skills_root.relative_to(plugin_root.resolve())
        except ValueError:
            return False, [f"{plugin_root.as_posix()}: manifest skills path escapes plugin root"]
        skill_files = sorted(skills_root.glob("*/SKILL.md"))
        if not skill_files:
            return False, [f"{plugin_root.as_posix()}: manifest skills path has no SKILL.md files"]
    return True, []


def _marketplace_payload(repo_root: Path) -> tuple[dict[str, Any], str | None, Path]:
    candidates = [
        repo_root / "Plugins" / "marketplace.json",
        repo_root / "plugins" / "marketplace.json",
        repo_root / ".agents" / "Plugins" / "marketplace.json",
        repo_root / ".agents" / "plugins" / "marketplace.json",
    ]
    for candidate in candidates:
        payload, error = _load_json(candidate)
        if payload is not None:
            return payload, None, candidate
        if candidate.exists():
            return {}, error, candidate
    return {}, f"marketplace not found in expected paths: {', '.join(str(p) for p in candidates)}", candidates[0]


def _installed_plugins(repo_root: Path) -> list[dict[str, Any]]:
    """
    Collect installed Ask plugin manifests under the repository root and produce normalized per-plugin entries.
    
    Searches for plugin manifest files matching platform- and case-variants under the given repo root, ignores any paths under `plugins/cache/` or `Plugins/cache/`, and deduplicates plugins by filesystem identity (st_dev, st_ino) with a fallback key when `stat()` fails. For each discovered manifest the function attempts to parse the manifest JSON; entries for unreadable/invalid manifests include `manifest_valid: False` and `manifest_error`. Valid entries include common manifest fields and a `governance` dict when present. Returned entries are sorted by plugin name or path.
    
    Parameters:
        repo_root (Path): Repository root used as the base directory for manifest discovery.
    
    Returns:
        list[dict[str, Any]]: A list of plugin descriptors. Each descriptor contains keys such as:
            - `name`: plugin name (from manifest or directory name)
            - `version`, `description` (when present)
            - `path`: displayable plugin path (repo-relative when possible)
            - `manifest_path`: repo-relative path to the manifest file
            - `manifest_valid` (bool)
            - `manifest_error` (present when `manifest_valid` is False)
            - `governance` (dict, when present)
    """
    installed: list[dict[str, Any]] = []
    resolved_repo_root = repo_root.resolve()
    seen_plugin_ids: set[tuple[int, int]] = set()
    manifest_patterns = (
        "plugins/*/.codex-plugin/plugin.json",
        "Plugins/*/.codex-plugin/plugin.json",
        "plugins/*/*/.codex-plugin/plugin.json",
        "Plugins/*/*/.codex-plugin/plugin.json",
    )

    def _display_plugin_path(plugin_dir_resolved: Path) -> str:
        """
        Return a human-readable POSIX path for a plugin directory, using a repository-relative path when possible.
        
        Parameters:
            plugin_dir_resolved (Path): The plugin directory path resolved to an absolute path.
        
        Returns:
            str: A POSIX-style path string relative to the resolved repository root if `plugin_dir_resolved` is under that root, otherwise the absolute POSIX path.
        """
        try:
            return plugin_dir_resolved.relative_to(resolved_repo_root).as_posix()
        except ValueError:
            return plugin_dir_resolved.as_posix()

    for pattern in manifest_patterns:
        for manifest_path in sorted(repo_root.glob(pattern)):
            rel = manifest_path.relative_to(repo_root).as_posix()
            if rel.startswith(("Plugins/cache/", "plugins/cache/")):
                continue
            plugin_dir = manifest_path.parent.parent
            plugin_dir_resolved = plugin_dir.resolve()
            try:
                stat = plugin_dir_resolved.stat()
                plugin_key = (stat.st_dev, stat.st_ino)
            except OSError:
                plugin_key = (-1, hash(str(plugin_dir_resolved)))
            if plugin_key in seen_plugin_ids:
                continue
            seen_plugin_ids.add(plugin_key)

            payload, error = _load_json(manifest_path)
            if payload is None:
                installed.append(
                    {
                        "name": plugin_dir.name,
                        "path": _display_plugin_path(plugin_dir_resolved),
                        "manifest_path": rel,
                        "manifest_valid": False,
                        "manifest_error": error,
                    }
                )
                continue

            installed.append(
                {
                    "name": str(payload.get("name") or plugin_dir.name),
                    "version": payload.get("version"),
                    "description": payload.get("description"),
                    "path": _display_plugin_path(plugin_dir_resolved),
                    "manifest_path": rel,
                    "manifest_valid": True,
                    "governance": payload.get("governance", {}),
                }
            )

    installed.sort(key=lambda item: str(item.get("name") or item.get("path") or ""))
    return installed


def _activation_state(
    *,
    repo_root: Path,
    installed: list[dict[str, Any]],
    marketplace: dict[str, Any],
) -> dict[str, Any]:
    def _normalized_marketplace_name(raw: Any) -> str | None:
        if isinstance(raw, str):
            normalized = raw.strip()
            if normalized:
                return normalized
        return None

    def _cache_status(
        *,
        plugin_name: str,
        marketplace_name: str | None,
        entry: dict[str, Any] | None,
    ) -> dict[str, Any]:
        candidates: list[str] = []

        if isinstance(entry, dict):
            direct_market = _normalized_marketplace_name(entry.get("marketplace"))
            if direct_market:
                candidates.append(direct_market)
            source = entry.get("source")
            if isinstance(source, dict):
                source_market = _normalized_marketplace_name(source.get("marketplace"))
                if source_market:
                    candidates.append(source_market)

        if marketplace_name:
            candidates.append(marketplace_name)

        # Backward compatibility for legacy local plugin cache families only.
        if any(candidate in {"local", "agent-skills-local"} for candidate in candidates):
            candidates.append("agent-skills-local")

        deduped_candidates = tuple(dict.fromkeys(candidates))
        cache_roots = (
            repo_root / ".agents" / "plugins-runtime" / "cache",
            repo_root / "plugins" / "cache",
            repo_root / "Plugins" / "cache",
        )
        inspected_roots: list[str] = []
        missing_reasons: list[str] = []

        def _candidate_plugin_roots(base: Path) -> list[Path]:
            roots = [base]
            if base.is_dir():
                roots.extend(sorted(child for child in base.iterdir() if child.is_dir()))
            return roots

        def _codex_marketplace_root_status(marketplace_root: Path) -> dict[str, Any] | None:
            if not marketplace_root.exists():
                return None
            marketplace_manifest = marketplace_root / ".agents" / "plugins" / "marketplace.json"
            marketplace_payload, marketplace_error = _load_json(marketplace_manifest)
            if marketplace_payload is None:
                return {
                    "present": True,
                    "content_ready": False,
                    "active_root": None,
                    "inspected_roots": [marketplace_root.as_posix()],
                    "issues": [
                        f"{marketplace_root.as_posix()}: missing Codex marketplace manifest "
                        f"at .agents/plugins/marketplace.json: {marketplace_error}"
                    ],
                }

            plugins = marketplace_payload.get("plugins")
            if not isinstance(plugins, list):
                return {
                    "present": True,
                    "content_ready": False,
                    "active_root": None,
                    "inspected_roots": [marketplace_manifest.as_posix()],
                    "issues": [f"{marketplace_manifest.as_posix()}: plugins must be a list"],
                }

            for item in plugins:
                if not isinstance(item, dict) or item.get("name") != plugin_name:
                    continue
                source = item.get("source")
                path_value = source.get("path") if isinstance(source, dict) else None
                if not isinstance(path_value, str) or not path_value.startswith("./"):
                    return {
                        "present": True,
                        "content_ready": False,
                        "active_root": None,
                        "inspected_roots": [marketplace_manifest.as_posix()],
                        "issues": [f"{marketplace_manifest.as_posix()}: local source path must start with ./"],
                    }
                relative = path_value.removeprefix("./")
                if not relative or any(part in {"", ".", ".."} for part in Path(relative).parts):
                    return {
                        "present": True,
                        "content_ready": False,
                        "active_root": None,
                        "inspected_roots": [marketplace_manifest.as_posix()],
                        "issues": [f"{marketplace_manifest.as_posix()}: local source path must stay within marketplace root"],
                    }
                plugin_root = marketplace_root / relative
                inspected = [marketplace_manifest.as_posix(), plugin_root.as_posix()]
                if not plugin_root.is_dir():
                    return {
                        "present": True,
                        "content_ready": False,
                        "active_root": None,
                        "inspected_roots": inspected,
                        "issues": [f"{plugin_root.as_posix()}: marketplace local source path is not a directory"],
                    }
                ok, issues = _plugin_root_content_status(plugin_root)
                return {
                    "present": True,
                    "content_ready": ok,
                    "active_root": plugin_root.as_posix() if ok else None,
                    "inspected_roots": inspected,
                    "issues": issues,
                }

            return {
                "present": True,
                "content_ready": False,
                "active_root": None,
                "inspected_roots": [marketplace_manifest.as_posix()],
                "issues": [f"{marketplace_manifest.as_posix()}: plugin is missing from Codex marketplace manifest"],
            }

        codex_marketplace_ready: list[dict[str, Any]] = []
        codex_marketplace_failures: list[dict[str, Any]] = []
        for cache_root in cache_roots:
            for market in deduped_candidates:
                marketplace_status = _codex_marketplace_root_status(cache_root / market)
                if marketplace_status is None:
                    continue
                if marketplace_status["content_ready"]:
                    codex_marketplace_ready.append(marketplace_status)
                    continue
                codex_marketplace_failures.append(marketplace_status)
        if codex_marketplace_failures:
            for failure in codex_marketplace_failures:
                inspected_roots.extend(failure["inspected_roots"])
                missing_reasons.extend(failure["issues"])
            return {
                "present": True,
                "content_ready": False,
                "active_root": None,
                "inspected_roots": inspected_roots,
                "issues": missing_reasons,
            }
        if codex_marketplace_ready:
            return codex_marketplace_ready[0]

        for cache_root in cache_roots:
            for market in deduped_candidates:
                plugin_base = cache_root / market / plugin_name
                if not plugin_base.exists():
                    continue
                for plugin_root in _candidate_plugin_roots(plugin_base):
                    inspected_roots.append(plugin_root.as_posix())
                    ok, issues = _plugin_root_content_status(plugin_root)
                    if not ok:
                        missing_reasons.extend(issues)
                        continue
                    return {
                        "present": True,
                        "content_ready": True,
                        "active_root": plugin_root.as_posix(),
                        "inspected_roots": inspected_roots,
                        "issues": [],
                    }
        return {
            "present": bool(inspected_roots),
            "content_ready": False,
            "active_root": None,
            "inspected_roots": inspected_roots,
            "issues": missing_reasons or ["plugin cache root not found"],
        }

    marketplace_name = _normalized_marketplace_name(marketplace.get("name"))
    entries = marketplace.get("plugins", [])
    by_name = {}
    if isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if isinstance(name, str) and name.strip():
                by_name[name.strip()] = item

    plugin_rows = []
    for item in installed:
        name = item.get("name")
        workspace_plugin_path = item.get("path")
        plugin_path = Path(str(workspace_plugin_path or ""))
        if not plugin_path.is_absolute():
            plugin_path = repo_root / plugin_path
        is_repo_managed = not _is_external_cached_plugin(repo_root, plugin_path) and not _is_external_plugin_path(
            repo_root, plugin_path
        )
        entry = by_name.get(name)
        cache_status = (
            _cache_status(
                plugin_name=str(name),
                marketplace_name=marketplace_name,
                entry=entry if isinstance(entry, dict) else None,
            )
            if isinstance(name, str) and name
            else {
                "present": False,
                "content_ready": False,
                "active_root": None,
                "inspected_roots": [],
                "issues": ["plugin name unavailable"],
            }
        )
        plugin_rows.append(
            {
                "name": name,
                "marketplace_name": marketplace_name,
                "registered_in_marketplace": bool(entry),
                "marketplace_source_path": (
                    ((entry.get("source") or {}).get("path")) if isinstance(entry, dict) else None
                ),
                "workspace_plugin_path": workspace_plugin_path,
                "repo_managed": is_repo_managed,
                "cache_present": bool(cache_status["present"]),
                "cache_content_ready": bool(cache_status["content_ready"]),
                "cache_active_root": cache_status["active_root"],
                "cache_issues": cache_status["issues"],
            }
        )

    return {
        "plugin_count": len(plugin_rows),
        "plugins": plugin_rows,
    }


def _codex_profile_homes() -> list[Path]:
    home = Path.home()
    profile_homes: list[Path] = []
    default_home = home / ".codex"
    if default_home.exists():
        profile_homes.append(default_home)
    profile_homes.extend(sorted(path for path in home.glob(".codex-*") if path.is_dir()))
    return profile_homes


def _enabled_plugin_ids(config_path: Path) -> tuple[set[str], str | None]:
    if not config_path.exists():
        return set(), None
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return set(), f"failed to read active config: {exc}"
    except tomllib.TOMLDecodeError as exc:
        return set(), f"failed to parse active config: {exc}"

    enabled: set[str] = set()
    plugins = payload.get("plugins")
    if not isinstance(plugins, dict):
        return enabled, None
    for plugin_id, plugin_config in plugins.items():
        if isinstance(plugin_id, str) and isinstance(plugin_config, dict) and plugin_config.get("enabled") is True:
            enabled.add(plugin_id)
    return enabled, None


def _profile_marketplace_plugin_status(
    *,
    profile_home: Path,
    marketplace_path: Path,
    plugin_name: str,
    expected_resolved_path: Path | None = None,
    require_symlink: bool = False,
) -> dict[str, Any]:
    def _marketplace_root() -> Path:
        try:
            relative = marketplace_path.relative_to(profile_home)
        except ValueError:
            return marketplace_path.parent
        if relative == Path(".agents/plugins/marketplace.json"):
            return profile_home
        if relative == Path(".claude-plugin/marketplace.json"):
            return profile_home
        if relative in {Path("Plugins/marketplace.json"), Path("plugins/marketplace.json")}:
            return profile_home
        return marketplace_path.parent

    payload, error = _load_json(marketplace_path)
    if payload is None:
        return {
            "ok": False,
            "marketplace_path": marketplace_path.as_posix(),
            "source_path": None,
            "resolved_path": None,
            "issues": [f"{marketplace_path.as_posix()}: {error}"],
        }
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        return {
            "ok": False,
            "marketplace_path": marketplace_path.as_posix(),
            "source_path": None,
            "resolved_path": None,
            "issues": [f"{marketplace_path.as_posix()}: plugins must be a list"],
        }
    for item in plugins:
        if not isinstance(item, dict) or item.get("name") != plugin_name:
            continue
        source = item.get("source")
        path_value = source.get("path") if isinstance(source, dict) else None
        if not isinstance(path_value, str) or not path_value.startswith("./"):
            return {
                "ok": False,
                "marketplace_path": marketplace_path.as_posix(),
                "source_path": path_value,
                "resolved_path": None,
                "issues": [f"{marketplace_path.as_posix()}: local source path must start with ./"],
            }
        relative = path_value.removeprefix("./")
        if not relative or any(part in {"", ".", ".."} for part in Path(relative).parts):
            return {
                "ok": False,
                "marketplace_path": marketplace_path.as_posix(),
                "source_path": path_value,
                "resolved_path": None,
                "issues": [f"{marketplace_path.as_posix()}: local source path must stay within marketplace root"],
            }
        plugin_root = _marketplace_root() / relative
        issues: list[str] = []
        if not plugin_root.is_dir():
            issues.append(f"{plugin_root.as_posix()}: marketplace local source path is not a directory")
        else:
            if require_symlink and not plugin_root.is_symlink():
                issues.append(f"{plugin_root.as_posix()}: compatibility plugin path must be a symlink alias")
            if expected_resolved_path is not None:
                try:
                    actual_resolved = plugin_root.resolve(strict=True)
                    expected_resolved = expected_resolved_path.resolve(strict=True)
                except OSError as exc:
                    issues.append(f"{plugin_root.as_posix()}: failed to resolve plugin alias: {exc}")
                else:
                    if actual_resolved != expected_resolved:
                        issues.append(
                            f"{plugin_root.as_posix()}: resolves to {actual_resolved.as_posix()} "
                            f"but expected {expected_resolved.as_posix()}"
                        )
            ok, content_issues = _plugin_root_content_status(plugin_root)
            issues.extend(content_issues if not ok else [])
        return {
            "ok": not issues,
            "marketplace_path": marketplace_path.as_posix(),
            "source_path": path_value,
            "resolved_path": plugin_root.as_posix(),
            "resolved_realpath": plugin_root.resolve().as_posix() if plugin_root.exists() else None,
            "is_symlink": plugin_root.is_symlink(),
            "issues": issues,
        }
    return {
        "ok": False,
        "marketplace_path": marketplace_path.as_posix(),
        "source_path": None,
        "resolved_path": None,
        "issues": [f"{marketplace_path.as_posix()}: plugin is missing from profile marketplace"],
    }


def _desktop_readiness_state(
    *,
    marketplace: dict[str, Any],
    activation: dict[str, Any],
    plugin_name: str | None,
) -> dict[str, Any]:
    marketplace_name = str(marketplace.get("name") or "agent-skills-local").strip() or "agent-skills-local"
    entries = marketplace.get("plugins", [])
    allowed_plugin_ids = {
        f"{item.get('name')}@{marketplace_name}"
        for item in entries
        if isinstance(item, dict) and isinstance(item.get("name"), str) and item.get("name")
    }
    default_profile_home = Path.home() / ".codex"
    personal_marketplace_path = Path.home() / ".agents" / "plugins" / "marketplace.json"
    profile_homes = _codex_profile_homes()
    personal_marketplace_payload, _personal_marketplace_error = _load_json(personal_marketplace_path)
    if personal_marketplace_payload is not None:
        personal_marketplace_name = str(personal_marketplace_payload.get("name") or marketplace_name).strip() or marketplace_name
        personal_plugins = personal_marketplace_payload.get("plugins")
        if isinstance(personal_plugins, list):
            for item in personal_plugins:
                if isinstance(item, dict) and isinstance(item.get("name"), str) and item.get("name"):
                    allowed_plugin_ids.add(f"{item.get('name')}@{personal_marketplace_name}")
    for profile_home in profile_homes:
        for relative_root in _LOCAL_PLUGIN_MARKETPLACE_ROOTS:
            profile_marketplace = profile_home / relative_root / "marketplace.json"
            payload, _error = _load_json(profile_marketplace)
            if payload is None:
                continue
            profile_marketplace_name = str(payload.get("name") or marketplace_name).strip() or marketplace_name
            profile_plugins = payload.get("plugins")
            if not isinstance(profile_plugins, list):
                continue
            for item in profile_plugins:
                if isinstance(item, dict) and isinstance(item.get("name"), str) and item.get("name"):
                    allowed_plugin_ids.add(f"{item.get('name')}@{profile_marketplace_name}")
    config_path = Path.home() / ".codex" / "config.toml"
    enabled_ids, config_error = _enabled_plugin_ids(config_path)
    stale_enabled_ids = sorted(
        plugin_id
        for plugin_id in enabled_ids
        if plugin_id.endswith(f"@{marketplace_name}") and plugin_id not in allowed_plugin_ids
    )

    plugin_rows: list[dict[str, Any]] = []
    for activation_row in activation.get("plugins", []):
        name = activation_row.get("name")
        if not isinstance(name, str) or not name:
            continue
        if plugin_name and name != plugin_name:
            continue
        expected_id = f"{name}@{marketplace_name}"
        personal_marketplace_check = (
            _profile_marketplace_plugin_status(
                profile_home=Path.home(),
                marketplace_path=personal_marketplace_path,
                plugin_name=name,
            )
            if personal_marketplace_path.exists()
            else {
                "ok": False,
                "marketplace_path": personal_marketplace_path.as_posix(),
                "source_path": None,
                "resolved_path": None,
                "resolved_realpath": None,
                "is_symlink": False,
                "issues": ["personal marketplace manifest is missing"],
            }
        )
        expected_plugin_realpath = (
            Path(str(personal_marketplace_check["resolved_path"]))
            if personal_marketplace_check.get("ok") and personal_marketplace_check.get("resolved_path")
            else None
        )
        profile_rows: list[dict[str, Any]] = []
        for profile_home in profile_homes:
            marketplace_candidates = [
                profile_home / ".agents" / "plugins" / "marketplace.json",
                profile_home / "Plugins" / "marketplace.json",
                profile_home / "plugins" / "marketplace.json",
            ]
            candidate_rows = [
                _profile_marketplace_plugin_status(
                    profile_home=profile_home,
                    marketplace_path=marketplace_path,
                    plugin_name=name,
                    expected_resolved_path=expected_plugin_realpath,
                    require_symlink=marketplace_path.parent != profile_home / "plugins",
                )
                for marketplace_path in marketplace_candidates
                if marketplace_path.exists()
            ]
            ok_rows = [row for row in candidate_rows if row["ok"]]
            issues = [issue for row in candidate_rows for issue in row.get("issues", [])]
            profile_rows.append(
                {
                    "profile_home": profile_home.as_posix(),
                    "ok": bool(ok_rows),
                    "marketplaces_checked": [row["marketplace_path"] for row in candidate_rows],
                    "active_marketplace_path": ok_rows[0]["marketplace_path"] if ok_rows else None,
                    "source_path": ok_rows[0]["source_path"] if ok_rows else None,
                    "resolved_path": ok_rows[0]["resolved_path"] if ok_rows else None,
                    "resolved_realpath": ok_rows[0].get("resolved_realpath") if ok_rows else None,
                    "is_symlink": ok_rows[0].get("is_symlink") if ok_rows else False,
                    "issues": [] if ok_rows else issues or ["profile has no plugin marketplace manifest"],
                }
            )

        active_profile_rows = [row for row in profile_rows if row["profile_home"] == default_profile_home.as_posix()]
        config_ready = config_error is None and expected_id in enabled_ids and not stale_enabled_ids
        personal_marketplace_ready = bool(personal_marketplace_check["ok"])
        profile_ready = bool(active_profile_rows) and active_profile_rows[0]["ok"]
        loadable = (
            bool(activation_row.get("cache_content_ready"))
            and config_ready
            and personal_marketplace_ready
            and profile_ready
        )
        blocker_codes: list[str] = []
        if not activation_row.get("cache_content_ready"):
            blocker_codes.append("PLUGIN_RUNTIME_CONTENT_MISSING")
        if config_error is not None:
            blocker_codes.append("PLUGIN_ACTIVE_CONFIG_UNREADABLE")
        if expected_id not in enabled_ids:
            blocker_codes.append("PLUGIN_NOT_ENABLED_IN_ACTIVE_CONFIG")
        if stale_enabled_ids:
            blocker_codes.append("PLUGIN_ACTIVE_CONFIG_STALE_IDS")
        if not default_profile_home.is_dir():
            blocker_codes.append("PLUGIN_CODEX_PROFILE_HOME_MISSING")
        elif not profile_ready:
            blocker_codes.append("PLUGIN_PROFILE_MIRROR_NOT_READY")
        if not personal_marketplace_ready:
            blocker_codes.append("PLUGIN_PERSONAL_MARKETPLACE_NOT_READY")
        plugin_rows.append(
            {
                "name": name,
                "plugin_id": expected_id,
                "desktop_loadable": loadable,
                "cache_ready": bool(activation_row.get("cache_content_ready")),
                "active_config_ready": config_ready,
                "personal_marketplace_ready": personal_marketplace_ready,
                "personal_marketplace_check": personal_marketplace_check,
                "profile_mirror_ready": profile_ready,
                "active_profile_home": default_profile_home.as_posix(),
                "profile_homes": [path.as_posix() for path in profile_homes],
                "profile_checks": profile_rows,
                "blockers": blocker_codes,
                "repair_commands": [
                    "./bin/ask skills sync --scope workspace --plugin-cache-refresh only --json --robot",
                    "./bin/ask plugins sync-local-runtime --json --robot",
                    "./bin/ask plugins prune-stale-config --json --robot",
                    f"./bin/ask plugins status {name} --json --robot",
                ],
            }
        )

    all_loadable = bool(plugin_rows) and all(row["desktop_loadable"] for row in plugin_rows)
    all_blockers = sorted({blocker for row in plugin_rows for blocker in row.get("blockers", [])})
    return {
        "contract": "plugin-desktop-readiness.v1",
        "status": "loadable" if all_loadable else "blocked",
        "desktop_loadable": all_loadable,
        "marketplace_name": marketplace_name,
        "config_path": config_path.as_posix(),
        "config_readable": config_error is None,
        "config_error": config_error,
        "enabled_plugin_ids": sorted(enabled_ids),
        "allowed_plugin_ids": sorted(allowed_plugin_ids),
        "stale_enabled_plugin_ids": stale_enabled_ids,
        "active_profile_home": default_profile_home.as_posix(),
        "profile_homes": [path.as_posix() for path in profile_homes],
        "plugins": plugin_rows,
        "blockers": all_blockers,
    }


def _run_shadowing_check(repo_root: Path) -> dict[str, Any]:
    cmd = ["bash", "Infrastructure/scripts/validation-and-linting/check_plugin_skill_shadowing.sh", "--repo-root", str(repo_root)]
    proc = subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True, check=False)
    stdout_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in proc.stderr.splitlines() if line.strip()]
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": stdout_lines[-8:],
        "stderr_tail": stderr_lines[-8:],
    }


def _is_nonempty_markdown(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(content.strip())


def _missing_or_blank_fields(payload: dict[str, Any], required_fields: tuple[str, ...]) -> list[str]:
    return [field for field in required_fields if payload.get(field) in (None, "")]


def _local_asset_warning(plugin_path: Path, asset_key: str, asset_ref: str) -> str | None:
    if asset_ref.startswith("http://") or asset_ref.startswith("https://"):
        return None

    plugin_root = plugin_path.resolve()
    asset_path = (plugin_path / asset_ref).resolve()
    try:
        asset_path.relative_to(plugin_root)
    except ValueError:
        return f"referenced asset escapes plugin root: interface.{asset_key} -> {asset_ref}"

    if not asset_path.exists():
        return f"referenced asset missing: interface.{asset_key} -> {asset_ref}"
    return None


def _is_external_cached_plugin(repo_root: Path, plugin_path: Path) -> bool:
    """
    Return True when plugin_path is a mirrored bundled/curated cache snapshot.
    """
    cache_root = (repo_root / "plugins" / "cache").resolve()
    try:
        rel = plugin_path.resolve().relative_to(cache_root)
    except ValueError:
        return False
    if not rel.parts:
        return False
    return rel.parts[0] in {"openai-curated", "openai-bundled"}


def _is_external_plugin_path(repo_root: Path, plugin_path: Path) -> bool:
    """
    Return True when plugin_path resolves outside the repository root.
    """
    try:
        plugin_path.resolve().relative_to(repo_root.resolve())
        return False
    except ValueError:
        return True


def _package_quality_check(repo_root: Path, installed: list[dict[str, Any]]) -> dict[str, Any]:
    required_manifest_fields = ("schema_version", "name", "version", "description", "interface")
    required_interface_fields = (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "websiteURL",
        "defaultPrompt",
    )

    plugin_rows: list[dict[str, Any]] = []
    has_failures = False

    for plugin in installed:
        plugin_name = str(plugin.get("name") or "unknown")
        plugin_path = repo_root / str(plugin.get("path") or "")
        manifest_path = repo_root / str(plugin.get("manifest_path") or "")
        is_external_cache = _is_external_cached_plugin(repo_root, plugin_path)
        is_external_path = _is_external_plugin_path(repo_root, plugin_path)
        is_repo_managed = not is_external_cache and not is_external_path

        issues: list[str] = []
        warnings: list[str] = []

        readme_path = plugin_path / "README.md"
        if not _is_nonempty_markdown(readme_path):
            warnings.append("README missing or empty")

        manifest_payload, manifest_error = _load_json(manifest_path)
        if manifest_payload is None:
            message = f"manifest unavailable for quality checks: {manifest_error}"
            if is_repo_managed:
                issues.append(message)
            else:
                warnings.append(f"{message} (allowed for external plugin)")
        else:
            missing_manifest_fields = _missing_or_blank_fields(manifest_payload, required_manifest_fields)
            if missing_manifest_fields:
                message = f"manifest missing core fields: {', '.join(missing_manifest_fields)}"
                if is_repo_managed:
                    issues.append(message)
                else:
                    warnings.append(f"{message} (allowed for external plugin)")

            interface_payload = manifest_payload.get("interface")
            if not isinstance(interface_payload, dict):
                message = "manifest interface payload is missing or invalid"
                if is_repo_managed:
                    issues.append(message)
                else:
                    warnings.append(f"{message} (allowed for external plugin)")
            else:
                missing_interface_fields = _missing_or_blank_fields(interface_payload, required_interface_fields)
                if missing_interface_fields:
                    message = f"manifest interface missing core fields: {', '.join(missing_interface_fields)}"
                    if is_repo_managed:
                        issues.append(message)
                    else:
                        warnings.append(f"{message} (allowed for external plugin)")

                for asset_key in ("composerIcon", "logo"):
                    asset_ref = interface_payload.get(asset_key)
                    if not isinstance(asset_ref, str) or not asset_ref.strip():
                        continue
                    warning = _local_asset_warning(plugin_path, asset_key, asset_ref)
                    if warning is not None:
                        warnings.append(warning)

        if issues:
            has_failures = True

        plugin_rows.append(
            {
                "name": plugin_name,
                "ok": not issues,
                "issues": issues,
                "warnings": warnings,
            }
        )

    return {
        "ok": not has_failures,
        "plugin_count": len(plugin_rows),
        "plugins": plugin_rows,
    }


def collect_plugin_state(
    repo_root: Path,
    *,
    plugin_name: str | None = None,
    run_doctor: bool = False,
) -> dict[str, Any]:
    installed = _installed_plugins(repo_root)
    marketplace, marketplace_error, marketplace_path = _marketplace_payload(repo_root)
    activation = _activation_state(repo_root=repo_root, installed=installed, marketplace=marketplace)

    if plugin_name:
        installed = [plugin for plugin in installed if plugin.get("name") == plugin_name]
        activation["plugins"] = [plugin for plugin in activation["plugins"] if plugin.get("name") == plugin_name]
        activation["plugin_count"] = len(activation["plugins"])
    desktop_readiness = _desktop_readiness_state(
        marketplace=marketplace,
        activation=activation,
        plugin_name=plugin_name,
    )

    blockers = []
    checks: dict[str, Any] = {
        "policy_identity": {"ok": True, "value": policy_identity()},
    }

    if marketplace_error:
        blockers.append("PLUGIN_STATE_UNAVAILABLE: marketplace metadata unavailable")
        checks["marketplace"] = {"ok": False, "error": marketplace_error}
    else:
        checks["marketplace"] = {
            "ok": True,
            "path": str(marketplace_path),
            "plugin_entries": len(marketplace.get("plugins", [])) if isinstance(marketplace.get("plugins"), list) else 0,
        }

    invalid_manifests = [item for item in installed if not item.get("manifest_valid", False)]
    if invalid_manifests:
        blockers.append("PLUGIN_STATE_UNAVAILABLE: one or more plugin manifests are invalid")
        checks["manifests"] = {
            "ok": False,
            "invalid_plugins": [item.get("name") for item in invalid_manifests],
        }
    else:
        checks["manifests"] = {"ok": True}

    activation_rows = activation.get("plugins", [])
    unregistered_plugins = (
        [
            str(item.get("name"))
            for item in activation_rows
            if item.get("name")
            and item.get("repo_managed")
            and not item.get("registered_in_marketplace")
        ]
        if not marketplace_error
        else []
    )
    missing_cache_plugins = [
        str(item.get("name"))
        for item in activation_rows
        if item.get("name") and item.get("repo_managed") and not item.get("cache_present")
    ]
    cache_content_blockers = [
        {
            "name": str(item.get("name")),
            "issues": item.get("cache_issues", []),
        }
        for item in activation_rows
        if item.get("name") and item.get("repo_managed") and not item.get("cache_content_ready")
    ]
    activation_warnings: list[str] = []
    if marketplace_error:
        activation_warnings.append(
            "Marketplace metadata failed to load; skipping plugin marketplace drift detection."
        )
    if missing_cache_plugins:
        activation_warnings.append(
            "Runtime cache is missing for one or more repo-managed plugins. "
            "Run bin/ask skills sync to mirror local plugin sources into cache."
        )
    if not marketplace_error and unregistered_plugins:
        blockers.append(
            "PLUGIN_MARKETPLACE_DRIFT: plugins missing from marketplace: "
            + ", ".join(sorted(unregistered_plugins))
        )
    if cache_content_blockers:
        blockers.append(
            "PLUGIN_RUNTIME_CONTENT_MISSING: installed plugin cache is missing manifest-declared contents: "
            + ", ".join(sorted(item["name"] for item in cache_content_blockers))
        )
    checks["activation"] = {
        "ok": not unregistered_plugins and not cache_content_blockers,
        "unregistered_plugins": sorted(unregistered_plugins),
        "missing_cache_plugins": sorted(missing_cache_plugins),
        "cache_content_blockers": cache_content_blockers,
        "warnings": activation_warnings,
    }

    if run_doctor:
        shadow_check = _run_shadowing_check(repo_root)
        checks["plugin_shadowing"] = shadow_check
        if not shadow_check["ok"]:
            blockers.append("PLUGIN_SKILL_SHADOWING: shadowing gate failed")
        package_quality = _package_quality_check(repo_root, installed)
        checks["plugin_package_quality"] = package_quality
        if not package_quality["ok"]:
            blockers.append("PLUGIN_PACKAGE_QUALITY: plugin package checks failed")

    return {
        "installed_state": {
            "plugin_count": len(installed),
            "plugins": installed,
        },
        "activation_state": activation,
        "desktop_readiness_state": desktop_readiness,
        "health_state": {
            "status": "healthy" if not blockers else "degraded",
            "blockers": blockers,
            "checks": checks,
        },
    }
