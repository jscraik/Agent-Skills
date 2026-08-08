from __future__ import annotations

import http.server
import json
import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.phoenix_observability import (  # noqa: E402
    PhoenixObservabilityError,
    build_phoenix_eval_trace_receipt,
    build_phoenix_mirror_receipt,
    build_phoenix_smoke_receipt,
    build_phoenix_status_receipt,
)
from ask.skills_sdk.phoenix_trace_plan import build_eval_trace_plan  # noqa: E402


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    env.setdefault("ASK_PHOENIX_AUTO_TRACE", "0")
    return env


def _write_trace_runtime(directory: Path) -> tuple[Path, Path]:
    runtime = directory / "fake-otel-python"
    calls = directory / "calls.jsonl"
    runtime.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import pathlib\n"
        "import sys\n"
        "payload = json.loads(sys.stdin.read())\n"
        f"pathlib.Path({calls.as_posix()!r}).open('a', encoding='utf-8').write(json.dumps(payload, sort_keys=True) + '\\n')\n"
        "print(json.dumps({'status': 'pass', 'http_status': 200}))\n",
        encoding="utf-8",
    )
    runtime.chmod(0o755)
    return runtime, calls


def _eval_trace_receipt(case_count: int) -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.eval-run-receipt.v0",
        "status": "pass",
        "operation": "eval_run",
        "runner": "deterministic_jsonl_v0",
        "codex_profile": "oss-local",
        "case_count": case_count,
        "passed_count": case_count,
        "failed_count": 0,
        "cases": [
            {"case_id": f"case-{index}", "status": "pass", "score": 1}
            for index in range(case_count)
        ],
    }


def _ab_variant(label: str, profile: str, output_digest: str, stdout_digest: str) -> dict[str, object]:
    return {
        "variant_label": label,
        "status": "pass",
        "exit_code": 0,
        "command_argv": ["codex", "exec", "--profile", profile, "--json", "-"],
        "output_last_message_digest": "sha256:" + (output_digest * 64),
        "runner_stdout_digest": "sha256:" + (stdout_digest * 64),
    }


def _ab_profile_receipt() -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.ab-run-receipt.v1",
        "status": "completed",
        "operation": "ab_run",
        "execution_profile": {"id": "codex-read-only"},
        "judge_profile": {"id": "oss-local", "codex_profile": "oss-local"},
        "experiment_id": "a" * 16,
        "variant_results": [
            _ab_variant("A", "oss-local", "a", "b"),
            _ab_variant("B", "oss-cloud", "c", "d"),
        ],
    }


_JUDGE_RUNTIME_ARGV = [
    "bash", "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh", "--env-file",
    "<operator-approved-opaque-env-stream>", "--require-env", "OLLAMA_API_KEY", "--", "bash",
    "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh", "--profile", "oss-cloud",
    "--strict-config", "--sandbox", "read-only", "--ephemeral", "--json", "-",
]
_JUDGE_LOGICAL_SHAPE = [
    "codex", "exec", "--profile", "oss-cloud", "--strict-config", "--sandbox", "read-only",
    "--ephemeral", "--json", "-",
]


def _judge_cloud_receipt() -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.ab-judge-score-receipt.v0",
        "status": "scored",
        "operation": "ab_judge_score",
        "judge_profile": {"id": "oss-cloud", "codex_profile": "oss-cloud"},
        "codex_profile": "oss-cloud",
        "codex_exec_invoked": True,
        "provider_invoked": True,
        "network_accessed": True,
        "mutation_performed": True,
        "judge_command_argv": _JUDGE_RUNTIME_ARGV,
        "judge_command_shape": _JUDGE_LOGICAL_SHAPE,
        "decision": {"winner": "inconclusive"},
    }


class _PhoenixHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("x-phoenix-server-version", "test-phoenix")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


