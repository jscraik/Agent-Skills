---
name: he-review
description: Review PRs, branches, diffs, and workflow artifacts for package-level go/no-go readiness with severity-ranked synthesis. Use when users need readiness synthesis rather than detailed technical-risk critique.
metadata:
  skill-type: code_quality_review
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this CE stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Full Context

- Full guide: [../../../fixtures/skill-archive/skills/code_quality_review/he-review/SKILL.full.md](../../../fixtures/skill-archive/skills/code_quality_review/he-review/SKILL.full.md)
- Stage references: [./references](./references)
- Stage scripts: [./scripts](./scripts)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Template: [./review-todo.md.tmpl](./review-todo.md.tmpl)

## Notes

- Context is preserved; it has been moved to deferred references for lower always-loaded cost.
- Keep edits additive in archived references and keep this entrypoint focused.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
