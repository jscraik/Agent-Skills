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
1. `python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/skill-factory --require-marketplace --marketplace-path .agents/Plugins/marketplace.json --allow-legacy-marketplace-path`
2. `python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/team_automation/skill-factory`
3. `python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor`
4. `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
5. `python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope skill-factory --format text`

## Failure Handling
- Validation failures are treated as packaging blockers.
- Marketplace drift is resolved before release by normalizing metadata and rerunning validation.
- Skill contract drift is resolved in the owning skill directory before repackaging.
