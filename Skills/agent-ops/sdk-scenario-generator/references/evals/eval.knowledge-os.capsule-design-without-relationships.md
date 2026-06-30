# eval.knowledge-os.capsule-design-without-relationships: Capsule Design Requires Relationships And Evals

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.capsule-design-without-relationships.md

Knowledge claim: Capsule design references must include relationship and eval surfaces, not only prose guidance.
Behavior under test: Observable KnowledgeOS validator behavior when a capsule-design artifact omits relationship mapping and eval coverage.
Failure mode: The validator accepts a polished but behavior-weak capsule-design reference.
Expected agent move: The validator rejects the capsule and points to the missing capsule-design sections.
Skill lift before failure: The validator accepts a readable but behavior-weak capsule-design reference.
Skill lift after behavior: The validator rejects capsule-design references that lack relationship and eval surfaces.
Observable delta: The negative fixture is rejected by the repo validator.

Given: A knowledge capsule design reference includes general guidance and ordinary operational headings but omits source model, relationship map, downstream integration, failure modes, and eval scenarios.
Should: The validator rejects the reference with capsule-design-missing-sections before the capsule can be treated as a portable handoff.
Expected failure: The handoff passes because it is readable and has generic headings, even though it cannot improve downstream skill or Jamie Brain behavior deterministically.

Bad answer patterns:
- The validator accepts the capsule because ordinary operational headings are present.

Good answer patterns:
- The validator rejects the capsule with capsule-design-missing-sections.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
