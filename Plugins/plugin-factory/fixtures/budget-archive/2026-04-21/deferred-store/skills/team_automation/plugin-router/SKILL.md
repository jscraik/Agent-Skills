---
name: plugin-router
description: Analyze broad, mixed, or unclear Plugin Factory follow-up requests and select the correct plugin lane. Use when plugin intent lacks a clear lane owner.
metadata:
  short-description: Route plugin follow-ups to the right factory lane
  skill-type: team_automation
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  metadata_source: frontmatter
---

# Plugin Router

Internal helper for Plugin Factory follow-up routing. The canonical front door is `[[plugin-factory-router]]`; use this skill only after that router selects a router follow-up or when a loaded Plugin Factory workflow explicitly asks for the detailed route map.

## Philosophy

- Route first, execute second.
- Prefer one clarification over unsafe guessing when ambiguity changes risk.

## When to Use

Use when plugin intent remains broad, mixed, or missing a clear lane owner after canonical Plugin Factory routing.

Do not use this as the root Plugin Factory entrypoint. Route root-level plugin lifecycle requests through `[[plugin-factory-router]]` first.

## Inputs

- request text
- optional path/source
- constraints and trust requirements

## Outputs

Return a routing handoff object with:
- `schema_version`
- `execution_mode`
- `selected_lane`
- `next_skill`
- `required_inputs`
- optional `blocked_by`
- `confidence`

## Workflow

Use the detailed routing protocol in `references/workflow.md`.

Required operational context is never removed; detailed guidance is relocated to references, not trimmed.

Read when:
- You need full lane-selection and handoff protocol details: [references/workflow.md](./references/workflow.md).

## Examples

- "Create a new plugin with marketplace entry." -> route to `[[plugin-creator]]`
- "Harden this imported plugin before release." -> route to `[[plugin-builder]]`
- "Install this plugin from GitHub and verify visibility." -> route to `[[plugin-installer]]`

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Constraints

- redact secrets and sensitive data by default
- no lane-specific execution

## Anti-Patterns

- executing lane logic before routing is complete
- routing by preference instead of explicit intent evidence
- emitting a handoff without required inputs/missing data

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
