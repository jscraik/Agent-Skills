---
status: complete
priority: p1
issue_id: '002'
tags:
  - code-review
  - reliability
  - telemetry
  - governance
dependencies: []
---

## Problem Statement
When run lock acquisition fails, the loop emits run_blocked/state/failure events in memory but returns before writing the updated events array back to events.jsonl.

## Findings
- In /Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/recursive_skill_loop.py:583, events.jsonl is initially written with only run_initialized.
- In /Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/recursive_skill_loop.py:585-636, lock-collision branch appends run_blocked, run_state_changed, and failure_event to memory then returns 5 without write_jsonl(events_path, events).
- This violates telemetry contract expectations in /Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md where blocked runs must be observable in events.jsonl.

## Proposed Solutions
### Option 1: Persist events immediately before early return on lock collision
- **Pros:** Minimal patch with clear behavior fix.
- **Cons:** Still relies on multiple write sites.
- **Effort:** Small
- **Risk:** Low

### Option 2: Wrap early-return branches in a finalize_run() helper that always flushes events
- **Pros:** Prevents similar telemetry gaps in other branches.
- **Cons:** Requires refactor of return paths.
- **Effort:** Medium
- **Risk:** Low

### Option 3: Add post-condition assertion for required terminal events before return
- **Pros:** Creates guardrail against future regressions.
- **Cons:** Needs explicit exception handling semantics.
- **Effort:** Medium
- **Risk:** Medium

## Recommended Action


## Technical Details
### Affected files/components
- `/Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/recursive_skill_loop.py`
- `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md`

## Acceptance Criteria
- [ ] Lock-collision run emits persisted run_blocked + run_state_changed + failure_event records in events.jsonl.
- [ ] Telemetry validator no longer reports missing blocked-event evidence for lock collisions.
- [ ] Unit/integration test exercises lock contention branch and asserts event flush.

## Work Log
- 2026-02-24: Implemented and validated fix in repository code.
- 2026-02-24: Created from PR #18 multi-agent code review synthesis.

## Resources
- PR: https://github.com/jscraik/Agent-Skills/pull/18
- Commit: 1c5f11d
- Known pattern docs:
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/index.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/schemas/gate-contract.schema.md`
