from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


OSS_CODEX_PROFILES = ("oss-local", "oss-cloud")
PHOENIX_PROJECT_NAME = "agent-skills-skills-sdk-evals"
MAX_CASE_SPANS = 20
SAFE_ATTRIBUTE_TYPES = (str, int, float, bool)


def _sha256_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _source_kind(receipt: dict[str, Any]) -> str:
    schema_version = str(receipt.get("schema_version") or "")
    operation = str(receipt.get("operation") or "")
    if "ab-judge-score" in schema_version or operation == "ab_judge_score":
        return "ab_judge_score_receipt"
    if "ab-run" in schema_version or operation == "ab_run":
        return "ab_run_receipt"
    if "eval-run" in schema_version or operation == "eval_run":
        return "eval_run_receipt"
    return "unsupported_receipt"


def _command_profile(command: list[str]) -> tuple[str | None, int | None, list[str]]:
    blockers: list[str] = []
    profile_positions = [index for index, item in enumerate(command) if item == "--profile"]
    if len(command) < 2 or command[:2] != ["codex", "exec"]:
        blockers.append("codex_exec_argv_missing")
    if len(profile_positions) != 1:
        blockers.append(f"profile_flag_count:{len(profile_positions)}")
        return None, None, blockers
    position = profile_positions[0]
    if position != 2 or position + 1 >= len(command):
        blockers.append(f"profile_flag_misplaced:{position}")
        return None, position, blockers
    candidate = command[position + 1]
    if candidate not in OSS_CODEX_PROFILES:
        blockers.append(f"profile_unsupported:{candidate}")
        return None, position, blockers
    return candidate, position, blockers


def _profile_from_argv(argv: Any, *, lane: str, claimed_profile: Any = None) -> dict[str, Any]:
    command = argv if isinstance(argv, list) and all(isinstance(item, str) for item in argv) else []
    derived_profile, profile_position, blockers = _command_profile(command)
    if isinstance(claimed_profile, str) and derived_profile != claimed_profile:
        blockers.append(f"claimed_profile_mismatch:{claimed_profile}:{derived_profile or 'missing'}")
    return {
        "lane": lane,
        "status": "blocked" if blockers else "pass",
        "derived_codex_profile": derived_profile,
        "claimed_codex_profile": claimed_profile if isinstance(claimed_profile, str) else None,
        "argv_digest": _sha256_json(command),
        "profile_flag_index": profile_position,
        "blockers": blockers,
    }


