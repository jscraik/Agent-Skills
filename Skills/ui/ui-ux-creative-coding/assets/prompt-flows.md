# Prompt Flows (Codex + Claude Code)

These are ready-to-run prompts. Replace bracketed parts.

---

## 1) “3 variants, pick one, implement”
**Prompt**
1. Create 3 UI variants for: [feature/screen/component].
2. Each variant must include:
   - layout + hierarchy decisions
   - token usage (Tailwind v4 `@theme` / CSS vars)
   - Radix primitive choices (if interactive)
   - motion notes (durations/easing, reduced motion)
   - a11y notes (keyboard/focus/labels)
3. Compare tradeoffs and pick the best.
4. Implement in code + add Storybook story + update acceptance checklist.

Constraints:
- Platform: [Tauri desktop / web / ChatGPT app]
- Tone: [calm/precise/playful/etc]
- Perf budget: [e.g., no always-on animation]

---

## 2) “Make it feel better” motion pass
**Prompt**
Given this component/screen: [paste code or describe],
1. Identify the 1–2 most important moments for feedback.
2. Add motion that communicates state (not decoration).
3. Keep durations within the motion spec. Respect prefers-reduced-motion.
4. Provide a before/after explanation and the patch.

---

## 3) Figma → tokens → Tailwind v4 mapping
**Prompt**
We have a Figma file with variables:
- Colors: [names or export]
- Type scale: [names]
- Radii: [names]
Map these into:
1. `assets/tokens.json` (semantic tokens)
2. Tailwind v4 `@theme` output (CSS vars)
3. A short “how to use” note for developers.

If values are missing, make conservative defaults and label them “assumed”.

---

## 4) Radix component spec → implementation
**Prompt**
Implement [component] using Radix primitives:
- Must support keyboard navigation and focus-visible styling.
- Style via Tailwind v4 + data-state attributes.
- Include variants: [list]
- Add Storybook stories for each variant + key states.

---

## 5) Apps SDK UI: choose view type + layout
**Prompt**
We’re building a ChatGPT app screen for: [task].
Decide whether this should be:
- inline card
- carousel
- fullscreen
Then design the layout + states:
- loading
- error
- empty
Also propose one “smile” detail that fits the constrained UI.
