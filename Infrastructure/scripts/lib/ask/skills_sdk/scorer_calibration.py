from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCORER_CALIBRATION_SCHEMA_VERSION = "skills-sdk.scorer-calibration-receipt.v0"
SCORER_CALIBRATION_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/scorer-calibration-receipt.v0.schema.json"
)
SCORER_CALIBRATION_ACCEPTANCE_TRACE = ["Braintrust scorer validation", "PU-030", "VP-030"]
CALIBRATION_BUNDLE_SCHEMA_VERSION = "skills-sdk.scorer-calibration-bundle.v1"
DEFAULT_BUNDLE_RELATIVE_PATH = Path("references/scorer-calibration/manifest.json")
PASS_LABEL = "pass"
FAIL_LABEL = "fail"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "json_root_not_object"
    return loaded, None


def _load_jsonl(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], str(exc)
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            loaded = json.loads(line)
        except json.JSONDecodeError as exc:
            return rows, f"line {index}: {exc}"
        if not isinstance(loaded, dict):
            return rows, f"line {index}: json_root_not_object"
        rows.append(loaded)
    return rows, None


def _path_from_manifest(bundle_dir: Path, value: object, default: str) -> Path:
    raw = str(value or default)
    path = Path(raw)
    return path if path.is_absolute() else bundle_dir / path


def _number(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _label(value: object) -> str:
    return str(value or "").strip()


def _confusion_matrix(rows: list[dict[str, Any]]) -> dict[str, int]:
    matrix = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for row in rows:
        expected = _label(row.get("expected_label"))
        predicted = _label(row.get("predicted_label"))
        if expected == PASS_LABEL and predicted == PASS_LABEL:
            matrix["tp"] += 1
        elif expected == FAIL_LABEL and predicted == FAIL_LABEL:
            matrix["tn"] += 1
        elif expected == FAIL_LABEL and predicted == PASS_LABEL:
            matrix["fp"] += 1
        elif expected == PASS_LABEL and predicted == FAIL_LABEL:
            matrix["fn"] += 1
    return matrix


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _metrics(matrix: dict[str, int]) -> dict[str, float | None]:
    tp = matrix["tp"]
    tn = matrix["tn"]
    fp = matrix["fp"]
    fn = matrix["fn"]
    total = tp + tn + fp + fn
    return {
        "tpr": _ratio(tp, tp + fn),
        "tnr": _ratio(tn, tn + fp),
        "precision": _ratio(tp, tp + fp),
        "accuracy": _ratio(tp + tn, total),
    }


def _manifest_checks(repo_root: Path, bundle_path: Path, manifest: dict[str, Any], load_error: str | None) -> list[dict[str, Any]]:
    parameter_missing = _parameter_missing(manifest)
    return [
        _check("calibration_bundle_present", "pass" if bundle_path.is_file() else "blocker", "Skill must carry a scorer calibration bundle manifest.", [_repo_relative(repo_root, bundle_path)]),
        _check("calibration_bundle_parse", "blocker" if load_error else "pass", "Scorer calibration bundle manifest must parse as a JSON object.", [load_error] if load_error else []),
        _check("judge_parameters_present", "blocker" if parameter_missing else "pass", "Calibration bundle must record model, temperature, and trial_count.", parameter_missing),
        *_manifest_required_string_checks(manifest),
        _threshold_check(manifest),
        *_manifest_identity_checks(manifest),
    ]


def _parameter_missing(manifest: dict[str, Any]) -> list[str]:
    parameters = manifest.get("parameters")
    if not isinstance(parameters, dict):
        return ["parameters"]
    return [field for field in ("model", "temperature", "trial_count") if field not in parameters]


def _manifest_identity_checks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _check("calibration_bundle_schema_version", "pass" if manifest.get("schema_version") == CALIBRATION_BUNDLE_SCHEMA_VERSION else "blocker", "Calibration bundle must declare the supported schema_version.", [str(manifest.get("schema_version"))]),
        _check("calibration_split_held_out", "pass" if manifest.get("split") == "held_out" else "blocker", "Calibration bundle must identify the examples as held_out.", [str(manifest.get("split"))]),
    ]


def _manifest_required_string_checks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _required_string_check(manifest, "scorer_id", "scorer_id_present", "Calibration bundle must declare scorer_id."),
        _required_string_check(manifest, "scorer_version_or_digest", "scorer_version_or_digest_present", "Calibration bundle must declare scorer_version_or_digest."),
        _required_string_check(manifest, "prompt_version", "prompt_version_present", "Calibration bundle must declare prompt_version."),
    ]


def _required_string_check(manifest: dict[str, Any], field: str, check_id: str, message: str) -> dict[str, Any]:
    return _check(check_id, "pass" if str(manifest.get(field) or "").strip() else "blocker", message, [field])


def _threshold_check(manifest: dict[str, Any]) -> dict[str, Any]:
    threshold = _number(manifest.get("threshold"))
    return _check("threshold_valid", "pass" if threshold is not None and 0 < threshold <= 1 else "blocker", "Calibration threshold must be a number between 0 and 1.", [str(manifest.get("threshold"))])


