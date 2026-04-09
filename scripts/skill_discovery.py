#!/usr/bin/env python3
"""Shared skill catalog helpers for counting and rendering the root index."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from selection_policy import (
    EXCLUDED_SCAN_SEGMENTS as POLICY_EXCLUDED_SCAN_SEGMENTS,
    HIDDEN_FLAT_SKILL_NAMES as POLICY_HIDDEN_FLAT_SKILL_NAMES,
    REPO_SCAN_ROOTS as POLICY_REPO_SCAN_ROOTS,
    policy_identity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FLAT_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
REPO_SCAN_ROOTS = POLICY_REPO_SCAN_ROOTS

# Ignore SKILL.md files in implementation/support subtrees that are not
# runtime-selectable skills.
EXCLUDED_REPO_SCAN_SEGMENTS = set(POLICY_EXCLUDED_SCAN_SEGMENTS)

# Keep hidden/internal skills out of runtime discovery. This mirrors
# scripts/sync_skills.sh hidden_flat_skills.
HIDDEN_FLAT_SKILL_NAMES = set(POLICY_HIDDEN_FLAT_SKILL_NAMES)


@dataclass(frozen=True)
class SkillEntry:
    name: str
    source_dir: Path
    category: str
    description: str


def get_policy_identity() -> str:
    return policy_identity()


def _iter_flat_skill_dirs() -> Iterable[Path]:
    if not FLAT_SKILLS_DIR.is_dir():
        return []

    dirs: List[Path] = []
    for item in sorted(FLAT_SKILLS_DIR.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir() and (item / "SKILL.md").exists():
            dirs.append(item)
    return dirs


def _iter_repo_skill_dirs() -> Iterable[Path]:
    dirs: List[Path] = []
    for root_name in REPO_SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for skill_md in sorted(root.rglob("SKILL.md")):
            rel_parts = skill_md.relative_to(root).parts
            if any(part in EXCLUDED_REPO_SCAN_SEGMENTS for part in rel_parts):
                continue
            dirs.append(skill_md.parent)
    return dirs


def _is_plugin_owned_skill_dir(skill_dir: Path) -> bool:
    try:
        rel = skill_dir.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return False

    parts = rel.parts
    if not parts or parts[0] != "plugins":
        return False
    return "skills" in parts[1:-1]


def _frontmatter_block(text: str) -> List[str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return []

    block: List[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return block
        block.append(line.rstrip("\n"))
    return []


def _parse_frontmatter(skill_md: Path) -> Dict[str, str]:
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    lines = _frontmatter_block(text)
    parsed: Dict[str, str] = {}

    current_key: str | None = None
    current_indent = 0
    metadata_key: str | None = None

    for raw_line in lines:
        if not raw_line.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_indent = indent
            metadata_key = None
            parsed[current_key] = value.strip().strip("\"'")
            continue

        if current_key == "metadata" and indent > current_indent and ":" in line:
            key, value = line.split(":", 1)
            metadata_key = key.strip()
            parsed[f"metadata.{metadata_key}"] = value.strip().strip("\"'")
            continue

        if metadata_key and current_key == "metadata" and indent > current_indent:
            existing = parsed.get(f"metadata.{metadata_key}", "")
            parsed[f"metadata.{metadata_key}"] = " ".join(
                part for part in (existing, line.strip("\"'")) if part
            ).strip()
            continue

        if current_key and indent > current_indent:
            existing = parsed.get(current_key, "")
            parsed[current_key] = " ".join(
                part for part in (existing, line.strip("\"'")) if part
            ).strip()

    return parsed


def _normalize_description(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized or "Skill description pending."


def discover_skill_entries(source: str = "auto") -> List[SkillEntry]:
    seen: set[str] = set()
    entries: List[SkillEntry] = []
    if source == "flat":
        skill_dirs = list(_iter_flat_skill_dirs())
    elif source == "repo":
        skill_dirs = list(_iter_repo_skill_dirs())
    else:
        skill_dirs = list(_iter_flat_skill_dirs()) or list(_iter_repo_skill_dirs())

    for skill_dir in skill_dirs:
        source_dir = skill_dir.resolve()
        skill_md = source_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        fm = _parse_frontmatter(skill_md)
        name = skill_dir.name.strip() or source_dir.name
        if not name or name in seen:
            continue
        if name in HIDDEN_FLAT_SKILL_NAMES and not _is_plugin_owned_skill_dir(
            source_dir
        ):
            continue

        try:
            rel_dir = source_dir.relative_to(REPO_ROOT)
        except ValueError:
            continue

        category = rel_dir.parent.as_posix() or "uncategorized"
        description = _normalize_description(
            fm.get("metadata.short-description") or fm.get("description", "")
        )
        entries.append(
            SkillEntry(
                name=name,
                source_dir=source_dir,
                category=category,
                description=description,
            )
        )
        seen.add(name)

    return sorted(entries, key=lambda entry: (entry.category, entry.name))


def _category_heading(category: str) -> str:
    words: List[str] = []
    for part in category.split("/"):
        words.append(part.replace("-", " ").title())
    return " — ".join(words)


def render_index(entries: List[SkillEntry], source: str = "auto") -> str:
    categories: Dict[str, List[SkillEntry]] = {}
    for entry in entries:
        categories.setdefault(entry.category, []).append(entry)

    sorted_categories = sorted(categories)
    lines = [
        "# Agent Skills Index",
        "",
        "Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/.agents/skills`.",
        "",
        "## Table of Contents",
        "- [Summary](#summary)",
        "- [Catalog](#catalog)",
    ]
    for category in sorted_categories:
        slug = category.replace("/", "-").replace(" ", "-").lower()
        lines.append(f"- [{_category_heading(category)}](#{slug})")

    source_label = {
        "flat": "`.agents/skills` flat runtime view",
        "repo": "repository skill scan",
        "auto": "auto-resolved catalog source",
    }.get(source, source)

    lines.extend(
        [
            "",
            "## Summary",
            f"- `total_skills`: {len(entries)}",
            f"- `catalog_source`: {source_label}",
            f"- `policy_identity`: {get_policy_identity()}",
            "",
            "## Catalog",
            "",
        ]
    )

    for category in sorted_categories:
        lines.append(f"## {_category_heading(category)}")
        lines.append("")
        for entry in categories[category]:
            lines.append(f"- `{entry.name}` — {entry.description}")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and count the surfaced skill catalog")
    parser.add_argument("--count", action="store_true", help="Print the current surfaced skill count")
    parser.add_argument("--write-index", type=Path, help="Write the generated root SKILL.md index")
    parser.add_argument(
        "--source",
        choices=("auto", "flat", "repo"),
        default="auto",
        help="Catalog source: flat runtime view, repo scan, or auto fallback (default).",
    )
    parser.add_argument(
        "--policy-identity",
        action="store_true",
        help="Print canonical selection-policy identity.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    entries = discover_skill_entries(source=args.source)

    if args.count:
        print(len(entries))

    if args.policy_identity:
        print(get_policy_identity())

    if args.write_index:
        rendered = render_index(entries, source=args.source)
        args.write_index.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote skill index: {args.write_index}")

    if not args.count and not args.write_index and not args.policy_identity:
        print(render_index(entries, source=args.source))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
