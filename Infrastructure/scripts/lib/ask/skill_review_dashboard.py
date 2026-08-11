from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_BUILDER_SCRIPT_DIR = REPO_ROOT / "Plugins" / "skill-factory" / "scripts" / "skill-builder"
if str(SKILL_BUILDER_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_BUILDER_SCRIPT_DIR))

from eval_signal_contract import (  # noqa: E402
    EXPECTED_SIGNAL_COMPOSITE_KEY,
    EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY,
    EXPECTED_SIGNAL_METRIC_KEY,
    EXPECTED_SIGNAL_MISSING_KEY,
    EXPECTED_SIGNAL_RISK_FACTORS_KEY,
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _percent(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return max(0, min(100, round(float(value))))
    if isinstance(value, str):
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", value)
        if match:
            return max(0, min(100, round(float(match.group(1)))))
        try:
            return max(0, min(100, round(float(value.strip()))))
        except ValueError:
            return default
    return default


def _escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _evidence_href(path: Path, *, repo_root: Path, output_path: Path) -> str:
    base = output_path.parent.resolve()
    target = path if path.is_absolute() else repo_root / path
    resolved = target.resolve()
    try:
        return Path(os.path.relpath(resolved, base)).as_posix()
    except ValueError:
        try:
            return resolved.relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return resolved.as_posix() if resolved.is_absolute() else target.as_posix()


def _status_class(percent: int) -> str:
    if percent >= 90:
        return "good"
    if percent >= 70:
        return "warn"
    return "bad"


def _first_match(pattern: str, text: str, default: Any = None) -> Any:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if not match:
        return default
    return match.group(1)


def _grade_rank(grade: Any) -> int:
    raw = str(grade or "").strip().upper()
    ranks = {
        "A+": 12,
        "A": 11,
        "A-": 10,
        "B+": 9,
        "B": 8,
        "B-": 7,
        "C+": 6,
        "C": 5,
        "C-": 4,
        "D": 3,
        "F": 0,
    }
    match = re.match(r"([A-F][+-]?)\b", raw)
    return ranks.get(match.group(1), -1) if match else -1


def _parse_tessl_review(stdout: str, status: str = "") -> dict[str, Any]:
    if status in {"not_run", "skipped"}:
        return {
            "review_score": 0,
            "description_score": 0,
            "content_score": 0,
            "validation_score": 0,
            "dimensions": [],
            "suggestions": [stdout.strip() or "Tessl review was not run for this report."],
            "status": status,
        }

    review_score = _percent(_first_match(r"Review Score:\s*(\d+(?:\.\d+)?)%", stdout, 0))
    description = _percent(_first_match(r"Description:\s*(\d+(?:\.\d+)?)%", stdout, 0))
    content = _percent(_first_match(r"Content:\s*(\d+(?:\.\d+)?)%", stdout, 0))
    validation = 100 if re.search(r"Overall:\s*PASSED\s*\(0 errors,\s*0 warnings\)", stdout, re.I) else 0
    if not validation and "Overall: PASSED" in stdout:
        validation = 80

    dimensions: list[dict[str, Any]] = []
    for match in re.finditer(r"^\s{2,}([a-z_]+):\s*(\d+)\s*/\s*(\d+)\s*-\s*(.+)$", stdout, re.MULTILINE):
        dimensions.append({
            "name": match.group(1).replace("_", " ").title(),
            "score": int(match.group(2)),
            "max": int(match.group(3)),
            "reasoning": match.group(4).strip(),
        })

    suggestions: list[str] = []
    in_suggestions = False
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped == "Suggestions:":
            in_suggestions = True
            continue
        if in_suggestions and stripped.startswith("-"):
            suggestions.append(stripped[1:].strip())
            continue
        if in_suggestions and stripped and not stripped.startswith("-") and not line.startswith("      "):
            in_suggestions = False

    return {
        "review_score": review_score,
        "description_score": description,
        "content_score": content,
        "validation_score": validation,
        "dimensions": dimensions,
        "suggestions": suggestions,
        "status": status or "reported",
    }


def _parse_plugin_eval(stdout: str, status: str = "") -> dict[str, Any]:
    if status in {"not_run", "skipped"}:
        return {
            "score": 0,
            "grade": status.replace("_", " "),
            "risk": status.replace("_", " "),
            "checks": status.replace("_", " "),
            "fail_count": 0,
            "warn_count": 0,
            "posture": "skipped",
            "posture_detail": stdout.strip() or "Plugin Eval was not run for this report.",
            "findings": [],
            "status": status,
        }

    score_raw = _first_match(r"Score:\s*(\d+)\s*/\s*100", stdout, None)
    grade = _first_match(r"Grade:\s*([^\n]+)", stdout, "Not reported")
    risk = _first_match(r"Risk:\s*([^\n]+)", stdout, "Not reported")
    checks = _first_match(r"Checks:\s*([^\n]+)", stdout, "Not reported")
    findings = [line.strip("- ") for line in stdout.splitlines() if line.strip().startswith("- ")][:8]
    fail_count = int(_first_match(r"(\d+)\s+fail", str(checks), 0) or 0)
    warn_count = int(_first_match(r"(\d+)\s+warn", str(checks), 0) or 0)
    grade_text = grade.strip() if isinstance(grade, str) else grade
    score_value = int(score_raw) if score_raw is not None else 0
    grade_floor_met = _grade_rank(grade_text) >= _grade_rank("B+")
    active_budget_acceptable = bool(re.search(r"Active budget:\s*\d+\s+tokens\s+\((good|moderate)\)", stdout))
    deferred_budget_only = fail_count == 1 and _has_deferred_budget_failure(stdout) and active_budget_acceptable
    deferred_budget_waived = deferred_budget_only and score_value >= 85
    grade_acceptable = grade_floor_met or deferred_budget_waived
    blocking_fail_count = 0 if deferred_budget_waived else fail_count
    posture, posture_detail = _plugin_eval_posture(
        fail_count=fail_count,
        warn_count=warn_count,
        grade_acceptable=grade_acceptable,
        deferred_budget_only=deferred_budget_waived,
    )
    return {
        "score": score_value,
        "grade": grade_text,
        "risk": risk.strip() if isinstance(risk, str) else risk,
        "checks": checks.strip() if isinstance(checks, str) else checks,
        "fail_count": fail_count,
        "blocking_fail_count": blocking_fail_count,
        "warn_count": warn_count,
        "grade_acceptable": grade_acceptable,
        "grade_floor_met": grade_floor_met,
        "deferred_budget_waived": deferred_budget_waived,
        "posture": posture,
        "posture_detail": posture_detail,
        "findings": findings,
        "status": status or "reported",
    }


def _plugin_eval_posture(*, fail_count: int, warn_count: int, grade_acceptable: bool, deferred_budget_only: bool) -> tuple[str, str]:
    if deferred_budget_only:
        return (
            "deferred_budget_guardrail",
            "Plugin Eval reported deferred reference budget pressure, but active budget is acceptable. "
            "Accept as a follow-up guardrail when local audit and Tessl quality pass.",
        )
    if fail_count:
        return "blocking", "Plugin Eval has failure-level findings and must block release confidence."
    if not grade_acceptable:
        return "blocking", "Plugin Eval is below the B+ local acceptance floor."
    if warn_count:
        return (
            "budget_guardrail",
            "Acceptable as a budget guardrail when local audit and Tessl quality pass; "
            "track warnings as follow-up or prove observed usage.",
        )
    return "pass", "Plugin Eval meets the local budget and ergonomics guardrail."


def _has_deferred_budget_failure(stdout: str) -> bool:
    return any(
        re.search(r"\[FAIL\]\s+deferred_cost_tokens-budget-high\b", line, flags=re.IGNORECASE)
        for line in stdout.splitlines()
    )


def _audit_security_summary(audit_data: dict[str, Any]) -> dict[str, Any]:
    data = _as_dict(_as_dict(audit_data).get("data"))
    openclaw = _as_dict(data.get("openclaw_guard") or data.get("openclaw"))
    stdout = str(openclaw.get("stdout") or "")
    warn_count = 0
    critical_count = 0
    warning_lines: list[str] = []
    for line in stdout.splitlines():
        lower = line.lower()
        if "warning" in lower or "warn" in lower:
            warning_lines.append(line.strip())
        if "critical" in lower:
            critical_count += 1
        if "warn" in lower:
            warn_count += 1
    summary_match = re.search(r"Summary:\s*(\d+)\s+critical\b[^\n]*?(\d+)\s+warn", stdout, re.IGNORECASE)
    if summary_match:
        critical_count = int(summary_match.group(1))
        warn_count = int(summary_match.group(2))
    if "0 critical" in stdout.lower():
        critical_count = 0
    if "0 warn" in stdout.lower() or "0 warnings" in stdout.lower():
        warn_count = 0
    return {
        "critical_count": critical_count,
        "warning_count": warn_count,
        "lines": warning_lines[:8],
        "status": openclaw.get("status") or "not_reported",
    }


def _parse_snyk_security(snyk_data: dict[str, Any]) -> dict[str, Any]:
    status = str(snyk_data.get("status") or "not_reported")
    stdout = str(snyk_data.get("stdout") or "")
    stderr = str(snyk_data.get("stderr") or "")
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    project_count = 0
    vuln_count = 0
    notes: list[str] = []

    def visit_report(report: Any) -> None:
        nonlocal project_count, vuln_count
        if not isinstance(report, dict):
            return
        project_count += 1
        vulns = report.get("vulnerabilities")
        if isinstance(vulns, list):
            vuln_count += len(vulns)
            for vuln in vulns:
                if not isinstance(vuln, dict):
                    continue
                severity = str(vuln.get("severity") or "").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
        summary = report.get("summary")
        if isinstance(summary, str) and summary:
            notes.append(summary)
        error = report.get("error") or report.get("message")
        if isinstance(error, str) and error:
            notes.append(error)

    if stdout.strip():
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            notes.append(stdout.strip().splitlines()[0][:220])
        else:
            if isinstance(parsed, list):
                for item in parsed:
                    visit_report(item)
            else:
                visit_report(parsed)
    if stderr.strip():
        notes.append(stderr.strip().splitlines()[0][:220])

    if status == "skipped":
        posture = "skipped"
        score = 100
        headline = "Snyk advisory not requested"
    elif status == "not_applicable":
        posture = "skipped"
        score = 100
        headline = "Snyk found no supported project files in this skill folder"
    elif status.startswith("blocked"):
        posture = "blocked"
        score = 70
        headline = "Snyk advisory blocked"
    elif status == "timeout":
        posture = "blocked"
        score = 70
        headline = "Snyk advisory timed out"
    elif severity_counts["critical"] or severity_counts["high"]:
        posture = "advisory"
        score = 45
        headline = "Snyk reported high-severity security advisories"
    elif severity_counts["medium"] or severity_counts["low"] or status == "advisory":
        posture = "advisory"
        score = 70
        headline = "Snyk reported security advisories"
    else:
        posture = "pass"
        score = 100
        headline = "Snyk advisory clean"

    reason = snyk_data.get("reason")
    if isinstance(reason, str) and reason:
        notes.insert(0, reason)

    return {
        "status": status,
        "posture": posture,
        "score": score,
        "headline": headline,
        "project_count": project_count,
        "vulnerability_count": vuln_count,
        "severity_counts": severity_counts,
        "notes": notes[:8],
    }


def _case_runner_status(case: dict[str, Any]) -> tuple[int, str, list[str]]:
    if case.get("blocked") is True:
        blocked_reasons = [str(item) for item in _as_list(case.get("blocked_reasons"))]
        if not blocked_reasons:
            blocked_reasons = [str(item) for item in _as_list(case.get("warnings"))]
        return 0, "blocked", blocked_reasons[:4]
    if case.get("passed") is True:
        return 100, "passed", []
    failures = [str(item) for item in _as_list(case.get("tier1_failures"))]
    warnings = [str(item) for item in _as_list(case.get("warnings"))]
    if failures:
        return 0, "failed", failures[:4]
    if warnings:
        return 70, "warning", warnings[:4]
    return 0, "not passed", []


def _case_expected_signal_notes(case: dict[str, Any]) -> tuple[int | None, list[str]]:
    scores: list[int] = []
    notes: list[str] = []
    for runner in _as_dict(case.get("runners")).values():
        if not isinstance(runner, dict):
            continue
        expected = _as_dict(_as_dict(runner.get("metrics")).get(EXPECTED_SIGNAL_METRIC_KEY))
        score = expected.get(EXPECTED_SIGNAL_COMPOSITE_KEY)
        if isinstance(score, int):
            scores.append(score)
        notes.extend(str(item) for item in _as_list(expected.get(EXPECTED_SIGNAL_RISK_FACTORS_KEY)))
        missing = _as_list(expected.get(EXPECTED_SIGNAL_MISSING_KEY))
        forbidden = _as_list(expected.get(EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY))
        if missing:
            notes.append(f"missing signals: {len(missing)}")
        if forbidden:
            notes.append(f"forbidden signals: {len(forbidden)}")
    if not scores:
        return None, []
    return round(sum(scores) / len(scores)), notes[:4]


def _scorecard_percent(scorecard: dict[str, Any]) -> int:
    cases = [
        case
        for case in _as_list(scorecard.get("cases"))
        if isinstance(case, dict) and case.get("blocked") is not True
    ]
    if not cases:
        return 0
    passed = sum(1 for case in cases if case.get("passed") is True)
    return round((passed / len(cases)) * 100)


def _canonical_target_identifier(target: str, repo_root: Path | None = None) -> str:
    path = Path(target)
    if path.name == "SKILL.md":
        path = path.parent
    root = repo_root.resolve() if repo_root else Path.cwd().resolve()
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(root)
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def _latest_scorecard(repo_root: Path, target_identifier: str) -> tuple[dict[str, Any] | None, list[Path]]:
    root = repo_root / "Infrastructure" / "artifacts" / "skills"
    if not root.exists():
        return None, []

    matching: list[Path] = []
    for path in root.glob("*/**/scorecard.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        skill_path = str(payload.get("skill_path") or "").strip()
        if skill_path and _canonical_target_identifier(skill_path, repo_root) == target_identifier:
            matching.append(path)

    scorecards = sorted(matching, key=lambda item: item.stat().st_mtime)
    if not scorecards:
        return None, []

    path = scorecards[-1]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, scorecards
    if not isinstance(payload, dict):
        return None, scorecards
    payload["_path"] = path
    return payload, scorecards


def _eval_model(repo_root: Path, target: str) -> dict[str, Any]:
    target_identifier = _canonical_target_identifier(target, repo_root)
    scorecard, scorecards = _latest_scorecard(repo_root, target_identifier)
    if not scorecard:
        return {
            "available": False,
            "score": 0,
            "message": "No skill eval scorecard found for this skill yet.",
            "cases": [],
            "scorecard_path": None,
        }
    cases = []
    passed = 0
    blocked = 0
    for case in _as_list(scorecard.get("cases")):
        if not isinstance(case, dict):
            continue
        score, status, notes = _case_runner_status(case)
        signal_score, signal_notes = _case_expected_signal_notes(case)
        if isinstance(signal_score, int):
            notes.append(f"expected signals: {signal_score}%")
        notes.extend(signal_notes)
        if status == "blocked":
            blocked += 1
        elif score == 100:
            passed += 1
        cases.append({
            "id": case.get("id") or "case",
            "name": case.get("name") or case.get("id") or "Unnamed case",
            "category": case.get("category") or "uncategorized",
            "score": score,
            "baseline_score": None,
            "status": status,
            "notes": notes,
            "riteway": case.get("riteway") if isinstance(case.get("riteway"), dict) else None,
            "agent_eval_artifacts": (
                case.get("agent_eval_artifacts")
                if isinstance(case.get("agent_eval_artifacts"), dict)
                else None
            ),
            "pass_rate_policy": (
                case.get("pass_rate_policy")
                if isinstance(case.get("pass_rate_policy"), dict)
                else None
            ),
            "expected_signal_score": signal_score,
            "runner_mode": scorecard.get("runner_mode") or "unknown",
        })
    total = len(cases)
    scored_total = max(total - blocked, 0)
    score = round((passed / scored_total) * 100) if scored_total else 0
    previous_score = None
    trend_ratio = None
    if len(scorecards) >= 2:
        try:
            previous_obj = json.loads(scorecards[-2].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous_obj = {}
        if isinstance(previous_obj, dict):
            previous_score = _scorecard_percent(previous_obj)
            if previous_score > 0:
                trend_ratio = round(score / previous_score, 2)
    return {
        "available": bool(total),
        "score": score,
        "scored_cases": scored_total,
        "blocked_cases": blocked,
        "message": (
            f"{passed}/{total} latest eval cases passed; {blocked} blocked by runner environment; "
            f"{scored_total} scored."
            if blocked
            else (f"{passed}/{total} latest eval cases passed." if total else "Latest scorecard had no cases.")
        ),
        "cases": cases,
        "scorecard_path": str(scorecard.get("_path")) if scorecard.get("_path") else None,
        "run_id": scorecard.get("run_id"),
        "eval_mode": scorecard.get("eval_mode"),
        "previous_score": previous_score,
        "trend_ratio": trend_ratio,
        "expected_signal_summary": scorecard.get("expected_signal_summary"),
    }


def _quality_model(report: dict[str, Any]) -> dict[str, Any]:
    data = _as_dict(report.get("data"))
    tessl_data = _as_dict(data.get("tessl_review"))
    plugin_data = _as_dict(data.get("plugin_eval"))
    tessl = _parse_tessl_review(
        str(tessl_data.get("stdout") or ""),
        str(tessl_data.get("status") or ""),
    )
    plugin = _parse_plugin_eval(
        str(plugin_data.get("stdout") or ""),
        str(plugin_data.get("status") or ""),
    )
    quality = tessl["review_score"] or round((tessl["description_score"] + tessl["content_score"] + tessl["validation_score"]) / 3)
    if not quality:
        quality = plugin["score"]
    return {"quality": quality, "tessl": tessl, "plugin": plugin}


def _render_bar(label: str, percent: int, detail: str = "") -> str:
    klass = _status_class(percent)
    return f"""
      <div class=\"metric\">
        <div class=\"metric-head\"><span>{_escape(label)}</span><strong class=\"{klass}\">{percent}%</strong></div>
        <div class=\"bar\"><span class=\"{klass}\" style=\"width:{percent}%\"></span></div>
        <p>{_escape(detail)}</p>
      </div>
    """


def _render_dimension_rows(dimensions: list[dict[str, Any]]) -> str:
    if not dimensions:
        return "<tr><td colspan=\"3\">No dimension detail was reported.</td></tr>"
    rows = []
    for item in dimensions:
        score = int(item.get("score") or 0)
        max_score = int(item.get("max") or 0)
        pct = round((score / max_score) * 100) if max_score else 0
        rows.append(
            "<tr>"
            f"<td>{_escape(item.get('name'))}</td>"
            f"<td>{_escape(item.get('reasoning'))}</td>"
            f"<td class=\"score {_status_class(pct)}\">{score} / {max_score}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _plugin_posture_class(plugin: dict[str, Any]) -> str:
    if plugin.get("posture") == "blocking":
        return "bad"
    if plugin.get("posture") in {"budget_guardrail", "deferred_budget_guardrail"}:
        return "warn"
    return "good"


def _snyk_posture_class(snyk: dict[str, Any]) -> str:
    if snyk.get("posture") in {"pass", "skipped"}:
        return "good"
    if snyk.get("posture") == "blocked":
        return "warn"
    return "bad"


def _render_eval_cases(evals: dict[str, Any]) -> str:
    if not evals.get("available"):
        return f"""
        <section class=\"empty-state\">
          <h2>Evals Not Run Yet</h2>
          <p>{_escape(evals.get('message'))}</p>
          <p>Run <code>./bin/ask evals run &lt;skill-path&gt; --mode smoke</code>, then rerun the dashboard to see scenario-level behavior.</p>
        </section>
        """
    rows = []
    for case in _as_list(evals.get("cases")):
        pct = int(case.get("score") or 0)
        baseline = case.get("baseline_score")
        status = str(case.get("status") or "")
        baseline_cell = (
            f"<td class=\"score {_status_class(int(baseline))}\">{int(baseline)}%</td>"
            if isinstance(baseline, int)
            else "<td><span>Blocked</span></td>"
            if status == "blocked"
            else "<td><span>Passed</span></td>"
            if status == "passed"
            else "<td><span>Not run</span></td>"
        )
        riteway = case.get("riteway") if isinstance(case.get("riteway"), dict) else {}
        riteway_lines = []
        for label, key in (
            ("unit", "unit"),
            ("given", "given"),
            ("should", "should"),
            ("actual", "actual"),
            ("expected", "expected"),
            ("reproduce", "reproduce"),
        ):
            value = riteway.get(key)
            if value:
                riteway_lines.append(f"{label}: {value}")
        evidence_notes = "; ".join(str(item) for item in _as_list(case.get("notes"))) or case.get("status")
        if riteway_lines:
            evidence_notes = f"{evidence_notes}\n" + "\n".join(riteway_lines)
        rows.append(
            "<tr>"
            f"<td><strong>{_escape(case.get('name'))}</strong><br><span>{_escape(case.get('category'))}</span></td>"
            f"{baseline_cell}"
            f"<td class=\"score {_status_class(pct)}\">{pct}%</td>"
            f"<td>{_escape(evidence_notes).replace(chr(10), '<br>')}</td>"
            "</tr>"
        )
    return f"""
      <section>
        <div class=\"section-head\">
          <div><h2>Evaluation Results</h2><p>{_escape(evals.get('message'))}</p></div>
          <span class=\"pill {_status_class(int(evals.get('score') or 0))}\">{int(evals.get('score') or 0)}%</span>
        </div>
        <table>
          <thead><tr><th>Scenario</th><th>Runner Status</th><th>Score</th><th>Evidence</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </section>
    """


def _render_review_mode_details(details: dict[str, Any]) -> str:
    lanes = [
        ("local_evals", "Local Evals"),
        ("plugin_eval", "Plugin Eval"),
        ("tessl_lint", "Tessl Lint"),
        ("tessl_review", "Tessl Review"),
        ("snyk", "Snyk"),
    ]
    rows: list[str] = []
    for key, label in lanes:
        lane = _as_dict(details.get(key))
        if not lane:
            continue
        role = lane.get("role") or "Not described in this report."
        command = lane.get("command") or "not recorded"
        badges = []
        for field in ("status", "default", "release_required", "canonical_source_shape"):
            value = lane.get(field)
            if value:
                badges.append(f"{field.replace('_', ' ')}: {_escape(value)}")
        badge_html = "".join(f"<span class=\"lane-badge\">{badge}</span>" for badge in badges)
        rows.append(
            "<div class=\"review-lane\">"
            f"<div><h3>{_escape(label)}</h3><p>{_escape(role)}</p>{badge_html}</div>"
            f"<code>{_escape(command)}</code>"
            "</div>"
        )
    if not rows:
        return ""
    return (
        "<div class=\"review-lanes\">"
        "<div class=\"section-head\"><div><h2>Review Lanes</h2>"
        "<p>How this local dashboard separates behavior checks, static guardrails, Tessl review, and optional security screening.</p>"
        "</div></div>"
        f"{''.join(rows)}"
        "</div>"
    )



def render_skill_review_dashboard(report_path: Path, output_path: Path, repo_root: Path) -> Path:
    """Render a dashboard without creating a facade/renderer import cycle."""
    from .skill_review_dashboard_render import render_skill_review_dashboard as render

    return render(report_path=report_path, output_path=output_path, repo_root=repo_root)