def _eval_run_profile_evidence(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    claimed = receipt.get("codex_profile")
    if receipt.get("codex_exec_invoked") is not True and str(receipt.get("runner") or "").startswith("deterministic"):
        return [{
            "lane": "deterministic-evaluator",
            "status": "not_applicable",
            "derived_codex_profile": None,
            "claimed_codex_profile": claimed if isinstance(claimed, str) else None,
            "argv_digest": None,
            "profile_flag_index": None,
            "blockers": [],
        }]
    argv = receipt.get("codex_exec_command_argv") or receipt.get("codex_exec_command_shape")
    return [_profile_from_argv(argv, lane="eval-run", claimed_profile=claimed)]


def _ab_profile_evidence(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    rows = receipt.get("variant_results")
    evidence = [
        _profile_from_argv(
            row.get("command_argv"),
            lane=f"ab-variant-{row.get('variant_label') or index}",
            claimed_profile=row.get("codex_profile"),
        )
        for index, row in enumerate(rows if isinstance(rows, list) else [])
        if isinstance(row, dict)
    ]
    if not evidence:
        evidence.append(_profile_from_argv(None, lane="ab-variants"))
    if [item.get("derived_codex_profile") for item in evidence] != list(OSS_CODEX_PROFILES):
        for item in evidence:
            item["blockers"].append("profile_order_required:oss-local,oss-cloud")
            item["status"] = "blocked"
    return evidence


def _profile_evidence(receipt: dict[str, Any], source_kind: str) -> list[dict[str, Any]]:
    if source_kind == "eval_run_receipt":
        return _eval_run_profile_evidence(receipt)
    if source_kind == "ab_run_receipt":
        return _ab_profile_evidence(receipt)
    if source_kind == "ab_judge_score_receipt":
        row = _profile_from_argv(
            receipt.get("judge_command_argv"),
            lane="judge-score",
            claimed_profile=receipt.get("codex_profile"),
        )
        return [row]
    return []


def _safe_attributes(values: dict[str, Any]) -> dict[str, str | int | float | bool]:
    return {
        key: value
        for key, value in values.items()
        if isinstance(value, SAFE_ATTRIBUTE_TYPES) and value != ""
    }


def _span_id(trace_id: str, ordinal: int) -> str:
    seed = f"{trace_id}:{ordinal}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()[:16]


class _SpanPlan:
    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.spans: list[dict[str, Any]] = []

    def add(
        self,
        name: str,
        *,
        parent_span_id: str | None,
        span_kind: str,
        status: str,
        attributes: dict[str, Any],
    ) -> str:
        span_id = _span_id(self.trace_id, len(self.spans))
        self.spans.append(
            {
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "name": name,
                "span_kind": span_kind,
                "status": status,
                "attributes": _safe_attributes(attributes),
            }
        )
        return span_id


def _root_attributes(receipt: dict[str, Any], source_kind: str, source_digest: str) -> dict[str, Any]:
    execution_profile = receipt.get("execution_profile")
    judge_profile = receipt.get("judge_profile")
    fixture = receipt.get("fixture")
    skill_a = receipt.get("skill_a")
    skill_b = receipt.get("skill_b")
    return {
        "skills_sdk.source_kind": source_kind,
        "skills_sdk.source_schema_version": receipt.get("schema_version"),
        "skills_sdk.source_receipt_digest": source_digest,
        "skills_sdk.eval_status": receipt.get("status"),
        "skills_sdk.runner": receipt.get("runner"),
        "skills_sdk.mode": receipt.get("mode"),
        "skills_sdk.package_id": receipt.get("package_id"),
        "skills_sdk.package_digest": receipt.get("package_digest"),
        "skills_sdk.dataset_digest": receipt.get("dataset_digest"),
        "skills_sdk.fixture_digest": fixture.get("digest") if isinstance(fixture, dict) else None,
        "skills_sdk.rubric_digest": receipt.get("rubric_digest"),
        "skills_sdk.experiment_id": receipt.get("experiment_id"),
        "skills_sdk.scenario_set_id": receipt.get("scenario_set_id") or receipt.get("scenario_set"),
        "skills_sdk.scenario_set_digest": receipt.get("scenario_set_digest"),
        "skills_sdk.skill_a_package_id": skill_a.get("package_id") if isinstance(skill_a, dict) else None,
        "skills_sdk.skill_a_package_digest": skill_a.get("package_digest") if isinstance(skill_a, dict) else None,
        "skills_sdk.skill_b_package_id": skill_b.get("package_id") if isinstance(skill_b, dict) else None,
        "skills_sdk.skill_b_package_digest": skill_b.get("package_digest") if isinstance(skill_b, dict) else None,
        "skills_sdk.case_count": receipt.get("case_count"),
        "skills_sdk.passed_count": receipt.get("passed_count"),
        "skills_sdk.failed_count": receipt.get("failed_count"),
        "skills_sdk.execution_profile": execution_profile.get("id") if isinstance(execution_profile, dict) else None,
        "skills_sdk.judge_profile": judge_profile.get("id") if isinstance(judge_profile, dict) else None,
        "skills_sdk.redacted": True,
    }


def _profile_spans(plan: _SpanPlan, parent_span_id: str, evidence: list[dict[str, Any]]) -> None:
    for item in evidence:
        plan.add(
            "skills-sdk.eval.profile-preflight",
            parent_span_id=parent_span_id,
            span_kind="CHAIN",
            status=str(item["status"]),
            attributes={
                "skills_sdk.lane": item["lane"],
                "skills_sdk.codex_profile": item["derived_codex_profile"],
                "skills_sdk.claimed_codex_profile": item["claimed_codex_profile"],
                "skills_sdk.argv_digest": item["argv_digest"],
                "skills_sdk.profile_flag_index": item["profile_flag_index"],
                "skills_sdk.blocker_count": len(item["blockers"]),
            },
        )


def _add_case_span(plan: _SpanPlan, scenario_parent: str, case: dict[str, Any], index: int) -> None:
    case_id = str(case.get("case_id") or case.get("id") or f"case-{index}")
    case_parent = plan.add(
        "skills-sdk.eval.scenario",
        parent_span_id=scenario_parent,
        span_kind="CHAIN",
        status=str(case.get("status") or "unknown"),
        attributes={
            "skills_sdk.case_id": case_id,
            "skills_sdk.case_index": index,
            "skills_sdk.case_status": case.get("status"),
            "skills_sdk.oracle": case.get("oracle"),
            "skills_sdk.score": case.get("score"),
        },
    )
    plan.add(
        "skills-sdk.eval.deterministic-evaluator",
        parent_span_id=case_parent,
        span_kind="EVALUATOR",
        status=str(case.get("status") or "unknown"),
        attributes={
            "skills_sdk.case_id": case_id,
            "skills_sdk.expected_digest": _sha256_json(case.get("expected")),
            "skills_sdk.actual_digest": _sha256_json(case.get("actual")),
            "skills_sdk.claim_ids_digest": _sha256_json(case.get("claim_ids")),
            "skills_sdk.gap_ids_digest": _sha256_json(case.get("gap_ids")),
            "skills_sdk.provenance_digest": _sha256_json(case.get("provenance")),
        },
    )


def _scenario_spans(plan: _SpanPlan, parent_span_id: str, receipt: dict[str, Any]) -> None:
    scenario_parent = plan.add(
        "skills-sdk.eval.scenario-selection",
        parent_span_id=parent_span_id,
        span_kind="RETRIEVER",
        status="pass",
        attributes={
            "skills_sdk.dataset_digest": receipt.get("dataset_digest"),
            "skills_sdk.scenario_set_id": receipt.get("scenario_set_id") or receipt.get("scenario_set"),
            "skills_sdk.scenario_set_digest": receipt.get("scenario_set_digest"),
            "skills_sdk.case_count": receipt.get("case_count"),
        },
    )
    cases = receipt.get("cases")
    for index, case in enumerate(cases[:MAX_CASE_SPANS] if isinstance(cases, list) else []):
        if isinstance(case, dict):
            _add_case_span(plan, scenario_parent, case, index)


def _ab_generation_spans(plan: _SpanPlan, parent_span_id: str, receipt: dict[str, Any], evidence: list[dict[str, Any]]) -> None:
    rows = receipt.get("variant_results")
    if not isinstance(rows, list):
        return
    for index, row in enumerate(rows[:2]):
        if not isinstance(row, dict):
            continue
        profile = evidence[index].get("derived_codex_profile") if index < len(evidence) else None
        plan.add(
            "skills-sdk.eval.generation",
            parent_span_id=parent_span_id,
            span_kind="LLM",
            status=str(row.get("status") or "unknown"),
            attributes={
                "skills_sdk.variant_label": row.get("variant_label"),
                "skills_sdk.codex_profile": profile,
                "skills_sdk.argv_digest": evidence[index].get("argv_digest") if index < len(evidence) else None,
                "skills_sdk.output_digest": row.get("output_last_message_digest"),
                "skills_sdk.event_log_digest": row.get("runner_stdout_digest"),
                "skills_sdk.exit_code": row.get("exit_code"),
            },
        )


def _dimension_spans(plan: _SpanPlan, score_parent: str, decision: dict[str, Any]) -> None:
    dimensions = decision.get("dimension_scores")
    for dimension in dimensions if isinstance(dimensions, list) else []:
        if not isinstance(dimension, dict):
            continue
        plan.add(
            "skills-sdk.eval.judge-dimension",
            parent_span_id=score_parent,
            span_kind="EVALUATOR",
            status="pass",
            attributes={
                "skills_sdk.dimension_id": dimension.get("dimension_id"),
                "skills_sdk.skill_a_score": dimension.get("skill_a_score"),
                "skills_sdk.skill_b_score": dimension.get("skill_b_score"),
            },
        )


def _judge_spans(plan: _SpanPlan, parent_span_id: str, receipt: dict[str, Any], evidence: list[dict[str, Any]]) -> None:
    judge_parent = plan.add(
        "skills-sdk.eval.judge-generation",
        parent_span_id=parent_span_id,
        span_kind="LLM",
        status=str(receipt.get("status") or "unknown"),
        attributes={
            "skills_sdk.codex_profile": evidence[0].get("derived_codex_profile") if evidence else None,
            "skills_sdk.argv_digest": evidence[0].get("argv_digest") if evidence else None,
            "skills_sdk.judge_prompt_digest": receipt.get("judge_prompt_digest"),
            "skills_sdk.judge_output_digest": receipt.get("judge_output_digest"),
            "skills_sdk.rubric_digest": receipt.get("rubric_digest"),
        },
    )
    decision = receipt.get("decision")
    if not isinstance(decision, dict):
        return
    score_parent = plan.add(
        "skills-sdk.eval.judge-score",
        parent_span_id=judge_parent,
        span_kind="EVALUATOR",
        status="pass" if receipt.get("status") == "scored" else "blocked",
        attributes={
            "skills_sdk.winner": decision.get("winner"),
            "skills_sdk.confidence": decision.get("confidence"),
            "skills_sdk.normalized_score_a": decision.get("normalized_score_a"),
            "skills_sdk.normalized_score_b": decision.get("normalized_score_b"),
        },
    )
    _dimension_spans(plan, score_parent, decision)


def _add_source_spans(
    plan: _SpanPlan,
    root_span_id: str,
    receipt: dict[str, Any],
    source_kind: str,
    evidence: list[dict[str, Any]],
) -> None:
    _profile_spans(plan, root_span_id, evidence)
    if source_kind == "eval_run_receipt":
        _scenario_spans(plan, root_span_id, receipt)
    elif source_kind == "ab_run_receipt":
        _ab_generation_spans(plan, root_span_id, receipt, evidence)
    elif source_kind == "ab_judge_score_receipt":
        _judge_spans(plan, root_span_id, receipt, evidence)


def _build_plan_spans(
    receipt: dict[str, Any],
    source_kind: str,
    source_digest: str,
    evidence: list[dict[str, Any]],
    blockers: list[str],
) -> tuple[_SpanPlan, str]:
    plan = _SpanPlan(source_digest.removeprefix("sha256:")[:32])
    root_span_id = plan.add(
        "skills-sdk.eval",
        parent_span_id=None,
        span_kind="CHAIN",
        status="blocked" if blockers else str(receipt.get("status") or "unknown"),
        attributes=_root_attributes(receipt, source_kind, source_digest),
    )
    _add_source_spans(plan, root_span_id, receipt, source_kind, evidence)
    plan.add(
        "skills-sdk.eval.receipt-validation",
        parent_span_id=root_span_id,
        span_kind="EVALUATOR",
        status="blocked" if blockers else "pass",
        attributes={
            "skills_sdk.source_receipt_digest": source_digest,
            "skills_sdk.blocker_count": len(blockers),
            "skills_sdk.redacted": True,
        },
    )
    return plan, root_span_id


def build_eval_trace_plan(receipt: dict[str, Any], source_digest: str | None = None) -> dict[str, Any]:
    if source_digest is None:
        source_digest = _sha256_json(receipt)
    source_kind = _source_kind(receipt)
    evidence = _profile_evidence(receipt, source_kind)
    blockers = [blocker for item in evidence for blocker in item["blockers"]]
    if source_kind == "unsupported_receipt":
        blockers.append("source_kind_unsupported")
    plan, root_span_id = _build_plan_spans(receipt, source_kind, source_digest, evidence, blockers)
    return {
        "trace_id": plan.trace_id,
        "root_span_id": root_span_id,
        "project_name": PHOENIX_PROJECT_NAME,
        "source_kind": source_kind,
        "source_receipt_digest": source_digest,
        "profile_evidence": evidence,
        "spans": plan.spans,
        "blockers": sorted(set(blockers)),
    }


OTLP_EXPORT_SCRIPT = r'''
import json
import sys
import time
import urllib.error
import urllib.request
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.common.v1.common_pb2 import AnyValue, KeyValue
from opentelemetry.proto.resource.v1.resource_pb2 import Resource
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, ScopeSpans, Span, Status

cfg = json.loads(sys.stdin.read())
now = time.time_ns()

def kv(key, value):
    target = AnyValue()
    if isinstance(value, bool):
        target.bool_value = value
    elif isinstance(value, int):
        target.int_value = value
    elif isinstance(value, float):
        target.double_value = value
    else:
        target.string_value = str(value)
    return KeyValue(key=key, value=target)

span_rows = cfg["plan"]["spans"]
span_id_to_children = {}
for row in span_rows:
    parent_id = row["parent_span_id"]
    if parent_id:
        span_id_to_children.setdefault(parent_id, []).append(row["span_id"])

span_timings = {}
for index, row in enumerate(span_rows):
    span_timings[row["span_id"]] = {
        "start": now + (index * 1000000),
        "end": now + ((index + 1) * 1000000),
    }

def get_max_descendant_end(span_id):
    children = span_id_to_children.get(span_id, [])
    if not children:
        return span_timings[span_id]["end"]
    child_ends = [get_max_descendant_end(child_id) for child_id in children]
    return max(child_ends)

for row in span_rows:
    span_id = row["span_id"]
    children = span_id_to_children.get(span_id, [])
    if children:
        max_child_end = get_max_descendant_end(span_id)
        span_timings[span_id]["end"] = max(span_timings[span_id]["end"], max_child_end + 1000000)

spans = []
for index, row in enumerate(span_rows):
    blocked = row["status"] in {"blocked", "fail", "failed", "error"}
    timing = span_timings[row["span_id"]]
    spans.append(Span(
        trace_id=bytes.fromhex(cfg["plan"]["trace_id"]),
        span_id=bytes.fromhex(row["span_id"]),
        parent_span_id=bytes.fromhex(row["parent_span_id"]) if row["parent_span_id"] else b"",
        name=row["name"],
        kind=Span.SPAN_KIND_INTERNAL,
        start_time_unix_nano=timing["start"],
        end_time_unix_nano=timing["end"],
        attributes=[kv(key, value) for key, value in row["attributes"].items()] + [
            kv("openinference.span.kind", row["span_kind"]),
        ],
        status=Status(code=Status.STATUS_CODE_ERROR if blocked else Status.STATUS_CODE_OK),
    ))

request = ExportTraceServiceRequest(resource_spans=[ResourceSpans(
    resource=Resource(attributes=[
        kv("service.name", "agent-skills"),
        kv("openinference.project.name", cfg["plan"]["project_name"]),
    ]),
    scope_spans=[ScopeSpans(spans=spans)],
)])
http_request = urllib.request.Request(
    cfg["endpoint"],
    data=request.SerializeToString(),
    headers={
        "content-type": "application/x-protobuf",
        "x-project-name": cfg["plan"]["project_name"],
    },
    method="POST",
)
try:
    with urllib.request.urlopen(http_request, timeout=cfg["timeout_seconds"]) as response:
        print(json.dumps({"status": "pass", "http_status": response.status}))
except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
    print(json.dumps({"status": "blocked", "error_class": type(exc).__name__}))
    raise SystemExit(2)
'''


def _run_export_process(
    plan: dict[str, Any],
    endpoint: str,
    otel_python: Path,
    timeout_seconds: float,
) -> subprocess.CompletedProcess[str] | dict[str, Any]:
    try:
        return subprocess.run(
            [otel_python.as_posix(), "-c", OTLP_EXPORT_SCRIPT],
            input=json.dumps(
                {"endpoint": endpoint, "plan": plan, "timeout_seconds": timeout_seconds},
                sort_keys=True,
            ),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds + 1.0,
        )
    except subprocess.TimeoutExpired:
        return {"status": "blocked", "error_class": "TimeoutExpired", "http_status": None}
    except OSError as exc:
        return {"status": "blocked", "error_class": type(exc).__name__, "http_status": None}


def _export_result(process: subprocess.CompletedProcess[str] | dict[str, Any]) -> dict[str, Any]:
    if isinstance(process, dict):
        return process
    try:
        payload = json.loads(process.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        payload = {"status": "blocked", "error_class": "MissingExportResult", "http_status": None}
    payload["returncode"] = process.returncode
    return payload


def emit_eval_trace_plan(
    plan: dict[str, Any],
    *,
    endpoint: str,
    otel_python: Path,
    timeout_seconds: float,
) -> dict[str, Any]:
    process = _run_export_process(plan, endpoint, otel_python, timeout_seconds)
    return _export_result(process)
