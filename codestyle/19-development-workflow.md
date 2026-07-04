# Development Workflow Standards

## Table of Contents
- [Scope](#scope)
- [Research and reuse first](#research-and-reuse-first)
- [Plan before implementation](#plan-before-implementation)
- [Build and verify loop](#build-and-verify-loop)
- [Temporary reproduction harnesses](#temporary-reproduction-harnesses)
- [Pre-review readiness](#pre-review-readiness)
- [Enforcement](#enforcement)

## Scope
- This module defines the end-to-end feature workflow before and around Git/PR operations.
- It complements [13-git-workflow.md](./13-git-workflow.md), which covers commit and PR mechanics.

## Research and reuse first
- Before writing new implementation code:
  1. Search the current repository for an existing pattern.
  2. Search trusted upstream sources (official docs, library docs, primary references).
  3. Reuse or adapt proven patterns where practical instead of creating net-new approaches.
- Prefer retrieval-led reasoning for fast-moving ecosystems and version-sensitive APIs.

## Plan before implementation
- For multi-step work, a short implementation plan MUST be defined before editing.
- Risks, dependencies, validation gates, and rollback path MUST be identified up front.
- Scope MUST remain explicit; non-required follow-ups SHOULD be deferred rather than blending unrelated work.

## Build and verify loop
1. Implement the smallest meaningful increment.
2. Run the smallest real executable path that exercises the exact production code touched whenever feasible.
3. Relevant tests/validators MUST run immediately, including `pnpm run quality:docstrings`, `pnpm run quality:size`, and `pnpm run test:related` for changed production source.

4. If runtime behavior or generated artifacts changed, `pnpm test:deep` MUST run before handoff.
5. Failures MUST be fixed before expanding scope.
6. Repeat until the intended behavior and contract checks are green (or explicitly blocked).


## Temporary reproduction harnesses
- If no existing test covers the exact touched path, agents MAY create a temporary local reproduction harness under `codex-scripts/`.
- `codex-scripts/` MUST remain gitignored and is for local evidence only.
- Temporary harnesses SHOULD import or invoke production code directly. Copy only the minimum fixtures or input data needed to reproduce behavior.
- If a temporary reproduction becomes generally useful, it SHOULD graduate into the tracked test suite or a maintained helper script instead of remaining in `codex-scripts/`.
- If the exact path cannot run because it depends on unavailable credentials, external services, unsafe side effects, or missing generated runtime state, the blocker MUST be recorded explicitly and the nearest meaningful validation SHOULD run instead.

## Pre-review readiness
- Before handoff or PR review:
  - Branch state and diff scope MUST be understood.
  - Required validation commands MUST be run and recorded.
  - Blocker reasons MUST be explicit for any skipped or blocked checks.

## Enforcement
- Required baseline validation for this repository:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm run quality:docstrings`
  - `pnpm run quality:size`
  - `pnpm run test:related`

  - `pnpm test:deep` when runtime behavior or generated artifacts change

  - `pnpm test`
  - `pnpm audit`
  - `pnpm check`
  - `bash scripts/validate-codestyle.sh`
  - `bash scripts/verify-work.sh --fast`
- Use exact command evidence format:
  - `Command: <exact command> -> pass|fail|blocked (<reason>)`
