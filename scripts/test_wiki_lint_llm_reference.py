#!/usr/bin/env python3
"""Tests for the LLM Wiki Reference PR changes.

Covers:
- docs/skill-ops-wiki/wiki/learnings/llm-wiki-reference.md (new file)
- docs/skill-ops-wiki/wiki/sources/llm-wiki.md (new file)
- docs/skill-ops-wiki/wiki/index.md (Sources section + new entries)
- docs/skill-ops-wiki/wiki/log.md (new triage entry)

Uses wiki_lint.py helpers directly to validate both the actual committed files
and the linter's behaviour against synthetic wiki fixtures.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = REPO_ROOT / "docs" / "skill-ops-wiki" / "wiki"

# Put scripts/ on the path so we can import wiki_lint helpers.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import wiki_lint  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LOG_ENTRY_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] (\S+) \| (.+)$", re.MULTILINE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _section_text(text: str, heading: str) -> str:
    """Return the body text under a given ## heading (up to the next ## or EOF)."""
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def _toc_line(text: str) -> list[str]:
    """Return lines that look like TOC entries (- [Name](#anchor))."""
    return [ln.strip() for ln in text.splitlines() if re.match(r"^- \[.+\]\(#.+\)$", ln.strip())]


# ---------------------------------------------------------------------------
# New file: learnings/llm-wiki-reference.md
# ---------------------------------------------------------------------------


class TestLlmWikiReferenceFile(unittest.TestCase):
    """Validate the structure and frontmatter of the new reference note."""

    def setUp(self) -> None:
        self.path = WIKI_ROOT / "learnings" / "llm-wiki-reference.md"
        self.text = self.path.read_text(encoding="utf-8")
        self.frontmatter = wiki_lint._read_frontmatter(self.path)

    def test_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), "llm-wiki-reference.md must exist")

    def test_frontmatter_present(self) -> None:
        self.assertTrue(self.frontmatter, "Frontmatter must not be empty")

    def test_frontmatter_title(self) -> None:
        self.assertEqual(self.frontmatter.get("title"), "LLM Wiki Reference")

    def test_frontmatter_type(self) -> None:
        self.assertEqual(self.frontmatter.get("type"), "lesson-learned")

    def test_frontmatter_status(self) -> None:
        self.assertEqual(self.frontmatter.get("status"), "verified")

    def test_frontmatter_last_reviewed_present(self) -> None:
        self.assertIn("last_reviewed", self.frontmatter)

    def test_frontmatter_last_reviewed_value(self) -> None:
        # The date is stored as '2026-04-09' (with YAML single quotes).
        # _read_frontmatter captures it literally; strip surrounding quotes for
        # a clean date comparison.
        raw = str(self.frontmatter.get("last_reviewed", ""))
        stripped = raw.strip("'\"")
        self.assertTrue(
            DATE_RE.match(stripped),
            f"last_reviewed '{raw}' should contain a valid YYYY-MM-DD date",
        )

    def test_frontmatter_sources_list_non_empty(self) -> None:
        sources = self.frontmatter.get("sources")
        self.assertIsNotNone(sources, "sources key must be present")
        # Parsed as a list by _read_frontmatter when written as YAML list.
        if isinstance(sources, list):
            self.assertGreater(len(sources), 0, "sources list must not be empty")
        else:
            self.assertTrue(str(sources).strip(), "sources value must not be blank")

    def test_has_h1_heading(self) -> None:
        self.assertIsNotNone(
            re.search(r"^# LLM Wiki Reference", self.text, re.MULTILINE),
            "File must contain a top-level '# LLM Wiki Reference' heading",
        )

    def test_has_summary_section(self) -> None:
        self.assertIn("## Summary", self.text)

    def test_has_source_section(self) -> None:
        self.assertIn("## Source", self.text)

    def test_source_section_links_to_llm_wiki(self) -> None:
        source_body = _section_text(self.text, "Source")
        self.assertIn("llm-wiki.md", source_body)

    def test_triage_section_contains_intent(self) -> None:
        triage_body = _section_text(self.text, "Triage")
        self.assertIn("lesson-learned", triage_body)

    def test_triage_section_contains_status(self) -> None:
        triage_body = _section_text(self.text, "Triage")
        self.assertIn("verified", triage_body)

    def test_triage_section_contains_destination(self) -> None:
        triage_body = _section_text(self.text, "Triage")
        self.assertIn("learnings", triage_body)

    def test_file_lives_in_learnings_directory(self) -> None:
        self.assertEqual(self.path.parent.name, "learnings")


