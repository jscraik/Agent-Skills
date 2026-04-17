#!/usr/bin/env python3
"""Tests for .codex/environments/environment.toml shell script changes.

Covers the detached-HEAD branch-creation logic added in this PR to the
setup script, Tools action, and Mise action:

- Skips branch creation when not inside a git work-tree
- Skips branch creation when git is not available
- Skips branch creation when already on a named branch
- Creates a branch in the form "codex/<slug>-worktree-<sha>" on detached HEAD
- repo_slug normalization: uppercase → lowercase
- repo_slug normalization: special characters → dashes, no leading/trailing dashes
- repo_slug fallback to "worktree" when basename normalises to empty string
- Branch-name collision: increments suffix until a free name is found
- Sets upstream to origin/main when refs/remotes/origin/main exists
- Skips upstream configuration when origin/main is not present
- Outputs expected "[codex] ..." diagnostic messages
- mise trust --yes .mise.toml is called (with || true so absence is non-fatal)
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# ---------------------------------------------------------------------------
# The core shell logic extracted from environment.toml (the new block).
# We test this snippet directly, calling it from a bash -c invocation so
# we can fully control the git environment.
# ---------------------------------------------------------------------------
DETACHED_HEAD_SNIPPET = textwrap.dedent("""\
    if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      current_branch="$(git symbolic-ref --short -q HEAD || true)"
      if [ -z "$current_branch" ]; then
        repo_slug="$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
        if [ -z "$repo_slug" ]; then
          repo_slug="worktree"
        fi
        short_sha="$(git rev-parse --short HEAD)"
        branch_base="codex/$repo_slug-worktree-$short_sha"
        branch_name="$branch_base"
        suffix=1
        while git show-ref --verify --quiet "refs/heads/$branch_name"; do
          branch_name="$branch_base-$suffix"
          suffix=$((suffix + 1))
        done
        echo "[codex] detached HEAD detected; creating branch $branch_name"
        git switch -c "$branch_name"
        if git show-ref --verify --quiet "refs/remotes/origin/main"; then
          git branch --set-upstream-to=origin/main "$branch_name" >/dev/null 2>&1 || true
          echo "[codex] tracking origin/main for $branch_name"
          echo "[codex] fast-forwarding $branch_name with origin/main"
          git pull --ff-only origin main
        fi
      fi
    fi
""")

# Same snippet but guarded only by git rev-parse (no `command -v git` check),
# as used in the Mise action which already asserts mise is present first.
DETACHED_HEAD_SNIPPET_MISE = textwrap.dedent("""\
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      current_branch="$(git symbolic-ref --short -q HEAD || true)"
      if [ -z "$current_branch" ]; then
        repo_slug="$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
        if [ -z "$repo_slug" ]; then
          repo_slug="worktree"
        fi
        short_sha="$(git rev-parse --short HEAD)"
        branch_base="codex/$repo_slug-worktree-$short_sha"
        branch_name="$branch_base"
        suffix=1
        while git show-ref --verify --quiet "refs/heads/$branch_name"; do
          branch_name="$branch_base-$suffix"
          suffix=$((suffix + 1))
        done
        echo "[codex] detached HEAD detected; creating branch $branch_name"
        git switch -c "$branch_name"
        if git show-ref --verify --quiet "refs/remotes/origin/main"; then
          git branch --set-upstream-to=origin/main "$branch_name" >/dev/null 2>&1 || true
          echo "[codex] tracking origin/main for $branch_name"
          echo "[codex] fast-forwarding $branch_name with origin/main"
          git pull --ff-only origin main
        fi
      fi
    fi
""")


def _bash(snippet: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a bash snippet, capturing stdout/stderr."""
    env = {k: v for k, v in os.environ.items()}
    # Ensure a clean, predictable git identity so commits work in temp repos.
    env.setdefault("GIT_AUTHOR_NAME", "Test")
    env.setdefault("GIT_AUTHOR_EMAIL", "test@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "Test")
    env.setdefault("GIT_COMMITTER_EMAIL", "test@example.com")
    return subprocess.run(
        ["bash", "-euo", "pipefail", "-c", snippet],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )


def _create_repo_with_commit(repo_dir: str) -> str:
    """Initialise a git repo in repo_dir, make one commit, return its short SHA."""
    cmds = [
        "git init -b main",
        "git config user.email test@example.com",
        "git config user.name Test",
        "touch .gitkeep && git add .gitkeep",
        "git commit -m init",
    ]
    for cmd in cmds:
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            cwd=repo_dir,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Setup command failed: {cmd!r}\n{result.stderr}")
    sha_result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd=repo_dir,
    )
    return sha_result.stdout.strip()


