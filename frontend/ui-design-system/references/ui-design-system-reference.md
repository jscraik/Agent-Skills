# UI Design System Reference (Jan 2026 baseline)

Use this as the detailed checklist and inventory. Keep outputs concise and tailored.

## 1) Governance (system contract)
- Charter: purpose, scope, non-goals, supported platforms, support model.
- Principles: clarity, consistency, accessibility-first, performance, privacy.
- AI UX principles: human-in-control, transparency, correction-first, avoid anthropomorphizing.
- Decision rights: owners, platform captains, RFC process.
- Lifecycle: proposal → alpha → beta → stable → deprecated → removed.
- Versioning: SemVer, release notes, token diffs, migration guides.

## 2) Foundations
- Brand: logo usage, color usage rules, iconography, voice/tone.
- Accessibility: WCAG 2.2 AA baseline; focus states; keyboard support; reduced motion.
- Layout: spacing scale, grid rules (web), adaptive layout (SwiftUI).
- Typography: scale, line-height, dynamic type strategy; responsive web rules.
- Motion: durations, easing, feedback states; limit surprise motion in embeds.

## 3) Tokens (source of truth)
- Standard: W3C/DTCG Design Tokens format (stable 2025.10).
- Layering: base → semantic → component tokens.
- Categories: color, type, spacing, radii, borders, shadows, opacity, z-index,
  motion, breakpoints, icon sizes, focus ring.
- Themes: light/dark + high contrast + brand themes as needed.
- Tailwind: map tokens to theme variables + CSS variables for runtime theming.
- Embedded widgets: expose host overrides via CSS variables (web) and environment
  injection (iOS); document safe overrides.

## 4) Components
- Taxonomy: primitives (behavior), styled components (tokens), composites (flows).
- Documentation standard per component:
  - purpose, anatomy, variants, states
  - accessibility (keyboard/ARIA/focus)
  - content rules and errors
  - theming hooks and platform notes
- Testing standard: Storybook interactions + a11y + visual regression in CI.

## 5) Patterns (product UX)
- Core patterns: forms, search/filter, empty/loading/error, onboarding, nav.
- Embedded widget patterns:
  - inline cards: lightweight, max 1-2 CTAs, no nested scroll
  - fullscreen for multi-step flows
- LLM-specific patterns:
  - prompt input (suggestions/templates)
  - streaming output; draft/final states
  - citations/source list
  - regenerate/compare variants
  - confirmation/undo for actions
  - refusal/safety flows
  - feedback/report issue

## 6) Stack-specific blueprint
- React web: Radix primitives + Tailwind + Storybook.
- SwiftUI: native components with token-driven theming and Dynamic Type.
- Embedded widgets: shadow DOM isolation + CSS var theming + host constraints.

## 7) QA and release gates
- Visual regression across viewports/themes.
- A11y tests (keyboard + SR + contrast).
- Lint rules: no raw hex, no hardcoded spacing.
- Performance budgets (bundle size/render time).
- Release notes: breaking changes + token diffs + a11y changes.

## 8) Suggested monorepo layout
- packages/tokens (DTCG JSON + build outputs)
- packages/tailwind-preset
- packages/ui-react (Radix + Tailwind)
- apps/storybook-docs
- packages/swift-tokens (generated)
- packages/swiftui-components
- packages/widgets (embedded runtime)
- examples/ (inline card, fullscreen, iOS demo)
- governance/ (RFCs, ADRs, releases, deprecations)

## 9) Minimum viable system path
- Define charter + principles + accessibility baseline.
- Establish tokens (color, type, spacing, radius) + light/dark.
- Ship core components (button, input, dialog, alert, text, layout).
- Stand up Storybook + a11y + visual regression.
- Document embedded widget constraints.

## 10) Gold-standard extras
- High-contrast theme, component tokens for AI UX.
- Structured tool/action patterns with confirmation gates.
- Comprehensive pattern library for AI flows.
- Automated token diff reporting and migration tooling.
