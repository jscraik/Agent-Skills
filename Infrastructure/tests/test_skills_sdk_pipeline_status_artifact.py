import json
import re
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = REPO_ROOT / "artifacts/recommended-skills-sdk-pipeline.html"
MATRIX_PATH = REPO_ROOT / "Infrastructure/config/skills-sdk/capability-matrix.v1.json"
LIFECYCLE_HTML_PATH = REPO_ROOT / "artifacts/skills-sdk-user-lifecycle-one-page.html"


class CapabilityStatusParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: dict[str, dict[str, str]] = {}
        self._current_id: str | None = None
        self._current_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "tr" and "data-capability-id" in attributes:
            capability_id = attributes["data-capability-id"]
            self._current_id = capability_id
            self._current_parts = []
            self.rows[capability_id] = {
                "status": attributes.get("data-status", ""),
                "pipeline_sections": attributes.get("data-pipeline-sections", ""),
                "text": "",
            }

    def handle_data(self, data: str) -> None:
        if self._current_id is not None:
            text = data.strip()
            if text:
                self._current_parts.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._current_id is not None:
            self.rows[self._current_id]["text"] = " ".join(self._current_parts)
            self._current_id = None
            self._current_parts = []


class TestSkillsSdkPipelineStatusArtifact(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        completed = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "sdk", "status", "--json", "--robot"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        cls.runtime_status = json.loads(completed.stdout)["data"]["skills_sdk_status"]
        cls.lifecycle_html = LIFECYCLE_HTML_PATH.read_text(encoding="utf-8")
        parser = CapabilityStatusParser()
        parser.feed(cls.html)
        cls.rows = parser.rows

    def test_pipeline_artifact_contains_status_truth_section(self) -> None:
        self.assertIn('data-capability-status="skills-sdk.capability-status.v1"', self.html)
        self.assertIn("Capability Truth", self.html)

    def test_every_matrix_capability_has_html_row(self) -> None:
        matrix_ids = [row["id"] for row in self.matrix["capabilities"]]

        self.assertEqual(list(self.rows), matrix_ids)

    def test_html_statuses_match_matrix_vocabulary(self) -> None:
        for capability in self.matrix["capabilities"]:
            with self.subTest(capability=capability["id"]):
                html_row = self.rows[capability["id"]]
                self.assertEqual(html_row["status"], capability["status"])
                self.assertIn(capability["status"], html_row["text"])

    def test_pipeline_artifact_statuses_match_live_sdk_status(self) -> None:
        runtime_by_id = {
            capability["id"]: capability
            for capability in self.runtime_status["capabilities"]
        }

        self.assertEqual(set(self.rows), set(runtime_by_id))
        for capability_id, runtime_row in runtime_by_id.items():
            with self.subTest(capability=capability_id):
                html_row = self.rows[capability_id]
                self.assertEqual(html_row["status"], runtime_row["status"])
                self.assertIn(runtime_row["title"], html_row["text"])

    def test_lifecycle_one_page_does_not_contradict_live_completed_capabilities(self) -> None:
        implemented_titles = {
            capability["title"]
            for capability in self.runtime_status["capabilities"]
            if capability["status"] == "implemented"
        }
        deferred_titles = {
            capability["title"]
            for capability in self.runtime_status["capabilities"]
            if capability["status"] in {"deferred", "placeholder_blocked", "blocked_missing_adapter", "out_of_scope"}
        }

        for title in implemented_titles:
            if title in self.lifecycle_html:
                self.assertIn(title, self.lifecycle_html)
        for title in deferred_titles:
            if title in self.lifecycle_html:
                title_index = self.lifecycle_html.index(title)
                nearby = self.lifecycle_html[max(0, title_index - 300): title_index + 300].lower()
                self.assertNotIn("completed", nearby)

    def test_every_pipeline_section_is_represented_in_html(self) -> None:
        matrix_sections = {
            section
            for capability in self.matrix["capabilities"]
            for section in capability["pipeline_sections"]
        }
        html_sections = {
            section
            for row in self.rows.values()
            for section in row["pipeline_sections"].split(",")
            if section
        }

        self.assertEqual(html_sections, matrix_sections)

    def test_html_does_not_overclaim_deferred_or_out_of_scope_rows(self) -> None:
        overclaim_patterns = [
            r"\bavailable now\b",
            r"\bready now\b",
            r"\bwrites enabled\b",
            r"\bpublishing enabled\b",
            r"\bsigning enabled\b",
            r"\bsandbox execution enabled\b",
            r"\beval execution enabled\b",
            r"\bregistry available\b",
        ]
        gated_statuses = {
            "placeholder_optional",
            "placeholder_blocked",
            "blocked_missing_adapter",
            "deferred",
            "out_of_scope",
        }

        for capability in self.matrix["capabilities"]:
            if capability["status"] not in gated_statuses:
                continue
            with self.subTest(capability=capability["id"]):
                text = self.rows[capability["id"]]["text"].lower()
                for pattern in overclaim_patterns:
                    self.assertIsNone(re.search(pattern, text), pattern)


if __name__ == "__main__":
    unittest.main()
