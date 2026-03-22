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
SOURCE_PROVIDER_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".codex-plugin/plugin.json",
)
SOURCE_MARKETPLACE_MANIFESTS = (
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
)
SOURCE_SURFACE_DEFAULTS = {
    "commands": ["./commands"],
    "skills": ["./skills"],
    "agents": ["./agents"],
    "hooks": ["./hooks.json", "./hooks/hooks.json"],
    "mcpServers": ["./.mcp.json"],
    "apps": ["./.app.json"],
}
SOURCE_CODEX_SUPPORT_DOCS = (
    ".codex/INSTALL.md",
    "docs/README.codex.md",
)

REQUIRED_PLUGIN_ROOT_FILES = [".codex-plugin/plugin.json"]

OPTIONAL_PLUGIN_STRING_FIELDS = [
    "description",
    "version",
    "homepage",
    "repository",
    "license",
]
OPTIONAL_PLUGIN_PATH_FIELDS = ["skills", "hooks", "mcpServers", "apps"]
OPTIONAL_AUTHOR_FIELDS = ["name", "email", "url"]
OPTIONAL_INTERFACE_STRING_FIELDS = [
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "brandColor",
]
OPTIONAL_INTERFACE_PATH_FIELDS = ["composerIcon", "logo"]

CLAUDE_TO_CODEX_TERMINOLOGY = {
    "commands/": "prompts/ or skills/ or both",
    "slash commands": "prompts",
    "slash-commands": "prompts",
    "commands key": "prompts and or skills surfaces",
}

SIMILARITY_STOPWORDS = {
    "a",
    "an",
    "and",
    "builder",
    "by",
    "codex",
    "convert",
    "converter",
    "create",
    "creator",
    "for",
    "from",
    "in",
    "into",
    "of",
    "or",
    "package",
    "plugin",
    "plugins",
    "the",
    "to",
    "with",
}
SIMILAR_PLUGIN_SCORE_THRESHOLD = 0.45


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


