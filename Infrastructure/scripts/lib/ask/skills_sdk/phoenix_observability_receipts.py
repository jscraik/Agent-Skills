from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ask.skills_sdk.phoenix_observability_support import (
    PHOENIX_ACCEPTANCE_TRACE,
    PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT,
    PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT,
    PHOENIX_EVAL_TRACE_SCHEMA_URI,
    PHOENIX_EVAL_TRACE_SCHEMA_VERSION,
    PHOENIX_MIRROR_SCHEMA_URI,
    PHOENIX_MIRROR_SCHEMA_VERSION,
    PHOENIX_SMOKE_SCHEMA_URI,
    PHOENIX_SMOKE_SCHEMA_VERSION,
    PHOENIX_STATUS_SCHEMA_URI,
    PHOENIX_STATUS_SCHEMA_VERSION,
    OSS_CODEX_PROFILES,
    SUPPORTED_SOURCE_KINDS,
    PhoenixObservabilityError,
    _check,
    _find_receipt,
    _mirror_contract_errors,
    _mirror_rows,
    _oss_profile_errors,
    _path_allowed,
    _raw_key_paths,
    _repo_relative,
    _safe_path_value,
    _sha256_bytes,
    _sha256_json,
    _source_kind,
    _write_jsonl,
)
from ask.skills_sdk.phoenix_trace_plan import PHOENIX_PROJECT_NAME


_SMOKE_SCRIPT = r'''
import json
import time
import urllib.error
import urllib.request
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.common.v1.common_pb2 import AnyValue, KeyValue
from opentelemetry.proto.resource.v1.resource_pb2 import Resource
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, ScopeSpans, Span, Status

cfg = json.loads(__import__("sys").stdin.read())
now = time.time_ns()

def kv(key, value):
    any_value = AnyValue()
    if isinstance(value, bool):
        any_value.bool_value = value
    elif isinstance(value, int):
        any_value.int_value = value
    else:
        any_value.string_value = str(value)
    return KeyValue(key=key, value=any_value)

attributes = [
    kv("codex.repo", cfg["repo_name"]),
    kv("codex.workflow", "oss-eval-observability"),
    kv("codex.profile", cfg["profile"]),
    kv("codex.guardrail.redacted", True),
    kv("codex.guardrail.source_kind", "observability_receipt"),
    kv("codex.validation.phoenix_status", "pass"),
    kv("codex.validation.mirror_contract", "pass"),
    kv("codex.acceptance_trace", ",".join(cfg["acceptance_trace"])),
    kv("openinference.span.kind", cfg["span_kind"]),
]
if cfg.get("command_name"):
    attributes.extend([
        kv("ask.command", cfg["command_name"]),
        kv("ask.status", cfg["command_status"] or "unknown"),
    ])
if cfg.get("latency_ms") is not None:
    attributes.append(kv("ask.latency_ms", int(cfg["latency_ms"])))
if cfg.get("model_name"):
    total_tokens = int(cfg["prompt_tokens"]) + int(cfg["completion_tokens"])
    attributes.extend([
        kv("llm.model_name", cfg["model_name"]),
        kv("llm.provider", cfg["provider"] or cfg["profile"]),
        kv("llm.token_count.prompt", int(cfg["prompt_tokens"])),
        kv("llm.token_count.completion", int(cfg["completion_tokens"])),
        kv("llm.token_count.total", total_tokens),
        kv("gen_ai.request.model", cfg["model_name"]),
        kv("gen_ai.response.model", cfg["model_name"]),
        kv("gen_ai.system", cfg["provider"] or cfg["profile"]),
        kv("gen_ai.usage.input_tokens", int(cfg["prompt_tokens"])),
        kv("gen_ai.usage.output_tokens", int(cfg["completion_tokens"])),
    ])

span = Span(
    trace_id=bytes.fromhex(cfg["trace_id"]),
    span_id=bytes.fromhex(cfg["span_id"]),
    name=cfg["span_name"],
    kind=Span.SPAN_KIND_INTERNAL,
    start_time_unix_nano=now,
    end_time_unix_nano=now + 1000000,
    attributes=attributes,
    status=Status(code=Status.STATUS_CODE_OK),
)
request = ExportTraceServiceRequest(
    resource_spans=[
        ResourceSpans(
            resource=Resource(attributes=[
                kv("service.name", "agent-skills"),
                kv("openinference.project.name", cfg["project_name"]),
            ]),
            scope_spans=[ScopeSpans(spans=[span])],
        )
    ]
)
http_request = urllib.request.Request(
    cfg["endpoint"],
    data=request.SerializeToString(),
    headers={
        "content-type": "application/x-protobuf",
        "x-project-name": cfg["project_name"],
    },
    method="POST",
)
try:
    with urllib.request.urlopen(http_request, timeout=cfg["timeout_seconds"]) as response:
        print(json.dumps({"status": "pass", "http_status": response.status}))
except urllib.error.HTTPError as exc:
    print(json.dumps({"service": "agent-skills", "status": "blocked", "http_status": exc.code, "error_class": type(exc).__name__}))
    raise SystemExit(2)
except (urllib.error.URLError, TimeoutError) as exc:
    print(json.dumps({"service": "agent-skills", "status": "blocked", "error_class": type(exc).__name__}))
    raise SystemExit(2)
'''


