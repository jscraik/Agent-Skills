from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.envelope import CallResult  # noqa: E402
from ask.selection_contract import EligibleCandidate, build_decision_payload  # noqa: E402
from ask.skills_sdk.eval_ab_plan import _experiment_id  # noqa: E402
from ask.skills_sdk.id_types import (  # noqa: E402
    BRANDED_ID_PATTERN,
    BrandedIdError,
    branded_id_from_digest,
    new_branded_id,
    require_branded_id,
)
from ask.skills_sdk.review_plan import build_review_plan  # noqa: E402


class TestSkillsSdkIdTypes(unittest.TestCase):
    def test_new_id_uses_kind_brand_and_alphanumeric_suffix(self) -> None:
        value = new_branded_id("ch", token_provider=lambda length: "a1" * (length // 2))

        self.assertEqual(value, "ch_a1a1a1a1a1a1")
        self.assertRegex(value, BRANDED_ID_PATTERN)
        self.assertEqual(require_branded_id(value, prefix="ch"), value)

    def test_new_id_rejects_invalid_brand_and_token_provider(self) -> None:
        with self.assertRaisesRegex(ValueError, "lowercase ASCII"):
            new_branded_id("Channel")
        with self.assertRaisesRegex(ValueError, "alphanumeric"):
            new_branded_id("ch", token_provider=lambda _length: "bad-token!!!")

    def test_require_branded_id_rejects_uuid_and_wrong_prefix(self) -> None:
        with self.assertRaises(BrandedIdError):
            require_branded_id("550e8400-e29b-41d4-a716-446655440000")
        with self.assertRaisesRegex(BrandedIdError, "prefix"):
            require_branded_id("rq_abcdefghijkl", prefix="tr")

    def test_digest_ids_are_stable_and_branded(self) -> None:
        first = branded_id_from_digest("ex", "sha256:0123456789abcdef", length=16)
        second = branded_id_from_digest("ex", "sha256:0123456789abcdef", length=16)

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("ex_"))
        self.assertRegex(first, BRANDED_ID_PATTERN)

    def test_review_plan_uses_receipt_instance_brand(self) -> None:
        receipt = build_review_plan(
            REPO_ROOT,
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
            max_lenses=1,
        )

        self.assertTrue(str(receipt["source_context"]["receipt_instance_id"]).startswith("rp_"))
        require_branded_id(str(receipt["source_context"]["receipt_instance_id"]), prefix="rp")

    def test_envelope_uses_trace_brand_when_not_operator_supplied(self) -> None:
        trace_id = CallResult().trace_id

        self.assertTrue(trace_id.startswith("tr_"))
        require_branded_id(trace_id, prefix="tr")

    def test_selection_uses_request_brand_when_not_operator_supplied(self) -> None:
        payload = build_decision_payload(
            request="select simplify",
            policy_identity="policy-v1",
            considered_limit=1,
            top_k=1,
            eligible_candidates=[EligibleCandidate("simplify", "Skills/agent-ops/simplify", "", 1)],
            ranked_candidates=[{"skill_name": "simplify", "skill_path": "Skills/agent-ops/simplify", "confidence": 1.0}],
            uncertainty_reasons=[],
        )

        self.assertTrue(payload["request_id"].startswith("rq_"))
        require_branded_id(payload["request_id"], prefix="rq")

    def test_ab_experiment_ids_are_branded_and_stable(self) -> None:
        preview = {
            "skill_a": {"package_digest": "sha256:a"},
            "skill_b": {"package_digest": "sha256:b"},
            "fixture": {"digest": "sha256:c"},
        }

        experiment_id = _experiment_id(preview, "codex-read-only", "oss-local")

        self.assertTrue(experiment_id.startswith("ex_"))
        require_branded_id(experiment_id, prefix="ex")


if __name__ == "__main__":
    unittest.main()
