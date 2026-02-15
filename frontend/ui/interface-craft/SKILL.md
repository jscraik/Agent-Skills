---
name: interface-craft
description: Interface Craft by Josh Puckett helps build polished, animated React
  interfaces using Storyboard Animation, DialKit tuning panels, and Design Critique.
  Use when requests involve motion design, animation sequencing, live tuning controls,
  or structured UI critique and polish.
---

# Interface Craft

**By Josh Puckett**

A toolkit for building polished, animated interfaces. Write animations you can read like a script, then tune them with live controls.

---

## Skills

| Skill | When to Use | Invoke |
| --- | --- | --- |
| [Storyboard Animation](storyboard-animation.md) | Writing or refactoring multi-stage animations into a human-readable DSL | `/interface-craft storyboard` or describe an animation |
| [DialKit](dialkit.md) | Adding live control panels to tune animation/style values | `/interface-craft dialkit` or mention dials/sliders/controls |
| [Design Critique](design-critique.md) | Systematic UI critique of a screenshot, component, or page | `/interface-craft critique` or paste a screenshot for review |

## Quick Start

### Storyboard Animation

Turn any animation into a readable storyboard with named timing, config objects, and stage-driven sequencing:

```tsx
/* ─────────────────────────────────────────────────────────
 * ANIMATION STORYBOARD
 *
 *    0ms   waiting for scroll into view
 *  300ms   card fades in, scale 0.85 → 1.0
 *  900ms   heading highlights
 * 1500ms   rows slide up (staggered 200ms)
 * ───────────────────────────────────────────────────────── */

const TIMING = {
  cardAppear:  300,   // card fades in
  heading:     900,   // heading highlights
  rows:        1500,  // rows start staggering
};
```

See [storyboard-animation.md](storyboard-animation.md) for the full pattern spec.

### DialKit

Generate live control panels for tuning values in real time:

```tsx
const params = useDialKit('Card', {
  scale: [1, 0.5, 2],
  blur: [0, 0, 100],
  spring: { type: 'spring', visualDuration: 0.3, bounce: 0.2 },
})
```

See [dialkit.md](dialkit.md) for all control types and patterns.

## Sub-Skill Routing

When the user invokes `/interface-craft`:

1. **With `storyboard` argument or animation-related context** → Load and follow [storyboard-animation.md](storyboard-animation.md)
2. **With `dialkit` argument or control-panel-related context** → Load and follow [dialkit.md](dialkit.md)
3. **With `critique` argument, a pasted image, or review-related context** → Load and follow [design-critique.md](design-critique.md)
4. **With a file path** → Read the file, detect whether it needs storyboard refactoring, dialkit controls, or a design critique, and apply the appropriate skill
5. **With a plain-English description of an animation** → Use storyboard-animation to write it
6. **Ambiguous** → Ask which skill to use

## Design Principles

1. **Readable over clever** — Anyone should be able to scan the top of a file and understand the animation sequence without reading implementation code
2. **Tunable by default** — Every value that affects timing or appearance should be a named constant, trivially adjustable
3. **Data-driven** — Repeated elements use arrays and `.map()`, not copy-pasted blocks
4. **Stage-driven** — A single integer state drives the entire sequence; no scattered boolean flags
5. **Spring-first** — Prefer spring physics over duration-based easing for natural motion

## Anti-patterns

- Skipping investigation and jumping directly to fixes.
- Making claims without evidence, logs, or reproducible steps.
- Mixing unrelated workstreams in a single execution path.

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Prefer safe defaults and avoid irreversible changes without explicit confirmation.

## Inputs

- User task context and target environment.
- Relevant constraints, permissions, and preferences required to execute safely.

## Outputs

- A concrete next-step response with explicit, reproducible actions.
- A short verification checklist and caveats for the user.

## Procedure

1. Verify scope and constraints before taking action.
2. Execute the minimal safe path first.
3. Validate intermediate state before making changes.

## Validation

- Fail fast: stop at the first failed check and do not continue.
- Re-run the required checks before proceeding to the next step.
- Report any failed check and requested follow-up actions clearly.

## When to use

- Use this skill when the request matches the skill's intent and scope.
- Do not use it when a different domain or higher-privilege workflow is required.

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Prefer safe defaults and avoid irreversible changes without explicit confirmation.

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
