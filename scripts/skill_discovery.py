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
    PLUGIN_VISIBLE_ROUTER_SKILL_NAMES as POLICY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
    PLUGIN_HIDDEN_LANE_SKILL_NAMES as POLICY_PLUGIN_HIDDEN_LANE_SKILL_NAMES,
    PLUGIN_SKILL_ROOT_GLOB as POLICY_PLUGIN_SKILL_ROOT_GLOB,
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
PLUGIN_VISIBLE_ROUTER_SKILL_NAMES = set(POLICY_PLUGIN_VISIBLE_ROUTER_SKILL_NAMES)
PLUGIN_HIDDEN_LANE_SKILL_NAMES = set(POLICY_PLUGIN_HIDDEN_LANE_SKILL_NAMES)


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
    """
    Discover repository skill directories that contain a SKILL.md under the configured REPO_SCAN_ROOTS, excluding any whose path contains a configured excluded segment.
    
    Returns:
        List[Path]: Paths to each directory containing a SKILL.md found under REPO_ROOT / <root_name> for each name in REPO_SCAN_ROOTS. Scan roots that do not exist are ignored; directories whose relative path contains a segment from EXCLUDED_REPO_SCAN_SEGMENTS are omitted.
    """
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


def _iter_plugin_skill_dirs() -> Iterable[Path]:
    """
    Return plugin-provided skill directories that contain a SKILL.md file.
    
    Searches repository paths that match the policy plugin-skill-root glob and collects the parent directories of any discovered SKILL.md files. Non-directory plugin roots are ignored, and any SKILL.md whose path (relative to the plugin root) contains a segment listed in EXCLUDED_REPO_SCAN_SEGMENTS is excluded.
    
    Returns:
    	list[Path]: Paths to directories containing SKILL.md discovered under plugin roots; an empty list if none are found.
    """
    dirs: List[Path] = []
    for plugin_root in sorted(REPO_ROOT.glob(POLICY_PLUGIN_SKILL_ROOT_GLOB)):
        if not plugin_root.is_dir():
            continue
        for skill_md in sorted(plugin_root.rglob("SKILL.md")):
            rel_parts = skill_md.relative_to(plugin_root).parts
            if any(part in EXCLUDED_REPO_SCAN_SEGMENTS for part in rel_parts):
                continue
            dirs.append(skill_md.parent)
    return dirs


def _is_plugin_owned_skill_dir(skill_dir: Path) -> bool:
    """
    Determine whether the given skill directory is owned by a plugin (i.e. it resides under REPO_ROOT/plugins/.../skills/...).
    
    Parameters:
    	skill_dir (Path): Path to the skill directory to test.
    
    Returns:
    	True if the directory is located inside a `plugins` subtree and contains a `skills` segment before the final path part, `False` otherwise.
    """
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
    """
    Normalises a skill description by collapsing consecutive whitespace to single spaces and trimming surrounding space; returns a fallback when empty.
    
    Returns:
        str: The cleaned description, or "Skill description pending." if the result is empty.
    """
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized or "Skill description pending."


