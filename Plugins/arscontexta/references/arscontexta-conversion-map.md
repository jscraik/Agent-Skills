# Ars Contexta Conversion Map

Source repository: https://github.com/agenticnotetaking/arscontexta.git  
Pinned commit: 2acfd5cc4473c4d06c46be63df748e77e00e2746

## Surface separation

### Package-owned Codex plugin surfaces
- `.codex-plugin/plugin.json`
- `README.md`
- `LICENSE`
- `hooks.json` + `hooks/Infrastructure/scripts/*`
- `Infrastructure/references/*` conversion artifacts

### Archived non-runtime conversion surfaces
- `Infrastructure/references/legacy/prompts/commands/*` (mapped from upstream plugin skills)
- `Infrastructure/references/legacy/prompts/workflows/*` (mapped from upstream skill-sources)
- `Infrastructure/references/legacy/agents/knowledge-guide.md`

### Generated runtime outputs (not packaged as executable Codex surfaces)
- `methodology/*` research corpus files (kept out of runtime payload in this pass)
- `generators/*` templates and feature blocks
- `platforms/*` provider-specific scaffolding

### Migration-only/provisional behavior
- Claude-specific environment references and command conventions are preserved as prompt content, not runtime-specific Codex hook glue.
- Any provider-specific wrappers remain documentary until runtime-verified in Codex.
