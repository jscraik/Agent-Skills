# eval.harness.brownfield-harness-without-boundaries: Brownfield Harness Without Boundaries

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.brownfield-harness-without-boundaries.md

Knowledge claim: Principle under test: The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.
Behavior under test: Observable agent behavior when an team increases agent autonomy in a legacy code area with hidden invariants, unclear interfaces, no local docs, and weak lint or example coverage.
Failure mode: The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents.
Expected agent move: The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.
Skill lift before failure: The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents.
Skill lift after behavior: The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.
Observable delta: The response avoids the weak pattern (The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents) and instead shows the expected behavior (The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes).

Given: A team increases agent autonomy in a legacy code area with hidden invariants, unclear interfaces, no local docs, and weak lint or example coverage.
Should: The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.
Expected failure: The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents.

Bad answer patterns:
- The agent responds by adding more generic prompt text while leaving the brownfield code unreadable to agents.

Good answer patterns:
- The agent recommends boundary, documentation, lint, example, or grader work before scaling autonomous changes.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
