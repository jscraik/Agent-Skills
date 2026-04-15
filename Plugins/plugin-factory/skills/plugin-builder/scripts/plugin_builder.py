#!/usr/bin/env python3
"""Scaffold and validate Codex plugin packages plus marketplace entries.

This tool requires `uv` for Python helper execution in scaffold flows.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable


MAX_PLUGIN_NAME_LENGTH = 64
PLUGIN_NAME_RE = re.compile(r"^[a-z0-9](?:-?[a-z0-9]){0,63}$")


def _discover_repo_root() -> Path:
    """
    Discover the repository root directory for this project.
    
    Searches the ancestor directories of this file and returns the first directory that contains a "plugins" subdirectory and either a ".git" entry or both "Plugins/plugin-factory/skills" and ".agents". If no such ancestor is found, returns the current working directory resolved to an absolute Path.
    
    Returns:
        Path: The discovered repository root directory, or the resolved current working directory if no match is found.
    """
    def _looks_like_repo_root(candidate: Path) -> bool:
        if not (candidate / "plugins").is_dir():
            return False
        if (candidate / ".git").exists():
            return True
        return (candidate / "plugins" / "plugin-factory" / "skills").is_dir() and (
            candidate / ".agents"
        ).is_dir()

    for ancestor in Path(__file__).resolve().parents:
        if _looks_like_repo_root(ancestor):
            return ancestor
    return Path.cwd().resolve()


REPO_ROOT = _discover_repo_root()
DEFAULT_PLUGIN_PARENT = REPO_ROOT / "plugins"
DEFAULT_MARKETPLACE_PATH = REPO_ROOT / ".agents" / "Plugins" / "marketplace.json"
SKILL_BUILDER_INIT = REPO_ROOT / "Skills" / "skill-builder" / "scripts" / "init_skill.py"
SHARED_SKILL_CONTRACT_DIR = REPO_ROOT / "Infrastructure" / "scripts"
if str(SHARED_SKILL_CONTRACT_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_SKILL_CONTRACT_DIR))
from canonical_skill_roots import CANONICAL_STANDALONE_SKILL_ROOTS  # noqa: E402

CODEX_AGENT_WRITER = (
    REPO_ROOT / "utilities" / "codex-agent-creator" / "scripts" / "write_role_config.sh"
)
DOCS_EXPERT_ASSETS = REPO_ROOT / "product" / "docs" / "docs-expert" / "assets"
DEFAULT_INSTALL_POLICY = "AVAILABLE"
DEFAULT_AUTH_POLICY = "ON_INSTALL"
DEFAULT_CATEGORY = "Productivity"
DEFAULT_OWNER = "Plugin Maintainers"
DEFAULT_AUTHOR_EMAIL = "maintainers@example.com"
DEFAULT_AUTHOR_URL = "https://github.com/example"
DEFAULT_PRIVACY_URL = "https://example.com/privacy"
DEFAULT_TERMS_URL = "https://example.com/terms"
DEFAULT_MARKETPLACE_NAME = "local-marketplace"
DEFAULT_MARKETPLACE_DISPLAY_NAME = "Local Plugins"
VALID_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
VALID_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
VALID_POLICY_PRODUCTS = {"CHATGPT", "CODEX", "ATLAS"}
DEFAULT_POLICY_PRODUCTS = ["CODEX"]
OPENAI_MARKETPLACE_RELATIVE_PATH = ".agents/Plugins/marketplace.json"
PINNED_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")
UV_INSTALL_HINT = "Install uv from https://docs.astral.sh/uv/getting-started/installation/."
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
# NOTE: interface.defaultPrompt is intentionally excluded from OPTIONAL_INTERFACE_STRING_FIELDS.
# It is validated separately because the contract allows either a string or an array of strings.
OPTIONAL_INTERFACE_PATH_FIELDS = ["composerIcon", "logo"]

CLAUDE_TO_CODEX_TERMINOLOGY = {
    "commands/": "skills/ plus optional interface.defaultPrompt",
    "prompts/": "skills/ plus optional interface.defaultPrompt",
    "slash commands": "skills/",
    "slash-commands": "skills/",
    "commands key": "skills/ plus optional interface.defaultPrompt",
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
DEFAULT_ARCHETYPE = "general"
ARCHETYPE_PROFILES: dict[str, dict[str, Any]] = {
    "general": {
        "display_name": "General",
        "category": "Productivity",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["workflow", "assistant"],
        "description": "A curated Codex plugin package for reusable workflows.",
        "short_description": "Reusable workflows packaged for Codex",
        "long_description": "A curated Codex plugin package that groups reusable workflows and optional integration surfaces.",
        "default_prompt": "Use this plugin to handle its primary workflow end to end.",
        "brand_color": "#3B82F6",
    },
    "coding_tool": {
        "display_name": "Coding Tool",
        "category": "Coding",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["coding", "developer-tools", "repository"],
        "description": "A Codex plugin package for codebase workflows and developer tooling.",
        "short_description": "Codebase workflows and developer tooling",
        "long_description": "A Codex plugin package that helps inspect repositories, modify code, and automate developer workflows.",
        "default_prompt": "Inspect this codebase and help me implement the next safe change.",
        "brand_color": "#2563EB",
    },
    "productivity_connector": {
        "display_name": "Productivity Connector",
        "category": "Productivity",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["productivity", "connector", "workspace"],
        "description": "A Codex plugin package for structured workspace and task workflows.",
        "short_description": "Workspace, planning, and task workflows",
        "long_description": "A Codex plugin package that connects structured workspace workflows, project context, and task actions.",
        "default_prompt": "Connect to this workspace and help me complete the next task.",
        "brand_color": "#0EA5E9",
    },
    "design_tool": {
        "display_name": "Design Tool",
        "category": "Design",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["design", "assets", "ui"],
        "description": "A Codex plugin package for design inspection, asset workflows, and UI implementation handoff.",
        "short_description": "Design inspection and UI handoff workflows",
        "long_description": "A Codex plugin package that supports design inspection, asset handling, and implementation-ready UI workflows.",
        "default_prompt": "Inspect the design context and help implement it accurately.",
        "brand_color": "#0D99FF",
    },
    "research_connector": {
        "display_name": "Research Connector",
        "category": "Research",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["research", "search", "knowledge"],
        "description": "A Codex plugin package for research, retrieval, and evidence-backed workflows.",
        "short_description": "Research and evidence-backed retrieval workflows",
        "long_description": "A Codex plugin package that helps gather sources, retrieve relevant context, and synthesize evidence-backed answers.",
        "default_prompt": "Gather the relevant sources and summarize the evidence for this question.",
        "brand_color": "#14B8A6",
    },
    "communication_connector": {
        "display_name": "Communication Connector",
        "category": "Communication",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["communication", "messages", "collaboration"],
        "description": "A Codex plugin package for messaging, collaboration, and communication workflows.",
        "short_description": "Messaging and collaboration workflows",
        "long_description": "A Codex plugin package that supports message retrieval, collaboration context, and communication tasks.",
        "default_prompt": "Find the relevant conversation and help me respond or summarize it.",
        "brand_color": "#8B5CF6",
    },
    "automation_orchestrator": {
        "display_name": "Automation Orchestrator",
        "category": "Productivity",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["automation", "workflow", "orchestrator"],
        "description": "A Codex plugin package for orchestrated multi-step workflows and automation.",
        "short_description": "Multi-step workflow orchestration",
        "long_description": "A Codex plugin package that coordinates repeatable multi-step workflows, integrations, and automation surfaces.",
        "default_prompt": "Run the next stage of this workflow and report what changed.",
        "brand_color": "#F59E0B",
    },
}
ARCHETYPE_TOKEN_HINTS: dict[str, set[str]] = {
    "coding_tool": {
        "code",
        "coding",
        "developer",
        "devtools",
        "github",
        "git",
        "repo",
        "repository",
        "terminal",
        "sentry",
        "debug",
    },
    "productivity_connector": {
        "drive",
        "docs",
        "sheets",
        "slides",
        "calendar",
        "notion",
        "linear",
        "task",
        "workspace",
        "todo",
        "productivity",
    },
    "design_tool": {
        "figma",
        "design",
        "asset",
        "assets",
        "icon",
        "image",
        "video",
        "media",
        "ui",
        "brand",
    },
    "research_connector": {
        "crawl",
        "docs",
        "knowledge",
        "research",
        "search",
        "web",
        "source",
        "evidence",
    },
    "communication_connector": {
        "chat",
        "communication",
        "conversation",
        "discord",
        "email",
        "gmail",
        "message",
        "messages",
        "slack",
        "mail",
    },
    "automation_orchestrator": {
        "agent",
        "automation",
        "automations",
        "orchestrate",
        "orchestrator",
        "pipeline",
        "workflow",
        "workflows",
    },
}


def _archetype_profile(archetype: str | None) -> dict[str, Any]:
    return ARCHETYPE_PROFILES.get(archetype or DEFAULT_ARCHETYPE, ARCHETYPE_PROFILES[DEFAULT_ARCHETYPE])


def _infer_plugin_archetype(
    plugin_name: str,
    *,
    payload: dict[str, Any] | None = None,
    enabled_surfaces: dict[str, bool] | None = None,
    plugin_root: Path | None = None,
) -> str:
    tokens: set[str] = _tokenize_text(plugin_name)
    if payload:
        interface = payload.get("interface") if isinstance(payload.get("interface"), dict) else {}
        tokens.update(
            _tokenize_text(
                str(payload.get("description") or ""),
                " ".join(_manifest_keywords(payload)),
                " ".join(_manifest_capabilities(payload)),
                str(interface.get("shortDescription") or ""),
                str(interface.get("longDescription") or ""),
                str(interface.get("category") or ""),
            )
        )
    surface_flags = dict(enabled_surfaces or {})
    if plugin_root is not None:
        surface_flags.setdefault("skills", (plugin_root / "skills").exists())
        surface_flags.setdefault("hooks", (plugin_root / "hooks.json").exists())
        surface_flags.setdefault("mcp", (plugin_root / ".mcp.json").exists())
        surface_flags.setdefault("apps", (plugin_root / ".app.json").exists())
        surface_flags.setdefault("agents", (plugin_root / "agents").exists())

    scores = {name: 0 for name in ARCHETYPE_PROFILES if name != DEFAULT_ARCHETYPE}
    for archetype, hints in ARCHETYPE_TOKEN_HINTS.items():
        scores[archetype] += len(tokens & hints) * 2

    if surface_flags.get("apps"):
        scores["productivity_connector"] += 2
        scores["communication_connector"] += 1
    if surface_flags.get("mcp"):
        scores["automation_orchestrator"] += 1
        scores["research_connector"] += 1
    if surface_flags.get("skills"):
        scores["coding_tool"] += 1
        scores["automation_orchestrator"] += 1
    if surface_flags.get("agents"):
        scores["automation_orchestrator"] += 2
        scores["coding_tool"] += 1
    if surface_flags.get("hooks"):
        scores["automation_orchestrator"] += 1

    best_archetype = max(scores, key=scores.get, default=DEFAULT_ARCHETYPE)
    if scores.get(best_archetype, 0) <= 0:
        return DEFAULT_ARCHETYPE
    return best_archetype


def _suggest_marketplace_category(
    plugin_name: str,
    *,
    archetype: str | None = None,
    payload: dict[str, Any] | None = None,
    enabled_surfaces: dict[str, bool] | None = None,
    plugin_root: Path | None = None,
) -> str:
    inferred = archetype or _infer_plugin_archetype(
        plugin_name,
        payload=payload,
        enabled_surfaces=enabled_surfaces,
        plugin_root=plugin_root,
    )
    return str(_archetype_profile(inferred)["category"])


def _display_name(plugin_name: str) -> str:
    return _display_name_from_identifier(plugin_name)


def _default_repo_url(plugin_name: str) -> str:
    return f"{DEFAULT_AUTHOR_URL}/{plugin_name}"


def _default_docs_url(plugin_name: str) -> str:
    return f"https://example.com/Plugins/{plugin_name}"


def _default_owner(plugin_name: str) -> str:
    return f"{_display_name(plugin_name)} Team"


def _surface_summary(enabled_surfaces: dict[str, bool]) -> list[str]:
    surfaces = [".codex-plugin/plugin.json", "README.md", "LICENSE", "Infrastructure/references/operational-spec.md"]
    if enabled_surfaces.get("skills"):
        surfaces.append("skills/<skill>/SKILL.md")
    if enabled_surfaces.get("agents"):
        surfaces.append("agents/<agent>.toml")
    if enabled_surfaces.get("hooks"):
        surfaces.append("hooks.json")
    if enabled_surfaces.get("mcp"):
        surfaces.append(".mcp.json")
    if enabled_surfaces.get("apps"):
        surfaces.append(".app.json")
    if enabled_surfaces.get("assets"):
        surfaces.append("assets/")
    return surfaces


def _load_docs_asset(name: str) -> str:
    return (DOCS_EXPERT_ASSETS / name).read_text(encoding="utf-8")


def _run_helper(command: list[str], description: str) -> str:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()

    details = [f"{description} failed with exit code {result.returncode}."]
    if result.stdout.strip():
        details.append("stdout:")
        details.append(result.stdout.strip())
    if result.stderr.strip():
        details.append("stderr:")
        details.append(result.stderr.strip())
    raise RuntimeError("\n".join(details))


def _uv_python_command() -> list[str]:
    uv_bin = shutil.which("uv")
    if not uv_bin:
        raise RuntimeError(
            "uv is required for Python helper execution in plugin-builder but was not found in PATH. "
            f"{UV_INSTALL_HINT}"
        )
    return [uv_bin, "run", "python"]


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
    if not PLUGIN_NAME_RE.fullmatch(plugin_name):
        raise ValueError(
            "Plugin name must be kebab-case and match "
            "`[a-z0-9](?:-?[a-z0-9]){0,63}`."
        )


def build_plugin_json(
    plugin_name: str,
    enabled_surfaces: dict[str, bool] | None = None,
    *,
    archetype: str | None = None,
) -> dict[str, Any]:
    enabled_surfaces = enabled_surfaces or {}
    profile = _archetype_profile(archetype)
    display_name = _display_name(plugin_name)
    owner = _default_owner(plugin_name)
    payload: dict[str, Any] = {
        "name": plugin_name,
        "version": "0.1.0",
        "description": profile["description"],
        "author": {
            "name": owner,
            "email": DEFAULT_AUTHOR_EMAIL,
            "url": DEFAULT_AUTHOR_URL,
        },
        "homepage": _default_docs_url(plugin_name),
        "repository": _default_repo_url(plugin_name),
        "license": "MIT",
        "keywords": ["plugin", plugin_name, *profile["keywords"]],
        "interface": {
            "displayName": display_name,
            "shortDescription": profile["short_description"],
            "longDescription": profile["long_description"],
            "developerName": owner,
            "category": profile["category"],
            "capabilities": profile["capabilities"],
            "websiteURL": _default_docs_url(plugin_name),
            "privacyPolicyURL": DEFAULT_PRIVACY_URL,
            "termsOfServiceURL": DEFAULT_TERMS_URL,
            "defaultPrompt": profile["default_prompt"],
            "brandColor": profile["brand_color"],
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
    if enabled_surfaces.get("image_assets"):
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


def _asset_brief_template(plugin_name: str) -> str:
    display_name = _display_name(plugin_name)
    return "\n".join(
        [
            f"# {display_name} Assets",
            "",
            "Use this directory for optional plugin visuals and shared package assets.",
            "",
            "## Policy",
            "- Do not add `interface.composerIcon`, `interface.logo`, or `interface.screenshots` to `.codex-plugin/plugin.json` until the referenced files actually exist.",
            "- Use `$imagegen` only when the plugin truly needs PNG assets such as icons, logos, screenshots, or marketplace art.",
            "- If the plugin is infra-only or has no visual surface, keep this directory empty or remove it.",
            "",
            "## Suggested files",
            "- `icon.png` for a square launcher/composer icon",
            "- `logo.png` for a wider plugin logo",
            "- `screenshot1.png` and follow-on screenshots only when a review surface needs them",
            "",
            "## Validation",
            "- Any image path declared in `plugin.json` must resolve to a real file under `./assets/`.",
            "",
        ]
    )


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
            "skills": bool(detected_surfaces.get("skills") or detected_surfaces.get("commands")),
            "hooks": bool(detected_surfaces.get("hooks")),
            "mcpServers": bool(detected_surfaces.get("mcpServers")),
            "apps": bool(detected_surfaces.get("apps")),
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
    plugin_root: Path,
    marketplace_path: Path,
    install_policy: str,
    auth_policy: str,
    policy_products: list[str],
    category: str,
    *,
    strict_openai_layout: bool = False,
) -> dict[str, Any]:
    return {
        "name": plugin_name,
        "source": {
            "source": "local",
            "path": _relative_repo_source_path(
                plugin_root,
                marketplace_path,
                strict_openai_layout=strict_openai_layout,
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
        "name": DEFAULT_MARKETPLACE_NAME,
        "interface": {
            "displayName": DEFAULT_MARKETPLACE_DISPLAY_NAME,
        },
        "plugins": [],
    }


def _display_name_from_identifier(value: str) -> str:
    words = [word for word in re.split(r"[-_\s]+", value.strip()) if word]
    if not words:
        return DEFAULT_MARKETPLACE_DISPLAY_NAME
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


def _marketplace_repo_root(marketplace_path: Path) -> Path:
    lexical_path = marketplace_path.expanduser().absolute()
    resolved_path = marketplace_path.resolve()
    for candidate in (resolved_path.parent, *resolved_path.parents):
        if (candidate / ".git").exists():
            repo_root = candidate
            break
    else:
        raise ValueError(
            f"Unable to locate repo root for marketplace path '{resolved_path}'. "
            "Expected a '.git' sentinel above the marketplace file."
        )

    lexical_repo_root: Path | None = None
    for candidate in (lexical_path.parent, *lexical_path.parents):
        try:
            if candidate.resolve() == repo_root:
                lexical_repo_root = candidate
                break
        except OSError:
            continue

    if lexical_repo_root is not None:
        # Keep lexical path components so ".agents/Plugins/..." remains visible
        # even when ".agents/plugins" is a symlink to "plugins".
        relative_marketplace = lexical_path.relative_to(lexical_repo_root).as_posix()
    else:
        relative_marketplace = resolved_path.relative_to(repo_root).as_posix()
    if relative_marketplace in {
        "Plugins/marketplace.json",
        OPENAI_MARKETPLACE_RELATIVE_PATH,
    }:
        return repo_root

    raise ValueError(
        "Marketplace file must live at 'Plugins/marketplace.json' or "
        "'.agents/Plugins/marketplace.json' relative to the repo root."
    )


def _marketplace_relative_path(marketplace_path: Path, repo_root: Path) -> str:
    lexical_path = marketplace_path.expanduser().absolute()
    for candidate in (lexical_path.parent, *lexical_path.parents):
        try:
            if candidate.resolve() == repo_root:
                return lexical_path.relative_to(candidate).as_posix()
        except OSError:
            continue
    return marketplace_path.resolve().relative_to(repo_root).as_posix()


def _enforce_openai_marketplace_layout(marketplace_path: Path, repo_root: Path) -> None:
    relative_marketplace = _marketplace_relative_path(marketplace_path, repo_root)
    if relative_marketplace == OPENAI_MARKETPLACE_RELATIVE_PATH:
        return
    raise ValueError(
        "OpenAI/Codex marketplace mode requires '.agents/Plugins/marketplace.json'. "
        f"Got '{relative_marketplace}' instead."
    )


def _relative_repo_source_path(
    plugin_root: Path,
    marketplace_path: Path,
    *,
    strict_openai_layout: bool = False,
) -> str:
    repo_root = _marketplace_repo_root(marketplace_path)
    if strict_openai_layout:
        _enforce_openai_marketplace_layout(marketplace_path, repo_root)
    resolved_plugin_root = plugin_root.resolve()
    if not _path_within_root(repo_root, resolved_plugin_root):
        raise ValueError(
            f"Plugin root '{resolved_plugin_root}' must stay within repo root '{repo_root}'."
        )
    relative_path = resolved_plugin_root.relative_to(repo_root).as_posix()
    return f"./{relative_path}"


def _marketplace_source_path_hint(
    source_path: Any,
    *,
    expected_path: str,
    marketplace_path: Path,
) -> str:
    if not isinstance(source_path, str) or not source_path.strip():
        return (
            f"Set source.path to '{expected_path}'. "
            f"Paths are resolved from the repo root that contains '{marketplace_path.name}'."
        )
    if ".." in source_path:
        return (
            f"source.path uses '..' but paths resolve from repo root. "
            f"Use '{expected_path}' instead of '{source_path}'."
        )
    if not source_path.startswith("./"):
        return (
            f"source.path should start with './' and resolve from repo root. "
            f"Use '{expected_path}'."
        )
    return f"Use '{expected_path}' to point at the canonical plugin package path."


def _check_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return [f"{field_name} must be an array of strings."]
    return []


def _normalize_policy_products(raw_products: Any) -> tuple[list[str], list[str]]:
    if raw_products is None:
        return [], []
    if not isinstance(raw_products, list):
        return [], ["must be an array of product names"]

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


def create_json_file(path: Path, payload: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        return
    write_json(path, payload, force=True)


def update_marketplace_json(
    marketplace_path: Path,
    plugin_name: str,
    plugin_root: Path,
    install_policy: str,
    auth_policy: str,
    policy_products: list[str],
    category: str | None,
    force: bool,
    *,
    strict_openai_layout: bool = False,
) -> None:
    if strict_openai_layout:
        repo_root = _marketplace_repo_root(marketplace_path)
        _enforce_openai_marketplace_layout(marketplace_path, repo_root)

    if marketplace_path.exists():
        payload = load_json(marketplace_path)
    else:
        payload = build_default_marketplace()
    _ensure_marketplace_interface(payload)

    plugins = payload.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError(f"{marketplace_path} field 'plugins' must be an array.")

    effective_category = category or _suggest_marketplace_category(plugin_name)
    new_entry = build_marketplace_entry(
        plugin_name,
        plugin_root,
        marketplace_path,
        install_policy,
        auth_policy,
        policy_products,
        effective_category,
        strict_openai_layout=strict_openai_layout,
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


def _load_plugin_payload(plugin_root: Path) -> dict[str, Any] | None:
    manifest_path = _plugin_manifest_path(plugin_root)
    if not manifest_path.is_file():
        return None
    return load_json(manifest_path)


def _plugin_manifest_path(plugin_root: Path) -> Path:
    return plugin_root / ".codex-plugin" / "plugin.json"


def _is_plugin_like_dir(path: Path) -> bool:
    return path.is_dir() and not path.name.startswith(".") and (path / ".codex-plugin").exists()


def _is_local_plugin_package_dir(path: Path) -> bool:
    return _is_plugin_like_dir(path) and _plugin_manifest_path(path).is_file()


def _collect_malformed_local_plugin_dirs(plugin_parent: Path) -> list[Path]:
    if not plugin_parent.exists() or not plugin_parent.is_dir():
        return []
    malformed: list[Path] = []
    for child in sorted(plugin_parent.iterdir()):
        if not _is_plugin_like_dir(child):
            continue
        if _is_local_plugin_package_dir(child):
            continue
        malformed.append(child)
    return malformed


def _normalize_marketplace_entry(
    entry: dict[str, Any],
    marketplace_path: Path,
    plugins_path: Path,
    *,
    strict_openai_layout: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    notes: list[str] = []
    normalized = dict(entry)
    plugin_name = normalized.get("name")
    if not isinstance(plugin_name, str) or not plugin_name.strip():
        raise ValueError("marketplace plugin entries must include a non-empty 'name'.")

    plugin_name = normalize_plugin_name(plugin_name)
    normalized["name"] = plugin_name
    plugin_root = plugins_path / plugin_name
    plugin_payload = _load_plugin_payload(plugin_root)
    expected_path = _relative_repo_source_path(
        plugin_root,
        marketplace_path,
        strict_openai_layout=strict_openai_layout,
    )

    source = normalized.get("source")
    if not isinstance(source, dict):
        source = {}
    if source.get("source") != "local":
        notes.append(f"{plugin_name}: normalized source.source to 'local'")
    if source.get("path") != expected_path:
        notes.append(f"{plugin_name}: normalized source.path to '{expected_path}'")
    source["source"] = "local"
    source["path"] = expected_path
    normalized["source"] = source

    policy = normalized.get("policy")
    if not isinstance(policy, dict):
        policy = {}
    install_policy = policy.get("installation")
    if install_policy not in VALID_INSTALL_POLICIES:
        legacy_install = normalized.get("installPolicy")
        if legacy_install in VALID_INSTALL_POLICIES:
            install_policy = legacy_install
            notes.append(f"{plugin_name}: migrated legacy installPolicy into policy.installation")
        else:
            install_policy = DEFAULT_INSTALL_POLICY
            notes.append(f"{plugin_name}: filled missing policy.installation with '{DEFAULT_INSTALL_POLICY}'")
    auth_policy = policy.get("authentication")
    if auth_policy not in VALID_AUTH_POLICIES:
        legacy_auth = normalized.get("authPolicy")
        if legacy_auth in VALID_AUTH_POLICIES:
            auth_policy = legacy_auth
            notes.append(f"{plugin_name}: migrated legacy authPolicy into policy.authentication")
        else:
            auth_policy = DEFAULT_AUTH_POLICY
            notes.append(f"{plugin_name}: filled missing policy.authentication with '{DEFAULT_AUTH_POLICY}'")
    policy["installation"] = install_policy
    policy["authentication"] = auth_policy
    if "products" in normalized and "products" not in policy:
        policy["products"] = normalized["products"]
    normalized_products, invalid_products = _normalize_policy_products(policy.get("products"))
    if invalid_products:
        notes.append(
            f"{plugin_name}: removed invalid policy.products values {sorted(set(invalid_products))}; "
            f"allowed values are {sorted(VALID_POLICY_PRODUCTS)}"
        )
    if not normalized_products:
        normalized_products = list(DEFAULT_POLICY_PRODUCTS)
        notes.append(
            f"{plugin_name}: filled missing policy.products with {normalized_products}"
        )
    policy["products"] = normalized_products
    normalized["policy"] = policy
    normalized.pop("installPolicy", None)
    normalized.pop("authPolicy", None)
    normalized.pop("products", None)

    category = normalized.get("category")
    if not isinstance(category, str) or not category.strip():
        suggested_category = _suggest_marketplace_category(
            plugin_name,
            payload=plugin_payload,
            plugin_root=plugin_root if plugin_root.exists() else None,
        )
        normalized["category"] = suggested_category
        notes.append(f"{plugin_name}: filled missing category with '{suggested_category}'")

    return normalized, notes


def _audit_marketplace(
    marketplace_path: Path,
    plugins_path: Path,
    *,
    strict_openai_layout: bool = False,
) -> dict[str, Any]:
    if strict_openai_layout:
        repo_root = _marketplace_repo_root(marketplace_path)
        _enforce_openai_marketplace_layout(marketplace_path, repo_root)

    payload = load_json(marketplace_path)
    _ensure_marketplace_interface(payload)
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError(f"{marketplace_path} field 'plugins' must be an array.")

    findings: list[dict[str, str]] = []
    seen_names: set[str] = set()
    entry_names: list[str] = []
    for entry in plugins:
        if not isinstance(entry, dict):
            findings.append({"severity": "error", "message": "marketplace entry must be an object."})
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            findings.append({"severity": "error", "message": "marketplace entry missing non-empty name."})
            continue
        entry_names.append(name)
        if name in seen_names:
            findings.append({"severity": "error", "message": f"duplicate marketplace entry for '{name}'."})
            continue
        seen_names.add(name)
        plugin_root = plugins_path / name
        source_plugin_root = plugin_root
        source = entry.get("source")
        if isinstance(source, dict):
            source_path = source.get("path")
            if _is_relative_plugin_path(source_path):
                source_plugin_root = (_marketplace_repo_root(marketplace_path) / source_path[2:]).resolve()
        findings.extend(
            {"severity": "error", "message": message}
            for message in _check_marketplace_entry(
                payload,
                name,
                plugin_root,
                marketplace_path,
                strict_openai_layout=strict_openai_layout,
            )
        )
        if not source_plugin_root.exists():
            findings.append(
                {
                    "severity": "warning",
                    "message": f"marketplace entry '{name}' points to missing plugin directory '{source_plugin_root}'.",
                }
            )
            continue
        plugin_payload = _load_plugin_payload(source_plugin_root)
        if plugin_payload is None:
            findings.append(
                {
                    "severity": "warning",
                    "message": f"plugin directory '{source_plugin_root}' is missing .codex-plugin/plugin.json.",
                }
            )
            continue
        suggested_category = _suggest_marketplace_category(
            name,
            payload=plugin_payload,
            plugin_root=source_plugin_root,
        )
        entry_category = entry.get("category")
        if not isinstance(entry_category, str) or not entry_category.strip():
            findings.append(
                {
                    "severity": "warning",
                    "message": f"marketplace entry '{name}' is missing category; suggested '{suggested_category}'.",
                }
            )
        elif entry_category != suggested_category:
            findings.append(
                {
                    "severity": "warning",
                    "message": f"marketplace entry '{name}' category '{entry_category}' differs from suggested '{suggested_category}'.",
                }
            )

    malformed_local_plugins = _collect_malformed_local_plugin_dirs(plugins_path)
    for malformed_dir in malformed_local_plugins:
        findings.append(
            {
                "severity": "warning",
                "message": (
                    f"plugin-like directory '{malformed_dir}' is missing a regular "
                    ".codex-plugin/plugin.json file."
                ),
            }
        )

    local_plugin_names = sorted(
        child.name
        for child in plugins_path.iterdir()
        if _is_local_plugin_package_dir(child)
    ) if plugins_path.exists() else []
    for plugin_name in local_plugin_names:
        if plugin_name not in seen_names:
            findings.append(
                {
                    "severity": "warning",
                    "message": f"local plugin '{plugin_name}' is missing a marketplace entry.",
                }
            )

    if entry_names != sorted(entry_names):
        findings.append(
            {
                "severity": "warning",
                "message": "marketplace plugin entries are not sorted by name.",
            }
        )

    return {
        "marketplace_path": str(marketplace_path),
        "plugins_path": str(plugins_path),
        "plugin_count": len(entry_names),
        "local_plugin_count": len(local_plugin_names),
        "findings": findings,
    }


def _normalize_marketplace_payload(
    marketplace_path: Path,
    plugins_path: Path,
    *,
    strict_openai_layout: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    if strict_openai_layout:
        repo_root = _marketplace_repo_root(marketplace_path)
        _enforce_openai_marketplace_layout(marketplace_path, repo_root)

    payload = load_json(marketplace_path) if marketplace_path.exists() else build_default_marketplace()
    _ensure_marketplace_interface(payload)
    plugins = payload.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError(f"{marketplace_path} field 'plugins' must be an array.")

    normalized_plugins: list[dict[str, Any]] = []
    notes: list[str] = []
    seen_names: set[str] = set()
    for entry in plugins:
        if not isinstance(entry, dict):
            raise ValueError("marketplace entries must be JSON objects.")
        normalized_entry, entry_notes = _normalize_marketplace_entry(
            entry,
            marketplace_path,
            plugins_path,
            strict_openai_layout=strict_openai_layout,
        )
        plugin_name = normalized_entry["name"]
        if plugin_name in seen_names:
            raise ValueError(f"duplicate marketplace entry for '{plugin_name}'. Resolve duplicates before normalization.")
        seen_names.add(plugin_name)
        normalized_plugins.append(normalized_entry)
        notes.extend(entry_notes)

    normalized_plugins.sort(key=lambda item: str(item["name"]))
    payload["plugins"] = normalized_plugins
    return payload, notes


def _readme_template(plugin_name: str) -> str:
    return _render_readme_template(
        plugin_name,
        {
            "skills": True,
            "hooks": False,
            "agents": False,
            "mcp": False,
            "apps": False,
            "assets": False,
        },
    )


def _license_template() -> str:
    current_year = str(date.today().year)
    return (
        _load_docs_asset("LICENSE_TEMPLATE.txt")
        .replace("{year}", current_year)
        .replace("{owner}", DEFAULT_OWNER)
    )


def _render_readme_template(plugin_name: str, enabled_surfaces: dict[str, bool]) -> str:
    display_name = _display_name(plugin_name)
    surface_lines = "\n".join(f"- `{surface}`" for surface in _surface_summary(enabled_surfaces))
    template = _load_docs_asset("README_TEMPLATE.md")
    return (
        template
        .replace(
            "# <Project name> helps <audience> <verb> <outcome>",
            f"# {display_name} helps teams ship reusable Codex workflows",
        )
        .replace(
            "One sentence: what this repo is for and who it serves.",
            f"This plugin package collects the manifest, plugin-owned skills, and optional integration surfaces for `{plugin_name}`.",
        )
        .replace("Last updated: YYYY-MM-DD", f"Last updated: {date.today().isoformat()}")
        .replace("Owner: <name/team>", f"Owner: {DEFAULT_OWNER}")
        .replace("Review cadence: <e.g., quarterly>", "Review cadence: quarterly")
        .replace("- Audience tier: <beginner/intermediate/expert>", "- Audience tier: intermediate")
        .replace(
            "- Scope: <what this doc covers>",
            "- Scope: package layout, scaffolded surfaces, validation, and maintenance expectations",
        )
        .replace(
            "- Non-scope: <what this doc does not cover>",
            "- Non-scope: implementing external MCP servers, app UIs, or non-plugin product features",
        )
        .replace("- Required approvals: <names/roles>", "- Required approvals: plugin owner")
        .replace("- Assumptions: <what must be true>", "- Assumptions: this package lives inside the Agent-Skills repo and follows the Codex plugin contract")
        .replace("- Risks / blast radius: <what can go wrong>", "- Risks / blast radius: stale metadata or duplicate plugin intent can make the package misleading")
        .replace("- Rollback / recovery: <how to recover>", "- Rollback / recovery: rerun scaffold with corrected inputs or remove the package before marketplace registration")
        .replace("- Required: <runtime/tooling versions>, <accounts>, <permissions>", "- Required: Python 3, repo access, and validator dependencies used by this repo")
        .replace("- Optional: <editor plugins>, <CLI helpers>", "- Optional: `jq`, `yq`, and Codex runtime tooling for deeper validation")
        .replace(
            "# commands the repo actually supports",
            f"uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py scaffold {plugin_name} --path plugins --with-skills --with-marketplace",
        )
        .replace(
            "### 2) Run it\n```sh\n```\n",
            "### 2) Run it\n```sh\n"
            f"uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/{plugin_name} --require-marketplace --marketplace-path .agents/Plugins/marketplace.json\n"
            "```\n",
        )
        .replace("- <what success looks like>", "- The plugin manifest validates and the package surfaces exist at the expected relative paths")
        .replace("### Do <task> to achieve <result>", "### Add or refine plugin-owned skills")
        .replace("- What you get:", "- What you get: a `skills/<skill>/` bundle generated through `skill-builder`")
        .replace("- Steps:\n```sh\n```\n- Verify:", "- Steps:\n```sh\n"
            f"uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py scaffold {plugin_name} --path plugins --with-skills --force\n"
            "```\n- Verify: confirm `skills/<skill>/SKILL.md`, `Infrastructure/references/`, `Infrastructure/scripts/`, `assets/`, and `agents/openai.yaml` exist\n")
        .replace("### Configure <thing> so that <result>", "### Validate package integrity before publishing")
        .replace("- Options table (if applicable):", "- Package surfaces:\n" + surface_lines + "\n")
        .replace("### Symptom: <what the reader sees>", "### Symptom: validation reports missing plugin-owned surfaces")
        .replace("Cause:\nFix:\n```sh\n```\n", "Cause: the scaffold was partial or a helper-generated surface was removed.\nFix:\n```sh\n"
            f"uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py scaffold {plugin_name} --path plugins --with-skills --with-agents --force\n"
            "```\n")
        .replace("- [ ] <criterion 1>", "- [ ] manifest exists at `.codex-plugin/plugin.json`")
        .replace("- [ ] <criterion 2>", "- [ ] plugin-owned skills and agents were scaffolded through shared builders when requested")
        .replace("- [ ] <criterion 3>", "- [ ] package validation passes before marketplace publication")
        .replace("- Lint outputs (Vale/markdownlint/link check):", "- Lint outputs (Vale/markdownlint/link check): not run by default for plugin scaffolds")
        .replace("- Brand check output:", "- Brand check output: not applicable unless assets are added")
        .replace("- Readability output (if available):", "- Readability output (if available): optional")
        .replace("- Checklist snapshot:", "- Checklist snapshot: confirm scaffold helpers ran successfully")
        .replace("- Key links:", "- Key links:\n  - `Infrastructure/references/operational-spec.md`\n  - `Infrastructure/references/package-guide.md`\n  - `Infrastructure/references/deconflict-report.md`")
        .replace("- Project layout:", f"- Project layout:\n{surface_lines}")
        .replace("- Commands:", "- Commands:\n  - scaffold via `plugin_builder.py scaffold`\n  - validate via `plugin_builder.py validate`\n  - inspect source via `plugin_builder.py inspect-source`")
        .replace("- Constraints / limits:", "- Constraints / limits:\n  - `prompts/`, `commands/`, and `slash-commands/` are migration inputs, not runtime surfaces")
        .replace(
            "\n---\n\n<!-- ASCII fallback (use if images are not supported):\nbrAInwav\nfrom demo to duty\n-->\n\n<img\n  src=\"./brand/brand-mark.webp\"\n  srcset=\"./brand/brand-mark.webp 1x, ./brand/brand-mark@2x.webp 2x\"\n  alt=\"brAInwav\"\n  height=\"28\"\n  align=\"left\"\n/>\n\n<br clear=\"left\" />\n\n**brAInwav**\n_from demo to duty_\n",
            "",
        )
    )


def _package_guide_template(plugin_name: str, enabled_surfaces: dict[str, bool]) -> str:
    display_name = _display_name(plugin_name)
    surface_lines = "\n".join(f"- `{surface}`" for surface in _surface_summary(enabled_surfaces))
    template = _load_docs_asset("DOC_TEMPLATE.md")
    return (
        template
        .replace(
            "# <Doc title as an informative sentence>",
            f"# {display_name} package guide for scaffolded plugin surfaces",
        )
        .replace(
            "One sentence: what this doc helps the reader do, and who it is for.",
            f"This guide explains what `plugin-builder` generated for `{plugin_name}` and how to extend it safely.",
        )
        .replace("Last updated: YYYY-MM-DD", f"Last updated: {date.today().isoformat()}")
        .replace("Owner: <name/team>", f"Owner: {DEFAULT_OWNER}")
        .replace("Review cadence: <e.g., quarterly>", "Review cadence: quarterly")
        .replace("- Audience tier: <beginner/intermediate/expert>", "- Audience tier: intermediate")
        .replace("- Scope: <what this doc covers>", "- Scope: package layout, helper ownership, and validation expectations")
        .replace("- Non-scope: <what this doc does not cover>", "- Non-scope: implementing the business logic behind the package")
        .replace("- Required approvals: <names/roles>", "- Required approvals: plugin owner")
        .replace("- Assumptions: <what must be true>", "- Assumptions: the plugin stays inside a repo that has access to the shared scaffold helpers")
        .replace("- Risks / blast radius: <what can go wrong>", "- Risks / blast radius: hand-editing generated files can drift from the helper contracts")
        .replace("- Rollback / recovery: <how to recover>", "- Rollback / recovery: regenerate missing surfaces or compare against the helper-owned templates")
        .replace("- Required: <tool/version>, <access>, <accounts>", "- Required: Python 3 plus the helper scripts committed in this repo")
        .replace("- Optional: <tooling>", "- Optional: `jq`, `yq`, OpenAI docs access for contract verification")
        .replace("# commands the repo actually supports", "ls -R .")
        .replace(
            "### 2) Run it\n```sh\n```\n",
            "### 2) Run it\n```sh\n"
            f"uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/{plugin_name}\n"
            "```\n",
        )
        .replace("- <what success looks like>", "- Every declared surface exists and helper-owned folders are in the expected locations")
        .replace("### Do <task> to achieve <result>", "### Understand which helper owns each package surface")
        .replace("- What you get:", "- What you get: a clear map of which builder created which part of the package")
        .replace("- Steps:\n```sh\n```\n- Verify:", "- Steps:\n```text\n"
            "skill-builder -> skills/<skill>/SKILL.md, Infrastructure/references/, Infrastructure/scripts/, assets/, agents/openai.yaml\n"
            "codex-agent-builder -> agents/<agent>.toml\n"
            "docs-expert assets -> README.md, LICENSE, Infrastructure/references/package-guide.md\n"
            "plugin-builder -> .codex-plugin/plugin.json, hooks.json, .mcp.json, .app.json, operational/deconflict docs\n"
            "```\n- Verify: compare generated files against the package tree below\n")
        .replace("### Configure <thing> so that <result>", "### Review the package tree before extending it")
        .replace("- Options table (if applicable):", "- Package tree:\n" + surface_lines + "\n")
        .replace("### Symptom: <what the reader sees>", "### Symptom: a plugin surface exists but does not match the owning helper contract")
        .replace("Cause:\nFix:\n```sh\n```\n", "Cause: the surface was hand-edited or generated with the wrong helper.\nFix:\n```sh\n"
            f"uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py scaffold {plugin_name} --path plugins --with-skills --with-agents --force\n"
            "```\n")
        .replace("- [ ] <criterion 1>", "- [ ] helper ownership of each surface is documented")
        .replace("- [ ] <criterion 2>", "- [ ] package layout matches the manifest and generated docs")
        .replace("- [ ] <criterion 3>", "- [ ] validation command is recorded for future changes")
        .replace("- Lint outputs (Vale/markdownlint/link check):", "- Lint outputs (Vale/markdownlint/link check): optional")
        .replace("- Brand check output (if applicable):", "- Brand check output (if applicable): only needed if package assets are customized")
        .replace("- Readability output (if available):", "- Readability output (if available): optional")
        .replace("- Checklist snapshot:", "- Checklist snapshot: compare manifest paths to actual package contents")
        .replace("- Key terms:", "- Key terms:\n  - package root\n  - plugin-owned skill\n  - plugin-owned agent\n  - runtime surface")
        .replace("- Links to related docs:", "- Links to related docs:\n  - `README.md`\n  - `Infrastructure/references/operational-spec.md`\n  - `Infrastructure/references/plugin-contract.md`")
        .replace("- Constraints / limits:", "- Constraints / limits:\n  - convert legacy prompt and command surfaces into `skills/`\n  - keep plugin-root shared docs separate from per-skill docs")
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
            source_summary_lines.append("- deprecated command shims were detected; command and prompt surfaces should be folded into skills unless intentionally archived outside the runtime package.")
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
            f"  owner: \"{DEFAULT_OWNER}\"",
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
            "- plugin-created or plugin-converted packages must keep `Infrastructure/references/operational-spec.md` present.",
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
    if not isinstance(value, str) or not value.startswith("./"):
        return False
    relative = value[2:]
    if not relative:
        return False
    path_obj = Path(relative)
    for component in path_obj.parts:
        if component in ("", ".", ".."):
            return False
    return True


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


def _scaffold_plugin_skill(skill_root: Path, skill_name: str, force: bool) -> str:
    skill_dir = skill_root / skill_name
    if skill_dir.exists():
        return f"skill-builder: kept existing plugin skill at {skill_dir}"

    command = [
        *_uv_python_command(),
        str(SKILL_BUILDER_INIT),
        skill_name,
        "--path",
        str(skill_root),
        "--target",
        "codex",
        "--resources",
        "scripts,references,assets",
    ]
    output = _run_helper(command, f"skill-builder scaffold for {skill_name}")
    if force and output:
        return f"skill-builder: created {skill_dir}\n{output}"
    return f"skill-builder: created {skill_dir}"


def _plugin_agent_instructions(plugin_name: str) -> str:
    return "\n".join(
        [
            f"You are the {plugin_name} plugin agent.",
            "Operate within the plugin package, prefer plugin-owned skills before ad hoc workflows, and keep edits inside the plugin root unless the user explicitly asks for broader repository work.",
            "If the request changes package docs, update README.md and Infrastructure/references/ alongside the implementation.",
            "If the request changes runtime surfaces, re-run plugin validation before reporting completion.",
        ]
    )


def _scaffold_plugin_agent(plugin_root: Path, agent_name: str, force: bool) -> str:
    output_path = plugin_root / "agents" / f"{agent_name}.toml"
    if output_path.exists():
        return f"codex-agent-builder: kept existing plugin agent at {output_path}"

    command = [
        "bash",
        str(CODEX_AGENT_WRITER),
        "--output",
        str(output_path),
        "--role-name",
        agent_name,
        "--model",
        "gpt-5.4-mini",
        "--reasoning",
        "medium",
        "--developer-instructions",
        _plugin_agent_instructions(agent_name),
        "--sandbox-mode",
        "workspace-write",
        "--network-access",
        "false",
        "--writable-roots",
        str(plugin_root),
    ]
    output = _run_helper(command, f"codex-agent-builder scaffold for {agent_name}")
    if force and output:
        return f"codex-agent-builder: created {output_path}\n{output}"
    return f"codex-agent-builder: created {output_path}"


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
        if not _is_local_plugin_package_dir(child):
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
    malformed_plugin_dirs = [str(path) for path in _collect_malformed_local_plugin_dirs(plugin_parent)]
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
        "malformed_plugin_dirs": malformed_plugin_dirs,
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

    malformed = overlap_report.get("malformed_plugin_dirs") or []
    lines.append("## Malformed local plugin directories")
    if not malformed:
        lines.append("- none")
    else:
        for path in malformed:
            lines.append(f"- `{path}` (missing regular `.codex-plugin/plugin.json`)")
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
        notes.append("Deprecated command shims detected; inspect command contents before converting them into plugin-owned skills.")
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


def _normalize_allowlist(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip().lower() for value in values if isinstance(value, str) and value.strip()}


def _normalize_domain_allowlist(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        candidate = value.strip().lower().lstrip("@")
        if candidate:
            normalized.add(candidate)
    return normalized


def _check_provenance_manifest(
    provenance_path: Path,
    plugin_root: Path,
    *,
    require_signed_provenance: bool,
    allowed_signer_emails: set[str],
    allowed_signer_domains: set[str],
    allowed_signer_logins: set[str],
) -> list[str]:
    if not provenance_path.exists():
        return [f"Provenance manifest not found: {provenance_path}"]

    try:
        payload = load_json(provenance_path)
    except Exception as exc:  # noqa: BLE001
        return [f"Provenance manifest is invalid JSON: {provenance_path}: {exc}"]

    if not isinstance(payload, dict):
        return [f"Provenance manifest must contain a JSON object: {provenance_path}"]

    failures: list[str] = []
    plugin_name = payload.get("plugin_name")
    if isinstance(plugin_name, str) and plugin_name.strip() and plugin_name.strip() != plugin_root.name:
        failures.append(
            f"Provenance plugin_name '{plugin_name.strip()}' does not match plugin directory '{plugin_root.name}'."
        )
    elif plugin_name is not None and not isinstance(plugin_name, str):
        failures.append("Provenance field 'plugin_name' must be a string when present.")

    source = payload.get("source")
    if not isinstance(source, dict):
        failures.append("Provenance field 'source' must be an object.")
    else:
        resolved_commit = source.get("resolved_commit")
        if not isinstance(resolved_commit, str) or not PINNED_COMMIT_RE.fullmatch(resolved_commit.strip()):
            failures.append(
                "Provenance source.resolved_commit must be a 40-character commit SHA."
            )
        for key in ("owner", "repo", "path"):
            value = source.get(key)
            if value is not None and not isinstance(value, str):
                failures.append(f"Provenance source.{key} must be a string when present.")

    verified_state: bool | None = None
    commit_verification = payload.get("commit_verification")
    if not isinstance(commit_verification, dict):
        failures.append("Provenance field 'commit_verification' must be an object.")
    else:
        verified = commit_verification.get("verified")
        if not isinstance(verified, bool):
            failures.append("Provenance commit_verification.verified must be a boolean.")
            verified = False
        verified_state = verified
        reason = commit_verification.get("reason")
        reason_text = reason.strip().lower() if isinstance(reason, str) and reason.strip() else "unknown"
        if reason is not None and not isinstance(reason, str):
            failures.append("Provenance commit_verification.reason must be a string when present.")
        if require_signed_provenance and verified is not True:
            failures.append(
                "Provenance manifest indicates unsigned or unverified source commit "
                f"(reason='{reason_text}')."
            )
        if require_signed_provenance and verified is True and reason_text != "valid":
            failures.append(
                "Provenance commit verification reason must be 'valid' when signed provenance is required. "
                f"Observed reason='{reason_text}'."
            )

    signer_identity = payload.get("signer_identity")
    allowlist_enabled = bool(allowed_signer_emails or allowed_signer_domains or allowed_signer_logins)
    if allowlist_enabled:
        if verified_state is not True:
            failures.append(
                "Signer allowlist checks require provenance commit_verification.verified=true."
            )
        reason = None
        if isinstance(commit_verification, dict):
            raw_reason = commit_verification.get("reason")
            if isinstance(raw_reason, str):
                stripped = raw_reason.strip().lower()
                reason = stripped if stripped else "unknown"
            elif raw_reason is None:
                reason = "unknown"
        if reason != "valid":
            failures.append(
                "Signer allowlist checks require provenance commit_verification.reason='valid'. "
                f"Observed reason='{reason or 'unknown'}'."
            )
        observed_emails: set[str] = set()
        observed_attested_logins: set[str] = set()
        metadata_emails: set[str] = set()
        metadata_logins: set[str] = set()
        if isinstance(signer_identity, dict):
            raw_emails = signer_identity.get("attested_emails")
            if raw_emails is None:
                raw_emails = signer_identity.get("emails")
            if isinstance(raw_emails, list):
                observed_emails = {
                    value.strip().lower()
                    for value in raw_emails
                    if isinstance(value, str) and value.strip()
                }
            raw_logins = signer_identity.get("attested_logins")
            if raw_logins is None:
                raw_logins = signer_identity.get("logins")
            if isinstance(raw_logins, list):
                observed_attested_logins = {
                    value.strip().lower()
                    for value in raw_logins
                    if isinstance(value, str) and value.strip()
                }
            raw_metadata_emails = signer_identity.get("metadata_emails")
            if isinstance(raw_metadata_emails, list):
                metadata_emails = {
                    value.strip().lower()
                    for value in raw_metadata_emails
                    if isinstance(value, str) and value.strip()
                }
            raw_metadata_logins = signer_identity.get("metadata_logins")
            if isinstance(raw_metadata_logins, list):
                metadata_logins = {
                    value.strip().lower()
                    for value in raw_metadata_logins
                    if isinstance(value, str) and value.strip()
                }
        observed_logins = observed_attested_logins if observed_attested_logins else metadata_logins
        login_identity_source = "attested" if observed_attested_logins else ("metadata" if metadata_logins else "none")
        observed_domains = {
            value.rsplit("@", 1)[1]
            for value in observed_emails
            if "@" in value and value.rsplit("@", 1)[1]
        }

        matched_email = (not allowed_signer_emails) or bool(observed_emails & allowed_signer_emails)
        matched_domain = (not allowed_signer_domains) or bool(observed_domains & allowed_signer_domains)
        matched_login = (not allowed_signer_logins) or bool(observed_logins & allowed_signer_logins)
        if not (matched_email and matched_domain and matched_login):
            failures.append(
                "Provenance signer identity did not match allowlist policy. "
                f"allowed_emails={sorted(allowed_signer_emails)} "
                f"allowed_domains={sorted(allowed_signer_domains)} "
                f"allowed_logins={sorted(allowed_signer_logins)} "
                f"observed_attested_emails={sorted(observed_emails)} "
                f"observed_domains={sorted(observed_domains)} "
                f"observed_signer_logins={sorted(observed_logins)} "
                f"observed_login_source={login_identity_source} "
                f"observed_attested_logins={sorted(observed_attested_logins)} "
                f"metadata_emails={sorted(metadata_emails)} "
                f"metadata_logins={sorted(metadata_logins)}."
            )

    return failures


def _check_plugin_skill_surface(plugin_root: Path, payload: dict[str, Any]) -> list[str]:
    skills_value = payload.get("skills")
    if not _is_relative_plugin_path(skills_value):
        return []

    skills_root = (plugin_root / skills_value[2:]).resolve()
    if not skills_root.exists() or not skills_root.is_dir():
        return []

    skill_packages = sorted(skills_root.glob("*/SKILL.md"))
    if skill_packages:
        return []
    return [
        "plugin.json field 'skills' points to a directory without any plugin-owned skill packages. "
        "Use skill-builder to create at least one `skills/<name>/SKILL.md` bundle."
    ]


def _check_duplicate_skill_ownership(plugin_root: Path, payload: dict[str, Any]) -> list[str]:
    skills_value = payload.get("skills")
    if not _is_relative_plugin_path(skills_value):
        return []

    skills_root = (plugin_root / skills_value[2:]).resolve()
    if not skills_root.exists() or not skills_root.is_dir():
        return []

    plugin_skill_names = {path.parent.name for path in skills_root.glob("*/SKILL.md")}
    if not plugin_skill_names:
        return []

    conflicts: dict[str, list[str]] = {}
    for skill_name in sorted(plugin_skill_names):
        for root_name in CANONICAL_STANDALONE_SKILL_ROOTS:
            root = REPO_ROOT / root_name
            if not root.exists():
                continue
            for match in sorted(root.rglob(f"{skill_name}/SKILL.md")):
                # Compatibility aliases are expected as symlinks back to plugin-owned canon.
                if match.parent.is_symlink():
                    continue
                rel = str(match.parent.relative_to(REPO_ROOT))
                conflicts.setdefault(skill_name, []).append(rel)

    if not conflicts:
        return []

    rendered: list[str] = []
    for skill_name, paths in sorted(conflicts.items()):
        unique_paths = sorted(set(paths))
        rendered.append(f"{skill_name}: {', '.join(unique_paths)}")

    return [
        "Plugin-owned skill names must be canonical in one lane only. "
        f"Standalone duplicates detected ({'; '.join(rendered)}). "
        "Move the standalone skill under `Plugins/<plugin>/skills/<name>` or rename it."
    ]


def _check_plugin_agent_surface(plugin_root: Path) -> list[str]:
    agents_root = plugin_root / "agents"
    if not agents_root.exists() or not agents_root.is_dir():
        return []

    role_configs = sorted(agents_root.glob("*.toml"))
    if role_configs:
        return []
    return [
        "Plugin package includes agents/ but no `.toml` role configs. "
        "Use codex-agent-builder to scaffold plugin-owned agents."
    ]


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
                                require_exists=True,
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
                            require_exists=True,
                        )
                    )

    for legacy_key in ("commands", "slashCommands", "slash_commands"):
        if legacy_key in payload:
            failures.append(
                f"plugin.json uses Claude-oriented field '{legacy_key}'. "
                "Use plugin-owned `skills/` and optionally `interface.defaultPrompt` instead."
            )

    declared_mcp = "mcpServers" in payload
    declared_apps = "apps" in payload
    if (plugin_root / ".mcp.json").exists() and not declared_mcp:
        failures.append(
            "Plugin package includes `.mcp.json` but `plugin.json` does not declare `mcpServers`. "
            "Only ship `.mcp.json` for real MCP wiring the manifest exposes."
        )
    if (plugin_root / ".app.json").exists() and not declared_apps:
        failures.append(
            "Plugin package includes `.app.json` but `plugin.json` does not declare `apps`. "
            "Only ship `.app.json` for real app integrations the manifest exposes."
        )

    failures.extend(_check_plugin_skill_surface(plugin_root, payload))
    failures.extend(_check_duplicate_skill_ownership(plugin_root, payload))
    failures.extend(_check_plugin_agent_surface(plugin_root))

    return failures


def _check_marketplace_entry(
    marketplace_payload: dict[str, Any],
    plugin_name: str,
    plugin_root: Path,
    marketplace_path: Path,
    *,
    strict_openai_layout: bool = False,
) -> list[str]:
    failures: list[str] = []
    expected_path = _relative_repo_source_path(
        plugin_root,
        marketplace_path,
        strict_openai_layout=strict_openai_layout,
    )
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
        source_path = source.get("path")
        source_path_hint = _marketplace_source_path_hint(
            source_path,
            expected_path=expected_path,
            marketplace_path=marketplace_path,
        )
        if not _is_relative_plugin_path(source_path):
            failures.append(
                f"marketplace plugin '{plugin_name}' source.path must be a './'-prefixed path relative to the repo root. "
                f"{source_path_hint}"
            )
        else:
            repo_root = _marketplace_repo_root(marketplace_path)
            resolved_source_root = (repo_root / source_path[2:]).resolve()
            if not _path_within_root(repo_root, resolved_source_root):
                failures.append(
                    f"marketplace plugin '{plugin_name}' source.path must stay within repo root '{repo_root}'. "
                    f"{source_path_hint}"
                )
            elif resolved_source_root != plugin_root.resolve():
                failures.append(
                    f"marketplace plugin '{plugin_name}' source.path resolves to '{resolved_source_root}', expected '{expected_path}'. "
                    f"{source_path_hint}"
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

    policy_products = None
    if isinstance(policy, dict):
        policy_products = policy.get("products")
    if policy_products is None:
        policy_products = plugin_entry.get("products")
    normalized_products, invalid_products = _normalize_policy_products(policy_products)
    if not normalized_products:
        failures.append(
            f"marketplace plugin '{plugin_name}' policy.products must include at least one product from "
            f"{sorted(VALID_POLICY_PRODUCTS)}."
        )
    if invalid_products:
        failures.append(
            f"marketplace plugin '{plugin_name}' policy.products contains invalid values {sorted(set(invalid_products))}; "
            f"allowed values are {sorted(VALID_POLICY_PRODUCTS)}."
        )

    category = plugin_entry.get("category")
    if not isinstance(category, str) or not category.strip():
        failures.append(
            f"marketplace plugin '{plugin_name}' category must be a non-empty string."
        )

    return failures


def _audit_plugin_compatibility(
    plugin_root: Path,
    marketplace_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not plugin_json_path.exists():
        raise ValueError(f"Missing plugin manifest: {plugin_json_path}")

    payload = load_json(plugin_json_path)
    inferred_archetype = _infer_plugin_archetype(
        plugin_root.name,
        payload=payload,
        plugin_root=plugin_root,
    )
    suggested_category = _suggest_marketplace_category(
        plugin_root.name,
        archetype=inferred_archetype,
        payload=payload,
        plugin_root=plugin_root,
    )

    warnings: list[str] = []
    recommendations: list[str] = []
    curated_files = [
        "README.md",
        "LICENSE",
        "Infrastructure/references/operational-spec.md",
        "Infrastructure/references/package-guide.md",
        "Infrastructure/references/deconflict-report.md",
    ]
    for relative_path in curated_files:
        if not (plugin_root / relative_path).exists():
            warnings.append(
                f"Missing curated package file '{relative_path}'. This is optional at runtime but common in hardened repo packages."
            )

    for field_name in ("version", "author", "homepage", "repository", "license", "keywords"):
        if field_name not in payload:
            warnings.append(
                f"Manifest is missing curated metadata field '{field_name}'."
            )

    interface = payload.get("interface")
    if not isinstance(interface, dict):
        warnings.append("Manifest is missing 'interface' metadata.")
        interface = {}
    for field_name in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "websiteURL",
        "privacyPolicyURL",
        "termsOfServiceURL",
        "defaultPrompt",
    ):
        if field_name not in interface:
            warnings.append(
                f"Manifest interface is missing curated field '{field_name}'."
            )

    if payload.get("skills") is None and (plugin_root / "skills").exists():
        warnings.append("Plugin has a skills/ directory but plugin.json does not declare 'skills'.")
    if payload.get("hooks") is None and (plugin_root / "hooks.json").exists():
        warnings.append("Plugin has hooks.json but plugin.json does not declare 'hooks'.")

    if marketplace_payload is not None:
        plugins = marketplace_payload.get("plugins")
        if isinstance(plugins, list):
            entry = next(
                (
                    item
                    for item in plugins
                    if isinstance(item, dict) and item.get("name") == plugin_root.name
                ),
                None,
            )
            if entry is None:
                warnings.append("Marketplace entry is missing for this plugin.")
            else:
                entry_category = entry.get("category")
                if not isinstance(entry_category, str) or not entry_category.strip():
                    warnings.append(
                        f"Marketplace entry is missing category; suggested '{suggested_category}'."
                    )
                elif entry_category != suggested_category:
                    warnings.append(
                        f"Marketplace category '{entry_category}' differs from suggested '{suggested_category}' for inferred archetype '{inferred_archetype}'."
                    )
        else:
            warnings.append("Marketplace payload does not contain a valid plugins array.")

    recommendations.append(
        f"Use archetype '{inferred_archetype}' as the default contract language for docs and marketplace metadata."
    )
    recommendations.append(
        f"Prefer marketplace category '{suggested_category}' unless product positioning requires a deliberate override."
    )
    recommendations.append(
        "Run `audit-marketplace` after marketplace changes so entry normalization and plugin coverage stay in sync."
    )

    return {
        "plugin_root": str(plugin_root),
        "inferred_archetype": inferred_archetype,
        "suggested_category": suggested_category,
        "warnings": warnings,
        "recommendations": recommendations,
    }


def _print_audit_report(report: dict[str, Any]) -> None:
    print(json.dumps(report, indent=2))


def _print_findings(findings: list[dict[str, str]]) -> None:
    if not findings:
        print("PASS: plugin contract validation succeeded.")
        return
    error_count = sum(1 for item in findings if item.get("severity") == "error")
    warning_count = sum(1 for item in findings if item.get("severity") == "warning")
    status = "FAIL" if error_count else "WARN"
    print(f"{status}: plugin contract validation findings (errors={error_count}, warnings={warning_count}):")
    for finding in findings:
        severity = str(finding.get("severity") or "error").upper()
        message = str(finding.get("message") or "").strip()
        print(f"  - [{severity}] {message}")


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
    malformed_plugin_dirs = overlap_report.get("malformed_plugin_dirs") or []
    if malformed_plugin_dirs:
        print("WARNING: malformed local plugin directories detected (missing regular .codex-plugin/plugin.json):")
        for malformed_dir in malformed_plugin_dirs:
            print(f"  - {malformed_dir}")
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
        "skills": (
            args.with_skills
            or args.with_prompts
            or bool(
                source_report
                and (
                    source_report["detected_surfaces"]["skills"]
                    or source_report["detected_surfaces"]["commands"]
                )
            )
        ),
        "hooks": args.with_hooks or bool(source_report and (Path(source_report["plugin_root"]) / "hooks").exists()),
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
    archetype = args.archetype or (
        _infer_plugin_archetype(plugin_name, enabled_surfaces=enabled_surfaces)
        if source_report is None
        else _infer_plugin_archetype(
            plugin_name,
            payload=load_json(Path(source_report["primary_manifest"])) if source_report.get("primary_manifest") else None,
            enabled_surfaces=enabled_surfaces,
        )
    )
    effective_category = args.category or _suggest_marketplace_category(
        plugin_name,
        archetype=archetype,
        enabled_surfaces=enabled_surfaces,
    )
    policy_products = _effective_policy_products(args.product)
    strict_openai_layout = not bool(args.allow_legacy_marketplace_path)

    plugin_root.mkdir(parents=True, exist_ok=True)

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    write_json(
        plugin_json_path,
        build_plugin_json(
            plugin_name,
            enabled_surfaces,
            archetype=archetype,
        ),
        args.force,
    )
    write_text(plugin_root / "README.md", _render_readme_template(plugin_name, enabled_surfaces), args.force)
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
    write_text(
        plugin_root / "references" / "package-guide.md",
        _package_guide_template(plugin_name, enabled_surfaces),
        args.force,
    )
    if optional_directories["assets"]:
        write_text(
            plugin_root / "assets" / "README.md",
            _asset_brief_template(plugin_name),
            args.force,
        )

    if enabled_surfaces["hooks"]:
        create_json_file(
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
        create_json_file(
            plugin_root / ".mcp.json",
            {"mcpServers": {}},
            args.force,
        )

    if enabled_surfaces["apps"]:
        create_json_file(
            plugin_root / ".app.json",
            {"apps": {}},
            args.force,
        )

    helper_notes: list[str] = []
    if optional_directories["skills"]:
        skill_name = normalize_plugin_name(args.skill_name or plugin_name)
        validate_plugin_name(skill_name)
        helper_notes.append(
            _scaffold_plugin_skill(plugin_root / "skills", skill_name, args.force)
        )

    if optional_directories["agents"]:
        agent_name = normalize_plugin_name(args.agent_name or plugin_name)
        validate_plugin_name(agent_name)
        helper_notes.append(
            _scaffold_plugin_agent(plugin_root, agent_name, args.force)
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
            effective_category,
            args.force,
            strict_openai_layout=strict_openai_layout,
        )

    print(f"Created plugin scaffold: {plugin_root}")
    print(f"plugin manifest: {plugin_json_path}")
    print(f"archetype: {archetype}")
    print(f"suggested marketplace category: {effective_category}")
    if helper_notes:
        print("helper scaffolds:")
        for note in helper_notes:
            for line in note.splitlines():
                print(f"  - {line}")
    if args.with_prompts:
        print("NOTE: --with-prompts is deprecated in this repo and now folds prompt content into skills/.")
    if marketplace_path is not None:
        print(f"marketplace manifest: {marketplace_path}")
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    plugin_root = Path(args.plugin_path).expanduser().resolve()
    findings: list[dict[str, str]] = []
    allowed_signer_emails = _normalize_allowlist(args.allow_signer_email)
    allowed_signer_domains = _normalize_domain_allowlist(args.allow_signer_domain)
    allowed_signer_logins = _normalize_allowlist(args.allow_signer_login)

    def add_finding(severity: str, message: str) -> None:
        findings.append({"severity": severity, "message": message})

    if not plugin_root.exists() or not plugin_root.is_dir():
        print(f"ERROR: plugin path is not a directory: {plugin_root}", file=sys.stderr)
        return 1

    for required_rel in REQUIRED_PLUGIN_ROOT_FILES:
        required_path = plugin_root / required_rel
        if not required_path.exists():
            add_finding("error", f"Missing required file: {required_path}")

    legacy_claude_manifest = plugin_root / ".claude-plugin" / "plugin.json"
    if legacy_claude_manifest.exists():
        add_finding(
            "error",
            "Detected legacy Claude manifest `.claude-plugin/plugin.json`. "
            "Converted Codex packages must use `.codex-plugin/plugin.json` as runtime manifest."
        )

    for deprecated_surface in ("prompts", "commands", "slash-commands"):
        deprecated_path = plugin_root / deprecated_surface
        if deprecated_path.exists():
            add_finding(
                "warning",
                f"Deprecated runtime surface detected: {deprecated_path}. "
                "Fold prompt or command content into skills/ and keep only interface.defaultPrompt as optional entry text."
            )

    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    source_inspection = _inspect_source_root(plugin_root)
    if not plugin_json_path.exists() and source_inspection["plugin_roots"]:
        add_finding(
            "error",
            "Path looks like a source marketplace/plugin repo with provider manifests, not a converted Codex package. "
            "Run `plugin_builder.py inspect-source <path>` first."
        )

    if plugin_json_path.exists():
        for message in _check_plugin_manifest(plugin_json_path):
            add_finding("error", message)
        overlap_report = _find_existing_plugin_overlaps(
            plugin_root.name,
            plugin_root.parent,
            exclude_root=plugin_root,
        )
        for malformed_dir in overlap_report.get("malformed_plugin_dirs") or []:
            add_finding(
                "warning",
                f"Malformed sibling plugin directory missing regular manifest: {malformed_dir}"
            )
        if overlap_report["exact_matches"] or overlap_report["similar_matches"]:
            add_finding(
                "warning",
                "Local plugin overlap detected in sibling plugin directory. "
                "Review Infrastructure/references/deconflict-report.md and confirm merge/fold/improve intent."
            )
            deconflict_report_path = plugin_root / "references" / "deconflict-report.md"
            if not deconflict_report_path.exists():
                add_finding(
                    "warning",
                    f"Missing deconflict report for overlapping plugin intent: {deconflict_report_path}"
                )

    provenance_manifest_path: Path | None = None
    if args.provenance_manifest:
        provenance_manifest_path = Path(args.provenance_manifest).expanduser().resolve()
    elif args.require_signed_provenance:
        provenance_manifest_path = plugin_root / ".codex-plugin" / "provenance.json"

    if provenance_manifest_path is not None:
        for message in _check_provenance_manifest(
            provenance_manifest_path,
            plugin_root,
            require_signed_provenance=bool(args.require_signed_provenance),
            allowed_signer_emails=allowed_signer_emails,
            allowed_signer_domains=allowed_signer_domains,
            allowed_signer_logins=allowed_signer_logins,
        ):
            add_finding("error", message)

    marketplace_path = Path(args.marketplace_path).expanduser()
    strict_openai_layout = not bool(args.allow_legacy_marketplace_path)
    extra_marketplace_paths = [
        Path(raw_path).expanduser()
        for raw_path in (args.extra_marketplace_path or [])
    ]
    all_marketplace_paths = list(dict.fromkeys([marketplace_path, *extra_marketplace_paths]))
    if args.require_marketplace:
        readable_marketplaces = 0
        validated_in_marketplace = 0
        delayed_errors: list[str] = []
        for path in all_marketplace_paths:
            if not path.exists():
                add_finding("warning", f"Marketplace file unavailable: {path}")
                continue
            try:
                marketplace_payload = load_json(path)
            except Exception as exc:  # noqa: BLE001
                add_finding("warning", f"Marketplace load failed for '{path}': {exc}")
                continue
            readable_marketplaces += 1
            try:
                entry_failures = _check_marketplace_entry(
                    marketplace_payload,
                    plugin_root.name,
                    plugin_root,
                    path,
                    strict_openai_layout=strict_openai_layout,
                )
            except Exception as exc:  # noqa: BLE001
                delayed_errors.append(f"{path}: {exc}")
                continue
            if not entry_failures:
                validated_in_marketplace += 1
                continue
            for message in entry_failures:
                delayed_errors.append(f"{path}: {message}")

        if readable_marketplaces == 0:
            add_finding(
                "error",
                "Marketplace validation failed: no readable marketplace manifests were available.",
            )
        elif validated_in_marketplace == 0:
            add_finding(
                "error",
                "Marketplace validation failed: plugin entry did not validate in any readable marketplace manifest.",
            )
            for message in delayed_errors:
                add_finding("error", message)
        elif delayed_errors:
            for message in delayed_errors:
                add_finding("warning", message)

    _print_findings(findings)
    has_errors = any(item.get("severity") == "error" for item in findings)
    return 2 if has_errors else 0


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


def _run_audit_marketplace(args: argparse.Namespace) -> int:
    marketplace_path = Path(args.marketplace_path).expanduser()
    plugins_path = Path(args.plugins_path).expanduser().resolve()
    if not marketplace_path.exists():
        print(f"ERROR: marketplace path does not exist: {marketplace_path}", file=sys.stderr)
        return 1
    try:
        report = _audit_marketplace(
            marketplace_path,
            plugins_path,
            strict_openai_layout=not bool(args.allow_legacy_marketplace_path),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    _print_audit_report(report)
    has_errors = any(item.get("severity") == "error" for item in report["findings"])
    return 2 if has_errors else 0


def _run_normalize_marketplace(args: argparse.Namespace) -> int:
    marketplace_path = Path(args.marketplace_path).expanduser()
    plugins_path = Path(args.plugins_path).expanduser().resolve()
    try:
        payload, notes = _normalize_marketplace_payload(
            marketplace_path,
            plugins_path,
            strict_openai_layout=not bool(args.allow_legacy_marketplace_path),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    changed = True
    if marketplace_path.exists():
        current_payload = load_json(marketplace_path)
        changed = current_payload != payload
    report = {
        "marketplace_path": str(marketplace_path),
        "plugins_path": str(plugins_path),
        "changed": changed,
        "notes": notes,
    }
    if args.write:
        write_json(marketplace_path, payload, force=True)
    else:
        report["normalized_payload"] = payload
    _print_audit_report(report)
    return 0


def _run_audit_compat(args: argparse.Namespace) -> int:
    plugin_root = Path(args.plugin_path).expanduser().resolve()
    if not plugin_root.exists() or not plugin_root.is_dir():
        print(f"ERROR: plugin path is not a directory: {plugin_root}", file=sys.stderr)
        return 1
    marketplace_payload = None
    if args.marketplace_path:
        marketplace_path = Path(args.marketplace_path).expanduser()
        if marketplace_path.exists():
            if not args.allow_legacy_marketplace_path:
                try:
                    repo_root = _marketplace_repo_root(marketplace_path)
                    _enforce_openai_marketplace_layout(marketplace_path, repo_root)
                except ValueError as exc:
                    print(f"ERROR: {exc}", file=sys.stderr)
                    return 1
            marketplace_payload = load_json(marketplace_path)
    report = _audit_plugin_compatibility(plugin_root, marketplace_payload=marketplace_payload)
    _print_audit_report(report)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold and validate Codex plugin packages (requires uv in PATH)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create a plugin skeleton with a complete plugin.json and package docs.",
    )
    scaffold_parser.add_argument("plugin_name")
    scaffold_parser.add_argument(
        "--archetype",
        choices=sorted(ARCHETYPE_PROFILES),
        default=None,
        help="Archetype that drives curated manifest defaults and category suggestions.",
    )
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
    scaffold_parser.add_argument("--with-hooks-json", action="store_true", help="Create hooks.json scaffold.")
    scaffold_parser.add_argument(
        "--with-prompts",
        action="store_true",
        help="Deprecated alias: fold prompt content into skills/ instead of creating prompts/.",
    )
    scaffold_parser.add_argument(
        "--skill-name",
        help="Plugin-owned skill name to scaffold under skills/ (defaults to plugin name).",
    )
    scaffold_parser.add_argument("--with-agents", action="store_true", help="Create agents/ directory.")
    scaffold_parser.add_argument(
        "--agent-name",
        help="Plugin-owned agent role name to scaffold under agents/ (defaults to plugin name).",
    )
    scaffold_parser.add_argument("--with-scripts", action="store_true", help="Create Infrastructure/scripts/ directory.")
    scaffold_parser.add_argument(
        "--with-assets",
        action="store_true",
        help="Create assets/ for optional docs or real visual assets without wiring manifest image paths by default.",
    )
    scaffold_parser.add_argument(
        "--with-mcp",
        action="store_true",
        help="Create .mcp.json scaffold only for a real MCP integration the plugin will expose.",
    )
    scaffold_parser.add_argument(
        "--with-apps",
        action="store_true",
        help="Create .app.json scaffold only for a real ChatGPT App or app connector surface the plugin will expose.",
    )
    scaffold_parser.add_argument(
        "--with-marketplace",
        action="store_true",
        help="Create or update .agents/Plugins/marketplace.json.",
    )
    scaffold_parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json (defaults to <repo>/.agents/Plugins/marketplace.json).",
    )
    scaffold_parser.add_argument(
        "--product",
        action="append",
        choices=sorted(VALID_POLICY_PRODUCTS),
        default=None,
        help=(
            "Marketplace policy.products value. Repeat for multiple products. "
            "Defaults to CODEX."
        ),
    )
    scaffold_parser.add_argument(
        "--allow-legacy-marketplace-path",
        action="store_true",
        help="Allow legacy Plugins/marketplace.json layout instead of strict .agents/Plugins/marketplace.json.",
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
        help="Marketplace category value. Defaults to an archetype-aware suggestion.",
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
        "--extra-marketplace-path",
        action="append",
        default=[],
        help="Additional marketplace manifests to load with graceful partial-failure handling.",
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
    validate_parser.add_argument(
        "--allow-legacy-marketplace-path",
        action="store_true",
        help="Allow legacy Plugins/marketplace.json layout instead of strict .agents/Plugins/marketplace.json.",
    )
    validate_parser.add_argument(
        "--provenance-manifest",
        help="Optional provenance manifest JSON path for source-commit verification checks.",
    )
    validate_parser.add_argument(
        "--require-signed-provenance",
        action="store_true",
        help=(
            "Require provenance commit verification to be signed/verified. "
            "Defaults to `<plugin>/.codex-plugin/provenance.json` when --provenance-manifest is omitted."
        ),
    )
    validate_parser.add_argument(
        "--allow-signer-email",
        action="append",
        default=[],
        help="Require provenance signer identity to include one of these exact email addresses.",
    )
    validate_parser.add_argument(
        "--allow-signer-domain",
        action="append",
        default=[],
        help="Require provenance signer identity to include one of these email domains.",
    )
    validate_parser.add_argument(
        "--allow-signer-login",
        action="append",
        default=[],
        help="Require provenance signer identity to include one of these GitHub logins.",
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

    audit_marketplace_parser = subparsers.add_parser(
        "audit-marketplace",
        help="Audit marketplace coverage, entry normalization, and plugin-directory alignment.",
    )
    audit_marketplace_parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json.",
    )
    audit_marketplace_parser.add_argument(
        "--plugins-path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Path to the local plugins directory.",
    )
    audit_marketplace_parser.add_argument(
        "--allow-legacy-marketplace-path",
        action="store_true",
        help="Allow legacy Plugins/marketplace.json layout instead of strict .agents/Plugins/marketplace.json.",
    )

    normalize_marketplace_parser = subparsers.add_parser(
        "normalize-marketplace",
        help="Normalize marketplace entries to canonical nested policy/source shape and sorted order.",
    )
    normalize_marketplace_parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json.",
    )
    normalize_marketplace_parser.add_argument(
        "--plugins-path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Path to the local plugins directory.",
    )
    normalize_marketplace_parser.add_argument(
        "--write",
        action="store_true",
        help="Write the normalized payload back to marketplace.json.",
    )
    normalize_marketplace_parser.add_argument(
        "--allow-legacy-marketplace-path",
        action="store_true",
        help="Allow legacy Plugins/marketplace.json layout instead of strict .agents/Plugins/marketplace.json.",
    )

    audit_compat_parser = subparsers.add_parser(
        "audit-compat",
        help="Audit a plugin against curated upstream-style package conventions.",
    )
    audit_compat_parser.add_argument("plugin_path", help="Path to plugin root.")
    audit_compat_parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Optional marketplace.json path for category and entry comparison.",
    )
    audit_compat_parser.add_argument(
        "--allow-legacy-marketplace-path",
        action="store_true",
        help="Allow legacy Plugins/marketplace.json layout instead of strict .agents/Plugins/marketplace.json.",
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
    if args.command == "audit-marketplace":
        raise SystemExit(_run_audit_marketplace(args))
    if args.command == "normalize-marketplace":
        raise SystemExit(_run_normalize_marketplace(args))
    if args.command == "audit-compat":
        raise SystemExit(_run_audit_compat(args))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
