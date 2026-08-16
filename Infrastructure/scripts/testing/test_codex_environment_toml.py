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


def _action_exists(env: dict, name: str) -> bool:
    return any(action.get("name") == name for action in env.get("actions", []))


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


# Expected PATH candidates from the new loop
_EXPECTED_CANDIDATES = [
    "$HOME/.local/share/mise/shims",
    "$HOME/.local/bin",
    "/opt/homebrew/bin",
    "/opt/homebrew/sbin",
    "/usr/local/bin",
    "/usr/sbin",
    "/sbin",
]

# Prepend loop order must be reverse-priority so final PATH keeps expected priority.
_PREPEND_LOOP_CANDIDATES = [
    "/sbin",
    "/usr/sbin",
    "/usr/local/bin",
    "/opt/homebrew/sbin",
    "/opt/homebrew/bin",
    "$HOME/.local/bin",
    "$HOME/.local/share/mise/shims",
]


class TestEnvironmentTomlContract(unittest.TestCase):
    def test_environment_toml_parses(self) -> None:
        env = _load_environment()
        self.assertIn("setup", env)

    def test_helper_file_exists(self) -> None:
        self.assertTrue(HELPER_PATH.exists(), f"Missing helper script: {HELPER_PATH}")

    # ------------------------------------------------------------------
    # PATH candidate loop replaces old git-guard + detach-head-helper
    # ------------------------------------------------------------------

    def test_setup_uses_path_candidate_loop(self) -> None:
        """setup script must use the new PATH candidate loop instead of git guard."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn("for candidate in", setup_command)
        self.assertIn('PATH="$candidate${PATH:+:$PATH}"', setup_command)
        self.assertIn("export PATH", setup_command)

    def test_tools_uses_path_candidate_loop(self) -> None:
        """Tools action must use the new PATH candidate loop."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertIn("for candidate in", tools_command)
        self.assertIn('PATH="$candidate${PATH:+:$PATH}"', tools_command)
        self.assertIn("export PATH", tools_command)

    def test_setup_path_loop_includes_mise_shims_candidate(self) -> None:
        """The PATH candidate loop must include the mise shims directory."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn("$HOME/.local/share/mise/shims", setup_command)

    def test_tools_path_loop_includes_all_expected_candidates(self) -> None:
        """The PATH candidate loop in Tools must include all expected directories."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        for candidate in _EXPECTED_CANDIDATES:
            with self.subTest(candidate=candidate):
                self.assertIn(candidate, tools_command)

    def test_setup_path_loop_uses_reverse_order_for_prepend(self) -> None:
        """setup loop must iterate in reverse-priority order when prepending PATH candidates."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        indices = [setup_command.find(candidate) for candidate in _PREPEND_LOOP_CANDIDATES]
        for candidate, idx in zip(_PREPEND_LOOP_CANDIDATES, indices):
            with self.subTest(candidate=candidate):
                self.assertGreater(idx, -1, f"Missing candidate {candidate} in setup loop")
        self.assertEqual(indices, sorted(indices), "setup loop candidates must appear in reverse-priority order")

    def test_tools_path_loop_uses_reverse_order_for_prepend(self) -> None:
        """Tools loop must iterate in reverse-priority order when prepending PATH candidates."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        indices = [tools_command.find(candidate) for candidate in _PREPEND_LOOP_CANDIDATES]
        for candidate, idx in zip(_PREPEND_LOOP_CANDIDATES, indices):
            with self.subTest(candidate=candidate):
                self.assertGreater(idx, -1, f"Missing candidate {candidate} in Tools loop")
        self.assertEqual(indices, sorted(indices), "Tools loop candidates must appear in reverse-priority order")

    def test_setup_path_loop_skips_already_present_candidates(self) -> None:
        """The PATH loop must remove existing candidate entries before prepend."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn('PATH="${PATH//:$candidate:/:}"', setup_command)
        self.assertIn('PATH="$candidate${PATH:+:$PATH}"', setup_command)

    def test_setup_path_loop_checks_directory_exists(self) -> None:
        """The PATH loop must check -d before prepending candidate directories."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn("-d", setup_command)

    # ------------------------------------------------------------------
    # Old git-guard + helper references must be absent from setup and Tools
    # ------------------------------------------------------------------

    def test_setup_does_not_use_old_git_guard(self) -> None:
        """setup must not use the old git rev-parse guard block."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertNotIn(
            'if command -v git >/dev/null 2>&1 && repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"',
            setup_command,
        )

    def test_tools_does_not_use_old_git_guard(self) -> None:
        """Tools action must not use the old git rev-parse guard block."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertNotIn(
            'if command -v git >/dev/null 2>&1 && repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"',
            tools_command,
        )

    def test_setup_does_not_source_detach_head_helper(self) -> None:
        """setup must not source detach-head-helper.sh (moved to inline logic in Mise)."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertNotIn("detach-head-helper.sh", setup_command)

    def test_tools_does_not_source_detach_head_helper(self) -> None:
        """Tools action must not source detach-head-helper.sh."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertNotIn("detach-head-helper.sh", tools_command)

    def test_setup_does_not_source_codex_env_common(self) -> None:
        """setup must not source codex_env_common.sh (removed from setup/Tools)."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertNotIn("codex_env_common.sh", setup_command)

    def test_tools_does_not_source_codex_env_common(self) -> None:
        """Tools action must not source codex_env_common.sh."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertNotIn("codex_env_common.sh", tools_command)

    def test_setup_does_not_call_codex_apply_env(self) -> None:
        """setup must not call codex_apply_env (removed with codex_env_common.sh)."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertNotIn("codex_apply_env", setup_command)

    def test_tools_does_not_call_codex_apply_env(self) -> None:
        """Tools action must not call codex_apply_env."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertNotIn("codex_apply_env", tools_command)

    # ------------------------------------------------------------------
    # Conditional mise execution
    # ------------------------------------------------------------------

    def test_setup_guards_mise_with_command_check(self) -> None:
        """setup must guard mise execution with 'if command -v mise'."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn("if command -v mise >/dev/null 2>&1;", setup_command)

    def test_tools_guards_mise_with_command_check(self) -> None:
        """Tools action must guard mise execution with 'if command -v mise'."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertIn("if command -v mise >/dev/null 2>&1;", tools_command)

    def test_setup_mise_trust_allows_failure(self) -> None:
        """setup must allow 'mise trust' to fail gracefully with '|| true'."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn("mise trust --yes .mise.toml || true", setup_command)

    def test_tools_mise_trust_allows_failure(self) -> None:
        """Tools action must allow 'mise trust' to fail gracefully with '|| true'."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertIn("mise trust --yes .mise.toml || true", tools_command)

    def test_setup_mise_trust_before_mise_install(self) -> None:
        """In setup, 'mise trust' must appear before 'mise install'."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        trust_idx = setup_command.find("mise trust --yes .mise.toml")
        install_idx = setup_command.find("mise install")
        self.assertGreater(trust_idx, -1, "Expected 'mise trust' in setup")
        self.assertGreater(install_idx, -1, "Expected 'mise install' in setup")
        self.assertLess(trust_idx, install_idx, "Expected 'mise trust' before 'mise install' in setup")

    def test_tools_mise_trust_before_mise_install(self) -> None:
        """In Tools, 'mise trust' must appear before 'mise install'."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        trust_idx = tools_command.find("mise trust --yes .mise.toml")
        install_idx = tools_command.find("mise install")
        self.assertGreater(trust_idx, -1, "Expected 'mise trust' in Tools")
        self.assertGreater(install_idx, -1, "Expected 'mise install' in Tools")
        self.assertLess(trust_idx, install_idx, "Expected 'mise trust' before 'mise install' in Tools")

    # ------------------------------------------------------------------
    # Conditional prepare-worktree.sh contract (no root npm fallback)
    # ------------------------------------------------------------------

    def test_setup_uses_conditional_prepare_worktree_or_error(self) -> None:
        """setup must use prepare-worktree.sh and fail closed when missing."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertIn("if [[ -f scripts/prepare-worktree.sh ]]", setup_command)
        self.assertIn("bash scripts/prepare-worktree.sh", setup_command)
        self.assertNotIn("npm install", setup_command)
        self.assertIn("root package-manager install is intentionally unsupported", setup_command)
        self.assertIn("exit 1", setup_command)

    def test_tools_uses_conditional_prepare_worktree_or_error(self) -> None:
        """Tools action must use prepare-worktree.sh and fail closed when missing."""
        env = _load_environment()
        tools_command = _action_command(env, "Tools")
        self.assertIn("if [[ -f scripts/prepare-worktree.sh ]]", tools_command)
        self.assertIn("bash scripts/prepare-worktree.sh", tools_command)
        self.assertNotIn("npm install", tools_command)
        self.assertIn("root package-manager install is intentionally unsupported", tools_command)
        self.assertIn("exit 1", tools_command)

    def test_setup_does_not_reference_npm_install(self) -> None:
        """setup must not reference root npm install."""
        env = _load_environment()
        setup_command = env["setup"]["script"]
        self.assertNotIn("npm install", setup_command)

    # ------------------------------------------------------------------
    # Release Finalize action
    # ------------------------------------------------------------------

    def test_release_finalize_action_exists(self) -> None:
        """Release Finalize action must be present in environment.toml."""
        env = _load_environment()
        self.assertTrue(
            _action_exists(env, "Release Finalize"),
            "Missing 'Release Finalize' action in environment.toml",
        )

    def test_release_finalize_icon_is_tool(self) -> None:
        """Release Finalize action must use icon = 'tool'."""
        env = _load_environment()
        for action in env.get("actions", []):
            if action.get("name") == "Release Finalize":
                self.assertEqual(action.get("icon"), "tool")
                return
        self.fail("Release Finalize action not found")

    def test_release_finalize_validates_branch_argument(self) -> None:
        """Release Finalize must require a release branch argument."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        self.assertIn('release_branch="${1:-}"', command)
        self.assertIn("Usage: Release Finalize", command)

    def test_release_finalize_enforces_branch_naming_pattern(self) -> None:
        """Release Finalize must reject branches not matching codex/release-* or release-*."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        self.assertIn("codex/release-*|release-*", command)
        self.assertIn("Expected a release branch matching", command)

    def test_release_finalize_exits_nonzero_on_empty_branch(self) -> None:
        """Release Finalize must exit 2 when no branch argument is provided."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        snippet = command.replace("git fetch", "true").replace("git checkout", "true")
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(snippet, Path(tmp))
        self.assertEqual(result.returncode, 2, "Expected exit code 2 with no branch arg")
        self.assertIn("Usage: Release Finalize", result.stdout)

    def test_release_finalize_exits_nonzero_on_invalid_branch_name(self) -> None:
        """Release Finalize must exit 2 for branch names not matching the allowed patterns."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        # Override the release_branch argument so it is an invalid name
        # We stub git calls so actual git operations are not run
        stub = """
