from typing import Literal

from run_skill_evals_core import *  # noqa: F403
from run_skill_evals_references import (
    _render_case_references as _render_case_references_impl,
    attach_declared_references,
)


def _render_case_references(skill_dir: Path, reference_paths: Sequence[str]) -> str:
    """Expose reference rendering through the compatibility facade."""
    return _render_case_references_impl(skill_dir, reference_paths)


def _evaluate_baseline_output(
    *,
    runner_name: str,
    case: EvalCase,
    skill_name: str,
    exit_code: int,
    stdout_text: str,
    stderr_text: str,
    output_text: str,
    schema_path: Optional[Path],
    codex_output_format: str,
    openai_output_format: str,
) -> Dict[str, Any]:
    failures: List[str] = []
    findings: List[str] = []
    warnings: List[str] = []
    metrics: Dict[str, Any] = {}

    blocker_class = _classify_runner_blocker(
        output_text=output_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        exit_code=exit_code,
    )
    blocked = blocker_class is not None
    if blocked:
        failures.append(f"{blocker_class}: no-skill baseline runner was blocked before comparison.")
    elif exit_code != 0:
        failures.append(f"{runner_name} no-skill baseline returned non-zero exit code: {exit_code}")

    selected_skill = detect_skill_selected(
        skill_name=skill_name,
        output_text=output_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        events=None,
    )
    metrics["selected_skill"] = selected_skill

    parsed_json: Optional[Any] = None
    used_json_assertions = False
    acceptance_skip_reason = _acceptance_skip_reason(exit_code=exit_code, output_text=output_text)
    if blocked:
        pass
    elif acceptance_skip_reason is not None:
        warnings.append(acceptance_skip_reason)
    else:
        expects_json = (
            (schema_path is not None and runner_name == "codex")
            or (runner_name in {"codex-kimi", "codex-zai"} and codex_output_format == "json")
            or (runner_name == "openai" and openai_output_format == "json")
        )
        if expects_json:
            try:
                parsed_json = json.loads(output_text)
            except Exception as e:  # noqa: BLE001
                failures.append(f"expected JSON output from no-skill baseline, but parsing failed: {e}")
            else:
                used_json_assertions = True

        if used_json_assertions and parsed_json is not None:
            failures.extend(
                evaluate_assertions_json(
                    parsed_json,
                    case.acceptance,
                    skill_name=skill_name,
                    selected_skill=selected_skill,
                )
            )
        else:
            failures.extend(
                evaluate_assertions_text(
                    output_text,
                    case.acceptance,
                    skill_name=skill_name,
                    selected_skill=selected_skill,
                )
            )

    rubric = extract_rubric_metrics(parsed_json) if parsed_json is not None else None
    if rubric:
        metrics["rubric"] = rubric

    if not blocked and case.expected_signals:
        try:
            expected_signal_result = evaluate_expected_signals(output_text, case.expected_signals)
        except ValueError as exc:
            failures.append(str(exc))
            expected_signal_result = None
        if expected_signal_result is not None:
            metrics[EXPECTED_SIGNAL_METRIC_KEY] = expected_signal_result
            min_expected_score = _extract_min_expected_signal_score(case.budgets)
            if (
                min_expected_score is not None
                and expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY] < min_expected_score
            ):
                findings.append(
                    "expected signal score below budget: "
                    f"got {expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY]} < "
                    f"min_expected_signal_score {min_expected_score:g}"
                )

    return {
        "baseline_type": "no_skill",
        "status": "executed",
        "runner": runner_name,
        "exit_code": exit_code,
        "passed": (len(failures) == 0) and not blocked,
        "blocked": blocked,
        "blocker_class": blocker_class,
        "tier1_failures": failures,
        "tier2_findings": findings,
        "warnings": warnings,
        "metrics": metrics,
        "used_schema": bool(schema_path and runner_name == "codex"),
    }


