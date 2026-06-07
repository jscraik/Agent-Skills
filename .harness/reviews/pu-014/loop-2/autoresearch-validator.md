# PU-014 Loop 2 Autoresearch Validator Review

## Findings

### P2 - Validation status overclaims completion without attached proof
- Evidence: trace plan line 98-104
- Why it matters: the trace plan says "Implementation validation: pass for focused local lane" but does not attach a command output, run artifact, or manifest reference in the document. That makes the status lane stronger than the evidence lane and invites stale readiness claims.
- Specific fix: downgrade the validation status to pending/not checked unless you add the concrete command evidence or artifact path that proves the pass.

### P2 - Closeout proof is still too weak for parsed envelope and schema proof
- Evidence: trace plan line 32-33
- Why it matters: the closeout proof only names a schema-version token in parsed CLI output. That still leaves room for a smoke check to succeed even if the robot envelope shape drifts or data.review_plan is missing. The stronger contract is already present in the test file, but the trace plan does not state it.
- Specific fix: rewrite the closeout proof to require parsed robot JSON containing data.review_plan, then validate that object against sdk-review-plan-receipt.v1.schema.json. Keep the schema-version token as a secondary assertion only.

## Coverage Notes

- Loop-1 gaps around handoff determinism, catalog failure handling, discoverability, local-only behavior, and --repo-file propagation now look fixed in the updated spec and trace plan.
- The live source and tests on disk already support the stronger contract than the trace-plan closeout wording describes, so the remaining risk is documentation/status drift rather than missing implementation surface.

## Accountability Receipt

- status: complete
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-2/autoresearch-validator.md
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/autoresearch-validator-pu-014-loop-2/manifest.json
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/autoresearch-validator-pu-014-loop-2/manifest.json
- findings:
  - P2: validation status overclaims completion without attached proof
  - P2: closeout proof is still too weak for parsed envelope and schema proof
- failures_or_blockers: none
- improvement_opportunities:
  - align validation status with actual run artifacts
  - tighten closeout proof to parsed JSON plus schema validation
- strengths:
  - loop-1 gaps were mostly closed in the updated spec and trace plan
  - the route truth is now aligned with the live worktree and tests
- validation_evidence:
  - read the updated spec and trace plan with line-numbered inspection
  - cross-checked the live worktree source and tests for route truth and envelope behavior
  - compared the updated artifacts against the loop-1 reviewer reports
- useful_findings:
  - status fields should point to concrete evidence, not aspirational wording
  - closeout proof should name parsed JSON assertions, not just schema-version strings
- avoided_false_positive:
  - did not re-flag the loop-1 gaps that are now covered by the updated artifacts
  - did not treat the existing route implementation as a defect because the planning slice is about evidence framing
- evidence_quality:
  - high
- followed_scope: true
- reusable_learning:
  - evidence boundaries need explicit JSON assertions when the contract is envelope-shaped
  - validation status should only say pass when the artifact includes proof or a manifest that proves it
- coordinator_score: 8
- next_action:
  - if this slice continues, update the trace plan's validation-status and closeout-proof wording to match the actual proof shape

WROTE: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-2/autoresearch-validator.md