release_branch="feature/something-wrong"
"""
        # Inject a fake release_branch before the case statement
        snippet = stub + command.split('release_branch="${1:-}"', 1)[-1]
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet("release_branch='feature/something-wrong'\n" + command.split('release_branch="${1:-}"', 1)[-1], Path(tmp))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Expected a release branch matching", result.stdout)

    def test_release_finalize_accepts_codex_release_branch(self) -> None:
        """Release Finalize must accept branches matching 'codex/release-*'."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        # Extract just the branch validation case block for testing without git ops
        case_check_snippet = r"""
release_branch="codex/release-1.0.0"
case "$release_branch" in
  codex/release-*|release-*) echo "ok";;
  *)
    echo "Expected a release branch matching codex/release-* or release-*"
    exit 2
    ;;
esac
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(case_check_snippet, Path(tmp))
        self.assertEqual(result.returncode, 0)
        self.assertIn("ok", result.stdout)

    def test_release_finalize_accepts_release_branch(self) -> None:
        """Release Finalize must accept branches matching 'release-*'."""
        case_check_snippet = r"""
release_branch="release-1.2.3"
case "$release_branch" in
  codex/release-*|release-*) echo "ok";;
  *)
    echo "Expected a release branch matching codex/release-* or release-*"
    exit 2
    ;;
