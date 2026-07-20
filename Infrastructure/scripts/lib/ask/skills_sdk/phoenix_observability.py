from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ask.skills_sdk.phoenix_trace_plan import PHOENIX_PROJECT_NAME


PHOENIX_STATUS_SCHEMA_VERSION = "skills-sdk.phoenix-status-receipt.v0"
PHOENIX_STATUS_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-status-receipt.v0.schema.json"
PHOENIX_MIRROR_SCHEMA_VERSION = "skills-sdk.phoenix-mirror-receipt.v0"
PHOENIX_MIRROR_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-mirror-receipt.v0.schema.json"
PHOENIX_SMOKE_SCHEMA_VERSION = "skills-sdk.phoenix-smoke-receipt.v0"
PHOENIX_SMOKE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-smoke-receipt.v0.schema.json"
PHOENIX_EVAL_TRACE_SCHEMA_VERSION = "skills-sdk.phoenix-eval-trace-receipt.v1"
PHOENIX_EVAL_TRACE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-eval-trace-receipt.v1.schema.json"
PHOENIX_ACCEPTANCE_TRACE = ["phoenix-oss-eval-observability-workflow-2026-07-08", "PU-026"]
PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT = 10
PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT = 20
SUPPORTED_SOURCE_KINDS = frozenset(
    {
        "eval_closeout",
        "eval_run_receipt",
        "ab_run_receipt",
        "ab_judge_score_receipt",
        "observability_receipt",
    }
)
OSS_CODEX_PROFILES = frozenset({"oss-local", "oss-cloud"})
ALLOWED_ROW_TYPES = frozenset(
    {
        "phoenix_eval_receipt_mirror",
        "phoenix_eval_case_mirror",
        "phoenix_eval_candidate_mirror",
    }
)
REQUIRED_ROOT_ROW_FIELDS = frozenset(
    {
        "event_type",
        "redacted",
        "trace_id",
        "source_kind",
        "source_receipt_path",
        "source_receipt_digest",
        "source_schema_version",
        "status",
    }
)
RAW_FIELD_NAMES = frozenset(
    {
        "prompt",
        "raw_prompt",
        "output",
        "raw_output",
        "transcript",
        "messages",
        "conversation",
        "tool_calls",
        "stdout",
        "stderr",
    }
)