def _hard_gate_gaps_for_case(case: EvalCase, *, eval_mode: str) -> List[Dict[str, Any]]:
    if eval_mode != "release" or not case.hard_gates:
        return []
    gaps: List[Dict[str, Any]] = []
    for gate in case.hard_gates:
        if gate not in _KNOWN_HARD_GATES:
            gaps.append({
                "type": "unknown_hard_gate",
                "case_id": case.id,
                "hard_gate": gate,
                "severity": "blocking",
                "message": f"release case references unknown hard_gate={gate!r}",
            })
            continue
        if not _case_has_check_surface(case):
            gaps.append({
                "type": "hard_gate_without_required_evidence",
                "case_id": case.id,
                "hard_gate": gate,
                "severity": "blocking",
                "message": (
                    f"hard_gate={gate!r} requires deterministic_checks, expected_signals, "
                    "or output_schema evidence in release mode"
                ),
            })
        elif not _case_evidence_surfaces(case):
            gaps.append({
                "type": "hard_gate_without_evidence_surface",
                "case_id": case.id,
                "hard_gate": gate,
                "severity": "blocking",
                "message": "hard-gated release case must declare a concrete evidence surface",
            })
    return gaps


def load_neutral_baseline_approvals(evals_path: Path) -> Dict[str, Dict[str, Any]]:
    obj = _load_evals_document(evals_path)
    raw = obj.get("neutral_baseline_approvals")
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise ValueError("`neutral_baseline_approvals` must be a list when provided.")

    approvals: Dict[str, Dict[str, Any]] = {}
    for i, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError(f"neutral_baseline_approvals entry #{i} must be a mapping.")
        approval_id = str(item.get("id") or "").strip()
        if not approval_id:
            raise ValueError(f"neutral_baseline_approvals entry #{i} missing non-empty `id`.")
        if approval_id in approvals:
            raise ValueError(f"duplicate neutral_baseline_approval id in evals.yaml: {approval_id}")
        approvals[approval_id] = dict(item)
    return approvals


def _case_shape(raw_case: Any, case_number: int) -> Dict[str, Any]:
    if not isinstance(raw_case, dict):
        raise ValueError(f"Case #{case_number} must be a mapping.")
    for field in ("name", "prompt", "acceptance"):
        if field not in raw_case:
            raise ValueError(f"Case #{case_number} missing `{field}`.")
    if not isinstance(raw_case["acceptance"], list):
        raise ValueError(f"Case #{case_number} `acceptance` must be a list.")
    return raw_case


def _optional_mapping(raw_case: Dict[str, Any], field: str, case_number: int) -> Optional[Dict[str, Any]]:
    value = raw_case.get(field)
    if value is not None and not isinstance(value, dict):
        raise ValueError(f"Case #{case_number} `{field}` must be a mapping when provided.")
    return value


def _optional_bool(raw_case: Dict[str, Any], field: str, case_number: int) -> Optional[bool]:
    value = raw_case.get(field)
    if value is not None and not isinstance(value, bool):
        raise ValueError(f"Case #{case_number} `{field}` must be boolean when provided.")
    return value


def _optional_choice(
    raw_case: Dict[str, Any], field: str, choices: Sequence[str], case_number: int
) -> Optional[str]:
    value = raw_case.get(field)
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized and normalized not in choices:
        raise ValueError(f"Case #{case_number} `{field}` must be one of {sorted(choices)}; got {normalized!r}.")
    return normalized or None


def _optional_text(raw_case: Dict[str, Any], field: str) -> Optional[str]:
    value = raw_case.get(field)
    if value is None:
        return None
    return str(value).strip() or None


def _case_identity_fields(raw_case: Dict[str, Any], case_number: int) -> Dict[str, Any]:
    default_id = f"case-{case_number:02d}"
    case_id = str(raw_case.get("id", default_id)).strip() or default_id
    category = _optional_choice(raw_case, "category", _VALID_CATEGORIES, case_number)
    prepend_skill = raw_case.get("prepend_skill", True)
    if not isinstance(prepend_skill, bool):
        raise ValueError(f"Case #{case_number} `prepend_skill` must be boolean when provided.")
    return {
        "id": case_id, "name": str(raw_case["name"]), "prompt": str(raw_case["prompt"]),
        "acceptance": list(raw_case["acceptance"]), "category": category,
        "should_trigger": _optional_bool(raw_case, "should_trigger", case_number),
        "prepend_skill": prepend_skill,
        "output_schema": str(raw_case["output_schema"]) if raw_case.get("output_schema") else None,
    }


