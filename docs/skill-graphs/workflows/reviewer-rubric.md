# Reviewer Rubric (Promotion Decisions)

Use this rubric to approve/reject lesson promotion candidates.

## Table of Contents

- [Scoring dimensions](#scoring-dimensions)
- [Hard fail conditions](#hard-fail-conditions)
- [Decision policy](#decision-policy)

## Scoring dimensions

Each dimension is scored `0-2`:

- `0`: fails expectation
- `1`: partially meets expectation
- `2`: clearly meets expectation

Dimensions:
1. **Impact evidence**: improvement is measurable and attributable.
2. **Non-regression**: critical criteria do not regress.
3. **Reusability**: lesson scope is clear and bounded.
4. **Operational safety**: no unsafe/ambiguous procedural guidance.
5. **Provenance completeness**: all required immutable metadata present.

## Hard fail conditions

Reject immediately if any are true:
- missing required provenance fields,
- unresolved security/privacy finding,
- contradictory lesson scope or lifecycle lineage,
- non-deterministic retrieval tie-break behavior.

## Decision policy

- Require total score `>=8/10` and no hard-fail flags.
- Require reviewer note with one sentence rationale.
- For rejected decisions, include a concrete remediation note.

Related:
- [Promotion gate workflow](/docs/skill-graphs/workflows/promotion-gate.md)
