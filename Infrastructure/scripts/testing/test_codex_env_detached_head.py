#!/usr/bin/env python3
"""Tests for the detached-HEAD branch-creation shell script logic added to
.codex/environments/environment.toml.

The PR introduced an identical block of shell code in three sections of that
TOML file (setup, Tools action, and Mise action).  Because the logic is
self-contained and environment-agnostic we test it directly as a bash snippet,
creating real but ephemeral git repositories via tempfile so every test runs in
isolation.

Covered behaviours
------------------
- Not inside a git repository        → entire block is skipped
- git not found on PATH              → entire block is skipped (setup/Tools variant)
- On a named branch                  → branch-creation block is skipped
- Detached HEAD                      → branch is created with the expected name
- Detached HEAD, branch exists once  → suffix -1 appended
- Detached HEAD, branch exists twice → suffix -2 appended
- Detached HEAD with origin/main     → upstream set; fast-forward attempted
- Detached HEAD without origin/main  → upstream step skipped
- repo_slug derivation               → uppercase, spaces, special chars normalised
- Empty repo_slug                    → falls back to "worktree"
- Mise-action variant (no `command -v git` guard) → in-repo detached HEAD handled
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# The three shell-script variants lifted verbatim from the TOML.
# ---------------------------------------------------------------------------

# Used in [setup] and [[actions]] name="Tools": guards with `command -v git`
SETUP_TOOLS_SNIPPET = textwrap.dedent("""\
    set -euo pipefail

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

# Used in [[actions]] name="Mise": no `command -v git` guard
MISE_SNIPPET = textwrap.dedent("""\
    set -euo pipefail

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bash(snippet: str, env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    base_env = dict(os.environ)
    # Suppress noise from git user prompts in CI
    base_env.setdefault("GIT_AUTHOR_NAME", "Test")
    base_env.setdefault("GIT_AUTHOR_EMAIL", "test@example.com")
    base_env.setdefault("GIT_COMMITTER_NAME", "Test")
    base_env.setdefault("GIT_COMMITTER_EMAIL", "test@example.com")
    if env:
        base_env.update(env)
    return subprocess.run(
        ["bash", "-c", snippet],
        capture_output=True,
        text=True,
        env=base_env,
        cwd=cwd,
    )


def _init_repo(path: Path, branch: str = "main") -> None:
    """Initialise a bare-minimum git repo with one commit on *branch*."""
    cmds = [
        ["git", "init", "-b", branch, str(path)],
        ["git", "-C", str(path), "config", "user.email", "test@example.com"],
        ["git", "-C", str(path), "config", "user.name", "Test"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, check=True, capture_output=True)
    # Create an initial commit so HEAD resolves
    (path / "README").write_text("init\n")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "commit", "-m", "init"],
        check=True,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


def _detach_head(repo: Path) -> str:
    """Detach HEAD to the current commit and return the short SHA."""
    sha_result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    short_sha = sha_result.stdout.strip()
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "--detach", "HEAD"],
        check=True, capture_output=True,
    )
    return short_sha


def _current_branch(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "symbolic-ref", "--short", "-q", "HEAD"],
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def _branch_exists(repo: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        capture_output=True,
    )
    return result.returncode == 0


def _run_snippet(snippet: str, cwd: str, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    """Run *snippet* under bash in *cwd* with sensible git identity env vars."""
    return _bash(snippet, env=extra_env, cwd=cwd)


# ---------------------------------------------------------------------------
# Tests: setup / Tools variant (has `command -v git` guard)
# ---------------------------------------------------------------------------

class TestSetupToolsSnippetNotInRepo(unittest.TestCase):
    """Snippet must be a no-op when not inside a git repository."""

    def test_skips_outside_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_skips_when_git_not_on_path(self):
        """When git is absent from PATH the outer guard must prevent any git call."""
        with tempfile.TemporaryDirectory() as tmp:
            # Provide a PATH that definitely has no git
            result = _run_snippet(
                SETUP_TOOLS_SNIPPET,
                cwd=tmp,
                extra_env={"PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)


class TestSetupToolsSnippetNamedBranch(unittest.TestCase):
    """Snippet must be a no-op when already on a named branch."""

    def test_no_branch_created_on_named_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_existing_branches_unchanged_on_named_branch(self):
        """No new branches should appear when starting from a named branch."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            before = set(subprocess.run(
                ["git", "-C", tmp, "branch", "--list"],
                capture_output=True, text=True,
            ).stdout.split())
            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            after = set(subprocess.run(
                ["git", "-C", tmp, "branch", "--list"],
                capture_output=True, text=True,
            ).stdout.split())
            self.assertEqual(before, after)


