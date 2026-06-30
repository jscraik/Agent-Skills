# eval.harness.pr-lifecycle-stops-before-main: PR Lifecycle Stops Before Main

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.pr-lifecycle-stops-before-main.md

Knowledge claim: Principle under test: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Behavior under test: Observable agent behavior when an agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Failure mode: The agent treats PR creation as the final delivery state.
Expected agent move: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Skill lift before failure: The agent treats PR creation as the final delivery state.
Skill lift after behavior: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Observable delta: The response avoids the weak pattern (The agent treats PR creation as the final delivery state) and instead shows the expected behavior (The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker).

Given: An agent opens a PR and reports done while CI, review, branch drift, merge queue, and landing state remain unchecked.
Should: The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.
Expected failure: The agent treats PR creation as the final delivery state.

Bad answer patterns:
- The agent treats PR creation as the final delivery state.

Good answer patterns:
- The agent identifies the missing lifecycle steps and either continues the loop or reports a precise blocker.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