def build_plugin_json(
    plugin_name: str,
    enabled_surfaces: dict[str, bool] | None = None,
) -> dict[str, Any]:
    enabled_surfaces = enabled_surfaces or {}
    payload: dict[str, Any] = {
        "name": plugin_name,
        "version": "0.1.0",
        "description": "[TODO: Brief plugin description]",
        "author": {
            "name": "[TODO: Author Name]",
            "email": "[TODO: author@example.com]",
            "url": "[TODO: https://github.com/author]",
        },
        "homepage": "[TODO: https://docs.example.com/plugin]",
        "repository": "[TODO: https://github.com/author/plugin]",
        "license": "MIT",
        "keywords": ["plugin", plugin_name],
        "interface": {
            "displayName": "[TODO: Plugin Display Name]",
            "shortDescription": "[TODO: Short description for subtitle]",
            "longDescription": "[TODO: Long description for details page]",
            "developerName": "[TODO: OpenAI]",
            "category": "[TODO: Productivity]",
            "capabilities": ["Interactive", "Write"],
            "websiteURL": "[TODO: https://openai.com/]",
            "privacyPolicyURL": "[TODO: https://openai.com/policies/row-privacy-policy/]",
            "termsOfServiceURL": "[TODO: https://openai.com/policies/row-terms-of-use/]",
            "defaultPrompt": "[TODO: Starter prompt for trying a plugin]",
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
    if enabled_surfaces.get("assets"):
        payload["interface"].update(
            {
                "composerIcon": "./assets/icon.png",
                "logo": "./assets/logo.png",
                "screenshots": [
                    "./assets/screenshot1.png",
                    "./assets/screenshot2.png",
                    "./assets/screenshot3.png",
                ],
            }
        )
    return payload


def _tokenize_text(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in re.findall(r"[a-z0-9]+", value.lower()):
            if len(token) <= 2 or token in SIMILARITY_STOPWORDS:
                continue
            tokens.add(token)
    return tokens


def _relative_surface_exists(plugin_root: Path, relative_path: str | None) -> bool:
    if not relative_path or not _is_relative_plugin_path(relative_path):
        return False
    return (plugin_root / relative_path[2:]).exists()


def _manifest_capabilities(payload: dict[str, Any]) -> list[str]:
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        return []
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list):
        return []
    return [item for item in capabilities if isinstance(item, str)]


def _manifest_keywords(payload: dict[str, Any]) -> list[str]:
    keywords = payload.get("keywords")
    if not isinstance(keywords, list):
        return []
    return [item for item in keywords if isinstance(item, str)]


def _plugin_signature_from_payload(
    plugin_root: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    description = payload.get("description") if isinstance(payload.get("description"), str) else ""
    interface = payload.get("interface") if isinstance(payload.get("interface"), dict) else {}
    long_description = (
        interface.get("longDescription")
        if isinstance(interface.get("longDescription"), str)
        else ""
    )
    short_description = (
        interface.get("shortDescription")
        if isinstance(interface.get("shortDescription"), str)
        else ""
    )
    return {
        "name": str(payload.get("name") or plugin_root.name),
        "root": str(plugin_root),
        "description": description,
        "keywords": _manifest_keywords(payload),
        "capabilities": _manifest_capabilities(payload),
        "text_tokens": sorted(
            _tokenize_text(
                str(payload.get("name") or ""),
                description,
                short_description,
                long_description,
                " ".join(_manifest_keywords(payload)),
            )
        ),
        "surface_flags": {
            "skills": _relative_surface_exists(plugin_root, payload.get("skills")),
            "hooks": _relative_surface_exists(plugin_root, payload.get("hooks")),
            "mcpServers": _relative_surface_exists(plugin_root, payload.get("mcpServers")),
            "apps": _relative_surface_exists(plugin_root, payload.get("apps")),
            "prompts": (plugin_root / "prompts").exists(),
            "agents": (plugin_root / "agents").exists(),
        },
    }


def _source_signature_from_report(
    plugin_name: str,
    source_report: dict[str, Any] | None,
) -> dict[str, Any]:
    signature = {
        "name": plugin_name,
        "source_name": None,
        "root": None,
        "description": "",
        "keywords": [],
        "capabilities": [],
        "text_tokens": sorted(_tokenize_text(plugin_name)),
        "surface_flags": {
            "skills": False,
            "hooks": False,
            "mcpServers": False,
            "apps": False,
            "prompts": False,
            "agents": False,
        },
    }
    if source_report is None:
        return signature

    signature["root"] = source_report.get("plugin_root")
    source_name = source_report.get("plugin_name")
    if isinstance(source_name, str) and source_name.strip():
        signature["source_name"] = source_name
    detected_surfaces = source_report.get("detected_surfaces") or {}
    signature["surface_flags"].update(
        {
            "skills": bool(detected_surfaces.get("skills")),
            "hooks": bool(detected_surfaces.get("hooks")),
            "mcpServers": bool(detected_surfaces.get("mcpServers")),
            "apps": bool(detected_surfaces.get("apps")),
            "prompts": bool(detected_surfaces.get("commands")),
            "agents": bool(detected_surfaces.get("agents")),
        }
    )

    primary_manifest_value = source_report.get("primary_manifest")
    if isinstance(primary_manifest_value, str):
        primary_manifest = Path(primary_manifest_value)
        if primary_manifest.exists():
            payload = load_json(primary_manifest)
            manifest_signature = _plugin_signature_from_payload(primary_manifest.parent.parent, payload)
            signature["description"] = manifest_signature["description"]
            signature["keywords"] = manifest_signature["keywords"]
            signature["capabilities"] = manifest_signature["capabilities"]
            signature["surface_flags"].update(manifest_signature["surface_flags"])
    signature["text_tokens"] = sorted(
        _tokenize_text(
            plugin_name,
            str(signature.get("source_name") or ""),
            str(signature.get("description") or ""),
            " ".join(signature.get("keywords") or []),
        )
    )
    return signature


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
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return payload


def _optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def build_default_marketplace() -> dict[str, Any]:
    return {
        "name": "[TODO: marketplace-name]",
        "interface": {
            "displayName": "[TODO: Marketplace Display Name]",
        },
        "plugins": [],
    }


def _display_name_from_identifier(value: str) -> str:
    words = [word for word in re.split(r"[-_\s]+", value.strip()) if word]
    if not words:
        return "[TODO: Marketplace Display Name]"
    return " ".join(word.capitalize() for word in words)


def _ensure_marketplace_interface(payload: dict[str, Any]) -> None:
    interface = payload.get("interface")
    if isinstance(interface, dict):
        display_name = interface.get("displayName")
        if isinstance(display_name, str) and display_name.strip():
            return
    marketplace_name = payload.get("name") if isinstance(payload.get("name"), str) else ""
    payload["interface"] = {
        "displayName": _display_name_from_identifier(marketplace_name),
    }


def _check_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return [f"{field_name} must be an array of strings."]
    return []


def _check_declared_plugin_path(
    plugin_root: Path,
    field_name: str,
    value: Any,
    *,
    require_exists: bool,
) -> list[str]:
    failures: list[str] = []
    if not _is_relative_plugin_path(value):
        return [f"{field_name} must be a relative path starting with './'."]
    candidate = (plugin_root / value[2:]).resolve()
    if not _path_within_root(plugin_root, candidate):
        failures.append(f"{field_name} must stay within the plugin root.")
        return failures
    if require_exists and not candidate.exists():
        failures.append(f"{field_name} points to a missing path: {value}")
    return failures


def _check_default_prompt(value: Any) -> list[str]:
    prompts: list[str]
    if isinstance(value, str):
        prompts = [value]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        prompts = value
    else:
        return [
            "plugin.json interface.defaultPrompt must be a string or an array of strings."
        ]

    failures: list[str] = []
    if len(prompts) > 3:
        failures.append(
            "plugin.json interface.defaultPrompt supports at most 3 prompts."
        )
    for prompt in prompts:
        if len(prompt) > 128:
            failures.append(
                "plugin.json interface.defaultPrompt entries must be 128 characters or fewer."
            )
            break
    return failures


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
    _ensure_marketplace_interface(payload)

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


def _operational_spec_template(
    plugin_name: str,
    enabled_surfaces: dict[str, bool],
    source_report: dict[str, Any] | None = None,
    includes_marketplace: bool = False,
) -> str:
    capability_rows: list[tuple[str, str]] = [
        ("package_validate", "Validate plugin contract, required docs, and declared surfaces."),
        ("runtime_activate", "Prepare the plugin package for runtime use after validation."),
        ("route_request", "Resolve an incoming request to the correct enabled plugin surface."),
        ("work_finalize", "Finalize runtime completion, failure, or retryable timeout state."),
    ]
    if enabled_surfaces.get("hooks"):
        capability_rows.append(("hook_execute", "Execute startup hook behavior for the plugin."))
    if enabled_surfaces.get("skills"):
        capability_rows.append(("skill_dispatch", "Dispatch a plugin-owned skill."))
    if enabled_surfaces.get("prompts"):
        capability_rows.append(("prompt_dispatch", "Dispatch a plugin-owned prompt."))
    if enabled_surfaces.get("agents"):
        capability_rows.append(("agent_dispatch", "Dispatch a plugin-owned agent."))
    if enabled_surfaces.get("mcp"):
        capability_rows.append(("mcp_attach", "Attach plugin MCP configuration or MCP-backed context."))
    if enabled_surfaces.get("apps"):
        capability_rows.append(("app_attach", "Attach plugin app metadata or app-backed context."))
    if includes_marketplace:
        capability_rows.append(("marketplace_register", "Register or verify the plugin marketplace entry."))

    capabilities = [name for name, _ in capability_rows]
    plugin_scope = ["package_validation", "runtime_request_routing"]
    if enabled_surfaces.get("skills"):
        plugin_scope.append("skill_dispatch")
    if enabled_surfaces.get("prompts"):
        plugin_scope.append("prompt_dispatch")
    if enabled_surfaces.get("agents"):
        plugin_scope.append("agent_dispatch")
    if enabled_surfaces.get("hooks"):
        plugin_scope.append("startup_hook_execution")
    if enabled_surfaces.get("mcp"):
        plugin_scope.append("mcp_context_attach")
    if enabled_surfaces.get("apps"):
        plugin_scope.append("app_context_attach")
    if includes_marketplace:
        plugin_scope.append("marketplace_registration")

    source_summary_lines: list[str] = []
    if source_report is not None:
        source_summary_lines.extend(
            [
                "Source-backed assumptions:",
                f"- detected source plugin root: `{source_report['plugin_root']}`",
                f"- provider manifests: `{', '.join(source_report['provider_manifests']) or 'none'}`",
            ]
        )
        if source_report.get("native_codex_docs"):
            source_summary_lines.append("- source already ships Codex-native docs; conversion may be additive rather than replacing the existing Codex lane.")
        if source_report.get("deprecated_command_files"):
            source_summary_lines.append("- deprecated command shims were detected; command surfaces should be treated as redirects unless revalidated.")
        if source_report.get("hook_glue_signals"):
            source_summary_lines.append("- provider-specific hook glue was detected; preserve hook intent, not source-provider wrapper behavior.")

    transition_rows: list[tuple[str, str, str, str, str, str, str]] = [
        (
            "PACKAGE_DEFINED",
            "validate_requested",
            "required package files and references exist",
            "validate package contract and references",
            f"`{plugin_name}.package_validate`",
            "SUCCESS",
            "PACKAGE_READY",
        ),
        (
            "PACKAGE_DEFINED",
            "validate_requested",
            "required package files or references are missing",
            "record package validation failure",
            f"`{plugin_name}.package_validate`",
            "FAILURE:VALIDATION_ERROR",
            "FAIL_VALIDATION",
        ),
        (
            "PACKAGE_DEFINED",
            "validate_requested",
            "validation dependencies are unavailable",
            "record blocked validation dependency",
            f"`{plugin_name}.package_validate`",
            "FAILURE:BLOCKED_DEPENDENCY",
            "FAIL_BLOCKED",
        ),
        (
            "PACKAGE_DEFINED",
            "validate_requested",
            "validation execution fails unexpectedly",
            "record system validation failure",
            f"`{plugin_name}.package_validate`",
            "FAILURE:SYSTEM_ERROR",
            "FAIL_SYSTEM",
        ),
    ]

    if includes_marketplace:
        transition_rows.extend(
            [
                (
                    "PACKAGE_READY",
                    "marketplace_requested",
                    "marketplace entry is required and registry is writable",
                    "register or verify marketplace entry",
                    f"`{plugin_name}.marketplace_register`",
                    "SUCCESS",
                    "PACKAGE_READY",
                ),
                (
                    "PACKAGE_READY",
                    "marketplace_requested",
                    "marketplace entry is required but registry is unavailable",
                    "record marketplace dependency failure",
                    f"`{plugin_name}.marketplace_register`",
                    "FAILURE:BLOCKED_DEPENDENCY",
                    "FAIL_BLOCKED",
                ),
            ]
        )

    if enabled_surfaces.get("hooks"):
        transition_rows.extend(
            [
                (
                    "PACKAGE_READY",
                    "session_started",
                    "hook surface is enabled and hook execution is supported",
                    "execute startup hook behavior",
                    f"`{plugin_name}.hook_execute`",
                    "SUCCESS",
                    "SESSION_READY",
                ),
                (
                    "PACKAGE_READY",
                    "session_started",
                    "hook surface is enabled but policy forbids execution",
                    "reject hook execution",
                    f"`{plugin_name}.hook_execute`",
                    "FAILURE:POLICY_FAIL",
                    "FAIL_POLICY",
                ),
                (
                    "PACKAGE_READY",
                    "session_started",
                    "hook surface is enabled and hook execution times out",
                    "record retryable hook timeout",
                    f"`{plugin_name}.hook_execute`",
                    "RETRYABLE:PLUGIN_TIMEOUT",
                    "FAIL_TIMEOUT",
                ),
                (
                    "PACKAGE_READY",
                    "session_started",
                    "hook surface is enabled and hook execution fails",
                    "record hook execution failure",
                    f"`{plugin_name}.hook_execute`",
                    "FAILURE:PLUGIN_FAILURE",
                    "FAIL_PLUGIN",
                ),
            ]
        )
    else:
        transition_rows.append(
            (
                "PACKAGE_READY",
                "session_started",
                "no hook surface is enabled",
                "activate package without startup hook",
                f"`{plugin_name}.runtime_activate`",
                "SUCCESS",
                "SESSION_READY",
            )
        )

    if enabled_surfaces.get("mcp"):
        transition_rows.extend(
            [
                (
                    "SESSION_READY",
                    "context_attach_requested",
                    "request requires MCP context and MCP surface is enabled",
                    "attach MCP context",
                    f"`{plugin_name}.mcp_attach`",
                    "SUCCESS",
                    "SESSION_READY",
                ),
                (
                    "SESSION_READY",
                    "context_attach_requested",
                    "request requires MCP context and MCP attach fails",
                    "record MCP attach failure",
                    f"`{plugin_name}.mcp_attach`",
                    "FAILURE:PLUGIN_FAILURE",
                    "FAIL_PLUGIN",
                ),
            ]
        )

    if enabled_surfaces.get("apps"):
        transition_rows.extend(
            [
                (
                    "SESSION_READY",
                    "app_attach_requested",
                    "request requires app context and app surface is enabled",
                    "attach app context",
                    f"`{plugin_name}.app_attach`",
                    "SUCCESS",
                    "SESSION_READY",
                ),
                (
                    "SESSION_READY",
                    "app_attach_requested",
                    "request requires app context and app attach fails",
                    "record app attach failure",
                    f"`{plugin_name}.app_attach`",
                    "FAILURE:PLUGIN_FAILURE",
                    "FAIL_PLUGIN",
                ),
            ]
        )

    request_rows: list[tuple[str, str, str, str, str, str, str]] = []
    if enabled_surfaces.get("skills"):
        request_rows.append(
            (
                "SESSION_READY",
                "request_received",
                "request resolves uniquely to a plugin skill",
                "dispatch plugin skill",
                f"`{plugin_name}.skill_dispatch`",
                "SUCCESS",
                "WORK_ACTIVE",
            )
        )
    if enabled_surfaces.get("prompts"):
        request_rows.append(
            (
                "SESSION_READY",
                "request_received",
                "request resolves uniquely to a plugin prompt",
                "dispatch plugin prompt",
                f"`{plugin_name}.prompt_dispatch`",
                "SUCCESS",
                "WORK_ACTIVE",
            )
        )
    if enabled_surfaces.get("agents"):
        request_rows.append(
            (
                "SESSION_READY",
                "request_received",
                "request resolves uniquely to a plugin agent and runtime supports agents",
                "dispatch plugin agent",
                f"`{plugin_name}.agent_dispatch`",
                "SUCCESS",
                "WORK_ACTIVE",
            )
        )
    request_rows.extend(
        [
            (
                "SESSION_READY",
                "request_received",
                "request does not resolve to any enabled plugin surface",
                "record route validation failure",
                f"`{plugin_name}.route_request`",
                "FAILURE:VALIDATION_ERROR",
                "FAIL_VALIDATION",
            ),
            (
                "SESSION_READY",
                "request_received",
                "request matches multiple enabled plugin surfaces",
                "record ambiguous routing failure",
                f"`{plugin_name}.route_request`",
                "FAILURE:POLICY_FAIL",
                "FAIL_POLICY",
            ),
        ]
    )
    transition_rows.extend(request_rows)

    transition_rows.extend(
        [
            (
                "WORK_ACTIVE",
                "work_completed",
                "active capability completed without plugin error",
                "finalize successful runtime result",
                f"`{plugin_name}.work_finalize`",
                "SUCCESS",
                "SUCCESS",
            ),
            (
                "WORK_ACTIVE",
                "work_failed",
                "active capability returned non-retryable plugin failure",
                "finalize runtime plugin failure",
                f"`{plugin_name}.work_finalize`",
                "FAILURE:PLUGIN_FAILURE",
                "FAIL_PLUGIN",
            ),
            (
                "WORK_ACTIVE",
                "work_failed",
                "active capability exceeded allowed duration",
                "finalize retryable timeout result",
                f"`{plugin_name}.work_finalize`",
                "RETRYABLE:PLUGIN_TIMEOUT",
                "FAIL_TIMEOUT",
            ),
        ]
    )

    capability_yaml = "\n".join(f"  - {capability}" for capability in capabilities)
    capability_yaml_registry = "\n".join(f"      - {capability}" for capability in capabilities)
    capability_map_yaml = "\n".join(
        line
        for capability, description in capability_rows
        for line in (
            f"  {capability}:",
            f"    plugin_id: {plugin_name}",
            f'    description: "{description}"',
        )
    )
    plugin_scope_yaml = "\n".join(f"    - {scope_entry}" for scope_entry in plugin_scope)
    transition_table = "\n".join(
        f"| {s} | {e} | {g} | {a} | {p} | {r} | {n} |"
        for s, e, g, a, p, r, n in transition_rows
    )
    diagram_lines = "\n".join(
        f"    {s} --> {n}: {e}" for s, e, _g, _a, _p, _r, n in transition_rows
    )

    source_section = ""
    if source_summary_lines:
        source_section = "\n".join(["", "## Source Notes", *source_summary_lines, ""])

    return "\n".join(
        [
            f"# {plugin_name} Operational Spec",
            "",
            "## Table of Contents",
            "- [Scope](#scope)",
            "- [Plugin Contract](#plugin-contract)",
            "- [Metadata](#metadata)",
            "- [Plugin Registry](#plugin-registry)",
            "- [Capability Map](#capability-map)",
            "- [Idempotency](#idempotency)",
            "- [Invariants](#invariants)",
            "- [Transition Table](#transition-table)",
            "- [Diagram](#diagram)",
            "- [Dry-Run Simulation](#dry-run-simulation)",
            "- [Transition Tracing](#transition-tracing)",
            "- [Logs](#logs)",
            "",
            "## Scope",
            f"This operational spec models the packaged `{plugin_name}` plugin behavior after creation or conversion.",
            "Transition table is the source of truth.",
            source_section.rstrip(),
            "",
            "## Plugin Contract",
            "```yaml",
            f"plugin_id: {plugin_name}",
            "capabilities:",
            capability_yaml,
            "result_status:",
            "  - SUCCESS",
            "  - FAILURE",
            "  - RETRYABLE",
            "errors:",
            "  - VALIDATION_ERROR",
            "  - BLOCKED_DEPENDENCY",
            "  - POLICY_FAIL",
            "  - SYSTEM_ERROR",
            "  - PLUGIN_TIMEOUT",
            "  - PLUGIN_FAILURE",
            "```",
            "",
            "## Metadata",
            "```yaml",
            "metadata:",
            "  owner: \"[TODO: plugin owner]\"",
            "  max_duration: \"validation <= 30s, runtime <= plugin-specific\"",
            "  escalation: \"escalate when validation fails, routing is ambiguous, or runtime dependencies are blocked\"",
            "  plugin_scope:",
            plugin_scope_yaml,
            "```",
            "",
            "## Plugin Registry",
            "```yaml",
            "plugin_registry:",
            f"  {plugin_name}:",
            f"    plugin_id: {plugin_name}",
            "    capabilities:",
            capability_yaml_registry,
            "```",
            "",
            "## Capability Map",
            "```yaml",
            "capability_map:",
            capability_map_yaml,
            "```",
            "",
            "## Idempotency",
            "- validation is idempotent for unchanged plugin contents.",
            "- session start activation is idempotent per identical runtime session input.",
            "- route selection must be deterministic for the same `(S,E,G)` tuple.",
            "- context attachment actions are idempotent when the requested context is already attached.",
            "",
            "## Invariants",
            "- failure states are terminal.",
            "- success state is terminal.",
            "- every plugin capability invocation must reference the plugin in `plugin_registry`.",
            "- non-terminal states must resolve through at least one deterministic transition.",
            "- plugin-created or plugin-converted packages must keep `references/operational-spec.md` present.",
            "",
            "## Transition Table",
            "| S | E | G | A | P | R | N |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            transition_table,
            "",
            "## Diagram",
            "```mermaid",
            "stateDiagram-v2",
            diagram_lines,
            "```",
            "",
            "## Dry-Run Simulation",
            "Dry-run evaluates transitions without mutating package or runtime state.",
            "",
            "```text",
            "1. Start with input state S and event E.",
            "2. Filter transition rows where S and E match exactly.",
            "3. Evaluate guards in row order until exactly one guard resolves true.",
            "4. Emit A, P, R, and N as the simulated transition.",
            "5. If no guard resolves true, return FAILURE:VALIDATION_ERROR to FAIL_VALIDATION.",
            "6. If more than one guard resolves true, return FAILURE:SYSTEM_ERROR to FAIL_SYSTEM.",
            "```",
            "",
            "## Transition Tracing",
            "Transition code format: `TC::<from_state>::<event>::<to_state>`",
            "",
            "## Logs",
            "```yaml",
            "logs:",
            '  workflow_id: "<uuid>"',
            f'  plugin_id: "{plugin_name}"',
            '  capability: "<capability name>"',
            '  transition_code: "TC::<from_state>::<event>::<to_state>"',
            '  from_state: "<state>"',
            '  to_state: "<state>"',
            '  correlation_id: "<trace or request id>"',
            '  result: "SUCCESS | FAILURE:<error> | RETRYABLE:<error>"',
            "```",
            "",
        ]
    )


def _is_relative_plugin_path(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("./")


def _path_within_root(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _normalize_declared_paths(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def _resolve_surface_paths(
    plugin_root: Path,
    declared_value: Any,
    defaults: list[str],
) -> list[dict[str, Any]]:
    raw_paths = _normalize_declared_paths(declared_value) or defaults
    resolved_items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_path in raw_paths:
        candidate = (plugin_root / raw_path).resolve()
        candidate_key = str(candidate)
        if candidate_key in seen:
            continue
        seen.add(candidate_key)
        resolved_items.append(
            {
                "declared": raw_path,
                "resolved": candidate_key,
                "exists": candidate.exists(),
                "within_plugin_root": _path_within_root(plugin_root, candidate),
            }
        )
    return resolved_items


def _safe_read_text(path: Path, max_chars: int = 4000) -> str:
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except (UnicodeDecodeError, OSError):
        return ""


def _detect_deprecated_command_files(plugin_root: Path, resolved_paths: dict[str, list[dict[str, Any]]]) -> list[str]:
    deprecated_files: list[str] = []
    for item in resolved_paths.get("commands", []):
        if not item["exists"] or not item["within_plugin_root"]:
            continue
        candidate = Path(item["resolved"])
        if not candidate.is_dir():
            continue
        for markdown_file in sorted(candidate.glob("*.md")):
            content = _safe_read_text(markdown_file, max_chars=1200).lower()
            if "deprecated" in content and "skill" in content:
                deprecated_files.append(str(markdown_file))
    return deprecated_files


def _detect_hook_glue_signals(plugin_root: Path, resolved_paths: dict[str, list[dict[str, Any]]]) -> list[str]:
    signals: list[str] = []
    hooks_root = plugin_root / "hooks"
    if not hooks_root.exists() or not hooks_root.is_dir():
        return signals

    wrapper_script = hooks_root / "run-hook.cmd"
    if wrapper_script.exists():
        signals.append(str(wrapper_script))

    for hook_file in sorted(hooks_root.iterdir()):
        if not hook_file.is_file() or hook_file.name == "run-hook.cmd":
            continue
        content = _safe_read_text(hook_file)
        if not content:
            continue
        if "CLAUDE_PLUGIN_ROOT" in content:
            signals.append(f"{hook_file}:uses_CLAUDE_PLUGIN_ROOT")
        if "hookSpecificOutput" in content and "additional_context" in content:
            signals.append(f"{hook_file}:multiplexes_provider_payload_fields")
    return signals


def _existing_provider_manifests(plugin_root: Path) -> list[str]:
    return [
        manifest_rel
        for manifest_rel in SOURCE_PROVIDER_MANIFESTS
        if (plugin_root / manifest_rel).exists()
    ]


def _select_primary_source_manifest(plugin_root: Path) -> Path | None:
    for manifest_rel in SOURCE_PROVIDER_MANIFESTS:
        manifest_path = plugin_root / manifest_rel
        if manifest_path.exists():
            return manifest_path
    return None


def _load_existing_plugin_signature(plugin_root: Path) -> dict[str, Any] | None:
    plugin_manifest = plugin_root / ".codex-plugin" / "plugin.json"
    if not plugin_manifest.exists():
        return None
    payload = load_json(plugin_manifest)
    return _plugin_signature_from_payload(plugin_root, payload)


def _collect_existing_plugin_signatures(plugin_parent: Path) -> list[dict[str, Any]]:
    plugin_parent = plugin_parent.expanduser().resolve()
    if not plugin_parent.exists() or not plugin_parent.is_dir():
        return []

    signatures: list[dict[str, Any]] = []
    for child in sorted(plugin_parent.iterdir()):
        if not child.is_dir():
            continue
        signature = _load_existing_plugin_signature(child)
        if signature is not None:
            signatures.append(signature)
    return signatures


def _ratio_overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / float(max(len(left), len(right)))


def _score_plugin_overlap(
    candidate: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    candidate_name = normalize_plugin_name(str(candidate.get("name") or ""))
    candidate_source_name = normalize_plugin_name(str(candidate.get("source_name") or ""))
    existing_name = normalize_plugin_name(str(existing.get("name") or ""))
    name_exact = candidate_name == existing_name
    source_name_exact = bool(candidate_source_name) and candidate_source_name == existing_name

    candidate_tokens = set(candidate.get("text_tokens") or [])
    existing_tokens = set(existing.get("text_tokens") or [])
    token_overlap = _ratio_overlap(candidate_tokens, existing_tokens)

    candidate_keywords = _tokenize_text(" ".join(candidate.get("keywords") or []))
    existing_keywords = _tokenize_text(" ".join(existing.get("keywords") or []))
    keyword_overlap = _ratio_overlap(candidate_keywords, existing_keywords)

    candidate_caps = _tokenize_text(" ".join(candidate.get("capabilities") or []))
    existing_caps = _tokenize_text(" ".join(existing.get("capabilities") or []))
    capability_overlap = _ratio_overlap(candidate_caps, existing_caps)

    candidate_surfaces = {
        key for key, enabled in (candidate.get("surface_flags") or {}).items() if enabled
    }
    existing_surfaces = {
        key for key, enabled in (existing.get("surface_flags") or {}).items() if enabled
    }
    surface_overlap = _ratio_overlap(candidate_surfaces, existing_surfaces)

    score = 0.0
    if name_exact:
        score += 0.6
    if source_name_exact:
        score += 0.45
    score += token_overlap * 0.2
    score += keyword_overlap * 0.1
    score += capability_overlap * 0.05
    score += surface_overlap * 0.05

    reasons: list[str] = []
    if name_exact:
        reasons.append("exact plugin name match")
    if source_name_exact:
        reasons.append("source plugin matches existing package")
    if token_overlap >= 0.34:
        reasons.append(f"text overlap={token_overlap:.2f}")
    if keyword_overlap >= 0.34:
        reasons.append(f"keyword overlap={keyword_overlap:.2f}")
    if capability_overlap >= 0.5:
        reasons.append(f"capability overlap={capability_overlap:.2f}")
    if surface_overlap >= 0.5:
        reasons.append(f"surface overlap={surface_overlap:.2f}")

    classification = "distinct"
    if name_exact:
        classification = "exact"
    elif source_name_exact or score >= SIMILAR_PLUGIN_SCORE_THRESHOLD:
        classification = "similar"

    return {
        "plugin_name": existing.get("name"),
        "plugin_root": existing.get("root"),
        "classification": classification,
        "score": round(score, 3),
        "reasons": reasons,
        "shared_surfaces": sorted(candidate_surfaces & existing_surfaces),
    }


def _find_existing_plugin_overlaps(
    plugin_name: str,
    plugin_parent: Path,
    source_report: dict[str, Any] | None = None,
    exclude_root: Path | None = None,
) -> dict[str, Any]:
    candidate = _source_signature_from_report(plugin_name, source_report)
    overlaps: list[dict[str, Any]] = []
    exclude_resolved = str(exclude_root.expanduser().resolve()) if exclude_root else None

    for existing in _collect_existing_plugin_signatures(plugin_parent):
        existing_root = str(existing["root"])
        if exclude_resolved and existing_root == exclude_resolved:
            continue
        scored = _score_plugin_overlap(candidate, existing)
        if scored["classification"] == "distinct":
            continue
        overlaps.append(scored)

    overlaps.sort(key=lambda item: (item["classification"] != "exact", -item["score"], item["plugin_name"]))
    exact_matches = [item for item in overlaps if item["classification"] == "exact"]
    similar_matches = [item for item in overlaps if item["classification"] == "similar"]

    recommendation = "new-plugin-ok"
    if exact_matches:
        recommendation = "merge-or-update-existing"
    elif similar_matches:
        recommendation = "review-fold-or-improve-first"

    return {
        "candidate_name": candidate.get("name") or plugin_name,
        "plugin_parent": str(plugin_parent.expanduser().resolve()),
        "recommendation": recommendation,
        "exact_matches": exact_matches,
        "similar_matches": similar_matches,
    }


def _deconflict_report_template(overlap_report: dict[str, Any]) -> str:
    lines = [
        "# Plugin Deconflict Report",
        "",
        "## Summary",
        f"- Candidate: `{overlap_report['candidate_name']}`",
        f"- Plugin parent: `{overlap_report['plugin_parent']}`",
        f"- Recommendation: `{overlap_report['recommendation']}`",
        "",
    ]

    for title, key in (
        ("Exact matches", "exact_matches"),
        ("Similar matches", "similar_matches"),
    ):
        matches = overlap_report.get(key) or []
        lines.append(f"## {title}")
        if not matches:
            lines.append("- none")
            lines.append("")
            continue
        for match in matches:
            reasons = ", ".join(match.get("reasons") or ["overlap detected"])
            shared_surfaces = ", ".join(match.get("shared_surfaces") or ["none"])
            lines.append(f"- `{match['plugin_name']}` at `{match['plugin_root']}`")
            lines.append(f"  score: `{match['score']}`; reasons: {reasons}; shared surfaces: {shared_surfaces}")
        lines.append("")

    lines.extend(
        [
            "## Decision rule",
            "- Prefer merge, fold, or improvement work when an exact or strong similar match already exists.",
            "- Only create a fresh plugin package when the overlap review says the existing packages do not cover the intended job.",
            "",
        ]
    )
    return "\n".join(lines)


def _inspect_source_plugin(plugin_root: Path) -> dict[str, Any]:
    plugin_root = plugin_root.expanduser().resolve()
    provider_manifests = _existing_provider_manifests(plugin_root)
    primary_manifest = _select_primary_source_manifest(plugin_root)
    payload = load_json(primary_manifest) if primary_manifest is not None else {}

    plugin_name = payload.get("name") if isinstance(payload.get("name"), str) else plugin_root.name
    custom_path_overrides: dict[str, Any] = {}
    resolved_paths: dict[str, list[dict[str, Any]]] = {}
    for surface_name, defaults in SOURCE_SURFACE_DEFAULTS.items():
        declared_value = payload.get(surface_name)
        if surface_name == "mcpServers" and isinstance(declared_value, dict):
            declared_value = None
        normalized_declared_paths = _normalize_declared_paths(declared_value)
        if normalized_declared_paths:
            custom_path_overrides[surface_name] = (
                normalized_declared_paths[0]
                if len(normalized_declared_paths) == 1
                else normalized_declared_paths
            )
        resolved_paths[surface_name] = _resolve_surface_paths(
            plugin_root,
            declared_value,
            defaults,
        )

    inline_mcp_servers = payload.get("mcpServers") if isinstance(payload.get("mcpServers"), dict) else None
    native_codex_docs = [
        str(plugin_root / relative_path)
        for relative_path in SOURCE_CODEX_SUPPORT_DOCS
        if (plugin_root / relative_path).exists()
    ]
    deprecated_command_files = _detect_deprecated_command_files(plugin_root, resolved_paths)
    hook_glue_signals = _detect_hook_glue_signals(plugin_root, resolved_paths)
    detected_surfaces = {
        surface_name: any(item["exists"] for item in items)
        for surface_name, items in resolved_paths.items()
    }

    notes: list[str] = []
    if len(provider_manifests) > 1:
        notes.append("Multiple provider manifests detected; treat sibling manifests as migration references.")
    if custom_path_overrides:
        notes.append("Manifest declares custom paths; conversion must resolve surfaces from the manifest, not defaults.")
    if inline_mcp_servers is not None:
        notes.append("Manifest embeds inline MCP definitions; prefer comparing them against any .mcp.json before conversion.")
    if inline_mcp_servers is not None and detected_surfaces["mcpServers"]:
        notes.append("Inline MCP definitions and file-based MCP config both exist; compare them for drift before emitting Codex .mcp.json.")
    if native_codex_docs:
        notes.append("Source already ships Codex-native install or usage docs; decide whether plugin packaging is additive or redundant.")
    if deprecated_command_files:
        notes.append("Deprecated command shims detected; inspect command contents before converting them into Codex prompts.")
    if hook_glue_signals:
        notes.append("Hook wrappers or provider-specific hook glue detected; preserve hook intent but rewrite Codex runtime shape explicitly.")
    for surface_name, items in resolved_paths.items():
        if any(not item["within_plugin_root"] for item in items):
            notes.append(
                f"{surface_name} declares a path outside the plugin root; reject path traversal before conversion."
            )

    return {
        "plugin_root": str(plugin_root),
        "plugin_name": plugin_name,
        "primary_manifest": str(primary_manifest) if primary_manifest is not None else None,
        "provider_manifests": provider_manifests,
        "custom_path_overrides": custom_path_overrides,
        "resolved_paths": resolved_paths,
        "detected_surfaces": detected_surfaces,
        "inline_mcp_server_names": sorted(inline_mcp_servers.keys()) if inline_mcp_servers else [],
        "native_codex_docs": native_codex_docs,
        "deprecated_command_files": deprecated_command_files,
        "hook_glue_signals": hook_glue_signals,
        "notes": notes,
    }


def _inspect_source_root(source_root: Path) -> dict[str, Any]:
    source_root = source_root.expanduser().resolve()
    marketplace_manifests = [
        str(source_root / manifest_rel)
        for manifest_rel in SOURCE_MARKETPLACE_MANIFESTS
        if (source_root / manifest_rel).exists()
    ]

    candidate_roots: list[Path] = []
    if _existing_provider_manifests(source_root):
        candidate_roots.append(source_root)

    nested_plugin_parent = source_root / "plugins"
    if nested_plugin_parent.exists() and nested_plugin_parent.is_dir():
        for child in sorted(nested_plugin_parent.iterdir()):
            if child.is_dir() and _existing_provider_manifests(child):
                candidate_roots.append(child)

    plugin_reports: list[dict[str, Any]] = []
    seen_roots: set[str] = set()
    for candidate_root in candidate_roots:
        resolved_candidate = str(candidate_root.resolve())
        if resolved_candidate in seen_roots:
            continue
        seen_roots.add(resolved_candidate)
        plugin_reports.append(_inspect_source_plugin(candidate_root))

    source_kind = "unknown"
    if marketplace_manifests or any(Path(report["plugin_root"]) != source_root for report in plugin_reports):
        source_kind = "marketplace_repo"
    elif plugin_reports:
        source_kind = "plugin_root"

    return {
        "source_root": str(source_root),
        "source_kind": source_kind,
        "marketplace_manifests": marketplace_manifests,
        "plugin_roots": plugin_reports,
    }


def _select_source_plugin_for_scaffold(source_path: Path, plugin_name: str) -> dict[str, Any]:
    inspection = _inspect_source_root(source_path)
    plugin_roots = inspection["plugin_roots"]
    if not plugin_roots:
        raise ValueError(
            f"No provider manifests found under source path {source_path.expanduser().resolve()}."
        )
    if len(plugin_roots) == 1:
        return plugin_roots[0]

    normalized_plugin_name = normalize_plugin_name(plugin_name)
    for report in plugin_roots:
        report_name = report.get("plugin_name")
        if isinstance(report_name, str) and normalize_plugin_name(report_name) == normalized_plugin_name:
            return report
        report_root_name = Path(report["plugin_root"]).name
        if normalize_plugin_name(report_root_name) == normalized_plugin_name:
            return report

    available_plugins = ", ".join(
        sorted(str(report.get("plugin_name") or Path(report["plugin_root"]).name) for report in plugin_roots)
    )
    raise ValueError(
        "Multiple plugin roots detected under source path; could not select one automatically "
        f"for scaffold '{plugin_name}'. Available: {available_plugins}"
    )


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
    plugin_root = plugin_json_path.parent.parent

    if "name" not in payload:
        failures.append("Missing required plugin.json field: name")

    name = payload.get("name")
    if isinstance(name, str):
        try:
            validate_plugin_name(name)
        except ValueError as exc:
            failures.append(f"Invalid plugin name: {exc}")
    else:
        failures.append("plugin.json field 'name' must be a string.")

    for field_name in OPTIONAL_PLUGIN_STRING_FIELDS:
        if field_name in payload and not isinstance(payload[field_name], str):
            failures.append(f"plugin.json field '{field_name}' must be a string.")

    if "keywords" in payload:
        failures.extend(
            _check_string_list(payload.get("keywords"), "plugin.json field 'keywords'")
        )

    if "author" in payload:
        author = payload.get("author")
        if not isinstance(author, dict):
            failures.append("plugin.json field 'author' must be an object.")
        else:
            for key in OPTIONAL_AUTHOR_FIELDS:
                if key in author and not isinstance(author[key], str):
                    failures.append(f"plugin.json author.{key} must be a string.")

    for path_key in OPTIONAL_PLUGIN_PATH_FIELDS:
        if path_key in payload:
            failures.extend(
                _check_declared_plugin_path(
                    plugin_root,
                    f"plugin.json field '{path_key}'",
                    payload[path_key],
                    require_exists=True,
                )
            )

    interface = payload.get("interface")
    if interface is not None:
        if not isinstance(interface, dict):
            failures.append("plugin.json field 'interface' must be an object when present.")
        else:
            for key in OPTIONAL_INTERFACE_STRING_FIELDS:
                if key in interface and not isinstance(interface[key], str):
                    failures.append(f"plugin.json interface.{key} must be a string.")

            if "capabilities" in interface:
                failures.extend(
                    _check_string_list(
                        interface.get("capabilities"),
                        "plugin.json interface.capabilities",
                    )
                )
            if "screenshots" in interface:
                failures.extend(
                    _check_string_list(
                        interface.get("screenshots"),
                        "plugin.json interface.screenshots",
                    )
                )
                if isinstance(interface.get("screenshots"), list):
                    for index, screenshot in enumerate(interface["screenshots"]):
                        failures.extend(
                            _check_declared_plugin_path(
                                plugin_root,
                                f"plugin.json interface.screenshots[{index}]",
                                screenshot,
                                require_exists=False,
                            )
                        )
            if "defaultPrompt" in interface:
                failures.extend(_check_default_prompt(interface.get("defaultPrompt")))

            for path_key in OPTIONAL_INTERFACE_PATH_FIELDS:
                if path_key in interface:
                    failures.extend(
                        _check_declared_plugin_path(
                            plugin_root,
                            f"plugin.json interface.{path_key}",
                            interface[path_key],
                            require_exists=False,
                        )
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
    interface = marketplace_payload.get("interface")
    if interface is not None:
        if not isinstance(interface, dict):
            failures.append("marketplace.json field 'interface' must be an object when present.")
        else:
            display_name = interface.get("displayName")
            if not isinstance(display_name, str) or not display_name.strip():
                failures.append(
                    "marketplace.json interface.displayName must be a non-empty string when present."
                )

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

    policy = plugin_entry.get("policy")
    install_policy = None
    auth_policy = None
    if isinstance(policy, dict):
        install_policy = policy.get("installation")
        auth_policy = policy.get("authentication")
    else:
        install_policy = plugin_entry.get("installPolicy")
        auth_policy = plugin_entry.get("authPolicy")

    if install_policy not in VALID_INSTALL_POLICIES:
        failures.append(
            f"marketplace plugin '{plugin_name}' policy.installation "
            f"(or legacy installPolicy) must be one of "
            f"{sorted(VALID_INSTALL_POLICIES)}."
        )

    if auth_policy not in VALID_AUTH_POLICIES:
        failures.append(
            f"marketplace plugin '{plugin_name}' policy.authentication "
            f"(or legacy authPolicy) must be one of "
            f"{sorted(VALID_AUTH_POLICIES)}."
        )

    category = plugin_entry.get("category")
    if category is not None and (not isinstance(category, str) or not category):
        failures.append(
            f"marketplace plugin '{plugin_name}' category must be a non-empty string when present."
        )

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

    source_report: dict[str, Any] | None = None
    if args.from_source_path:
        source_report = _select_source_plugin_for_scaffold(
            Path(args.from_source_path),
            plugin_name,
        )
        print(f"Detected source plugin root: {source_report['plugin_root']}")

    overlap_report = _find_existing_plugin_overlaps(
        plugin_name,
        Path(args.path),
        source_report=source_report,
        exclude_root=plugin_root if plugin_root.exists() else None,
    )
    if overlap_report["exact_matches"] or overlap_report["similar_matches"]:
        print("Local plugin overlap review:")
        print(json.dumps(overlap_report, indent=2))
        if not args.allow_overlap and not args.force:
            print(
                "ERROR: existing local plugin overlap detected. "
                "Review merge/fold/improve options first or rerun with --allow-overlap.",
                file=sys.stderr,
            )
            return 2

    optional_directories = {
        "skills": args.with_skills or bool(source_report and source_report["detected_surfaces"]["skills"]),
        "hooks": args.with_hooks or bool(source_report and (Path(source_report["plugin_root"]) / "hooks").exists()),
        "prompts": args.with_prompts,
        "agents": args.with_agents or bool(source_report and source_report["detected_surfaces"]["agents"]),
        "scripts": args.with_scripts,
        "assets": args.with_assets,
    }
    for folder, enabled in optional_directories.items():
        if enabled:
            (plugin_root / folder).mkdir(parents=True, exist_ok=True)

    enabled_surfaces = {
        "skills": optional_directories["skills"],
        "hooks": args.with_hooks_json or optional_directories["hooks"] or bool(source_report and source_report["detected_surfaces"]["hooks"]),
        "prompts": optional_directories["prompts"],
        "agents": optional_directories["agents"],
        "mcp": bool(
            args.with_mcp
            or (
                source_report
                and (
                    source_report["detected_surfaces"]["mcpServers"]
                    or bool(source_report["inline_mcp_server_names"])
                )
            )
        ),
        "apps": bool(args.with_apps or (source_report and source_report["detected_surfaces"].get("apps"))),
        "assets": optional_directories["assets"],
    }

    plugin_root.mkdir(parents=True, exist_ok=True)

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    write_json(plugin_json_path, build_plugin_json(plugin_name, enabled_surfaces), args.force)
    write_text(plugin_root / "README.md", _readme_template(plugin_name), args.force)
    write_text(plugin_root / "LICENSE", _license_template(), args.force)

    write_text(
        plugin_root / "references" / "operational-spec.md",
        _operational_spec_template(
            plugin_name,
            enabled_surfaces=enabled_surfaces,
            source_report=source_report,
            includes_marketplace=bool(args.with_marketplace),
        ),
        args.force,
    )
    write_text(
        plugin_root / "references" / "deconflict-report.md",
        _deconflict_report_template(overlap_report),
        args.force,
    )

    if enabled_surfaces["hooks"]:
        create_stub_file(
            plugin_root / "hooks.json",
            {"hooks": {"SessionStart": [], "Stop": []}},
            args.force,
        )

    if args.with_mcp or (
        source_report
        and (
            source_report["detected_surfaces"]["mcpServers"]
            or bool(source_report["inline_mcp_server_names"])
        )
    ):
        create_stub_file(
            plugin_root / ".mcp.json",
            {"mcpServers": {}},
            args.force,
        )

    if enabled_surfaces["apps"]:
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
    source_inspection = _inspect_source_root(plugin_root)
    if not plugin_json_path.exists() and source_inspection["plugin_roots"]:
        findings.append(
            "Path looks like a source marketplace/plugin repo with provider manifests, not a converted Codex package. "
            "Run `plugin_builder.py inspect-source <path>` first."
        )

    if plugin_json_path.exists():
        findings.extend(_check_plugin_manifest(plugin_json_path))
        overlap_report = _find_existing_plugin_overlaps(
            plugin_root.name,
            plugin_root.parent,
            exclude_root=plugin_root,
        )
        if overlap_report["exact_matches"] or overlap_report["similar_matches"]:
            findings.append(
                "Local plugin overlap detected in sibling plugin directory. "
                "Review references/deconflict-report.md and confirm merge/fold/improve intent."
            )
            deconflict_report_path = plugin_root / "references" / "deconflict-report.md"
            if not deconflict_report_path.exists():
                findings.append(
                    f"Missing deconflict report for overlapping plugin intent: {deconflict_report_path}"
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

    _print_findings(findings)
    return 0 if not findings else 2


def _run_inspect_source(args: argparse.Namespace) -> int:
    source_root = Path(args.source_path).expanduser().resolve()
    if not source_root.exists() or not source_root.is_dir():
        print(f"ERROR: source path is not a directory: {source_root}", file=sys.stderr)
        return 1
    inspection = _inspect_source_root(source_root)
    print(json.dumps(inspection, indent=2))
    return 0


def _run_inspect_local(args: argparse.Namespace) -> int:
    source_report: dict[str, Any] | None = None
    if args.from_source_path:
        source_report = _select_source_plugin_for_scaffold(
            Path(args.from_source_path),
            args.plugin_name,
        )

    overlap_report = _find_existing_plugin_overlaps(
        args.plugin_name,
        Path(args.path),
        source_report=source_report,
    )
    print(json.dumps(overlap_report, indent=2))
    return 0


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
    scaffold_parser.add_argument(
        "--from-source-path",
        help="Optional source repo or plugin path to inspect for scaffold surface auto-detection.",
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
        help="Marketplace policy.installation value.",
    )
    scaffold_parser.add_argument(
        "--auth-policy",
        default=DEFAULT_AUTH_POLICY,
        choices=sorted(VALID_AUTH_POLICIES),
        help="Marketplace policy.authentication value.",
    )
    scaffold_parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help="Marketplace category value.",
    )
    scaffold_parser.add_argument(
        "--allow-overlap",
        action="store_true",
        help="Allow scaffolding when an exact or similar local plugin already exists.",
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

    inspect_parser = subparsers.add_parser(
        "inspect-source",
        help="Inspect a source marketplace or plugin repo for plugin roots, custom paths, and MCP definitions.",
    )
    inspect_parser.add_argument("source_path", help="Path to a source repo or plugin root.")

    inspect_local_parser = subparsers.add_parser(
        "inspect-local",
        help="Inspect existing local plugins for exact or similar overlap before scaffolding.",
    )
    inspect_local_parser.add_argument("plugin_name", help="Candidate plugin name.")
    inspect_local_parser.add_argument(
        "--path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Parent directory containing local plugin packages to compare against.",
    )
    inspect_local_parser.add_argument(
        "--from-source-path",
        help="Optional source repo or plugin path to improve overlap scoring using source metadata.",
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
    if args.command == "inspect-source":
        raise SystemExit(_run_inspect_source(args))
    if args.command == "inspect-local":
        raise SystemExit(_run_inspect_local(args))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
