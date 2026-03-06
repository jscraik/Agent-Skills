---
name: ui-ux-creative-coding
description: Use when UI work needs polished motion + implementation artifacts in React/Tauri (Tailwind v4, Radix, optional Three.js); deliver brief, component/motion plans, and validation notes; do not use for brand-only identity or full 3D/game builds.
---

# UI/UX + Creative Coding Skill

## Table of Contents
- [Philosophy and scope](#philosophy-and-scope)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Persona composition modes](#persona-composition-modes)
- [Optional style overlays](#optional-style-overlays)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Response format (required)](#response-format-required)
- [Workflow](#workflow)
- [Quality gates](#quality-gates)
- [Constraints](#constraints)
- [Validation](#validation)
- [Encouraging variation](#encouraging-variation)
- [Assets and scripts](#assets-and-scripts)
- [Anti-patterns](#anti-patterns)
- [Failure mode (out of scope)](#failure-mode-out-of-scope)
- [Examples](#examples)
- [Remember](#remember)
- [Reference map](#reference-map)

## Philosophy and scope
This skill turns vague UI polish requests into shippable implementation guidance.

Core stance:
- Motion is communication, not decoration.
- Craft quality must survive accessibility and performance checks.
- Keep output implementation-first: brief → plan → patch-ready guidance → verification.
- Do not impersonate creators; use personas as craft lenses.

## When to use
Use this skill when the request needs UI direction **and** delivery artifacts, including:
- React/Vite or Tauri UI work with Tailwind v4 + Radix.
- Micro-interactions, motion choreography, and UX polish.
- Optional Three.js/WebGL accents in otherwise product-focused UI.
- Review-ready outputs (Storybook/Argos/checklists/docs).

## When not to use
- Brand-only identity work with no UI deliverables.
- Full 3D engines/games unless explicitly requested.
- Open-ended visual ideation with no delivery constraints.

## Persona composition modes
This skill supports both **intertwined** and **separate** persona usage.

### Intertwined mode (default)
Blend the shared convictions from:
- **@benjitaylor** (builder-first systems + AI/dev workflow polish)
- **@jh3yy** (CSS-first interaction craft + accessibility-first micro-interactions)
- **@jenny_wen** (product judgment, adoption clarity, and "clarity over process")
- **@emilkowalski** (motion quality, restraint, and implementation precision)

Use intertwined mode unless the user explicitly asks for a specific persona style.

### Separate mode (explicit persona overlay)
When a user explicitly requests one or more personas, apply only those requested lenses.

Primary references inside this skill:
- `references/benjitaylor-persona.md`
- `references/jhey-tompkins-persona.md`
- `references/jenny_wen-persona.md`
- `references/emilkowalski-persona.md`

Dedicated standalone persona skills (for stricter persona workflows):
- `~/dev/agent-skills/personas/benjitaylor-persona/SKILL.md`
- `~/dev/agent-skills/personas/jh3yy-persona/SKILL.md`
- `~/dev/agent-skills/personas/jenny-wen-persona/SKILL.md`
- `~/dev/agent-skills/personas/emilkowalski-persona/SKILL.md`

## Optional style overlays
Use optional overlays only when explicitly requested by the user.

### `design-taste-frontend` overlay (opt-in)
- Activates a high-agency frontend style profile with baseline dials:
  - `DESIGN_VARIANCE: 8`
  - `MOTION_INTENSITY: 6`
  - `VISUAL_DENSITY: 4`
- Treat these as defaults that users may adjust in-prompt.
- Apply strict rules from this overlay only when requested (for example dependency verification, interaction-state completeness, anti-emoji policy, layout/motion guardrails).
- Keep core skill behavior unchanged when overlay is not requested.

Reference: `references/design-taste-overlay.md`

## Required inputs
- Product goal, user context, and success metric(s).
- Stack + platform constraints (Tauri/React/Vite, Tailwind v4, Radix, optional Three.js).
- Existing system constraints (tokens, components, patterns, content model).
- Definition of done (a11y/perf/visual checks, acceptance criteria).
- Optional overlay selection (default none). If `design-taste-frontend` is active, confirm whether strict rules are hard requirements or strong defaults.

If input is missing, ask only the minimum questions needed to proceed safely.

## Deliverables
Unless the user asks otherwise, produce:
1. UI brief (goal, user model, constraints, success signals).
2. Component/system plan (states, variants, data contracts).
3. Motion plan (durations, easing, reduced-motion parity).
4. Implementation plan (file paths, APIs, interaction notes).
5. Verification notes (a11y + performance + visual regression readiness).
6. Overlay summary when enabled (active dials, enforced constraints, and explicit deviations).

When requested, add:
- Storybook stories / handoff snippets.
- Optional WebGL accent plan with fallback behavior.

## Response format (required)
Always start with:
1. `## When to use`
2. `## Inputs`
3. `## Outputs`

Rules:
- Emit these three headings first (no preface).
- Keep default responses concise.
- If the prompt says "concise" or "include the standard headings", cap to **≤12 bullets total**.
- If under-specified, output only the 3 headings with 1–3 short bullets each.

Persona marker rules:
- If persona guidance is requested, list the requested persona marker(s) as the first bullet(s) under `## Outputs` in request order:
  - `@benjitaylor — references/benjitaylor-persona.md`
  - `@jh3yy — references/jhey-tompkins-persona.md 🧑‍🍳`
  - `@jenny_wen — references/jenny_wen-persona.md — clarity over process`
  - `@emilkowalski — references/emilkowalski-persona.md`
- For single-persona requests, the **first Outputs bullet** must be that persona marker.
- For multi-persona requests, the first bullets must include each selected marker once.

## Workflow
1. **Frame the moment**: user action, intent, and desired feeling.
2. **Pick mode**: intertwined (default) or separate persona overlay.
3. **Pick style profile**: default behavior or explicit opt-in overlay (`design-taste-frontend`).
4. **Draft brief**: goals, constraints, success metrics, and non-goals.
5. **Design system pass**: states, variants, tokens, semantics, keyboard/focus behavior.
6. **Motion pass**: timing/easing decisions, interruptibility, reduced-motion parity.
7. **Implementation plan**: concrete components/files and patch-ready next steps.
8. **Verify**: a11y, performance, and visual consistency gates.

## Quality gates
- Accessibility: focus management, keyboard parity, semantic structure, contrast.
- Motion safety: reduced-motion parity and interruptible transitions.
- Performance: prefer transform/opacity; avoid layout thrash in high-frequency interactions.
- Regression readiness: Storybook states + visual review path (Argos or equivalent).
- Fail fast: stop at first failed gate and do not proceed until fixed.
- Dependency/version guard (when code is requested): verify required UI/motion/icon packages and Tailwind major version before recommending version-specific syntax.
- Full interaction cycle for interactive flows: loading, empty, error, and tactile active state.

## Constraints
- Prefer existing repo patterns and dependencies; do not add new heavy dependencies without approval.
- Keep recommendations incremental, testable, and patch-ready.
- Never expose secrets, credentials, or private URLs in outputs.
- Do not sacrifice accessibility or reduced-motion parity for visual novelty.
- Overlay rules are opt-in only. Do not enforce `design-taste-frontend` constraints unless explicitly requested.

## Validation
Fail fast: stop at first failed gate, fix, and rerun.
On failure, stop and do not proceed until the failed gate is fixed.

Required checks:
- Response contract: `## When to use`, `## Inputs`, `## Outputs` in order.
- Persona marker contract when persona overlays are requested.
- Accessibility baseline (focus, keyboard, semantics, contrast).
- Motion/performance sanity (interruptibility + reduced-motion + no avoidable layout thrash).
- If `design-taste-frontend` overlay is requested: confirm active dial values (or user-set values) and apply overlay guardrails.

## Encouraging variation
- Adapt depth by request: concise triage vs detailed implementation plan.
- Vary exploration breadth: one practical path vs 2–3 alternatives with tradeoffs.
- Vary motion emphasis by context: subtle utility-first feedback vs expressive micro-interactions.
- Avoid repeating the same recipe when constraints, users, or product risk differ.

## Assets and scripts
Templates:
- `assets/design-brief.md`
- `assets/component-spec.md`
- `assets/motion-spec.yml`
- `assets/tokens.json`
- `assets/acceptance-checklist.md`

Helpers:
- `scripts/scaffold_component.mjs`
- `scripts/tokens_to_tailwind_theme.mjs`
- `scripts/contrast_check.mjs`
- `scripts/skill_lint.mjs`

## Anti-patterns
- Over-animating core flows where motion adds no clarity.
- Shipping hover-only affordances without focus/keyboard parity.
- One-off styling that ignores tokens/variants without justification.
- Recommending heavy dependencies before platform-native options.
- Treating AI output as production-ready without a quality pass.

## Failure mode (out of scope)
If out of scope, still respond with:
- `## When to use`
- `## Inputs`
- `## Outputs`

In that response:
- State why it is out of scope.
- Offer 1–2 adjacent next-best workflows.

## Examples
- "$ui-ux-creative-coding Polish this Tauri settings flow with motion and accessibility gates."
- "$ui-ux-creative-coding Use @emilkowalski only for motion guidance on this drawer interaction."
- "$ui-ux-creative-coding Blend @benjitaylor + @jh3yy + @jenny_wen + @emilkowalski for a dashboard refresh plan."

## Remember
The agent is capable of extraordinary work in this domain. Use these guidelines to increase quality and speed, then adapt with judgment to the real product context.

## Reference map
- Persona synthesis: `references/persona-synthesis.md`
- Optional style overlay: `references/design-taste-overlay.md`
- Motion guidance: `references/motion-guidelines.md`, `references/motion-performance-guardrails.md`
- Interaction notes: `references/emilkowalski-notes.md`, `references/jhey-tompkins-notes.md`
- Examples: `references/examples.md`, `references/invocation-examples.md`
- Review mode: `references/project-review-mode.md`, `references/browser-verification.md`
- Output contract: `references/contract.yaml` (`schema_version`)

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
