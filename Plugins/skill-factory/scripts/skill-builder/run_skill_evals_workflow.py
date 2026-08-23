"""Bounded orchestration stages for the skill evaluation runner."""
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Sequence, Tuple
from run_skill_evals_discovery import (
    EXPECTED_SIGNAL_COMPOSITE_KEY, EXPECTED_SIGNAL_METRIC_KEY, EvalCase, RUNNER_BLOCKER_TAXONOMY, _acceptance_skip_reason, _baseline_comparison_from_records, _build_next_reproduce_command, _case_evidence_surfaces, _case_has_executed_check_evidence, _case_requires_no_skill_baseline, _claim_to_evidence_summary, _classify_runner_blocker, _eval_timeout_seconds, _evaluate_baseline_output, _extract_bool_budget,
    _extract_min_expected_signal_score, _extract_min_rubric_score, _extract_min_skill_lift, _extract_require_overall_pass, _filter_cases, _filter_cases_for_eval_mode, _guess_repo_root, _has_skip_git_repo_check, _is_codex_untrusted_repo_error, _is_smoke_only_case, _isolated_codex_home_for_eval, _load_evals_document, _make_relative, _no_skill_baseline_prompt,
    _parse_agent_self_assessment, _parse_csv_args, _parse_runners, _preflight_codex_live_runner, _print_case_listing, _resolve_case_timeout, _resolve_existing_optional_case_artifact_path, _resolve_optional_case_artifact_path, _resolve_path, _resolve_skill_md_path, _rewrite_dash_prefixed_codex_args, _riteway_case_report, _riteway_case_warnings, _safe_slug, _write_provisional_workflow_closeout,
    attach_declared_references, build_arg_parser, detect_skill_selected, evaluate_assertions_json, evaluate_assertions_text, evaluate_expected_signals, evaluate_trace, extract_rubric_metrics, load_evals, load_jsonl_events, load_neutral_baseline_approvals, load_skill_frontmatter, run_alt_codex_exec, run_codex_exec, run_discovery_smoke, run_openai_exec,
)
from run_skill_evals_outputs import _finalize_decision, _initialize_summary, _present_result, _write_final_outputs

class _EvalRunError(RuntimeError):
    """A user-facing evaluation configuration or execution error."""


def _fail(message: str) -> NoReturn:
    raise _EvalRunError(message)


def _parse_run_arguments(argv: Optional[Sequence[str]]) -> Dict[str, Any]:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    normalized_argv = _rewrite_dash_prefixed_codex_args(raw_argv)
    args = build_arg_parser().parse_args(normalized_argv)
    conflicts = (
        (args.dual_run and args.runners, "--dual-run cannot be combined with --runners. Choose one mode."),
        (args.smoke and args.dual_run, "--smoke cannot be combined with --dual-run."),
        (args.smoke and args.runners, "--smoke cannot be combined with --runners. Use one shortcut or the explicit runner list."),
        (args.smoke and args.runner != "codex", "--smoke cannot be combined with an explicit non-default --runner. Use one or the other."),
        (bool(args.codex_settings), "--codex-settings is deprecated because plain `codex` runner was removed. Use --codex-kimi-settings or --codex-zai-settings."),
    )
    for active, message in conflicts:
        if active:
            _fail(message)
    return {"args": args}


def _load_skill_contract(context: Dict[str, Any]) -> None:
    args = context["args"]
    skill_md = _resolve_skill_md_path(args.path)
    if not skill_md.exists():
        _fail(f"SKILL.md not found at: {skill_md}")
    skill_dir = skill_md.parent
    skill_frontmatter = load_skill_frontmatter(skill_md)
    skill_name = str(skill_frontmatter.get("name") or "").strip()
    if not skill_name:
        _fail(f"SKILL.md frontmatter missing valid `name`: {skill_md}")
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        _fail(f"Missing evals file: {evals_path}")
    context.update({
        "skill_md": skill_md, "skill_dir": skill_dir,
        "skill_frontmatter": skill_frontmatter, "skill_name": skill_name,
        "skill_contract_text": skill_md.read_text(encoding="utf-8"), "evals_path": evals_path,
    })


def _load_and_filter_cases(context: Dict[str, Any]) -> Optional[int]:
    args = context["args"]
    evals_path = context["evals_path"]
    try:
        evals_doc = _load_evals_document(evals_path)
        cases = load_evals(evals_path, reference_mode="defer")
        approvals = load_neutral_baseline_approvals(evals_path)
        case_filters = _parse_csv_args(args.case)
        category_filters = _parse_csv_args(args.category)
        cases = _filter_cases(
            cases, case_filters=case_filters, categories=category_filters,
            exact_case_ids=args.eval_mode == "release" and bool(case_filters),
        )
        cases = _filter_cases_for_eval_mode(cases, eval_mode=args.eval_mode)
        claim_summary = _claim_to_evidence_summary(
            evals_doc, cases, eval_mode=args.eval_mode, skill_dir=context["skill_dir"],
            focused_subset=bool(case_filters),
        )
    except ValueError as exc:
        _fail(str(exc))
    context.update({
        "evals_doc": evals_doc, "cases": cases, "neutral_baseline_approvals": approvals,
        "case_filters": case_filters, "category_filters": category_filters,
        "claim_to_evidence": claim_summary,
    })
    if args.list_cases:
        _print_case_listing(cases)
        return 0
    if not cases:
        _fail(f"No eval cases matched the selected filters and eval mode `{args.eval_mode}`.")
    return None