def _detach_head(repo_dir: str) -> None:
    """Detach HEAD at the current commit."""
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=repo_dir,
    ).stdout.strip()
    subprocess.run(
        ["git", "checkout", "--detach", sha],
        capture_output=True,
        text=True,
        cwd=repo_dir,
    )


def _run_snippet(snippet: str, cwd: str) -> subprocess.CompletedProcess:
    """Run the given shell snippet with set -euo pipefail in cwd."""
    return _bash(snippet, cwd=cwd)


# ---------------------------------------------------------------------------
# Tests: skip conditions (no git / not in repo / named branch)
# ---------------------------------------------------------------------------


class TestDetachedHeadSkipConditions(unittest.TestCase):
    """Snippet must be a no-op when preconditions are not met."""

    def test_skips_when_not_in_git_repo(self) -> None:
        """No branch creation outside a git work-tree."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_skips_when_git_not_available(self) -> None:
        """If git is not on PATH the outer guard skips the block silently."""
        with tempfile.TemporaryDirectory() as tmp:
            # Provide a PATH that contains no git binary.
            env = {k: v for k, v in os.environ.items()}
            env["PATH"] = "/usr/bin:/bin"
            result = subprocess.run(
                ["bash", "-euo", "pipefail", "-c", DETACHED_HEAD_SNIPPET],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_skips_on_named_branch(self) -> None:
        """When HEAD points to a named branch, no new branch is created."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            # HEAD is already on 'main' – not detached.
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex] detached HEAD detected", result.stdout)

    def test_skips_on_named_branch_non_main(self) -> None:
        """On a feature branch (named), the snippet does nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            subprocess.run(
                ["git", "switch", "-c", "feature/foo"],
                capture_output=True,
                cwd=tmp,
            )
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)


# ---------------------------------------------------------------------------
# Tests: branch creation in detached HEAD state
# ---------------------------------------------------------------------------


class TestDetachedHeadBranchCreation(unittest.TestCase):
    """Core branch-creation logic executed when HEAD is detached."""

    def test_creates_branch_on_detached_head(self) -> None:
        """A new branch is created when HEAD is detached."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] detached HEAD detected", result.stdout)

    def test_branch_name_format(self) -> None:
        """Created branch follows codex/<slug>-worktree-<sha> pattern."""
        with tempfile.TemporaryDirectory(prefix="my-repo-") as tmp:
            short_sha = _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            # Extract the branch name from the output
            branch_line = next(
                (l for l in result.stdout.splitlines() if "detached HEAD detected" in l),
                "",
            )
            self.assertIn(f"worktree-{short_sha}", branch_line)
            self.assertTrue(branch_line.startswith("[codex] detached HEAD detected; creating branch codex/"))

    def test_branch_actually_exists_after_creation(self) -> None:
        """After the snippet runs, the new branch must exist in the repo."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            # git branch should now list a codex/... branch
            br_result = subprocess.run(
                ["git", "branch", "--list", "codex/*"],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertTrue(br_result.stdout.strip(), "No codex/* branch found after snippet run")

    def test_head_is_on_new_branch_after_creation(self) -> None:
        """After branch creation, HEAD must be on the newly created branch."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            current = subprocess.run(
                ["git", "symbolic-ref", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=tmp,
            ).stdout.strip()
            self.assertTrue(current.startswith("codex/"), f"Expected codex/ branch, got: {current!r}")


# ---------------------------------------------------------------------------
# Tests: repo_slug normalisation
# ---------------------------------------------------------------------------


