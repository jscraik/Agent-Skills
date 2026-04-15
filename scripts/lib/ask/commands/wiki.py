#!/usr/bin/env python3
"""Wiki operations for Skill Ops Wiki."""

from __future__ import annotations

import re
import shutil
import subprocess
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ask.envelope import CallResult, ErrorObject

INTENT_TO_DESTINATION = {
    "finding": "failures",
    "playbook": "playbooks",
    "design-asset": "assets/ui",
    "lesson-learned": "learnings",
}

DESTINATION_TO_SECTION = {
    "failures": "Failures",
    "playbooks": "Playbooks",
    "assets/ui": "Assets",
    "learnings": "Learnings",
}


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "note"


def wiki_lint(repo_root: Path, *, wiki_root: str, max_age_days: int) -> CallResult:
    """Run wiki lint checks and return structured output."""
    result = CallResult()

    cmd = [
        "python3",
        "scripts/wiki_lint.py",
        "--wiki-root",
        wiki_root,
        "--max-age-days",
        str(max_age_days),
    ]

    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=False, timeout=60)
        output = process.stdout.strip()
        error_output = process.stderr.strip()

        result.data["wiki_root"] = wiki_root
        result.data["max_age_days"] = max_age_days
        result.data["raw_output"] = output
        if error_output:
            result.data["raw_error"] = error_output

        if process.returncode == 0:
            result.status = "success"
            result.data["message"] = "Wiki lint passed."
            result.metadata["next_steps"] = ["ask wiki ingest '<title>' --source '<source>' --summary '<summary>'"]
            return result

        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=output or error_output or "Wiki lint failed.",
                fix_suggestion="Review lint output and update docs/skill-ops-wiki/wiki pages or links.",
            )
        )
        return result
    except (OSError, subprocess.TimeoutExpired) as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Failed to execute wiki_lint: {e}",
                fix_suggestion="Ensure scripts/wiki_lint.py exists and is executable.",
            )
        )
        return result


def _safe_summary(value: str) -> str:
    compact = " ".join(value.split())
    if len(compact) <= 110:
        return compact
    return compact[:107].rstrip() + "..."


def _strip_frontmatter(markdown: str) -> str:
    lines = markdown.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                return "\n".join(lines[idx + 1 :]).lstrip("\n")
    return markdown


def _with_collision_suffix(directory: Path, filename: str, timestamp_compact: str) -> str:
    candidate = directory / filename
    if not candidate.exists():
        return filename

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    base = f"{stem}-{timestamp_compact}"

    candidate_name = f"{base}{suffix}"
    if not (directory / candidate_name).exists():
        return candidate_name

    counter = 1
    while True:
        candidate_name = f"{base}-{counter}{suffix}"
        if not (directory / candidate_name).exists():
            return candidate_name
        counter += 1


def _default_index() -> str:
    return (
        "# Skill Ops Wiki Index\n\n"
        "## Table of Contents\n"
        "- [Failures](#failures)\n"
        "- [Playbooks](#playbooks)\n"
        "- [Assets](#assets)\n"
        "- [Learnings](#learnings)\n"
        "- [Operations](#operations)\n\n"
        "## Failures\n\n"
        "| Page | Summary |\n"
        "| --- | --- |\n\n"
        "## Playbooks\n\n"
        "| Page | Summary |\n"
        "| --- | --- |\n\n"
        "## Assets\n\n"
        "| Page | Summary |\n"
        "| --- | --- |\n\n"
        "## Learnings\n\n"
        "| Page | Summary |\n"
        "| --- | --- |\n\n"
        "## Operations\n\n"
    )


def _section_for_destination(destination_rel: str) -> str:
    normalized = destination_rel.strip("/")
    for prefix, section in DESTINATION_TO_SECTION.items():
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return section
    return "Operations"


def _ensure_section_block(text: str, section: str) -> str:
    heading = f"## {section}"
    if heading in text:
        return text
    if not text.endswith("\n"):
        text += "\n"
    if section in {"Failures", "Playbooks", "Assets", "Learnings"}:
        return text + f"\n{heading}\n\n| Page | Summary |\n| --- | --- |\n"
    return text + f"\n{heading}\n\n"


