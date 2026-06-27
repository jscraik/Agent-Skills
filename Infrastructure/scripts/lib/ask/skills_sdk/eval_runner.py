from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


EVAL_CASE_SCHEMA_VERSION = "skills-sdk.eval-case.v0"
EVAL_RUN_RECEIPT_SCHEMA_VERSION = "skills-sdk.eval-run-receipt.v0"
EVAL_RUN_RECEIPT_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/eval-run-receipt.v0.schema.json"
)
EVAL_RUN_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]
_ALLOWED_PREFLIGHT_WARNING_PREFIXES = (
    "Using isolated CODEX_HOME for live eval session writes:",
)


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _blocked_receipt(
    repo_root: Path,
    dataset_path: Path,
    blocker: str,
    *,
    skill_ir_schema_version: str | None = None,
    package_id: str | None = None,
    package_digest: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": EVAL_RUN_RECEIPT_SCHEMA_VERSION,
        "schema_uri": EVAL_RUN_RECEIPT_SCHEMA_URI,
        "status": "blocked",
        "runner": "deterministic_jsonl_v0",
        "dataset_path": _repo_relative(repo_root, dataset_path),
        "dataset_digest": "sha256:" + ("0" * 64),
        "skill_ir_schema_version": skill_ir_schema_version,
        "package_id": package_id,
        "package_digest": package_digest,
        "target_path": None,
        "mode": None,
        "case_count": 0,
        "passed_count": 0,
        "failed_count": 0,
        "cases": [],
        "blockers": [blocker],
        "mutation_performed": False,
        "acceptance_trace": EVAL_RUN_ACCEPTANCE_TRACE,
    }


CASE_FIELDS = ("schema_version", "case_id", "input", "expected", "actual", "oracle", "acceptance_trace")


