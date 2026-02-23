---
date: 2026-02-23
topic: skill-graph-recursive-loop-parity-pass
---

# Skill Knowledge Graph Recursive Loop (Implementation-Complete Parity Pass)

## What We're Building
We will close the implementation gap between the documented recursive skill-learning system and its executable behavior by making the loop production-like for v1. The change focuses on making canonical lesson lifecycle and governance controls real: persist canonical lesson outcomes, emit required daily operational telemetry, enforce run ownership/idempotency, and implement true adversarial review behavior instead of metadata-only markers.

## Why This Approach
We selected **Approach A (parity-first, minimal blast radius)** because the core value of the feature depends on trust in runtime outputs. Without durable canonical state and governance controls, downstream tools (human promotion, promotion queues, telemetry-driven decisions) cannot be reliably consumed. A focused integration pass minimizes conceptual drift while avoiding a large platform rewrite.

## Key Decisions
- **Scope-first parity:** implement the documented-but-missing runtime primitives first (`canonical lesson graph`, `daily telemetry`, `judge mode`, `review governance`, `run-state guardrails`) before adding new capabilities.
- **Store behavior in repo-first files:** persist canonical lessons and governance state in structured local artifacts colocated with existing run outputs to keep the system auditable and easy to inspect.
- **Always-on telemetry in normal runs:** event logging and daily outputs become required operational artifacts, not debug flags.
- **Explicit quality gates over informal rules:** reviewer authorization, expected-version validation, and idempotent run transitions are first-class checks before approvals are accepted.
- **Keep pilot posture aligned:** preserve current recursive-flow intent while explicitly aligning implementation to documented v1 semantics (no speculative feature expansion).

## Open Questions
None (all planning inputs are sufficiently specified for this pass).

## Next Steps
→ `/workflows:plan` for implementation sequencing, test plan, and rollout checks.
