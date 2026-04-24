---
name: plugin-factory-router
description: Front-door entrypoint for plugin-factory. Use when a plugin task needs lane routing.
metadata:
  skill-type: team_automation
---

# Plugin Factory Router

Use this entrypoint when a plugin request does not clearly name the right lane.

## When to use

- Use when a plugin request is broad, mixed, or under-specified.
- Use when lane selection needs explicit routing before execution.

## Required inputs

- User request text.
- Optional repository path, plugin source URL, or target plugin name.
- Any stated constraints (security posture, trust requirements, install target).

## Deliverables

- One selected lane (`plugin-creator`, `plugin-builder`, `plugin-installer`, or `plugin-router` follow-up).
- One-sentence rationale for the lane selection.
- One exact next command or prompt to execute.

## Failure mode

- If lane choice is materially ambiguous, ask one blocking clarification instead of guessing.
- If required context is missing (for example, unknown repository target), return blocked with the missing input.

## Gotchas

- Do not execute lane-specific implementation from this router; hand off only.
- Do not select multiple primary lanes in one response.
- Keep routing evidence-based; avoid preference-based routing.

## Workflow

Use [references/workflow.md](./references/workflow.md) for route map and handoff behavior.

Required operational context is never removed; detailed guidance is relocated to references, not trimmed.

Read when:
- You need complete routing decision and handoff protocol details: [references/workflow.md](./references/workflow.md).

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```
