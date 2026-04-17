---
status: complete
priority: p1
issue_id: '001'
tags:
  - code-review
  - security
  - reliability
  - concurrency
dependencies: []
---

## Problem Statement
Canonical lesson persistence uses a check-then-write CAS pattern without any lock or atomic compare-and-swap, so concurrent approvals can both pass expected-version validation and overwrite each other.

## Findings
- In /Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/human_promote_recursive_run.sh:358-376, the script computes current_version from index + JSONL snapshot and validates expected_version against that snapshot.
- In /Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/human_promote_recursive_run.sh:431-439, it rewrites canonical-lessons.jsonl and canonical-lesson-index.json from the stale in-memory snapshot without revalidation or locking.
- If two promotion runs execute concurrently for the same scope, one write can clobber the other and silently lose approved lesson history.

## Proposed Solutions
### Option 1: Add file locking around canonical lesson read/modify/write
- **Pros:** Straightforward and explicit protection against concurrent writers.
- **Cons:** Requires robust lock lifecycle handling in shell/Python boundary.
- **Effort:** Medium
- **Risk:** Low

### Option 2: Implement atomic CAS with content hash recheck before commit
- **Pros:** Preserves optimistic concurrency semantics and avoids coarse locking.
- **Cons:** More complex implementation and retry behavior.
- **Effort:** Large
- **Risk:** Medium

### Option 3: Move canonical persistence into a single Python helper with transaction-like guard
- **Pros:** Reduces shell complexity and centralizes correctness checks.
- **Cons:** Requires refactor and new test coverage.
- **Effort:** Medium
- **Risk:** Low

## Recommended Action


## Technical Details
### Affected files/components
- `/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/human_promote_recursive_run.sh`
- `/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/lessons/canonical-lessons.jsonl`
- `/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skill-graphs/lessons/canonical-lesson-index.json`

## Acceptance Criteria
- [ ] Concurrent approvals for same scope cannot lose entries in canonical-lessons.jsonl.
- [ ] A failed CAS emits deterministic blocker evidence and preserves prior canonical state.
- [ ] Concurrency regression test covers double-write race with expected-version token reuse.

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