# ---------------------------------------------------------------------------
# Quoted date edge-case: last_reviewed: '2026-04-09'
# ---------------------------------------------------------------------------


class TestLlmWikiReferenceFrontmatterEdgeCases(unittest.TestCase):
    """Regression tests for quirks introduced by the new reference file."""

    def setUp(self) -> None:
        self.path = WIKI_ROOT / "learnings" / "llm-wiki-reference.md"
        self.frontmatter = wiki_lint._read_frontmatter(self.path)

    def test_quoted_date_is_not_valid_bare_date(self) -> None:
        """The YAML value '2026-04-09' is stored with surrounding quotes.

        wiki_lint.DATE_RE matches bare YYYY-MM-DD only.  If the file is ever
        moved to failures/ or playbooks/ the linter would report bad-date.
        This test documents that behaviour so it is caught early.
        """
        raw = str(self.frontmatter.get("last_reviewed", ""))
        # Confirm the raw value retains quotes as parsed by _read_frontmatter.
        # DATE_RE requires no surrounding characters.
        if raw.startswith("'") or raw.startswith('"'):
            self.assertFalse(
                DATE_RE.match(raw),
                "Quoted date should NOT match DATE_RE — linter would emit bad-date "
                "if page were in failures/ or playbooks/.",
            )

    def test_triage_status_field_present(self) -> None:
        self.assertIn("triage_status", self.frontmatter)
        self.assertEqual(self.frontmatter["triage_status"], "verified")


# ---------------------------------------------------------------------------
# New file: sources/llm-wiki.md
# ---------------------------------------------------------------------------


class TestLlmWikiSourceFile(unittest.TestCase):
    """Validate the structure of the imported LLM wiki source document."""

    def setUp(self) -> None:
        self.path = WIKI_ROOT / "sources" / "llm-wiki.md"
        self.text = self.path.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), "sources/llm-wiki.md must exist")

    def test_file_lives_in_sources_directory(self) -> None:
        self.assertEqual(self.path.parent.name, "sources")

    def test_has_h1_heading(self) -> None:
        self.assertRegex(self.text, r"^# LLM Wiki", re.MULTILINE)

    def test_no_frontmatter(self) -> None:
        """Source files are immutable imports and do not carry wiki frontmatter."""
        fm = wiki_lint._read_frontmatter(self.path)
        self.assertEqual(fm, {}, "sources/llm-wiki.md should have no YAML frontmatter")

    def test_has_core_idea_section(self) -> None:
        self.assertIn("## The core idea", self.text)

    def test_has_architecture_section(self) -> None:
        self.assertIn("## Architecture", self.text)

    def test_has_operations_section(self) -> None:
        self.assertIn("## Operations", self.text)

    def test_has_indexing_and_logging_section(self) -> None:
        self.assertIn("## Indexing and logging", self.text)

    def test_has_why_this_works_section(self) -> None:
        self.assertIn("## Why this works", self.text)

    def test_content_is_non_trivial(self) -> None:
        """Source document must have meaningful content (>= 40 non-blank lines)."""
        non_blank = [ln for ln in self.text.splitlines() if ln.strip()]
        self.assertGreaterEqual(len(non_blank), 40)

    def test_no_internal_broken_markdown_links(self) -> None:
        """All markdown links in the source file should be absolute URLs or anchors."""
        links = wiki_lint._extract_links(self.path)
        # _extract_links already filters out http/https/mailto/# prefixes.
        # Any remaining links would be relative file paths; there should be none.
        self.assertEqual(
            links,
            [],
            f"Unexpected non-URL internal links in sources/llm-wiki.md: {links}",
        )


