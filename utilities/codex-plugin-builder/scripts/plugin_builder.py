#!/usr/bin/env python3
"""Scaffold and validate Codex plugin packages plus marketplace entries."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


MAX_PLUGIN_NAME_LENGTH = 64
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PLUGIN_PARENT = REPO_ROOT / "plugins"
DEFAULT_MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
DEFAULT_INSTALL_POLICY = "AVAILABLE"
DEFAULT_AUTH_POLICY = "ON_INSTALL"
DEFAULT_CATEGORY = "Productivity"
VALID_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
VALID_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}

REQUIRED_PLUGIN_ROOT_FILES = [
    ".codex-plugin/plugin.json",
    "README.md",
    "LICENSE",
]

REQUIRED_PLUGIN_FIELDS = [
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "hooks",
    "mcpServers",
    "apps",
    "interface",
]

REQUIRED_AUTHOR_FIELDS = ["name", "email", "url"]
REQUIRED_INTERFACE_FIELDS = [
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "defaultPrompt",
    "brandColor",
    "composerIcon",
    "logo",
    "screenshots",
]

CLAUDE_TO_CODEX_TERMINOLOGY = {
    "commands/": "prompts/",
    "slash commands": "prompts",
    "slash-commands": "prompts",
    "commands key": "prompts key",
}


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


def build_plugin_json(plugin_name: str) -> dict[str, Any]:
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
            "defaultPrompt": "[TODO: Starter prompt for trying a plugin]",
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
        "installPolicy": install_policy,
        "authPolicy": auth_policy,
        "category": category,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return payload


def build_default_marketplace() -> dict[str, Any]:
    return {
        "name": "[TODO: marketplace-name]",
        "plugins": [],
    }


def write_json(path: Path, data: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists. Use --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_stub_file(path: Path, payload: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        return
    write_json(path, payload, force=True)


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


def _readme_template(plugin_name: str) -> str:
    return "\n".join(
        [
            f"# {plugin_name}",
            "",
            "## Overview",
            "TODO: Describe what this plugin does and when to use it.",
            "",
            "## Surfaces",
            "- Skills",
            "- Prompts (optional)",
            "- Agents (optional)",
            "- Hooks",
            "- MCP",
            "",
            "## Validation",
            "Run plugin and skill validators before publishing.",
            "",
        ]
    )


def _license_template() -> str:
    return "\n".join(
        [
            "MIT License",
            "",
            "Copyright (c) [TODO: year] [TODO: owner]",
            "",
            "Permission is hereby granted, free of charge, to any person obtaining a copy",
            "of this software and associated documentation files (the \"Software\"), to deal",
            "in the Software without restriction, including without limitation the rights",
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell",
            "copies of the Software, and to permit persons to whom the Software is",
            "furnished to do so, subject to the following conditions:",
            "",
            "The above copyright notice and this permission notice shall be included in all",
            "copies or substantial portions of the Software.",
            "",
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR",
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,",
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE",
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER",
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,",
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE",
            "SOFTWARE.",
            "",
        ]
    )


def _is_relative_plugin_path(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("./")


def _check_required_fields(
    payload: dict[str, Any], required_keys: Iterable[str], object_name: str
) -> list[str]:
    failures: list[str] = []
    for key in required_keys:
        if key not in payload:
            failures.append(f"Missing required {object_name} field: {key}")
    return failures


def _check_plugin_manifest(plugin_json_path: Path) -> list[str]:
    failures: list[str] = []
    payload = load_json(plugin_json_path)

    failures.extend(_check_required_fields(payload, REQUIRED_PLUGIN_FIELDS, "plugin.json"))

    name = payload.get("name")
    if isinstance(name, str):
        try:
            validate_plugin_name(name)
        except ValueError as exc:
            failures.append(f"Invalid plugin name: {exc}")
    else:
        failures.append("plugin.json field 'name' must be a string.")

    if not isinstance(payload.get("keywords"), list):
        failures.append("plugin.json field 'keywords' must be an array of strings.")
    elif not all(isinstance(item, str) for item in payload["keywords"]):
        failures.append("plugin.json field 'keywords' must contain only strings.")

    author = payload.get("author")
    if not isinstance(author, dict):
        failures.append("plugin.json field 'author' must be an object.")
    else:
        failures.extend(_check_required_fields(author, REQUIRED_AUTHOR_FIELDS, "author"))
        for key in REQUIRED_AUTHOR_FIELDS:
            if key in author and not isinstance(author[key], str):
                failures.append(f"plugin.json author.{key} must be a string.")

    for path_key in ("skills", "hooks", "mcpServers", "apps"):
        if path_key in payload and not _is_relative_plugin_path(payload[path_key]):
            failures.append(
                f"plugin.json field '{path_key}' must be a relative path starting with './'."
            )

    interface = payload.get("interface")
    if not isinstance(interface, dict):
        failures.append("plugin.json field 'interface' must be an object.")
    else:
        failures.extend(_check_required_fields(interface, REQUIRED_INTERFACE_FIELDS, "interface"))
        for key in REQUIRED_INTERFACE_FIELDS:
            if key == "capabilities":
                value = interface.get(key)
                if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                    failures.append("plugin.json interface.capabilities must be an array of strings.")
            elif key == "screenshots":
                value = interface.get(key)
                if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                    failures.append("plugin.json interface.screenshots must be an array of strings.")
                else:
                    for shot in value:
                        if not shot.startswith("./assets/") or not shot.lower().endswith(".png"):
                            failures.append(
                                "plugin.json interface.screenshots entries must be PNG paths "
                                "under './assets/'."
                            )
            else:
                if key in interface and not isinstance(interface[key], str):
                    failures.append(f"plugin.json interface.{key} must be a string.")

        for path_key in ("composerIcon", "logo"):
            if path_key in interface and not _is_relative_plugin_path(interface[path_key]):
                failures.append(
                    f"plugin.json interface.{path_key} must be a relative path starting with './'."
                )

    for legacy_key in ("commands", "slashCommands", "slash_commands"):
        if legacy_key in payload:
            failures.append(
                f"plugin.json uses Claude-oriented field '{legacy_key}'. "
                "Use Codex prompt surface fields (`prompts/` path and `interface.defaultPrompt`) instead."
            )

    return failures


def _check_marketplace_entry(
    marketplace_payload: dict[str, Any], plugin_name: str
) -> list[str]:
    failures: list[str] = []
    plugins = marketplace_payload.get("plugins")
    if not isinstance(plugins, list):
        return ["marketplace.json field 'plugins' must be an array."]

    plugin_entry: dict[str, Any] | None = None
    for entry in plugins:
        if isinstance(entry, dict) and entry.get("name") == plugin_name:
            plugin_entry = entry
            break

    if plugin_entry is None:
        return [f"marketplace.json missing plugin entry for '{plugin_name}'."]

    source = plugin_entry.get("source")
    if not isinstance(source, dict):
        failures.append(f"marketplace plugin '{plugin_name}' field 'source' must be an object.")
    else:
        if source.get("source") != "local":
            failures.append(
                f"marketplace plugin '{plugin_name}' source.source must be 'local'."
            )
        expected_path = f"./plugins/{plugin_name}"
        if source.get("path") != expected_path:
            failures.append(
                f"marketplace plugin '{plugin_name}' source.path must be '{expected_path}'."
            )

    install_policy = plugin_entry.get("installPolicy")
    if install_policy not in VALID_INSTALL_POLICIES:
        failures.append(
            f"marketplace plugin '{plugin_name}' installPolicy must be one of "
            f"{sorted(VALID_INSTALL_POLICIES)}."
        )

    auth_policy = plugin_entry.get("authPolicy")
    if auth_policy not in VALID_AUTH_POLICIES:
        failures.append(
            f"marketplace plugin '{plugin_name}' authPolicy must be one of "
            f"{sorted(VALID_AUTH_POLICIES)}."
        )

    if not isinstance(plugin_entry.get("category"), str) or not plugin_entry.get("category"):
        failures.append(f"marketplace plugin '{plugin_name}' category must be a non-empty string.")

    return failures


def _print_findings(findings: list[str]) -> None:
    if not findings:
        print("PASS: plugin contract validation succeeded.")
        return
    print("FAIL: plugin contract validation found issues:")
    for finding in findings:
        print(f"  - {finding}")


def _run_scaffold(args: argparse.Namespace) -> int:
    raw_plugin_name = args.plugin_name
    plugin_name = normalize_plugin_name(raw_plugin_name)
    if plugin_name != raw_plugin_name:
        print(f"Note: Normalized plugin name from '{raw_plugin_name}' to '{plugin_name}'.")
    validate_plugin_name(plugin_name)

    plugin_root = (Path(args.path).expanduser().resolve() / plugin_name)
    plugin_root.mkdir(parents=True, exist_ok=True)

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    write_json(plugin_json_path, build_plugin_json(plugin_name), args.force)
    write_text(plugin_root / "README.md", _readme_template(plugin_name), args.force)
    write_text(plugin_root / "LICENSE", _license_template(), args.force)

    optional_directories = {
        "skills": args.with_skills,
        "hooks": args.with_hooks,
        "prompts": args.with_prompts,
        "agents": args.with_agents,
        "scripts": args.with_scripts,
        "assets": args.with_assets,
    }
    for folder, enabled in optional_directories.items():
        if enabled:
            (plugin_root / folder).mkdir(parents=True, exist_ok=True)

    if args.with_hooks_json:
        create_stub_file(
            plugin_root / "hooks.json",
            {"hooks": {"SessionStart": [], "Stop": []}},
            args.force,
        )

    if args.with_mcp:
        create_stub_file(
            plugin_root / ".mcp.json",
            {"mcpServers": {}},
            args.force,
        )

    if args.with_apps:
        create_stub_file(
            plugin_root / ".app.json",
            {"apps": {}},
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
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    plugin_root = Path(args.plugin_path).expanduser().resolve()
    findings: list[str] = []

    if not plugin_root.exists() or not plugin_root.is_dir():
        print(f"ERROR: plugin path is not a directory: {plugin_root}", file=sys.stderr)
        return 1

    for required_rel in REQUIRED_PLUGIN_ROOT_FILES:
        required_path = plugin_root / required_rel
        if not required_path.exists():
            findings.append(f"Missing required file: {required_path}")

    legacy_claude_manifest = plugin_root / ".claude-plugin" / "plugin.json"
    if legacy_claude_manifest.exists():
        findings.append(
            "Detected legacy Claude manifest `.claude-plugin/plugin.json`. "
            "Converted Codex packages must use `.codex-plugin/plugin.json` as runtime manifest."
        )

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    if plugin_json_path.exists():
        findings.extend(_check_plugin_manifest(plugin_json_path))

    # Claude -> Codex terminology enforcement for conversion safety.
    commands_dir = plugin_root / "commands"
    prompts_dir = plugin_root / "prompts"
    slash_commands_dir = plugin_root / "slash-commands"
    if commands_dir.exists() and not prompts_dir.exists():
        findings.append(
            "Detected Claude-oriented `commands/` without Codex `prompts/`. "
            "Map commands -> prompts during conversion."
        )
    if slash_commands_dir.exists() and not prompts_dir.exists():
        findings.append(
            "Detected `slash-commands/` without Codex `prompts/`. "
            "Map slash commands -> prompts during conversion."
        )

    marketplace_path = Path(args.marketplace_path).expanduser().resolve()
    if args.require_marketplace:
        if not marketplace_path.exists():
            findings.append(
                f"Marketplace file required but missing: {marketplace_path}"
            )
        else:
            marketplace_payload = load_json(marketplace_path)
            findings.extend(
                _check_marketplace_entry(marketplace_payload, plugin_root.name)
            )
    elif marketplace_path.exists():
        marketplace_payload = load_json(marketplace_path)
        findings.extend(_check_marketplace_entry(marketplace_payload, plugin_root.name))

    _print_findings(findings)
    return 0 if not findings else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold and validate Codex plugin packages."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create a plugin skeleton with placeholder plugin.json and package docs.",
    )
    scaffold_parser.add_argument("plugin_name")
    scaffold_parser.add_argument(
        "--path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Parent directory for plugin creation (defaults to <repo>/plugins).",
    )
    scaffold_parser.add_argument("--with-skills", action="store_true", help="Create skills/ directory.")
    scaffold_parser.add_argument("--with-hooks", action="store_true", help="Create hooks/ directory.")
    scaffold_parser.add_argument("--with-hooks-json", action="store_true", help="Create hooks.json placeholder.")
    scaffold_parser.add_argument("--with-prompts", action="store_true", help="Create prompts/ directory.")
    scaffold_parser.add_argument("--with-agents", action="store_true", help="Create agents/ directory.")
    scaffold_parser.add_argument("--with-scripts", action="store_true", help="Create scripts/ directory.")
    scaffold_parser.add_argument("--with-assets", action="store_true", help="Create assets/ directory.")
    scaffold_parser.add_argument("--with-mcp", action="store_true", help="Create .mcp.json placeholder.")
    scaffold_parser.add_argument("--with-apps", action="store_true", help="Create .app.json placeholder.")
    scaffold_parser.add_argument(
        "--with-marketplace",
        action="store_true",
        help="Create or update .agents/plugins/marketplace.json.",
    )
    scaffold_parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json (defaults to <repo>/.agents/plugins/marketplace.json).",
    )
    scaffold_parser.add_argument(
        "--install-policy",
        default=DEFAULT_INSTALL_POLICY,
        choices=sorted(VALID_INSTALL_POLICIES),
        help="Marketplace installPolicy value.",
    )
    scaffold_parser.add_argument(
        "--auth-policy",
        default=DEFAULT_AUTH_POLICY,
        choices=sorted(VALID_AUTH_POLICIES),
        help="Marketplace authPolicy value.",
    )
    scaffold_parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help="Marketplace category value.",
    )
    scaffold_parser.add_argument("--force", action="store_true", help="Overwrite existing files.")

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate plugin contract and optional marketplace entry.",
    )
    validate_parser.add_argument("plugin_path", help="Path to plugin root.")
    validate_parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json for entry checks.",
    )
    validate_parser.add_argument(
        "--require-marketplace",
        action="store_true",
        help="Fail when marketplace.json or plugin entry is missing.",
    )
    validate_parser.add_argument(
        "--show-terminology-map",
        action="store_true",
        help="Print Claude->Codex terminology mapping reference.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if getattr(args, "show_terminology_map", False):
        print("Terminology map (Claude -> Codex):")
        for src, dst in CLAUDE_TO_CODEX_TERMINOLOGY.items():
            print(f"  - {src} -> {dst}")
    if args.command == "scaffold":
        raise SystemExit(_run_scaffold(args))
    if args.command == "validate":
        raise SystemExit(_run_validate(args))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
