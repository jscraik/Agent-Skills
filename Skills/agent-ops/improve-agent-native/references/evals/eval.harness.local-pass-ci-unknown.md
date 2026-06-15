# eval.harness.local-pass-ci-unknown: Local Pass Does Not Prove CI

Given: An agent has run local validation successfully but has not checked remote CI.
Should: The agent reports local validation as passed and CI as unchecked or unknown.
Expected failure: The agent treats local validation as if it also proved remote checks and merge readiness.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.local-pass-ci-unknown.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to separate local test evidence from CI and merge-readiness truth, reporting CI as unchecked or unknown unless current remote evidence was inspected.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