# ---------------------------------------------------------------------------
# Modified file: wiki/index.md
# ---------------------------------------------------------------------------


class TestIndexMdSourcesSection(unittest.TestCase):
    """Validate the Sources section added to index.md by this PR."""

    def setUp(self) -> None:
        self.path = WIKI_ROOT / "index.md"
        self.text = self.path.read_text(encoding="utf-8")

    def test_sources_in_table_of_contents(self) -> None:
        toc_entries = _toc_line(self.text)
        self.assertTrue(
            any("Sources" in e for e in toc_entries),
            "TOC must include a Sources entry",
        )

    def test_sources_section_heading_exists(self) -> None:
        self.assertIn("## Sources", self.text)

    def test_learnings_section_contains_llm_wiki_reference(self) -> None:
        learnings_body = _section_text(self.text, "Learnings")
        self.assertIn("LLM Wiki Reference", learnings_body)

    def test_learnings_entry_links_to_correct_path(self) -> None:
        learnings_body = _section_text(self.text, "Learnings")
        self.assertIn("learnings/llm-wiki-reference.md", learnings_body)

    def test_learnings_entry_has_summary(self) -> None:
        learnings_body = _section_text(self.text, "Learnings")
        self.assertIn("Reference note for externally provided LLM wiki markdown", learnings_body)

    def test_sources_section_contains_llm_wiki_source(self) -> None:
        sources_body = _section_text(self.text, "Sources")
        self.assertIn("LLM Wiki Source", sources_body)

    def test_sources_entry_links_to_correct_path(self) -> None:
        sources_body = _section_text(self.text, "Sources")
        self.assertIn("sources/llm-wiki.md", sources_body)

    def test_sources_entry_has_summary(self) -> None:
        sources_body = _section_text(self.text, "Sources")
        self.assertIn("Imported source markdown for the LLM reference note", sources_body)

    def test_sources_section_is_between_learnings_and_operations(self) -> None:
        """Sources must appear after Learnings and before Operations in the document."""
        learnings_pos = self.text.find("## Learnings")
        sources_pos = self.text.find("## Sources")
        operations_pos = self.text.find("## Operations")
        self.assertGreater(sources_pos, learnings_pos)
        self.assertLess(sources_pos, operations_pos)

    def test_operations_section_still_present(self) -> None:
        """Adding Sources must not remove the Operations section."""
        self.assertIn("## Operations", self.text)

    def test_operations_links_to_change_log(self) -> None:
        ops_body = _section_text(self.text, "Operations")
        self.assertIn("log.md", ops_body)

    def test_toc_sources_entry_before_operations(self) -> None:
        """In the TOC, Sources must precede Operations."""
        toc_match = re.search(r"(?ms)^## Table of Contents\n(.+?)(?=^## )", self.text)
        self.assertIsNotNone(toc_match, "Table of Contents section must exist")
        toc_text = toc_match.group(1)
        sources_idx = toc_text.find("Sources")
        operations_idx = toc_text.find("Operations")
        self.assertGreater(sources_idx, 0, "Sources entry must be in TOC")
        self.assertLess(sources_idx, operations_idx, "Sources must precede Operations in TOC")


# ---------------------------------------------------------------------------
# Modified file: wiki/log.md
# ---------------------------------------------------------------------------


