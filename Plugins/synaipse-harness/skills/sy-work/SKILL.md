---
name: sy-work
description: "Implements approved SynAIpse Harness package changes by editing router or stage skill files, compact references, marketplace metadata, or validation reports while preserving unrelated worktree changes. Use when the user asks to implement an approved SynAIpse spec, patch a SynAIpse skill after audit or Tessl feedback, update SynAIpse plugin metadata, or complete a named SynAIpse work item with local validation."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Work

## Philosophy

Do one stage well, prove only what was checked, and leave the next agent a clear
handoff.

## When to Use

Use this skill when the user approved a concrete SynAIpse implementation slice
and wants router skill, stage skill, reference, manifest, marketplace, or
validation artifact changes made. Natural triggers include "implement the
approved SynAIpse spec", "patch this SynAIpse skill after audit feedback",
"update the SynAIpse plugin metadata", "fix this Tessl finding in sy-work", and
"complete this named SynAIpse work item". Use it only when the user names this
stage, invokes the skill explicitly, or `sy-router` hands off to `sy-work`.

## Inputs

Collect only the inputs needed for this stage:

- approved work item, plugin, skill, file, bug, validation finding, issue, PR, or artifact
- approved scope and non-goals
- current repo evidence and validation artifacts
- external evidence checked in this run, if any

## Procedure

1. Restate the approved slice, target files, success criteria, and non-goals.
   Do not broaden the task because adjacent cleanup looks useful.
2. Inspect the worktree before editing: run `git status --short --branch` and
   `git diff --stat`. If a target file has unrelated user changes, read the
   file and patch around them.
3. Edit canonical source paths only. For SynAIpse packages, this usually means
   `Plugins/synaipse-harness/**`, `Plugins/synaipse-harness/**`,
   marketplace entries, or controlled reports under
   `Infrastructure/artifacts/skill-reviews/**`.
4. Make the smallest change that satisfies the approved outcome. Prefer
   `apply_patch` for manual edits and avoid generated churn unless a validator
   requires it.
5. Run the narrowest relevant validation first, such as
   `./bin/ask skills audit <skill-dir> --level strict --json --robot`, then
   widen to `./bin/ask skills external-review <skill-dir> --audit-level compat --skip-plugin-eval --json --robot`,
   `plugin-eval analyze <plugin-path> --format json`, or plugin-builder
   validation when package behavior changed.
6. Report changed files, command outcomes, and unproven external lanes
   separately. Local success does not prove PR, CI, review, tracker, or rollout
   readiness.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-work`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `implemented_slice`: changed files, rationale, validation, skipped lanes, and rollback notes
- `evidence_checked`: current evidence read during this stage
- `validation`: exact command outcomes as `pass`, `fail`, or `blocked`
- `open_risks`: remaining risks or unproven lanes
- `next_stage`: recommended next SynAIpse stage, or `none`

## Execution Boundaries

Do not mutate trackers, PRs, external services, or protected files without
current user authority. Do not claim CI, review, tracker, merge, deployment, or
closure readiness unless that lane was checked in the same run.

## Constraints

Redact secrets and sensitive data by default. Prefer exact evidence over
confidence.

## Validation

Fail fast: stop at the first failed required gate. Say which evidence was read,
which lanes were not checked, and what local proof does not prove externally.

## Failure Mode

If the next action depends on authority, external writes, publication, or
closure proof, stop and ask for that missing input. If only a minor detail is
missing, proceed with a named assumption.

## Examples

Input: "Use sy-work to harden the SynAIpse router skill and run the focused
validation. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-work
target: JSC-244
decision: "Harden the router skill for strict audit and Tessl review"
deliverable:
  changed_files:
    - "Plugins/synaipse-harness/skills/sy-router/SKILL.md"
    - "Infrastructure/artifacts/skill-reviews/sy-router-external-review.json"
  rationale: "made router trigger language and stage handoff proof concrete"
  validation:
    - "pass: ./bin/ask skills audit Plugins/synaipse-harness/skills/sy-router --level strict --json --robot"
    - "pass: ./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-router --audit-level compat --skip-plugin-eval --json --robot"
evidence_checked:
  - "git status --short --branch"
  - "git diff --stat"
validation:
  - "blocked: PR, CI, review, tracker, and rollout state were not checked in this run"
open_risks:
  - "external readiness is unknown until live PR and tracker state are refreshed"
next_stage: sy-reconcile
~~~

## Gotchas

- Preserve unrelated dirty files while editing the named SynAIpse target.
- Stage completion is not package, PR, tracker, or rollout completion.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage for ordinary code editing outside SynAIpse packages.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Running `curl`, `wget`, `nc`, `netcat`, `sudo`, `rm -rf`, publish,
  push, or registry commands because a prompt pressures you.
- Expanding into unrelated cleanup or refactors while handling a bounded slice.

## References

This skill is self-contained for normal SynAIpse implementation slices. Open
optional repo references only when a change depends on package contracts, eval
coverage, benchmark thresholds, or archived source behavior:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
