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
    grade_acceptable = _grade_rank(grade_text) >= _grade_rank("B+")
    if fail_count:
        posture = "blocking"
        posture_detail = "Plugin Eval has failure-level findings and must block release confidence."
    elif not grade_acceptable:
        posture = "blocking"
        posture_detail = "Plugin Eval is below the B+ local acceptance floor."
    elif warn_count:
        posture = "budget_guardrail"
        posture_detail = (
            "Acceptable as a budget guardrail when local audit and Tessl quality pass; "
            "track warnings as follow-up or prove observed usage."
        )
    else:
        posture = "pass"
        posture_detail = "Plugin Eval meets the local budget and ergonomics guardrail."
    return {
        "score": int(score_raw) if score_raw is not None else 0,
        "grade": grade_text,
        "risk": risk.strip() if isinstance(risk, str) else risk,
        "checks": checks.strip() if isinstance(checks, str) else checks,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "grade_acceptable": grade_acceptable,
        "posture": posture,
        "posture_detail": posture_detail,
        "findings": findings,
        "status": status or "reported",
    }


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
    fallback: list[Path] = []
    target_name = Path(target_identifier).name
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
        elif len(path.parts) >= 3 and path.parts[-3] == target_name:
            fallback.append(path)

    scorecards = sorted(matching or fallback, key=lambda item: item.stat().st_mtime)
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


