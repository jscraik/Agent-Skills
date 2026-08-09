"""Shared fixtures and assertions for the Skills SDK schema spine tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"

SCHEMA_NAMES = {
    "manifest-source": "manifest-source.v1.schema.json",
    "check-receipt": "check-receipt.v1.schema.json",
    "sdk-check": "sdk-check.v1.schema.json",
    "capability-evidence-receipt": "capability-evidence-receipt.v0.schema.json",
    "evidence-status": "evidence-status.v1.schema.json",
    "risk-classification": "risk-classification.v1.schema.json",
    "risk-mode-taxonomy-receipt": "risk-mode-taxonomy-receipt.v0.schema.json",
    "skill-intake-review-receipt": "skill-intake-review-receipt.v0.schema.json",
    "install-preview": "install-preview.v1.schema.json",
    "install-receipt": "install-receipt.v1.schema.json",
    "lockfile-preview": "lockfile-preview.v1.schema.json",
    "lockfile": "lockfile.v1.schema.json",
    "skill-ir": "skill-ir.v0.schema.json",
    "package-manifest": "package-manifest.v0.schema.json",
    "package-digest-receipt": "package-digest-receipt.v0.schema.json",
    "package-hardening-receipt": "package-hardening-receipt.v0.schema.json",
    "package-security-signature-receipt": "package-security-signature-receipt.v0.schema.json",
    "security-lane-receipt": "security-lane-receipt.v0.schema.json",
    "trust-decision-receipt": "trust-decision-receipt.v0.schema.json",
    "observability-feedback-receipt": "observability-feedback-receipt.v0.schema.json",
    "observability-promotion-receipt": "observability-promotion-receipt.v0.schema.json",
    "emitter-preview-receipt": "emitter-preview-receipt.v0.schema.json",
    "ci-policy-preview-receipt": "ci-policy-preview-receipt.v0.schema.json",
    "security-adapter-discovery-receipt": "security-adapter-discovery-receipt.v0.schema.json",
    "static-explorer-receipt": "static-explorer-receipt.v0.schema.json",
    "scenario-quality-receipt": "scenario-quality-receipt.v0.schema.json",
    "scenario-registry-entry": "scenario-registry-entry.v0.schema.json",
    "scenario-adaptation-receipt": "scenario-adaptation-receipt.v0.schema.json",
    "scorer-quality-receipt": "scorer-quality-receipt.v0.schema.json",
    "signing-policy": "signing-policy.v0.schema.json",
    "signing-intent-receipt": "signing-intent-receipt.v0.schema.json",
    "sandbox-profile": "sandbox-profile.v0.schema.json",
    "sandbox-profile-receipt": "sandbox-profile-receipt.v0.schema.json",
    "skill-intake-receipt": "skill-intake-receipt.v0.schema.json",
    "eval-profile-preview-receipt": "eval-profile-preview-receipt.v0.schema.json",
    "ab-rubric-receipt": "ab-rubric-receipt.v0.schema.json",
    "ab-preview-receipt": "ab-preview-receipt.v0.schema.json",
    "ab-plan-receipt": "ab-plan-receipt.v0.schema.json",
    "ab-run-receipt": "ab-run-receipt.v0.schema.json",
    "ab-plan-receipt-v1": "ab-plan-receipt.v1.schema.json",
    "ab-run-receipt-v1": "ab-run-receipt.v1.schema.json",
    "ab-judge-preview-receipt": "ab-judge-preview-receipt.v0.schema.json",
    "ab-judge-score-receipt": "ab-judge-score-receipt.v0.schema.json",
    "eval-case": "eval-case.v0.schema.json",
    "eval-run-receipt": "eval-run-receipt.v0.schema.json",
    "phoenix-smoke-receipt": "phoenix-smoke-receipt.v0.schema.json",
    "phoenix-eval-trace-receipt": "phoenix-eval-trace-receipt.v1.schema.json",
    "project-conformance-receipt": "project-conformance-receipt.v1.schema.json",
    "placeholder-lifecycle": "placeholder-lifecycle.v1.schema.json",
    "review-plan-receipt": "sdk-review-plan-receipt.v1.schema.json",
    "review-plan-trace": "sdk-review-plan-trace.v1.schema.json",
    "review-handoff-receipt": "sdk-review-handoff-receipt.v1.schema.json",
    "pipeline-start": "pipeline-start.v1.schema.json",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class SchemaSpineTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            name: _json(SCHEMA_DIR / schema_name)
            for name, schema_name in SCHEMA_NAMES.items()
        }
        cls.schemas_by_file = {
            schema_name: _json(SCHEMA_DIR / schema_name)
            for schema_name in SCHEMA_NAMES.values()
        }

    def assert_valid(self, schema_key: str, fixture_name: str) -> dict:
        payload = _json(FIXTURE_DIR / "valid" / fixture_name)
        _validate_schema_subset(
            self.schemas[schema_key],
            payload,
            {**self.schemas, **self.schemas_by_file},
        )
        return payload

    def assert_invalid(self, schema_key: str, fixture_name: str) -> None:
        payload = _json(FIXTURE_DIR / "invalid" / fixture_name)
        with self.assertRaises(AssertionError):
            _validate_schema_subset(
                self.schemas[schema_key],
                payload,
                {**self.schemas, **self.schemas_by_file},
            )
