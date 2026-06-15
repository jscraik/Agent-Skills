# eval.harness.done-without-validation: Done Without Validation Is Rejected

Given: An agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Should: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Expected failure: The agent says done because implementation edits were made.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.done-without-validation.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to rejects closure when validation is absent, names the missing proof lane, and gives the next validation command or explicit blocker before claiming done.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
