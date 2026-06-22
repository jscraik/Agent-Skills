from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.capability_evidence import (  # noqa: E402
    _classify_ref,
    build_capability_evidence_receipt,
)
from ask.commands import skills_impl  # noqa: E402


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkCapabilityEvidence(unittest.TestCase):
    def test_command_builds_preview_receipt_without_executing_commands(self) -> None:
        process = _run_ask("sdk", "evidence", "verify", "--scope", "capability-matrix", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_capability_evidence"]
        receipt = payload["receipt"]

        self.assertIn(payload["status"], {"pass", "blocked"})
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["command_execution_performed"])
        self.assertGreater(receipt["evidence_ref_count"], 0)
        self.assertTrue(any(row["kind"] == "command" and row["status"] == "not_run" for row in receipt["evidence_rows"]))

    def test_file_ref_passes_when_repo_local_file_exists(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "UBIQUITOUS_LANGUAGE.md")

        self.assertEqual((kind, status, lane), ("file", "pass", "local"))
        self.assertIn("exists", reason)
        self.assertEqual(evidence, ["UBIQUITOUS_LANGUAGE.md"])

    def test_missing_file_ref_blocks(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "Infrastructure/tests/fixtures/missing-evidence.txt")

        self.assertEqual((kind, status, lane), ("file", "blocked", "local"))
        self.assertIn("does not exist", reason)
        self.assertEqual(evidence, ["Infrastructure/tests/fixtures/missing-evidence.txt"])

    def test_repo_local_ref_with_external_marker_resolves_as_file(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "Skills/github/teach/SKILL.md")

        self.assertEqual((kind, status, lane), ("file", "pass", "local"))
        self.assertIn("exists", reason)
        self.assertEqual(evidence, ["Skills/github/teach/SKILL.md"])

    def test_missing_repo_local_ref_with_external_marker_blocks(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "Skills/github/teach/missing-evidence.md")

        self.assertEqual((kind, status, lane), ("file", "blocked", "local"))
        self.assertIn("does not exist", reason)
        self.assertEqual(evidence, ["Skills/github/teach/missing-evidence.md"])

    def test_schema_ref_must_parse_as_json(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(
            REPO_ROOT,
            "Infrastructure/config/schemas/skills-sdk/capability-evidence-receipt.v0.schema.json",
        )

        self.assertEqual((kind, status, lane), ("schema", "pass", "local"))
        self.assertIn("parses as JSON", reason)
        self.assertEqual(evidence, ["Infrastructure/config/schemas/skills-sdk/capability-evidence-receipt.v0.schema.json"])

    def test_receipt_ref_must_parse_as_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            receipt_path = Path(temp_dir) / "bad-receipt.json"
            receipt_path.write_text("not json", encoding="utf-8")
            receipt_ref = receipt_path.relative_to(REPO_ROOT).as_posix()

            kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, receipt_ref)

        self.assertEqual((kind, status, lane), ("receipt", "blocked", "local"))
        self.assertIn("did not parse as JSON", reason)
        self.assertEqual(evidence, [receipt_ref])

    def test_command_ref_is_not_run_by_verifier(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "./bin/ask sdk status --json --robot")

        self.assertEqual((kind, status, lane), ("command", "not_run", "local_command"))
        self.assertIn("not executed", reason)
        self.assertEqual(evidence, ["./bin/ask"])

    def test_ask_placeholder_command_ref_is_not_unknown(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "ask sdk eval ab-run --skill-a <skill-a> --json --robot")

        self.assertEqual((kind, status, lane), ("command", "not_run", "local_command"))
        self.assertIn("not executed", reason)
        self.assertEqual(evidence, ["ask"])

    def test_pytest_node_ref_passes_when_named_test_exists(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(
            REPO_ROOT,
            "Infrastructure/tests/test_skills_sdk_capability_evidence.py::TestSkillsSdkCapabilityEvidence::test_command_ref_is_not_run_by_verifier",
        )

        self.assertEqual((kind, status, lane), ("file", "pass", "local"))
        self.assertIn("named test is present", reason)
        self.assertEqual(
            evidence,
            [
                "Infrastructure/tests/test_skills_sdk_capability_evidence.py::TestSkillsSdkCapabilityEvidence::test_command_ref_is_not_run_by_verifier"
            ],
        )

    def test_pytest_node_ref_blocks_when_named_test_is_missing(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(
            REPO_ROOT,
            "Infrastructure/tests/test_skills_sdk_capability_evidence.py::TestSkillsSdkCapabilityEvidence::test_missing_node",
        )

        self.assertEqual((kind, status, lane), ("file", "blocked", "local"))
        self.assertIn("named test was not found", reason)
        self.assertEqual(
            evidence,
            ["Infrastructure/tests/test_skills_sdk_capability_evidence.py::TestSkillsSdkCapabilityEvidence::test_missing_node"],
        )

    def test_pytest_node_ref_requires_full_class_match(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            test_path = Path(temp_dir) / "test_capability_node.py"
            test_path.write_text(
                "class OtherClass:\n"
                "    def test_same_name(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            test_ref = f"{test_path.relative_to(REPO_ROOT).as_posix()}::ExpectedClass::test_same_name"

            kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, test_ref)

        self.assertEqual((kind, status, lane), ("file", "blocked", "local"))
        self.assertIn("named test was not found", reason)
        self.assertEqual(evidence, [test_ref])

    def test_external_ref_stays_out_of_local_readiness(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "https://github.com/example/repo/actions/runs/1")

        self.assertEqual((kind, status, lane), ("external_lane", "not_run", "external"))
        self.assertIn("External evidence lanes", reason)
        self.assertEqual(evidence, ["https://github.com/example/repo/actions/runs/1"])

    def test_unknown_ref_blocks_instead_of_becoming_proof(self) -> None:
        kind, status, reason, evidence, lane = _classify_ref(REPO_ROOT, "not a path and not a command")

        self.assertEqual((kind, status, lane), ("unknown", "blocked", "local"))
        self.assertIn("neither a known command nor a repo-local file", reason)
        self.assertEqual(evidence, ["not a path and not a command"])

    def test_builder_counts_blockers_and_not_run_refs(self) -> None:
        matrix = {
            "capabilities": [
                {"id": "docs", "evidence_refs": ["UBIQUITOUS_LANGUAGE.md"]},
                {"id": "cmd", "evidence_refs": ["./bin/ask sdk status --json --robot"]},
                {"id": "bad", "evidence_refs": ["missing-evidence.txt"]},
            ]
        }

        with mock.patch("ask.skills_sdk.capability_evidence.load_capability_matrix", return_value=matrix):
            receipt = build_capability_evidence_receipt(REPO_ROOT)

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["pass_count"], 1)
        self.assertEqual(receipt["not_run_count"], 1)
        self.assertEqual(receipt["blocked_count"], 1)
        self.assertEqual(receipt["blockers"][0]["capability_id"], "bad")

    def test_command_wrapper_errors_when_receipt_blocks(self) -> None:
        blocked_receipt = {
            "status": "blocked",
            "agent_summary": "Capability evidence verification checked 1 evidence ref(s): 0 passed, 1 blocked.",
            "blockers": [{"capability_id": "bad", "ref": "missing.txt"}],
        }

        with mock.patch.object(skills_impl, "_build_capability_evidence_receipt", return_value=blocked_receipt):
            result = skills_impl.skills_sdk_capability_evidence(REPO_ROOT, scope="capability-matrix")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["skills_sdk_capability_evidence"]["status"], "blocked")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")


if __name__ == "__main__":
    unittest.main()