def _select_runners(args: Any) -> List[str]:
    if args.runners:
        try:
            return _parse_runners(args.runners)
        except ValueError as exc:
            _fail(str(exc))
    if args.dual_run:
        return ["codex", "codex-kimi"]
    if args.smoke:
        return ["discovery-smoke"]
    return [args.runner]


def _optional_runner_settings(args: Any, command: str, field: str, workspace_root: Path) -> Optional[Path]:
    candidate = _resolve_path(getattr(args, field), base=workspace_root)
    if command == "codex" and not candidate.exists():
        _fail(f"{field.replace('_', '-')} file not found: {candidate} (override with --{field.replace('_', '-')})")
    return candidate if candidate.exists() else None


def _optional_executable(args: Any, field: str, label: str) -> Optional[Path]:
    value = getattr(args, field)
    executable = Path(value).expanduser() if value else None
    if executable and not executable.exists():
        _fail(f"{label} not found: {executable}")
    return executable


def _workspace_root(args: Any, skill_dir: Path) -> Path:
    if args.workspace:
        return Path(args.workspace).expanduser().resolve()
    return _guess_repo_root(skill_dir)


def _configure_execution(context: Dict[str, Any]) -> None:
    args = context["args"]
    workspace_root = _workspace_root(args, context["skill_dir"])
    codex_home = Path(args.codex_home).expanduser().resolve() if args.codex_home else None
    codex_bin = _optional_executable(args, "codex_bin", "--codex-bin")
    openai_bin = _optional_executable(args, "openai_bin", "--openai-bin")
    selected_runners = _select_runners(args)
    kimi_command = str(args.codex_kimi_command or "").strip() or "codex-kimi"
    zai_command = str(args.codex_zai_command or "").strip() or "codex-zai"
    context.update({
        "workspace_root": workspace_root, "codex_home": codex_home, "codex_bin": codex_bin,
        "openai_bin": openai_bin, "selected_runners": selected_runners,
        "codex_fallback_profile": str(args.codex_fallback_profile or "").strip() or None,
        "codex_kimi_command": kimi_command, "codex_zai_command": zai_command,
        "codex_kimi_settings": _optional_runner_settings(args, kimi_command, "codex_kimi_settings", workspace_root),
        "codex_zai_settings": _optional_runner_settings(args, zai_command, "codex_zai_settings", workspace_root),
        "preflight_warnings": [],
    })


def _isolate_codex_home(context: Dict[str, Any]) -> None:
    args = context["args"]
    if "codex" not in context["selected_runners"]:
        return
    if context["codex_home"] is not None and args.profile != "oss-cloud":
        return
    try:
        codex_home, warnings = _isolated_codex_home_for_eval(args.profile, source_home=context["codex_home"])
    except ValueError as exc:
        _fail(str(exc))
    context["codex_home"] = codex_home
    context["preflight_warnings"].extend(warnings)


def _route_smoke_cases(context: Dict[str, Any]) -> None:
    cases = context["cases"]
    case_filters = context["case_filters"]
    runners = context["selected_runners"]
    smoke_only = bool(runners) and all(runner == "discovery-smoke" for runner in runners)
    has_smoke = any(case.smoke_mode for case in cases)
    if smoke_only and has_smoke:
        context["cases"] = [case for case in cases if case.smoke_mode]
    elif smoke_only:
        _fail("discovery-smoke runner requires eval cases with `smoke_mode`; none matched the selected filters. Use a live runner such as `codex` for behavior evals, or add discovery-specific smoke_mode cases.")
    elif has_smoke:
        context["cases"] = [case for case in cases if not _is_smoke_only_case(case)]
        if case_filters and not context["cases"]:
            _fail("selected case filters matched only smoke-only discovery contract cases, which live/model runners skip. Use --runner discovery-smoke for discovery contract cases or select a behavior smoke case for live/model runners.")


def _attach_selected_references(context: Dict[str, Any]) -> None:
    try:
        context["cases"] = attach_declared_references(
            context["evals_path"], context["cases"], context["evals_doc"]
        )
    except ValueError as exc:
        _fail(str(exc))


def _preflight_execution(context: Dict[str, Any]) -> None:
    args = context["args"]
    if "codex" not in context["selected_runners"]:
        return
    warnings = context["preflight_warnings"]
    workspace_root = context["workspace_root"]
    if not (workspace_root / ".git").exists() and not _has_skip_git_repo_check(args.codex_arg):
        warnings.append("Workspace does not appear to be a trusted git repository. Codex may fail with 'Not inside a trusted directory'. If this is an ephemeral directory, add --codex-arg=--skip-git-repo-check.")
    errors, auth_warnings = _preflight_codex_live_runner(
        workspace_root=workspace_root, codex_bin=context["codex_bin"], codex_home=context["codex_home"]
    )
    warnings.extend(auth_warnings)
    if errors:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        _fail("\nERROR: ".join(errors))


