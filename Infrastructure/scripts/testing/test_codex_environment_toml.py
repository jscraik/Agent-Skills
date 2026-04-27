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

            # Assert that "mise trust" appears before "mise install"
            trust_idx = command.find("mise trust --yes .mise.toml")
            install_idx = command.find("mise install")
            self.assertGreater(trust_idx, -1, "Expected 'mise trust --yes .mise.toml' in command")
            self.assertGreater(install_idx, -1, "Expected 'mise install' in command")
            self.assertLess(trust_idx, install_idx, "Expected 'mise trust' to appear before 'mise install'")

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

    # ------------------------------------------------------------------
    # New in this PR: codex_env_common.sh is sourced in setup/Tools/Mise
    # ------------------------------------------------------------------

    def test_setup_tools_mise_source_codex_env_common(self) -> None:
        """setup, Tools, and Mise actions must source codex_env_common.sh inside the git guard."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for label, command in (("setup", setup_command), ("Tools", tools_command), ("Mise", mise_command)):
            with self.subTest(action=label):
                self.assertIn(
                    'source "$repo_root/Infrastructure/scripts/codex-preflight/codex_env_common.sh"',
                    command,
                    f"Action {label!r} must source codex_env_common.sh",
                )

    def test_setup_tools_mise_call_codex_apply_env(self) -> None:
        """setup, Tools, and Mise actions must call codex_apply_env after sourcing the script."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for label, command in (("setup", setup_command), ("Tools", tools_command), ("Mise", mise_command)):
            with self.subTest(action=label):
                self.assertIn(
                    "codex_apply_env",
                    command,
                    f"Action {label!r} must call codex_apply_env",
                )

    def test_codex_env_common_sourced_after_detach_head_helper(self) -> None:
        """codex_env_common.sh must be sourced *after* detach-head-helper.sh in each guarded action."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for label, command in (("setup", setup_command), ("Tools", tools_command), ("Mise", mise_command)):
            with self.subTest(action=label):
                helper_idx = command.find("detach-head-helper.sh")
                common_idx = command.find("codex_env_common.sh")
                self.assertGreater(helper_idx, -1, f"Action {label!r} must source detach-head-helper.sh")
                self.assertGreater(common_idx, -1, f"Action {label!r} must source codex_env_common.sh")
                self.assertLess(
                    helper_idx,
                    common_idx,
                    f"Action {label!r}: detach-head-helper.sh must come before codex_env_common.sh",
                )

    def test_codex_apply_env_called_after_source_in_each_action(self) -> None:
        """codex_apply_env must be called after the codex_env_common.sh source line in each action."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        for label, command in (("setup", setup_command), ("Tools", tools_command), ("Mise", mise_command)):
            with self.subTest(action=label):
                source_idx = command.find("codex_env_common.sh")
                apply_idx = command.find("codex_apply_env")
                self.assertGreater(source_idx, -1, f"Action {label!r} must source codex_env_common.sh")
                self.assertGreater(apply_idx, -1, f"Action {label!r} must call codex_apply_env")
                self.assertLess(
                    source_idx,
                    apply_idx,
                    f"Action {label!r}: codex_env_common.sh source must precede codex_apply_env call",
                )

    def test_codex_env_common_path_uses_infrastructure_scripts_codex_preflight(self) -> None:
        """The sourced codex_env_common.sh path must use the canonical Infrastructure/ prefix."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        tools_command = _action_command(env, "Tools")
        mise_command = _action_command(env, "Mise")

        canonical_fragment = "Infrastructure/scripts/codex-preflight/codex_env_common.sh"
        for label, command in (("setup", setup_command), ("Tools", tools_command), ("Mise", mise_command)):
            with self.subTest(action=label):
                self.assertIn(
                    canonical_fragment,
                    command,
                    f"Action {label!r} must use canonical codex_env_common.sh path",
                )

    def test_codex_env_common_file_exists_at_sourced_path(self) -> None:
        """The codex_env_common.sh script referenced in environment.toml must exist on disk."""
        codex_env_common = REPO_ROOT / "Infrastructure" / "scripts" / "codex-preflight" / "codex_env_common.sh"
        self.assertTrue(
            codex_env_common.exists(),
            f"codex_env_common.sh not found at expected path: {codex_env_common}",
        )


if __name__ == "__main__":
    unittest.main()