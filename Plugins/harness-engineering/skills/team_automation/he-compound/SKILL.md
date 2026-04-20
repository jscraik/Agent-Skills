---
name: he-compound
description: "Analyze compound-engineering artifact state and capture verified solved problems into durable `docs/solutions/` knowledge, including refreshing an existing solution doc instead of creating a duplicate when the same problem is solved again. Use when the user needs a CE request started or resumed from the right place, or wants a fresh fix turned into reusable team knowledge."
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this CE stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Full Context

- Full guide: [../../../fixtures/skill-archive/skills/team_automation/he-compound/SKILL.full.md](../../../fixtures/skill-archive/skills/team_automation/he-compound/SKILL.full.md)
- Stage references: [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Notes

- Context is preserved; it has been moved to deferred references for lower always-loaded cost.
- Keep edits additive in archived references and keep this entrypoint focused.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
