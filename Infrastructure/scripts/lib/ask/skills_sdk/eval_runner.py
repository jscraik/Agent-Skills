from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


EVAL_CASE_SCHEMA_VERSION = "skills-sdk.eval-case.v0"
EVAL_RUN_RECEIPT_SCHEMA_VERSION = "skills-sdk.eval-run-receipt.v0"
EVAL_RUN_RECEIPT_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-run-receipt.v0.schema.json"
)
EVAL_RUN_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]


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


def _blocked_receipt(repo_root: Path, dataset_path: Path, blocker: str) -> dict[str, Any]:
    return {
        "schema_version": EVAL_RUN_RECEIPT_SCHEMA_VERSION,
        "schema_uri": EVAL_RUN_RECEIPT_SCHEMA_URI,
        "status": "blocked",
        "runner": "deterministic_jsonl_v0",
        "dataset_path": _repo_relative(repo_root, dataset_path),
        "dataset_digest": "sha256:" + ("0" * 64),
        "skill_ir_schema_version": None,
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


def _receipt(repo_root: Path, dataset_path: Path, cases: list[dict[str, str]], skill_ir_schema_version: str | None) -> dict[str, Any]:
    failed_count = sum(1 for item in cases if item["status"] == "fail")
    return {
        "schema_version": EVAL_RUN_RECEIPT_SCHEMA_VERSION,
        "schema_uri": EVAL_RUN_RECEIPT_SCHEMA_URI,
        "status": "fail" if failed_count else "pass",
        "runner": "deterministic_jsonl_v0",
        "dataset_path": _repo_relative(repo_root, dataset_path),
        "dataset_digest": _sha256_file(dataset_path),
        "skill_ir_schema_version": skill_ir_schema_version,
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


def run_deterministic_eval(
    repo_root: Path,
    *,
    dataset: str,
    skill_ir_schema_version: str | None = None,
) -> dict[str, Any]:
    """Run exact-match JSONL eval cases without invoking providers or mutating state."""
    dataset_path = Path(dataset)
    if not dataset_path.is_absolute():
        dataset_path = repo_root / dataset_path
    if not dataset_path.is_file():
        return _blocked_receipt(repo_root, dataset_path, f"dataset not found: {_repo_relative(repo_root, dataset_path)}")

    try:
        cases = _load_cases(dataset_path)
    except ValueError as exc:
        return _blocked_receipt(repo_root, dataset_path, str(exc))

    return _receipt(repo_root, dataset_path, [_case_result(case) for case in cases], skill_ir_schema_version)