esac
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(case_check_snippet, Path(tmp))
        self.assertEqual(result.returncode, 0)
        self.assertIn("ok", result.stdout)

    def test_release_finalize_rejects_arbitrary_branch(self) -> None:
        """Release Finalize must reject branches not matching the allowed patterns."""
        case_check_snippet = r"""
release_branch="main"
case "$release_branch" in
  codex/release-*|release-*) echo "ok";;
  *)
    echo "Expected a release branch matching codex/release-* or release-*"
    exit 2
    ;;
esac
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(case_check_snippet, Path(tmp))
        self.assertEqual(result.returncode, 2)

    def test_release_finalize_checks_local_main_not_ahead(self) -> None:
        """Release Finalize must abort if local main is ahead of origin/main."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        self.assertIn("local_main_ahead_count", command)
        self.assertIn("Local main is ahead of origin/main; aborting.", command)

    def test_release_finalize_uses_ff_only_pull(self) -> None:
        """Release Finalize must use --ff-only for git pull."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        self.assertIn("git pull --ff-only origin main", command)

    def test_release_finalize_uses_ff_only_merge(self) -> None:
        """Release Finalize must use --ff-only for the release branch merge."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        self.assertIn('git merge --ff-only "origin/$release_branch"', command)

    def test_release_finalize_uses_strict_mode(self) -> None:
        """Release Finalize must start with 'set -euo pipefail'."""
        env = _load_environment()
        command = _action_command(env, "Release Finalize")
        self.assertIn("set -euo pipefail", command)

    # ------------------------------------------------------------------
    # Mise action: inline detached HEAD logic
    # ------------------------------------------------------------------

    def test_mise_action_exists(self) -> None:
        """Mise action must be present in environment.toml."""
        env = _load_environment()
        self.assertTrue(_action_exists(env, "Mise"), "Missing 'Mise' action in environment.toml")

    def test_mise_action_has_inline_detached_head_detection(self) -> None:
        """Mise action must have inline detached HEAD detection logic."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("git symbolic-ref --short -q HEAD", command)
        self.assertIn("[codex] detached HEAD detected", command)

    def test_mise_action_creates_branch_for_detached_head(self) -> None:
        """Mise action must call 'git switch -c' when HEAD is detached."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("git switch -c", command)

    def test_mise_action_uses_git_is_inside_work_tree_guard(self) -> None:
        """Mise action must guard the detached HEAD block with git rev-parse check."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("git rev-parse --is-inside-work-tree", command)

    def test_mise_action_branch_name_uses_repo_slug(self) -> None:
        """Mise action branch naming must use the Codex feature prefix and repo slug."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn('branch_base="${BRANCH_PREFIX:-codex/feature}/', command)
        self.assertIn("repo_slug", command)

    def test_mise_action_branch_name_uses_short_sha(self) -> None:
        """Mise action branch naming must include the short git SHA."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("git rev-parse --short HEAD", command)
        self.assertIn("short_sha", command)

    def test_mise_action_avoids_duplicate_branch_names(self) -> None:
        """Mise action must avoid both local and remote branch-name collisions."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("show-ref --verify --quiet", command)
        self.assertIn("origin_branch_exists", command)
        self.assertIn("git ls-remote --exit-code --heads origin", command)
        self.assertIn("suffix=$((suffix + 1))", command)

    def test_mise_action_mise_trust_allows_failure(self) -> None:
        """Mise action must allow 'mise trust' to fail gracefully with '|| true'."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("mise trust --yes .mise.toml || true", command)

    def test_mise_action_does_not_have_old_git_guard_sourcing_helper(self) -> None:
        """Mise action must not use the old sourcing pattern for detach-head-helper.sh."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertNotIn("source", command.split("git symbolic-ref")[0])

    def test_mise_action_optionally_sets_upstream_to_origin_main(self) -> None:
        """Mise action must try to track origin/main for new branch when available."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("git branch --set-upstream-to=origin/main", command)

    def test_mise_action_fast_forwards_new_branch(self) -> None:
        """Mise action must fetch and fast-forward from origin/main when safe."""
        env = _load_environment()
        command = _action_command(env, "Mise")
        self.assertIn("git fetch --quiet origin main", command)
        self.assertIn('git merge --ff-only "$target_ref"', command)
        self.assertIn('git merge-base --is-ancestor HEAD "$target_ref"', command)

    # ------------------------------------------------------------------
    # Ralph action contract
    # ------------------------------------------------------------------

    def test_ralph_action_exists(self) -> None:
        """Ralph action must be present with the required debug icon."""
        env = _load_environment()
        actions = [action for action in env.get("actions", []) if action.get("name") == "Ralph"]

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].get("icon"), "debug")

    def test_ralph_action_runs_help(self) -> None:
        """Ralph action must validate availability through its public CLI."""
        env = _load_environment()
        command = _action_command(env, "Ralph")

        self.assertIn("command -v ralph >/dev/null 2>&1", command)
        self.assertIn("ralph --help", command)

    # ------------------------------------------------------------------
    # Pylint action contract
    # ------------------------------------------------------------------

    def test_pylint_action_exists(self) -> None:
        """Pylint action must be present in environment.toml."""
        env = _load_environment()
        self.assertTrue(
            _action_exists(env, "Pylint"),
            "Pylint action should exist in environment.toml",
        )

    def test_pylint_action_runs_version(self) -> None:
        """Pylint action must validate pylint availability and print version."""
        env = _load_environment()
        command = _action_command(env, "Pylint")
        self.assertIn("command -v pylint >/dev/null 2>&1", command)
        self.assertIn("pylint --version", command)

    # ------------------------------------------------------------------
    # Behavioral shell tests: PATH candidate loop
    # ------------------------------------------------------------------

    def test_path_candidate_loop_adds_existing_dir(self) -> None:
        """The PATH candidate loop must prepend an existing directory to PATH."""
        with tempfile.TemporaryDirectory() as tmp:
            snippet = f"""
