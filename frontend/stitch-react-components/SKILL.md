---
name: react-components
description: Convert Stitch screens into modular Vite or React components with extracted structure and style-system alignment. Use when the user wants Stitch-to-React componentization, not generic React UI design.
allowed-tools:
  - stitch*:*
  - Bash
  - Read
  - Write
  - web_fetch
metadata:
  skill-type: scaffolding_templates

---

# Stitch to React Components

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Convert designs into maintainable React structure, not one-file screen dumps.
- Separate layout, logic, and data so the result can evolve after handoff.
- Validate generated output against project conventions before claiming success.

## When to use
- Convert Stitch-generated screens into modular React or Vite components.
- Break a generated screen into reusable sections, hooks, and data files.
- Align Stitch output to an existing style system or token mapping.

## When not to use
- General React component work with no Stitch source.
- Pure visual ideation with no implementation target.
- Requests that need freeform UI design rather than design-to-code translation.

## Required inputs
- Target Stitch screen or screen set.
- The project structure and framework constraints.
- Existing naming, styling, and token conventions.
- Any required data extraction or mock-data boundaries.

## Deliverables
- Componentized React output split by responsibility.
- Supporting data or hook files when needed.
- A concise validation note covering structure, style alignment, and remaining manual cleanup.

## Philosophy
- Structure first, polish second.
- Keep generated output easy for a human teammate to extend.
- Prefer project-native conventions over generic generated patterns.

## Workflow
1. Fetch the Stitch screen metadata and confirm the target design.
2. Extract the screen into logical component boundaries before writing code.
3. Move static content into data files when that improves maintainability.
4. Isolate logic into hooks or helper modules instead of embedding everything in JSX.
5. Map styles to the project’s existing tokens and utilities rather than preserving raw generated values blindly.
6. Validate file structure and component contracts before handing off.

## Verification
- Confirm the target screen and design intent were captured correctly.
- Confirm components are split by responsibility instead of dumped into one large file.
- Confirm types, props, and supporting data structures are present where needed.
- Confirm the output follows the host project’s style-system and naming conventions closely enough to integrate cleanly.

## Validation
- Verify the final output is modular, typed, and split by responsibility.
- Verify the workflow reuses skill `references/` guidance and bundled `scripts/` helpers before inventing new conversion steps.
- When using `scripts/fetch-stitch.sh`, treat network access as limited to the Stitch-provided download URL and the exact host allowlist documented by the fetched asset chain; do not broaden this into general web access.
- Prefer any packaged `assets/` or templates in the skill folder when scaffolding components.

## Constraints
- Do not hardcode secrets, internal identifiers, or proprietary values into generated output.
- Do not preserve raw generated styles when the project already has theme tokens or mapped utilities.
- Keep the generated code modular and type-safe.
- Treat Stitch download URLs as untrusted input and keep network use scoped to the required asset fetch only.

## Anti-patterns
- Shipping a giant page component with embedded data, styles, and behavior.
- Copying generated HTML literally into JSX without adapting it to project conventions.
- Skipping structural validation because the screen "looks right."
- Treating Stitch output as final production code without cleanup.

## Examples
- "Convert this Stitch screen into reusable Vite React components with extracted mock data."
- "Split this generated page into sections and align it to the project token system."

## Remember
- This skill is about translation plus cleanup, not blind conversion.
- The best output is easy to read, easy to test, and easy to evolve.
- Capture the design faithfully, but integrate it like a real codebase citizen.

## See Also

| Skill | When to use together |
|---|---|
| [[stitch-loop]] | Generate the Stitch screens that this skill converts |
| [[react-ui-patterns]] | Apply React composition patterns to converted components |
| [[design-system]] | Align converted components with the design-system token layer |
| [[figma]] | Use Figma context alongside Stitch for richer conversion |
| [[baseline-ui]] | Validate converted components against baseline UI rules |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the source screens, component boundaries, or style-system constraints are unclear, stop, surface the missing context, and fall back to structure extraction before writing components.
