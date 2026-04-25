---
name: he-work
description: Execute an approved plan, todo list, or tightly scoped spec with traceable progress and validation. Use when Harness Engineering work should be implemented.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Execute with traceable progress and verification at every step.
- Minimize drift between approved plan and delivered behavior.
- Keep execution state, task state, and governing artifacts synchronized so code never silently becomes the new source of truth.

## When to use

- Use when implementation is expected from an approved plan, todo list, or tightly scoped spec.
- Use when delivery must include validation and explicit blocker reporting.
- Use when approved work needs to be shipped in small verified slices rather than restated, replanned, or deferred.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

Read `../shared/references/approval-flow.md` before deciding whether to continue, ask a blocker question, or stop for approval.

1. Choose the correct execution lane before coding: `plan-led`, `todo-led`, or the narrow `small-spec-direct` path.
2. Read linked artifacts completely and restate the execution contract: active IDs, invariants, non-goals, validation gates, and explicit scope boundaries.
3. Read the relevant `CONTEXT.md` when domain terms govern behavior, and keep implementation names aligned unless the plan explicitly says otherwise.
4. Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
5. Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
6. Stop and update the governing artifact or linked Linear issue before continuing if execution uncovers contract drift, domain drift, hidden scope, or changed boundaries.
7. Report completed work, blockers, validation evidence, and the shipping handoff package.

## Validation

- Ensure each delivered increment has evidence of verification.
- Ensure deviations from plan are explicit and justified.
- Ensure implementation does not introduce domain-language drift from `CONTEXT.md` or the approved artifact without an explicit update.
- Ensure the selected execution lane matches the source artifact and risk profile.
- Ensure contract drift is reflected in the governing artifact before off-plan implementation continues.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not silently expand scope beyond approved artifacts.
- Do not let code become the only record of a changed domain decision; update the governing artifact or Linear issue first.
- Do not treat medium- or high-risk raw specs as directly executable work without planning.
- Do not mark checklist or phase state complete before validation evidence exists.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Shipping changes without validation evidence.
- Ignoring plan/spec drift introduced during execution.
- Executing directly from a risky raw spec that should route to planning first.
- Letting task tracking, artifact status, and real code state diverge during delivery.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
