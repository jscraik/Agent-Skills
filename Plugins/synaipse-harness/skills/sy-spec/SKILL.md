---
name: sy-spec
description: "Creates scoped SynAIpse Harness plugin and skill technical specs by turning approved intent into requirements, non-goals, affected files, acceptance criteria, validation commands, risks, rollback notes, and next-stage handoff. Use when the user asks to write a SynAIpse spec, clarify plugin or skill requirements, define stage acceptance criteria, prepare package implementation scope, or document a Harness replacement change before planning or coding."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Spec

## Philosophy

Convert approved intent into a buildable contract that separates what must
change, what must not change, how success is observed, and how rollback works.

## When to Use

Use this skill when intent is approved and the user needs a precise SynAIpse technical spec, plugin requirements doc, stage acceptance criteria, implementation scope, or plugin/skill change contract before planning, tracker work, or implementation. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-strategy` hands off to `sy-spec`.

## Inputs

Collect only the inputs needed to write a buildable spec:

- approved intent, user outcome, target plugin, skill, PR, issue, or repo area
- in-scope and out-of-scope files, commands, data, and external services
- current evidence from `git status --short --branch`, `rg`, existing artifacts, or user-provided context
- validation commands that will prove acceptance criteria and lanes they cannot prove

## Procedure

1. Confirm the spec boundary:
   - Record the approved intent, user outcome, target package or repo area, and explicit non-goals.
   - Run `git status --short --branch` and inspect only relevant files with `rg` or `rg --files` before claiming current structure.
2. Map affected surfaces:
   - List files, skill handles, plugin metadata, scripts, schemas, eval fixtures, artifacts, commands, external services, and tracker or PR lanes touched by the proposed change.
   - Mark each surface as `change`, `read_only`, `not_checked`, or `out_of_scope`.
3. Write observable requirements and acceptance criteria:
   - Use `given/when/then`, exact output fields, command outcomes, or artifact paths.
   - Avoid acceptance criteria such as `works well`, `is robust`, or `is production ready` without measurable evidence.
4. Define validation and evidence limits:
   - Include exact commands such as `./bin/ask skills audit <skill-path> --level strict --json --robot`, `plugin-eval analyze <plugin-path> --format json`, or the repo wrapper required by the target surface.
   - State what each command proves and what it does not prove, especially PR, CI, review, tracker, mergeability, or deployment lanes.
5. End with risks, rollback, and handoff:
   - Include `risks`, `rollback`, `blocked_inputs`, `next_stage`, and `handoff_notes`.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-spec`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `technical_specification`: the concrete stage deliverable
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

Input: "Use sy-spec for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-spec
target: JSC-244
decision: "Specify the SynAIpse router split"
deliverable:
  requirements:
    - "router plugin exposes one implicit sy-strategy skill"
    - "stage plugin exposes explicit-only stage skills"
  non_goals:
    - "retire harness-engineering in the same slice"
  acceptance:
    - "plugin eval grade is B+ or better for both packages"
    - "each stage skill Tessl review_score is greater than 90"
  validation_commands:
    - "plugin-eval analyze Plugins/synaipse-harness --format json"
    - "./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-strategy --audit-level compat --skip-plugin-eval --json --robot"
  rollback:
    - "leave harness-engineering installed until SynAIpse install and rollout acceptance are checked"
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
- A spec without measurable acceptance criteria is not ready for planning.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Writing implementation steps before requirements and acceptance criteria are clear.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Expanding the spec beyond approved intent.

## References

This skill is self-contained for normal spec writing. Open optional repo
references only when the spec needs contract, eval, benchmark, or source
provenance details:

- `references/contract.yaml`: compact stage contract.
- `references/evals.yaml`: strict audit and Tessl scenario coverage.
- `references/task-profile.json`: family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root`: preserved source
  material from the imported replacement package.