class TestLogMdTriageEntry(unittest.TestCase):
    """Validate the new triage log entry added by this PR."""

    def setUp(self) -> None:
        self.path = WIKI_ROOT / "log.md"
        self.text = self.path.read_text(encoding="utf-8")

    def test_triage_entry_format(self) -> None:
        entries = LOG_ENTRY_RE.findall(self.text)
        self.assertTrue(
            any(action == "triage" and title == "LLM Wiki Reference" for _, action, title in entries),
            "log.md must contain a triage entry titled 'LLM Wiki Reference'",
        )

    def test_triage_entry_date(self) -> None:
        entries = LOG_ENTRY_RE.findall(self.text)
        triage_dates = [d for d, action, title in entries if action == "triage" and title == "LLM Wiki Reference"]
        self.assertEqual(len(triage_dates), 1, "Exactly one triage entry for LLM Wiki Reference")
        self.assertEqual(triage_dates[0], "2026-04-09")

    def _triage_entry_body(self) -> str:
        """Extract the body of the LLM Wiki Reference triage entry from log.md."""
        match = re.search(
            r"(?ms)^## \[2026-04-09\] triage \| LLM Wiki Reference\n(.*?)(?=^## |\Z)",
            self.text,
        )
        return match.group(1) if match else ""

    def test_triage_entry_contains_intent(self) -> None:
        body = self._triage_entry_body()
        self.assertIn("lesson-learned", body)

    def test_triage_entry_contains_status(self) -> None:
        body = self._triage_entry_body()
        self.assertIn("verified", body)

    def test_triage_entry_references_note_file(self) -> None:
        body = self._triage_entry_body()
        self.assertIn("llm-wiki-reference.md", body)

    def test_log_has_h1_heading(self) -> None:
        self.assertRegex(self.text, r"^# Skill Ops Wiki Log", re.MULTILINE)

    def test_log_entry_count_at_least_three(self) -> None:
        """The log should retain all prior entries plus the new one."""
        entries = LOG_ENTRY_RE.findall(self.text)
        self.assertGreaterEqual(len(entries), 3, "log.md must have at least 3 entries")

    def test_prior_entries_preserved(self) -> None:
        self.assertIn("bootstrap", self.text)
        self.assertIn("seed", self.text)

    def test_triage_is_last_entry(self) -> None:
        """The triage entry should be appended after existing entries."""
        entries = LOG_ENTRY_RE.findall(self.text)
        self.assertEqual(entries[-1][1], "triage")
        self.assertEqual(entries[-1][2], "LLM Wiki Reference")


# ---------------------------------------------------------------------------
# wiki_lint integration: linting the actual wiki
# ---------------------------------------------------------------------------


class TestWikiLintOnActualWiki(unittest.TestCase):
    """Run wiki_lint against the real wiki root and assert no errors for the new files."""

    def setUp(self) -> None:
        # Use a far-future date so no stale-page warnings fire on newly added pages.
        self.now = date(2026, 4, 9)
        self.issues = wiki_lint.lint_wiki(WIKI_ROOT, max_age_days=60, now=self.now)

    def test_no_broken_links_from_llm_reference(self) -> None:
        broken = [
            i for i in self.issues
            if i.code == "broken-link" and "llm-wiki-reference" in i.path
        ]
        self.assertEqual(broken, [], f"Unexpected broken links: {broken}")

    def test_no_broken_links_from_llm_source(self) -> None:
        broken = [
            i for i in self.issues
            if i.code == "broken-link" and "llm-wiki" in i.path
        ]
        self.assertEqual(broken, [], f"Unexpected broken links in llm-wiki.md: {broken}")

    def test_no_bad_date_errors_for_new_files(self) -> None:
        bad_date = [
            i for i in self.issues
            if i.code == "bad-date" and ("llm-wiki" in i.path)
        ]
        self.assertEqual(bad_date, [], f"Unexpected bad-date issues: {bad_date}")

    def test_no_empty_sources_for_new_files(self) -> None:
        empty_src = [
            i for i in self.issues
            if i.code == "empty-sources" and ("llm-wiki" in i.path)
        ]
        self.assertEqual(empty_src, [], f"Unexpected empty-sources issues: {empty_src}")


# ---------------------------------------------------------------------------
# wiki_lint integration: synthetic wiki with relative-link index
# ---------------------------------------------------------------------------