def _case_timeout_fields(raw_case: Dict[str, Any], case_number: int) -> Dict[str, Any]:
    timeout_sec = raw_case.get("timeout_sec")
    if timeout_sec is not None:
        try:
            timeout_sec = float(timeout_sec)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Case #{case_number} `timeout_sec` must be numeric when provided.") from exc
        if timeout_sec <= 0:
            raise ValueError(f"Case #{case_number} `timeout_sec` must be > 0 when provided.")
    timeout_profile = _optional_choice(raw_case, "timeout_profile", _TIMEOUT_PROFILE_CHOICES, case_number)
    return {
        "timeout_sec": timeout_sec,
        "timeout_profile": timeout_profile,
        "smoke_mode": _optional_text(raw_case, "smoke_mode"),
        "eval_modes": _normalize_eval_modes(raw_case.get("eval_modes"), case_number=case_number),
    }


def _case_contract_fields(raw_case: Dict[str, Any], case_number: int) -> Dict[str, Any]:
    return {
        "deterministic_checks": _optional_mapping(raw_case, "deterministic_checks", case_number),
        "expected_signals": _optional_mapping(raw_case, "expected_signals", case_number),
        "budgets": _optional_mapping(raw_case, "budgets", case_number),
        "comparison_inputs": _optional_mapping(raw_case, "comparison_inputs", case_number),
        "iteration_round_state": _optional_choice(raw_case, "iteration_round_state", _ROUND_STATE_CHOICES, case_number),
        "metric_availability": _optional_choice(raw_case, "metric_availability", _METRIC_AVAILABILITY_CHOICES, case_number),
        "readiness_state": _optional_choice(raw_case, "readiness_state", _READINESS_STATE_CHOICES, case_number),
        "comparison_review_artifact": _optional_text(raw_case, "comparison_review_artifact"),
    }


def _case_claim_fields(
    raw_case: Dict[str, Any], case_number: int, claims: Dict[str, Any]
) -> Dict[str, Any]:
    claim_ids = _normalize_string_list(raw_case.get("claim_ids"), field_name="claim_ids", case_number=case_number)
    unknown = [claim_id for claim_id in claim_ids if claims and claim_id not in claims]
    if unknown:
        raise ValueError(f"Case #{case_number} references unknown claim_ids: {', '.join(unknown)}.")
    return {
        "claim_ids": claim_ids,
        "realistic": _optional_bool(raw_case, "realistic", case_number),
        "why_realistic": _optional_text(raw_case, "why_realistic"),
        "hard_gates": _normalize_string_list(raw_case.get("hard_gates"), field_name="hard_gates", case_number=case_number),
        "expected_evidence": _normalize_string_list(raw_case.get("expected_evidence"), field_name="expected_evidence", case_number=case_number),
    }


def _case_baseline_fields(
    raw_case: Dict[str, Any], case_number: int, baselines: Dict[str, Any]
) -> Dict[str, Any]:
    baseline_type = _optional_choice(raw_case, "baseline_type", _BASELINE_TYPE_CHOICES, case_number)
    approval_id = _optional_text(raw_case, "neutral_baseline_approval_id")
    baseline_id = _optional_text(raw_case, "baseline_id")
    if baseline_id is not None and baseline_id not in baselines:
        raise ValueError(f"Case #{case_number} references unknown baseline_id={baseline_id!r}.")
    if baseline_type == "neutral_repo_baseline" and not approval_id:
        raise ValueError(
            f"Case #{case_number} uses baseline_type=neutral_repo_baseline but is missing `neutral_baseline_approval_id`."
        )
    return {
        "baseline_type": baseline_type,
        "baseline_id": baseline_id,
        "neutral_baseline_approval_id": approval_id,
    }


