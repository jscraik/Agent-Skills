"""
Structural and content validation tests for PR artifacts:

  - artifacts/recommended-skills-sdk-pipeline.html
  - artifacts/reports/skills-sdk-gap-analysis-current-code-tree-2026-06-03.md

Covers:
  HTML:
    - Valid HTML5 doctype and required meta tags
    - Title and document language
    - All expected lane-filter tabs and view-mode buttons
    - Default aria-pressed states for controls
    - All 15 expected sections with data-lanes attribute
    - CSS custom property declarations in :root
    - JavaScript section with all required function and export names
    - Decision matrix column headers and data row count
    - AX Product Doctrine card count
    - Lifecycle step count (00-20)
    - Pipeline section presence
    - Accessibility attributes (aria-label, aria-live)
    - Correct section aria-labels

  Markdown:
    - Document title and date
    - Executive Recommendation section with Hybrid verdict
    - Decision Frame table with four option rows
    - Evidence Reviewed section
    - Five Current Tree Strengths
    - Ten Critical Gaps
    - Ten Domain-by-Domain Gap Matrix rows
    - Recommended Architecture Move with code block
    - Four phases in What Should Happen Next
    - Final Recommendation section
"""

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

HTML_PATH = REPO_ROOT / "artifacts" / "recommended-skills-sdk-pipeline.html"
MD_PATH = (
    REPO_ROOT
    / "artifacts"
    / "reports"
    / "skills-sdk-gap-analysis-current-code-tree-2026-06-03.md"
)


# ---------------------------------------------------------------------------
# Minimal HTML parser to collect elements and attributes
# ---------------------------------------------------------------------------


class _ElementCollector(HTMLParser):
    """Collect all start tags, their attributes, and raw text content."""

    def __init__(self):
        super().__init__()
        self.elements: list[dict] = []  # list of {tag, attrs, attrs_dict}
        self._in_style: bool = False
        self._in_script: bool = False
        self.style_text: str = ""
        self.script_text: str = ""
        self._raw_data: list[str] = []

    # ---- overrides --------------------------------------------------------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)
        self.elements.append({"tag": tag, "attrs": attrs, "attrs_dict": attrs_dict})
        self._in_style = tag == "style"
        self._in_script = tag == "script"

    def handle_endtag(self, tag: str):
        if tag in ("style", "script"):
            self._in_style = False
            self._in_script = False

    def handle_data(self, data: str):
        self._raw_data.append(data)
        if self._in_style:
            self.style_text += data
        if self._in_script:
            self.script_text += data

    # ---- helpers ----------------------------------------------------------

    def find_all(self, tag: str) -> list[dict]:
        return [el for el in self.elements if el["tag"] == tag]

    def find_all_with_attr(self, tag: str, attr: str) -> list[dict]:
        return [
            el
            for el in self.elements
            if el["tag"] == tag and attr in el["attrs_dict"]
        ]

    def find_all_with_attr_value(
        self, tag: str, attr: str, value: str
    ) -> list[dict]:
        return [
            el
            for el in self.elements
            if el["tag"] == tag and el["attrs_dict"].get(attr) == value
        ]


def _parse_html(path: Path) -> _ElementCollector:
    collector = _ElementCollector()
    collector.feed(path.read_text(encoding="utf-8"))
    return collector


# ---------------------------------------------------------------------------
# HTML tests — document structure
# ---------------------------------------------------------------------------


class TestHtmlFileExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(HTML_PATH.exists(), f"HTML artifact not found at {HTML_PATH}")

    def test_file_is_non_empty(self):
        content = HTML_PATH.read_text(encoding="utf-8")
        self.assertGreater(len(content), 1000, "HTML file appears too small")


class TestHtmlDocumentStructure(unittest.TestCase):
    def setUp(self):
        self._raw = HTML_PATH.read_text(encoding="utf-8")
        self._doc = _parse_html(HTML_PATH)

    def test_has_html5_doctype(self):
        self.assertTrue(
            self._raw.lstrip().lower().startswith("<!doctype html"),
            "HTML file must begin with <!doctype html>",
        )

    def test_html_element_has_lang_en(self):
        html_els = self._doc.find_all_with_attr_value("html", "lang", "en")
        self.assertEqual(
            len(html_els), 1, "Expected exactly one <html lang='en'> element"
        )

    def test_charset_meta_present(self):
        metas = self._doc.find_all("meta")
        charsets = [
            m for m in metas if m["attrs_dict"].get("charset", "").lower() == "utf-8"
        ]
        self.assertEqual(len(charsets), 1, "Expected <meta charset='utf-8'>")

    def test_viewport_meta_present(self):
        metas = self._doc.find_all("meta")
        viewports = [
            m for m in metas if m["attrs_dict"].get("name", "").lower() == "viewport"
        ]
        self.assertGreater(len(viewports), 0, "Expected a viewport meta tag")

    def test_title_is_correct(self):
        self.assertIn("Skills SDK Pipeline Design Map", self._raw)

    def test_has_body_element(self):
        bodies = self._doc.find_all("body")
        self.assertEqual(len(bodies), 1, "Expected exactly one <body> element")

    def test_has_main_element(self):
        mains = self._doc.find_all("main")
        self.assertEqual(len(mains), 1, "Expected exactly one <main> element")

    def test_has_header_element(self):
        headers = self._doc.find_all("header")
        self.assertGreater(len(headers), 0, "Expected at least one <header> element")


