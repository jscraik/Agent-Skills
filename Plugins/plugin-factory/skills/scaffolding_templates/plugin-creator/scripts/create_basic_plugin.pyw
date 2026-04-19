#!/usr/bin/env python3
"""Scaffold a plugin directory and optionally update marketplace.json."""

from __future__ import annotations

import argparse
from datetime import date
import json
import re
from pathlib import Path
from typing import Any


MAX_PLUGIN_NAME_LENGTH = 64
OPENAI_MARKETPLACE_RELATIVE_PATH = ".agents/Plugins/marketplace.json"
LEGACY_MARKETPLACE_RELATIVE_PATH = "Plugins/marketplace.json"


def _discover_repo_root() -> Path:
    """
    Locate the repository root directory based on the script's location.

    Searches the script's ancestor directories for a directory that qualifies as
    the repository root. A candidate is accepted if it contains a `plugins`
    directory and either a `.git` entry, or both a `.agents` directory and
    `Plugins/plugin-factory/skills`.

    Returns:
    	Path: Resolved path to the discovered repository root.

    Raises:
        RuntimeError: When repository root discovery fails.
    """
    def _plugins_roots(candidate: Path) -> tuple[Path, ...]:
        return (candidate / "Plugins", candidate / "plugins")

    def _looks_like_repo_root(candidate: Path) -> bool:
        if not any(path.is_dir() for path in _plugins_roots(candidate)):
            return False
        if (candidate / ".git").exists():
            return True
        has_factory = any((root / "plugin-factory" / "skills").is_dir() for root in _plugins_roots(candidate))
        return has_factory and (candidate / ".agents").is_dir()

    for ancestor in Path(__file__).resolve().parents:
        if _looks_like_repo_root(ancestor):
            return ancestor
    raise RuntimeError(
        "Unable to discover repository root from script location. "
        "Run from the canonical repository or pass explicit --path and --marketplace-path."
    )


REPO_ROOT: Path | None = None
DEFAULT_PLUGIN_PARENT: Path | None = None
DEFAULT_MARKETPLACE_PATH: Path | None = None


def _get_repo_root() -> Path:
    global REPO_ROOT
    if REPO_ROOT is None:
        REPO_ROOT = _discover_repo_root()
    return REPO_ROOT


def _get_default_plugin_parent() -> Path:
    return _get_repo_root() / "Plugins" / "third-party"


def _get_default_marketplace_path() -> Path:
    return _get_repo_root() / OPENAI_MARKETPLACE_RELATIVE_PATH
DEFAULT_INSTALL_POLICY = "AVAILABLE"
DEFAULT_AUTH_POLICY = "ON_INSTALL"
DEFAULT_CATEGORY = "Productivity"
DEFAULT_MARKETPLACE_DISPLAY_NAME = "Local Plugin Marketplace"
DEFAULT_VERSION = "0.1.0"
DEFAULT_OWNER_NAME = "Agent Skills Team"
DEFAULT_REVIEW_CADENCE = "monthly"
DEFAULT_AUTHOR_EMAIL = "maintainers@example.com"
DEFAULT_AUTHOR_URL = "https://github.com/example"
DEFAULT_LICENSE = "MIT"
DEFAULT_PRIVACY_URL = "https://example.com/privacy"
DEFAULT_TERMS_URL = "https://example.com/terms"
DEFAULT_LIFECYCLE_STATE = "incubating"
DEFAULT_MATURITY = "experimental"
VALID_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
VALID_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
VALID_POLICY_PRODUCTS = {"CHATGPT", "CODEX", "ATLAS"}
DEFAULT_POLICY_PRODUCTS = ["CODEX"]


def normalize_plugin_name(plugin_name: str) -> str:
    """
    Convert a plugin name into kebab-case suitable for identifiers and filenames.
    
    Converts the input to lowercase, replaces runs of non-alphanumeric characters with a single hyphen, collapses repeated hyphens, and removes leading or trailing hyphens.
    
    Returns:
        str: Kebab-case string containing only lowercase ASCII letters, digits and single hyphens; leading and trailing hyphens are removed.
    """
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


def _display_name(plugin_name: str) -> str:
    return " ".join(part.capitalize() for part in plugin_name.split("-") if part)


def _default_docs_url(plugin_name: str) -> str:
    return f"https://example.com/Plugins/{plugin_name}"


