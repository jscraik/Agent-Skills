from run_skill_evals_discovery import *  # noqa: F403

def main(argv: Optional[Sequence[str]]=None) -> int:
    """
    Run the full skill evaluation workflow from parsed CLI arguments, execute selected runners against eval cases, and write evaluation reports.

    This function parses and validates CLI arguments (or the provided argv list), loads the skill and eval cases, selects and runs configured runners for each case (including deterministic trace evaluation when enabled), aggregates per-runner and per-case results, emits artifacts (reports, scorecard, junit, release manifest), and determines an overall pass/fail decision.

    Parameters:
        argv (Optional[Sequence[str]]): Optional list of CLI arguments to parse instead of sys.argv[1:].

    Returns:
        int: Exit code: `0` when required gates pass; `1` for configuration/IO/preflight errors; `2` when evaluation gates fail.
    """
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    normalized_argv = _rewrite_dash_prefixed_codex_args(raw_argv)
    args = build_arg_parser().parse_args(normalized_argv)
    if args.dual_run and args.runners:
        print('ERROR: --dual-run cannot be combined with --runners. Choose one mode.', file=sys.stderr)
        return 1
    if args.smoke and args.dual_run:
        print('ERROR: --smoke cannot be combined with --dual-run.', file=sys.stderr)
        return 1
    if args.smoke and args.runners:
        print('ERROR: --smoke cannot be combined with --runners. Use one shortcut or the explicit runner list.', file=sys.stderr)
        return 1
    if args.smoke and args.runner != 'codex':
        print('ERROR: --smoke cannot be combined with an explicit non-default --runner. Use one or the other.', file=sys.stderr)
        return 1
    if args.codex_settings:
        print('ERROR: --codex-settings is deprecated because plain `codex` runner was removed. Use --codex-kimi-settings or --codex-zai-settings.', file=sys.stderr)
        return 1
    skill_md = _resolve_skill_md_path(args.path)
    if not skill_md.exists():
        print(f'ERROR: SKILL.md not found at: {skill_md}', file=sys.stderr)
        return 1
    skill_dir = skill_md.parent
    skill_frontmatter = load_skill_frontmatter(skill_md)
    skill_name = str(skill_frontmatter.get('name') or '').strip()
    if not skill_name:
        print(f'ERROR: SKILL.md frontmatter missing valid `name`: {skill_md}', file=sys.stderr)
        return 1
    skill_contract_text = skill_md.read_text(encoding='utf-8')
    evals_path = skill_dir / 'references' / 'evals.yaml'
    if not evals_path.exists():
        print(f'ERROR: Missing evals file: {evals_path}', file=sys.stderr)
        return 1
    try:
        evals_doc = _load_evals_document(evals_path)
        cases = load_evals(evals_path)
        neutral_baseline_approvals = load_neutral_baseline_approvals(evals_path)
    except ValueError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    case_filters = _parse_csv_args(args.case)
    category_filters = _parse_csv_args(args.category)
    try:
        cases = _filter_cases(cases, case_filters=case_filters, categories=category_filters, exact_case_ids=args.eval_mode == 'release' and bool(case_filters))
    except ValueError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    cases = _filter_cases_for_eval_mode(cases, eval_mode=args.eval_mode)
    try:
        claim_to_evidence = _claim_to_evidence_summary(evals_doc, cases, eval_mode=args.eval_mode, skill_dir=skill_dir, focused_subset=bool(case_filters))
    except ValueError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    if args.list_cases:
        _print_case_listing(cases)
        return 0
    if not cases:
        print(f'ERROR: No eval cases matched the selected filters and eval mode `{args.eval_mode}`.', file=sys.stderr)
        return 1
    workspace_root = Path(args.workspace).expanduser().resolve() if args.workspace else _guess_repo_root(skill_dir)
    codex_home = Path(args.codex_home).expanduser().resolve() if args.codex_home else None
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and (not codex_bin.exists()):
        print(f'ERROR: --codex-bin not found: {codex_bin}', file=sys.stderr)
        return 1
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and (not codex_bin.exists()):
        print(f'ERROR: --codex-bin not found: {codex_bin}', file=sys.stderr)
        return 1
    openai_bin = Path(args.openai_bin).expanduser() if args.openai_bin else None
    if openai_bin and (not openai_bin.exists()):
        print(f'ERROR: --openai-bin not found: {openai_bin}', file=sys.stderr)
        return 1
    if args.runners:
        try:
            selected_runners = _parse_runners(args.runners)
        except ValueError as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            return 1
    elif args.dual_run:
        selected_runners = ['codex', 'codex-kimi']
    elif args.smoke:
        selected_runners = ['discovery-smoke']
    else:
        selected_runners = [args.runner]
    codex_fallback_profile = str(args.codex_fallback_profile or '').strip() or None
    codex_kimi_command = str(args.codex_kimi_command or '').strip() or 'codex-kimi'
    codex_zai_command = str(args.codex_zai_command or '').strip() or 'codex-zai'
    preflight_warnings: List[str] = []
    if 'codex' in selected_runners and (codex_home is None or args.profile == 'oss-cloud'):
        try:
            codex_home, isolation_warnings = _isolated_codex_home_for_eval(args.profile, source_home=codex_home)
        except ValueError as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            return 1
        preflight_warnings.extend(isolation_warnings)
    smoke_runners_only = bool(selected_runners) and all((r == 'discovery-smoke' for r in selected_runners))
    has_smoke_cases = any((c.smoke_mode for c in cases))
    if smoke_runners_only and has_smoke_cases:
        cases = [c for c in cases if c.smoke_mode]
    elif smoke_runners_only:
        print('ERROR: discovery-smoke runner requires eval cases with `smoke_mode`; none matched the selected filters. Use a live runner such as `codex` for behavior evals, or add discovery-specific smoke_mode cases.', file=sys.stderr)
        return 1
    elif not smoke_runners_only and has_smoke_cases:
        cases = [c for c in cases if not _is_smoke_only_case(c)]
        if case_filters and (not cases):
            print('ERROR: selected case filters matched only smoke-only discovery contract cases, which live/model runners skip. Use --runner discovery-smoke for discovery contract cases or select a behavior smoke case for live/model runners.', file=sys.stderr)
            return 1
    capture_jsonl = bool(args.capture_jsonl or any((c.deterministic_checks or c.budgets for c in cases)) or (args.eval_mode == 'release' and 'codex' in selected_runners))
    if 'codex' in selected_runners and args.dual_run and (not capture_jsonl):
        print('ERROR: --dual-run requires --capture-jsonl for deterministic Codex checks.', file=sys.stderr)
        return 1
    codex_kimi_settings: Optional[Path] = None
    if 'codex-kimi' in selected_runners:
        if codex_kimi_command == 'codex':
            codex_kimi_settings = _resolve_path(args.codex_kimi_settings, base=workspace_root)
            if not codex_kimi_settings.exists():
                print(f'ERROR: codex-kimi settings file not found: {codex_kimi_settings} (override with --codex-kimi-settings)', file=sys.stderr)
                return 1
        else:
            candidate = _resolve_path(args.codex_kimi_settings, base=workspace_root)
            if candidate.exists():
                codex_kimi_settings = candidate
    codex_zai_settings: Optional[Path] = None
    if 'codex-zai' in selected_runners:
        if codex_zai_command == 'codex':
            codex_zai_settings = _resolve_path(args.codex_zai_settings, base=workspace_root)
            if not codex_zai_settings.exists():
                print(f'ERROR: codex-zai settings file not found: {codex_zai_settings} (override with --codex-zai-settings)', file=sys.stderr)
                return 1
        else:
            candidate = _resolve_path(args.codex_zai_settings, base=workspace_root)
            if candidate.exists():
                codex_zai_settings = candidate
    preflight_errors: List[str] = []
    if 'codex' in selected_runners:
        if not (workspace_root / '.git').exists() and (not _has_skip_git_repo_check(args.codex_arg)):
            preflight_warnings.append("Workspace does not appear to be a trusted git repository. Codex may fail with 'Not inside a trusted directory'. If this is an ephemeral directory, add --codex-arg=--skip-git-repo-check.")
        auth_errors, auth_warnings = _preflight_codex_live_runner(workspace_root=workspace_root, codex_bin=codex_bin, codex_home=codex_home)
        preflight_errors.extend(auth_errors)
        preflight_warnings.extend(auth_warnings)
    if preflight_errors:
        for message in preflight_errors:
            print(f'ERROR: {message}', file=sys.stderr)
        for message in preflight_warnings:
            print(f'WARNING: {message}', file=sys.stderr)
        return 1
    reports_root = Path(args.reports_dir).expanduser().resolve() / skill_name
    reports_root.mkdir(parents=True, exist_ok=True)
    reports_base: Optional[Path] = None
    run_id = ''
    for _ in range(8):
        candidate = dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        candidate_path = reports_root / candidate
        try:
            candidate_path.mkdir(parents=False, exist_ok=False)
            reports_base = candidate_path
            run_id = candidate
            break
        except FileExistsError:
            continue
    if reports_base is None or not run_id:
        print('ERROR: unable to allocate unique report directory run_id', file=sys.stderr)
        return 1
    git_meta = _git_metadata(skill_dir)
    readiness_summary: Dict[str, int] = {state: 0 for state in sorted(_READINESS_STATE_CHOICES)}
    readiness_summary['unknown'] = 0
    round_state_summary: Dict[str, int] = {state: 0 for state in sorted(_ROUND_STATE_CHOICES)}
    round_state_summary['unknown'] = 0
    comparison_review_paths: List[str] = []
    used_neutral_baseline_approvals: Set[str] = set()
    summary: Dict[str, Any] = {'schema_version': '2.1', 'tool': 'run_skill_evals', 'generated_at': _utc_now_iso(), 'skill': skill_name, 'skill_path': _make_relative(skill_dir, workspace_root), 'skill_release': {'name': skill_name, 'version': str(skill_frontmatter.get('version') or '0.0.0+local'), 'compatibility': skill_frontmatter.get('compatibility') or 'codex', 'release_channel': skill_frontmatter.get('release_channel') or 'local', 'schema_version': str(skill_frontmatter.get('schema_version') or '1'), 'source_commit': git_meta.get('commit'), 'source_branch': git_meta.get('branch')}, 'workspace_root': str(workspace_root), 'runner_mode': ','.join(selected_runners), 'eval_mode': args.eval_mode, 'tier2_mode': args.tier2_mode, 'run_id': run_id, 'case_filters': case_filters, 'category_filters': category_filters, 'timeout_profile': args.timeout_profile, 'timeout_sec': _eval_timeout_seconds(timeout_sec=args.timeout_sec, timeout_profile=args.timeout_profile), 'capture_jsonl': capture_jsonl, 'cases': [], 'passed': True, 'tier1_failures': 0, 'tier2_findings': 0, 'blocked_cases': 0, 'blocked_class_summary': {key: 0 for key in RUNNER_BLOCKER_TAXONOMY}, 'blocker_taxonomy': dict(RUNNER_BLOCKER_TAXONOMY), 'preflight_warnings': preflight_warnings, 'readiness_summary': readiness_summary, 'round_state_summary': round_state_summary, 'neutral_baseline_approvals_used': [], 'claim_to_evidence': claim_to_evidence, 'eval_contract_migration': _eval_contract_migration_summary(cases, eval_mode=args.eval_mode)}
    if args.eval_mode == 'release':
        summary['security_dependency_screening'] = _snyk_release_gate(skill_dir=skill_dir, workspace_root=workspace_root)
    else:
        summary['security_dependency_screening'] = {'schema_version': 'skill-release-snyk-gate.v1', 'required': False, 'status': 'skipped', 'reason': 'Snyk dependency screening is required only for release evals of manifest-backed skill packages.', 'manifest_paths': [], 'command': None, 'exit_code': None, 'stdout': '', 'stderr': ''}
    any_tier1_failed = False
    any_tier2_failed = False
    any_blocked = False
    next_reproduce_command = _build_next_reproduce_command(args, selected_runners=selected_runners, capture_jsonl=capture_jsonl)
    for idx, c in enumerate(cases, 1):
        case_slug = _safe_slug(c.id or c.name)
        case_dir = reports_base / f'{idx:02d}-{case_slug}'
        case_dir.mkdir(parents=True, exist_ok=True)
        schema_path: Optional[Path] = None
        if c.output_schema:
            schema_path = Path(c.output_schema)
            if not schema_path.is_absolute():
                schema_path = (skill_dir / schema_path).resolve()
            if not schema_path.exists():
                print(f'ERROR: Case {c.name}: output_schema not found: {schema_path}', file=sys.stderr)
                return 1
        prompt_body = c.prompt.strip() + '\n'
        if c.prepend_skill:
            try:
                skill_label = skill_md.relative_to(workspace_root)
            except ValueError:
                skill_label = skill_md.name
            composed_prompt = f'${skill_name}\n\nThe local skill handle may not expand inside this isolated eval runner. Apply this SKILL.md content directly; do not try to read the skill file.\n\n<SKILL.md path="{skill_label}">\n{skill_contract_text}\n</SKILL.md>\n\nTask:\n{prompt_body}'
        else:
            composed_prompt = prompt_body
        (case_dir / 'prompt.txt').write_text(composed_prompt, encoding='utf-8')
        _write_provisional_workflow_closeout(reports_base=reports_base, workspace_root=workspace_root, skill_dir=skill_dir, eval_mode=args.eval_mode, runner_mode=summary['runner_mode'], next_reproduce_command=next_reproduce_command)
        case_timeout_sec, case_timeout_profile = _resolve_case_timeout(c, cli_timeout_sec=args.timeout_sec, cli_timeout_profile=args.timeout_profile)
        comparison_review_artifact = _resolve_optional_case_artifact_path(case_dir, c.comparison_review_artifact, workspace_root)
        neutral_baseline_approval: Optional[Dict[str, Any]] = None
        if c.baseline_type == 'neutral_repo_baseline':
            approval_id = c.neutral_baseline_approval_id or ''
            neutral_baseline_approval = neutral_baseline_approvals.get(approval_id)
            if neutral_baseline_approval is None:
                print(f'ERROR: case {c.id} references missing neutral_baseline_approval_id={approval_id!r} in {evals_path}', file=sys.stderr)
                return 1
        case_tier1_failures: List[str] = []
        case_tier2_findings: List[str] = []
        case_warnings: List[str] = _riteway_case_warnings(c, eval_mode=args.eval_mode)
        case_blocked_reasons: List[str] = []
        case_notes: List[str] = []
        runner_records: Dict[str, Any] = {}
        for runner_name in selected_runners:
            runner_dir = case_dir / runner_name
            runner_dir.mkdir(parents=True, exist_ok=True)
            output_path = runner_dir / 'output_last_message.txt'
            jsonl_path = runner_dir / 'codex_events.jsonl' if runner_name == 'codex' and capture_jsonl else None
            if runner_name in {'codex-kimi', 'codex-zai'}:
                if runner_name == 'codex-kimi':
                    runner_settings = codex_kimi_settings
                    runner_command = codex_kimi_command
                elif runner_name == 'codex-zai':
                    runner_settings = codex_zai_settings
                    runner_command = codex_zai_command
                rc, stdout, stderr = run_alt_codex_exec(workspace_root=workspace_root, prompt=composed_prompt, output_last_message_path=output_path, codex_bin=codex_bin, output_format=args.codex_output_format, settings_path=runner_settings, cli_command=runner_command, timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile, extra_codex_args=args.codex_arg or None)
                runner_exec_warnings: List[str] = []
            elif runner_name == 'openai':
                rc, stdout, stderr = run_openai_exec(workspace_root=workspace_root, prompt=composed_prompt, output_last_message_path=output_path, openai_bin=openai_bin, output_format=args.openai_output_format, timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile, extra_openai_args=args.openai_arg or None)
                runner_exec_warnings = []
            elif runner_name == 'discovery-smoke':
                rc, stdout, stderr, runner_exec_warnings = run_discovery_smoke(skill_md_path=skill_md, skill_dir=skill_dir, case=c, output_last_message_path=output_path)
            else:
                rc, stdout, stderr, runner_exec_warnings = run_codex_exec(workspace_root=workspace_root, prompt=composed_prompt, output_last_message_path=output_path, output_schema_path=schema_path, sandbox=args.sandbox, ask_for_approval=args.ask_for_approval, model=args.model, profile=args.profile, codex_home=codex_home, jsonl_path=jsonl_path, codex_bin=codex_bin, timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile, extra_codex_args=args.codex_arg or None, fallback_profile=codex_fallback_profile)
            runner_dir.mkdir(parents=True, exist_ok=True)
            (runner_dir / 'stderr.txt').write_text(stderr or '', encoding='utf-8')
            (runner_dir / 'stdout.txt').write_text(stdout or '', encoding='utf-8')
            output_text = output_path.read_text(encoding='utf-8') if output_path.exists() else ''
            runner_dir.mkdir(parents=True, exist_ok=True)
            (runner_dir / 'final.txt').write_text(output_text, encoding='utf-8')
            runner_tier1_failures: List[str] = []
            runner_tier2_findings: List[str] = []
            runner_warnings: List[str] = list(runner_exec_warnings)
            runner_notes: List[str] = []
            runner_metrics: Dict[str, Any] = {}
            runner_blocked_runtime = False
            events: Optional[List[Dict[str, Any]]] = None
            if runner_name == 'codex' and jsonl_path is not None:
                events, parse_warnings = load_jsonl_events(jsonl_path)
                runner_warnings.extend(parse_warnings)
                if c.deterministic_checks or c.budgets:
                    trace_result = evaluate_trace(events, deterministic_checks=c.deterministic_checks, budgets=c.budgets)
                    runner_metrics['trace'] = trace_result.to_dict()['metrics']
                    runner_tier1_failures.extend(trace_result.hard_failures)
                    if args.tier2_mode != 'off':
                        runner_tier2_findings.extend(trace_result.soft_failures)
                    runner_warnings.extend(trace_result.warnings)
                else:
                    trace_result = evaluate_trace(events, deterministic_checks=None, budgets=None)
                    runner_metrics['trace'] = trace_result.to_dict()['metrics']
            if runner_name == 'codex' and (c.deterministic_checks or c.budgets) and (jsonl_path is None):
                runner_tier1_failures.append('deterministic_checks/budgets requested but Codex JSONL was not captured (enable --capture-jsonl).')
            selected_skill = detect_skill_selected(skill_name=skill_name, output_text=output_text, stdout_text=stdout, stderr_text=stderr, events=events)
            if runner_name == 'discovery-smoke' and selected_skill is None and c.smoke_mode:
                selected_skill = True
            runner_metrics['selected_skill'] = selected_skill
            if c.should_trigger is not None and selected_skill is not None and (selected_skill != c.should_trigger):
                runner_tier1_failures.append(f'should_trigger failed: expected {c.should_trigger}, detected {selected_skill}')
            budgets = c.budgets if isinstance(c.budgets, dict) else {}
            require_selection_signal = bool(budgets.get('require_selection_signal'))
            if c.should_trigger is True and selected_skill is None:
                message = f'should_trigger={c.should_trigger} but selection signal unavailable (selected_skill is None). Cannot verify selection expectation without signal evidence.'
                if require_selection_signal:
                    runner_tier1_failures.append(message)
                else:
                    runner_notes.append(message + ' Discovery-smoke or budgets.require_selection_signal=true should own hard selection proof.')
            if c.should_trigger is False and selected_skill is None:
                runner_notes.append('should_trigger=false and selection signal unavailable; treating absence of positive selection evidence as acceptable for this negative case.')
            runner_blocker_class = _classify_runner_blocker(output_text=output_text, stdout_text=stdout, stderr_text=stderr, exit_code=rc)
            runner_blocked_runtime = runner_blocker_class is not None
            runner_blocked_reasons: List[str] = []
            if runner_blocked_runtime:
                definition = RUNNER_BLOCKER_TAXONOMY.get(runner_blocker_class or 'blocked_runtime', 'The eval runner was blocked before skill behavior could be judged.')
                runner_blocked_reasons.append(f'{runner_blocker_class}: {definition} This is an eval runner blocker, not a skill behavior failure.')
            elif rc != 0:
                runner_tier1_failures.append(f'{runner_name} returned non-zero exit code: {rc}')
                if runner_name == 'codex' and _is_codex_untrusted_repo_error(stderr):
                    runner_warnings.append('Codex rejected this workspace as untrusted. Use a trusted git repo as --workspace, or pass --codex-arg=--skip-git-repo-check for ephemeral temp directories.')
            parsed_json: Optional[Any] = None
            used_json_assertions = False
            acceptance_skip_reason = _acceptance_skip_reason(exit_code=rc, output_text=output_text)
            if runner_blocked_runtime:
                pass
            elif acceptance_skip_reason is not None:
                runner_warnings.append(acceptance_skip_reason)
            else:
                if schema_path and runner_name == 'codex':
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:
                        runner_tier1_failures.append(f'expected JSON output (schema used), but parsing failed: {e}')
                    else:
                        used_json_assertions = True
                elif runner_name in {'codex-kimi', 'codex-zai'} and args.codex_output_format == 'json':
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:
                        runner_tier1_failures.append(f'expected JSON output (Codex json format), but parsing failed: {e}')
                    else:
                        used_json_assertions = True
                elif runner_name == 'openai' and args.openai_output_format == 'json':
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:
                        runner_tier1_failures.append(f'expected JSON output (OpenAI json format), but parsing failed: {e}')
                    else:
                        used_json_assertions = True
                if used_json_assertions and parsed_json is not None:
                    runner_tier1_failures.extend(evaluate_assertions_json(parsed_json, c.acceptance, skill_name=skill_name, selected_skill=selected_skill))
                else:
                    runner_tier1_failures.extend(evaluate_assertions_text(output_text, c.acceptance, skill_name=skill_name, selected_skill=selected_skill))
            agent_self_assessment = _parse_agent_self_assessment(output_text)
            if agent_self_assessment is False and (not runner_blocked_runtime):
                runner_tier1_failures.append("Agent self-assessment reports explicit failure (e.g., 'Pass/fail: Fail'). Treating this as a hard failure regardless of exit_code.")
            rubric = extract_rubric_metrics(parsed_json) if parsed_json is not None else None
            if rubric:
                runner_metrics['rubric'] = rubric
                min_score = _extract_min_rubric_score(c.budgets)
                if args.tier2_mode != 'off' and min_score is not None and isinstance(rubric.get('score'), (int, float)) and (float(rubric['score']) < min_score):
                    runner_tier2_findings.append(f"rubric score below budget: got {rubric['score']} < min_rubric_score {min_score}")
                require_overall_pass = _extract_require_overall_pass(c.budgets)
                if args.tier2_mode != 'off' and require_overall_pass is True and (rubric.get('overall_pass') is False):
                    runner_tier2_findings.append('rubric overall_pass is false but require_overall_pass budget is true')
            if not runner_blocked_runtime and c.expected_signals:
                try:
                    expected_signal_result = evaluate_expected_signals(output_text, c.expected_signals)
                except ValueError as exc:
                    runner_tier1_failures.append(str(exc))
                    expected_signal_result = None
                if expected_signal_result is not None:
                    runner_metrics[EXPECTED_SIGNAL_METRIC_KEY] = expected_signal_result
                    min_expected_score = _extract_min_expected_signal_score(c.budgets)
                    if args.tier2_mode != 'off' and min_expected_score is not None and (expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY] < min_expected_score):
                        runner_tier2_findings.append(f'expected signal score below budget: got {expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY]} < min_expected_signal_score {min_expected_score:g}')
            runner_record = {'runner': runner_name, 'exit_code': rc, 'passed': len(runner_tier1_failures) == 0 and (not runner_blocked_runtime), 'blocked': runner_blocked_runtime, 'blocker_class': runner_blocker_class, 'blocked_reasons': runner_blocked_reasons, 'tier1_failures': runner_tier1_failures, 'tier2_findings': runner_tier2_findings, 'warnings': runner_warnings, 'notes': runner_notes, 'artifacts': {'dir': _make_relative(runner_dir, workspace_root), 'final': _make_relative(runner_dir / 'final.txt', workspace_root), 'raw_response': _make_relative(runner_dir / 'final.txt', workspace_root), 'stdout': _make_relative(runner_dir / 'stdout.txt', workspace_root), 'stderr': _make_relative(runner_dir / 'stderr.txt', workspace_root), 'jsonl': _make_relative(jsonl_path, workspace_root) if jsonl_path else None, 'judge_details': _make_relative(runner_dir / 'result.json', workspace_root)}, 'metrics': runner_metrics, 'used_schema': bool(schema_path and runner_name == 'codex')}
            if _case_requires_no_skill_baseline(c):
                baseline_record: Dict[str, Any]
                baseline_dir = runner_dir / 'baseline-no-skill'
                baseline_dir.mkdir(parents=True, exist_ok=True)
                baseline_output_path = baseline_dir / 'output_last_message.txt'
                baseline_jsonl_path = baseline_dir / 'codex_events.jsonl' if runner_name == 'codex' and capture_jsonl else None
                if runner_name in {'codex-kimi', 'codex-zai'}:
                    if runner_name == 'codex-kimi':
                        runner_settings = codex_kimi_settings
                        runner_command = codex_kimi_command
                    else:
                        runner_settings = codex_zai_settings
                        runner_command = codex_zai_command
                    baseline_rc, baseline_stdout, baseline_stderr = run_alt_codex_exec(workspace_root=workspace_root, prompt=prompt_body, output_last_message_path=baseline_output_path, codex_bin=codex_bin, output_format=args.codex_output_format, settings_path=runner_settings, cli_command=runner_command, timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile, extra_codex_args=args.codex_arg or None)
                    baseline_exec_warnings = []
                elif runner_name == 'openai':
                    baseline_rc, baseline_stdout, baseline_stderr = run_openai_exec(workspace_root=workspace_root, prompt=prompt_body, output_last_message_path=baseline_output_path, openai_bin=openai_bin, output_format=args.openai_output_format, timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile, extra_openai_args=args.openai_arg or None)
                    baseline_exec_warnings = []
                elif runner_name == 'discovery-smoke':
                    baseline_rc, baseline_stdout, baseline_stderr, baseline_exec_warnings = run_discovery_smoke(skill_md_path=skill_md, skill_dir=skill_dir, case=c, output_last_message_path=baseline_output_path, include_skill_context=False)
                else:
                    baseline_rc, baseline_stdout, baseline_stderr, baseline_exec_warnings = run_codex_exec(workspace_root=workspace_root, prompt=prompt_body, output_last_message_path=baseline_output_path, output_schema_path=schema_path, sandbox=args.sandbox, ask_for_approval=args.ask_for_approval, model=args.model, profile=args.profile, codex_home=codex_home, jsonl_path=baseline_jsonl_path, codex_bin=codex_bin, timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile, extra_codex_args=args.codex_arg or None, fallback_profile=codex_fallback_profile)
                (baseline_dir / 'stdout.txt').write_text(baseline_stdout or '', encoding='utf-8')
                (baseline_dir / 'stderr.txt').write_text(baseline_stderr or '', encoding='utf-8')
                baseline_output_text = baseline_output_path.read_text(encoding='utf-8') if baseline_output_path.exists() else ''
                (baseline_dir / 'final.txt').write_text(baseline_output_text, encoding='utf-8')
                baseline_record = _evaluate_baseline_output(runner_name=runner_name, case=c, skill_name=skill_name, exit_code=baseline_rc, stdout_text=baseline_stdout, stderr_text=baseline_stderr, output_text=baseline_output_text, schema_path=schema_path, codex_output_format=args.codex_output_format, openai_output_format=args.openai_output_format)
                baseline_record['warnings'] = list(baseline_exec_warnings) + list(baseline_record.get('warnings') or [])
                baseline_record['artifacts'] = {'dir': _make_relative(baseline_dir, workspace_root), 'final': _make_relative(baseline_dir / 'final.txt', workspace_root), 'raw_response': _make_relative(baseline_dir / 'final.txt', workspace_root), 'stdout': _make_relative(baseline_dir / 'stdout.txt', workspace_root), 'stderr': _make_relative(baseline_dir / 'stderr.txt', workspace_root), 'jsonl': _make_relative(baseline_jsonl_path, workspace_root) if baseline_jsonl_path else None, 'judge_details': _make_relative(baseline_dir / 'result.json', workspace_root)}
                (baseline_dir / 'result.json').write_text(json.dumps(baseline_record, indent=2, ensure_ascii=False), encoding='utf-8')
                runner_record['baseline'] = baseline_record
                runner_record['baseline_comparison'] = _baseline_comparison_from_records(runner_record=runner_record, baseline_record=baseline_record)
            (runner_dir / 'result.json').write_text(json.dumps(runner_record, indent=2, ensure_ascii=False), encoding='utf-8')
            runner_records[runner_name] = runner_record
            case_tier1_failures.extend([f'[{runner_name}] {x}' for x in runner_tier1_failures])
            case_tier2_findings.extend([f'[{runner_name}] {x}' for x in runner_tier2_findings])
            case_warnings.extend([f'[{runner_name}] {x}' for x in runner_warnings])
            case_blocked_reasons.extend([f'[{runner_name}] {x}' for x in runner_blocked_reasons])
            case_notes.extend([f'[{runner_name}] {x}' for x in runner_notes])
        case_blocked = any((bool(record.get('blocked')) for record in runner_records.values()))
        case_blocker_classes = sorted({str(record.get('blocker_class')) for record in runner_records.values() if record.get('blocker_class')})
        baseline_comparisons = {runner_name: record['baseline_comparison'] for runner_name, record in runner_records.items() if isinstance(record, dict) and isinstance(record.get('baseline_comparison'), dict)}
        compared_baselines = [comparison for comparison in baseline_comparisons.values() if comparison.get('status') == 'compared']
        skill_lift: Optional[int] = None
        is_beneficial = False
        baseline_regression = False
        if compared_baselines:
            skill_lift = max((int(comparison.get('skill_lift') or 0) for comparison in compared_baselines))
            is_beneficial = any((bool(comparison.get('is_beneficial')) for comparison in compared_baselines))
            baseline_regression = any((bool(comparison.get('regression')) for comparison in compared_baselines))
        require_skill_lift = _extract_bool_budget(c.budgets, 'require_skill_lift')
        min_skill_lift = _extract_min_skill_lift(c.budgets)
        if require_skill_lift is True or min_skill_lift is not None:
            if not compared_baselines:
                case_tier1_failures.append('skill lift budget requested but no executed no-skill baseline comparison was available')
            else:
                if require_skill_lift is True and (not is_beneficial):
                    case_tier1_failures.append('require_skill_lift failed: skill-enabled run did not beat the no-skill baseline')
                if min_skill_lift is not None and (skill_lift is None or skill_lift < min_skill_lift):
                    case_tier1_failures.append(f"min_skill_lift failed: got {(skill_lift if skill_lift is not None else 'none')} < {min_skill_lift}")
        case_tier1_failed = len(case_tier1_failures) > 0
        case_tier2_failed = len(case_tier2_findings) > 0
        case_pass = not case_tier1_failed and (args.tier2_mode != 'fail' or not case_tier2_failed)
        case_pass = case_pass and (not case_blocked)
        riteway_report = _riteway_case_report(c, case_dir=case_dir, workspace_root=workspace_root, runner_records=runner_records)
        case_record = {'id': c.id, 'name': c.name, 'category': c.category, 'eval_modes': list(c.eval_modes) if c.eval_modes else None, 'should_trigger': c.should_trigger, 'prepend_skill': c.prepend_skill, 'baseline_type': c.baseline_type, 'baseline_id': c.baseline_id, 'claim_ids': list(c.claim_ids), 'realistic': c.realistic, 'why_realistic': c.why_realistic, 'hard_gates': list(c.hard_gates), 'expected_evidence': list(c.expected_evidence), 'riteway': riteway_report, 'pass_rate_policy': {'threshold': c.pass_rate_threshold, 'calibration_artifact': _resolve_optional_case_artifact_path(case_dir, c.pass_rate_calibration_artifact, workspace_root), 'gate_status': 'calibrated_gate' if _resolve_existing_optional_case_artifact_path(case_dir, c.pass_rate_calibration_artifact, workspace_root) else 'advisory'} if c.pass_rate_threshold is not None else None, 'agent_eval_artifacts': {'raw_response': _resolve_optional_case_artifact_path(case_dir, c.raw_response_artifact, workspace_root), 'judge_details': _resolve_optional_case_artifact_path(case_dir, c.judge_detail_artifact, workspace_root)}, 'evidence_surfaces': _case_evidence_surfaces(c), 'check_evidence': _case_has_executed_check_evidence(c, runner_records), 'comparison_inputs': dict(c.comparison_inputs) if c.comparison_inputs else None, 'iteration_round_state': c.iteration_round_state, 'metric_availability': c.metric_availability, 'readiness_state': c.readiness_state, 'comparison_review_artifact': comparison_review_artifact, 'neutral_baseline_approval': neutral_baseline_approval, 'baseline_comparisons': baseline_comparisons, 'skill_lift': skill_lift, 'is_beneficial': is_beneficial, 'baseline_regression': baseline_regression, 'expected_signals': bool(c.expected_signals), 'timeout_profile': case_timeout_profile, 'timeout_sec': _eval_timeout_seconds(timeout_sec=case_timeout_sec, timeout_profile=case_timeout_profile), 'dir': _make_relative(case_dir, workspace_root), 'runners': runner_records, 'passed': case_pass, 'blocked': case_blocked, 'blocker_classes': case_blocker_classes, 'blocked_reasons': case_blocked_reasons, 'tier1_failed': case_tier1_failed, 'tier2_failed': case_tier2_failed, 'tier1_failures': case_tier1_failures, 'tier2_findings': case_tier2_findings, 'warnings': case_warnings, 'notes': case_notes}
        (case_dir / 'result.json').write_text(json.dumps(case_record, indent=2, ensure_ascii=False), encoding='utf-8')
        summary['cases'].append(case_record)
        if c.readiness_state:
            summary['readiness_summary'][c.readiness_state] = summary['readiness_summary'].get(c.readiness_state, 0) + 1
        else:
            summary['readiness_summary']['unknown'] += 1
        if c.iteration_round_state:
            summary['round_state_summary'][c.iteration_round_state] = summary['round_state_summary'].get(c.iteration_round_state, 0) + 1
        else:
            summary['round_state_summary']['unknown'] += 1
        if comparison_review_artifact:
            comparison_review_paths.append(comparison_review_artifact)
        if c.neutral_baseline_approval_id:
            used_neutral_baseline_approvals.add(c.neutral_baseline_approval_id)
        if case_tier1_failed:
            any_tier1_failed = True
            summary['tier1_failures'] += 1
        if case_blocked:
            any_blocked = True
            summary['blocked_cases'] += 1
            for blocker_class in case_blocker_classes:
                summary['blocked_class_summary'][blocker_class] = summary['blocked_class_summary'].get(blocker_class, 0) + 1
        if case_tier2_failed:
            any_tier2_failed = True
            summary['tier2_findings'] += 1
    summary['expected_signal_summary'] = summarize_expected_signal_results(summary['cases'])
    _attach_claim_execution_results(summary['claim_to_evidence'], summary['cases'], eval_mode=args.eval_mode, focused_subset=bool(case_filters))
    snyk_gate_passed = _snyk_release_gate_passed(summary['security_dependency_screening'])
    claim_gate_passed = bool(summary['claim_to_evidence'].get('passed', True))
    if _mark_no_case_evidence_blocked(summary):
        any_blocked = True
    summary['passed'] = not any_blocked and (not any_tier1_failed) and snyk_gate_passed and (args.tier2_mode != 'fail' or not any_tier2_failed)
    summary['passed'] = summary['passed'] and claim_gate_passed
    summary['decision'] = 'pass' if summary['passed'] else 'fail'
    if any_blocked:
        summary['decision'] = 'blocked'
    if not snyk_gate_passed:
        snyk_status = str(summary['security_dependency_screening'].get('status', ''))
        summary['decision'] = 'blocked' if snyk_status.startswith('blocked') else 'fail'
    if not claim_gate_passed:
        summary['decision'] = 'blocked'
    summary['exit_code'] = 0 if summary['passed'] else 2
    summary_path = reports_base / 'summary.json'
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    scorecard_path = Path(args.scorecard_out).expanduser().resolve() if args.scorecard_out else reports_base / 'scorecard.json'
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(workspace_root))
        except ValueError:
            return str(p)
    summary['artifacts'] = {'reports_base': _rel(reports_base), 'summary': _rel(summary_path), 'scorecard': _rel(scorecard_path)}
    if comparison_review_paths:
        unique_paths = sorted(set(comparison_review_paths))
        summary['artifacts']['comparison_review'] = unique_paths[0] if len(unique_paths) == 1 else unique_paths
    summary['neutral_baseline_approvals_used'] = sorted(used_neutral_baseline_approvals)
    release_manifest_path = reports_base / 'release_manifest.json'
    junit_path = Path(args.junit_out).expanduser().resolve() if args.junit_out else reports_base / 'junit.xml'
    summary['artifacts']['release_manifest'] = _rel(release_manifest_path)
    summary['artifacts']['junit'] = _rel(junit_path)
    _write_junit_report(summary, junit_path)
    release_manifest = {'schema_version': '1.0', 'tool': 'run_skill_evals', 'generated_at': summary['generated_at'], 'skill': summary['skill_release'], 'run': {'run_id': run_id, 'eval_mode': args.eval_mode, 'runner_mode': summary['runner_mode'], 'tier2_mode': args.tier2_mode, 'capture_jsonl': capture_jsonl, 'readiness_summary': summary['readiness_summary'], 'round_state_summary': summary['round_state_summary'], 'neutral_baseline_approvals_used': summary['neutral_baseline_approvals_used'], 'security_dependency_screening': summary['security_dependency_screening'], 'claim_to_evidence': summary['claim_to_evidence'], 'reports_base': _rel(reports_base)}, 'artifacts': summary['artifacts']}
    release_manifest_path.write_text(json.dumps(release_manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    final_closeout_cases = [_case_closeout_from_summary(case) for case in summary['cases'] if isinstance(case, dict)]
    final_blocker_class = None
    if summary['decision'] == 'blocked':
        for case in final_closeout_cases:
            if case.get('blocker_class'):
                final_blocker_class = str(case.get('blocker_class'))
                break
        final_blocker_class = final_blocker_class or 'blocked_missing_artifact'
    _write_workflow_closeout(reports_base=reports_base, workspace_root=workspace_root, skill_dir=skill_dir, eval_mode=args.eval_mode, runner_mode=summary['runner_mode'], status='pass' if summary['decision'] == 'pass' else 'blocked' if summary['decision'] == 'blocked' else 'fail', cases=final_closeout_cases, blocker_class=final_blocker_class, missing_suite_artifacts=False, next_reproduce_command=next_reproduce_command)
    if args.format == 'json':
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f'Skill evals: {skill_name}')
        print(f'Reports: {reports_base}')
        print(f'Scorecard: {scorecard_path}')
        print(f'Release manifest: {release_manifest_path}')
        print(f'JUnit: {junit_path}')
        print(f"Runner mode: {summary['runner_mode']}")
        print(f'Eval mode: {args.eval_mode}')
        if case_filters:
            print(f"Case filters: {', '.join(case_filters)}")
        if category_filters:
            print(f"Category filters: {', '.join(category_filters)}")
        print(f'Timeout profile: {args.timeout_profile}')
        print(f"Timeout seconds: {summary['timeout_sec']}")
        print(f'Tier-2 mode: {args.tier2_mode}')
        for gap in summary.get('claim_to_evidence', {}).get('blocking_gaps', []):
            print(f"CLAIM-GATE: {gap.get('type')}: {gap.get('message')}")
        for w in summary.get('preflight_warnings', []):
            print(f'WARNING: {w}')
        for c in summary['cases']:
            status = 'PASS' if c['passed'] else 'FAIL'
            print(f"- {status}: {c['id']} ({c['name']})")
            for f in c['tier1_failures']:
                print(f'    - TIER1: {f}')
            for f in c['tier2_findings']:
                print(f'    - TIER2: {f}')
        if summary['passed'] and any_tier2_failed and (args.tier2_mode == 'warn'):
            print('RESULT: PASS (tier-2 findings present; warn mode)')
        elif summary['passed']:
            print('RESULT: PASS')
        else:
            print('RESULT: FAIL')
    return int(summary['exit_code'])

__all__ = [name for name in globals() if not name.startswith("__")]