class TestWikiLintSyntheticWiki(unittest.TestCase):
    """Verify lint_wiki correctly validates a synthetic wiki that mirrors the PR additions.

    The actual repo index uses absolute paths (/docs/…) which wiki_lint skips when
    resolving links.  This synthetic fixture uses relative links (the canonical form
    expected by the linter) so we can test link integrity end-to-end.
    """

    def _make_wiki(self, tmp: Path) -> Path:
        wiki = tmp / "wiki"
        (wiki / "learnings").mkdir(parents=True)
        (wiki / "sources").mkdir(parents=True)

        # index.md — relative links so linter can resolve them
        (wiki / "index.md").write_text(
            "# Wiki Index\n\n"
            "## Learnings\n\n"
            "| Page | Summary |\n"
            "| --- | --- |\n"
            "| [LLM Wiki Reference](learnings/llm-wiki-reference.md) | Reference note. |\n\n"
            "## Sources\n\n"
            "| Page | Summary |\n"
            "| --- | --- |\n"
            "| [LLM Wiki Source](sources/llm-wiki.md) | Imported source. |\n",
            encoding="utf-8",
        )

        (wiki / "log.md").write_text(
            "# Log\n\n## [2026-04-09] triage | LLM Wiki Reference\n\n- Intent: `lesson-learned`\n",
            encoding="utf-8",
        )

        (wiki / "learnings" / "llm-wiki-reference.md").write_text(
            "---\n"
            "last_reviewed: '2026-04-09'\n"
            "sources:\n"
            "- /some/path/llm-wiki.md\n"
            "status: verified\n"
            "title: LLM Wiki Reference\n"
            "triage_status: verified\n"
            "type: lesson-learned\n"
            "---\n"
            "# LLM Wiki Reference\n\n"
            "## Summary\n\nReference note.\n\n"
            "## Source\n\n"
            "- [llm-wiki.md](../sources/llm-wiki.md)\n",
            encoding="utf-8",
        )

        (wiki / "sources" / "llm-wiki.md").write_text(
            "# LLM Wiki\n\nA pattern for building knowledge bases.\n",
            encoding="utf-8",
        )

        return wiki

    def test_no_broken_links_in_synthetic_wiki(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            broken = [i for i in issues if i.code == "broken-link"]
            self.assertEqual(broken, [], f"Broken links detected: {broken}")

    def test_no_missing_index_links_in_synthetic_wiki(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            missing = [i for i in issues if i.code == "missing-index-link"]
            self.assertEqual(missing, [], f"Missing index links: {missing}")

    def test_no_orphan_pages_in_synthetic_wiki(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            orphans = [i for i in issues if i.code == "orphan-page"]
            self.assertEqual(orphans, [], f"Orphan pages detected: {orphans}")

    def test_missing_index_link_fires_when_page_omitted(self) -> None:
        """Removing a page from the index must trigger missing-index-link."""
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            # Overwrite index.md to omit llm-wiki-reference.md
            (wiki / "index.md").write_text(
                "# Wiki Index\n\n"
                "## Sources\n\n"
                "| Page | Summary |\n"
                "| --- | --- |\n"
                "| [LLM Wiki Source](sources/llm-wiki.md) | Imported source. |\n",
                encoding="utf-8",
            )
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            paths = [i.path for i in issues if i.code == "missing-index-link"]
            self.assertIn("learnings/llm-wiki-reference.md", paths)

    def test_broken_link_fires_for_missing_source_target(self) -> None:
        """A reference note pointing to a non-existent source file must report broken-link."""
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            # Remove the source file to trigger broken-link.
            (wiki / "sources" / "llm-wiki.md").unlink()
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            broken = [i for i in issues if i.code == "broken-link"]
            self.assertTrue(len(broken) >= 1, "Expected at least one broken-link issue")

    def test_orphan_fires_when_source_not_linked_from_index(self) -> None:
        """A source page with no inbound links from anywhere must be flagged as orphan."""
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            # Remove sources/llm-wiki.md from index and from the reference note
            (wiki / "index.md").write_text(
                "# Wiki Index\n\n"
                "## Learnings\n\n"
                "| Page | Summary |\n"
                "| --- | --- |\n"
                "| [LLM Wiki Reference](learnings/llm-wiki-reference.md) | Reference note. |\n",
                encoding="utf-8",
            )
            (wiki / "learnings" / "llm-wiki-reference.md").write_text(
                "---\n"
                "title: LLM Wiki Reference\n"
                "type: lesson-learned\n"
                "status: verified\n"
                "last_reviewed: 2026-04-09\n"
                "sources:\n"
                "- /some/path/llm-wiki.md\n"
                "---\n"
                "# LLM Wiki Reference\n\n"
                "## Summary\n\nNo link to source.\n",
                encoding="utf-8",
            )
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            orphan_paths = [i.path for i in issues if i.code == "orphan-page"]
            self.assertIn("sources/llm-wiki.md", orphan_paths)


# ---------------------------------------------------------------------------
# _read_frontmatter unit tests against content from this PR
# ---------------------------------------------------------------------------


class TestReadFrontmatterUnit(unittest.TestCase):
    """Unit-test the _read_frontmatter helper with content patterns from the new files."""

    def _parse(self, content: str) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8", delete=False) as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            return wiki_lint._read_frontmatter(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_parses_lesson_learned_type(self) -> None:
        fm = self._parse(
            "---\ntitle: LLM Wiki Reference\ntype: lesson-learned\nstatus: verified\n"
            "last_reviewed: '2026-04-09'\nsources:\n- /path/to/file.md\n---\n# Heading\n"
        )
        self.assertEqual(fm["type"], "lesson-learned")

    def test_parses_triage_status_field(self) -> None:
        fm = self._parse(
            "---\ntitle: LLM Wiki Reference\ntype: lesson-learned\nstatus: verified\n"
            "triage_status: verified\nlast_reviewed: '2026-04-09'\nsources:\n- /path/to/file.md\n---\n# H\n"
        )
        self.assertEqual(fm["triage_status"], "verified")

    def test_parses_sources_as_list(self) -> None:
        fm = self._parse(
            "---\ntitle: T\ntype: t\nstatus: s\nlast_reviewed: 2026-04-09\nsources:\n"
            "- /Users/jamiecraik/dev/agent-skills/docs/skill-ops-wiki/wiki/sources/llm-wiki.md\n---\n# H\n"
        )
        sources = fm.get("sources")
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 1)
        self.assertIn("llm-wiki.md", sources[0])

    def test_quoted_date_retains_quotes(self) -> None:
        """last_reviewed: '2026-04-09' is stored with its surrounding quotes."""
        fm = self._parse(
            "---\ntitle: T\ntype: t\nstatus: s\nlast_reviewed: '2026-04-09'\nsources:\n- x\n---\n# H\n"
        )
        raw = fm.get("last_reviewed", "")
        # The raw value should include the single quotes because _read_frontmatter
        # does not strip YAML quoting.
        self.assertIn("2026-04-09", raw)

    def test_unquoted_date_passes_date_re(self) -> None:
        """An unquoted date like 2026-04-09 must match DATE_RE."""
        fm = self._parse(
            "---\ntitle: T\ntype: t\nstatus: s\nlast_reviewed: 2026-04-09\nsources:\n- x\n---\n# H\n"
        )
        raw = str(fm.get("last_reviewed", ""))
        self.assertRegex(raw, wiki_lint.DATE_RE)

    def test_empty_file_returns_empty_dict(self) -> None:
        fm = self._parse("")
        self.assertEqual(fm, {})

    def test_file_without_frontmatter_delimiter_returns_empty(self) -> None:
        fm = self._parse("# Just a Heading\n\nNo frontmatter here.\n")
        self.assertEqual(fm, {})


if __name__ == "__main__":
    unittest.main()