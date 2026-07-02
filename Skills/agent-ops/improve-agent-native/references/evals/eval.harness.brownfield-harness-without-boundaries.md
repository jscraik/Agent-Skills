# eval.harness.brownfield-harness-without-boundaries: Brownfield Harness Without Boundaries

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.brownfield-harness-without-boundaries.md

Knowledge claim: Principle under test: The package requires boundary, documentation, lint, example, or evaluation work before scaling autonomous changes.
Behavior under test: Package guidance for a team increasing autonomy in a legacy code area with hidden invariants, unclear interfaces, no local docs, and weak lint or example coverage.
Failure mode: The package permits generic prompt text while leaving the brownfield code unreadable to operators.
Expected package behavior: Require boundary, documentation, lint, example, or evaluation work before scaling autonomous changes.
Skill lift before failure: Generic prompt text is treated as enough while brownfield code remains unreadable to operators.
Skill lift after behavior: The package requires boundary, documentation, lint, example, or evaluation work before scaling autonomous changes.
Observable delta: The package avoids the weak pattern and requires boundary, documentation, lint, example, or evaluation work before scaling autonomous changes.

Given: A team increases agent autonomy in a legacy code area with hidden invariants, unclear interfaces, no local docs, and weak lint or example coverage.
Should: Require boundary, documentation, lint, example, or evaluation work before scaling autonomous changes.
Expected failure: The package permits generic prompt text while leaving the brownfield code unreadable to operators.

Bad answer patterns:
- Generic prompt text is treated as enough while brownfield code remains unreadable to operators.

Good answer patterns:
- The package requires boundary, documentation, lint, example, or evaluation work before scaling autonomous changes.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
