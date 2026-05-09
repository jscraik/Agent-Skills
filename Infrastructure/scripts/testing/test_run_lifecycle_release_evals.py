from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "Plugins"
    / "harness-engineering"
    / "scripts"
    / "run_lifecycle_release_evals.py"
)


def load_runner():
    spec = importlib.util.spec_from_file_location("run_lifecycle_release_evals", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def test_ask_eval_blocks_when_ask_is_missing(tmp_path: Path) -> None:
    runner = load_runner()

    result = runner._run_ask_eval(tmp_path, "he-router", "smoke", 1)

    assert result["status"] == "blocked"
    assert result["decision"] == "blocked"
    assert result["returncode"] != 0
    assert result["errors"][0]["code"] == "ERR_ASK_UNAVAILABLE"
    assert "./bin/ask is missing" in result["errors"][0]["message"]


def test_ask_eval_blocks_when_ask_is_not_executable(tmp_path: Path) -> None:
    runner = load_runner()
    ask = tmp_path / "bin" / "ask"
    ask.parent.mkdir()
    ask.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    ask.chmod(0o644)

    result = runner._run_ask_eval(tmp_path, "he-router", "smoke", 1)

    assert result["status"] == "blocked"
    assert result["errors"][0]["code"] == "ERR_ASK_UNAVAILABLE"
    assert "./bin/ask is not executable" in result["errors"][0]["message"]


def test_ask_availability_accepts_executable_wrapper(tmp_path: Path) -> None:
    runner = load_runner()
    ask = tmp_path / "bin" / "ask"
    ask.parent.mkdir()
    ask.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    ask.chmod(0o755)

    assert runner._ask_unavailable_reason(tmp_path) is None


def test_required_router_sample_gate_fails_summary() -> None:
    runner = load_runner()
    result = {
        "skill": "he-router",
        "mode": "smoke",
        "runner": "codex",
        "returncode": 0,
        "status": "success",
    }
    router_sample_gate = {
        "required": True,
        "status": "fail",
        "returncode": 1,
        "errors": [{"code": "ERR_ROUTER_SAMPLE", "message": "sample failed"}],
    }

    summary = runner.summarize([result], router_sample_gate=router_sample_gate)

    assert summary["status"] == "fail"
    assert summary["failing_skills"] == []
    assert summary["failing_gates"] == ["router_samples"]
    assert summary["router_sample_gate"] == router_sample_gate
