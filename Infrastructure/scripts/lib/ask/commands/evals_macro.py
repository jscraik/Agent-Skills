from __future__ import annotations

import json
import re
import shlex
import shutil
from pathlib import Path

from ask.envelope import CallResult, ErrorObject

from .evals_core import (
    DEFAULT_MACRO_EVAL_REPORTS_GLOB,
    _eval_lifecycle_event_types,
    _safe_slug,
    _utc_now_iso,
)
from .evals_shared import EvalArtifactReadError, _load_json_file

def _repo_relative_text(repo_root: Path, text: str) -> str:
    if not text:
        return text
    root = str(repo_root.resolve())
    return text.replace(root + "/", "").replace(root, ".")


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _evals_run_validation_command(
    path: str,
    *,
    mode: str,
    runner: str,
    dashboard: bool,
    codex_profile: str | None = None,
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
    handoff_readiness_path: str | None = None,
    timeout_seconds: int | None = None,
) -> str:
    parts = ["./bin/ask", "evals", "run", path, "--mode", mode, "--runner", runner]
    if codex_profile:
        parts.extend(["--profile", codex_profile])
    if tessl_live_private:
        parts.append("--tessl-live-private")
    if tessl_workspace:
        parts.extend(["--tessl-workspace", tessl_workspace])
    if tessl_live_dry_run:
        parts.append("--tessl-live-dry-run")
    if handoff_readiness_path:
        parts.extend(["--handoff-readiness", handoff_readiness_path])
    if timeout_seconds is not None:
        parts.extend(["--timeout-seconds", str(timeout_seconds)])
    if not dashboard:
        parts.append("--no-dashboard")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _evals_validation_command(action: str) -> str:
    return " ".join(shlex.quote(part) for part in ["./bin/ask", "evals", action, "--json", "--robot"])


def _macro_eval_validation_command(output_dir: str | None = None, summaries_glob: str | None = None) -> str:
    parts = ["./bin/ask", "evals", "macro-report"]
    if output_dir:
        parts.extend(["--output-dir", output_dir])
    if summaries_glob:
        parts.extend(["--summaries-glob", summaries_glob])
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _macro_case_type(case: dict) -> str:
    category = case.get("category")
    if isinstance(category, str) and category.strip():
        return category.strip()
    case_id = str(case.get("id") or "unknown")
    return re.split(r"[-_:]", case_id, maxsplit=1)[0] or "unknown"


def _macro_run_outcome(summary: dict, case: dict) -> str:
    decision = str(summary.get("decision") or "").strip().lower()
    if decision == "blocked":
        return "blocked"
    if case.get("blocked") is True:
        return "blocked"
    blockers = case.get("blocker_classes")
    if isinstance(blockers, list) and blockers:
        return "blocked"
    if case.get("passed") is True:
        return "passed"
    if case.get("passed") is False:
        return "failed"
    if decision in {"pass", "passed"}:
        return "passed"
    return "failed" if decision == "fail" else "unknown"


def _first_string(values: object) -> str | None:
    if isinstance(values, list):
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _macro_eval_finding(summary: dict, case: dict) -> str:
    for key in ("blocker_classes", "tier1_failures", "tier2_findings", "warnings"):
        finding = _first_string(case.get(key))
        if finding:
            return finding
    runners = case.get("runners")
    if isinstance(runners, dict):
        for runner_name in sorted(runners):
            runner = runners.get(runner_name)
            if not isinstance(runner, dict):
                continue
            for key in ("blocker_classes", "tier1_failures", "tier2_findings", "warnings"):
                finding = _first_string(runner.get(key))
                if finding:
                    return f"[{runner_name}] {finding}"
    claim_to_evidence = summary.get("claim_to_evidence")
    if isinstance(claim_to_evidence, dict):
        blocking_gaps = claim_to_evidence.get("blocking_gaps")
        if isinstance(blocking_gaps, list) and blocking_gaps:
            first_gap = blocking_gaps[0]
            if isinstance(first_gap, dict):
                return str(first_gap.get("type") or first_gap.get("claim_id") or "claim_to_evidence_gap")
            return str(first_gap)
    return "none"


