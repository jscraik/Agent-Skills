# eval.pr-green-sweep.status-summary-without-queue: Status Summary Without Queue

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.status-summary-without-queue.md

Knowledge claim: PR green sweeps own an action queue rather than status-only reporting.
Behavior under test: Queue construction before PR mutation.
Failure mode: Status-only reporting with no next safe action per PR.
Expected agent move: Classify PRs into auto_fixable_now, needs_merge_conflict_strategy, blocked_policy_or_approval, blocked_external_ci, needs_user_decision, and cleanup_only as evidence allows.
Skill lift before failure: The agent lists PR states without a next action.
Skill lift after behavior: The agent classifies every actionable PR into a queue bucket.
Observable delta: The response contains queue buckets before fix proposals.

Given: A user asks for a sweep of open PRs and wants to know which PRs can be fixed, which are blocked by CI, and which need a decision.
Should: The agent builds URL-first PR cards and action queue buckets before proposing edits.
Expected failure: The agent gives an interesting read-only summary without auto-fixable, blocked, decision, or cleanup buckets.

Bad answer patterns:
- The agent only summarizes PR status.
- The agent proposes edits before queueing and dirty-path classification.

Good answer patterns:
- The agent builds URL-first PR cards and queue buckets before patching.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
