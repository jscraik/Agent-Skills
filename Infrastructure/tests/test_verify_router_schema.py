"""Focused routing-quality receipt schema tests."""

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validation-and-linting"
    / "verify_router_schema.py"
)
SPEC = importlib.util.spec_from_file_location("verify_router_schema", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def routing_quality_payload() -> dict[str, object]:
    """Return one minimal valid routing-quality receipt."""
    return {
        "schema_version": "routing-quality.v1",
        "run_id": "run",
        "policy_identity": "policy",
        "decision_status_counts": {},
        "unresolved_ambiguity_rate": 0.0,
        "no_candidate_rate": 0.0,
        "top_rejection_reasons": [],
        "explainability_completeness_ratio": 1.0,
        "parity_status": "pass",
        "history_status": "accepted",
        "gate_outcomes": {"hard": {"history_persistence": "pass"}},
    }


class TestRoutingQualitySchema(unittest.TestCase):
    """Enforce history evidence on routing-quality receipts."""

    def test_valid_history_evidence_passes(self) -> None:
        """Matching accepted history and persistence evidence is valid."""
        self.assertEqual(MODULE.validate_routing_quality(routing_quality_payload()), [])

    def test_missing_history_evidence_fails(self) -> None:
        """Receipts cannot omit authoritative history evidence."""
        payload = routing_quality_payload()
        del payload["history_status"]
        del payload["gate_outcomes"]

        issues = MODULE.validate_routing_quality(payload)

        self.assertIn("missing required fields: gate_outcomes, history_status", issues)
        self.assertIn("invalid history_status", issues)
        self.assertIn("invalid history_persistence gate", issues)

    def test_contradictory_history_evidence_fails(self) -> None:
        """Rejected history cannot claim successful persistence."""
        payload = routing_quality_payload()
        payload["history_status"] = "schema_invalid_history"

        self.assertIn(
            "history_status contradicts history_persistence gate",
            MODULE.validate_routing_quality(payload),
        )


if __name__ == "__main__":
    unittest.main()
