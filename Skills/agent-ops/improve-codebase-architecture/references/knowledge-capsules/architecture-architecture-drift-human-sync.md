# Architecture Drift Human Sync

Stop treating passing tests as sufficient when agent-authored changes alter ownership, vocabulary, dependency direction, or shared mental models.

Pack id: pack.codebase-architecture
Facet id: architecture_drift_human_sync
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.drift-needs-human-sync: Drift Needs Human Sync

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Architecture drift becomes a coordination problem when boundaries, ownership, or mental models change faster than the humans and agents sharing the codebase can realign.

Interpretation notes:
- This claim supports pausing patch work for synchronous alignment when structural drift changes shared understanding.
- It should be used when architecture drift crosses owner, team, or runtime boundaries.

## Eval Scenarios

### eval.arch.architecture-drift-human-sync: Architecture Drift Human Sync

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.drift-needs-human-sync

Knowledge claim: The architecture reviewer classifies local tests as insufficient, recommends a human architecture alignment decision plus a durable ADR or spec update, and names the tracer proof needed before further autonomous edits.
Behavior under test: The architecture reviewer classifies local tests as insufficient, recommends a human architecture alignment decision plus a durable ADR or spec update, and names the tracer proof needed before further autonomous edits.
Failure mode: The reviewer treats passing tests as proof the architecture is safe and recommends continuing with line-level cleanup only.
Expected agent move: The architecture reviewer classifies local tests as insufficient, recommends a human architecture alignment decision plus a durable ADR or spec update, and names the tracer proof needed before further autonomous edits.
Skill lift target: The architecture reviewer classifies local tests as insufficient, recommends a human architecture alignment decision plus a durable ADR or spec update, and names the tracer proof needed before further autonomous edits.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.architecture-drift-human-sync.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: Agent-authored patches have changed module ownership, vocabulary, and dependency direction across several files, while tests still pass and no human decision record explains the new shape.
Should: The architecture reviewer classifies local tests as insufficient, recommends a human architecture alignment decision plus a durable ADR or spec update, and names the tracer proof needed before further autonomous edits.
Expected failure: The reviewer treats passing tests as proof the architecture is safe and recommends continuing with line-level cleanup only.
Reproduce with: references/evals/eval.arch.architecture-drift-human-sync.md
