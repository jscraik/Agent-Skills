#!/usr/bin/env python3
"""Contract tests for git hook command surfaces."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_HOOK_RUNNER_PATTERNS = (
    "make hooks-",
    ".git/hooks",
    "pre-commit run",
    "prek run",
    "prek hook-run",
)
ROOT_PREK_EXPECTED = {
    "pre-commit": "bash scripts/hooks/pre-commit.sh",
    "commit-msg": "bash scripts/hooks/commit-msg.sh",
    "pre-push": "bash scripts/hooks/pre-push.sh",
}
INFRASTRUCTURE_PREK_EXPECTED = {
    "pre-commit": "bash ../scripts/hooks/pre-commit.sh",
    "commit-msg": "bash ../scripts/hooks/commit-msg.sh",
    "pre-push": "bash ../scripts/hooks/pre-push.sh",
}
SIMPLE_GIT_HOOKS_EXPECTED = {
    "pre-commit": "bash scripts/hooks/pre-commit.sh",
    "commit-msg": "bash scripts/hooks/commit-msg.sh $1",
    "pre-push": "bash scripts/hooks/pre-push.sh",
}
SIMPLE_GIT_HOOKS_JSON_EXPECTED = {
    **SIMPLE_GIT_HOOKS_EXPECTED,
    "commit-msg": 'bash scripts/hooks/commit-msg.sh \\"$1\\"',
}


def _assert_environment_validator_contract(text: str, validator: str) -> None:
    _assert_commands_present(text)
    _assert_simple_hook_commands_present(text)
    assert '"make hooks-pre-commit"' not in text
    assert '"make hooks-pre-push"' not in text
    assert "validate_generated_prek_hook.py" in text
    assert 're.search(r"(?:\\$HOME' not in text
    assert 'export PREK_HOME="$CODEX_HOOK_CACHE_ROOT/prek"' in validator
    assert 'validate_hook_cache_path "$CODEX_HOOK_CACHE_ROOT"' in validator
    assert 'secure_hook_cache_dir "$PREK_HOME"' in validator


def _assert_commands_present(text: str) -> None:
    for command in ROOT_PREK_EXPECTED.values():
        assert command in text


def _assert_simple_hook_commands_present(text: str) -> None:
    for command in SIMPLE_GIT_HOOKS_EXPECTED.values():
        escaped = command.replace("$", "\\$")
        assert escaped in text or command in text


def _write_generated_hook_fixture(
    tmp_path: Path, root_assignment: str, name: str
) -> Path:
    hook = tmp_path / name
    hook.write_text(
        f"""#!/usr/bin/env bash
# agent-skills prek home begin
export CODEX_HOOK_CACHE_ROOT={root_assignment}
export PREK_HOME="$CODEX_HOOK_CACHE_ROOT/prek"
AGENT_SKILLS_REPO_ROOT="$(git rev-parse --show-toplevel)"
AGENT_SKILLS_GIT_COMMON_DIR="$(git rev-parse --path-format=absolute --git-common-dir)"
source "$AGENT_SKILLS_REPO_ROOT/Infrastructure/scripts/lib/secure-hook-cache.sh"
CODEX_HOOK_CACHE_ROOT="$(validate_hook_cache_path "$CODEX_HOOK_CACHE_ROOT" "$AGENT_SKILLS_REPO_ROOT" "$AGENT_SKILLS_GIT_COMMON_DIR")"
PREK_HOME="$(validate_hook_cache_path "$PREK_HOME" "$AGENT_SKILLS_REPO_ROOT" "$AGENT_SKILLS_GIT_COMMON_DIR")"
secure_hook_cache_dir "$CODEX_HOOK_CACHE_ROOT"
secure_hook_cache_dir "$PREK_HOME"
cd "$AGENT_SKILLS_REPO_ROOT"
# agent-skills prek home end
""",
        encoding="utf-8",
    )
    return hook


def _local_prek_entries(path: Path) -> dict[str, list[str]]:
    """
    Extract stage-to-hook-entry mappings from local repositories in a pre-commit configuration file.

    Parameters:
    	path (Path): Path to a pre-commit configuration TOML file.

    Returns:
    	dict[str, list[str]]: Mapping of stage names to lists of hook entry commands from local repositories.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    entries: dict[str, list[str]] = {}
    for repo in data.get("repos", []):
        if repo.get("repo") != "local":
            continue
        for hook in repo.get("hooks", []):
            entry = hook.get("entry")
            if not isinstance(entry, str):
                continue
            for stage in hook.get("stages", []):
                if stage not in entries:
                    entries[stage] = []
                entries[stage].append(entry)
    return entries


