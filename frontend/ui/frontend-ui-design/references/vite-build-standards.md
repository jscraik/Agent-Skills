# Vite Build Standards (Dec 2025)

Last verified: 2026-01-01

Use for web/App SDK UI builds.

## Build performance
- Prefer ESM + native code-splitting via dynamic import.
- Avoid giant initial bundles; split by route/feature.
- Keep CSS lean; purge unused classes.
- Measure bundle size and performance budgets before shipping.

## Assets
- Use modern image formats (AVIF/WebP) with fallbacks when needed.
- Avoid inline base64 for large assets; keep in /public or imported with hashing.
- Preload critical fonts and images; lazy-load non-critical media.

## Env and config
- Use `.env` + `import.meta.env` for env config; never hardcode secrets.
- Keep alias paths consistent with TS config.

## React fast refresh
- Keep component boundaries stable; avoid re-creating hooks in conditionals.

## Output validation
- Confirm build output is deterministic and warning-free.
- Run accessibility and performance checks in CI where possible.