# ---------------------------------------------------------------------------
# HTML tests — navigation controls
# ---------------------------------------------------------------------------


class TestHtmlLaneTabs(unittest.TestCase):
    """All 10 lane-filter tabs must be present with correct data-lane-filter values."""

    EXPECTED_LANES = {
        "all",
        "agent",
        "package",
        "runtime",
        "security",
        "testing",
        "evalops",
        "knowledge",
        "plugin",
        "governance",
    }

    def setUp(self):
        self._doc = _parse_html(HTML_PATH)
        self._tabs = self._doc.find_all_with_attr("button", "data-lane-filter")

    def test_tab_count_is_ten(self):
        self.assertEqual(len(self._tabs), 10, "Expected exactly 10 lane-filter tabs")

    def test_all_lane_filter_values_present(self):
        found = {t["attrs_dict"]["data-lane-filter"] for t in self._tabs}
        self.assertEqual(found, self.EXPECTED_LANES)

    def test_all_tab_has_aria_pressed_true(self):
        all_tabs = [
            t for t in self._tabs if t["attrs_dict"].get("data-lane-filter") == "all"
        ]
        self.assertEqual(len(all_tabs), 1, "Expected exactly one 'all' tab")
        self.assertEqual(
            all_tabs[0]["attrs_dict"].get("aria-pressed"),
            "true",
            "The 'All' tab must start with aria-pressed='true'",
        )

    def test_non_all_tabs_have_aria_pressed_false(self):
        for tab in self._tabs:
            lane = tab["attrs_dict"].get("data-lane-filter")
            if lane == "all":
                continue
            with self.subTest(lane=lane):
                self.assertEqual(
                    tab["attrs_dict"].get("aria-pressed"),
                    "false",
                    f"Non-active tab '{lane}' must start with aria-pressed='false'",
                )

    def test_all_tabs_have_type_button(self):
        for tab in self._tabs:
            with self.subTest(lane=tab["attrs_dict"].get("data-lane-filter")):
                self.assertEqual(tab["attrs_dict"].get("type"), "button")

    def test_all_tabs_have_atlas_tab_class(self):
        for tab in self._tabs:
            with self.subTest(lane=tab["attrs_dict"].get("data-lane-filter")):
                self.assertIn("atlas-tab", tab["attrs_dict"].get("class", ""))


class TestHtmlViewModes(unittest.TestCase):
    """All 8 view-mode buttons must be present with correct data-view-mode values."""

    EXPECTED_MODES = {
        "all",
        "overview",
        "lifecycle",
        "sdk",
        "knowledge",
        "evalops",
        "runtime",
        "outputs",
    }

    def setUp(self):
        self._doc = _parse_html(HTML_PATH)
        self._modes = self._doc.find_all_with_attr("button", "data-view-mode")

    def test_mode_count_is_eight(self):
        self.assertEqual(len(self._modes), 8, "Expected exactly 8 view-mode buttons")

    def test_all_view_mode_values_present(self):
        found = {m["attrs_dict"]["data-view-mode"] for m in self._modes}
        self.assertEqual(found, self.EXPECTED_MODES)

    def test_full_map_mode_has_aria_pressed_true(self):
        full_map = [
            m for m in self._modes if m["attrs_dict"].get("data-view-mode") == "all"
        ]
        self.assertEqual(len(full_map), 1, "Expected exactly one 'all' view mode")
        self.assertEqual(
            full_map[0]["attrs_dict"].get("aria-pressed"),
            "true",
            "The 'Full Map' (all) mode must start with aria-pressed='true'",
        )

    def test_non_full_map_modes_have_aria_pressed_false(self):
        for mode in self._modes:
            vm = mode["attrs_dict"].get("data-view-mode")
            if vm == "all":
                continue
            with self.subTest(view_mode=vm):
                self.assertEqual(
                    mode["attrs_dict"].get("aria-pressed"),
                    "false",
                    f"Non-active mode '{vm}' must start with aria-pressed='false'",
                )

    def test_all_modes_have_atlas_mode_class(self):
        for mode in self._modes:
            with self.subTest(view_mode=mode["attrs_dict"].get("data-view-mode")):
                self.assertIn("atlas-mode", mode["attrs_dict"].get("class", ""))


# ---------------------------------------------------------------------------
# HTML tests — sections with data-lanes
# ---------------------------------------------------------------------------


