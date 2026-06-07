# PU-014 Loop 2 Agent-Native Review

## Summary
The updated spec and trace plan now match the live worktree on the main loop-1 issues: the `sdk review plan` route exists, typoed repo-relative paths are rejected, `--repo-file` is traced, and the builder path is explicitly local-only. Two planning-contract gaps remain: the traceability proof for the main robot envelope is still too weak, and the public receipt contract omits `schema_uri` even though the emitted schema requires it.

The loop-1 intent/schema split appears resolved in the live worktree because the CLI parser and public receipt schema now share the same intent enum. I did not flag the earlier stale-route, typoed-path, repo-file, or local-only issues again because they are now covered.

## Findings

### 1. P2 - Closeout proof still only asserts `schema_version` instead of the parsed robot envelope
- Evidence:
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:32`
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:160`
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:161`
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:162`
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:116`
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:117`
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:118`
- Why it matters:
  - The traceability row still says the closeout proof is a `schema_version` check only, which is too weak for the spec's parsed-envelope requirement.
  - A smoke check that only looks for the schema version string can pass even if `data.review_plan` is missing, malformed, or missing the `status` and `mutation_performed` fields the spec calls out.
- Specific fix:
  - Rewrite the R1 closeout proof to require parsed robot JSON assertions on `data.review_plan.status`, `mutation_performed`, and at least one selected lens, or point the row at the focused test that already performs those assertions.
- Confidence: high

### 2. P2 - `schema_uri` is required by the schema but omitted from the documented public receipt contract
- Evidence:
  - `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json:7`
  - `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json:8`
  - `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json:29`
  - `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json:30`
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:70`
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:86`
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:34`
- Why it matters:
  - The emitted receipt and schema require `schema_uri`, but the public contract text does not list it anywhere in R3 or the traceability map.
  - That creates a spec/schema mismatch for downstream consumers: a reader following the planning artifacts will not know the field is required, even though validation will require it.
- Specific fix:
  - Add `schema_uri` to R3 and the trace plan's receipt-field list, or remove it from the schema and implementation if it is meant to stay internal.
- Confidence: high

## What's Working Well
- The loop-1 route-truth issue is gone: the worktree already exposes `sdk review plan`, and the capability matrix plus pipeline artifact include `review_plan` as implemented.
- The loop-1 typoed-path issue is closed: the tests now reject `Skills/agent-ops/simplifie` instead of downgrading it to `unresolved_handle`.
- The loop-1 repo-file and local-only concerns are now covered by explicit traceability text and focused tests.
- The schema-backed receipt approach is a solid base for deterministic handoff.

## Accountability Receipt
- status: complete
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-2/agent-native-reviewer.md
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/agent-native-reviewer-pu-014-loop-2/manifest.json
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/agent-native-reviewer-pu-014-loop-2/manifest.json
- findings: 2
- failures_or_blockers: none
- improvement_opportunities:
  - Tighten the traceability map so the closeout proof matches the parsed-envelope acceptance criteria.
  - Make the public receipt contract list every required field that validation enforces, including `schema_uri`.
- strengths:
  - The planning artifacts now reflect the live worktree on the previously stale route and typoed-path issues.
  - The trace plan already includes local-only behavior checks and deterministic handoff coverage.
  - The updated contract is much closer to an agent-operable, non-mutating review route.
- validation_evidence:
  - Read the updated spec and trace plan with line-numbered output.
  - Cross-checked the live worktree for `sdk review plan`, `review_plan`, the public schema, the capability matrix, and the pipeline artifact.
  - Inspected the focused review-plan tests for parsed robot output, typoed-path refusal, `--repo-file` propagation, and local-only behavior.
- next_action:
  - Patch the planning artifacts so the traceability proof and public receipt field list match the actual emitted contract.
- useful_findings:
  - A traceability row should point at the strongest assertion, not a smoke-level string match, when a parsed envelope is part of the acceptance bar.
  - If a schema introduces a required field, the public contract text must mention it or explicitly classify it as internal.
- avoided_false_positive:
  - Did not re-flag the stale-route, typoed-path, repo-file, or local-only issues from loop 1 because the updated artifacts and live worktree now cover them.
  - Did not flag PR, CI, or mergeability lanes because the spec explicitly keeps them out of scope for this slice.
- evidence_quality:
  - High for the cited line references.
  - High for the live worktree cross-checks.
- followed_scope: true
- reusable_learning:
  - For future SDK routing specs, keep the public receipt field list in lockstep with the JSON schema.
  - Prefer a parsed-envelope closeout proof whenever a command returns robot JSON.
- coordinator_score: 8

WROTE: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-2/agent-native-reviewer.md
