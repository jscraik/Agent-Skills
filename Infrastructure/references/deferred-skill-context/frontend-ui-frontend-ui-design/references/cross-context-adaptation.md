# Cross-Context Adaptation

Last verified: 2026-03-29

Use this guide when a request is specifically about adapting an existing interface
across contexts (for example desktop to mobile, web to print, or web to email).
Treat adaptation as a product-context change, not just a viewport resize.

## Table of Contents
- [Core principle](#core-principle)
- [Adaptation intake](#adaptation-intake)
- [Source-to-target matrix](#source-to-target-matrix)
- [Context patterns](#context-patterns)
- [Implementation notes](#implementation-notes)
- [Verification checklist](#verification-checklist)
- [Common anti-patterns](#common-anti-patterns)

## Core principle
- Preserve core goals, terminology, and information architecture.
- Adapt layout, interaction, and information density to fit the target context.
- Never remove critical workflows just to "fit mobile." Reframe them.

## Adaptation intake
Capture this before proposing UI changes:
- Source context:
  - intended device and viewport,
  - input assumptions (pointer, keyboard, hover),
  - performance assumptions (network/CPU),
  - what currently works well.
- Target context:
  - device class and orientation,
  - input model (touch, keyboard, voice, remote),
  - operational constraints (connection, battery, print, email client limits),
  - expected user behavior (quick glance vs focused work).

## Source-to-target matrix
For each target context, record:
- Keep:
  - core jobs, labels, and mental model to preserve.
- Adapt:
  - layout shifts,
  - interaction affordances,
  - content density/priority,
  - navigation model.
- Redesign:
  - patterns that are invalid or misleading in the target context
    (for example hover-only details on touch).

Minimum matrix fields:
- `context`
- `layout_strategy`
- `interaction_strategy`
- `content_strategy`
- `navigation_strategy`
- `critical_risks`

## Context patterns
### Mobile (desktop -> mobile)
- Layout:
  - shift from wide multi-column to single-column or staged progression,
  - keep key actions within thumb-reachable regions.
- Interaction:
  - minimum touch targets of 44x44,
  - avoid hover dependencies,
  - use bottom sheets or inline expansion where dropdown complexity fails.
- Content:
  - prioritize primary tasks first,
  - use progressive disclosure for secondary details.

### Tablet
- Layout:
  - use hybrid two-column patterns where useful,
  - adapt by orientation (portrait vs landscape) with meaningful changes.
- Interaction:
  - support both touch and pointer behavior.
- Content:
  - show more parallel context than phone, but avoid desktop over-density.

### Desktop (mobile -> desktop)
- Layout:
  - reintroduce horizontal structure intentionally, not as auto-expansion,
  - use sensible max widths to avoid unreadable ultra-wide stretches.
- Interaction:
  - add keyboard support and hover details where they improve efficiency,
  - keep interactions consistent with mobile mental model.
- Content:
  - increase simultaneous visibility where it improves workflow speed.

### Print
- Remove interactive chrome and controls.
- Define logical page breaks and printable hierarchy.
- Include metadata (for example title/date/page number) when required.

### Email
- Prefer single-column composition.
- Expect limited client support; keep complexity low.
- Move complex interactions to linked web flows.

## Implementation notes
- Prefer content-driven breakpoints over arbitrary device-only breakpoints.
- Use container queries for component-level adaptation when available.
- Use `clamp()` for fluid typography/spacing where it improves continuity.
- Avoid relying on `display: none` to "solve" adaptation for critical features.
- Pair responsive layout changes with input-model changes (touch vs pointer).

## Verification checklist
- Validate target contexts with explicit viewport and/or device coverage.
- Test orientation shifts where relevant.
- Verify keyboard and screen-reader parity after adaptation.
- Verify reduced-motion behavior still works in every adapted path.
- Confirm no critical action becomes hidden or unreachable.

## Common anti-patterns
- Treating adaptation as proportional scaling only.
- Preserving desktop hover patterns unchanged on touch surfaces.
- Shipping one layout that technically fits but breaks task flow.
- Changing information architecture across contexts without clear product reason.
- Declaring adaptation complete without testing real-device behavior.
