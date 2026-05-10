# Plugin Creator Workflow

Use this file for execution details after loading `SKILL.md`.

## Procedure

1. Normalize plugin name (kebab-case).
2. Classify non-trivial plugins with `references/factory-governance-spine.md` before choosing `router_plugin`, `visible_skill_family`, `delivery_plugin`, or `coding_harness_plugin` posture.
3. Create plugin root and required `.codex-plugin/plugin.json`.
4. Add optional plugin surfaces only when requested.
5. Update marketplace entry only when requested.
6. If adopting an existing skill, move it into plugin ownership (`git mv` preferred), not copy.

## Bundled Hook Surface

Create `hooks/hooks.json` only when the request names lifecycle behavior,
guardrails, setup context, validation hooks, command checks, or plugin-bundled
automation. Do not add hooks to every scaffold by default.

When hooks are requested:
- set `plugin.json` field `"hooks"` to `"./hooks/hooks.json"`;
- create a parseable `hooks/hooks.json` file;
- use `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` for plugin-owned scripts or data;
- document that execution requires `[features] plugins = true`, `hooks = true`,
  and `plugin_hooks = true` while plugin hooks remain behind the feature gate.

Use multiple manifest hook paths only when the plugin has clearly separable hook
files. Avoid inline hook objects in generated scaffolds except for small tests.

## Core Commands

```bash
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw <plugin-name>
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw <plugin-name> --with-marketplace
```

## Optional Flags Guidance

- `--with-hooks`: create `hooks/hooks.json` and declare it in `plugin.json`.
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
