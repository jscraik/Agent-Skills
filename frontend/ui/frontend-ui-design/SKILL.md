---
name: frontend-ui-design
description: "Create and review production-ready frontend UI components with accessibility and distinct visual direction. Use when building or redesigning frontend UI."
---

# Frontend Design System (Apps SDK UI + React + Tauri)

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## 0) What this skill does
This skill guides creation of distinctive, production-grade frontend interfaces
that avoid generic "AI slop" aesthetics. Implement real working code with
exceptional attention to aesthetic details and creative choices.

Design and implement UI/UX and reusable components across:
- ChatGPT Apps SDK widgets (React + Apps SDK UI, hosted runtime)
- Tauri desktop apps (web UI + Rust command layer)

This skill enforces:
- Single token source-of-truth (DTCG/W3C design tokens)
- WCAG 2.2 AA + platform accessibility compliance
- Neuroinclusive defaults (reduced cognitive load, predictable focus, optional density)
- Performance and responsiveness targets

Gold standard rule (Jan 2026):
All guidance, decisions, and outputs must align with industry gold-standard
best practices and compliance targets as of Jan 2026 across all projects.

## 0.5) Philosophy
- Design is a system: tokens → components → patterns → QA.
- Accessibility and clarity are non-negotiable.
- Be bold, but never at the cost of usability or trust.

## 1) Decision priority stack (must follow)
1. Usability and task success first
2. Accessibility and neuroinclusive design
3. Performance and responsiveness
4. Information architecture and consistency
5. Brand aesthetics and purposeful motion

## 1.5) Brand baseline (global)
Default to the shared canonical design system across all surfaces (ChatGPT widgets, React, Tauri desktop).
Use the common tokens and component rules in:
- `references/design-guidelines-canonical.md` (full)
- `references/design-guidelines-summary.md` (quick)
These are the canonical design tokens/system for all projects unless the user explicitly opts out.

If a platform constraint conflicts with the brand (e.g., system control
requirements), keep platform compliance but preserve the brand wherever it does
not break usability or accessibility. Ask for confirmation before diverging.

Opt-out confirmation prompt (use verbatim):
"You asked for a different brand. Do you want to override the Apps-in-ChatGPT baseline for this task (yes/no)?"

## 2) When to use
Use for:
- FEATURE_DESIGN: journeys, specs, interaction maps, accessibility maps, developer handoff
- Design system work: tokens, theming, component contracts, cross-platform parity rules
- Implementation: React (Apps SDK UI) component code and Tauri web UI
- Audits: a11y, focus order, keyboard nav, reduced motion, contrast, performance feedback timing
- Reviews: existing UI code/implementations for improvements and compliance

Do not use for:
- Backend architecture, auth, payments, non-UI business logic (unless directly required for UI state or tool wiring)

## 3) Inputs (ask only if blocking; max 2 questions)
If not provided and needed to proceed:
1) Target surfaces: ChatGPT widget only vs widget + Tauri desktop (macOS/Windows/Linux)
2) Critical path: "what must succeed" + primary user goal

