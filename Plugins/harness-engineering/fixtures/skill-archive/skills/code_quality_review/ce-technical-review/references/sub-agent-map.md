# Sub-Agent Map

## Table of Contents
- [Purpose](#purpose)
- [Selection contract](#selection-contract)
- [Baseline mapping](#baseline-mapping)
- [Language specialists](#language-specialists)
- [Risk specialists](#risk-specialists)
- [Document-review specialists](#document-review-specialists)
- [Execution pattern](#execution-pattern)

## Purpose
Define deterministic reviewer/sub-agent mapping for `ce-technical-review` so fanout is consistent, minimal, and technically aligned.

## Selection contract
1. Start with required baseline reviewers.
2. Add language specialists based on changed files.
3. Add risk specialists only when evidence indicates that risk.
4. Keep the smallest reviewer set that materially improves confidence.
5. Prefer bounded parallel execution; fall back to serial with the same selection.

## Baseline mapping
Always include:
- `correctness-reviewer`
- `testing-reviewer`
- `code-simplicity-reviewer`

## Language specialists
Add exactly when relevant:
- `kieran-rails-reviewer` for Ruby/Rails files
- `kieran-typescript-reviewer` for TypeScript/JavaScript files
- `kieran-python-reviewer` for Python files

## Risk specialists
Add by risk signal:
- `security-reviewer`: auth/authz, secrets, trust boundaries, untrusted input
- `performance-reviewer`: hot paths, expensive queries, latency regression risk
- `data-integrity-guardian`: schema/migration/persistence correctness
- `schema-drift-detector`: schema dump drift or migration/schema mismatch
- `reliability-reviewer`: partial-state hazards, retry/idempotency, degraded-mode behavior
- `deployment-verification-agent`: rollout/rollback and production verification contracts
- `api-contract-reviewer`: public/downstream API contract changes
- `architecture-strategist`: multi-module design and boundary changes
- `maintainability-reviewer`: elevated complexity/coupling risk
- `julik-frontend-races-reviewer`: async UI race/timing and DOM lifecycle hazards

## Document-review specialists
For specs/plans, add:
- `spec-flow-analyzer`
- `feasibility-reviewer`

Then add risk specialists when the document introduces those risk domains.

## Execution pattern
Deterministic order:
1. baseline
2. language
3. risk
4. document-specific additions

Avoid in technical baseline:
- editorial-only roles
- style-first convention critics before correctness/testing risk coverage
