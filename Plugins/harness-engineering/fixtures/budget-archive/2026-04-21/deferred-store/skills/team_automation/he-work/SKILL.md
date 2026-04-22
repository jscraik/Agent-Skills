---
name: he-work
description: "Execute a plan, todo list, or tightly scoped spec with traceable progress, validation, contract-drift control, UI execution gates, and optional external delegation. Use when the user wants Harness Engineering work implemented, not just planned."
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering execution stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Execute with traceable progress and verification at every step.
- Minimize drift between approved plan and delivered behavior.
- Keep execution state, task state, and governing artifacts synchronized so code never silently becomes the new source of truth.

## When to use

- Use when implementation is expected from an approved plan, todo list, or tightly scoped spec.
- Use when delivery must include validation and explicit blocker reporting.
- Use when approved work needs to be shipped in small verified slices rather than restated, replanned, or deferred.

## Inputs

- Approved plan/spec/todo artifact and execution scope.
- Validation requirements, constraints, and risk boundaries.
- Optional execution posture such as `test-first`, `characterization-first`, or explicit external delegation.
- Linked upstream artifacts that define scope, invariants, and non-goals.

## Outputs

- Implemented progress summary with completed/blocked items.
- Validation outcomes and next action.
- Explicit execution lane: `plan-led`, `todo-led`, or `small-spec-direct`.
- Shipping handoff summary with drift notes, remaining risks, and follow-up recommendation.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Choose the correct execution lane before coding: `plan-led`, `todo-led`, or the narrow `small-spec-direct` path.
2. Read linked artifacts completely and restate the execution contract: active IDs, invariants, non-goals, validation gates, and explicit scope boundaries.
3. Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
4. Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
5. Stop and update the governing artifact before continuing if execution uncovers contract drift, hidden scope, or changed boundaries.
6. Report completed work, blockers, validation evidence, and the shipping handoff package.

## Validation

- Ensure each delivered increment has evidence of verification.
- Ensure deviations from plan are explicit and justified.
- Ensure the selected execution lane matches the source artifact and risk profile.
- Ensure contract drift is reflected in the governing artifact before off-plan implementation continues.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not silently expand scope beyond approved artifacts.
- Do not treat medium- or high-risk raw specs as directly executable work without planning.
- Do not mark checklist or phase state complete before validation evidence exists.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Shipping changes without validation evidence.
- Ignoring plan/spec drift introduced during execution.
- Executing directly from a risky raw spec that should route to planning first.
- Letting task tracking, artifact status, and real code state diverge during delivery.

## Examples

- "Implement this approved plan and keep the markdown task state aligned with what actually lands."
- "Work through this todo artifact in small verified slices and tell me where drift appears."
- "This spec is tiny and low risk. If it really is safe, execute it directly and validate the result."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Approval flow: [../../shared/references/approval-flow.md](../../shared/references/approval-flow.md)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.
