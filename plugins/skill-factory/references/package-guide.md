# Skill Factory Package Guide

## What This Package Owns
- Plugin metadata in `.codex-plugin/plugin.json`
- Plugin-level docs and assets in `README.md`, `LICENSE`, `assets/`, and `references/`
- Plugin-owned skills in `skills/`

## Ownership Boundaries
- `skill-builder` owns skill-authoring hardening and validators.
- `skill-refactor` owns session-scan and refactor recommendation workflows.
- `plugin-builder` owns package contract validation for plugin-level structure.

## Common Maintenance Flow
1. Update plugin-owned skills under `plugins/skill-factory/skills/`.
2. Keep compatibility aliases synced (for example `utilities/skill-refactor` symlink).
3. Run package and skill validation commands.
4. Run projection sync and integrity checks when alias/canonical paths change.

## Commands
```bash
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py audit-compat plugins/skill-factory
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py validate plugins/skill-factory --require-marketplace --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
bash scripts/validate_skill_authoring_family.sh
python3 scripts/projection_integrity.py verify --scope skill-factory --format text
```
