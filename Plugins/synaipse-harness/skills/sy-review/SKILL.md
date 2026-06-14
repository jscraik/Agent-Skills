---
name: sy-review
description: "Review the completed slice for correctness, risk, evidence gaps, and next-stage blockers. Use when the user asks for review, PR readiness, risk assessment, blocker identification, or post-work verification."
metadata:
  skill-type: team_automation
  version: "0.1.0"
  level: molecule
  command_visibility: orchestrator
  sdk_stage: review
  lifecycle_state: active
  owner: SynAIpse Harness
---
# SynAIpse Harness Review

## When to use

Use when the user asks for review, PR readiness, risk assessment, blocker identification, or post-work verification.

## Required inputs

- User request or routed handoff naming this stage.
- Current repository, branch, artifact, tracker, PR, validation, and session evidence when available.
- The previous-stage artifact when this stage depends on one.

## Deliverables

- A stage result with schema_version, stage, status, evidence_refs, blocked_by, and next_stage.
- Exact validation status using pass, fail, or blocked.
- A handoff that names what is proven and what remains unproven.

## Procedure

1. Restate the active repo, branch, requested stage, and available evidence.
2. Check the previous-stage artifact or explain why it is not required.
3. Perform only the work owned by review.
4. Record evidence refs and classify each lane as pass, fail, blocked, or not_checked.
5. Emit the next-stage handoff to eval-report or a blocker with the smallest recovery step.

## Validation

Fail fast: stop at the first failed required gate, classify the blocker, and do not proceed to downstream stages until the failure is resolved or explicitly waived. Run the smallest relevant local check for changed files; for package-level changes, run plugin validation and SDK proof commands from the repository wrapper.

## Handoff

Return the stage artifact or blocker, then hand off to eval-report only after this stage's exit criteria are satisfied.

## Failure modes

- Missing previous-stage artifact: block and request or create the required artifact through the owning stage.
- Conflicting evidence lanes: route to reconcile.
- Repeated failure or durable learning: route to reinforce.
- Requested action exceeds authority: block with the required authorization.

## Gotchas

- Do not use this stage to skip the lifecycle, merge evidence lanes, mutate external systems without explicit authorization, or complete another stage's exit criteria.

- Similar legacy names may exist in caches or older Harness Engineering packages; do not expose them as SynAIpse active skills.
- A local artifact can explain work, but it does not prove remote PR, CI, tracker, or deployment state.
- If multiple stages seem plausible, route to sy-reframe instead of doing blended stage work.

## References

- Stage contract: [contract](./references/contract.yaml)
- Eval cases: [evals](./references/evals.yaml)
- Task profile: [task profile](./references/task-profile.json)
- Source context: [source context](./references/source-context.yaml)