def _default_repo_url(plugin_name: str) -> str:
    return f"{DEFAULT_AUTHOR_URL}/{plugin_name}"


def _build_governance(owner: str, review_cadence: str) -> dict[str, str]:
    return {
        "lifecycle_state": DEFAULT_LIFECYCLE_STATE,
        "maturity": DEFAULT_MATURITY,
        "owner": owner,
        "review_cadence": review_cadence,
        "last_reviewed": date.today().isoformat(),
        "metadata_source": "plugin_manifest",
    }


def _build_canonical_plugin_json(
    plugin_name: str,
    *,
    description: str,
    owner: str,
    review_cadence: str,
    enabled_surfaces: dict[str, bool],
) -> dict[str, Any]:
    display_name = _display_name(plugin_name)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "name": plugin_name,
        "version": DEFAULT_VERSION,
        "description": description,
        "author": {
            "name": owner,
            "email": DEFAULT_AUTHOR_EMAIL,
            "url": DEFAULT_AUTHOR_URL,
        },
        "homepage": _default_docs_url(plugin_name),
        "repository": _default_repo_url(plugin_name),
        "license": DEFAULT_LICENSE,
        "keywords": ["plugin", plugin_name, "codex"],
        "governance": _build_governance(owner, review_cadence),
        "interface": {
            "displayName": display_name,
            "shortDescription": description,
            "longDescription": description,
            "developerName": owner,
            "category": DEFAULT_CATEGORY,
            "capabilities": ["Interactive", "Read", "Write"],
            "websiteURL": _default_docs_url(plugin_name),
            "privacyPolicyURL": DEFAULT_PRIVACY_URL,
            "termsOfServiceURL": DEFAULT_TERMS_URL,
            "defaultPrompt": f"Help me use {display_name}.",
            "brandColor": "#3B82F6",
        },
    }
    if enabled_surfaces.get("skills"):
        payload["skills"] = "./skills/"
    if enabled_surfaces.get("hooks"):
        payload["hooks"] = "./hooks.json"
    if enabled_surfaces.get("mcp"):
        payload["mcpServers"] = "./.mcp.json"
    if enabled_surfaces.get("apps"):
        payload["apps"] = "./.app.json"
    return payload


def _default_description(plugin_name: str) -> str:
    display_name = _display_name(plugin_name)
    return f"{display_name} plugin scaffold for Codex workflows."


def _resolve_scaffold_metadata(
    plugin_name: str,
    *,
    description: str | None,
    owner: str | None,
    review_cadence: str | None,
) -> tuple[str, str, str]:
    resolved_description = description.strip() if description and description.strip() else _default_description(plugin_name)
    resolved_owner = owner.strip() if owner and owner.strip() else DEFAULT_OWNER_NAME
    resolved_review_cadence = (
        review_cadence.strip()
        if review_cadence and review_cadence.strip()
        else DEFAULT_REVIEW_CADENCE
    )
    return resolved_description, resolved_owner, resolved_review_cadence