def _upsert_index_entry(index_path: Path, *, title: str, relative_link: str, summary: str, destination_rel: str) -> None:
    if not index_path.exists():
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(_default_index(), encoding="utf-8")

    text = index_path.read_text(encoding="utf-8")
    section = _section_for_destination(destination_rel)
    text = _ensure_section_block(text, section)

    section_pattern = re.compile(
        rf"(?ms)^## {re.escape(section)}\n(.*?)(?=^## |\Z)"
    )
    match = section_pattern.search(text)
    if not match:
        return

    block = match.group(1)
    link_token = f"]({relative_link})"

    if section in {"Failures", "Playbooks", "Assets", "Learnings"}:
        row = f"| [{title}]({relative_link}) | {summary} |"
        rows = block.splitlines()
        if "| Page | Summary |" not in block:
            rows = ["", "| Page | Summary |", "| --- | --- |"] + rows

        replaced = False
        new_rows: list[str] = []
        for line in rows:
            if link_token in line and line.strip().startswith("|"):
                new_rows.append(row)
                replaced = True
            else:
                new_rows.append(line)
        if not replaced:
            new_rows.append(row)
        new_block = "\n".join(new_rows).rstrip() + "\n\n"
    else:
        line = f"- [{title}]({relative_link}) | {summary}"
        rows = [r for r in block.splitlines() if r.strip()]
        replaced = False
        new_rows = []
        for row_line in rows:
            if link_token in row_line:
                new_rows.append(line)
                replaced = True
            else:
                new_rows.append(row_line)
        if not replaced:
            new_rows.append(line)
        new_block = "\n" + "\n".join(new_rows) + "\n\n"

    updated = text[: match.start(1)] + new_block + text[match.end(1) :]
    index_path.write_text(updated, encoding="utf-8")


