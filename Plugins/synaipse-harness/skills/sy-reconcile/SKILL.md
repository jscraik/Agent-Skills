---
name: sy-reconcile
description: "Produces a SynAIpse Harness readiness report by checking local worktree, validation, PR, CI, review threads, tracker status, artifacts, and sessions as separate evidence lanes, then identifying blockers and the next stage. Use when the user asks to check status, see what is blocking a PR, verify merge readiness, summarize CI/review state, or reconcile conflicting progress claims."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
---
# SynAIpse Harness Reconcile

## Philosophy

Keep local proof, PR state, CI, reviews, tracker, artifacts, and merge readiness
as separate lanes so one passing surface cannot falsely close another.

## When to Use

Use this skill when the user needs truthful status across local and external evidence surfaces, asks what is blocking work, asks whether a PR is ready to merge, or needs conflicting progress claims reconciled. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-router` hands off to `sy-reconcile`.

## Inputs

Collect only the inputs needed to refresh evidence lanes:

- target repo, branch, PR, issue, artifact, or session
- lanes that matter: local, validation, PR, CI, review threads, tracker, artifacts, sessions, mergeability
- authority for external checks such as `gh pr view`, `gh pr checks`, or tracker reads
- latest local artifacts and commands already run

## Procedure

1. List the evidence lanes needed for the objective:
   - Use `local_worktree`, `local_validation`, `plugin_eval`, `tessl`, `artifact`, `PR`, `CI`, `review_thread`, `tracker`, `session`, and `mergeability` when relevant.
   - Mark lanes outside current authority as `not_checked`, not `pass`.
2. Refresh authorized lanes with concrete checks:
   - Local state: `git status --short --branch` and `git diff --stat`.
   - Local validation: rerun or read the exact command output named by the user, such as `./bin/ask skills audit <skill-path> --level strict --json --robot`.
   - Plugin quality: `plugin-eval analyze <plugin-path> --format json` or the saved report path.
   - Tessl: read `Infrastructure/artifacts/skill-reviews/<skill>-external-review.json` and record `review_score`.
   - PR and CI, when authorized: `gh pr view <number> --json state,mergeable,reviewDecision,reviewThreads` and `gh pr checks <number> --watch=false`.
3. Record each lane as `pass`, `fail`, `blocked`, `stale`, or `not_checked` with evidence references.
4. Resolve contradictions lane by lane:
   - Prefer live command output over old summaries.
   - Prefer current artifact contents over mailbox text.
   - Do not let local validation prove PR, CI, review, tracker, or mergeability.
5. Recommend the next stage based on the weakest required lane:
   - Use `sy-fix-bugs` for failing validation, `sy-work` for implementation gaps, `sy-eval-report` for closure proof, or `sy-heartbeat` for a pause/resume checkpoint.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-reconcile`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `reconciliation_report`: the concrete stage deliverable
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

Input: "Use sy-reconcile for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-reconcile
target: JSC-244
decision: "Can the replacement retire harness-engineering?"
deliverable:
  lanes:
    local_worktree: "pass: git status --short --branch checked"
    plugin_eval: "pass: plugin-eval analyze Plugins/synaipse-harness --format json"
    tessl: "fail: sy-reconcile review_score 78"
    PR: "not_checked: no PR number provided"
    CI: "not_checked: no PR number provided"
    tracker: "not_checked: no tracker authority in this run"
  next_stage: "sy-work"
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
- A passing local lane cannot prove PR, CI, review, tracker, or mergeability.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Treating old summaries as current lane evidence.
- Mutating PRs, trackers, or external services while reconciling status.

## References

This skill is self-contained for normal readiness reconciliation. Open optional
repo references only when the lane report needs contract, eval, benchmark, or
source provenance details:

- `references/contract.yaml`: compact stage contract.
- `references/evals.yaml`: strict audit and Tessl scenario coverage.
- `references/task-profile.json`: family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root`: preserved source
  material from the imported replacement package.
