#!/usr/bin/env python3
"""Scaffold a plugin directory and optionally update marketplace.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Optional


MAX_PLUGIN_NAME_LENGTH = 64
DEFAULT_PLUGIN_PARENT = Path.cwd() / "plugins"
DEFAULT_MARKETPLACE_PATH = Path.cwd() / ".agents" / "plugins" / "marketplace.json"
DEFAULT_INSTALL_POLICY = "AVAILABLE"
DEFAULT_AUTH_POLICY = "ON_INSTALL"
DEFAULT_CATEGORY = "Productivity"
DEFAULT_MARKETPLACE_DISPLAY_NAME = "[TODO: Marketplace Display Name]"
VALID_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
VALID_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
VALID_POLICY_PRODUCTS = {"CHATGPT", "CODEX", "ATLAS"}
DEFAULT_POLICY_PRODUCTS = ["CODEX"]
OPENAI_MARKETPLACE_RELATIVE_PATH = ".agents/plugins/marketplace.json"
LEGACY_MARKETPLACE_RELATIVE_PATH = "plugins/marketplace.json"


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
    if not re.fullmatch(r"[a-z0-9](?:-?[a-z0-9]){0,63}", plugin_name):
        raise ValueError(
            "Plugin name must be kebab-case and match "
            "`[a-z0-9](?:-?[a-z0-9]){0,63}`."
        )


def build_plugin_json(plugin_name: str) -> dict:
    return {
        "name": plugin_name,
        "version": "[TODO: 1.2.0]",
        "description": "[TODO: Brief plugin description]",
        "author": {
            "name": "[TODO: Author Name]",
            "email": "[TODO: author@example.com]",
            "url": "[TODO: https://github.com/author]",
        },
        "homepage": "[TODO: https://docs.example.com/plugin]",
        "repository": "[TODO: https://github.com/author/plugin]",
        "license": "[TODO: MIT]",
        "keywords": ["[TODO: keyword1]", "[TODO: keyword2]"],
        "skills": "[TODO: ./skills/]",
        "hooks": "[TODO: ./hooks.json]",
        "mcpServers": "[TODO: ./.mcp.json]",
        "apps": "[TODO: ./.app.json]",
        "interface": {
            "displayName": "[TODO: Plugin Display Name]",
            "shortDescription": "[TODO: Short description for subtitle]",
            "longDescription": "[TODO: Long description for details page]",
            "developerName": "[TODO: OpenAI]",
            "category": "[TODO: Productivity]",
            "capabilities": ["[TODO: Interactive]", "[TODO: Write]"],
            "websiteURL": "[TODO: https://openai.com/]",
            "privacyPolicyURL": "[TODO: https://openai.com/policies/row-privacy-policy/]",
            "termsOfServiceURL": "[TODO: https://openai.com/policies/row-terms-of-use/]",
            "defaultPrompt": [
                "[TODO: Summarize my inbox and draft replies for me.]",
                "[TODO: Find open bugs and turn them into tickets.]",
                "[TODO: Review today's meetings and flag gaps.]",
            ],
            "brandColor": "[TODO: #3B82F6]",
            "composerIcon": "[TODO: ./assets/icon.png]",
            "logo": "[TODO: ./assets/logo.png]",
            "screenshots": [
                "[TODO: ./assets/screenshot1.png]",
                "[TODO: ./assets/screenshot2.png]",
                "[TODO: ./assets/screenshot3.png]",
            ],
        },
    }


def build_marketplace_entry(
    plugin_name: str,
    plugin_root: Path,
    marketplace_path: Path,
    install_policy: str,
    auth_policy: str,
    policy_products: list[str],
    category: str,
    *,
    allow_legacy_marketplace_path: bool,
) -> dict[str, Any]:
    return {
        "name": plugin_name,
        "source": {
            "source": "local",
            "path": _relative_repo_source_path(
                plugin_root,
                marketplace_path,
                allow_legacy_marketplace_path=allow_legacy_marketplace_path,
            ),
        },
        "policy": {
            "installation": install_policy,
            "authentication": auth_policy,
            "products": policy_products,
        },
        "category": category,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_policy_products(raw_products: Any) -> tuple[list[str], list[str]]:
    if raw_products is None:
        return [], []
    if not isinstance(raw_products, list):
        return [], ["<non-list>"]

    normalized: list[str] = []
    invalid: list[str] = []
    for value in raw_products:
        if not isinstance(value, str) or not value.strip():
            invalid.append(str(value))
            continue
        token = value.strip().upper()
        if token not in VALID_POLICY_PRODUCTS:
            invalid.append(value.strip())
            continue
        if token not in normalized:
            normalized.append(token)
    return normalized, invalid


def _effective_policy_products(raw_products: list[str] | None) -> list[str]:
    candidates = raw_products or list(DEFAULT_POLICY_PRODUCTS)
    normalized, invalid = _normalize_policy_products(candidates)
    if invalid:
        raise ValueError(
            f"Invalid --product values {sorted(set(invalid))}. "
            f"Allowed values are {sorted(VALID_POLICY_PRODUCTS)}."
        )
    if not normalized:
        return list(DEFAULT_POLICY_PRODUCTS)
    return normalized


def _path_within_root(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _marketplace_repo_root(
    marketplace_path: Path,
    *,
    allow_legacy_marketplace_path: bool,
) -> Path:
    # Preserve lexical path components so ".agents/plugins/..." remains valid
    # even when ".agents/plugins" is a symlink to "plugins".
    absolute = marketplace_path.expanduser().absolute()
    if absolute.name != "marketplace.json":
        raise ValueError("marketplace path must end with 'marketplace.json'.")

    plugins_dir = absolute.parent
    if plugins_dir.name != "plugins":
        raise ValueError(
            "marketplace path must live under '.agents/plugins/' "
            "or legacy 'plugins/' directory."
        )

    dot_agents_or_root = plugins_dir.parent
    if dot_agents_or_root.name == ".agents":
        return dot_agents_or_root.parent.resolve()

    if allow_legacy_marketplace_path:
        return dot_agents_or_root.resolve()

    relative_path = absolute.as_posix()
    raise ValueError(
        f"OpenAI/Codex marketplace mode requires '{OPENAI_MARKETPLACE_RELATIVE_PATH}'. "
        f"Legacy path '{LEGACY_MARKETPLACE_RELATIVE_PATH}' is disabled by default. "
        f"Got '{relative_path}'. Pass --allow-legacy-marketplace-path to override."
    )


def _relative_repo_source_path(
    plugin_root: Path,
    marketplace_path: Path,
    *,
    allow_legacy_marketplace_path: bool,
) -> str:
    repo_root = _marketplace_repo_root(
        marketplace_path,
        allow_legacy_marketplace_path=allow_legacy_marketplace_path,
    )
    resolved_plugin_root = plugin_root.resolve()
    if not _path_within_root(repo_root, resolved_plugin_root):
        raise ValueError(
            f"Plugin root '{resolved_plugin_root}' must stay within repo root '{repo_root}'."
        )
    return f"./{resolved_plugin_root.relative_to(repo_root).as_posix()}"


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
    plugin_root: Path,
    install_policy: str,
    auth_policy: str,
    policy_products: list[str],
    category: str,
    force: bool,
    *,
    allow_legacy_marketplace_path: bool,
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

    new_entry = build_marketplace_entry(
        plugin_name,
        plugin_root,
        marketplace_path,
        install_policy,
        auth_policy,
        policy_products,
        category,
        allow_legacy_marketplace_path=allow_legacy_marketplace_path,
    )

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
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def create_stub_file(path: Path, payload: dict, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a plugin skeleton with placeholder plugin.json."
    )
    parser.add_argument("plugin_name")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help=(
            "Parent directory for plugin creation (defaults to <cwd>/plugins). "
            "When using a home-rooted marketplace, use <home>/plugins."
        ),
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
        help=(
            "Create or update marketplace.json. "
            "By default, OpenAI/Codex mode expects <root>/.agents/plugins/marketplace.json."
        ),
    )
    parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help=(
            "Path to marketplace.json (defaults to <cwd>/.agents/plugins/marketplace.json). "
            "For a home-rooted marketplace, use <home>/.agents/plugins/marketplace.json."
        ),
    )
    parser.add_argument(
        "--product",
        action="append",
        choices=sorted(VALID_POLICY_PRODUCTS),
        default=None,
        help=(
            "Marketplace policy.products value. Repeat for multiple products. "
            "Defaults to CODEX."
        ),
    )
    parser.add_argument(
        "--allow-legacy-marketplace-path",
        action="store_true",
        help=(
            "Allow legacy plugins/marketplace.json layout instead of strict "
            ".agents/plugins/marketplace.json."
        ),
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
    policy_products = _effective_policy_products(args.product)

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    write_json(plugin_json_path, build_plugin_json(plugin_name), args.force)

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

    marketplace_path: Optional[Path] = None
    if args.with_marketplace:
        marketplace_path = Path(args.marketplace_path).expanduser()
        update_marketplace_json(
            marketplace_path,
            plugin_name,
            plugin_root,
            args.install_policy,
            args.auth_policy,
            policy_products,
            args.category,
            args.force,
            allow_legacy_marketplace_path=bool(args.allow_legacy_marketplace_path),
        )

    print(f"Created plugin scaffold: {plugin_root}")
    print(f"plugin manifest: {plugin_json_path}")
    if marketplace_path is not None:
        print(f"marketplace manifest: {marketplace_path}")


if __name__ == "__main__":
    main()
