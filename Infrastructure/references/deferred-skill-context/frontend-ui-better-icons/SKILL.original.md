---
name: better-icons
description: Search and extract SVG icons from Iconify collections through the better-icons CLI or MCP. Use when the user needs production-ready icons for UI work, not custom illustration design.
metadata:
  skill-type: scaffolding_templates
---

# Better Icons

Search, compare, and export Iconify icons without drifting into inconsistent icon choices.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Workflow](#workflow)
- [Validation](#validation)
- [References](#references)

## Standards snapshot
- Favor one icon family per surface unless the codebase already mixes families intentionally.
- Preserve accessibility: decorative icons stay hidden from assistive tech, semantic icons need a text label or adjacent copy.
- Prefer token-aligned sizing and color over ad hoc pixel and hex values.
- Use the CLI or MCP to fetch exact SVGs; do not retype vendor markup by hand.

## When to use
- You need to search Iconify collections for a suitable icon family or glyph.
- You need the exact SVG for one or more icons.
- You want to sync an icon into a project file with the `better-icons` tooling.
- You are reviewing icon choices and want a fast consistency pass before implementation.

## Required inputs
- Search query or explicit icon ID in `prefix:name` format.
- Optional collection prefix such as `lucide`, `mdi`, or `heroicons`.
- Optional output target if the SVG should be written or synced into a file.
- Optional framework target for sync workflows such as `react`, `vue`, or `svelte`.
- Any project icon constraints already in use: family, stroke weight, theme tokens, accessibility rules.

## Deliverables
- Search results with the strongest candidates first.
- Raw SVG markup or a synced project icon file.
- A short recommendation when multiple icon families could work.
- A concise note on accessibility or consistency risks when relevant.

## Philosophy
- Choose the smallest set of icons that preserves visual consistency.
- Prefer repo-grounded icon choices over novelty or personal taste.
- Treat accessibility and token alignment as part of icon selection, not cleanup.

## Failure mode
- If the user needs full UI design, iconography strategy, or visual branding direction, route to a UI or design-system skill instead.
- If the user only needs a favicon or OG asset, route to the dedicated graphics skill rather than stretching this one.
- If the requested icon would introduce a style mismatch, say so plainly and recommend a better-matched family.

## Constraints
- Redact secrets, sensitive file paths, and proprietary names by default in outputs and examples.
- Do not overwrite icon files or shared registries without making the target path explicit.
- Keep the scope to icon selection, retrieval, and sync guidance.

## Workflow
1. Confirm the use case.
2. Inspect the repo or request for an existing icon family before proposing new families.
3. Search narrowly first:
   - use a prefix if the project already has a preferred collection;
   - widen only if the first pass is weak.
4. Return 3 to 5 candidates at most unless the user asked for a larger set.
5. Fetch the final SVG or sync the chosen icon into the project.
6. Call out any integration risk:
   - mixed fill and stroke styles;
   - missing label or hit area for interactive controls;
   - hardcoded colors that bypass design tokens.

## Anti-patterns
- Mixing multiple icon families on the same surface without a deliberate reason.
- Returning an undifferentiated dump of dozens of icons when only a few candidates matter.
- Using semantic icons without considering labels or affordance.

## Validation
- Fail fast: stop at the first failed gate and correct it before broadening the search or sync step.
- `better-icons search home --limit 5` should return a usable candidate list.
- `better-icons get lucide:home` should emit valid SVG markup.
- If syncing, verify the target file changed in the expected location and the icon naming matches project conventions.
- Keep the final output small and deterministic; do not dump dozens of near-duplicate icons.

## Examples
- "Find a `lucide` icon for audit logs and return the top three candidates."
- "Fetch `mdi:database-lock` as raw SVG and keep the color as `currentColor`."
- "Sync this icon into our React icon file and preserve existing naming."

## References
- Contract: `Infrastructure/references/contract.yaml`
- Evals: `Infrastructure/references/evals.yaml`
- Task profile: `Infrastructure/references/task-profile.json`
- Asset preview: `assets/better-icons.png`

## See Also

| Skill | When to use together |
|---|---|
| [[frontend-ui-design]] | Source icons for UI components being designed |
| [[design-system]] | Integrate icon tokens into the design system |
| [[shadcn-ui]] | Add Iconify icons to shadcn/ui component projects |
| [[favicon-generator]] | Use alongside favicon generation for icon-family consistency |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
