# eval.harness.slop-feedback-not-systematized: Slop Feedback Not Systematized

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.slop-feedback-not-systematized.md

Knowledge claim: Principle under test: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Behavior under test: Observable agent behavior when reviewers collect recurring slop patterns for a week, but the cleanup loop fixes only the current code and saves no next-run artifact.
Failure mode: The agent treats cleanup as complete because the visible slop was removed once.
Expected agent move: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Skill lift before failure: The agent treats cleanup as complete because the visible slop was removed once.
Skill lift after behavior: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Observable delta: The response avoids the weak pattern (The agent treats cleanup as complete because the visible slop was removed once) and instead shows the expected behavior (The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up).

Given: Reviewers collect recurring slop patterns for a week, but the cleanup loop fixes only the current code and saves no next-run artifact.
Should: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Expected failure: The agent treats cleanup as complete because the visible slop was removed once.

Bad answer patterns:
- The agent treats cleanup as complete because the visible slop was removed once.

Good answer patterns:
- The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
