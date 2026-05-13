from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock


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
    assert summary["eval_runtime"]["codex_model"] == "gpt-5.3-codex-spark"
    assert summary["eval_runtime"]["reasoning_flags"] == []


def test_direct_codex_eval_uses_spark_and_ignores_user_config() -> None:
    runner = load_runner()
    completed = mock.Mock(returncode=0, stdout=json.dumps({"decision": "pass"}), stderr="")

    with mock.patch.object(runner.subprocess, "run", return_value=completed) as run:
        result = runner._run_skill_builder_eval(
            Path("/tmp/repo"),
            "he-router",
            "release",
            "codex",
            (),
            (),
            90,
            "gpt-5.4",
            None,
            Path("/tmp/codex-home"),
        )

    assert result["status"] == "success"
    cmd = run.call_args.args[0]
    assert cmd[cmd.index("--model") + 1] == "gpt-5.3-codex-spark"
    assert cmd[cmd.index("--codex-arg") + 1] == "--ignore-user-config"
    assert "--reasoning" not in cmd
    assert "--reasoning-effort" not in cmd


def test_direct_codex_eval_omits_codex_home_when_not_explicit() -> None:
    runner = load_runner()
    completed = mock.Mock(returncode=0, stdout=json.dumps({"decision": "pass"}), stderr="")

    with mock.patch.object(runner.subprocess, "run", return_value=completed) as run:
        result = runner._run_skill_builder_eval(
            Path("/tmp/repo"),
            "he-router",
            "release",
            "codex",
            (),
            (),
            90,
            None,
            None,
            None,
        )

    assert result["status"] == "success"
    cmd = run.call_args.args[0]
    assert "--codex-home" not in cmd


def test_usage_limit_jsonl_classifies_as_tool_preflight() -> None:
    runner = load_runner()

    with tempfile.TemporaryDirectory() as tmpdir:
        jsonl = Path(tmpdir) / "codex_events.jsonl"
        jsonl.write_text(
            '{"type":"error","message":"You have hit your usage limit for GPT-5.3-Codex-Spark."}\n',
            encoding="utf-8",
        )
        parsed = {
            "cases": [
                {
                    "id": "explicit-eval-route",
                    "name": "Explicit eval route",
                    "category": "happy",
                    "tier1_failures": ["[codex] codex returned non-zero exit code: 1"],
                    "runners": {
                        "codex": {
                            "artifacts": {
                                "jsonl": str(jsonl),
                            }
                        }
                    },
                }
            ]
        }

        classified = runner._classify_case_failures(parsed)

    assert len(classified["tool_preflight_cases"]) == 1
    assert classified["tool_preflight_cases"][0]["id"] == "explicit-eval-route"
    assert classified["other_failure_cases"] == []


def test_split_release_can_stop_after_first_tool_preflight_failure() -> None:
    runner = load_runner()

    def run_case(*args):
        return {
            "skill": "he-router",
            "returncode": 1,
            "status": "error",
            "decision": "fail",
            "case_filters": [args[3][0]],
            "failure_classification": {
                "timeout_cases": [],
                "content_failure_cases": [],
                "other_failure_cases": [],
                "tool_preflight_cases": [
                    {
                        "id": args[3][0],
                        "name": args[3][0],
                        "category": None,
                        "tier1_failures": ["codex returned non-zero exit code: 1"],
                    }
                ],
            },
            "errors": [
                {
                    "code": "ERR_CODEX_RUNNER_PREFLIGHT",
                    "message": "Codex live eval runner failed before producing final output.",
                }
            ],
            "raw_output": "",
        }

    runner._list_skill_builder_cases = lambda *args: (["case-a", "case-b"], None)
    runner._run_skill_builder_eval = run_case

    result = runner.run_skill(
        Path("/tmp/repo"),
        "he-router",
        "release",
        "codex",
        (),
        (),
        90,
        None,
        None,
        True,
        Path("/tmp/codex-home"),
    )

    assert result["early_stop_reason"] == "tool_preflight_failure_limit"
    assert result["executed_case_count"] == 1
    assert result["skipped_case_count"] == 1
