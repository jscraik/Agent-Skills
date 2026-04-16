# Sub-Agent Map

Read when: selecting specialist lanes for `ce-reliability-review` on multi-component or high-blast-radius targets.

## Purpose
Keep reliability review fan-out deterministic and risk-driven, not role-sprawl-driven.

## Selection contract
1. Start with baseline reliability lanes.
2. Add only lanes that match observed risk signals in the target.
3. Keep the smallest lane set that materially improves failure analysis confidence.
4. Prefer bounded parallel; fall back to serial with the same lane set.

## Baseline lanes
Always include:
- `reliability-reviewer`
- `learnings-researcher`

## Risk-specific lanes
Add by signal:
- public or downstream contract behavior at risk: `api-contract-reviewer`
- auth/authz, trust boundaries, or secrets exposure affecting resilience: `security-reviewer`
- resource-exhaustion or scaling failure risk: `performance-reviewer`
- persistence, migration, or durable-state integrity risk: `data-integrity-guardian` or `data-migration-expert`
- rollout, rollback, and operator runbook readiness: `deployment-verification-agent`
- architecture-heavy containment or boundary concerns: `architecture-strategist`

## Optional escalation lane
For explicit assumption stress-testing:
- `adversarial-reviewer`

## Execution order
1. baseline lanes
2. risk-specific lanes
3. optional escalation lane (explicitly requested only)
