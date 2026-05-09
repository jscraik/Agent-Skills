"""
Tests for session-evidence-workflow.md — covering the handoffs.json guidance
added in the skill-refactor-handoff-fallback PR.

Scope (diff-bounded):
  - skill-refactor-handoffs.json is documented as the primary artifact consumed first
  - Existence verification of handoffs.json is required before use
  - Missing file triggers "collector contract drift" report with the artifact path
  - Strict validation flows must stop when handoffs.json is absent
  - Non-strict recommendation flows may continue with provisional recommendations
    from skill-refactor-evidence.json, index.json, and redaction-report.json
  - A warning about --codex-sessions-dir for archived/non-default session roots
    is included in the non-strict fallback guidance
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = next(
    p
    for p in Path(__file__).resolve().parents
    if (p / "Infrastructure").is_dir()
)

WORKFLOW_DOC = (
    REPO_ROOT
    / "Infrastructure"
    / "references"
    / "deferred-skill-context"
    / "skill-factory-skill-refactor"
    / "references"
    / "session-evidence-workflow.md"
)


class TestWorkflowDocExists(unittest.TestCase):
    """Sanity check: the document must exist and be non-empty."""

    def test_file_exists(self):
        self.assertTrue(WORKFLOW_DOC.exists(), f"Missing: {WORKFLOW_DOC}")

    def test_file_is_non_empty(self):
        content = WORKFLOW_DOC.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 0)


class TestHandoffsJsonPrimaryArtifact(unittest.TestCase):
    """skill-refactor-handoffs.json must be documented as the primary artifact."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_handoffs_json_is_mentioned(self):
        self.assertIn(
            "skill-refactor-handoffs.json",
            self._text,
            "skill-refactor-handoffs.json must be referenced in the workflow doc",
        )

    def test_handoffs_json_consumed_first(self):
        """The document must instruct consuming handoffs.json *first*."""
        self.assertIn(
            "first",
            self._text,
            "The document must include the word 'first' in relation to handoffs.json",
        )
        # Verify 'first' appears near the handoffs.json reference
        idx_handoffs = self._text.find("skill-refactor-handoffs.json")
        segment = self._text[max(0, idx_handoffs - 100): idx_handoffs + 150]
        self.assertIn(
            "first",
            segment,
            "The word 'first' should appear near the skill-refactor-handoffs.json reference",
        )

    def test_handoffs_json_documents_decision_types(self):
        """handoffs.json should be described as carrying keep/improve/skillify/route-to-he decisions."""
        for decision in ("keep", "improve", "skillify", "route-to-he"):
            self.assertIn(
                decision,
                self._text,
                f"Decision type '{decision}' must be documented for handoffs.json",
            )

    def test_handoffs_json_includes_root_causes_and_evidence_labels(self):
        """handoffs.json guidance must mention root causes and evidence labels."""
        self.assertIn("root cause", self._text)
        self.assertIn("evidence", self._text)


