"""Summary, artifact, and presentation stages for skill evaluations."""

from run_skill_evals_discovery import *  # noqa: F403


def _initial_summary(context: Dict[str, Any]) -> Dict[str, Any]:
    args = context["args"]
    skill_frontmatter = context["skill_frontmatter"]
    skill_dir = context["skill_dir"]
    workspace_root = context["workspace_root"]
    git_meta = _git_metadata(skill_dir)
    readiness = {state: 0 for state in sorted(_READINESS_STATE_CHOICES)}
    readiness["unknown"] = 0
    round_states = {state: 0 for state in sorted(_ROUND_STATE_CHOICES)}
    round_states["unknown"] = 0
    return {
        "schema_version": "2.1", "tool": "run_skill_evals", "generated_at": _utc_now_iso(),
        "skill": context["skill_name"], "skill_path": _make_relative(skill_dir, workspace_root),
        "skill_release": {"name": context["skill_name"], "version": str(skill_frontmatter.get("version") or "0.0.0+local"), "compatibility": skill_frontmatter.get("compatibility") or "codex", "release_channel": skill_frontmatter.get("release_channel") or "local", "schema_version": str(skill_frontmatter.get("schema_version") or "1"), "source_commit": git_meta.get("commit"), "source_branch": git_meta.get("branch")},
        "workspace_root": str(workspace_root), "runner_mode": ",".join(context["selected_runners"]),
        "eval_mode": args.eval_mode, "tier2_mode": args.tier2_mode, "run_id": context["run_id"],
        "case_filters": context["case_filters"], "category_filters": context["category_filters"],
        "timeout_profile": args.timeout_profile, "timeout_sec": _eval_timeout_seconds(timeout_sec=args.timeout_sec, timeout_profile=args.timeout_profile),
        "capture_jsonl": context["capture_jsonl"], "cases": [], "passed": True,
        "tier1_failures": 0, "tier2_findings": 0, "blocked_cases": 0,
        "blocked_class_summary": {key: 0 for key in RUNNER_BLOCKER_TAXONOMY},
        "blocker_taxonomy": dict(RUNNER_BLOCKER_TAXONOMY), "preflight_warnings": context["preflight_warnings"],
        "readiness_summary": readiness, "round_state_summary": round_states,
        "neutral_baseline_approvals_used": [], "claim_to_evidence": context["claim_to_evidence"],
        "eval_contract_migration": _eval_contract_migration_summary(context["cases"], eval_mode=args.eval_mode),
    }


def _security_screening(context: Dict[str, Any]) -> Dict[str, Any]:
    if context["args"].eval_mode == "release":
        return _snyk_release_gate(
            skill_dir=context["skill_dir"], workspace_root=context["workspace_root"]
        )
    return {
        "schema_version": "skill-release-snyk-gate.v1", "required": False, "status": "skipped",
        "reason": "Snyk dependency screening is required only for release evals of manifest-backed skill packages.",
        "manifest_paths": [], "command": None, "exit_code": None, "stdout": "", "stderr": "",
    }


def _initialize_summary(context: Dict[str, Any]) -> None:
    summary = _initial_summary(context)
    summary["security_dependency_screening"] = _security_screening(context)
    context["summary"] = summary


def _decision_label(
    summary: Dict[str, Any], *, blocked: bool, snyk_passed: bool, claim_passed: bool
) -> str:
    if blocked:
        return "blocked"
    if not snyk_passed:
        status = str(summary["security_dependency_screening"].get("status", ""))
        return "blocked" if status.startswith("blocked") else "fail"
    if not claim_passed:
        return "blocked"
    return "pass" if summary["passed"] else "fail"


def _finalize_decision(context: Dict[str, Any]) -> None:
    args = context["args"]
    summary = context["summary"]
    summary["expected_signal_summary"] = summarize_expected_signal_results(summary["cases"])
    _attach_claim_execution_results(
        summary["claim_to_evidence"], summary["cases"], eval_mode=args.eval_mode,
        focused_subset=bool(context["case_filters"]),
    )
    snyk_passed = _snyk_release_gate_passed(summary["security_dependency_screening"])
    claim_passed = bool(summary["claim_to_evidence"].get("passed", True))
    if _mark_no_case_evidence_blocked(summary):
        context["any_blocked"] = True
    summary["passed"] = (
        not context["any_blocked"] and not context["any_tier1_failed"] and snyk_passed
        and (args.tier2_mode != "fail" or not context["any_tier2_failed"]) and claim_passed
    )
    summary["decision"] = _decision_label(
        summary, blocked=context["any_blocked"],
        snyk_passed=snyk_passed, claim_passed=claim_passed,
    )
    summary["exit_code"] = 0 if summary["passed"] else 2


def _relative_artifact(path: Path, workspace_root: Path) -> str:
    try:
        return str(path.relative_to(workspace_root))
    except ValueError:
        return str(path)


