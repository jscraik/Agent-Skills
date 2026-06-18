# Deep Module Symptom Map

Identify whether a proposed module hides real coordination complexity or only adds indirection and vocabulary.

Pack id: pack.codebase-architecture
Facet id: deep_module_symptom_map
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.deep-modules-hide-coordination: Deep Modules Hide Coordination

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A module is architecturally valuable when its interface is simpler than its implementation and when it reduces caller knowledge, coordination burden, and change amplification.

Interpretation notes:
- This claim supports rejecting shallow wrappers that do not hide behavior.
- It should be tested against caller simplification, not directory layout alone.

## Lenses

### lens.arch.deep-module-symptom-map: Deep Module Symptom Map

- Type: lens
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.deep-modules-hide-coordination

- Name the complexity symptom before proposing structure.
- Treat caller knowledge as evidence: hidden ordering, repeated setup, duplicated validation, or implementation facts in tests and docs are boundary smells.
- A deeper module should reduce what callers need to know, not merely move code to a new file.
- Prefer moving coordination behind the owner that already has the evidence and validation contract.
- Reject abstractions that add indirection without stable variation or hidden complexity.