def _allocate_report_directory(reports_root: Path) -> Tuple[Path, str]:
    reports_root.mkdir(parents=True, exist_ok=True)
    for _ in range(8):
        run_id = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        reports_base = reports_root / run_id
        try:
            reports_base.mkdir(parents=False, exist_ok=False)
        except FileExistsError:
            continue
        return reports_base, run_id
    _fail("unable to allocate unique report directory run_id")


def _initialize_reporting(context: Dict[str, Any]) -> None:
    args = context["args"]
    cases = context["cases"]
    capture_jsonl = bool(
        args.capture_jsonl or any(case.deterministic_checks or case.budgets for case in cases)
        or (args.eval_mode == "release" and "codex" in context["selected_runners"])
    )
    if "codex" in context["selected_runners"] and args.dual_run and not capture_jsonl:
        _fail("--dual-run requires --capture-jsonl for deterministic Codex checks.")
    reports_root = Path(args.reports_dir).expanduser().resolve() / context["skill_name"]
    reports_base, run_id = _allocate_report_directory(reports_root)
    context.update({
        "capture_jsonl": capture_jsonl, "reports_base": reports_base, "run_id": run_id,
        "comparison_review_paths": [], "used_neutral_baseline_approvals": set(),
        "any_tier1_failed": False, "any_tier2_failed": False, "any_blocked": False,
        "next_reproduce_command": _build_next_reproduce_command(
            args, selected_runners=context["selected_runners"], capture_jsonl=capture_jsonl
        ),
    })


def _case_schema_path(context: Dict[str, Any], case: EvalCase) -> Optional[Path]:
    if not case.output_schema:
        return None
    schema_path = Path(case.output_schema)
    if not schema_path.is_absolute():
        schema_path = (context["skill_dir"] / schema_path).resolve()
    if not schema_path.exists():
        _fail(f"Case {case.name}: output_schema not found: {schema_path}")
    return schema_path


def _composed_case_prompt(context: Dict[str, Any], case: EvalCase) -> str:
    prompt_body = case.prompt.strip() + "\n"
    if not case.prepend_skill:
        return prompt_body
    try:
        skill_label = context["skill_md"].relative_to(context["workspace_root"])
    except ValueError:
        skill_label = context["skill_md"].name
    return (
        f"${context['skill_name']}\n\nThe local skill handle may not expand inside this isolated eval runner. "
        "Apply this SKILL.md content directly; do not try to read the skill file.\n\n"
        f"<SKILL.md path=\"{skill_label}\">\n{context['skill_contract_text']}\n</SKILL.md>\n\nTask:\n{prompt_body}"
    )


def _neutral_baseline_approval(context: Dict[str, Any], case: EvalCase) -> Optional[Dict[str, Any]]:
    if case.baseline_type != "neutral_repo_baseline":
        return None
    approval_id = case.neutral_baseline_approval_id or ""
    approval = context["neutral_baseline_approvals"].get(approval_id)
    if approval is None:
        _fail(
            f"case {case.id} references missing neutral_baseline_approval_id={approval_id!r} "
            f"in {context['evals_path']}"
        )
    return approval


def _prepare_case(context: Dict[str, Any], case: EvalCase, index: int) -> Dict[str, Any]:
    case_dir = context["reports_base"] / f"{index:02d}-{_safe_slug(case.id or case.name)}"
    case_dir.mkdir(parents=True, exist_ok=True)
    composed_prompt = _composed_case_prompt(context, case)
    (case_dir / "prompt.txt").write_text(composed_prompt, encoding="utf-8")
    _write_provisional_workflow_closeout(
        reports_base=context["reports_base"], workspace_root=context["workspace_root"],
        skill_dir=context["skill_dir"], eval_mode=context["args"].eval_mode,
        runner_mode=context["summary"]["runner_mode"], next_reproduce_command=context["next_reproduce_command"],
    )
    timeout_sec, timeout_profile = _resolve_case_timeout(
        case, cli_timeout_sec=context["args"].timeout_sec,
        cli_timeout_profile=context["args"].timeout_profile,
    )
    return {
        "case": case, "case_dir": case_dir, "schema_path": _case_schema_path(context, case),
        "composed_prompt": composed_prompt, "timeout_sec": timeout_sec, "timeout_profile": timeout_profile,
        "comparison_review_artifact": _resolve_optional_case_artifact_path(
            case_dir, case.comparison_review_artifact, context["workspace_root"]
        ),
        "neutral_baseline_approval": _neutral_baseline_approval(context, case),
        "tier1_failures": [], "tier2_findings": [],
        "warnings": _riteway_case_warnings(case, eval_mode=context["args"].eval_mode),
        "blocked_reasons": [], "notes": [], "runner_records": {},
    }


