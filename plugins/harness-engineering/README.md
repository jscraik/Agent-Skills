# Harness Engineering Plugin

Codex plugin package that bundles the compound-engineering workflow family in one installable plugin.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## Included Surfaces
- `.codex-plugin/plugin.json`
- `.mcp.json`
- `.app.json`
- `hooks/` (package-level hook placeholders)
- `scripts/` (package-level script placeholders)
- `skills/`
  - `ce-brainstorm`
  - `ce-compound`
  - `ce-compound-refresh`
  - `ce-deepen-plan`
  - `ce-deepen-spec`
  - `ce-ideate`
  - `ce-plan`
  - `ce-reliability-review`
  - `ce-review`
  - `ce-spec`
  - `ce-tdd`
  - `ce-technical-review`
  - `ce-work`

## Source Of Truth
- Source skill family:
  - `plugins/harness-engineering/skills/`
- Packaged skill family:
  - `plugins/harness-engineering/skills/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating CE lifecycle behavior, keep all packaged skills in this plugin aligned with the compound-engineering contracts.

## Usage
The `harness-engineering` plugin helps you:
- Run CE ideation, specification, planning, execution, and review workflows end-to-end.
- Keep CE lifecycle skills bundled together for consistent plugin installation.
- Reuse CE workflow references and agents included with each lifecycle skill.

## Validation
Validate the package:

```sh
python3 utilities/plugin-builder/scripts/plugin_builder.py validate plugins/harness-engineering --require-marketplace --marketplace-path .agents/plugins/marketplace.json
```

Audit marketplace alignment:

```sh
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins
```
