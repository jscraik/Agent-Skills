from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ask.envelope import CallResult, ErrorCode, ErrorObject


@dataclass(frozen=True)
class MemorySource:
    source_id: str
    label: str
    root: Path
    source_type: str = "markdown"
    patterns: tuple[str, ...] = ("*.md", "*.mdx")


MEMORY_SOURCES = (
    MemorySource("harness-memory", "Harness memory", Path(".harness") / "memory"),
    MemorySource("harness-solutions", "Harness solutions", Path(".harness") / "solutions"),
    MemorySource("wiki-learnings", "Skill Ops wiki learnings", Path("Wiki") / "wiki" / "learnings"),
    MemorySource("docs-solutions", "Solution docs", Path("Docs") / "solutions"),
    MemorySource("docs-agent-guidance", "Agent guidance docs", Path("Docs") / "agents"),
    MemorySource("graph-lessons", "Skill graph lessons", Path("Infrastructure") / "artifacts" / "skill-graphs" / "lessons"),
)


def _validation_error(message: str, fix: str) -> CallResult:
    result = CallResult(status="error")
    result.errors.append(ErrorObject(code=ErrorCode.ERR_VALIDATION, message=message, fix_suggestion=fix))
    return result


def _memory_validation_command(
    action: str,
    *args: str,
    source_id: str | None = None,
    limit: int | None = None,
) -> str:
    parts = ["./bin/ask", "memory", action, *args]
    if source_id:
        parts.extend(["--source", source_id])
    if limit is not None:
        parts.extend(["--limit", str(limit)])
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _entry_id(source_id: str, relative_path: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", relative_path.lower()).strip("-")
    return f"{source_id}:{slug or 'root'}"


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        cleaned = value.strip().strip("\"'")
        if cleaned:
            data[key.strip()] = cleaned
    return data


def _body(text: str) -> str:
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        for idx, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[idx + 1 :]).lstrip()
    return text


def _snippet(text: str, query: str | None = None, *, max_len: int = 240) -> str:
    compact = re.sub(r"\s+", " ", _body(text)).strip()
    if not query:
        return compact[:max_len]
    match = re.search(re.escape(query), compact, flags=re.IGNORECASE)
    if not match:
        return compact[:max_len]
    start = max(0, match.start() - 80)
    return compact[start : start + max_len]


def _iter_entries(repo_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for source in MEMORY_SOURCES:
        source_root = repo_root / source.root
        if not source_root.exists():
            continue
        for pattern in source.patterns:
            for path in sorted(source_root.rglob(pattern)):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                relative_path = str(path.relative_to(repo_root))
                stat = path.stat()
                entries.append(
                    {
                        "id": _entry_id(source.source_id, relative_path),
                        "source": {"id": source.source_id, "label": source.label, "type": source.source_type},
                        "source_id": source.source_id,
                        "source_label": source.label,
                        "path": relative_path,
                        "provenance": {
                            "provider": source.source_id,
                            "provider_label": source.label,
                            "repo_relative_path": relative_path,
                        },
                        "title": _frontmatter(text).get("title") or path.stem.replace("-", " ").replace("_", " "),
                        "freshness": {"mtime": int(stat.st_mtime), "size_bytes": stat.st_size},
                        "frontmatter": _frontmatter(text),
                        "snippet": _snippet(text),
                        "_content": text,
                    }
                )
    entries.sort(key=lambda item: (item["source_id"], item["path"]))
    return entries


def _filter_source(entries: list[dict[str, Any]], source_id: str | None) -> list[dict[str, Any]]:
    if source_id is None:
        return entries
    normalized = source_id.strip()
    if not normalized:
        raise ValueError("source must not be blank")
    return [entry for entry in entries if entry["source_id"] == normalized]


def memory_list(repo_root: Path, source_id: str | None = None, limit: int = 20) -> CallResult:
    validation_command = _memory_validation_command("list", source_id=source_id, limit=limit)
    if limit < 0:
        result = _validation_error("memory list limit must be non-negative", "Pass --limit 0 or a positive integer.")
        result.data["validation_commands"] = [validation_command]
        return result
    try:
        entries = _filter_source(_iter_entries(repo_root), source_id)
    except ValueError as exc:
        result = _validation_error(str(exc), "Pass a non-empty --source value or omit --source.")
        result.data["validation_commands"] = [validation_command]
        return result
    public = [{k: v for k, v in entry.items() if k != "_content"} for entry in entries[:limit]]
    result = CallResult()
    result.data["validation_commands"] = [validation_command]
    result.data["memory"] = {
        "schema_version": "memory-provider.v1",
        "agent_summary": f"Listed {len(public)} memory entr{'y' if len(public) == 1 else 'ies'}.",
        "count": len(public),
        "total_count": len(entries),
        "entries": public,
    }
    return result


def memory_read(repo_root: Path, identifier: str) -> CallResult:
    validation_command = _memory_validation_command("read", identifier)
    if not identifier.strip():
        result = _validation_error("memory id must not be blank", "Pass a memory id from memory list.")
        result.data["validation_commands"] = [validation_command]
        return result
    for entry in _iter_entries(repo_root):
        if entry["id"] == identifier or entry["path"] == identifier:
            public = {k: v for k, v in entry.items() if k != "_content"}
            public["content"] = entry["_content"]
            result = CallResult()
            result.data["memory"] = {
                "schema_version": "memory-provider.v1",
                "agent_summary": f"Read memory entry {entry['id']}.",
                "entry": public,
            }
            result.data["validation_commands"] = [validation_command]
            return result
    result = _validation_error(f"memory id not found: {identifier}", "Run memory list and use an id from the result.")
    result.data["validation_commands"] = [validation_command]
    return result


def memory_search(repo_root: Path, query: str, source_id: str | None = None, limit: int = 20) -> CallResult:
    validation_command = _memory_validation_command("search", query, source_id=source_id, limit=limit)
    if not query.strip():
        result = _validation_error("memory search query must not be blank", "Pass a non-empty search query.")
        result.data["validation_commands"] = [validation_command]
        return result
    if limit < 0:
        result = _validation_error("memory search limit must be non-negative", "Pass --limit 0 or a positive integer.")
        result.data["validation_commands"] = [validation_command]
        return result
    try:
        entries = _filter_source(_iter_entries(repo_root), source_id)
    except ValueError as exc:
        result = _validation_error(str(exc), "Pass a non-empty --source value or omit --source.")
        result.data["validation_commands"] = [validation_command]
        return result
    needle = query.lower()
    matches: list[dict[str, Any]] = []
    for entry in entries:
        haystack = "\n".join([entry["title"], entry["path"], entry["_content"]]).lower()
        if needle not in haystack:
            continue
        public = {k: v for k, v in entry.items() if k != "_content"}
        public["snippet"] = _snippet(entry["_content"], query)
        matches.append(public)
    result = CallResult()
    result.data["validation_commands"] = [validation_command]
    result.data["memory"] = {
        "schema_version": "memory-provider.v1",
        "agent_summary": f"Found {len(matches[:limit])} memory entr{'y' if len(matches[:limit]) == 1 else 'ies'}.",
        "query": query,
        "count": len(matches[:limit]),
        "total_count": len(matches),
        "results": matches[:limit],
    }
    return result