def wiki_add(
    repo_root: Path,
    *,
    title: str,
    summary: str,
    source: str,
    intent: str,
    status: str,
    destination: Optional[str] = None,
    tags: Optional[list[str]] = None,
    asset_link: Optional[str] = None,
    dry_run: bool = False,
) -> CallResult:
    """Create a triaged wiki note and update index/log links."""
    result = CallResult()

    wiki_root = repo_root / "docs" / "skill-ops-wiki"
    wiki_dir = wiki_root / "wiki"
    index_path = wiki_dir / "index.md"
    log_path = wiki_dir / "log.md"

    cleaned_title = title.strip()
    cleaned_summary = summary.strip()
    cleaned_source = source.strip()
    cleaned_intent = intent.strip().lower()
    cleaned_status = status.strip().lower()

    # Validate intent
    if destination is None and cleaned_intent not in INTENT_TO_DESTINATION:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Unrecognized intent '{cleaned_intent}'. Must be one of: {', '.join(INTENT_TO_DESTINATION.keys())}",
                fix_suggestion="Use a valid intent: finding, playbook, design-asset, or lesson-learned.",
            )
        )
        return result

    # Validate status
    allowed_statuses = {"verified", "fix-now", "draft", "active", "needs-verification"}
    if cleaned_status not in allowed_statuses:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Unrecognized status '{cleaned_status}'. Must be one of: {', '.join(sorted(allowed_statuses))}",
                fix_suggestion="Use a valid status: active, draft, fix-now, needs-verification, or verified.",
            )
        )
        return result

    destination_rel = (destination or INTENT_TO_DESTINATION.get(cleaned_intent, "")).strip().strip("/")
    cleaned_tags = [t.strip() for t in (tags or []) if t and t.strip()]

    if not wiki_root.exists():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skill Ops Wiki not found: {wiki_root}",
                fix_suggestion="Initialize docs/skill-ops-wiki before adding triaged notes.",
            )
        )
        return result

    if not cleaned_title:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Title cannot be empty."))
        return result
    if not cleaned_summary:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Summary cannot be empty."))
        return result
    if not cleaned_source:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Source cannot be empty."))
        return result
    if not destination_rel:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"No destination resolved for intent '{cleaned_intent}'.",
                fix_suggestion="Pass --destination or use intent: finding|playbook|design-asset|lesson-learned.",
            )
        )
        return result

    # Sanitize destination_rel to prevent path traversal
    destination_parts = []
    for part in destination_rel.split("/"):
        part = part.strip()
        if part and part != ".." and part != ".":
            destination_parts.append(part)

    if not destination_parts:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Destination path is invalid or empty after sanitization.",
                fix_suggestion="Use a valid destination path without '..' or '.' segments.",
            )
        )
        return result

    destination_rel = "/".join(destination_parts)

    timestamp = datetime.now(timezone.utc)
    timestamp_compact = timestamp.strftime("%Y%m%dT%H%M%SZ")
    date_iso = timestamp.strftime("%Y-%m-%d")
    slug = _slugify(cleaned_title)

    note_dir = wiki_dir / destination_rel
    note_filename = f"{slug}.md"
    note_filename = _with_collision_suffix(note_dir, note_filename, timestamp_compact)
    note_path = note_dir / note_filename

    # Validate that note_path is within wiki_dir
    try:
        resolved_note_path = note_path.resolve()
        resolved_wiki_dir = wiki_dir.resolve()
        note_rel = resolved_note_path.relative_to(resolved_wiki_dir).as_posix()
    except ValueError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Destination path escapes wiki directory.",
                fix_suggestion="Use a valid destination within the wiki directory.",
            )
        )
        return result

    tags_line = ", ".join(cleaned_tags) if cleaned_tags else "none"
    safe_summary = _safe_summary(cleaned_summary)
    if destination_rel.startswith("failures"):
        frontmatter_type = "failure"
        frontmatter_status = "active" if cleaned_status in {"verified", "fix-now"} else "draft"
    elif destination_rel.startswith("playbooks"):
        frontmatter_type = "playbook"
        frontmatter_status = "active" if cleaned_status in {"verified", "fix-now"} else "draft"
    else:
        frontmatter_type = cleaned_intent
        frontmatter_status = cleaned_status

    # Build frontmatter dict and serialize with YAML to prevent injection
    frontmatter_dict = {
        "title": cleaned_title,
        "type": frontmatter_type,
        "status": frontmatter_status,
        "triage_status": cleaned_status,
        "last_reviewed": date_iso,
        "sources": [cleaned_source],
    }
    try:
        import yaml  # lazy import — optional dep; not needed for most ask commands
    except (ImportError, ModuleNotFoundError):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="PyYAML is required for wiki features but is not installed.",
                fix_suggestion="Install PyYAML with: pip install PyYAML",
            )
        )
        return result
    frontmatter_yaml = yaml.safe_dump(frontmatter_dict, default_flow_style=False, allow_unicode=True)
    frontmatter_lines = [
        "---",
        frontmatter_yaml.rstrip(),
        "---",
        "",
    ]

    body = (
        f"# {cleaned_title}\n\n"
        "## Triage\n\n"
        f"- Intent: `{cleaned_intent}`\n"
        f"- Status: `{cleaned_status}`\n"
        f"- Destination: `docs/skill-ops-wiki/wiki/{destination_rel}`\n"
        f"- Tags: {tags_line}\n\n"
        "## Summary\n\n"
        f"{cleaned_summary}\n\n"
        "## Source\n\n"
        f"- {cleaned_source}\n"
    )
    if asset_link:
        body += f"\n## Assets\n\n- [{Path(asset_link).name}]({asset_link})\n"

    log_entry = (
        f"\n## [{date_iso}] triage | {cleaned_title}\n\n"
        f"- Intent: `{cleaned_intent}`\n"
        f"- Status: `{cleaned_status}`\n"
        f"- Source: {cleaned_source}\n"
        f"- Note: `docs/skill-ops-wiki/wiki/{note_rel}`\n"
    )

    result.data["title"] = cleaned_title
    result.data["intent"] = cleaned_intent
    result.data["status"] = cleaned_status
    result.data["destination"] = destination_rel
    result.data["source"] = cleaned_source
    result.data["summary"] = cleaned_summary
    result.data["tags"] = cleaned_tags
    if asset_link:
        result.data["asset_link"] = asset_link
    result.data["note_path"] = f"docs/skill-ops-wiki/wiki/{note_rel}"
    result.data["index_path"] = "docs/skill-ops-wiki/wiki/index.md"
    result.data["log_path"] = "docs/skill-ops-wiki/wiki/log.md"
    result.data["dry_run"] = dry_run

    if dry_run:
        result.status = "success"
        result.data["preview_note"] = "\n".join(frontmatter_lines) + body
        result.data["preview_index_link"] = f"- [{cleaned_title}]({note_rel}) | {safe_summary}"
        result.data["preview_log_entry"] = log_entry.strip()
        result.metadata["next_steps"] = [
            f"ask wiki add \"{cleaned_title}\" --summary \"{cleaned_summary}\" --source \"{cleaned_source}\" --intent {cleaned_intent} --status {cleaned_status}",
            "ask wiki lint",
        ]
        return result

    note_dir.mkdir(parents=True, exist_ok=True)
    note_path.write_text("\n".join(frontmatter_lines) + body + "\n", encoding="utf-8")

    _upsert_index_entry(
        index_path,
        title=cleaned_title,
        relative_link=note_rel,
        summary=safe_summary,
        destination_rel=destination_rel,
    )

    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("# Skill Ops Wiki Log\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(log_entry)

    result.status = "success"
    result.data["message"] = f"Added triaged wiki note at docs/skill-ops-wiki/wiki/{note_rel}"
    result.metadata["next_steps"] = ["ask wiki lint"]
    return result


def _extract_title(markdown: str, fallback: str) -> str:
    body = _strip_frontmatter(markdown)
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _extract_snippet(markdown: str, tokens: list[str]) -> str:
    body = _strip_frontmatter(markdown)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("#"):
            continue
        if line.startswith("|") and line.endswith("|"):
            continue
        lowered = line.lower()
        if any(token in lowered for token in tokens):
            if len(line) <= 180:
                return line
            return line[:177].rstrip() + "..."
    for line in lines:
        if not line.startswith("#"):
            if len(line) <= 180:
                return line
            return line[:177].rstrip() + "..."
    return ""


def wiki_query(
    repo_root: Path,
    *,
    query: str,
    wiki_root: str = "docs/skill-ops-wiki/wiki",
    limit: int = 5,
) -> CallResult:
    """Search wiki pages by keyword relevance and return ranked results."""
    result = CallResult()
    cleaned_query = query.strip()
    if not cleaned_query:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Query cannot be empty."))
        return result

    wiki_root_path = (repo_root / wiki_root).resolve()
    if not wiki_root_path.exists():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Wiki root not found: {wiki_root_path}",
                fix_suggestion="Ensure docs/skill-ops-wiki/wiki exists before querying.",
            )
        )
        return result

    tokens = [t for t in re.split(r"[^a-z0-9]+", cleaned_query.lower()) if t]
    pages = sorted(p for p in wiki_root_path.rglob("*.md") if p.name not in {"index.md", "log.md"})

    ranked = []
    for page in pages:
        markdown = page.read_text(encoding="utf-8", errors="replace")
        search_space = _strip_frontmatter(markdown)
        lowered = search_space.lower()
        score = 0
        for token in tokens:
            hits = lowered.count(token)
            score += hits
            if token in page.stem.lower():
                score += 4
            if token in str(page.relative_to(wiki_root_path)).lower():
                score += 2
        if score <= 0:
            continue
        title = _extract_title(markdown, page.stem.replace("-", " ").title())
        snippet = _extract_snippet(markdown, tokens)
        try:
            display_path = page.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            display_path = os.path.relpath(page.resolve(), repo_root.resolve()).replace("\\", "/")
        ranked.append(
            {
                "score": score,
                "title": title,
                "path": display_path,
                "snippet": snippet,
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["path"]))
    capped = ranked[: max(1, min(limit, 25))]

    result.status = "success"
    result.data["query"] = cleaned_query
    result.data["count"] = len(ranked)
    result.data["results"] = capped
    if not capped:
        result.data["message"] = "No matching wiki pages found."
        result.metadata["next_steps"] = ["ask wiki ingest '<title>' --source '<source>' --summary '<summary>'"]
    else:
        result.data["message"] = f"Found {len(capped)} matching wiki page(s)."
        result.metadata["next_steps"] = [
            "ask wiki add --interactive",
            "ask wiki lint",
        ]
    return result


