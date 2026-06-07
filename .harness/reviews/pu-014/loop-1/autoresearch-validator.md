# PU-014 Autoresearch Validator Review

Scope: review only the two planning artifacts on disk:
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md
- .harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md

## Findings

### P2 - Closeout proof is too weak for the required receipt contract
Evidence:
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:42-49
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:104-106
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:118-126
- .harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:29-38

Why it matters:
The spec requires a successful robot JSON envelope containing data.review_plan and a schema-backed receipt. The trace plan closeout proof only asks for smoke output that contains schema_version=skills-sdk.review-plan-receipt.v1. That can pass even if the parsed envelope is malformed, data.review_plan is missing, or the receipt shape drifts.

Specific fix:
Replace the smoke only closeout proof with an assertion on parsed robot JSON, including data.review_plan, and keep the schema validation test as the main proof of contract correctness.

### P2 - The local only and no external service boundary is prose only, not enforced
Evidence:
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:128-133
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:184-187
- .harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:39-40
- .harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:77-82

Why it matters:
Both documents say the feature should not run reviewers or external services, but the trace plan does not add a negative test or acceptance check that proves the sdk review plan path stays local only. A hidden network or service call could be introduced and still satisfy the listed validation commands.

Specific fix:
Add an explicit acceptance criterion and a regression test that fails if the review plan path makes any outbound network or service call, or otherwise asserts that all routing data is derived from local inputs only.

### P3 - --repo-file routing input is specified but not covered in the trace plan
Evidence:
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:59-66
- .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:118-126
- .harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:42-63
- .harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:77-82

Why it matters:
--repo-file is part of the command contract and is explicitly framed as a routing signal, but the trace plan does not add parsing, propagation, or determinism coverage for it. That leaves a gap where a required input can be silently ignored while the rest of the plan still appears complete.

Specific fix:
Add a test that exercises one and multiple --repo-file values and asserts the intended effect on review routing, or document an explicit no op contract if the input is meant to be accepted but not yet used.

## Accountability Receipt

- status: completed
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-1/autoresearch-validator.md
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/autoresearch-validator-pu-014-loop-1/manifest.json
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/autoresearch-validator-pu-014-loop-1/manifest.json
- findings: 3
- failures_or_blockers: none
- improvement_opportunities:
  - tighten closeout proof to parse and assert the review plan robot envelope
  - add a negative test for outbound calls so the local only boundary is enforced
  - cover --repo-file propagation or explicitly document it as a no op
- strengths:
  - the spec and trace plan both clearly scope the feature as read only and non mutating
  - the trace plan already separates local validation from PR, CI, review, and mergeability lanes
  - the schema backed approach is a strong base for future review routing
- validation_evidence:
  - read both planning artifacts from disk with line numbered output
  - confirmed the repo codestyle fallback guidance before reviewing the artifacts
- useful_findings:
  - schema version string checks are not enough to prove the envelope shape
  - prose only no external service boundaries need a test to stay durable
  - routed inputs should be covered explicitly when they are part of the command contract
- avoided_false_positive:
  - did not flag the separate PR, CI, review, and mergeability lane because the trace plan explicitly keeps it out of scope until a PR exists
  - did not flag the advisory read only wording itself because both artifacts already state that boundary
- evidence_quality:
  - high for the cited line references
  - moderate for the no network issue because the plan does not enumerate the internal call graph, so the finding is based on contract coverage rather than a runtime trace
  - high for the repo file gap because the command contract names it directly
- followed_scope: true
- reusable_learning:
  - for future routing plans, require at least one test that parses the robot JSON envelope instead of relying on smoke text matches
  - if a command must remain local only, encode that as a negative test, not just a non goal
- coordinator_score: 8

WROTE: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-1/autoresearch-validator.md
