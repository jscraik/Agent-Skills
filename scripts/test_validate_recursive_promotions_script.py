#!/usr/bin/env python3
"""Regression tests for validate_recursive_promotions.sh changed-only strict mode."""

from __future__ import annotations

import json
import subprocess
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


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


class ValidateRecursivePromotionsScriptTests(unittest.TestCase):
    def test_strict_runs_with_changed_only_skips_global_scan_when_no_changed_runs(self) -> None:
        with TemporaryDirectory() as tmpdir_raw:
            base_repo = Path(tmpdir_raw) / "repo"
            _build_git_repo_snapshot(base_repo)
            script = base_repo / "scripts" / "validate_recursive_promotions.sh"

            runs_root = base_repo / "artifacts" / "skill-graphs" / "runs"
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
            _run("git", "add", "artifacts", cwd=base_repo)
            _run("git", "add", "docs/guide.md", cwd=base_repo)
            _run("git", "commit", "-m", "base", cwd=base_repo)
            base = _git_sha(base_repo)

            _write_text(doc, "updated")
            _run("git", "add", "docs/guide.md", cwd=base_repo)
            _run("git", "commit", "-m", "docs change", cwd=base_repo)
            head = _git_sha(base_repo)

            report_json = (
                base_repo
                / "artifacts"
                / "skill-graphs"
                / "pilot"
                / "promotion-validation-report.json"
            )
            parity_manifest = (
                base_repo
                / "artifacts"
                / "skill-graphs"
                / "pilot"
                / "artifact-parity-manifest.json"
            )

            proc = _run(
                "bash",
                str(script),
                "--changed-only",
                "--base-sha",
                base,
                "--head-sha",
                head,
                "--runs-root",
                str(runs_root),
                "--report-json",
                str(report_json),
                "--parity-manifest",
                str(parity_manifest),
                "--strict-runs",
                cwd=base_repo,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertTrue(report_json.exists())
            payload = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("status"), "ok")
            self.assertEqual(payload.get("validated"), 0)
            self.assertTrue(parity_manifest.exists())


if __name__ == "__main__":
    unittest.main()
