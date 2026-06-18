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
        self._current_cell_parts: list[str] | None = None
        self._current_cells: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "tr" and "data-capability-id" in attributes:
            capability_id = attributes["data-capability-id"]
            self._current_id = capability_id
            self._current_parts = []
            self._current_cells = []
            self.rows[capability_id] = {
                "status": attributes.get("data-status", ""),
                "pipeline_sections": attributes.get("data-pipeline-sections", ""),
                "owner_surface": "",
                "next_slice": "",
                "text": "",
            }
        elif tag == "td" and self._current_id is not None:
            self._current_cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_id is not None:
            text = data.strip()
            if text:
                self._current_parts.append(text)
                if self._current_cell_parts is not None:
                    self._current_cell_parts.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._current_id is not None and self._current_cell_parts is not None:
            self._current_cells.append(" ".join(self._current_cell_parts))
            self._current_cell_parts = None
        elif tag == "tr" and self._current_id is not None:
            if len(self._current_cells) >= 4:
                self.rows[self._current_id]["owner_surface"] = self._current_cells[2]
                self.rows[self._current_id]["next_slice"] = self._current_cells[3]
            self.rows[self._current_id]["text"] = " ".join(self._current_parts)
            self._current_id = None
            self._current_parts = []
            self._current_cells = []


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

    def test_pipeline_artifact_declares_status_command_as_source(self) -> None:
        self.assertIn('data-source-command="./bin/ask sdk status --json --robot"', self.html)
        self.assertIn(
            'data-projection-source="Infrastructure/config/skills-sdk/capability-matrix.v1.json"',
            self.html,
        )
        self.assertIn(
            "visual projection of <code>./bin/ask sdk status --json --robot</code>",
            self.html,
        )

    def test_source_artifacts_exist_and_include_generated_from(self) -> None:
        source_artifacts = self.runtime_status["source_artifacts"]
        self.assertIn(self.runtime_status["generated_from"], source_artifacts)
        for source_artifact in source_artifacts:
            with self.subTest(source_artifact=source_artifact):
                self.assertTrue((REPO_ROOT / source_artifact).exists(), source_artifact)

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

    def test_public_wrappers_emit_same_sdk_status_payload(self) -> None:
        wrapper_commands = [
            [sys.executable, "bin/ask", "sdk", "status", "--json", "--robot"],
            [sys.executable, "bin/skills-sdk", "status", "--json", "--robot"],
        ]

        for command in wrapper_commands:
            with self.subTest(command=" ".join(command)):
                completed = subprocess.run(
                    command,
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=True,
                )
                wrapper_status = json.loads(completed.stdout)["data"]["skills_sdk_status"]
                self.assertEqual(wrapper_status, self.runtime_status)

    def test_pipeline_artifact_authority_cells_match_live_sdk_status(self) -> None:
        runtime_by_id = {
            capability["id"]: capability
            for capability in self.runtime_status["capabilities"]
        }

        for capability_id, runtime_row in runtime_by_id.items():
            with self.subTest(capability=capability_id):
                html_row = self.rows[capability_id]
                self.assertEqual(html_row["owner_surface"], runtime_row["owner_surface"])
                self.assertEqual(html_row["next_slice"], runtime_row["next_slice"])

    def test_pipeline_artifact_does_not_advertise_completed_pus_as_next_slice(self) -> None:
        completed_pus: set[str] = set()
        for capability in self.runtime_status["capabilities"]:
            if capability["status"] != "implemented":
                continue
            completed_pus.update(re.findall(r"\bPU-\d+\b", capability["notes"]))

        for pu_id in sorted(completed_pus):
            with self.subTest(pu_id=pu_id):
                self.assertIsNone(re.search(rf"\bNext(?: slice)?: {re.escape(pu_id)}\b", self.html))

    def test_pipeline_artifact_does_not_advertise_source_artifact_pus_as_next_slice(self) -> None:
        source_pus: set[str] = set()
        for source_artifact in self.runtime_status["source_artifacts"]:
            source_pus.update(re.findall(r"\bPU-\d+\b", source_artifact))

        for pu_id in sorted(source_pus):
            with self.subTest(pu_id=pu_id):
                self.assertIsNone(re.search(rf"\bNext(?: slice)?: {re.escape(pu_id)}\b", self.html))

    def test_static_docs_remain_projection_only(self) -> None:
        runtime_by_id = {
            capability["id"]: capability
            for capability in self.runtime_status["capabilities"]
        }
        static_docs = runtime_by_id["static_docs"]

        self.assertEqual(static_docs["status"], "preview_only")
        self.assertFalse(static_docs["mutation_performed"])
        self.assertIn("projection-only", self.rows["static_docs"]["text"].lower())

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
