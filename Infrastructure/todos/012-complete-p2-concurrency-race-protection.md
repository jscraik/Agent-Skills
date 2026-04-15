---
status: complete
priority: p2
issue_id: "012"
tags:
  - code-review
  - concurrency
  - reliability
dependencies: []
---

# Missing explicit concurrency/race-protection requirements

## Problem Statement
The plan emphasizes atomic writes and backup restoration but does not define concurrency control for overlapping invocations. Without a lock strategy, simultaneous `run_graph_op.sh` calls can still race on parse inputs and NDJSON/appended artifact writes.

## Findings
- Safety guidance includes atomic rename and `.bak` backups, but no process lock/serialized execution section:
  `Docs/plans/...:211-214`.
- Evolution NDJSON operations are stateful and append-based (`graph-metrics.ndjson`) and therefore sensitive to concurrent writes unless protected.
  See: `Docs/plans/...:444-450`.

## Proposed Solutions

### Option 1: Add artifact-level lock file protocol
**Approach:** Add a lock per operation (`Infrastructure/ops/health/graph/.lock`) acquired before parse/write stages and released in `trap`.

**Pros:**
- Prevents interleaving writes and partial snapshots.
- Straightforward to implement in Bash + Python wrappers.

**Cons:**
- Requires cleanup on stale locks.

**Effort:** 2-3 hours

**Risk:** Medium

### Option 2: Serialize by caller (single-queue external orchestration)
**Approach:** Use orchestration layer to guarantee one run at a time.

**Pros:**
- Simpler script logic if infrastructure already serializes jobs.

**Cons:**
- Fragile in environments with direct manual execution.

**Effort:** 1-2 hours

**Risk:** Medium-High

### Option 3: Skip lock and rely on `mv` atomicity only
**Approach:** Keep only atomic rename and tolerate collisions.

**Pros:**
- Lowest immediate implementation complexity.

**Cons:**
- Does not prevent read-modify-write conflicts or NDJSON append races.

**Effort:** 0.5 hour

**Risk:** High

## Recommended Action

TBD: adopt Option 1 and include stale-lock recovery in recovery checklist.

## Technical Details

**Affected sections/files:**
- `Technical Considerations` concurrency and race controls in command implementation.
- `run_graph_op.sh CLI Contract` and `Implementation Tasks` execution sequence.
- NDJSON snapshot append behavior.

## Acceptance Criteria
- [ ] One lock per command invocation sequence is defined and tested.
- [ ] Parallel invocations return deterministic success/fail/queue behavior.
- [ ] NDJSON append remains stable under concurrent load tests.

## Work Log

### 2026-02-26 - Initial Discovery

**By:** code review process

**Actions:**
- Reviewed snapshot append behavior and write-atomicity requirements.
- Identified missing lock/queue guarantees for concurrency.

**Learnings:**
- Atomic rename alone does not address concurrent `run_graph_op.sh` races.

## Notes
- This is a reliability blocker for operational automation where two prompts may run graph ops concurrently.
