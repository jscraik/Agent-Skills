---
schema_version: 1
title: "Symphony Service Implementation Plan"
type: "feat"
status: "active"
date: "2026-04-10"
origin: "Docs/brainstorms/2026-04-10-symphony-requirements.md"
requirements: "Docs/brainstorms/2026-04-10-symphony-requirements.md"
spec: "Docs/specs/2026-04-10-symphony-service-spec.md"
source_spec: "Docs/specs/2026-04-10-symphony-service-spec.md"
ui_spec: "Docs/ui-specs/2026-04-10-symphony-ops-ui-spec.md"
linear_project: "JSC"
linear_issue: "JSC-200"
linear_parent: "JSC-190"
linear_children: []
linear_status: "In Progress"
linear_comment_required: true
branch: "feature/JSC-200-symphony-service"
pr: "pending"
traceability_required: true
plan_route: "fresh"
plan_depth: "deep"
---

# Symphony Service Implementation Plan

## Overview

Ship a first implementation of Symphony orchestrator behavior with deterministic retry and workspace safety.

## Problem Frame

Current issue execution is manual and inconsistent; this plan defines an auditable implementation path.

## Linear Work Item Contract

- Linear issue: JSC-200
- Parent / children: JSC-190 parent, no child issues yet
- Current Linear status: In Progress
- Branch: feature/JSC-200-symphony-service
- PR: pending
- Linear comment required: true

## Requirements Trace

- R1. Poll eligible tracker work and dispatch within bounded concurrency.
- R2. Keep per-issue work isolated and observable.

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-200 | R1 | SA1 | P0 | AC1 | pending |
| JSC-200 | R2 | SA2 | P1 | AC2 | pending |

## Scope Boundaries

- Do not build a multi-tenant control plane.
- Do not embed ticket business logic in the orchestrator.

## Context & Research

### Relevant Code and Patterns
- services/symphony/orchestrator.py and existing worker lifecycle wrappers

### Institutional Learnings
- Reuse prior retry/backoff handling from queue processors to avoid duplicate claim races.

### External References
- Linear GraphQL pagination documentation

## Key Technical Decisions

- Single-authority in-memory orchestrator state: Simplifies idempotency and makes restart recovery tracker-driven.

## Open Questions

### Resolved During Planning
- Should retries persist across process restart: No; restart recovery is tracker + workspace based.

### Deferred to Implementation
- Should we support remote SSH workers in v1: Kept as extension after core local reliability is proven.

## Implementation Units

- [ ] **P0 / Unit 1: Orchestrator state and poll loop**

**Goal:** Stand up deterministic poll->reconcile->dispatch sequencing.

**Requirements:** R1, R2

**Dependencies:** None

**Files:**
- Create: `services/symphony/orchestrator.py`
- Modify: `services/symphony/main.py`
- Test: `Infrastructure/tests/symphony/test_orchestrator.py`

**Approach:** Introduce a single runtime-state object and serialize all mutations in the scheduler loop.

**Patterns to follow:**
- Follow existing queue scheduler instrumentation conventions

**Test scenarios:**
- Dispatch occurs only for active and unclaimed issues.
- Terminal-state issue stops running worker and releases claim.

**Verification:** Scheduler logs show deterministic tick stages and expected issue transitions.

## System-Wide Impact

- **Interaction graph:** Issue tracker adapter, workspace manager, and agent runner all route through orchestrator callbacks.
- **Error propagation:** Worker failure and timeout map to retry queue entries with bounded backoff.
- **State lifecycle risks:** Claim set and running map must stay consistent through abnormal worker exits.
- **API surface parity:** Status APIs mirror the same running/retrying state model.
- **Integration coverage:** Integration tests must cover poll, reconcile, retry timer, and shutdown behavior together.

## Risks & Dependencies

- Tracker API outages could starve dispatch; mitigation is skip-and-retry with operator-visible logs.

## Documentation / Operational Notes

- Document workflow frontmatter keys and runtime reload behavior in operations docs.

## Execution Ledger (Planning Mode)

STEP_ID | status (pending|in_progress|completed) | owner | evidence
---|---|---|---
P0-U1 | pending | planning-agent | plan scaffold generated

## Sources & References

- Linear issue: JSC-200
- Origin document: Docs/brainstorms/2026-04-10-symphony-requirements.md
- Spec: Docs/specs/2026-04-10-symphony-service-spec.md
- Plan: Docs/plans/2026-04-10-feat-symphony-service-plan.md
- Related code: services/symphony/*
- Related PRs: pending
- External docs: https://linear.app/developers/graphql
