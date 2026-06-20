from __future__ import annotations

import builtins
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.emitter_contracts import validate_emitter_preview_receipt  # noqa: E402
from ask.skills_sdk.emitter_preview import (  # noqa: E402
    EmitterPreviewError,
    build_emitter_preview_receipt,
)
from ask.skills_sdk.observability_feedback import (  # noqa: E402
    ObservabilityFeedbackError,
    build_observability_feedback_receipt,
)
from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.package_hardening import build_package_hardening_receipt  # noqa: E402
from ask.skills_sdk.signing_intent import SigningIntentError, build_signing_intent_receipt  # noqa: E402
from ask.skills_sdk.trust_ledger import TrustLedgerError, build_trust_decision_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_observability_feedback_receipt,
    validate_signing_intent_receipt,
    validate_trust_decision_receipt,
)


FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
FIXTURE_POLICY = (
    REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json"
)


class TestSkillsSdkReceiptHardeningGate(unittest.TestCase):
    def _package_receipts(self) -> tuple[dict, dict]:
        package_receipt = build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )
        return package_receipt, build_package_hardening_receipt(package_receipt)

    def test_signing_fallback_preserves_full_policy_contract(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()
        policy = deepcopy(json.loads(FIXTURE_POLICY.read_text(encoding="utf-8")))
        policy["acceptance_trace"] = ["BAD"]
        policy["allowed_algorithms"] = ["cosign-keyless", 123]
        real_import = builtins.__import__

        def import_without_pydantic(name: str, *args: object, **kwargs: object) -> object:
            if name == "pydantic":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            with mock.patch("builtins.__import__", side_effect=import_without_pydantic):
                with self.assertRaises(SigningIntentError) as raised:
                    build_signing_intent_receipt(
                        policy_path=policy_path,
                        package_receipt=package_receipt,
                        hardening_receipt=hardening_receipt,
                        repo_root=REPO_ROOT,
                    )

        receipt = validate_signing_intent_receipt(raised.exception.receipt)
        evidence = {item for blocker in receipt.blockers for item in blocker.evidence}

        self.assertIn("acceptance_trace.0:literal_error", evidence)
        self.assertIn("allowed_algorithms.1:string_type", evidence)
        self.assertFalse(receipt.signing_performed)
        self.assertFalse(receipt.key_material_accessed)

    def test_signing_receipts_keep_repo_relative_policy_paths(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()

        payload = build_signing_intent_receipt(
            policy_path=FIXTURE_POLICY,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
            repo_root=REPO_ROOT,
        )
        receipt = validate_signing_intent_receipt(payload)

        self.assertEqual(
            receipt.policy_path,
            "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json",
        )

    def test_observability_blocks_external_event_paths_before_reading(self) -> None:
        package_receipt, _hardening_receipt = self._package_receipts()

        with self.assertRaises(ObservabilityFeedbackError) as raised:
            build_observability_feedback_receipt(
                REPO_ROOT,
                package_receipt=package_receipt,
                events_path="/etc/passwd",
            )

        receipt = validate_observability_feedback_receipt(raised.exception.receipt)

        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.event_count, 0)
        self.assertEqual(receipt.scenario_candidates, [])
        self.assertEqual([blocker.id for blocker in receipt.blockers], ["events_path_allowed"])

    def test_trust_ledger_blocks_external_or_malformed_evidence_without_leaking_digests(self) -> None:
        package_receipt, _hardening_receipt = self._package_receipts()

        with self.assertRaises(TrustLedgerError) as raised:
            build_trust_decision_receipt(
                REPO_ROOT,
                package_receipt=package_receipt,
                decision="trust",
                reason="external ledger path should block before hashing",
                owner="skills-sdk-tests",
                apply=False,
                ledger_path="/etc/passwd",
            )

        receipt = validate_trust_decision_receipt(raised.exception.receipt)
        self.assertEqual(receipt.status, "blocked")
        self.assertIsNone(receipt.ledger_before_digest)
        self.assertIsNone(receipt.ledger_after_digest)
        self.assertFalse(receipt.mutation_performed)

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(TrustLedgerError) as malformed:
                build_trust_decision_receipt(
                    REPO_ROOT,
                    package_receipt=package_receipt,
                    decision="revoke",
                    reason="short digest should not enter receipts",
                    owner="skills-sdk-tests",
                    apply=False,
                    ledger_path=str(Path(tmpdir) / "trust-ledger.jsonl"),
                    revoked_package_digest="sha256:x",
                )

        malformed_receipt = validate_trust_decision_receipt(malformed.exception.receipt)
        self.assertIsNone(malformed_receipt.revoked_package_digest)
        self.assertIn("trust_decision_shape", {blocker.id for blocker in malformed_receipt.blockers})

    def test_emitter_target_root_is_schema_safe_for_pass_and_blocked_paths(self) -> None:
        package_receipt, hardening_receipt = self._package_receipts()

        normalized = build_emitter_preview_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
            target_root=".agents/skills/",
        )
        normalized_receipt = validate_emitter_preview_receipt(normalized)
        self.assertEqual(normalized_receipt.target_root, ".agents/skills")

        with self.assertRaises(EmitterPreviewError) as raised:
            build_emitter_preview_receipt(
                REPO_ROOT,
                package_receipt=package_receipt,
                hardening_receipt=hardening_receipt,
                target_root="/.agents/skills",
            )

        blocked_receipt = validate_emitter_preview_receipt(raised.exception.receipt)
        self.assertEqual(blocked_receipt.status, "blocked")
        self.assertEqual(blocked_receipt.target_root, ".agents/skills")
        self.assertEqual(blocked_receipt.write_plan, [])


if __name__ == "__main__":
    unittest.main()