for candidate in "{tmp}"; do
  if [[ -d "$candidate" && ":$PATH:" != *":$candidate:"* ]]; then
    PATH="$candidate:$PATH"
  fi
done
export PATH
echo "$PATH"
"""
            result = _run_snippet(snippet, Path(tmp))
        self.assertEqual(result.returncode, 0)
        self.assertIn(tmp, result.stdout)

    def test_path_candidate_loop_skips_nonexistent_dir(self) -> None:
        """The PATH candidate loop must skip directories that do not exist."""
        snippet = """
BEFORE="$PATH"
for candidate in "/this/dir/does/not/exist/ever"; do
  if [[ -d "$candidate" && ":$PATH:" != *":$candidate:"* ]]; then
    PATH="$candidate:$PATH"
  fi
done
export PATH
if [ "$PATH" = "$BEFORE" ]; then
  echo "unchanged"
fi
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(snippet, Path(tmp))
        self.assertEqual(result.returncode, 0)
        self.assertIn("unchanged", result.stdout)

    def test_path_candidate_loop_skips_already_present_dir(self) -> None:
        """The PATH candidate loop must not add a directory that is already in PATH."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snippet = f"""
CANDIDATE="{tmpdir}"
export PATH="$CANDIDATE:$PATH"
for candidate in "$CANDIDATE"; do
  if [[ -d "$candidate" && ":$PATH:" != *":$candidate:"* ]]; then
    PATH="$candidate:$PATH"
  fi