class TestSkillsSdkPhoenixObservability(unittest.TestCase):
    def _serve_phoenix(self) -> tuple[http.server.HTTPServer, str]:
        server = http.server.HTTPServer(("127.0.0.1", 0), _PhoenixHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, f"http://127.0.0.1:{server.server_port}"

    def _write_receipt(self, directory: Path, *, include_raw: bool = False, codex_exec_invoked: bool = True) -> Path:
        receipt = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "status": "pass",
            "operation": "eval_run",
            "target_path": "Skills/example/SKILL.md",
            "package_id": "example",
            "package_digest": "sha256:" + ("a" * 64),
            "runner": "codex",
            "mode": "release",
            "codex_profile": "oss-local",
            "codex_exec_invoked": codex_exec_invoked,
            "cases": [
                {
                    "case_id": "local-case",
                    "status": "pass",
                    "score": 1,
                }
            ],
        }
        if codex_exec_invoked:
            receipt["codex_exec_command_shape"] = [
                "codex",
                "exec",
                "--profile",
                "oss-local",
                "--sandbox",
                "read-only",
                "-",
            ]
        if include_raw:
            receipt["prompt"] = "raw prompt must never enter mirror rows"
            receipt["cases"][0]["output"] = "raw output must never enter mirror rows"
        path = directory / "eval-run.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path

    def test_status_receipt_checks_reachable_phoenix_endpoint(self) -> None:
        server, base_url = self._serve_phoenix()
        self.addCleanup(server.shutdown)

        receipt = build_phoenix_status_receipt(REPO_ROOT, base_url=base_url, timeout_seconds=2)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["server_version"], "test-phoenix")
        self.assertEqual(receipt["otlp_http_endpoint"], f"{base_url}/v1/traces")
        self.assertFalse(receipt["mutation_performed"])

    def test_repo_config_keeps_generic_tracing_opt_in_and_pins_eval_project(self) -> None:
        config = json.loads(
            (REPO_ROOT / "Infrastructure/config/observability/phoenix.json").read_text(encoding="utf-8")
        )
        compose = (REPO_ROOT / "Infrastructure/config/observability/compose.phoenix.yaml").read_text(
            encoding="utf-8"
        )

        self.assertFalse(config["enabled"])
        self.assertFalse(config["eval_tracing_enabled"])
        self.assertEqual(config["project_name"], "agent-skills-skills-sdk-evals")
        self.assertEqual(config["model"], "qwen3.5:9b-mlx")
        self.assertEqual(config["provider"], "ollama")
        self.assertEqual(config["otel_python"], "~/.agents/otel-collector/.venv/bin/python")
        self.assertIn("arizephoenix/phoenix@sha256:", compose)
        self.assertIn("ASK_PHOENIX_DATA_DIR:?", compose)
        self.assertIn('127.0.0.1:6006:6006', compose)
        self.assertIn('127.0.0.1:4317:4317', compose)
        self.assertIn("PHOENIX_WORKING_DIR: /mnt/data", compose)

    def test_mirror_preview_whitelists_receipt_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = self._write_receipt(Path(temp_dir))

            receipt = build_phoenix_mirror_receipt(REPO_ROOT, receipt_path=receipt_path.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["row_count"], 2)
        serialized = json.dumps(receipt["preview_rows"], sort_keys=True)
        self.assertIn("oss-local", serialized)
        self.assertIn("codex_exec_invoked", serialized)
        self.assertNotIn("raw prompt", serialized)
        self.assertNotIn("raw output", serialized)
        self.assertIn({"id": "mirror_redaction", "status": "pass", "severity": "info", "message": "Source receipts mirrored into Phoenix must not contain raw prompts, transcripts, messages, tool calls, stdout, stderr, or outputs.", "evidence": ["raw_keys_seen:0"]}, receipt["checks"])

    def test_mirror_blocks_raw_source_receipt_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = self._write_receipt(Path(temp_dir), include_raw=True)

            with pytest.raises(PhoenixObservabilityError) as raised:
                build_phoenix_mirror_receipt(REPO_ROOT, receipt_path=receipt_path.as_posix())

        receipt = raised.value.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("mirror_redaction", {check["id"] for check in receipt["blockers"]})

    def test_mirror_blocks_oss_profile_without_codex_exec_proof(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = self._write_receipt(Path(temp_dir), codex_exec_invoked=False)

            with pytest.raises(PhoenixObservabilityError) as raised:
                build_phoenix_mirror_receipt(REPO_ROOT, receipt_path=receipt_path.as_posix())

        receipt = raised.value.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("oss_profile_execution_contract", {check["id"] for check in receipt["blockers"]})

    def test_mirror_blocks_generic_json_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "generic.json"
            with path.open("w", encoding="utf-8") as handle:
                json.dump({"schema_version": "not-an-eval.v0", "status": "pass"}, handle)
                handle.write("\n")

            with pytest.raises(PhoenixObservabilityError) as raised:
                build_phoenix_mirror_receipt(REPO_ROOT, receipt_path=path.as_posix())

        receipt = raised.value.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("source_kind_supported", {check["id"] for check in receipt["blockers"]})

    def test_mirror_write_emits_jsonl_when_out_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            receipt_path = self._write_receipt(root)
            out_path = root / "phoenix.jsonl"

            receipt = build_phoenix_mirror_receipt(
                REPO_ROOT,
                receipt_path=receipt_path.as_posix(),
                out_path=out_path.as_posix(),
                write=True,
            )

            lines = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(receipt["status"], "written")
        self.assertEqual(receipt["row_count"], 2)
        self.assertEqual(lines[0]["event_type"], "phoenix_eval_receipt_mirror")
        self.assertTrue(receipt["mutation_performed"])

    def test_mirror_write_blocks_ambiguous_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            receipt_path = self._write_receipt(root)
            out_path = root / "phoenix.json"

            with pytest.raises(PhoenixObservabilityError) as raised:
                build_phoenix_mirror_receipt(
                    REPO_ROOT,
                    receipt_path=receipt_path.as_posix(),
                    out_path=out_path.as_posix(),
                    write=True,
                )

        receipt = raised.value.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("output_path_allowed", {check["id"] for check in receipt["blockers"]})

    def test_smoke_blocks_when_configured_otel_runtime_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_python = Path(temp_dir) / "missing-python"

            receipt = build_phoenix_smoke_receipt(
                REPO_ROOT,
                base_url="http://127.0.0.1:6006",
                otel_python_path=missing_python.as_posix(),
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("otel_python_available", {check["id"] for check in receipt["blockers"]})
        self.assertFalse(receipt["mutation_performed"])

    def test_smoke_uses_configured_otel_runtime_for_protobuf_export(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "fake-otel-python"
            runtime.write_text(
                """#!/usr/bin/env python3
import json
import sys

payload = json.loads(sys.stdin.read())
assert payload["endpoint"] == "http://127.0.0.1:6006/v1/traces"
assert payload["profile"] == "oss-cloud"
assert payload["project_name"] == "agent-skills-skills-sdk-evals"
print(json.dumps({"status": "pass", "http_status": 200}))
""",
                encoding="utf-8",
            )
            runtime.chmod(0o755)

            receipt = build_phoenix_smoke_receipt(
                REPO_ROOT,
                base_url="http://127.0.0.1:6006",
                profile="oss-cloud",
                otel_python_path=runtime.as_posix(),
            )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["span_name"], "agent-skills.phoenix.smoke")
        self.assertEqual(receipt["profile"], "oss-cloud")
        self.assertEqual(receipt["project_name"], "agent-skills-skills-sdk-evals")
        self.assertEqual(receipt["otel_python_path"], runtime.as_posix())
        self.assertTrue(receipt["mutation_performed"])
        self.assertIn("agent-skills-skills-sdk-evals", receipt["agent_summary"])

    def test_smoke_expands_user_otel_runtime_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / ".agents" / "otel-python"
            runtime.parent.mkdir()
            runtime.write_text(
                """#!/usr/bin/env python3
import json
import sys

json.loads(sys.stdin.read())
print(json.dumps({"status": "pass", "http_status": 200}))
""",
                encoding="utf-8",
            )
            runtime.chmod(0o755)
            with patch.dict(os.environ, {"HOME": temp_dir}, clear=False):
                receipt = build_phoenix_smoke_receipt(
                    REPO_ROOT,
                    base_url="http://127.0.0.1:6006",
                    otel_python_path="~/.agents/otel-python",
                )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["otel_python_path"], runtime.as_posix())

    def test_smoke_blocks_project_routing_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "Infrastructure" / "config" / "observability"
            config_dir.mkdir(parents=True)
            (config_dir / "phoenix.json").write_text(
                json.dumps({"project_name": "wrong-project"}),
                encoding="utf-8",
            )
            runtime = root / "fake-otel-python"
            runtime.write_text(
                """#!/usr/bin/env python3
import json
import sys

json.loads(sys.stdin.read())
print(json.dumps({"status": "pass", "http_status": 200}))
""",
                encoding="utf-8",
            )
            runtime.chmod(0o755)

            receipt = build_phoenix_smoke_receipt(
                root,
                base_url="http://127.0.0.1:6006",
                otel_python_path=runtime.as_posix(),
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["project_name"], "agent-skills-skills-sdk-evals")
        self.assertIn("phoenix_project_name", {check["id"] for check in receipt["blockers"]})
        project_check = next(check for check in receipt["checks"] if check["id"] == "phoenix_project_name")
        self.assertEqual(project_check["evidence"], ["wrong-project"])
        self.assertFalse(receipt["mutation_performed"])

    def test_smoke_records_optional_llm_model_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "fake-otel-python"
            runtime.write_text(
                """#!/usr/bin/env python3
import json
import sys

payload = json.loads(sys.stdin.read())
assert payload["span_kind"] == "LLM"
assert payload["model_name"] == "qwen/qwen3-coder"
assert payload["provider"] == "local-oss"
assert payload["prompt_tokens"] == 11
assert payload["completion_tokens"] == 7
print(json.dumps({"status": "pass", "http_status": 200}))
""",
                encoding="utf-8",
            )
            runtime.chmod(0o755)

            receipt = build_phoenix_smoke_receipt(
                REPO_ROOT,
                base_url="http://127.0.0.1:6006",
                profile="oss-local",
                model_name="qwen/qwen3-coder",
                provider="local-oss",
                prompt_tokens=11,
                completion_tokens=7,
                otel_python_path=runtime.as_posix(),
            )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["span_kind"], "LLM")
        self.assertEqual(receipt["span_name"], "agent-skills.phoenix.qwen/qwen3-coder")
        self.assertEqual(receipt["model_name"], "qwen/qwen3-coder")
        self.assertEqual(receipt["provider"], "local-oss")
        self.assertEqual(receipt["total_tokens"], 18)

    def test_smoke_records_optional_ask_command_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "fake-otel-python"
            runtime.write_text(
                """#!/usr/bin/env python3
import json
import sys

payload = json.loads(sys.stdin.read())
assert payload["command_name"] == "repo status --json --robot"
assert payload["command_status"] == "success"
assert payload["latency_ms"] == 12
print(json.dumps({"status": "pass", "http_status": 200}))
""",
                encoding="utf-8",
            )
            runtime.chmod(0o755)

            receipt = build_phoenix_smoke_receipt(
                REPO_ROOT,
                base_url="http://127.0.0.1:6006",
                command_name="repo status --json --robot",
                command_status="success",
                latency_ms=12,
                otel_python_path=runtime.as_posix(),
            )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["command_name"], "repo status --json --robot")
        self.assertEqual(receipt["command_status"], "success")
        self.assertEqual(receipt["latency_ms"], 12)

    def test_smoke_blocks_negative_llm_token_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "fake-otel-python"
            runtime.write_text("#!/usr/bin/env python3\nraise SystemExit(99)\n", encoding="utf-8")
            runtime.chmod(0o755)

            receipt = build_phoenix_smoke_receipt(
                REPO_ROOT,
                base_url="http://127.0.0.1:6006",
                model_name="qwen/qwen3-coder",
                prompt_tokens=-1,
                otel_python_path=runtime.as_posix(),
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("llm_token_counts_valid", {check["id"] for check in receipt["blockers"]})
        self.assertFalse(receipt["mutation_performed"])

    def test_eval_trace_receipt_emits_run_and_case_spans_from_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, calls = _write_trace_runtime(Path(temp_dir))

            trace_receipt = build_phoenix_eval_trace_receipt(
                REPO_ROOT,
                eval_receipt=_eval_trace_receipt(1),
                base_url="http://127.0.0.1:6006",
                otel_python_path=runtime.as_posix(),
                enabled=True,
            )
            payloads = [json.loads(line) for line in calls.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(trace_receipt["status"], "pass")
        self.assertEqual(trace_receipt["observability_status"], "emitted")
        self.assertEqual(trace_receipt["emitted_span_count"], 6)
        self.assertTrue(trace_receipt["case_span_trace_enabled"])
        self.assertEqual(trace_receipt["case_span_count"], 1)
        self.assertEqual(payloads[0]["plan"]["project_name"], "agent-skills-skills-sdk-evals")
        self.assertEqual(len(payloads[0]["plan"]["spans"]), 6)
        self.assertEqual({span["trace_id"] for span in trace_receipt["emitted_spans"]}, {trace_receipt["trace_id"]})

    def test_eval_trace_case_spans_are_opt_in_and_capped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, calls = _write_trace_runtime(Path(temp_dir))

            trace_receipt = build_phoenix_eval_trace_receipt(
                REPO_ROOT,
                eval_receipt=_eval_trace_receipt(30),
                base_url="http://127.0.0.1:6006",
                otel_python_path=runtime.as_posix(),
                enabled=True,
                trace_case_spans=True,
                case_span_limit=50,
            )
            payloads = [json.loads(line) for line in calls.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(trace_receipt["status"], "pass")
        self.assertEqual(trace_receipt["emitted_span_count"], 44)
        self.assertTrue(trace_receipt["case_span_trace_enabled"])
        self.assertEqual(trace_receipt["case_span_limit"], 20)
        self.assertEqual(trace_receipt["case_span_count"], 20)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(len(payloads[0]["plan"]["spans"]), 44)

    def test_eval_trace_blocks_raw_eval_receipts(self) -> None:
        trace_receipt = build_phoenix_eval_trace_receipt(
            REPO_ROOT,
            eval_receipt={
                "schema_version": "skills-sdk.eval-run-receipt.v0",
                "status": "pass",
                "operation": "eval_run",
                "output": "raw output must not be traced",
            },
        )

        self.assertEqual(trace_receipt["status"], "blocked")
        self.assertIn("eval_trace_redaction", {check["id"] for check in trace_receipt["blockers"]})
        self.assertFalse(trace_receipt["mutation_performed"])

    def test_ab_trace_keeps_ordered_runtime_profiles_and_metadata_profiles_separate(self) -> None:
        trace_receipt = build_phoenix_eval_trace_receipt(
            REPO_ROOT, eval_receipt=_ab_profile_receipt(), enabled=False
        )

        self.assertEqual(trace_receipt["status"], "pass")
        self.assertEqual(trace_receipt["observability_status"], "not_run")
        self.assertEqual(
            [row["derived_codex_profile"] for row in trace_receipt["profile_evidence"]],
            ["oss-local", "oss-cloud"],
        )
        root_attributes = trace_receipt["span_plan"][0]["attributes"]
        self.assertEqual(root_attributes["skills_sdk.execution_profile"], "codex-read-only")
        self.assertEqual(root_attributes["skills_sdk.judge_profile"], "oss-local")
        generation_spans = [span for span in trace_receipt["span_plan"] if span["name"] == "skills-sdk.eval.generation"]
        self.assertEqual(
            [span["attributes"]["skills_sdk.codex_profile"] for span in generation_spans],
            ["oss-local", "oss-cloud"],
        )

    def test_ab_trace_accepts_selected_cloud_lane(self) -> None:
        receipt = {
            "schema_version": "skills-sdk.ab-run-receipt.v1",
            "status": "completed",
            "operation": "ab_run",
            "execution_lane": "oss-cloud",
            "codex_profile": "oss-cloud",
            "runtime_profile_gates": [{"lane": "oss-cloud", "codex_profile": "oss-cloud"}],
            "variant_results": [
                {
                    "variant_label": "A",
                    "status": "pass",
                    "exit_code": 0,
                    "codex_profile": "oss-cloud",
                    "command_argv": ["codex", "exec", "--profile", "oss-cloud", "--json", "-"],
                },
                {
                    "variant_label": "B",
                    "status": "pass",
                    "exit_code": 0,
                    "codex_profile": "oss-cloud",
                    "command_argv": ["codex", "exec", "--profile", "oss-cloud", "--json", "-"],
                },
            ],
        }

        plan = build_eval_trace_plan(receipt)

        self.assertEqual(plan["blockers"], [])
        self.assertEqual(
            [row["derived_codex_profile"] for row in plan["profile_evidence"]],
            ["oss-cloud", "oss-cloud"],
        )

    def test_judge_trace_accepts_configs_wrapped_runtime_with_logical_shape(self) -> None:
        trace_receipt = build_phoenix_eval_trace_receipt(
            REPO_ROOT, eval_receipt=_judge_cloud_receipt(), enabled=False
        )

        self.assertEqual(trace_receipt["status"], "pass")
        self.assertEqual(trace_receipt["observability_status"], "not_run")
        self.assertEqual(trace_receipt["profile_evidence"][0]["derived_codex_profile"], "oss-cloud")
        self.assertEqual(trace_receipt["profile_evidence"][0]["blockers"], [])

    def test_judge_trace_blocks_shape_that_does_not_match_runtime_argv(self) -> None:
        receipt = {
            "schema_version": "skills-sdk.ab-judge-score-receipt.v0",
            "status": "scored",
            "operation": "ab_judge_score",
            "judge_profile": {"id": "oss-cloud", "codex_profile": "oss-cloud"},
            "codex_profile": "oss-cloud",
            "codex_exec_invoked": True,
            "provider_invoked": True,
            "network_accessed": True,
            "mutation_performed": True,
            "judge_command_argv": [
                "bash",
                "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh",
                "--env-file",
                "<operator-approved-opaque-env-stream>",
                "--require-env",
                "OLLAMA_API_KEY",
                "--",
                "bash",
                "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh",
                "--profile",
                "oss-cloud",
                "--strict-config",
                "--sandbox",
                "read-only",
                "--ephemeral",
                "--json",
                "-",
            ],
            "judge_command_shape": ["codex", "exec", "--profile", "oss-local"],
        }

        plan = build_eval_trace_plan(receipt)

        self.assertIn("judge_command_shape_mismatch", plan["blockers"])
        self.assertEqual(plan["profile_evidence"][0]["status"], "blocked")

    def test_ab_trace_uses_first_runtime_gate_for_all_lane_top_level_variants(self) -> None:
        receipt = {
            "schema_version": "skills-sdk.ab-run-receipt.v1",
            "status": "completed",
            "operation": "ab_run",
            "execution_lane": "all",
            "codex_profile": "oss-local",
            "runtime_profile_gates": [
                {"lane": "oss-local", "codex_profile": "oss-local"},
                {"lane": "oss-cloud", "codex_profile": "oss-cloud"},
            ],
            "variant_results": [
                {
                    "variant_label": "A",
                    "status": "pass",
                    "exit_code": 0,
                    "codex_profile": "oss-local",
                    "command_argv": ["codex", "exec", "--profile", "oss-local", "--json", "-"],
                },
                {
                    "variant_label": "B",
                    "status": "pass",
                    "exit_code": 0,
                    "codex_profile": "oss-local",
                    "command_argv": ["codex", "exec", "--profile", "oss-local", "--json", "-"],
                },
            ],
        }

        plan = build_eval_trace_plan(receipt)

        self.assertEqual(plan["blockers"], [])
        self.assertEqual(
            [row["derived_codex_profile"] for row in plan["profile_evidence"]],
            ["oss-local", "oss-local"],
        )

    def test_ab_trace_blocks_explicit_all_lane_without_runtime_gates(self) -> None:
        plan = build_eval_trace_plan(
            {
                "schema_version": "skills-sdk.ab-run-receipt.v1",
                "status": "completed",
                "operation": "ab_run",
                "execution_lane": "all",
                "codex_profile": "oss-local",
                "runtime_profile_gates": [],
                "variant_results": [
                    {
                        "variant_label": "A",
                        "status": "pass",
                        "codex_profile": "oss-local",
                        "command_argv": ["codex", "exec", "--profile", "oss-local", "--json", "-"],
                    },
                    {
                        "variant_label": "B",
                        "status": "pass",
                        "codex_profile": "oss-cloud",
                        "command_argv": ["codex", "exec", "--profile", "oss-cloud", "--json", "-"],
                    },
                ],
            }
        )

        self.assertTrue(plan["blockers"])
        self.assertTrue(
            any("profile_order_required:selected-execution-lane" in blocker for blocker in plan["blockers"])
        )

    def test_ab_trace_rejects_metadata_only_duplicate_substituted_and_reordered_profiles(self) -> None:
        counterexamples = {
            "judge_metadata_only": [
                ["codex", "exec", "--json", "-"],
                ["codex", "exec", "--json", "-"],
            ],
            "duplicate": [
                ["codex", "exec", "--profile", "oss-local", "--profile", "oss-cloud", "-"],
                ["codex", "exec", "--profile", "oss-cloud", "-"],
            ],
            "substituted": [
                ["codex", "exec", "--profile", "oss-local-code", "-"],
                ["codex", "exec", "--profile", "oss-cloud", "-"],
            ],
            "reordered": [
                ["codex", "exec", "--profile", "oss-cloud", "-"],
                ["codex", "exec", "--profile", "oss-local", "-"],
            ],
        }
        for label, commands in counterexamples.items():
            with self.subTest(label=label):
                plan = build_eval_trace_plan(
                    {
                        "schema_version": "skills-sdk.ab-run-receipt.v1",
                        "status": "completed",
                        "operation": "ab_run",
                        "judge_profile": {"id": "oss-local", "codex_profile": "oss-local"},
                        "variant_results": [
                            {"variant_label": "A", "status": "pass", "command_argv": commands[0]},
                            {"variant_label": "B", "status": "pass", "command_argv": commands[1]},
                        ],
                    }
                )

                self.assertTrue(plan["blockers"])
                self.assertNotEqual(
                    [row["derived_codex_profile"] for row in plan["profile_evidence"]],
                    ["oss-local", "oss-cloud"],
                )

if __name__ == "__main__":
    unittest.main()
