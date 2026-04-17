# Skill Factory Package Guide

## What This Package Owns
- Plugin metadata in `.codex-plugin/plugin.json`
- Plugin-level docs and assets in `README.md`, `LICENSE`, `assets/`, and `Infrastructure/references/`
- Plugin-owned skills in `skills/`

## Ownership Boundaries
- `skill-builder` owns skill-authoring hardening and validators.
- `skill-refactor` owns session-scan and refactor recommendation workflows.
- `plugin-builder` owns package contract validation for plugin-level structure.

## Common Maintenance Flow
1. Update plugin-owned skills under `Plugins/skill-factory/skills/`.
2. Keep compatibility aliases synced (for example `Skills/skill-refactor` symlink).
3. Run package and skill validation commands.
4. Run projection sync and integrity checks when alias/canonical paths change.

## Commands
```bash
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/Infrastructure/scripts/plugin_builder.py audit-compat Plugins/skill-factory
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/skill-factory --require-marketplace --marketplace-path .agents/Plugins/marketplace.json --allow-legacy-marketplace-path
bash Infrastructure/scripts/validate_skill_authoring_family.sh
python3 Infrastructure/scripts/projection_integrity.py verify --scope skill-factory --format text
```
