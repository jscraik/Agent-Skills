# Project Review Mode (Repo Audit)

Yes, this skill can run a deterministic audit if the agent has repo access (Codex CLI / Codex) or you provide key files/logs. Default to this mode when the user says "review", "audit", or "refactor".

## 1) Snapshot
- Capture: stack, app surfaces, routes/screens, key packages.
- Output: a short "Project Map" (what exists + where).

## 2) Run diagnostics (if tools available)
- JS/TS: `pnpm -s biome check .`
- TS build: `pnpm -s typecheck` (or `tsc -p ...` if present).
- Rust: `cargo fmt --check` and `cargo clippy -- -D warnings`.
- Tests: `pnpm -s test` / `cargo test` (if configured).
- Storybook: confirm stories exist for new/changed components.

If commands are missing, infer equivalents from package scripts.

## 3) Component & UX audit
- Radix usage: focus, keyboard, portal layering, aria.
- Tokens: hardcoded colors/spacing that should be tokens.
- State coverage: loading/empty/error/success/auth-expired.
- Desktop UX: shortcuts, focus restore, context menus, hover-only affordances.
- Motion: reduced-motion, durations/easing, layout thrash risks.

## 4) Findings output format
Return a prioritized list with:
- Severity: Blocker / High / Medium / Low.
- Category: Build/Lint | Architecture | UI | A11y | Motion | Perf | DX.
- Evidence: file path + snippet or rule.
- Recommendation: specific change.
- Effort: S / M / L.
- Risk: Low / Med | High.

## 5) Refactor plan
Provide 3 layers:
- Quick wins (same day).
- Structural refactors (1–3 days).
- Strategic improvements (1–2 weeks).

## 6) Optional patch
If asked, implement changes as small patches:
- Keep diffs minimal and testable.
- Add/adjust Storybook stories for changed UI.
- Update tokens (`@theme`) instead of hardcoding styles.
