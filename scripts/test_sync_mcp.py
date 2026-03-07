#!/usr/bin/env python3
"""Tests for scripts/sync_mcp.py.

Coverage targets:
  - build_antigravity_config: STDIO servers, HTTP servers with bearer tokens,
    env_http_headers, disabled servers, injected defaults (agentation, sequential-thinking).
  - main(): merge preserves existing top-level keys; corrupted existing JSON is
    handled gracefully; output file is written atomically with expected shape.

Run with:
  python3 scripts/test_sync_mcp.py
  python3 -m pytest scripts/test_sync_mcp.py -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# sync_mcp.py does `import tomli as tomllib` (not the stdlib tomllib) and
# calls sys.exit(1) on ImportError.  Pre-seed sys.modules["tomli"] with the
# stdlib tomllib (available since Python 3.11) BEFORE importing the module so
# the exit never fires.
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent

def _ensure_tomli_available() -> None:
    if "tomli" in sys.modules:
        return
    try:
        import tomllib  # stdlib on 3.11+
        sys.modules["tomli"] = tomllib  # type: ignore[assignment]
        return
    except ModuleNotFoundError:
        pass
    try:
        import tomli  # noqa: F401  # third-party fallback
        return
    except ModuleNotFoundError:
        pass
    # Last resort: minimal stub so the import succeeds in restricted envs.
    stub = types.ModuleType("tomli")
    stub.load = lambda f: {}  # type: ignore[attr-defined]
    sys.modules["tomli"] = stub

_ensure_tomli_available()
sys.path.insert(0, str(SCRIPT_DIR))
import sync_mcp  # noqa: E402

WRAPPER = (
    "set -a; "
    "[ -f ~/.codex/.env ] && . ~/.codex/.env >/dev/null 2>&1; "
    "[ -f ~/dev/config/.env ] && . ~/dev/config/.env >/dev/null 2>&1; "
    "set +a; exec "
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _exec_string(mcp_obj: dict) -> str:
    """Return the exec portion of the sh -c arg (strips the wrapper prefix)."""
    assert mcp_obj["command"] == "sh"
    sh_arg = mcp_obj["args"][1]
    assert sh_arg.startswith(WRAPPER), f"Missing wrapper prefix in: {sh_arg!r}"
    return sh_arg[len(WRAPPER):]


# ---------------------------------------------------------------------------
# build_antigravity_config
# ---------------------------------------------------------------------------
class TestBuildAntigravityConfigStdio(unittest.TestCase):

    def _config(self, servers: dict) -> dict:
        return sync_mcp.build_antigravity_config({"mcp_servers": servers})

    def test_stdio_server_is_included(self):
        cfg = self._config({"myserver": {"command": "npx", "args": ["-y", "some-pkg"]}})
        self.assertIn("myserver", cfg["mcpServers"])

    def test_stdio_server_uses_sh_wrapper(self):
        cfg = self._config({"s": {"command": "node", "args": ["server.js"]}})
        obj = cfg["mcpServers"]["s"]
        self.assertEqual(obj["command"], "sh")
        self.assertEqual(obj["args"][0], "-c")

    def test_stdio_server_exec_contains_command_and_args(self):
        cfg = self._config({"s": {"command": "npx", "args": ["-y", "pkg@1.0"]}})
        exec_str = _exec_string(cfg["mcpServers"]["s"])
        self.assertIn("npx", exec_str)
        self.assertIn("-y", exec_str)
        self.assertIn("pkg@1.0", exec_str)

    def test_disabled_server_is_excluded(self):
        cfg = self._config({
            "active": {"command": "npx", "args": []},
            "inactive": {"command": "npx", "args": [], "enabled": False},
        })
        self.assertIn("active", cfg["mcpServers"])
        self.assertNotIn("inactive", cfg["mcpServers"])

    def test_server_without_command_or_url_is_skipped(self):
        cfg = self._config({"ghost": {"foo": "bar"}})
        self.assertNotIn("ghost", cfg["mcpServers"])


class TestBuildAntigravityConfigHttp(unittest.TestCase):

    def _config(self, server_cfg: dict) -> dict:
        return sync_mcp.build_antigravity_config({"mcp_servers": {"srv": server_cfg}})

    def test_http_server_uses_mcp_remote(self):
        cfg = self._config({"url": "https://example.com/mcp"})
        exec_str = _exec_string(cfg["mcpServers"]["srv"])
        self.assertIn("mcp-remote", exec_str)
        self.assertIn("https://example.com/mcp", exec_str)

    def test_bearer_token_env_var_added_as_auth_header(self):
        cfg = self._config({"url": "https://api.example.com/mcp", "bearer_token_env_var": "MY_TOKEN"})
        exec_str = _exec_string(cfg["mcpServers"]["srv"])
        self.assertIn("Authorization", exec_str)
        self.assertIn("$MY_TOKEN", exec_str)

    def test_env_http_headers_added(self):
        cfg = self._config({
            "url": "https://api.example.com/mcp",
            "env_http_headers": {"X-Api-Key": "SOME_KEY"},
        })
        exec_str = _exec_string(cfg["mcpServers"]["srv"])
        self.assertIn("X-Api-Key", exec_str)
        self.assertIn("$SOME_KEY", exec_str)

    def test_multiple_env_http_headers(self):
        cfg = self._config({
            "url": "https://api.example.com/mcp",
            "env_http_headers": {"X-Key1": "K1", "X-Key2": "K2"},
        })
        exec_str = _exec_string(cfg["mcpServers"]["srv"])
        self.assertIn("$K1", exec_str)
        self.assertIn("$K2", exec_str)


class TestBuildAntigravityConfigDefaults(unittest.TestCase):

    def test_sequential_thinking_injected_when_absent(self):
        cfg = sync_mcp.build_antigravity_config({"mcp_servers": {}})
        self.assertIn("sequential-thinking", cfg["mcpServers"])

    def test_sequential_thinking_not_duplicated_when_present(self):
        cfg = sync_mcp.build_antigravity_config({
            "mcp_servers": {
                "sequential-thinking": {"command": "node", "args": ["custom.js"]}
            }
        })
        # Should still be present (the user-defined one was kept via the loop).
        self.assertIn("sequential-thinking", cfg["mcpServers"])
        # Only one entry (no duplication).
        self.assertEqual(
            list(cfg["mcpServers"]).count("sequential-thinking"), 1
        )

    def test_agentation_injected_when_absent(self):
        cfg = sync_mcp.build_antigravity_config({"mcp_servers": {}})
        self.assertIn("agentation", cfg["mcpServers"])

    def test_agentation_exec_contains_agentation_mcp(self):
        cfg = sync_mcp.build_antigravity_config({"mcp_servers": {}})
        obj = cfg["mcpServers"]["agentation"]
        sh_arg = obj["args"][1]
        self.assertIn("agentation-mcp", sh_arg)

    def test_output_has_mcp_servers_key(self):
        cfg = sync_mcp.build_antigravity_config({"mcp_servers": {}})
        self.assertIn("mcpServers", cfg)

    def test_empty_mcp_servers_still_has_defaults(self):
        cfg = sync_mcp.build_antigravity_config({})
        servers = cfg["mcpServers"]
        self.assertIn("sequential-thinking", servers)
        self.assertIn("agentation", servers)


# ---------------------------------------------------------------------------
# main() — file merge behaviour
# ---------------------------------------------------------------------------
class TestMainMergeBehaviour(unittest.TestCase):
    """Tests that main() writes the expected JSON and merges correctly."""

    def _run_main(self, tmp: Path, codex_toml: dict, existing_json: dict | None = None):
        """Call main() with fake config/output paths injected via monkeypatching."""
        config_path = tmp / "config.toml"
        output_path = tmp / "mcp_config.json"

        if existing_json is not None:
            output_path.write_text(json.dumps(existing_json), encoding="utf-8")

        # Patch the module-level path constants and load_codex_config.
        with (
            patch.object(sync_mcp, "CODEX_CONFIG_PATH", str(config_path)),
            patch.object(sync_mcp, "ANTIGRAVITY_MCP_PATH", str(output_path)),
            patch.object(sync_mcp, "load_codex_config", return_value=codex_toml),
        ):
            sync_mcp.main()

        return json.loads(output_path.read_text(encoding="utf-8"))

    def test_main_creates_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_main(Path(tmp), {})
            self.assertIn("mcpServers", result)

    def test_main_preserves_existing_top_level_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = {"customKey": "preserved", "mcpServers": {}}
            result = self._run_main(Path(tmp), {}, existing_json=existing)
            self.assertEqual(result.get("customKey"), "preserved")

    def test_main_replaces_mcp_servers_not_merges(self):
        """mcpServers is fully replaced; stale entries don't linger."""
        with tempfile.TemporaryDirectory() as tmp:
            existing = {"mcpServers": {"stale-server": {"command": "old"}}}
            # Codex config has no servers → only defaults injected.
            result = self._run_main(Path(tmp), {}, existing_json=existing)
            self.assertNotIn("stale-server", result["mcpServers"])

    def test_main_handles_corrupted_existing_json(self):
        """Corrupted existing file is treated as empty rather than crashing."""
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "mcp_config.json"
            output_path.write_text("{not valid json}", encoding="utf-8")
            config_path = Path(tmp) / "config.toml"
            with (
                patch.object(sync_mcp, "CODEX_CONFIG_PATH", str(config_path)),
                patch.object(sync_mcp, "ANTIGRAVITY_MCP_PATH", str(output_path)),
                patch.object(sync_mcp, "load_codex_config", return_value={}),
            ):
                sync_mcp.main()
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertIn("mcpServers", result)

    def test_main_server_count_matches_stdout(self, capsys=None):
        """Server count printed to stdout matches mcpServers length."""
        with tempfile.TemporaryDirectory() as tmp:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                result = self._run_main(Path(tmp), {"mcp_servers": {
                    "server-a": {"command": "npx", "args": ["-y", "pkg-a"]},
                    "server-b": {"url": "https://b.example.com/mcp"},
                }})
            output = buf.getvalue()
            expected_count = len(result["mcpServers"])
            self.assertIn(str(expected_count), output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
