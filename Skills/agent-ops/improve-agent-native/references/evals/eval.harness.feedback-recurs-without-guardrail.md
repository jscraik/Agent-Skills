# eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture

Given: A reviewer repeats the same correction that appeared in an earlier agent task.
Should: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Expected failure: The agent applies another one-off fix without addressing recurrence.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.feedback-recurs-without-guardrail.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to classifies repeated steering as an operational failure and proposes or records the smallest durable guardrail, test, validator, instruction route, or bounded skip reason.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
