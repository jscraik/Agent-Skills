# eval.arch.cache-treated-as-source-of-truth: Cache Treated As Source Of Truth

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.cache-treated-as-source-of-truth.md

Knowledge claim: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Behavior under test: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Failure mode: The reviewer accepts the faster read path as the architecture boundary without identifying source-of-truth or recovery semantics.
Expected agent move: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Skill lift before failure: The reviewer accepts the faster read path as the architecture boundary without identifying source-of-truth or recovery semantics.
Skill lift after behavior: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Observable delta: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.

Given: A design review finds a cache, generated export, or indexed projection that callers use as if it were authoritative, while the real source of truth and replay path are unclear.
Should: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Expected failure: The reviewer accepts the faster read path as the architecture boundary without identifying source-of-truth or recovery semantics.

Bad answer patterns:
- The reviewer accepts the faster read path as the architecture boundary without identifying source-of-truth or recovery semantics.

Good answer patterns:
- The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
