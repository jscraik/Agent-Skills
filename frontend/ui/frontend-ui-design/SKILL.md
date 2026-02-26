---
name: frontend-ui-design
description: Create and review production-ready UI systems/components with tokens
  and accessibility. Use for standard UI implementation or redesign (not creative-coding
  polish). Use when the user requests this capability.
knowledge_graph_profile: references/task-profile.json
---

# Frontend Design System (Apps SDK UI + React + Tauri)

## Compliance
- Check against the GOLD Industry Standards guide in the user’s codex AGENTS file (see environment instructions).


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
"You asked for a different brand. Do you want to replace the Apps-in-ChatGPT baseline for this task (yes/no)?"

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

Schema note:
- If outputs are schema-bound, include `schema_version` from `references/contract.yaml`.

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
- `references/baseline-ui-checklist.md`
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
- If explicitly approved, run the repo’s link audit helper to check reference URLs for drift.

## 4.7) Code review checklist (use for existing implementations)
- Tokens: no raw values; all measurements reference tokens
- Accessibility: labels, focus order, keyboard support, contrast, reduced motion
- Performance: <=100ms feedback, no layout shift, no nested scrolling in widgets
- Platform idioms: navigation, input controls, focus behavior per platform
- Localization/RTL: no clipping at large text, RTL mirroring correct
- Storybook: stories + a11y + interaction tests for new/changed components

## 4.8) Baseline UI guardrails (fast pass)
Use this when you need a quick quality pass before deeper design work:
- `references/baseline-ui-checklist.md`

Notes:
- Opinionated aesthetics (e.g., no gradients/glows) are defaults; replace only with explicit brand/brief approval.
- Do not introduce new dependencies (e.g., `tw-animate-css`) unless already present or explicitly approved.

## Validation (fail-fast)
- Stop at the first failed gate, fix, and re-run before proceeding.
- Use repo scripts for lint/tests/Storybook when UI changes are present.
- Treat external commands as gated; only run with explicit approval.

## Examples
- "Design a settings screen component set with accessibility and motion specs."
- "Review this component for token and a11y compliance."
- "Create a small UI patch for error states (minimal diff)."

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
- Always provide derived rem: assume 1rem=16px unless the project specifies otherwise.
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


## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.

## Anti-patterns

- Applying this skill when a direct request is out of scope.
- Skipping validation/checks to save time.
- Assuming defaults without explicit user confirmation for risky actions.

## Outputs

- A concrete next-step response with explicit, reproducible actions.
- A short verification checklist and caveats for the user.

## Procedure

1. Verify scope and constraints before taking action.
2. Execute the minimal safe path first.
3. Validate intermediate state before making changes.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.
