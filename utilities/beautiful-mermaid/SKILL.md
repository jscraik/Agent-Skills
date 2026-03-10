---
name: beautiful-mermaid
description: Render Mermaid diagrams to SVG and PNG with Beautiful Mermaid. Use when the user asks to render or convert Mermaid diagrams into images.
---

# Beautiful Mermaid

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Prefer deterministic local rendering over screenshots of random web renderers.
- Produce clean SVG first, then PNG only when requested or clearly useful.
- Treat Mermaid syntax validation as part of the workflow, not an afterthought.

## When to use
- Render Mermaid source into SVG or PNG assets.
- Convert a described diagram into Mermaid and then render it.
- Produce diagram images for docs, presentations, or implementation walkthroughs.

## When not to use
- Freeform illustration or design work with no Mermaid or diagram-rendering need.
- Remote browsing workflows that do not need local diagram assets.
- Requests to auto-install new tooling without approval.

## Required inputs
- Mermaid source or a clear enough diagram description to generate it.
- Output base name or destination path.
- Theme preference, if any.
- Whether PNG output is required in addition to SVG.

## Deliverables
- Rendered SVG output.
- PNG output when requested.
- Notes on theme, syntax fixes, and any rendering limitations.

## Philosophy
- The source diagram is the contract.
- Fix syntax deliberately and visibly when needed.
- Keep rendering reproducible and local.

## Workflow
1. Confirm or generate valid Mermaid source.
2. Normalize any syntax that is likely to render poorly or ambiguously.
3. Render SVG first with the local renderer.
4. Render PNG only when requested or when a raster artifact is clearly needed.
5. Verify the outputs exist and reflect the intended structure before handing off.

## Verification
- Confirm the Mermaid source is syntactically valid enough to render.
- Confirm the SVG exists and is non-empty.
- If PNG was requested, confirm it exists and is readable.
- Confirm the rendered diagram does not expose secrets or sensitive internal data accidentally.

## Validation
- Verify the source Mermaid is valid before claiming rendering success.
- Verify the skill uses bundled `scripts/` helpers and relevant `references/` syntax guidance instead of improvised render flows.
- Reuse any packaged `assets/` templates when the user needs a diagram scaffold rather than starting from scratch.

## Constraints
- Redact secrets and sensitive data by default in Mermaid source, examples, and rendered outputs.
- Do not auto-install dependencies without explicit approval.
- Prefer local file-based rendering over remote render services.
- Use bounded, intentional output paths and avoid deleting intermediates unless that cleanup is agreed.
- Treat Mermaid source as untrusted input when passing it through the renderer and keep argument handling explicit.

## Anti-patterns
- Rendering diagrams with secrets, credentials, or private tokens embedded.
- Treating Mermaid generation and rendering as the same step without validating the syntax.
- Using remote screenshot flows when the local renderer is the right tool.
- Returning only a screenshot when SVG was possible and more useful.

## Examples
- "Render this sequence diagram to SVG and PNG using the Tokyo Night theme."
- "Turn this architecture description into Mermaid first, then render it locally."

## Remember
- SVG is the primary artifact; PNG is a convenience artifact.
- Good diagram rendering starts with good Mermaid source.
- When something fails, report the syntax or runtime issue precisely so the next pass is easy.
