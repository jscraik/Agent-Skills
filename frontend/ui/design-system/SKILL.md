---
name: design-system
description: Analyze or implement repository-grounded design-system layers such as tokens, typography, iconography, spacing, styles, aliases, and theme variables. Use when the user wants monorepo design-system work, not ordinary component styling or backend-only changes.
metadata:
  skill-type: library_api_reference

---

# Design System

## Table of Contents
- [Working agreement](#working-agreement)
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Required context](#required-context)
- [Principles](#principles)
- [Variation and adaptation](#variation-and-adaptation)
- [Workflow](#workflow)
- [Deliverables](#deliverables)
- [Constraints](#constraints)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Reference map](#reference-map)
- [Remember](#remember)

## Working agreement
- Follow `AGENTS.md` (repo root) and treat docs as maps.
- Prefer retrieval-led reasoning: inspect canonical files before proposing answers/changes.
- Treat this as the brand/design map for this repo: validate `docs/design-system/CHARTER.md` and `docs/design-system/UPSTREAM_ALIGNMENT.md` before token/theme edits.
- Use `zsh -lc`, `rg`, `fd`, and `jq`; avoid `grep`/`find` for repo-wide scans.
- If any of `rg`, `fd`, or `jq` are unavailable in the current environment, use a compatible fallback and note the substitute command used.
- Artifact boundary:
  - Local CLI: write outputs to `./artifacts/`
  - Hosted shell: write outputs to `/mnt/data/`

Current baseline markers:
- React 19 for component-layer guidance and stateful UI patterns.
- Next.js 16 when the target surface is a Next.js app or widget shell.
- Tailwind CSS v4 for utility and token usage guidance.
- WCAG 2.2 AA for accessibility acceptance and QA.

## When to use
- Use this skill when the user asks about design-system behavior, token usage, typography, spacing, iconography, theme variables, or UI styling consistency in this repo.
- Use this skill when implementing or auditing changes touching `packages/tokens`, `packages/ui/src/styles`, `packages/ui/src/icons`, or design-system docs/stories.
- Do **not** use this skill for backend-only, infra-only, or MCP server tasks that do not affect UI/design-system layers.

## Required inputs
- User goal (audit, implementation, migration, or Q&A).
- Target scope (package/component/docs area).
- Constraints (theme mode, compatibility posture, delivery format).

## Required context
Collect only the minimum set needed for the user request:

1. Brand and governance:
   - `brand/README.md`
   - `docs/design-system/CHARTER.md`
   - `docs/design-system/ADOPTION_CHECKLIST.md`
   - `docs/design-system/UPSTREAM_ALIGNMENT.md`

2. Canonical token source:
   - `packages/tokens/src/tokens/index.dtcg.json`
   - `packages/tokens/src/alias-map.ts`
   - `packages/tokens/schema/dtcg.schema.json`
   - `packages/tokens/src/validation/token-validator.ts`
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
6. Rules and coverage artifacts:
   - `docs/design-system/CONTRACT.md`
   - `docs/design-system/collections/*.md`
   - `docs/design-system/COVERAGE_MATRIX.md`
   - `docs/design-system/A11Y_CONTRACTS.md`
   - `packages/tokens/docs/FIGMA_EXPORT_GUIDE.md`
7. Surface examples:
   - `packages/ui/src/storybook/design-system/**`
   - `packages/ui/src/design-system/showcase/**`

If the request is ambiguous, ask one focused clarification question.

## Principles
- **Layer discipline:** change the correct tier (Brand → Alias → Mapped).
- **Semantic-first UI:** components consume mapped/semantic tokens, not raw literals.
- **Evidence over intuition:** always cite concrete file paths and token names.
- **Smallest safe diff:** prefer minimal, auditable changes and explicit validation steps.
- **Design-system consistency:** typography, spacing, and icon choices should align to existing scales/categories.

## Variation and adaptation
- Adapt output depth by request type: quick Q&A, deep audit report, implementation patch plan, or migration checklist.
- Use different recommendation strategies for small, medium, and large changes rather than repeating one template.
- Avoid generic outputs; tailor findings to the exact surface (`packages/ui`, `packages/tokens`, Storybook, widgets) and requested constraints.

## Workflow
1. **Classify the request mode**
   - `audit`, `implementation`, `migration`, or `Q&A`.
2. **Build a focused system snapshot**
   - Verify brand posture with `docs/design-system/CHARTER.md`, `ADOPTION_CHECKLIST.md`, and `UPSTREAM_ALIGNMENT.md` before token/theme edits.
   - Use `jq` for DTCG keys/values and `rg`/`fd` for usage tracing (with environment fallbacks when needed).
   - Record relevant pillars: color, typography, spacing, radius/size/shadow, motion, icons, brand-mode behavior.
3. **Trace the layer path for each finding/change**
   - Brand token in DTCG → generated foundation vars → alias vars → mapped theme vars → component/story usage.
4. **Produce response or implement edits**
   - Include exact file references and affected token names.
   - For code changes, avoid introducing hard-coded color values or ad-hoc pixel values in component code unless explicitly requested.
   - For brand decisions (new/renamed semantic tokens, dark/high-contrast additions), cite `docs/design-system/CONTRACT.md` and `docs/design-system/collections/brand-collection-rules.md`.
5. **Validate**
   - Run the smallest relevant checks from [Validation](#validation).
   - If token source files changed (`packages/tokens/src/tokens/index.dtcg.json`, `packages/tokens/src/alias-map.ts`), verify `packages/tokens/SCHEMA_VERSION` and regenerate artifacts to confirm coherence.
     - Primary: `pnpm -C packages/tokens generate`
     - Repo-level alias: `pnpm generate:tokens`
   - If `UPSTREAM_ALIGNMENT.md` changed, include upstream alignment evidence (verification stamp or explicit reason alignment validation is intentionally deferred).
6. **Write artifacts**
   - For `audit`, `implementation`, and `migration` modes: save artifacts under `./artifacts/design-system/` (or `/mnt/data/design-system/`).
   - For `Q&A`: return concise evidence-backed findings; artifact output is optional if requested.

## Deliverables
Depending on user request, produce one or more:
- `design-system-brief.md` — current state + evidence table by pillar.
- `design-system-delta.md` — what changed, why, and layer impact.
- `token-impact-matrix.md` — token path tracing (Brand/Alias/Mapped/Usage).
- `brand-audit-matrix.md` — brand-asset, contract, and accessibility constraints checked.
- `migration-checklist.md` — ordered migration steps + risk notes.
- `validation-report.md` — commands run + pass/fail summary.
- For structured outputs (YAML/JSON), include a top-level `schema_version` field.

## Constraints
- Keep changes in the correct token tier; preserve Brand → Alias → Mapped layering.
- Preserve brand-mode parity (`light`, `dark`, and `highContrast` when that mode is part of the canonical contract for the touched layer).
- Prefer semantic tokens in UI code; avoid introducing raw literals unless explicitly required.
- Redact secrets and avoid destructive actions without explicit confirmation.

## Validation
Fail fast: stop at the first failed gate, fix, then rerun.

Run only what matches the touched area:

```bash
# Baseline design-system checks
pnpm validate:tokens
pnpm ds:matrix:check
# Add only if the request touches runtime/systemwide behavior
pnpm test:policy
# Add when UI component behavior changed
pnpm -C packages/ui build
```

Targeted checks:
- token structure quick checks with `jq` on `packages/tokens/src/tokens/index.dtcg.json`
- mode-parity checks with `rg -n "light|dark|highContrast"` across token and theme files
- regeneration drift check with `pnpm -C packages/tokens generate && git diff -- ...`
- token usage and literal hygiene checks with `rg` in `packages/ui/src`

## Anti-patterns
- ❌ Editing only `theme.css` when the real change belongs in DTCG/alias layers.
- ❌ Adding raw color/spacing literals to components when semantic tokens exist.
- ❌ Treating deprecated icon sources as canonical (`@design-studio/astudio-icons` for new work).
- ❌ Skipping brand-mode/accessibility contracts when updating color systems or motion defaults.
- ❌ Returning advice without file-path evidence from this repository.

## Examples
- Triggering prompt: “Audit our typography and spacing tokens and show where they map into UI styles.”
- Triggering prompt: “Migrate these components to canonical icon imports and tokenized spacing.”
- Non-triggering prompt: “Debug MCP tool auth timeouts in the Cloudflare worker.”

## Reference map
- `./references/system-map.md` — canonical file map by design-system pillar.
- `brand/README.md` — current brand asset catalog and visual identity entry points.
- `./references/contract.yaml` — expected behavior and boundaries.
- `./references/evals.yaml` — trigger and safety eval cases.
- `./references/plan.md` — build plan and assumptions.
- `./assets/design-system-brief-template.md` — report template for outputs.

## Remember
This skill is here to unlock high-confidence design-system decisions. The agent is capable of extraordinary work in this domain—use judgment, stay evidence-backed, and push boundaries with creative but safe options when multiple valid approaches exist.

## See Also

| Skill | When to use together |
|---|---|
| [[baseline-ui]] | Validate UI components against design-system tokens |
| [[frontend-ui-design]] | Implement components using design-system token layer |
| [[figma]] | Extract Figma tokens as source of truth for the design system |
| [[shadcn-ui]] | Adapt shadcn/ui to use design-system token aliases |
| [[fixing-accessibility]] | Combine token changes with accessibility fixes |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Quality Uplift
- Philosophy and approach: apply a clear framework, explain why, consider tradeoff decisions, and use a practical mental model for execution.
- Guiding question: Why is this the right context-specific path?
- Guiding question: What tradeoff is being made and how is risk reduced?
- Guiding question: How do we verify behavior end-to-end before completion?
- Anti-pattern warning: avoid generic or repetitive output; DO NOT hide failures; NEVER skip validation; avoid common pitfall and mistake patterns.
- Anti-pattern warning: treat incorrect or wrong assumptions as blockers, and call out anti-pattern risks explicitly.
- Variation: vary recommendations by context-specific constraints; adapt, customize, and use different approaches when constraints differ.
- Variation: prefer diverse, unique alternatives and avoid repetition or cookie-cutter template convergence.
- Empowerment: enable users to explore options confidently, be capable and creative, unlock safe choices, and empower execution.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If token layers, theme ownership, or canonical source files are unclear, stop, report the ambiguity, and fall back to a design-system discovery pass before editing tokens or aliases.
