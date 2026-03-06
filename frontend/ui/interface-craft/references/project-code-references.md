# Project Code References: DialKit, Bloom, Pasito

Repository-grounded reference set for Josh-style implementation guidance in Interface Craft.

## Table of Contents
- [Repository Index](#repository-index)
- [DialKit Patterns](#dialkit-patterns)
- [Bloom Patterns](#bloom-patterns)
- [Pasito Patterns](#pasito-patterns)
- [External Component Benchmark](#external-component-benchmark)
- [How to Apply in Interface Craft Outputs](#how-to-apply-in-interface-craft-outputs)

## Repository Index

- DialKit repo: <https://github.com/joshpuckett/dialkit>
- Bloom repo: <https://github.com/joshpuckett/bloom>
- Pasito repo: <https://github.com/joshpuckett/pasito>

Package references:
- `dialkit` (npm)
- `bloom-menu` (npm package sourced from `joshpuckett/bloom`)
- `pasito` (npm)

## DialKit Patterns

Use DialKit as the baseline for live tuning and typed control schemas.

Primary source files:
- [`README.md`](https://github.com/joshpuckett/dialkit/blob/main/README.md) (setup + control taxonomy)
- [`src/hooks/useDialKit.ts`](https://github.com/joshpuckett/dialkit/blob/main/src/hooks/useDialKit.ts) (typed config resolution)
- [`src/components/DialRoot.tsx`](https://github.com/joshpuckett/dialkit/blob/main/src/components/DialRoot.tsx) (portal-mounted panel root)

Observed patterns to reuse:
1. **Root-level tuning surface**: mount `DialRoot` once near app root and keep feature components clean.
2. **Typed control inference**: schema maps to resolved values (number, boolean, color, select, spring, nested folders).
3. **Action callbacks over hidden state**: explicit `onAction` handlers for side-effectful controls.
4. **Spring-first knobs**: tune `visualDuration` and `bounce` directly for animation feel.

## Bloom Patterns

Use Bloom as the baseline for compound composition + morphing interactions.

Primary source files:
- [`README.md`](https://github.com/joshpuckett/bloom/blob/main/README.md) (API shape + a11y commitments)
- [`packages/bloom/src/Root.tsx`](https://github.com/joshpuckett/bloom/blob/main/packages/bloom/src/Root.tsx) (controllable root state + context contract)
- [`packages/bloom/src/Container.tsx`](https://github.com/joshpuckett/bloom/blob/main/packages/bloom/src/Container.tsx) (direction-aware morph container)
- [`packages/bloom/src/SubMenuTrigger.tsx`](https://github.com/joshpuckett/bloom/blob/main/packages/bloom/src/SubMenuTrigger.tsx) (render-prop active states + keyboard interaction)

Observed patterns to reuse:
1. **Compound components**: `Root`, `Container`, `Trigger`, `Content`, `Item`, and submenu primitives.
2. **Controllable/uncontrolled parity**: `open`, `onOpenChange`, `defaultOpen` contract.
3. **Directional layout math**: direction/anchor and transform-origin are first-class concerns.
4. **A11y as behavior, not garnish**: role attributes, keyboard handlers, and reduced-motion branching are built into component logic.
5. **Morphing container mechanics**: animate width/height/radius/offset from trigger state to menu state.

## Pasito Patterns

Use Pasito as the baseline for tiny UI primitives, themeability, and constrained motion.

Primary source files:
- [`packages/pasito/README.md`](https://github.com/joshpuckett/pasito/blob/main/packages/pasito/README.md) (API + theming model)
- [`packages/pasito/src/react/Stepper.tsx`](https://github.com/joshpuckett/pasito/blob/main/packages/pasito/src/react/Stepper.tsx) (state-driven rendering + CSS custom property injection)
- [`packages/pasito/src/react/hooks/useAutoPlay.ts`](https://github.com/joshpuckett/pasito/blob/main/packages/pasito/src/react/hooks/useAutoPlay.ts) (headless timing hook contract)
- [`packages/pasito/src/styles/Stepper.css`](https://github.com/joshpuckett/pasito/blob/main/packages/pasito/src/styles/Stepper.css) (tokenized CSS variable surface + reduced-motion fallback)

Observed patterns to reuse:
1. **CSS-variable-first theming**: expose visual tokens instead of hardcoded styling.
2. **Headless logic + view split**: timing/control logic in hooks, rendering in components.
3. **Small public API**: concise component + hook interface with sensible defaults.
4. **Accessibility defaults**: tablist semantics, selected state annotations, keyboard-focus support.
5. **Reduced-motion guardrails**: transitions collapse when user preference requests reduced motion.

## External Component Benchmark

- Component Gallery: <https://component.gallery>

When to use:
1. user asks for component-level inspiration or quality benchmarking;
2. we need additional pattern breadth beyond DialKit/Bloom/Pasito.

How to use safely:
1. extract interaction/architecture patterns, not brand visuals;
2. translate into project-native constraints (tokens, spacing, accessibility, performance);
3. include a short “why this pattern fits” justification in output.

## How to Apply in Interface Craft Outputs

When users ask for Josh-style coding guidance:

1. **Cite at least one concrete source pattern** from DialKit, Bloom, or Pasito.
2. **Match pattern to intent**:
   - live tuning -> DialKit
   - morphing menus / compound architecture -> Bloom
   - lightweight, themeable, token-driven primitives -> Pasito
3. **Translate into imperative guidance**:
   - “Expose controllable state props”
   - “Move timing logic into a hook”
   - “Make visual tokens CSS variables”
4. **Carry forward quality gates**:
   - keyboard-first interactions
   - ARIA/state semantics
   - reduced-motion handling
