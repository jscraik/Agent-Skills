# eval.harness.context-dump-instead-of-slice: Context Dump Instead Of Slice

Given: A task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Should: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Expected failure: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.context-dump-instead-of-slice.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to use the narrow rule locator, clause ID, or directly relevant reference first and avoids dumping broad unrelated context before the task requires it.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