class TestHtmlSections(unittest.TestCase):
    """All expected filterable sections must be present with correct attributes."""

    EXPECTED_SECTION_LABELS = {
        "AX product doctrine",
        "Agent execution and control plane",
        "Full skill lifecycle",
        "Release decision matrix",
        "Public SDK surface and developer loop",
        "Domain model integrity lane",
        "Knowledge engineering and context acquisition lane",
        "Complexity control lane",
        "Language engineering lane",
        "Compiler and emitter discipline lane",
        "Data reliability and evolution lane",
        "Testing strategy and quality evidence lane",
        "Codex plugin distribution and host integration lane",
        "AI eval operations and evaluative evidence lane",
        "Skills SDK pipeline from source to emitted artifacts",
    }

    def setUp(self):
        self._doc = _parse_html(HTML_PATH)
        self._raw = HTML_PATH.read_text(encoding="utf-8")
        self._sections_with_lanes = self._doc.find_all_with_attr(
            "section", "data-lanes"
        )

    def test_section_count_is_fifteen(self):
        self.assertEqual(
            len(self._sections_with_lanes),
            15,
            f"Expected 15 sections with data-lanes, found {len(self._sections_with_lanes)}",
        )

    def test_all_expected_section_labels_present(self):
        """Every expected aria-label must appear in the HTML source."""
        for label in self.EXPECTED_SECTION_LABELS:
            with self.subTest(label=label):
                self.assertIn(
                    label,
                    self._raw,
                    f"Expected section aria-label '{label}' not found in HTML",
                )

    def test_doctrine_section_data_lanes(self):
        """Doctrine section must appear in all 9 non-'all' lanes."""
        doctrine_sections = [
            s
            for s in self._sections_with_lanes
            if s["attrs_dict"].get("aria-label") == "AX product doctrine"
        ]
        self.assertEqual(len(doctrine_sections), 1)
        lanes = doctrine_sections[0]["attrs_dict"]["data-lanes"].split()
        for lane in ["agent", "package", "runtime", "security", "testing",
                     "evalops", "knowledge", "plugin", "governance"]:
            with self.subTest(lane=lane):
                self.assertIn(lane, lanes)

    def test_pipeline_section_present(self):
        pipeline_sections = [
            s
            for s in self._sections_with_lanes
            if "pipeline" in (s["attrs_dict"].get("aria-label") or "").lower()
        ]
        self.assertGreater(len(pipeline_sections), 0, "Pipeline section not found")

    def test_all_sections_have_data_collapsible(self):
        """Every data-lanes section must also declare data-collapsible."""
        for section in self._sections_with_lanes:
            label = section["attrs_dict"].get("aria-label", "(no label)")
            with self.subTest(label=label):
                self.assertIn(
                    "data-collapsible",
                    section["attrs_dict"],
                    f"Section '{label}' missing data-collapsible attribute",
                )

    def test_all_sections_have_data_views(self):
        """Every data-lanes section must also declare data-views."""
        for section in self._sections_with_lanes:
            label = section["attrs_dict"].get("aria-label", "(no label)")
            with self.subTest(label=label):
                self.assertIn(
                    "data-views",
                    section["attrs_dict"],
                    f"Section '{label}' missing data-views attribute",
                )


# ---------------------------------------------------------------------------
# HTML tests — accessibility
# ---------------------------------------------------------------------------


class TestHtmlAccessibility(unittest.TestCase):
    def setUp(self):
        self._raw = HTML_PATH.read_text(encoding="utf-8")
        self._doc = _parse_html(HTML_PATH)

    def test_atlas_status_has_aria_live_polite(self):
        divs = self._doc.find_all("div")
        status_divs = [
            d
            for d in divs
            if d["attrs_dict"].get("aria-live") == "polite"
        ]
        self.assertGreater(
            len(status_divs), 0, "Expected at least one div with aria-live='polite'"
        )

    def test_nav_has_aria_label(self):
        navs = self._doc.find_all("nav")
        self.assertGreater(len(navs), 0, "Expected at least one <nav> element")
        for nav in navs:
            self.assertIn(
                "aria-label",
                nav["attrs_dict"],
                "Every <nav> should have an aria-label",
            )

    def test_atlas_tabs_div_has_aria_label(self):
        self.assertIn('aria-label="Architecture lanes"', self._raw)

    def test_atlas_modes_div_has_aria_label(self):
        self.assertIn('aria-label="Design map view modes"', self._raw)

    def test_sections_have_aria_labels(self):
        sections = self._doc.find_all("section")
        for section in sections:
            with self.subTest(attrs=section["attrs_dict"]):
                # Sections with data-lanes must have aria-label
                if "data-lanes" in section["attrs_dict"]:
                    self.assertIn(
                        "aria-label",
                        section["attrs_dict"],
                        "Section with data-lanes must have aria-label",
                    )


# ---------------------------------------------------------------------------
# HTML tests — CSS custom properties
# ---------------------------------------------------------------------------


class TestHtmlCssCustomProperties(unittest.TestCase):
    EXPECTED_VARS = [
        "--ink",
        "--muted",
        "--line",
        "--paper",
        "--panel",
        "--source",
        "--parse",
        "--ir",
        "--pass",
        "--emit",
        "--risk",
        "--runtime",
        "--complexity",
        "--data",
        "--language",
        "--testing",
        "--plugin",
        "--evalops",
        "--agent",
        "--knowledge",
        "--doctrine",
        "--shadow",
    ]

    def setUp(self):
        self._doc = _parse_html(HTML_PATH)

    def test_root_block_has_all_expected_css_vars(self):
        style = self._doc.style_text
        self.assertIn(":root", style, "Expected :root block in <style>")
        for var in self.EXPECTED_VARS:
            with self.subTest(var=var):
                self.assertIn(
                    var, style, f"CSS custom property '{var}' not found in :root"
                )

    def test_box_sizing_border_box_present(self):
        self.assertIn("box-sizing: border-box", self._doc.style_text)

    def test_responsive_media_queries_present(self):
        style = self._doc.style_text
        # Expect both breakpoints: 1120px and 720px
        self.assertIn("1120px", style)
        self.assertIn("720px", style)


