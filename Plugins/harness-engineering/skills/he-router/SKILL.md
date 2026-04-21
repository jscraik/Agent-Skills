---
name: he-router
description: Analyze Harness Engineering requests and choose one stage plus next command. Use when intent is unclear.
metadata:
  skill-type: team_automation
---

# Harness Engineering Router

Select exactly one `harness-engineering` stage and return one executable next step.

## When To Use

- No stage is explicit.
- Multiple stages appear plausible.

## Inputs

- User request text.
- Optional artifact paths.

## Outputs

- `schema_version: 1` when structured output is requested.
- One stage from [../../references/routing-map.json](../../references/routing-map.json).
- One rationale sentence and one exact next command.
- One subagent plan with mapped roles, available/missing split, and fallback.

## Procedure

1. Parse stage and artifact hints from the request.
2. Pick one stage using `../../references/routing-map.json`.
3. Resolve mapped roles from `~/.codex/agents/manifest.json`.
4. Return outputs.
5. If still ambiguous after one clarification, return blocked with missing input.

## Philosophy

- Prefer evidence-backed routing over confident guessing.
- Prefer the smallest safe stage that can unblock execution.

## Constraints

- Select exactly one primary stage.
- Do not implement product code.
- Redact secrets and sensitive data from routing context.
- If mapped roles are missing, include fallback guidance that references `[[codex-agent-creator]]`.
- Do not remove important context for budget trimming; move it to references and index it in [../../references/deferred-context-index.md](../../references/deferred-context-index.md).

## Anti Patterns

- Selecting a stage without request or artifact evidence.
- Returning multiple primary stages.
- Omitting fallback guidance for missing mapped roles.

## Examples

- "I need HE help but I don't know the stage."
- "This request might be plan or work. Route me."

## Validation

- Ensure selected stage is in the HE stage set from `../../references/routing-map.json`.
- Ensure the next command is executable and stage-specific.
- Ensure rationale and subagent plan use request evidence.
- Fail fast at first failed gate.

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
- [references/task-profile.json](./references/task-profile.json)
- [../../references/subagent-routing.md](../../references/subagent-routing.md)
- [../../references/deferred-context-index.md](../../references/deferred-context-index.md)
