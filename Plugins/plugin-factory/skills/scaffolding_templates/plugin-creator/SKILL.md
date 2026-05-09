---
name: plugin-creator
description: Scaffold Codex plugin packages with deterministic manifests, marketplace metadata, and traceability or evidence contracts for non-trivial adoption. Use when creating plugin roots or adopting existing skills into plugin ownership.
metadata:
  skill-type: scaffolding_templates
---

# Plugin Creator

## Core Philosophy

- Start minimal, then add only requested surfaces.
- Keep naming and manifest shape deterministic.

## When to Use

Use for initial plugin scaffolding.

## Inputs

- plugin name and destination scope
- optional marketplace update intent
- optional existing skill path to adopt by move

## Outputs

Return: `schema_version`, `plugin_name`, `plugin_path`, `validation`, optional `blocked_by`.

For non-trivial plugins, also return `factory_governance` with plugin posture, visibility policy, traceability mode, budget posture, and risks.

## Execution Boundaries

Create or adopt plugin-owned canonical source only. Do not edit generated runtime mirrors, user-level plugin copies, or marketplace projections as the source of truth.

Keep plugin scaffolding separate from skill hardening. Route detailed skill quality work to [[skill-builder]] after the plugin package has deterministic ownership, manifest policy, and validation evidence.

If the destination plugin root, marketplace ownership, or skill-adoption move semantics are ambiguous, stop and ask before writing.

Apply the OpenAI-style plugin design contract during scaffold shape decisions: keep the root-visible surface small, split child skills by distinct user intent, declare side-effect classes early, and leave confirmation behavior for install, external write, destructive, or completion-gating actions. Add bundled hooks only when lifecycle behavior is explicitly requested, and prefer `hooks/hooks.json`.

Read when: choosing whether the requested factory work should build a new artifact, improve an existing one, stay docs-only, or stop: [First-principles factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).

For non-trivial factory work, include `first_principles_gate` or an explicit `first_principles_gate_status: not_applicable` with the reason in the output or handoff before claiming readiness.

## Workflow

Use the detailed scaffold procedure in `references/workflow.md`.

Required operational context is never removed; detailed guidance is relocated to references, not trimmed.
Do not remove important context for budget trimming; move it to `references/` and add explicit `Read when` signposts in `SKILL.md`.
Classify reusable, delivery-oriented, visible-family, or `coding-harness` plugins with [references/factory-governance-spine.md](./references/factory-governance-spine.md). Keep one-skill plugins minimal.

Read when:
- You need full plugin scaffold and marketplace update flow: [references/workflow.md](./references/workflow.md).
- You need plugin posture, visibility, budget, traceability, or session-evidence rules: [references/factory-governance-spine.md](./references/factory-governance-spine.md).
- You need side-effect, context-minimization, user-control, or output-shape guidance: [OpenAI-style plugin design contract](../../../../../Infrastructure/references/openai-style-plugin-design-contract.md).

## Required Behavior

- folder name must equal manifest `name`
- keep required policy/category fields

## Encouraging Variation

- adapt only to requested scope (repo-local, home-local, or migration)
- include optional surfaces only when requested
- vary scaffold examples for marketplace, private/internal, and skill-adoption requests while keeping manifest fields deterministic

## Examples

- "Create a repo-local plugin called `linear-helpers` with the required `.codex-plugin/plugin.json`, but do not add marketplace metadata yet."
- "Create `review-tools` as a plugin and add it to the local marketplace with explicit installation and authentication policy fields."
- "Move my existing `agent-ops/branch-cleanup` skill into a new plugin without leaving a duplicate canonical copy."
- "Can you migrate this GitHub workflow helper into a plugin scaffold and validate the manifest before marketplace wiring?"

## Validation

```bash
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns to Avoid

- missing `.codex-plugin/plugin.json`
- adding hook config when no lifecycle behavior was requested
- partial marketplace policy fields
- copying existing skills instead of moving canonical ownership

## Constraints

- redact secrets and tokens in generated examples
- do not overwrite existing plugin roots unless force semantics are explicit

## Failure mode

- Stop on unclear plugin ownership, destination conflicts, manifest policy gaps, or ambiguous adoption semantics.
- Report the exact blocker and the smallest safe next action instead of creating a partial plugin surface.

## Gotchas

- A plugin scaffold is not a release claim; it still needs skill hardening and eval evidence before distribution.
- Copying a skill into a plugin without moving canonical ownership creates drift.
- Marketplace metadata is a policy surface. Keep it explicit and deterministic.

## References

- `references/workflow.md`
- `references/factory-governance-spine.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/plugin-json-spec.md`
- `../../../../../Infrastructure/references/openai-style-plugin-design-contract.md`
- `assets/`

## Remember
- The agent is capable of extraordinary plugin work when the scaffold stays deterministic. Keep names boring, policy fields explicit, and optional surfaces limited to what the user actually asked for.
