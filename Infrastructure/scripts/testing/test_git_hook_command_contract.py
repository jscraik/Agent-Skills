#!/usr/bin/env python3
"""Contract tests for git hook command surfaces."""

from __future__ import annotations

import re
import subprocess
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


def _local_prek_entries(path: Path) -> dict[str, str]:
    """
    Extract stage-to-hook-entry mappings from local repositories in a pre-commit configuration file.
    
    Parameters:
    	path (Path): Path to a pre-commit configuration TOML file.
    
    Returns:
    	dict[str, str]: Mapping of stage names to hook entry commands from local repositories.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    entries: dict[str, str] = {}
    for repo in data.get("repos", []):
        if repo.get("repo") != "local":
            continue
        for hook in repo.get("hooks", []):
            entry = hook.get("entry")
            if not isinstance(entry, str):
                continue
            for stage in hook.get("stages", []):
                entries[stage] = entry
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
        assert entries == expected
        for command in entries.values():
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
        for hook_name, command in SIMPLE_GIT_HOOKS_EXPECTED.items():
            assert f'"{hook_name}": "{command}"' in text
            _assert_not_nested(command, path)
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
    for command in ROOT_PREK_EXPECTED.values():
        assert command in text
    for command in SIMPLE_GIT_HOOKS_EXPECTED.values():
        assert command.replace("$", "\\$") in text or command in text
    assert '"make hooks-pre-commit"' not in text
    assert '"make hooks-pre-push"' not in text


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
