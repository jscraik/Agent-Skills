from __future__ import annotations

import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from review_authority_parser_replay import (  # noqa: E402
    EXPECTED_DATA_KEYS,
    EXPECTED_RECEIPT_SCHEMAS,
    EXPECTED_RECEIPT_STATUSES,
    FAMILIES,
    REQUIRED_NO_WRITE_KEYS,
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
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        selected_commands = {row["family"]: row["command"] for row in selection["selected_preview_commands"]}
        for family in FAMILIES:
            key = EXPECTED_DATA_KEYS[family]
            receipt = {
                "schema_version": EXPECTED_RECEIPT_SCHEMAS[family],
                "status": EXPECTED_RECEIPT_STATUSES[family],
                **{key: False for key in REQUIRED_NO_WRITE_KEYS[family]},
            }
            if family == "knowledge":
                receipt.update(
                    {
                        "proof_results": [],
                        "copied_files": [{"action": "preview"}],
                    }
                )
            if family == missing_receipt_family:
                body = {"result": "missing-receipt"}
            else:
                if family == mutation_family:
                    receipt["mutation_performed"] = True
                if family == "install":
                    body = {"status": receipt.pop("status"), "preview": receipt}
                else:
                    body = {"receipt": receipt}
            payload = {
                "status": "success",
                "metadata": {
                    "command": selected_commands[family].removeprefix("./bin/ask ")
                },
                "data": {key: body},
            }
            (capture_dir / f"{family}.json").write_text(json.dumps(payload), encoding="utf-8")
            (capture_dir / f"{family}.exit").write_text("0\n", encoding="utf-8")
            (capture_dir / f"{family}.stderr").write_text("", encoding="utf-8")

    def test_worker_review_accepts_captured_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            self.assertEqual(_worker_findings(capture_dir, ARTIFACT, SELECTION), [])

    def test_worker_review_prefers_captured_command_argv_over_facade_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            selected_command = next(
                row["command"] for row in json.loads(SELECTION.read_text(encoding="utf-8"))["selected_preview_commands"] if row["family"] == "trust"
            )
            payload_path = capture_dir / "trust.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            payload["metadata"]["command"] = "sdk trust decide --preview"
            payload["metadata"]["command_argv"] = shlex.split(selected_command)
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            self.assertEqual(_worker_findings(capture_dir, ARTIFACT, SELECTION), [])

    def test_worker_review_rejects_unquoted_legacy_capture_for_quoted_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            payload_path = capture_dir / "trust.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            payload["metadata"]["command"] = payload["metadata"]["command"].replace("'", "")
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            self.assertTrue(any("worker capture command does not match" in finding["message"] for finding in findings))

    def test_worker_review_rejects_mutation_and_missing_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir, mutation_family="trust", missing_receipt_family="install")
            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            messages = [finding["message"] for finding in findings]
            self.assertTrue(any("mutation or external-access flag" in message for message in messages))
            self.assertTrue(any("nested receipt schema_version/status" in message for message in messages))

    def test_worker_review_rejects_partial_no_write_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            payload_path = capture_dir / "eval.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            del payload["data"][EXPECTED_DATA_KEYS["eval"]]["receipt"]["network_accessed"]
            payload_path.write_text(json.dumps(payload), encoding="utf-8")
            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            self.assertTrue(any("omits explicit no-write fields" in finding["message"] for finding in findings))

    def test_worker_review_rejects_blocked_install_preview_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            payload_path = capture_dir / "install.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            payload["data"][EXPECTED_DATA_KEYS["install"]]["status"] = "blocked"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            self.assertTrue(any("nested receipt schema_version/status" in finding["message"] for finding in findings))

    def test_worker_review_rejects_wrong_family_receipt_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            payload_path = capture_dir / "eval.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            payload["data"][EXPECTED_DATA_KEYS["eval"]]["receipt"]["schema_version"] = "bogus.schema"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            self.assertTrue(any("nested receipt schema_version/status" in finding["message"] for finding in findings))

    def test_worker_review_accepts_family_specific_no_write_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            knowledge_receipt = json.loads((capture_dir / "knowledge.json").read_text(encoding="utf-8"))
            receipt = knowledge_receipt["data"][EXPECTED_DATA_KEYS["knowledge"]]
            receipt = receipt["receipt"]
            self.assertEqual(REQUIRED_NO_WRITE_KEYS["knowledge"], frozenset({"mutation_performed"}))
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual(receipt["proof_results"], [])
            self.assertEqual(receipt["copied_files"], [{"action": "preview"}])
            self.assertEqual(_worker_findings(capture_dir, ARTIFACT, SELECTION), [])

    def test_worker_review_rejects_knowledge_capture_without_preview_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            payload_path = capture_dir / "knowledge.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            receipt = payload["data"][EXPECTED_DATA_KEYS["knowledge"]]["receipt"]
            receipt.pop("proof_results")
            receipt["copied_files"][0]["action"] = "write"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            messages = [finding["message"] for finding in findings]
            self.assertTrue(any("proof_results evidence" in message for message in messages))
            self.assertTrue(any("copied_files must prove preview-only" in message for message in messages))

    def test_worker_review_rejects_capture_for_different_candidate_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_dir = Path(temp_dir)
            self._write_capture_dir(capture_dir)
            payload_path = capture_dir / "plugin.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            payload["metadata"]["command"] = "sdk plugin review Infrastructure/tests/fixtures/skills_sdk/other_skill --kind skill --preview --json --robot"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")
            findings = _worker_findings(capture_dir, ARTIFACT, SELECTION)
            self.assertTrue(any("worker capture command does not match" in finding["message"] for finding in findings))

    def test_qa_review_accepts_candidate_and_focused_test(self) -> None:
        self.assertEqual(_qa_findings(ARTIFACT, SELECTION), [])

    def test_adversarial_review_checks_negative_contracts(self) -> None:
        self.assertEqual(_adversarial_findings(ARTIFACT, SELECTION), [])

    def test_review_binds_reordered_candidate_rows_by_family(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        artifact["commands"] = list(reversed(artifact["commands"]))
        self.assertEqual(_artifact_shape_findings(artifact, selection, ARTIFACT, SELECTION), [])

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

    def test_review_rejects_candidate_command_not_bound_to_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "artifact.json"
            artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
            artifact["commands"][0]["command"] += " --unexpected"
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            findings = _adversarial_findings(artifact_path, SELECTION)
            self.assertTrue(any("does not exactly match the selected preview row" in finding["message"] for finding in findings))

    def test_review_rejects_missing_source_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "artifact.json"
            artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
            artifact["commands"][0]["source_fixture"] = "Infrastructure/tests/fixtures/skills_sdk/does-not-exist"
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            findings = _adversarial_findings(artifact_path, SELECTION)
            self.assertTrue(any("fixture path is not a safe" in finding["message"] for finding in findings))

    def test_review_rejects_unsafe_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            selection_path = Path(temp_dir) / "selection.json"
            selection = json.loads(SELECTION.read_text(encoding="utf-8"))
            selection["source_files"] = ["../outside-repo.py"]
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            findings = _adversarial_findings(ARTIFACT, selection_path)
            self.assertTrue(any("declared source digest could not be recomputed" in finding["message"] for finding in findings))


if __name__ == "__main__":
    unittest.main()