def _assert_not_nested(command: str, source: Path) -> None:
    """
    Validate that a hook command does not embed nested hook runner patterns.
    
    Parameters:
        command (str): The hook command to validate.
        source (Path): The source file path where the command is defined.
    
    Raises:
        AssertionError: If the command contains a forbidden hook runner pattern.
    """
    lower_command = command.lower()
    for pattern in FORBIDDEN_HOOK_RUNNER_PATTERNS:
        assert pattern not in lower_command, (
            f"{source} hook command must call a leaf adapter, not nested runner "
            f"{pattern!r}: {command!r}"
        )


def test_prek_entries_call_leaf_adapters() -> None:
    """
    Verify prek configuration files define leaf adapter commands for git hooks.
    
    Asserts both root and Infrastructure prek.toml files contain the expected hook adapter command mappings and that no command invokes a nested hook runner.
    """
    for rel_path, expected in [
        ("prek.toml", ROOT_PREK_EXPECTED),
        ("Infrastructure/prek.toml", INFRASTRUCTURE_PREK_EXPECTED),
    ]:
        path = REPO_ROOT / rel_path
        entries = _local_prek_entries(path)
        # Convert list of entries back to single values for comparison
        entries_flat = {stage: cmds[0] if len(cmds) == 1 else cmds for stage, cmds in entries.items()}
        assert entries_flat == expected
        for commands in entries.values():
            for command in commands:
                _assert_not_nested(command, path)


def test_simple_git_hooks_template_calls_leaf_adapters() -> None:
    """
    Verify that git hook setup scripts contain leaf adapter commands and do not reference nested runners or make targets.
    
    Asserts that the setup-git-hooks.js files in both root and Infrastructure directories define the expected hook entry commands as JSON strings, do not contain forbidden nested hook runner patterns, and do not reference make hook convenience targets.
    """
    for rel_path in [
        "Infrastructure/scripts/setup-git-hooks.js",
        "scripts/setup-git-hooks.js",
    ]:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        for hook_name, command in SIMPLE_GIT_HOOKS_JSON_EXPECTED.items():
            expected = f'"{hook_name}": "{command}"'
            assert expected in text
            _assert_not_nested(command.replace('\\\"', '"'), path)
        assert "make hooks-pre-commit" not in text
        assert "make hooks-pre-push" not in text


def test_make_hook_targets_are_convenience_wrappers_only() -> None:
    """
    Verify that Makefile hook targets directly invoke leaf adapter scripts without nesting into other make targets.
    
    Asserts that the root Makefile contains hook targets (pre-commit, commit-msg, pre-push) with exact shell invocations to adapter scripts, and the Infrastructure Makefile does not delegate to upstream make targets but instead directly calls the adapter scripts.
    """
    root_makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert (
        "hooks-pre-commit: ## Run local pre-commit gates before creating a commit\n"
        "\t@bash scripts/hooks/pre-commit.sh"
    ) in root_makefile
    assert "hooks-commit-msg: ## Validate commit message policy" in root_makefile
    assert '\t@bash scripts/hooks/commit-msg.sh "$(HOOK_COMMIT_MSG_FILE)"' in root_makefile
    assert (
        "hooks-pre-push: ## Run local pre-push governance gates before pushing\n"
        "\t@bash scripts/hooks/pre-push.sh"
    ) in root_makefile

    infrastructure_makefile = (REPO_ROOT / "Infrastructure/Makefile").read_text(
        encoding="utf-8"
    )
    assert "$(MAKE) -C .. hooks-" not in infrastructure_makefile
    assert "@bash ../scripts/hooks/pre-commit.sh" in infrastructure_makefile
    assert '@bash ../scripts/hooks/commit-msg.sh "$(HOOK_COMMIT_MSG_FILE)"' in infrastructure_makefile
    assert "@bash ../scripts/hooks/pre-push.sh" in infrastructure_makefile


def test_environment_check_enforces_adapter_hook_shape() -> None:
    """
    Validate that the environment-check script contains expected leaf adapter hook commands and excludes nested hook runner patterns.
    """
    path = REPO_ROOT / "Infrastructure/scripts/check-environment_impl.sh"
    text = path.read_text(encoding="utf-8")
    validator = (REPO_ROOT / "Infrastructure/scripts/validation-and-linting/validate_generated_prek_hook.py").read_text(encoding="utf-8")
    _assert_environment_validator_contract(text, validator)


