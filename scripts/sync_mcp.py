#!/usr/bin/env python3
import sys
import os
import json
import logging

try:
    import tomli as tomllib
except ModuleNotFoundError:
    logging.error("Error: Please install tomli if using Python < 3.11: pip install tomli")
    sys.exit(1)

CODEX_CONFIG_PATH = os.path.expanduser("~/.codex/config.toml")
ANTIGRAVITY_MCP_PATH = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")

def load_codex_config():
    if not os.path.exists(CODEX_CONFIG_PATH):
        print(f"Error: Could not find {CODEX_CONFIG_PATH}")
        sys.exit(1)
    
    with open(CODEX_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)

def build_antigravity_config(codex_config):
    mcp_servers = {}
    
    # We build an inline sh -c string to source your two .env files 
    # and explicitly export variables before executing the MCP command.
    wrapper = "set -a; [ -f ~/.codex/.env ] && . ~/.codex/.env >/dev/null 2>&1; [ -f ~/dev/config/.env ] && . ~/dev/config/.env >/dev/null 2>&1; set +a; exec "
    
    servers = codex_config.get("mcp_servers", {})
    for server_name, config in servers.items():
        if config.get("enabled") is False:
            continue
            
        mcp_obj = {}
        
        # 1. STDIO servers
        if "command" in config:
            cmd = config["command"]
            args = config.get("args", [])
            
            # Combine into a single executed string
            full_exec = f'{cmd}'
            for arg in args:
                # Basic escaping for args
                full_exec += f' "{arg}"'
                
            mcp_obj["command"] = "sh"
            mcp_obj["args"] = [
                "-c",
                wrapper + full_exec
            ]
            
        # 2. HTTP servers (Requires mcp-remote bridge for Antigravity)
        elif "url" in config:
            url = config["url"]
            full_exec = f'npx -y mcp-remote "{url}"'
            
            # Auth header (bearer_token_env_var)
            if "bearer_token_env_var" in config:
                env_var = config["bearer_token_env_var"]
                full_exec += f' --header "Authorization: Bearer ${env_var}"'
                
            # Auth header (env_http_headers)
            if "env_http_headers" in config:
                for header_key, header_var in config["env_http_headers"].items():
                    full_exec += f' --header "{header_key}: ${header_var}"'
            
            mcp_obj["command"] = "sh"
            mcp_obj["args"] = [
                "-c",
                wrapper + full_exec
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
            "args": ["-c", wrapper + "npx -y agentation-mcp server"]
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
            print(f"Warning: Existing MCP config at {ANTIGRAVITY_MCP_PATH} is not valid JSON; starting from a fresh config.", file=sys.stderr)
            existing_config = {}
            pass
            
    existing_config["mcpServers"] = antigravity_mcp_config["mcpServers"]
    
    with open(ANTIGRAVITY_MCP_PATH, "w") as f:
        json.dump(existing_config, f, indent=2)
        
    print(f"✅ Generated {len(antigravity_mcp_config['mcpServers'])} MCP servers in {ANTIGRAVITY_MCP_PATH}")
    print("Restart Antigravity or type '/refresh' to pick up the changes.")

if __name__ == "__main__":
    main()
