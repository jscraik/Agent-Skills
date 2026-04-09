#!/usr/bin/env python3
"""Targeted regression tests for wiki command helpers."""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / "scripts" / "lib"))

from ask.commands import wiki as wiki_commands  # noqa: E402


def _section_block(text: str, section: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(section)}\n(.*?)(?=^## |\Z)", text)
    if not match:
        return ""
    return match.group(1)


class WikiCommandTests(unittest.TestCase):
    def _make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="wiki-cmd-"))
        (root / "docs" / "skill-ops-wiki" / "wiki").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "skill-ops-wiki" / "raw").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "skill-ops-wiki" / "wiki" / "index.md").write_text(
            wiki_commands._default_index(),
            encoding="utf-8",
        )
        (root / "docs" / "skill-ops-wiki" / "wiki" / "log.md").write_text(
            "# Skill Ops Wiki Log\n",
            encoding="utf-8",
        )
        return root

    def test_wiki_add_routes_to_expected_section(self) -> None:
        repo_root = self._make_repo()
        result = wiki_commands.wiki_add(
            repo_root,
            title="Routing Test",
            summary="Ensures failure notes land in failures section.",
            source="local://routing",
            intent="finding",
            status="verified",
            destination="failures",
            dry_run=False,
        )
        self.assertEqual(result.status, "success")

        index_text = (repo_root / "docs" / "skill-ops-wiki" / "wiki" / "index.md").read_text(encoding="utf-8")
        failures_block = _section_block(index_text, "Failures")
        operations_block = _section_block(index_text, "Operations")

        self.assertIn("[Routing Test](failures/routing-test.md)", failures_block)
        self.assertNotIn("[Routing Test](failures/routing-test.md)", operations_block)

    def test_upsert_index_replaces_existing_row(self) -> None:
        repo_root = self._make_repo()
        index_path = repo_root / "docs" / "skill-ops-wiki" / "wiki" / "index.md"

        wiki_commands._upsert_index_entry(
            index_path,
            title="Playbook Row",
            relative_link="playbooks/playbook-row.md",
            summary="Old summary",
            destination_rel="playbooks",
        )
        wiki_commands._upsert_index_entry(
            index_path,
            title="Playbook Row",
            relative_link="playbooks/playbook-row.md",
            summary="Updated summary",
            destination_rel="playbooks",
        )

        text = index_path.read_text(encoding="utf-8")
        playbooks_block = _section_block(text, "Playbooks")
        self.assertEqual(playbooks_block.count("(playbooks/playbook-row.md)"), 1)
        self.assertIn("Updated summary", playbooks_block)
        self.assertNotIn("Old summary", playbooks_block)

    def test_query_snippet_skips_frontmatter_noise(self) -> None:
        repo_root = self._make_repo()
        page = repo_root / "docs" / "skill-ops-wiki" / "wiki" / "failures" / "snippet-test.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            """---
title: Signing Snippet Test
type: failure
status: active
last_reviewed: 2026-04-09
sources:
  - local://snippet
---

# Signing Snippet Test

This body line discusses signing flow behavior and should be selected.
""",
            encoding="utf-8",
        )

        query = wiki_commands.wiki_query(repo_root, query="signing")
        self.assertEqual(query.status, "success")
        self.assertGreaterEqual(query.data.get("count", 0), 1)
        first = query.data["results"][0]
        self.assertIn("body line discusses signing", first.get("snippet", "").lower())
        self.assertNotIn("title:", first.get("snippet", "").lower())


if __name__ == "__main__":
    unittest.main()