# ---------------------------------------------------------------------------
# HTML tests — JavaScript section
# ---------------------------------------------------------------------------


class TestHtmlJavaScript(unittest.TestCase):
    """Key functions and window exports must exist in the embedded script."""

    REQUIRED_FUNCTION_NAMES = [
        "applyAtlasFilters",
        "setLane",
        "setViewMode",
        "toggleSection",
        "sectionTitle",
    ]

    REQUIRED_WINDOW_EXPORTS = [
        "window.setAtlasLane",
        "window.setAtlasViewMode",
        "window.toggleAtlasSection",
    ]

    REQUIRED_LANE_LABELS = [
        "all",
        "package",
        "runtime",
        "security",
        "testing",
        "evalops",
        "knowledge",
        "plugin",
        "governance",
        "agent",
    ]

    REQUIRED_MODE_LABELS = [
        "overview",
        "lifecycle",
        "sdk",
        "evalops",
        "runtime",
        "outputs",
    ]

    def setUp(self):
        self._doc = _parse_html(HTML_PATH)
        self._script = self._doc.script_text

    def test_script_block_is_non_empty(self):
        self.assertGreater(
            len(self._script.strip()), 200, "Script block appears empty or too small"
        )

    def test_all_required_functions_defined(self):
        for fn in self.REQUIRED_FUNCTION_NAMES:
            with self.subTest(function=fn):
                self.assertIn(
                    fn,
                    self._script,
                    f"Function '{fn}' not found in script block",
                )

    def test_all_window_exports_present(self):
        for export in self.REQUIRED_WINDOW_EXPORTS:
            with self.subTest(export=export):
                self.assertIn(
                    export,
                    self._script,
                    f"Window export '{export}' not found in script",
                )

    def test_lane_labels_object_has_all_keys(self):
        for lane in self.REQUIRED_LANE_LABELS:
            with self.subTest(lane=lane):
                self.assertIn(
                    lane,
                    self._script,
                    f"laneLabels key '{lane}' not found in script",
                )

    def test_mode_labels_object_has_expected_keys(self):
        for mode in self.REQUIRED_MODE_LABELS:
            with self.subTest(mode=mode):
                self.assertIn(
                    mode,
                    self._script,
                    f"modeLabels key '{mode}' not found in script",
                )

    def test_atlas_tab_selector_used(self):
        self.assertIn(".atlas-tab", self._script)

    def test_atlas_mode_selector_used(self):
        self.assertIn(".atlas-mode", self._script)

    def test_data_lanes_selector_used(self):
        self.assertIn("[data-lanes]", self._script)

    def test_aria_pressed_is_set_in_filter(self):
        self.assertIn("aria-pressed", self._script)

    def test_section_collapse_button_created(self):
        self.assertIn("lane-collapse", self._script)

    def test_filter_logic_handles_all_lane(self):
        """applyAtlasFilters must branch on activeLane === 'all'."""
        self.assertIn('activeLane === "all"', self._script)

    def test_filter_logic_handles_all_mode(self):
        """applyAtlasFilters must branch on activeMode === 'all'."""
        self.assertIn('activeMode === "all"', self._script)

    def test_lane_muted_class_toggled(self):
        self.assertIn("lane-muted", self._script)

    def test_click_listeners_registered_for_tabs(self):
        self.assertIn("addEventListener", self._script)
        self.assertIn("setLane", self._script)

    def test_click_listeners_registered_for_modes(self):
        self.assertIn("setViewMode", self._script)


# ---------------------------------------------------------------------------
# HTML tests — decision matrix content
# ---------------------------------------------------------------------------


class TestHtmlDecisionMatrix(unittest.TestCase):
    """Release decision matrix must have 7 headers and 11 data rows."""

    EXPECTED_CLAIM_TEXTS = [
        "Safe to publish",
        "Safe to install",
        "Safe to run",
        "Safe to upgrade",
        "Safe to migrate",
        "Safe to rollback",
        "Safe to keep installed",
        "Safe to archive",
        "Safe to decommission",
        "AX doctrine satisfied",
        "Insufficient evidence",
    ]

    EXPECTED_COLUMN_HEADERS = [
        "Claim",
        "Required Evidence",
        "Owner/Approver",
        "Expiry",
        "Blocking Failures",
        "Waiver Rule",
        "Receipt Emitted",
    ]

    def setUp(self):
        self._raw = HTML_PATH.read_text(encoding="utf-8")

    def test_all_column_headers_present(self):
        for header in self.EXPECTED_COLUMN_HEADERS:
            with self.subTest(header=header):
                self.assertIn(
                    header, self._raw, f"Column header '{header}' not found in HTML"
                )

    def test_all_claim_rows_present(self):
        for claim in self.EXPECTED_CLAIM_TEXTS:
            with self.subTest(claim=claim):
                self.assertIn(
                    claim, self._raw, f"Decision matrix claim '{claim}' not found"
                )

    def test_matrix_grid_class_present(self):
        self.assertIn("matrix-grid", self._raw)

    def test_release_gate_report_present(self):
        self.assertIn("Release Gate Report", self._raw)

    def test_rollback_receipt_present(self):
        self.assertIn("Rollback Receipt", self._raw)


