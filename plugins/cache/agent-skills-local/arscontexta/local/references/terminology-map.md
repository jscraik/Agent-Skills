<!-- GENERATED PROJECTION: source=plugins/arscontexta/references/terminology-map.md; DO NOT EDIT PROJECTION COPY. -->

# Terminology Map (Claude -> Codex)

## Core mapping
- `.claude-plugin/plugin.json` -> `.codex-plugin/plugin.json`
- `commands/` and slash-command UX -> `prompts/`
- durable workflows with rich logic -> retained as skill-like prompt equivalents under `prompts/workflows/`

## Decisions for this package
- Upstream plugin-level skills were mapped to `prompts/commands/`.
- Upstream generated workflow command surfaces from `skill-sources/` were mapped to `prompts/workflows/`.
- Existing Codex-native skill remains in `skills/arscontexta/` as an operator surface.

## Exclusions
- Claude-only runtime markers are not treated as Codex runtime contract fields.
