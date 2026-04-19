# Plugin Manifest Spec (Concise)

Use this reference for required scaffold fields and template refresh commands.

## Canonical Templates

- `Infrastructure/templates/plugin.json.tmpl`
- `Infrastructure/templates/marketplace-entry.json.tmpl`

Rendered samples:
- `references/plugin-manifest.sample.json`
- `references/marketplace-entry.sample.json`

## Refresh Commands

```bash
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/Infrastructure/scripts/render_plugin_creator_templates.py
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/Infrastructure/scripts/check_plugin_creator_template_drift.py --update
```

## Required `plugin.json` Fields

- `name` (kebab-case, matches plugin folder name)
- `version`
- `description`
- `skills` (relative path, typically `./skills/`)
- `interface` block

`interface` minimum fields:
- `displayName`
- `shortDescription`
- `category`
- `defaultPrompt` (array of short strings; max 3 entries)

## Required Marketplace Entry Fields

- `name`
- `source.source` and `source.path`
- `policy.installation`
- `policy.authentication`
- `category`

Defaults:
- `policy.installation`: `AVAILABLE`
- `policy.authentication`: `ON_INSTALL`

## Path Rules

- Use relative paths beginning with `./`.
- Keep plugin source path as `./Plugins/<plugin-name>` for both repo and home marketplace layouts.

## Validation

```bash
python3 Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/Infrastructure/scripts/check_plugin_creator_template_drift.py
```