class TestRepoSlugNormalisation(unittest.TestCase):
    """repo_slug derived from basename(PWD) must be normalised correctly."""

    def _slug_for_dirname(self, dirname: str) -> str:
        """Return the slug the snippet would compute for a directory named dirname."""
        snippet = (
            f'repo_slug="$(echo "{dirname}" | tr \'[:upper:]\' \'[:lower:]\' | '
            "sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')\";"
            'printf "%s" "$repo_slug"'
        )
        result = _bash(snippet)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_lowercase_conversion(self) -> None:
        """Uppercase letters in dirname must be lowercased."""
        slug = self._slug_for_dirname("MyRepo")
        self.assertEqual(slug, "myrepo")

    def test_special_chars_to_dashes(self) -> None:
        """Non-alphanumeric characters must be replaced with dashes."""
        slug = self._slug_for_dirname("my_repo.name")
        self.assertEqual(slug, "my-repo-name")

    def test_leading_dashes_removed(self) -> None:
        """Leading dashes in the slug must be stripped."""
        slug = self._slug_for_dirname("---myrepo")
        self.assertEqual(slug, "myrepo")

    def test_trailing_dashes_removed(self) -> None:
        """Trailing dashes in the slug must be stripped."""
        slug = self._slug_for_dirname("myrepo---")
        self.assertEqual(slug, "myrepo")

    def test_consecutive_special_chars_become_single_dash(self) -> None:
        """Multiple consecutive non-alphanumeric chars become a single dash."""
        slug = self._slug_for_dirname("my___repo")
        self.assertEqual(slug, "my-repo")

    def test_mixed_case_and_special_chars(self) -> None:
        """Combined uppercase and special chars are handled together."""
        slug = self._slug_for_dirname("My-Awesome_Repo!")
        self.assertNotIn(" ", slug)
        self.assertNotIn("_", slug)
        self.assertNotIn("!", slug)
        self.assertFalse(slug.startswith("-"))
        self.assertFalse(slug.endswith("-"))
        self.assertEqual(slug, slug.lower())

    def test_fallback_to_worktree_when_slug_empty(self) -> None:
        """When normalisation yields an empty string, slug must fall back to 'worktree'."""
        # A name consisting solely of non-alphanumeric characters normalises to empty.
        snippet = (
            'dirname="---"; '
            'repo_slug="$(echo "$dirname" | tr \'[:upper:]\' \'[:lower:]\' | '
            "sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')\";"
            'if [ -z "$repo_slug" ]; then repo_slug="worktree"; fi; '
            'printf "%s" "$repo_slug"'
        )
        result = _bash(snippet)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "worktree")

    def test_branch_name_uses_normalised_slug(self) -> None:
        """The created branch name uses the normalised repo_slug."""
        with tempfile.TemporaryDirectory(prefix="My_Repo-") as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            current = subprocess.run(
                ["git", "symbolic-ref", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=tmp,
            ).stdout.strip()
            # Branch name must be all lowercase with no underscores or uppercase
            branch_suffix = current.replace("codex/", "", 1)
            self.assertEqual(branch_suffix, branch_suffix.lower())
            self.assertNotIn("_", branch_suffix)


# ---------------------------------------------------------------------------
# Tests: branch-name collision / suffix increment
# ---------------------------------------------------------------------------


class TestBranchNameCollision(unittest.TestCase):
    """When the base branch name already exists, a numeric suffix is appended."""

    def _get_current_branch(self, repo_dir: str) -> str:
        return subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_dir,
        ).stdout.strip()

    def test_suffix_appended_on_collision(self) -> None:
        """If codex/<slug>-worktree-<sha> already exists, a -1 suffix is used."""
        with tempfile.TemporaryDirectory() as tmp:
            short_sha = _create_repo_with_commit(tmp)
            slug = Path(tmp).name.lower()
            slug = subprocess.run(
                ["bash", "-c",
                 f'echo "{slug}" | tr \'[:upper:]\' \'[:lower:]\' | '
                 "sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'"],
                capture_output=True,
                text=True,
            ).stdout.strip()
            base_name = f"codex/{slug}-worktree-{short_sha}"
            # Pre-create the base branch name so a collision is forced.
            subprocess.run(
                ["git", "branch", base_name],
                capture_output=True,
                cwd=tmp,
            )
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            current = self._get_current_branch(tmp)
            self.assertTrue(
                current.endswith("-1"),
                f"Expected branch with -1 suffix, got: {current!r}",
            )

    def test_suffix_increments_past_multiple_collisions(self) -> None:
        """Suffix keeps incrementing until a free branch name is found."""
        with tempfile.TemporaryDirectory() as tmp:
            short_sha = _create_repo_with_commit(tmp)
            slug = Path(tmp).name.lower()
            slug = subprocess.run(
                ["bash", "-c",
                 f'echo "{slug}" | tr \'[:upper:]\' \'[:lower:]\' | '
                 "sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'"],
                capture_output=True,
                text=True,
            ).stdout.strip()
            base_name = f"codex/{slug}-worktree-{short_sha}"
            # Pre-create base and -1 variants.
            subprocess.run(["git", "branch", base_name], capture_output=True, cwd=tmp)
            subprocess.run(["git", "branch", f"{base_name}-1"], capture_output=True, cwd=tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            current = self._get_current_branch(tmp)
            self.assertTrue(
                current.endswith("-2"),
                f"Expected branch with -2 suffix, got: {current!r}",
            )

    def test_no_collision_uses_base_name(self) -> None:
        """When no collision exists, branch name is exactly codex/<slug>-worktree-<sha>."""
        with tempfile.TemporaryDirectory() as tmp:
            short_sha = _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            current = self._get_current_branch(tmp)
            self.assertTrue(
                current.startswith("codex/") and current.endswith(f"-worktree-{short_sha}"),
                f"Unexpected branch name: {current!r}",
            )


# ---------------------------------------------------------------------------
# Tests: origin/main upstream configuration
# ---------------------------------------------------------------------------


class TestOriginMainUpstream(unittest.TestCase):
    """Upstream tracking is set iff refs/remotes/origin/main exists."""

    def _setup_remote_with_main(self, tmp: str) -> str:
        """Create a remote repo with a 'main' branch and a clone of it.

        Returns the clone directory. The clone has HEAD detached at the tip of
        origin/main so the snippet can exercise the upstream-configuration path.
        """
        remote_dir = os.path.join(tmp, "remote")
        clone_dir = os.path.join(tmp, "clone")
        os.makedirs(remote_dir)
        env = {k: v for k, v in os.environ.items()}
        env.update({
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        })

        def _run(cmd: str, cwd: str | None = None) -> None:
            r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                               cwd=cwd, env=env)
            if r.returncode != 0:
                raise RuntimeError(f"Remote setup failed: {cmd!r}\n{r.stderr}")

        # Build a remote repo with a commit on 'main'.
        _run("git init -b main", cwd=remote_dir)
        _run("git config user.email test@example.com", cwd=remote_dir)
        _run("git config user.name Test", cwd=remote_dir)
        _run("touch .gitkeep && git add .gitkeep && git commit -m init", cwd=remote_dir)

        # Clone the remote repo.
        _run(f"git clone {remote_dir} {clone_dir}")
        _run("git config user.email test@example.com", cwd=clone_dir)
        _run("git config user.name Test", cwd=clone_dir)

        # Verify origin/main ref exists in the clone.
        check = subprocess.run(
            ["git", "show-ref", "--verify", "refs/remotes/origin/main"],
            capture_output=True, text=True, cwd=clone_dir,
        )
        if check.returncode != 0:
            raise RuntimeError("refs/remotes/origin/main not found after clone")

        # Detach HEAD at the tip of origin/main.
        sha_r = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            capture_output=True, text=True, cwd=clone_dir,
        )
        sha = sha_r.stdout.strip()
        _run(f"git checkout --detach {sha}", cwd=clone_dir)

        return clone_dir

    def test_sets_upstream_when_origin_main_exists(self) -> None:
        """When origin/main is reachable, upstream is configured and output emitted."""
        with tempfile.TemporaryDirectory() as tmp:
            # _setup_remote_with_main leaves HEAD detached at origin/main's tip.
            clone_dir = self._setup_remote_with_main(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=clone_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] tracking origin/main", result.stdout)
            self.assertIn("[codex] fast-forwarding", result.stdout)

    def test_skips_upstream_when_origin_main_absent(self) -> None:
        """When there is no origin/main remote ref, upstream config is skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex] tracking origin/main", result.stdout)
            self.assertNotIn("[codex] fast-forwarding", result.stdout)


# ---------------------------------------------------------------------------
# Tests: diagnostic output messages
# ---------------------------------------------------------------------------


class TestDiagnosticOutput(unittest.TestCase):
    """Verify expected [codex] output messages are produced."""

    def test_detached_head_message_contains_branch_name(self) -> None:
        """The diagnostic message must include the full branch name."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            detected_lines = [l for l in lines if "detached HEAD detected" in l]
            self.assertTrue(detected_lines, "Expected '[codex] detached HEAD detected' message")
            self.assertRegex(detected_lines[0], r"creating branch codex/.+-worktree-[0-9a-f]+")

    def test_no_output_when_on_named_branch(self) -> None:
        """No [codex] output when HEAD is on a named branch."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "")


# ---------------------------------------------------------------------------
# Tests: mise trust line (new addition)
# ---------------------------------------------------------------------------


class TestMiseTrustLine(unittest.TestCase):
    """The `mise trust --yes .mise.toml || true` line must be non-fatal."""

    def test_mise_trust_with_missing_mise_does_not_fail(self) -> None:
        """mise trust with || true must not abort the script even if mise is absent."""
        snippet = "mise trust --yes .mise.toml || true"
        env = {k: v for k, v in os.environ.items()}
        # Replace PATH with one that has no mise binary.
        env["PATH"] = "/usr/bin:/bin"
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", snippet],
            capture_output=True,
            text=True,
            env=env,
            cwd="/tmp",
        )
        self.assertEqual(result.returncode, 0, f"mise trust should not abort: {result.stderr}")

    def test_mise_trust_with_missing_toml_does_not_fail(self) -> None:
        """mise trust on non-existent .mise.toml must not abort due to || true."""
        with tempfile.TemporaryDirectory() as tmp:
            # No .mise.toml in tmp — if mise is present it will fail, but || true catches it.
            snippet = "mise trust --yes .mise.toml || true"
            result = subprocess.run(
                ["bash", "-euo", "pipefail", "-c", snippet],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 0, f"Unexpected failure: {result.stderr}")


# ---------------------------------------------------------------------------
# Tests: Mise-action variant (no `command -v git` outer guard)
# ---------------------------------------------------------------------------


class TestMiseActionVariant(unittest.TestCase):
    """The Mise action uses a slightly different guard (no `command -v git` check)."""

    def test_mise_variant_skips_when_not_in_repo(self) -> None:
        """The Mise-action snippet must be a no-op outside a git repo."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(DETACHED_HEAD_SNIPPET_MISE, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_mise_variant_creates_branch_on_detached_head(self) -> None:
        """The Mise-action variant also creates a branch on detached HEAD."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET_MISE, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] detached HEAD detected", result.stdout)

    def test_mise_variant_skips_on_named_branch(self) -> None:
        """The Mise-action variant is also a no-op on named branches."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            result = _run_snippet(DETACHED_HEAD_SNIPPET_MISE, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)


# ---------------------------------------------------------------------------
# Regression: idempotency — running snippet twice is harmless
# ---------------------------------------------------------------------------


class TestIdempotency(unittest.TestCase):
    """Running the snippet a second time on the same repo must not error."""

    def test_second_run_on_named_branch_is_noop(self) -> None:
        """After first run creates a branch, a second run finds a named branch → no-op."""
        with tempfile.TemporaryDirectory() as tmp:
            _create_repo_with_commit(tmp)
            _detach_head(tmp)
            # First run: creates branch, HEAD is now named.
            r1 = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(r1.returncode, 0, r1.stderr)
            # Second run: HEAD is now on a named branch → snippet does nothing.
            r2 = _run_snippet(DETACHED_HEAD_SNIPPET, cwd=tmp)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            self.assertNotIn("[codex] detached HEAD detected", r2.stdout)


if __name__ == "__main__":
    unittest.main()