def build_plugin_json(
    plugin_name: str,
    *,
    description: str | None = None,
    owner: str | None = None,
    review_cadence: str | None = None,
    enabled_surfaces: dict[str, bool] | None = None,
) -> dict[str, Any]:
    resolved_description, resolved_owner, resolved_review_cadence = _resolve_scaffold_metadata(
        plugin_name,
        description=description,
        owner=owner,
        review_cadence=review_cadence,
    )
    return _build_canonical_plugin_json(
        plugin_name,
        description=resolved_description,
        owner=resolved_owner,
        review_cadence=resolved_review_cadence,
        enabled_surfaces=enabled_surfaces or {},
    )


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
    # Preserve lexical path components so ".agents/Plugins/..." remains valid
    # even when ".agents/plugins" is a symlink to "plugins".
    absolute = marketplace_path.expanduser().absolute()
    if absolute.name != "marketplace.json":
        raise ValueError("marketplace path must end with 'marketplace.json'.")

    plugins_dir = absolute.parent
    if plugins_dir.name.lower() != "plugins":
        raise ValueError(
            "marketplace path must live under '.agents/Plugins/' "
            "or legacy 'Plugins/' directory."
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
    rel_parts = list(resolved_plugin_root.relative_to(repo_root).parts)
    if rel_parts and rel_parts[0].lower() == "plugins":
        rel_parts[0] = "Plugins"
    return f"./{'/'.join(rel_parts)}"


def build_default_marketplace() -> dict[str, Any]:
    return {
        "name": "local-marketplace",
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


def create_json_file(path: Path, payload: dict, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def create_text_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_readme(plugin_name: str, description: str | None = None) -> str:
    title = _display_name(plugin_name)
    summary = description.strip() if description and description.strip() else _default_description(plugin_name)
    return f"# {title}\n\n{summary}\n"


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for creating a plugin scaffold.

    Recognises options to control created surfaces, marketplace update behaviour, policy and governance metadata. Defaults for `--path` and `--marketplace-path` are resolved lazily in main() when not provided.

    Returns:
    	argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Create a plugin scaffold with a fully populated canonical plugin manifest."
    )
    parser.add_argument("plugin_name")
    parser.add_argument(
        "--path",
        default=None,
        help=(
            "Parent directory for plugin creation "
            "(defaults to <repo-root>/Plugins/third-party resolved from this script location). "
            "When using a home-rooted marketplace, use <home>/Plugins/<category>."
        ),
    )
    parser.add_argument("--with-skills", action="store_true", help="Create skills/ directory")
    parser.add_argument("--with-hooks", action="store_true", help="Create hooks/ directory")
    parser.add_argument("--with-scripts", action="store_true", help="Create Infrastructure/scripts/ directory")
    parser.add_argument("--with-assets", action="store_true", help="Create assets/ directory")
    parser.add_argument("--with-mcp", action="store_true", help="Create .mcp.json manifest scaffold")
    parser.add_argument("--with-apps", action="store_true", help="Create .app.json manifest scaffold")
    parser.add_argument(
        "--with-marketplace",
        action="store_true",
        help=(
            "Create or update marketplace.json. "
            "By default, OpenAI/Codex mode expects <root>/.agents/Plugins/marketplace.json."
        ),
    )
    parser.add_argument(
        "--marketplace-path",
        default=None,
        help=(
            "Path to marketplace.json "
            "(defaults to <repo-root>/.agents/Plugins/marketplace.json resolved from this script location). "
            "For a home-rooted marketplace, use <home>/.agents/Plugins/marketplace.json."
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
            "Allow legacy Plugins/marketplace.json layout instead of strict "
            ".agents/Plugins/marketplace.json."
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
    parser.add_argument(
        "--description",
        help="Plugin description used in manifest and README. Defaults to a generated description.",
    )
    parser.add_argument(
        "--owner",
        help=f"Plugin owner for governance metadata (default: {DEFAULT_OWNER_NAME}).",
    )
    parser.add_argument(
        "--review-cadence",
        help=f"Review cadence for governance metadata (default: {DEFAULT_REVIEW_CADENCE}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Apply defaults if not provided by user
    if args.path is None:
        args.path = str(DEFAULT_PLUGIN_PARENT)
    if args.marketplace_path is None:
        args.marketplace_path = str(DEFAULT_MARKETPLACE_PATH)

    raw_plugin_name = args.plugin_name
    plugin_name = normalize_plugin_name(raw_plugin_name)
    if plugin_name != raw_plugin_name:
        print(f"Note: Normalized plugin name from '{raw_plugin_name}' to '{plugin_name}'.")
    validate_plugin_name(plugin_name)

    plugin_root = (Path(args.path).expanduser().resolve() / plugin_name)
    plugin_root.mkdir(parents=True, exist_ok=True)
    policy_products = _effective_policy_products(args.product)

    enabled_surfaces = {
        "skills": bool(args.with_skills),
        "hooks": bool(args.with_hooks),
        "mcp": bool(args.with_mcp),
        "apps": bool(args.with_apps),
    }

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    write_json(
        plugin_json_path,
        build_plugin_json(
            plugin_name,
            description=args.description,
            owner=args.owner,
            review_cadence=args.review_cadence,
            enabled_surfaces=enabled_surfaces,
        ),
        args.force,
    )
    create_text_file(
        plugin_root / "README.md",
        build_readme(plugin_name, args.description),
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
        create_json_file(
            plugin_root / ".mcp.json",
            {"mcpServers": {}},
            args.force,
        )

    if args.with_apps:
        create_json_file(
            plugin_root / ".app.json",
            {
                "apps": {},
            },
            args.force,
        )

    marketplace_path: Path | None = None
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
