---
name: sy-brainstorm
description: "Analyzes SynAIpse Harness plugin, router, stage, or retirement decisions by creating a decision matrix, scoring risk and reversibility, and recommending one next stage. Use when the user asks to compare lifecycle options, weigh pros and cons, brainstorm migration approaches, or decide which plugin path to take."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Brainstorm

## Philosophy

Do one stage well, prove only what was checked, and leave the next agent a clear
handoff.

## When to Use

Use this skill when the user asks to compare options, weigh pros and cons, brainstorm approaches, evaluate alternatives, find overlooked leverage, or decide which path to take before spec, plan, tracker work, or implementation. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-strategy` hands off to `sy-brainstorm`.

## Inputs

Collect only the inputs needed for this stage:

- decision, target, bug, task, PR, file, artifact, or session being handled
- approved scope and non-goals
- current repo evidence and validation artifacts
- external evidence checked in this run, if any

## Procedure

1. State the decision in one sentence.
2. List 3 to 5 candidate options, including the user's options first.
3. Score each option on evidence fit, effort, reversibility, blast radius,
   validation cost, and operator clarity using the anchors below.
4. Reject weak options with concrete reasons: missing evidence, high blast radius, unclear owner, duplicate scope, or no validation path.
5. Recommend one survivor option, one next stage, and the assumption that would change the recommendation.

Scoring anchors:

- `evidence_fit`: high means current repo or artifact evidence supports the
  option; medium means evidence is partial; low means the option is mostly
  speculative.
- `effort`: high means broad edits or coordination; medium means a focused
  slice; low means one small artifact or doc change.
- `reversibility`: high means rollback is simple; medium means rollback needs
  coordination; low means replacement or migration risk is hard to undo.
- `blast_radius`: high touches shared routing or installs; medium touches one
  package; low touches one skill or reference.
- `validation_cost`: high needs multiple live lanes; medium needs local audit
  plus one external review; low has one deterministic check.
- `operator_clarity`: high is easy to explain and resume; medium needs a
  handoff; low creates routing or ownership confusion.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-brainstorm`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `decision_matrix`: the concrete stage deliverable
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

Input: "Use sy-brainstorm for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-brainstorm
target: JSC-244
decision: "How to introduce SynAIpse Harness"
deliverable:
  survivor: "Separate plugin, validate it, then retire harness-engineering after rollout acceptance"
  rejected:
    - "Direct replacement: low reversibility until install and rollout proof exist"
    - "Keep both forever: creates long-term routing ambiguity"
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
