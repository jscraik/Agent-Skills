# Extended Guidance

- Adapter: React + Apps SDK UI setup/patterns
  See: `adapters/react-apps-sdk-ui.md`
  References: `references/apps-sdk-ui-react.md`,
  `references/react-quality.md`,
  `references/tailwind-best-practices.md`,
  `references/vite-build-standards.md`

- Adapter: Tauri desktop (web UI + Rust command layer)
  See: `adapters/tauri.md`
  References: `references/tauri.md`, `references/rust-frontend-bridge.md`

When producing output, include "Implementation Snippets" for every surface in scope and follow adapter constraints.

## 11) Repo integration guidance (for this monorepo)
Given this repo layout:
- Tokens live in: `packages/tokens/src/tokens/**`
- React components live in: `packages/ui/src/components/ui/**`
- Storybook app lives in: `platforms/web/apps/storybook`
- Storybook guide lives in: `packages/ui/STORYBOOK_GUIDE.md`
Canonical repo: https://github.com/jscraik/Chatui.git
Storybook requirements: see `references/storybook.md`.
Storybook standards: see `references/storybook-standards.md`.

## 11.1) ChatUI design + Apps SDK references (repo)
Use these when working inside `/Users/jamiecraik/chatui`:
- Design rules: `docs/guides/DESIGN_GUIDELINES.md` (Apps SDK UI first, avoid raw tokens)
- Apps SDK integration: `docs/guides/CHATGPT_INTEGRATION.md`
- Apps SDK gap analysis: `docs/architecture/APPS_SDK_GAP_ANALYSIS.md`
- Apps SDK compliance audit: `docs/audits/APPS_SDK_COMPLIANCE_AUDIT.md`
- Token package docs: `packages/tokens/README.md`
- Exact tokens + layout rules: `references/chatui-exact-tokens.md`
Core usage expectations (from design guidelines):
- Prefer `@chatui/ui` wrappers before importing `@openai/apps-sdk-ui` directly.
- Do not import `@radix-ui/*` outside `packages/ui/src/primitives`.
- Do not import `lucide-react` directly; use `packages/ui/src/icons` adapter.

## 11.2) Token workflow (ChatUI)
- Canonical tokens: `packages/tokens/src/tokens/index.dtcg.json`
- Foundations: `packages/tokens/src/foundations.css` (audit/extension only)
- App tokens: `packages/tokens/src/tokens.css`
- Figma export workflow: `packages/tokens/docs/FIGMA_EXPORT_GUIDE.md`
- Generate tokens: `pnpm generate:tokens`
- Sync TS exports: `pnpm -C packages/tokens tokens:sync`
- Validate tokens: `pnpm validate:tokens`

## 11.3) ChatUI compliance checks
- Lint compliance: `pnpm lint:compliance`
- Widget a11y tests: `pnpm test:a11y:widgets`
- Web e2e: `pnpm test:e2e:web`
- Web visual: `pnpm test:visual:web`
- Storybook visual: `pnpm test:visual:storybook`

## 11.4) Apps SDK compliance quick checks (ChatUI)
Reference: `docs/architecture/APPS_SDK_GAP_ANALYSIS.md`, `docs/audits/APPS_SDK_COMPLIANCE_AUDIT.md`
- Widget resource metadata: `openai/widgetDomain`, `openai/widgetDescription`, `openai/widgetPrefersBorder`
- CSP metadata: `openai/widgetCSP.connect_domains`, `resource_domains`, `redirect_domains`, `frame_domains`
- Tool metadata: `openai/outputTemplate`, `openai/toolInvocation/invoking`, `openai/toolInvocation/invoked`
- Tool hints: `readOnlyHint`, `destructiveHint`, `openWorldHint`, `openai/visibility`, `openai/widgetAccessible`
- Tool responses: `content`, `structuredContent`, `_meta`; keep `structuredContent` < 4k tokens
- Optional flows: `openai/closeWidget`, `openai/fileParams` when using uploads
- State: `widgetSessionId` and `toolResponseMetadata` use (widget-only)
- Re-verify against current Apps SDK docs: https://developers.openai.com/apps-sdk/reference and https://developers.openai.com/apps-sdk/build/chatgpt-ui/

