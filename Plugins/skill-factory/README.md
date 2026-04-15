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
  - `Infrastructure/references/`
- `skills/skill-creator/`
  - `SKILL.md`
  - `agents/`
  - `Infrastructure/references/`
  - `Infrastructure/scripts/`
  - `assets/`
- `skills/skill-builder/`
  - `SKILL.md`
  - `agents/`
  - `Infrastructure/references/`
  - `Infrastructure/scripts/`
  - `Infrastructure/templates/`
  - `workflows/`
- `skills/skill-refactor/`
  - `SKILL.md`
  - `agents/`
  - `Infrastructure/references/`
  - `Infrastructure/scripts/`
  - `assets/`
- `skills/skillify/`
  - `SKILL.md`
  - `agents/`
  - `Infrastructure/references/`
- `skills/skill-installer/`
  - `SKILL.md`
  - `agents/`
  - `Infrastructure/references/`
  - `Infrastructure/scripts/`
  - `assets/`

## Source Of Truth
- Canonical writable source (edit here):
  - `Plugins/skill-factory/skills/skill-factory/`
  - `Plugins/skill-factory/skills/skill-creator/`
  - `Plugins/skill-factory/skills/skill-builder/`
  - `Plugins/skill-factory/skills/skill-refactor/`
  - `Plugins/skill-factory/skills/skillify/`
  - `Plugins/skill-factory/skills/skill-installer/`
- Compatibility aliases (do not edit directly):
  - `Skills/skill-builder/`
  - `Skills/skill-refactor/`
  - `Skills/skillify/`
  - `Skills/skill-creator/`
  - `Skills/skill-installer/`
- Package-local router surface:
  - `Plugins/skill-factory/skills/skill-factory/`
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
python3 Plugins/plugin-factory/skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/skill-factory --require-marketplace --marketplace-path .agents/Plugins/marketplace.json --allow-legacy-marketplace-path
```

Validate bundled skills:

```sh
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skill-factory
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skill-builder
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skill-refactor
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skill-creator
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skillify
python3 Skills/skill-builder/Infrastructure/scripts/quick_validate.py Plugins/skill-factory/skills/skill-installer
```

Projection sync + parity gate:

```sh
bash Infrastructure/scripts/sync_projection_trees.sh skill-factory
PROJECTION_INTEGRITY_SCOPE=skill-factory bash Infrastructure/scripts/validate_projection_integrity.sh
```

Authoring-family governance gate (required for skill-authoring family changes):

```sh
bash Infrastructure/scripts/validate_skill_authoring_family.sh
```
