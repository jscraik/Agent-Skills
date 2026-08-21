from __future__ import annotations

import html
import json
import re
from typing import Any


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
    grade_acceptable = grade_floor_met
    blocking_fail_count = fail_count
    posture, posture_detail = _plugin_eval_posture(
        fail_count=fail_count,
        warn_count=warn_count,
        grade_acceptable=grade_acceptable,
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
        "posture": posture,
        "posture_detail": posture_detail,
        "findings": findings,
        "status": status or "reported",
    }


def _plugin_eval_posture(*, fail_count: int, warn_count: int, grade_acceptable: bool) -> tuple[str, str]:
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
