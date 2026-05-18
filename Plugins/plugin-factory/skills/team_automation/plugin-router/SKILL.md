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

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

## Execution Boundaries

Apply the OpenAI-style plugin design contract when ambiguity affects side-effect class, package boundary, child-skill separation, user steering, or plugin output shape. Route once; do not execute lane logic from this helper.

Plugin Router owns lane selection, missing-input reporting, and handoff shape. It does not scaffold, harden, install, refresh projections, mutate marketplace state, or make release-readiness claims.

Read when:
- You need full lane-selection and handoff protocol details: [references/workflow.md](./references/workflow.md).
- You need side-effect, context-minimization, or user-control routing checks: [OpenAI-style plugin design contract](../../../../../Infrastructure/references/openai-style-plugin-design-contract.md).
- You need to choose whether plugin factory work should build a new artifact, improve an existing one, stay docs-only, or stop: [First-principles factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).

For non-trivial factory work, include `first_principles_gate` or an explicit `first_principles_gate_status: not_applicable` with the reason in the output or handoff before claiming readiness.

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

## Failure Mode

- Stop when one request can validly route to multiple lanes with different side-effect classes, ownership boundaries, or validation gates.
- Ask one blocking question or return `blocked_by` instead of guessing the lane.

## Gotchas

- Router confidence is not execution authorization.
- A plugin lifecycle request may contain skill work; route the plugin boundary first, then hand off skill hardening only when ownership is explicit.
- Marketplace or install intent changes the side-effect class even if the user phrases it as a review.

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `../../../../../Infrastructure/references/openai-style-plugin-design-contract.md`
