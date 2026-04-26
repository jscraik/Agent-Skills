#!/usr/bin/env python3
"""Lint the Skill Ops Wiki for link integrity, index coverage, and review freshness."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\n]+)\)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_KEY_RE = re.compile(r"^([a-z_]+):\s*(.+?)\s*$")


@dataclass
class Issue:
    code: str
    severity: str
    path: str
    message: str


def _read_frontmatter(path: Path) -> dict[str, str | list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}

    out: dict[str, str | list[str]] = {}
    idx = 1
    while idx < len(lines):
        line = lines[idx].strip()
        if line == "---":
            break
        match = FRONTMATTER_KEY_RE.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            out[key] = value
            idx += 1
        elif line.endswith(":"):
            # Multi-line list handling (e.g., sources:)
            key = line.rstrip(":")
            list_values: list[str] = []
            idx += 1
            while idx < len(lines):
                next_line = lines[idx]
                if next_line.strip().startswith("- "):
                    list_values.append(next_line.strip()[2:].strip())
                    idx += 1
                elif next_line.strip() and not next_line.strip().startswith("#"):
                    break
                else:
                    idx += 1
                    break
            out[key] = list_values
        else:
            idx += 1
    return out


def _extract_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    links: list[str] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target:
            continue
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(target)
    return links


def _resolve_link(source: Path, target: str) -> Path | None:
    target_no_anchor = target.split("#", 1)[0].strip()
    if not target_no_anchor:
        return None
    if target_no_anchor.startswith("/"):
        return None
    return (source.parent / target_no_anchor).resolve()


def _collect_wiki_pages(wiki_root: Path) -> list[Path]:
    pages = sorted(p.resolve() for p in wiki_root.rglob("*.md"))
    return pages


def lint_wiki(wiki_root: Path, max_age_days: int, now: date) -> list[Issue]:
    wiki_root = wiki_root.resolve()
    issues: list[Issue] = []
    pages = _collect_wiki_pages(wiki_root)
    page_set = {p.resolve() for p in pages}

    inbound_count: dict[Path, int] = {p: 0 for p in pages}
    index_path = (wiki_root / "index.md").resolve()
    exempt_orphans = {index_path, (wiki_root / "log.md").resolve()}

    for page in pages:
        rel = page.relative_to(wiki_root).as_posix()

        frontmatter = _read_frontmatter(page)
        if rel.startswith(("failures/", "playbooks/")):
            for key in ("title", "type", "status", "last_reviewed", "sources"):
                if key not in frontmatter:
                    issues.append(Issue("missing-frontmatter", "error", rel, f"Missing frontmatter key: {key}"))

            # Validate sources field content
            if "sources" in frontmatter:
                sources_value = frontmatter["sources"]
                if isinstance(sources_value, list):
                    if not sources_value:
                        issues.append(Issue("empty-sources", "error", rel, "sources field is empty (must contain at least one entry)"))
                elif isinstance(sources_value, str) and not sources_value.strip():
                    issues.append(Issue("empty-sources", "error", rel, "sources field is empty (must contain at least one entry)"))

            last_reviewed = frontmatter.get("last_reviewed", "")
            if last_reviewed and DATE_RE.match(last_reviewed):
                reviewed_on = datetime.strptime(last_reviewed, "%Y-%m-%d").date()
                age_days = (now - reviewed_on).days
                if age_days > max_age_days:
                    issues.append(
                        Issue(
                            "stale-page",
                            "warning",
                            rel,
                            f"last_reviewed is {age_days} days old (max {max_age_days}).",
                        )
                    )
            elif last_reviewed:
                issues.append(Issue("bad-date", "error", rel, f"Invalid last_reviewed format: {last_reviewed}"))

        for link in _extract_links(page):
            resolved = _resolve_link(page, link)
            if resolved is None:
                continue
            if resolved.suffix != ".md":
                continue
            if resolved not in page_set:
                issues.append(Issue("broken-link", "error", rel, f"Link target not found: {link}"))
                continue
            inbound_count[resolved] = inbound_count.get(resolved, 0) + 1

    # Ensure all structured pages are discoverable from index.
    index_links = set()
    if index_path.exists():
        for link in _extract_links(index_path):
            resolved = _resolve_link(index_path, link)
            if resolved is not None:
                index_links.add(resolved)

    for page in pages:
        rel = page.relative_to(wiki_root).as_posix()
        if rel in {"index.md", "log.md"}:
            continue
        if page not in index_links:
            issues.append(Issue("missing-index-link", "error", rel, "Page is not linked from wiki/index.md."))

    for page, count in inbound_count.items():
        if page in exempt_orphans:
            continue
        if count == 0:
            rel = page.relative_to(wiki_root).as_posix()
            issues.append(Issue("orphan-page", "warning", rel, "No inbound markdown links found."))

    return issues


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint the Skill Ops Wiki.")
    parser.add_argument(
        "--wiki-root",
        default="Wiki/wiki",
        help="Path to wiki root directory.",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=60,
        help="Maximum allowed age for last_reviewed before warning.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    wiki_root = Path(args.wiki_root).resolve()
    if not wiki_root.exists():
        print(f"[wiki-lint] ERROR: wiki root not found: {wiki_root}", file=sys.stderr)
        return 2

    issues = lint_wiki(wiki_root, max_age_days=args.max_age_days, now=datetime.now(timezone.utc).date())
    if not issues:
        print("[wiki-lint] PASS: no issues found")
        return 0

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    print(f"[wiki-lint] issues: errors={len(errors)} warnings={len(warnings)}")
    for issue in issues:
        print(f"- [{issue.severity.upper()}] {issue.path} :: {issue.code} :: {issue.message}")

    return 1 if errors or warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
