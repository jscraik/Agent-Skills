# Acceptance Checklist (definition of done)

## UX
- [ ] The primary user task can be completed quickly with no confusion.
- [ ] States exist and look intentional: loading, empty, error (and offline if needed).
- [ ] Copy is clear and action-oriented; labels match user mental model.
- [ ] At least one “smile” detail exists *without* harming speed/usability.

## Component system
- [ ] Component APIs are consistent with the system (variants, sizes, slots).
- [ ] Tokens are used (no random magic numbers for spacing/typography).
- [ ] State styling uses `data-*` / CSS vars cleanly (especially with Radix).

## Accessibility
- [ ] Keyboard-only flow works end-to-end.
- [ ] Focus is always visible and never trapped incorrectly.
- [ ] Screen reader labels are correct (where applicable).
- [ ] `prefers-reduced-motion` is respected.
- [ ] Contrast meets minimums (run `scripts/contrast_check.mjs` if using `assets/tokens.json`).

## Performance
- [ ] No continuous animation without justification.
- [ ] No layout-thrashing animations; transforms/opacity preferred.
- [ ] Interaction remains responsive under load.
- [ ] If WebGL is used: fallback exists and GPU cost is bounded.

## Quality pipeline
- [ ] Storybook story exists for each new/changed component.
- [ ] Argos snapshots cover key variants/states.
- [ ] Biome + TypeScript pass clean.
- [ ] Any tricky behavior is documented (short note in code or docs).

## Apps SDK (if building a ChatGPT app)
- [ ] View type choice is intentional (inline card / carousel / fullscreen).
- [ ] Loading and error states are explicit and helpful.
- [ ] Output is readable in the constrained UI space.
