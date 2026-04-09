# Harness Engineering Plugin

Codex plugin package for the compound-engineering lifecycle. This plugin routes work across CE stages from ideation through implementation and readiness review.

## Table of Contents
- [What This Is](#what-this-is)
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## What This Is
`harness-engineering` is the CE lifecycle plugin, not the `@brainwav/coding-harness` infrastructure toolchain.

Use this plugin when you need stage routing and delivery workflow:
- request shaping and ideation
- spec and plan hardening
- implementation execution
- technical/readiness/reliability reviews
- solved-problem learning capture

Use `coding-harness` instead when you need:
- `harness init`, `harness upgrade`, or scaffold updates
- harness-managed CI migration
- environment action-sync or harness governance checks

## Included Surfaces
- `.codex-plugin/plugin.json`
- `references/routing-map.json`
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
- Repo:
  - `https://github.com/jscraik/Agent-Skills`

When updating CE lifecycle behavior, keep packaged skills and the routing map aligned.

## Usage
Start with `ce-compound` when users do not know the exact stage:
- It routes requests to the right CE stage using `references/routing-map.json`.
- It outputs a stage decision, required inputs, and next command.

Call stage skills directly when stage intent is explicit:
- `ce-brainstorm`, `ce-spec`, `ce-plan`, `ce-work`, `ce-review`, `ce-technical-review`, `ce-reliability-review`, `ce-compound`, `ce-compound-refresh`.

## Validation
Validate plugin contract and marketplace registration:

```sh
python3 utilities/plugin-builder/scripts/plugin_builder.py validate plugins/harness-engineering --require-marketplace --marketplace-path .agents/plugins/marketplace.json --allow-legacy-marketplace-path
```

Audit marketplace alignment:

```sh
python3 utilities/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/plugins/marketplace.json --plugins-path plugins --allow-legacy-marketplace-path
```
