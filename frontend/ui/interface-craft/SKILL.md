---
name: interface-craft
description: Interface Craft by Josh Puckett helps build polished React interfaces with Motion + DialKit, CSS-variable theming, storyboard motion, and critique/range/depth workflows; use when requests involve UI motion, critique, refinement, concept exploration, or interaction craft.
---

# Interface Craft

**By Josh Puckett**

A toolkit for building polished, animated interfaces. Write motion like a script, tune values live, critique with specificity, explore conceptual range, then push depth with uncommon care.

---

## Table of Contents
- [Skills](#skills)
- [Quick Start](#quick-start)
- [Tech + Coding Baseline](#tech--coding-baseline)
- [Critique Order](#critique-order)
- [Try It Out](#try-it-out)
- [Sub-Skill Routing](#sub-skill-routing)
- [Design Principles](#design-principles)
- [Reference Map](#reference-map)
- [When to use](#when-to-use)
- [Anti-patterns](#anti-patterns)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Examples](#examples)
- [Constraints / Safety](#constraints--safety)
- [Validation](#validation)

## Skills

| Skill | When to Use | Invoke |
| --- | --- | --- |
| [Storyboard Animation](storyboard-animation.md) | Writing or refactoring multi-stage animations into a readable, stage-driven DSL | `/interface-craft storyboard` or describe an animation |
| [DialKit Live Tuning](dialkit.md) | Building real-time control panels to feel value changes instantly and explore variants | `/interface-craft dialkit` or mention sliders/dials/controls |
| [Design Critique](design-critique.md) | Systematic UI critique using noticing, expectation gaps, and uncommon-care opportunities | `/interface-craft critique` or paste a screenshot |
| [Conceptual Range](conceptual-range.md) | Generating structurally different UX directions before going deep on implementation | `/interface-craft range` or ask for alternatives/concepts |
| [Conceptual Depth](conceptual-depth.md) | Refining one chosen concept through progressive quality levels (1→10) | `/interface-craft depth` or ask to push/polish/refine further |
| [Separation of Concerns](separation-of-concerns.md) | Isolating one design question at a time with right-fidelity prototypes | `/interface-craft concerns` or ask for a minimal focused prototype |
| [Recreate Everything](recreate-everything.md) | Reverse-engineering inspiring interactions fast to learn techniques and expand your toolbelt | `/interface-craft recreate` or ask “how did they do this?” |
| [Industry Standards](industry-standards.md) | Benchmarking quality against platform/category expectations before innovating | `/interface-craft standards` or ask where the baseline bar is |

## Quick Start

### Storyboard Animation
```tsx
const TIMING = {
  cardAppear: 300,
  heading: 900,
  rows: 1500,
}
```

### DialKit
```tsx
const params = useDialKit('Card', {
  scale: [1, 0.5, 2],
  blur: [0, 0, 100],
  spring: { type: 'spring', visualDuration: 0.3, bounce: 0.2 },
})
```

### Range → Depth
Use conceptual range when the core solution may be wrong. Once a direction is chosen, use conceptual depth to push quality beyond “good enough.”

## Tech + Coding Baseline

Use these defaults unless the user asks for a different stack:

1. **React + motion + DialKit** — use React for component composition, `motion` (Framer Motion) for non-trivial animation, and DialKit for live parameter tuning.
2. **Compound components first** — structure complex widgets into modular parts (`Root`, `Container`, `Item`, `SubMenu`) instead of monolith components.
3. **Expose controllable state** — support controlled props (`open`, `onOpenChange`, `value`, `onValueChange`) and keep internal orchestration inside hooks.
4. **Render-prop state when useful** — pass active/selected state to children when it improves customization and removes brittle prop plumbing.
5. **Theme with CSS variables** — avoid hardcoded tokens; use component-prefixed custom properties so teams can retheme safely.
6. **Spring-first motion** — prefer spring physics with tunable `visualDuration` + `bounce`; use refined cubic-bezier fallback only when springs are not viable.
7. **Keyboard + accessibility by default** — verify `tabIndex`, ARIA roles/states/labels, and test `prefers-reduced-motion` behavior before final polish.
8. **Avoid black-box dependencies** — prefer small, transparent components where state and callbacks are interceptable.

## Critique Order

Run critique in this order for consistent Josh-style reviews:

1. **Motion + polish** — assess sequence quality, spring feel, and “uncommon care” details first.
2. **Accessibility + input modes** — confirm keyboard-first flow, ARIA correctness, and reduced-motion safety.
3. **Architecture + theming** — verify component structure, state API clarity, and CSS-variable-driven customization.

## Try It Out

- **Build and tune a component**
  “Build a notification toast that slides in from the top with a spring animation. Add DialKit controls for spring, opacity, and vertical offset so I can tune it in real time.”

- **Get a design critique**
  “Review the settings page component for design quality. Look at hierarchy, spacing, color usage, and interaction patterns. What would you improve?”

- **Choreograph a complex animation**
  “Create a page transition where the old content fades out, then the new content slides up with staggered children. Use the storyboard animation pattern for sequencing and add DialKit controls for each timing value.”

## Sub-Skill Routing

When the user invokes `/interface-craft`:

1. **Storyboard context** (`storyboard`, animation sequencing, motion timing cleanup) → [storyboard-animation.md](storyboard-animation.md)
2. **Dial controls context** (`dialkit`, sliders, tune, tweak, control panel) → [dialkit.md](dialkit.md)
3. **Critique context** (`critique`, `review`, screenshot/image feedback) → [design-critique.md](design-critique.md)
4. **Range context** (`alternatives`, `options`, `breadth`, `concept exploration`, `don’t commit too early`) → [conceptual-range.md](conceptual-range.md)
5. **Depth context** (`push further`, `polish`, `iterate`, `1 to 10`, `world class`) → [conceptual-depth.md](conceptual-depth.md)
6. **Concern-isolation context** (`minimal prototype`, `just test interaction`, `wireframe fidelity`, `one question`) → [separation-of-concerns.md](separation-of-concerns.md)
7. **Recreate context** (`how did they do this`, `recreate`, `reverse engineer interaction`) → [recreate-everything.md](recreate-everything.md)
8. **Standards context** (`industry standard`, `is this below baseline`, `platform expectations`) → [industry-standards.md](industry-standards.md)
9. **File path only** → Inspect file, select best matching workflow (or combine critique + range + depth)
10. **Ambiguous** → Ask which workflow they want first

## Design Principles

1. **Readable over clever** — anyone should scan the top of a file and understand the flow
2. **Tunable by default** — every critical value should be named and adjustable
3. **Data-driven structures** — repeated elements come from arrays and `.map()`
4. **Stage-driven motion** — one stage state coordinates sequence timing
5. **Noticing before fixing** — capture concrete observations before prescribing changes
6. **Range before commitment** — generate structurally different concepts before optimizing a single one
7. **Depth after selection** — once a direction is selected, iterate deliberately from baseline to exceptional
8. **Uncommon care** — improve edge cases, error paths, and overlooked moments that build trust
9. **Concern isolation** — resolve one design question at a time at the right level of fidelity
10. **Recreate to learn** — replicate inspiring patterns quickly to build capability
11. **Meet the baseline, then innovate** — respect platform/category standards before deviation
12. **Tools must match the medium** — favor adaptive, responsive, data-real workflows over static mock certainty
13. **Design as systems** — components, constraints, and reusable primitives over one-off screens
14. **Keyboard-first confidence** — treat keyboard and reduced-motion support as quality gates, not cleanup
15. **Themeable by construction** — expose styling via CSS variables and avoid hardcoded visual tokens

## Reference Map

- [Noticing + critique lens](design-critique.md)
- [Concept generation breadth](conceptual-range.md)
- [Refinement and quality ladder](conceptual-depth.md)
- [Focused prototype strategy](separation-of-concerns.md)
- [Reverse-engineering workflow](recreate-everything.md)
- [Baseline quality benchmarking](industry-standards.md)
- [Live tuning panel patterns](dialkit.md)
- [Storyboard sequencing pattern](storyboard-animation.md)
- [Principles summary](references/josh-principles.md)
- [Refinement case patterns](references/refinement-case-studies.md)
- [Persona style + corpus synthesis](references/persona-profile.md)
- [Project-backed code references (DialKit/Bloom/Pasito)](references/project-code-references.md)
- [Coding defaults + critique tone cues](references/persona-profile.md#preferred-coding-tech-and-tooling)
- [Component benchmark library](https://component.gallery)

## When to use

- Use this skill for React/UI motion design, visual/interface critique, interaction refinement, and concept range/depth workflows.
- Use this skill when users ask for better polish, clearer hierarchy, “how to make this feel better,” or to recreate notable interaction patterns.
- Do not use this skill for backend-only optimization or non-UI infrastructure work.

## Anti-patterns

- Jumping to fixes before a noticing/diagnosis pass.
- Treating cosmetic variants as conceptual range.
- Overbuilding fidelity before resolving the core concern.
- Ignoring platform/category baseline standards before innovating.

## Inputs

- User intent and target workflow (storyboard, dialkit, critique, range, depth, concerns, recreate, standards).
- Interface artifact: screenshot, component path/code, or URL.
- Platform/context constraints (web/iOS/etc.) and quality goals/facets (if provided).

## Outputs

- Structured critique and refinement plans, or implementation-ready motion/tuning snippets.
- Ranked opportunities and tradeoffs grounded in user impact.
- Workflow-specific artifacts (range options, depth ladder, baseline gap assessment, recreate plan).
- For code-level guidance, include a compact **Repo Pattern to Borrow** block (source, rationale, smallest implementation step).

## Procedure

1. Route to the correct sub-skill based on user intent and evidence available.
2. Run the minimum workflow needed to answer the user’s request.
3. If the response includes implementation guidance, include one repo-grounded pattern from DialKit, Bloom, or Pasito using each sub-skill’s copy-ready snippet format.
4. Validate output against baseline quality and stated goals before finalizing.

## Examples

- “Build and tune a notification toast with DialKit controls.”
- “Critique this settings page and tell me what to improve first.”
- “Give me 3 structurally different concepts before we commit.”
- “Push this component from level 3 to level 8 with uncommon-care refinements.”

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default.
- Prefer reversible edits and explicit assumptions.
- Do not claim visual certainty from code-only review; label inferred observations.

## Validation

- Fail fast on missing context or blocked inputs.
- Re-check that routing (storyboard/dialkit/critique/range/depth/concerns/recreate/standards) matches user intent.
- For critique/range/depth outputs, prioritize structural and behavioral issues before visual polish.
- For implementation guidance, verify a concrete **Repo Pattern to Borrow** block is present.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