def _macro_behavior_pattern(case_type: str, run_outcome: str, eval_finding: str) -> str:
    finding_slug = _safe_slug(eval_finding.lower())[:80] if eval_finding != "none" else "none"
    return f"{_safe_slug(case_type.lower())}:{run_outcome}:{finding_slug}"


def _macro_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _macro_runner_metric_keys(case: dict) -> set[str]:
    metric_keys: set[str] = set()
    runners = case.get("runners")
    if not isinstance(runners, dict):
        return metric_keys
    for runner in runners.values():
        if not isinstance(runner, dict):
            continue
        metrics = runner.get("metrics")
        if not isinstance(metrics, dict):
            continue
        metric_keys.update(str(key) for key in metrics.keys())
    return metric_keys


def _macro_verifier_types(case: dict) -> list[str]:
    verifier_types: set[str] = set(_macro_string_list(case.get("evidence_surfaces")))
    metric_keys = _macro_runner_metric_keys(case)
    if "trace" in metric_keys:
        verifier_types.add("trace_metrics")
    if "expected_signals" in metric_keys or case.get("expected_signals") is True:
        verifier_types.add("expected_signals")
    if "rubric" in metric_keys:
        verifier_types.add("rubric")
    if _macro_string_list(case.get("hard_gates")):
        verifier_types.add("hard_gates")
    if _macro_string_list(case.get("expected_evidence")):
        verifier_types.add("expected_evidence")
    if case.get("check_evidence") is True:
        verifier_types.add("executed_check_evidence")
    return sorted(verifier_types)


def _macro_verification_strategy(case: dict) -> str:
    verifier_types = set(_macro_verifier_types(case))
    if "executed_check_evidence" in verifier_types:
        return "executed_deterministic"
    if verifier_types & {"deterministic_checks", "expected_signals", "output_schema", "hard_gates"}:
        return "declared_not_executed"
    if case.get("passed") is not None:
        return "acceptance_only"
    return "unknown"


def _macro_baseline_status(case: dict) -> str:
    baseline_type = str(case.get("baseline_type") or "").strip()
    baseline_id = str(case.get("baseline_id") or "").strip()
    if not baseline_type and not baseline_id:
        return "none_declared"
    comparisons = case.get("baseline_comparisons")
    if isinstance(comparisons, dict) and comparisons:
        statuses = {
            str(comparison.get("status") or "")
            for comparison in comparisons.values()
            if isinstance(comparison, dict)
        }
        if "compared" in statuses:
            return "executed_compared"
        if statuses:
            return "declared_unexecuted"
    if case.get("comparison_review_artifact") or case.get("comparison_inputs") or case.get("neutral_baseline_approval"):
        return "declared_with_review_surface"
    return "declared_unverified"


def _macro_summary_paths(repo_root: Path, summaries_glob: str) -> list[Path]:
    return sorted(path for path in repo_root.glob(summaries_glob) if path.is_file())