def _phoenix_config(repo_root: Path) -> dict[str, Any]:
    config_path = repo_root / "Infrastructure" / "config" / "observability" / "phoenix.json"
    if not config_path.is_file():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"__config_error__": type(exc).__name__}
    if not isinstance(payload, dict):
        return {"__config_error__": "config_top_level_not_object"}
    return payload


def _config_checks(config: dict[str, Any]) -> list[dict[str, Any]]:
    error = config.get("__config_error__")
    if error is None:
        return []
    return [_check("phoenix_config", "blocker", "phoenix.json must be valid UTF-8 JSON with an object at the top level.", [f"error_class:{error}"])]


def _config_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "on"}


def _phoenix_eval_enabled(config: dict[str, Any]) -> bool:
    env_value = os.environ.get("ASK_PHOENIX_EVAL_TRACE")
    if env_value is not None:
        return _config_bool(env_value)
    if "eval_tracing_enabled" in config:
        return _config_bool(config.get("eval_tracing_enabled"))
    return _config_bool(config.get("enabled"))


def _config_path(config: dict[str, Any], key: str) -> Path | None:
    value = config.get(key)
    return Path(value).expanduser() if isinstance(value, str) and value else None


def _status_probe(base_url: str, timeout_seconds: float) -> tuple[list[dict[str, Any]], str | None, int | None, Any]:
    parsed = urlparse(base_url)
    checks = [
        _check(
            "phoenix_base_url",
            "pass" if parsed.scheme in {"http", "https"} and parsed.netloc else "blocker",
            "Phoenix base URL must be an absolute http(s) URL.",
            [base_url],
        )
    ]
    server_version: str | None = None
    http_status: int | None = None
    if checks[0]["status"] == "pass":
        try:
            with urlopen(Request(base_url, method="HEAD"), timeout=timeout_seconds) as response:  # noqa: S310
                http_status = int(response.status)
                server_version = response.headers.get("x-phoenix-server-version")
        except HTTPError as exc:
            http_status = int(exc.code)
        except (OSError, URLError, TimeoutError) as exc:
            checks.append(_check("phoenix_http", "blocker", "Phoenix UI endpoint must respond before traces can be trusted.", [f"error_class:{type(exc).__name__}"]))
        else:
            checks.append(_check("phoenix_http", "pass", "Phoenix UI endpoint responded.", [f"status:{http_status}"]))
    return checks, server_version, http_status, parsed


def _status_payload(base_url: str, checks: list[dict[str, Any]], server_version: str | None, http_status: int | None, parsed: Any) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "blocked" if blockers else "pass"
    return {
        "schema_version": PHOENIX_STATUS_SCHEMA_VERSION,
        "schema_uri": PHOENIX_STATUS_SCHEMA_URI,
        "status": status,
        "operation": "phoenix_status_check",
        "base_url": base_url,
        "ui_url": base_url,
        "otlp_http_endpoint": base_url.rstrip("/") + "/v1/traces",
        "otlp_grpc_endpoint": "http://localhost:4317" if parsed.hostname in {"localhost", "127.0.0.1"} else None,
        "server_version": server_version,
        "http_status": http_status,
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "acceptance_trace": list(PHOENIX_ACCEPTANCE_TRACE),
        "agent_summary": f"Phoenix is reachable at {base_url}; traces can target {base_url.rstrip('/')}/v1/traces." if status == "pass" else f"Phoenix is not reachable at {base_url}; start the Docker service and rerun the status check.",
    }


