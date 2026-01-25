# UI Brief (template)

> Use this for any feature, screen, component set, or interaction pass.
> Goal: make intent and constraints explicit so implementation choices stay coherent.

## 1) Context
- **Product / area**:
- **Platform(s)**: (Tauri desktop / web / ChatGPT app / mobile web)
- **Audience**: (who is this for?)
- **Primary user job**: (what are they trying to get done?)
- **Success looks like**: (what changes for the user?)

## 2) The moment we’re designing
- **User story (plain language)**:
- **Happy path**: (steps)
- **Critical states**:
  - loading:
  - empty:
  - error:
  - offline (if applicable):
  - permissions/auth (if applicable):

## 3) Constraints & non-goals
- **Must keep**: (existing UI patterns, brand, OS conventions)
- **Performance budget**: (e.g., “no always-on animation”, “60fps on laptop”, “idle CPU near 0”)
- **Accessibility bar**: (keyboard-first, reduced motion, contrast)
- **Non-goals**: (what we will not solve right now)

## 4) Visual intent
Pick 3–5 adjectives (examples): calm, precise, playful, confident, warm, fast, tactile, minimal, expressive.

- **Adjectives**:
- **Reference UI(s)**: (screens, apps, URLs, screenshots)

## 5) Interaction intent
- **Feedback moments**: (hover/press/success/error)
- **Delight hook**: 1 small “smile” detail that does not block the task
- **Motion guidance**:
  - what should be animated?
  - what should not be animated?

## 6) Components & tokens
- **New components needed**:
- **Existing components to reuse**:
- **Tokens to add/change**: (colors, radii, spacing, typography, motion)

## 7) Verification
- **Acceptance criteria** (bullet list):
- **Storybook stories required**:
- **Argos snapshot coverage**:
- **A11y checks**: (keyboard flow, focus order, labels)

## 8) Open questions (max 3)
Keep questions tight. If unknown, make safe assumptions and document them.