# ---------------------------------------------------------------------------
# HTML tests — lifecycle steps
# ---------------------------------------------------------------------------


class TestHtmlLifecycleSteps(unittest.TestCase):
    """All 21 lifecycle steps (00-20) must be present."""

    EXPECTED_STEPS = [
        ("00", "Discover and Triage"),
        ("01", "Research"),
        ("02", "Knowledge Capture"),
        ("03", "Knowledge Distillation"),
        ("04", "Design"),
        ("05", "Author"),
        ("06", "Compile"),
        ("07", "Review"),
        ("08", "Evaluate"),
        ("09", "Gate and Sign"),
        ("10", "Stage Rollout"),
        ("11", "Publish"),
        ("12", "Install"),
        ("13", "Run"),
        ("14", "Operate and Monitor"),
        ("15", "Incident Response"),
        ("16", "Reattest"),
        ("17", "Update, Roll Back, Revoke"),
        ("18", "Deprecate and Migrate"),
        ("19", "Archive and Replace"),
        ("20", "Decommission"),
    ]

    def setUp(self):
        self._raw = HTML_PATH.read_text(encoding="utf-8")

    def test_all_21_lifecycle_steps_present(self):
        for num, title in self.EXPECTED_STEPS:
            with self.subTest(step=num, title=title):
                self.assertIn(
                    title,
                    self._raw,
                    f"Lifecycle step {num} '{title}' not found in HTML",
                )

    def test_feedback_loop_element_present(self):
        self.assertIn("Feedback loop", self._raw)

    def test_lifecycle_step_count_matches_life_step_class(self):
        """life-step class count should match expected step count."""
        count = self._raw.count('class="life-step"')
        self.assertEqual(count, 21, f"Expected 21 life-step elements, found {count}")


# ---------------------------------------------------------------------------
# HTML tests — AX doctrine cards
# ---------------------------------------------------------------------------


class TestHtmlDoctrineCards(unittest.TestCase):
    EXPECTED_CARD_TITLES = [
        "Thin Surface",
        "Strong Guardrails",
        "Durable Memory",
        "Professional Output",
        "Progressive Disclosure",
        "Token Efficiency",
        "Cognitive Complexity Budget",
        "Agent Experience",
    ]

    def setUp(self):
        self._raw = HTML_PATH.read_text(encoding="utf-8")

    def test_all_doctrine_card_titles_present(self):
        for title in self.EXPECTED_CARD_TITLES:
            with self.subTest(title=title):
                self.assertIn(
                    title, self._raw, f"Doctrine card title '{title}' not found"
                )

    def test_doctrine_card_count_is_eight(self):
        count = self._raw.count('class="doctrine-card"')
        self.assertEqual(count, 8, f"Expected 8 doctrine-card elements, found {count}")

    def test_mantra_text_present(self):
        """The mantra should match the AX doctrine tagline."""
        self.assertIn(
            "Thin surface. Strong guardrails. Durable memory. Professional output.",
            self._raw,
        )


# ---------------------------------------------------------------------------
# HTML tests — pipeline section
# ---------------------------------------------------------------------------


class TestHtmlPipelineSection(unittest.TestCase):
    EXPECTED_STAGE_CLASSES = ["source", "parse", "ir", "passes", "emitters"]
    EXPECTED_STAGE_TITLES = [
        "Canonical Skill Source",
        "Parse and Normalize",
        "Skill IR",
        "Domain Passes",
        "Emitters and Outputs",
    ]

    def setUp(self):
        self._raw = HTML_PATH.read_text(encoding="utf-8")

    def test_pipeline_section_exists(self):
        self.assertIn('class="pipeline"', self._raw)

    def test_all_stage_classes_present(self):
        for cls in self.EXPECTED_STAGE_CLASSES:
            with self.subTest(stage=cls):
                self.assertIn(
                    f'class="stage {cls}"',
                    self._raw,
                    f"Pipeline stage '{cls}' not found",
                )

    def test_all_stage_titles_present(self):
        for title in self.EXPECTED_STAGE_TITLES:
            with self.subTest(title=title):
                self.assertIn(
                    title, self._raw, f"Pipeline stage title '{title}' not found"
                )

    def test_ir_core_element_present(self):
        self.assertIn("ir-core", self._raw)

    def test_assurance_section_present(self):
        self.assertIn('class="assurance"', self._raw)

    def test_arrow_connectors_present(self):
        count = self._raw.count('class="arrow"')
        self.assertGreater(count, 0, "Expected at least one arrow connector element")


# ---------------------------------------------------------------------------
# Markdown tests — file structure
# ---------------------------------------------------------------------------


class TestMarkdownFileExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(MD_PATH.exists(), f"Markdown artifact not found at {MD_PATH}")

    def test_file_is_non_empty(self):
        content = MD_PATH.read_text(encoding="utf-8")
        self.assertGreater(len(content), 500, "Markdown file appears too small")