def build_phoenix_status_receipt(repo_root: Path, *, base_url: str = "http://localhost:6006", timeout_seconds: float = 2.0) -> dict[str, Any]:
    del repo_root
    checks, server_version, http_status, parsed = _status_probe(base_url, timeout_seconds)
    return _status_payload(base_url, checks, server_version, http_status, parsed)


def _smoke_identity(repo_root: Path, base_url: str, profile: str, config: dict[str, Any], model_name: str | None) -> dict[str, Any]:
    parsed = urlparse(base_url)
    project_name = PHOENIX_PROJECT_NAME
    configured_project_name = config.get("project_name")
    checks = [
        _check("phoenix_base_url", "pass" if parsed.scheme in {"http", "https"} and parsed.netloc else "blocker", "Phoenix base URL must be an absolute http(s) URL.", [base_url]),
        _check("phoenix_project_name", "pass" if "project_name" not in config or configured_project_name == project_name else "blocker", "Phoenix traces must target the Skills SDK eval project.", [str(configured_project_name) if configured_project_name is not None else project_name]),
        _check("oss_profile_supported", "pass" if profile in OSS_CODEX_PROFILES else "blocker", "Phoenix smoke traces are restricted to declared OSS Codex profiles.", [profile]),
    ]
    span_kind = "LLM" if model_name else "WORKFLOW"
    span_name = f"agent-skills.phoenix.{model_name}" if model_name else "agent-skills.phoenix.smoke"
    return {"endpoint": base_url.rstrip("/") + "/v1/traces", "project_name": project_name, "span_kind": span_kind, "span_name": span_name, "trace_id": uuid.uuid4().hex, "span_id": uuid.uuid4().hex[:16], "checks": checks, "repo_name": repo_root.name}


def _smoke_checks(identity: dict[str, Any], prompt_tokens: int, completion_tokens: int, otel_python: Path | None) -> list[dict[str, Any]]:
    checks = list(identity["checks"])
    token_errors = [name for name, value in (("prompt_tokens_negative", prompt_tokens), ("completion_tokens_negative", completion_tokens)) if value < 0]
    checks.append(_check("llm_token_counts_valid", "pass" if not token_errors else "blocker", "Phoenix LLM smoke token counts must be non-negative integers.", token_errors))
    checks.append(_check("otel_python_available", "pass" if otel_python is not None and otel_python.is_file() else "blocker", "Phoenix smoke emission requires an explicit --otel-python path, ASK_PHOENIX_OTEL_PYTHON, or phoenix.json otel_python.", [otel_python.as_posix()] if otel_python is not None else ["missing_explicit_otel_python"]))
    return checks


