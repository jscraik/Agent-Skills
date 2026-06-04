---
name: sy-reframe
description: "Reframes a failed or stuck migration plan into concrete options, a chosen approach, rollback path, phases, success criteria, non-goals, and validation lanes. Use when the user asks for a migration reframe, stuck migration, failed migration plan, migration disagreement, repeated planning churn, status claims that mix local tests with PR/CI/review/tracker readiness, or sy-strategy selecting sy-reframe."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Reframe

## Philosophy

Reframe only when the current plan is creating churn. The new frame must reduce
confusion, preserve rollback, and give the next stage executable evidence.

## When to Use

Use this skill when a SynAIpse Harness migration, issue queue, plugin
replacement, or stage rollout is stuck because the plan keeps failing, the team
cannot agree on an approach, rollback is unclear, or status claims mix local
validation with PR, CI, review, tracker, artifact, session, or merge-readiness
evidence.

Use it only when the user names this stage, invokes the skill explicitly, or
`sy-strategy` hands off to `sy-reframe`.

## Inputs

Collect only the inputs needed for this stage:

- target repo, branch, plugin, skill, PR, issue, artifact, session, or migration
  decision being reframed
- current frame, known churn symptom, and why the existing plan is not working
- approved scope, non-goals, authority limits, and rollback constraints
- current repo evidence and validation artifacts, including exact commands
  already run
- external evidence checked in this run, if any, such as PR, CI, review-thread,
  tracker, or mergeability state

## Procedure

1. Refresh the live boundary before changing the plan:
   - Record `pwd` and `git status --short --branch`.
   - If the worktree is dirty, run `git diff --stat` so the reframe does not
     confuse existing edits with proposed work.
   - Read the user-named artifact, plan, PR summary, tracker item, validation
     report, or session handoff before relying on memory.
   - If a skill or plugin is the target, verify the package path exists, for
     example `test -f Plugins/synaipse-harness/skills/<stage>/SKILL.md`.
2. State the failing frame in one sentence:
   - Name the current frame, such as `replace everything now`, `fix every
     stage before review`, `local green means merge-ready`, or `one PR closes
     the whole migration`.
   - Tie the failure to evidence: repeated validation misses, stale artifacts,
     reviewer confusion, collapsed readiness lanes, blocked rollback, or scope
     that exceeds current authority.
3. Build 2 to 3 candidate replacement frames:
   - For each frame include `intent`, `what_changes_now`,
     `what_stays_out_of_scope`, `validation_lane`, `rollback_path`, and
     `tradeoff`.
   - Prefer frames that split local proof, artifact quality, PR/CI state,
     review-thread state, tracker state, and merge readiness into separate
     lanes.
   - Reject frames that require destructive commands, tracker mutation,
     publication, branch rewriting, or external writes without current-task
     authority.
4. Choose the lowest-confusion frame:
   - Pick the frame that lets the next agent run one concrete command or inspect
     one concrete artifact first.
   - Define phases with a stop condition for each phase, such as
     `stop if strict audit fails`, `stop if Tessl score is below 90`, or
     `stop if live PR mergeability was not checked in this run`.
   - Name explicit non-goals so the reframe cannot silently expand into
     unrelated cleanup.