def _case_artifact_fields(raw_case: Dict[str, Any], case_number: int) -> Dict[str, Any]:
    fields = ("actual_artifact", "expected_artifact", "raw_response_artifact", "judge_detail_artifact")
    result = {
        field: _optional_case_artifact_string(raw_case.get(field), field_name=field, case_number=case_number)
        for field in fields
    }
    result.update({
        "unit": _optional_case_string(raw_case.get("unit")),
        "given": _optional_case_string(raw_case.get("given")),
        "should": _optional_case_string(raw_case.get("should")),
        "reproduce": _optional_case_string(raw_case.get("reproduce")),
        "pass_rate_calibration_artifact": _optional_case_artifact_string(
            raw_case.get("pass_rate_calibration_artifact"),
            field_name="pass_rate_calibration_artifact", case_number=case_number,
        ),
    })
    return result


def _build_eval_case(
    raw_case: Any, case_number: int, claims: Dict[str, Any], baselines: Dict[str, Any]
) -> EvalCase:
    case = _case_shape(raw_case, case_number)
    fields: Dict[str, Any] = {}
    for values in (
        _case_identity_fields(case, case_number),
        _case_timeout_fields(case, case_number),
        _case_contract_fields(case, case_number),
        _case_claim_fields(case, case_number, claims),
        _case_baseline_fields(case, case_number, baselines),
        _case_artifact_fields(case, case_number),
    ):
        fields.update(values)
    threshold = _optional_float(case.get("pass_rate_threshold"), field_name="pass_rate_threshold", case_number=case_number)
    if threshold is not None and not math.isfinite(threshold):
        raise ValueError(f"Case #{case_number} `pass_rate_threshold` must be a finite number.")
    fields["pass_rate_threshold"] = threshold
    return EvalCase(**fields)


def load_evals(
    evals_path: Path,
    *,
    reference_mode: Literal["attach", "defer"] = "attach",
) -> List[EvalCase]:
    obj = _load_evals_document(evals_path)
    claims = _load_claims(obj)
    baselines = _load_baselines(obj)
    cases = [
        _build_eval_case(raw_case, case_number, claims, baselines)
        for case_number, raw_case in enumerate(obj["cases"], 1)
    ]
    if reference_mode == "defer":
        return cases
    return attach_declared_references(evals_path, cases, obj)


def _case_matches_eval_mode(case: EvalCase, *, eval_mode: str) -> bool:
    if eval_mode == "standard":
        return True
    if case.eval_modes:
        return eval_mode in case.eval_modes
    if eval_mode == "release":
        return True
    if case.category in {"negative", "pressure"}:
        return False
    if case.deterministic_checks or case.budgets:
        return False
    return True


def _filter_cases_for_eval_mode(cases: Sequence[EvalCase], *, eval_mode: str) -> List[EvalCase]:
    return [case for case in cases if _case_matches_eval_mode(case, eval_mode=eval_mode)]


def _reporting_metadata(obj: Dict[str, Any]) -> Dict[str, Any]:
    raw = obj.get("reporting")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("`reporting` must be a mapping when provided.")
    reporting = dict(raw)
    preferred_source_format = reporting.get("preferred_source_format")
    if preferred_source_format is not None:
        if not isinstance(preferred_source_format, str):
            raise ValueError("`reporting.preferred_source_format` must be a string when provided.")
        normalized = preferred_source_format.strip().lower()
        if normalized and normalized not in {"mdx", "markdown", "json"}:
            raise ValueError("`reporting.preferred_source_format` must be one of: mdx, markdown, json.")
        reporting["preferred_source_format"] = normalized
    for path_field in ("report_template", "component_bundle"):
        raw_path = reporting.get(path_field)
        if raw_path is not None and not isinstance(raw_path, str):
            raise ValueError(f"`reporting.{path_field}` must be a string when provided.")
        if isinstance(raw_path, str) and raw_path.strip():
            report_path = Path(raw_path)
            if report_path.is_absolute():
                raise ValueError(f"`reporting.{path_field}` must be a repo-relative path.")
            if ".." in report_path.parts:
                raise ValueError(f"`reporting.{path_field}` must not contain path traversal.")
    return reporting


