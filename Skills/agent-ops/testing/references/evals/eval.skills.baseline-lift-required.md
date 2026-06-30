# eval.skills.baseline-lift-required: Baseline Lift Required

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.baseline-lift-required.md

Knowledge claim: Skill readiness requires behavioral lift evidence in addition to structural conformance.
Behavior under test: The Skills SDK gate refuses to claim skill readiness without baseline lift evidence.
Failure mode: Structural validation is accepted as behavioral proof.
Expected agent move: Block readiness, name the missing baseline proof fields, and preserve conformance as a separate evidence lane.
Skill lift before failure: The Skills SDK accepts structural conformance as behavior proof.
Skill lift after behavior: The Skills SDK requires baseline lift fields before readiness.
Observable delta: The answer names missing baseline, absolute delta, normalized gain, denominator, and negative-delta evidence.

Given: A proposed Skills SDK gate says a skill is ready because it validates structurally and has a high conformance score, but the receipt has no no-skill baseline, prior-skill baseline, absolute delta, normalized gain, or task denominator.
Should: The agent blocks the readiness claim, separates conformance from behavior proof, and asks for a baseline lift receipt with absolute and normalized movement plus negative-delta reporting.
Expected failure: The agent treats a valid SKILL.md file or registry conformance score as proof that the skill improves behavior.

Bad answer patterns:
- The agent says the skill is ready because the file validates.
- The agent reports normalized gain without baseline pass rate or absolute delta.

Good answer patterns:
- The agent blocks readiness and requests no-skill or prior-skill baseline evidence.
- The agent reports conformance and lift as separate lanes.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
