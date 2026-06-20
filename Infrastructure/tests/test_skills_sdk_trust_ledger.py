from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.trust_ledger import TrustLedgerError, build_trust_decision_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_robot_envelope, validate_trust_decision_receipt  # noqa: E402


FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


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


def _run_trust_preview(ledger_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "trust",
            "decide",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--decision",
            "trust",
            "--reason",
            "fixture passed local checks",
            "--owner",
            "skills-sdk-tests",
            "--ledger",
            ledger_path.as_posix(),
            "--preview",
            "--json",
            "--robot",
        ],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkTrustLedger(unittest.TestCase):
    def _package_receipt(self) -> dict:
        return build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )

    def test_builder_previews_local_trust_decision_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "trust-ledger.jsonl"
            payload = build_trust_decision_receipt(
                REPO_ROOT,
                package_receipt=self._package_receipt(),
                decision="trust",
                reason="fixture passed local checks",
                owner="skills-sdk-tests",
                apply=False,
                ledger_path=ledger_path.as_posix(),
            )

            receipt = validate_trust_decision_receipt(payload)

            self.assertEqual(receipt.status, "preview")
            self.assertEqual(receipt.decision, "trust")
            self.assertFalse(receipt.mutation_performed)
            self.assertFalse(receipt.trust_store_mutated)
            self.assertFalse(ledger_path.exists())
            self.assertIsNotNone(receipt.ledger_entry)

    def test_builder_apply_appends_local_ledger_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "trust-ledger.jsonl"
            payload = build_trust_decision_receipt(
                REPO_ROOT,
                package_receipt=self._package_receipt(),
                decision="distrust",
                reason="fixture distrust path",
                owner="skills-sdk-tests",
                apply=True,
                ledger_path=ledger_path.as_posix(),
            )

            receipt = validate_trust_decision_receipt(payload)
            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(receipt.status, "recorded")
            self.assertTrue(receipt.mutation_performed)
            self.assertFalse(receipt.trust_store_mutated)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["decision"], "distrust")
            self.assertIn("reason_digest", entries[0])
            self.assertIn("owner_digest", entries[0])
            self.assertIn("package_digest_digest", entries[0])
            self.assertNotIn("reason", entries[0])
            self.assertNotIn("owner", entries[0])
            self.assertNotIn("package_digest", entries[0])

    def test_builder_blocks_revoke_without_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "trust-ledger.jsonl"
            with self.assertRaises(TrustLedgerError) as raised:
                build_trust_decision_receipt(
                    REPO_ROOT,
                    package_receipt=self._package_receipt(),
                    decision="revoke",
                    reason="missing digest fixture",
                    owner="skills-sdk-tests",
                    apply=True,
                    ledger_path=ledger_path.as_posix(),
                )

            receipt = validate_trust_decision_receipt(raised.exception.receipt)

            self.assertEqual(receipt.status, "blocked")
            self.assertFalse(receipt.mutation_performed)
            self.assertFalse(receipt.trust_store_mutated)
            self.assertFalse(ledger_path.exists())
            self.assertIn("revoked_package_digest:missing", receipt.blockers[0].evidence)

    def test_public_cli_previews_trust_decision_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "trust-ledger.jsonl"
            completed = _run_trust_preview(ledger_path)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = validate_robot_envelope(json.loads(completed.stdout))
            payload = envelope.data["skills_sdk_trust_decide"]
            self.assertIsInstance(payload, dict)
            receipt = validate_trust_decision_receipt(payload["receipt"])

            self.assertEqual(payload["status"], "preview")
            self.assertEqual(receipt.package_id, "skills-sdk-valid-fixture")
            self.assertFalse(payload["mutation_performed"])
            self.assertFalse(ledger_path.exists())

    def test_public_cli_requires_preview_or_apply(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "trust",
                "decide",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                "--decision",
                "trust",
                "--reason",
                "fixture passed local checks",
                "--owner",
                "skills-sdk-tests",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        self.assertEqual(envelope.status, "error")
        self.assertIn("exactly one of --preview or --apply", envelope.errors[0].message)


if __name__ == "__main__":
    unittest.main()
