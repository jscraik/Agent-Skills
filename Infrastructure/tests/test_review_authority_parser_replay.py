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
    _qa_findings,
    _worker_findings,
)


ARTIFACT = ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-receipt.v1.json"
SELECTION = ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-selection.json"


class TestReviewAuthorityParserReplay(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
