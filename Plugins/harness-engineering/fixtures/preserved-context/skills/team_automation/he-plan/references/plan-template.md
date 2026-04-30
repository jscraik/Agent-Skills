---
schema_version: 1
title: "Symphony Service Implementation Plan"
type: "feat"
status: "active"
date: "2026-04-10"
origin: "docs/brainstorms/2026-04-10-symphony-requirements.md"
spec: "Docs/specs/2026-04-10-symphony-service-spec.md"
ui_spec: "docs/ui-specs/2026-04-10-symphony-ops-ui-spec.md"
plan_route: "fresh"
plan_depth: "deep"
---

# Symphony Service Implementation Plan

## Overview

Ship a first implementation of Symphony orchestrator behavior with deterministic retry and workspace safety.

## Problem Frame

Current issue execution is manual and inconsistent; this plan defines an auditable implementation path.

## Requirements Trace

- R1. Poll eligible tracker work and dispatch within bounded concurrency.
- R2. Keep per-issue work isolated and observable.

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

- Origin document: docs/brainstorms/2026-04-10-symphony-requirements.md
- Related code: services/symphony/*
- Related issues/PRs: JSC-200
- External docs: https://linear.app/developers/graphql