from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from ask.skills_sdk.capability_status import load_capability_matrix


DEFAULT_CAPABILITY_HTML = Path("artifacts/recommended-skills-sdk-pipeline.html")
CANONICAL_ATLAS_PIPELINE_STEPS = (
    "foundry",
    "sdk_entry_lifecycle",
    "guardrails_oss_security",
    "sdk_early_lifecycle",
    "proof_oss_local",
    "sdk_middle_lifecycle",
    "proof_oss_cloud",
    "sdk_prerelease_lifecycle",
    "tessl_distribution",
    "local_runtime",
)
DOCS_PROJECTION_CHECKED_FIELDS = (
    "id",
    "status",
    "pipeline_sections",
    "declared_summary_counts",
    "declared_pipeline_step_order",
)


class _CapabilityTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict[str, Any]] = []
        self.summary_counts: list[dict[str, Any]] = []
        self.pipeline_steps: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        summary_statuses = attributes.get("data-capability-summary-statuses", "").strip()
        if summary_statuses:
            self.summary_counts.append(
                {
                    "statuses": [item.strip() for item in summary_statuses.split(",") if item.strip()],
                    "count": attributes.get("data-count", "").strip(),
                }
            )
        pipeline_step = attributes.get("data-pipeline-step", "").strip()
        if pipeline_step:
            self.pipeline_steps.append(pipeline_step)
        if tag != "tr":
            return
        row = attributes
        capability_id = row.get("data-capability-id", "").strip()
        if not capability_id:
            return
        self.rows.append(
            {
                "id": capability_id,
                "status": row.get("data-status", "").strip(),
                "pipeline_sections": [
                    item.strip()
                    for item in row.get("data-pipeline-sections", "").split(",")
                    if item.strip()
                ],
            }
        )


def _load_projection_rows(
    path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str], dict[str, Any] | None]:
    parser = _CapabilityTableParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return [], [], [], {
            "code": "projection_parse_failed",
            "path": path.as_posix(),
            "message": str(exc),
        }
    return parser.rows, parser.summary_counts, parser.pipeline_steps, None


def _summary_count_blockers(
    summary_counts: list[dict[str, Any]],
    expected_status_counts: dict[str, int],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for summary in summary_counts:
        statuses = summary["statuses"]
        expected = sum(expected_status_counts.get(status, 0) for status in statuses)
        try:
            actual = int(summary["count"])
        except ValueError:
            actual = summary["count"]
        if actual != expected:
            blockers.append(
                {
                    "code": "summary_count_mismatch",
                    "statuses": statuses,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return blockers


def _pipeline_step_blockers(pipeline_steps: list[str]) -> list[dict[str, Any]]:
    if not pipeline_steps or tuple(pipeline_steps) == CANONICAL_ATLAS_PIPELINE_STEPS:
        return []
    return [
        {
            "code": "pipeline_step_order_mismatch",
            "expected": list(CANONICAL_ATLAS_PIPELINE_STEPS),
            "actual": pipeline_steps,
        }
    ]


def _duplicate_ids(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        capability_id = row["id"]
        if capability_id in seen:
            duplicates.add(capability_id)
        seen.add(capability_id)
    return sorted(duplicates)


def _row_mismatches(
    expected_by_id: dict[str, dict[str, Any]],
    actual_by_id: dict[str, dict[str, Any]],
    key: str,
) -> list[dict[str, Any]]:
    return sorted(
        (
            {"id": capability_id, "expected": expected_by_id[capability_id][key], "actual": actual_by_id[capability_id][key]}
            for capability_id in set(expected_by_id) & set(actual_by_id)
            if expected_by_id[capability_id][key] != actual_by_id[capability_id][key]
        ),
        key=lambda row: row["id"],
    )


def _blockers(
    html_path: Path,
    expected_by_id: dict[str, dict[str, Any]],
    actual_by_id: dict[str, dict[str, Any]],
    duplicate_ids: list[str],
    parse_blocker: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    missing = sorted(set(expected_by_id) - set(actual_by_id))
    extra = sorted(set(actual_by_id) - set(expected_by_id))
    if not html_path.is_file():
        blockers.append({"code": "missing_projection_artifact", "path": html_path.as_posix()})
    if parse_blocker:
        blockers.append(parse_blocker)
    if duplicate_ids:
        blockers.append({"code": "duplicate_capability_rows", "capability_ids": duplicate_ids})
    if missing:
        blockers.append({"code": "missing_capability_rows", "capability_ids": missing})
    if extra:
        blockers.append({"code": "extra_capability_rows", "capability_ids": extra})
    for code, key in (("status_mismatch", "status"), ("pipeline_sections_mismatch", "pipeline_sections")):
        mismatches = _row_mismatches(expected_by_id, actual_by_id, key)
        if mismatches:
            blockers.append({"code": code, "rows": mismatches})
    return blockers


def _artifact_label(repo_root: Path, html_path: Path) -> str:
    if html_path.exists() and html_path.resolve().is_relative_to(repo_root.resolve()):
        return html_path.resolve().relative_to(repo_root.resolve()).as_posix()
    return html_path.as_posix()


def verify_capability_docs_projection(
    repo_root: Path,
    *,
    artifact_path: Path | None = None,
) -> dict[str, Any]:
    """Verify the static capability table mirrors the SDK capability matrix."""
    relative_artifact = artifact_path or DEFAULT_CAPABILITY_HTML
    html_path = relative_artifact if relative_artifact.is_absolute() else repo_root / relative_artifact
    matrix = load_capability_matrix(repo_root)
    capabilities = matrix["capabilities"]
    expected_by_id = {row["id"]: row for row in capabilities}
    rows, summary_counts, pipeline_steps, parse_blocker = (
        _load_projection_rows(html_path) if html_path.is_file() else ([], [], [], None)
    )
    actual_by_id = {row["id"]: row for row in rows}
    blockers = _blockers(html_path, expected_by_id, actual_by_id, _duplicate_ids(rows), parse_blocker)
    expected_status_counts = {
        status: sum(1 for row in capabilities if row["status"] == status)
        for status in {row["status"] for row in capabilities}
    }
    blockers.extend(_summary_count_blockers(summary_counts, expected_status_counts))
    blockers.extend(_pipeline_step_blockers(pipeline_steps))
    status = "pass" if not blockers else "blocked"
    return {
        "schema_version": "skills-sdk.docs-projection-verify.v0",
        "status": status,
        "artifact_path": _artifact_label(repo_root, html_path),
        "matrix_path": "Infrastructure/config/skills-sdk/capability-matrix.v1.json",
        "capability_count": len(capabilities),
        "projection_row_count": len(rows),
        "checked_fields": list(DOCS_PROJECTION_CHECKED_FIELDS),
        "blockers": blockers,
        "mutation_performed": False,
        "agent_summary": (
            f"Capability docs projection matches {len(capabilities)} matrix row(s)."
            if status == "pass"
            else f"Capability docs projection is blocked by {len(blockers)} drift class(es)."
        ),
    }
