# eval.harness.brownfield-harness-without-boundaries: Brownfield Harness Without Boundaries

Given: A team increases agent autonomy in a legacy code area with hidden invariants, unclear interfaces, no local docs, and weak lint or example coverage.
Should: The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.
Expected failure: The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.brownfield-harness-without-boundaries.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to recommend boundary, documentation, lint, example, or grader work before increasing autonomous change scope in a brownfield repo.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
