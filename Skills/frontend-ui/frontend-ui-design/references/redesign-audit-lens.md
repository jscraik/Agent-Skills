# Redesign Audit Lens

## Table of Contents
- [Purpose](#purpose)
- [Use this when](#use-this-when)
- [Audit sequence](#audit-sequence)
- [High-signal anti-generic checks](#high-signal-anti-generic-checks)
- [Realism checks for generated UI content](#realism-checks-for-generated-ui-content)
- [Adoption note](#adoption-note)

## Purpose
Provide a fast, repeatable redesign pass for existing interfaces that look generic, inconsistent, or low-trust.

This lens is for product-quality upgrades, not stylistic experimentation.

## Use this when
- A user asks to redesign an existing page or app surface.
- A UI "works" but lacks hierarchy, credibility, or clear interaction states.
- AI-generated defaults created repetitive layouts or placeholder-heavy content.

## Audit sequence
1. Confirm the primary job-to-be-done and the single dominant action per surface.
2. Check structural hierarchy first: primary action clarity, object prominence, and progressive disclosure.
3. Verify complete state coverage: loading, empty, partial, error, interrupted, and recovery.
4. Verify trust-critical cues are visible at decision time (actor, scope, consequence, undo/review path).
5. Apply craft polish only after the structural issues are fixed.

## High-signal anti-generic checks
- Replace repetitive "three equal feature cards" defaults when they harm hierarchy or scanning.
- Ensure nav/location context is explicit (current page or active item is visibly indicated).
- Avoid dead CTAs or fake interactions (for example `href="#"`) unless the user explicitly requests placeholders.
- Keep motion purposeful and performant (`transform`/`opacity` first, reduced-motion parity).
- Prefer deliberate palette + elevation logic over random accents, glow-heavy treatments, or inconsistent surface tones.

## Realism checks for generated UI content
- Avoid placeholder names and unrealistic perfect-round metrics in production-style examples.
- Use believable data variance and contextual copy instead of generic marketing filler.
- Keep empty and error states actionable with one clear next step.

## Adoption note
This lens folds reusable principles from external redesign heuristics into `frontend-ui-design` while remaining compatible with this repository's existing quality, accessibility, and token-system requirements.