def _alt_runner_configuration(context: Dict[str, Any], runner_name: str) -> Tuple[Optional[Path], str]:
    if runner_name == "codex-kimi":
        return context["codex_kimi_settings"], context["codex_kimi_command"]
    return context["codex_zai_settings"], context["codex_zai_command"]


def _invoke_runner(
    context: Dict[str, Any], case_state: Dict[str, Any], runner_name: str,
    output_path: Path, jsonl_path: Optional[Path]
) -> Tuple[int, str, str, List[str]]:
    args = context["args"]
    common = {"workspace_root": context["workspace_root"], "prompt": case_state["composed_prompt"], "output_last_message_path": output_path, "timeout_sec": case_state["timeout_sec"], "timeout_profile": case_state["timeout_profile"]}
    if runner_name in {"codex-kimi", "codex-zai"}:
        settings, command = _alt_runner_configuration(context, runner_name)
        rc, stdout, stderr = run_alt_codex_exec(
            **common, codex_bin=context["codex_bin"], output_format=args.codex_output_format,
            settings_path=settings, cli_command=command, extra_codex_args=args.codex_arg or None,
        )
        return rc, stdout, stderr, []
    if runner_name == "openai":
        rc, stdout, stderr = run_openai_exec(
            **common, openai_bin=context["openai_bin"], output_format=args.openai_output_format,
            extra_openai_args=args.openai_arg or None,
        )
        return rc, stdout, stderr, []
    if runner_name == "discovery-smoke":
        return run_discovery_smoke(
            skill_md_path=context["skill_md"], skill_dir=context["skill_dir"],
            case=case_state["case"], output_last_message_path=output_path,
        )
    return run_codex_exec(
        **common, output_schema_path=case_state["schema_path"], sandbox=args.sandbox,
        ask_for_approval=args.ask_for_approval, model=args.model, profile=args.profile,
        codex_home=context["codex_home"], jsonl_path=jsonl_path, codex_bin=context["codex_bin"],
        extra_codex_args=args.codex_arg or None, fallback_profile=context["codex_fallback_profile"],
    )


def _write_runner_outputs(
    runner_dir: Path, output_path: Path, stdout: str, stderr: str
) -> str:
    runner_dir.mkdir(parents=True, exist_ok=True)
    (runner_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")
    (runner_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")
    output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
    (runner_dir / "final.txt").write_text(output_text, encoding="utf-8")
    return output_text


def _runner_state(
    runner_name: str, rc: int, stdout: str, stderr: str,
    output_text: str, warnings: List[str]
) -> Dict[str, Any]:
    return {
        "runner_name": runner_name, "rc": rc, "stdout": stdout, "stderr": stderr,
        "output_text": output_text, "tier1_failures": [], "tier2_findings": [],
        "warnings": list(warnings), "notes": [], "metrics": {}, "blocked": False,
        "blocker_class": None, "blocked_reasons": [], "events": None, "parsed_json": None,
    }


def _evaluate_trace_evidence(
    context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any],
    jsonl_path: Optional[Path]
) -> None:
    case = case_state["case"]
    if state["runner_name"] == "codex" and jsonl_path is not None:
        events, warnings = load_jsonl_events(jsonl_path)
        state["events"] = events
        state["warnings"].extend(warnings)
        trace = evaluate_trace(
            events, deterministic_checks=case.deterministic_checks,
            budgets=case.budgets,
        )
        state["metrics"]["trace"] = trace.to_dict()["metrics"]
        if case.deterministic_checks or case.budgets:
            state["tier1_failures"].extend(trace.hard_failures)
            if context["args"].tier2_mode != "off":
                state["tier2_findings"].extend(trace.soft_failures)
            state["warnings"].extend(trace.warnings)
    if state["runner_name"] == "codex" and (case.deterministic_checks or case.budgets) and jsonl_path is None:
        state["tier1_failures"].append(
            "deterministic_checks/budgets requested but Codex JSONL was not captured (enable --capture-jsonl)."
        )


def _evaluate_selection_evidence(
    context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any]
) -> None:
    case = case_state["case"]
    selected = detect_skill_selected(
        skill_name=context["skill_name"], output_text=state["output_text"],
        stdout_text=state["stdout"], stderr_text=state["stderr"], events=state["events"],
    )
    if state["runner_name"] == "discovery-smoke" and selected is None and case.smoke_mode:
        selected = True
    state["selected_skill"] = selected
    state["metrics"]["selected_skill"] = selected
    _record_selection_expectation(case, selected, state)


def _record_selection_expectation(
    case: EvalCase, selected: Optional[bool], state: Dict[str, Any]
) -> None:
    if case.should_trigger is not None and selected is not None and selected != case.should_trigger:
        state["tier1_failures"].append(f"should_trigger failed: expected {case.should_trigger}, detected {selected}")
    require_signal = bool((case.budgets or {}).get("require_selection_signal"))
    if case.should_trigger is True and selected is None:
        message = "should_trigger=True but selection signal unavailable (selected_skill is None). Cannot verify selection expectation without signal evidence."
        if require_signal:
            state["tier1_failures"].append(message)
        else:
            state["notes"].append(message + " Discovery-smoke or budgets.require_selection_signal=true should own hard selection proof.")
    if case.should_trigger is False and selected is None:
        state["notes"].append("should_trigger=false and selection signal unavailable; treating absence of positive selection evidence as acceptable for this negative case.")


