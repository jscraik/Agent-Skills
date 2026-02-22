---
name: design-system
description: "Analyze and implement repository-grounded design-system work (tokens, typography, iconography, spacing, styles, aliases, and theme variables) for this monorepo. Use when requests involve UI styling systems or token-layer changes; don’t use for backend/MCP-only tasks with no UI impact. Outputs: evidence-backed analysis or changes with canonical file references, layer impact, and validation commands. Success: work aligns to Brand→Alias→Mapped rules and passes design-system checks."
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
- Follow `/Users/jamiecraik/dev/design-system/AGENTS.md` and treat docs as maps.
- Prefer retrieval-led reasoning: inspect canonical files before proposing answers/changes.
- Use `zsh -lc`, `rg`, `fd`, and `jq`; avoid `grep`/`find` for repo-wide scans.
- Artifact boundary:
  - Local CLI: write outputs to `./artifacts/`
  - Hosted shell: write outputs to `/mnt/data/`

## Scope and triggers
- Use this skill when the user asks about design-system behavior, token usage, typography, spacing, iconography, theme variables, or UI styling consistency in this repo.
- Use this skill when implementing or auditing changes touching `packages/tokens`, `packages/ui/src/styles`, `packages/ui/src/icons`, or design-system docs/stories.
- Do **not** use this skill for backend-only, infra-only, or MCP server tasks that do not affect UI/design-system layers.

## Required inputs
- User goal (audit, implementation, migration, or Q&A).
- Target scope (package/component/docs area).
- Constraints (theme mode, compatibility posture, delivery format).

## Required context
Collect only the minimum set needed for the user request:

1. Canonical token source:
   - `packages/tokens/src/tokens/index.dtcg.json`
2. Generated token outputs:
   - `packages/tokens/src/foundations.css`
   - `packages/tokens/src/aliases.css`
   - `packages/tokens/tailwind.preset.ts`
3. Runtime mapped theme slots:
   - `packages/ui/src/styles/theme.css`
4. Icon system source:
   - `packages/ui/src/icons/index.ts`
   - `docs/design-system/ICON_CONSOLIDATION.md`
5. Governance + rules:
   - `docs/design-system/CONTRACT.md`
   - `docs/design-system/collections/*.md`
6. Surface examples:
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
   - Use `jq` for DTCG keys/values and `rg` for CSS variable usage.
   - Record only relevant pillars: color, typography, spacing, radius/size/shadow, icons.
3. **Trace the layer path for each finding/change**
   - Brand token in DTCG → generated foundation vars → alias vars → mapped theme vars → component/story usage.
4. **Produce response or implement edits**
   - Include exact file references and affected token names.
   - For code changes, avoid introducing hex/rgb literals or ad-hoc px values in component code unless explicitly requested.
5. **Validate**
   - Run the smallest relevant checks from [Validation](#validation).
6. **Write artifacts**
   - Save the summary/report under `./artifacts/design-system/` (or `/mnt/data/design-system/`).

## Deliverables
Depending on user request, produce one or more:
- `design-system-brief.md` — current state + evidence table by pillar.
- `design-system-delta.md` — what changed, why, and layer impact.
- `token-impact-matrix.md` — token path tracing (Brand/Alias/Mapped/Usage).
- `migration-checklist.md` — ordered migration steps + risk notes.
- `validation-report.md` — commands run + pass/fail summary.
- For structured outputs (YAML/JSON), include a top-level `schema_version` field.

## Constraints
- Keep changes in the correct token tier; preserve Brand → Alias → Mapped layering.
- Prefer semantic tokens in UI code; avoid introducing raw literals unless explicitly required.
- Redact secrets and avoid destructive actions without explicit confirmation.

## Validation
Fail fast: stop at the first failed gate, fix, then rerun.

Run only what matches the touched area:

```bash
pnpm validate:tokens
pnpm ds:matrix:check
pnpm test:policy
pnpm -C packages/ui build
```

Targeted checks:

```bash
# token structure quick checks
jq 'keys' packages/tokens/src/tokens/index.dtcg.json
jq '.type.web | keys' packages/tokens/src/tokens/index.dtcg.json
jq '.space | keys' packages/tokens/src/tokens/index.dtcg.json

# find direct token usage or potential literals in UI code
rg -n "--foundation-|--ds-|--color-" packages/ui/src
rg -n "#[0-9a-fA-F]{3,8}|rgba?\(" packages/ui/src
```

## Anti-patterns
- ❌ Editing only `theme.css` when the real change belongs in DTCG/alias layers.
- ❌ Adding raw color/spacing literals to components when semantic tokens exist.
- ❌ Treating deprecated icon sources as canonical (`@design-studio/astudio-icons` for new work).
- ❌ Returning advice without file-path evidence from this repository.

## Examples
- Triggering prompt: “Audit our typography and spacing tokens and show where they map into UI styles.”
- Triggering prompt: “Migrate these components to canonical icon imports and tokenized spacing.”
- Non-triggering prompt: “Debug MCP tool auth timeouts in the Cloudflare worker.”

## Reference map
- `./references/system-map.md` — canonical file map by design-system pillar.
- `./references/contract.yaml` — expected behavior and boundaries.
- `./references/evals.yaml` — trigger and safety eval cases.
- `./references/plan.md` — build plan and assumptions.
- `./assets/design-system-brief-template.md` — report template for outputs.

## Remember
This skill is here to unlock high-confidence design-system decisions. The agent is capable of extraordinary work in this domain—use judgment, stay evidence-backed, and push boundaries with creative but safe options when multiple valid approaches exist.
