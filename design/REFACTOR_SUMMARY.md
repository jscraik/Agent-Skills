# Spec Pipeline Refactor Summary

## What Changed

Refactored the spec skills to use a **3-stage pipeline** from the transcript curriculum:
1. Foundation Spec (What + Why)
2. UX Spec (How it feels)
3. Build Plan (How we execute)

## Files Created

### Shared References (`design/references/`)

1. **foundation-spec-template.md** (33 lines)
   - One-sentence summary
   - Core problem with anti-goal
   - Target user + context
   - Success metrics + guardrails
   - MVP scope (must-have vs out-of-scope)
   - User stories (top 5-10)
   - Primary journey (happy path)

2. **ux-spec-template.md** (32 lines)
   - Mental model alignment
   - Information architecture (entities, relationships)
   - Affordances & actions (clickable/editable/destructive)
   - System feedback states (empty/loading/error/partial/auth)
   - UX acceptance criteria (Given/When/Then)

3. **build-plan-template.md** (28 lines)
   - Epics (sequenced)
   - Stories per epic with acceptance criteria
   - Data + contracts (lightweight)
   - Test strategy (unit/integration/E2E/failure-mode)
   - Release plan (feature flags, rollout, monitoring)

4. **spec-linter-checklist.md** (25 lines)
   - Problem & success checks
   - UX ambiguity removal checks
   - Execution checks
   - Communication clarity checks
   - Evidence discipline checks

5. **prompts.md** (46 lines)
   - Socratic Spec Reviewer (Foundation)
   - UX Ambiguity Killer (PRD → UX)
   - Build Plan Decomposer (UX → epics/stories)

## Files Modified

### product-spec/SKILL.md (467 lines)
- Added "The Spec Pipeline" section explaining 3-stage approach
- Added "Shared References" section pointing to 5 new templates
- Integrated 3-stage pipeline into Core Workflow:
  - Step 2: Draft Foundation Spec (Stage 1)
  - Step 3: Draft UX Spec (Stage 2)
  - Step 4: Draft Build Plan (Stage 3)
  - Step 5: Run Spec Linter Checklist
- Added output artifacts with new naming convention:
  - `.spec/foundation-YYYY-MM-DD-<slug>.md`
  - `.spec/ux-YYYY-MM-DD-<slug>.md`
  - `.spec/build-plan-YYYY-MM-DD-<slug>.md`
- Preserved all existing functionality (Oracle, adversarial debate, RALPH, interview mode, review mode, Lite PRD)

### All 12 prd-*/SKILL.md files
Added "Pipeline Context" section to each:

1. **prd-clarifier** (189 lines)
   - Supports all stages via structured Q&A
   - Shared: spec-linter-checklist, prompts

2. **prd-to-ux** (213 lines)
   - Implements Stage 2 (UX Spec)
   - Shared: ux-spec-template, spec-linter-checklist, prompts

3. **prd-to-arch** (114 lines) / **prd-to-arch-lite** (107 lines)
   - Part of Stage 3 (Build Plan)
   - Shared: build-plan-template, spec-linter-checklist

4. **prd-to-api** (109 lines) / **prd-to-api-lite** (105 lines)
   - Part of Stage 3 (Build Plan)
   - Shared: build-plan-template, spec-linter-checklist

5. **prd-to-testplan** (105 lines)
   - Part of Stage 3 (Build Plan)
   - Shared: build-plan-template, spec-linter-checklist

6. **prd-to-risk** (103 lines)
   - Supports all stages
   - Shared: spec-linter-checklist

7. **prd-to-roadmap** (103 lines)
   - Supports all stages
   - Shared: spec-linter-checklist

8. **prd-to-qa-cases** (103 lines)
   - Part of Stage 3 (Build Plan)
   - Shared: build-plan-template, spec-linter-checklist

9. **prd-to-accessibility** (106 lines)
   - Supports Stage 2 (UX Spec)
   - Shared: ux-spec-template, spec-linter-checklist

10. **prd-to-security-review** (105 lines)
    - Supports all stages
    - Shared: spec-linter-checklist

## Verification Results

✅ All 5 shared reference files exist and are non-empty
✅ All 13 skills have Pipeline Context section
✅ All 12 prd-* skills reference shared templates
✅ All 3 pipeline stages documented in product-spec
✅ Legacy references preserved in product-spec/references/
✅ All existing functionality preserved

## Evidence

- File counts and line counts verified via `wc -l` and `find`
- Pipeline context sections verified via `grep`
- Shared reference usage verified via grep across all skills
- Pipeline workflow stages verified via grep in product-spec

## Transcript Sources

The pipeline is synthesized from these transcripts:
- `youtube-vibe-planning-pyramid.md` — Clarity before execution
- `youtube-stop-skipping-planning-ai-uis.md` — Explicit UX mental models and states
- `podcast-ai-prototyping-tools-complete-guide-colin-lennys-podcast.md` — Small-chunk execution with plans
- `youtube-5-books-that-will-change-how-you-make-money.md` — Positioning constraints for stakeholder communication

## Evidence Gaps

None identified during refactoring.
