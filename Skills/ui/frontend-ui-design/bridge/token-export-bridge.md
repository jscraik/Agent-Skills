# Token Export Bridge Contract (canonical)

## Canonical input
- `packages/tokens/src/tokens/index.dtcg.json`

## Required outputs
Web:
- `packages/ui/src/styles/tokens.css`
- `packages/ui/src/styles/theme.css`

Docs:
- `docs/theming/token-reference.md`
- `docs/architecture/cross-platform-design.md` (must link to the token reference)

## Invariants
- Semantic token references only in components.
- Generated artifacts are committed; CI regen + diff check must pass.
- Modes: light/dark/contrast/density are token-driven.
- Docs must be derived from canonical tokens (no manual edits to generated sections).

## Review checklist
- Any new UI measurement references a token
- Any new state introduces tokens (focus/pressed/disabled/etc.)
- Reduced motion path exists for any animation
- Focus order + accessible names specified in FEATURE_DESIGN
- Token reference docs updated (or CI diff passes)
