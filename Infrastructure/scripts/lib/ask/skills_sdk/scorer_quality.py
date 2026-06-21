from __future__ import annotations

from pathlib import Path
from typing import Any


SCORER_QUALITY_SCHEMA_VERSION = "skills-sdk.scorer-quality-receipt.v0"
SCORER_QUALITY_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/scorer-quality-receipt.v0.schema.json"
)
SCORER_QUALITY_ACCEPTANCE_TRACE = ["Braintrust scorer validation", "PU-030", "VP-030"]
ALLOWED_SCORER_TYPES = {"deterministic", "llm_judge", "hybrid", "external_tessl"}
ALLOWED_SCOPES = {"span", "trace", "suite"}
REQUIRED_CALIBRATION_PROBES = {
    "obvious_correct",
    "obvious_wrong",
    "short_correct_vs_verbose_wrong",
    "rubric_copying_rejected",
    "skill_name_mention_not_enough",
    "evidence_lane_overclaim_rejected",
}
REQUIRED_SEGMENTATION_FIELDS = {"category", "claim_ids", "eval_modes"}
LLM_SCORER_TYPES = {"llm_judge", "hybrid", "external_tessl"}


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _yaml_safe_load(text: str) -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise ValueError("pyyaml_unavailable") from exc
    return yaml.safe_load(text)


