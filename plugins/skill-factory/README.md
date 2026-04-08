# Skill Factory Plugin

Codex plugin package that bundles the skill-authoring family in one installable plugin.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## Included Surfaces
- `.codex-plugin/plugin.json`
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
- `skills/skill-installer/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `assets/`

## Source Of Truth
- Source skill family:
  - `skills-system/skill-creator/`
  - `utilities/skill-builder/`
  - `skills-system/skill-installer/`
- Packaged skill family:
  - `plugins/skill-factory/skills/skill-creator/`
  - `plugins/skill-factory/skills/skill-builder/`
  - `plugins/skill-factory/skills/skill-installer/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating family logic, keep packaged skills aligned with the source family paths above.

## Usage
The `skill-factory` plugin helps you:
- Create new skills and scaffolds (`skill-creator`).
- Improve and harden skills (`skill-builder`).
- Install and verify plugins from trusted sources (`skill-installer`).
- Keep scripts, references, and assets shipped with each family skill.

## Validation
Validate the package:

```sh
python3 utilities/plugin-builder/scripts/plugin_builder.py validate plugins/skill-factory --require-marketplace --marketplace-path plugins/marketplace.json
```

Validate bundled skills:

```sh
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-builder
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-creator
python3 utilities/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skill-installer
```
