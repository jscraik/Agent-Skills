# arscontexta

Codex plugin package converted from Ars Contexta.

## Included surfaces
- `.codex-plugin/plugin.json`
- `skills/arscontexta/`
- `prompts/commands/*` (mapped from upstream plugin skills)
- `prompts/workflows/*` (mapped from upstream skill-sources)
- `hooks.json` and `hooks/scripts/*`
- `agents/knowledge-guide.md`
- `.app.json` and `.mcp.json`
- `references/*` conversion and contract artifacts

## Source of truth
- Repository: <https://github.com/agenticnotetaking/arscontexta.git>
- Pinned commit: `2acfd5cc4473c4d06c46be63df748e77e00e2746`

## Scope notes
This package now carries mapped command surfaces and hook payloads for parity-oriented review. Runtime-specific behavior that depends on provider internals remains documented as provisional until Codex runtime verification.
