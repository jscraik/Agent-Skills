# Emil Persona Research Pack (NotebookLM, 2026-03-07)

## Table of Contents
- [Source context](#source-context)
- [High-signal principles](#high-signal-principles)
- [Common anti-patterns](#common-anti-patterns)
- [Implementation patterns](#implementation-patterns)
- [Sonner and Vaul engineering signals](#sonner-and-vaul-engineering-signals)
- [Validation checklist for responses](#validation-checklist-for-responses)
- [How to apply in persona outputs](#how-to-apply-in-persona-outputs)

## Source context
- Source notebook URL:
  <https://notebooklm.google.com/notebook/240f2b0d-729f-49c1-88c6-7f0c2e1f09ac?authuser=1>
- Retrieval method:
  - `python3 scripts/run.py ask_question.py --notebook-url ...` (NotebookLM skill workflow)
  - Three queries were used:
    1. notebook overview + recurring principles
    2. top principles, anti-patterns, concrete snippets, validation checklist
    3. Sonner/Vaul-specific implementation and DX guidance

## High-signal principles
1. Motion must have purpose (state continuity, feedback, hierarchy) rather than decoration.
2. Keep UI animation fast (typically under ~300ms) to preserve perceived responsiveness.
3. Interactive motion must be interruptible and retargetable.
4. Prioritize hardware-friendly properties (`transform`, `opacity`, `clip-path`) for smoothness.
5. Use immediate tactile feedback for interactions (for example subtle `:active` scale).
6. Prefer custom, natural-feeling easing (usually ease-out for entry).
7. Make motion origin-aware so UI appears from the triggering element.
8. Respect momentum/velocity for gesture-driven interactions.
9. Use percentage-based transforms for dynamic-size elements.
10. Treat reduced motion as first-class with practical fallback behavior.

## Common anti-patterns
- Animating high-frequency and keyboard-driven actions (adds friction over time).
- Entering from `scale(0)` (often feels abrupt/artificial).
- Overusing `ease-in` for UI entry (slow start feels laggy).
- Using `linear` for spatial movement (robotic feel; keep for progress/time visuals).
- Using rigid keyframes for rapidly changing interactive state where interruption is needed.
- Keeping tooltip delays for every adjacent item in a cluster.

## Implementation patterns
- **Button press feedback**
```css
button:active { transform: scale(0.97); transition: transform 150ms ease-out; }
```
- **Origin-aware dropdown**
```css
.menu { transform-origin: bottom center; }
```
- **Dynamic element off-screen positioning**
```css
.panel { transform: translateY(100%); }
```
- **Clip-path reveal without layout shifts**
```css
.active-mask { clip-path: inset(0 0 100% 0); }
.active-mask[data-open='true'] { clip-path: inset(0 0 0 0); }
```
- **Velocity-aware dismiss logic**
```text
velocity = distance / time
if velocity > threshold => dismiss, else snap back
```

## Sonner and Vaul engineering signals
- **DX-first APIs:** prefer low-friction integration and familiar primitives.
  - Example signals: observer-style toast trigger ergonomics and promise-state helpers.
- **Gesture quality details:** pointer capture, damping, velocity projection, and snap logic.
- **Mobile robustness:** handle scroll-vs-drag conflicts and viewport/keyboard behavior.
- **State/runtime hygiene:** pause timers when document is hidden.
- **Docs as product:** interactive examples, copy-paste snippets, and explanation of “why it feels better.”

## Validation checklist for responses
- Does the response start with purpose + constraints?
- Are recommendations concrete and implementation-ready?
- Is interaction frequency considered before adding motion?
- Are performance-sensitive properties prioritized?
- Is interruptibility covered for interactive elements?
- Is reduced-motion behavior included?
- Is at least one practical test loop included (slow motion, interruption, real device)?

## How to apply in persona outputs
1. Lead with practical tradeoffs (feel vs speed vs accessibility vs DX).
2. Use concise implementation examples, not abstract statements only.
3. Prefer “remove animation” recommendations for repetitive/high-frequency flows.
4. Include one verification loop to keep quality measurable.
5. When user asks for evidence, cite this research pack plus concrete patterns.
