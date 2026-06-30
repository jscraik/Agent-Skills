# eval.ryan.stakeholder-synthesis: Stakeholder Update Synthesizes Raw Activity

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.stakeholder-synthesis.md

Knowledge claim: Principle under test: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Behavior under test: Observable agent behavior when an agent has a long log of commits, tests, and review notes and must brief a cross-functional stakeholder.
Failure mode: The agent dumps raw activity or validation output without explaining why it matters to the audience.
Expected agent move: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Skill lift before failure: The agent dumps raw activity or validation output without explaining why it matters to the audience.
Skill lift after behavior: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Observable delta: The response avoids the weak pattern (The agent dumps raw activity or validation output without explaining why it matters to the audience) and instead shows the expected behavior (The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary).

Given: An agent has a long log of commits, tests, and review notes and must brief a cross-functional stakeholder.
Should: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Expected failure: The agent dumps raw activity or validation output without explaining why it matters to the audience.

Bad answer patterns:
- The agent dumps raw activity or validation output without explaining why it matters to the audience.

Good answer patterns:
- The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