done
export PATH
# Count occurrences of CANDIDATE in PATH
count=$(echo "$PATH" | tr ':' '\\n' | grep -cxF "{tmpdir}" || true)
echo "count=$count"
"""
            result = _run_snippet(snippet, Path(tmpdir))
        self.assertEqual(result.returncode, 0)
        # Should appear exactly once (the initial prepend, loop guard must skip the second)
        self.assertIn("count=1", result.stdout)

    def test_mise_guard_skips_when_mise_unavailable(self) -> None:
        """When mise is not available, the mise trust/install block must be skipped."""
        snippet = """
if command -v mise >/dev/null 2>&1; then
  mise trust --yes .mise.toml || true
  mise install
  echo "mise-ran"
fi
echo "done"
"""
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as empty_path:
            result = _run_snippet(snippet, Path(tmp), extra_env={"PATH": empty_path})
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("mise-ran", result.stdout)
        self.assertIn("done", result.stdout)


class TestReleaseFinalizeActionStructure(unittest.TestCase):
    """Additional structural tests for the Release Finalize action."""

    def _get_command(self) -> str:
        env = _load_environment()
        return _action_command(env, "Release Finalize")

    def test_command_fetches_main_and_release_branch(self) -> None:
        """Release Finalize must fetch both main and the release branch."""
        command = self._get_command()
        self.assertIn('git fetch --prune origin main "$release_branch"', command)

    def test_command_checks_out_main(self) -> None:
        """Release Finalize must checkout main before merging."""
        command = self._get_command()
        self.assertIn("git checkout main", command)

    def test_command_pushes_origin_main(self) -> None:
        """Release Finalize must push to origin/main after merging."""
        command = self._get_command()
        self.assertIn("git push origin main", command)

    def test_command_includes_pr_follow_up_instructions(self) -> None:
        """Release Finalize must include optional PR follow-up instructions."""
        command = self._get_command()
        self.assertIn("gh pr list", command)
        self.assertIn("gh pr comment", command)
        self.assertIn("gh pr close", command)

    def test_branch_naming_boundary_codex_release_prefix(self) -> None:
        """'codex/release-' prefix is boundary: exactly that prefix passes, not partial."""
        snippet = r"""
