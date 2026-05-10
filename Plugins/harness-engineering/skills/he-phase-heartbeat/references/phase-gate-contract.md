# Phase Gate Contract

Use this contract when a Harness Engineering heartbeat is keeping `he-work` alive across plan phases.
Do not substitute `he-heartbeat` for stale evidence inside an approved phase
loop; stale phase evidence is a stop condition for `he-phase-heartbeat`.

## Evidence Intake

Before scheduling or continuing work, create or read a bounded session-collector bundle.

Preferred command shape:

```bash
cd ~/.agents/session-collector
UV_CACHE_DIR=/tmp/session-collector-uv-cache uv run --python 3.12 python main.py --days 1 --bundle-dir <bundle-dir> --output <summary-json> --verbose
```

Required bundle artifacts:

- `manifest.json`
- `index.json`
- `harness-engineering-evidence.json`
- `skillify-candidates.json`
- `redaction-report.json`

Optional supporting artifacts:

- `skill-proof-candidates.json`
- `solved-problems.json`
- `aggregate.json`

If skill invocation analytics are unavailable or legacy, use the Harness Engineering evidence and skillify candidates as coarse workflow evidence. Do not claim precise skill invocation counts unless `skill-invocation-summary.json` supports them.

## Phase Exit Gate

For each phase:

1. Confirm the phase is approved, incomplete, reopened, or evidence-missing.
2. Confirm the changed diff belongs to that phase.
3. Run `simplify` over the phase diff.
4. Run `he-fix-bugs` only when failing evidence exists.
5. Run `he-code-review` for readiness and traceability.
6. Record exact validation command outcomes.
7. Set `slack_policy` to `none`, `bounded`, or `blocked`.
8. Commit only the completed phase diff, or report the blocker.

## Stop Rules

Stop the heartbeat when:

- all phases are complete with evidence,
- the final phase gate passes and commit status is known,
- the plan path disappears or becomes ambiguous,
- the same deterministic blocker repeats twice,
- validation evidence is stale and the next wake-up would only repeat the same
  ritual without new information,
- user approval is required for a guarded action,
- the user asks to pause or stop.

## Reporting

Each wake-up should report:

- live state checked,
- active phase,
- changed files,
- collector bundle path,
- validation status,
- review gate status,
- commit status,
- blocker and smallest recovery step,
- slack policy,
- next expected wake-up or stop reason.

When evidence is stale, record `slack_policy: blocked`, stop the phase loop, and
request or generate fresh phase evidence. Do not ask which policy file should be
edited unless the task is explicitly to change heartbeat policy.
