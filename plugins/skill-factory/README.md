# Skill Factory Plugin

Codex plugin package that bundles the skill-authoring family in one installable plugin.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## Included Surfaces
- `.codex-plugin/plugin.json`
- `skills/skill-factory/`
  - `SKILL.md`
  - `agents/`
  - `references/`
- `skills/skill-creator/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `assets/`
- `skills/skill-builder/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `templates/`
  - `workflows/`
- `skills/skill-refactor/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `assets/`
- `skills/skillify/`
  - `SKILL.md`
  - `agents/`
  - `references/`
- `skills/skill-installer/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `assets/`

## Source Of Truth
- Canonical writable source (edit here):
  - `plugins/skill-factory/skills/skill-factory/`
  - `plugins/skill-factory/skills/skill-creator/`
  - `plugins/skill-factory/skills/skill-builder/`
  - `plugins/skill-factory/skills/skill-refactor/`
  - `plugins/skill-factory/skills/skillify/`
  - `plugins/skill-factory/skills/skill-installer/`
- Compatibility aliases (do not edit directly):
  - `utilities/skill-builder/`
  - `utilities/skill-refactor/`
  - `utilities/skillify/`
  - `skills-system/skill-creator/`
  - `skills-system/skill-installer/`
- Package-local router surface:
  - `plugins/skill-factory/skills/skill-factory/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating family logic, edit plugin paths first and keep compatibility aliases pointing at the same canonical targets.

## Usage
The `skill-factory` plugin helps you:
- Start from a front-door router (`skill-factory`) that classifies requests into create/improve/install/skillify lanes.
- Create new skills and scaffolds (`skill-creator`).
- Capture completed workflows into reusable skill contracts (`skillify`).
- Improve and harden skills (`skill-builder`).
- Audit skill usage/failures and recommend deconflict actions (`skill-refactor`).
- Install and verify skills from trusted sources (`skill-installer`).
- Keep scripts, references, and assets shipped with each family skill.

## Validation
Validate the package:

```sh
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py validate plugins/skill-factory --require-marketplace --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
```

Validate bundled skills:

```sh
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-factory
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-builder
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-refactor
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-creator
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skillify
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-installer
```

Projection sync + parity gate:

```sh
bash scripts/sync_projection_trees.sh skill-factory
PROJECTION_INTEGRITY_SCOPE=skill-factory bash scripts/validate_projection_integrity.sh
```

Authoring-family governance gate (required for skill-authoring family changes):

```sh
bash scripts/validate_skill_authoring_family.sh
```