def wiki_add_asset(
    repo_root: Path,
    *,
    asset_path: str,
    title: str,
    summary: str,
    source: str = "",
    status: str = "verified",
    destination: str = "assets/ui",
    tags: Optional[list[str]] = None,
    dry_run: bool = False,
) -> CallResult:
    """Copy an asset into wiki raw storage and add a linked wiki asset note."""
    result = CallResult()
    wiki_root = repo_root / "docs" / "skill-ops-wiki"
    raw_assets_dir = wiki_root / "raw" / "assets"

    asset_input = Path(asset_path).expanduser()
    if not asset_input.is_absolute():
        asset_input = (repo_root / asset_input).resolve()
    else:
        asset_input = asset_input.resolve()

    if not asset_input.exists() or not asset_input.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Asset file not found: {asset_input}",
                fix_suggestion="Provide an existing screenshot/image path.",
            )
        )
        return result

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ext = asset_input.suffix or ".bin"
    asset_slug = _slugify(title or asset_input.stem)
    stored_name = f"{timestamp}-{asset_slug}{ext.lower()}"
    safe_name = _with_collision_suffix(raw_assets_dir, stored_name, timestamp)
    stored_path = raw_assets_dir / safe_name
    stored_repo_rel = f"docs/skill-ops-wiki/raw/assets/{safe_name}"
    markdown_asset_link = f"../../raw/assets/{safe_name}"

    # Preflight validation before mutating storage
    preflight_result = wiki_add(
        repo_root,
        title=title,
        summary=summary,
        source=source.strip() or str(asset_input),
        intent="design-asset",
        status=status,
        destination=destination,
        tags=tags or [],
        asset_link=markdown_asset_link,
        dry_run=True,
    )

    if preflight_result.status == "error":
        return preflight_result

    if not dry_run:
        raw_assets_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset_input, stored_path)

    note_result = wiki_add(
        repo_root,
        title=title,
        summary=summary,
        source=source.strip() or str(asset_input),
        intent="design-asset",
        status=status,
        destination=destination,
        tags=tags or [],
        asset_link=markdown_asset_link,
        dry_run=dry_run,
    )
    note_result.data["asset_source"] = str(asset_input)
    note_result.data["asset_stored_path"] = stored_repo_rel
    note_result.data["asset_link"] = markdown_asset_link
    if note_result.status == "success":
        next_steps = note_result.metadata.get("next_steps", [])
        if "ask wiki lint" not in next_steps:
            next_steps.append("ask wiki lint")
        note_result.metadata["next_steps"] = next_steps
    return note_result


