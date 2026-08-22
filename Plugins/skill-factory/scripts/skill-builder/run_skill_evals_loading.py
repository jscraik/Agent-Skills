from run_skill_evals_core import *  # noqa: F403

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


def load_evals(evals_path: Path) -> List[EvalCase]:
    obj = _load_evals_document(evals_path)
    claims = _load_claims(obj)
    baselines = _load_baselines(obj)

    cases: List[EvalCase] = []
    for i, c in enumerate(obj["cases"], 1):
        if not isinstance(c, dict):
            raise ValueError(f"Case #{i} must be a mapping.")
        for k in ("name", "prompt", "acceptance"):
            if k not in c:
                raise ValueError(f"Case #{i} missing `{k}`.")
        if not isinstance(c["acceptance"], list):
            raise ValueError(f"Case #{i} `acceptance` must be a list.")

        case_id_raw = c.get("id", f"case-{i:02d}")
        case_id = str(case_id_raw).strip() or f"case-{i:02d}"

        category = c.get("category")
        if category is not None:
            category = str(category).strip().lower()
            if category and category not in _VALID_CATEGORIES:
                raise ValueError(
                    f"Case #{i} category must be one of {sorted(_VALID_CATEGORIES)}; got {category!r}."
                )

        should_trigger = c.get("should_trigger")
        if should_trigger is not None and not isinstance(should_trigger, bool):
            raise ValueError(f"Case #{i} `should_trigger` must be boolean when provided.")

        deterministic_checks = c.get("deterministic_checks")
        if deterministic_checks is not None and not isinstance(deterministic_checks, dict):
            raise ValueError(f"Case #{i} `deterministic_checks` must be a mapping when provided.")

        expected_signals = c.get("expected_signals")
        if expected_signals is not None and not isinstance(expected_signals, dict):
            raise ValueError(f"Case #{i} `expected_signals` must be a mapping when provided.")

        budgets = c.get("budgets")
        if budgets is not None and not isinstance(budgets, dict):
            raise ValueError(f"Case #{i} `budgets` must be a mapping when provided.")

        prepend_skill = c.get("prepend_skill", True)
        if not isinstance(prepend_skill, bool):
            raise ValueError(f"Case #{i} `prepend_skill` must be boolean when provided.")

        timeout_sec = c.get("timeout_sec")
        if timeout_sec is not None:
            try:
                timeout_sec = float(timeout_sec)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Case #{i} `timeout_sec` must be numeric when provided.") from exc
            if timeout_sec <= 0:
                raise ValueError(f"Case #{i} `timeout_sec` must be > 0 when provided.")

        timeout_profile = c.get("timeout_profile")
        if timeout_profile is not None:
            timeout_profile = str(timeout_profile).strip().lower()
            if timeout_profile and timeout_profile not in _TIMEOUT_PROFILE_CHOICES:
                raise ValueError(
                    f"Case #{i} `timeout_profile` must be one of {_TIMEOUT_PROFILE_CHOICES}; "
                    f"got {timeout_profile!r}."
                )

        smoke_mode = c.get("smoke_mode")
        if smoke_mode is not None:
            smoke_mode = str(smoke_mode).strip()
            if not smoke_mode:
                smoke_mode = None
        eval_modes = _normalize_eval_modes(c.get("eval_modes"), case_number=i)

        baseline_type = c.get("baseline_type")
        if baseline_type is not None:
            baseline_type = str(baseline_type).strip().lower()
            if baseline_type and baseline_type not in _BASELINE_TYPE_CHOICES:
                raise ValueError(
                    f"Case #{i} `baseline_type` must be one of {sorted(_BASELINE_TYPE_CHOICES)}; "
                    f"got {baseline_type!r}."
                )

        comparison_inputs = c.get("comparison_inputs")
        if comparison_inputs is not None and not isinstance(comparison_inputs, dict):
            raise ValueError(f"Case #{i} `comparison_inputs` must be a mapping when provided.")

        iteration_round_state = c.get("iteration_round_state")
        if iteration_round_state is not None:
            iteration_round_state = str(iteration_round_state).strip().lower()
            if iteration_round_state and iteration_round_state not in _ROUND_STATE_CHOICES:
                raise ValueError(
                    f"Case #{i} `iteration_round_state` must be one of {sorted(_ROUND_STATE_CHOICES)}; "
                    f"got {iteration_round_state!r}."
                )

        metric_availability = c.get("metric_availability")
        if metric_availability is not None:
            metric_availability = str(metric_availability).strip().lower()
            if metric_availability and metric_availability not in _METRIC_AVAILABILITY_CHOICES:
                raise ValueError(
                    f"Case #{i} `metric_availability` must be one of {sorted(_METRIC_AVAILABILITY_CHOICES)}; "
                    f"got {metric_availability!r}."
                )

        readiness_state = c.get("readiness_state")
        if readiness_state is not None:
            readiness_state = str(readiness_state).strip().lower()
            if readiness_state and readiness_state not in _READINESS_STATE_CHOICES:
                raise ValueError(
                    f"Case #{i} `readiness_state` must be one of {sorted(_READINESS_STATE_CHOICES)}; "
                    f"got {readiness_state!r}."
                )

        comparison_review_artifact = c.get("comparison_review_artifact")
        if comparison_review_artifact is not None:
            comparison_review_artifact = str(comparison_review_artifact).strip()
            if not comparison_review_artifact:
                comparison_review_artifact = None

        neutral_baseline_approval_id = c.get("neutral_baseline_approval_id")
        if neutral_baseline_approval_id is not None:
            neutral_baseline_approval_id = str(neutral_baseline_approval_id).strip()
            if not neutral_baseline_approval_id:
                neutral_baseline_approval_id = None

        claim_ids = _normalize_string_list(c.get("claim_ids"), field_name="claim_ids", case_number=i)
        unknown_claim_ids = [claim_id for claim_id in claim_ids if claims and claim_id not in claims]
        if unknown_claim_ids:
            raise ValueError(
                f"Case #{i} references unknown claim_ids: {', '.join(unknown_claim_ids)}."
            )

        realistic = c.get("realistic")
        if realistic is not None and not isinstance(realistic, bool):
            raise ValueError(f"Case #{i} `realistic` must be boolean when provided.")

        why_realistic = c.get("why_realistic")
        if why_realistic is not None:
            why_realistic = str(why_realistic).strip()
            if not why_realistic:
                why_realistic = None

        baseline_id = c.get("baseline_id")
        if baseline_id is not None:
            baseline_id = str(baseline_id).strip()
            if not baseline_id:
                baseline_id = None
            elif baseline_id not in baselines:
                raise ValueError(f"Case #{i} references unknown baseline_id={baseline_id!r}.")

        hard_gates = _normalize_string_list(c.get("hard_gates"), field_name="hard_gates", case_number=i)
        expected_evidence = _normalize_string_list(
            c.get("expected_evidence"),
            field_name="expected_evidence",
            case_number=i,
        )
        pass_rate_threshold = _optional_float(
            c.get("pass_rate_threshold"),
            field_name="pass_rate_threshold",
            case_number=i,
        )
        if pass_rate_threshold is not None and not math.isfinite(pass_rate_threshold):
            raise ValueError(f"Case #{i} `pass_rate_threshold` must be a finite number.")

        if baseline_type == "neutral_repo_baseline" and not neutral_baseline_approval_id:
            raise ValueError(
                f"Case #{i} uses baseline_type=neutral_repo_baseline but is missing `neutral_baseline_approval_id`."
            )

        cases.append(
            EvalCase(
                id=case_id,
                name=str(c["name"]),
                prompt=str(c["prompt"]),
                acceptance=list(c["acceptance"]),
                output_schema=str(c["output_schema"]) if c.get("output_schema") else None,
                should_trigger=should_trigger,
                category=category if category else None,
                deterministic_checks=deterministic_checks,
                expected_signals=expected_signals,
                budgets=budgets,
                prepend_skill=prepend_skill,
                timeout_sec=timeout_sec,
                timeout_profile=timeout_profile if timeout_profile else None,
                smoke_mode=smoke_mode,
                eval_modes=eval_modes,
                baseline_type=baseline_type if baseline_type else None,
                comparison_inputs=dict(comparison_inputs) if isinstance(comparison_inputs, dict) else None,
                iteration_round_state=iteration_round_state if iteration_round_state else None,
                metric_availability=metric_availability if metric_availability else None,
                readiness_state=readiness_state if readiness_state else None,
                comparison_review_artifact=comparison_review_artifact,
                neutral_baseline_approval_id=neutral_baseline_approval_id,
                claim_ids=claim_ids,
                realistic=realistic,
                why_realistic=why_realistic,
                baseline_id=baseline_id,
                hard_gates=hard_gates,
                expected_evidence=expected_evidence,
                unit=_optional_case_string(c.get("unit")),
                given=_optional_case_string(c.get("given")),
                should=_optional_case_string(c.get("should")),
                actual_artifact=_optional_case_artifact_string(c.get("actual_artifact"), field_name="actual_artifact", case_number=i),
                expected_artifact=_optional_case_artifact_string(c.get("expected_artifact"), field_name="expected_artifact", case_number=i),
                reproduce=_optional_case_string(c.get("reproduce")),
                raw_response_artifact=_optional_case_artifact_string(c.get("raw_response_artifact"), field_name="raw_response_artifact", case_number=i),
                judge_detail_artifact=_optional_case_artifact_string(c.get("judge_detail_artifact"), field_name="judge_detail_artifact", case_number=i),
                pass_rate_threshold=pass_rate_threshold,
                pass_rate_calibration_artifact=_optional_case_artifact_string(c.get("pass_rate_calibration_artifact"), field_name="pass_rate_calibration_artifact", case_number=i),
            )
        )
    return cases


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


from run_skill_evals_references import (  # noqa: E402
    _render_case_references,
    attach_declared_references,
)

_load_evals_without_declared_references = load_evals


def load_evals_with_declared_references(evals_path: Path) -> List[EvalCase]:
    """Attach validated package references without changing legacy case parsing."""
    document = _load_evals_document(evals_path)
    cases = _load_evals_without_declared_references(evals_path)
    return attach_declared_references(evals_path, cases, document)


load_evals = load_evals_with_declared_references


__all__ = [name for name in globals() if not name.startswith("__")]
