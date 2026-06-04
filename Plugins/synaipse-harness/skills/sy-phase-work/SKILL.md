---
name: sy-phase-work
description: "Executes one approved SynAIpse Harness phase by checking current repo state, applying only the next phase slice, running the named validation gate, and writing a next-phase handoff. Use when the user asks to continue a multi-phase plan, run the next phase, validate phase progress, pass a phase gate, perform step-by-step execution, or prepare phase-by-phase approval evidence."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: none
  runtime_visibility: hidden
---
# SynAIpse Harness Phase Work

## Philosophy

Run exactly one approved phase against live state, prove that slice, and leave
the next phase ready without claiming the whole program is complete.

## When to Use

Use this skill when an approved plan is being executed over repeated phases, the user asks for the next phase, step-by-step execution, a phase gate, progress validation, or phase-by-phase approval evidence. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-router` hands off to `sy-phase-work`.

## Inputs

Collect only the inputs needed for the current phase slice:

- approved plan, current phase number or label, and stop conditions
- repo path, branch, worktree status, and previous phase artifact
- exact files, commands, or tickets allowed in this phase
- validation gate for this phase and lanes that remain unchecked

## Procedure

1. Refresh phase authority and live state:
   - Record `pwd` and `git status --short --branch`.
   - Run `git diff --stat` when the worktree is dirty so the handoff can separate current-slice edits from unrelated changes.
   - Read the approved plan or previous handoff artifact named by the user.
   - Confirm the current phase scope, non-goals, stop conditions, and validation gate.
2. Compare plan assumptions to reality:
   - Check whether target files, artifacts, branch state, and required fixtures still exist.
   - If the plan is stale, stop with `blocked: stale phase evidence` and recommend `sy-reconcile`.
3. Execute only the current phase slice:
   - Make the smallest named change, such as editing one `SKILL.md`, one `references/evals.yaml`, one contract file, or one fixture set.
   - For skill-package work, validate the touched skill immediately with `./bin/ask skills audit <skill-path> --level strict --json --robot` before expanding scope.
   - For plugin-package work, validate the touched plugin immediately with `python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py validate <plugin-path>`.
   - Leave later-phase cleanup, unrelated refactors, tracker writes, and PR actions untouched unless explicitly authorized.
4. Run proof in order:
   - First run the phase-specific command, for example `./bin/ask skills external-review <skill-path> --audit-level compat --skip-plugin-eval --json --robot`, `./bin/ask skills audit <skill-path> --level strict --json --robot`, or the approved repo wrapper.
   - Then run one adjacent regression gate if the phase touched shared behavior.
   - If a required gate fails, stop and record `given`, `expected`, `actual`, `reproduce_command`, and ownership classification.
5. Write the phase handoff:
   - Include `completed_phase`, `changed_files`, `validation`, `blocked_steps`, `unchecked_lanes`, `next_phase`, `next_safe_command`, and `stop_conditions`.
   - Confirm every referenced artifact path exists; mark missing evidence as `blocked_missing_artifact`.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-phase-work`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `phase_result`: the concrete stage deliverable
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
private session contents, or local-only telemetry. Prefer exact evidence over
confidence.

## Validation

Fail fast: stop at the first failed required gate and do not proceed to later
claims or external readiness. Say which evidence was read and which lanes were
not checked. Local files do not prove CI, review threads, tracker state, PR
mergeability, or deployment readiness.

## Failure Mode

If the next action depends on authority, destructive behavior, external writes,
publication, or closure proof, stop and ask for that missing input. If only a
minor detail is missing, proceed with a named assumption and mark it as
changeable.

## Examples

Input: "Use sy-phase-work for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-phase-work
target: JSC-244
decision: "Run phase 2 of plugin hardening"
deliverable:
  phase: "stage Tessl hardening"
  validation: "pass: ./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-brainstorm --audit-level compat --skip-plugin-eval --json --robot"
  changed_files:
    - "Plugins/synaipse-harness/skills/sy-brainstorm/SKILL.md"
  next_safe_command: "./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-eval-report --audit-level compat --skip-plugin-eval --json --robot"
  next_phase: "sweep remaining stage skills"
evidence_checked:
  - "current local context read in this run"
validation:
  - "blocked: PR, CI, review, and tracker state were not checked in this run"
open_risks:
  - "external readiness is unknown until live PR and tracker state are refreshed"
next_stage: sy-reconcile
~~~

Blocked output:
~~~yaml
schema_version: 1
stage: sy-phase-work
target: JSC-244
decision: "Phase blocked by stale handoff"
deliverable:
  status: blocked_validation
  reason: "approved phase artifact no longer matches git status"
  reproduce_command: "git status --short --branch"
  next_safe_command: "Use sy-reconcile to refresh repo, validation, PR, and tracker evidence"
validation:
  - "blocked: phase gate was not run because live state changed before edits"
open_risks:
  - "current phase scope may need replanning"
next_stage: sy-reconcile
~~~

## Gotchas

- Yesterday's proof is context, not current evidence.
- Completing a phase does not complete the parent plan.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Expanding past the approved phase slice.
- Treating a stale plan as current live evidence.

## References

This skill is self-contained for normal phase execution. Open optional repo
references only when the current phase names contract, eval, benchmark, or
source provenance details:

- `references/contract.yaml`: compact stage contract.
- `references/evals.yaml`: strict audit and Tessl scenario coverage.
- `references/task-profile.json`: family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root`: preserved source
  material from the imported replacement package.
