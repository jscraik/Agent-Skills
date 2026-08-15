#!/usr/bin/env python3
"""Regression tests for validate_recursive_promotions.sh changed-only strict mode."""

from __future__ import annotations

import json
import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class ChangedOnlyFixture:
    """Describe the disposable repository state used by changed-only validation."""

    base_sha: str
    head_sha: str
    runs_root: Path
    report_json: Path
    parity_manifest: Path


def _run(*cmd: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*cmd],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _init_git_repo(workdir: Path) -> None:
    _run("git", "init", cwd=workdir)
    _run("git", "config", "user.email", "ci@example.com", cwd=workdir)
    _run("git", "config", "user.name", "ci", cwd=workdir)
    _run("git", "config", "commit.gpgsign", "false", cwd=workdir)


def _build_git_repo_snapshot(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        REPO_ROOT,
        dest,
        symlinks=True,
        dirs_exist_ok=True,
        ignore_dangling_symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git",
            ".mypy_cache",
            ".pytest_cache",
            "__pycache__",
            "node_modules",
        ),
    )
    _init_git_repo(dest)
    _run("git", "add", ".", cwd=dest)
    _run("git", "commit", "-m", "seed", cwd=dest)


def _git_sha(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def _prepare_changed_only_fixture(base_repo: Path) -> ChangedOnlyFixture:
    _build_git_repo_snapshot(base_repo)
    runs_root = base_repo / ".tmp" / "agent-skills-artifacts" / "skill-graphs" / "runs"
    (runs_root / "run_legacy").mkdir(parents=True, exist_ok=True)
    _write_json(
        runs_root / "run_legacy" / "run.json",
        {
            "schema_version": "1.0",
            "run_id": "run_legacy",
            "terminal_status": "failed",
            "stop_reason": "policy_failed",
            "prompt_hash": "deadbeef",
        },
    )
    doc = base_repo / "docs" / "guide.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    _write_text(doc, "baseline")
    _run("git", "add", ".tmp", cwd=base_repo)
    _run("git", "add", "docs/guide.md", cwd=base_repo)
    _run("git", "commit", "-m", "base", cwd=base_repo)
    base_sha = _git_sha(base_repo)
    _write_text(doc, "updated")
    _run("git", "add", "docs/guide.md", cwd=base_repo)
    _run("git", "commit", "-m", "docs change", cwd=base_repo)
    evidence_root = base_repo / ".harness" / "evidence" / "skill-graphs" / "pilot"
    return ChangedOnlyFixture(
        base_sha=base_sha,
        head_sha=_git_sha(base_repo),
        runs_root=runs_root,
        report_json=evidence_root / "promotion-validation-report.json",
        parity_manifest=evidence_root / "artifact-parity-manifest.json",
    )


def _run_changed_only_validation(
    base_repo: Path,
    fixture: ChangedOnlyFixture,
) -> subprocess.CompletedProcess[str]:
    script = (
        base_repo
        / "Infrastructure"
        / "scripts"
        / "lifecycle-and-sync"
        / "validate_recursive_promotions.sh"
    )
    return _run(
        "bash",
        str(script),
        "--changed-only",
        "--base-sha",
        fixture.base_sha,
        "--head-sha",
        fixture.head_sha,
        "--runs-root",
        str(fixture.runs_root),
        "--report-json",
        str(fixture.report_json),
        "--parity-manifest",
        str(fixture.parity_manifest),
        "--strict-runs",
        cwd=base_repo,
    )


class ValidateRecursivePromotionsScriptTests(unittest.TestCase):
    def test_strict_runs_with_changed_only_skips_global_scan_when_no_changed_runs(self) -> None:
        with TemporaryDirectory() as tmpdir_raw:
            base_repo = Path(tmpdir_raw) / "repo"
            fixture = _prepare_changed_only_fixture(base_repo)
            proc = _run_changed_only_validation(base_repo, fixture)
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertTrue(fixture.report_json.exists())
            payload = json.loads(fixture.report_json.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("status"), "ok")
            self.assertEqual(payload.get("validated"), 0)
            self.assertTrue(fixture.parity_manifest.exists())


if __name__ == "__main__":
    unittest.main()
