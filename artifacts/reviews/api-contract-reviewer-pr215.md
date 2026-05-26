{
  "reviewer": "api-contract",
  "findings": [
    {
      "severity": "high",
      "title": "Breaking v1 payload contract: new required checks field added without schema version bump",
      "classification": "introduced_by_current_patch",
      "confidence": 0.97,
      "evidence": [
        "Infrastructure/config/schemas/skill-doctor.v1.schema.json:30 keeps schema_version const at skill-doctor.v1.",
        "Infrastructure/config/schemas/skill-doctor.v1.schema.json:231-239 now requires checks.projection_ownership.",
        "Infrastructure/tests/test_jsc351_codex_abi_schema_contracts.py:295-307 enforces projection_ownership as required for v1 payloads."
      ],
      "impact": "Any existing producer or fixture that still emits valid pre-change skill-doctor.v1 payloads (without checks.projection_ownership) will fail schema validation immediately. This is a backward-incompatible contract change shipped under the same schema identity.",
      "remediation": "Either (a) bump the payload/schema identity (for example skill-doctor.v2) and treat projection_ownership as required only in v2, or (b) keep v1 backward-compatible by making projection_ownership optional in schema and behaviorally additive."
    }
  ],
  "residual_risks": [
    {
      "area": "CLI/human-output compatibility",
      "note": "The human output check-count expectation changed from pass=6 to pass=7 (Infrastructure/tests/test_ask_cli_impl.py:1989). If external parsers or dashboards pattern-match exact count text, this may be a soft compatibility drift even when JSON parsing remains stable."
    },
    {
      "area": "Error-shape consistency",
      "note": "No direct error-shape regression found in sampled paths; blocker/warning classes remain structured. Risk remains that downstream tooling relying on fixed check-name sets must be updated in lockstep."
    },
    {
      "area": "Manifest schema rollout",
      "note": "New schema file skills-sdk.project.v1 is additive and versioned, but integration points that assume only prior schema filenames may require explicit allowlist updates."
    }
  ],
  "testing_gaps": [
    {
      "gap": "No explicit backward-compat test validating pre-change skill-doctor.v1 payload acceptance",
      "evidence": "Current tests assert the new required field (Infrastructure/tests/test_jsc351_codex_abi_schema_contracts.py:295-307) but do not preserve old v1 payload validity guarantees."
    }
  ]
}
WROTE: artifacts/reviews/api-contract-reviewer-pr215.md
