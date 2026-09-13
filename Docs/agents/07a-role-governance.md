# Role Governance

## Table of Contents
- [Decision rights](#decision-rights)
- [Escalation rule](#escalation-rule)

## Decision rights
- Repository-wide instruction: follow `AGENTS.md` first.
- Skill/assistant-specific instructions go in `AGENTS.md`.
- Agent-specific run instructions go in the active skill prompt/`SKILL.md` when present.

## Escalation rule
- Implement explicitly requested instruction changes within their authorized
  scope. Resolve authority and subtree precedence before treating a difference
  as a conflict. Ask only when a remaining decision changes scope, risk, or
  authority; an already authorized policy edit needs no duplicate confirmation.
