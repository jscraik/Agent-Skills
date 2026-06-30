# eval.skills.task-completion-not-quality: Task Completion Not Quality

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.task-completion-not-quality.md

Knowledge claim: Task completion does not prove reusable, composable, or maintainable skill quality.
Behavior under test: The Skills SDK gate keeps task pass evidence separate from ecosystem-quality evidence.
Failure mode: A one-task pass is overclaimed as broad skill quality.
Expected agent move: Report local task proof, block reusable-quality claims, and request cross-task, composition, and drift evidence.
Skill lift before failure: The Skills SDK overclaims one task pass as broad skill quality.
Skill lift after behavior: The Skills SDK separates task pass proof from reusable quality claims.
Observable delta: The answer names local behavior proof and blocks broader quality claims pending additional evidence.

Given: A skill passes one verifier-backed task, and the report claims the skill is reusable and maintainable without any cross-task reuse, composition, or environment-change evidence.
Should: The agent accepts the task pass as local behavior evidence but refuses broader skill-quality claims until reusability, composability, and maintainability evidence exists.
Expected failure: The agent turns a single task-completion pass into reusable skill-quality proof.

Bad answer patterns:
- The agent says one task pass proves the skill is reusable.
- The agent does not ask for composition or maintainability evidence.

Good answer patterns:
- The agent accepts the local pass only within its narrow proof lane.
- The agent asks for reusability, composability, and maintainability evidence.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
