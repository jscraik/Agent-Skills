---
status: pending
priority: p2
issue_id: '003'
tags:
  - code-review
  - quality
  - governance
  - telemetry
dependencies: []
---

## Problem Statement
Validation treats missing promotion_approved event and missing run/events.jsonl as warnings rather than errors for approved decisions, allowing approvals without required audit evidence.

## Findings
- In /Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/validate_recursive_promotion.py:354-364, missing promotion_approved event or missing events.jsonl appends warnings only.
- Validator status remains ok when errors are empty (line 393), so CI can pass without required event evidence.
- Docs state approved decisions must emit promotion_approved and run events in events.jsonl.

## Proposed Solutions
### Option 1: Promote missing promotion_approved and missing events.jsonl to hard errors
- **Pros:** Aligns implementation with documented governance contract.
- **Cons:** May fail legacy artifacts until backfilled.
- **Effort:** Small
- **Risk:** Low

### Option 2: Introduce strict-mode flag defaulting to strict in CI
- **Pros:** Allows gradual migration for historical runs.
- **Cons:** Maintains two behaviors if not later removed.
- **Effort:** Medium
- **Risk:** Low

### Option 3: Add CI assertion that approved decisions must contain promotion_approved in same run dir
- **Pros:** Separate explicit gate for audit evidence.
- **Cons:** Potential duplicate logic with validator.
- **Effort:** Small
- **Risk:** Low

## Recommended Action


## Technical Details
### Affected files/components
- `/Users/jamiecraik/dev/agent-skills/utilities/skill-creator/scripts/validate_recursive_promotion.py`
- `/Users/jamiecraik/dev/agent-skills/scripts/validate_recursive_promotions.sh`
- `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md`

## Acceptance Criteria
- [ ] Approved decision validation fails when promotion_approved event is absent.
- [ ] Approved decision validation fails when run/events.jsonl is absent or unreadable.
- [ ] CI pipeline fails for governance evidence gaps and passes with complete events.

## Work Log
- 2026-02-24: Created from PR #18 multi-agent code review synthesis.

## Resources
- PR: https://github.com/jscraik/Agent-Skills/pull/18
- Commit: 1c5f11d
- Known pattern docs:
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/index.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/telemetry/daily-outputs.md`
  - `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/schemas/gate-contract.schema.md`
