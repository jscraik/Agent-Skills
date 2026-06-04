---
name: sy-strategy
description: "Creates SynAIpse Harness strategy briefs for plugin replacement, split-package rollout, skill hardening order, old-plugin retirement timing, and migration choices. Use when the user asks whether SynAIpse should replace Harness Engineering, ship as its own plugin first, split router and stages, retire an old package, or choose the next validation gate before planning."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Strategy

## Philosophy

Do one stage well, prove only what was checked, and leave the next agent a clear
handoff.

## When to Use

Use this skill when the user needs a strategic choice about SynAIpse package
replacement, rollout shape, stage split, hardening priority, or old-plugin
retirement. Natural triggers include "should SynAIpse replace Harness
Engineering", "ship it as its own plugin first", "split router and stages",
"retire the old package", and "choose the next proof gate". Use it only when
the user names this stage, invokes the skill explicitly, or `sy-router` hands
off to `sy-strategy`.

## Inputs

Collect only the inputs needed for this stage:

- decision question, target plugin or skill, issue, PR, file, artifact, or session
- approved scope and non-goals
- current repo evidence and validation artifacts
- external evidence checked in this run, if any

## Procedure

1. Inspect local evidence before deciding: run `git status --short --branch`
   and read the named spec, plugin manifest, skill, audit report, or validation
   artifact that frames the decision.
2. State one strategic question and the decision horizon, such as "choose the
   rollout shape before package validation" or "decide whether retirement is
   allowed after install proof".
3. Write the evidence summary in this exact lane format:
   `local_files: <checked|not_checked> - <paths or reason>`,
   `validation: <checked|not_checked> - <commands or reason>`,
   `pr_ci: <checked|not_checked> - <evidence or reason>`,
   `review_tracker_rollout: <checked|not_checked> - <evidence or reason>`.
4. Compare options in this exact matrix format:
   `option | leverage(high/med/low) | risk(high/med/low) | reversible(yes/no/partial) | time_to_proof | blocker | decision`.
   Include "wait and gather proof" when missing evidence could change the
   answer.
5. Pick one recommended option and write:
   `recommendation`, `why_now`, `rejected_options`, `non_goals`,
   `proof_required_before_retirement`, and `rollback_or_stop_condition`.
6. End with `next_stage`, the exact file, command, or external lane it must
   check, and the evidence that would change the recommendation.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-strategy`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `strategy_brief`: question, options, scoring, recommendation, non-goals, and stop condition
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

If the recommendation depends on authority, external writes, publication, or
closure proof, stop and ask for that missing input. If only a minor detail is
missing, proceed with a named assumption.

## Examples

Input: "Use sy-strategy to decide whether SynAIpse should replace Harness
Engineering now or ship as its own plugin first. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-strategy
target: JSC-244
decision: "Should SynAIpse replace Harness Engineering now or ship independently first?"
deliverable:
  options:
    - path: "replace harness-engineering immediately"
      leverage: "high"
      risk: "high because rollout and install proof are not checked"
      reversibility: "medium"
    - path: "ship SynAIpse as a separate plugin first"
      leverage: "high"
      risk: "lower because retirement remains reversible"
      reversibility: "high"
  recommendation: "validate separate plugin first, then retire only after install, eval, Tessl, and rollout proof"
  non_goals:
    - "retire harness-engineering before live rollout proof"
evidence_checked:
  - "git status --short --branch"
  - "local SynAIpse package files and validation artifacts"
validation:
  - "blocked: PR, CI, review, tracker, and install state were not checked in this run"
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

This skill is self-contained for normal SynAIpse strategy work. Open optional
repo references only when the decision depends on package contracts, eval
coverage, benchmark thresholds, or archived source behavior:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
