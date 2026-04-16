# Motion Guidelines

## Table of Contents
- [Opportunity audit](#opportunity-audit)
- [Animation strategy layers](#animation-strategy-layers)
- [Timing defaults](#timing-defaults)
- [Easing defaults](#easing-defaults)
- [Implementation constraints](#implementation-constraints)
- [Reduced-motion parity](#reduced-motion-parity)
- [Quality checks](#quality-checks)

## Opportunity audit
Before proposing animation, classify where motion solves a real problem:
- Missing feedback: clicks, toggles, and submissions without acknowledgment.
- Abrupt transitions: show/hide or state changes that feel jarring.
- Unclear relationships: hierarchy or spatial relation is hard to read.
- Guidance gaps: no directional cue for important next actions.
- Optional delight: a small branded flourish after function is already clear.

## Animation strategy layers
Plan motion as layers, not isolated effects:
- Hero moment: one signature animation for the surface.
- Feedback layer: immediate acknowledgment for interaction events.
- Transition layer: smooth state changes and layout shifts.
- Delight layer: restrained surprise moments that do not block workflows.

Use one strong hero moment before adding multiple secondary effects.

## Timing defaults
| Motion type | Recommended duration |
| --- | --- |
| Micro-interactions | 100-150ms |
| Standard UI transitions | 150-250ms |
| Modals and drawers | 200-300ms |
| Layout shifts and entrance choreography | 300-500ms |

Rules:
- Keep interaction feedback under 200ms.
- Most UI animation should stay under 300ms.
- Exit animations should be about 20-25% faster than entrances.
- Longer travel distance can justify slightly longer duration.

## Easing defaults
Recommended curves:
- `cubic-bezier(0.25, 1, 0.5, 1)` for refined easing out.
- `cubic-bezier(0.22, 1, 0.36, 1)` for a snappier finish.
- `cubic-bezier(0.16, 1, 0.3, 1)` for decisive transitions.

Avoid decorative bounce/elastic curves in production UI unless explicitly requested.

## Implementation constraints
- Prefer compositor properties: `transform` and `opacity`.
- Avoid layout property animation (`width`, `height`, `top`, `left`).
- Keep `will-change` temporary and scoped.
- Avoid heavy motion on large surfaces or low-end paths.
- Favor CSS transitions/keyframes for simple state change; use JS animation only when choreography needs runtime control.

## Reduced-motion parity
Always provide a reduced-motion path with equivalent usability.

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

This should simplify motion without removing critical feedback.

## Quality checks
- Motion remains smooth on target hardware (aim for 60fps).
- Every animation can be explained as feedback, transition, guidance, or delight.
- Users can interact without waiting on long animations.
- Reduced-motion mode preserves clarity and task success.
