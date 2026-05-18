# Architecture Review - sdk_north_star_round2_architecture_strategist

## Findings (severity-ranked)

1. HIGH: Contract inconsistency in required output shape can break downstream consumers.
- Evidence: [2026-05-17-agent-skills-sdk-north-star.md](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:169) states doctor output "always returns" `next_command`, while [same file](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:332) softens this to "`next_command` where applicable".
- Architectural impact: This creates an unstable interface contract for harness/schema consumers and increases coupling to implementation nuance.
- Remediation: Make `next_command` consistently required with explicit null/empty semantics, or consistently optional and reflected in schema + AC text + fixture assertions.

2. MEDIUM: Ownership boundary is stated but not operationalized with explicit ownership map and decision rights.
- Evidence: The strategy warns that harness must not own skill internals ([line 62](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:62), [line 300](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:300), [line 347](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:347)), but phases and acceptance criteria do not define owner/accountable roles per contract surface.
- Architectural impact: Boundary drift risk remains high during implementation because ownership is principle-level, not enforceable at execution planning time.
- Remediation: Add a compact ownership matrix (ASK vs harness) for each surface (`doctor`, `package`, `profiles`, `events`, `prove`, schema stewardship, gate policy authority).

3. MEDIUM: Freshness/readiness policy is under-specified for deterministic multi-environment behavior.
- Evidence: Deterministic status is required ([line 170](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:170)), and stale memory can be warning/blocked by profile ([line 188](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:188), [line 329](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:329)), but no canonical time source/boundary conditions are defined.
- Architectural impact: Two operators can produce divergent readiness results from the same artifact set, weakening trust in doctor as the "single trusted readiness contract."
- Remediation: Define explicit freshness contract inputs (timestamp field, timezone normalization, comparison authority, threshold semantics) and add boundary tests.

## Compliance Check

- Strong alignment with repository architecture intent:
  - Canonical source vs runtime projection separation is explicit ([lines 45, 58-60](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:45)).
  - Thin-surface and guardrail framing is consistent with control-plane direction ([lines 32-39](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:32)).
  - Harness-as-consumer boundary is clearly stated ([lines 108-110, 286-289](/Users/jamiecraik/dev/agent-skills/.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:108)).

## Risk Summary

- Primary closure risk: interface and governance ambiguity, not vision quality.
- The roadmap is directionally strong, but these contract-level ambiguities are Type 1 architectural decisions and should be resolved before declaring this ready as the implementation north star.

VERDICT: request_changes
WROTE: /Users/jamiecraik/dev/agent-skills/artifacts/reviews/sdk_north_star_round2_architecture_strategist.md
