from __future__ import annotations

from pathlib import Path
from typing import Any


STRUCTURED_SECTIONS = frozenset({
    "principles",
    "heuristics",
    "checklists",
    "rubrics",
    "lenses",
    "eval-scenarios",
})
PLAYBOOK_SECTIONS = frozenset({
    "core-thesis",
    "principles",
    "guidance",
    "decision-rules",
    "output-shape",
    "examples",
    "recovery",
    "validation-ideas",
    "boundaries",
})


def validate_operational_references(
    extraction_root: Path,
    manifest: dict[str, Any],
    findings: list[str],
) -> None:
    """Recheck the KnowledgeOS operational-reference contract at SDK ingest."""
    capsules = manifest.get("capsules")
    if not isinstance(capsules, list) or not capsules:
        findings.append("manifest:missing_capsules")
        return
    for index, capsule in enumerate(capsules):
        _validate_capsule(extraction_root, capsule, index, findings)


def _validate_capsule(
    extraction_root: Path,
    capsule: object,
    index: int,
    findings: list[str],
) -> None:
    if not isinstance(capsule, dict):
        findings.append(f"manifest:capsule_not_object:{index}")
        return
    target_path = str(capsule.get("target_path") or "")
    if not target_path:
        findings.append(f"manifest:capsule_missing_target_path:{index}")
        return
    try:
        text = (extraction_root / target_path).read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        findings.append(f"references:missing_or_invalid_capsule:{target_path}")
        return
    _validate_capsule_text(text, target_path, findings)


def _validate_capsule_text(text: str, target_path: str, findings: list[str]) -> None:
    if not text.startswith("# "):
        findings.append(f"references:missing_h1:{target_path}")
    headings = {_normalize_heading(line[3:]) for line in text.splitlines() if line.startswith("## ")}
    structured = "claim-cards" in headings and bool(headings & STRUCTURED_SECTIONS)
    if structured or PLAYBOOK_SECTIONS <= headings:
        return
    missing = ",".join(sorted(PLAYBOOK_SECTIONS - headings))
    findings.append(f"references:weak_operational_reference:{target_path}:missing:{missing}")


def _normalize_heading(value: str) -> str:
    return "-".join(value.strip().lower().replace("&", "and").split())
