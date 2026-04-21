# Harness Engineering Plugin

Codex plugin package for the harness-engineering lifecycle. This plugin routes work across HE stages from ideation through implementation and readiness review.

## Table of Contents
- [What This Is](#what-this-is)
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Usage](#usage)
- [Validation](#validation)

## What This Is
`harness-engineering` is the HE lifecycle plugin, not the `@brainwav/coding-harness` infrastructure toolchain.

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
- `Plugins/harness-engineering/references/routing-map.json`
- `skills/`
  - `he-brainstorm`
  - `he-compound`
  - `he-compound-refresh`
  - `he-deepen-plan`
  - `he-deepen-spec`
  - `he-ideate`
  - `he-improve`
  - `he-fix-bugs`
  - `he-refine`
  - `he-plan`
  - `he-prune-branches`
  - `he-router`
  - `he-reliability-review`
  - `he-code-review`
  - `he-spec`
  - `he-tdd`
  - `he-technical-review`
  - `he-work`

## Source Of Truth
- Source skill family:
  - `Plugins/harness-engineering/skills/`
- Packaged skill family:
  - `Plugins/harness-engineering/skills/`
- Repo:
  - `https://github.com/jscraik/Agent-Skills`

When updating HE lifecycle behavior, keep packaged skills and the routing map aligned.

## Usage
Start with `he-router` when users do not know the exact stage:
- It picks the primary HE stage and returns the exact next command.
- It escalates to `he-compound` when lifecycle-orchestration is needed.
- It now returns a stage-specific subagent plan derived from `references/routing-map.json`.

Use `he-compound` when the user needs lifecycle orchestration:
- It routes requests to the right HE stage using `references/routing-map.json`.
- It outputs a stage decision, required inputs, and next command.

Call stage skills directly when stage intent is explicit:
- `he-router`, `he-ideate`, `he-brainstorm`, `he-spec`, `he-deepen-spec`, `he-plan`, `he-deepen-plan`, `he-improve`, `he-fix-bugs`, `he-prune-branches`, `he-refine`, `he-work`, `he-code-review`, `he-technical-review`, `he-reliability-review`, `he-tdd`, `he-compound`, `he-compound-refresh`.

## Subagent Orchestration
- Canonical mapping: `Plugins/harness-engineering/references/subagent-routing.md`
- Machine-readable policy map: `Plugins/harness-engineering/references/routing-map.json`
- Agent availability source: `~/.codex/agents/manifest.json`

Runtime behavior:
- Stage skills resolve mapped roles from `~/.codex/agents/manifest.json` before delegation.
- Stages apply policy per map (`always`, `conditional`, `manual-only`).
- If automatic spawning is unavailable, stage outputs must continue inline and provide explicit manual launch guidance for the same mapped roles.

## Validation
Validate plugin contract and marketplace registration:

```sh
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py validate Plugins/harness-engineering --require-marketplace --marketplace-path .agents/Plugins/marketplace.json
```

Audit marketplace alignment:

```sh
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/Plugins/marketplace.json --plugins-path Plugins
```

Troubleshooting note:
- `validate` supports a legacy fallback when `.agents/Plugins/marketplace.json` is unavailable:
  `python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py validate Plugins/harness-engineering --require-marketplace --allow-legacy-marketplace-path --marketplace-path Plugins/marketplace.json`
- `audit-marketplace` does not have the legacy override flag; keep `.agents/Plugins/marketplace.json` available for that audit.
