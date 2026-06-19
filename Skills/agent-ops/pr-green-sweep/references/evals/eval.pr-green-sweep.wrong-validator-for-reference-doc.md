# eval.pr-green-sweep.wrong-validator-for-reference-doc: Wrong Validator For Reference Doc

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.wrong-validator-for-reference-doc.md

Knowledge claim: Validation must match the changed surface in PR closeout work.
Behavior under test: Path-aware validation selection before gates.
Failure mode: A generic validator is used for reference docs, generated manifests, and validation output.
Expected agent move: Choose skill audit for skill packages, link or markdown checks for references, generator checks for manifests, CI config validation for CI, and repo tests for source code.
Skill lift before failure: The agent validates the wrong surface and stages noise.
Skill lift after behavior: The agent selects path-owned validators and excludes unrelated outputs.
Observable delta: Validation decisions are reported before gate execution.

Given: A PR touches a skill entrypoint, a standalone reference document, a generated manifest, CI config, and validation output.
Should: The agent maps each path to the owning validation surface and keeps generated or validation-only outputs out of the source fix unless the repo contract owns them.
Expected failure: The agent runs a generic test or skill audit over all paths and stages generated evidence blindly.

Bad answer patterns:
- The agent runs only a generic test command.
- The agent stages generated validation output without ownership proof.

Good answer patterns:
- The agent classifies every changed path and names its verifier before running checks.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
