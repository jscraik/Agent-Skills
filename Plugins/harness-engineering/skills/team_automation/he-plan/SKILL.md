---
name: he-plan
description: Own the compound-engineering planning stage by turning a spec, brainstorm, bug report, or feature description into an execution-ready implementation plan. Use when the user wants either the CE planning stage or canonical generic multi-step implementation planning.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this CE stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Full Context

- Full guide: [../../../fixtures/skill-archive/skills/team_automation/he-plan/SKILL.full.md](../../../fixtures/skill-archive/skills/team_automation/he-plan/SKILL.full.md)
- Stage references: [./references](./references)
- Stage scripts: [./scripts](./scripts)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Template: [./plan.md.tmpl](./plan.md.tmpl)

## Notes

- Context is preserved; it has been moved to deferred references for lower always-loaded cost.
- Keep edits additive in archived references and keep this entrypoint focused.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
