# Token Export Bridge (Summary)

Last verified: 2026-01-01

Use this summary when you need quick constraints. The full contract is in
`bridge/token-export-bridge.md` and mapping docs.

## Canonical input
- Canonical DTCG/W3C bundle at a stable path (recommended:
  `packages/tokens/src/tokens/index.dtcg.json`).
- If tokens are split by domain, the build step must compile into the canonical
  bundle.

## Output matrix (must be deterministic and committed)
- Web CSS vars: `packages/ui/src/styles/tokens.css`
- Web theme glue: `packages/ui/src/styles/theme.css`
- Tailwind mapping: `tailwind.config.ts` (or generated fragment)
- Swift tokens: `swift/ChatUIFoundation/Sources/ChatUIFoundation/Foundation/Generated/Tokens.swift`
- Swift theme glue: `swift/ChatUIThemes/Sources/ChatUIThemes/Generated/Theme+Tokens.swift`
- Docs: `docs/theming/token-reference.md`
- Docs: `docs/architecture/cross-platform-design.md`

## Mapping invariants
- No ad-hoc values in components.
- Use semantic tokens, not palette primitives.
- Modes must be tokenized (light/dark/contrast/density).
- All interactive states must have token coverage.

## Drift prevention gates
- Regenerate tokens and diff-check in CI.
- Fail on mismatch.
- Enforce lint/rules against disallowed literals.
- Docs regen or committed output required.
