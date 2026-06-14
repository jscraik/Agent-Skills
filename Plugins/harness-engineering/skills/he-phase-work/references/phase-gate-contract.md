# Phase Gate Contract

Read when: collector commands, required artifacts, phase-exit sequence, stop rules, report fields, or the detail relocated out of `SKILL.md` is needed during a phase work.

Use this contract when a 10 minute Harness Engineering heartbeat is keeping `he-work` alive across plan phases.
Do not substitute `he-phase-work` for stale evidence inside an approved phase
loop; stale phase evidence is a stop condition for `he-phase-work`.

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

## Side-Effect Classification

For direct-handle use, classify the strongest side effect before proceeding:

- `read_only`: inspect plan, git state, collector artifacts, validation logs, or existing heartbeat state.
- `artifact_write`: write plan/eval/handoff evidence inside the approved workspace.
- `repo_write`: edit canonical source files belonging to the active phase.
- `external_write`: create or update heartbeat automations, issue comments, PR bodies, or trackers.
- `destructive`: delete, force-push, merge, deploy, close trackers, resolve review threads, or remove evidence.

Ask for explicit approval or block before `external_write` or `destructive` actions unless the user already granted that authority for the exact target.

## Phase Exit Gate

For each phase:

1. Confirm the phase is approved, incomplete, reopened, or evidence-missing.
2. Confirm the changed diff belongs to that phase.
3. Run `simplify` over the phase diff.
4. Run the phase's smallest relevant tests or validation command and record exact outcomes.
5. Run `he-fix-bugs` only when failing evidence exists, then rerun the relevant failing gate.
6. Run `he-code-review` for readiness and traceability.
7. Stage only completed-phase files with scoped `git add`, or report `git_staging_status: blocked`.
8. Update Linear or the tracker with phase evidence, or report `linear_update_status: blocked` with ready-to-post text.
9. Set `slack_policy` to `none`, `bounded`, or `blocked`.

## Stop Rules

Stop the heartbeat when:

- all phases are complete with evidence,
- the final phase gate passes, final eval/reinforce/reconcile closeout has run, and staging status is known,
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
- git staging status,
- Linear update status,
- blocker and smallest recovery step,
- slack policy,
- next expected wake-up or stop reason.

When evidence is stale, record `slack_policy: blocked`, stop the phase loop, and
request or generate fresh phase evidence. Do not ask which policy file should be
edited unless the task is explicitly to change heartbeat policy.

## Local Command Probe Preference

For coding-harness work, prefer source-truth command probes from the target repo, such as `pnpm exec tsx src/cli.ts ...`, before broader gates. Record exact outcomes and do not treat a broad green gate as proof that the phase-specific command path was exercised.

## Relocated Entrypoint Detail

These details were moved out of the always-loaded `SKILL.md` body to preserve context while reducing invoke cost:

- Start with two or three focused surfaces and expand only when phase evidence proves broader context is required.
- Search for an existing matching heartbeat before creating another one, and include cadence, live checks, stop rules, reporting policy, and forbidden unattended actions.
- Use a 10 minute heartbeat for phase work; do not stretch phase work into an arbitrary monitor cadence.
- Keep the XP operating contract explicit by setting `slack_policy` to `none`, `bounded`, or `blocked`.
- For plugin-level confidence claims, run or require the HE lifecycle release eval lane across changed lifecycle skills plus adjacent route/work skills.
- Treat static Plugin Eval budget failures as blocking, excluded from the runtime claim, or assigned follow-up; do not hide them under strict audit success.
