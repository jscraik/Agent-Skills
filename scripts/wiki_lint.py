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


def _read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}

    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = FRONTMATTER_KEY_RE.match(line.strip())
        if not match:
            continue
        key = match.group(1).strip()
        value = match.group(2).strip()
        out[key] = value
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


def _resolve_link(source: Path, target: str, wiki_root: Path) -> Path | None:
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
            for key in ("title", "type", "status", "last_reviewed"):
                if key not in frontmatter:
                    issues.append(Issue("missing-frontmatter", "error", rel, f"Missing frontmatter key: {key}"))

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
            resolved = _resolve_link(page, link, wiki_root)
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
            resolved = _resolve_link(index_path, link, wiki_root)
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
        default="docs/skill-ops-wiki/wiki",
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

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
