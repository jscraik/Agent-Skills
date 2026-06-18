# Data Ownership And Consistency

Separate source of truth, derived data, consistency expectations, recovery paths, and production-visible failure signals.

Pack id: pack.codebase-architecture
Facet id: data_ownership_and_consistency
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.data-ownership-needs-consistency-contract: Data Ownership Needs Consistency Contract

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Persistence, cache, queue, snapshot, and index designs need an explicit system of record, consistency expectation, replay or backfill path, and production-visible failure signal.

Interpretation notes:
- This claim supports a data-intensive capsule for architecture surfaces with state.
- It should distinguish source of truth from derived or stale views.

## Rubrics

### rubric.arch.data-ownership-and-consistency: Data Ownership And Consistency Rubric

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.data-ownership-needs-consistency-contract

- source-of-truth: Is the system of record distinct from caches, indexes, snapshots, and exports?
  - pass: The review names authoritative and derived data stores plus the owner of each.
  - fail: A cache, projection, or generated artifact can be mistaken for the source of truth.
- consistency-expectation: Are staleness, ordering, replay, and partial failure consequences explicit?
  - pass: The design states accepted consistency behavior and user-visible or operator-visible consequences.
  - fail: The design uses vague consistency language without failure consequences.
- migration-and-recovery: Is there a backfill, replay, rollback, or quarantine path for bad or partial data?
  - pass: The review names the recovery mechanism and a stop condition.
  - fail: The design assumes perfect data shape or one-shot migration success.
- observability: Can operators observe the boundary when it fails in production-like conditions?
  - pass: The design exposes classified failures, counts, traces, or durable receipts.
  - fail: The only proof is a local pass or hidden log line.

## Eval Scenarios

### eval.arch.cache-treated-as-source-of-truth: Cache Treated As Source Of Truth

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.data-ownership-needs-consistency-contract

Knowledge claim: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Behavior under test: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Failure mode: The reviewer accepts the faster read path as the architecture boundary without identifying source-of-truth or recovery semantics.
Expected agent move: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Skill lift target: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.cache-treated-as-source-of-truth.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A design review finds a cache, generated export, or indexed projection that callers use as if it were authoritative, while the real source of truth and replay path are unclear.
Should: The reviewer separates authoritative and derived data, names consistency and staleness expectations, and asks for recovery or backfill proof.
Expected failure: The reviewer accepts the faster read path as the architecture boundary without identifying source-of-truth or recovery semantics.
Reproduce with: references/evals/eval.arch.cache-treated-as-source-of-truth.md
