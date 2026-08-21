"""Canonical catalog parity diagnostics shared across ask command surfaces."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from statistics import median
from typing import Any

from skill_discovery import discover_catalog_entries, get_policy_identity


CATALOG_PARITY_SCHEMA_VERSION = "catalog-parity.v1"
REQUIRED_SURFACES = (
    "README.md",
    "SKILL.md",
    "ask skills list",
    "route considered metadata",
)
HISTORY_PATH = Path(".tmp/agent-skills-artifacts/selection-quality/history.jsonl")


def _extract_readme_count(readme_path: Path) -> int | None:
    """
    Extract the bolded skills count from a README file.

    Recognizes formats like **123 skills** or **123 canonical skills** and returns the parsed integer when present; if the file is missing or no matching pattern is found, returns None.

    Returns:
        int | None: The parsed skills count if present, `None` otherwise.
    """
    if not readme_path.exists():
        return None
    content = readme_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"\*\*(\d+)(?:\s+canonical)?\s+skills\*\*", content)
    if not match:
        return None
    return int(match.group(1))


def _extract_root_skill_index_count(index_path: Path) -> int | None:
    """
    Extract the `total_skills` value declared in a root skill index file.

    Parameters:
        index_path (Path): Path to the root SKILL.md index file to read.

    Returns:
        int | None: The parsed `total_skills` integer if present in the file, otherwise `None`.
    """
    if not index_path.exists():
        return None
    content = index_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"-\s+`total_skills`:\s*(\d+)", content)
    if not match:
        return None
    return int(match.group(1))


def _extract_root_skill_index_policy_identity(index_path: Path) -> str | None:
    """
    Extract the 16-hex-character policy identity from a root skill index file.

    Parameters:
        index_path (Path): Path to the root skill index file (e.g. SKILL.md).

    Returns:
        str | None: The matched 16-character lowercase hexadecimal policy identity if present, otherwise `None` (including when the file does not exist or the identity cannot be found).
    """
    if not index_path.exists():
        return None
    content = index_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"-\s+`policy_identity`:\s*([a-f0-9]{16})", content)
    if not match:
        return None
    return match.group(1)


def _history_counts(payload: dict[str, Any]) -> tuple[tuple[float, float, float] | None, str | None]:
    totals = payload.get("totals")
    status_counts = payload.get("status_counts")
    if not isinstance(totals, dict) or not isinstance(status_counts, dict):
        return None, "schema_invalid_history"
    if "fixtures" not in totals or not {"unresolved_ambiguity", "degraded_no_candidates"}.issubset(status_counts):
        return None, "schema_invalid_history"
    try:
        fixtures = float(totals.get("fixtures", 0) or 0)
        unresolved = float(status_counts.get("unresolved_ambiguity", 0) or 0)
        no_candidate = float(status_counts.get("degraded_no_candidates", 0) or 0)
    except (TypeError, ValueError):
        return None, "schema_invalid_history"
    if not all(math.isfinite(value) for value in (fixtures, unresolved, no_candidate)):
        return None, "schema_invalid_history"
    return (fixtures, unresolved, no_candidate), None


def _nested_history_rates(payload: dict[str, Any]) -> tuple[dict[str, float] | None, str | None]:
    counts, issue = _history_counts(payload)
    if issue or counts is None:
        return None, issue
    fixtures, unresolved, no_candidate = counts
    if fixtures <= 0:
        return None, None
    if unresolved < 0 or no_candidate < 0 or unresolved > fixtures or no_candidate > fixtures:
        return None, "schema_invalid_history"
    return {
        "unresolved_ambiguity_rate": unresolved / fixtures,
        "no_candidate_rate": no_candidate / fixtures,
    }, None


def _history_rates(payload: dict[str, Any]) -> tuple[dict[str, float] | None, str | None]:
    unresolved = payload.get("unresolved_ambiguity_rate")
    no_candidate = payload.get("no_candidate_rate")
    if unresolved is None or no_candidate is None:
        return _nested_history_rates(payload)
    try:
        rates = {
            "unresolved_ambiguity_rate": float(unresolved),
            "no_candidate_rate": float(no_candidate),
        }
    except (TypeError, ValueError):
        return None, "schema_invalid_history"
    if not all(math.isfinite(value) for value in rates.values()):
        return None, "schema_invalid_history"
    if not all(0 <= value <= 1 for value in rates.values()):
        return None, "schema_invalid_history"
    return rates, None


def _read_history_rows(history_path: Path) -> tuple[list[dict[str, float]] | None, str | None]:
    rows: list[dict[str, float]] = []
    for raw in history_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return None, "schema_invalid_history"
        if not isinstance(payload, dict):
            return None, "schema_invalid_history"
        rates, issue = _history_rates(payload)
        if issue:
            return None, issue
        if rates:
            rows.append(rates)
    return rows, None


def _metric_deteriorated(current_value: float, baseline_value: float) -> bool:
    return current_value > baseline_value * 1.2 and current_value - baseline_value >= 0.01


def _history_deteriorated(current: dict[str, float], baseline: list[dict[str, float]]) -> bool:
    unresolved_baseline = median(row["unresolved_ambiguity_rate"] for row in baseline)
    no_candidate_baseline = median(row["no_candidate_rate"] for row in baseline)
    return _metric_deteriorated(current["unresolved_ambiguity_rate"], unresolved_baseline) or _metric_deteriorated(
        current["no_candidate_rate"], no_candidate_baseline
    )


def _latest_history_metrics(history_path: Path) -> tuple[dict[str, float] | None, str | None]:
    """Return the latest routing-quality metrics and their validation status."""
    if not history_path.exists():
        return None, "missing_history"
    rows, issue = _read_history_rows(history_path)
    if issue:
        return None, issue
    if rows is None or len(rows) < 8:
        return None, "insufficient_history"
    current = rows[-1]
    if _history_deteriorated(current, rows[-8:-1]):
        return current, "trend_deterioration"
    return current, None


def _policy_identity_drift(
    surfaces: list[dict[str, Any]],
    active_policy_identity: str,
) -> tuple[str, str, str] | None:
    """Return a blocking tuple when a stamped surface has stale policy identity."""
    for surface in surfaces:
        if surface["policy_identity_required"] and surface.get("policy_identity") != active_policy_identity:
            return (
                "missing_or_mismatched_policy_identity",
                "missing_policy_identity",
                "Refresh projections so policy identity stamps match the active selection policy.",
            )
    return None


def _history_trend_drift(repo_root: Path) -> tuple[str, tuple[str, str, str] | None]:
    """Classify local trend history without turning missing telemetry into source drift."""
    _, history_issue = _latest_history_metrics(repo_root / HISTORY_PATH)
    if history_issue == "missing_history":
        return "not_collected", None
    if history_issue == "insufficient_history":
        return history_issue, None
    if history_issue == "schema_invalid_history":
        return (
            history_issue,
            ("trend_schema_invalid_history", "schema_invalid_history", f"Repair {HISTORY_PATH.as_posix()} to valid schema entries."),
        )
    if history_issue == "trend_deterioration":
        return (
            history_issue,
            ("trend_deterioration", "soft_gate_deterioration", "Resolve routing-quality deterioration before strict validation can pass."),
        )
    return "available", None


def compute_catalog_parity(
    repo_root: Path,
    *,
    strict: bool = False,
    skills_list_count: int | None = None,
    route_considered_total: int | None = None,
) -> dict[str, Any]:
    """
    Produce a diagnostic report comparing the canonical catalog and active policy identity against observed counts and metadata across repository and runtime surfaces.

    Parameters:
        repo_root (Path): Repository root used to read README.md, SKILL.md, and history artifacts.
        strict (bool): When True, require matching policy identity on stamped surfaces and enforce routing-quality history gates.
        skills_list_count (int | None): Optional override for the observed "ask skills list" total; when None the canonical count is used.
        route_considered_total (int | None): Optional override for the observed "route considered metadata" total; when None the canonical count is used.

    Returns:
        report (dict[str, Any]): Diagnostic report with the following keys:
            - `schema_version`: report schema identifier.
            - `policy_identity`: active policy identity used for comparisons.
            - `canonical_count`: canonical skill count discovered from the catalog.
            - `surfaces`: list of per-surface dictionaries containing `surface_name`, `observed_count`, `canonical_count`, `parity_ok`, `policy_identity`, and `policy_identity_required`.
            - `drift_detected`: `True` if any gating condition failed, `False` otherwise.
            - `drift_class`: classification of the detected drift or `None`.
            - `blocking_reason`: short code describing why strict validation is blocked, or `None`.
            - `operator_action`: human-readable remediation guidance when blocked, or `None`.
            - `decision_status`: `"blocked_catalog_parity"` when blocked, otherwise `"resolved"`.
            - `required_surfaces`: list of surfaces considered required.
            - `strict_mode`: echoes the `strict` parameter.
    """
    # Keep parity anchored to repository-owned discovery so local runtime
    # projection drift cannot spuriously block doctor-catalog/route workflows.
    canonical_count = len(discover_catalog_entries(source="repo"))
    active_policy_identity = get_policy_identity()

    readme_count = _extract_readme_count(repo_root / "README.md")
    skill_index_count = _extract_root_skill_index_count(repo_root / "SKILL.md")
    skill_index_policy_identity = _extract_root_skill_index_policy_identity(repo_root / "SKILL.md")
    list_count = skills_list_count if skills_list_count is not None else canonical_count
    considered_total = route_considered_total if route_considered_total is not None else canonical_count

    surfaces = [
        {
            "surface_name": "README.md",
            "observed_count": readme_count,
            "canonical_count": canonical_count,
            "parity_ok": readme_count == canonical_count,
            "policy_identity": None,
            "policy_identity_required": False,
        },
        {
            "surface_name": "SKILL.md",
            "observed_count": skill_index_count,
            "canonical_count": canonical_count,
            "parity_ok": skill_index_count == canonical_count,
            "policy_identity": skill_index_policy_identity,
            "policy_identity_required": True,
        },
        {
            "surface_name": "ask skills list",
            "observed_count": list_count,
            "canonical_count": canonical_count,
            "parity_ok": list_count == canonical_count,
            "policy_identity": active_policy_identity,
            "policy_identity_required": True,
        },
        {
            "surface_name": "route considered metadata",
            "observed_count": considered_total,
            "canonical_count": canonical_count,
            "parity_ok": considered_total == canonical_count,
            "policy_identity": active_policy_identity,
            "policy_identity_required": True,
        },
    ]

    drift_detected = any(not item["parity_ok"] for item in surfaces)
    drift_class = "count_mismatch" if drift_detected else None
    blocking_reason = "required_surface_count_mismatch" if drift_detected else None
    history_status = "not_checked"
    operator_action = (
        "Run `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`, regenerate catalog projections, then rerun doctor-catalog."
        if drift_detected
        else None
    )

    if strict and not drift_detected:
        identity_drift = _policy_identity_drift(surfaces, active_policy_identity)
        if identity_drift is not None:
            drift_class, blocking_reason, operator_action = identity_drift
            drift_detected = True

    if strict and not drift_detected:
        history_status, history_drift = _history_trend_drift(repo_root)
        if history_drift is not None:
            drift_class, blocking_reason, operator_action = history_drift
            drift_detected = True

    report = {
        "schema_version": CATALOG_PARITY_SCHEMA_VERSION,
        "policy_identity": active_policy_identity,
        "canonical_count": canonical_count,
        "surfaces": surfaces,
        "drift_detected": drift_detected,
        "drift_class": drift_class,
        "blocking_reason": blocking_reason,
        "history_status": history_status,
        "operator_action": operator_action,
        "decision_status": "blocked_catalog_parity" if drift_detected else "resolved",
        "required_surfaces": list(REQUIRED_SURFACES),
        "strict_mode": strict,
    }
    return report
