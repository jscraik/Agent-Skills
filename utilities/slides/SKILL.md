---
name: slides
description: "Create, edit, validate, or debug PowerPoint-compatible slide decks with PptxGenJS and visual overflow checks. Use when the user wants `.pptx` work, not generic web UI design or prose editing."
metadata:
  skill-type: team_automation
---

# Slides

Create, edit, recreate, and validate presentation decks with editable PowerPoint output, reproducible authoring, and evidence-backed visual review.

## Standards snapshot (March 2026)
- Prefer editable `.pptx` output plus rebuildable source over opaque visual exports.
- Preserve slide geometry, typography intent, and native PowerPoint editability whenever the task allows it.
- Treat rendering review, overflow checks, and font verification as release gates, not optional polish.
- Keep the workflow reproducible so another agent can regenerate the deck without hidden context.

## When to use
- Creating a new `.pptx` deck from scratch.
- Updating or extending an existing presentation while preserving its theme and layout.
- Recreating a deck from screenshots, PDFs, or visual references into editable slides.
- Validating an existing deck for overflow, font drift, or render-quality regressions.

## When not to use
- The user wants a generic HTML explainer, dashboard, or browser-only visual artifact.
- The task is prose editing without any slide deliverable.
- A static image is enough and no editable slide output is required.

## Required inputs
- The source material or deck path.
- Whether the deliverable is creation, editing, recreation, or validation-only.
- Required output path and whether rebuildable source must be included.
- Constraints on aspect ratio, fonts, branding, dependencies, or visual-review tooling.

## Deliverables
- An updated or newly created `.pptx` deck aligned to the request.
- Rebuildable JavaScript source when the deck is authored or materially edited with PptxGenJS.
- A short evidence summary covering render review, overflow checks, font drift, and blockers.
- If requested, a structured status report with a `schema_version` field.

## Failure mode
- If required tools are missing, report the exact dependency blocker and stop instead of improvising.
- If rendering support is unavailable, preserve the editable source and mark visual validation as blocked rather than claiming the deck was reviewed.
- If preserving an existing deck matters, do not silently change aspect ratio, typography, or density to make the edit easier.

## Workflow
1. Confirm whether the task is creation, editing, recreation, or validation-only.
2. Determine slide size up front and preserve the original ratio when one already exists.
3. Use JavaScript plus PptxGenJS for authoring or substantial edits so the result stays rebuildable.
4. Reuse the bundled helper library in `assets/pptxgenjs_helpers/` instead of reimplementing layout and sizing logic.
5. Keep text as text and simple charts as native PowerPoint elements when practical.
6. Render the deck for review when tools are available.
7. Run overflow, bounds, and font checks before delivery and fix the first real issue before continuing.

## Tooling and references
- Author with PptxGenJS.
- Reuse helpers from `assets/pptxgenjs_helpers/`.
- Use `scripts/render_slides.py` for rasterized review.
- Use `scripts/slides_test.py` for overflow and bounds detection.
- Use `scripts/create_montage.py` for contact-sheet review on large decks.
- Use `scripts/detect_font.py` to detect missing or substituted fonts.
- Use `scripts/ensure_raster_image.py` when odd assets need debug-ready PNG output.
- Reference files:
  - `references/pptxgenjs-helpers.md`
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `agents/openai.yaml`

## Temp and output conventions
- Do deck work in a task-local workspace instead of editing final deliverables in place.
- Keep helper assets next to the authoring script so the deck can be rebuilt without hidden dependencies.
- Write review images and montages to a temporary render directory and clean them up when they are no longer needed.
- Copy only final requested artifacts to the destination path after validation passes.

## Dependencies
Prefer explicit local tools over hidden runtime assumptions.

Authoring:

```bash
npm install pptxgenjs
```

Rendering and review:

```bash
python3 --version
libreoffice --version
```

If a dependency is missing, report the exact install gap before continuing.

## Validation
- Verify the output `.pptx` exists and opens as a presentation file.
- Verify required companion source files are present when rebuildable output was requested.
- Verify rendered slide images when rendering tools are available.
- Verify overflow or bounds warnings are resolved or explicitly documented as intentional.
- Fail fast at the first failed validation gate and report the exact blocker.

## Anti-patterns
- Using `python-pptx` for deck generation when editable authoring with bundled helpers is the standard path.
- Delivering a deck without checking for clipped text or out-of-bounds elements.
- Claiming rendering or font validation without tool output.
- Rasterizing content that should remain editable without a clear reason.
- Quietly changing aspect ratio, typography, or layout density during a routine update.

## Variation
- Use a creation-first workflow for greenfield decks.
- Use a render-compare workflow for screenshot or PDF recreations.
- Use a minimal-diff workflow for small edits to an existing deck.
- Increase review rigor for board decks, sales collateral, or screenshot-matched recreations.

## Examples
- Build a clean 10-slide investor update deck with editable charts and speaker-safe spacing.
- Recreate a screenshot-based keynote into a rebuildable `.pptx` and authoring `.js`.
- Update an existing deck’s copy and charts while preserving theme and layout.
- Diagnose which slides overflow the canvas and fix the offending elements before delivery.

## See Also

| Skill | When to use together |
|---|---|
| [[beautiful-mermaid]] | Embed high-quality Mermaid diagrams in slide decks |
| [[visual-explainer]] | Use when a scrollable HTML page is better than slides |
| [[remotion]] | Animate a slide deck as a Remotion video |
| [[product-spec]] | Turn a product spec into a presentation deck |
| [[imagegen]] | Generate illustrative images for slide backgrounds |

**Topic map:** [[frontend-ui]]

## Remember
Treat the deck like a product artifact. If it is not editable, reviewable, and reproducible, it is not done.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
