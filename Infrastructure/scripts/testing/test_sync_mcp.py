#!/usr/bin/env python3
"""Tests for Infrastructure/scripts/lifecycle-and-sync/sync_mcp.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent


def _ensure_tomli_available() -> None:
    if "tomli" in sys.modules:
        return
    try:
        import tomllib

        sys.modules["tomli"] = tomllib  # type: ignore[assignment]
        return
    except ModuleNotFoundError:
        pass
    try:
        import tomli  # noqa: F401

        return
    except ModuleNotFoundError:
        pass
    fallback_module = types.ModuleType("tomli")
    fallback_module.load = lambda _file: {}  # type: ignore[attr-defined]
    sys.modules["tomli"] = fallback_module


_ensure_tomli_available()
SYNC_MCP_PATH = SCRIPT_DIR.parent / "lifecycle-and-sync" / "sync_mcp.py"


def _load_sync_mcp_module():
    spec = importlib.util.spec_from_file_location("sync_mcp_under_test", SYNC_MCP_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load sync_mcp module from {SYNC_MCP_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


sync_mcp = _load_sync_mcp_module()


def _shell_script(mcp_obj: dict) -> str:
    assert mcp_obj["command"] == "sh"
    assert mcp_obj["args"][0] == "-c"
    return mcp_obj["args"][1]


def _assert_wrapper_present(shell_script: str) -> None:
    assert "set -a;" in shell_script
    assert "~/.codex/.env" in shell_script
    assert "~/dev/configs/.env" in shell_script
    assert "set +a" in shell_script


class TestBuildCodexMcpConfigStdio(unittest.TestCase):
    def _config(self, servers: dict) -> dict:
        return sync_mcp.build_codex_mcp_config({"mcp_servers": servers})

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
        obj = cfg["mcpServers"]["s"]
        script = _shell_script(obj)
        _assert_wrapper_present(script)
        self.assertIn('exec "$@"', script)
        self.assertEqual(obj["args"][2], "sync-mcp")
        self.assertEqual(obj["args"][3], "npx")
        self.assertIn("-y", obj["args"])
        self.assertIn("pkg@1.0", obj["args"])

    def test_disabled_server_is_excluded(self):
        cfg = self._config(
            {
                "active": {"command": "npx", "args": []},
                "inactive": {"command": "npx", "args": [], "enabled": False},
            }
        )
        self.assertIn("active", cfg["mcpServers"])
        self.assertNotIn("inactive", cfg["mcpServers"])

    def test_server_without_command_or_url_is_skipped(self):
        cfg = self._config({"ghost": {"foo": "bar"}})
        self.assertNotIn("ghost", cfg["mcpServers"])


class TestBuildCodexMcpConfigHttp(unittest.TestCase):
    def _config(self, server_cfg: dict) -> dict:
        return sync_mcp.build_codex_mcp_config({"mcp_servers": {"srv": server_cfg}})

    def test_http_server_uses_mcp_remote(self):
        cfg = self._config({"url": "https://example.com/mcp"})
        script = _shell_script(cfg["mcpServers"]["srv"])
        _assert_wrapper_present(script)
        self.assertIn("mcp-remote", script)
        self.assertIn("https://example.com/mcp", script)

    def test_bearer_token_env_var_added_as_auth_header(self):
        cfg = self._config({"url": "https://api.example.com/mcp", "bearer_token_env_var": "MY_TOKEN"})
        script = _shell_script(cfg["mcpServers"]["srv"])
        _assert_wrapper_present(script)
        self.assertIn("Authorization", script)
        self.assertIn("MY_TOKEN", script)

    def test_env_http_headers_added(self):
        cfg = self._config(
            {
                "url": "https://api.example.com/mcp",
                "env_http_headers": {"X-Api-Key": "SOME_KEY"},
            }
        )
        script = _shell_script(cfg["mcpServers"]["srv"])
        _assert_wrapper_present(script)
        self.assertIn("X-Api-Key", script)
        self.assertIn("SOME_KEY", script)

    def test_multiple_env_http_headers(self):
        cfg = self._config(
            {
                "url": "https://api.example.com/mcp",
                "env_http_headers": {"X-Key1": "K1", "X-Key2": "K2"},
            }
        )
        script = _shell_script(cfg["mcpServers"]["srv"])
        _assert_wrapper_present(script)
        self.assertIn("K1", script)
        self.assertIn("K2", script)


class TestBuildCodexMcpConfigOutput(unittest.TestCase):
    def test_output_has_mcp_servers_key(self):
        cfg = sync_mcp.build_codex_mcp_config({"mcp_servers": {}})
        self.assertIn("mcpServers", cfg)

    def test_empty_mcp_servers_produces_empty_output(self):
        cfg = sync_mcp.build_codex_mcp_config({})
        self.assertEqual(cfg["mcpServers"], {})


class TestMainMergeBehaviour(unittest.TestCase):
    def _run_main(self, tmp: Path, codex_toml: dict, existing_json: dict | None = None):
        config_path = tmp / "config.toml"
        output_path = tmp / "mcp_config.json"

        if existing_json is not None:
            output_path.write_text(json.dumps(existing_json), encoding="utf-8")

        with (
            patch.object(sync_mcp, "CODEX_CONFIG_PATH", str(config_path)),
            patch.object(sync_mcp, "CODEX_MCP_EXPORT_PATH", str(output_path)),
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
        with tempfile.TemporaryDirectory() as tmp:
            existing = {"mcpServers": {"stale-server": {"command": "old"}}}
            result = self._run_main(Path(tmp), {}, existing_json=existing)
            self.assertNotIn("stale-server", result["mcpServers"])

    def test_main_handles_corrupted_existing_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "mcp_config.json"
            output_path.write_text("{not valid json}", encoding="utf-8")
            config_path = Path(tmp) / "config.toml"
            with (
                patch.object(sync_mcp, "CODEX_CONFIG_PATH", str(config_path)),
                patch.object(sync_mcp, "CODEX_MCP_EXPORT_PATH", str(output_path)),
                patch.object(sync_mcp, "load_codex_config", return_value={}),
            ):
                sync_mcp.main()
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertIn("mcpServers", result)

    def test_main_server_count_matches_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            import io
            from contextlib import redirect_stdout

            buf = io.StringIO()
            with redirect_stdout(buf):
                result = self._run_main(
                    Path(tmp),
                    {
                        "mcp_servers": {
                            "server-a": {"command": "npx", "args": ["-y", "pkg-a"]},
                            "server-b": {"url": "https://b.example.com/mcp"},
                        }
                    },
                )
            output = buf.getvalue()
            expected_count = len(result["mcpServers"])
            self.assertIn(str(expected_count), output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
