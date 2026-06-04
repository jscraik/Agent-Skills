---
name: sy-heartbeat
description: "Creates SynAIpse Harness status checkpoints and resume packets by recording current state, checked evidence, stop conditions, and the next safe command. Use when the user wants to save progress, pause work, schedule a follow-up, resume later, or hand off a long-running task."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: atom
  command_visibility: none
  runtime_visibility: hidden
---
# SynAIpse Harness Heartbeat

## Philosophy

Make later continuation safe by preserving exact state, authority, blockers,
commands, artifacts, and unchecked evidence lanes.

## When to Use

Use this skill when the user wants a future checkpoint, monitor, reminder, status check, pause-and-resume note, or continuation packet. Use it only when the user names this stage,
invokes the skill explicitly, or `sy-router` hands off to `sy-heartbeat`.

## Inputs

Collect only the inputs needed to make the resume packet executable:

- current objective, repo, branch, worktree, and active stage
- latest checked artifact paths and validation command outcomes
- authorized checkpoint trigger or explicit no-scheduling boundary
- lanes checked in this run and lanes intentionally left unchecked

## Procedure

1. Capture current state with evidence, not memory alone:
   - Record `pwd`, `git status --short --branch`, and the active branch or worktree.
   - Read the latest relevant artifact, such as `.harness/audits/<date>-*.md`, `Infrastructure/artifacts/skill-reviews/<skill>-external-review.json`, or the user-named handoff file.
   - If external state matters, record whether PR, CI, review, tracker, or deployment lanes were checked in this run.
2. Define the checkpoint trigger:
   - Use a concrete time, condition, or next event such as `after Tessl sweep completes`, `when PR checks finish`, `tomorrow 09:00`, or `after user approves rollout`.
   - If no trigger is authorized, write a resume packet only and mark scheduling as `blocked: no automation authority`.
3. List stop conditions that prevent automatic continuation:
   - Include worktree drift, failed validation, missing permissions, conflicting user instruction, stale tracker state, or destructive/external write requirements.
4. Write a resume packet with these fields:
   - `repo`, `branch`, `objective`, `last_completed_step`, `current_blocker`, `artifacts`, `commands_to_rerun`, `unchecked_lanes`, `stop_conditions`, and `next_safe_command`.
   - Use exact paths and commands, for example `./bin/ask skills external-review <skill-path> --audit-level compat --skip-plugin-eval --json --robot`.
5. Validate the packet before claiming it is usable:
   - Confirm every referenced artifact path exists or mark it `missing`.
   - Confirm every next command is non-destructive and within current authority.
   - Do not create, update, or schedule automation unless the user explicitly authorized that write.

## Outputs

Return concise prose unless the caller requests JSON. Include these fields when
a structured handoff is useful:

- `schema_version`: `1`
- `stage`: `sy-heartbeat`
- `target`: repo, PR, issue, file, artifact, or session being handled
- `heartbeat_packet`: the concrete stage deliverable
- `evidence_checked`: current evidence read during this stage
- `validation`: exact command outcomes as `pass`, `fail`, or `blocked`
- `open_risks`: remaining risks or unproven lanes
- `next_stage`: recommended next SynAIpse stage, or `none`

## Execution Boundaries

Do not mutate trackers, PRs, external services, automations, or protected files
unless the user gave that authority in the current task. Creating a resume
packet is allowed; scheduling or sending it requires explicit write authority.

## Constraints

Redact secrets and sensitive data by default. Do not expose tokens, credentials,
private session contents, or local-only telemetry. Prefer exact artifact paths
and command outcomes over confidence.

## Validation

Fail fast: stop at the first failed required gate and do not proceed to later
claims or external readiness. Local files do not prove CI, review threads,
tracker state, PR mergeability, or deployment readiness.

## Failure Mode

If scheduling, external writes, or closure proof need authority that is missing,
return `blocked: missing authority` and provide the resume packet only.

## Examples

Input: "Use sy-heartbeat for JSC-244. Keep evidence lanes separate."

Output:
~~~yaml
schema_version: 1
stage: sy-heartbeat
target: JSC-244
decision: "Checkpoint plugin eval hardening"
deliverable:
  resume_packet:
    next_check: "rerun Tessl sweep after stage rewrites"
    next_safe_command: "./bin/ask skills external-review Plugins/synaipse-harness/skills/sy-heartbeat --audit-level compat --skip-plugin-eval --json --robot"
    artifacts:
      - "Infrastructure/artifacts/skill-reviews/sy-heartbeat-external-review.json"
    unchecked_lanes:
      - "PR, CI, review, tracker, and deployment state"
    stop_conditions:
      - "worktree changes outside plugin scope"
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
- A checkpoint is useful only if the next agent can rerun the named command.
- If the user asks for "done", say which evidence lanes are done and unchecked.

## Anti-Patterns

- Picking this stage from a vague request without router evidence.
- Claiming CI, review, tracker, or merge readiness from local files alone.
- Scheduling automation without explicit current-task authority.
- Expanding into unrelated cleanup while handling a checkpoint.

## References

This skill is self-contained for normal checkpoint work. Open optional repo
references only when the caller asks for contract, eval, benchmark, or source
provenance details:

- `references/contract.yaml`: compact stage contract.
- `references/evals.yaml`: strict audit and Tessl scenario coverage.
- `references/task-profile.json`: family benchmark thresholds.
- `.harness/archives/synaipse-harness-full/plugin-root`: preserved source
  material from the imported replacement package.
