---
status: pending
priority: P2
issue_id: "003"
tags: [code-review, quality]
dependencies: []
---

# 003 stabilize-orchestrator-state-reconciliation

## Problem Statement

Reconciliation can leave stale running entries after worker failures, causing duplicate or blocked dispatch.

## Findings

- Retry queue entries are created without clearing stale running metadata in one failure path.
- Terminal-state transitions are not always reflected before slot calculations.

## Technical Details

- Affected files:
  - `services/symphony/orchestrator.py`
  - `Infrastructure/tests/symphony/test_orchestrator_retries.py`
- Evidence:
  - `Review trace from he-code-review finding set P1/P2 batch`

## Proposed Solutions

### Option A: Minimal corrective patch
- Approach: Fix stale-entry cleanup in the failure/retry transition only.
- Pros: Low risk and fast to ship.
- Cons: May leave hidden coupling in other transitions.
- Effort: small
- Risk: medium

### Option B: Consolidated state-transition helper
- Approach: Centralize running/claimed/retry mutations in one helper used by all exit paths.
- Pros: Reduces future drift and improves auditability.
- Cons: Touches more code paths and tests.
- Effort: medium
- Risk: medium

## Recommended Action

Implement Option B and extend tests to cover abnormal exit + terminal refresh ordering.

## Acceptance Criteria

- [ ] No stale running entry remains after abnormal worker exit.
- [ ] Retry scheduling and slot math remain consistent under terminal transitions.
- [ ] Regression tests cover both failure and terminal reconciliation paths.

## Work Log

- 2026-04-10 he-code-review: Created from review synthesis. Initial triage complete; ready for implementation planning.
