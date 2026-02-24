---
status: pending
priority: p3
issue_id: '008'
tags:
  - code-review
  - quality
  - maintainability
dependencies: []
---

## Problem Statement
Pilot profile identifiers are hard-coded in multiple files, increasing drift risk between run generation and report aggregation.

## Findings
- In /Users/jamiecraik/dev/agent-skills/scripts/run_recursive_skill_shadow_cycle.sh:43-48, profiles array is hard-coded.
- In /Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/build_recursive_skill_shadow_report.py:14-19, PILOT_PROFILES repeats same values.
- A profile update requires synchronized edits in separate shell and Python code paths.

## Proposed Solutions
### Option 1: Move pilot profile list to single JSON/YAML config consumed by both scripts
- **Pros:** Eliminates drift and simplifies updates.
- **Cons:** Adds shared config loading logic.
- **Effort:** Small
- **Risk:** Low

### Option 2: Generate shell list from Python source via helper command
- **Pros:** No new config file; one source of truth remains Python.
- **Cons:** Couples shell script to Python runtime call.
- **Effort:** Medium
- **Risk:** Low

### Option 3: Add validation check asserting both lists match
- **Pros:** Low-cost safety net if duplication remains.
- **Cons:** Does not remove duplication itself.
- **Effort:** Small
- **Risk:** Low

## Recommended Action


## Technical Details
### Affected files/components
- `/Users/jamiecraik/dev/agent-skills/scripts/run_recursive_skill_shadow_cycle.sh`
- `/Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/build_recursive_skill_shadow_report.py`

## Acceptance Criteria
- [ ] A single source of truth defines pilot profiles for runner and report paths.
- [ ] Profile additions/removals require one edit and pass CI checks.
- [ ] Regression test or lint rule detects profile-list drift.

## Work Log
- 2026-02-24: Created from PR #18 multi-agent code review synthesis.

## Resources
- PR: https://github.com/jscraik/Agent-Skills/pull/18
- Commit: 1c5f11d
- Known pattern docs:
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/index.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/schemas/gate-contract.schema.md`
