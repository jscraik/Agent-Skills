# PU-014 Adversarial Review

## Accountability Receipt

- status: complete
- artifact_paths:
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-1/adversarial-reviewer.md
  - /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/adversarial-reviewer-pu-014-loop-1/manifest.json
- manifest_path: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/agent-runs/adversarial-reviewer-pu-014-loop-1/manifest.json
- findings: 3
- failures_or_blockers: none
- improvement_opportunities:
  - Refresh the spec's current evidence against the live worktree before the next implementation slice.
  - Add a negative case that distinguishes typoed repo-relative paths from true handle-like targets.
  - Resolve the allowed intent set at the spec/schema boundary instead of leaving it split across surfaces.
- strengths:
  - The trace plan does cover the core positive path, explicit write path, and unsafe-path refusal.
  - The planned tests already include schema validation and no-write-by-default coverage.
- validation_evidence:
  - Read /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md with line numbers.
  - Read /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/plan/2026-06-07-skills-sdk-pu-014-lens-routed-review-trace-plan.md with line numbers.
  - Cross-checked current worktree truth in /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/Infrastructure/scripts/lib/ask/commands/sdk.py, /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/Infrastructure/config/skills-sdk/capability-matrix.v1.json, and /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/artifacts/recommended-skills-sdk-pipeline.html.
- next_action:
  - Tighten the spec and trace plan so the implementation slice cannot silently drift into duplicate routes, misclassified targets, or intent/schema mismatch.

## Findings

### 1. Stale route evidence makes the spec describe an older SDK surface than the worktree actually contains
- Severity: P2
- Confidence: 0.98
- Validation ownership: introduced by current planning artifacts
- Evidence:
  - Spec current evidence says Infrastructure/scripts/lib/ask/commands/sdk.py exposes sdk lenses and sdk determinism, but no sdk review route at lines 31-33.
  - The live worktree already has sdk review and sdk review plan parsing at Infrastructure/scripts/lib/ask/commands/sdk.py:203-230.
  - The capability matrix already contains review_plan as implemented at Infrastructure/config/skills-sdk/capability-matrix.v1.json:170-184.
  - The pipeline artifact already renders the review_plan row at artifacts/recommended-skills-sdk-pipeline.html:2194-2195.
- Why it matters:
  - The spec's current evidence section is already stale, so a maintainer following it will plan against a surface that no longer matches the checked-in worktree.
  - That creates route-truth drift: reviewers can re-open an already-present route, duplicate work, or validate the wrong delta.
- Specific fix:
  - Refresh the spec evidence to the live surface, then rewrite the Approved Intent and Current Evidence Checked sections so they describe the actual remaining delta only.
  - If the route is already present by design, change the stage framing from add route to the narrower schema/status hardening work that remains.

### 2. A typoed repo path will be downgraded into a handle instead of being rejected as a missing path
- Severity: P1
- Confidence: 0.96
- Validation ownership: introduced by current planning artifacts
- Evidence:
  - Spec R5 only says missing target files may still produce a receipt when the target is a handle-like value, and that unresolved targets must be classified as unresolved_handle at lines 92-103.
  - The trace plan resolves target_kind as repo_path, skill_source, or unresolved_handle at lines 44-49.
  - The trace plan's negative coverage only names handle-like missing targets, unsafe paths, and invalid max lenses at lines 60-63.
- Why it matters:
  - A typo such as Skills/agent-ops/simplifie is still repo-relative, but the plan gives it no separate missing repo path branch, so it can fall through to unresolved_handle.
  - That silently hides a path typo as an intentional handle lookup and produces a misleading advisory receipt instead of a hard path failure.
- Specific fix:
  - Add an explicit missing_repo_path or equivalent error classification for repo-relative paths that do not exist.
  - Add a negative acceptance case for a typoed repo-relative path that should fail rather than be treated as unresolved_handle.

### 3. The intent surface is split between the CLI, the receipt schema, and the trace plan without a normalization contract
- Severity: P2
- Confidence: 0.93
- Validation ownership: introduced by current planning artifacts
- Evidence:
  - Spec R2 says the command must accept --intent <known lens task intent> at lines 59-66.
  - The trace plan reuses existing lens selection and only says to build receipt content from task_intent at lines 44-49.
  - The current command parser accepts every KNOWN_TASK_INTENTS value at Infrastructure/scripts/lib/ask/commands/sdk.py:214-221.
  - The public review-plan schema only allows five intents at Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json:35-40.
  - The trace plan tests only invalid max lenses, unsafe receipt paths, and handle-like missing targets at lines 60-63; it does not cover any accepted-intent-to-schema mapping.
- Why it matters:
  - A valid CLI intent such as architecture_review or security_review can parse successfully and still fail to fit the public receipt contract, or be forced into an undocumented narrowing step.
  - That is a contract split that will surface as either schema failures, unexpected rejection of legitimate intents, or hidden normalization logic that the tests do not pin down.
- Specific fix:
  - Either narrow the CLI/spec to the exact receipt schema intent set, or define an explicit normalization/mapping layer and test every accepted intent against the emitted receipt contract.
  - Add a negative case for a valid-but-out-of-schema intent so the boundary is explicit instead of accidental.

## Validation Notes

- The review was limited to the two planning artifacts plus live worktree cross-checks needed to verify stale claims.
- I did not edit source files.
- I did not run implementation validation commands.

WROTE: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review/.harness/reviews/pu-014/loop-1/adversarial-reviewer.md
