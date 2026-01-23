# AGENTS.md

## Project summary
This is a React + Vite + Tailwind web app. Primary dev target is **mobile Safari (iOS)** and the iOS Simulator.

## Working agreements for Codex
- Prefer **small, targeted diffs**. Avoid refactors unless explicitly requested.
- Do **not** add new production dependencies unless the user asks. If a new dev dependency seems necessary, explain why first.
- Use existing project conventions (file structure, component patterns, naming).
- When changing UI/CSS:
  - Prefer Tailwind utilities and existing design tokens.
  - Avoid introducing one-off global CSS unless necessary.
  - Keep accessibility intact (tap targets, focus states, contrast).
- When you’re unsure about the intended design, **ask** or propose options (but keep the default minimal).

## Package manager rule
Use the package manager indicated by the lockfile and do not mix:
- `pnpm-lock.yaml` → `pnpm`
- `yarn.lock` → `yarn`
- otherwise → `npm`

## Commands: discover, don’t guess
Before running checks, read `package.json` and use existing scripts.
Common scripts (if present):
- `dev`: start Vite
- `build`: production build
- `lint`: lint
- `typecheck`: TypeScript checks (sometimes `tsc -p . --noEmit`)
- `test`: unit tests

If a needed script is missing, prefer running the underlying tool via the package manager (e.g. `pnpm eslint .`) only if it already exists in `devDependencies`.

## iOS Simulator workflow (UI issues)
Use a tight “snapshot → change → snapshot” loop:
1. Capture a **before** screenshot on iOS Simulator Safari.
2. Identify the minimal root cause (safe-area, viewport units, overflow, font sizing, sticky, etc.).
3. Implement the smallest fix.
4. Run the fastest available checks (`lint`/`typecheck`/`test` as available).
5. Capture an **after** screenshot and confirm the issue is resolved.

### Screenshot artifacts
Store temporary screenshots and reports under:
- `.ios-web/` (or your project’s equivalent)
Do not commit these artifacts unless asked.

## iOS Safari gotchas to consider (common causes)
- Safe areas / notch: `env(safe-area-inset-*)`, padding, and `viewport-fit=cover` interactions.
- `100vh` / address bar: prefer `dvh/svh/lvh` or CSS that doesn’t rely on fixed `100vh` on mobile.
- `position: sticky` inside overflow containers.
- `overflow-x` from long words / transforms / full-width elements.
- Touch hit areas (minimum ~44px) and fixed headers overlapping content.

## Codex automation helpers (optional but recommended)
- `bin/ui-codex triage --issue "…" --profile iphone_pro --path /…`
- `bin/ui-codex fix --issue "…" --profile iphone_pro --path /…`

These produce a structured JSON report using `codex exec --output-schema`.