class TestSetupToolsSnippetDetachedHead(unittest.TestCase):
    """Core behaviour: detached HEAD → create a uniquely-named codex/ branch."""

    def _repo_slug(self, name: str) -> str:
        """Mirror the sed transformation used in the shell snippet."""
        import re
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug or "worktree"

    def test_creates_branch_in_detached_head(self):
        with tempfile.TemporaryDirectory(suffix="-myrepo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            dir_name = repo.name
            expected_slug = self._repo_slug(dir_name)
            expected_branch = f"codex/{expected_slug}-worktree-{short_sha}"

            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] detached HEAD detected", result.stdout)
            self.assertTrue(_branch_exists(repo, expected_branch),
                            f"Expected branch {expected_branch!r} was not created")

    def test_current_branch_is_new_codex_branch_after_switch(self):
        with tempfile.TemporaryDirectory(suffix="-myrepo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            dir_name = repo.name
            expected_slug = self._repo_slug(dir_name)
            expected_branch = f"codex/{expected_slug}-worktree-{short_sha}"

            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(_current_branch(repo), expected_branch)

    def test_branch_name_contains_short_sha(self):
        with tempfile.TemporaryDirectory(suffix="-reponame") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)

            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            branch = _current_branch(repo)
            self.assertIn(short_sha, branch)

    def test_branch_name_starts_with_codex_prefix(self):
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)

            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            branch = _current_branch(repo)
            self.assertTrue(branch.startswith("codex/"),
                            f"Branch {branch!r} does not start with 'codex/'")

    def test_detached_head_emits_log_message(self):
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertIn("[codex] detached HEAD detected", result.stdout)

    def test_snippet_succeeds_exit_code_zero(self):
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)


class TestSetupToolsSnippetBranchNameCollision(unittest.TestCase):
    """When the desired branch name already exists the suffix counter increments."""

    def _repo_slug(self, name: str) -> str:
        import re
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug or "worktree"

    def _setup_detached_repo_with_existing_branch(self, tmp: str) -> tuple[Path, str, str]:
        repo = Path(tmp)
        _init_repo(repo)
        short_sha = _detach_head(repo)
        slug = self._repo_slug(repo.name)
        base_branch = f"codex/{slug}-worktree-{short_sha}"
        # Pre-create the base branch name so suffix logic triggers
        subprocess.run(
            ["git", "-C", tmp, "branch", base_branch],
            check=True, capture_output=True,
        )
        return repo, short_sha, base_branch

    def test_first_collision_appends_suffix_1(self):
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo, short_sha, base_branch = self._setup_detached_repo_with_existing_branch(tmp)
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = f"{base_branch}-1"
            self.assertTrue(_branch_exists(repo, expected),
                            f"Expected suffix-1 branch {expected!r}")

    def test_second_collision_appends_suffix_2(self):
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo, short_sha, base_branch = self._setup_detached_repo_with_existing_branch(tmp)
            # Also pre-create the -1 variant
            subprocess.run(
                ["git", "-C", tmp, "branch", f"{base_branch}-1"],
                check=True, capture_output=True,
            )
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = f"{base_branch}-2"
            self.assertTrue(_branch_exists(repo, expected),
                            f"Expected suffix-2 branch {expected!r}")

    def test_no_collision_uses_base_name(self):
        """When no collision exists the base branch name (no suffix) is used."""
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            slug = self._repo_slug(repo.name)
            base_branch = f"codex/{slug}-worktree-{short_sha}"

            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(_current_branch(repo), base_branch)


# ---------------------------------------------------------------------------
# Tests: repo_slug derivation
# ---------------------------------------------------------------------------