## 11.5) Apps SDK runtime API references (ChatUI)
- Runtime API surface: `packages/runtime/README.md`
- Source of truth: `packages/runtime/src/index.tsx`
- Architecture overview: `docs/architecture/WIDGET_ARCHITECTURE.md`

## 11.6) Apps SDK UI version sync (ChatUI)
- Check `packages/ui/package.json` and `packages/widgets/package.json` for the current `@openai/apps-sdk-ui` version.
- Keep the version aligned in pnpm-lock and update docs when bumping.
- Current (as of 2026-01-04): `^0.2.1` in both packages.

## 11.7) Brand component specs (baseline)
When asked to build core UI controls in the Apps-in-ChatGPT brand, follow:
- `references/brand-components.md`

## 11.8) Layout grids + breakpoints
For cross-platform layout guidance (web, desktop), use:
- `references/layout-grids-breakpoints.md`

## 11.9) Iconography (official set)
Use the Apps-in-ChatGPT icon set and category guidance:
- `references/iconography-apps-in-chatgpt.md`

Supplemental icons (when missing from the official set):
- `references/iconography-missing-icons.md`

Context control:
- Never paste the full SVG catalog in a response.
- Load only the single category file you need, and include only the icons required.

Default expectation:
- Token changes happen in `packages/tokens` first.
- React and desktop surfaces consume generated/mapped tokens (no hand-written divergence).
- Docs live in `docs/components/**` and `docs/architecture/**` and must include accessibility notes and cross-platform parity rules.
- Use Storybook stories (`*.stories.tsx`/`*.stories.mdx`) to document and test new React components.

## 11.10) Cross-platform diff matrix
When platform deviations are required, include:
- `references/cross-platform-diff-matrix.md`

## 12) Example prompts that should trigger this skill
- "Design a settings panel that works as a ChatGPT widget (inline + fullscreen) and a desktop window; include tokens, focus order, reduced motion, and tests."
- "Add a token-based Button component across React and desktop UI with matching states and accessibility mappings."
- "Audit the Modal and Dialog components for WCAG 2.2 AA; propose fixes with code."
- "Replicate the Apps-in-ChatGPT UI style in a new widget and provide tokens/components."
- "Review the current UI implementation for token usage, a11y, RTL, and performance issues."
- "Add a new token and provide deprecation/migration notes for the old one."
- "Document the cross-platform deviations between web and desktop for this feature."
- "Provide QA recipes and test steps for Button, Input, Modal, List, Carousel, and Tabs."
- "Audit localization/RTL readiness and formatting rules for dates and numbers."

---

# 13) Token Export Bridge (mandatory)
The authoritative bridge contract and mapping rules live in `bridge/`.
Always follow these docs, and include them in FILE_PLAN when tokens or
components change:
- `bridge/token-export-bridge.md`
- `bridge/mapping.web.md`
- `bridge/mapping.docs.md`

## 14) Apps-in-ChatGPT brand guide
When the user asks to match or replicate the ChatGPT apps UI (inline cards,
carousel, PiP, fullscreen), use:
- `references/brand-apps-in-chatgpt.md`

If the request conflicts with this guide, ask for confirmation before
diverging.

## 15) Brand dos and don'ts
Use the quick guardrails in:
- `references/brand-dos-donts.md`

## 16) Component QA recipes
When validating components, use:
- `references/component-qa-recipes.md`

## 17) Internationalization and localization
Use the i18n/RTL guide:
- `references/i18n-localization.md`

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.

## Examples
- See `references/extra.md` for extended examples and notes.

## Procedure
1) Confirm objective.
2) Gather required inputs.
3) Execute steps.
4) Validate output.

## Antipatterns
- Do not add features outside the agreed scope.
