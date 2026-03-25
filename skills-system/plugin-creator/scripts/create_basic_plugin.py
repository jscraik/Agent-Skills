#!/usr/bin/env python3
"""Scaffold a lifecycle-aware plugin directory and optionally update marketplace.json."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


MAX_PLUGIN_NAME_LENGTH = 64
DEFAULT_PLUGIN_PARENT = Path.cwd() / "plugins"
DEFAULT_MARKETPLACE_PATH = Path.cwd() / ".agents" / "plugins" / "marketplace.json"
DEFAULT_INSTALL_POLICY = "AVAILABLE"
DEFAULT_AUTH_POLICY = "ON_INSTALL"
DEFAULT_CATEGORY = "Productivity"
DEFAULT_MARKETPLACE_DISPLAY_NAME = "Local Plugins"
DEFAULT_VERSION = "0.1.0"
DEFAULT_LIFECYCLE_STATE = "incubating"
DEFAULT_MATURITY = "experimental"
VALID_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
VALID_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
VALID_LIFECYCLE_STATES = {"incubating", "active", "maintenance", "deprecated"}
VALID_MATURITY_LEVELS = {"experimental", "validated", "canonical"}


def normalize_plugin_name(plugin_name: str) -> str:
    """Normalize a plugin name to lowercase hyphen-case."""
    normalized = plugin_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def validate_plugin_name(plugin_name: str) -> None:
    if not plugin_name:
        raise ValueError("Plugin name must include at least one letter or digit.")
    if len(plugin_name) > MAX_PLUGIN_NAME_LENGTH:
        raise ValueError(
            f"Plugin name '{plugin_name}' is too long ({len(plugin_name)} characters). "
            f"Maximum is {MAX_PLUGIN_NAME_LENGTH} characters."
        )


def plugin_display_name(plugin_name: str) -> str:
    return " ".join(part.capitalize() for part in plugin_name.split("-"))


def build_plugin_json(
    plugin_name: str,
    description: str,
    owner: str,
    review_cadence: str,
    last_reviewed: str,
    lifecycle_state: str,
    maturity: str,
    category: str,
    with_skills: bool,
    with_hooks: bool,
    with_mcp: bool,
    with_apps: bool,
) -> dict:
    display_name = plugin_display_name(plugin_name)
    payload = {
        "schema_version": 1,
        "name": plugin_name,
        "version": DEFAULT_VERSION,
        "description": description,
        "author": {
            "name": owner,
        },
        "license": "MIT",
        "keywords": ["plugin", plugin_name, "incubating"],
        "governance": {
            "lifecycle_state": lifecycle_state,
            "maturity": maturity,
            "owner": owner,
            "review_cadence": review_cadence,
            "last_reviewed": last_reviewed,
            "metadata_source": "plugin_manifest",
        },
        "interface": {
            "displayName": display_name,
            "shortDescription": description,
            "longDescription": (
                f"Incubating plugin scaffold for {display_name}. "
                "Replace this starter metadata before treating the plugin as active."
            ),
            "developerName": owner,
            "category": category,
            "capabilities": ["Interactive", "Read"],
            "defaultPrompt": [
                f"Help me evaluate whether {display_name} is ready to move beyond incubating."
            ],
            "brandColor": "#3B82F6",
        },
    }
    if with_skills:
        payload["skills"] = "./skills/"
    if with_hooks:
        payload["hooks"] = "./hooks.json"
    if with_mcp:
        payload["mcpServers"] = "./.mcp.json"
    if with_apps:
        payload["apps"] = "./.app.json"
    return payload


def build_marketplace_entry(
    plugin_name: str,
    install_policy: str,
    auth_policy: str,
    category: str,
) -> dict[str, Any]:
    return {
        "name": plugin_name,
        "source": {
            "source": "local",
            "path": f"./plugins/{plugin_name}",
        },
        "policy": {
            "installation": install_policy,
            "authentication": auth_policy,
        },
        "category": category,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def build_default_marketplace() -> dict[str, Any]:
    return {
        "name": "[TODO: marketplace-name]",
        "interface": {
            "displayName": DEFAULT_MARKETPLACE_DISPLAY_NAME,
        },
        "plugins": [],
    }


def validate_marketplace_interface(payload: dict[str, Any]) -> None:
    interface = payload.get("interface")
    if interface is not None and not isinstance(interface, dict):
        raise ValueError("marketplace.json field 'interface' must be an object.")


def update_marketplace_json(
    marketplace_path: Path,
    plugin_name: str,
    install_policy: str,
    auth_policy: str,
    category: str,
    force: bool,
) -> None:
    if marketplace_path.exists():
        payload = load_json(marketplace_path)
    else:
        payload = build_default_marketplace()

    if not isinstance(payload, dict):
        raise ValueError(f"{marketplace_path} must contain a JSON object.")

    validate_marketplace_interface(payload)

    plugins = payload.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError(f"{marketplace_path} field 'plugins' must be an array.")

    new_entry = build_marketplace_entry(plugin_name, install_policy, auth_policy, category)

    for index, entry in enumerate(plugins):
        if isinstance(entry, dict) and entry.get("name") == plugin_name:
            if not force:
                raise FileExistsError(
                    f"Marketplace entry '{plugin_name}' already exists in {marketplace_path}. "
                    "Use --force to overwrite that entry."
                )
            plugins[index] = new_entry
            break
    else:
        plugins.append(new_entry)

    write_json(marketplace_path, payload, force=True)


def write_json(path: Path, data: dict, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists. Use --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def create_stub_file(path: Path, payload: dict, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a lifecycle-aware plugin skeleton with honest starter metadata."
    )
    parser.add_argument("plugin_name")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Parent directory for plugin creation (defaults to <cwd>/plugins)",
    )
    parser.add_argument("--with-skills", action="store_true", help="Create skills/ directory")
    parser.add_argument("--with-hooks", action="store_true", help="Create hooks/ directory")
    parser.add_argument("--with-scripts", action="store_true", help="Create scripts/ directory")
    parser.add_argument("--with-assets", action="store_true", help="Create assets/ directory")
    parser.add_argument("--with-mcp", action="store_true", help="Create .mcp.json placeholder")
    parser.add_argument("--with-apps", action="store_true", help="Create .app.json placeholder")
    parser.add_argument(
        "--with-marketplace",
        action="store_true",
        help="Create or update <cwd>/.agents/plugins/marketplace.json",
    )
    parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json (defaults to <cwd>/.agents/plugins/marketplace.json)",
    )
    parser.add_argument(
        "--install-policy",
        default=DEFAULT_INSTALL_POLICY,
        choices=sorted(VALID_INSTALL_POLICIES),
        help="Marketplace policy.installation value",
    )
    parser.add_argument(
        "--auth-policy",
        default=DEFAULT_AUTH_POLICY,
        choices=sorted(VALID_AUTH_POLICIES),
        help="Marketplace policy.authentication value",
    )
    parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help="Marketplace category value",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Short plugin description used in the manifest and interface block",
    )
    parser.add_argument(
        "--owner",
        required=True,
        help="Primary maintainer or owner string for lifecycle governance",
    )
    parser.add_argument(
        "--review-cadence",
        required=True,
        help="Concrete review cadence such as monthly or quarterly",
    )
    parser.add_argument(
        "--last-reviewed",
        default=date.today().isoformat(),
        help="ISO date for the most recent lifecycle review (defaults to today)",
    )
    parser.add_argument(
        "--lifecycle-state",
        default=DEFAULT_LIFECYCLE_STATE,
        choices=sorted(VALID_LIFECYCLE_STATES),
        help="Initial lifecycle state for the plugin",
    )
    parser.add_argument(
        "--maturity",
        default=DEFAULT_MATURITY,
        choices=sorted(VALID_MATURITY_LEVELS),
        help="Initial maturity level for the plugin",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_plugin_name = args.plugin_name
    plugin_name = normalize_plugin_name(raw_plugin_name)
    if plugin_name != raw_plugin_name:
        print(f"Note: Normalized plugin name from '{raw_plugin_name}' to '{plugin_name}'.")
    validate_plugin_name(plugin_name)

    plugin_root = (Path(args.path).expanduser().resolve() / plugin_name)
    plugin_root.mkdir(parents=True, exist_ok=True)

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    write_json(
        plugin_json_path,
        build_plugin_json(
            plugin_name,
            args.description,
            args.owner,
            args.review_cadence,
            args.last_reviewed,
            args.lifecycle_state,
            args.maturity,
            args.category,
            args.with_skills,
            args.with_hooks,
            args.with_mcp,
            args.with_apps,
        ),
        args.force,
    )

    optional_directories = {
        "skills": args.with_skills,
        "hooks": args.with_hooks,
        "scripts": args.with_scripts,
        "assets": args.with_assets,
    }
    for folder, enabled in optional_directories.items():
        if enabled:
            (plugin_root / folder).mkdir(parents=True, exist_ok=True)

    if args.with_mcp:
        create_stub_file(
            plugin_root / ".mcp.json",
            {"mcpServers": {}},
            args.force,
        )

    if args.with_apps:
        create_stub_file(
            plugin_root / ".app.json",
            {
                "apps": {},
            },
            args.force,
        )

    marketplace_path: Path | None = None
    if args.with_marketplace:
        marketplace_path = Path(args.marketplace_path).expanduser().resolve()
        update_marketplace_json(
            marketplace_path,
            plugin_name,
            args.install_policy,
            args.auth_policy,
            args.category,
            args.force,
        )

    print(f"Created plugin scaffold: {plugin_root}")
    print(f"plugin manifest: {plugin_json_path}")
    if marketplace_path is not None:
        print(f"marketplace manifest: {marketplace_path}")


if __name__ == "__main__":
    main()
