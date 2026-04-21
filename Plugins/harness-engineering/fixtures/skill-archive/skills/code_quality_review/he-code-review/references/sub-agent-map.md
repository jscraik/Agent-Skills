# Sub-Agent Map

## Table of Contents
- [Purpose](#purpose)
- [Selection contract](#selection-contract)
- [Baseline readiness lanes](#baseline-readiness-lanes)
- [Language specialists](#language-specialists)
- [Risk specialists](#risk-specialists)
- [Execution pattern](#execution-pattern)

## Purpose
Define deterministic sub-agent mapping for `he-code-review` so broad readiness reviews stay consistent and do not drift into unbounded fanout.

## Selection contract
1. Start with baseline readiness lanes.
2. Add language specialists only when relevant files or artifacts are in scope.
3. Add risk specialists only when evidence indicates those risk domains.
4. Keep the smallest reviewer set that materially improves confidence.
5. Prefer bounded parallel; fall back to serial with the same selection.

## Baseline readiness lanes
Always include:
- `agent-native-reviewer`
- `learnings-researcher`
- `code-simplicity-reviewer`

## Language specialists
Add as needed:
- `kieran-rails-reviewer`
- `kieran-typescript-reviewer`
- `kieran-python-reviewer`
- `julik-frontend-races-reviewer` for async UI timing/DOM lifecycle risk
- `design-implementation-reviewer` for Figma-sensitive UI implementation risk

## Risk specialists
Add by signal:
- `architecture-strategist` for architecture-heavy boundary changes
- `api-contract-reviewer` for public/downstream API contract impact
- `security-reviewer` for auth/authz, secrets, trust boundaries, or untrusted input
- `performance-reviewer` for hot paths, query scale, or latency risk
- `data-integrity-guardian` for schema/migration/persistence correctness
- `schema-drift-detector` for schema drift or mismatch risk
- `reliability-reviewer` for partial-state, retry, and failure-mode hazards
- `deployment-verification-agent` for rollout/rollback verification requirements

## Execution pattern
Deterministic order:
1. baseline readiness lanes
2. language specialists
3. risk specialists

Avoid in baseline mapping:
- editorial-only roles
- style-first critics before correctness and risk coverage
