---
name: he-work
description: "Implement approved Harness Engineering work. Use when a plan, todo list, or tiny spec needs traceable delivery and validation."
metadata:
  skill-type: team_automation
---

# he-work Entry

Use when implementation is expected from an approved plan, todo list, or tightly scoped low-risk spec.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

- Ship small verified slices.
- Keep code, artifact state, Linear state, and validation evidence aligned.

## When to use

Use `he-work` when the user wants implementation of approved Harness Engineering work with traceable progress and validation evidence.

## Required inputs

- An approved plan, todo list, scoped spec, or explicitly low-risk direct implementation request.
- Active Linear issue for non-trivial tracked work, plus branch and PR context when available.
- Governing acceptance IDs, validation commands, invariants, non-goals, and scope boundaries.

## Deliverables

- Implemented slices tied to plan/spec/todo IDs.
- Updated task state and handoff evidence covering validation, deviations, blockers, and PR or pending-PR status.
- Linear update or explicit blocker when tracker mutation is requested or required.

## Core Contract

- Choose `plan-led`, `todo-led`, or narrow `small-spec-direct` before editing.
- Read linked artifacts completely and restate active IDs, invariants, non-goals, validation gates, and scope boundaries.
- Resolve the active Linear work item before coding; stop when non-trivial tracked work has no issue.
- Keep markdown task state, code state, Linear status/comment state, and validation evidence synchronized.
- Implement in small verified slices and stop on contract drift, hidden scope, domain drift, or failed gates.

## Procedure

1. Choose the execution lane and read the governing artifact.
2. Resolve Linear, branch, PR, IDs, and validation gates.
3. Implement one verified slice at a time.
4. Update handoff evidence and stop on drift or failed gates.

## Traceability

Final handoff must record completed IDs, validation evidence, PR link or pending-PR blocker, and Linear update/comment result. Do not ship tracked work with only a PR link; tie PR evidence back to Linear and the governing plan/spec.

## Validation

- Verify each delivered increment.
- Document any deviation from plan.
- Confirm branch, PR, plan/spec, and Linear identifiers align before handoff.
- For tracked handoff artifacts, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <artifact-path>` before claiming completion.
- Reflect contract drift in the governing artifact before off-plan implementation continues.
- Stop at the first failed gate.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not expand scope beyond approved artifacts.
- Do not claim completion without validation evidence.

## Anti-patterns

- Letting code become the only record of a changed decision.
- Finishing tracked work without Linear/spec/plan/PR traceability.
- Marking checklist state complete before validation exists.

## Examples

- "Implement this approved plan and keep task state aligned."
- "Work through this todo artifact in verified slices."

## Failure mode

If the governing artifact is missing, Linear context is required but absent, or validation cannot prove the delivered slice, stop and report the blocker before continuing.

## Gotchas

- Do not expand scope beyond approved IDs without updating the governing artifact.
- Do not claim completion without validation evidence.
- Keep PR links as delivery evidence tied back to Linear, not a substitute for tracker state.

## References

- Full guide: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-work/SKILL.full.md`
- Handoff and shipping: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-work/references/handoff-and-shipping.md`
- Execution modes: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-work/references/execution-modes.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Session evidence contract: `Plugins/harness-engineering/references/session-evidence-contract.md`
- Subagent routing: `Plugins/harness-engineering/references/subagent-routing.md`
- Domain routing: `Plugins/harness-engineering/references/domain-model-routing.md`
