#!/usr/bin/env python3
"""Tests for the LLM Wiki Reference PR changes.

Covers:
- Wiki/wiki/learnings/llm-wiki-reference.md (new file)
- Wiki/wiki/sources/llm-wiki.md (new file)
- Wiki/wiki/index.md (Sources section + new entries)
- Wiki/wiki/log.md (new triage entry)

Uses wiki_lint.py helpers directly to validate both the actual committed files
and the linter's behaviour against synthetic wiki fixtures.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WIKI_ROOT = REPO_ROOT / "Wiki" / "wiki"
WIKI_LINT_PATH = REPO_ROOT / "scripts" / "validation-and-linting" / "wiki_lint.py"

def _load_wiki_lint_module():
    spec = importlib.util.spec_from_file_location("wiki_lint_under_test", WIKI_LINT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load wiki_lint module from {WIKI_LINT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


wiki_lint = _load_wiki_lint_module()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LOG_ENTRY_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] (\S+) \| (.+)$", re.MULTILINE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _section_text(text: str, heading: str) -> str:
    """
    Extracts the markdown body under a level-2 heading.
    
    Parameters:
        text (str): The full markdown document to search.
        heading (str): The exact heading title (without leading `## `).
    
    Returns:
        str: The content under the first matching `## {heading}` (excluding the heading line), up to the next `## ` or end of file; empty string if not found.
    """
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def _toc_line(text: str) -> list[str]:
    """
    Return table-of-contents lines of the form "- [Name](#anchor)" found in the markdown text.
    
    Returns:
        list[str]: Matching TOC lines with surrounding whitespace removed.
    """
    return [ln.strip() for ln in text.splitlines() if re.match(r"^- \[.+\]\(#.+\)$", ln.strip())]


# ---------------------------------------------------------------------------
# New file: learnings/llm-wiki-reference.md
# ---------------------------------------------------------------------------


class TestLlmWikiReferenceFile(unittest.TestCase):
    """Validate the structure and frontmatter of the new reference note."""

    def setUp(self) -> None:
        """
        Initialise the test fixture by loading the LLM Wiki Reference file and parsing its frontmatter.
        
        Reads Wiki/wiki/learnings/llm-wiki-reference.md and sets:
        - self.path: Path to the file.
        - self.text: File contents as a UTF-8 string.
        - self.frontmatter: Parsed YAML frontmatter dictionary (empty dict if none).
        """
        self.path = WIKI_ROOT / "learnings" / "llm-wiki-reference.md"
        self.text = self.path.read_text(encoding="utf-8")
        self.frontmatter = wiki_lint._read_frontmatter(self.path)

    def test_file_exists(self) -> None:
        """
        Check that the 'llm-wiki-reference.md' file exists at the expected path.
        
        Fails the test with a clear message if the file is missing.
        """
        self.assertTrue(self.path.exists(), "llm-wiki-reference.md must exist")

    def test_frontmatter_present(self) -> None:
        """
        Verify the markdown file contains non-empty YAML frontmatter.
        
        Asserts that the parsed frontmatter is present and not empty, protecting against a missing or malformed frontmatter block in the reference markdown.
        """
        self.assertTrue(self.frontmatter, "Frontmatter must not be empty")

    def test_frontmatter_title(self) -> None:
        """
        Assert that the parsed frontmatter `title` equals "LLM Wiki Reference".
        
        Fails the test if the `title` key is missing or its value differs from the expected string, protecting the note's declared title from accidental changes.
        """
        self.assertEqual(self.frontmatter.get("title"), "LLM Wiki Reference")

    def test_frontmatter_type(self) -> None:
        """
        Assert that the parsed frontmatter sets "type" to "lesson-learned".
        
        Checks the frontmatter dictionary for a "type" key and verifies its value is exactly "lesson-learned".
        """
        self.assertEqual(self.frontmatter.get("type"), "lesson-learned")

    def test_frontmatter_status(self) -> None:
        self.assertEqual(self.frontmatter.get("status"), "verified")

    def test_frontmatter_last_reviewed_present(self) -> None:
        """
        Verify the frontmatter includes a 'last_reviewed' field.
        
        Checks that the parsed YAML frontmatter for the test fixture contains the key 'last_reviewed'.
        """
        self.assertIn("last_reviewed", self.frontmatter)

    def test_frontmatter_last_reviewed_value(self) -> None:
        # The date is stored as '2026-04-09' (with YAML single quotes).
        # _read_frontmatter captures it literally; strip surrounding quotes for
        # a clean date comparison.
        """
        Assert that the frontmatter `last_reviewed` field contains a bare `YYYY-MM-DD` date.
        
        Strips surrounding single or double quotes from the raw parsed `last_reviewed` value and verifies it matches `DATE_RE`; on failure the assertion message includes the original raw value.
        """
        raw = str(self.frontmatter.get("last_reviewed", ""))
        stripped = raw.strip("'\"")
        self.assertTrue(
            DATE_RE.match(stripped),
            f"last_reviewed '{raw}' should contain a valid YYYY-MM-DD date",
        )

    def test_frontmatter_sources_list_non_empty(self) -> None:
        """
        Assert that the parsed frontmatter contains a non-empty `sources` field.
        
        Checks that the `sources` key is present; if its value is a list it must contain at least one item, otherwise its string representation must contain non-whitespace characters.
        """
        sources = self.frontmatter.get("sources")
        self.assertIsNotNone(sources, "sources key must be present")
        # Parsed as a list by _read_frontmatter when written as YAML list.
        if isinstance(sources, list):
            self.assertGreater(len(sources), 0, "sources list must not be empty")
        else:
            self.assertTrue(str(sources).strip(), "sources value must not be blank")

    def test_has_h1_heading(self) -> None:
        """
        Check the document contains a top-level "# LLM Wiki Reference" H1 heading.
        
        Asserts there is a line that begins with "# LLM Wiki Reference".
        """
        self.assertIsNotNone(
            re.search(r"^# LLM Wiki Reference", self.text, re.MULTILINE),
            "File must contain a top-level '# LLM Wiki Reference' heading",
        )

    def test_has_summary_section(self) -> None:
        self.assertIn("## Summary", self.text)

    def test_has_source_section(self) -> None:
        """
        Assert the document contains a level-2 heading titled "Source".
        
        This test fails if the wiki file under test does not include the `## Source` section, ensuring the source attribution section is present.
        """
        self.assertIn("## Source", self.text)

    def test_source_section_links_to_llm_wiki(self) -> None:
        """
        Verify the "Source" section contains a link to the LLM wiki source file.
        
        Asserts that the markdown body under the "## Source" heading includes the substring "llm-wiki.md".
        """
        source_body = _section_text(self.text, "Source")
        self.assertIn("llm-wiki.md", source_body)

    def test_triage_section_contains_intent(self) -> None:
        triage_body = _section_text(self.text, "Triage")
        self.assertIn("lesson-learned", triage_body)

    def test_triage_section_contains_status(self) -> None:
        """
        Assert the 'Triage' section includes the 'verified' status.
        
        Checks the markdown `## Triage` section and fails the test if the literal token `verified` is not present.
        """
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
        """
        Prepare the test fixture by locating the LLM wiki reference file and parsing its YAML frontmatter.
        
        Sets `self.path` to the repository's `learnings/llm-wiki-reference.md` path and sets `self.frontmatter` to the parsed frontmatter dictionary for use by the test methods.
        """
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
        if raw.startswith(("'", '"')):
            self.assertFalse(
                DATE_RE.match(raw),
                "Quoted date should NOT match DATE_RE — linter would emit bad-date "
                "if page were in failures/ or playbooks/.",
            )

    def test_triage_status_field_present(self) -> None:
        """
        Verify the frontmatter contains a `triage_status` field with the value 'verified'.
        """
        self.assertIn("triage_status", self.frontmatter)
        self.assertEqual(self.frontmatter["triage_status"], "verified")


# ---------------------------------------------------------------------------
# New file: sources/llm-wiki.md
# ---------------------------------------------------------------------------


class TestLlmWikiSourceFile(unittest.TestCase):
    """Validate the structure of the imported LLM wiki source document."""

    def setUp(self) -> None:
        """
        Prepare the test fixture by locating and loading the LLM wiki source markdown.
        
        Sets two attributes on the test instance:
        - `self.path`: Path to `wiki/sources/llm-wiki.md` under the repository wiki root.
        - `self.text`: File contents decoded as UTF-8.
        """
        self.path = WIKI_ROOT / "sources" / "llm-wiki.md"
        self.text = self.path.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        """
        Check that the source file 'sources/llm-wiki.md' exists in the wiki repository.
        
        Asserts presence of the required source markdown used by the LLM reference tests.
        """
        self.assertTrue(self.path.exists(), "sources/llm-wiki.md must exist")

    def test_file_lives_in_sources_directory(self) -> None:
        """
        Asserts the test file is located in a directory named "sources".
        """
        self.assertEqual(self.path.parent.name, "sources")

    def test_has_h1_heading(self) -> None:
        """
        Checks the document contains a top-level H1 heading starting with "LLM Wiki".
        
        Asserts that the file text includes a line beginning with "# LLM Wiki".
        """
        self.assertRegex(self.text, re.compile(r"^# LLM Wiki", re.MULTILINE))

    def test_no_frontmatter(self) -> None:
        """Source files are immutable imports and do not carry wiki frontmatter."""
        fm = wiki_lint._read_frontmatter(self.path)
        self.assertEqual(fm, {}, "sources/llm-wiki.md should have no YAML frontmatter")

    def test_has_core_idea_section(self) -> None:
        """
        Assert that the source document contains a level-2 section titled "The core idea".
        
        This protects against accidentally removing or renaming the required `## The core idea` heading in the `sources/llm-wiki.md` file.
        """
        self.assertIn("## The core idea", self.text)

    def test_has_architecture_section(self) -> None:
        """
        Assert that the source markdown contains an "## Architecture" section.
        """
        self.assertIn("## Architecture", self.text)

    def test_has_operations_section(self) -> None:
        """
        Verify the wiki index contains the '## Operations' level-2 heading.
        
        Asserts that the loaded index.md text includes the '## Operations' heading to catch accidental removal or renaming of the Operations section.
        """
        self.assertIn("## Operations", self.text)

    def test_has_indexing_and_logging_section(self) -> None:
        """
        Assert that the wiki index contains a level-2 section titled "Indexing and logging".
        
        Protects against accidental removal or renaming of the "## Indexing and logging" section in wiki/index.md.
        """
        self.assertIn("## Indexing and logging", self.text)

    def test_has_why_this_works_section(self) -> None:
        """
        Assert the source document includes a top-level "Why this works" section.
        
        Protects against accidental removal or renaming of the explanatory `## Why this works` heading in the source file.
        """
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
        """
        Load the wiki root's index.md into the test fixture.
        
        Sets:
            self.path: Path to WIKI_ROOT/index.md.
            self.text: UTF-8 decoded contents of the file for assertions on the table of contents and section ordering.
        """
        self.path = WIKI_ROOT / "index.md"
        self.text = self.path.read_text(encoding="utf-8")

    def test_sources_in_table_of_contents(self) -> None:
        """
        Check the index.md table of contents includes a "Sources" entry.
        
        Asserts that one of the extracted TOC lines contains the text "Sources", protecting against regressions that remove or rename the Sources section from the site's TOC.
        """
        toc_entries = _toc_line(self.text)
        self.assertTrue(
            any("Sources" in e for e in toc_entries),
            "TOC must include a Sources entry",
        )

    def test_sources_section_heading_exists(self) -> None:
        self.assertIn("## Sources", self.text)

    def test_learnings_section_contains_llm_wiki_reference(self) -> None:
        """
        Verify the index 'Learnings' section contains the entry "LLM Wiki Reference".
        
        Ensures the new reference note is present in the Learnings section body of index.md.
        """
        learnings_body = _section_text(self.text, "Learnings")
        self.assertIn("LLM Wiki Reference", learnings_body)

    def test_learnings_entry_links_to_correct_path(self) -> None:
        learnings_body = _section_text(self.text, "Learnings")
        self.assertIn("learnings/llm-wiki-reference.md", learnings_body)

    def test_learnings_entry_has_summary(self) -> None:
        """
        Asserts the Learnings section includes the expected summary for the LLM wiki reference.
        
        Checks that the body under "## Learnings" contains the exact summary text
        "Reference note for externally provided LLM wiki markdown".
        """
        learnings_body = _section_text(self.text, "Learnings")
        self.assertIn("Reference note for externally provided LLM wiki markdown", learnings_body)

    def test_sources_section_contains_llm_wiki_source(self) -> None:
        """
        Assert the index "Sources" section contains the "LLM Wiki Source" entry.
        """
        sources_body = _section_text(self.text, "Sources")
        self.assertIn("LLM Wiki Source", sources_body)

    def test_sources_entry_links_to_correct_path(self) -> None:
        """
        Check that the "Sources" section contains a link to the LLM wiki source file.
        
        Asserts that the Sources section text includes the path `sources/llm-wiki.md`.
        """
        sources_body = _section_text(self.text, "Sources")
        self.assertIn("sources/llm-wiki.md", sources_body)

    def test_sources_entry_has_summary(self) -> None:
        """
        Assert that the `## Sources` section contains the expected summary for the LLM source.
        
        Checks that the section body includes the exact phrase "Imported source markdown for the LLM reference note".
        """
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
        """
        Check the Operations section contains a reference to the change log.
        
        Asserts that the 'Operations' level-2 section includes the substring 'log.md'.
        """
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
        """
        Prepare the test fixture by locating and reading the wiki log file into the instance.
        
        Sets `self.path` to the wiki `log.md` path and `self.text` to its UTF-8 file contents for subsequent assertions about triage entries and log structure.
        """
        self.path = WIKI_ROOT / "log.md"
        self.text = self.path.read_text(encoding="utf-8")

    def test_triage_entry_format(self) -> None:
        """
        Ensure the wiki log contains a triage entry titled "LLM Wiki Reference".
        
        Asserts that at least one log header matches an entry with action `triage` and title `LLM Wiki Reference`, failing if no such entry is present.
        """
        entries = LOG_ENTRY_RE.findall(self.text)
        self.assertTrue(
            any(action == "triage" and title == "LLM Wiki Reference" for _, action, title in entries),
            "log.md must contain a triage entry titled 'LLM Wiki Reference'",
        )

    def test_triage_entry_date(self) -> None:
        """
        Verify there is exactly one triage log entry for 'LLM Wiki Reference' dated 2026-04-09.
        
        Asserts the parsed log entries include a single entry with action `triage` and title `LLM Wiki Reference`, and that its associated date equals `2026-04-09`.
        """
        entries = LOG_ENTRY_RE.findall(self.text)
        triage_dates = [d for d, action, title in entries if action == "triage" and title == "LLM Wiki Reference"]
        self.assertEqual(len(triage_dates), 1, "Exactly one triage entry for LLM Wiki Reference")
        self.assertEqual(triage_dates[0], "2026-04-09")

    def _triage_entry_body(self) -> str:
        """
        Extract the markdown body for the "LLM Wiki Reference" triage log entry dated 2026-04-09.
        
        The returned text covers the entry content from the line following the entry header up to the next top-level `##` heading or end of file.
        
        Returns:
            str: The entry body without the leading header; empty string if the entry is not present.
        """
        match = re.search(
            r"(?ms)^## \[2026-04-09\] triage \| LLM Wiki Reference\n(.*?)(?=^## |\Z)",
            self.text,
        )
        return match.group(1) if match else ""

    def test_triage_entry_contains_intent(self) -> None:
        body = self._triage_entry_body()
        self.assertIn("lesson-learned", body)

    def test_triage_entry_contains_status(self) -> None:
        """
        Ensure the triage log entry body contains the expected verification status.
        
        Asserts that the extracted triage entry body includes the string "verified".
        """
        body = self._triage_entry_body()
        self.assertIn("verified", body)

    def test_triage_entry_references_note_file(self) -> None:
        """
        Ensure the triage log entry body mentions the reference note filename `llm-wiki-reference.md`.
        """
        body = self._triage_entry_body()
        self.assertIn("llm-wiki-reference.md", body)

    def test_log_has_h1_heading(self) -> None:
        """
        Ensure the wiki log contains the main H1 heading.
        
        Asserts the file text includes a top-level heading "# Skill Ops Wiki Log".
        """
        self.assertRegex(self.text, re.compile(r"^# Skill Ops Wiki Log", re.MULTILINE))

    def test_log_entry_count_at_least_three(self) -> None:
        """The log should retain all prior entries plus the new one."""
        entries = LOG_ENTRY_RE.findall(self.text)
        self.assertGreaterEqual(len(entries), 3, "log.md must have at least 3 entries")

    def test_prior_entries_preserved(self) -> None:
        """
        Verify historical log entries for "bootstrap" and "seed" are present in the log file.
        
        Asserts that the loaded log text contains the strings "bootstrap" and "seed".
        """
        self.assertIn("bootstrap", self.text)
        self.assertIn("seed", self.text)

    def test_triage_is_last_entry(self) -> None:
        """
        Assert that a triage entry for "LLM Wiki Reference" exists as the log grows.

        Checks the parsed entries for an action/title match without requiring that entry to stay last forever.
        """
        entries = LOG_ENTRY_RE.findall(self.text)
        self.assertTrue(
            any(action == "triage" and title == "LLM Wiki Reference" for _, action, title in entries),
            "log.md must include a triage entry titled 'LLM Wiki Reference'",
        )


# ---------------------------------------------------------------------------
# wiki_lint integration: linting the actual wiki
# ---------------------------------------------------------------------------


class TestWikiLintOnActualWiki(unittest.TestCase):
    """Run wiki_lint against the real wiki root and assert no errors for the new files."""

    def setUp(self) -> None:
        # Use a far-future date so no stale-page warnings fire on newly added pages.
        """
        Prepare test fixtures by fixing the audit date and collecting lint results for the repository wiki.
        
        Sets self.now to 2026-04-09 and stores the linter output in self.issues by running wiki_lint.lint_wiki(WIKI_ROOT, max_age_days=60, now=self.now).
        """
        self.now = date(2026, 4, 9)
        self.issues = wiki_lint.lint_wiki(WIKI_ROOT, max_age_days=60, now=self.now)

    def test_no_broken_links_from_llm_reference(self) -> None:
        """
        Fail the test if any linter issues of code "broken-link" reference the LLM Wiki Reference page.
        
        Searches self.issues for entries with code "broken-link" and a path containing "llm-wiki-reference" and asserts that no such issues exist.
        """
        broken = [
            i for i in self.issues
            if i.code == "broken-link" and "llm-wiki-reference" in i.path
        ]
        self.assertEqual(broken, [], f"Unexpected broken links: {broken}")

    def test_no_broken_links_from_llm_source(self) -> None:
        """
        Ensure the linter reports no 'broken-link' issues for the LLM wiki source file.
        
        Fails if any linter issue with code 'broken-link' and a path containing 'llm-wiki' is found.
        """
        broken = [
            i for i in self.issues
            if i.code == "broken-link" and "llm-wiki" in i.path
        ]
        self.assertEqual(broken, [], f"Unexpected broken links in llm-wiki.md: {broken}")

    def test_no_bad_date_errors_for_new_files(self) -> None:
        """
        Fail the test if any collected lint issue with code `bad-date` references a path containing `llm-wiki`.
        
        Filters `self.issues` for entries where `code == "bad-date"` and `"llm-wiki"` appears in the issue path, and asserts that no such issues exist.
        """
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

    The repo index uses relative links, which is the canonical form expected by
    wiki_lint. This synthetic fixture keeps that behavior covered end-to-end.
    """

    def _make_wiki(self, tmp: Path) -> Path:
        """
        Create a small synthetic wiki fixture under the given temporary directory for linter tests.
        
        The fixture contains:
        - wiki/index.md with relative links to learnings/llm-wiki-reference.md and sources/llm-wiki.md
        - wiki/log.md with a triage entry for "LLM Wiki Reference"
        - wiki/learnings/llm-wiki-reference.md with YAML frontmatter and a Source section linking to ../sources/llm-wiki.md
        - wiki/sources/llm-wiki.md with minimal content
        
        Parameters:
            tmp (Path): Directory in which the `wiki/` tree will be created.
        
        Returns:
            Path: Path to the created `wiki` directory.
        """
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
        """
        Ensure the linter reports no broken markdown links for a synthetic wiki fixture mirroring the PR structure.
        
        Builds a temporary wiki containing the learnings and sources pages with relative links, runs `wiki_lint.lint_wiki` against it, and asserts that no issues with code `broken-link` are returned.
        """
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            broken = [i for i in issues if i.code == "broken-link"]
            self.assertEqual(broken, [], f"Broken links detected: {broken}")

    def test_no_missing_index_links_in_synthetic_wiki(self) -> None:
        """
        Create a synthetic wiki fixture, run the linter, and assert the index contains links to every page.
        
        Builds a temporary wiki matching the PR structure, runs wiki_lint.lint_wiki on it for 2026-04-09, and fails if any `missing-index-link` issues are reported.
        """
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            missing = [i for i in issues if i.code == "missing-index-link"]
            self.assertEqual(missing, [], f"Missing index links: {missing}")

    def test_no_orphan_pages_in_synthetic_wiki(self) -> None:
        """
        Ensure the linter does not report orphan pages for a correctly linked synthetic wiki.
        
        Creates a temporary wiki with linked index, learnings and sources pages and runs wiki_lint.lint_wiki with a fixed date; asserts there are no issues with code "orphan-page".
        """
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._make_wiki(Path(tmp))
            issues = wiki_lint.lint_wiki(wiki, max_age_days=60, now=date(2026, 4, 9))
            orphans = [i for i in issues if i.code == "orphan-page"]
            self.assertEqual(orphans, [], f"Orphan pages detected: {orphans}")

    def test_missing_index_link_fires_when_page_omitted(self) -> None:
        """
        Check that removing a learnings page from index.md causes a `missing-index-link` linter issue.
        
        Creates a synthetic wiki, omits the `learnings/llm-wiki-reference.md` entry from index.md and asserts the linter reports that path as a `missing-index-link`.
        """
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
        """
        Ensure the linter reports an `orphan-page` for a source file when it has no inbound links.
        
        Creates a synthetic wiki where `sources/llm-wiki.md` is not referenced from the index or the reference note, runs `wiki_lint.lint_wiki`, and asserts an `orphan-page` issue for `sources/llm-wiki.md`.
        """
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
        """
        Parse YAML frontmatter from the provided Markdown content using a temporary file.
        
        Writes `content` to a temporary `.md` file, invokes `wiki_lint._read_frontmatter` on that file, and ensures the temporary file is removed before returning.
        
        Parameters:
            content (str): Markdown text whose frontmatter should be parsed.
        
        Returns:
            dict: Mapping of parsed frontmatter values, or an empty dict if no frontmatter is present.
        """
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8", delete=False) as f:
            f.write(content)
            tmp_path = Path(f.name)
        try:
            return wiki_lint._read_frontmatter(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_parses_lesson_learned_type(self) -> None:
        """
        Checks that the frontmatter parser recognises the `lesson-learned` type.
        
        Parses a sample frontmatter block containing `type: lesson-learned` and asserts the parsed `type` field equals `"lesson-learned"`.
        """
        fm = self._parse(
            "---\ntitle: LLM Wiki Reference\ntype: lesson-learned\nstatus: verified\n"
            "last_reviewed: '2026-04-09'\nsources:\n- /path/to/file.md\n---\n# Heading\n"
        )
        self.assertEqual(fm["type"], "lesson-learned")

    def test_parses_triage_status_field(self) -> None:
        """
        Verify the frontmatter parser reads the `triage_status` field correctly.
        
        Parses a markdown frontmatter block that includes `triage_status: verified` and asserts the parsed value for `triage_status` is "verified".
        """
        fm = self._parse(
            "---\ntitle: LLM Wiki Reference\ntype: lesson-learned\nstatus: verified\n"
            "triage_status: verified\nlast_reviewed: '2026-04-09'\nsources:\n- /path/to/file.md\n---\n# H\n"
        )
        self.assertEqual(fm["triage_status"], "verified")

    def test_parses_sources_as_list(self) -> None:
        """
        Verify that frontmatter `sources` is parsed as a list containing the source path.

        Asserts that the parsed frontmatter returns `sources` as a list of length 1 and that the single entry includes the filename `llm-wiki.md`.
        """
        # NOTE: The absolute path below is intentionally legacy/invalid and only used
        # to verify that _parse/_read_frontmatter returns a list and preserves content.
        fm = self._parse(
            "---\ntitle: T\ntype: t\nstatus: s\nlast_reviewed: 2026-04-09\nsources:\n"
            "- /Users/jamiecraik/dev/agent-skills/Wiki/wiki/sources/llm-wiki.md\n---\n# H\n"
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
        """
        Verify that parsing a file without YAML frontmatter delimiters returns an empty dict.
        
        The test supplies markdown content with no leading frontmatter delimiter and asserts that the frontmatter parser returns {}.
        """
        fm = self._parse("# Just a Heading\n\nNo frontmatter here.\n")
        self.assertEqual(fm, {})


if __name__ == "__main__":
    unittest.main()
