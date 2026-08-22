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
HISTORY_WINDOW_RUNS = 8


def rejected_history_path(history_path: Path) -> Path:
    """Return the sidecar used to preserve the latest rejected candidate."""
    return history_path.with_name(f"{history_path.stem}.rejected.json")


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


def _history_counts(
    payload: dict[str, Any],
) -> tuple[tuple[float, float, float] | None, str | None]:
    totals = payload.get("totals")
    status_counts = payload.get("status_counts")
    if not isinstance(totals, dict) or not isinstance(status_counts, dict):
        return None, "schema_invalid_history"
    if "fixtures" not in totals or not {
        "unresolved_ambiguity",
        "degraded_no_candidates",
    }.issubset(status_counts):
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


def _nested_history_rates(
    payload: dict[str, Any],
) -> tuple[dict[str, float] | None, str | None]:
    counts, issue = _history_counts(payload)
    if issue or counts is None:
        return None, issue
    fixtures, unresolved, no_candidate = counts
    if fixtures < 0:
        return None, "schema_invalid_history"
    if fixtures <= 0:
        return None, None
    if (
        unresolved < 0
        or no_candidate < 0
        or unresolved > fixtures
        or no_candidate > fixtures
    ):
        return None, "schema_invalid_history"
    return {
        "unresolved_ambiguity_rate": unresolved / fixtures,
        "no_candidate_rate": no_candidate / fixtures,
    }, None


def _history_rates(
    payload: dict[str, Any],
) -> tuple[dict[str, float] | None, str | None]:
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


def _read_history_rows(
    history_path: Path,
) -> tuple[list[dict[str, float]] | None, str | None]:
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
    return (
        current_value > baseline_value * 1.2 and current_value - baseline_value >= 0.01
    )


def _history_deteriorated(
    current: dict[str, float], baseline: list[dict[str, float]]
) -> bool:
    unresolved_baseline = median(row["unresolved_ambiguity_rate"] for row in baseline)
    no_candidate_baseline = median(row["no_candidate_rate"] for row in baseline)
    return _metric_deteriorated(
        current["unresolved_ambiguity_rate"], unresolved_baseline
    ) or _metric_deteriorated(current["no_candidate_rate"], no_candidate_baseline)


def _latest_history_metrics(
    history_path: Path,
) -> tuple[dict[str, float] | None, str | None]:
    """Return the latest routing-quality metrics and their validation status."""
    if not history_path.exists():
        return None, "missing_history"
    rows, issue = _read_history_rows(history_path)
    if issue:
        return None, issue
    if rows is None or len(rows) < HISTORY_WINDOW_RUNS:
        return None, "insufficient_history"
    current = rows[-1]
    if _history_deteriorated(current, rows[-HISTORY_WINDOW_RUNS:-1]):
        return current, "trend_deterioration"
    return current, None


def candidate_history_issue(
    history_path: Path, candidate: dict[str, Any]
) -> str | None:
    """Validate one candidate against the retained baseline without mutating it."""
    candidate_rates, issue = _history_rates(candidate)
    if issue or candidate_rates is None:
        return issue or "schema_invalid_history"
    if not history_path.exists():
        return None
    rows, issue = _read_history_rows(history_path)
    if issue:
        return issue
    baseline_runs = HISTORY_WINDOW_RUNS - 1
    if rows is None or len(rows) < baseline_runs:
        return None
    if _history_deteriorated(candidate_rates, rows[-baseline_runs:]):
        return "trend_deterioration"
    return None


def _rejected_history_issue(history_path: Path) -> str | None:
    """Revalidate preserved rejection evidence against the current history."""
    rejected_path = rejected_history_path(history_path)
    if not history_path.exists() or not rejected_path.exists():
        return None
    try:
        payload = json.loads(rejected_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "schema_invalid_history"
    if not isinstance(payload, dict):
        return "schema_invalid_history"
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict):
        return "schema_invalid_history"
    return candidate_history_issue(history_path, candidate)


def _policy_identity_drift(
    surfaces: list[dict[str, Any]],
    active_policy_identity: str,
) -> tuple[str, str, str] | None:
    """Return a blocking tuple when a stamped surface has stale policy identity."""
    for surface in surfaces:
        if (
            surface["policy_identity_required"]
            and surface.get("policy_identity") != active_policy_identity
        ):
            return (
                "missing_or_mismatched_policy_identity",
                "missing_policy_identity",
                "Refresh projections so policy identity stamps match the active selection policy.",
            )
    return None


