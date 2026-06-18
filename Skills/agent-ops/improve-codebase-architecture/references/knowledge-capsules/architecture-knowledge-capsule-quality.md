# Knowledge Capsule Quality

Keep book-backed skill capsules source-bound, bounded, and lifecycle-honest instead of turning useful advice into unaudited runtime authority.

Pack id: pack.codebase-architecture
Facet id: knowledge_capsule_quality
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.capsules-need-lineage: Capsules Need Lineage

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill-local knowledge capsules should preserve source context, claim lineage, bounded use, and observable justification rather than exporting polished advice alone.

Interpretation notes:
- This claim keeps package capsules source-bound without depending on another pack's normalized claims.
- It supports evals that reject book-inspired capsule text without claim lineage.

### claim.arch.export-proof-is-not-lifecycle-proof: Export Proof Is Not Lifecycle Proof

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A successful export or smoke test is outcome evidence for artifact structure, not proof that the source knowledge, review process, lifecycle state, or downstream runtime adoption is valid.

Interpretation notes:
- This claim supports package closeouts that separate export structure from knowledge lifecycle proof.
- It should prevent draft capsules from being described as validated just because they export cleanly.

## Eval Scenarios

### eval.arch.capsule-without-claim-lineage: Capsule Without Claim Lineage

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.capsules-need-lineage

Knowledge claim: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Behavior under test: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Failure mode: The reviewer accepts the capsule because the advice sounds useful and the source book exists in the repo.
Expected agent move: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Skill lift target: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.capsule-without-claim-lineage.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A skill package vendors a book-inspired capsule that contains polished advice but no source_refs, derived_from_claims, asset ids, or load_when boundary.
Should: The reviewer blocks promotion, asks for source-bound claim lineage and a bounded skill-local capsule, and avoids treating the capsule as runtime instruction authority.
Expected failure: The reviewer accepts the capsule because the advice sounds useful and the source book exists in the repo.
Reproduce with: references/evals/eval.arch.capsule-without-claim-lineage.md

### eval.arch.pack-export-overclaims-lifecycle: Pack Export Overclaims Lifecycle

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.export-proof-is-not-lifecycle-proof

Knowledge claim: The reviewer separates export structure proof from lifecycle review, validation evidence, runtime availability, and downstream skill adoption.
Behavior under test: The reviewer separates export structure proof from lifecycle review, validation evidence, runtime availability, and downstream skill adoption.
Failure mode: The reviewer treats generated export files as proof that the new knowledge is reviewed, validated, and installed in the target skill.
Expected agent move: The reviewer separates export structure proof from lifecycle review, validation evidence, runtime availability, and downstream skill adoption.
Skill lift target: The reviewer separates export structure proof from lifecycle review, validation evidence, runtime availability, and downstream skill adoption.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.pack-export-overclaims-lifecycle.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A pack export and smoke test pass for draft capsules, and the closeout says the knowledge is validated or ready for runtime use.
Should: The reviewer separates export structure proof from lifecycle review, validation evidence, runtime availability, and downstream skill adoption.
Expected failure: The reviewer treats generated export files as proof that the new knowledge is reviewed, validated, and installed in the target skill.
Reproduce with: references/evals/eval.arch.pack-export-overclaims-lifecycle.md
