# eval.harness.architecture-drift-hidden-by-agent-velocity: Architecture Drift Hidden By Agent Velocity

Given: A team ships many agent-authored changes and discovers that core architectural patterns changed without shared human understanding.
Should: The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.
Expected failure: The agent proposes only more line-level review or more automated tests.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.architecture-drift-hidden-by-agent-velocity.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to names architecture drift risk and recommends a synchronous alignment loop plus durable ADR/spec update before celebrating agent throughput.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
