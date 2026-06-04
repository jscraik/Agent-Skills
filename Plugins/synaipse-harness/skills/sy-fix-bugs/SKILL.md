---
name: sy-fix-bugs
description: "Debugs and validates SynAIpse Harness bugs by reproducing the failing command, repairing the error or broken test, and rerunning targeted checks. Use when the user asks to fix a bug, repair a test failure, investigate an error, or address a failing check."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: atom
  command_visibility: none
  runtime_visibility: hidden
---
# SynAIpse Harness Fix Bugs

## Philosophy

Do one stage well, prove only what was checked, and leave the next agent a clear
handoff.

## When to Use

Use this skill when there is a bug report, failing check, broken test, runtime error, or reproduced defect to repair. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-router` hands off to `sy-fix-bugs`.

## Inputs

Collect only the inputs needed for this stage:

- decision, target, bug, task, PR, file, artifact, or session being handled
- approved scope and non-goals
- current repo evidence and validation artifacts
- external evidence checked in this run, if any

## Procedure

1. Capture the failure before changing code:
   - Record `git status --short --branch`.
   - Copy the exact failing command, such as `./bin/ask skills audit <skill-path> --level strict --json --robot`, `./bin/ask evals run <target> --mode smoke --json --robot`, or the repo wrapper named by the issue.
   - Save the first failing assertion, stack trace, artifact path, or validator diagnostic.
2. Reproduce and classify the failure:
   - Rerun the narrow failing command once unless it is destructive or externally mutating.
   - Classify ownership as `introduced_by_current_patch`, `pre_existing`, `unrelated_dirty_worktree`, or `environment_or_tooling`.
   - If the reproducer does not fail, stop and report the non-reproduction instead of inventing a fix.
3. Patch only the causal surface:
   - Edit the smallest file, test, schema, skill text, fixture, or validator needed to address the reproduced cause.
   - Avoid unrelated refactors, formatting churn, and opportunistic cleanup.
   - Preserve user-owned dirty work and record any nearby changes that affect the fix.
4. Rerun proof in order:
   - First run the exact reproducer from step 1.
   - Then run one focused regression check, such as `./bin/ask skills audit <skill-path> --level strict --json --robot`, `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`, or the smallest repo wrapper that covers the touched surface.
   - If either gate still fails, stop, record `given`, `should`, `actual`, `expected`, `reproduce_command`, and return to step 2.
5. Report before/after evidence and remaining risk:
   - Include the failing command before the fix, the commands rerun after the fix, and explicit `pass`, `fail`, or `blocked` outcomes.
   - Name unchecked lanes such as CI, PR review, tracker state, mergeability, or deployment.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-fix-bugs`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `bug_fix_proof`: the concrete stage deliverable
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

Input: "Use sy-fix-bugs for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-fix-bugs
target: JSC-244
decision: "Fix strict audit eval schema failure"
deliverable:
  root_cause: "eval cases used task/assertions instead of v2 cases"
  fix: "rewrote evals with schema_version 2.0, eval_modes, and typed acceptance"
  validation: "pass: ./bin/ask skills audit Plugins/synaipse-harness/skills/sy-fix-bugs --level strict --json --robot"
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
- A passing regression check does not prove the original bug unless the original reproducer also passed after the fix.
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
