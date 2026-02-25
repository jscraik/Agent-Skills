# Kill Switch and Escalation Runbook (Phase 4+)

Operator runbook for safely halting autonomous behavior.

## Table of Contents

- [When to trigger](#when-to-trigger)
- [Control hierarchy](#control-hierarchy)
- [Immediate response](#immediate-response)
- [Escalation policy](#escalation-policy)
- [Rollback drill evidence](#rollback-drill-evidence)
- [Recovery checklist](#recovery-checklist)

## When to trigger

Trigger kill switch if any occur:
- repeated budget overrun,
- unresolved evaluator conflict,
- evidence of canonical poisoning,
- sensitive data leakage risk.

## Control hierarchy

Runtime controls are file-based and fail-closed:

1. Global emergency controls:
   - `controls/kill-switch.txt`
   - `controls/rollback-required.txt`
2. Rollout mode:
   - `controls/rollout-mode.txt` with `off | observe_only | active`
3. Feature kill switches:
   - `controls/auto_capture.disabled`
   - `controls/auto_apply.disabled`
4. Per-skill kill switches:
   - `controls/skills/<scope_skill>/auto_capture.disabled`
   - `controls/skills/<scope_skill>/auto_apply.disabled`

Precedence: kill-switch/rollback controls override rollout mode; rollout mode then gates auto-capture and auto-apply.

## Immediate response

1. Set runtime mode to `off`.
2. Mark active run terminal as `aborted` or `escalated` with reason code.
3. Emit `run_state_changed` and `failure_event`.
4. Freeze promotion approvals pending review.

## Escalation policy

- Severity `warn`: runtime owner triage within same business day.
- Severity `fail`: governance + security owners notified immediately.
- Any `fail` involving data leakage blocks promotions until clearance.

## Rollback drill evidence

Run the propagation drill:

```bash
bash scripts/run_recursive_rollout_drill.sh
```

Evidence artifacts:
- `/artifacts/skill-graphs/pilot/rollback-drill-report.json`
- `/docs/skill-graphs/pilots/rollback-drill.md`

## Recovery checklist

- Root-cause analysis documented.
- Corrective action linked to affected profile(s).
- Regression checks pass for impacted controls.
- Reviewer signs off re-enable decision.
