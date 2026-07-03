# Scenario Registry Guardrails MVP

Date: 2026-07-03

Branch: `codex-scenario-registry-guardrails`

Status: implementation slice

## Scope

This slice implements the first governed shared scenario registry guardrails for
the Skills SDK eval pipeline.

Implemented:

- Scenario registry entry JSON schema.
- Scenario adaptation receipt JSON schema.
- Reusable no-direct-registry-use guardrail module.
- Standalone `validate_no_direct_registry_scenario_use.py` validator.
- Scenario-quality integration so registry-derived coverage is blocked unless
  an SDK adaptation receipt proves local adaptation.
- Regression tests for direct registry references, authorized adaptation
  receipts, and unauthenticated/ad hoc validator usage.

Not implemented:

- Registry storage commands.
- Scenario registry suggest/adapt CLI commands.
- Registry promotion or demotion workflow.
- Tessl, oss-cloud, publication, release, or merge-readiness lanes.

## Guardrail Contract

Shared scenarios are seed/source assets only. A local skill package cannot count
registry-derived coverage until:

1. The scenario is materialized into local `references/evals.yaml`.
2. A local `references/scenario-adaptation-receipts/<case-id>.json` receipt
   exists.
3. The receipt has schema `skills-sdk.scenario-adaptation-receipt.v0` and
   status `pass`.
4. The receipt names the target skill and target case id.
5. The receipt declares local criteria as authoritative.
6. Scenario-quality validates the adapted local package.

Direct registry references in `SKILL.md` are blocked. Direct registry
references in `references/evals.yaml` are blocked unless backed by the SDK
adaptation receipt.

## Validation Plan

Run focused Infrastructure tests for:

- direct registry references failing,
- adapted local scenarios with receipts passing,
- unauthenticated validator usage blocking,
- schema-spine validation for the new schema contracts,
- full scenario-quality regression coverage.