def _macro_eval_events_from_summary(repo_root: Path, summary_path: Path) -> list[dict]:
    summary = _load_json_file(summary_path)
    cases = summary.get("cases")
    if not isinstance(cases, list):
        return []
    release_manifest_path = summary_path.with_name("release_manifest.json")
    release_manifest = _load_json_file(release_manifest_path) if release_manifest_path.is_file() else {}
    events: list[dict] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            continue
        case_type = _macro_case_type(case)
        run_outcome = _macro_run_outcome(summary, case)
        eval_finding = _macro_eval_finding(summary, case)
        behavior_pattern = _macro_behavior_pattern(case_type, run_outcome, eval_finding)
        verifier_types = _macro_verifier_types(case)
        event = {
            "schema_version": "1.0",
            "source": "ask_evals_macro_report",
            "skill": summary.get("skill") or (summary.get("skill_release") or {}).get("name"),
            "run_id": summary.get("run_id"),
            "generated_at": summary.get("generated_at"),
            "eval_mode": summary.get("eval_mode"),
            "runner_mode": summary.get("runner_mode"),
            "summary_decision": summary.get("decision"),
            "case_id": case.get("id") or f"case-{index}",
            "case_name": case.get("name"),
            "case_type": case_type,
            "run_outcome": run_outcome,
            "eval_finding": eval_finding,
            "behavior_pattern": behavior_pattern,
            "tier1_failed": bool(case.get("tier1_failed")),
            "tier2_failed": bool(case.get("tier2_failed")),
            "blocked": run_outcome == "blocked",
            "baseline_type": case.get("baseline_type"),
            "baseline_id": case.get("baseline_id"),
            "baseline_status": _macro_baseline_status(case),
            "skill_lift": case.get("skill_lift"),
            "is_beneficial": case.get("is_beneficial"),
            "baseline_regression": case.get("baseline_regression"),
            "readiness_state": case.get("readiness_state"),
            "metric_availability": case.get("metric_availability"),
            "check_evidence": bool(case.get("check_evidence")),
            "verification_strategy": _macro_verification_strategy(case),
            "verifier_types": verifier_types,
            "summary_path": _repo_relative_path(repo_root, summary_path),
            "release_manifest_path": _repo_relative_path(repo_root, release_manifest_path) if release_manifest else None,
        }
        events.append(event)
    return events


def _macro_group_counts(events: list[dict], fields: tuple[str, ...]) -> list[dict]:
    counts: dict[tuple[str, ...], int] = {}
    for event in events:
        key = tuple(str(event.get(field) or "unknown") for field in fields)
        counts[key] = counts.get(key, 0) + 1
    rows = [
        {**{field: key[index] for index, field in enumerate(fields)}, "trace_count": count}
        for key, count in counts.items()
    ]
    return sorted(rows, key=lambda row: (-int(row["trace_count"]), tuple(str(row[field]) for field in fields)))


def _macro_group_list_counts(events: list[dict], field: str) -> list[dict]:
    counts: dict[str, int] = {}
    for event in events:
        values = event.get(field)
        if not isinstance(values, list) or not values:
            values = ["none"]
        for value in values:
            key = str(value or "unknown")
            counts[key] = counts.get(key, 0) + 1
    return sorted(
        [{field[:-1] if field.endswith("s") else field: key, "trace_count": count} for key, count in counts.items()],
        key=lambda row: (-int(row["trace_count"]), tuple(str(value) for value in row.values())),
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _write_macro_mdx_report(path: Path, report: dict) -> None:
    report_json = json.dumps(report, indent=2, sort_keys=True)
    lines = [
        "---",
        "title: Skill Macro Eval Report",
        "schema_version: skill-macro-eval-report.mdx.v1",
        f"generated_at: {report['generated_at']}",
        "---",
        "",
        "import {",
        "  MacroEvalArtifacts,",
        "  MacroEvalFlowTable,",
        "  MacroEvalLeaderboard,",
        "  MacroEvalTotals,",
        "} from \"./components/eval-report\";",
        "",
        f"export const macroReport = {report_json};",
        "",
        "# Skill Macro Eval Report",
        "",
        "This deterministic report converts saved skill eval summaries into compact macro-eval events for population-level review.",
        "",
        "## Totals",
        "",
        "<MacroEvalTotals totals={macroReport.totals} />",
        "",
        "## Artifacts",
        "",
        "<MacroEvalArtifacts artifacts={macroReport.artifacts} />",
        "",
        "## Top Behavior Patterns",
        "",
        "<MacroEvalLeaderboard rows={macroReport.groups.by_behavior_pattern} labelField=\"behavior_pattern\" />",
        "",
        "",
        "## Top Findings",
        "",
        "<MacroEvalLeaderboard rows={macroReport.groups.by_eval_finding} labelField=\"eval_finding\" />",
        "",
        "## Case Outcome Finding Flow",
        "",
        "<MacroEvalFlowTable rows={macroReport.groups.by_case_outcome_finding} />",
        "",
        "## Skill Pattern Concentration",
        "",
        "<MacroEvalFlowTable rows={macroReport.groups.by_skill_behavior_pattern} />",
        "",
        "## Boundary",
        "",
        "This is a deterministic evidence export and review dashboard. It does not perform semantic clustering, BERTopic-style topic discovery, or AgentTrace-style root-cause diagnosis.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _copy_macro_mdx_components(repo_root: Path, target_dir: Path) -> Path | None:
    component_source = repo_root / "Infrastructure" / "templates" / "components" / "eval-report.tsx"
    if not component_source.is_file():
        return None
    component_target = target_dir / "components" / "eval-report.tsx"
    component_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(component_source, component_target)
    return component_target


def _append_macro_summary_events(
    result: CallResult,
    events: list[dict],
    repo_root: Path,
    summary_path: Path,
) -> bool:
    try:
        events.extend(_macro_eval_events_from_summary(repo_root, summary_path))
    except EvalArtifactReadError as exc:
        result.status = "error"
        result.data["artifact_errors"] = [{
            "path": _repo_relative_path(repo_root, summary_path),
            "message": str(exc),
        }]
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Macro eval report could not read summary evidence: {exc}",
            fix_suggestion="Repair or replace the malformed summary artifact, then rerun ./bin/ask evals macro-report --json --robot.",
        ))
        return False
    return True


