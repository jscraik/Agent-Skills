"""Read-only plugin state snapshots for ask plugin lifecycle commands."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT))
if str(SCRIPTS_ROOT / "lifecycle-and-sync") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "lifecycle-and-sync"))

from selection_policy import policy_identity


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
    installed: list[dict[str, Any]] = []
    resolved_repo_root = repo_root.resolve()
    seen_plugin_ids: set[tuple[int, int]] = set()
    manifest_patterns = (
        "plugins/*/.codex-plugin/plugin.json",
        "Plugins/*/.codex-plugin/plugin.json",
        "plugins/*/*/.codex-plugin/plugin.json",
        "Plugins/*/*/.codex-plugin/plugin.json",
    )

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
                        "path": plugin_dir_resolved.relative_to(resolved_repo_root).as_posix(),
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
                    "path": plugin_dir_resolved.relative_to(resolved_repo_root).as_posix(),
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

    def _cache_present(
        *,
        plugin_name: str,
        marketplace_name: str | None,
        entry: dict[str, Any] | None,
    ) -> bool:
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

        # Backward-compat fallback used by existing local plugin cache projections.
        candidates.append("agent-skills-local")

        deduped_candidates = tuple(dict.fromkeys(candidates))
        cache_roots = (
            repo_root / ".agents" / "plugins-runtime" / "cache",
            repo_root / "plugins" / "cache",
            repo_root / "Plugins" / "cache",
        )
        for cache_root in cache_roots:
            for market in deduped_candidates:
                if (cache_root / market / plugin_name).exists():
                    return True
        return False

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
        entry = by_name.get(name)
        cache_present = (
            _cache_present(
                plugin_name=str(name),
                marketplace_name=marketplace_name,
                entry=entry if isinstance(entry, dict) else None,
            )
            if isinstance(name, str) and name
            else False
        )
        plugin_rows.append(
            {
                "name": name,
                "marketplace_name": marketplace_name,
                "registered_in_marketplace": bool(entry),
                "marketplace_source_path": (
                    ((entry.get("source") or {}).get("path")) if isinstance(entry, dict) else None
                ),
                "workspace_plugin_path": item.get("path"),
                "cache_present": cache_present,
            }
        )

    return {
        "plugin_count": len(plugin_rows),
        "plugins": plugin_rows,
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

        issues: list[str] = []
        warnings: list[str] = []

        readme_path = plugin_path / "README.md"
        if not _is_nonempty_markdown(readme_path):
            warnings.append("README missing or empty")

        manifest_payload, manifest_error = _load_json(manifest_path)
        if manifest_payload is None:
            issues.append(f"manifest unavailable for quality checks: {manifest_error}")
        else:
            missing_manifest_fields = _missing_or_blank_fields(manifest_payload, required_manifest_fields)
            if missing_manifest_fields:
                issues.append(f"manifest missing core fields: {', '.join(missing_manifest_fields)}")

            interface_payload = manifest_payload.get("interface")
            if not isinstance(interface_payload, dict):
                issues.append("manifest interface payload is missing or invalid")
            else:
                missing_interface_fields = _missing_or_blank_fields(interface_payload, required_interface_fields)
                if missing_interface_fields:
                    issues.append(f"manifest interface missing core fields: {', '.join(missing_interface_fields)}")

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
        "health_state": {
            "status": "healthy" if not blockers else "degraded",
            "blockers": blockers,
            "checks": checks,
        },
    }
