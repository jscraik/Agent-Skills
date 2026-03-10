---
name: slides
description: Use when tasks involve creating, editing, recreating, validating, or visually debugging presentation slide decks (`.pptx`) with editable PowerPoint output, PptxGenJS authoring, bundled layout helpers, and render/overflow checks; do not use for generic web UI design, prose editing, or non-presentation visual explainers.
---

# Slides Skill

Create and edit presentation slide decks with strong defaults for editable output, visual validation, and layout-safe delivery.

## When to use
- Create a new `.pptx` deck from requirements, outlines, screenshots, or existing reference material.
- Rebuild slides from a PDF, screenshot set, or prior deck while preserving editability where possible.
- Update an existing deck without breaking layout, typography, charts, or aspect ratio.
- Diagnose slide overflow, overlaps, font substitution, or rendering differences before delivery.
- Generate presentation-ready slides that need both the final `.pptx` and rebuildable source.

## When not to use
- Generic web UI layout, frontend component work, or dashboard design that should route to a frontend/UI skill.
- Markdown, Word, or prose-only document editing without presentation deck output.
- Static visual summaries that do not need editable PowerPoint artifacts.
- Requests that only need image editing, illustration generation, or slide-adjacent brand exploration.

## Inputs
- Requested slide task: create, edit, recreate, debug, or validate.
- Source material such as screenshots, PDFs, existing decks, charts, copy, or branding guidance.
- Destination path for the final `.pptx` and whether the authoring `.js` should also be delivered.
- Constraints on fonts, aspect ratio, theme, dependencies, or whether local rendering tools are available.

## Outputs
- Updated or newly created `.pptx` deck aligned to the request.
- Rebuildable JavaScript source when the deck is authored or substantially edited with PptxGenJS.
- Short evidence summary covering layout checks, rendering review, font issues, and blockers.
- When a structured status report is requested, include a `schema_version` field in the returned payload.

## Philosophy
- Prefer editable slide output over opaque screenshots whenever the request allows it.
- Keep deck work reproducible: source code, helper assets, and validation should travel together.
- Validate visually before delivery whenever rendering tools are available.
- What proves this deck still fits the canvas after the change?
- Which elements should remain native PowerPoint content instead of rasterized artwork?

## Constraints
- Redact secrets, tokens, credentials, and sensitive slide content by default.
- Do not claim rendering, overflow checks, or font validation happened unless the corresponding tools actually ran.
- Do not silently change aspect ratio, theme fonts, or slide density when preserving an existing deck matters.
- Keep network access out of the workflow unless the user explicitly requires an external asset fetch.
- If required tools are missing, report the exact dependency blocker and stop instead of improvising.
- Treat speaker notes, hidden slides, comments, and embedded metadata as sensitive content unless the user explicitly asks to surface them.

## Workflow
1. Confirm whether the task is deck creation, deck editing, recreation from references, or validation-only.
2. Determine the slide size up front and default to 16:9 only when the source does not clearly specify another ratio.
3. Use JavaScript plus PptxGenJS for authoring or major edits so the result stays rebuildable and editable.
4. Reuse the bundled helper library in `assets/pptxgenjs_helpers/` instead of reimplementing spacing, code, image, LaTeX, or layout utilities.
5. Preserve text as text and simple charts as native PowerPoint elements when practical.
6. Render the deck and inspect output images before delivery when rendering tools are available.
7. Run overflow and bounds checks for dense or edge-to-edge layouts, then fix the first real issue before continuing.

## Tooling
- Use PptxGenJS for slide generation and substantial edits to `.pptx` decks.
- Use the bundled helpers in `assets/pptxgenjs_helpers/` for text sizing, image placement, SVG handling, equations, and layout helpers.
- Use `scripts/render_slides.py` to rasterize decks for visual review.
- Use `scripts/slides_test.py` to detect out-of-bounds or overflow issues.
- Use `scripts/create_montage.py` to build quick-contact-sheet previews for large decks.
- Use `scripts/detect_font.py` to detect missing or substituted fonts when LibreOffice rendering is in play.
- Use `scripts/ensure_raster_image.py` when vector or odd asset formats need debug-ready PNG output.

## Temp and output conventions
- Do deck work in a task-local workspace instead of editing final deliverables in place.
- Keep helper assets next to the authoring script so the deck can be rebuilt without hidden dependencies.
- Write review images and montages to a temporary render directory, then delete them when they are no longer needed.
- Copy only final requested artifacts to the destination path after validation passes.

## Dependencies
Prefer local, explicit tools over hidden runtime assumptions.

