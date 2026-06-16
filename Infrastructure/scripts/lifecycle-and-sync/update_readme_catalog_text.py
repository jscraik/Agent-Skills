#!/usr/bin/env python3
"""Refresh README catalog summary text for skill sync."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CURRENT_AGENT_SKILLS_KIT_SENTENCE = (
    "A governed **Agent Skills Kit** repository for Codex and AI coding agents. "
    "Author skills once, validate quality, expose SDK skill names, and sync "
    "routed skills and plugins into flat runtime projections through the `ask` CLI."
)

SUMMARY_PATTERNS: tuple[str, ...] = (
    (
        r"A governed \*\*Agent Skills Kit\*\* repository for Codex and AI coding agents\.\s+"
        r"Author skills once, validate quality, expose `\$` command-surface handles, and sync\s+"
        r"routed skills and plugins into runtime projections through the `ask` CLI\."
    ),
    (
        r"A governed \*\*Agent Skills Kit\*\* repository for Codex and AI coding agents\.\s+"
        r"Author skills once, validate quality, expose SDK skill names, and sync\s+"
        r"routed skills and plugins into flat runtime projections through the `ask` CLI\."
    ),
    (
        r"A governed \*\*Agent Skills Kit\*\* repository of \*\*\d+ skills\*\* "
        r"for Codex and AI coding agents\."
    ),
    (
        r"A governed repository of \*\*skills\*\* for AI coding agents\. Built around "
        r"the \*\*Agent Skills Kit \(`ask`\)\*\* CLI\."
    ),
)

COUNT_PATTERNS: tuple[str, ...] = (
    r"A governed repository of \*\*\d+(?: canonical)? skills\*\* for AI coding agents",
    r"A governed repository of \*\*skills\*\* for AI coding agents",
    r"A governed repository of AI coding skills\.",
)


def refresh_readme_catalog_text(content: str, catalog_count: int | str) -> str:
    """Return README content with canonical intro and catalog count text."""
    catalog_count = str(catalog_count)
    sentence_replacements = 0
    for pattern in SUMMARY_PATTERNS:
        content, sentence_replacements = re.subn(
            pattern,
            CURRENT_AGENT_SKILLS_KIT_SENTENCE,
            content,
            count=1,
        )
        if sentence_replacements:
            break

    count_replacements = 0
    count_sentence = f"A governed repository of **{catalog_count} skills** for AI coding agents"
    for pattern in COUNT_PATTERNS:
        content, count_replacements = re.subn(
            pattern,
            count_sentence,
            content,
            count=1,
        )
        if count_replacements:
            break

    if sentence_replacements == 0 and count_replacements == 0:
        content, insertions = re.subn(
            r"^(# Agent Skills\s*\n\s*)",
            rf"\1{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\n",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if insertions == 0:
            raise ValueError(
                "Failed to refresh README governed-repository sentence; expected # Agent Skills heading."
            )

    content = re.sub(
        rf"(?:{SUMMARY_PATTERNS[0]}\s*\n\s*){{2,}}",
        CURRENT_AGENT_SKILLS_KIT_SENTENCE + "\n\n",
        content,
    )
    content = re.sub(
        r"This repository currently exposes \*\*\d+ skills\*\* in the default catalog",
        f"This repository currently exposes **{catalog_count} skills** in the default catalog",
        content,
        count=1,
    )
    content = re.sub(
        r"currently expects \*\*\d+\*\* skills",
        f"currently expects **{catalog_count}** skills",
        content,
        count=1,
    )
    return content


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh README catalog summary text.")
    parser.add_argument("readme_path", type=Path)
    parser.add_argument("catalog_count", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    content = args.readme_path.read_text(encoding="utf-8")
    refreshed = refresh_readme_catalog_text(content, args.catalog_count)
    args.readme_path.write_text(refreshed, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
