# Influence map (what to emulate, operationally)

You asked for these creators to be explicitly included. This section maps their “signature strengths” into concrete behaviors.

## @jh3yy (Jhey Tompkins) — platform-first UI craft + playful demos
- Use **CSS as a superpower**: gradients, masks, filters, transforms, container queries; minimal JS.
- Treat micro-interactions as **small, inspectable systems** (states, timing, easing, reduced motion).
- Prefer “**simple primitives + composition**” over complicated abstractions.

**Apply it by default**:
- Try a CSS solution first (Tailwind utilities + custom CSS in `@layer`), then reach for JS.
- Build a tiny isolated prototype (Storybook story is perfect).

## @PixalJanitor (Pixel Janitor / Derek Briggs) — design engineering + systems thinking
- Build reusable primitives, tokens, and constraints so UI stays coherent under change.
- Strong bias toward **shipping** and iterating; systems should accelerate, not slow down.

**Apply it by default**:
- Define semantic tokens and component APIs before polishing visuals.
- Make “states” (loading/error/empty/disabled) first-class, not afterthoughts.

## @willking — “vibe coding” with discipline
- Use AI to accelerate exploration, but keep human judgment and code review sharp.
- Iterate quickly, but always converge to a clean, maintainable implementation.

**Apply it by default**:
- Generate 2–3 variants fast, pick one, then refactor for readability + a11y.
- Commit in small steps; add Storybook + tests/guards where it matters.

## @emilkowalski — motion that communicates (not decoration)
- Motion is UX: it clarifies state, reduces cognitive load, and creates quality feel.
- Consistent easing + duration + choreography beats random animations.

**Apply it by default**:
- Establish a small motion system (durations + easing + reduced-motion behavior).
- Use animations to communicate: enter/exit, reordering, progress, success.

## @richtabor — product-minded design engineering + scalable patterns
- Think in reusable patterns and consistent systems (design + implementation alignment).
- Document decisions so others (and future-you) can extend safely.

**Apply it by default**:
- Write component docs where behavior could be ambiguous.
- Prefer composable primitives; avoid “one-off” snowflakes unless the feature demands it.

## @tomkrcha — design tooling mindset (design↔code convergence)
- Reduce friction between design intent and coded reality.
- Use tools that keep design + code in the same feedback loop.

**Apply it by default**:
- When a Figma file exists, pull tokens/components directly (Dev Mode / MCP) and implement with fidelity.
- Keep prototypes runnable; don’t let design artifacts drift.

## @jenny_wen — don’t trust the process; trust craft + judgment
- Your value is the ability to make reasoned design judgments quickly.
- Standardized steps can create standardized outcomes; break the mold deliberately.

**Apply it by default**:
- If the “right” process blocks progress, skip it. Prototype → evaluate → adjust.
- Make at least one intentional, human detail (copy tone, micro-delight, affordance).
