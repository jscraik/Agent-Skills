# Harness Engineering Deferred Context Index

This reference preserves context moved out of active `SKILL.md` entrypoints during budget hardening.

Use this file when you need detailed stage doctrine, extended examples, legacy/archive context, or full stage asset/script references that are intentionally deferred from always-loaded entrypoints.

## Preserved Context

- Full stage guides and archived references remain in `fixtures/skill-archive/**`.
- Canonical contract/eval/task profiles remain in each stage under `Infrastructure/references/**`.
- Canonical subagent role policy remains in:
  - `references/routing-map.json`
  - `references/subagent-routing.md`
- Router role-resolution policy for `he-router` requires checking `~/.codex/agents/manifest.json` and preferring `he-*` mapped roles when available in the stage map.

## Stage Archive Paths

- `he-router`: `skills/he-router/references/*` (active canonical), plus router policy in `references/routing-map.json`.
- `he-code-review`: `fixtures/skill-archive/skills/code_quality_review/he-code-review/`
- `he-reliability-review`: `fixtures/skill-archive/skills/code_quality_review/he-reliability-review/`
- `he-technical-review`: `fixtures/skill-archive/skills/code_quality_review/he-technical-review/`
- `he-brainstorm`: `fixtures/skill-archive/skills/team_automation/he-brainstorm/`
- `he-compound`: `fixtures/skill-archive/skills/team_automation/he-compound/`
- `he-compound-refresh`: `fixtures/skill-archive/skills/team_automation/he-compound-refresh/`
- `he-deepen-plan`: `fixtures/skill-archive/skills/team_automation/he-deepen-plan/`
- `he-deepen-spec`: `fixtures/skill-archive/skills/team_automation/he-deepen-spec/`
- `he-fix-bugs`: `fixtures/skill-archive/skills/team_automation/he-fix-bugs/`
- `he-ideate`: `fixtures/skill-archive/skills/team_automation/he-ideate/`
- `he-improve`: `fixtures/skill-archive/skills/team_automation/he-improve/`
- `he-plan`: `fixtures/skill-archive/skills/team_automation/he-plan/`
- `he-prune-branches`: `fixtures/skill-archive/skills/team_automation/he-prune-branches/`
- `he-refine`: `fixtures/skill-archive/skills/team_automation/he-refine/`
- `he-spec`: `fixtures/skill-archive/skills/team_automation/he-spec/`
- `he-tdd`: `fixtures/skill-archive/skills/team_automation/he-tdd/`
- `he-work`: `fixtures/skill-archive/skills/team_automation/he-work/`

## Preservation Contract

- Active `SKILL.md` files should remain concise and routing-safe.
- Context trimmed for token budget must be linked here or in stage-local `references/*`.
- Do not delete archived context; move and link it.