def _history_trend_drift(repo_root: Path) -> tuple[str, tuple[str, str, str] | None]:
    """Classify local trend history without turning missing telemetry into source drift."""
    history_path = repo_root / HISTORY_PATH
    history_issue = _rejected_history_issue(history_path)
    if history_issue is None:
        _, history_issue = _latest_history_metrics(history_path)
    if history_issue == "missing_history":
        return "not_collected", None
    if history_issue == "insufficient_history":
        return history_issue, None
    if history_issue == "schema_invalid_history":
        rejected = rejected_history_path(history_path)
        return (
            history_issue,
            (
                "trend_schema_invalid_history",
                "schema_invalid_history",
                (
                    f"Repair {HISTORY_PATH.as_posix()} to valid schema entries; "
                    f"remove or repair {rejected.name} if the rejected sidecar is corrupt."
                ),
            ),
        )
    if history_issue == "trend_deterioration":
        return (
            history_issue,
            (
                "trend_deterioration",
                "soft_gate_deterioration",
                "Resolve routing-quality deterioration before strict validation can pass.",
            ),
        )
    return "available", None


def _surface(
    name: str,
    observed: int | None,
    canonical: int,
    *,
    identity: str | None,
    required: bool,
) -> dict[str, Any]:
    """Build one catalog parity surface record."""
    return {
        "surface_name": name,
        "observed_count": observed,
        "canonical_count": canonical,
        "parity_ok": observed == canonical,
        "policy_identity": identity,
        "policy_identity_required": required,
    }


def _catalog_surfaces(
    repo_root: Path,
    canonical: int,
    identity: str,
    skills_list_count: int | None,
    route_considered_total: int | None,
) -> list[dict[str, Any]]:
    """Collect canonical and runtime-facing count surfaces."""
    list_count = canonical if skills_list_count is None else skills_list_count
    considered = canonical if route_considered_total is None else route_considered_total
    return [
        _surface(
            "README.md",
            _extract_readme_count(repo_root / "README.md"),
            canonical,
            identity=None,
            required=False,
        ),
        _surface(
            "SKILL.md",
            _extract_root_skill_index_count(repo_root / "SKILL.md"),
            canonical,
            identity=_extract_root_skill_index_policy_identity(repo_root / "SKILL.md"),
            required=True,
        ),
        _surface(
            "ask skills list", list_count, canonical, identity=identity, required=True
        ),
        _surface(
            "route considered metadata",
            considered,
            canonical,
            identity=identity,
            required=True,
        ),
    ]


def _catalog_drift(
    repo_root: Path,
    surfaces: list[dict[str, Any]],
    identity: str,
    *,
    strict: bool,
) -> tuple[bool, str | None, str | None, str, str | None]:
    """Resolve count, identity, and history drift in precedence order."""
    if any(not item["parity_ok"] for item in surfaces):
        return (
            True,
            "count_mismatch",
            "required_surface_count_mismatch",
            "not_checked",
            (
                "Run `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`, regenerate catalog projections, then rerun doctor-catalog."
            ),
        )
    if not strict:
        return False, None, None, "not_checked", None
    identity_drift = _policy_identity_drift(surfaces, identity)
    if identity_drift:
        drift_class, reason, action = identity_drift
        return True, drift_class, reason, "not_checked", action
    history_status, history_drift = _history_trend_drift(repo_root)
    if history_drift:
        return (
            True,
            history_drift[0],
            history_drift[1],
            history_status,
            history_drift[2],
        )
    return False, None, None, history_status, None


def compute_catalog_parity(
    repo_root: Path,
    *,
    strict: bool = False,
    skills_list_count: int | None = None,
    route_considered_total: int | None = None,
) -> dict[str, Any]:
    """Compute repository-owned catalog parity diagnostics."""
    canonical = len(discover_catalog_entries(source="repo"))
    identity = get_policy_identity()
    surfaces = _catalog_surfaces(
        repo_root, canonical, identity, skills_list_count, route_considered_total
    )
    detected, drift_class, reason, history_status, action = _catalog_drift(
        repo_root, surfaces, identity, strict=strict
    )
    return {
        "schema_version": CATALOG_PARITY_SCHEMA_VERSION,
        "policy_identity": identity,
        "canonical_count": canonical,
        "surfaces": surfaces,
        "drift_detected": detected,
        "drift_class": drift_class,
        "blocking_reason": reason,
        "history_status": history_status,
        "operator_action": action,
        "decision_status": "blocked_catalog_parity" if detected else "resolved",
        "required_surfaces": list(REQUIRED_SURFACES),
        "strict_mode": strict,
    }