def _evaluate_blocker_evidence(state: Dict[str, Any]) -> None:
    blocker = _classify_runner_blocker(
        output_text=state["output_text"], stdout_text=state["stdout"],
        stderr_text=state["stderr"], exit_code=state["rc"],
    )
    state["blocker_class"] = blocker
    state["blocked"] = blocker is not None
    if state["blocked"]:
        definition = RUNNER_BLOCKER_TAXONOMY.get(
            blocker or "blocked_runtime", "The eval runner was blocked before skill behavior could be judged."
        )
        state["blocked_reasons"].append(
            f"{blocker}: {definition} This is an eval runner blocker, not a skill behavior failure."
        )
    elif state["rc"] != 0:
        state["tier1_failures"].append(f"{state['runner_name']} returned non-zero exit code: {state['rc']}")
        if state["runner_name"] == "codex" and _is_codex_untrusted_repo_error(state["stderr"]):
            state["warnings"].append("Codex rejected this workspace as untrusted. Use a trusted git repo as --workspace, or pass --codex-arg=--skip-git-repo-check for ephemeral temp directories.")


def _parse_runner_json(context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any]) -> bool:
    runner_name = state["runner_name"]
    expects_json = bool(case_state["schema_path"] and runner_name == "codex")
    expects_json = expects_json or runner_name in {"codex-kimi", "codex-zai"} and context["args"].codex_output_format == "json"
    expects_json = expects_json or runner_name == "openai" and context["args"].openai_output_format == "json"
    if not expects_json:
        return False
    try:
        state["parsed_json"] = json.loads(state["output_text"])
    except (TypeError, ValueError) as exc:
        label = "schema used" if case_state["schema_path"] and runner_name == "codex" else f"{runner_name} json format"
        state["tier1_failures"].append(f"expected JSON output ({label}), but parsing failed: {exc}")
        return False
    return True


def _evaluate_acceptance(
    context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any]
) -> None:
    if state["blocked"]:
        return
    skip_reason = _acceptance_skip_reason(exit_code=state["rc"], output_text=state["output_text"])
    if skip_reason is not None:
        state["warnings"].append(skip_reason)
        return
    case = case_state["case"]
    used_json = _parse_runner_json(context, case_state, state)
    if used_json and state["parsed_json"] is not None:
        failures = evaluate_assertions_json(
            state["parsed_json"], case.acceptance,
            skill_name=context["skill_name"], selected_skill=state["selected_skill"],
        )
    else:
        failures = evaluate_assertions_text(
            state["output_text"], case.acceptance,
            skill_name=context["skill_name"], selected_skill=state["selected_skill"],
        )
    state["tier1_failures"].extend(failures)


def _evaluate_rubric(context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any]) -> None:
    if _parse_agent_self_assessment(state["output_text"]) is False and not state["blocked"]:
        state["tier1_failures"].append("Agent self-assessment reports explicit failure (e.g., 'Pass/fail: Fail'). Treating this as a hard failure regardless of exit_code.")
    rubric = extract_rubric_metrics(state["parsed_json"]) if state["parsed_json"] is not None else None
    if not rubric:
        return
    state["metrics"]["rubric"] = rubric
    case = case_state["case"]
    min_score = _extract_min_rubric_score(case.budgets)
    if context["args"].tier2_mode != "off" and min_score is not None and isinstance(rubric.get("score"), (int, float)) and float(rubric["score"]) < min_score:
        state["tier2_findings"].append(f"rubric score below budget: got {rubric['score']} < min_rubric_score {min_score}")
    require_pass = _extract_require_overall_pass(case.budgets)
    if context["args"].tier2_mode != "off" and require_pass is True and rubric.get("overall_pass") is False:
        state["tier2_findings"].append("rubric overall_pass is false but require_overall_pass budget is true")


def _evaluate_expected_signal(
    context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any]
) -> None:
    case = case_state["case"]
    if state["blocked"] or not case.expected_signals:
        return
    try:
        result = evaluate_expected_signals(state["output_text"], case.expected_signals)
    except ValueError as exc:
        state["tier1_failures"].append(str(exc))
        return
    state["metrics"][EXPECTED_SIGNAL_METRIC_KEY] = result
    minimum = _extract_min_expected_signal_score(case.budgets)
    if context["args"].tier2_mode != "off" and minimum is not None and result[EXPECTED_SIGNAL_COMPOSITE_KEY] < minimum:
        state["tier2_findings"].append(
            f"expected signal score below budget: got {result[EXPECTED_SIGNAL_COMPOSITE_KEY]} "
            f"< min_expected_signal_score {minimum:g}"
        )


