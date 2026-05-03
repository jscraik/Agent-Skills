# Plugin Creator Workflow

Use this file for execution details after loading `SKILL.md`.

## Procedure

1. Normalize plugin name (kebab-case).
2. Classify non-trivial plugins with `references/factory-governance-spine.md` before choosing router, visible-family, delivery, or `coding-harness` posture.
3. Create plugin root and required `.codex-plugin/plugin.json`.
4. Add optional plugin surfaces only when requested.
5. Update marketplace entry only when requested.
6. If adopting an existing skill, move it into plugin ownership (`git mv` preferred), not copy.

## Core Commands

```bash
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw <plugin-name>
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw <plugin-name> --with-marketplace
```

## Optional Flags Guidance

- `--with-marketplace`: create/update marketplace entry with explicit policy fields.
- `--path <path>`: set custom destination root (parent directory for plugin creation).
- `--force`: replace an existing scaffold only with explicit overwrite intent.

## Completion Contract

Return:
- resolved plugin name and path
- created surfaces
- marketplace status
- factory governance posture for non-trivial plugins
- validation command outcomes
- explicit `blocked_by` when required input is missing
