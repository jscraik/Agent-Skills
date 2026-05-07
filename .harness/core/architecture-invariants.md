# Architecture Invariants

Purpose: preserve the irreducible architecture. Load this before changing structural boundaries.

## Proven Invariants

- `./bin/ask` is the public control-plane contract.
- Canonical sources are edited; generated/runtime projections are not source.
- Generated command handles are shallow pointers, never workflow logic.
- Runtime visible surface must stay budgeted.
- Source/projection/catalog parity is a trust boundary.
- `repo doctor` is the first repo-health truth surface.
- Completion claims require validation or closeout evidence.
- Large command modules are architectural risk, not strategic depth.

## Strategic Assumptions

- The repo is a proof-backed local control plane with a broader workbench around it.
- Breadth is exploration until evidence promotes it to trusted core.
- Local-first remains default until proof justifies portability adapters.

## Operating Principles

- Preserve public contracts; rewrite tactical internals boldly when they reduce coupling.
- Add service boundaries before adding feature logic to overgrown command modules.
- Prefer deep modules that make callers know less.
- Treat source/projection ambiguity as architecture drift.
- Treat hidden orchestration as a defect.

## Forbidden Regressions

- Runtime projections become de facto source.
- Handles contain duplicated workflow instructions.
- New command logic accumulates in already over-threshold modules.
- Catalog size becomes a quality claim.
- Structural audit is described as outcome proof.

## Evidence Basis

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `.harness/review/agent-skills-architecture-review.md`
