# Kill Switch and Escalation Runbook (Phase 4+)

Operator runbook for safely halting autonomous behavior.

## Table of Contents

- [When to trigger](#when-to-trigger)
- [Control hierarchy](#control-hierarchy)
- [Wave rollout safety model](#wave-rollout-safety-model)
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
   - `Infrastructure/artifacts/skill-graphs/controls/kill-switch.txt`
   - `Infrastructure/artifacts/skill-graphs/controls/rollback-required.txt`
2. Rollout mode:
   - `Infrastructure/artifacts/skill-graphs/controls/rollout-mode.txt` with `off | observe_only | active`
3. Gate enforcement mode:
   - `Infrastructure/artifacts/skill-graphs/controls/hard-gate-mode.txt` with `auto | force_on | force_off`
   - default is `auto` when missing or invalid
4. Feature kill switches:
   - `Infrastructure/artifacts/skill-graphs/controls/auto_capture.disabled`
   - `Infrastructure/artifacts/skill-graphs/controls/auto_apply.disabled`
5. Per-skill kill switches:
   - `Infrastructure/artifacts/skill-graphs/controls/skills/<scope_skill>/auto_capture.disabled`
   - `Infrastructure/artifacts/skill-graphs/controls/skills/<scope_skill>/auto_apply.disabled`

## Mandatory pre-run invocation check

Before changing rollout state or enabling auto-apply, run a pre-invocation check:

1. Confirm control files exist and are readable.
2. Confirm the objective/profile is routed through the required delegation mode
   (`autopilot / co-pilot / manual override` with legacy `collaboration` handled as compatibility).
3. Confirm network/external action assumptions in the run profile.
4. Confirm one-tap feedback and evidence packet fields are expected for the selected mode.

The promotion workflow references this as the mandatory gate in `docs/skill-graphs/workflows/promotion-gate.md`.

Precedence: kill-switch/rollback controls override rollout mode; rollout mode then gates hard-gate behavior and feature switches.

## Wave rollout safety model

Use explicit onboarding waves:

1. `wave-0-controls`:
   - kill-switch precedence verified
   - rollout mode precedence verified
   - `events.jsonl` envelope integrity verified
2. `wave-1-manual`:
   - manual-mode skills only
   - `observe_only`
   - reviewer signoff required for promotion candidates
3. `wave-2-co-pilot`:
   - remaining co-pilot skills by domain cohort
   - auto-apply remains disabled until uplift/non-regression gates pass

Every wave blocker in readiness artifacts must include:
- `owner`
- `due_date`
- `escalation_date`

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
bash Infrastructure/scripts/lifecycle-and-sync/run_recursive_rollout_drill.sh
```

Evidence artifacts:
- `/Infrastructure/artifacts/skill-graphs/pilot/rollback-drill-report.json`
- `/docs/skill-graphs/pilots/rollback-drill.md`

## Recovery checklist

- Root-cause analysis documented.
- Corrective action linked to affected profile(s).
- Regression checks pass for impacted controls.
- Reviewer signs off re-enable decision.
