#!/usr/bin/env python3
"""Export MCP configuration from Codex TOML to JSON."""

import json
import os
import re
import shlex
import shutil
import subprocess
import sys

try:
    import tomllib  # stdlib (Python >= 3.11)
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None

CODEX_CONFIG_PATH = "~/.codex/config.toml"
CODEX_MCP_EXPORT_PATH = "~/.codex/mcp_config.json"
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

NAME_MAPPING = {"repo-prompt": "repoprompt"}


def is_valid_env_var_name(value):
    return isinstance(value, str) and ENV_VAR_RE.fullmatch(value) is not None


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


def _load_toml_with_newer_python(path):
    loader = (
        "import json, sys, tomllib\n"
        "with open(sys.argv[1], 'rb') as f:\n"
        "    print(json.dumps(tomllib.load(f)))"
    )
    for candidate in _iter_fallback_pythons():
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


def load_codex_config():
    path = os.path.expanduser(CODEX_CONFIG_PATH)
    if not os.path.exists(path):
        print(f"Error: Could not find {path}")
        sys.exit(1)

    if tomllib is not None:
        with open(path, "rb") as f:
            return tomllib.load(f)

    fallback = _load_toml_with_newer_python(path)
    if fallback is not None:
        return fallback

    print("Error: Could not parse Codex config. Install tomli or use Python 3.11+.", file=sys.stderr)
    sys.exit(1)


def build_codex_mcp_config(codex_config):
    mcp_servers = {}
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

        if "command" in config:
            cmd = str(config["command"])
            args = [str(arg) for arg in config.get("args", [])]
            mcp_servers[mcp_name] = {
                "command": "sh",
                "args": ["-c", f'{wrapper}; exec "$@"', "sync-mcp", cmd, *args],
            }
            continue

        if "url" in config:
            url = str(config["url"])
            script_lines = [wrapper, f"set -- npx -y mcp-remote {shlex.quote(url)}"]

            if "bearer_token_env_var" in config:
                env_var = config["bearer_token_env_var"]
                if is_valid_env_var_name(env_var):
                    script_lines.append('set -- "$@" --header "Authorization: Bearer ${' + env_var + '}"')

            if "env_http_headers" in config:
                for header_key, header_var in config["env_http_headers"].items():
                    if is_valid_env_var_name(header_var):
                        header_prefix = shlex.quote(f"{header_key}: ")
                        script_lines.append('set -- "$@" --header ' + header_prefix + '"${' + header_var + '}"')

            mcp_servers[mcp_name] = {
                "command": "sh",
                "args": ["-c", "; ".join(script_lines + ['exec "$@"'])],
            }

    return {"mcpServers": mcp_servers}


def main():
    codex_config = load_codex_config()
    export_mcp_config = build_codex_mcp_config(codex_config)

    output_path = os.path.expanduser(CODEX_MCP_EXPORT_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    existing_config = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing_config = {}

    existing_config["mcpServers"] = export_mcp_config["mcpServers"]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(existing_config, f, indent=2)

    count = len(export_mcp_config["mcpServers"])
    print(f"Synced {count} MCP servers to {output_path}")


if __name__ == "__main__":
    main()