Authoring/runtime:

```bash
npm install pptxgenjs
```

Rendering and review helpers use Python and local presentation tools:

```bash
python3 --version
libreoffice --version
```

Some helper workflows may also need image tooling such as ImageMagick, Poppler, or Inkscape depending on the asset mix. If a dependency is missing, report the exact install gap before continuing.

Fallback expectations:
- If LibreOffice is missing, preserve the editable source and report visual validation as blocked.
- If Poppler or `pdf2image` support is missing, skip PNG review and report the missing render dependency explicitly.
- If theme fonts are unavailable locally, report font drift as a validation warning instead of silently accepting substitutions.

## Recalculation and visual review
- Render decks to slide images before delivery whenever rendering support exists.
- Review the rendered output for clipped text, overlaps, bad crops, font substitutions, and canvas overflow.
- For recreated decks, compare against the original reference render before finalizing.
- If a warning is intentional, leave a short comment in the authoring source near the affected element.

Helpful validation commands:

```bash
python3 scripts/render_slides.py deck.pptx --output_dir rendered
python3 scripts/create_montage.py --input_dir rendered --output_file montage.png
python3 scripts/slides_test.py deck.pptx
python3 scripts/detect_font.py deck.pptx --json
```

## Slide rules

### Authoring rules
- Set theme fonts explicitly when typography matters.
- Use helper-based text sizing instead of relying on loose auto-fit behavior.
- Use bullet options rather than literal bullet glyphs.
- Prefer native PowerPoint charts for simple chart types that reviewers may need to edit later.
- Use SVG or raster artwork only when native PowerPoint elements are not a good fit.
- Include overlap and out-of-bounds checks in generated JavaScript when you author or heavily revise slides.

### Preservation rules
- Match the original aspect ratio before rebuilding or editing an existing deck.
- Preserve editability where possible: text should stay text and simple visuals should stay native.
- Do not flatten the whole deck into images just to make layout easier.
- Keep slide spacing, alignment, and style consistent across the deck.

## Validation
- Verify the output `.pptx` exists and opens as a presentation file.
- Verify required companion source files are present when the task calls for rebuildable output.
- Verify rendered slide images when rendering tools are available.
- Verify overflow or bounds warnings are resolved or explicitly documented as intentional.
- Fail fast: stop at the first failed validation gate and report the exact blocker.

## Anti-patterns
- Using `python-pptx` for deck generation when editable PowerPoint authoring is required.
- Delivering a deck without checking for clipped text or out-of-bounds elements.
- Claiming font validation or rendering review without running the corresponding tool.
- Rasterizing content that should stay editable without a clear reason.
- Quietly changing aspect ratio, typography, or layout density during a routine update.
- Treating a screenshot recreation task like a generic design exercise without matching the source geometry first.
- Exposing speaker notes, comments, or hidden-slide content when the task only asks for visible slide output.

## Variation
- Use a creation-first workflow for greenfield decks, a render-compare workflow for recreation tasks, and a minimal-diff workflow for small edits to existing decks.
- Increase visual review rigor for board decks, sales presentations, or screenshot-driven recreations.
- Adapt the helper/tool mix based on whether the task is authoring-heavy, validation-heavy, or asset-conversion-heavy.
- Prefer a validation-only lane when the user already has a deck and only wants overflow, font, or render diagnostics.

## Examples
- Build a clean 10-slide investor update deck with editable charts and speaker-safe spacing.
- Recreate a screenshot-based keynote into a rebuildable `.pptx` and authoring `.js`.
- Update an existing deck’s copy and charts while preserving theme and layout.
- Diagnose which slides overflow the canvas and fix the offending elements before delivery.

## Resource map
- Interface metadata: `agents/openai.yaml`
- Helper library: `assets/pptxgenjs_helpers/`
- Skill assets: `assets/slides-small.svg`, `assets/slides.png`
- Rendering and validation scripts: `scripts/`
- Helper reference: `references/pptxgenjs-helpers.md`
- Validation contracts: `references/contract.yaml`, `references/evals.yaml`

## Quality Uplift
- Philosophy and approach: favor editable, rebuildable decks with evidence-backed visual review.
- Guiding question: what evidence proves the deck still fits and renders correctly?
- Guiding question: which elements should remain native PowerPoint objects?
- Anti-pattern warning: do not claim successful rendering or font validation without tool output.
- Variation: adapt validation depth based on whether the task is creation, recreation, or minor revision.
- Empowerment: help users ship presentation-quality decks confidently by keeping the workflow reproducible and auditable.
