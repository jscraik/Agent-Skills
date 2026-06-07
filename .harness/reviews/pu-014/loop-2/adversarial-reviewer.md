# PU-014 Adversarial Review, Loop 2

## Findings

### P2 - Smoke-only closeout proof can pass without proving the robot envelope contract
- Severity: P2
- Confidence: 0.97
- Validation ownership: introduced by current planning artifacts
- Evidence:
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:30-33` still uses a closeout proof that only checks `data.review_plan.schema_version=skills-sdk.review-plan-receipt.v1`.
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:48-49,107-128,160-171` requires a successful robot JSON envelope containing `data.review_plan`, schema validation, stable next commands, and the implemented advisory row.
- Impacted behavior:
  - A malformed envelope or missing `data.review_plan` can still satisfy the closeout proof, so the planning lane can report success while the actual API contract is broken.
- Remediation:
  - Replace the smoke-only closeout proof with parsed-JSON assertions on `status == success`, `data.review_plan` presence, schema validity, `mutation_performed == false`, and the stability checks that the spec already asks for.
- Why it matters:
  - This is the exact kind of proof drift that lets an implementation look complete from a string match while the envelope shape or routed payload silently regresses.

### P2 - The spec still frames PU-014 as adding a route that the worktree already exposes
- Severity: P2
- Confidence: 0.93
- Validation ownership: introduced by current planning artifacts
- Evidence:
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:23-35` frames the slice as making the review-plan route operational, while the current evidence section already says `Infrastructure/scripts/lib/ask/commands/sdk.py` exposes `sdk review plan`.
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:20-26,43-78` treats the route, schema, status row, and HTML artifact as the remaining implementation target.
  - Live worktree evidence already shows the route and route truth in place: `Infrastructure/scripts/lib/ask/commands/sdk.py:203-239`, `Infrastructure/config/skills-sdk/capability-matrix.v1.json:170-183`, and `artifacts/recommended-skills-sdk-pipeline.html:2195`.
- Impacted behavior:
  - The plan stays one step behind the worktree truth, which can send the next agent to re-implement or re-validate a route that is already present and instead miss the narrower remaining hardening delta.
- Remediation:
  - Rewrite the stage framing to say the route already exists and PU-014 now hardens receipt/schema/status truth, or explicitly split the already-implemented route from the remaining contract-hardening slice.
- Why it matters:
  - This is route-truth drift, not just wording. If the artifact claims the wrong delta, downstream reviewers can validate the wrong thing.

### P2 - Receipt-out policy is narrower in code than the spec currently promises
- Severity: P2
- Confidence: 0.86
- Validation ownership: introduced by current planning artifacts
- Evidence:
  - `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md:88-90` says `--receipt-out` may use a safe explicit path accepted by existing repo conventions.
  - `.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md:35-36,63-65,80-85` only traces repo-local receipt writes and unsafe-path refusal.
  - `Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py:175-185` rejects any receipt path that resolves outside the repository root.
- Impacted behavior:
  - A maintainer reading the spec will believe there is a supported safe outside-repo receipt lane, but the current plan and builder only support repo-root writes. That makes the safety contract ambiguous and the validation target impossible to read unambiguously.
- Remediation:
  - Either narrow R4 to repo-root-only receipt writes, or define the outside-repo convention explicitly and add a test for it.
- Why it matters:
  - Receipt safety has to be unambiguous. Otherwise operators will infer a supported path that the implementation will never honor.

## What Closed Loop 1
- Intent/schema parity is now aligned: `KNOWN_TASK_INTENTS` and the review-plan schema enum match.
- Typoed repo-relative targets are now rejected instead of being downgraded to `unresolved_handle`.
- The local-only builder boundary is now explicit in the test plan.

## Accountability Receipt
- status: complete
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-2/adversarial-reviewer.md
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/adversarial-reviewer-pu-014-loop-2/manifest.json
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/adversarial-reviewer-pu-014-loop-2/manifest.json
- findings: 3
- failures_or_blockers: none
- improvement_opportunities:
  - Make closeout proofs parse the robot envelope instead of matching one field.
  - Reframe the spec so it matches the route truth already present in the worktree.
  - Decide whether receipt-out supports only repo-root writes or an explicit outside-repo convention.
- strengths:
  - The plan now covers the typoed-path refusal path that loop 1 called out.
  - The schema and parser intent set are aligned.
  - The local-only builder guard is explicitly tested.
- validation_evidence:
  - Read the updated spec and trace plan with line-numbered inspection.
  - Cross-checked the live worktree for the command, capability matrix, and pipeline row.
  - Re-read the loop-1 adversarial and autoresearch reports to verify which items were already closed.
- useful_findings:
  - Closeout proofs should assert the parsed envelope, not a schema-version substring.
  - Route-truth claims need to be rewritten when the worktree already contains the route.
  - Receipt-path policy must be narrowed or explicitly broadened, but not left implied.
- avoided_false_positive:
  - Did not re-flag the intent/schema parity split because the schema enum now matches `KNOWN_TASK_INTENTS`.
  - Did not re-flag the typoed repo-relative path classification bug because the plan and code now reject it explicitly.
  - Did not re-flag the local-only boundary because the builder tests now guard against outbound helpers.
- evidence_quality:
  - High for the on-disk line references.
  - High for the stale-route finding because the current worktree shows the route and status row already exist.
  - Moderate for the receipt-out policy finding because the spec leaves room for an outside-repo convention that the plan never defines.
- followed_scope: true
- reusable_learning:
  - If a closeout proof is meant to prove a JSON contract, parse the JSON and assert the fields that matter.
  - If the live worktree already contains the route, rewrite the planning artifact to describe the remaining hardening slice only.
  - If a write path has to be safe, make the allowed path class explicit in one surface and test it there.
- coordinator_score: 8
- next_action: update the spec or trace plan to remove the stale route framing and tighten the receipt-out closeout proof before implementation begins.

WROTE: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-2/adversarial-reviewer.md