def discover_skill_entries(source: str = "auto", visibility: str = "default") -> List[SkillEntry]:
    """
    Discover skill entries from the configured skill sources.

    Parameters:
        source (str): Which repository surface to scan. One of:
            - "auto": prefer flat skills if present, otherwise fall back to repository scan;
            - "flat": scan only the flat skills directory (optionally augment with plugin lanes in advanced visibility);
            - "repo": scan repository roots. Default "auto".
        visibility (str): Visibility mode affecting which skills are included.
            - "default": hide policy-marked hidden flat skills and hide certain plugin lane skills;
            - "advanced": include plugin lane skills that are otherwise hidden. Default "default".

    Returns:
        List[SkillEntry]: A list of discovered SkillEntry objects, deduplicated by name and sorted by (category, name). Each entry's category is derived from the skill path relative to the repository root and the description is chosen from frontmatter (`metadata.short-description` or `description`) then normalised.

    Raises:
        ValueError: If `visibility` is not "default" or "advanced", or if `source` is not one of "auto", "flat", or "repo".
    """
    if source not in {"auto", "flat", "repo"}:
        raise ValueError(f"Unsupported source: {source}")
    if visibility not in {"default", "advanced"}:
        raise ValueError(f"Unsupported visibility mode: {visibility}")

    seen: set[str] = set()
    entries: List[SkillEntry] = []
    if source == "flat":
        skill_dirs = list(_iter_flat_skill_dirs())
        if visibility == "advanced":
            # Flat runtime intentionally hides plugin lane skills; advanced mode
            # augments from plugin sources so lanes remain discoverable.
            skill_dirs.extend(_iter_plugin_skill_dirs())
    elif source == "repo":
        skill_dirs = list(_iter_repo_skill_dirs())
        skill_dirs.extend(_iter_plugin_skill_dirs())
    else:
        skill_dirs = list(_iter_flat_skill_dirs())
        if skill_dirs:
            if visibility == "advanced":
                # Default listing follows flat runtime projection; advanced mode
                # adds plugin lanes without changing default surface area.
                skill_dirs.extend(_iter_plugin_skill_dirs())
        else:
            skill_dirs = list(_iter_repo_skill_dirs())
            skill_dirs.extend(_iter_plugin_skill_dirs())

    for skill_dir in skill_dirs:
        source_dir = skill_dir.resolve()
        skill_md = source_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        fm = _parse_frontmatter(skill_md)
        name = skill_dir.name.strip() or source_dir.name
        if not name or name in seen:
            continue
        plugin_owned = _is_plugin_owned_skill_dir(source_dir)
        if name in HIDDEN_FLAT_SKILL_NAMES:
            continue
        if visibility != "advanced" and plugin_owned and name not in PLUGIN_VISIBLE_ROUTER_SKILL_NAMES:
            continue
        if (
            visibility != "advanced"
            and plugin_owned
            and name in PLUGIN_HIDDEN_LANE_SKILL_NAMES
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
    """
    Format a slash-separated category path into a human-friendly heading.
    
    Parameters:
        category (str): Category path with parts separated by '/', where parts may contain '-' to indicate word breaks.
    
    Returns:
        heading (str): A display heading where each path part has '-' replaced by spaces, is title-cased, and parts are joined with " — ".
    """
    words: List[str] = []
    for part in category.split("/"):
        words.append(part.replace("-", " ").title())
    return " — ".join(words)


def render_index(entries: List[SkillEntry], source: str = "auto", visibility: str = "default") -> str:
    """
    Render a Markdown catalogue of the provided skill entries grouped by category.
    
    Builds a document containing a title, table of contents, a Summary block
    (with `total_skills`, `catalog_source`, `visibility`, and `policy_identity`),
    and a Catalog section where entries are listed under category headings as
    "`name` — description".
    
    Parameters:
        entries (List[SkillEntry]): Skill entries to include in the index.
        source (str): Source label used in the Summary; typically "flat", "repo" or "auto".
            These map to "`.agents/skills` flat runtime view", "repository skill scan"
            and "auto-resolved catalog source" respectively.
        visibility (str): Visibility mode included in the Summary; expected values are
            "default" or "advanced" and influence which skills are presented elsewhere
            in the discovery process.
    
    Returns:
        str: The complete Markdown document as a single string.
    """
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
            f"- `visibility`: {visibility}",
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
    """
    Parse command-line arguments for the skill index utility.
    
    Returns:
        argparse.Namespace: Parsed CLI options with attributes `count`, `write_index`, `source`, `visibility` and `policy_identity`.
    """
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
        "--visibility",
        choices=("default", "advanced"),
        default="default",
        help="Catalog visibility mode: default hides lane skills, advanced shows all.",
    )
    parser.add_argument(
        "--policy-identity",
        action="store_true",
        help="Print canonical selection-policy identity.",
    )
    return parser.parse_args()


def main() -> int:
    """
    Parse command-line arguments, discover skill entries, and perform the requested output actions.
    
    The function handles the CLI options produced by parse_args(): it discovers skill entries using the chosen source and visibility, prints the total count when requested, prints the policy identity when requested, writes the rendered skill index to a file when a path is provided, and prints the rendered index to stdout when no other output-only options are given. File writes use UTF-8 encoding and append a final newline.
    
    Returns:
        int: Exit code `0` on successful completion.
    """
    args = parse_args()
    entries = discover_skill_entries(source=args.source, visibility=args.visibility)

    if args.count:
        print(len(entries))

    if args.policy_identity:
        print(get_policy_identity())

    if args.write_index:
        rendered = render_index(entries, source=args.source, visibility=args.visibility)
        args.write_index.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote skill index: {args.write_index}")

    if not args.count and not args.write_index and not args.policy_identity:
        print(render_index(entries, source=args.source, visibility=args.visibility))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())