def _example_shape_checks(rows: list[dict[str, Any]], examples_error: str | None) -> list[dict[str, Any]]:
    shape_errors = [
        error
        for index, row in enumerate(rows, start=1)
        for error in _example_shape_errors(index, row)
    ]
    return [
        _check("calibration_examples_parse", "blocker" if examples_error else "pass", "Calibration examples must parse as JSONL objects.", [examples_error] if examples_error else []),
        _check("calibration_example_shape", "blocker" if shape_errors else "pass", "Every calibration example must include id, labels, score, probe_type, and raw_artifact.", shape_errors),
    ]


def _example_shape_errors(index: int, row: dict[str, Any]) -> list[str]:
    row_id = str(row.get("id") or f"line-{index}")
    errors: list[str] = []
    if not str(row.get("id") or "").strip():
        errors.append(f"{row_id}:missing_id")
    for field in ("expected_label", "predicted_label"):
        if _label(row.get(field)) not in {PASS_LABEL, FAIL_LABEL}:
            errors.append(f"{row_id}:{field}")
    for field in ("raw_artifact", "probe_type"):
        if not str(row.get(field) or "").strip():
            errors.append(f"{row_id}:{field}")
    if _number(row.get("score")) is None:
        errors.append(f"{row_id}:score")
    return errors


def _threshold_checks(rows: list[dict[str, Any]], threshold: float | None) -> list[dict[str, Any]]:
    if threshold is None:
        return []
    mismatches: list[str] = []
    for row in rows:
        score = _number(row.get("score"))
        if score is None:
            continue
        expected_prediction = PASS_LABEL if score >= threshold else FAIL_LABEL
        if _label(row.get("predicted_label")) != expected_prediction:
            mismatches.append(str(row.get("id") or "unknown"))
    return [
        _check("score_threshold_consistent", "blocker" if mismatches else "pass", "Predicted labels must match the bundle threshold and per-example score.", mismatches)
    ]


def _raw_artifact_checks(repo_root: Path, bundle_dir: Path, rows: list[dict[str, Any]], raw_dir: Path) -> list[dict[str, Any]]:
    missing, mismatches = _raw_artifact_findings(bundle_dir, rows)
    return [
        _check("raw_artifact_dir_present", "pass" if raw_dir.is_dir() else "blocker", "Calibration bundle must include a raw artifact directory.", [_repo_relative(repo_root, raw_dir)]),
        _check("raw_artifacts_present", "blocker" if missing else "pass", "Every calibration example must point to an existing raw artifact.", missing),
        _check("raw_artifacts_match_examples", "blocker" if mismatches else "pass", "Raw scorer artifacts must match example ids, labels, and scores.", mismatches),
    ]