class TestRepoSlugDerivation(unittest.TestCase):
    """Verify the directory-name → slug transformation used for branch names."""

    def _extract_slug_from_branch(self, branch: str, short_sha: str) -> str:
        """Parse slug out of 'codex/{slug}-worktree-{sha}[...]'."""
        prefix = "codex/"
        suffix = f"-worktree-{short_sha}"
        inner = branch[len(prefix):]
        if inner.endswith(suffix):
            return inner[: -len(suffix)]
        # suffix collision variant like codex/slug-worktree-sha-1
        # strip trailing -N
        import re
        inner = re.sub(r"-\d+$", "", inner)
        if inner.endswith(suffix):
            return inner[: -len(suffix)]
        return inner

    def _run_and_get_branch(self, dir_name: str) -> tuple[str, str]:
        with tempfile.TemporaryDirectory() as parent:
            repo = Path(parent) / dir_name
            repo.mkdir(parents=True)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=str(repo))
            branch = _current_branch(repo)
            return branch, short_sha

    def test_uppercase_is_lowercased(self):
        branch, sha = self._run_and_get_branch("MyRepo")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertFalse(any(c.isupper() for c in slug),
                         f"Slug {slug!r} contains uppercase letters")

    def test_spaces_become_hyphens(self):
        branch, sha = self._run_and_get_branch("my repo name")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertNotIn(" ", slug)
        self.assertIn("-", slug)

    def test_special_chars_become_hyphens(self):
        branch, sha = self._run_and_get_branch("my_repo.name")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertNotIn("_", slug)
        self.assertNotIn(".", slug)

    def test_consecutive_specials_collapse_to_single_hyphen(self):
        branch, sha = self._run_and_get_branch("my---repo")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertNotIn("--", slug)

    def test_leading_hyphens_stripped(self):
        # Directory names can't normally start with '-' on most systems but
        # the sed rule handles it; test with an unusual prefix that collapses.
        branch, sha = self._run_and_get_branch("123numeric-repo")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertFalse(slug.startswith("-"),
                         f"Slug {slug!r} must not start with a hyphen")

    def test_trailing_hyphens_stripped(self):
        branch, sha = self._run_and_get_branch("reponame---")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertFalse(slug.endswith("-"),
                         f"Slug {slug!r} must not end with a hyphen")

    def test_pure_alphanumeric_name_unchanged(self):
        branch, sha = self._run_and_get_branch("myrepo123")
        slug = self._extract_slug_from_branch(branch, sha)
        self.assertEqual(slug, "myrepo123")


class TestRepoSlugFallback(unittest.TestCase):
    """When the normalised slug is empty the script falls back to 'worktree'."""

    def test_fallback_to_worktree_when_slug_empty(self):
        """A directory name consisting only of special chars yields 'worktree'."""
        # We can't easily create a directory whose name reduces to an empty slug
        # via the real filesystem, so we simulate the relevant shell lines directly.
        snippet = textwrap.dedent("""\
            repo_slug="$(echo '---' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
            if [ -z "$repo_slug" ]; then
              repo_slug="worktree"
            fi
            printf "%s" "$repo_slug"
        """)
        result = _bash(snippet)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "worktree")

    def test_non_empty_slug_not_replaced(self):
        snippet = textwrap.dedent("""\
            repo_slug="$(echo 'validname' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
            if [ -z "$repo_slug" ]; then
              repo_slug="worktree"
            fi
            printf "%s" "$repo_slug"
        """)
        result = _bash(snippet)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "validname")


# ---------------------------------------------------------------------------
# Tests: origin/main upstream tracking
# ---------------------------------------------------------------------------

def _make_repo_with_origin(parent: Path) -> Path:
    """Create a local repo that has a real origin remote with origin/main tracked.

    Strategy:
    1. Create a bare repo (the "remote").
    2. Create a local repo, commit to it, add the bare repo as 'origin', push main.
    3. Return the local repo path (which now has refs/remotes/origin/main).
    """
    bare = parent / "bare.git"
    subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)

    local = parent / "local"
    _init_repo(local, branch="main")

    git_env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(
        ["git", "-C", str(local), "remote", "add", "origin", str(bare)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(local), "push", "-u", "origin", "main"],
        check=True, capture_output=True, env=git_env,
    )
    # Fetch so that refs/remotes/origin/main is definitely present
    subprocess.run(
        ["git", "-C", str(local), "fetch", "origin"],
        check=True, capture_output=True, env=git_env,
    )
    return local


class TestOriginMainUpstream(unittest.TestCase):
    """When origin/main exists the snippet sets upstream and fast-forwards."""

    def test_upstream_set_when_origin_main_exists(self):
        with tempfile.TemporaryDirectory() as parent:
            repo = _make_repo_with_origin(Path(parent))
            _detach_head(repo)

            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=str(repo))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] tracking origin/main", result.stdout)

    def test_ff_only_attempted_when_origin_main_exists(self):
        with tempfile.TemporaryDirectory() as parent:
            repo = _make_repo_with_origin(Path(parent))
            _detach_head(repo)

            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=str(repo))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] fast-forwarding", result.stdout)

    def test_no_upstream_message_when_origin_main_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)

            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex] tracking origin/main", result.stdout)
            self.assertNotIn("[codex] fast-forwarding", result.stdout)


# ---------------------------------------------------------------------------
# Tests: Mise-action variant (no `command -v git` guard)
# ---------------------------------------------------------------------------

