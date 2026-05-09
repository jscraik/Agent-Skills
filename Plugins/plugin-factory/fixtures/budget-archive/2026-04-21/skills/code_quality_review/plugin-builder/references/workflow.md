# Plugin Builder Workflow

Use this file for execution detail after loading `SKILL.md`.

## Mode Selection

1. `scaffold`: normalize an early plugin shell to the required package contract.
2. `convert`: transform a source package format into Codex plugin structure.
3. `harden`: validate and tighten an already-Codex plugin package.

## Procedure

1. Confirm mode and source scope.
2. Run source inspection for capability and surface mapping.
3. Run contract validation and compatibility audit.
4. Apply minimal remediations required for policy-safe packaging.
5. Return machine-checkable output with explicit blockers.

## Bundled Hook Hardening

When a package includes plugin-bundled hooks, validate them as executable
runtime behavior:

- prefer `hooks/hooks.json` and manifest `"hooks": "./hooks/hooks.json"`;
- accept legacy root `hooks.json` only during migration or when explicitly
  declared in the manifest;
- verify hook files parse and remain inside the plugin root;
- require command hooks to use `${PLUGIN_ROOT}` or `${PLUGIN_DATA}` for
  plugin-owned files instead of local absolute paths;
- include the `plugin_hooks` feature-gate caveat in release or install notes.

## Command Matrix

```bash
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py inspect-source <source>
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate <plugin-path> --require-marketplace --marketplace-path .agents/Plugins/marketplace.json
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py audit-compat <plugin-path> --marketplace-path .agents/Plugins/marketplace.json
python3 -m unittest Infrastructure.tests.test_plugin_bundled_hooks_contract -v
```

## Blockers

- malformed `.codex-plugin/plugin.json`
- malformed or undiscoverable plugin-bundled hook config
- missing required policy/category fields in marketplace entry
- unresolved source-to-skill mapping during conversion

## Completion Contract

Return:
- mode selected and why
- exact commands run
- remediation actions taken
- pass/fail status for each gate
- downstream handoff (typically `plugin-installer` or none)
