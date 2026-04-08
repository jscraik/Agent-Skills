# Plugin Factory Plugin

Codex plugin package that bundles the plugin-authoring family in one installable plugin.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## Included Surfaces
- `.codex-plugin/plugin.json`
- `skills/plugin-builder/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
- `skills/plugin-creator/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `assets/`
- `skills/plugin-installer/`
  - `SKILL.md`
  - `agents/`
  - `references/`
  - `scripts/`
  - `assets/`

## Source Of Truth
- Source skill family:
  - `utilities/plugin-builder/`
  - `skills-system/plugin-creator/`
  - `skills-system/plugin-installer/`
- Packaged skill family:
  - `plugins/plugin-factory/skills/plugin-builder/`
  - `plugins/plugin-factory/skills/plugin-creator/`
  - `plugins/plugin-factory/skills/plugin-installer/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating family logic, keep packaged skills aligned with the source family paths above.

## Usage
The `plugin-factory` plugin helps you:
- Create plugin scaffolds and marketplace entries (`plugin-factory:plugin-creator`).
- Harden and validate plugin packages (`plugin-factory:plugin-builder`).
- Install and verify plugins from trusted sources (`plugin-factory:plugin-installer`).
- Keep scripts, references, and assets shipped with each family skill.

## Validation
Validate the package:

```sh
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py validate plugins/plugin-factory --require-marketplace --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
```

Validate marketplace and compatibility:

```sh
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py audit-compat plugins/plugin-factory --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins --allow-legacy-marketplace-path
```
