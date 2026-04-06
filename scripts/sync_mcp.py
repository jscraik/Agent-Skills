#!/usr/bin/env python3
import sys
import os
import json
import logging
import re
import shlex

try:
    import tomllib  # stdlib (Python ≥ 3.11)
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]  # third-party backport
    except ModuleNotFoundError:
        logging.error("Error: Please install tomli: pip install tomli")
        sys.exit(1)

CODEX_CONFIG_PATH = os.path.expanduser("~/.codex/config.toml")
ANTIGRAVITY_MCP_PATH = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")
ENV_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def is_valid_env_var_name(value):
    return isinstance(value, str) and ENV_VAR_RE.fullmatch(value) is not None

def load_codex_config():
    if not os.path.exists(CODEX_CONFIG_PATH):
        print(f"Error: Could not find {CODEX_CONFIG_PATH}")
        sys.exit(1)
    
    with open(CODEX_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)

def build_antigravity_config(codex_config):
    mcp_servers = {}
    
    # Source .env files and then execute the configured command safely.
    wrapper = "set -a; [ -f ~/.codex/.env ] && . ~/.codex/.env >/dev/null 2>&1; [ -f ~/dev/config/.env ] && . ~/dev/config/.env >/dev/null 2>&1; set +a"
    
    servers = codex_config.get("mcp_servers", {})
    for server_name, config in servers.items():
        if config.get("enabled") is False:
            continue
            
        mcp_obj = {}
        
        # 1. STDIO servers
        if "command" in config:
            cmd = str(config["command"])
            args = [str(arg) for arg in config.get("args", [])]

            mcp_obj["command"] = "sh"
            mcp_obj["args"] = [
                "-c",
                f"{wrapper}; exec \"$@\"",
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
                else:
                    logging.warning("Skipping invalid bearer_token_env_var for %s", server_name)
                
            # Auth header (env_http_headers)
            if "env_http_headers" in config:
                for header_key, header_var in config["env_http_headers"].items():
                    if is_valid_env_var_name(header_var):
                        header_prefix = shlex.quote(f"{header_key}: ")
                        script_lines.append(
                            f'set -- "$@" --header {header_prefix}"${{{header_var}}}"'
                        )
                    else:
                        logging.warning("Skipping invalid env_http_headers var for %s: %s", server_name, header_key)
            
            mcp_obj["command"] = "sh"
            mcp_obj["args"] = [
                "-c",
                "; ".join(script_lines + ['exec "$@"']),
            ]
        else:
            continue
            
        mcp_servers[server_name] = mcp_obj

    # Antigravity ships sequentially-thinking by default typically
    if "sequential-thinking" not in mcp_servers:
        mcp_servers["sequential-thinking"] = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
        }
        
    # User requested agentation MCP to be globally available in Antigravity
    if "agentation" not in mcp_servers:
        mcp_servers["agentation"] = {
            "command": "sh",
            "args": ["-c", f"{wrapper}; exec npx -y agentation-mcp server"]
        }

    return {"mcpServers": mcp_servers}

def main():
    codex_config = load_codex_config()
    antigravity_mcp_config = build_antigravity_config(codex_config)
    
    os.makedirs(os.path.dirname(ANTIGRAVITY_MCP_PATH), exist_ok=True)
    
    # Merge carefully
    existing_config = {}
    if os.path.exists(ANTIGRAVITY_MCP_PATH):
        try:
            with open(ANTIGRAVITY_MCP_PATH, "r") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(
                f"Warning: Existing MCP config at {ANTIGRAVITY_MCP_PATH} is not valid JSON; starting from a fresh config. ({e})",
                file=sys.stderr,
            )
            existing_config = {}
            
    existing_config["mcpServers"] = antigravity_mcp_config["mcpServers"]
    
    with open(ANTIGRAVITY_MCP_PATH, "w") as f:
        json.dump(existing_config, f, indent=2)
        
    print(f"✅ Generated {len(antigravity_mcp_config['mcpServers'])} MCP servers in {ANTIGRAVITY_MCP_PATH}")
    print("Restart Antigravity or type '/refresh' to pick up the changes.")

if __name__ == "__main__":
    main()