def _smoke_export(identity: dict[str, Any], repo_root: Path, profile: str, model_name: str | None, provider: str | None, prompt_tokens: int, completion_tokens: int, command_name: str | None, command_status: str | None, latency_ms: int | None, timeout_seconds: float, otel_python: Path) -> tuple[bool, str | None]:
    config = {**identity, "repo_name": repo_root.name, "profile": profile, "model_name": model_name, "provider": provider, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "command_name": command_name, "command_status": command_status, "latency_ms": latency_ms, "timeout_seconds": timeout_seconds, "acceptance_trace": PHOENIX_ACCEPTANCE_TRACE}
    try:
        process = subprocess.run([otel_python.as_posix(), "-c", _SMOKE_SCRIPT], input=json.dumps(config, sort_keys=True), text=True, capture_output=True, check=False, timeout=timeout_seconds + 1.0)
        try:
            result = json.loads(process.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            result = {"status": "blocked", "error": "missing_json_export_result"}
        if process.returncode == 0 and result.get("status") == "pass":
            return True, None
        return False, ":".join(("ExportProcessFailed", str(process.returncode), str(result.get("error_class") or "ExportRejected")))
    except subprocess.TimeoutExpired:
        return False, "TimeoutExpired"
    except OSError as exc:
        return False, type(exc).__name__


def _smoke_payload(identity: dict[str, Any], checks: list[dict[str, Any]], profile: str, model_name: str | None, provider: str | None, prompt_tokens: int, completion_tokens: int, command_name: str | None, command_status: str | None, latency_ms: int | None, otel_python: Path | None) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "blocked" if blockers else "pass"
    emitted = not blockers
    return {"schema_version": PHOENIX_SMOKE_SCHEMA_VERSION, "schema_uri": PHOENIX_SMOKE_SCHEMA_URI, "status": status, "operation": "phoenix_smoke_trace", "base_url": identity["endpoint"].removesuffix("/v1/traces"), "otlp_http_endpoint": identity["endpoint"], "project_name": identity["project_name"], "span_name": identity["span_name"], "span_kind": identity["span_kind"], "trace_id": identity["trace_id"], "span_id": identity["span_id"], "profile": profile, "model_name": model_name, "provider": provider, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens, "command_name": command_name, "command_status": command_status, "latency_ms": latency_ms, "otel_python_path": otel_python.as_posix() if otel_python is not None else None, "timestamp_unix_seconds": int(time.time()), "checks": checks, "blockers": blockers, "mutation_performed": emitted, "acceptance_trace": list(PHOENIX_ACCEPTANCE_TRACE), "agent_summary": f"Phoenix {identity['span_kind'].lower()} smoke trace emitted to project {identity['project_name']} at {identity['endpoint']}; refresh that project's Tracing view." if status == "pass" else f"Phoenix smoke trace is blocked for {identity['endpoint']}."}


def _build_phoenix_smoke_receipt(repo_root: Path, *, base_url: str = "http://localhost:6006", profile: str = "oss-local", timeout_seconds: float = 10.0, otel_python_path: str | None = None, model_name: str | None = None, provider: str | None = None, prompt_tokens: int = 0, completion_tokens: int = 0, command_name: str | None = None, command_status: str | None = None, latency_ms: int | None = None) -> dict[str, Any]:
    config = _phoenix_config(repo_root)
    identity = _smoke_identity(repo_root, base_url, profile, config, model_name)
    otel_python = Path(otel_python_path).expanduser() if otel_python_path else _config_path(config, "otel_python")
    checks = _config_checks(config) + _smoke_checks(identity, prompt_tokens, completion_tokens, otel_python)
    if not [check for check in checks if check["status"] == "blocker"] and otel_python is not None:
        emitted, error = _smoke_export(identity, repo_root, profile, model_name, provider, prompt_tokens, completion_tokens, command_name, command_status, latency_ms, timeout_seconds, otel_python)
        checks.append(_check("phoenix_otlp_export", "pass" if emitted else "blocker", "Phoenix OTLP HTTP endpoint must accept a deterministic smoke span.", [identity["endpoint"]] if error is None else [identity["endpoint"], error]))
    return _smoke_payload(identity, checks, profile, model_name, provider, prompt_tokens, completion_tokens, command_name, command_status, latency_ms, otel_python)


def _eval_plan(eval_receipt: dict[str, Any], trace_case_spans: bool, case_span_limit: int) -> tuple[dict[str, Any], str, str, Any, int]:
    from ask.skills_sdk.phoenix_trace_plan import build_eval_trace_plan  # noqa: PLC0415

    bounded_limit = max(0, min(case_span_limit, PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT))
    source_digest = _sha256_json(eval_receipt)
    plan_receipt = dict(eval_receipt)
    cases = eval_receipt.get("cases")
    if isinstance(cases, list):
        plan_receipt["cases"] = cases[:bounded_limit] if trace_case_spans else []
    return build_eval_trace_plan(plan_receipt, source_digest=source_digest), source_digest, _source_kind(eval_receipt), cases, bounded_limit


def _eval_checks(eval_receipt: dict[str, Any], plan: dict[str, Any], source_kind: str, profile: str | None) -> list[dict[str, Any]]:
    raw_paths = _raw_key_paths(eval_receipt)
    checks = [_check("source_kind_supported", "pass" if source_kind in {"eval_run_receipt", "ab_run_receipt", "ab_judge_score_receipt"} else "blocker", "Phoenix eval tracing accepts eval_run_receipt, ab_run_receipt, and ab_judge_score_receipt.", [source_kind]), _check("eval_trace_redaction", "pass" if not raw_paths else "blocker", "Eval trace receipts must not contain raw prompts, outputs, transcripts, tool calls, stdout, or stderr.", [f"raw_keys_seen:{len(raw_paths)}"]), _check("codex_profile_argv_proof", "blocker" if plan["blockers"] else "pass", "Provider-backed eval traces must derive each Codex runtime profile from the executed argv.", list(plan["blockers"]))]
    if profile is not None:
        derived = [row.get("derived_codex_profile") for row in plan["profile_evidence"] if row.get("derived_codex_profile") is not None]
        checks.append(_check("profile_argument_matches_argv", "pass" if not derived or derived == [profile] else "blocker", "The optional observer profile argument must not contradict argv-derived runtime profile evidence.", [f"observer_profile:{profile}", f"argv_profiles:{','.join(derived)}"]))
    return checks


def _eval_runtime(repo_root: Path, base_url: str, otel_python_path: str | None, enabled: bool | None) -> tuple[bool, str, Path | None]:
    config = _phoenix_config(repo_root)
    should_emit = _phoenix_eval_enabled(config) if enabled is None else enabled
    configured_url = config.get("base_url") if isinstance(config.get("base_url"), str) else None
    resolved_url = configured_url if base_url == "http://localhost:6006" and configured_url else base_url
    return should_emit, resolved_url.rstrip("/") + "/v1/traces", Path(otel_python_path).expanduser() if otel_python_path else _config_path(config, "otel_python")


def _eval_status(blockers: list[dict[str, Any]], emitted: bool) -> str:
    if blockers:
        return "blocked"
    return "emitted" if emitted else "not_run"


def _eval_emitted_spans(plan: dict[str, Any], command_name: str, emitted: bool) -> list[dict[str, Any]]:
    if not emitted:
        return []
    return [
        {
            "span_name": span["name"],
            "trace_id": plan["trace_id"],
            "span_id": span["span_id"],
            "parent_span_id": span["parent_span_id"],
            "command_name": command_name,
            "command_status": span["status"],
        }
        for span in plan["spans"]
    ]


def _eval_payload_header(eval_receipt: dict[str, Any], plan: dict[str, Any], source_digest: str, source_kind: str, profile: str | None) -> dict[str, Any]:
    return {
        "schema_version": PHOENIX_EVAL_TRACE_SCHEMA_VERSION,
        "schema_uri": PHOENIX_EVAL_TRACE_SCHEMA_URI,
        "operation": "phoenix_eval_trace",
        "source_receipt_digest": source_digest,
        "source_kind": source_kind,
        "eval_status": eval_receipt.get("status"),
        "runner": eval_receipt.get("runner"),
        "mode": eval_receipt.get("mode"),
        "profile": profile,
        "profile_evidence": plan["profile_evidence"],
        "package_id": eval_receipt.get("package_id"),
        "package_digest": eval_receipt.get("package_digest"),
        "project_name": plan["project_name"],
        "trace_id": plan["trace_id"],
        "root_span_id": plan["root_span_id"],
    }


def _eval_payload_counts(repo_root: Path, eval_receipt: dict[str, Any], plan: dict[str, Any], cases: Any, trace_case_spans: bool, bounded_limit: int, emitted: bool) -> dict[str, Any]:
    spans = plan["spans"]
    return {
        "target_path": _safe_path_value(repo_root, eval_receipt.get("target_path")),
        "case_count": int(eval_receipt["case_count"] if "case_count" in eval_receipt else len(cases or [])),
        "passed_count": int(eval_receipt.get("passed_count") or 0),
        "failed_count": int(eval_receipt.get("failed_count") or 0),
        "span_plan": spans,
        "planned_span_count": len(spans),
        "emitted_span_count": len(spans) if emitted else 0,
        "case_span_trace_enabled": trace_case_spans,
        "case_span_limit": bounded_limit,
        "case_span_count": sum(span["name"] == "skills-sdk.eval.scenario" for span in spans),
    }


def _eval_payload_result(checks: list[dict[str, Any]], plan: dict[str, Any], command_name: str, should_emit: bool, emitted: bool) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    observability_status = _eval_status(blockers, emitted)
    return {
        "status": "blocked" if blockers else "pass",
        "observability_status": observability_status,
        "enabled": should_emit,
        "emitted_spans": _eval_emitted_spans(plan, command_name, emitted),
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": emitted,
        "acceptance_trace": list(PHOENIX_ACCEPTANCE_TRACE),
        "agent_summary": (
            f"Phoenix emitted {len(plan['spans'])} nested span(s) to project {plan['project_name']}."
            if emitted
            else f"Phoenix eval observability is {observability_status}."
        ),
    }


def _eval_payload(repo_root: Path, eval_receipt: dict[str, Any], plan: dict[str, Any], source_digest: str, source_kind: str, cases: Any, bounded_limit: int, checks: list[dict[str, Any]], profile: str | None, command_name: str, trace_case_spans: bool, should_emit: bool, emitted: bool) -> dict[str, Any]:
    payload = _eval_payload_header(eval_receipt, plan, source_digest, source_kind, profile)
    payload.update(_eval_payload_counts(repo_root, eval_receipt, plan, cases, trace_case_spans, bounded_limit, emitted))
    payload.update(_eval_payload_result(checks, plan, command_name, should_emit, emitted))
    return payload


def _build_phoenix_eval_trace_receipt(repo_root: Path, *, eval_receipt: dict[str, Any], command_name: str = "sdk eval run", base_url: str = "http://localhost:6006", profile: str | None = None, otel_python_path: str | None = None, timeout_seconds: float = 2.0, enabled: bool | None = None, trace_case_spans: bool = True, case_span_limit: int = PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT) -> dict[str, Any]:
    from ask.skills_sdk.phoenix_trace_plan import emit_eval_trace_plan  # noqa: PLC0415

    plan, source_digest, source_kind, cases, bounded_limit = _eval_plan(eval_receipt, trace_case_spans, case_span_limit)
    checks = _config_checks(_phoenix_config(repo_root)) + _eval_checks(eval_receipt, plan, source_kind, profile)
    should_emit, endpoint, otel_python = _eval_runtime(repo_root, base_url, otel_python_path, enabled)
    if should_emit:
        checks.append(_check("otel_python_available", "pass" if otel_python is not None and otel_python.is_file() else "blocker", "Phoenix eval trace emission requires the configured OpenTelemetry Python runtime.", [otel_python.as_posix()] if otel_python is not None else ["missing_otel_python"]))
    export_result: dict[str, Any] | None = None
    if should_emit and not [check for check in checks if check["status"] == "blocker"] and otel_python is not None:
        export_result = emit_eval_trace_plan(plan, endpoint=endpoint, otel_python=otel_python, timeout_seconds=timeout_seconds)
        checks.append(_check("phoenix_otlp_export", "pass" if export_result.get("status") == "pass" else "blocker", "Phoenix must accept the deterministic nested eval trace in the configured project.", [f"project:{plan['project_name']}", f"endpoint:{endpoint}", f"error_class:{export_result.get('error_class') or 'none'}"]))
    return _eval_payload(repo_root, eval_receipt, plan, source_digest, source_kind, cases, bounded_limit, checks, profile, command_name, trace_case_spans, should_emit, export_result is not None and export_result.get("status") == "pass")


def _mirror_source(repo_root: Path, receipt_path: str) -> tuple[Path, list[dict[str, Any]], str, dict[str, Any], list[dict[str, Any]], list[str]]:
    source = Path(receipt_path)
    if not source.is_absolute():
        source = repo_root / source
    checks = [_check("source_path_allowed", "pass" if _path_allowed(repo_root, source) else "blocker", "Source receipt must stay inside the repository or a temporary evidence path.", [_repo_relative(repo_root, source)])]
    source_digest = "sha256:missing"
    receipt: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    raw_paths: list[str] = []
    if checks[0]["status"] == "pass" and source.is_file():
        try:
            raw_bytes = source.read_bytes()
            source_digest = _sha256_bytes(raw_bytes)
            receipt = _find_receipt(json.loads(raw_bytes.decode("utf-8")))
            raw_paths = _raw_key_paths(receipt)
            rows = _mirror_rows(repo_root, source, source_digest, receipt)
            checks.append(_check("source_json", "pass", "Source receipt JSON parsed.", [_repo_relative(repo_root, source)]))
            source_kind = _source_kind(receipt)
            checks.append(_check("source_kind_supported", "pass" if source_kind in SUPPORTED_SOURCE_KINDS else "blocker", "Phoenix mirror accepts eval_closeout, eval_run_receipt, ab_run_receipt, ab_judge_score_receipt, and observability_receipt.", [source_kind]))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            checks.append(_check("source_json", "blocker", "Source receipt must be valid UTF-8 JSON with a receipt-shaped object.", [f"error_class:{type(exc).__name__}"]))
    elif checks[0]["status"] == "pass":
        checks.append(_check("source_json", "blocker", "Source receipt path must exist.", [_repo_relative(repo_root, source)]))
    return source, checks, source_digest, receipt, rows, raw_paths


def _mirror_checks(checks: list[dict[str, Any]], rows: list[dict[str, Any]], raw_paths: list[str], receipt: dict[str, Any]) -> None:
    checks.append(_check("mirror_redaction", "blocker" if raw_paths else "pass", "Source receipts mirrored into Phoenix must not contain raw prompts, transcripts, messages, tool calls, stdout, stderr, or outputs.", [f"raw_keys_seen:{len(raw_paths)}"]))
    contract_errors = _mirror_contract_errors(rows)
    checks.append(_check("mirror_row_contract", "blocker" if contract_errors else "pass", "Mirror rows must be redacted allowlisted objects with stable event types and root fields.", contract_errors))
    profile_errors = _oss_profile_errors(receipt)
    checks.append(_check("oss_profile_execution_contract", "blocker" if profile_errors else "pass", "oss-local and oss-cloud mirrored receipts must prove codex exec invocation.", profile_errors))


def _mirror_destination(repo_root: Path, source: Path, out_path: str | None, write: bool, checks: list[dict[str, Any]]) -> Path | None:
    if out_path:
        destination = Path(out_path)
        if not destination.is_absolute():
            destination = repo_root / destination
        errors = ["suffix_not_jsonl"] if destination.suffix != ".jsonl" else []
        if source.resolve(strict=False) == destination.resolve(strict=False):
            errors.append("output_matches_source")
        checks.append(_check("output_path_allowed", "pass" if _path_allowed(repo_root, destination) and not errors else "blocker", "Output JSONL must be an explicit .jsonl path inside the repository or a temporary evidence path and must not overwrite the source receipt.", [_repo_relative(repo_root, destination), *errors]))
        return destination
    if write:
        checks.append(_check("output_path_allowed", "blocker", "--write requires --out so the mirror artifact is explicit.", []))
    return None


def _mirror_payload(repo_root: Path, source: Path, destination: Path | None, receipt: dict[str, Any], source_digest: str, rows: list[dict[str, Any]], checks: list[dict[str, Any]], write: bool) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "blocked" if blockers else ("written" if write else "preview")
    return {"schema_version": PHOENIX_MIRROR_SCHEMA_VERSION, "schema_uri": PHOENIX_MIRROR_SCHEMA_URI, "status": status, "operation": "phoenix_eval_receipt_mirror", "source_receipt_path": _repo_relative(repo_root, source), "source_receipt_digest": source_digest, "source_schema_version": receipt.get("schema_version"), "source_kind": _source_kind(receipt) if receipt else "missing", "out_path": _repo_relative(repo_root, destination) if destination is not None else None, "row_count": len(rows), "preview_rows": rows[:5], "checks": checks, "blockers": blockers, "mutation_performed": bool(write and not blockers), "acceptance_trace": list(PHOENIX_ACCEPTANCE_TRACE), "agent_summary": f"Phoenix mirror {'wrote' if write else 'previewed'} {len(rows)} redacted row(s) from {_repo_relative(repo_root, source)}." if not blockers else f"Phoenix mirror is blocked for {_repo_relative(repo_root, source)}."}


def _build_phoenix_mirror_receipt(repo_root: Path, *, receipt_path: str, out_path: str | None = None, write: bool = False) -> dict[str, Any]:
    source, checks, source_digest, receipt, rows, raw_paths = _mirror_source(repo_root, receipt_path)
    _mirror_checks(checks, rows, raw_paths, receipt)
    destination = _mirror_destination(repo_root, source, out_path, write, checks)
    blockers = [check for check in checks if check["status"] == "blocker"]
    if write and not blockers and destination is not None:
        _write_jsonl(destination, rows)
    payload = _mirror_payload(repo_root, source, destination, receipt, source_digest, rows, checks, write)
    if blockers:
        raise PhoenixObservabilityError(payload)
    return payload


build_phoenix_eval_trace_receipt = _build_phoenix_eval_trace_receipt
build_phoenix_mirror_receipt = _build_phoenix_mirror_receipt
build_phoenix_smoke_receipt = _build_phoenix_smoke_receipt
