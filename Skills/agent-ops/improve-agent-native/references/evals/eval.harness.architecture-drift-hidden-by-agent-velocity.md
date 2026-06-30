# eval.harness.architecture-drift-hidden-by-agent-velocity: Architecture Drift Hidden By Agent Velocity

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.architecture-drift-hidden-by-agent-velocity.md

Knowledge claim: Principle under test: The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.
Behavior under test: Observable agent behavior when an team ships many agent-authored changes and discovers that core architectural patterns changed without shared human understanding.
Failure mode: The agent proposes only more line-level review or more automated tests.
Expected agent move: The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.
Skill lift before failure: The agent proposes only more line-level review or more automated tests.
Skill lift after behavior: The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.
Observable delta: The response avoids the weak pattern (The agent proposes only more line-level review or more automated tests) and instead shows the expected behavior (The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update).

Given: A team ships many agent-authored changes and discovers that core architectural patterns changed without shared human understanding.
Should: The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.
Expected failure: The agent proposes only more line-level review or more automated tests.

Bad answer patterns:
- The agent proposes only more line-level review or more automated tests.

Good answer patterns:
- The agent recommends a synchronous architecture alignment loop plus a durable ADR or spec update.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
