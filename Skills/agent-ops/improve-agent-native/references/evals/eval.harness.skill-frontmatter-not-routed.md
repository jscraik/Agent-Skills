# eval.harness.skill-frontmatter-not-routed: Skill Frontmatter Not Routed

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.skill-frontmatter-not-routed.md

Knowledge claim: Principle under test: The agent treats the short description and trigger surface as the first thing to test and repair.
Behavior under test: Observable agent behavior when an detailed skill contains correct instructions, but cold agents often do not select it for the tasks it is meant to govern.
Failure mode: The agent keeps adding detail to the skill body even though routing is the failing layer.
Expected agent move: The agent treats the short description and trigger surface as the first thing to test and repair.
Skill lift before failure: The agent keeps adding detail to the skill body even though routing is the failing layer.
Skill lift after behavior: The agent treats the short description and trigger surface as the first thing to test and repair.
Observable delta: The response avoids the weak pattern (The agent keeps adding detail to the skill body even though routing is the failing layer) and instead shows the expected behavior (The agent treats the short description and trigger surface as the first thing to test and repair).

Given: A detailed skill contains correct instructions, but cold agents often do not select it for the tasks it is meant to govern.
Should: The agent treats the short description and trigger surface as the first thing to test and repair.
Expected failure: The agent keeps adding detail to the skill body even though routing is the failing layer.

Bad answer patterns:
- The agent keeps adding detail to the skill body even though routing is the failing layer.

Good answer patterns:
- The agent treats the short description and trigger surface as the first thing to test and repair.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
