# Professional UI Rubric 2026

## Table of Contents
- [Purpose](#purpose)
- [Scoring model](#scoring-model)
- [Professional quality criteria](#professional-quality-criteria)
- [Shared output contract](#shared-output-contract)
- [Validation lane references](#validation-lane-references)

## Purpose
Provide one shared quality bar for app and web UI recommendations across `frontend/ui/*` skills so outputs stay consistent, professional, and implementation-ready.

## Scoring model
- Score each criterion from `0` to `4`.
- Treat `3` as release-ready quality and `4` as exemplary quality.
- Treat any `0` in accessibility or state coverage as a release blocker.

## Professional quality criteria
1. Spacing rhythm and density
- Thresholds:
  - spacing uses tokenized scales or documented exceptions;
  - dense surfaces preserve readable grouping and section separation;
  - no arbitrary spacing values without rationale.

2. Visual hierarchy and CTA clarity
- Thresholds:
  - one dominant focal anchor per primary viewport or section;
  - primary CTA is visually and semantically clear;
  - supporting actions are de-emphasized but still discoverable.

3. Full state coverage
- Thresholds:
  - explicit behavior for `loading`, `empty`, `error`, and `success`;
  - edge states include user guidance for next action;
  - state transitions do not hide critical context.

4. Motion restraint and reduced-motion parity
- Thresholds:
  - motion supports comprehension, feedback, or hierarchy;
  - reduced-motion path remains intentionally designed;
  - no heavy or distracting motion that harms task completion.

5. Copy tone consistency for product UI
- Thresholds:
  - action labels are object-action clear;
  - errors explain what happened and what to do next;
  - tone matches product context and user decision stakes.

## Shared output contract
- Include concise design rationale:
  - why this approach is correct for the user task and context.
- Include before/after quality checklist:
  - what quality risks existed before;
  - what changed after recommendations or edits.
- Include measurable acceptance criteria:
  - explicit threshold-style checks tied to accessibility, hierarchy, spacing, states, and motion behavior.

## Validation lane references
- Accessibility lane:
  - axe checks and WCAG 2.2 AA review.
- Responsive lane:
  - breakpoint verification for mobile, tablet, and desktop where applicable.
- Visual regression lane:
  - Storybook, Playwright, or Argos diff review for changed surfaces.
- Design-system lane:
  - token and semantic-style compliance against canonical design-system rules.
