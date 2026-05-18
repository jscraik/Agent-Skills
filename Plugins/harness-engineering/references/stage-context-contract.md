# Stage Context Contract

Read when: an HE stage is about to choose scope, write a durable artifact, mutate files, or hand off to another stage.

This contract keeps stage entrypoints deep. Cross-stage state is resolved once into a compact context object, then stage files own only their stage-specific decisions.

## Context Shape

When structured context is needed, carry this shape:

```yaml
schema_version: 1
stage_context:
  selected_stage: he-router|he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-fix-bugs|he-improve|he-reconcile|he-reinforce|he-heartbeat|he-eval-report|he-strategy|he-reframe|he-linear-plan|he-phase-work
  selected_slice: "<milestone, parent issue, reframe phase, or execution slice>"
  slice_status: resolved|blocked|not_applicable
  tracker_status: resolved|created|blocked|not_applicable|user_opted_out
  artifact_identity_status: pass|blocked|not_applicable
  artifact_route_status: pass|blocked|not_applicable
  evidence_freshness: fresh|stale|blocked|not_applicable
  session_trace_status: resolved|blocked|not_applicable
  linear_delta_status: pass|blocked|not_applicable
  domain_skill_status: applied|skipped|blocked|not_applicable
  steering_status: asked|assumed_headless|not_needed|blocked
  coding_harness_status: pass|blocked|not_applicable
  project_brain_status: updated|blocked|not_checked|not_applicable
  validation_status: pass|fail|blocked|not_run_with_reason|not_applicable
  git_staging_status: staged|blocked|not_applicable
  blocker: "<smallest recovery step or null>"
```

## Resolution Order

1. Resolve repo, branch, dirty state, PR, Linear, and artifact-chain identity from live repo evidence or session evidence.
2. Identify exactly one selected slice before writing specs, plans, work, reviews, evals, or Linear plans.
3. Resolve tracker state for non-trivial durable work; record an explicit blocker instead of guessing.
4. Resolve artifact route and Artifact Identity before writing `.harness/**` docs.
5. Run the Linear Delta Capture Gate when consuming existing tracked plans or Linear-backed slices.
6. Apply specialist skill steering only when a proven domain need improves the current stage output without reopening scope.
7. Apply interactive steering only when a consequential choice remains unresolved after source inspection; in headless/autonomous mode, record assumptions and blockers instead of asking.
8. When the stage wrote or updated files, apply `git-staging-contract.md` before
   handoff so current-turn artifacts are staged without sweeping unrelated
   dirty work.
9. Emit the lifecycle exit contract at handoff.

## Ownership

- `SKILL.md` owns the stage boundary and short numbered procedure.
- This contract owns repeated stage-context resolution.
- Stage references own durable detail.
- Validators and evals own proof that the context was not skipped.

Do not copy this contract into stage entrypoints. Link it, consume it, and keep stage procedures focused.
