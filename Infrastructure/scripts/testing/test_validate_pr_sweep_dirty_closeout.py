from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_pr_sweep_dirty_closeout.py"
)
SPEC = importlib.util.spec_from_file_location("validate_pr_sweep_dirty_closeout", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_pr_sweep_dirty_closeout = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_pr_sweep_dirty_closeout
SPEC.loader.exec_module(validate_pr_sweep_dirty_closeout)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["/usr/bin/git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "initial")
    return repo


def test_dirty_worktree_without_ledger_fails(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    (repo / "untracked.txt").write_text("new\n", encoding="utf-8")

    payload = validate_pr_sweep_dirty_closeout.validate(repo)

    assert payload["status"] == "fail"
    assert payload["findings"][0]["code"] == "dirty_worktree_ledger_required"
    assert payload["unledgered_paths"] == sorted(["tracked.txt", "untracked.txt"])


def test_dirty_worktree_with_complete_ledger_passes(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    (repo / "untracked.txt").write_text("new\n", encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps(
            {
                "schema_version": "pr-sweep-worktree-closeout/v1",
                "dirty_worktree_ledger": [
                    {"path": "tracked.txt", "owner": "sdk-ratchet"},
                    {"path": "untracked.txt", "owner": "evidence-artifact"},
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = validate_pr_sweep_dirty_closeout.validate(repo, ledger_path=ledger)

    assert payload["status"] == "pass"
    assert payload["unledgered_paths"] == []


def test_require_clean_blocks_even_when_dirty_paths_are_ledgered(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"dirty_worktree_ledger": [{"path": "tracked.txt"}]}), encoding="utf-8")

    payload = validate_pr_sweep_dirty_closeout.validate(repo, ledger_path=ledger, require_clean=True)

    assert payload["status"] == "fail"
    assert payload["findings"][0]["code"] == "primary_worktree_dirty"


def test_staged_path_is_included_in_dirty_paths(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")

    payload = validate_pr_sweep_dirty_closeout.validate(repo)

    assert payload["status"] == "fail"
    assert payload["dirty_state"]["staged_paths"] == ["tracked.txt"]
    assert payload["unledgered_paths"] == ["tracked.txt"]