def _raw_artifact_findings(bundle_dir: Path, rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    mismatches: list[str] = []
    for row in rows:
        raw_value, raw_path = _raw_artifact_path(bundle_dir, row)
        if not raw_path.is_file():
            missing.append(raw_value or str(row.get("id") or ""))
        else:
            mismatches.extend(_raw_artifact_mismatches(raw_value, raw_path, row))
    return missing, mismatches


def _raw_artifact_path(bundle_dir: Path, row: dict[str, Any]) -> tuple[str, Path]:
    raw_value = str(row.get("raw_artifact") or "")
    raw_path = Path(raw_value)
    return raw_value, raw_path if raw_path.is_absolute() else bundle_dir / raw_path


def _raw_artifact_mismatches(raw_value: str, raw_path: Path, row: dict[str, Any]) -> list[str]:
    raw_payload, raw_error = _load_json(raw_path)
    if raw_error or raw_payload is None:
        return [f"{raw_value}:parse"]
    checks = {
        "id": raw_payload.get("id") == row.get("id"),
        "expected_label": raw_payload.get("expected_label") == row.get("expected_label"),
        "predicted_label": raw_payload.get("predicted_label") == row.get("predicted_label"),
        "score": _number(raw_payload.get("score")) == _number(row.get("score")),
    }
    return [f"{raw_value}:{field}" for field, passed in checks.items() if not passed]


def _confusion_checks(manifest: dict[str, Any], rows: list[dict[str, Any]], matrix: dict[str, int]) -> list[dict[str, Any]]:
    limits = _confusion_limits(manifest)
    return [
        _minimum_check("held_out_example_count", len(rows), limits["minimum_examples"], "Calibration bundle must include the declared minimum held-out examples."),
        _minimum_check("true_positive_coverage", matrix["tp"], limits["minimum_tp"], "Calibration must include enough known-pass examples caught as pass."),
        _minimum_check("true_negative_coverage", matrix["tn"], limits["minimum_tn"], "Calibration must include enough known-fail examples caught as fail."),
        _maximum_check("false_positive_limit", matrix["fp"], limits["max_fp"], "Calibration false positives must stay within the declared limit."),
        _maximum_check("false_negative_limit", matrix["fn"], limits["max_fn"], "Calibration false negatives must stay within the declared limit."),
    ]


def _confusion_limits(manifest: dict[str, Any]) -> dict[str, int | None]:
    return {
        "minimum_examples": _manifest_int_limit(manifest, "minimum_examples", default=1),
        "minimum_tp": _manifest_int_limit(manifest, "minimum_true_positives", default=1),
        "minimum_tn": _manifest_int_limit(manifest, "minimum_true_negatives", default=1),
        "max_fp": _manifest_int_limit(manifest, "max_false_positives", default=0),
        "max_fn": _manifest_int_limit(manifest, "max_false_negatives", default=0),
    }


def _manifest_int_limit(manifest: dict[str, Any], key: str, *, default: int) -> int | None:
    raw = manifest.get(key, default)
    if isinstance(raw, bool):
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


def _minimum_check(check_id: str, observed: int, minimum: int | None, message: str) -> dict[str, Any]:
    if minimum is None:
        return _check(check_id, "blocker", message, ["invalid_limit"])
    return _check(check_id, "pass" if observed >= minimum else "blocker", message, [f"{observed}<{minimum}"] if observed < minimum else [])


def _maximum_check(check_id: str, observed: int, maximum: int | None, message: str) -> dict[str, Any]:
    if maximum is None:
        return _check(check_id, "blocker", message, ["invalid_limit"])
    return _check(check_id, "pass" if observed <= maximum else "blocker", message, [f"{observed}>{maximum}"] if observed > maximum else [])


def _quality_checks(
    repo_root: Path,
    *,
    bundle_path: Path,
    manifest: dict[str, Any],
    manifest_error: str | None,
    rows: list[dict[str, Any]],
    examples_error: str | None,
    examples_path: Path,
    raw_dir: Path,
    matrix: dict[str, int],
) -> list[dict[str, Any]]:
    checks = _manifest_checks(repo_root, bundle_path, manifest, manifest_error)
    checks.append(_check("calibration_examples_present", "pass" if examples_path.is_file() else "blocker", "Calibration bundle must include an examples JSONL artifact.", [_repo_relative(repo_root, examples_path)]))
    checks.extend(_example_shape_checks(rows, examples_error))
    checks.extend(_threshold_checks(rows, _number(manifest.get("threshold"))))
    checks.extend(_raw_artifact_checks(repo_root, bundle_path.parent, rows, raw_dir))
    checks.extend(_confusion_checks(manifest, rows, matrix))
    return checks


def _receipt(
    repo_root: Path,
    *,
    query: str,
    skill_md: Path,
    bundle_path: Path,
    examples_path: Path,
    raw_dir: Path,
    manifest: dict[str, Any],
    rows: list[dict[str, Any]],
    matrix: dict[str, int],
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": SCORER_CALIBRATION_SCHEMA_VERSION,
        "schema_uri": SCORER_CALIBRATION_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "scorer_calibration_preview",
        "query": query,
        "skill_path": _repo_relative(repo_root, skill_md),
        "bundle_path": _repo_relative(repo_root, bundle_path),
        "examples_path": _repo_relative(repo_root, examples_path),
        "raw_artifacts_dir": _repo_relative(repo_root, raw_dir),
        "ready": not blockers,
        "scorer_id": str(manifest.get("scorer_id") or ""),
        "scorer_version_or_digest": str(manifest.get("scorer_version_or_digest") or ""),
        "prompt_version": str(manifest.get("prompt_version") or ""),
        "threshold": _number(manifest.get("threshold")),
        "parameters": manifest.get("parameters") if isinstance(manifest.get("parameters"), dict) else {},
        "example_count": len(rows),
        "confusion_matrix": matrix,
        "metrics": _metrics(matrix),
        "quality_checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "promotion_performed": False,
        "acceptance_trace": SCORER_CALIBRATION_ACCEPTANCE_TRACE,
        "agent_summary": f"scorer calibration preview checked {len(rows)} held-out example(s) for {query}.",
    }


def build_scorer_calibration_receipt(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    skill_md = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    bundle_path = skill_md.parent / DEFAULT_BUNDLE_RELATIVE_PATH
    manifest, manifest_error = _load_json(bundle_path) if bundle_path.is_file() else ({}, "missing_calibration_bundle")
    manifest = manifest or {}
    examples_path = _path_from_manifest(bundle_path.parent, manifest.get("examples_path"), "examples.jsonl")
    raw_dir = _path_from_manifest(bundle_path.parent, manifest.get("raw_artifacts_dir"), "raw")
    rows, examples_error = _load_jsonl(examples_path) if examples_path.is_file() else ([], "missing_examples_jsonl")
    matrix = _confusion_matrix(rows)
    checks = _quality_checks(
        repo_root,
        bundle_path=bundle_path,
        manifest=manifest,
        manifest_error=manifest_error,
        rows=rows,
        examples_error=examples_error,
        examples_path=examples_path,
        raw_dir=raw_dir,
        matrix=matrix,
    )
    return _receipt(
        repo_root,
        query=query,
        skill_md=skill_md,
        bundle_path=bundle_path,
        examples_path=examples_path,
        raw_dir=raw_dir,
        manifest=manifest,
        rows=rows,
        matrix=matrix,
        checks=checks,
    )
