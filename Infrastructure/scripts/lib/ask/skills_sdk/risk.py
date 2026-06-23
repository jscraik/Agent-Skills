from __future__ import annotations

from pathlib import Path
from typing import Any


RISK_CLASSIFICATION_SCHEMA_VERSION = "skills-sdk.risk-classification.v1"
RISK_CLASSIFICATION_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/risk-classification.v1.schema.json"
)

RISK_ACCEPTANCE_TRACE = [
    "FR-003",
    "FR-018",
    "FR-019",
    "NFR-001",
    "NFR-002",
    "SA-025",
    "SA-026",
    "SA-027",
    "SA-028",
    "VP-020",
    "VP-022",
]


def _sensor(
    sensor_id: str,
    placement: str,
    *,
    required: bool,
    cost: str,
    blocking_behavior: str,
    status: str = "selected",
    receipt_required: bool = True,
) -> dict[str, Any]:
    return {
        "id": sensor_id,
        "placement": placement,
        "required": required,
        "cost": cost,
        "blocking_behavior": blocking_behavior,
        "status": status,
        "receipt_required": receipt_required,
    }


MANIFEST_SOURCE_SENSOR = _sensor(
    "manifest_source",
    "source",
    required=True,
    cost="low",
    blocking_behavior="block",
)

_SOURCE_PROFILES: dict[str, dict[str, Any]] = {
    "docs_only": {
        "risk_tier": "low",
        "probability": "low",
        "impact": "low",
        "detectability": "high",
        "cost": "low",
        "blocking_behavior": "advisory",
        "receipt_required": True,
        "sensors": [
            MANIFEST_SOURCE_SENSOR,
            _sensor(
                "static_metadata",
                "static",
                required=False,
                cost="low",
                blocking_behavior="advisory",
                receipt_required=False,
            ),
        ],
    },
    "referenced": {
        "risk_tier": "medium",
        "probability": "medium",
        "impact": "medium",
        "detectability": "medium",
        "cost": "low",
        "blocking_behavior": "warn",
        "receipt_required": True,
        "sensors": [
            MANIFEST_SOURCE_SENSOR,
            _sensor(
                "reference_boundary",
                "static",
                required=True,
                cost="low",
                blocking_behavior="warn",
            ),
        ],
    },
    "scripted": {
        "risk_tier": "high",
        "probability": "medium",
        "impact": "high",
        "detectability": "medium",
        "cost": "medium",
        "blocking_behavior": "block",
        "receipt_required": True,
        "sensors": [
            MANIFEST_SOURCE_SENSOR,
            _sensor(
                "static_script_scan",
                "static",
                required=True,
                cost="low",
                blocking_behavior="block",
            ),
            _sensor(
                "codex_sandbox_boundary",
                "runtime_adapter",
                required=True,
                cost="medium",
                blocking_behavior="block",
                status="selected",
            ),
        ],
    },
    "external": {
        "risk_tier": "privileged",
        "probability": "high",
        "impact": "high",
        "detectability": "low",
        "cost": "high",
        "blocking_behavior": "block",
        "receipt_required": True,
        "sensors": [
            MANIFEST_SOURCE_SENSOR,
            _sensor(
                "external_adapter_detection",
                "external_adapter",
                required=True,
                cost="medium",
                blocking_behavior="block",
            ),
            _sensor(
                "intake_quarantine_boundary",
                "static",
                required=True,
                cost="medium",
                blocking_behavior="block",
                status="selected",
            ),
        ],
    },
    "placeholder": {
        "risk_tier": "medium",
        "probability": "unknown",
        "impact": "unknown",
        "detectability": "high",
        "cost": "low",
        "blocking_behavior": "skip_optional",
        "receipt_required": True,
        "sensors": [
            _sensor(
                "placeholder_lifecycle",
                "schema",
                required=True,
                cost="low",
                blocking_behavior="skip_optional",
                status="skipped_optional",
            )
        ],
    },
}

_SCRIPT_MARKERS = (
    "scripts/",
    "bin/",
    "exec ",
    "subprocess",
    "shell",
    "command:",
    "commands:",
    "tools:",
)

_REFERENCE_MARKERS = (
    "references/",
    "assets/",
    "examples/",
    "docs/",
    "http://",
    "https://",
    "repo:",
)


def _truthy_metadata(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, str) and value.strip().lower() in {"none", "n/a", "false"}:
        return False
    return True


def _skill_root_for(path: Path) -> Path:
    return path.parent if path.name == "SKILL.md" else path


def _declared_source_kind(fields: dict[str, Any]) -> str | None:
    declared = str(fields.get("source_kind") or fields.get("source-kind") or "").strip().lower()
    return declared if declared in _SOURCE_PROFILES else None


def _is_scripted_source(fields: dict[str, Any], skill_root: Path, lower_body: str) -> bool:
    return (
        any(_truthy_metadata(fields.get(key)) for key in ("commands", "tools", "runtime_needs"))
        or any((skill_root / name).exists() for name in ("scripts", "bin"))
        or any(marker in lower_body for marker in _SCRIPT_MARKERS)
    )


def _is_referenced_source(fields: dict[str, Any], skill_root: Path, lower_body: str) -> bool:
    return (
        any(_truthy_metadata(fields.get(key)) for key in ("references", "examples", "assets"))
        or any((skill_root / name).exists() for name in ("references", "examples", "assets", "docs"))
        or any(marker in lower_body for marker in _REFERENCE_MARKERS)
    )


def classify_source_kind(
    source_path: Path | None,
    frontmatter: dict[str, Any] | None = None,
    body_text: str | None = None,
) -> str:
    """Classify the V1.0 source shape without executing source content."""
    if source_path is None or not source_path.exists():
        return "placeholder"

    if source_path.name == "package.json":
        return "external"

    fields = frontmatter or {}
    lower_body = (body_text or "").lower()
    skill_root = _skill_root_for(source_path)

    provenance = str(fields.get("provenance") or "").lower()
    declared_source_kind = _declared_source_kind(fields)
    if declared_source_kind:
        return declared_source_kind
    if "external" in provenance or _truthy_metadata(fields.get("external")):
        return "external"

    if _is_scripted_source(fields, skill_root, lower_body):
        return "scripted"

    if _is_referenced_source(fields, skill_root, lower_body):
        return "referenced"

    if str(fields.get("status") or "").strip().lower() in {"placeholder", "not_run"}:
        return "placeholder"

    return "docs_only"


def build_risk_classification(
    source_path: Path | None,
    frontmatter: dict[str, Any] | None = None,
    body_text: str | None = None,
) -> dict[str, Any]:
    """Return a schema-shaped V1.0 risk classification receipt."""
    source_kind = classify_source_kind(source_path, frontmatter, body_text)
    profile = _SOURCE_PROFILES[source_kind]
    sensors = [dict(sensor) for sensor in profile["sensors"]]
    return {
        "schema_version": RISK_CLASSIFICATION_SCHEMA_VERSION,
        "schema_uri": RISK_CLASSIFICATION_SCHEMA_URI,
        "source_kind": source_kind,
        "risk_tier": profile["risk_tier"],
        "probability": profile["probability"],
        "impact": profile["impact"],
        "detectability": profile["detectability"],
        "cost": profile["cost"],
        "blocking_behavior": profile["blocking_behavior"],
        "receipt_required": profile["receipt_required"],
        "sensor_ids": [sensor["id"] for sensor in sensors],
        "sensors": sensors,
        "acceptance_trace": RISK_ACCEPTANCE_TRACE,
    }
