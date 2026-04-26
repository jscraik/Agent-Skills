import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_SEE_ALSO = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "check-see-also.py"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30, check=False)


def _git(cmd: list[str], cwd: Path) -> None:
    result = _run(["git", *cmd], cwd)
    assert result.returncode == 0, result.stderr


def _commit(cwd: Path, message: str) -> None:
    _git(["add", "."], cwd)
    _git(["commit", "-m", message], cwd)


def _init_repo(repo: Path) -> None:
    repo.mkdir()
    _git(["init"], repo)
    _git(["config", "user.email", "test@example.com"], repo)
    _git(["config", "user.name", "Test User"], repo)
    base_skill = repo / "Skills" / "existing" / "SKILL.md"
    base_skill.parent.mkdir(parents=True)
    base_skill.write_text(
        "---\nname: existing\n---\n\n# Existing\n\nExisting skill body.\n",
        encoding="utf-8",
    )
    _commit(repo, "base")
    _git(["update-ref", "refs/remotes/origin/main", "HEAD"], repo)


def test_changed_existing_skill_is_skipped_when_pr_adds_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    skill = repo / "Skills" / "existing" / "SKILL.md"
    skill.write_text(
        "---\nname: existing\n---\n\n# Existing\n\nChanged existing skill body.\n",
        encoding="utf-8",
    )
    _commit(repo, "modify existing skill")

    result = _run(
        [sys.executable, str(CHECK_SEE_ALSO), ".", "--changed-files", "Skills/existing/SKILL.md"],
        repo,
    )

    assert result.returncode == 0, result.stderr


def test_added_skill_still_requires_see_also_entries(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    skill = repo / "Skills" / "new-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: new-skill\n---\n\n# New Skill\n\nNew skill body.\n",
        encoding="utf-8",
    )
    _commit(repo, "add new skill")

    result = _run(
        [sys.executable, str(CHECK_SEE_ALSO), ".", "--changed-files", "Skills/new-skill/SKILL.md"],
        repo,
    )

    assert result.returncode == 1
    assert "'Skills/new-skill' has only 0 See Also" in result.stderr
