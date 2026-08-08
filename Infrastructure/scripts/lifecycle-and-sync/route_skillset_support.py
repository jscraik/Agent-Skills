"""Manifest and text-scoring helpers for :mod:`route_skillset`."""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import MappingProxyType
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES
from skillset_model import rel, repo_root

DEFAULT_SKILLSETS_DIR = repo_root() / ".skillsets"

STOPWORDS = frozenset({
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "but",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "should",
    "so",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
})

# TOKEN_RE captures alphanumeric tokens with optional hyphens.
# Minimum token length is 1 character to include single-letter terms like "i".
# The second character group is optional to allow single-character tokens.
TOKEN_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
TOKEN_ALIASES = MappingProxyType({
    "verification": "verify",
})


def tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in TOKEN_RE.findall(text.lower()):
        cleaned = token.strip("-")
        if not cleaned:
            continue
        if cleaned in STOPWORDS:
            continue
        tokens.add(cleaned)
        if cleaned in TOKEN_ALIASES:
            tokens.add(TOKEN_ALIASES[cleaned])
        tokens.update(part for part in cleaned.split("-") if part and part not in STOPWORDS)
        tokens.update(TOKEN_ALIASES[part] for part in cleaned.split("-") if part in TOKEN_ALIASES)
    return tokens


def normalize_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _source_path_exists_within_root(source_root: Path, source_path: Path) -> bool:
    candidate = source_root / source_path
    if not candidate.is_file():
        return False
    try:
        candidate.resolve().relative_to(source_root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _parse_manifest_row(
    line: str,
    *,
    line_no: int,
    manifest_path: Path,
    source_roots: list[Path],
) -> dict[str, Any]:
    try:
        row = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid manifest JSON at {rel(manifest_path)}:{line_no}: {exc}") from exc
    if not isinstance(row, dict):
        raise ValueError(f"Invalid manifest row at {rel(manifest_path)}:{line_no}: expected JSON object")
    _validate_manifest_fields(row, line_no=line_no, manifest_path=manifest_path)
    _validate_manifest_source(row, line_no=line_no, manifest_path=manifest_path, source_roots=source_roots)
    _validate_manifest_triggers(row, line_no=line_no, manifest_path=manifest_path)
    return row


def _validate_manifest_fields(row: dict[str, Any], *, line_no: int, manifest_path: Path) -> None:
    for field in ("id", "description", "level", "source_path"):
        if not isinstance(row.get(field), str) or not row.get(field):
            raise ValueError(
                f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field {field!r} must be a non-empty string"
            )


def _validate_manifest_source(
    row: dict[str, Any], *, line_no: int, manifest_path: Path, source_roots: list[Path]
) -> None:
    source_path = Path(str(row["source_path"]))
    if source_path.is_absolute() or ".." in source_path.parts:
        raise ValueError(
            f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field 'source_path' must be a repo-relative path"
        )
    if not any(_source_path_exists_within_root(root, source_path) for root in source_roots):
        raise ValueError(
            f"Invalid manifest row at {rel(manifest_path)}:{line_no}: source_path {row['source_path']!r} does not exist"
        )


def _validate_manifest_triggers(row: dict[str, Any], *, line_no: int, manifest_path: Path) -> None:
    triggers = row.get("triggers", [])
    if not isinstance(triggers, list) or any(not isinstance(item, str) for item in triggers):
        raise ValueError(
            f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field 'triggers' must be a list of strings"
        )


def read_manifest(skill_set: str, skillsets_dir: Path = DEFAULT_SKILLSETS_DIR) -> tuple[list[dict[str, Any]], str | None]:
    if skill_set not in ROOT_SKILL_SET_NAMES:
        return [], "invalid_skill_set"
    manifest_path = skillsets_dir / skill_set / "manifest.jsonl"
    if not manifest_path.is_file():
        return [], "manifest_missing"
    source_roots = [skillsets_dir.parent, repo_root()]
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        rows.append(
            _parse_manifest_row(
                line,
                line_no=line_no,
                manifest_path=manifest_path,
                source_roots=source_roots,
            )
        )
    return rows, None


def score_row(row: dict[str, Any], task: str) -> tuple[float, list[str]]:
    task_phrase = normalize_phrase(task)
    phrase_candidates = [
        normalize_phrase(str(row.get("id", "")).replace("-", " ")),
        *[normalize_phrase(str(item)) for item in row.get("triggers", []) if isinstance(item, str)],
    ]
    for phrase in phrase_candidates:
        if len(phrase.split()) >= 2 and phrase in task_phrase:
            return 1.0, [f"matched phrase '{phrase}'"]

    task_tokens = tokenize(task)
    haystack_parts = [
        str(row.get("id", "")),
        str(row.get("description", "")),
        " ".join(str(item) for item in row.get("triggers", []) if isinstance(item, str)),
    ]
    row_tokens = tokenize(" ".join(haystack_parts))
    if not task_tokens or not row_tokens:
        return 0.0, []
    overlap = task_tokens & row_tokens
    confidence = len(overlap) / max(len(task_tokens), 1)
    reasons = [f"matched term '{term}'" for term in sorted(overlap)[:3]]
    return round(min(confidence, 1.0), 4), reasons


def signal_matches(task_text: str, task_tokens: set[str], signal: str) -> bool:
    signal_text = signal.lower().strip()
    if not signal_text:
        return False
    if signal_text in task_text:
        return True
    signal_tokens = tokenize(signal_text)
    if not signal_tokens:
        return False
    return signal_tokens <= task_tokens


def row_by_id(rows: list[dict[str, Any]], stage_id: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("id") == stage_id:
            return row
    return None
