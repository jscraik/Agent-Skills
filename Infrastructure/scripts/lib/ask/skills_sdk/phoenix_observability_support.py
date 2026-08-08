from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any


PHOENIX_STATUS_SCHEMA_VERSION = "skills-sdk.phoenix-status-receipt.v0"
PHOENIX_STATUS_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-status-receipt.v0.schema.json"
PHOENIX_MIRROR_SCHEMA_VERSION = "skills-sdk.phoenix-mirror-receipt.v0"
PHOENIX_MIRROR_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-mirror-receipt.v0.schema.json"
PHOENIX_SMOKE_SCHEMA_VERSION = "skills-sdk.phoenix-smoke-receipt.v0"
PHOENIX_SMOKE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-smoke-receipt.v0.schema.json"
PHOENIX_EVAL_TRACE_SCHEMA_VERSION = "skills-sdk.phoenix-eval-trace-receipt.v1"
PHOENIX_EVAL_TRACE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/phoenix-eval-trace-receipt.v1.schema.json"
PHOENIX_ACCEPTANCE_TRACE = ("phoenix-oss-eval-observability-workflow-2026-07-08", "PU-026")
PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT = 10
PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT = 20


class PhoenixObservabilityError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


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


def _find_nested_receipt(data: dict[str, Any]) -> dict[str, Any] | None:
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
    return None


def _find_receipt(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            nested = _find_nested_receipt(data)
            if nested is not None:
                return nested
        receipt = payload.get("receipt")
        if isinstance(receipt, dict):
            return receipt
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


def _case_rows_from_cases(cases: list[Any], trace_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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
    return rows


def _candidate_rows(candidates: list[Any], trace_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
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


def _case_rows(receipt: dict[str, Any], trace_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cases = receipt.get("cases")
    if isinstance(cases, list):
        rows.extend(_case_rows_from_cases(cases, trace_id))
    candidates = receipt.get("scenario_candidates")
    if isinstance(candidates, list):
        rows.extend(_candidate_rows(candidates, trace_id))
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
