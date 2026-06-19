# Action Queue

Classify PRs into next-action buckets before edits and keep one PR in the mutation lane at a time.

Pack id: pack.pr-green-sweep
Facet id: action_queue
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

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

### claim.harness.pr-lifecycle-skill: PR Lifecycle Can Be A Skill

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

The PR lifecycle can be encoded as a skill that keeps working through review, CI, flakes, updates, merge queue, and landing in main.

Interpretation notes:
- This claim concretizes the existing full-job-or-not-done principle for PR operations.

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

### claim.harness.lifecycle-exit-proof: Exit Needs Status And Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

A lifecycle stage should not claim done without validation evidence or a concrete reason validation is not applicable.

Interpretation notes:
- This claim supports closure-grade output rules.

## Principles

### principle.harness.pr-lifecycle-is-skillable-loop: PR Lifecycle Is A Skillable Loop

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Treat PR delivery as a closed loop that can be skillified through landing in main.

Rationale: The work is not complete when the diff exists; agents need a durable loop for review, CI, repair, updates, queueing, and final landing.

Application notes:
- Define the skill exit state as landed or explicitly blocked.
- Separate local validation from remote CI and review truth.
- Keep looping through flakes and branch drift until the contract says stop.

## Heuristics

### heuristic.pr-green-sweep.queue-before-patching: Queue Before Patching

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.pr-green-sweep.action-queue-precedes-edits, claim.pr-green-sweep.single-mutation-lane

Build URL-first PR cards and queue buckets before editing, then mutate only the active PR until it is pushed, blocked, validated, or cleanup-only.

Use when:
- The user asks for open PRs to be made green or merged.
- Multiple PRs or dirty paths could be mixed in one working tree.

Avoid when:
- The user asks only for a read-only summary.
- A single local test failure has no PR, review, CI, or cleanup context.

### heuristic.harness.skillify-pr-lifecycle: Skillify PR Lifecycle

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Encode PR delivery as a loop that checks review, CI, branch drift, flakes, merge queue, and landing state.

Use when:
- Agents repeatedly stop after opening or updating a PR.
- The repo has a known remote review and CI path.

Avoid when:
- The work intentionally stops at a local patch or draft artifact.
- Credentials or policy prevent the agent from observing the remote lifecycle.

## Eval Scenarios

### eval.pr-green-sweep.status-summary-without-queue: Status Summary Without Queue

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.pr-green-sweep.action-queue-precedes-edits

Knowledge claim: PR green sweeps own an action queue rather than status-only reporting.
Behavior under test: Queue construction before PR mutation.
Failure mode: Status-only reporting with no next safe action per PR.
Expected agent move: Classify PRs into auto_fixable_now, needs_merge_conflict_strategy, blocked_policy_or_approval, blocked_external_ci, needs_user_decision, and cleanup_only as evidence allows.
Skill lift target: The response contains queue buckets before fix proposals.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.status-summary-without-queue.md
Promotion status: candidate
Capsule refs: pr-green-sweep
Weak eval flags: none

Given: A user asks for a sweep of open PRs and wants to know which PRs can be fixed, which are blocked by CI, and which need a decision.
Should: The agent builds URL-first PR cards and action queue buckets before proposing edits.
Expected failure: The agent gives an interesting read-only summary without auto-fixable, blocked, decision, or cleanup buckets.
Reproduce with: references/evals/eval.pr-green-sweep.status-summary-without-queue.md

### eval.harness.pr-lifecycle-stops-before-main: PR Lifecycle Stops Before Main

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.pr-lifecycle-skill, claim.harness.full-job-verified-result

Knowledge claim: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Behavior under test: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Failure mode: The agent treats PR creation as the final delivery state.
Expected agent move: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Skill lift target: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.pr-lifecycle-stops-before-main.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: An agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Should: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Expected failure: The agent treats PR creation as the final delivery state.
Reproduce with: references/evals/eval.harness.pr-lifecycle-stops-before-main.md
