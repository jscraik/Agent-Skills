# Context Preservation

3. Resolve mapped roles from `~/.codex/agents/manifest.json` using the exact canonical role names from `Plugins/harness-engineering/references/routing-map.json`.
4. Return outputs.
5. If still ambiguous after one clarification, return blocked with missing input.
# Moved Router Evidence Line

If required evidence is missing, return the missing input and the most likely stage with low confidence.
