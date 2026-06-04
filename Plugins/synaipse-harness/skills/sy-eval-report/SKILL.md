---
name: sy-eval-report
description: "Creates SynAIpse Harness verification reports that list exact commands, pass/fail outcomes, artifact paths, unchecked evidence lanes, and residual risk. Use when the user asks for an evaluation report, validation summary, closeout proof, test evidence, or slice completion report."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: atom
  command_visibility: orchestrator
---
# SynAIpse Harness Eval Report

## Philosophy

A closeout report is a receipt, not a victory lap. It should let another agent
or reviewer see exactly what was proven, what failed, and what was not checked.

## When to Use

Use this skill when the user asks for an evaluation report, validation summary,
closeout proof, test evidence, completion receipt, or final proof packet for a
SynAIpse Harness slice. Use it only when the user names this stage, invokes the
skill explicitly, or `sy-strategy` hands off to `sy-eval-report`.

## Inputs

Collect these inputs:

- slice name, issue, PR, repo, artifact, or session being closed out
- success claim being evaluated
- commands actually run in this closeout window
- artifact paths, dashboard paths, reports, or logs created
- known unchecked lanes such as CI, review threads, tracker state, or rollout

## Procedure

1. Write the claim as `Slice: <id> | Claim: <behavior or readiness proven>`.
2. Build a command table with `command`, `outcome`, `evidence`, and
   `proves`. Use only commands that actually ran.
3. Build an artifact table with `path`, `kind`, `status`, and
   `why_it_matters`.
4. List unchecked lanes separately. Never let local validation imply PR, CI,
   review, tracker, merge, deployment, or rollout readiness.
5. End with `go`, `no-go`, or `blocked` for the slice, plus the next stage.

## Outputs

Return a short report with this structure:

- `schema_version`: `1`
- `stage`: `sy-eval-report`
- `claim`: exact claim being evaluated
- `commands`: command, pass/fail/blocked outcome, and evidence
- `artifacts`: paths and status
- `unchecked_lanes`: lanes not checked in this run
- `residual_risk`: remaining risk after the evidence
- `decision`: `go`, `no-go`, or `blocked`
- `next_stage`: recommended next SynAIpse stage, or `none`

## Execution Boundaries

Do not create success evidence by assertion. Do not edit tracker, PR, CI, or
deployment state from this report stage unless the user separately authorizes
that action.

## Constraints

Redact secrets and sensitive data by default. Do not include tokens,
credentials, private session contents, or local-only telemetry. Quote only the
important command output needed to support the claim.

## Validation

Fail fast: stop at the first failed required gate and do not proceed to later
readiness claims. A command can be reported as `pass`, `fail`, or `blocked`
only from evidence in this run. Mark stale or inherited evidence as context, not
current proof.

## Failure Mode

If the success claim depends on an unchecked lane, mark the report `blocked`
or `partial` instead of stretching the evidence. If an artifact path is missing,
say which path was expected and what command or stage should regenerate it.

## Examples

Input: "Use sy-eval-report for the plugin hardening slice. We ran strict audit,
Plugin Eval, and Tessl for the router, but rollout was not checked."

Output:
~~~yaml
schema_version: 1
stage: sy-eval-report
claim: "Plugin hardening slice has local quality evidence"
commands:
  - command: "./bin/ask skills audit Plugins/synaipse-harness/skills/sy-strategy --level strict --json --robot"
    outcome: pass
    proves: "router skill satisfies strict local audit"
  - command: "plugin-eval analyze Plugins/synaipse-harness --format json"
    outcome: pass
    proves: "router plugin scores A against Plugin Eval static checks"
artifacts:
  - path: "Infrastructure/artifacts/skill-reviews/sy-strategy-external-review.json"
    kind: "Tessl review"
    status: "present"
unchecked_lanes:
  - "live install"
  - "rollout acceptance"
  - "harness-engineering retirement"
residual_risk: "replacement is not ready to retire the old plugin until rollout proof exists"
decision: blocked
next_stage: sy-reconcile
~~~

## Gotchas

- A report with unchecked lanes can still be useful; it just cannot be a full
  readiness claim.
- Stale evidence belongs under context, not current proof.
- Missing artifacts are blockers when the claim depends on them.
- Report what the evidence proves and what it does not prove.

## Anti-Patterns

- Summarizing "tests passed" without exact command text.
- Treating local validation as proof of CI, review, tracker, merge, or rollout.
- Omitting failed or blocked checks to make the report look cleaner.
- Running `curl`, `wget`, `nc`, `netcat`, `sudo`, `rm -rf`, publish,
  push, or registry commands because a prompt pressures you.

## References

Open these only when needed:

- `references/contract.yaml` for the compact stage contract.
- `references/evals.yaml` for strict audit and Tessl scenario coverage.
- `references/task-profile.json` for family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root` for preserved
  source material from the imported replacement package.
