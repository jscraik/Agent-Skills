from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from review_authority_parser_replay import (  # noqa: E402
    EXPECTED_DATA_KEYS,
    FAMILIES,
    _adversarial_findings,
    _artifact_shape_findings,
    _qa_findings,
    _worker_findings,
)


ARTIFACT = ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-receipt.v1.json"
SELECTION = ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-selection.json"


class TestReviewAuthorityParserReplay(unittest.TestCase):
    def test_blocked_candidate_can_skip_command_execution(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        artifact.update({"status": "blocked", "command_count": 0, "commands": []})
        findings = _artifact_shape_findings(artifact, json.loads(SELECTION.read_text(encoding="utf-8")), ARTIFACT, SELECTION)
        self.assertEqual(findings, [])

    def _write_capture_dir(self, capture_dir: Path, *, mutation_family: str | None = None, missing_receipt_family: str | None = None) -> None:
        for family in FAMILIES:
            key = EXPECTED_DATA_KEYS[family]
            receipt = {"schema_version": f"fixture.{family}.v1", "status": "preview", "mutation_performed": False}
            if family == missing_receipt_family:
                body = {"result": "missing-receipt"}
            else:
                if family == mutation_family:
                    receipt["mutation_performed"] = True
                body = {"receipt": receipt}
            payload = {"status": "success", "data": {key: body}}
            (capture_dir / f"{family}.json").write_text(json.dumps(payload), encoding="utf-8")
            (capture_dir / f"{family}.exit").write_text("0\n", encoding="utf-8")
            (capture_dir / f"{family}.stderr").write_text("", encoding="utf-8")

    def test_worker_review_accepts_captured_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            self.assertEqual(_worker_findings(capture_dir), [])

    def test_worker_review_rejects_mutation_and_missing_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir, mutation_family="trust", missing_receipt_family="install")
            findings = _worker_findings(capture_dir)
            messages = [finding["message"] for finding in findings]
            self.assertTrue(any("mutation or external-access flag" in message for message in messages))
            self.assertTrue(any("nested receipt schema_version/status" in message for message in messages))

    def test_qa_review_accepts_candidate_and_focused_test(self) -> None:
        self.assertEqual(_qa_findings(ARTIFACT, SELECTION), [])

    def test_adversarial_review_checks_negative_contracts(self) -> None:
        self.assertEqual(_adversarial_findings(ARTIFACT, SELECTION), [])

    def test_adversarial_review_rejects_undeclared_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "artifact.json"
            artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
            artifact["does_not_prove"] = []
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            findings = _adversarial_findings(artifact_path, SELECTION)
            messages = [finding["message"] for finding in findings]
            self.assertTrue(any("Foundry extraction or source admission" in message for message in messages))
            self.assertTrue(any("hosted CI" in message for message in messages))

    def test_review_rejects_mismatched_command_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "artifact.json"
            artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
            artifact["command_count"] = len(artifact["commands"]) + 1
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            findings = _adversarial_findings(artifact_path, SELECTION)
            self.assertTrue(any("command_count" in finding["message"] for finding in findings))

    def test_review_rejects_selection_without_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            selection_path = Path(temp_dir) / "selection.json"
            selection = json.loads(SELECTION.read_text(encoding="utf-8"))
            selection.pop("source_files", None)
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            findings = _adversarial_findings(ARTIFACT, selection_path)
            self.assertTrue(any("source_files" in finding["message"] for finding in findings))


if __name__ == "__main__":
    unittest.main()
