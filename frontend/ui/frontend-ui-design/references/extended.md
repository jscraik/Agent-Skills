# Extended guidance

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
