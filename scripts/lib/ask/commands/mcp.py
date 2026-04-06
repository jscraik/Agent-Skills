#!/usr/bin/env python3
"""MCP (Model Context Protocol) configuration sync commands."""
import os
import json
import logging
import re
import shlex
from pathlib import Path
from ask.envelope import CallResult, ErrorObject

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

CODEX_CONFIG_PATH = os.path.expanduser("~/.codex/config.toml")
ANTIGRAVITY_MCP_PATH = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")
ENV_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def is_valid_env_var_name(value):
    return isinstance(value, str) and ENV_VAR_RE.fullmatch(value) is not None


def load_codex_config():
    if not os.path.exists(CODEX_CONFIG_PATH):
        return None

    if tomllib is None:
        return None

    with open(CODEX_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def build_antigravity_config(codex_config):
    mcp_servers = {}
    NAME_MAPPING = {
        "repo-prompt": "repoprompt",
    }

    # Loader to source .env files (handles regular files and FIFOs with 0.5s timeout)
    source_env = (
        'for f in ~/.codex/.env ~/dev/config/.env; do '
        '[ -e "$f" ] && { tmp=$(mktemp); timeout 0.5s cat "$f" > "$tmp" || true; [ -s "$tmp" ] && . "$tmp"; rm -f "$tmp"; }; '
        'done'
    )
    # Ensure Homebrew and Mise shims are on the PATH for npx and other tools
    wrapper = (
        'export PATH="/opt/homebrew/bin:$HOME/.local/share/mise/shims:$PATH"; '
        f'set -a; {source_env}; set +a'
    )

    servers = codex_config.get("mcp_servers", {})
    for server_name, config in servers.items():
        if config.get("enabled") is False:
            continue

        mcp_name = NAME_MAPPING.get(server_name, server_name)
        mcp_obj = {}

        # 1. STDIO servers
        if "command" in config:
            cmd = str(config["command"])
            args = [str(arg) for arg in config.get("args", [])]

            mcp_obj["command"] = "sh"
            mcp_obj["args"] = [
                "-c",
                f'{wrapper}; exec "$@"',
                "sync-mcp",
                cmd,
                *args,
            ]

        # 2. HTTP servers (Requires mcp-remote bridge for Antigravity)
        elif "url" in config:
            url = str(config["url"])
            script_lines = [
                wrapper,
                f"set -- npx -y mcp-remote {shlex.quote(url)}",
            ]

            # Auth header (bearer_token_env_var)
            if "bearer_token_env_var" in config:
                env_var = config["bearer_token_env_var"]
                if is_valid_env_var_name(env_var):
                    script_lines.append(
                        f'set -- "$@" --header "Authorization: Bearer ${{{env_var}}}"'
                    )

            # Auth header (env_http_headers)
            if "env_http_headers" in config:
                for header_key, header_var in config["env_http_headers"].items():
                    if is_valid_env_var_name(header_var):
                        header_prefix = shlex.quote(f"{header_key}: ")
                        script_lines.append(
                            f'set -- "$@" --header {header_prefix}"${{{header_var}}}"'
                        )

            mcp_obj["command"] = "sh"
            mcp_obj["args"] = [
                "-c",
                "; ".join(script_lines + ['exec "$@"']),
            ]
        else:
            continue

        # Deduplicate remote servers by URL
        if "url" in config:
            is_duplicate = False
            for existing_mcp in mcp_servers.values():
                if existing_mcp.get("command") == "sh" and any(config["url"] in arg for arg in existing_mcp.get("args", [])):
                    is_duplicate = True
                    break
            if is_duplicate:
                continue

        mcp_servers[mcp_name] = mcp_obj

    # User requested agentation MCP to be globally available in Antigravity
    if "agentation" not in mcp_servers:
        mcp_servers["agentation"] = {
            "command": "sh",
            "args": [
                "-c",
                f"{wrapper}; exec npx -y agentation-mcp server"
            ]
        }

    return {"mcpServers": mcp_servers}


def sync_mcp(repo_root: Path, dry_run: bool = False) -> CallResult:
    """Sync MCP configuration from Codex to Antigravity."""
    result = CallResult()

    if tomllib is None:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_DEPENDENCY",
            message="tomli/tomllib not available. Install tomli: pip install tomli",
            fix_suggestion="pip install tomli"
        ))
        return result

    codex_config = load_codex_config()

    if codex_config is None:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Could not load Codex config from {CODEX_CONFIG_PATH}",
            fix_suggestion="Ensure ~/.codex/config.toml exists and is valid TOML"
        ))
        return result

    antigravity_mcp_config = build_antigravity_config(codex_config)
    server_count = len(antigravity_mcp_config["mcpServers"])

    result.data["servers"] = list(antigravity_mcp_config["mcpServers"].keys())
    result.data["server_count"] = server_count
    result.data["dry_run"] = dry_run
    result.data["target_path"] = ANTIGRAVITY_MCP_PATH

    if dry_run:
        result.status = "success"
        result.metadata["next_steps"] = ["ask mcp sync"]
        return result

    # Ensure directory exists
    os.makedirs(os.path.dirname(ANTIGRAVITY_MCP_PATH), exist_ok=True)

    # Merge carefully with existing config
    existing_config = {}
    if os.path.exists(ANTIGRAVITY_MCP_PATH):
        try:
            with open(ANTIGRAVITY_MCP_PATH, "r") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing_config = {}

    existing_config["mcpServers"] = antigravity_mcp_config["mcpServers"]

    try:
        with open(ANTIGRAVITY_MCP_PATH, "w") as f:
            json.dump(existing_config, f, indent=2)
        result.status = "success"
        result.metadata["next_steps"] = ["Restart Antigravity or type '/refresh' to pick up changes"]
    except OSError as e:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_RUNTIME",
            message=f"Failed to write MCP config: {e}"
        ))

    return result
