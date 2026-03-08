---
status: complete
priority: p2
issue_id: '005'
tags:
  - code-review
  - performance
  - scalability
dependencies: []
---

## Problem Statement
Shadow report generation scans all run directories and fully parses journals before applying window filters, causing runtime and IO growth proportional to total historical runs.

## Findings
- In /Users/jamiecraik/dev/agent-skills/utilities/skill-builder/scripts/build_recursive_skill_shadow_report.py:504-533, all run_* directories are loaded and parsed.
- Window filtering happens later at lines 541-547, after full load.
- load_jsonl uses read_text().splitlines() (lines 101-108), which reads full file into memory.

## Proposed Solutions
### Option 1: Pre-filter using run.json finished_at before loading journals/events
- **Pros:** Large IO savings with small code change.
- **Cons:** Requires resilient handling of malformed run.json timestamps.
- **Effort:** Medium
- **Risk:** Low

### Option 2: Implement incremental index/cache for recent runs
- **Pros:** Best long-term scalability for daily telemetry jobs.
- **Cons:** Adds cache invalidation and index maintenance complexity.
- **Effort:** Large
- **Risk:** Medium

### Option 3: Stream JSONL parsing instead of read_text splitlines
- **Pros:** Reduces peak memory even when full file parse is needed.
- **Cons:** Moderate refactor across helper functions.
- **Effort:** Small
- **Risk:** Low

## Recommended Action


## Technical Details
### Affected files/components
- `/Users/jamiecraik/dev/agent-skills/utilities/skill-builder/scripts/build_recursive_skill_shadow_report.py`

## Acceptance Criteria
- [ ] Report generation scales with active window size rather than total historical run count.
- [ ] Large historical run set does not materially increase daily report runtime.
- [ ] Memory usage remains bounded during JSONL parsing.

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