def _runner_artifacts(
    context: Dict[str, Any], runner_dir: Path, jsonl_path: Optional[Path]
) -> Dict[str, Any]:
    workspace_root = context["workspace_root"]
    return {
        "dir": _make_relative(runner_dir, workspace_root),
        "final": _make_relative(runner_dir / "final.txt", workspace_root),
        "raw_response": _make_relative(runner_dir / "final.txt", workspace_root),
        "stdout": _make_relative(runner_dir / "stdout.txt", workspace_root),
        "stderr": _make_relative(runner_dir / "stderr.txt", workspace_root),
        "jsonl": _make_relative(jsonl_path, workspace_root) if jsonl_path else None,
        "judge_details": _make_relative(runner_dir / "result.json", workspace_root),
    }


def _runner_record(
    context: Dict[str, Any], case_state: Dict[str, Any], state: Dict[str, Any],
    runner_dir: Path, jsonl_path: Optional[Path]
) -> Dict[str, Any]:
    return {
        "runner": state["runner_name"], "exit_code": state["rc"],
        "passed": not state["tier1_failures"] and not state["blocked"],
        "blocked": state["blocked"], "blocker_class": state["blocker_class"],
        "blocked_reasons": state["blocked_reasons"], "tier1_failures": state["tier1_failures"],
        "tier2_findings": state["tier2_findings"], "warnings": state["warnings"],
        "notes": state["notes"], "artifacts": _runner_artifacts(context, runner_dir, jsonl_path),
        "metrics": state["metrics"],
        "used_schema": bool(case_state["schema_path"] and state["runner_name"] == "codex"),
    }


def _baseline_prompt(case: EvalCase) -> str:
    return _no_skill_baseline_prompt(case).strip() + "\n"


def _invoke_baseline(
    context: Dict[str, Any], case_state: Dict[str, Any], runner_name: str,
    output_path: Path, jsonl_path: Optional[Path]
) -> Tuple[int, str, str, List[str]]:
    args = context["args"]
    case = case_state["case"]
    common = {"workspace_root": context["workspace_root"], "prompt": _baseline_prompt(case), "output_last_message_path": output_path, "timeout_sec": case_state["timeout_sec"], "timeout_profile": case_state["timeout_profile"]}
    if runner_name in {"codex-kimi", "codex-zai"}:
        settings, command = _alt_runner_configuration(context, runner_name)
        rc, stdout, stderr = run_alt_codex_exec(
            **common, codex_bin=context["codex_bin"], output_format=args.codex_output_format,
            settings_path=settings, cli_command=command, extra_codex_args=args.codex_arg or None,
        )
        return rc, stdout, stderr, []
    if runner_name == "openai":
        rc, stdout, stderr = run_openai_exec(
            **common, openai_bin=context["openai_bin"], output_format=args.openai_output_format,
            extra_openai_args=args.openai_arg or None,
        )
        return rc, stdout, stderr, []
    if runner_name == "discovery-smoke":
        return run_discovery_smoke(
            skill_md_path=context["skill_md"], skill_dir=context["skill_dir"], case=case,
            output_last_message_path=output_path, include_skill_context=False,
        )
    return run_codex_exec(
        **common, output_schema_path=case_state["schema_path"], sandbox=args.sandbox,
        ask_for_approval=args.ask_for_approval, model=args.model, profile=args.profile,
        codex_home=context["codex_home"], jsonl_path=jsonl_path, codex_bin=context["codex_bin"],
        extra_codex_args=args.codex_arg or None, fallback_profile=context["codex_fallback_profile"],
    )


def _attach_baseline(
    context: Dict[str, Any], case_state: Dict[str, Any], runner_name: str,
    runner_dir: Path, runner_record: Dict[str, Any]
) -> None:
    case = case_state["case"]
    if not _case_requires_no_skill_baseline(case):
        return
    baseline_dir = runner_dir / "baseline-no-skill"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    output_path = baseline_dir / "output_last_message.txt"
    jsonl_path = baseline_dir / "codex_events.jsonl" if runner_name == "codex" and context["capture_jsonl"] else None
    rc, stdout, stderr, warnings = _invoke_baseline(context, case_state, runner_name, output_path, jsonl_path)
    output_text = _write_runner_outputs(baseline_dir, output_path, stdout, stderr)
    baseline = _evaluate_baseline_output(
        runner_name=runner_name, case=case, skill_name=context["skill_name"], exit_code=rc,
        stdout_text=stdout, stderr_text=stderr, output_text=output_text,
        schema_path=case_state["schema_path"], codex_output_format=context["args"].codex_output_format,
        openai_output_format=context["args"].openai_output_format,
    )
    baseline["warnings"] = list(warnings) + list(baseline.get("warnings") or [])
    baseline["artifacts"] = _runner_artifacts(context, baseline_dir, jsonl_path)
    (baseline_dir / "result.json").write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")
    runner_record["baseline"] = baseline
    runner_record["baseline_comparison"] = _baseline_comparison_from_records(
        runner_record=runner_record, baseline_record=baseline
    )


