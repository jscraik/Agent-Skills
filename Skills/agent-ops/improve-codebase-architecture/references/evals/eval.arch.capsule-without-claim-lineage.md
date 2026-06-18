# eval.arch.capsule-without-claim-lineage: Capsule Without Claim Lineage

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.capsule-without-claim-lineage.md

Knowledge claim: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Behavior under test: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Failure mode: The reviewer accepts the capsule because the advice sounds useful and the source book exists in the repo.
Expected agent move: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Skill lift before failure: The reviewer accepts the capsule because the advice sounds useful and the source book exists in the repo.
Skill lift after behavior: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Observable delta: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.

Given: A skill package vendors a book-inspired capsule that contains polished advice but no source_refs, derived_from_claims, asset ids, or load_when boundary.
Should: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Expected failure: The reviewer accepts the capsule because the advice sounds useful and the source book exists in the repo.

Bad answer patterns:
- The reviewer accepts the capsule because the advice sounds useful and the source book exists in the repo.

Good answer patterns:
- The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