def _reporting_artifact_exists(relative_path: str, *, search_roots: Sequence[Path]) -> bool:
    for root in search_roots:
        root_resolved = root.resolve()
        candidate = root / relative_path
        if not candidate.is_file():
            continue
        try:
            candidate_resolved = candidate.resolve()
            candidate_resolved.relative_to(root_resolved)
        except (OSError, ValueError):
            continue
        return True
    return False


def _claim_to_evidence_summary(
    evals_doc: Dict[str, Any],
    cases: Sequence[EvalCase],
    *,
    eval_mode: str,
    skill_dir: Path,
    focused_subset: bool = False,
) -> Dict[str, Any]:
    claims = _load_claims(evals_doc)
    baselines = _load_baselines(evals_doc)
    reporting = _reporting_metadata(evals_doc)
    claim_records: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []

    if eval_mode == "release" and cases and not claims:
        gaps.append({
            "type": "missing_claim_registry",
            "severity": "blocking",
            "message": "release evals must define top-level claims before claim evidence can pass",
        })

    for claim_id, claim in sorted(claims.items()):
        covering = [case for case in cases if claim_id in case.claim_ids]
        hard_gate = bool(claim.get("hard_gate"))
        risk = str(claim.get("risk") or "medium").strip().lower()
        blocking = (
            eval_mode == "release"
            and not focused_subset
            and hard_gate
            and risk in {"critical", "high"}
        )
        evidence_required = _normalize_string_list(
            claim.get("evidence_required"),
            field_name=f"claims[{claim_id}].evidence_required",
        )
        evidence_surfaces = sorted({surface for case in covering for surface in _case_evidence_surfaces(case)})

        record = {
            "id": claim_id,
            "claim_type": claim.get("claim_type"),
            "risk": risk,
            "hard_gate": hard_gate,
            "source": claim.get("source"),
            "evidence_required": list(evidence_required),
            "evidence_surfaces": evidence_surfaces,
            "cases": [case.id for case in covering],
        }
        claim_records.append(record)

        if not covering:
            gaps.append({
                "type": "claim_without_case",
                "claim_id": claim_id,
                "severity": "blocking" if blocking else "advisory",
                "message": "claim has no eval case linked through claim_ids",
            })
            continue

        if blocking and not any(case.acceptance for case in covering):
            gaps.append({
                "type": "claim_without_acceptance",
                "claim_id": claim_id,
                "severity": "blocking",
                "message": "high-risk hard-gate claim lacks acceptance checks",
            })
        if blocking and not evidence_surfaces:
            gaps.append({
                "type": "claim_without_evidence_surface",
                "claim_id": claim_id,
                "severity": "blocking",
                "message": "high-risk hard-gate claim lacks deterministic, signal, schema, hard-gate, or expected-evidence coverage",
            })
        if blocking and evidence_required and not evidence_surfaces:
            gaps.append({
                "type": "claim_evidence_required_unmapped",
                "claim_id": claim_id,
                "severity": "blocking",
                "message": "claim declares evidence_required but no covering case declares an evidence surface",
            })

    for case in cases:
        if claims and not case.claim_ids:
            gaps.append({
                "type": "case_without_claim",
                "case_id": case.id,
                "severity": "advisory",
                "message": "case is not linked to a claim_id",
            })
        if eval_mode == "release" and case.claim_ids:
            if case.realistic is not True:
                gaps.append({
                    "type": "missing_realism_evidence",
                    "case_id": case.id,
                    "severity": "blocking",
                    "message": "release claim-linked case must set realistic: true",
                })
            if not case.why_realistic:
                gaps.append({
                    "type": "missing_realism_rationale",
                    "case_id": case.id,
                    "severity": "blocking",
                    "message": "release claim-linked case must explain why_realistic",
                })
        if case.baseline_id and case.baseline_id not in baselines:
            gaps.append({
                "type": "unknown_baseline",
                "case_id": case.id,
                "severity": "blocking",
                "message": f"case references unknown baseline_id={case.baseline_id!r}",
            })
        if _case_uses_smoke_or_release(case, eval_mode=eval_mode):
            missing_shape = _riteway_shape_missing_fields(case)
            if missing_shape:
                gaps.append({
                    "type": "missing_riteway_shape",
                    "case_id": case.id,
                    "severity": "advisory",
                    "missing_fields": missing_shape,
                    "realistic": case.realistic,
                    "message": (
                        "smoke/release eval should declare unit, given, should, actual_artifact, "
                        "expected_artifact, and reproduce"
                    ),
                })
        weak_reasons = _weak_acceptance_reasons(case)
        if weak_reasons:
            gaps.append({
                "type": "weak_acceptance_shape",
                "case_id": case.id,
                "severity": "advisory",
                "reasons": weak_reasons,
                "message": "migration pass found acceptance that only checks trigger words or generic phrases",
            })
        if case.pass_rate_threshold is not None and not case.pass_rate_calibration_artifact:
            gaps.append({
                "type": "uncalibrated_pass_rate_threshold",
                "case_id": case.id,
                "severity": "advisory",
                "message": "pass-rate threshold is advisory until calibrated against labeled examples",
            })
        gaps.extend(_hard_gate_gaps_for_case(case, eval_mode=eval_mode))

    report_template = str(reporting.get("report_template") or "").strip()
    report_template_exists: Optional[bool] = None
    component_bundle = str(reporting.get("component_bundle") or "").strip()
    component_bundle_exists: Optional[bool] = None
    preferred_source_format = str(reporting.get("preferred_source_format") or "").strip().lower()
    search_roots = [WORKSPACE_ROOT, REPO_ROOT, skill_dir, SCRIPT_DIR]
    if eval_mode == "release" and preferred_source_format == "mdx" and not report_template:
        gaps.append({
            "type": "missing_report_template",
            "severity": "blocking",
            "message": "release MDX reporting must declare report_template",
        })
    if preferred_source_format == "mdx" and report_template and Path(report_template).suffix != ".mdx":
        gaps.append({
            "type": "invalid_report_template_type",
            "severity": "blocking" if eval_mode == "release" else "advisory",
            "message": f"MDX report_template must point to a .mdx file: {report_template}",
        })
    if preferred_source_format == "mdx" and component_bundle and Path(component_bundle).suffix not in {".tsx", ".jsx"}:
        gaps.append({
            "type": "invalid_report_component_bundle_type",
            "severity": "blocking" if eval_mode == "release" else "advisory",
            "message": f"MDX component_bundle must point to a .tsx or .jsx file: {component_bundle}",
        })
    if report_template:
        report_template_exists = _reporting_artifact_exists(report_template, search_roots=search_roots)
        if report_template_exists is False:
            gaps.append({
                "type": "missing_report_template",
                "severity": "blocking" if eval_mode == "release" else "advisory",
                "message": f"report_template does not exist: {report_template}",
            })
    if component_bundle:
        component_bundle_exists = _reporting_artifact_exists(component_bundle, search_roots=search_roots)
        if component_bundle_exists is False:
            gaps.append({
                "type": "missing_report_component_bundle",
                "severity": "blocking" if eval_mode == "release" else "advisory",
                "message": f"component_bundle does not exist: {component_bundle}",
            })
    elif eval_mode == "release" and preferred_source_format == "mdx":
        gaps.append({
            "type": "missing_report_component_bundle",
            "severity": "blocking",
            "message": "release MDX reporting must declare component_bundle",
        })

    blocking_gaps = [gap for gap in gaps if gap.get("severity") == "blocking"]
    return {
        "schema_version": "claim-to-evidence.v1",
        "claims": claim_records,
        "baselines": sorted(baselines),
        "reporting": reporting,
        "report_template_exists": report_template_exists,
        "component_bundle_exists": component_bundle_exists,
        "gaps": gaps,
        "blocking_gaps": blocking_gaps,
        "passed": not blocking_gaps,
    }


