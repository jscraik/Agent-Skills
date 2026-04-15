# Sub-Agent Map

## Table of Contents
- [Purpose](#purpose)
- [Selection contract](#selection-contract)
- [Parent orchestrator responsibilities](#parent-orchestrator-responsibilities)
- [Execution delegates](#execution-delegates)
- [Verification specialists](#verification-specialists)
- [Execution pattern](#execution-pattern)

## Purpose
Define deterministic sub-agent mapping for `ce-work` so execution delegation and verification coverage are explicit and bounded.

## Selection contract
1. Keep contract restatement, artifact updates, and shipping handoff in the parent orchestrator.
2. Delegate only isolated implementation slices with clear acceptance boundaries.
3. Add verification specialists only when risk signals require them.
4. Keep the smallest specialist set that materially improves confidence.
5. If delegation is unavailable or unsafe, collapse to serial execution in the main thread.

## Parent orchestrator responsibilities
Always keep in parent:
- lane selection and risk triage
- governing-artifact reads and contract restatement
- contract-drift updates to plan/spec artifacts
- branch/worktree and git decision control
- final handoff package and completion decision

## Execution delegates
Use only when user/plan explicitly requests delegation (`external-delegate`, `swarm-mode`, or equivalent):
- `worker` for isolated implementation units with non-overlapping files and explicit done criteria

Do not delegate:
- broad architectural decisions
- artifact drift reconciliation
- final merge/handoff recommendations

## Verification specialists
Add by risk signal after implementation slices land:
- `correctness-reviewer` for logic/correctness-sensitive changes
- `testing-reviewer` for test adequacy and missing high-value cases
- `security-reviewer` for auth/authz, untrusted input, secrets, or trust boundaries
- `performance-reviewer` for hot path, query scale, or latency risk
- `data-integrity-guardian` for schema/migration/persistence correctness
- `reliability-reviewer` for partial-state, retry/idempotency, and failure-mode hazards
- `api-contract-reviewer` for public/downstream API behavior changes
- `design-implementation-reviewer` for non-trivial UI fidelity-sensitive changes
- `julik-frontend-races-reviewer` for async frontend race/timing risks
- `deployment-verification-agent` for rollout/rollback and production verification plans

## Execution pattern
Deterministic order:
1. parent contract and task setup
2. optional `worker` delegation for isolated units
3. merge and local validation gates
4. risk-based verification specialists
5. parent-owned handoff and final status

Avoid in execution baseline mapping:
- editorial-only roles
- broad fanout before isolated-unit boundaries are clear