def _validate_case(item: object, line_number: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(f"line {line_number} must be a JSON object")
    missing = [key for key in CASE_FIELDS if key not in item]
    if missing:
        raise ValueError(f"line {line_number} missing required field(s): {', '.join(missing)}")
    if item["schema_version"] != EVAL_CASE_SCHEMA_VERSION:
        raise ValueError(f"line {line_number} has unsupported schema_version: {item['schema_version']}")
    if item["oracle"] != "exact_match":
        raise ValueError(f"line {line_number} has unsupported oracle: {item['oracle']}")
    for key in ("case_id", "input", "expected", "actual"):
        if not isinstance(item[key], str):
            raise ValueError(f"line {line_number} field {key} must be a string")
    if not item["case_id"] or not item["input"] or not item["expected"]:
        raise ValueError(f"line {line_number} case_id, input, and expected must be non-empty")
    _validate_trace(item["acceptance_trace"], line_number)
    return item


def _validate_trace(trace: object, line_number: int) -> None:
    if not isinstance(trace, list) or not trace or not all(isinstance(value, str) and value for value in trace):
        raise ValueError(f"line {line_number} acceptance_trace must be a non-empty string list")


def _load_json_cases(dataset_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else [payload]
    return [_validate_case(item, index) for index, item in enumerate(items, start=1)]


def _load_jsonl_cases(dataset_path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_number} is not valid JSON: {exc.msg}") from exc
            cases.append(_validate_case(item, line_number))
    if not cases:
        raise ValueError("dataset has no eval cases")
    return cases


def _load_cases(dataset_path: Path) -> list[dict[str, Any]]:
    cases = _load_jsonl_cases(dataset_path) if dataset_path.suffix == ".jsonl" else _load_json_cases(dataset_path)
    if not cases:
        raise ValueError("dataset has no eval cases")
    return cases


def _case_result(case: dict[str, Any]) -> dict[str, str]:
    passed = case["actual"] == case["expected"]
    return {
        "case_id": case["case_id"],
        "status": "pass" if passed else "fail",
        "oracle": case["oracle"],
        "expected": case["expected"],
        "actual": case["actual"],
    }


def _summary_count(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return max(value, 0)
    if isinstance(value, list):
        return len(value)
    return 0


def _actionable_preflight_warnings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    warnings = [str(item) for item in value if str(item).strip()]
    return [
        warning
        for warning in warnings
        if not any(warning.startswith(prefix) for prefix in _ALLOWED_PREFLIGHT_WARNING_PREFIXES)
    ]


def _integer_summary(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): raw_value
        for key, raw_value in value.items()
        if isinstance(raw_value, int) and not isinstance(raw_value, bool) and raw_value >= 0
    }


def _expected_signal_summary(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"runs": 0, "average": None, "minimum": None, "risky_cases": []}
    risky_cases = value.get("risky_cases")
    return {
        "runs": _summary_count(value.get("runs")),
        "average": value.get("average") if isinstance(value.get("average"), (int, float)) else None,
        "minimum": value.get("minimum") if isinstance(value.get("minimum"), (int, float)) else None,
        "risky_cases": [str(item) for item in risky_cases] if isinstance(risky_cases, list) else [],
    }


def _quality_assertion(assertion_id: str, expected: str, actual: object, passes: bool) -> dict[str, str]:
    return {
        "id": assertion_id,
        "status": "pass" if passes else "fail",
        "expected": expected,
        "actual": str(actual),
    }


def _quality_gate_fields(scorecard: dict[str, Any]) -> dict[str, Any]:
    decision = str(scorecard.get("decision") or "").strip().lower() or None
    passed = scorecard.get("passed")
    preflight_warnings = _actionable_preflight_warnings(scorecard.get("preflight_warnings"))
    security_screening = scorecard.get("security_dependency_screening")
    return {
        "scorecard_schema_version": str(scorecard.get("schema_version") or "") or None,
        "decision": decision,
        "passed": passed if isinstance(passed, bool) else None,
        "promotion_eligible": scorecard.get("promotion_eligible")
        if isinstance(scorecard.get("promotion_eligible"), bool)
        else None,
        "blocked_cases": _summary_count(scorecard.get("blocked_cases")),
        "tier1_failures": _summary_count(scorecard.get("tier1_failures")),
        "tier2_findings": _summary_count(scorecard.get("tier2_findings")),
        "preflight_warning_count": len(preflight_warnings),
        "readiness_summary": _integer_summary(scorecard.get("readiness_summary")),
        "expected_signal_summary": _expected_signal_summary(scorecard.get("expected_signal_summary")),
        "security_dependency_screening_status": (
            str(security_screening.get("status"))
            if isinstance(security_screening, dict) and security_screening.get("status") is not None
            else None
        ),
    }


def _quality_assertions(fields: dict[str, Any]) -> list[dict[str, str]]:
    expected_signals = fields["expected_signal_summary"]
    assertions = [
        _quality_assertion("scorecard_decision_passes", "decision == pass", fields["decision"], fields["decision"] == "pass"),
        _quality_assertion("scorecard_passed_true", "passed == true", fields["passed"], fields["passed"] is True),
        _quality_assertion("blocked_cases_zero", "blocked_cases == 0", fields["blocked_cases"], fields["blocked_cases"] == 0),
        _quality_assertion("tier1_failures_zero", "tier1_failures == 0", fields["tier1_failures"], fields["tier1_failures"] == 0),
        _quality_assertion("tier2_findings_zero", "tier2_findings == 0", fields["tier2_findings"], fields["tier2_findings"] == 0),
        _quality_assertion(
            "preflight_warnings_zero",
            "preflight_warnings == 0",
            fields["preflight_warning_count"],
            fields["preflight_warning_count"] == 0,
        ),
        _quality_assertion(
            "expected_signal_risky_cases_zero",
            "expected_signal_summary.risky_cases == 0",
            len(expected_signals["risky_cases"]),
            len(expected_signals["risky_cases"]) == 0,
        ),
    ]
    return assertions


def internal_scorecard_quality_gates(scorecard: dict[str, Any]) -> dict[str, Any] | None:
    """Extract calibrated SDK quality gates from the internal skill eval scorecard."""
    if not scorecard:
        return None
    fields = _quality_gate_fields(scorecard)
    assertions = _quality_assertions(fields)
    failed_assertions = [item["id"] for item in assertions if item["status"] != "pass"]
    return {
        "source": "internal_scorecard",
        **fields,
        "assertions": assertions,
        "failed_assertions": failed_assertions,
    }


def _receipt(
    repo_root: Path,
    dataset_path: Path,
    cases: list[dict[str, str]],
    skill_ir_schema_version: str | None,
    package_id: str | None,
    package_digest: str | None,
) -> dict[str, Any]:
    failed_count = sum(1 for item in cases if item["status"] == "fail")
    return {
        "schema_version": EVAL_RUN_RECEIPT_SCHEMA_VERSION,
        "schema_uri": EVAL_RUN_RECEIPT_SCHEMA_URI,
        "status": "fail" if failed_count else "pass",
        "runner": "deterministic_jsonl_v0",
        "dataset_path": _repo_relative(repo_root, dataset_path),
        "dataset_digest": _sha256_file(dataset_path),
        "skill_ir_schema_version": skill_ir_schema_version,
        "package_id": package_id,
        "package_digest": package_digest,
        "target_path": None,
        "mode": None,
        "case_count": len(cases),
        "passed_count": len(cases) - failed_count,
        "failed_count": failed_count,
        "cases": cases,
        "blockers": [],
        "mutation_performed": False,
        "acceptance_trace": EVAL_RUN_ACCEPTANCE_TRACE,
    }


def _package_identity_fields(
    skill_ir_schema_version: str | None,
    package_id: str | None,
    package_digest: str | None,
) -> dict[str, str | None]:
    return {
        "skill_ir_schema_version": skill_ir_schema_version,
        "package_id": package_id,
        "package_digest": package_digest,
    }


def run_deterministic_eval(
    repo_root: Path,
    *,
    dataset: str,
    skill_ir_schema_version: str | None = None,
    package_id: str | None = None,
    package_digest: str | None = None,
) -> dict[str, Any]:
    """Run exact-match JSONL eval cases without invoking providers or mutating state."""
    dataset_path = Path(dataset)
    if not dataset_path.is_absolute():
        dataset_path = repo_root / dataset_path
    package_identity = _package_identity_fields(skill_ir_schema_version, package_id, package_digest)
    if not dataset_path.is_file():
        return _blocked_receipt(
            repo_root,
            dataset_path,
            f"dataset not found: {_repo_relative(repo_root, dataset_path)}",
            **package_identity,
        )

    try:
        cases = _load_cases(dataset_path)
    except ValueError as exc:
        return _blocked_receipt(
            repo_root,
            dataset_path,
            str(exc),
            **package_identity,
        )

    return _receipt(
        repo_root,
        dataset_path,
        [_case_result(case) for case in cases],
        **package_identity,
    )