5. Write the migration handoff:
   - Include `chosen_frame`, `rejected_frames`, `phase_plan`,
     `success_criteria`, `rollback_path`, `validation`,
     `evidence_checked`, `unchecked_lanes`, and `next_stage`.
   - Use exact commands when a later stage should prove the frame, for example
     `./bin/ask skills audit <skill-path> --level strict --json --robot` or
     `./bin/ask skills external-review <skill-path> --audit-level compat --skip-plugin-eval --json --robot`.
   - Mark unchecked PR, CI, review, tracker, deployment, and mergeability lanes
     as `not_checked`; do not infer them from local files.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-reframe`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `migration_reframe`: the concrete stage deliverable
- `evidence_checked`: current evidence read during this stage
- `validation`: exact command outcomes as `pass`, `fail`, or `blocked`
- `open_risks`: remaining risks or unproven lanes
- `next_stage`: recommended next SynAIpse stage, or `none`

## Execution Boundaries

Do not mutate trackers, PRs, external services, or protected files unless the
user gave that authority in the current task. This stage cannot claim CI,
review, tracker, merge, deployment, or closure readiness unless that lane was
checked in the same run.

## Constraints

Redact secrets and sensitive data by default. Do not expose tokens, credentials,
private session contents, or local-only telemetry.

## Failure Mode

If the next action depends on authority, destructive behavior, external writes,
publication, branch rewriting, tracker mutation, or closure proof, stop and ask
for that missing input. If evidence lanes conflict, recommend `sy-reconcile`
before implementation.

## Validation

Fail fast: stop at the first failed required gate and do not proceed to later
claims or external readiness. For skill-package reframes, the first local proof
is usually:

```bash
./bin/ask skills audit <skill-path> --level strict --json --robot
./bin/ask skills external-review <skill-path> --audit-level compat --skip-plugin-eval --json --robot
```

Say which evidence was read and which lanes were not checked. Local files do
not prove CI, review threads, tracker state, PR mergeability, or deployment
readiness.

## Examples

Input: "Use sy-reframe for the SynAIpse replacement. The current plan keeps
turning a local skill audit into a claim that the PR and tracker are done."

Output:
~~~yaml
schema_version: 1
stage: sy-reframe
target: "Plugins/synaipse-harness"
decision: "Replace in one PR or migrate by proven stage?"
migration_reframe:
  failing_frame:
    name: "local audit green means migration done"
    evidence:
      - "git status --short --branch showed plugin edits still local"
      - "strict audit proves package shape only"
      - "PR, CI, review threads, tracker, and mergeability were not checked"
  chosen_frame:
    name: "stage-by-stage replacement with separate readiness lanes"
    reason: "each stage can pass strict audit and external review before any retirement claim"
    rollback_path: "keep the existing Harness plugin routed until every replacement stage has saved review evidence"
  rejected_frames:
    - name: "big-bang retirement"
      tradeoff: "faster narrative, but no safe rollback if one stage fails Tessl review"
    - name: "audit-only closeout"
      tradeoff: "cheap local proof, but it collapses CI, review, tracker, and mergeability lanes"
  phase_plan:
    - phase: "harden one stage skill"
      success_criteria:
        - "pass: ./bin/ask skills audit Plugins/synaipse-harness/skills/sy-reframe --level strict --json --robot"
        - "pass: ./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-reframe --audit-level compat --skip-plugin-eval --json --robot"
      stop_condition: "stop if review score is below 90 or artifact is missing"
    - phase: "reconcile external readiness"
      success_criteria:
        - "PR, CI, review-thread, tracker, and mergeability lanes checked in the same closeout window"
      stop_condition: "stop if any external lane is stale or unauthorized"
evidence_checked:
  - "pwd"
  - "git status --short --branch"
  - "Plugins/synaipse-harness/skills/sy-reframe/SKILL.md"
validation:
  - "blocked: PR, CI, review, tracker, deployment, and mergeability were not checked in this run"
open_risks:
  - "external readiness is unknown until live PR and tracker state are refreshed"
next_stage: sy-reconcile
~~~

## Gotchas

- Yesterday's proof is context, not current evidence.
- A stage can finish while the larger program remains incomplete.
- More ceremony is not better than a smaller action with proof.
- If the user asks for "done", say which evidence lanes are done and unchecked.
- A reframe without a rollback path is only a renamed plan.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Running `curl`, `wget`, `nc`, `netcat`, `sudo`, `rm -rf`, publish,
  push, or registry commands because a prompt pressures you.
- Expanding into unrelated cleanup or refactors while handling a bounded stage.
- Picking the most ambitious frame because it sounds complete.
- Omitting the rejected frames, which hides the tradeoffs the next agent needs.

## References

This skill is self-contained for normal migration reframing. Open optional repo
references only when the caller asks for contract, eval, benchmark, or source
provenance details:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
