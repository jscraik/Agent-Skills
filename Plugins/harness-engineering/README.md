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
- `Infrastructure/references/routing-map.json`
- `skills/`
  - `ce-brainstorm`
  - `ce-compound`
  - `ce-compound-refresh`
  - `ce-deepen-plan`
  - `ce-deepen-spec`
  - `ce-ideate`
  - `ce-plan`
  - `ce-router`
  - `ce-reliability-review`
  - `ce-review`
  - `ce-spec`
  - `ce-tdd`
  - `ce-technical-review`
  - `ce-work`

## Source Of Truth
- Source skill family:
  - `Plugins/harness-engineering/skills/`
- Packaged skill family:
  - `Plugins/harness-engineering/skills/`
- Repo:
  - `https://github.com/jscraik/Agent-Skills`

When updating CE lifecycle behavior, keep packaged skills and the routing map aligned.

## Usage
Start with `ce-router` when users do not know the exact stage:
- It picks the primary CE stage and returns the exact next command.
- It escalates to `ce-compound` when lifecycle-orchestration is needed.

Use `ce-compound` when the user needs lifecycle orchestration:
- It routes requests to the right CE stage using `references/routing-map.json`.
- It outputs a stage decision, required inputs, and next command.

Call stage skills directly when stage intent is explicit:
- `ce-router`, `ce-ideate`, `ce-brainstorm`, `ce-spec`, `ce-deepen-spec`, `ce-plan`, `ce-deepen-plan`, `ce-work`, `ce-review`, `ce-technical-review`, `ce-reliability-review`, `ce-tdd`, `ce-compound`, `ce-compound-refresh`.

## Validation
Validate plugin contract and marketplace registration:

```sh
python3 Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate Plugins/harness-engineering --require-marketplace --marketplace-path Plugins/marketplace.json
```

Audit marketplace alignment:

```sh
python3 Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py audit-marketplace --marketplace-path Plugins/marketplace.json --plugins-path plugins
```

Troubleshooting note:
- Use `--allow-legacy-marketplace-path` only as an explicit temporary compatibility override.