def test_hook_adapters_do_not_call_hook_runners() -> None:
    """
    Verify that hook adapter scripts invoke leaf validators without calling hook orchestrators.
    """
    for rel_path in [
        "Infrastructure/scripts/hooks/pre-commit.sh",
        "Infrastructure/scripts/hooks/commit-msg.sh",
        "Infrastructure/scripts/hooks/pre-push.sh",
    ]:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_HOOK_RUNNER_PATTERNS:
            assert pattern not in text.lower(), (
                f"{path} contains nested runner pattern {pattern!r}"
            )
        assert re.search(r"bash .*validate_all\.sh|node scripts/validate-commit-msg\.js", text)


def test_hook_sandbox_env_replaces_unusable_inherited_cache_only(tmp_path: Path) -> None:
    """Hooks must not inherit a desktop cache path that they cannot use."""
    helper = REPO_ROOT / "scripts/hooks/_sandbox_env.sh"
    command = [
        "bash",
        "-c",
        'source "$1"; printf "%s\\n%s\\n" "$UV_CACHE_DIR" "$XDG_CACHE_HOME"',
        "bash",
        str(helper),
    ]
    unusable = "/dev/null/agent-skills-uv-cache"
    environment = {
        **os.environ,
        "TMPDIR": str(tmp_path),
        "UV_CACHE_DIR": unusable,
        "XDG_CACHE_HOME": str(tmp_path / "explicit-xdg-cache"),
    }
    result = subprocess.run(command, capture_output=True, text=True, check=False, env=environment)

    assert result.returncode == 0, result.stderr
    uv_cache, xdg_cache = result.stdout.splitlines()
    assert uv_cache == str(tmp_path / "agent-skills-uv-cache")
    assert xdg_cache == str(tmp_path / "explicit-xdg-cache")