def _load_evals(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = _yaml_safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "evals_yaml_not_object"
    return loaded, None


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_set(value: Any) -> set[str]:
    return {str(item) for item in _list(value)}


def _calibration_probe_types(scorer_quality: dict[str, Any]) -> set[str]:
    return {
        str(item.get("probe_type"))
        for item in _list(scorer_quality.get("calibration_cases"))
        if isinstance(item, dict) and item.get("probe_type")
    }


def _calibration_case_ids(scorer_quality: dict[str, Any]) -> list[str]:
    return [
        str(item.get("id") or f"case-{index}")
        for index, item in enumerate(_list(scorer_quality.get("calibration_cases")))
        if isinstance(item, dict)
    ]


def _has_expected_outcome(item: dict[str, Any]) -> bool:
    return any(key in item and str(item[key]).strip() for key in ("expected_score", "expected_label", "expected_direction"))


def _calibration_outcome_checks(scorer_quality: dict[str, Any]) -> dict[str, list[str]]:
    missing: list[str] = []
    for index, item in enumerate(_list(scorer_quality.get("calibration_cases"))):
        if isinstance(item, dict) and not _has_expected_outcome(item):
            missing.append(str(item.get("id") or f"case-{index}"))
    return {"missing_expected_outcome": missing}


def _requires_rationale(scorer_type: str) -> bool:
    return scorer_type in LLM_SCORER_TYPES


def _rationale_checks(scorer_quality: dict[str, Any], scorer_type: str) -> list[dict[str, Any]]:
    rationale = _mapping(scorer_quality.get("rationale_audit"))
    if not _requires_rationale(scorer_type):
        return []
    required = rationale.get("required") is True
    sampled_count = rationale.get("sampled_count")
    sampled_ok = isinstance(sampled_count, int) and sampled_count >= 3
    return [
        _check(
            "rationale_audit_required",
            "pass" if required else "blocker",
            "LLM or external judge scorers must require rationale review before score trends are trusted.",
            [] if required else ["rationale_audit.required"],
        ),
        _check(
            "rationale_audit_sampled",
            "pass" if sampled_ok else "blocker",
            "Rationale audit must sample at least 3 judge decisions.",
            [] if sampled_ok else [f"sampled_count:{sampled_count}"],
        ),
    ]


def _parameters_checks(scorer_quality: dict[str, Any], scorer_type: str) -> list[dict[str, Any]]:
    parameters = _mapping(scorer_quality.get("parameters"))
    if not _requires_rationale(scorer_type):
        return []
    missing = [field for field in ("model", "temperature", "trial_count") if field not in parameters]
    return [
        _check(
            "judge_parameters_versioned",
            "blocker" if missing else "pass",
            "LLM or external judge scorers must record model, temperature, and trial count parameters.",
            missing,
        )
    ]


def _presence_checks(repo_root: Path, evals_path: Path, scorer_quality: dict[str, Any], load_error: str | None) -> list[dict[str, Any]]:
    return [
        _check("evals_yaml_present", "pass" if evals_path.is_file() else "blocker", "Skill must carry references/evals.yaml.", [_repo_relative(repo_root, evals_path)]),
        _check("evals_yaml_parse", "blocker" if load_error else "pass", "references/evals.yaml must parse as YAML object.", [load_error] if load_error else []),
        _check("scorer_quality_declared", "pass" if scorer_quality else "blocker", "references/evals.yaml must declare scorer_quality before score trends are trusted.", [_repo_relative(repo_root, evals_path)]),
    ]


def _identity_checks(scorer_quality: dict[str, Any]) -> list[dict[str, Any]]:
    scorer_type = str(scorer_quality.get("scorer_type") or "")
    scope = str(scorer_quality.get("scope") or "")
    pass_threshold = scorer_quality.get("pass_threshold")
    return [
        _check("scorer_id_present", "pass" if str(scorer_quality.get("scorer_id") or "").strip() else "blocker", "scorer_quality must declare a stable scorer_id.", ["scorer_id"]),
        _check("scorer_type_allowed", "pass" if scorer_type in ALLOWED_SCORER_TYPES else "blocker", "scorer_type must be deterministic, llm_judge, hybrid, or external_tessl.", [scorer_type]),
        _check("scorer_scope_allowed", "pass" if scope in ALLOWED_SCOPES else "blocker", "scope must be span, trace, or suite.", [scope]),
        _check("scorer_version_or_digest_present", "pass" if str(scorer_quality.get("scorer_version_or_digest") or "").strip() else "blocker", "Scorer prompt or code must carry a version or digest.", ["scorer_version_or_digest"]),
        _check("pass_threshold_valid", "pass" if isinstance(pass_threshold, (int, float)) and 0 < float(pass_threshold) <= 1 else "blocker", "pass_threshold must be a number between 0 and 1.", [str(pass_threshold)]),
        _check("deterministic_checks_first", "pass" if scorer_quality.get("deterministic_checks_first") is True else "blocker", "Scorer quality must prefer deterministic checks before LLM judges.", ["deterministic_checks_first"]),
    ]


def _calibration_checks(repo_root: Path, evals_path: Path, scorer_quality: dict[str, Any]) -> list[dict[str, Any]]:
    probe_types = _calibration_probe_types(scorer_quality)
    missing_probes = sorted(REQUIRED_CALIBRATION_PROBES - probe_types)
    outcome_gaps = _calibration_outcome_checks(scorer_quality)
    segmentation_fields = _string_set(scorer_quality.get("segmentation_fields"))
    missing_segments = sorted(REQUIRED_SEGMENTATION_FIELDS - segmentation_fields)
    bias_probes = _string_set(scorer_quality.get("bias_probes")) | probe_types
    return [
        _check("calibration_cases_present", "pass" if _list(scorer_quality.get("calibration_cases")) else "blocker", "Scorer quality must include calibration cases.", [_repo_relative(repo_root, evals_path)]),
        _check("calibration_probe_coverage", "blocker" if missing_probes else "pass", "Calibration must include obvious, bias, rubric-copying, skill-name, and evidence-lane probes.", missing_probes),
        _check("calibration_expected_outcomes", "blocker" if outcome_gaps["missing_expected_outcome"] else "pass", "Every calibration case must declare expected_score, expected_label, or expected_direction.", outcome_gaps["missing_expected_outcome"]),
        _check("verbosity_bias_probe_present", "pass" if "short_correct_vs_verbose_wrong" in bias_probes or "verbosity_bias" in bias_probes else "blocker", "Calibration must test verbosity bias explicitly.", _calibration_case_ids(scorer_quality)),
        _check("segmentation_fields_present", "blocker" if missing_segments else "pass", "Scorer receipts must support segmented analysis by category, claim_ids, and eval_modes.", missing_segments),
    ]


def _scorer_quality_checks(repo_root: Path, evals_path: Path, evals_payload: dict[str, Any] | None, load_error: str | None) -> list[dict[str, Any]]:
    scorer_quality = _mapping(evals_payload.get("scorer_quality") if evals_payload else None)
    scorer_type = str(scorer_quality.get("scorer_type") or "")
    checks = _presence_checks(repo_root, evals_path, scorer_quality, load_error)
    checks.extend(_identity_checks(scorer_quality))
    checks.extend(_calibration_checks(repo_root, evals_path, scorer_quality))
    checks.extend(_rationale_checks(scorer_quality, scorer_type))
    checks.extend(_parameters_checks(scorer_quality, scorer_type))
    return checks


def _receipt(
    repo_root: Path,
    *,
    query: str,
    skill_md: Path,
    evals_path: Path,
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": SCORER_QUALITY_SCHEMA_VERSION,
        "schema_uri": SCORER_QUALITY_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "scorer_quality_preview",
        "query": query,
        "skill_path": _repo_relative(repo_root, skill_md),
        "evals_path": _repo_relative(repo_root, evals_path),
        "ready": not blockers,
        "quality_checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "promotion_performed": False,
        "acceptance_trace": SCORER_QUALITY_ACCEPTANCE_TRACE,
        "agent_summary": f"scorer quality preview checked scorer calibration for {query}.",
    }


def build_scorer_quality_receipt(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    skill_md = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    evals_path = skill_md.parent / "references" / "evals.yaml"
    evals_payload, load_error = _load_evals(evals_path) if evals_path.is_file() else (None, "missing_evals_yaml")
    checks = _scorer_quality_checks(repo_root, evals_path, evals_payload, load_error)
    return _receipt(repo_root, query=query, skill_md=skill_md, evals_path=evals_path, checks=checks)