class TestHandoffsJsonExistenceVerification(unittest.TestCase):
    """The document must require verifying handoffs.json exists before use."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_verify_existence_instruction_present(self):
        """Existence check instruction must appear."""
        self.assertIn(
            "verify",
            self._text.lower(),
            "The document must include a 'verify' instruction for handoffs.json",
        )

    def test_verify_exists_near_handoffs_json(self):
        """The existence-check language should be near the handoffs.json reference."""
        idx = self._text.find("Before using")
        self.assertGreater(
            idx, -1,
            "'Before using' phrasing must appear in the document",
        )
        segment = self._text[idx: idx + 200]
        self.assertIn(
            "skill-refactor-handoffs.json",
            segment,
            "'Before using' clause must reference skill-refactor-handoffs.json",
        )

    def test_missing_file_triggers_contract_drift_report(self):
        """Missing handoffs.json must produce a 'collector contract drift' report."""
        self.assertIn(
            "collector contract drift",
            self._text,
            "Missing handoffs.json must trigger a 'collector contract drift' report",
        )

    def test_missing_artifact_path_in_drift_report(self):
        """Drift report must include the missing artifact path."""
        idx = self._text.find("collector contract drift")
        self.assertGreater(idx, -1)
        segment = self._text[max(0, idx - 50): idx + 300]
        self.assertIn(
            "path",
            segment.lower(),
            "Collector contract drift report must reference the missing artifact path",
        )


class TestStrictValidationFlowBehavior(unittest.TestCase):
    """Strict validation flows must stop when handoffs.json is absent."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_strict_flow_documented(self):
        self.assertIn(
            "strict",
            self._text.lower(),
            "Strict validation flow behavior must be documented",
        )

    def test_strict_flow_stops_on_missing_handoffs(self):
        """The document must state that strict flows stop when handoffs.json is missing."""
        # Find "strict" in the context of "stop"
        idx = self._text.lower().find("strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 300]
        self.assertIn(
            "stop",
            segment.lower(),
            "Strict flows must be described as stopping when handoffs.json is absent",
        )

    def test_strict_flow_uses_stop_there_language(self):
        """Exact phrasing: strict flows 'must stop there'."""
        self.assertIn(
            "stop there",
            self._text,
            "Document must use 'stop there' language for strict validation flows",
        )


class TestNonStrictFallbackBehavior(unittest.TestCase):
    """Non-strict flows may continue with provisional recommendations."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_non_strict_flow_documented(self):
        self.assertIn(
            "non-strict",
            self._text,
            "Non-strict recommendation flow must be documented",
        )

    def test_non_strict_allows_continuation(self):
        """Non-strict flows may continue with provisional recommendations."""
        idx = self._text.find("non-strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 300]
        self.assertIn(
            "continue",
            segment.lower(),
            "Non-strict flows must be described as continuing after missing handoffs.json",
        )

    def test_provisional_recommendations_mentioned(self):
        self.assertIn(
            "provisional",
            self._text,
            "The document must mention 'provisional' recommendations for the non-strict path",
        )

    def test_fallback_includes_skill_refactor_evidence_json(self):
        """skill-refactor-evidence.json must be listed as a fallback artifact."""
        idx = self._text.find("non-strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 400]
        self.assertIn(
            "skill-refactor-evidence.json",
            segment,
            "skill-refactor-evidence.json must be a fallback artifact in the non-strict path",
        )

    def test_fallback_includes_index_json(self):
        """index.json must be listed as a fallback artifact."""
        idx = self._text.find("non-strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 400]
        self.assertIn(
            "index.json",
            segment,
            "index.json must be a fallback artifact in the non-strict path",
        )

    def test_fallback_includes_redaction_report_json(self):
        """redaction-report.json must be listed as a fallback artifact."""
        idx = self._text.find("non-strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 400]
        self.assertIn(
            "redaction-report.json",
            segment,
            "redaction-report.json must be a fallback artifact in the non-strict path",
        )

    def test_codex_sessions_dir_warning_in_fallback(self):
        """Non-strict fallback must warn operators about --codex-sessions-dir."""
        idx = self._text.find("non-strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 600]
        self.assertIn(
            "--codex-sessions-dir",
            segment,
            "Non-strict fallback must warn about --codex-sessions-dir for non-default roots",
        )

    def test_codex_sessions_dir_warning_mentions_archived_or_non_default(self):
        """The --codex-sessions-dir warning must cover archived or non-default session roots."""
        idx = self._text.find("non-strict")
        self.assertGreater(idx, -1)
        segment = self._text[idx: idx + 600]
        has_archived = "archived" in segment
        has_non_default = "non-default" in segment
        self.assertTrue(
            has_archived or has_non_default,
            "The --codex-sessions-dir warning must mention 'archived' or 'non-default' session roots",
        )


class TestPreExistingArtifactsUnchanged(unittest.TestCase):
    """Regression: artifacts documented before this PR must still be present."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_skill_refactor_evidence_json_still_present(self):
        self.assertIn("skill-refactor-evidence.json", self._text)

    def test_solved_problems_json_still_present(self):
        self.assertIn("solved-problems.json", self._text)

    def test_index_json_still_present(self):
        self.assertIn("index.json", self._text)

    def test_redaction_report_json_still_present(self):
        self.assertIn("redaction-report.json", self._text)

    def test_codex_sessions_dir_flag_still_documented(self):
        self.assertIn("--codex-sessions-dir", self._text)


class TestHandoffsJsonOrderingInDocument(unittest.TestCase):
    """handoffs.json must appear before the other artifacts in the consumption guidance."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_handoffs_json_appears_before_evidence_json_in_consume_section(self):
        """In the 'Consume' paragraph, handoffs.json position must precede evidence.json."""
        idx_handoffs = self._text.find("skill-refactor-handoffs.json")
        idx_evidence = self._text.find("skill-refactor-evidence.json")
        self.assertGreater(idx_handoffs, -1, "skill-refactor-handoffs.json must exist in doc")
        self.assertGreater(idx_evidence, -1, "skill-refactor-evidence.json must exist in doc")
        self.assertLess(
            idx_handoffs,
            idx_evidence,
            "skill-refactor-handoffs.json must appear before skill-refactor-evidence.json "
            "in the document (it is the primary artifact consumed first)",
        )

    def test_verification_block_follows_consume_guidance(self):
        """'Before using' existence-check must come after the consumption paragraph."""
        idx_consume = self._text.find("Consume `${TEMP_PREFIX}/skill-refactor-handoffs.json`")
        idx_verify = self._text.find("Before using `${TEMP_PREFIX}/skill-refactor-handoffs.json`")
        self.assertGreater(idx_consume, -1, "'Consume' paragraph must be present")
        self.assertGreater(idx_verify, -1, "'Before using' verification block must be present")
        self.assertLess(
            idx_consume,
            idx_verify,
            "The consumption guidance must appear before the existence-verification block",
        )


class TestNoBrokenTemplateVariables(unittest.TestCase):
    """TEMP_PREFIX template variables must be well-formed in the new guidance."""

    def setUp(self):
        self._text = WORKFLOW_DOC.read_text(encoding="utf-8")

    def test_temp_prefix_handoffs_json_is_well_formed(self):
        pattern = r"\$\{TEMP_PREFIX\}/skill-refactor-handoffs\.json"
        matches = re.findall(pattern, self._text)
        self.assertGreaterEqual(
            len(matches),
            2,
            "skill-refactor-handoffs.json must appear at least twice with the "
            "${TEMP_PREFIX} prefix (consumption guidance + verification block)",
        )

    def test_no_malformed_temp_prefix_references(self):
        """No bare 'skill-refactor-handoffs.json' reference should lack the prefix."""
        # Count total occurrences vs prefixed ones
        total = len(re.findall(r"skill-refactor-handoffs\.json", self._text))
        prefixed = len(re.findall(r"\$\{TEMP_PREFIX\}/skill-refactor-handoffs\.json", self._text))
        self.assertEqual(
            total,
            prefixed,
            "Every reference to skill-refactor-handoffs.json should include the "
            "${TEMP_PREFIX}/ prefix",
        )


if __name__ == "__main__":
    unittest.main()
