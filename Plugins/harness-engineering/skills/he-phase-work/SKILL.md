---
name: he-phase-work
description: "Runs approved Harness Engineering plans in recurring phases: check live state, wake with he-heartbeat, execute only the active he-work slice, verify gates, update Linear only with approval, and stop before unsafe staging or closure. Use when a plan, issue, or PR needs continued phase-by-phase execution."
metadata:
  version: 1.0.0
  skill-type: team_automation
  trigger_terms: "he phase work; continue approved plan; run phases; recurring implementation; phase gate; keep issue moving"
---

# HE Phase Work

## Philosophy
Move an approved plan one safe phase at a time. The heartbeat wakes the thread; this skill decides whether the next phase is safe and delegates implementation to `he-work`.

## When to Use
Use when the user asks to continue an approved plan, issue, PR, or recurring implementation loop with phase gates, validation, and optional Linear updates.

## When Not to Use
Use `he-work` for one-off implementation. Use `he-plan` or `he-spec` when the phase sequence is not approved. Stop if plan path, active phase, edit authority, Linear authority, or validation gate is unclear.

## Inputs
Approved plan path, target issue/PR, active phase, branch/dirty state, validation command, heartbeat authority, Linear authority, staging authority, and provenance evidence when cited.

## Outputs
Return phase status: active phase, gates, validation outcomes, heartbeat status, Linear update status, git staging status, blockers, and next safe action.

## Procedure
Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, superseded, or
low-signal text.

1. Check live state: `git status --short`, branch, plan path, active phase, latest validation, target issue/PR, and blockers.
2. Verify the plan exists and names the current phase, validation gate, rollback, and stop condition.
3. Ensure exactly one matching heartbeat exists or return the heartbeat prompt when automation authority is missing.
4. Hand only the active implementation slice to `he-work`.
5. Run the phase validation command after `he-work`. If it fails, route to `he-work` or `he-code-review` with the exact command and output.
6. Refresh dashboards/browser only after a real validation or eval run.
7. Ask before Linear mutation, staging, commit, push, or closure.

## Validation
Fail fast: stop at the first failed gate and do not proceed until fixed, waived by an authorized gate, or reported as blocked.

~~~bash
git status --short
git branch --show-current
test -f <approved-plan-path>
rg -n "phase|gate|validation|blocked|rollback" <approved-plan-path>
./bin/ask skills audit <touched-skill-path> --level strict --json --robot
~~~

## Failure Mode
Stop when phase identity, plan path, authority, validation, heartbeat target, or live issue/PR state is missing. Return the smallest recovery step.

## Constraints
Redact secrets and sensitive data by default. Do not invent phases, silently create automation, stage files, close trackers, or treat stale validation as current proof.

## Execution Boundaries
This skill orchestrates. Code edits belong to `he-work`; review repair belongs to `he-code-review`; tracker mutation requires approval.

## Gotchas
- Browser refresh is evidence display, not validation.
- Heartbeat existence does not authorize implementation.
- One phase means one active slice and one validation loop.

## Examples
- When the user asks, "Continue JSC-246 phase 2," inspect the approved plan, verify the active phase, run only that slice, and report the validation gate.
- When the user asks, "Keep this PR moving every 10 minutes," confirm heartbeat authority before creating or reusing automation.

## Delegation Examples
Send the active slice to implementation:
~~~text
he-work: Implement only Phase 2 from .harness/plan/JSC-246-dashboard.md. Allowed files: Infrastructure/scripts/lib/ask/skill_review_dashboard.py. Run python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q. Do not stage.
~~~

Send a failed gate to review/repair:
~~~text
he-code-review: Review the Phase 2 failure. Command failed: python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q. Determine whether this is an implementation bug, missing test update, or blocked environment.
~~~

## Output Template
~~~yaml
schema_version: 1
selected_stage: he-phase-work
target: JSC-246
active_phase: "Phase 2: dashboard scorecard"
heartbeat_status: existing
phase_gates:
  - name: plan_exists
    command: "test -f .harness/plan/JSC-246-dashboard.md"
    outcome: pass
validation:
  - command: "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
    outcome: pass
linear_update_status: confirmation_required
git_staging_status: not_staged
next_safe_action: "Report phase evidence; ask before Linear mutation."
~~~

## Stage Arc Boundary
Before artifact writes, mutation, scheduling, handoff, or closure claims, apply
`../../references/stage-arc-boundary-contract.md`. Structured outputs and
handoffs must include `stage_arc_boundary` with `left_arc`, `active_arc`,
`right_arc`, `coding_lens`, and `testing_lens`; block when left evidence is
stale, active mutation exceeds authority, right-side proof is missing, or a
required persona lens is not covered.

## References
- Phase gates: `references/phase-gate-contract.md`, `references/contract.yaml`, `references/evals.yaml`
- Shared policy: `../../references/subagent-call-contract.md`, `../../references/deferred-context-index.md`