class TestMarkdownDocumentStructure(unittest.TestCase):
    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")
        self._lines = self._content.splitlines()

    def test_title_header_present(self):
        self.assertIn(
            "# Skills SDK Gap Analysis Report: Current Code Tree", self._content
        )

    def test_date_is_present(self):
        self.assertIn("2026-06-03", self._content)

    def test_executive_recommendation_section_present(self):
        self.assertIn("## Executive Recommendation", self._content)

    def test_hybrid_verdict_stated(self):
        self.assertIn("**Hybrid**", self._content)

    def test_decision_frame_section_present(self):
        self.assertIn("## Decision Frame", self._content)

    def test_evidence_reviewed_section_present(self):
        self.assertIn("## Evidence Reviewed", self._content)

    def test_current_tree_strengths_section_present(self):
        self.assertIn("## Current Tree Strengths", self._content)

    def test_critical_gaps_section_present(self):
        self.assertIn("## Critical Gaps", self._content)

    def test_gap_matrix_section_present(self):
        self.assertIn("## Domain-by-Domain Gap Matrix", self._content)

    def test_recommended_architecture_section_present(self):
        self.assertIn("## Recommended Architecture Move", self._content)

    def test_what_should_happen_next_section_present(self):
        self.assertIn("## What Should Happen Next", self._content)

    def test_final_recommendation_section_present(self):
        self.assertIn("## Final Recommendation", self._content)


# ---------------------------------------------------------------------------
# Markdown tests — Decision Frame table
# ---------------------------------------------------------------------------


