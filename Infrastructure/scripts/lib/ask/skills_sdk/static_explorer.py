from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.capability_status import build_capability_status


STATIC_EXPLORER_SCHEMA_VERSION = "skills-sdk.static-explorer-receipt.v0"
STATIC_EXPLORER_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/static-explorer-receipt.v0.schema.json"
)
STATIC_EXPLORER_ACCEPTANCE_TRACE = ["PU-029", "FR-003", "FR-008", "VP-029"]
MANIFEST_ROOT = Path(".skillsets")


class StaticExplorerError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _load_manifest_rows(repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted((repo_root / MANIFEST_ROOT).glob("*/manifest.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.relative_to(repo_root).as_posix()}:{line_number}:{exc.msg}")
                continue
            if isinstance(value, dict):
                rows.append(value)
            else:
                errors.append(f"{path.relative_to(repo_root).as_posix()}:{line_number}:not_object")
    return rows, errors


def _skill_index(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    index: list[dict[str, str]] = []
    for row in rows:
        skill_id = str(row.get("id") or "").strip()
        source_path = str(row.get("source_path") or "").strip()
        skill_set = str(row.get("skill_set") or "").strip()
        if skill_id and source_path and skill_set:
            index.append({"id": skill_id, "skill_set": skill_set, "source_path": source_path})
    return sorted(index, key=lambda item: (item["skill_set"], item["id"]))


def _capability_index(capabilities: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "id": str(row["id"]),
            "title": str(row["title"]),
            "status": str(row["status"]),
            "owner_surface": str(row["owner_surface"]),
        }
        for row in capabilities
    ]


def build_static_explorer_receipt(repo_root: Path) -> dict[str, Any]:
    status = build_capability_status(repo_root)
    manifest_rows, manifest_errors = _load_manifest_rows(repo_root)
    skills = _skill_index(manifest_rows)
    checks = [
        _check("capability_status_loaded", "pass", "Capability index must come from sdk status JSON.", [status["schema_version"]]),
        _check("skill_manifests_parse", "blocker" if manifest_errors else "pass", "Skill index must come from rooted manifest JSONL.", manifest_errors),
    ]
    blockers = [check for check in checks if check["status"] == "blocker"]
    receipt = {
        "schema_version": STATIC_EXPLORER_SCHEMA_VERSION,
        "schema_uri": STATIC_EXPLORER_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "static_explorer_preview",
        "capability_count": len(status["capabilities"]),
        "skill_count": len(skills),
        "skill_sets": sorted({skill["skill_set"] for skill in skills}),
        "capability_index": [] if blockers else _capability_index(status["capabilities"]),
        "skill_index": [] if blockers else skills,
        "projection_inputs": [
            "Infrastructure/config/skills-sdk/capability-matrix.v1.json",
            ".skillsets/*/manifest.jsonl",
        ],
        "explorer_checks": checks,
        "blockers": blockers,
        "html_rendered": False,
        "hosted_publish_requested": False,
        "mutation_performed": False,
        "acceptance_trace": STATIC_EXPLORER_ACCEPTANCE_TRACE,
        "agent_summary": (
            "static explorer preview is blocked by source JSON validation."
            if blockers
            else f"static explorer preview indexed {len(status['capabilities'])} capability row(s) and {len(skills)} skill row(s)."
        ),
    }
    if blockers:
        raise StaticExplorerError(receipt)
    return receipt
