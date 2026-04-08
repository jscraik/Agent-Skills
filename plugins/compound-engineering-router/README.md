# Compound Engineering Router plugin

Codex plugin package for the existing `compound-engineering-router` workflow skill. It packages the router as a plugin-owned skill bundle under `skills/compound-engineering-router/` while keeping the current source skill at `product/ops/compound-engineering-router/` as the upstream authoring path for now. The packaged bundle follows the CE stage model directly: packaged CE routes are primary, legacy prompt aliases are compatibility notes, and UI-first routing is folded into `ce-spec` versus `ce-plan` instead of a standalone `ui-workflow` lane.

## Table of Contents
- [Included Surfaces](#included-surfaces)
- [Source Of Truth](#source-of-truth)
- [Agent Dependencies](#agent-dependencies)
- [Usage](#usage)
- [Validation](#validation)
- [Notes](#notes)

## Included Surfaces
- `.codex-plugin/plugin.json`
- `skills/compound-engineering-router/`
- `references/operational-spec.md`
- `references/package-guide.md`
- `references/plugin-contract.md`
- `references/required-agents.md`
- `references/external-agent-seeds/`
- `references/deconflict-report.md`

## Source Of Truth
- Source skill: `product/ops/compound-engineering-router/`
- Packaged skill: `plugins/compound-engineering-router/skills/compound-engineering-router/`
- Repo: `https://github.com/jscraik/Agent-Skills`

When updating the router logic, keep the packaged skill bundle aligned with the source skill until the plugin becomes the canonical maintenance path.

## Agent Dependencies
The packaged skill depends on globally configured agent roles rather than plugin-owned `.toml` files. Validate these role names against the active Codex config at runtime:

- `repo-research-analyst`
- `learnings-researcher`
- `issue-intelligence-analyst` (optional; use when configured)
- `spec-flow-analyzer`
- `ui-ux-design`
- `design-implementation-reviewer`
- `julik-frontend-races-reviewer`
- `kieran-typescript-reviewer`

See `references/required-agents.md` for the route-by-route mapping. `ce:ideate` can use `issue-intelligence-analyst` when issue-tracker intent is active and the helper is present; otherwise, keep the bounded direct fallback path. The package also includes a checked-in seed set at `references/external-agent-seeds/` so dependencies can be reinstalled deterministically instead of relying on one live workstation copy.

## Usage
Validate the package:

```sh
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate plugins/compound-engineering-router --require-marketplace --marketplace-path plugins/marketplace.json
```

Audit curated compatibility:

```sh
python3 utilities/codex-plugin-builder/scripts/plugin_builder.py audit-compat plugins/compound-engineering-router --marketplace-path plugins/marketplace.json
```

Validate the packaged skill bundle:

```sh
python3 utilities/skill-builder/scripts/quick_validate.py plugins/compound-engineering-router/skills/compound-engineering-router
python3 utilities/skill-builder/scripts/skill_gate.py plugins/compound-engineering-router/skills/compound-engineering-router
python3 utilities/skill-builder/scripts/analyze_skill.py plugins/compound-engineering-router/skills/compound-engineering-router
python3 utilities/skill-builder/scripts/openclaw_skill_guard.py plugins/compound-engineering-router/skills/compound-engineering-router --mode both
```

## Validation
- Keep the marketplace entry in `plugins/marketplace.json`.
- Do not add `prompts/`, `commands/`, or `slash-commands/` as runtime plugin surfaces.
- Prefer updating the packaged skill by syncing from the source skill bundle rather than hand-editing only one side.
- Keep the packaged `agents/openai.yaml` aligned with `product/ops/compound-engineering-router/agents/openai.yaml`.
- Keep the package contract aligned with the packaged CE route table, including `ideate` and `compound-refresh`.
- Do not reintroduce a standalone `ui-workflow` route at the plugin layer; UI-first requests should continue to route through `ce-spec` or `ce-plan`.

## Notes
- The plugin uses the `automation_orchestrator` archetype for metadata, but its runtime surface is intentionally small: manifest, docs, and one plugin-owned skill.
- No hook, MCP, app, or asset surfaces are declared in this first-pass conversion.
