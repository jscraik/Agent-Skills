# eval.skills.description-routing-not-conformance: Description Routing Not Conformance

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.description-routing-not-conformance.md

Knowledge claim: Format conformance is not semantic routing quality.
Behavior under test: The Skills SDK gate separates description conformance from trigger reliability.
Failure mode: Description length and parseability are accepted as routing proof.
Expected agent move: Keep conformance green, mark routing quality unproven, and request trigger/non-trigger selection evidence.
Skill lift before failure: The Skills SDK treats conformance as routing proof.
Skill lift after behavior: The Skills SDK requires trigger and non-trigger routing evidence.
Observable delta: The answer names conformance, semantic routing, and selection evidence as separate lanes.

Given: A skill package passes frontmatter validation and description-length checks, but cold agents still select it for unrelated tasks and miss it for its intended task because the description uses broad generic language.
Should: The agent classifies conformance as passed but routing quality as unproven, then asks for trigger/non-trigger examples or selection evidence before readiness.
Expected failure: The agent treats valid frontmatter and a long description as proof that the skill routes correctly.

Bad answer patterns:
- The agent says the skill routes well because frontmatter is valid.
- The agent rewards description length as primary proof.

Good answer patterns:
- The agent requests positive and negative routing examples.
- The agent keeps format conformance separate from semantic trigger quality.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