def _attach_claim_execution_results(
    claim_summary: Dict[str, Any],
    case_results: Sequence[Dict[str, Any]],
    *,
    eval_mode: str,
    focused_subset: bool = False,
) -> None:
    cases_by_id = {str(case.get("id")): case for case in case_results}
    gaps = list(claim_summary.get("gaps") or [])
    existing_gap_keys = {
        (gap.get("type"), gap.get("claim_id"), gap.get("case_id"))
        for gap in gaps
        if isinstance(gap, dict)
    }
    for claim in claim_summary.get("claims", []):
        if not isinstance(claim, dict):
            continue
        claim_id = str(claim.get("id") or "")
        linked_results: List[Dict[str, Any]] = []
        for case_id in claim.get("cases") or []:
            case = cases_by_id.get(str(case_id))
            if not case:
                continue
            runner_artifacts = []
            for runner in (case.get("runners") or {}).values():
                if isinstance(runner, dict):
                    artifacts = runner.get("artifacts")
                    if isinstance(artifacts, dict) and any(value for value in artifacts.values()):
                        runner_artifacts.append({
                            "runner": runner.get("runner"),
                            "artifacts": artifacts,
                        })
            linked_results.append({
                "case_id": case.get("id"),
                "passed": bool(case.get("passed")),
                "blocked": bool(case.get("blocked")),
                "tier1_failed": bool(case.get("tier1_failed")),
                "tier2_failed": bool(case.get("tier2_failed")),
                "evidence_surfaces": case.get("evidence_surfaces") or [],
                "check_evidence": bool(case.get("check_evidence")),
                "runner_artifacts": runner_artifacts,
            })
        claim["case_results"] = linked_results
        if (
            eval_mode == "release"
            and not focused_subset
            and claim.get("hard_gate")
            and str(claim.get("risk") or "").lower() in {"critical", "high"}
            and not any(
                result.get("passed")
                and result.get("runner_artifacts")
                and result.get("check_evidence")
                for result in linked_results
            )
        ):
            key = ("claim_without_passing_case", claim_id, None)
            if key not in existing_gap_keys:
                gaps.append({
                    "type": "claim_without_passing_case",
                    "claim_id": claim_id,
                    "severity": "blocking",
                    "message": "high-risk hard-gate claim has no passing case with runner artifacts",
                })
                existing_gap_keys.add(key)
    blocking_gaps = [gap for gap in gaps if isinstance(gap, dict) and gap.get("severity") == "blocking"]
    claim_summary["gaps"] = gaps
    claim_summary["blocking_gaps"] = blocking_gaps
    claim_summary["passed"] = not blocking_gaps


