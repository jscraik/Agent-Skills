# Legacy Seam Characterization

Characterize behavior and create a narrow seam before moving ownership, changing structure, or extracting abstractions in legacy code.

Pack id: pack.codebase-architecture
Facet id: legacy_seam_characterization
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.legacy-change-starts-with-characterization: Legacy Change Starts With Characterization

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Legacy architecture work should characterize current behavior and create a narrow seam before moving ownership, changing structure, or extracting abstractions.

Interpretation notes:
- This claim supports recommending discovery or tests before redesign when proof is thin.
- It keeps the first move reversible under uncertainty.

## Heuristics

### heuristic.arch.legacy-seam-characterization: Legacy Seam Characterization Heuristic

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.legacy-change-starts-with-characterization

When behavior is poorly characterized, recommend a seam and a narrow characterization check before moving ownership or introducing a new abstraction.

Use when:
- A module has hidden invariants, weak tests, surprising callers, or unclear public behavior.
- The desired architecture change would move responsibilities before current behavior is reproducible.
- The safest first move is discovery, characterization, or a small mechanical refactor.

Avoid when:
- The boundary already has strong contract tests and stable caller evidence.
- The requested change is a local bug fix with no structural effect.
- A seam would add indirection without making behavior easier to verify.
