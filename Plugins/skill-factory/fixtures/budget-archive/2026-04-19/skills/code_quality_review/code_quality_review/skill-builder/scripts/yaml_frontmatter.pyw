"""
yaml_frontmatter.py

Canonical SKILL.md frontmatter parser shared across skill-builder scripts.

Replaces four independent copy-paste implementations in:
  skill_gate.py, analyze_skill.py, upgrade_skill.py, quick_validate.py

Public API
----------
read_text(path)
    Read a file as strict UTF-8. Raises ValueError on encoding errors.

parse_frontmatter(raw, *, strict_line1=False)
    Parse ``---``-delimited YAML frontmatter from raw SKILL.md text.
    Returns (frontmatter_dict, body_str, fm_start_line, fm_end_line).

resolve_skill_md_path(path_like)
    Accept a skill directory or a direct SKILL.md path; return a Path.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # callers that need yaml must ensure it is available

_DELIM_RE = re.compile(r"^\s*---\s*$")


def resolve_skill_md_path(path_like: str | Path) -> Path:
    """Return the resolved SKILL.md path for a skill dir or direct file path."""
    p = Path(path_like).expanduser().resolve()
    return (p / "SKILL.md") if p.is_dir() else p


def read_text(path: Path) -> str:
    """
    Read *path* as strict UTF-8.

    Raises
    ------
    ValueError
        If the file contains non-UTF-8 bytes, with the byte offset in the
        message. Callers should surface this as a SKILL.md format error
        rather than silently replacing replacement characters.
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"SKILL.md contains non-UTF-8 bytes at position {exc.start} "
            f"(0x{path.read_bytes()[exc.start]:02x}): {path}"
        ) from exc


def parse_frontmatter(
    raw: str,
    *,
    strict_line1: bool = False,
) -> Tuple[Dict[str, Any], str, int, int]:
    """
    Parse YAML frontmatter from raw SKILL.md text.

    Parameters
    ----------
    raw:
        Full file contents as a string.
    strict_line1:
        When True the very first line must be ``---`` (no leading blank
        lines permitted).  When False the first *non-empty* line must be
        ``---``.

    Returns
    -------
    (frontmatter_dict, body_text, fm_start_line, fm_end_line)
        Line numbers are 1-indexed; *fm_start_line* is the line of the
        opening ``---``, *fm_end_line* is the line of the closing ``---``.

    Raises
    ------
    ValueError
        On any structural or parse error (empty file, missing delimiter,
        tabs in YAML, invalid YAML, non-mapping frontmatter).
    """
    lines = raw.splitlines(keepends=True)
    if not lines:
        raise ValueError("SKILL.md is empty.")

    if strict_line1:
        if not _DELIM_RE.match(lines[0]):
            raise ValueError("Strict mode: frontmatter must start on line 1 with `---`.")
        start_idx: int = 0
    else:
        _found: int | None = next(
            (i for i, ln in enumerate(lines) if ln.strip()), None
        )
        if _found is None:
            raise ValueError("SKILL.md has no content.")
        start_idx = _found
        if not _DELIM_RE.match(lines[start_idx]):
            raise ValueError(
                "Missing YAML frontmatter. Expected `---` as the first non-empty line."
            )

    end_idx: int | None = next(
        (j for j in range(start_idx + 1, len(lines)) if _DELIM_RE.match(lines[j])),
        None,
    )
    if end_idx is None:
        raise ValueError("Unterminated YAML frontmatter — missing closing `---`.")

    yaml_text = "".join(lines[start_idx + 1 : end_idx])

    if "\t" in yaml_text:
        raise ValueError(
            "Frontmatter YAML must use spaces for indentation — tabs found."
        )

    if yaml is None:
        raise RuntimeError(
            "PyYAML is not installed. Install it or use the pyyaml venv:\n"
            "  ~/.venvs/pyyaml/bin/python <script>"
        )

    try:
        fm_obj = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in frontmatter: {exc}") from exc

    if fm_obj is None:
        fm: Dict[str, Any] = {}
    elif isinstance(fm_obj, dict):
        fm = fm_obj
    else:
        raise ValueError("Frontmatter YAML must be a mapping (key: value pairs).")

    body = "".join(lines[end_idx + 1 :]).lstrip("\n")
    return fm, body, start_idx + 1, end_idx + 1
