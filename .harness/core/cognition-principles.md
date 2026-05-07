# Cognition Principles

Purpose: protect future-agent reasoning quality and reduce context load.

## Proven Invariants

- Repository cognition is part of the product.
- Current truth must be easier to find than historical evidence.
- Abstractions must reduce reasoning cost.
- Docs that repeat command output should be generated or validated.
- Raw artifact volume is not knowledge.

## Strategic Assumptions

- Fresh agents should operate from a small command path, not broad docs.
- Context cost is an architecture cost.
- The best control-plane interface makes agents know less.

## Operating Principles

- Optimize for local reasoning.
- Keep first-contact paths short.
- Replace repeated prose with command output or validators.
- Quarantine raw history behind indexes.
- Keep stale/generated/runtime surfaces out of primary browsing paths.
- Name proof, source, runtime, projection, and fixture roles explicitly.

## Forbidden Regressions

- Historical artifacts compete with current operating contracts.
- Docs become the only way to discover execution truth.
- Agents must inspect giant files for small behavior.
- Generated/runtime files look editable.
- Broad skill browsing replaces routed recommendation.

## Evidence Basis

- `.harness/features/*.md`
- `.harness/strategy/agent-skills-strategy.md`
- `.harness/refactors/repository-cognition-burndown.md`
