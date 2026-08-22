"""Focused routing-quality receipt schema tests."""

import importlib.util
import math
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory


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


def catalog_parity_payload() -> dict[str, object]:
    """Return one minimal valid catalog-parity receipt."""
    return {
        "schema_version": "catalog-parity.v1",
        "policy_identity": "policy",
        "canonical_count": 1,
        "surfaces": [],
        "drift_detected": False,
        "drift_class": None,
        "blocking_reason": None,
        "operator_action": None,
        "decision_status": "resolved",
        "history_status": "available",
    }


class TestCatalogParitySchema(unittest.TestCase):
    """Enforce explicit catalog history status evidence."""

    def test_valid_history_statuses_pass(self) -> None:
        """Every status emitted by catalog parity satisfies the schema."""
        for status in (
            "available",
            "insufficient_history",
            "not_checked",
            "not_collected",
            "schema_invalid_history",
            "trend_deterioration",
        ):
            with self.subTest(status=status):
                payload = catalog_parity_payload()
                payload["history_status"] = status
                if status in {"schema_invalid_history", "trend_deterioration"}:
                    payload.update(
                        {
                            "decision_status": "blocked_catalog_parity",
                            "drift_detected": True,
                            "drift_class": status,
                            "blocking_reason": status,
                            "operator_action": "Repair history evidence.",
                        }
                    )
                self.assertEqual(MODULE.validate_catalog_parity(payload), [])

    def test_missing_history_status_fails(self) -> None:
        """Catalog receipts cannot omit authoritative history evidence."""
        payload = catalog_parity_payload()
        del payload["history_status"]

        issues = MODULE.validate_catalog_parity(payload)

        self.assertIn("missing required fields: history_status", issues)
        self.assertIn("invalid history_status", issues)

    def test_unhashable_history_status_is_invalid(self) -> None:
        """Malformed container statuses return schema issues instead of raising."""
        payload = catalog_parity_payload()
        payload["history_status"] = []

        self.assertIn("invalid history_status", MODULE.validate_catalog_parity(payload))

    def test_blocking_history_requires_complete_blocked_catalog_state(self) -> None:
        """Strict history blockers cannot be paired with resolved catalog evidence."""
        for status in ("schema_invalid_history", "trend_deterioration"):
            with self.subTest(status=status):
                payload = catalog_parity_payload()
                payload["history_status"] = status

                issues = MODULE.validate_catalog_parity(payload)

                self.assertIn(
                    "blocking history_status must block catalog parity", issues
                )
                self.assertIn(
                    "blocked catalog parity must set drift_detected=true", issues
                )
                self.assertIn(
                    "blocked catalog parity must include blocking_reason", issues
                )

    def test_blocked_catalog_requires_all_diagnostic_fields(self) -> None:
        """Blocked receipts carry drift classification, reason, and recovery."""
        payload = catalog_parity_payload()
        payload.update(
            {
                "decision_status": "blocked_catalog_parity",
                "drift_detected": True,
                "history_status": "trend_deterioration",
                "drift_class": "trend_deterioration",
                "blocking_reason": "soft_gate_deterioration",
                "operator_action": "Repair routing quality.",
            }
        )

        self.assertEqual(MODULE.validate_catalog_parity(payload), [])


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

    def test_boolean_and_non_finite_rates_fail(self) -> None:
        """Malformed JSON-compatible numeric values cannot pass as rates."""
        for value in (True, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                payload = routing_quality_payload()
                payload["no_candidate_rate"] = value
                self.assertIn(
                    "no_candidate_rate must be numeric",
                    MODULE.validate_routing_quality(payload),
                )

    def test_oversized_integer_rate_reports_range_error(self) -> None:
        """Arbitrary-size JSON integers cannot crash finite-value checks."""
        payload = routing_quality_payload()
        payload["no_candidate_rate"] = 10**1000

        self.assertIn(
            "no_candidate_rate must be within [0,1]",
            MODULE.validate_routing_quality(payload),
        )

    def test_unhashable_history_status_is_invalid(self) -> None:
        """Malformed container statuses return schema issues instead of raising."""
        payload = routing_quality_payload()
        payload["history_status"] = []

        self.assertIn(
            "invalid history_status", MODULE.validate_routing_quality(payload)
        )

    def test_unhashable_history_persistence_gate_is_invalid(self) -> None:
        """Malformed gate containers return schema issues instead of raising."""
        for gate in ([], {}):
            with self.subTest(gate=gate):
                payload = routing_quality_payload()
                payload["gate_outcomes"] = {
                    "hard": {"history_persistence": gate}
                }

                self.assertIn(
                    "invalid history_persistence gate",
                    MODULE.validate_routing_quality(payload),
                )

    def test_invalid_input_reports_service_and_source(self) -> None:
        """Input failures return a contextual service-owned diagnostic."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.json"
            path.write_text("not-json", encoding="utf-8")
            output = StringIO()
            original_argv = sys.argv
            self.addCleanup(setattr, sys, "argv", original_argv)
            sys.argv = [str(SCRIPT_PATH), "--input", str(path)]

            with self.assertLogs(MODULE.logger, level="ERROR") as logs:
                with redirect_stdout(output):
                    status = MODULE.main()

            self.assertEqual(status, 1)
            self.assertIn("service=router-schema-verifier", output.getvalue())
            self.assertIn(str(path), output.getvalue())
            self.assertIn("service=router-schema-verifier", logs.output[0])


class TestDecisionSchemaBoundaries(unittest.TestCase):
    """Reject JSON values that exploit Python's container and Boolean types."""

    def test_container_decision_statuses_are_invalid(self) -> None:
        """Selection and goal validators return issues instead of raising."""
        self.assertEqual(
            MODULE._selection_status_issues({"decision_status": []}),
            ["invalid decision_status"],
        )
        self.assertEqual(
            MODULE._goal_status_issues({"decision_status": {}}),
            ["invalid decision_status"],
        )

    def test_boolean_selection_counters_are_invalid(self) -> None:
        """Boolean values cannot satisfy integer counter fields."""
        payload = {
            "selected_candidates": [],
            "considered_candidates": [],
            "excluded_candidates": [],
            "considered_limit": True,
            "considered_total": False,
            "considered_truncated": False,
            "truncated_count": True,
        }

        self.assertEqual(
            MODULE._selection_type_issues(payload),
            [
                "considered_limit must be an integer",
                "considered_total must be an integer",
                "truncated_count must be an integer",
            ],
        )


if __name__ == "__main__":
    unittest.main()
