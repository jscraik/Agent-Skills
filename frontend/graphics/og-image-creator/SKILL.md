---
name: og-image-builder
description: Generate brand-aligned Open Graph images for existing routes by inspecting a web codebase and rendering assets with Playwright components. Use when a user asks for route-specific OG image generation or refresh in an existing app.
metadata:
  skill-type: scaffolding_templates
---

# OG Image Builder

Generate route-aware social preview images that feel native to the product instead of generic social card templates.

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
- Study the codebase first; OG images should inherit the product's visual language.
- Prefer scripted generation and route discovery over one-off image editing.
- Use actual page metadata, titles, and descriptions rather than placeholders.
- Keep outputs compatible with common OG consumers: 1200x630, stable URLs, reasonable file size.

## When to use
- A site or app needs route-specific Open Graph images.
- Existing OG images are generic, missing, or visually disconnected from the product.
- The user wants a scripted workflow that can regenerate assets after content changes.
- A codebase already has components, colors, and assets worth reusing in the OG system.

## Required inputs
- Target repo or page set to inspect.
- Framework context if already known: Next.js, Astro, React Router, or similar.
- Output preference:
  - static asset generation;
  - metadata wiring only;
  - or both.
- Any branding constraints such as logo usage, typography, or page-type distinctions.

## Deliverables
- Generated OG image assets in the correct static output location.
- A short route map covering which pages received which visual treatment.
- Minimal metadata wiring notes or code updates when requested.
- A concise explanation of any pages intentionally grouped into shared templates.

## Philosophy
- Brand alignment beats generic polish.
- Route-aware templates are better than a single overfit social card.
- Scripted generation is the default because OG assets need maintenance, not one-off artistry.

## Failure mode
- If the task is primarily about metadata tags rather than image generation, route to the metadata skill.
- If there is no accessible repo or page context, stop before inventing brand treatments.
- If the user wants illustration or marketing design from scratch rather than repo-grounded social cards, say so and redirect accordingly.

## Constraints
- Redact secrets, unpublished URLs, and internal environment details by default in generated previews and notes.
- Do not replace metadata patterns wholesale when the user only asked for image generation.
- Keep outputs tied to real routes and brand assets that exist in the project.

## Workflow
1. Discover the framework and route structure.
2. Extract brand signals:
   - logo and icons;
   - palette;
   - fonts;
   - recurring layout motifs.
3. Group routes into sensible page types such as landing, docs, article, product, or company.
4. Use the bundled scripts for repeatable generation:
   - `scripts/analyze_codebase.py`
   - `scripts/generate_og_images.py`
5. Reuse existing components or design primitives where possible.
6. Generate page-specific or template-shared OG images with real content.
7. Wire or verify metadata references only after the image outputs are stable.

## Anti-patterns
- Using the same template for landing pages, docs, and articles without checking context.
- Filling OG cards with placeholder copy or dev-only URLs.
- Rebuilding brand language from scratch when the repo already exposes usable components and tokens.

## Validation
- Fail fast: stop at the first broken asset path, route mismatch, or metadata reference instead of compensating with placeholders.
- Confirm generated images are 1200x630 unless the target stack has a deliberate alternative.
- Ensure OG image URLs and metadata point to real assets, not localhost or dev-only paths.
- Check at least one sample per page type for legibility and brand fit.
- Keep file sizes reasonable for social crawlers and preview loading.

## Examples
- "Generate OG images for our marketing pages by reusing the current homepage branding."
- "Audit our docs OG cards and make them look like the product instead of generic gradients."
- "Set up a repeatable workflow that regenerates OG images for article pages from metadata."

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Best practices: `references/best-practices.md`
- Framework workflows: `references/framework-workflows.md`
- OG specs: `references/og-specifications.md`
- Scripts: `scripts/analyze_codebase.py`, `scripts/generate_og_images.py`
- README: `README.md`
- Asset preview: `assets/og-image-creator.png`

## See Also

| Skill | When to use together |
|---|---|
| [[fixing-metadata]] | Wire generated OG images into correct meta tags |
| [[favicon-generator]] | Generate OG images and favicons as a complete brand suite |
| [[imagegen]] | Use imagegen for non-route-specific image generation |
| [[cloudflare-deploy]] | Serve OG images via Cloudflare Pages after generation |

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