def _macro_eval_totals(summary_paths: list[Path], events: list[dict]) -> dict[str, int]:
    return {
        "summaries_scanned": len(summary_paths),
        "events": len(events),
        "skills": len({event.get("skill") for event in events if event.get("skill")}),
        "behavior_patterns": len({event.get("behavior_pattern") for event in events if event.get("behavior_pattern")}),
    }


def _macro_eval_artifacts(
    repo_root: Path,
    events_path: Path,
    report_path: Path,
    mdx_path: Path,
    components_path: Path | None,
) -> dict[str, str | None]:
    return {
        "events_jsonl": _repo_relative_path(repo_root, events_path),
        "report_json": _repo_relative_path(repo_root, report_path),
        "report_mdx": _repo_relative_path(repo_root, mdx_path),
        "report_components": _repo_relative_path(repo_root, components_path) if components_path else None,
    }


def _macro_eval_groups(events: list[dict]) -> dict[str, list[dict]]:
    return {
        "by_skill": _macro_group_counts(events, ("skill",)),
        "by_case_type": _macro_group_counts(events, ("case_type",)),
        "by_run_outcome": _macro_group_counts(events, ("run_outcome",)),
        "by_eval_finding": _macro_group_counts(events, ("eval_finding",)),
        "by_behavior_pattern": _macro_group_counts(events, ("behavior_pattern",)),
        "by_verification_strategy": _macro_group_counts(events, ("verification_strategy",)),
        "by_baseline_status": _macro_group_counts(events, ("baseline_status",)),
        "by_verifier_type": _macro_group_list_counts(events, "verifier_types"),
        "by_case_outcome_finding": _macro_group_counts(events, ("case_type", "run_outcome", "eval_finding")),
        "by_skill_behavior_pattern": _macro_group_counts(events, ("skill", "behavior_pattern")),
    }


