#!/usr/bin/env python3
"""Contract tests for .codex/environments/environment.toml."""

from __future__ import annotations

import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = REPO_ROOT / ".codex/environments/environment.toml"
HELPER_PATH = REPO_ROOT / ".codex/environments/detach-head-helper.sh"


def _load_environment() -> dict:
    with ENV_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _action_command(env: dict, name: str) -> str:
    for action in env.get("actions", []):
        if action.get("name") == name:
            return action.get("command", "")
    raise AssertionError(f"Missing action {name!r} in environment.toml")


def _run_snippet(snippet: str, cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["/bin/bash", "-euo", "pipefail", "-c", snippet],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class TestEnvironmentTomlContract(unittest.TestCase):
    def test_environment_toml_parses(self) -> None:
        env = _load_environment()
        self.assertIn("setup", env)

    def test_helper_file_exists(self) -> None:
        self.assertTrue(HELPER_PATH.exists(), f"Missing helper script: {HELPER_PATH}")

    def test_setup_tools_mise_use_guarded_helper(self) -> None:
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for command in (setup_command, tools_command, mise_command):
            self.assertIn(
                'if command -v git >/dev/null 2>&1 && repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then',
                command,
            )
            self.assertIn('source "$repo_root/.codex/environments/detach-head-helper.sh"', command)
            self.assertIn("codex_attach_detached_head", command)

    def test_setup_tools_mise_do_not_embed_old_inline_logic(self) -> None:
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for command in (setup_command, tools_command, mise_command):
            self.assertNotIn('current_branch="$(git symbolic-ref --short -q HEAD || true)"', command)
            self.assertNotIn("git pull --ff-only origin main", command)

    def test_mise_trust_contract_matches_current_behavior(self) -> None:
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for command in (setup_command, tools_command, mise_command):
            self.assertIn("mise trust --yes .mise.toml", command)
            self.assertNotIn("mise trust --yes .mise.toml || true", command)

    def test_guard_branch_skips_when_git_unavailable(self) -> None:
        guard_snippet = """
if command -v git >/dev/null 2>&1 && repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  source "$repo_root/.codex/environments/detach-head-helper.sh"
  codex_attach_detached_head
fi
"""
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as empty_path:
            result = _run_snippet(guard_snippet, Path(tmp), extra_env={"PATH": empty_path})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)


if __name__ == "__main__":
    unittest.main()
