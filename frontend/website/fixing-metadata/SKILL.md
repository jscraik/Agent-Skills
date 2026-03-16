---
name: fixing-metadata
description: Audit and fix HTML metadata including titles, descriptions, canonical URLs, Open Graph tags, Twitter cards, favicons, JSON-LD, and robots directives. Use when adding SEO metadata or shipping pages that need correct meta tags.
license: MIT
---

# Fixing Metadata

Use this skill for precise metadata remediation, not broad SEO platform rewrites.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Priority order](#priority-order)
- [Workflow](#workflow)
- [Validation](#validation)
- [References](#references)

## Standards snapshot
- Metadata should be deterministic, minimal, and aligned with the project’s existing framework pattern.
- Canonical URL, `og:url`, title, and description should agree unless there is a deliberate exception.
- Prefer stable public URLs and production-safe defaults over clever dynamic metadata.
- Keep changes scoped to metadata and related assets; do not widen into unrelated page refactors.

## When to use
- A page or route is missing or misconfigured metadata.
- The user needs an audit of titles, descriptions, canonical tags, robots directives, or social card tags.
- A launch or shareability pass needs favicon, manifest, JSON-LD, or metadata verification.
- A repo needs minimal targeted fixes for SEO or social preview correctness.

## Required inputs
- Target page, route, or file scope.
- Framework context if known:
  - Next.js metadata API;
  - React Helmet;
  - Astro head tags;
  - manual HTML head management.
- Any explicit constraints such as “metadata only” or “no refactors.”
- The intended public URL or canonical host when metadata depends on environment config.

## Deliverables
- Prioritized findings or scoped metadata edits.
- Minimal remediation guidance with exact tag or config fixes.
- A short validation checklist covering search and social preview correctness.

## Failure mode
- If the user is really asking for OG image design, route to the OG image skill.
- If the task needs a full marketing SEO strategy rather than metadata repair, say so and keep this skill narrowly scoped.
- If the canonical host or public URL is unknown, stop before inventing production metadata.

## Priority order
1. Correctness and duplication
2. Title and description
3. Canonical and indexing
4. Open Graph and Twitter cards
5. Icons and manifest
6. Structured data
7. Locale and alternates

## Workflow
1. Confirm the metadata surface and framework pattern already in use.
2. Fix critical correctness issues first:
   - duplicate tags;
   - conflicting metadata sources;
   - unstable or unsafe values.
3. Align title, description, canonical URL, and `og:url`.
4. Verify social card tags use absolute production-safe URLs.
5. Add icons, manifest, or JSON-LD only when they map to real project assets and content.
6. Keep the diff minimal and scoped to metadata-related files.

## Validation
- Confirm no duplicate title, description, canonical, or robots tags remain.
- Ensure canonical and `og:url` target the same preferred public URL.
- Verify OG and Twitter image URLs are absolute and point to real assets.
- If JSON-LD is added, check that it reflects visible page content rather than invented data.

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Agent metadata: `agents/internal.yaml`

## See Also

| Skill | When to use together |
|---|---|
| [[fixing-accessibility]] | Fix ARIA and semantic HTML alongside metadata |
| [[og-image-creator]] | Generate OG images that the metadata tags will reference |
| [[favicon-generator]] | Add favicon tags alongside other head metadata |
| [[cloudflare-deploy]] | Verify metadata is served correctly after Cloudflare deployment |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
