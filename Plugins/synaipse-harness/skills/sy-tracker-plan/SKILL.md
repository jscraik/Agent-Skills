---
name: sy-tracker-plan
description: "Converts approved SynAIpse Harness specs, trace maps, or replacement plans into small tracker-ready tasks with owners, dependencies, acceptance criteria, validation commands, evidence fields, and non-goals. Use when the user asks for Linear tasks, a tracker plan, a task breakdown, ticket-ready work, or a plugin hardening plan prepared without creating tracker issues."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Tracker Plan

## Philosophy

Do one stage well, prove only what was checked, and leave the next agent a clear
handoff.

## When to Use

Use this skill when the user wants tracker-ready work items from an approved
spec, trace plan, replacement decision, or implementation plan. Natural
triggers include "Linear tasks", "tracker plan", "break this into tickets",
"task breakdown", "ticket-ready", and "execution tracking". Use it only when
the user names this stage, invokes the skill explicitly, or `sy-router` hands
off to `sy-tracker-plan`.

## Inputs

Collect only the inputs needed for this stage:

- approved spec, trace plan, strategy decision, issue, plugin, skill, PR, or artifact
- approved scope and non-goals
- current repo evidence and validation artifacts
- external evidence checked in this run, if any

## Procedure

1. Read the approved source before drafting tasks. Check current local context
   with `git status --short --branch` and read the named spec, trace map,
   package path, or `SKILL.md` files.
2. Extract only approved work. Put suspected extras into `out_of_scope`
   instead of turning them into tasks.
3. Split tasks so each has one owner, one outcome, one dependency posture, one
   validation path, and one closeout artifact.
4. Order tasks by dependency, risk, and fastest proof. Mark blockers before
   downstream work so tracker readers do not start hidden prerequisite work.
5. Write acceptance criteria as observable outcomes, not intent. Include exact
   commands when known, such as `./bin/ask skills audit <skill-dir> --level strict --json --robot`,
   `./bin/ask skills external-review <skill-dir> --audit-level compat --skip-plugin-eval --json --robot`,
   and `plugin-eval analyze <plugin-path> --format json`.
6. Do not create, update, close, assign, or comment on tracker issues unless
   the user explicitly authorizes tracker mutation in the current request.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-tracker-plan`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `tracker_task_plan`: ticket-ready tasks with dependency, owner, acceptance criteria, proof, and non-goals
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

Input: "Use sy-tracker-plan to break the SynAIpse replacement validation into
ticket-ready tasks. Do not create Linear issues yet."

Output:
~~~yaml
schema_version: 1
stage: sy-tracker-plan
target: JSC-244
decision: "Prepare tracker tasks for plugin hardening"
deliverable:
  tasks:
    - title: "Harden router skill"
      owner: "router package"
      dependency: "plugin skeleton exists"
      acceptance_criteria:
        - "strict audit passes"
        - "Plugin Eval grade is B+ or higher"
        - "Tessl review_score is greater than 90"
      proof: "strict audit, Plugin Eval JSON, Tessl external-review JSON"
    - title: "Harden stage plugin"
      owner: "stage package"
      dependency: "stage skill files exist with compact references"
      acceptance_criteria:
        - "every stage skill strict audit passes"
        - "every stage skill Tessl review_score is greater than 90"
      proof: "strict audit sweep plus per-skill Tessl reports"
  tracker_mutation: "blocked: user did not authorize creating issues"
evidence_checked:
  - "git status --short --branch"
  - "local SynAIpse skill and package paths"
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

This skill is self-contained for normal SynAIpse tracker planning. Open optional
repo references only when a task depends on package contracts, eval coverage,
benchmark thresholds, or archived source behavior:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
