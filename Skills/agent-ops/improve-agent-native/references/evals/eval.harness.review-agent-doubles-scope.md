# eval.harness.review-agent-doubles-scope: Review Agent Doubles Scope

Given: A reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Should: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Expected failure: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.review-agent-doubles-scope.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to separate current blocking defects from backlog or scope-expanding review comments, preserving the original delivery boundary while naming deferred follow-up explicitly.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
