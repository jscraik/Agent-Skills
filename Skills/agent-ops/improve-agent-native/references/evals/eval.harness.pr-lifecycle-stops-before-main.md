# eval.harness.pr-lifecycle-stops-before-main: PR Lifecycle Stops Before Main

Given: An agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Should: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Expected failure: The agent treats PR creation as the final delivery state.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.pr-lifecycle-stops-before-main.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to identify unclosed PR lifecycle steps, such as review, checks, merge, checkout main, and pull, and either continues or reports the precise blocker.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
