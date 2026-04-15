#!/usr/bin/env python3
"""MCP (Model Context Protocol) configuration sync commands."""
import os
import json
import re
import shlex
import shutil
import subprocess
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
FALLBACK_PYTHONS = (
    "python3",
    "python3.12",
    "/usr/local/bin/python3.12",
    "/opt/homebrew/bin/python3.12",
    "python3.11",
    "/usr/local/bin/python3.11",
    "/opt/homebrew/bin/python3.11",
)


def is_valid_env_var_name(value):
    return isinstance(value, str) and ENV_VAR_RE.fullmatch(value) is not None


def load_codex_config():
    if not os.path.exists(CODEX_CONFIG_PATH):
        return None

    if tomllib is None:
        return _load_toml_with_newer_python(CODEX_CONFIG_PATH)

    with open(CODEX_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def _load_toml_with_newer_python(path: str):
    """Parse TOML via an available Python 3.11+ interpreter when possible."""
    loader = (
        "import json, sys, tomllib\n"
        "with open(sys.argv[1], 'rb') as f:\n"
        "    print(json.dumps(tomllib.load(f)))"
    )
    for candidate in _iter_fallback_pythons():
        if candidate is None:
            continue
        try:
            proc = subprocess.run(
                [candidate, "-c", loader, path],
                check=True,
                capture_output=True,
                text=True,
            )
            return json.loads(proc.stdout)
        except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
            continue
    return None


def _iter_fallback_pythons():
    seen = set()
    for candidate in FALLBACK_PYTHONS:
        if os.path.isabs(candidate):
            resolved = candidate if os.path.exists(candidate) else None
        else:
            resolved = shutil.which(candidate)

        if not resolved or resolved in seen:
            continue

        try:
            version_check = subprocess.run(
                [resolved, "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            continue

        if version_check.returncode == 0:
            seen.add(resolved)
            yield resolved


def build_antigravity_config(codex_config):
    mcp_servers = {}
    NAME_MAPPING = {
        "repo-prompt": "repoprompt",
    }

    # Source .env files and ensure Node/npm tool paths are available.
    wrapper = (
        "set -a; "
        "[ -f ~/.codex/.env ] && . ~/.codex/.env >/dev/null 2>&1; "
        "[ -f ~/dev/configs/.env ] && . ~/dev/configs/.env >/dev/null 2>&1; "
        "set +a; "
        'export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/share/mise/shims:$PATH"'
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

    if tomllib is None and not list(_iter_fallback_pythons()):
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_DEPENDENCY",
            message="tomli/tomllib not available and no python3.11+/python3.12 fallback found.",
            fix_suggestion="Install tomli (`uv pip install tomli`) or install Python 3.11+"
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
