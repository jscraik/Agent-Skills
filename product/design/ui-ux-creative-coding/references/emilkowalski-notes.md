# Emil Kowalski — Motion Craft Notes (Jan 2026)

Use these notes when shaping motion and micro‑interactions. Keep them practical and code‑anchored.

## Core principles
- **Motion is UX communication**: every movement should explain state, intent, or change.
- **Timing + easing are decisions**: select values deliberately; avoid defaults without rationale.
- **Less but better**: if motion doesn’t improve clarity or feedback, remove it.
- **Consistency across components**: choreography, durations, and easing should harmonize.

## Practical heuristics
- Prefer **CSS-first** primitives (transform, opacity, filter, clip-path) before heavier tooling.
- Use motion to **reinforce hierarchy**: keep primary actions snappy; secondary actions softer.
- **Practice-based refinement**: iterate on timing/easing as a first‑class step, not a polish afterthought.
- Keep **reduced‑motion** paths equivalent in meaning (not just disabling movement).

## Motion patterns to reference
- **Clip-path transitions** and **masking** for structured reveals.
- **RotateX / 3D hints** sparingly for depth cues.
- **Gradient + mask** layering for subtle emphasis without layout shifts.
- **“No animation”** as a valid outcome when clarity is already optimal.

## Checklist for reviews
- Does the animation explain state change (loading → ready, collapsed → expanded)?
- Is the easing intentional (e.g., ease‑out for entrances, ease‑in for exits)?
- Are durations consistent with the system’s motion scale?
- Is there a reduced‑motion alternative that preserves meaning?
- Could this be implemented with CSS before adding a library?