class PhoenixObservabilityError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _sha256_bytes(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _path_allowed(repo_root: Path, path: Path) -> bool:
    resolved = path.resolve(strict=False)
    roots = (
        repo_root.resolve(),
        Path(tempfile.gettempdir()).resolve(),
        Path("/private/tmp").resolve(),
        Path("/tmp").resolve(),
    )
    return any(resolved == root or root in resolved.parents for root in roots)


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker" if status == "blocker" else "info",
        "message": message,
        "evidence": evidence or [],
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_receipt(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        data = payload["data"]
        for key in (
            "skills_sdk_eval_run",
            "skills_sdk_observability_promote",
            "skills_sdk_observability_feedback",
        ):
            value = data.get(key)
            if isinstance(value, dict) and isinstance(value.get("receipt"), dict):
                return value["receipt"]
        for value in data.values():
            if isinstance(value, dict) and isinstance(value.get("receipt"), dict):
                return value["receipt"]
            if isinstance(value, dict) and isinstance(value.get("schema_version"), str):
                return value
    if isinstance(payload, dict) and isinstance(payload.get("receipt"), dict):
        return payload["receipt"]
    if isinstance(payload, dict):
        return payload
    raise TypeError("receipt payload must be a JSON object")


def _raw_key_paths(value: Any, *, prefix: str = "$") -> list[str]:
    if isinstance(value, dict):
        paths: list[str] = []
        for key, child in value.items():
            child_path = f"{prefix}.{key}"
            if key in RAW_FIELD_NAMES:
                paths.append(child_path)
            paths.extend(_raw_key_paths(child, prefix=child_path))
        return paths
    if isinstance(value, list):
        paths: list[str] = []
        for index, child in enumerate(value):
            paths.extend(_raw_key_paths(child, prefix=f"{prefix}[{index}]"))
        return paths
    return []


def _source_kind(receipt: dict[str, Any]) -> str:
    schema_version = str(receipt.get("schema_version") or "")
    operation = str(receipt.get("operation") or "")
    if "ab-judge-score" in schema_version or operation == "ab_judge_score":
        return "ab_judge_score_receipt"
    if "ab-run" in schema_version or operation == "ab_run":
        return "ab_run_receipt"
    if "eval-closeout" in schema_version or "eval_closeout" in operation:
        return "eval_closeout"
    if "eval-run" in schema_version or "eval_run" in operation:
        return "eval_run_receipt"
    if "observability" in schema_version:
        return "observability_receipt"
    return "generic_receipt"


def _safe_path_value(repo_root: Path, value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute():
        if _path_allowed(repo_root, path):
            return _repo_relative(repo_root, path)
        return None
    return path.as_posix()


def _mirror_contract_errors(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not rows:
        errors.append("rows:empty")
        return errors
    root_missing = sorted(REQUIRED_ROOT_ROW_FIELDS - set(rows[0]))
    if root_missing:
        errors.append(f"row:0:missing:{','.join(root_missing)}")
    for index, row in enumerate(rows):
        event_type = row.get("event_type")
        if event_type not in ALLOWED_ROW_TYPES:
            errors.append(f"row:{index}:event_type:{event_type!s}")
        if row.get("redacted") is not True:
            errors.append(f"row:{index}:redacted_not_true")
        raw_paths = _raw_key_paths(row)
        if raw_paths:
            errors.append(f"row:{index}:raw_keys:{','.join(raw_paths)}")
    return errors


def _oss_profile_errors(receipt: dict[str, Any]) -> list[str]:
    from ask.skills_sdk.phoenix_trace_plan import build_eval_trace_plan  # noqa: PLC0415

    source_kind = _source_kind(receipt)
    if source_kind not in {"eval_run_receipt", "ab_run_receipt", "ab_judge_score_receipt"}:
        return []
    return list(build_eval_trace_plan(receipt)["blockers"])


def _case_rows(receipt: dict[str, Any], trace_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cases = receipt.get("cases")
    if isinstance(cases, list):
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                continue
            rows.append(
                {
                    "event_type": "phoenix_eval_case_mirror",
                    "redacted": True,
                    "trace_id": trace_id,
                    "case_index": index,
                    "case_id": str(case.get("case_id") or case.get("id") or f"case-{index}"),
                    "status": str(case.get("status") or case.get("result") or "unknown"),
                    "blocker_class": case.get("blocker_class"),
                    "score": case.get("score"),
                    "source_digest": _sha256_json(
                        {
                            "case_id": case.get("case_id") or case.get("id") or index,
                            "status": case.get("status") or case.get("result"),
                            "score": case.get("score"),
                        }
                    ),
                }
            )
    scenario_candidates = receipt.get("scenario_candidates")
    if isinstance(scenario_candidates, list):
        for index, candidate in enumerate(scenario_candidates):
            if not isinstance(candidate, dict):
                continue
            rows.append(
                {
                    "event_type": "phoenix_eval_candidate_mirror",
                    "redacted": True,
                    "trace_id": trace_id,
                    "case_index": index,
                    "case_id": str(candidate.get("id") or f"candidate-{index}"),
                    "status": str(candidate.get("promotion_status") or "unknown"),
                    "candidate_type": candidate.get("candidate_type"),
                    "source_event_digest": candidate.get("source_event_digest"),
                }
            )
    return rows


def _mirror_rows(repo_root: Path, receipt_path: Path, source_digest: str, receipt: dict[str, Any]) -> list[dict[str, Any]]:
    trace_id = source_digest.removeprefix("sha256:")[:32]
    root = {
        "event_type": "phoenix_eval_receipt_mirror",
        "redacted": True,
        "trace_id": trace_id,
        "source_kind": _source_kind(receipt),
        "source_receipt_path": _repo_relative(repo_root, receipt_path),
        "source_receipt_digest": source_digest,
        "source_schema_version": receipt.get("schema_version"),
        "status": receipt.get("status"),
        "operation": receipt.get("operation"),
        "target_path": _safe_path_value(repo_root, receipt.get("target_path") or receipt.get("skill_path") or receipt.get("source_path")),
        "package_id": receipt.get("package_id"),
        "package_digest": receipt.get("package_digest"),
        "runner": receipt.get("runner"),
        "mode": receipt.get("mode"),
        "codex_profile": receipt.get("codex_profile"),
        "codex_exec_invoked": receipt.get("codex_exec_invoked"),
        "blocker_class": receipt.get("blocker_class"),
        "tessl_workspace": receipt.get("tessl_workspace") or receipt.get("workspace"),
    }
    rows = [root]
    rows.extend(_case_rows(receipt, trace_id))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def build_phoenix_status_receipt(
    repo_root: Path,
    *,
    base_url: str = "http://localhost:6006",
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    parsed = urlparse(base_url)
    checks: list[dict[str, Any]] = []
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        checks.append(_check("phoenix_base_url", "blocker", "Phoenix base URL must be an absolute http(s) URL.", [base_url]))
    else:
        checks.append(_check("phoenix_base_url", "pass", "Phoenix base URL is absolute.", [base_url]))

    server_version: str | None = None
    http_status: int | None = None
    if checks[-1]["status"] == "pass":
        request = Request(base_url, method="HEAD")
        try:
            with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - operator-provided local/service URL.
                http_status = int(response.status)
                server_version = response.headers.get("x-phoenix-server-version")
        except HTTPError as exc:
            http_status = int(exc.code)
        except (OSError, URLError, TimeoutError) as exc:
            checks.append(
                _check(
                    "phoenix_http",
                    "blocker",
                    "Phoenix UI endpoint must respond before traces can be trusted.",
                    [f"error_class:{type(exc).__name__}"],
                )
            )
        else:
            checks.append(_check("phoenix_http", "pass", "Phoenix UI endpoint responded.", [f"status:{http_status}"]))
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
        "acceptance_trace": PHOENIX_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Phoenix is reachable at {base_url}; traces can target {base_url.rstrip('/')}/v1/traces."
            if status == "pass"
            else f"Phoenix is not reachable at {base_url}; start the Docker service and rerun the status check."
        ),
    }


def build_phoenix_smoke_receipt(
    repo_root: Path,
    *,
    base_url: str = "http://localhost:6006",
    profile: str = "oss-local",
    timeout_seconds: float = 10.0,
    otel_python_path: str | None = None,
    model_name: str | None = None,
    provider: str | None = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    command_name: str | None = None,
    command_status: str | None = None,
    latency_ms: int | None = None,
) -> dict[str, Any]:
    parsed = urlparse(base_url)
    endpoint = base_url.rstrip("/") + "/v1/traces"
    config = _phoenix_config(repo_root)
    configured_project_name = config.get("project_name")
    project_name = PHOENIX_PROJECT_NAME
    project_name_evidence = (
        [str(configured_project_name)]
        if configured_project_name is not None
        else [project_name]
    )
    checks: list[dict[str, Any]] = []
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        checks.append(_check("phoenix_base_url", "blocker", "Phoenix base URL must be an absolute http(s) URL.", [base_url]))
    else:
        checks.append(_check("phoenix_base_url", "pass", "Phoenix base URL is absolute.", [base_url]))
    checks.append(
        _check(
            "phoenix_project_name",
            "pass"
            if "project_name" not in config or configured_project_name == PHOENIX_PROJECT_NAME
            else "blocker",
            "Phoenix traces must target the Skills SDK eval project.",
            project_name_evidence,
        )
    )
    checks.append(
        _check(
            "oss_profile_supported",
            "pass" if profile in OSS_CODEX_PROFILES else "blocker",
            "Phoenix smoke traces are restricted to declared OSS Codex profiles.",
            [profile],
        )
    )
    token_errors = []
    if prompt_tokens < 0:
        token_errors.append("prompt_tokens_negative")
    if completion_tokens < 0:
        token_errors.append("completion_tokens_negative")
    checks.append(
        _check(
            "llm_token_counts_valid",
            "pass" if not token_errors else "blocker",
            "Phoenix LLM smoke token counts must be non-negative integers.",
            token_errors,
        )
    )

    trace_id = uuid.uuid4().hex
    span_id = uuid.uuid4().hex[:16]
    span_kind = "LLM" if model_name else "WORKFLOW"
    span_name = f"agent-skills.phoenix.{model_name}" if model_name else "agent-skills.phoenix.smoke"
    emitted = False
    export_error: str | None = None
    otel_python = Path(otel_python_path).expanduser() if otel_python_path else None
    checks.append(
        _check(
            "otel_python_available",
            "pass" if otel_python is not None and otel_python.is_file() else "blocker",
            "Phoenix smoke emission requires an explicit --otel-python path, ASK_PHOENIX_OTEL_PYTHON, or phoenix.json otel_python.",
            [otel_python.as_posix()] if otel_python is not None else ["missing_explicit_otel_python"],
        )
    )
    if not [check for check in checks if check["status"] == "blocker"]:
        smoke_script = r'''
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
    print(json.dumps({"status": "blocked", "http_status": exc.code, "error_class": type(exc).__name__}))
    raise SystemExit(2)
'''
        assert otel_python is not None
        try:
            process = subprocess.run(
                [otel_python.as_posix(), "-c", smoke_script],
                input=json.dumps(
                    {
                        "endpoint": endpoint,
                        "project_name": project_name,
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "span_name": span_name,
                        "span_kind": span_kind,
                        "repo_name": repo_root.name,
                        "profile": profile,
                        "model_name": model_name,
                        "provider": provider,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "command_name": command_name,
                        "command_status": command_status,
                        "latency_ms": latency_ms,
                        "timeout_seconds": timeout_seconds,
                        "acceptance_trace": PHOENIX_ACCEPTANCE_TRACE,
                    },
                    sort_keys=True,
                ),
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout_seconds + 1.0,
            )
            try:
                export_result = json.loads(process.stdout.strip().splitlines()[-1])
            except (IndexError, json.JSONDecodeError):
                export_result = {"status": "blocked", "error": "missing_json_export_result"}
            emitted = process.returncode == 0 and export_result.get("status") == "pass"
            if not emitted:
                export_error = ":".join(
                    (
                        "ExportProcessFailed",
                        str(process.returncode),
                        str(export_result.get("error_class") or "ExportRejected"),
                    )
                )
        except subprocess.TimeoutExpired:
            export_error = "TimeoutExpired"
        except OSError as exc:
            export_error = type(exc).__name__
        checks.append(
            _check(
                "phoenix_otlp_export",
                "pass" if emitted and export_error is None else "blocker",
                "Phoenix OTLP HTTP endpoint must accept a deterministic smoke span.",
                [endpoint] if export_error is None else [endpoint, export_error],
            )
        )
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "blocked" if blockers else "pass"
    return {
        "schema_version": PHOENIX_SMOKE_SCHEMA_VERSION,
        "schema_uri": PHOENIX_SMOKE_SCHEMA_URI,
        "status": status,
        "operation": "phoenix_smoke_trace",
        "base_url": base_url,
        "otlp_http_endpoint": endpoint,
        "project_name": project_name,
        "span_name": span_name,
        "span_kind": span_kind,
        "trace_id": trace_id,
        "span_id": span_id,
        "profile": profile,
        "model_name": model_name,
        "provider": provider,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "command_name": command_name,
        "command_status": command_status,
        "latency_ms": latency_ms,
        "otel_python_path": otel_python.as_posix() if otel_python is not None else None,
        "timestamp_unix_seconds": int(time.time()),
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": emitted and not blockers,
        "acceptance_trace": PHOENIX_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Phoenix {span_kind.lower()} smoke trace emitted to project {project_name} at {endpoint}; refresh that project's Tracing view."
            if status == "pass"
            else f"Phoenix smoke trace is blocked for {endpoint}."
        ),
    }


def emit_ask_result_to_phoenix(
    repo_root: Path,
    *,
    command_name: str,
    command_status: str,
    latency_ms: int | None,
    base_url: str,
    profile: str,
    otel_python_path: str | None = None,
    model_name: str | None = None,
    provider: str | None = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    return build_phoenix_smoke_receipt(
        repo_root,
        base_url=base_url,
        profile=profile,
        timeout_seconds=timeout_seconds,
        otel_python_path=otel_python_path,
        model_name=model_name,
        provider=provider,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        command_name=command_name,
        command_status=command_status,
        latency_ms=latency_ms,
    )


def _config_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _phoenix_config(repo_root: Path) -> dict[str, Any]:
    config_path = repo_root / "Infrastructure" / "config" / "observability" / "phoenix.json"
    if not config_path.is_file():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _phoenix_eval_enabled(config: dict[str, Any]) -> bool:
    env_value = os.environ.get("ASK_PHOENIX_EVAL_TRACE")
    if env_value is not None:
        return _config_bool(env_value)
    if "eval_tracing_enabled" in config:
        return _config_bool(config.get("eval_tracing_enabled"))
    return _config_bool(config.get("enabled"))


def _config_path(config: dict[str, Any], key: str) -> Path | None:
    value = config.get(key)
    if not isinstance(value, str) or not value:
        return None
    return Path(value).expanduser()


def build_phoenix_eval_trace_receipt(
    repo_root: Path,
    *,
    eval_receipt: dict[str, Any],
    command_name: str = "sdk eval run",
    base_url: str = "http://localhost:6006",
    profile: str | None = None,
    otel_python_path: str | None = None,
    timeout_seconds: float = 2.0,
    enabled: bool | None = None,
    trace_case_spans: bool = True,
    case_span_limit: int = PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT,
) -> dict[str, Any]:
    from ask.skills_sdk.phoenix_trace_plan import (  # noqa: PLC0415
        build_eval_trace_plan,
        emit_eval_trace_plan,
    )

    config = _phoenix_config(repo_root)
    bounded_case_span_limit = max(0, min(case_span_limit, PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT))
    source_digest = _sha256_json(eval_receipt)
    plan_receipt = dict(eval_receipt)
    cases = eval_receipt.get("cases")
    if isinstance(cases, list):
        plan_receipt["cases"] = cases[:bounded_case_span_limit] if trace_case_spans else []
    plan = build_eval_trace_plan(plan_receipt, source_digest=source_digest)
    raw_paths = _raw_key_paths(eval_receipt)
    source_kind = _source_kind(eval_receipt)
    checks = [
        _check(
            "source_kind_supported",
            "pass" if source_kind in {"eval_run_receipt", "ab_run_receipt", "ab_judge_score_receipt"} else "blocker",
            "Phoenix eval tracing accepts eval_run_receipt, ab_run_receipt, and ab_judge_score_receipt.",
            [source_kind],
        ),
        _check(
            "eval_trace_redaction",
            "pass" if not raw_paths else "blocker",
            "Eval trace receipts must not contain raw prompts, outputs, transcripts, tool calls, stdout, or stderr.",
            [f"raw_keys_seen:{len(raw_paths)}"],
        ),
        _check(
            "codex_profile_argv_proof",
            "blocker" if plan["blockers"] else "pass",
            "Provider-backed eval traces must derive each Codex runtime profile from the executed argv.",
            list(plan["blockers"]),
        ),
    ]
    if profile is not None:
        derived_profiles = [
            row.get("derived_codex_profile")
            for row in plan["profile_evidence"]
            if row.get("derived_codex_profile") is not None
        ]
        override_matches = not derived_profiles or derived_profiles == [profile]
        checks.append(
            _check(
                "profile_argument_matches_argv",
                "pass" if override_matches else "blocker",
                "The optional observer profile argument must not contradict argv-derived runtime profile evidence.",
                [f"observer_profile:{profile}", f"argv_profiles:{','.join(derived_profiles)}"],
            )
        )
    should_emit = _phoenix_eval_enabled(config) if enabled is None else enabled
    configured_base_url = config.get("base_url") if isinstance(config.get("base_url"), str) else None
    resolved_base_url = configured_base_url if base_url == "http://localhost:6006" and configured_base_url else base_url
    endpoint = resolved_base_url.rstrip("/") + "/v1/traces"
    otel_python = Path(otel_python_path).expanduser() if otel_python_path else _config_path(config, "otel_python")
    if should_emit:
        checks.append(
            _check(
                "otel_python_available",
                "pass" if otel_python is not None and otel_python.is_file() else "blocker",
                "Phoenix eval trace emission requires the configured OpenTelemetry Python runtime.",
                [otel_python.as_posix()] if otel_python is not None else ["missing_otel_python"],
            )
        )
    export_result: dict[str, Any] | None = None
    pre_export_blockers = [check for check in checks if check["status"] == "blocker"]
    if should_emit and not pre_export_blockers and otel_python is not None:
        export_result = emit_eval_trace_plan(
            plan,
            endpoint=endpoint,
            otel_python=otel_python,
            timeout_seconds=timeout_seconds,
        )
        checks.append(
            _check(
                "phoenix_otlp_export",
                "pass" if export_result.get("status") == "pass" else "blocker",
                "Phoenix must accept the deterministic nested eval trace in the configured project.",
                [
                    f"project:{plan['project_name']}",
                    f"endpoint:{endpoint}",
                    f"error_class:{export_result.get('error_class') or 'none'}",
                ],
            )
        )
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "blocked" if blockers else "pass"
    observability_status = "blocked" if blockers else ("emitted" if export_result else "not_run")
    emitted = export_result is not None and export_result.get("status") == "pass"
    case_span_count = sum(1 for span in plan["spans"] if span["name"] == "skills-sdk.eval.scenario")
    return {
        "schema_version": PHOENIX_EVAL_TRACE_SCHEMA_VERSION,
        "schema_uri": PHOENIX_EVAL_TRACE_SCHEMA_URI,
        "status": status,
        "operation": "phoenix_eval_trace",
        "source_receipt_digest": source_digest,
        "source_kind": source_kind,
        "eval_status": eval_receipt.get("status"),
        "observability_status": observability_status,
        "runner": eval_receipt.get("runner"),
        "mode": eval_receipt.get("mode"),
        "profile": profile,
        "profile_evidence": plan["profile_evidence"],
        "target_path": _safe_path_value(repo_root, eval_receipt.get("target_path")),
        "package_id": eval_receipt.get("package_id"),
        "package_digest": eval_receipt.get("package_digest"),
        "case_count": int(eval_receipt.get("case_count") or len(cases or [])),
        "passed_count": int(eval_receipt.get("passed_count") or 0),
        "failed_count": int(eval_receipt.get("failed_count") or 0),
        "project_name": plan["project_name"],
        "trace_id": plan["trace_id"],
        "root_span_id": plan["root_span_id"],
        "span_plan": plan["spans"],
        "planned_span_count": len(plan["spans"]),
        "emitted_span_count": len(plan["spans"]) if emitted else 0,
        "case_span_trace_enabled": trace_case_spans,
        "case_span_limit": bounded_case_span_limit,
        "case_span_count": case_span_count,
        "enabled": should_emit,
        "emitted_spans": [
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
        if emitted
        else [],
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": emitted,
        "acceptance_trace": PHOENIX_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Phoenix emitted {len(plan['spans'])} nested span(s) to project {plan['project_name']}."
            if emitted
            else f"Phoenix eval observability is {observability_status}; eval status remains {eval_receipt.get('status')}."
        ),
    }


def build_phoenix_mirror_receipt(
    repo_root: Path,
    *,
    receipt_path: str,
    out_path: str | None = None,
    write: bool = False,
) -> dict[str, Any]:
    source = Path(receipt_path)
    if not source.is_absolute():
        source = repo_root / source
    checks = [
        _check(
            "source_path_allowed",
            "pass" if _path_allowed(repo_root, source) else "blocker",
            "Source receipt must stay inside the repository or a temporary evidence path.",
            [_repo_relative(repo_root, source)],
        )
    ]
    source_digest = "sha256:missing"
    rows: list[dict[str, Any]] = []
    raw_paths: list[str] = []
    receipt: dict[str, Any] = {}
    if checks[0]["status"] == "pass" and source.is_file():
        raw_bytes = source.read_bytes()
        source_digest = _sha256_bytes(raw_bytes)
        payload = json.loads(raw_bytes.decode("utf-8"))
        receipt = _find_receipt(payload)
        raw_paths = _raw_key_paths(receipt)
        rows = _mirror_rows(repo_root, source, source_digest, receipt)
        checks.append(_check("source_json", "pass", "Source receipt JSON parsed.", [_repo_relative(repo_root, source)]))
        source_kind = _source_kind(receipt)
        checks.append(
            _check(
                "source_kind_supported",
                "pass" if source_kind in SUPPORTED_SOURCE_KINDS else "blocker",
                "Phoenix mirror accepts eval_closeout, eval_run_receipt, ab_run_receipt, ab_judge_score_receipt, and observability_receipt.",
                [source_kind],
            )
        )
    elif checks[0]["status"] == "pass":
        checks.append(_check("source_json", "blocker", "Source receipt path must exist.", [_repo_relative(repo_root, source)]))
    checks.append(
        _check(
            "mirror_redaction",
            "blocker" if raw_paths else "pass",
            "Source receipts mirrored into Phoenix must not contain raw prompts, transcripts, messages, tool calls, stdout, stderr, or outputs.",
            [f"raw_keys_seen:{len(raw_paths)}"],
        )
    )
    contract_errors = _mirror_contract_errors(rows)
    checks.append(
        _check(
            "mirror_row_contract",
            "blocker" if contract_errors else "pass",
            "Mirror rows must be redacted allowlisted objects with stable event types and root fields.",
            contract_errors,
        )
    )
    profile_errors = _oss_profile_errors(receipt)
    checks.append(
        _check(
            "oss_profile_execution_contract",
            "blocker" if profile_errors else "pass",
            "oss-local and oss-cloud mirrored receipts must prove codex exec invocation.",
            profile_errors,
        )
    )
    destination: Path | None = None
    if out_path:
        destination = Path(out_path)
        if not destination.is_absolute():
            destination = repo_root / destination
        output_errors: list[str] = []
        if destination.suffix != ".jsonl":
            output_errors.append("suffix_not_jsonl")
        if source.resolve(strict=False) == destination.resolve(strict=False):
            output_errors.append("output_matches_source")
        checks.append(
            _check(
                "output_path_allowed",
                "pass" if _path_allowed(repo_root, destination) and not output_errors else "blocker",
                "Output JSONL must be an explicit .jsonl path inside the repository or a temporary evidence path and must not overwrite the source receipt.",
                [_repo_relative(repo_root, destination), *output_errors],
            )
        )
    elif write:
        checks.append(_check("output_path_allowed", "blocker", "--write requires --out so the mirror artifact is explicit.", []))

    blockers = [check for check in checks if check["status"] == "blocker"]
    if write and not blockers and destination is not None:
        _write_jsonl(destination, rows)
    status = "blocked" if blockers else ("written" if write else "preview")
    receipt_payload = {
        "schema_version": PHOENIX_MIRROR_SCHEMA_VERSION,
        "schema_uri": PHOENIX_MIRROR_SCHEMA_URI,
        "status": status,
        "operation": "phoenix_eval_receipt_mirror",
        "source_receipt_path": _repo_relative(repo_root, source),
        "source_receipt_digest": source_digest,
        "source_schema_version": receipt.get("schema_version"),
        "source_kind": _source_kind(receipt) if receipt else "missing",
        "out_path": _repo_relative(repo_root, destination) if destination is not None else None,
        "row_count": len(rows),
        "preview_rows": rows[:5],
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": bool(write and not blockers),
        "acceptance_trace": PHOENIX_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Phoenix mirror {'wrote' if write else 'previewed'} {len(rows)} redacted row(s) from {_repo_relative(repo_root, source)}."
            if not blockers
            else f"Phoenix mirror is blocked for {_repo_relative(repo_root, source)}."
        ),
    }
    if blockers:
        raise PhoenixObservabilityError(receipt_payload)
    return receipt_payload