def test_hook_sandbox_env_rejects_non_searchable_cache_directory(tmp_path: Path) -> None:
    """Hooks need a structurally usable cache path independent of effective uid."""
    helper = REPO_ROOT / "scripts/hooks/_sandbox_env.sh"
    inaccessible_cache = Path("/dev/null") / "agent-skills-inaccessible-cache"
    command = [
        "bash",
        "-c",
        'source "$1"; printf "%s" "$UV_CACHE_DIR"',
        "bash",
        str(helper),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TMPDIR": str(tmp_path), "UV_CACHE_DIR": str(inaccessible_cache)},
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == str(tmp_path / "agent-skills-uv-cache")


def test_hook_adapters_resolve_root_without_inherited_git_context() -> None:
    for rel_path in [
        "Infrastructure/scripts/hooks/pre-commit.sh",
        "Infrastructure/scripts/hooks/pre-push.sh",
    ]:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert 'git -C "$SCRIPT_DIR" rev-parse --show-toplevel' in text
        assert 'REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"' in text


def test_pre_push_adapter_keeps_upstream_diff_scope() -> None:
    """
    Verify the pre-push hook adapter preserves upstream-aware diff scoping.
    """
    text = (REPO_ROOT / "Infrastructure/scripts/hooks/pre-push.sh").read_text(
        encoding="utf-8"
    )
    assert "@{upstream}...HEAD" in text
    assert "HEAD^..HEAD" in text
    assert "diagnose_changed_skills.py" in text


def test_hook_adapters_use_sandbox_safe_temp_files() -> None:
    helper = (REPO_ROOT / "Infrastructure/scripts/hooks/_sandbox_env.sh").read_text(encoding="utf-8")
    assert "/private/tmp" in helper
    assert "/tmp" in helper
    assert "UV_CACHE_DIR" in helper

    for rel_path in [
        "scripts/hooks/commit-msg.sh",
        "scripts/hooks/pre-commit.sh",
        "scripts/hooks/pre-push.sh",
        "Infrastructure/scripts/hooks/commit-msg.sh",
        "Infrastructure/scripts/hooks/pre-commit.sh",
        "Infrastructure/scripts/hooks/pre-push.sh",
    ]:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert 'source "$SCRIPT_DIR/_sandbox_env.sh"' in text

    for rel_path in [
        "scripts/hooks/pre-commit.sh",
        "scripts/hooks/pre-push.sh",
        "Infrastructure/scripts/hooks/pre-commit.sh",
        "Infrastructure/scripts/hooks/pre-push.sh",
    ]:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert 'mktemp "$TMPDIR/agent-skills-' in text


def test_hook_adapters_resolve_root_after_sanitizing_git_context() -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/hooks/_sandbox_env.sh"
    hook_dir = REPO_ROOT / "Infrastructure/scripts/hooks"
    poisoned_env = os.environ.copy()
    poisoned_env.update(
        {
            "GIT_DIR": str(hook_dir),
            "GIT_WORK_TREE": str(hook_dir),
            "GIT_COMMON_DIR": str(hook_dir),
            "GIT_INDEX_FILE": str(hook_dir / "index"),
        }
    )
    command = (
        f'source "{helper}"; '
        f'git -C "{hook_dir}" rev-parse --show-toplevel'
    )
    result = subprocess.run(
        ["bash", "-c", command],
        capture_output=True,
        text=True,
        check=False,
        env=poisoned_env,
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == REPO_ROOT.resolve()


def test_hook_sandbox_preserves_git_temporary_index(tmp_path: Path) -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/hooks/_sandbox_env.sh"
    temporary_index = str(tmp_path / "index")
    result = subprocess.run(
        ["bash", "-c", f'source "{helper}"; printf "%s" "$GIT_INDEX_FILE"'],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "GIT_INDEX_FILE": temporary_index},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == temporary_index


def test_pre_commit_names_and_proves_current_index_lock_policy() -> None:
    for rel_path in [
        "scripts/hooks/pre-commit.sh",
        "Infrastructure/scripts/hooks/pre-commit.sh",
    ]:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert "--allow-parent-owned-index-lock" in text
        assert "--allow-current-index-lock" not in text
        assert 'hook_git_dir="${GIT_DIR:-}"' in text
        assert 'hook_git_index_file="${GIT_INDEX_FILE:-}"' in text
        assert 'GIT_DIR="$hook_git_dir" GIT_INDEX_FILE="$hook_git_index_file"' in text


def test_harness_fallback_wrappers_share_supported_version() -> None:
    expected = re.compile(r'FALLBACK_PACKAGE="@brainwav/coding-harness@\$SUPPORTED_VERSION"')
    global_fallback = 'if command -v harness >/dev/null 2>&1; then\n\t\texec harness "$@"\n\tfi'
    npm_fallback = 'if [[ "${HARNESS_CLI_ALLOW_NPM_EXEC:-}" == "1" ]]; then'
    wrapper_paths = [
        REPO_ROOT / "scripts/harness-cli.sh",
        REPO_ROOT / "Infrastructure/scripts/harness-cli.sh",
    ]
    wrapper_texts = [path.read_text(encoding="utf-8") for path in wrapper_paths]
    assert all(expected.search(text) for text in wrapper_texts)
    assert all('SUPPORTED_VERSION="0.15.3"' in text for text in wrapper_texts)
    assert all(global_fallback in text for text in wrapper_texts)
    assert all(text.index(global_fallback) < text.index(npm_fallback) for text in wrapper_texts)


def test_secure_hook_cache_rejects_symlinks_and_enforces_private_mode(tmp_path: Path) -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/lib/secure-hook-cache.sh"
    cache_dir = tmp_path / "cache"
    create = subprocess.run(
        ["bash", "-c", f'source "{helper}"; secure_hook_cache_dir "$1"', "bash", str(cache_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert create.returncode == 0, create.stderr
    assert cache_dir.stat().st_mode & 0o777 == 0o700

    target = tmp_path / "target"
    target.mkdir()
    symlink = tmp_path / "symlink-cache"
    symlink.symlink_to(target, target_is_directory=True)
    reject = subprocess.run(
        ["bash", "-c", f'source "{helper}"; secure_hook_cache_dir "$1"', "bash", str(symlink)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert reject.returncode != 0
    assert "must not be a symlink" in reject.stderr


def test_secure_hook_cache_rejects_existing_unmarked_directories(tmp_path: Path) -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/lib/secure-hook-cache.sh"
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir(mode=0o755)
    reject = subprocess.run(
        ["bash", "-c", f'source "{helper}"; secure_hook_cache_dir "$1"', "bash", str(unrelated)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert reject.returncode != 0
    assert "ownership marker" in reject.stderr


def test_secure_hook_cache_rejects_insecure_parent_chain(tmp_path: Path) -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/lib/secure-hook-cache.sh"
    unsafe_parent = tmp_path / "unsafe-parent"
    unsafe_parent.mkdir()
    unsafe_parent.chmod(0o777)
    candidate = unsafe_parent / "cache"
    reject = subprocess.run(
        ["bash", "-c", f'source "{helper}"; secure_hook_cache_dir "$1"', "bash", str(candidate)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert reject.returncode != 0
    assert "world-writable" in reject.stderr


def test_secure_hook_cache_allows_descendants_of_marked_root(tmp_path: Path) -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/lib/secure-hook-cache.sh"
    root = tmp_path / "root"
    child = root / "prek"
    command = f'source "{helper}"; secure_hook_cache_dir "$1"; secure_hook_cache_dir "$2"'
    result = subprocess.run(
        ["bash", "-c", command, "bash", str(root), str(child)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (root / ".agent-skills-hook-cache").read_text(encoding="utf-8") == "agent-skills-hook-cache/v1\n"


def test_hook_cache_paths_are_absolute_and_outside_repo(tmp_path: Path) -> None:
    helper = REPO_ROOT / "Infrastructure/scripts/lib/secure-hook-cache.sh"
    common_dir = Path(
        subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=REPO_ROOT, text=True, capture_output=True, check=True,
        ).stdout.strip()
    )
    command = f'source "{helper}"; validate_hook_cache_path "$1" "$2" "$3"'
    for candidate in ("relative-cache", str(REPO_ROOT), str(common_dir)):
        result = subprocess.run(
            ["bash", "-c", command, "bash", candidate, str(REPO_ROOT), str(common_dir)],
            text=True, capture_output=True, check=False,
        )
        assert result.returncode != 0
    approved = tmp_path / "cache"
    result = subprocess.run(
        ["bash", "-c", command, "bash", str(approved), str(REPO_ROOT), str(common_dir)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()) == approved.resolve()


def test_generated_prek_hooks_reapply_secure_cache_contract() -> None:
    installer = (
        REPO_ROOT / "Infrastructure/scripts/install-prek-hooks.sh"
    ).read_text(encoding="utf-8")
    assert 'source "$AGENT_SKILLS_REPO_ROOT/Infrastructure/scripts/lib/secure-hook-cache.sh"' in installer
    assert 'secure_hook_cache_dir "$CODEX_HOOK_CACHE_ROOT"' in installer
    assert 'secure_hook_cache_dir "$PREK_HOME"' in installer
    assert 'validate_hook_cache_path "$PREK_HOME"' in installer
    assert 'new_hook_cache_root' in installer
    assert 'agent-skills-hook-cache.XXXXXX' not in installer
    assert 'mkdir -p "$PREK_HOME"' not in installer
    assert 'export PREK_HOME="$CODEX_HOOK_CACHE_ROOT/prek"' in installer
    assert 'cd "$AGENT_SKILLS_REPO_ROOT"' in installer


def test_generated_hook_validator_accepts_shell_suffix_and_rejects_injection(tmp_path: Path) -> None:
    validator = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/validate_generated_prek_hook.py"
    common_dir = Path(
        subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    )

    valid = _write_generated_hook_fixture(tmp_path, str(tmp_path / "cache.sh"), "valid-hook.sh")
    accepted = subprocess.run(
        [sys.executable, str(validator), str(valid), str(REPO_ROOT), str(common_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr

    malicious = _write_generated_hook_fixture(
        tmp_path,
        f"{tmp_path}/cache$(touch {tmp_path}/pwned)",
        "malicious-hook.sh",
    )
    rejected = subprocess.run(
        [sys.executable, str(validator), str(malicious), str(REPO_ROOT), str(common_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert not (tmp_path / "pwned").exists()


def test_hook_adapters_pass_bash_syntax() -> None:
    """
    Verify that bash adapter scripts pass syntax validation.
    
    Runs bash syntax checking on all adapter scripts under Infrastructure/scripts/hooks/ to ensure they are parseable before installation.
    """
    scripts = [
        REPO_ROOT / "Infrastructure/scripts/hooks/pre-commit.sh",
        REPO_ROOT / "Infrastructure/scripts/hooks/commit-msg.sh",
        REPO_ROOT / "Infrastructure/scripts/hooks/pre-push.sh",
    ]
    for script in scripts:
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"{script}: {result.stderr}"
