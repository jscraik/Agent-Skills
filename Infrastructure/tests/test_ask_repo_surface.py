from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ASK_LIB = Path(__file__).resolve().parents[1] / "scripts" / "lib"
if str(ASK_LIB) not in sys.path:
    sys.path.insert(0, str(ASK_LIB))
LIFECYCLE_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "lifecycle-and-sync"
if str(LIFECYCLE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE_SCRIPTS))

from ask.commands import repo as repo_commands  # noqa: E402


def _run_ask(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def test_repo_surface_json_envelope() -> None:
    result = _run_ask(["repo", "surface", "--json"])

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["metadata"]["command"] == "repo surface --json"
    report = payload["data"]["repo_surface"]
    assert report["schema_version"] == 1
    assert report["metadata"]["inventory_scope"] == "tracked_files"
    assert "findings" in report
    assert "summary" in report
    for step in report["metadata"]["next_steps"]:
        assert {"type", "command", "rationale"} <= step.keys()


def test_repo_surface_strict_json_reports_expected_policy_debt() -> None:
    result = _run_ask(["repo", "surface", "--strict", "--json"])

    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["data"]["strict"] is True
    report = payload["data"]["repo_surface"]
    if report["summary"]["blocking_findings"] > 0:
        assert result.returncode != 0
        assert payload["status"] == "error"
        assert report["status"] == "error"
        first = report["findings"][0]
        assert first["blocking"] is True
        assert first["severity"] == "error"
        assert {"type", "command", "rationale"} <= first["metadata"]["next_steps"][0].keys()
    else:
        assert result.returncode == 0
        assert payload["status"] == "success"
        assert report["status"] == "success"


def test_repo_surface_trace_id_is_preserved() -> None:
    result = _run_ask(["--trace-id", "repo-surface-test", "repo", "surface", "--json"])

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["trace_id"] == "repo-surface-test"


def test_repo_surface_invalid_json_is_top_level_error(monkeypatch, tmp_path) -> None:
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=["check_repo_surface_inventory.py"],
            returncode=0,
            stdout="not json",
            stderr="",
        )

    monkeypatch.setattr(repo_commands.subprocess, "run", fake_run)

    result = repo_commands.repo_surface(tmp_path)

    assert result.status == "error"
    assert result.data["repo_surface"]["status"] == "error"
    assert result.errors[0].message == "Repo surface inventory emitted invalid JSON."
