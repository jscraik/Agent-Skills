# Component.gallery Playbook

## Table of Contents
- [Why use component.gallery](#why-use-componentgallery)
- [Operator checklist (copy/paste)](#operator-checklist-copypaste)
- [Default workflow](#default-workflow)
- [Extraction template](#extraction-template)
- [Filled example (drawer)](#filled-example-drawer)
- [Filled example (modal)](#filled-example-modal)
- [Filled example (popover)](#filled-example-popover)
- [Decision rules](#decision-rules)
- [Safety and adaptation rules](#safety-and-adaptation-rules)
- [Useful links](#useful-links)

## Why use component.gallery
`component.gallery` is a curated reference for real-world component implementations across systems and stacks.

Use it to:
- compare multiple implementation approaches,
- identify feature and accessibility expectations,
- decide fit by technology constraints,
- avoid reinventing patterns that are already proven.

## Operator checklist (copy/paste)
Use this when you need a fast benchmark pass.

- [ ] **Pick component:** modal / drawer / popover / dropdown / tabs / tooltip.
- [ ] **Open page:** component page + aliases/definition.
- [ ] **Filter:** apply Tech + Features filters relevant to the stack.
- [ ] **Collect 3+:** capture at least three comparable systems.
- [ ] **Record states:** default, hover/focus/active, loading, empty, error, disabled.
- [ ] **Record accessibility:** keyboard/focus behavior, semantics, reduced-motion expectations.
- [ ] **Choose default + fallback:** include one explicit tradeoff.
- [ ] **Write rationale:** why selected pattern fits product + stack constraints.
- [ ] **Add adaptation note:** how to implement in React/Tailwind/Radix/Tauri.

## Default workflow
1. Start with the target component page (for example modal/drawer/dropdown).
2. Scan aliases and definitions to validate terminology.
3. Filter by **Tech** and **Features** when available.
4. Collect patterns from at least 3 comparable systems.
5. Capture:
   - behavior states,
   - accessibility notes,
   - implementation implications for React/Tailwind/Radix/Tauri.
6. Choose one default pattern and one fallback with tradeoffs.

## Extraction template
- Component:
- Candidate systems reviewed:
- Shared baseline behaviors:
- Accessibility expectations:
- Motion/interaction expectations:
- Stack-fit notes:
- Recommended pattern:
- Alternative considered:
- Why rejected:

## Filled example (drawer)
- Component: Drawer
- Candidate systems reviewed: Radix-like pattern, mobile bottom-sheet style, panel-over-content style
- Shared baseline behaviors:
  - open/close trigger,
  - dismiss via ESC / backdrop / close action,
  - focus management and return to trigger,
  - scroll lock strategy.
- Accessibility expectations:
  - keyboard path complete,
  - semantic role/labels present,
  - reduced-motion variant.
- Motion/interaction expectations:
  - interruptible open/close transitions,
  - no abrupt teleport when state changes quickly.
- Stack-fit notes:
  - React + Radix + Tailwind v4 favors composable primitives and tokenized durations/easing.
- Recommended pattern:
  - composable, token-driven drawer with explicit state model and reduced-motion parity.
- Alternative considered:
  - highly stylized custom physics drawer.
- Why rejected:
  - higher implementation complexity and lower predictability for current product timeline.

## Filled example (modal)
- Component: Modal / Dialog
- Candidate systems reviewed: native dialog-style pattern, headless composable dialog, full-screen mobile modal variant
- Shared baseline behaviors:
  - open/close trigger,
  - ESC + backdrop dismissal rules,
  - initial focus and focus return behavior,
  - background interaction lock.
- Accessibility expectations:
  - role/label semantics defined,
  - keyboard traversal and focus trap correctness,
  - reduced-motion open/close variant.
- Motion/interaction expectations:
  - quick, clear enter/exit with interruptibility,
  - avoid heavy blur/scale effects that hurt readability.
- Stack-fit notes:
  - React + Radix + Tailwind v4 supports tokenized overlay/content transitions with composable primitives.
- Recommended pattern:
  - composable dialog with strict a11y baseline and restrained token-driven motion.
- Alternative considered:
  - highly stylized full-screen animated takeover modal.
- Why rejected:
  - introduces unnecessary cognitive load for frequent workflows and complicates reduced-motion parity.

## Filled example (popover)
- Component: Popover
- Candidate systems reviewed: anchored popover menu, rich-content popover panel, command-style popover
- Shared baseline behaviors:
  - anchored placement to trigger,
  - open/close by click/keyboard,
  - outside-click + ESC dismissal,
  - focus return to trigger on close.
- Accessibility expectations:
  - semantic trigger and labelled content,
  - keyboard navigation for interactive content,
  - no hover-only critical actions.
- Motion/interaction expectations:
  - origin-aware enter/exit from trigger position,
  - short interruptible transitions,
  - reduced-motion fallback (opacity-only or instant).
- Stack-fit notes:
  - React + Radix + Tailwind v4 maps well to composable anchored popovers with tokenized motion and collision-aware positioning.
- Recommended pattern:
  - anchored, composable popover with strict focus/dismiss rules and minimal motion.
- Alternative considered:
  - custom physics-based floating panel with continuous pointer-follow effects.
- Why rejected:
  - higher complexity, weaker accessibility predictability, and unnecessary overhead for product workflows.

## Decision rules
- Prefer patterns with clear state coverage and accessibility support.
- Prefer patterns that map to existing stack constraints over novelty.
- Prefer composable primitives over monolithic one-off solutions.
- When uncertain, pick the simplest pattern that remains extensible.

## Safety and adaptation rules
- Do not visually clone a source implementation.
- Extract principles and adapt to product context, brand, and constraints.
- Keep reduced-motion and keyboard parity explicit in the final recommendation.
- Cite the comparison rationale, not just final taste preference.

## Useful links
- Home: <https://component.gallery/>
- Components index: <https://component.gallery/components>
- About/method: <https://component.gallery/about>
- Local quick card: `assets/component-benchmark-quick-card.md`
