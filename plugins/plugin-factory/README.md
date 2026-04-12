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
- Canonical writable source (edit here):
  - `plugins/plugin-factory/skills/plugin-builder/`
  - `plugins/plugin-factory/skills/plugin-creator/`
  - `plugins/plugin-factory/skills/plugin-installer/`
- Compatibility aliases (do not edit directly):
  - `utilities/plugin-builder/`
  - `skills-system/plugin-creator/`
  - `skills-system/plugin-installer/`
- Generated projection cache (do not edit directly):
  - `.agents/plugins-runtime/cache/agent-skills-local/plugin-factory/local/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating family logic, edit plugin paths first and regenerate projections.

## Usage
The `plugin-factory` plugin helps you:
- Create plugin scaffolds and marketplace entries (`plugin-factory:plugin-creator`).
- Harden and validate plugin packages (`plugin-factory:plugin-builder`).
- Install and verify plugins from trusted sources (`plugin-factory:plugin-installer`).
- Keep scripts, references, and assets shipped with each family skill.

`ask` workflow shortcuts:

```sh
ask plugins create my-plugin --with-marketplace
ask plugins import https://github.com/<owner>/<repo> --path plugins/<plugin-name> --dry-run
ask plugins harden plugins/my-plugin
```

## Validation
Sync projection trees first:

```sh
bash scripts/sync_projection_trees.sh plugin-factory
```

Verify projection integrity:

```sh
bash scripts/validate_projection_integrity.sh
```

Run the required authoring-family gate:

```sh
bash scripts/validate_skill_authoring_family.sh
```

Validate the package:

```sh
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py validate plugins/plugin-factory --require-marketplace --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
```

Validate marketplace and compatibility:

```sh
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py audit-compat plugins/plugin-factory --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
python3 plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins --allow-legacy-marketplace-path
```
