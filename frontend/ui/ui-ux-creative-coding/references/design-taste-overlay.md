# Design Taste Frontend Overlay (Opt-In)

## Table of Contents
- [Purpose](#purpose)
- [Activation contract](#activation-contract)
- [Default dials](#default-dials)
- [Overlay rule set](#overlay-rule-set)
- [Implementation and verification notes](#implementation-and-verification-notes)
- [Out-of-scope for this overlay](#out-of-scope-for-this-overlay)

## Purpose
This profile adds a high-agency, anti-generic UI execution style for requests that explicitly opt in.

Use this overlay to strengthen implementation discipline (state coverage, dependency checks, motion performance, and craft constraints) without changing default behavior of `ui-ux-creative-coding`.

## Activation contract
- Activate **only** when the user explicitly requests this overlay/profile.
- If not requested, do not apply these rules by default.
- Treat rules as:
  - **Hard requirements** only when the user asks for strict enforcement.
  - **Strong defaults** otherwise.

## Default dials
Baseline values (unless user overrides):
- `DESIGN_VARIANCE: 8`
- `MOTION_INTENSITY: 6`
- `VISUAL_DENSITY: 4`

## Overlay rule set

### 1) Dependency + version checks
- Before recommending/importing third-party packages, verify package presence/version in `package.json`.
- If missing, provide install command before code.
- Check Tailwind major version and avoid cross-version syntax assumptions.

### 2) Interaction completeness
- Include loading, empty, and error states for interactive flows.
- Include tactile action feedback (for example, active-state press response).

### 3) Performance and animation discipline
- Prefer transform/opacity over layout-affecting animation.
- Isolate interactive/heavy motion in small Client Components when needed.
- Avoid mixing multiple animation engines in the same component tree.

### 4) Layout and responsiveness
- Prefer grid for structured multi-column composition.
- Avoid mobile viewport instability patterns for full-height sections (`min-h-[100dvh]` over `h-screen`).
- Ensure asymmetric desktop patterns degrade cleanly to single-column mobile layouts.

### 5) Visual and content hygiene
- Anti-emoji policy: no emoji in shipped UI text/copy/alt unless explicitly requested.
- Avoid generic filler copy and placeholder data patterns when generating examples.
- Keep visual language consistent (palette, elevation logic, typography hierarchy).

## Implementation and verification notes
- Summarize active dials in output when overlay is enabled.
- Call out any intentional deviations from overlay defaults.
- Validate against:
  - accessibility baseline,
  - motion/reduced-motion parity,
  - performance guardrails,
  - dependency/version correctness.

## Out-of-scope for this overlay
- Brand-only identity exploration with no UI implementation artifacts.
- Full game-like 3D scene engineering unless explicitly requested.
