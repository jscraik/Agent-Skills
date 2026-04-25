---
name: he-router
description: Route ambiguous Harness Engineering requests to one lifecycle stage when users ask where to start, resume, plan, implement, review, debug, or resolve domain terminology.
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
3. Route explicit domain-model, ubiquitous-language, `CONTEXT.md`, glossary, or terminology requests by artifact state: fuzzy idea to `he-brainstorm`, first contract to `he-spec`, existing spec conflict to `he-deepen-spec`, execution drift to `he-work`, review drift to a review stage.
4. Resolve mapped roles from `~/.codex/agents/manifest.json`, preferring `he-*` roles when available in the stage map.
5. Return outputs.
6. If still ambiguous after one clarification, return blocked with missing input.

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

- "Can you inspect this Linear issue and rough spec, then tell me whether this should go to `he-plan` or `he-work` next?"
- "The branch is implemented and CI is green; please route me to the right Harness Engineering review stage before merge."
- "The ticket says account but `CONTEXT.md` says Customer. Can you validate which Harness Engineering stage should resolve that before planning?"

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
- [../../references/domain-model-routing.md](../../references/domain-model-routing.md)
Read when: routing domain-model, ubiquitous-language, `CONTEXT.md`, glossary, terminology, or Linear issue wording requests.