def _eval_contract_migration_summary(cases: Sequence[EvalCase], *, eval_mode: str) -> Dict[str, Any]:
    missing_shape: List[Dict[str, Any]] = []
    weak_acceptance: List[Dict[str, Any]] = []
    uncalibrated_thresholds: List[Dict[str, Any]] = []
    for case in cases:
        missing = _riteway_shape_missing_fields(case)
        if _case_uses_smoke_or_release(case, eval_mode=eval_mode) and missing:
            missing_shape.append({
                "case_id": case.id,
                "missing_fields": missing,
                "realistic": case.realistic,
            })
        weak_reasons = _weak_acceptance_reasons(case)
        if weak_reasons:
            weak_acceptance.append({
                "case_id": case.id,
                "reasons": weak_reasons,
            })
        if case.pass_rate_threshold is not None and not case.pass_rate_calibration_artifact:
            uncalibrated_thresholds.append({
                "case_id": case.id,
                "pass_rate_threshold": case.pass_rate_threshold,
                "policy": "advisory_until_calibrated",
            })
    return {
        "schema_version": "eval-contract-migration.v1",
        "riteway_shape_missing_cases": missing_shape,
        "weak_acceptance_cases": weak_acceptance,
        "uncalibrated_pass_rate_thresholds": uncalibrated_thresholds,
    }


__all__ = [name for name in globals() if not name.startswith("__")]
