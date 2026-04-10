# Skill Factory Plugin Operational Spec

## Purpose
Define the runtime contract for `skill-factory` as a plugin package that routes skill workflow intents to plugin-owned skills.

## Scope
- Package validation and activation
- Routing to `skill-creator`, `skill-builder`, `skill-refactor`, `skill-installer`, `skillify`, and `skill-factory`
- Skill handoff boundaries between plugin-level docs and per-skill contracts

## Required Runtime Surfaces
- `.codex-plugin/plugin.json`
- `skills/`
- `README.md`
- `LICENSE`

## Validation Contract
1. `python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py validate plugins/skill-factory --require-marketplace --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path`
2. `python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-factory`
3. `python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-refactor`
4. `bash scripts/validate_skill_authoring_family.sh`
5. `python3 scripts/projection_integrity.py verify --scope skill-factory --format text`

## Failure Handling
- Validation failures are treated as packaging blockers.
- Marketplace drift is resolved before release by normalizing metadata and rerunning validation.
- Skill contract drift is resolved in the owning skill directory before repackaging.