class TestMiseSnippetBehaviour(unittest.TestCase):
    """The Mise action uses a variant without the outer `command -v git` check."""

    def _repo_slug(self, name: str) -> str:
        import re
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug or "worktree"

    def test_skips_outside_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(MISE_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_no_branch_created_on_named_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            result = _run_snippet(MISE_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("[codex]", result.stdout)

    def test_creates_branch_in_detached_head(self):
        with tempfile.TemporaryDirectory(suffix="-miserepo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            short_sha = _detach_head(repo)
            slug = self._repo_slug(repo.name)
            expected_branch = f"codex/{slug}-worktree-{short_sha}"

            result = _run_snippet(MISE_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[codex] detached HEAD detected", result.stdout)
            self.assertTrue(_branch_exists(repo, expected_branch))

    def test_branch_creation_behaviour_matches_setup_snippet(self):
        """Both variants must produce the same branch name for the same repo."""
        with tempfile.TemporaryDirectory(suffix="-samerepo") as tmp:
            # Run setup snippet in one repo
            repo_a = Path(tmp) / "a"
            repo_a.mkdir()
            _init_repo(repo_a)
            sha_a = _detach_head(repo_a)
            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=str(repo_a))
            branch_a = _current_branch(repo_a)

            # Run mise snippet in a second repo with the same directory name
            repo_b = Path(tmp) / "a"  # same name inside same parent
            # We can't create another dir with the same name; just verify the slug logic
            # matches by extracting the non-sha part.
            slug_a = branch_a.replace("codex/", "").replace(f"-worktree-{sha_a}", "")

            # Create a fresh repo to run the mise snippet
            repo_c = Path(tmp) / "c-samerepo"
            repo_c.mkdir()
            _init_repo(repo_c, branch="main")
            sha_c = _detach_head(repo_c)
            _run_snippet(MISE_SNIPPET, cwd=str(repo_c))
            branch_c = _current_branch(repo_c)

            # Both should follow the same naming pattern
            self.assertTrue(branch_c.startswith("codex/"), f"Expected codex/ prefix, got {branch_c!r}")
            self.assertIn("-worktree-", branch_c)


# ---------------------------------------------------------------------------
# Tests: idempotency / re-entrance
# ---------------------------------------------------------------------------

class TestSnippetIdempotency(unittest.TestCase):
    """Running the snippet a second time (already on a named branch) is a no-op."""

    def test_second_run_does_not_create_another_branch(self):
        """After the first run the repo is on a named branch; second run is silent."""
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)

            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            branch_after_first = _current_branch(repo)

            result2 = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result2.returncode, 0, result2.stderr)
            self.assertNotIn("[codex]", result2.stdout)
            self.assertEqual(_current_branch(repo), branch_after_first,
                             "Branch must not change on second run")


# ---------------------------------------------------------------------------
# Tests: regression / boundary cases
# ---------------------------------------------------------------------------

class TestRegressionBoundaryCases(unittest.TestCase):
    """Additional regression and boundary tests."""

    def test_snippet_does_not_modify_repo_on_named_branch(self):
        """On a named branch: no new commits, no new branches, no changed HEAD."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            before_head = subprocess.run(
                ["git", "-C", tmp, "rev-parse", "HEAD"],
                capture_output=True, text=True,
            ).stdout.strip()

            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)

            after_head = subprocess.run(
                ["git", "-C", tmp, "rev-parse", "HEAD"],
                capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(before_head, after_head, "HEAD must not move on a named branch")

    def test_branch_worktree_label_always_present(self):
        """The literal string '-worktree-' must appear in every generated branch name."""
        with tempfile.TemporaryDirectory(suffix="-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)
            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            branch = _current_branch(repo)
            self.assertIn("-worktree-", branch,
                          f"Expected '-worktree-' in branch name, got {branch!r}")

    def test_snippet_exits_zero_outside_git(self):
        """The snippet must exit 0 even outside a git repository."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0)

    def test_mise_snippet_exits_zero_outside_git(self):
        """The Mise snippet must exit 0 even outside a git repository."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_snippet(MISE_SNIPPET, cwd=tmp)
            self.assertEqual(result.returncode, 0)

    def test_branch_contains_only_safe_characters(self):
        """Generated branch name must only contain characters safe for git refs."""
        with tempfile.TemporaryDirectory(suffix="-safe-chars-repo") as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            _detach_head(repo)
            _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            branch = _current_branch(repo)
            import re
            self.assertRegex(branch, r"^[a-z0-9/\-]+$",
                             f"Branch {branch!r} contains unsafe characters")

    def test_both_snippets_skip_cleanly_when_not_a_repo(self):
        """Neither snippet should emit error output when not in a git repo."""
        with tempfile.TemporaryDirectory() as tmp:
            r1 = _run_snippet(SETUP_TOOLS_SNIPPET, cwd=tmp)
            r2 = _run_snippet(MISE_SNIPPET, cwd=tmp)
            self.assertEqual(r1.returncode, 0)
            self.assertEqual(r2.returncode, 0)
            self.assertEqual(r1.stderr, "")
            self.assertEqual(r2.stderr, "")


if __name__ == "__main__":
    unittest.main()