def _execute_runner(context: Dict[str, Any], case_state: Dict[str, Any], runner_name: str) -> Dict[str, Any]:
    runner_dir = case_state["case_dir"] / runner_name
    runner_dir.mkdir(parents=True, exist_ok=True)
    output_path = runner_dir / "output_last_message.txt"
    jsonl_path = runner_dir / "codex_events.jsonl" if runner_name == "codex" and context["capture_jsonl"] else None
    rc, stdout, stderr, warnings = _invoke_runner(context, case_state, runner_name, output_path, jsonl_path)
    output_text = _write_runner_outputs(runner_dir, output_path, stdout, stderr)
    state = _runner_state(runner_name, rc, stdout, stderr, output_text, warnings)
    _evaluate_trace_evidence(context, case_state, state, jsonl_path)
    _evaluate_selection_evidence(context, case_state, state)
    _evaluate_blocker_evidence(state)
    _evaluate_acceptance(context, case_state, state)
    _evaluate_rubric(context, case_state, state)
    _evaluate_expected_signal(context, case_state, state)
    record = _runner_record(context, case_state, state, runner_dir, jsonl_path)
    _attach_baseline(context, case_state, runner_name, runner_dir, record)
    (runner_dir / "result.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def _accumulate_runner_record(case_state: Dict[str, Any], runner_name: str, record: Dict[str, Any]) -> None:
    case_state["runner_records"][runner_name] = record
    groups = (
        ("tier1_failures", "tier1_failures"), ("tier2_findings", "tier2_findings"),
        ("warnings", "warnings"), ("blocked_reasons", "blocked_reasons"), ("notes", "notes"),
    )
    for target, source in groups:
        case_state[target].extend(f"[{runner_name}] {item}" for item in record[source])


def _baseline_lift(case_state: Dict[str, Any]) -> Dict[str, Any]:
    records = case_state["runner_records"]
    comparisons = {
        name: record["baseline_comparison"] for name, record in records.items()
        if isinstance(record, dict) and isinstance(record.get("baseline_comparison"), dict)
    }
    compared = [value for value in comparisons.values() if value.get("status") == "compared"]
    return {
        "baseline_comparisons": comparisons,
        "compared": compared,
        "skill_lift": max((int(value.get("skill_lift") or 0) for value in compared), default=None),
        "is_beneficial": any(bool(value.get("is_beneficial")) for value in compared),
        "baseline_regression": any(bool(value.get("regression")) for value in compared),
    }


def _apply_lift_budgets(case_state: Dict[str, Any], lift: Dict[str, Any]) -> None:
    case = case_state["case"]
    require_lift = _extract_bool_budget(case.budgets, "require_skill_lift")
    minimum = _extract_min_skill_lift(case.budgets)
    if require_lift is not True and minimum is None:
        return
    if not lift["compared"]:
        case_state["tier1_failures"].append(
            "skill lift budget requested but no executed no-skill baseline comparison was available"
        )
        return
    if require_lift is True and not lift["is_beneficial"]:
        case_state["tier1_failures"].append(
            "require_skill_lift failed: skill-enabled run did not beat the no-skill baseline"
        )
    if minimum is not None and (lift["skill_lift"] is None or lift["skill_lift"] < minimum):
        actual = lift["skill_lift"] if lift["skill_lift"] is not None else "none"
        case_state["tier1_failures"].append(f"min_skill_lift failed: got {actual} < {minimum}")


def _case_status(context: Dict[str, Any], case_state: Dict[str, Any]) -> Dict[str, Any]:
    records = case_state["runner_records"]
    blocked = any(bool(record.get("blocked")) for record in records.values())
    blocker_classes = sorted({
        str(record.get("blocker_class")) for record in records.values() if record.get("blocker_class")
    })
    tier1_failed = bool(case_state["tier1_failures"])
    tier2_failed = bool(case_state["tier2_findings"])
    passed = not tier1_failed and (context["args"].tier2_mode != "fail" or not tier2_failed)
    return {
        "blocked": blocked, "blocker_classes": blocker_classes,
        "tier1_failed": tier1_failed, "tier2_failed": tier2_failed,
        "passed": passed and not blocked,
    }


def _case_evidence_record(
    context: Dict[str, Any], case_state: Dict[str, Any], lift: Dict[str, Any], status: Dict[str, Any]
) -> Dict[str, Any]:
    case = case_state["case"]
    case_dir = case_state["case_dir"]
    workspace_root = context["workspace_root"]
    pass_rate = None
    if case.pass_rate_threshold is not None:
        calibration = _resolve_optional_case_artifact_path(case_dir, case.pass_rate_calibration_artifact, workspace_root)
        pass_rate = {"threshold": case.pass_rate_threshold, "calibration_artifact": calibration, "gate_status": "calibrated_gate" if _resolve_existing_optional_case_artifact_path(case_dir, case.pass_rate_calibration_artifact, workspace_root) else "advisory"}
    return {
        "id": case.id, "name": case.name, "category": case.category,
        "eval_modes": list(case.eval_modes) if case.eval_modes else None,
        "should_trigger": case.should_trigger, "prepend_skill": case.prepend_skill,
        "baseline_type": case.baseline_type, "baseline_id": case.baseline_id,
        "claim_ids": list(case.claim_ids), "realistic": case.realistic, "why_realistic": case.why_realistic,
        "hard_gates": list(case.hard_gates), "expected_evidence": list(case.expected_evidence),
        "riteway": _riteway_case_report(case, case_dir=case_dir, workspace_root=workspace_root, runner_records=case_state["runner_records"]),
        "pass_rate_policy": pass_rate, "agent_eval_artifacts": {"raw_response": _resolve_optional_case_artifact_path(case_dir, case.raw_response_artifact, workspace_root), "judge_details": _resolve_optional_case_artifact_path(case_dir, case.judge_detail_artifact, workspace_root)},
        "evidence_surfaces": _case_evidence_surfaces(case), "check_evidence": _case_has_executed_check_evidence(case, case_state["runner_records"]),
        "comparison_inputs": dict(case.comparison_inputs) if case.comparison_inputs else None,
        "iteration_round_state": case.iteration_round_state, "metric_availability": case.metric_availability,
        "readiness_state": case.readiness_state, "comparison_review_artifact": case_state["comparison_review_artifact"],
        "neutral_baseline_approval": case_state["neutral_baseline_approval"],
        "baseline_comparisons": lift["baseline_comparisons"], "skill_lift": lift["skill_lift"],
        "is_beneficial": lift["is_beneficial"], "baseline_regression": lift["baseline_regression"],
        "expected_signals": bool(case.expected_signals), "timeout_profile": case_state["timeout_profile"],
        "timeout_sec": _eval_timeout_seconds(timeout_sec=case_state["timeout_sec"], timeout_profile=case_state["timeout_profile"]),
        "dir": _make_relative(case_dir, workspace_root), "runners": case_state["runner_records"],
        "passed": status["passed"], "blocked": status["blocked"], "blocker_classes": status["blocker_classes"],
        "blocked_reasons": case_state["blocked_reasons"], "tier1_failed": status["tier1_failed"],
        "tier2_failed": status["tier2_failed"], "tier1_failures": case_state["tier1_failures"],
        "tier2_findings": case_state["tier2_findings"], "warnings": case_state["warnings"], "notes": case_state["notes"],
    }


def _update_state_counter(summary: Dict[str, Any], group: str, value: Optional[str]) -> None:
    key = value or "unknown"
    summary[group][key] = summary[group].get(key, 0) + 1


def _update_summary_for_case(
    context: Dict[str, Any], case_state: Dict[str, Any], record: Dict[str, Any]
) -> None:
    case = case_state["case"]
    summary = context["summary"]
    summary["cases"].append(record)
    _update_state_counter(summary, "readiness_summary", case.readiness_state)
    _update_state_counter(summary, "round_state_summary", case.iteration_round_state)
    if case_state["comparison_review_artifact"]:
        context["comparison_review_paths"].append(case_state["comparison_review_artifact"])
    if case.neutral_baseline_approval_id:
        context["used_neutral_baseline_approvals"].add(case.neutral_baseline_approval_id)
    for flag, count_key in (("tier1_failed", "tier1_failures"), ("tier2_failed", "tier2_findings"), ("blocked", "blocked_cases")):
        if record[flag]:
            context[f"any_{flag}"] = True
            summary[count_key] += 1
    for blocker in record["blocker_classes"] if record["blocked"] else ():
        summary["blocked_class_summary"][blocker] = summary["blocked_class_summary"].get(blocker, 0) + 1


def _execute_case(context: Dict[str, Any], case: EvalCase, index: int) -> None:
    case_state = _prepare_case(context, case, index)
    for runner_name in context["selected_runners"]:
        record = _execute_runner(context, case_state, runner_name)
        _accumulate_runner_record(case_state, runner_name, record)
    lift = _baseline_lift(case_state)
    _apply_lift_budgets(case_state, lift)
    status = _case_status(context, case_state)
    record = _case_evidence_record(context, case_state, lift, status)
    (case_state["case_dir"] / "result.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _update_summary_for_case(context, case_state, record)


def _execute_cases(context: Dict[str, Any]) -> None:
    for index, case in enumerate(context["cases"], 1):
        _execute_case(context, case, index)


def execute_eval_workflow(argv: Optional[Sequence[str]] = None) -> int:
    try:
        context = _parse_run_arguments(argv)
        _load_skill_contract(context)
        early_exit = _load_and_filter_cases(context)
        if early_exit is not None:
            return early_exit
        _configure_execution(context)
        _isolate_codex_home(context)
        _route_smoke_cases(context)
        _attach_selected_references(context)
        _preflight_execution(context)
        _initialize_reporting(context)
        _initialize_summary(context)
        _execute_cases(context)
        _finalize_decision(context)
        _write_final_outputs(context)
        _present_result(context)
        return int(context["summary"]["exit_code"])
    except _EvalRunError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


__all__ = [name for name in globals() if not name.startswith("__")]
