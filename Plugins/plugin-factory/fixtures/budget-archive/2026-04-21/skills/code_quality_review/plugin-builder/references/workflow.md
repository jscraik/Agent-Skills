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

## Command Matrix

```bash
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py inspect-source <source>
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate <plugin-path> --require-marketplace --marketplace-path .agents/Plugins/marketplace.json
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py audit-compat <plugin-path> --marketplace-path .agents/Plugins/marketplace.json
```

## Blockers

- malformed `.codex-plugin/plugin.json`
- missing required policy/category fields in marketplace entry
- unresolved source-to-skill mapping during conversion

## Completion Contract

Return:
- mode selected and why
- exact commands run
- remediation actions taken
- pass/fail status for each gate
- downstream handoff (typically `plugin-installer` or none)
