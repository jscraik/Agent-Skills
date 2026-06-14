# Phase Gate Contract

Read when: collector commands, required artifacts, phase-exit sequence, stop rules, report fields, or the detail relocated out of `SKILL.md` is needed during phase work.

Use this contract when `he-phase-work` is keeping `he-work` alive across approved plan phases.
Do not substitute `he-phase-work` for stale evidence inside an approved phase
loop; stale phase evidence is a stop condition for `he-phase-heartbeat`.
Use `he-phase-work` only as the approved 10-minute wake-up mechanism for the
phase-work loop.

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

Ask for explicit approval or block before `external_write`, `destructive`, or
phase-boundary `git add` actions unless the user already granted that authority
for the exact target.

## Phase Exit Gate

For each phase:

1. Confirm the phase is approved, incomplete, reopened, or evidence-missing.
2. Confirm the changed diff belongs to that phase.
3. Run `simplify` over the phase diff.
4. Run the phase's required tests or validation command.
5. Run `he-fix-bugs` only when failing evidence exists.
6. Run `he-code-review` for readiness and traceability.
7. Record exact validation command outcomes.
8. Stage only completed-phase files with `git add` when local staging authority is explicit; otherwise report `git_staging_status: blocked` with the ready paths.
9. Update Linear or the tracker only when external-write authority is explicit; otherwise report `linear_update_status: blocked` with the prepared update text.
10. Set `slack_policy` to `none`, `bounded`, or `blocked`.
11. Commit only the completed phase diff, or report the blocker.

After the final phase, run `he-eval-report`, then `he-reinforce`, then
`he-reconcile`, and apply the same validation and staging boundaries to their
artifacts.

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
- git staging status,
- Linear or tracker update status,
- commit status,
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
- Search for an existing matching heartbeat before creating another one; use a 10-minute cadence unless the user gave a different explicit cadence, and include live checks, stop rules, reporting policy, and forbidden unattended actions.
- Keep the XP operating contract explicit by setting `slack_policy` to `none`, `bounded`, or `blocked`.
- For plugin-level confidence claims, run or require the HE lifecycle release eval lane across changed lifecycle skills plus adjacent route/work skills.
- Treat static Plugin Eval budget failures as blocking, excluded from the runtime claim, or assigned follow-up; do not hide them under strict audit success.
