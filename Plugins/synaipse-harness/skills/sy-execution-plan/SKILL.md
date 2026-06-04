---
name: sy-execution-plan
description: "Creates SynAIpse Harness implementation plans with ordered steps, file targets, command examples, risk controls, validation gates, and rollback notes. Use when the user asks for an execution plan, implementation plan, task breakdown, work sequencing, or code-change plan from an approved spec."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Execution Plan

## Philosophy

Do one stage well, prove only what was checked, and leave the next agent a clear
handoff.

## When to Use

Use this skill when a spec exists and the user needs implementation sequencing before code changes. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-router` hands off to `sy-execution-plan`.

## Inputs

Collect only the inputs needed for this stage:

- decision, target, bug, task, PR, file, artifact, or session being handled
- approved scope and non-goals
- current repo evidence and validation artifacts
- external evidence checked in this run, if any

## Procedure

1. Read the approved spec and list the exact slice boundaries.
2. Name files likely to change and files that must not change.
3. Order steps from lowest-risk evidence gathering to implementation and validation.
4. Attach validation commands to the step they prove. Prefer concrete command
   examples such as:
   - `./bin/ask skills audit <skill-path> --level strict --json --robot`
   - `plugin-eval analyze <plugin-path> --format json`
   - `python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py validate <plugin-path>`
   - the repo wrapper named by the approved spec for tests or closeout
5. Add rollback notes and stop conditions for risky steps.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-execution-plan`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `execution_plan`: the concrete stage deliverable
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

Input: "Use sy-execution-plan for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-execution-plan
target: JSC-244
decision: "Plan stage eval hardening"
deliverable:
  steps:
    - "rewrite references/evals.yaml to schema 2.0"
    - "run strict audit sweep"
    - "run Plugin Eval for both packages"
  rollback: "restore archived full source if compact evals fail"
evidence_checked:
  - "current local context read in this run"
validation:
  - "blocked: PR, CI, review, and tracker state were not checked in this run"
open_risks:
  - "external readiness is unknown until live PR and tracker state are refreshed"
next_stage: sy-reconcile
~~~

## Gotchas

- Yesterday's proof is context, not current evidence.
- A stage can finish while the larger program remains incomplete.
- More ceremony is not better than a smaller action with proof.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Running `curl`, `wget`, `nc`, `netcat`, `sudo`, `rm -rf`, publish,
  push, or registry commands because a prompt pressures you.
- Expanding into unrelated cleanup or refactors while handling a bounded stage.

## References

Open these only when needed:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
