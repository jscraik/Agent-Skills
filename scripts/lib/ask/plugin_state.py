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
        repo_root / ".agents" / "plugins" / "marketplace.json",
        repo_root / "plugins" / "marketplace.json",
    ]
    for candidate in candidates:
        payload, error = _load_json(candidate)
        if payload is not None:
            return payload, None, candidate
        if candidate.exists():
            return {}, error, candidate
    return {}, f"marketplace not found in expected paths: {', '.join(str(p) for p in candidates)}", candidates[0]


def _installed_plugins(repo_root: Path) -> list[dict[str, Any]]:
    plugins_root = repo_root / "plugins"
    installed: list[dict[str, Any]] = []
    if not plugins_root.exists():
        return installed

    for manifest_path in sorted(plugins_root.glob("*/.codex-plugin/plugin.json")):
        # Guard against nested caches and fixtures.
        rel = manifest_path.relative_to(repo_root).as_posix()
        if rel.startswith("plugins/cache/"):
            continue
        plugin_dir = manifest_path.parent.parent
        payload, error = _load_json(manifest_path)
        if payload is None:
            installed.append(
                {
                    "name": plugin_dir.name,
                    "path": plugin_dir.relative_to(repo_root).as_posix(),
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
                "path": plugin_dir.relative_to(repo_root).as_posix(),
                "manifest_path": rel,
                "manifest_valid": True,
                "governance": payload.get("governance", {}),
            }
        )
    return installed


def _activation_state(
    *,
    repo_root: Path,
    installed: list[dict[str, Any]],
    marketplace: dict[str, Any],
) -> dict[str, Any]:
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
        plugin_rows.append(
            {
                "name": name,
                "registered_in_marketplace": bool(entry),
                "marketplace_source_path": (
                    ((entry.get("source") or {}).get("path")) if isinstance(entry, dict) else None
                ),
                "workspace_plugin_path": item.get("path"),
                "cache_present": (repo_root / "plugins" / "cache" / "agent-skills-local" / str(name)).exists(),
            }
        )

    return {
        "plugin_count": len(plugin_rows),
        "plugins": plugin_rows,
    }


def _run_shadowing_check(repo_root: Path) -> dict[str, Any]:
    cmd = ["bash", "scripts/check_plugin_skill_shadowing.sh", "--repo-root", str(repo_root)]
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
