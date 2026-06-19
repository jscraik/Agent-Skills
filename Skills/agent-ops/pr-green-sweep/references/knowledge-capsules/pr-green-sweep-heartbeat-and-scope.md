# Heartbeat And Scope

Gate until-green rotation on a single Codex thread heartbeat and keep sweep scope explicit before PR discovery.

Pack id: pack.pr-green-sweep
Facet id: heartbeat_and_scope
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.codex.thread-automation-preserves-context: Thread Automation Preserves Context

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Codex thread automations are heartbeat-style recurring wake-ups attached to the current thread for scheduled work that should preserve conversation context.

Interpretation notes:
- This source supports the heartbeat mechanism, not the full PR closeout workflow.
- A durable automation prompt should include recurring action, report criteria, stop rule, and user-input boundary.

### claim.pr-green-sweep.heartbeat-gates-rotation: Heartbeat Gates Until-Green Rotation

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Until-green PR sweeps must create, reuse, update, or explicitly block on one heartbeat before rotating through PRs.

Interpretation notes:
- The heartbeat is a continuation contract, not a status decoration.
- A blocked heartbeat stops PR rotation before edits.

### claim.pr-green-sweep.current-state-is-live-lane-proof: Current State Is Live Lane Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

A PR sweep can act only from current live lane proof for PR URL, head SHA, review state, required checks, heartbeat state, dirty paths, and cleanup evidence.

Interpretation notes:
- Local validation does not prove remote merge readiness.
- Cleanup evidence is a separate lane from PR check evidence.

### claim.pr-green-sweep.authorization-rungs-are-separate: Authorization Rungs Are Separate

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Discovery, heartbeat, edits, push, CI rerun, merge, remote deletion, worktree deletion, and release are separate permission rungs.

Interpretation notes:
- Destructive cleanup and policy override require their own proof and approval.

### claim.pr-green-sweep.action-queue-precedes-edits: Action Queue Precedes Edits

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

The sweep must build an action queue before patching so every PR is classified by the next safe action or blocker.

Interpretation notes:
- Queue buckets prevent status-only reporting when the user asked for follow-through.

### claim.pr-green-sweep.single-mutation-lane: Single Mutation Lane

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Multi-PR sweeps should mutate only one PR at a time until that PR is pushed, validated, blocked, or cleanup-only.

Interpretation notes:
- Serial mutation protects dirty-worktree ownership and stale-check boundaries.

### claim.harness.review-needs-proof: Agent Work Needs Review Evidence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent-produced work should be accepted through review evidence, not through invisible trust in the trajectory.

Interpretation notes:
- This anchors readiness and evidence-boundary assets.

### claim.harness.provenance-not-validation: Provenance Does Not Prove Validation

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Session, transcript, telemetry, and provenance evidence can explain history or correlation, but cannot prove current tests, CI, runtime health, tracker state, or user acceptance without live proof.

Interpretation notes:
- This claim sharpens the existing evidence boundary lens.

### claim.harness.human-authority-boundaries: High-Impact Boundaries Need Human Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent autonomy still requires human or governance authority at high-impact boundaries such as release, security policy, identity, authorization, revocation, secrets, and compliance.

Interpretation notes:
- This claim prevents overgeneralizing post-merge review and zero-human-code patterns.

### claim.harness.full-job-verified-result: The Full Job Ends In A Verified Result

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

A useful agent should drive the change to a verified result, not stop after editing files.

Interpretation notes:
- This strengthens the Ryan-derived proof lane by making behavioral verification part of the job boundary.

### claim.harness.parallel-tokens-need-safety: Parallel Token Work Needs Safety

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

High token consumption becomes valuable only when harnessed through safe, aligned, productive parallel and asynchronous workflows.

Interpretation notes:
- This makes token volume a harness-readiness question rather than a raw usage target.

## Principles

### principle.pr-green-sweep.live-proof-before-motion: Live Proof Before Motion

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.pr-green-sweep.heartbeat-gates-rotation, claim.pr-green-sweep.current-state-is-live-lane-proof, claim.pr-green-sweep.authorization-rungs-are-separate

Move a PR sweep only from fresh live proof for the lane being changed.

Rationale: Until-green work crosses local code, review, CI, merge, heartbeat, and cleanup systems; stale proof in one lane does not authorize motion in another.

Application notes:
- Report heartbeat status before non-trivial sweep work.
- Refresh latest head SHA and required checks after every push.
- Stop at the authorization rung that has current approval and proof.

## Checklists

### checklist.pr-green-sweep.until-green-current-state: Until-Green Current State Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.codex.thread-automation-preserves-context, claim.pr-green-sweep.heartbeat-gates-rotation, claim.pr-green-sweep.current-state-is-live-lane-proof, claim.pr-green-sweep.action-queue-precedes-edits, claim.pr-green-sweep.single-mutation-lane

- [ ] Report heartbeat_status first for non-trivial until-green work.
- [ ] Use a thread automation when the sweep should preserve current thread context between wake-ups.
- [ ] Include the recurring action, report criteria, stop rule, and user-input boundary in the heartbeat prompt.
- [ ] Name the repo full name, active branch, and local status.
- [ ] Use the full GitHub PR URL for every actionable PR.
- [ ] Record the PR head branch and latest head SHA.
- [ ] Record merge state, branch protection, review decision, and unresolved review-thread state.
- [ ] Record required check names, statuses, target URLs, and stale-evidence markers.
- [ ] Classify dirty paths before staging, committing, pushing, merging, or pruning.
- [ ] Classify each PR into action queue buckets before patching.
- [ ] Keep one PR in the mutation lane until pushed, validated, blocked, or cleanup-only.

## Eval Scenarios

### eval.pr-green-sweep.rotation-without-heartbeat: Rotation Without Heartbeat

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.pr-green-sweep.heartbeat-gates-rotation

Knowledge claim: Until-green PR sweeps require a heartbeat gate before rotation.
Behavior under test: Heartbeat creation, reuse, update, or blocked reporting before PR mutation.
Failure mode: The agent starts PR rotation without a heartbeat status and stop rule.
Expected agent move: Report heartbeat_status first with a heartbeat id or blocker and stop before edits when heartbeat setup is blocked.
Skill lift target: The response starts with heartbeat_status before the action queue.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.rotation-without-heartbeat.md
Promotion status: candidate
Capsule refs: pr-green-sweep
Weak eval flags: none

Given: A user asks the agent to keep rotating through open PRs until they are green.
Should: The agent reports heartbeat_status first and creates, reuses, updates, or blocks on exactly one heartbeat before PR rotation.
Expected failure: The agent skips heartbeat handling and starts patching or summarizing PRs.
Reproduce with: references/evals/eval.pr-green-sweep.rotation-without-heartbeat.md
