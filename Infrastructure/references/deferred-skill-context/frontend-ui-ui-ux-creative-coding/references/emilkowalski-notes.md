# Emil Kowalski — Motion Craft Notes (Refresh 2026-03-18)

Use these notes when shaping motion craft. For interaction‑level guidance, see `emilkowalski-interactions.md`.

## Core principles
- **Motion is UX communication**: every movement should explain state, intent, or change.
- **Timing + easing are decisions**: select values deliberately; avoid defaults without rationale.
- **Less but better**: if motion doesn’t improve clarity or feedback, remove it.
- **Consistency across components**: choreography, durations, and easing should harmonize.
- **Invisible details compound**: transform origins, press states, and interruption handling matter even when users do not name them.

## Animation decision framework
- **Frequency first**: high-frequency, keyboard-led actions usually deserve no motion or only minimal visual confirmation.
- **Purpose check**: keep animation only when it supports spatial continuity, state clarity, feedback, explanation, or a less jarring transition.
- **Easing choice**:
  - Enter or reveal: prefer **ease-out** so feedback starts immediately.
  - On-screen morph or movement: prefer **ease-in-out** or a stronger custom curve.
  - Hover or color-only feedback: plain **ease** is often enough.
  - Constant motion: **linear**.
- **Duration bands**:
  - Press feedback: **100-160ms**
  - Tooltips / small popovers: **125-200ms**
  - Dropdowns / selects: **150-250ms**
  - Modals / drawers: **200-500ms**
- **Default rule**: typical UI animation should stay under **300ms** unless the interaction is deliberately slow (for example hold-to-confirm or explanatory motion).

## Practical heuristics
- Prefer **CSS-first** primitives (transform, opacity, filter, clip-path) before heavier tooling.
- Use motion to **reinforce hierarchy**: keep primary actions snappy; secondary actions softer.
- **Practice-based refinement**: iterate on timing/easing as a first‑class step, not a polish afterthought.
- Keep **reduced‑motion** paths equivalent in meaning (not just disabling movement).
- Prefer stronger custom curves over weak defaults when the interaction needs more punch, but document why the curve exists.
- Perceived speed matters: faster spinners, shorter selects, and instant follow-up tooltips can make the whole product feel quicker.

## Motion patterns to reference
- **Clip-path transitions** and **masking** for structured reveals.
- **RotateX / translateZ / rotateY** sparingly for depth cues and loader accents.
- **Gradient + mask** layering for subtle emphasis without layout shifts.
- **Momentum + damping** for drag‑to‑dismiss interactions (avoid abrupt stops).
- **“No animation”** as a valid outcome when clarity is already optimal.
- **@starting-style** for clean enter transitions when platform support allows.
- **Blur during crossfades** only as a subtle bridge when two overlapping states otherwise read as a broken swap.

## Component craft principles
- **Buttons must feel responsive**: add a subtle press scale (`0.97-0.99`) for immediate feedback.
- **Never animate from `scale(0)`**: start near `0.9-0.95` with opacity so the element feels like it already has mass.
- **Origin-aware overlays**: popovers and menus should animate from their trigger origin; centered modals are the exception.
- **Transitions over keyframes** for dynamic UI that users can trigger repeatedly or interrupt mid-flight.
- **Good defaults over option sprawl**: aim for components that feel polished without heavy setup.
- **Edge-case polish matters**: hidden-tab timers, hover gap fills, pointer capture, and other invisible fixes are part of the quality bar.

## Checklist for reviews
- Does the animation explain state change (loading → ready, collapsed → expanded)?
- Is the easing intentional and chosen for the type of movement, not left as a default?
- Are durations consistent with the system’s motion scale?
- Is there a reduced‑motion alternative that preserves meaning?
- Could this be implemented with CSS before adding a library?
- Is this interaction frequent enough that it should be reduced further or removed entirely?
