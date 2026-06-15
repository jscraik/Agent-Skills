# eval.harness.slop-feedback-not-systematized: Slop Feedback Not Systematized

Given: Reviewers collect recurring slop patterns for a week, but the cleanup loop fixes only the current code and saves no next-run artifact.
Should: The agent identifies the missing systematization step and records a durable guardrail, artifact, or follow-up.
Expected failure: The agent treats cleanup as complete because the visible slop was removed once.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.slop-feedback-not-systematized.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to turn vague slop feedback into a durable mechanism, artifact, checklist, validator, or follow-up instead of another prose-only promise.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
