import json
import os
from pathlib import Path
from typing import Any


TELEMETRY_DIRNAME = ".skill-telemetry"
INVOCATIONS_FILENAME = "skill-invocations.jsonl"


def skill_telemetry_dir(repo_root: Path) -> Path:
    """Return the ASK-local generated skill telemetry projection directory."""
    override = os.environ.get("SKILL_TELEMETRY_DIR", "").strip()
    if not override:
        return repo_root / TELEMETRY_DIRNAME
    override_path = Path(override)
    return override_path if override_path.is_absolute() else repo_root / override_path


def analytics_projection_path(repo_root: Path) -> Path:
    """Return the normalized skill invocation projection path."""
    return skill_telemetry_dir(repo_root) / INVOCATIONS_FILENAME


def skill_invocation_analytics(repo_root: Path, handle: str) -> dict[str, Any]:
    """Summarize native Codex skill invocation evidence for one skill handle."""
    projection_path = analytics_projection_path(repo_root)
    projection_ref = _projection_ref(repo_root, projection_path)
    if not projection_path.is_file():
        return {
            "status": "unavailable_or_legacy",
            "evidence_class": "native_skill_invocation_projection",
            "projection_path": projection_ref,
            "note": "No ASK-local skill invocation projection is available.",
        }

    invocation_count = 0
    matching_invocation_count = 0
    latest: dict[str, Any] | None = None
    parse_errors: list[dict[str, Any]] = []
    normalized = _normalize_handle(handle)
    try:
        with projection_path.open(encoding="utf-8") as projection:
            for line_number, raw_line in enumerate(projection, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    parse_errors.append({"line": line_number, "message": str(exc)})
                    continue
                if isinstance(record, dict):
                    invocation_count += 1
                    if _record_matches_skill(record, normalized):
                        matching_invocation_count += 1
                        latest = _latest_record(latest, record)
                else:
                    parse_errors.append({"line": line_number, "message": "record is not an object"})
    except OSError as exc:
        return {
            "status": "unavailable_or_legacy",
            "evidence_class": "native_skill_invocation_projection",
            "projection_path": projection_ref,
            "note": f"Skill invocation projection could not be read: {exc}",
            "parse_error_count": 1,
            "parse_errors": [{"line": None, "message": str(exc)}],
        }

    if parse_errors and not invocation_count:
        status = "parse_error"
    elif parse_errors:
        status = "parse_warning"
    else:
        status = "available" if matching_invocation_count else "no_matching_invocations"

    summary: dict[str, Any] = {
        "status": status,
        "evidence_class": "native_skill_invocation_projection",
        "projection_path": projection_ref,
        "invocation_count": invocation_count,
        "matching_invocation_count": matching_invocation_count,
        "parse_error_count": len(parse_errors),
    }
    if latest:
        summary["latest_invocation"] = _public_invocation_fields(latest)
    if parse_errors:
        summary["parse_errors"] = parse_errors[:3]
    return summary


def _projection_ref(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def _normalize_handle(value: str) -> str:
    return value.strip().lstrip("$").lower().replace("_", "-")


def _record_matches_skill(record: dict[str, Any], normalized: str) -> bool:
    candidates = [
        record.get("skill_id"),
        record.get("skill"),
        record.get("handle"),
        record.get("skill_handle"),
    ]
    return any(_normalize_handle(str(candidate)) == normalized for candidate in candidates if candidate)


def _latest_record(current: dict[str, Any] | None, candidate: dict[str, Any]) -> dict[str, Any]:
    if current is None:
        return candidate
    current_key = str(current.get("timestamp") or current.get("started_at") or "")
    candidate_key = str(candidate.get("timestamp") or candidate.get("started_at") or "")
    return candidate if candidate_key >= current_key else current


def _public_invocation_fields(record: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "skill_id",
        "plugin_id",
        "turn_id_hash",
        "thread_id_hash",
        "invoke_type",
        "scope",
        "model_slug",
        "product_client_id_hash",
        "repository_hash",
        "timestamp",
    )
    return {key: record[key] for key in allowed if key in record}
