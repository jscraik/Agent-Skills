# eval.harness.done-without-validation: Done Without Validation Is Rejected

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.done-without-validation.md

Knowledge claim: Principle under test: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Behavior under test: Observable agent behavior when an agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Failure mode: The agent says done because implementation edits were made.
Expected agent move: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Skill lift before failure: The agent says done because implementation edits were made.
Skill lift after behavior: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Observable delta: The response avoids the weak pattern (The agent says done because implementation edits were made) and instead shows the expected behavior (The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure).

Given: An agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Should: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Expected failure: The agent says done because implementation edits were made.

Bad answer patterns:
- The agent says done because implementation edits were made.

Good answer patterns:
- The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
