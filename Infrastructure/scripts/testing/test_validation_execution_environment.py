#!/usr/bin/env python3
"""Regression tests for deterministic validation and hook installation runtimes."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATE_ALL = REPO_ROOT / "Infrastructure/scripts/validate_all.sh"
INSTALL_PREK_HOOKS = REPO_ROOT / "Infrastructure/scripts/install-prek-hooks.sh"


def _run(*command: str, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run a command with captured text output for an isolated fixture repository."""
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _create_hook_fixture(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repository"
    _run("git", "init", "-q", str(repo), cwd=tmp_path, env=os.environ.copy()).check_returncode()
    script_dir = repo / "Infrastructure/scripts"
    script_dir.mkdir(parents=True)
    shutil.copy2(INSTALL_PREK_HOOKS, script_dir / "install-prek-hooks.sh")
    helper_target = script_dir / "lib/secure-hook-cache.sh"
    helper_target.parent.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "Infrastructure/scripts/lib/secure-hook-cache.sh", helper_target)
    (repo / "prek.toml").write_text("repos = []\n", encoding="utf-8")
    return repo, script_dir


def _common_hooks_dir(repo: Path) -> Path:
    result = _run(
        "git",
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
        cwd=repo,
        env=os.environ.copy(),
    )
    return Path(result.stdout.strip()) / "hooks"


def _write_fake_prek(tmp_path: Path) -> Path:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_prek = fake_bin / "prek"
    fake_prek.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
if git config --get core.hooksPath >/dev/null; then
  echo 'Cowardly refusing to install hooks with core.hooksPath set.' >&2
  exit 19
fi
hooks_dir="$(git rev-parse --path-format=absolute --git-common-dir)/hooks"
mkdir -p "$hooks_dir"
for hook in pre-commit commit-msg pre-push; do
  cat > "$hooks_dir/$hook" <<'HOOK'
#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK
done
""",
        encoding="utf-8",
    )
    fake_prek.chmod(0o755)
    return fake_bin


def _hook_env(tmp_path: Path, fake_bin: Path) -> dict[str, str]:
    return {
        **os.environ,
        "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
        "CODEX_HOOK_CACHE_ROOT": str(tmp_path / "hook-cache"),
    }


def test_validate_all_uses_locked_infrastructure_python() -> None:
    """The broad validator must use its locked project environment, not ambient Python."""
    env = {key: value for key, value in os.environ.items() if key != "PYTHON_BIN"}
    result = _run(
        "bash",
        str(VALIDATE_ALL),
        "--ephemeral",
        "--fail-fast",
        "--changed-files",
        "Infrastructure/scripts/validation-and-linting/validate_pr_pipeline_toolchain.py",
        cwd=REPO_ROOT,
        env=env,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Python launcher: uv run --frozen --project Infrastructure" in result.stdout
    assert "Python launcher: python3" not in result.stdout


def test_prek_reinstalls_when_expected_hooks_path_is_already_configured(
    tmp_path: Path,
) -> None:
    """Hook refresh must be idempotent when prepare-worktree configured common hooks."""
    repo, script_dir = _create_hook_fixture(tmp_path)
    hooks_dir = _common_hooks_dir(repo)
    _run(
        "git",
        "config",
        "--local",
        "core.hooksPath",
        str(hooks_dir),
        cwd=repo,
        env=os.environ.copy(),
    ).check_returncode()

    env = _hook_env(tmp_path, _write_fake_prek(tmp_path))

    result = _run("bash", str(script_dir / "install-prek-hooks.sh"), cwd=repo, env=env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "hooks ready" in result.stdout
    configured = _run(
        "git", "config", "--local", "--get", "core.hooksPath", cwd=repo, env=env
    ).stdout.strip()
    assert configured == str(hooks_dir)
    assert "agent-skills prek home begin" in (hooks_dir / "pre-commit").read_text(
        encoding="utf-8"
    )