def _write_primary_outputs(context: Dict[str, Any]) -> Tuple[Path, Path, Path, Path]:
    args = context["args"]
    summary = context["summary"]
    reports_base = context["reports_base"]
    workspace_root = context["workspace_root"]
    summary_path = reports_base / "summary.json"
    scorecard_path = Path(args.scorecard_out).expanduser().resolve() if args.scorecard_out else reports_base / "scorecard.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    summary["artifacts"] = {"reports_base": _relative_artifact(reports_base, workspace_root), "summary": _relative_artifact(summary_path, workspace_root), "scorecard": _relative_artifact(scorecard_path, workspace_root)}
    review_paths = sorted(set(context["comparison_review_paths"]))
    if review_paths:
        summary["artifacts"]["comparison_review"] = review_paths[0] if len(review_paths) == 1 else review_paths
    summary["neutral_baseline_approvals_used"] = sorted(context["used_neutral_baseline_approvals"])
    release_path = reports_base / "release_manifest.json"
    junit_path = Path(args.junit_out).expanduser().resolve() if args.junit_out else reports_base / "junit.xml"
    summary["artifacts"].update({"release_manifest": _relative_artifact(release_path, workspace_root), "junit": _relative_artifact(junit_path, workspace_root)})
    return summary_path, scorecard_path, release_path, junit_path


def _release_manifest(context: Dict[str, Any]) -> Dict[str, Any]:
    args = context["args"]
    summary = context["summary"]
    return {
        "schema_version": "1.0", "tool": "run_skill_evals", "generated_at": summary["generated_at"],
        "skill": summary["skill_release"],
        "run": {"run_id": context["run_id"], "eval_mode": args.eval_mode, "runner_mode": summary["runner_mode"], "tier2_mode": args.tier2_mode, "capture_jsonl": context["capture_jsonl"], "readiness_summary": summary["readiness_summary"], "round_state_summary": summary["round_state_summary"], "neutral_baseline_approvals_used": summary["neutral_baseline_approvals_used"], "security_dependency_screening": summary["security_dependency_screening"], "claim_to_evidence": summary["claim_to_evidence"], "reports_base": _relative_artifact(context["reports_base"], context["workspace_root"])},
        "artifacts": summary["artifacts"],
    }


def _write_closeout(context: Dict[str, Any]) -> None:
    summary = context["summary"]
    cases = [_case_closeout_from_summary(case) for case in summary["cases"] if isinstance(case, dict)]
    blocker_class = None
    if summary["decision"] == "blocked":
        blocker_class = next((str(case.get("blocker_class")) for case in cases if case.get("blocker_class")), None)
        blocker_class = blocker_class or "blocked_missing_artifact"
    _write_workflow_closeout(
        reports_base=context["reports_base"], workspace_root=context["workspace_root"],
        skill_dir=context["skill_dir"], eval_mode=context["args"].eval_mode,
        runner_mode=summary["runner_mode"],
        status="pass" if summary["decision"] == "pass" else "blocked" if summary["decision"] == "blocked" else "fail",
        cases=cases, blocker_class=blocker_class, missing_suite_artifacts=False,
        next_reproduce_command=context["next_reproduce_command"],
    )


def _write_final_outputs(context: Dict[str, Any]) -> None:
    summary_path, scorecard_path, release_path, junit_path = _write_primary_outputs(context)
    summary = context["summary"]
    _write_junit_report(summary, junit_path)
    release_path.write_text(json.dumps(_release_manifest(context), indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    context.update({"summary_path": summary_path, "scorecard_path": scorecard_path, "release_manifest_path": release_path, "junit_path": junit_path})
    _write_closeout(context)


def _print_case_results(summary: Dict[str, Any]) -> None:
    for case in summary["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(f"- {status}: {case['id']} ({case['name']})")
        for failure in case["tier1_failures"]:
            print(f"    - TIER1: {failure}")
        for finding in case["tier2_findings"]:
            print(f"    - TIER2: {finding}")


def _print_human_summary(context: Dict[str, Any]) -> None:
    args = context["args"]
    summary = context["summary"]
    for label, value in (("Skill evals", context["skill_name"]), ("Reports", context["reports_base"]), ("Scorecard", context["scorecard_path"]), ("Release manifest", context["release_manifest_path"]), ("JUnit", context["junit_path"]), ("Runner mode", summary["runner_mode"]), ("Eval mode", args.eval_mode)):
        print(f"{label}: {value}")
    if context["case_filters"]:
        print(f"Case filters: {', '.join(context['case_filters'])}")
    if context["category_filters"]:
        print(f"Category filters: {', '.join(context['category_filters'])}")
    for label, value in (("Timeout profile", args.timeout_profile), ("Timeout seconds", summary["timeout_sec"]), ("Tier-2 mode", args.tier2_mode)):
        print(f"{label}: {value}")
    for gap in summary.get("claim_to_evidence", {}).get("blocking_gaps", []):
        print(f"CLAIM-GATE: {gap.get('type')}: {gap.get('message')}")
    for warning in summary.get("preflight_warnings", []):
        print(f"WARNING: {warning}")
    _print_case_results(summary)
    suffix = " (tier-2 findings present; warn mode)" if summary["passed"] and context["any_tier2_failed"] and args.tier2_mode == "warn" else ""
    print(f"RESULT: {'PASS' if summary['passed'] else 'FAIL'}{suffix}")


def _present_result(context: Dict[str, Any]) -> None:
    if context["args"].format == "json":
        print(json.dumps(context["summary"], indent=2, ensure_ascii=False))
    else:
        _print_human_summary(context)


__all__ = [name for name in globals() if not name.startswith("__")]
