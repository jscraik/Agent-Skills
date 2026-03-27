---
name: favicon-generator
description: Generate complete favicon/app icon suites with templates and assets. Use when the user needs favicons or app icons for a web/app project.
metadata:
  skill-type: scaffolding_templates

---

# Favicon Generator

Create favicon and app-icon sets that match the actual product identity instead of inventing a disconnected mark.

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
- Reuse the existing brand mark whenever possible.
- Design for 16x16 and 32x32 first; if it fails there, it fails everywhere.
- Prefer script-backed generation and repeatable outputs over hand-edited export drift.
- Only add manifest and platform icons that the target app will actually use.

## When to use
- The user needs a favicon suite for a website or web app.
- The user needs browser icons plus optional PWA or app-style icon outputs.
- A repo has branding in place but is missing a production-ready icon set.
- Existing favicon assets are inconsistent, blurry, or incomplete and need replacement.

## Required inputs
- Brand source:
  - existing logo SVG or PNG;
  - a codebase icon already used as the product mark;
  - or explicit direction that a fresh mark is needed.
- Brand colors or the repo location where they can be derived.
- Target outputs: web only, or also PWA and app-style icons.
- Desired output path if the skill should write assets into a repo.

## Deliverables
- `favicon.ico` plus a PNG set for the requested sizes.
- `site.webmanifest` if the user actually wants PWA-ready assets.
- Integration guidance with the exact metadata or HTML references to wire in.
- A short rationale when choosing one mark treatment over another.

## Philosophy
- Reuse the product’s real mark before inventing a new one.
- Favor clarity at tiny sizes over decorative detail.
- Keep generation reproducible so future refreshes do not drift.

## Failure mode
- If the request is really about broader brand identity or logo design, pause and recommend a design skill first.
- If the codebase already has a canonical icon and the user asks for something radically different, surface the brand-consistency tradeoff before generating.
- If the source asset is too low quality for a clean export, say so and request a better source rather than masking it with effects.

## Constraints
- Redact secrets, private URLs, and sensitive repo paths by default in examples and generated guidance.
- Do not replace an existing canonical icon suite without making the overwrite explicit.
- Keep the scope to favicon assets and the minimum metadata wiring needed.

## Workflow
1. Discover whether the repo already has a canonical logo, mark, or icon.
2. Confirm the real deployment target:
   - browser favicon only;
   - browser + Apple touch icon;
   - browser + manifest/PWA set.
3. Pick the simplest mark that survives tiny sizes:
   - reduce fine detail;
   - increase padding;
   - avoid hairline strokes.
4. Use the bundled generator workflow when creating assets:
   - `scripts/generate_favicon.py`
   - `scripts/generate_favicon.html`
5. Keep decorative effects subtle and only if the mark stays legible at 16x16.
6. Return the exact files created and the minimal integration changes needed.

## Anti-patterns
- Designing a new icon when the app already has a clear product mark.
- Using heavy effects to compensate for a weak base mark.
- Shipping manifest or icon sizes the app will never reference.

## Validation
- Fail fast: stop at the first failed gate and repair the source asset or output path before generating more variants.
- Check the mark at 16x16, 32x32, and one large reference size before finalizing.
- Confirm generated file names match the integration snippet.
- If a manifest is included, ensure it references real output files.
- If writing to a repo, keep changes scoped to icon assets and metadata wiring only.

## Examples
- "Generate a browser favicon set from the existing SVG logo and give me the exact tags to add."
- "Refresh our PWA icons so they match the new app mark without touching unrelated branding."
- "Audit our current favicon outputs and tell me which assets are missing or blurry."

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Effects guidance: `references/effects-guide.md`
- Extended guidance: `references/extended.md`
- Extra notes: `references/extra.md`
- Scripts: `scripts/generate_favicon.py`, `scripts/generate_favicon.html`
- Asset preview: `assets/favicon-generator.png`

## See Also

| Skill | When to use together |
|---|---|
| [[fixing-metadata]] | Pair with metadata fixes to ensure correct favicon references |
| [[design-system]] | Keep favicon palette consistent with design-system tokens |
| [[og-image-creator]] | Generate OG images alongside favicons for complete brand suite |
| [[cloudflare-deploy]] | Include favicon assets in Cloudflare Pages deployments |

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
