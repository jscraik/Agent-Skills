"""Canonical catalog parity diagnostics shared across ask command surfaces."""

from __future__ import annotations

import json
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
HISTORY_PATH = Path(".harness/evidence/selection-quality/history.jsonl")


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


def _latest_history_metrics(history_path: Path) -> tuple[dict[str, float] | None, str | None]:
    """
    Parse routing-quality history JSONL and determine the latest metrics and trend status.

    Reads the provided history JSONL, validates records, computes median baselines from the previous seven entries, and detects routing-quality deterioration in the latest row.

    Returns:
        A tuple of `(current_metrics, status)`:
        - `current_metrics` (`dict[str, float] | None`): the most recent record containing keys `unresolved_ambiguity_rate` and `no_candidate_rate`, or `None` when a usable current record cannot be produced.
        - `status` (`str | None`): one of:
            - `"missing_history"` — history file does not exist.
            - `"schema_invalid_history"` — the file contains invalid JSON or unexpected schema/values.
            - `"insufficient_history"` — fewer than eight usable rows available to compute baselines.
            - `"trend_deterioration"` — latest metrics show deterioration versus the baseline.
            - `None` — parsing succeeded and no deterioration was detected.
    """
    if not history_path.exists():
        return None, "missing_history"

    rows: list[dict[str, Any]] = []
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

        unresolved = payload.get("unresolved_ambiguity_rate")
        no_candidate = payload.get("no_candidate_rate")
        if unresolved is None or no_candidate is None:
            # Allow alternate nested structure emitted by some validators.
            totals = payload.get("totals") if isinstance(payload.get("totals"), dict) else {}
            fixtures = float(totals.get("fixtures", 0) or 0)
            status_counts = payload.get("status_counts") if isinstance(payload.get("status_counts"), dict) else {}
            unresolved_count = float(status_counts.get("unresolved_ambiguity", 0) or 0)
            no_candidate_count = float(status_counts.get("degraded_no_candidates", 0) or 0)
            if fixtures <= 0:
                continue
            unresolved = unresolved_count / fixtures
            no_candidate = no_candidate_count / fixtures
        try:
            rows.append(
                {
                    "unresolved_ambiguity_rate": float(unresolved),
                    "no_candidate_rate": float(no_candidate),
                }
            )
        except (TypeError, ValueError):
            return None, "schema_invalid_history"

    if len(rows) < 8:
        return None, "insufficient_history"

    current = rows[-1]
    baseline_window = rows[-8:-1]
    unresolved_baseline = median(row["unresolved_ambiguity_rate"] for row in baseline_window)
    no_candidate_baseline = median(row["no_candidate_rate"] for row in baseline_window)

    def deteriorated(current_value: float, baseline_value: float) -> bool:
        """
        Determine whether a metric has deteriorated relative to a baseline.

        A deterioration is reported when the current value exceeds the baseline by more than 20% and the absolute increase is at least 0.01.

        Parameters:
            current_value (float): The current metric value.
            baseline_value (float): The baseline metric value to compare against.

        Returns:
            bool: `True` if the current value is greater than the baseline by more than 20% and by at least 0.01, `False` otherwise.
        """
        return (current_value > baseline_value * 1.2) and ((current_value - baseline_value) >= 0.01)

    if deteriorated(current["unresolved_ambiguity_rate"], unresolved_baseline) or deteriorated(
        current["no_candidate_rate"], no_candidate_baseline
    ):
        return current, "trend_deterioration"
    return current, None


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
    operator_action = (
        "Run `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`, regenerate catalog projections, then rerun doctor-catalog."
        if drift_detected
        else None
    )

    if strict and not drift_detected:
        for surface in surfaces:
            if not surface["policy_identity_required"]:
                continue
            if surface.get("policy_identity") != active_policy_identity:
                drift_detected = True
                drift_class = "missing_or_mismatched_policy_identity"
                blocking_reason = "missing_policy_identity"
                operator_action = "Refresh projections so policy identity stamps match the active selection policy."
                break

    if strict and not drift_detected:
        _, history_issue = _latest_history_metrics(repo_root / HISTORY_PATH)
        if history_issue == "insufficient_history":
            drift_detected = True
            drift_class = "trend_insufficient_history"
            blocking_reason = "insufficient_history"
            operator_action = "Collect at least 7 prior routing-quality runs before strict trend enforcement."
        elif history_issue == "schema_invalid_history":
            drift_detected = True
            drift_class = "trend_schema_invalid_history"
            blocking_reason = "schema_invalid_history"
            operator_action = "Repair .harness/evidence/selection-quality/history.jsonl to valid schema entries."
        elif history_issue == "missing_history":
            drift_detected = True
            drift_class = "trend_insufficient_history"
            blocking_reason = "insufficient_history"
            operator_action = "Create .harness/evidence/selection-quality/history.jsonl from completed validation runs."
        elif history_issue == "trend_deterioration":
            drift_detected = True
            drift_class = "trend_deterioration"
            blocking_reason = "soft_gate_deterioration"
            operator_action = "Resolve routing-quality deterioration before strict validation can pass."

    report = {
        "schema_version": CATALOG_PARITY_SCHEMA_VERSION,
        "policy_identity": active_policy_identity,
        "canonical_count": canonical_count,
        "surfaces": surfaces,
        "drift_detected": drift_detected,
        "drift_class": drift_class,
        "blocking_reason": blocking_reason,
        "operator_action": operator_action,
        "decision_status": "blocked_catalog_parity" if drift_detected else "resolved",
        "required_surfaces": list(REQUIRED_SURFACES),
        "strict_mode": strict,
    }
    return report
