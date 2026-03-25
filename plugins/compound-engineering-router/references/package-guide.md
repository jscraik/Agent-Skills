# Compound Engineering Router package guide

This package wraps the existing `compound-engineering-router` skill in a Codex plugin boundary. The plugin keeps runtime surfaces small and packages the router logic as a plugin-owned skill bundle.

## Table of Contents
- [Package Layout](#package-layout)
- [Helper Ownership](#helper-ownership)
- [Verified External Agents](#verified-external-agents)
- [Sync Workflow](#sync-workflow)
- [Validation Commands](#validation-commands)

## Package Layout
- `.codex-plugin/plugin.json`: runtime plugin manifest
- `README.md`: package overview and usage
- `LICENSE`: package license
- `references/operational-spec.md`: runtime package contract
- `references/plugin-contract.md`: plugin packaging rules used for validation
- `references/required-agents.md`: verified external agent roles referenced by the packaged skill
- `references/external-agent-seeds/`: checked-in recovery seeds for the full verified external helper bundle
- `references/deconflict-report.md`: overlap review for the package name and intent
- `skills/compound-engineering-router/`: packaged skill bundle copied from `product/ops/compound-engineering-router/`

## Helper Ownership
- `codex-plugin-builder` created the plugin root, manifest, and package reference docs.
- `skill-builder` created the initial plugin-owned skill folder.
- This conversion then replaced the stub skill content with the real router bundle from `product/ops/compound-engineering-router/`, and subsequent syncs keep the packaged skill aligned with the packaged CE route table.

## Verified External Agents
This plugin does not ship plugin-root `agents/*.toml` files because the router skill depends on already-registered global roles in the canonical Codex config. The conversion verified these exact role names in `/Users/jamiecraik/dev/config/codex/config.toml`:

- `repo-research-analyst`
- `learnings-researcher`
- `issue-intelligence-analyst`
- `spec-flow-analyzer`
- `ui-ux-design`
- `design-implementation-reviewer`
- `julik-frontend-races-reviewer`
- `kieran-typescript-reviewer`

The packaged skill's `agents/openai.yaml` is synced from the source skill and the route-level mapping lives in `references/required-agents.md`. `ce:ideate` now has a verified `issue-intelligence-analyst` helper in the canonical Codex config, while the skill still preserves a bounded fallback for other runtimes. To avoid future drift, the plugin also carries a checked-in recovery seed set at `references/external-agent-seeds/` for the full verified helper bundle.

## Sync Workflow
When the source skill changes:

1. Update `product/ops/compound-engineering-router/`.
2. Sync those changes into `plugins/compound-engineering-router/skills/compound-engineering-router/`.
3. Rerun plugin and skill validation.
4. Update plugin-root docs when package metadata, the route model, or external agent dependencies change.

Current sync expectations:
- packaged CE routes are primary and should stay aligned with the source route table
- legacy prompt aliases are compatibility notes only
- UI-first routing belongs to `ce-spec` versus `ce-plan`, not a standalone `ui-workflow` route

## Validation Commands
```sh
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate plugins/compound-engineering-router --require-marketplace --marketplace-path plugins/marketplace.json
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py audit-compat plugins/compound-engineering-router --marketplace-path plugins/marketplace.json
python3 utilities/skill-builder/scripts/quick_validate.py plugins/compound-engineering-router/skills/compound-engineering-router
python3 utilities/skill-builder/scripts/skill_gate.py plugins/compound-engineering-router/skills/compound-engineering-router
python3 utilities/skill-builder/scripts/analyze_skill.py plugins/compound-engineering-router/skills/compound-engineering-router
python3 utilities/skill-builder/scripts/openclaw_skill_guard.py plugins/compound-engineering-router/skills/compound-engineering-router --mode both
```
