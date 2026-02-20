# Kill Switch and Escalation Runbook (Phase 4+)

Operator runbook for safely halting autonomous behavior.

## Table of Contents

- [When to trigger](#when-to-trigger)
- [Immediate response](#immediate-response)
- [Escalation policy](#escalation-policy)
- [Recovery checklist](#recovery-checklist)

## When to trigger

Trigger kill switch if any occur:
- repeated budget overrun,
- unresolved evaluator conflict,
- evidence of canonical poisoning,
- sensitive data leakage risk.

## Immediate response

1. Set runtime mode to `manual_only`.
2. Mark active run terminal as `aborted` or `escalated` with reason code.
3. Emit `run_state_changed` and `failure_event`.
4. Freeze promotion approvals pending review.

## Escalation policy

- Severity `warn`: runtime owner triage within same business day.
- Severity `fail`: governance + security owners notified immediately.
- Any `fail` involving data leakage blocks promotions until clearance.

## Recovery checklist

- Root-cause analysis documented.
- Corrective action linked to affected profile(s).
- Regression checks pass for impacted controls.
- Reviewer signs off re-enable decision.