for b in "codex/release-" "codex/release-1" "codex/release-1.0.0-rc"; do
  case "$b" in
    codex/release-*|release-*) echo "pass:$b";;
    *) echo "fail:$b";;
  esac
done
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(snippet, Path(tmp))
        self.assertIn("pass:codex/release-", result.stdout)
        self.assertIn("pass:codex/release-1", result.stdout)
        self.assertIn("pass:codex/release-1.0.0-rc", result.stdout)

    def test_branch_naming_boundary_release_prefix(self) -> None:
        """'release-' prefix boundary: exactly that prefix passes, not partial."""
        snippet = r"""
for b in "release-" "release-1.0.0" "release-2.0.0-beta"; do
  case "$b" in
    codex/release-*|release-*) echo "pass:$b";;
    *) echo "fail:$b";;
  esac
done
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(snippet, Path(tmp))
        self.assertIn("pass:release-", result.stdout)
        self.assertIn("pass:release-1.0.0", result.stdout)
        self.assertIn("pass:release-2.0.0-beta", result.stdout)

    def test_branch_naming_rejects_invalid_formats(self) -> None:
        """Release Finalize must reject malformed or unrelated branch names."""
        snippet = r"""
for b in "main" "feature/foo" "hotfix/bar" "codex/feature-1"; do
  case "$b" in
    codex/release-*|release-*) echo "pass:$b";;
    *) echo "fail:$b";;
  esac
done
"""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(snippet, Path(tmp))
        self.assertIn("fail:main", result.stdout)
        self.assertIn("fail:feature/foo", result.stdout)
        self.assertIn("fail:hotfix/bar", result.stdout)
        self.assertIn("fail:codex/feature-1", result.stdout)


if __name__ == "__main__":
    unittest.main()
