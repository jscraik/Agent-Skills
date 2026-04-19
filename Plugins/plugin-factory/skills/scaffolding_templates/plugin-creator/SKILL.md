---
name: plugin-creator
description: Scaffold a minimal Codex plugin package and optional marketplace entry. Use when the user needs first-pass plugin creation.
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

## Workflow

Use the detailed scaffold procedure in `references/workflow.md`.

## Required Behavior

- folder name must equal manifest `name`
- keep required policy/category fields

## Encouraging Variation

- adapt only to requested scope (repo-local, home-local, or migration)
- include optional surfaces only when requested

## Validation

```bash
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns to Avoid

- missing `.codex-plugin/plugin.json`
- partial marketplace policy fields
- copying existing skills instead of moving canonical ownership

## Constraints

- redact secrets and tokens in generated examples
- do not overwrite existing plugin roots unless force semantics are explicit

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/plugin-json-spec.md`
- `assets/`
