# eval.skills.library-maintenance-required: Library Maintenance Required

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.library-maintenance-required.md

Knowledge claim: Skill libraries need library-time maintenance because individual task success does not prove ecosystem health.
Behavior under test: The Skills SDK gate requires library-level health evidence before SDK readiness claims.
Failure mode: Task-time repair success is treated as library readiness.
Expected agent move: Request contract catalog, graph or dependency view, utility/compatibility/risk/validation checks, shared-asset coherence, and routing-quality evidence.
Skill lift before failure: The Skills SDK equates individual task repairs with library health.
Skill lift after behavior: The Skills SDK requires library-time health checks and routing evidence.
Observable delta: The answer names contract, graph, utility, compatibility, risk, validation, shared-asset, and routing evidence.

Given: A skill library grows after several successful task-time fixes, but there is no library-level contract catalog, dependency or shared-asset check, utility/compatibility/risk/validation report, or routing-quality check as the library size increases.
Should: The agent classifies this as skill technical debt risk and asks for library-time maintenance evidence before treating the library as SDK-ready.
Expected failure: The agent treats successful individual task repairs as proof that the library is healthy.

Bad answer patterns:
- The agent says the library is healthy because recent tasks passed.
- The agent ignores routing quality as the library size grows.

Good answer patterns:
- The agent asks for library-level maintenance and routing evidence.
- The agent separates task-time repair proof from ecosystem health proof.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
