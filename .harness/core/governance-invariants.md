# Governance Invariants

Purpose: keep governance useful, compressed, and subordinate to execution truth.

## Proven Invariants

- Governance must reduce ambiguity.
- Every required check needs owner, proof target, failure action, and blocking status.
- CI/check ownership must be explicit.
- Compatibility paths need owner, reason, removal condition, and validation coverage.
- New default-visible skills require proof status.

## Strategic Assumptions

- More governance is not more trust.
- Governance breadth without proof semantics is false sophistication.
- A few high-signal gates beat many unclear checks.

## Operating Principles

- Add gates only when they catch real drift.
- Prefer generated ownership maps over provider lore.
- Keep Linear shape coarse: initiatives, projects, then next executable issues.
- Do not convert every review finding into a ticket.
- Process complexity is architectural debt.

## Forbidden Regressions

- Required checks without source contract.
- New governance checklists with no execution effect.
- Compatibility layers without expiry.
- Review rituals that do not improve routing, validation, or safety.
- Governance outranks live repo evidence.

## Evidence Basis

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `.harness/refactors/governance-compression.md`
