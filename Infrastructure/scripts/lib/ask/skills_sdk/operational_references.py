from __future__ import annotations

from pathlib import Path, PurePosixPath
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
        _validate_capsule(extraction_root, manifest, capsule, index, findings)


def operational_reference_paths(manifest: dict[str, Any]) -> tuple[str, ...]:
    """Return the manifest-declared reference paths in stable order."""
    capsules = manifest.get("capsules")
    if not isinstance(capsules, list):
        return ()
    paths = []
    for capsule in capsules:
        if not isinstance(capsule, dict):
            continue
        target_path = str(capsule.get("target_path") or "").strip()
        if target_path and target_path not in paths:
            paths.append(target_path)
    return tuple(paths)


def _validate_capsule(
    extraction_root: Path,
    manifest: dict[str, Any],
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
    source_path = _validate_capsule_path(extraction_root, manifest, target_path, findings)
    if source_path is None:
        return
    try:
        text = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        findings.append(f"references:missing_or_invalid_capsule:{target_path}")
        return
    _validate_capsule_text(text, target_path, findings)


def _validate_capsule_path(
    extraction_root: Path,
    manifest: dict[str, Any],
    target_path: str,
    findings: list[str],
) -> Path | None:
    relative = PurePosixPath(target_path)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("references",):
        findings.append(f"references:invalid_capsule_path:{target_path}")
        return None
    if relative.suffix != ".md":
        findings.append(f"references:capsule_not_markdown:{target_path}")
        return None
    if relative.parts[1:2] == ("knowledge-capsules",) and not _legacy_capsule_subdirectory_allowed(manifest):
        findings.append(f"references:legacy_knowledge_capsule_subdir_unjustified:{target_path}")
        return None
    source_path = extraction_root.joinpath(*relative.parts)
    if _path_or_parent_is_symlink(extraction_root, source_path):
        findings.append(f"references:symlinked_capsule:{target_path}")
        return None
    try:
        source_path.resolve().relative_to(extraction_root.resolve())
    except ValueError:
        findings.append(f"references:invalid_capsule_path:{target_path}")
        return None
    return source_path


def _path_or_parent_is_symlink(extraction_root: Path, source_path: Path) -> bool:
    current = source_path
    while current != extraction_root:
        if current.is_symlink():
            return True
        current = current.parent
    return extraction_root.is_symlink()


def _legacy_capsule_subdirectory_allowed(manifest: dict[str, Any]) -> bool:
    storage = manifest.get("capsule_storage")
    if not isinstance(storage, dict):
        return False
    return storage.get("allow_legacy_subdirectory") is True and bool(str(storage.get("justification") or "").strip())


def _validate_capsule_text(text: str, target_path: str, findings: list[str]) -> None:
    if not text.startswith("# "):
        findings.append(f"references:missing_h1:{target_path}")
    sections = _section_bodies(text)
    structured = bool(sections.get("claim-cards")) and any(
        sections.get(section) for section in STRUCTURED_SECTIONS
    )
    playbook = all(sections.get(section) for section in PLAYBOOK_SECTIONS)
    if structured or playbook:
        return
    missing = ",".join(sorted(section for section in PLAYBOOK_SECTIONS if not sections.get(section)))
    findings.append(f"references:weak_operational_reference:{target_path}:missing:{missing}")


def _section_bodies(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    fence: str | None = None
    for line in text.splitlines():
        delimiter = _fence_delimiter(line)
        if fence is not None:
            if delimiter and delimiter[0] == fence[0] and len(delimiter) >= len(fence):
                fence = None
            continue
        if delimiter:
            fence = delimiter
            continue
        if line.startswith("## "):
            current = _normalize_heading(line[3:])
            sections.setdefault(current, [])
        elif current is not None and line.strip() and not line.lstrip().startswith("#"):
            sections[current].append(line.strip())
    return {heading: "\n".join(lines) for heading, lines in sections.items()}


def _fence_delimiter(line: str) -> str | None:
    stripped = line.lstrip()
    if len(line) - len(stripped) > 3 or not stripped:
        return None
    marker = stripped[0]
    if marker not in {"`", "~"}:
        return None
    length = len(stripped) - len(stripped.lstrip(marker))
    return marker * length if length >= 3 else None


def _normalize_heading(value: str) -> str:
    return "-".join(value.strip().lower().replace("&", "and").split())
