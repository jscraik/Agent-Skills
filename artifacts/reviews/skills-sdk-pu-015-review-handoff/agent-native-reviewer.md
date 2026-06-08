# Agent-Native Architecture Review

### Summary
The PU-015 handoff spec and trace plan describe a read-only review packaging surface, not a review runner. The two docs are aligned on the important parity boundary: they require provenance, trace integrity, explicit caller target and intent, and repo-root containment before any handoff receipt is emitted.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Create review handoff receipt | ./bin/ask sdk review handoff in the spec/trace plan | Planned review_handoff command | Yes, via the spec requirements and trace plan | Must-have | Covered by the docs |
| Create review-plan provenance and trace sidecar | ./bin/ask sdk review plan --receipt-out ... in the spec/trace plan | Planned review_plan updates | Yes | Must-have | Covered by the docs |
| Surface capability truth in status and HTML | ask sdk status and artifacts/recommended-skills-sdk-pipeline.html | Planned status/matrix update | Yes | Must-have | Covered by the docs |

### Findings

#### Critical (Must Fix)
None.

#### Warnings (Should Fix)
None.

#### Observations
1. The docs are already explicit that review_handoff is packaging only, which reduces the chance of accidental review execution.
2. The trace-sidecar requirement is the strongest anti-copy safeguard in the slice, and it is spelled out clearly in both artifacts.

### What's Working Well
- The handoff command is kept separate from review execution.
- The provenance model is strong: repo root, HEAD, branch policy, receipt instance id, target identity, and trace digest all have to line up.
- Output containment is specified as symlink-aware instead of prefix-based.
- The validation plan includes negative tests for copied, edited, stale, unresolved, and symlink-escaping inputs.

### Score
- 3/3 high-priority capabilities are agent-accessible
- Verdict: PASS

### Accountability Receipt
- status: pass
- artifact_paths:
  - /private/tmp/agent-skills-pu-015-review-handoff/artifacts/reviews/skills-sdk-pu-015-review-handoff/agent-native-reviewer.md
  - /private/tmp/agent-skills-pu-015-review-handoff/artifacts/agent-runs/agent-native-reviewer-20260608-154430/manifest.json
- findings:
  - none
- failures_or_blockers:
  - none
- improvement_opportunities:
  - Add a tiny example receipt pair to the validation fixtures once implementation starts, so reviewers can verify the trace-sidecar contract faster.
- strengths:
  - clear separation between receipt packaging and review completion
  - explicit anti-copy provenance checks
  - repo-root-local output containment requirements
- validation_evidence:
  - /private/tmp/agent-skills-pu-015-review-handoff/.harness/specs/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-spec.md:44-50
  - /private/tmp/agent-skills-pu-015-review-handoff/.harness/specs/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-spec.md:52-75
  - /private/tmp/agent-skills-pu-015-review-handoff/.harness/specs/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-spec.md:76-98
  - /private/tmp/agent-skills-pu-015-review-handoff/.harness/specs/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-spec.md:135-149
  - /private/tmp/agent-skills-pu-015-review-handoff/.harness/plan/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-trace-plan.md:31-40
  - /private/tmp/agent-skills-pu-015-review-handoff/.harness/plan/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-trace-plan.md:59-77
- next_action:
  - Implement the planned review_handoff command, schema, and tests in the PU-015 worktree.
- manifest_path: /private/tmp/agent-skills-pu-015-review-handoff/artifacts/agent-runs/agent-native-reviewer-20260608-154430/manifest.json

WROTE: /private/tmp/agent-skills-pu-015-review-handoff/artifacts/reviews/skills-sdk-pu-015-review-handoff/agent-native-reviewer.md