class TestMarkdownDecisionFrameTable(unittest.TestCase):
    EXPECTED_OPTIONS = [
        "Refactor in place",
        "Extract new module",
        "Create new project",
        "Hybrid",
    ]

    EXPECTED_VERDICTS = [
        "Good, but risky alone",
        "Best immediate move",
        "Too early",
        "Recommended",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_table_has_option_column(self):
        self.assertIn("| Option |", self._content)

    def test_table_has_verdict_column(self):
        self.assertIn("| Verdict |", self._content)

    def test_table_has_why_column(self):
        self.assertIn("| Why |", self._content)

    def test_all_four_options_present(self):
        for option in self.EXPECTED_OPTIONS:
            with self.subTest(option=option):
                self.assertIn(
                    option,
                    self._content,
                    f"Decision option '{option}' not found in markdown",
                )

    def test_all_verdicts_present(self):
        for verdict in self.EXPECTED_VERDICTS:
            with self.subTest(verdict=verdict):
                self.assertIn(
                    verdict,
                    self._content,
                    f"Decision verdict '{verdict}' not found in markdown",
                )

    def test_hybrid_is_recommended(self):
        """The Hybrid row must be marked as Recommended."""
        # Check that 'Recommended' appears somewhere after 'Hybrid' in the table
        hybrid_idx = self._content.find("| Hybrid |")
        self.assertGreater(hybrid_idx, -1, "Hybrid row not found in table")
        recommended_idx = self._content.find("Recommended", hybrid_idx)
        self.assertGreater(
            recommended_idx, hybrid_idx, "'Recommended' must follow the Hybrid row"
        )


# ---------------------------------------------------------------------------
# Markdown tests — Evidence Reviewed
# ---------------------------------------------------------------------------


class TestMarkdownEvidenceReviewed(unittest.TestCase):
    EXPECTED_EVIDENCE_ITEMS = [
        "ARCHITECTURE.md",
        "UBIQUITOUS_LANGUAGE.md",
        "Infrastructure/config/skills-sdk.json",
        "skills_sdk",
        "skills_impl.py",
        "Infrastructure/tests/**",
        "artifacts/recommended-skills-sdk-pipeline.html",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_key_evidence_items_listed(self):
        for item in self.EXPECTED_EVIDENCE_ITEMS:
            with self.subTest(item=item):
                self.assertIn(
                    item,
                    self._content,
                    f"Evidence item '{item}' not found in Evidence Reviewed section",
                )

    def test_repo_status_validation_command_present(self):
        self.assertIn("repo status", self._content)

    def test_bin_ask_command_mentioned(self):
        self.assertIn("./bin/ask", self._content)


# ---------------------------------------------------------------------------
# Markdown tests — Current Tree Strengths
# ---------------------------------------------------------------------------


class TestMarkdownCurrentTreeStrengths(unittest.TestCase):
    EXPECTED_STRENGTHS = [
        "SDK-Like Control Plane",
        "Skill Package Contracts",
        "Project-Local Skill Manifest",
        "Eval and Tessl Support",
        "Deep Modules",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_at_least_five_strengths_present(self):
        """All five Current Tree Strength headers must appear."""
        for strength in self.EXPECTED_STRENGTHS:
            with self.subTest(strength=strength):
                self.assertIn(
                    strength,
                    self._content,
                    f"Strength '{strength}' not found in markdown",
                )

    def test_five_numbered_strength_sections(self):
        """Strengths are numbered 1-5 using ### N. prefix."""
        count = len(re.findall(r"^### \d+\.", self._content, re.MULTILINE))
        self.assertGreaterEqual(
            count, 5, f"Expected at least 5 numbered strength sections, found {count}"
        )


# ---------------------------------------------------------------------------
# Markdown tests — Critical Gaps
# ---------------------------------------------------------------------------


class TestMarkdownCriticalGaps(unittest.TestCase):
    EXPECTED_GAP_TITLES = [
        "Project Manifest Validation Is Not Strong Enough",
        "Lifecycle Defaults Are Ambiguous",
        "Command Surface Authority Is Duplicated",
        "skills init` Is Repo-Coupled",
        "SDK Identity Is Still Tied to Current Branding",
        "Runtime Enforcement Is Mostly Modeled, Not Enforced",
        "Eval Ops Are Strong but Fragmented",
        "Knowledge Engineering Is Not Yet a Package Contract",
        "Registry, Install, Publish, and Package Manager",
        "Governance Is Strong but Not Yet SDK-State-Machine Strong",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_ten_gaps_numbered(self):
        gap_headers = re.findall(r"^### Gap \d+:", self._content, re.MULTILINE)
        self.assertEqual(
            len(gap_headers),
            10,
            f"Expected 10 '### Gap N:' headers, found {len(gap_headers)}",
        )

    def test_gap_numbers_are_sequential_one_to_ten(self):
        gap_nums = re.findall(r"### Gap (\d+):", self._content)
        self.assertEqual(
            [int(n) for n in gap_nums],
            list(range(1, 11)),
            "Gap numbers must be sequential from 1 to 10",
        )

    def test_all_gap_titles_present(self):
        for title in self.EXPECTED_GAP_TITLES:
            with self.subTest(title=title):
                self.assertIn(
                    title, self._content, f"Gap title fragment '{title}' not found"
                )

    def test_each_gap_has_decision_classification(self):
        """Each Gap section must end with a 'Decision classification:' line."""
        decisions = re.findall(r"Decision classification:", self._content)
        self.assertEqual(
            len(decisions),
            10,
            f"Expected 10 Decision classification lines, found {len(decisions)}",
        )

    def test_gap1_blocked_manifest_state_mentioned(self):
        """Gap 1 must describe the three manifest states."""
        self.assertIn("absent", self._content)
        self.assertIn("valid", self._content)
        self.assertIn("invalid", self._content)

    def test_gap6_fail_closed_mentioned(self):
        self.assertIn("fail-closed", self._content)


# ---------------------------------------------------------------------------
# Markdown tests — Domain-by-Domain Gap Matrix
# ---------------------------------------------------------------------------


class TestMarkdownGapMatrix(unittest.TestCase):
    EXPECTED_SDK_DOMAINS = [
        "Authoring SDK",
        "Package SDK",
        "Skill IR/compiler",
        "Security SDK",
        "Runtime SDK",
        "Eval SDK",
        "Knowledge SDK",
        "Registry SDK",
        "Governance SDK",
        "AX/DX",
    ]

    EXPECTED_RECOMMENDED_MOVES = [
        "Refactor in place",
        "Internal SDK module",
        "New internal module",
        "Consolidate in module",
        "New package contract",
        "Hybrid",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_all_sdk_domains_present(self):
        for domain in self.EXPECTED_SDK_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(
                    domain,
                    self._content,
                    f"SDK domain '{domain}' not found in gap matrix",
                )

    def test_gap_matrix_table_has_headers(self):
        self.assertIn("| SDK Domain |", self._content)
        self.assertIn("| Current Tree Status |", self._content)
        self.assertIn("| Main Gap |", self._content)
        self.assertIn("| Recommended Move |", self._content)

    def test_gap_matrix_has_ten_data_rows(self):
        """Count table rows that follow the separator row."""
        # Find the gap matrix section
        matrix_start = self._content.find("## Domain-by-Domain Gap Matrix")
        self.assertGreater(matrix_start, -1)
        matrix_section = self._content[matrix_start:]
        # Data rows start with | (non-separator, non-header)
        data_rows = re.findall(
            r"^\| [A-Z][^-].*\|$", matrix_section, re.MULTILINE
        )
        # Header row + 10 data rows = 11 rows starting with capital letters
        # Subtract the header row
        non_header = [r for r in data_rows if "SDK Domain" not in r]
        self.assertEqual(
            len(non_header),
            10,
            f"Expected 10 data rows in gap matrix, found {len(non_header)}: {non_header}",
        )

    def test_recommended_moves_vocabulary_present(self):
        for move in self.EXPECTED_RECOMMENDED_MOVES:
            with self.subTest(move=move):
                self.assertIn(
                    move, self._content, f"Recommended move '{move}' not found"
                )


# ---------------------------------------------------------------------------
# Markdown tests — Recommended Architecture Move
# ---------------------------------------------------------------------------


class TestMarkdownArchitectureMove(unittest.TestCase):
    EXPECTED_DIRECTORIES = [
        "ir.py",
        "manifests.py",
        "diagnostics.py",
        "commands.py",
        "receipts.py",
        "authoring/",
        "package/",
        "security/",
        "runtime/",
        "evals/",
        "knowledge/",
        "registry/",
        "governance/",
        "adapters/",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_architecture_code_block_present(self):
        self.assertIn("```text", self._content)

    def test_skills_sdk_core_path_mentioned(self):
        self.assertIn("skills_sdk/", self._content)

    def test_adapters_section_mentioned(self):
        self.assertIn("adapters/", self._content)

    def test_agent_skills_kit_adapter_mentioned(self):
        self.assertIn("agent_skills_kit_repo.py", self._content)

    def test_key_proposed_modules_present(self):
        for d in self.EXPECTED_DIRECTORIES:
            with self.subTest(directory=d):
                self.assertIn(
                    d,
                    self._content,
                    f"Proposed directory/file '{d}' not in architecture move",
                )

    def test_sdk_boundary_explanation_present(self):
        self.assertIn("SDK core = portable contracts", self._content)
        self.assertIn("Adapters =", self._content)


# ---------------------------------------------------------------------------
# Markdown tests — What Should Happen Next (phases)
# ---------------------------------------------------------------------------


class TestMarkdownPhasePlan(unittest.TestCase):
    EXPECTED_PHASE_TITLES = [
        "Phase 0: Stabilize Current Control Points",
        "Phase 1: Define the SDK Core Contract",
        "Phase 2: Consolidate Existing Tooling Into Domains",
        "Phase 3: Run Owner-Repo Portability Fixtures",
        "Phase 4: Decide Whether to Extract",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_all_five_phases_present(self):
        for phase in self.EXPECTED_PHASE_TITLES:
            with self.subTest(phase=phase):
                self.assertIn(
                    phase,
                    self._content,
                    f"Phase heading '{phase}' not found in markdown",
                )

    def test_phase_0_highest_leverage_mentioned(self):
        self.assertIn("Highest leverage fixes", self._content)

    def test_phase_3_extraction_gate_mentioned(self):
        self.assertIn("extraction gate", self._content)

    def test_phase_4_extract_criteria_listed(self):
        """Phase 4 must list several extraction criteria."""
        self.assertIn("Extract only when", self._content)
        self.assertIn("SDK core imports no repo-specific constants", self._content)


# ---------------------------------------------------------------------------
# Markdown tests — Final Recommendation
# ---------------------------------------------------------------------------


class TestMarkdownFinalRecommendation(unittest.TestCase):
    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_final_recommendation_is_hybrid(self):
        final_idx = self._content.find("## Final Recommendation")
        self.assertGreater(final_idx, -1)
        final_section = self._content[final_idx:]
        self.assertIn(
            "**Hybrid**",
            final_section,
            "Final Recommendation must state Hybrid verdict",
        )

    def test_final_recommendation_mentions_incubation(self):
        final_idx = self._content.find("## Final Recommendation")
        final_section = self._content[final_idx:]
        self.assertIn("incubation", final_section)

    def test_final_recommendation_describes_first_implementation_slice(self):
        self.assertIn(
            "Project manifest hardening", self._content
        )

    def test_final_recommendation_code_block_present(self):
        """The final recommendation should contain a summary code block."""
        final_idx = self._content.find("## Final Recommendation")
        final_section = self._content[final_idx:]
        self.assertIn("```text", final_section)

    def test_refactor_not_discard_sentiment(self):
        """Report must caution against starting from scratch."""
        # The sentence is wrapped across lines in the markdown source.
        self.assertIn("from scratch would discard", self._content)


# ---------------------------------------------------------------------------
# Boundary / regression tests
# ---------------------------------------------------------------------------


class TestHtmlLaneModeConsistency(unittest.TestCase):
    """Lanes declared in section data-lanes must align with lane tab filter values."""

    VALID_LANE_VALUES = {
        "agent", "package", "runtime", "security", "testing",
        "evalops", "knowledge", "plugin", "governance",
    }

    def setUp(self):
        self._doc = _parse_html(HTML_PATH)

    def test_all_section_lanes_are_known_values(self):
        sections = self._doc.find_all_with_attr("section", "data-lanes")
        for section in sections:
            label = section["attrs_dict"].get("aria-label", "(no label)")
            lanes = section["attrs_dict"]["data-lanes"].split()
            for lane in lanes:
                with self.subTest(section=label, lane=lane):
                    self.assertIn(
                        lane,
                        self.VALID_LANE_VALUES,
                        f"Section '{label}' declares unknown lane '{lane}'",
                    )

    def test_all_section_views_are_known_values(self):
        valid_views = {
            "overview", "lifecycle", "sdk", "knowledge", "evalops",
            "runtime", "outputs",
        }
        sections = self._doc.find_all_with_attr("section", "data-views")
        for section in sections:
            label = section["attrs_dict"].get("aria-label", "(no label)")
            views = section["attrs_dict"]["data-views"].split()
            for view in views:
                with self.subTest(section=label, view=view):
                    self.assertIn(
                        view,
                        valid_views,
                        f"Section '{label}' declares unknown view '{view}'",
                    )


class TestMarkdownNoBrokenInternalReferences(unittest.TestCase):
    """Internal file paths mentioned in Evidence Reviewed must be real."""

    EXPECTED_PATHS_RELATIVE = [
        "ARCHITECTURE.md",
        "UBIQUITOUS_LANGUAGE.md",
    ]

    def setUp(self):
        self._content = MD_PATH.read_text(encoding="utf-8")

    def test_key_referenced_files_exist_in_repo(self):
        for rel_path in self.EXPECTED_PATHS_RELATIVE:
            full_path = REPO_ROOT / rel_path
            with self.subTest(path=rel_path):
                self.assertTrue(
                    full_path.exists(),
                    f"Referenced file '{rel_path}' does not exist at {full_path}",
                )

    def test_report_itself_is_referenced_in_evidence(self):
        """The report cites recommended-skills-sdk-pipeline.html as evidence."""
        self.assertIn("recommended-skills-sdk-pipeline.html", self._content)


if __name__ == "__main__":
    unittest.main()