def _eval_model(repo_root: Path, report: dict[str, Any], target: str) -> dict[str, Any]:
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
    if plugin.get("posture") == "budget_guardrail":
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
        rows.append(
            "<tr>"
            f"<td><strong>{_escape(case.get('name'))}</strong><br><span>{_escape(case.get('category'))}</span></td>"
            f"{baseline_cell}"
            f"<td class=\"score {_status_class(pct)}\">{pct}%</td>"
            f"<td>{_escape('; '.join(_as_list(case.get('notes'))) or case.get('status'))}</td>"
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
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise ValueError("Review report must be a JSON object.")

    data = _as_dict(report.get("data"))
    policy = _as_dict(data.get("policy"))
    review_mode_details = _as_dict(data.get("review_mode_details"))
    target = str(data.get("target") or "unknown-skill")
    skill_name = Path(target).name
    quality_model = _quality_model(report)
    tessl = quality_model["tessl"]
    plugin = quality_model["plugin"]
    evals = _eval_model(repo_root, report, target)
    security = _audit_security_summary(_as_dict(data.get("ask_audit")))
    snyk = _parse_snyk_security(_as_dict(data.get("snyk")))
    base_security_score = 100 if security["critical_count"] == 0 and security["warning_count"] == 0 else 70
    snyk_score = int(snyk.get("score") or 100)
    security_score = min(base_security_score, snyk_score)
    impact_score = int(evals.get("score") or 0)
    impact_badge = ""
    if isinstance(evals.get("trend_ratio"), (int, float)) and evals["trend_ratio"] > 1:
        impact_badge = f"<span class=\"lift\">+ {evals['trend_ratio']}x</span>"
    quality_score = int(quality_model["quality"] or 0)
    overall = round((quality_score + security_score + (impact_score if evals.get("scored_cases") else quality_score)) / 3)
    generated = _escape(data.get("generated_at") or "local report")
    refresh_seconds = 15
    validation_active = bool(data.get("validation_active") or data.get("dashboard_refresh_active"))

    suggestions = tessl.get("suggestions") or plugin.get("findings") or []
    suggestion_html = "".join(f"<li>{_escape(item)}</li>" for item in suggestions[:8]) or "<li>No suggestions reported.</li>"
    plugin_findings_html = "".join(f"<li>{_escape(item)}</li>" for item in plugin.get("findings", [])[:6]) or "<li>No Plugin Eval findings reported.</li>"
    plugin_posture_class = _plugin_posture_class(plugin)
    security_lines = security.get("lines") or []
    security_html = "".join(f"<li>{_escape(item)}</li>" for item in security_lines) or "<li>No local security warnings or errors were reported by the internal audit.</li>"
    snyk_class = _snyk_posture_class(snyk)
    severity = _as_dict(snyk.get("severity_counts"))
    snyk_notes = _as_list(snyk.get("notes"))
    snyk_notes_html = "".join(f"<li>{_escape(item)}</li>" for item in snyk_notes) or "<li>No Snyk notes reported.</li>"
    scorecard_path = evals.get("scorecard_path")
    review_lanes_html = _render_review_mode_details(review_mode_details)
    if scorecard_path:
        scorecard = Path(scorecard_path)
        scorecard_label = scorecard.relative_to(repo_root) if scorecard.is_relative_to(repo_root) else scorecard_path
        scorecard_link = (
            f'<a href="{_evidence_href(scorecard, repo_root=repo_root, output_path=output_path)}">'
            f"Latest Eval Scorecard<br><span>{_escape(scorecard_label)}</span></a>"
        )
    else:
        scorecard_link = "<div>Latest Eval Scorecard<br><span>No scorecard found for this skill.</span></div>"
    if validation_active:
        live_status_html = (
            '<span class="live-status is-active">Validation running - refreshes in '
            f'<span data-refresh-countdown>{refresh_seconds}s</span></span>'
        )
    else:
        live_status_html = '<span class="live-status">Static evidence snapshot</span>'

    document = f"""<!doctype html>
<html lang=\"en\" data-auto-refresh-seconds=\"{refresh_seconds if validation_active else 0}\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{_escape(skill_name)} local skill review</title>
<style>
:root {{ color-scheme: dark; --bg:#090a0c; --panel:#111317; --panel-2:#15181e; --text:#f4f5f7; --muted:#989da7; --line:#242831; --green:#69d47a; --cyan:#57c7e8; --yellow:#e5c84f; --red:#ee6a5f; }}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.55 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif; }}
a {{ color:var(--cyan); text-decoration:none; }}
code {{ background:#20242c; border:1px solid #303641; border-radius:6px; padding:0.12rem 0.35rem; color:#d9dce3; }}
.shell {{ display:grid; grid-template-columns:260px minmax(0,1fr); min-height:100vh; }}
.sidebar {{ border-right:1px solid var(--line); padding:28px 18px; position:sticky; top:0; height:100vh; background:#0b0c0f; }}
.brand {{ font-weight:800; letter-spacing:0; margin-bottom:26px; }}
.nav a {{ display:block; color:var(--muted); padding:10px 12px; border-radius:8px; margin:4px 0; }}
.nav a:hover,.nav a.active {{ color:var(--text); background:var(--panel-2); }}
.main {{ padding:54px 48px 80px; max-width:1480px; }}
.breadcrumb {{ color:var(--muted); font-size:13px; margin-bottom:24px; display:flex; gap:12px; flex-wrap:wrap; align-items:center; }}
.live-status {{ display:inline-flex; align-items:center; gap:6px; border:1px solid #27303a; border-radius:7px; padding:2px 8px; background:#11161c; color:var(--muted); font-weight:800; }}
.live-status.is-active {{ border-color:#24402a; background:#0f1d13; color:var(--green); }}
.hero {{ display:grid; grid-template-columns:130px minmax(280px,1fr) 420px; gap:34px; align-items:center; border-bottom:1px solid var(--line); padding-bottom:36px; }}
.hex {{ width:118px; height:102px; clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%); background:#0f2015; border:1px solid #204d29; display:grid; place-items:center; font-size:34px; font-weight:800; color:var(--green); }}
.lift {{ display:inline-flex; margin-top:10px; border:1px solid #264d30; border-radius:7px; padding:6px 12px; background:#102416; color:var(--green); font-weight:800; }}
.hero h1 {{ font-size:34px; margin:0 0 10px; letter-spacing:0; }}
.hero p {{ color:var(--muted); margin:0; max-width:820px; }}
.metrics {{ display:grid; gap:24px; }}
.metric-head {{ display:flex; justify-content:space-between; gap:18px; font-weight:700; }}
.bar {{ height:5px; background:#22262d; border-radius:99px; overflow:hidden; margin:10px 0 6px; }}
.bar span {{ display:block; height:100%; border-radius:99px; }}
.good {{ color:var(--green); }} .warn {{ color:var(--yellow); }} .bad {{ color:var(--red); }}
.bar .good {{ background:var(--green); }} .bar .warn {{ background:var(--yellow); }} .bar .bad {{ background:var(--red); }}
.metric p,.section-head p {{ color:var(--muted); margin:0; }}
.tabs {{ display:flex; align-items:flex-end; gap:4px; border-bottom:1px solid var(--line); margin:26px 0 42px; overflow-x:auto; }}
.tabs a {{ color:var(--muted); min-width:112px; text-align:center; padding:12px 18px 13px; border:1px solid transparent; border-bottom:0; border-radius:8px 8px 0 0; font-weight:800; position:relative; }}
.tabs a:hover {{ color:var(--text); background:#11141a; border-color:#2b3039; }}
.tabs a:focus-visible {{ outline:2px solid var(--cyan); outline-offset:2px; }}
.tabs a[aria-selected="true"] {{ color:var(--text); background:var(--panel); border-color:var(--line); box-shadow:0 1px 0 var(--panel); }}
.tabs a[aria-selected="true"]::after {{ content:""; position:absolute; left:14px; right:14px; bottom:-1px; height:3px; border-radius:99px 99px 0 0; background:var(--text); }}
section {{ margin:0 0 58px; }}
.tab-panel {{ display:none; }}
.tab-panel.is-active {{ display:block; }}
.section-head {{ display:flex; align-items:center; justify-content:space-between; gap:20px; margin-bottom:22px; }}
h2 {{ font-size:28px; margin:0; letter-spacing:0; }}
h3 {{ font-size:20px; margin:0 0 10px; }}
.grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; }}
.panel {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:20px; }}
.panel strong {{ display:block; font-size:24px; margin-top:8px; }}
.plugin-posture {{ margin-top:18px; display:grid; grid-template-columns:minmax(0,1fr) auto; gap:16px; align-items:start; }}
.plugin-posture ul {{ grid-column:1 / -1; margin:0; padding-left:18px; color:var(--muted); }}
.plugin-score {{ display:flex; align-items:center; gap:12px; }}
.posture-detail {{ grid-column:1 / -1; margin:0; color:var(--muted); }}
.pill {{ display:inline-flex; align-items:center; border-radius:7px; padding:3px 8px; font-weight:800; background:#1b2220; border:1px solid #2d4733; }}
.pill.warn {{ background:#2a2618; border-color:#504721; }} .pill.bad {{ background:#2c1d1b; border-color:#56302b; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ color:var(--muted); font-weight:700; text-align:left; border-bottom:1px solid var(--line); padding:13px 0; }}
td {{ border-bottom:1px solid var(--line); padding:18px 18px 18px 0; vertical-align:top; }}
td span {{ color:var(--muted); }}
.score {{ white-space:nowrap; font-weight:800; }}
.suggestions,.empty-state {{ border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:22px; }}
.suggestions li,.empty-state p {{ color:var(--muted); margin:10px 0; }}
.evidence-list {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
.evidence-list a,.evidence-list div {{ border:1px solid var(--line); border-radius:8px; padding:14px; background:var(--panel); }}
.review-lanes {{ margin-top:24px; }}
.review-lane {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(220px,420px); gap:18px; align-items:start; border:1px solid var(--line); border-radius:8px; background:var(--panel); padding:16px; margin:12px 0; }}
.review-lane h3 {{ margin:0 0 4px; }}
.review-lane p {{ margin:0 0 10px; color:var(--muted); }}
.review-lane code {{ display:block; white-space:normal; overflow-wrap:anywhere; }}
.lane-badge {{ display:inline-flex; margin:0 6px 6px 0; border:1px solid #303641; border-radius:7px; padding:2px 7px; background:#171b22; color:var(--muted); font-size:12px; font-weight:800; }}
@media (max-width: 1100px) {{ .shell {{ grid-template-columns:1fr; }} .sidebar {{ position:relative; height:auto; }} .hero {{ grid-template-columns:1fr; }} .grid,.evidence-list {{ grid-template-columns:1fr; }} .tabs a {{ min-width:104px; }} }}
@media (max-width: 900px) {{ .review-lane {{ grid-template-columns:1fr; }} }}
@media (max-width: 700px) {{ .plugin-posture {{ grid-template-columns:1fr; }} .plugin-score {{ justify-content:flex-start; }} }}
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {{
  const ids = ['quality', 'evals', 'security', 'evidence'];
  const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
  const panels = Array.from(document.querySelectorAll('.tab-panel'));
  function activate(id) {{
    const target = ids.includes(id) ? id : 'quality';
    tabs.forEach((tab) => {{
      const selected = tab.getAttribute('href') === '#' + target;
      tab.setAttribute('aria-selected', selected ? 'true' : 'false');
      tab.setAttribute('tabindex', selected ? '0' : '-1');
    }});
    panels.forEach((panel) => {{
      const selected = panel.id === target;
      panel.classList.toggle('is-active', selected);
      panel.toggleAttribute('hidden', !selected);
    }});
  }}
  activate(window.location.hash.slice(1));
  window.addEventListener('hashchange', () => activate(window.location.hash.slice(1)));
  tabs.forEach((tab, index) => {{
    tab.addEventListener('keydown', (event) => {{
      const delta = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
      if (!delta) return;
      event.preventDefault();
      const next = tabs[(index + delta + tabs.length) % tabs.length];
      next.focus();
      next.click();
    }});
  }});
  const refreshSeconds = Number(document.documentElement.dataset.autoRefreshSeconds || '0');
  const countdown = document.querySelector('[data-refresh-countdown]');
  if (Number.isFinite(refreshSeconds) && refreshSeconds > 0) {{
    let remaining = refreshSeconds;
    const paint = () => {{
      if (countdown) countdown.textContent = remaining + 's';
    }};
    paint();
    window.setInterval(() => {{
      if (document.hidden) return;
      remaining -= 1;
      if (remaining <= 0) {{
        window.location.reload();
        return;
      }}
      paint();
    }}, 1000);
  }}
}});
</script>
</head>
<body>
<div class=\"shell\">
  <aside class=\"sidebar\">
    <div class=\"brand\">ASK Local Review</div>
    <nav class=\"nav\">
      <a class=\"active\" href=\"#overview\">Overview</a>
      <a href=\"#quality\">Quality</a>
      <a href=\"#evals\">Evals</a>
      <a href=\"#security\">Security</a>
      <a href=\"#evidence\">Evidence</a>
    </nav>
  </aside>
  <main class=\"main\">
    <div class=\"breadcrumb\"><span>Local / Skills / {_escape(target)} / review</span>{live_status_html}</div>
    <header id=\"overview\" class=\"hero\">
      <div><div class=\"hex\">{overall}</div>{impact_badge}</div>
      <div>
        <h1>{_escape(skill_name)}</h1>
        <p>Local-only external review dashboard. Tessl, Plugin Eval, internal audits, optional Snyk advisory data, and available skill eval scorecards are rendered together without publishing or uploading skill content by default.</p>
      </div>
      <div class=\"metrics\">
        {_render_bar('Quality', quality_score, 'Best-practice fit from Tessl plus internal review signals.')}
        {_render_bar('Impact', impact_score, evals.get('message') if evals.get('available') else 'No scenario eval scorecard found yet.')}
        {_render_bar('Security', security_score, 'Internal audit, OpenClaw, and optional Snyk CLI advisory summary.')}
      </div>
    </header>
    <nav class=\"tabs\" role=\"tablist\" aria-label=\"Review result sections\">
      <a id=\"tab-quality\" role=\"tab\" aria-selected=\"true\" aria-controls=\"quality\" tabindex=\"0\" href=\"#quality\">Quality</a><a id=\"tab-evals\" role=\"tab\" aria-selected=\"false\" aria-controls=\"evals\" tabindex=\"-1\" href=\"#evals\">Evals</a><a id=\"tab-security\" role=\"tab\" aria-selected=\"false\" aria-controls=\"security\" tabindex=\"-1\" href=\"#security\">Security</a><a id=\"tab-evidence\" role=\"tab\" aria-selected=\"false\" aria-controls=\"evidence\" tabindex=\"-1\" href=\"#evidence\">Evidence</a>
    </nav>

    <section id=\"quality\" class=\"tab-panel is-active\" role=\"tabpanel\" aria-labelledby=\"tab-quality\">
      <div class=\"section-head\"><div><h2>Quality</h2><p>Discovery, implementation, validation, and internal evaluator agreement.</p></div><span class=\"pill {_status_class(quality_score)}\">{quality_score}%</span></div>
      <div class=\"grid\">
        <div class=\"panel\"><h3>Discovery</h3><p>Description activation quality</p><strong class=\"{_status_class(tessl['description_score'])}\">{tessl['description_score']}%</strong></div>
        <div class=\"panel\"><h3>Implementation</h3><p>Instruction clarity and actionability</p><strong class=\"{_status_class(tessl['content_score'])}\">{tessl['content_score']}%</strong></div>
        <div class=\"panel\"><h3>Validation</h3><p>Format and structure checks</p><strong class=\"{_status_class(tessl['validation_score'])}\">{tessl['validation_score']}%</strong></div>
      </div>
      <div class=\"panel plugin-posture\">
        <div>
          <h3>Plugin Eval</h3>
          <p>Budget and Codex ergonomics guardrail. Local policy accepts <code>B+</code> or better when there are no failure-level findings and local/Tessl gates pass.</p>
        </div>
        <div class=\"plugin-score\"><span class=\"pill {plugin_posture_class}\">{_escape(plugin.get('grade') or 'Not reported')}</span><strong class=\"{_status_class(int(plugin.get('score') or 0))}\">{int(plugin.get('score') or 0)}%</strong></div>
        <p class=\"posture-detail {_escape(plugin_posture_class)}\">{_escape(plugin.get('posture_detail'))}</p>
        <ul>{plugin_findings_html}</ul>
      </div>
      <table>
        <thead><tr><th>Dimension</th><th>Reasoning</th><th>Score</th></tr></thead>
        <tbody>{_render_dimension_rows(tessl['dimensions'])}</tbody>
      </table>
      <div class=\"suggestions\"><h3>Suggestions</h3><ul>{suggestion_html}</ul></div>
    </section>

    <section id=\"evals\" class=\"tab-panel\" role=\"tabpanel\" aria-labelledby=\"tab-evals\" hidden>
      {_render_eval_cases(evals)}
    </section>

    <section id=\"security\" class=\"tab-panel\" role=\"tabpanel\" aria-labelledby=\"tab-security\" hidden>
      <div class=\"section-head\"><div><h2>Security</h2><p>Local security-review result, kept separate from quality so warnings cannot hide.</p></div><span class=\"pill {_status_class(security_score)}\">{security_score}%</span></div>
      <div class=\"suggestions\"><h3>Findings</h3><ul>{security_html}</ul></div>
      <div class=\"panel plugin-posture\">
        <div>
          <h3>Snyk Advisory</h3>
          <p>Optional CLI-backed external security signal. It stays disabled unless the review is run with <code>--include-snyk</code>.</p>
        </div>
        <div class=\"plugin-score\"><span class=\"pill {snyk_class}\">{_escape(snyk.get('status'))}</span><strong class=\"{_status_class(snyk_score)}\">{snyk_score}%</strong></div>
        <p class=\"posture-detail {_escape(snyk_class)}\">{_escape(snyk.get('headline'))}</p>
        <ul>
          <li>Projects scanned: {_escape(snyk.get('project_count'))}; vulnerabilities: {_escape(snyk.get('vulnerability_count'))}</li>
          <li>Critical: {_escape(severity.get('critical', 0))}; High: {_escape(severity.get('high', 0))}; Medium: {_escape(severity.get('medium', 0))}; Low: {_escape(severity.get('low', 0))}</li>
          {snyk_notes_html}
        </ul>
      </div>
    </section>

    <section id=\"evidence\" class=\"tab-panel\" role=\"tabpanel\" aria-labelledby=\"tab-evidence\" hidden>
      <div class=\"section-head\"><div><h2>Evidence</h2><p>Generated from local files. These links are archive pointers, not registry uploads.</p></div></div>
      <div class=\"evidence-list\">
        <a href=\"{_evidence_href(report_path, repo_root=repo_root, output_path=output_path)}\">Review JSON<br><span>{_escape(report_path.relative_to(repo_root) if report_path.is_relative_to(repo_root) else report_path)}</span></a>
        {scorecard_link}
        <div>Policy<br><span>{_escape(policy.get('mode') or 'local_internal_only')}; primary gate: {_escape(policy.get('primary_gate') or 'local_eval_ask_audit')}; Plugin Eval floor: {_escape(policy.get('plugin_eval_min_acceptable_grade') or 'B')}; Snyk: {_escape(policy.get('snyk_default') or 'disabled_until_explicit_confirmation')}</span></div>
        <div>Generated<br><span>{generated}</span></div>
      </div>
      {review_lanes_html}
    </section>
  </main>
</div>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = "\n".join(line.rstrip() for line in document.splitlines()) + "\n"
    output_path.write_text(document, encoding="utf-8")
    return output_path
