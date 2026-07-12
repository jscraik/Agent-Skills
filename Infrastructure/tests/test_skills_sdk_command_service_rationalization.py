from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk.command_evidence_plan import build_command_evidence_plan_receipt  # noqa: E402
from helpers.schema_validator import _validate_schema_subset  # noqa: E402


ARTIFACT_PATH = REPO_ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/command-service-rationalization.v1.json"
RECEIPT_PATH = REPO_ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/command-evidence-plan.v0.json"
SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/command-service-rationalization.v1.schema.json"


class TestSkillsSdkCommandServiceRationalization(unittest.TestCase):
    def test_retained_inventory_is_schema_valid_and_revision_bound(self) -> None:
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate_schema_subset(schema, artifact, {SCHEMA_PATH.name: schema})
        self._assert_receipt_link(artifact, receipt)
        self._assert_inventory_counts(artifact, receipt)
        self._assert_revision_binding(artifact)

    def _assert_receipt_link(self, artifact: dict, receipt: dict) -> None:
        self.assertEqual(receipt, build_command_evidence_plan_receipt(REPO_ROOT))
        declared_path = (REPO_ROOT / artifact["source_receipt_path"]).resolve()
        self.assertEqual(declared_path, RECEIPT_PATH.resolve())
        self.assertTrue(declared_path.is_relative_to(REPO_ROOT.resolve()))
        self.assertTrue(declared_path.is_file())
        self.assertEqual(artifact["source_receipt_schema"], receipt["schema_version"])

    def _assert_inventory_counts(self, artifact: dict, receipt: dict) -> None:
        self.assertEqual(artifact["command_count"], receipt["command_count"])
        self.assertEqual(artifact["service_count"], receipt["service_count"])
        self.assertEqual(artifact["blockers"], [])
        self.assertFalse(artifact["mutation_performed"])
        self.assertFalse(artifact["command_execution_performed"])
        counts = Counter(command["replay_disposition"] for command in receipt["commands"])
        self.assertEqual(artifact["command_disposition_counts"], counts)
        self.assertEqual(sum(counts.values()), artifact["command_count"])
        expected_services = [
            {key: service[key] for key in ("path", "disposition", "caller_modules")}
            for service in receipt["services"]
        ]
        self.assertEqual(artifact["service_dispositions"], expected_services)
        self.assertEqual(len(artifact["service_dispositions"]), artifact["service_count"])
        self.assertEqual(len({service["path"] for service in artifact["service_dispositions"]}), artifact["service_count"])
        self.assertEqual(len(set(artifact["source_files"])), len(artifact["source_files"]))

    def _assert_revision_binding(self, artifact: dict) -> None:
        self.assertEqual(artifact["source_tree_digest"], _source_tree_digest(artifact["source_files"]))
        self.assertEqual(artifact["base_source_tree_digest"], _git_source_tree_digest(artifact["base_commit"], artifact["base_source_files"]))
        self.assertEqual(
            artifact["source_delta"],
            [{"path": "Infrastructure/scripts/lib/ask/skills_sdk/command_evidence_plan.py", "reason": "Normalize nested caller_modules tuples to JSON arrays so the v0 receipt schema validates."}],
        )
        self.assertTrue(all((REPO_ROOT / path).is_file() for path in artifact["source_files"]))
        self.assertTrue(_git_commit_exists(artifact["base_commit"]))
        self.assertIn(artifact["base_commit"], _git_head_and_parents())
        self.assertIn("Foundry extraction or source admission", artifact["does_not_prove"])
        self.assertIn("Tessl, registry, hosted CI, installed-runtime, or release readiness", artifact["does_not_prove"])

    def test_plan_builder_remains_non_mutating_and_schema_valid(self) -> None:
        receipt = build_command_evidence_plan_receipt(REPO_ROOT)
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/command-evidence-plan-receipt.v0.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        _validate_schema_subset(schema, receipt, {schema_path.name: schema})
        self.assertEqual(receipt["status"], "planned")
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["command_execution_performed"])


def _source_tree_digest(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update((REPO_ROOT / path).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _git_source_tree_digest(commit: str, paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        result = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update(result.stdout)
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _git_commit_exists(commit: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    return result.returncode == 0


def _git_head_and_parents() -> set[str]:
    result = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
    )
    return set(result.stdout.split())


if __name__ == "__main__":
    unittest.main()