def macro_eval_report(
    repo_root: Path,
    *,
    output_dir: str | None = None,
    summaries_glob: str = DEFAULT_MACRO_EVAL_REPORTS_GLOB,
) -> CallResult:
    """Export deterministic macro-eval events from saved skill eval summaries."""
    result = CallResult()
    result.data["validation_commands"] = [_macro_eval_validation_command(output_dir, summaries_glob)]
    summary_paths = _macro_summary_paths(repo_root, summaries_glob)
    events: list[dict] = []
    for summary_path in summary_paths:
        if not _append_macro_summary_events(result, events, repo_root, summary_path):
            return result

    target_dir = repo_root / (output_dir or "Infrastructure/artifacts/evals/macro")
    events_path = target_dir / "macro-eval-events.jsonl"
    report_path = target_dir / "macro-eval-report.json"
    mdx_path = target_dir / "macro-eval-report.mdx"
    _write_jsonl(events_path, events)
    components_path = _copy_macro_mdx_components(repo_root, target_dir)
    report = {
        "schema_version": "1.0",
        "generated_at": _utc_now_iso(),
        "source": "ask_evals_macro_report",
        "summaries_glob": summaries_glob,
        "totals": _macro_eval_totals(summary_paths, events),
        "artifacts": _macro_eval_artifacts(repo_root, events_path, report_path, mdx_path, components_path),
        "groups": _macro_eval_groups(events),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_macro_mdx_report(mdx_path, report)

    result.status = "success"
    result.data.update(report)
    return result


def _resolve_eval_skill_path(repo_root: Path, path: str) -> str:
    """Resolve generated runtime skill paths back to canonical eval sources."""
    requested = Path(path)
    parts = requested.parts
    if len(parts) >= 3 and parts[0] == ".agents" and parts[1] == "skills":
        handle = parts[2]
        source_roots = [
            repo_root / "Skills",
            repo_root / "Plugins",
            repo_root / "skills-system",
        ]
        for source_root in source_roots:
            if not source_root.is_dir():
                continue
            if source_root.name == "Plugins":
                candidates = source_root.glob(f"*/skills/**/{handle}")
            elif source_root.name == "skills-system":
                candidates = [source_root / handle]
            else:
                candidates = source_root.glob(f"*/{handle}")
            for candidate in sorted(candidates):
                if (candidate / "references" / "evals.yaml").is_file():
                    return candidate.relative_to(repo_root).as_posix()

    if (repo_root / requested / "references" / "evals.yaml").is_file():
        return path

    return path


def _eval_lifecycle_event(
    *,
    event_type: str,
    path: str,
    mode: str,
    runner: str,
    status: str,
    blocker_class: str | None = None,
) -> dict:
    return {
        "schema_version": "capability-lifecycle-event.v1",
        "event_type": event_type,
        "event_definition": _eval_lifecycle_event_types().get(event_type),
        "occurred_at": _utc_now_iso(),
        "subject": {
            "query": path,
            "target_kind": "skill_path",
            "handle": Path(path).name,
            "canonical_source_path": path,
            "eval_mode": mode,
            "runner": runner,
        },
        "outcome": {
            "status": status,
            "blocker_classes": [blocker_class] if blocker_class else [],
            "warning_classes": [],
        },
    }


def _start_eval_lifecycle(result: CallResult, *, path: str, mode: str, runner: str) -> None:
    started = _eval_lifecycle_event(
        event_type="eval_started",
        path=path,
        mode=mode,
        runner=runner,
        status="running",
    )
    result.data["lifecycle_events"] = [started]
    result.data["lifecycle_event"] = started
    result.data["lifecycle_event_types"] = _eval_lifecycle_event_types()


def _finish_eval_lifecycle(
    result: CallResult,
    *,
    path: str,
    mode: str,
    runner: str,
    eval_status: str,
    blocker_class: str | None = None,
) -> None:
    final_event_type = "eval_blocked" if blocker_class else "eval_completed"
    final_event = _eval_lifecycle_event(
        event_type=final_event_type,
        path=path,
        mode=mode,
        runner=runner,
        status=eval_status,
        blocker_class=blocker_class,
    )
    result.data.setdefault("lifecycle_events", []).append(final_event)
    result.data["lifecycle_event"] = final_event

__all__ = [name for name in globals() if not name.startswith("__")]
