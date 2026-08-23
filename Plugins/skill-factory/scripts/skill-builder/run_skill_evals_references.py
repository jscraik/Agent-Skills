"""Validate and attach package-local references to skill evaluation cases."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from run_skill_evals_core import EvalCase, _normalize_string_list

MAX_REFERENCE_BYTES = 64 * 1024
MAX_CASE_REFERENCE_BYTES = 256 * 1024


def _skill_dir_for_evals(evals_path: Path) -> Path:
    if evals_path.parent.name == "references":
        return evals_path.parent.parent
    return evals_path.parent


def _resolve_reference(skill_dir: Path, declared_path: str) -> Path:
    relative = Path(declared_path)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("references",):
        raise ValueError(f"reference_paths entry must stay under references/: {declared_path}")
    target = skill_dir / relative
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"reference_paths entry must be a package-local regular file: {declared_path}")
    resolved = target.resolve()
    try:
        resolved.relative_to(skill_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"reference_paths entry escapes the skill package: {declared_path}") from exc
    return resolved


def _render_case_references(skill_dir: Path, reference_paths: Sequence[str]) -> str:
    blocks: List[str] = []
    total_bytes = 0
    for declared_path in reference_paths:
        resolved = _resolve_reference(skill_dir, declared_path)
        try:
            size_bytes = resolved.stat().st_size
            if size_bytes > MAX_REFERENCE_BYTES:
                raise ValueError(
                    f"reference_paths entry exceeds {MAX_REFERENCE_BYTES} bytes: {declared_path}"
                )
            content = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError(f"reference_paths entry could not be read: {declared_path}") from exc
        size_bytes = len(content.encode("utf-8"))
        if size_bytes > MAX_REFERENCE_BYTES:
            raise ValueError(
                f"reference_paths entry exceeds {MAX_REFERENCE_BYTES} bytes: {declared_path}"
            )
        total_bytes += size_bytes
        if total_bytes > MAX_CASE_REFERENCE_BYTES:
            raise ValueError(
                "reference_paths entries exceed "
                f"{MAX_CASE_REFERENCE_BYTES} cumulative bytes at: {declared_path}"
            )
        blocks.append(f'<REFERENCE path="{declared_path}">\n{content}\n</REFERENCE>')
    if not blocks:
        return ""
    return "Selected package references:\n\n" + "\n\n".join(blocks)


def _case_reference_paths(raw_case: Any, case_number: int) -> Tuple[str, ...]:
    if not isinstance(raw_case, dict):
        raise ValueError(f"Case #{case_number} must be a mapping.")
    return _normalize_string_list(
        raw_case.get("reference_paths"),
        field_name="reference_paths",
        case_number=case_number,
    )


def _prompt_with_references(prompt: str, rendered_references: str) -> str:
    if not rendered_references:
        return prompt
    return f"{rendered_references}\n\nUser task:\n{prompt}"


def attach_declared_references(
    evals_path: Path,
    cases: Sequence[EvalCase],
    document: Dict[str, Any],
) -> List[EvalCase]:
    """Return cases with validated reference paths and prompt context attached."""
    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list) or len(raw_cases) != len(cases):
        raise ValueError("eval cases changed while declared references were being attached")
    skill_dir = _skill_dir_for_evals(evals_path)
    result: List[EvalCase] = []
    for case_number, (case, raw_case) in enumerate(zip(cases, raw_cases), 1):
        reference_paths = _case_reference_paths(raw_case, case_number)
        rendered = _render_case_references(skill_dir, reference_paths)
        result.append(
            replace(
                case,
                prompt=_prompt_with_references(case.prompt, rendered),
                reference_paths=reference_paths,
            )
        )
    return result


__all__ = [name for name in globals() if not name.startswith("__")]
