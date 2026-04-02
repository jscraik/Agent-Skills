---
name: design-system
description: "Analyze and implement repository-grounded design-system work (tokens, typography, iconography, spacing, styles, aliases, and theme variables) for this monorepo. Use when requests involve UI styling systems or token-layer changes; don’t use for backend/MCP-only tasks with no UI impact. Outputs: evidence-backed analysis or changes with canonical file references, layer impact, and validation commands. Success: work aligns to Brand→Alias→Mapped rules and passes design-system checks."
metadata:
  skill-type: product_verification
  lifecycle_state: active
  maturity: canonical
  owner: Design System Team
  last_reviewed: 2026-03-28
  review_cadence: quarterly
  metadata_source: frontmatter
---

# Design System

## Table of Contents
- [Working agreement](#working-agreement)
- [Scope and triggers](#scope-and-triggers)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Required context](#required-context)
- [Standards snapshot](#standards-snapshot)
- [Principles](#principles)
- [Normalization and Extraction Rules](#normalization-and-extraction-rules)
- [Variation and adaptation](#variation-and-adaptation)
- [Workflow](#workflow)
- [Deliverables](#deliverables)
- [Constraints](#constraints)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [Examples](#examples)
- [Reference map](#reference-map)
- [See Also](#see-also)
- [Remember](#remember)

## Working agreement
- Follow `/Users/jamiecraik/dev/design-system/AGENTS.md` and treat docs as maps.
- Prefer retrieval-led reasoning: inspect canonical files before proposing answers/changes.
- This skill is a design/brand map for the repo; when token or visual guidance is requested, validate both design contracts (`docs/design-system/CHARTER.md`, `docs/design-system/UPSTREAM_ALIGNMENT.md`) and canonical token sources before editing.
- Use `zsh -lc`, `rg`, `fd`, and `jq`; avoid `grep`/`find` for repo-wide scans.
- For multi-step or path-sensitive work, run `bash -lc 'source scripts/codex-preflight.sh && preflight_repo'` before editing.
- Artifact boundary:
  - Local CLI: write outputs to `./artifacts/`
  - Hosted shell: write outputs to `/mnt/data/`

## Scope and triggers
- Use this skill when the user asks about design-system behavior, token usage, typography, spacing, iconography, theme variables, or UI styling consistency in this repo.
- Use this skill when implementing or auditing changes touching `packages/tokens`, `packages/ui/src/styles`, `packages/ui/src/icons`, or design-system docs/stories.
- Do **not** use this skill for backend-only, infra-only, or MCP server tasks that do not affect UI/design-system layers.

## When to use
- Use when the task requires design-system governance, token-layer decisions, or cross-surface UI consistency enforcement.
- Use when the user needs evidence-backed recommendations tied to canonical design-system contracts and token layers.
- Avoid using this skill for backend-only or infrastructure-only requests; route those to backend/infra skills.

## Required inputs
- User goal (audit, implementation, migration, or Q&A).
- Target scope (package/component/docs area).
- Constraints (theme mode, compatibility posture, delivery format).

## Required context
Collect only the minimum set needed for the user request:

1. Brand and adoption contracts:
   - `brand/README.md`
   - `docs/design-system/CHARTER.md`
   - `docs/design-system/ADOPTION_CHECKLIST.md`
   - `docs/design-system/UPSTREAM_ALIGNMENT.md`

2. Canonical token source:
   - `packages/tokens/src/tokens/index.dtcg.json`
   - `packages/tokens/src/alias-map.ts`
   - `packages/tokens/schema/dtcg.schema.json`
3. Generated token outputs:
   - `packages/tokens/src/foundations.css`
   - `packages/tokens/src/aliases.css`
   - `packages/tokens/src/tokens.css`
   - `packages/tokens/src/enhanced.css`
   - `packages/tokens/tailwind.preset.ts`
4. Runtime mapped theme slots:
   - `packages/ui/src/styles/theme.css`
5. Icon system source:
   - `packages/ui/src/icons/index.ts`
   - `docs/design-system/ICON_CONSOLIDATION.md`
6. Governance + rules:
   - `docs/design-system/CONTRACT.md`
   - `docs/design-system/PROFESSIONAL_UI_CONTRACT.md`
   - `docs/design-system/AGENT_UI_ROUTING.md`
   - `docs/design-system/COMPONENT_LIFECYCLE.json`
   - `docs/design-system/ENFORCEMENT_EXEMPTIONS.json`
   - `docs/design-system/collections/*.md`
   - `docs/design-system/COVERAGE_MATRIX.md`
   - `docs/design-system/A11Y_CONTRACTS.md`
   - `packages/tokens/docs/FIGMA_EXPORT_GUIDE.md`
7. Surface examples:
   - `packages/ui/src/storybook/design-system/**`
   - `packages/ui/src/design-system/showcase/**`
8. Guidance policy + scope:
   - `.design-system-guidance.json`
   - `packages/design-system-guidance/**`

If the request is ambiguous, ask one focused clarification question.

## Standards snapshot
- Treat React 19 and Next.js 16 as the default app-level baselines when mapping design-system guidance into implementation-facing recommendations.
- Treat Tailwind CSS v4 token integration as the default utility contract for generated preset and UI consumption paths.
- Hold accessibility decisions to WCAG 2.2 AA outcomes, including focus visibility, contrast, and keyboard-operable components.
- Keep semantic token governance aligned to DTCG/W3C token structure and the repo's Brand -> Alias -> Mapped contract.
- Use `frontend/ui/references/skill-routing-matrix-2026.md` when implementation requests blur token governance and screen-level UI execution.

## Principles
- **Layer discipline:** change the correct tier (Brand → Alias → Mapped).
- **Semantic-first UI:** components consume mapped/semantic tokens, not raw literals.
- **Evidence over intuition:** always cite concrete file paths and token names.
- **Smallest safe diff:** prefer minimal, auditable changes and explicit validation steps.
- **Design-system consistency:** typography, spacing, and icon choices should align to existing scales/categories.
- Ask: "Why does this belong in Brand, Alias, or Mapped rather than a local override?"
- Ask: "What tradeoff are we accepting if we skip normalization and patch the symptom?"
- Ask: "Can we prove this change improves consistency without widening scope?"

## Normalization and Extraction Rules
- Normalize before inventing. If a surface drifts, first determine whether the root cause is:
  - one-off literals,
  - misuse of an existing token or component,
  - a missing semantic token,
  - a missing reusable component or documented pattern.
- Extract only when reuse is real:
  - repeated 3+ times already, or
  - highly likely to recur across nearby surfaces.
- Do not create tokens for every single value. New tokens must carry semantic meaning, not just preserve arbitrary numbers.
- Prefer replacing bespoke implementations with canonical design-system equivalents instead of preserving drift through wrappers.
- When extracting a reusable pattern, define the migration path as part of the recommendation:
  - what becomes shared,
  - what gets replaced,
  - what dead code can be removed after migration.

## Variation and adaptation
- Adapt output depth by request type: quick Q&A, deep audit report, implementation patch plan, or migration checklist.
- Use different recommendation strategies for small, medium, and large changes rather than repeating one template.
- Avoid generic outputs; tailor findings to the exact surface (`packages/ui`, `packages/tokens`, Storybook, widgets) and requested constraints.
- Keep package boundary explicit: start with one surface and one validation lane before expanding to cross-package refactors.

## Workflow
1. **Classify the request mode**
   - `audit`, `implementation`, `migration`, or `Q&A`.
2. **Build a focused system snapshot**
   - For path-sensitive work, run repo preflight first (`source scripts/codex-preflight.sh && preflight_repo` via `bash`).
   - Verify brand posture with `docs/design-system/CHARTER.md` and `ADOPTION_CHECKLIST.md` before touching tokens or theme.
   - Use `jq` for DTCG keys/values and `rg`/`fd` for CSS variable and component usage.
   - Record only relevant pillars: color, typography, spacing, radius/size/shadow, motion, icons, brand-mode behavior.
3. **Classify drift or extraction opportunity**
   - Decide whether the issue is normalization work, true system extraction, or a local exception.
   - If normalization is enough, prefer the smallest change that restores canonical behavior.
   - If extraction is justified, identify reuse count, future consumers, and migration cost before proposing a new shared primitive or token.
4. **Trace the layer path for each finding/change**
   - Brand token in DTCG → generated foundation vars → alias vars → mapped theme vars → component/story usage.
5. **Produce response or implement edits**
   - Include exact file references and affected token names.
   - For code changes, avoid introducing hex/rgb literals or ad-hoc px values in component code unless explicitly requested.
   - For brand decisions (new/renamed semantic tokens, dark/high contrast additions), cite `docs/design-system/CONTRACT.md` and `docs/design-system/collections/brand-collection-rules.md`.
6. **Validate**
   - Run the smallest relevant checks from [Validation](#validation).
   - If token files changed, verify schema version in `packages/tokens/SCHEMA_VERSION` and the generated artifacts stay coherent.
   - If guidance policy scope or protected surfaces changed, run both `design-system-guidance:ratchet` and `design-system-guidance:check:ci` and report warn/error counts.
7. **Write artifacts**
   - Save the summary/report under `./artifacts/design-system/` (or `/mnt/data/design-system/`).

## Deliverables
Depending on user request, produce one or more:
- `design-system-brief.md` — current state + evidence table by pillar.
- `design-system-delta.md` — what changed, why, and layer impact.
- `token-impact-matrix.md` — token path tracing (Brand/Alias/Mapped/Usage).
- `brand-audit-matrix.md` — brand-asset, contract, and accessibility constraints checked.
- `migration-checklist.md` — ordered migration steps + risk notes.
- `normalization-plan.md` — drift source, canonical replacement path, and cleanup notes.
- `validation-report.md` — commands run + pass/fail summary.
- For structured outputs (YAML/JSON), include a top-level `schema_version` field.

## Constraints
- Keep changes in the correct token tier; preserve Brand → Alias → Mapped layering.
- Preserve brand-mode parity (`light`, `dark`, `highContrast`) when editing design tokens.
- Prefer semantic tokens in UI code; avoid introducing raw literals unless explicitly required.
- Redact secrets and avoid destructive actions without explicit confirmation.

## Validation
Fail fast: stop at the first failed gate, fix, then rerun.

Run only what matches the touched area:
- `pnpm validate:tokens`
- `pnpm ds:matrix:check`
- `pnpm test:policy`
- `pnpm design-system-guidance:ratchet`
- `pnpm design-system-guidance:check:ci`
- `pnpm -C packages/ui build`

Targeted checks:
- Token structure quick checks:
  - `jq 'keys' packages/tokens/src/tokens/index.dtcg.json`
  - `jq '.type.web | keys' packages/tokens/src/tokens/index.dtcg.json`
  - `jq '.space | keys' packages/tokens/src/tokens/index.dtcg.json`
  - `jq '.color | keys' packages/tokens/src/tokens/index.dtcg.json`
  - `jq '.radius | keys' packages/tokens/src/tokens/index.dtcg.json`
- Find direct token usage or potential literals in UI code:
  - `rg -n "--foundation-|--ds-|--color-" packages/ui/src`
  - `rg -n "#[0-9a-fA-F]{3,8}|rgba?\(" packages/ui/src`
  - `rg -n "highContrast|--background|--foreground" packages/ui/src/styles/theme.css packages/tokens/src/tokens/index.dtcg.json`

## Anti-patterns
- ❌ Avoid editing only `theme.css` when the real change belongs in DTCG/alias layers.
- ❌ Do not add raw color or spacing literals to components when semantic tokens exist.
- ❌ Never create a new token or shared component before proving reuse or semantic need.
- ❌ Anti-pattern warning: treating deprecated icon sources as canonical (`@design-studio/astudio-icons` for new work) is incorrect.
- ❌ Avoid skipping brand-mode/accessibility contracts when updating color systems or motion defaults.
- ❌ Do not skip guidance policy checks when touching protected surfaces or `.design-system-guidance.json`.
- ❌ Returning advice without file-path evidence from this repository is the wrong review posture.

## Failure mode
- If the task is backend-only, infra-only, or MCP-only with no UI/token impact, decline this skill and route to a backend/infra skill path.
- If scope is too vague to locate touched surfaces, ask one focused clarification question before edits.
- If required design-system checks fail due unrelated repo-wide debt, report the exact failing gate and continue with bounded evidence for touched files only.

## Gotchas
- `check-see-also.py` expects a strict `## See Also` table plus `**Topic map:** [[...]]` format; plain bullets are not counted.
- Commit-time validation may run progressive-disclosure in strict mode; ensure required headings stay present even if warn-mode lint passes.

## Examples
- Triggering prompt: “Audit our typography and spacing tokens and show where they map into UI styles.”
- Triggering prompt: “Migrate these components to canonical icon imports and tokenized spacing.”
- Non-triggering prompt: “Debug MCP tool auth timeouts in the Cloudflare worker.”

## Reference map
- `brand/README.md` — current brand asset catalog and visual identity entry points.
- `./references/system-map.md` — canonical file map by design-system pillar.
- `./references/contract.yaml` — expected behavior and boundaries.
- `./references/evals.yaml` — trigger and safety eval cases.
- `./references/plan.md` — build plan and assumptions.
- `frontend/ui/references/design-system-integration-contract.md` — shared typography/spacing/iconography/token integration contract for sibling `frontend/ui` skills.
- `docs/design-system/PROFESSIONAL_UI_CONTRACT.md` — quality bar and semantics contract for UI outputs.
- `docs/design-system/AGENT_UI_ROUTING.md` — route-first map from request type to canonical surfaces.
- `./assets/design-system-brief-template.md` — report template for outputs.

## See Also
| Skill | When to use together |
|---|---|
| [[frontend-ui-design]] | Implement component and screen changes after design-system decisions are set |
| [[baseline-ui]] | Run a UI guardrail pass after token or theme updates |
| [[shadcn-ui]] | Apply design-system tokens while integrating shadcn components |

**Topic map:** [[frontend-ui]]

## Remember
This skill is here to unlock high-confidence design-system decisions. The agent is capable of extraordinary work in this domain—use judgment, stay evidence-backed, and push boundaries with creative but safe options when multiple valid approaches exist.
