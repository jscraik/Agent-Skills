from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def build_scenario_set_parity_checks(
    repo_root: Path,
    skill_dir: Path,
    canonical_ids: set[str],
    tessl_staged_json: Path | None,
    tessl_score_json: Path | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if tessl_staged_json is None and tessl_score_json is None:
        return None, []
    expected_ids = canonical_ids | _reviewed_fixture_ids(skill_dir)
    parity = _empty_parity(canonical_ids, expected_ids)
    checks: list[dict[str, Any]] = []
    if tessl_staged_json is not None:
        checks.append(_staged_parity_check(repo_root, tessl_staged_json, expected_ids, parity))
    if tessl_score_json is not None:
        checks.append(_score_parity_check(repo_root, tessl_score_json, expected_ids, parity))
    return parity, checks


def _empty_parity(canonical_ids: set[str], expected_ids: set[str]) -> dict[str, Any]:
    return {
        "canonical_count": len(canonical_ids),
        "reviewed_fixture_count": len(expected_ids - canonical_ids),
        "staged_tessl_count": None,
        "score_receipt_path_count": None,
        "score_receipt_declared_count": None,
        "missing_from_staged": [],
        "extra_in_staged": [],
        "missing_from_score_receipt": [],
        "extra_in_score_receipt": [],
    }


def _staged_parity_check(repo_root: Path, path: Path, expected_ids: set[str], parity: dict[str, Any]) -> dict[str, Any]:
    payload, error = _load_json_object(path) if path.is_file() else (None, "missing_staged_tessl_json")
    if payload is None:
        return _readable_check(repo_root, path, "scenario_set_staged_tessl_readable", error or "invalid_json")
    staged_ids = _staged_tessl_ids(payload)
    return _diff_check(
        "scenario_set_staged_tessl_matches_sdk",
        "Staged Tessl scenarios must match canonical evals.yaml plus reviewed fixture scenarios.",
        expected_ids,
        staged_ids,
        parity,
        missing_key="missing_from_staged",
        extra_key="extra_in_staged",
        count_key="staged_tessl_count",
    )


def _score_parity_check(repo_root: Path, path: Path, expected_ids: set[str], parity: dict[str, Any]) -> dict[str, Any]:
    payload, error = _load_json_object(path) if path.is_file() else (None, "missing_tessl_score_json")
    receipt = _tessl_score_receipt(payload) if payload is not None else None
    if receipt is None:
        return _readable_check(repo_root, path, "scenario_set_score_receipt_readable", error or "missing_receipt")
    score_ids, declared_count = _score_receipt_ids(receipt)
    parity["score_receipt_path_count"] = len(score_ids)
    parity["score_receipt_declared_count"] = declared_count
    check = _diff_check(
        "scenario_set_score_receipt_matches_sdk",
        "Tessl score receipt scenario paths and declared count must match the SDK scenario universe.",
        expected_ids,
        score_ids,
        parity,
        missing_key="missing_from_score_receipt",
        extra_key="extra_in_score_receipt",
        count_key=None,
    )
    if declared_count is not None and declared_count != len(expected_ids):
        check["status"] = "blocker"
        check["evidence"].append(f"declared_count:{declared_count}:expected:{len(expected_ids)}")
    return check


def _diff_check(
    check_id: str,
    message: str,
    expected_ids: set[str],
    observed_ids: set[str],
    parity: dict[str, Any],
    *,
    missing_key: str,
    extra_key: str,
    count_key: str | None,
) -> dict[str, Any]:
    missing = sorted(expected_ids - observed_ids)
    extra = sorted(observed_ids - expected_ids)
    parity[missing_key] = missing
    parity[extra_key] = extra
    if count_key is not None:
        parity[count_key] = len(observed_ids)
    return _check(
        check_id,
        "blocker" if missing or extra else "pass",
        message,
        [f"missing:{item}" for item in missing] + [f"extra:{item}" for item in extra],
    )


def _readable_check(repo_root: Path, path: Path, check_id: str, evidence: str) -> dict[str, Any]:
    message = "Scenario-set parity requires readable Tessl evidence when supplied."
    return _check(check_id, "blocker", message, [_repo_relative(repo_root, path), evidence])


def _load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "json_not_object"
    return loaded, None


def _reviewed_fixture_ids(skill_dir: Path) -> set[str]:
    evals_dir = skill_dir / "references" / "evals"
    if not evals_dir.is_dir():
        return set()
    return {
        f"generated-eval.{path.stem.removeprefix('eval.')}"
        for path in evals_dir.glob("eval.*.md")
        if path.is_file()
    }


def _staged_tessl_ids(payload: dict[str, Any]) -> set[str]:
    staged_files = _find_first_list(payload, "staged_files") or []
    return {
        match.group(1)
        for item in staged_files
        if (match := re.search(r"(?:^|/)evals/([^/]+)/task\.md$", str(item)))
    }


def _find_first_list(value: Any, key: str) -> list[Any] | None:
    if isinstance(value, dict):
        candidate = value.get(key)
        if isinstance(candidate, list):
            return candidate
        return _find_in_children(value.values(), key)
    if isinstance(value, list):
        return _find_in_children(value, key)
    return None


def _find_in_children(values: Any, key: str) -> list[Any] | None:
    for nested in values:
        found = _find_first_list(nested, key)
        if found is not None:
            return found
    return None


def _tessl_score_receipt(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if payload is None:
        return None
    data = payload.get("data")
    if isinstance(data, dict):
        score = data.get("skills_sdk_eval_tessl_score")
        if isinstance(score, dict) and isinstance(score.get("receipt"), dict):
            return score["receipt"]
    if isinstance(payload.get("receipt"), dict):
        return payload["receipt"]
    return payload if payload.get("schema_version") == "skills-sdk.tessl-score-receipt.v0" else None


def _score_receipt_ids(receipt: dict[str, Any]) -> tuple[set[str], int | None]:
    score_summary = receipt.get("score_summary") if isinstance(receipt.get("score_summary"), dict) else {}
    feedback_loop = receipt.get("feedback_loop") if isinstance(receipt.get("feedback_loop"), dict) else {}
    ids = _regression_ids(score_summary) | _string_ids(score_summary.get("ties")) | _win_ids(score_summary.get("wins"))
    ids |= _string_ids(feedback_loop.get("regression_paths"))
    declared = score_summary.get("scenario_count")
    return ids, declared if isinstance(declared, int) else None


def _regression_ids(score_summary: dict[str, Any]) -> set[str]:
    return {
        item["path"]
        for item in score_summary.get("regressions") or []
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def _win_ids(value: Any) -> set[str]:
    ids = _string_ids(value)
    ids.update(item["path"] for item in value or [] if isinstance(item, dict) and isinstance(item.get("path"), str))
    return ids


def _string_ids(value: Any) -> set[str]:
    return {item for item in value or [] if isinstance(item, str)}


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}
