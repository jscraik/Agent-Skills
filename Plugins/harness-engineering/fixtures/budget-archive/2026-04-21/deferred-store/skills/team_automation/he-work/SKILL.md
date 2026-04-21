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

## When to use

- Use when implementation is expected from an approved plan, todo list, or tightly scoped spec.
- Use when delivery must include validation and explicit blocker reporting.

## Inputs

- Approved plan/spec/todo artifact and execution scope.
- Validation requirements, constraints, and risk boundaries.

## Outputs

- Implemented progress summary with completed/blocked items.
- Validation outcomes and next action.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Validate execution scope against upstream artifacts.
2. Implement in bounded increments with continuous verification.
3. Report completed work, blockers, and required follow-up.

## Validation

- Ensure each delivered increment has evidence of verification.
- Ensure deviations from plan are explicit and justified.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not silently expand scope beyond approved artifacts.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Shipping changes without validation evidence.
- Ignoring plan/spec drift introduced during execution.

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