Otherwise proceed with assumptions and state them.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs`

## 4) Output contract (always produce these sections in order)
When invoked, output:

1) FEATURE_DESIGN
   - Aesthetic direction (web/React/Apps SDK UI only)
   - Visual direction (web/React/Apps SDK UI only)
   - User journeys (happy path + 2 edge/failure paths)
   - IA / navigation model
   - Screen-by-screen spec (default/loading/empty/error/offline/permission states)
   - Interaction patterns + error prevention
   - Responsive/adaptive rules (breakpoints + platform mapping)
   - Motion spec + reduced-motion alternative for every animation
   - Accessibility map:
     - names/labels/roles (ARIA mapping)
     - focus order per state
     - keyboard behavior and shortcuts
     - localization/RTL considerations (if user-facing text or icons are directional)
   - Performance risks + mitigations (web/Tauri UI)
   - Acceptance criteria + test plan

2) TOKEN_REFERENCED_MEASUREMENTS
   - Every measurement includes: token ref + px + rem
   - No ad-hoc styling values unless explicitly justified + added back into tokens

3) IMPLEMENTATION_SNIPPETS
   - Apps SDK widget (React + Apps SDK UI) snippets
   - Tauri snippet(s) if applicable (web UI + Rust command/IPC stub)
   - Each snippet includes accessibility hooks and reduced-motion handling
   - Storybook (React): CSF story snippet(s) for new/updated components with a11y + interaction coverage

4) ACCESSIBILITY_TESTING_STEPS
   - Keyboard navigation
   - Automated checks: axe-core/Playwright a11y (web)
   - Reduce Motion
   - High Contrast
   - Text scaling + layout reflow (no clipping at large sizes)
   - RTL pass (if applicable)
   - Contrast checks for all states

5) VALIDATION_CHECKLIST
   - Task success >=95% for critical flows (how measured)
   - WCAG 2.2 AA verification items
   - Localization + RTL verified where applicable
   - Performance: <=100ms interaction feedback
   - Web performance: Core Web Vitals targets (INP <=200ms, LCP <=2.5s, CLS <=0.1) when web
   - Layout stability (no major CLS/jank in web)
   - Keyboard completeness
   - Contrast validation for all component states
   - Automated accessibility tests pass (axe-core/Playwright or equivalent)
   - Storybook coverage for new/updated components (a11y + interaction tests; visual regression when UI changes)

6) FILE_PLAN
   - Repo-relative files to add/update for the feature or component(s)

Use `assets/FEATURE_DESIGN.template.md` as the default structure.

For small, focused tasks (single component tweak or minor UI patch), you may
compress the output by omitting IA/navigation and screen-by-screen states,
but still include accessibility, performance, and token-referenced measurements.

## 4.5) Standards baseline (Jan 2026)
Follow current industry standards as a minimum bar and cite compliance targets
in the deliverables:
- WCAG 2.2 AA for web accessibility
- WAI-ARIA Authoring Practices for patterns and keyboard behavior
- DTCG/W3C Design Tokens spec for token structure and naming

Reference pack:
- `references/a11y-gold-standard.md`
- `references/standards-jan-2026.md`
- `references/tauri.md`
- `references/rust-frontend-bridge.md`

Evidence rule:
- If you claim compliance, include specific checklist items from the references.

## 4.6) Gold standard audit checklist (Jan 2026)
Use this as a quick compliance pass and link to the verified sources:
- WCAG 2.2: https://www.w3.org/TR/wcag/
- WCAG Understanding: https://www.w3.org/WAI/WCAG22/Understanding/
- WAI-ARIA APG: https://www.w3.org/WAI/ARIA/apg/
- ARIA 1.2: https://www.w3.org/TR/wai-aria-1.2/
- Design Tokens Format: https://www.designtokens.org/TR/2025.10/format/
- Storybook Accessibility Tests: https://storybook.js.org/docs/writing-tests/accessibility-testing

Automated link audit:
- Run `scripts/link_audit.sh` to check all reference URLs for drift.

## 4.7) Code review checklist (use for existing implementations)
- Tokens: no raw values; all measurements reference tokens
- Accessibility: labels, focus order, keyboard support, contrast, reduced motion
- Performance: <=100ms feedback, no layout shift, no nested scrolling in widgets
- Platform idioms: navigation, input controls, focus behavior per platform
- Localization/RTL: no clipping at large text, RTL mirroring correct
- Storybook: stories + a11y + interaction tests for new/changed components

## 5) Design tokens (single source-of-truth)
### Standard
- Author tokens in DTCG/W3C design tokens JSON (semantic-first).
- Token naming is stable; platform bindings map tokens to runtime constructs.
- Follow the latest stable Design Tokens spec referenced in `references/standards-jan-2026.md`.

### Naming
Use nested DTCG groups (no dots in token or group names):
- color/<role>/<state>
- space/<step>
- radius/<step>
- shadow/<step>
- motion/duration/<step>
- motion/easing/<step>
- type/<textStyle>/<property>
- size/<component>/<property>
- density/<mode>/<property> (for neuroinclusive density toggles)

### Units + conversions
- Token values stored in px (dimensions) and ms (durations).
- Always provide derived rem: assume 1rem=16px unless project overrides.
### DTCG token mapping (web)
Use the canonical naming and mapping guidance:
- `references/token-mapping-dtcg.md`

### Token governance (lifecycle)
Follow lifecycle rules:
- `references/token-governance.md`

### Foundations alignment (widget + cross-platform consistency)
- Prefer the foundations scale for spacing and basic type ramp when building ChatGPT-hosted UI.
- Quick reference is in `references/foundations-cheatsheet.md`.

## 6) Accessibility + neuroinclusion (hard requirements)
### Accessibility
- Provide explicit focus order per screen state.
- Provide ARIA intent mapping for all interactive controls.
- All interactive controls must have accessible names.
- Dynamic Type:
  - Web: support text scaling (do not lock line-height or container height).
- Reduced motion alternatives for every animation.
- Contrast verification for default/hover/pressed/disabled/focus states.
- Minimum contrast ratios: follow `references/contrast-minimums.md`.
- Hit targets: design for >=44x44 (or equivalent) for primary touch targets.
  - Follow the detailed checklist in `references/a11y-gold-standard.md`.
 - Directional UI: ensure RTL-safe layout and icon mirroring where appropriate.

### Neuroinclusive defaults
- Chunked content; progressive disclosure.
- Persistent labels (no placeholder-only forms).
- Predictable focus patterns; avoid surprise navigation.
- Optional density modes:
  - Comfortable (default): larger spacing/line height
  - Compact: reduced spacing while preserving hit targets

## 7) Performance gates (hard requirements)
- Interaction feedback <=100ms (visual state change, loading affordance, haptic/aural where applicable).
- Avoid nested scrolling in ChatGPT widgets; size content to contents and/or request fullscreen for complex flows.
- Avoid layout shift: reserve space for async content and media.
- Web: target Core Web Vitals (INP <=200ms, LCP <=2.5s, CLS <=0.1) unless project defines stricter gates.

## 7.5) Data safety and UX safeguards
- Prefer idempotent writes and confirmation for destructive actions.
- Redact secrets/sensitive data by default.

## 7.6) Web toolchain standards (Vite + Tailwind + React)
When delivering web/App SDK UI output, follow these:
- Vite build hygiene and asset rules (see `references/vite-build-standards.md`).
- Tailwind token mapping and theming rules (see `references/tailwind-best-practices.md`).
- React quality and accessibility rules (see `references/react-quality.md`).
- Apps SDK UI kit: prefer exact pins unless the repo standardizes ranges; in
  ChatUI follow existing package.json constraints and do not change versions
  without explicit approval. Upgrade only via explicit version bump + changelog.

## 7.7) Security by design (frontend)
- Avoid unsafe HTML injection; sanitize user content and prefer text rendering.
- Treat URLs as untrusted input; validate protocols and block javascript: or file: injection.
- Redact PII/secrets from UI logs, screenshots, and error surfaces.
- Use Content Security Policy where applicable and avoid inline scripts/styles in web builds.

## 8) Anti-Patterns to Avoid

❌ **Hard-coded measurements**: Never use `padding: 12px` or `spacing: 16` in components
   - Why: Breaks cross-platform parity; makes theming impossible; creates drift
   - Better: `padding: var(--space-3)` or `Tokens.spacing.s3`

❌ **Placeholder-only forms**: Using only placeholders without persistent labels
   - Why: Fails WCAG 2.2 AA; cognitive burden for users; disappears on input
   - Better: Always provide visible labels or use `floating-label` pattern with tokens

❌ **Animation without reduced-motion alternative**: Any animation without a static/fade fallback
   - Why: Violates accessibility preferences; causes vestibular issues
   - Better: Gate every animation with `@media (prefers-reduced-motion)` or Environment values

❌ **Ignoring localization or RTL**: Hard-coded strings, layout mirroring bugs
   - Why: Breaks internationalization and reading order; accessibility issues
   - Better: Use localization keys, allow truncation/wrapping, validate RTL

❌ **Ad-hoc state partitioning**: Mixing business data, UI state, and prefs without clear boundaries
   - Why: Widget state leaks; security issues; hard to debug sync problems
   - Better: Use a clear separation (toolOutput / widgetState / backend)

❌ **Color-only differentiation**: Using color alone to convey meaning
   - Why: Fails for color-blind users; low contrast in some modes
   - Better: Combine color with icons, patterns, or text labels

❌ **"Just add a modal"**: Using modals for everything
   - Why: Breaks flow; focus trap issues; poor on small screens
   - Better: Use inline expansion, sheets, or dedicated screens based on platform

❌ **Skip acceptance criteria**: Shipping without measurable success criteria
   - Why: Cannot verify task success; no regression guard
   - Better: Always include FEATURE_DESIGN > Acceptance criteria with measurable >=95% task success

## 9) Variation Guidance

**IMPORTANT**: Outputs MUST vary based on context. This skill should not converge on repeated "favorite" patterns.

**Dimensions that should vary**:
- **Target surface**: Widget inline (max 2 actions) vs fullscreen vs desktop window (macOS/Windows/Linux)
- **User context**: First-time user (education, affordances) vs power user (shortcuts, density)
- **Accessibility preferences**: Reduced motion (fade/skip) vs full animation; high contrast; larger text

**What creates context-appropriateness**:
- Ask about target platforms (section 3) before defaulting
- Check existing codebase patterns before creating new patterns
- Match complexity to task: simple input ≠ full screen form

**Avoid converging on**:
- Always choosing "fullscreen" for every flow
- Always using the same component library pattern
- Defaulting to "web-first" patterns on native platforms
- Reusing the exact same layout across all surfaces

## 9.5) Frontend aesthetic direction (web/React only)
When the task includes web UI construction (HTML/CSS/JS, React, or Apps SDK UI),
apply a clear, intentional visual direction. Avoid generic "AI slop" aesthetics.

Use the brand guide in `references/brand-apps-in-chatgpt.md` as the default
visual direction for all apps unless the user explicitly opts out.

Otherwise, use these rules in addition to the platform adapters:
- Pick a distinct aesthetic direction and commit to it.
- Typography: avoid generic fonts (Inter/Roboto/Arial/system); use a distinctive
  display font + refined body font pairing.
- Color: choose a cohesive palette with bold accents; avoid purple-on-white
  defaults.
- Layout: embrace asymmetry or deliberate grid breaks where appropriate.
- Motion: include at least one high-impact moment and always include a
  reduced-motion alternative.
- Backgrounds: add depth (gradients, textures, or subtle patterns) instead of
  flat single-color fills.

Detailed guidance: `references/frontend-aesthetics.md`.

## 9.5.1) Design Thinking
Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos,
  retro-futuristic, organic/natural, luxury/refined, playful/toy-like,
  editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel,
  industrial/utilitarian, etc. There are so many flavors to choose from. Use
  these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance,
  accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing
  someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision.
Bold maximalism and refined minimalism both work - the key is intentionality,
not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

Remember: Codex is capable of extraordinary creative work. Don't hold back,
show what can truly be created when thinking outside the box and committing
fully to a distinctive vision.

## 10) Surface adapters (wired in)
This umbrella skill delegates surface-specific constraints to adapters:

- Adapter: ChatGPT widget runtime + UX rules
  See: `adapters/apps-sdk-widget.md`
  Reference: `references/widget-runtime.md`

See references/extra.md for extended guidance.

## When To Use
- Use when the task matches this skill's purpose and triggers.

## Procedure
1) Confirm objective.
2) Gather required inputs.
3) Execute steps.
4) Validate output.

## Inputs
- User request
- Relevant files/paths

## Outputs
- Updated artifacts or guidance
- Summary of changes

## Constraints
- Redact secrets/sensitive data by default.
- Ask before adding dependencies or making system-wide changes.

## Validation
- Fail fast on first failed gate.
- Run required checks when applicable.

## Philosophy
- Prefer minimal, high-signal changes over broad refactors.

## Antipatterns
- Do not add features outside the agreed scope.

- Redact secrets/sensitive data by default.