def wiki_ingest(
    repo_root: Path,
    *,
    title: str,
    sources: list[str],
    summary: str,
    tags: list[str],
    dry_run: bool = False,
) -> CallResult:
    """Capture a raw source ingest note and append a wiki log entry."""
    result = CallResult()

    wiki_root = repo_root / "docs" / "skill-ops-wiki"
    raw_dir = wiki_root / "raw"
    log_path = wiki_root / "wiki" / "log.md"

    if not wiki_root.exists():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skill Ops Wiki not found: {wiki_root}",
                fix_suggestion="Initialize docs/skill-ops-wiki before ingesting.",
            )
        )
        return result

    if not title.strip():
        result.status = "error"
        result.errors.append(
            ErrorObject(code="ERR_VALIDATION", message="Ingest title cannot be empty.")
        )
        return result

    timestamp = datetime.now(timezone.utc)
    timestamp_compact = timestamp.strftime("%Y%m%dT%H%M%SZ")
    date_iso = timestamp.strftime("%Y-%m-%d")
    slug = _slugify(title)
    raw_filename = f"{timestamp_compact}-{slug}.md"
    raw_filename = _with_collision_suffix(raw_dir, raw_filename, timestamp_compact)
    raw_path = raw_dir / raw_filename

    cleaned_sources = [s.strip() for s in sources if s and s.strip()]
    cleaned_tags = [t.strip() for t in tags if t and t.strip()]

    sources_block = "\n".join(f"- {src}" for src in cleaned_sources) if cleaned_sources else "- (none provided)"
    tags_line = ", ".join(cleaned_tags) if cleaned_tags else "none"

    raw_body = (
        f"# Raw Ingest: {title.strip()}\n\n"
        f"- Captured: {timestamp.isoformat()}\n"
        f"- Tags: {tags_line}\n\n"
        "## Sources\n\n"
        f"{sources_block}\n\n"
        "## Summary\n\n"
        f"{summary.strip()}\n"
    )

    log_entry = (
        f"\n## [{date_iso}] ingest | {title.strip()}\n\n"
        f"- Source(s): {', '.join(cleaned_sources) if cleaned_sources else '(none provided)'}\n"
        f"- Summary: {summary.strip()}\n"
        f"- Raw note: `docs/skill-ops-wiki/raw/{raw_filename}`\n"
    )

    result.data["title"] = title.strip()
    result.data["sources"] = cleaned_sources
    result.data["summary"] = summary.strip()
    result.data["tags"] = cleaned_tags
    result.data["raw_note"] = f"docs/skill-ops-wiki/raw/{raw_filename}"
    result.data["log_file"] = "docs/skill-ops-wiki/wiki/log.md"
    result.data["dry_run"] = dry_run

    if dry_run:
        result.status = "success"
        result.data["preview_raw_note"] = raw_body
        result.data["preview_log_entry"] = log_entry.strip()
        result.metadata["next_steps"] = [
            f"ask wiki ingest \"{title.strip()}\" --summary \"{summary.strip()}\" --source \"<source>\"",
            "ask wiki lint",
        ]
        return result

    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw_body + "\n", encoding="utf-8")

    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("# Skill Ops Wiki Log\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(log_entry)

    result.status = "success"
    result.data["message"] = f"Ingested source note at docs/skill-ops-wiki/raw/{raw_filename}"
    result.metadata["next_steps"] = ["ask wiki lint"]
    return result