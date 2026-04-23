---
name: markdown-converter
description: "Convert source files into Markdown outputs using the bundled converter workflow. Use when a user asks to transform documents, notes, or technical files into clean Markdown format."
metadata:
  skill-type: team_automation
---

# Markdown Converter

Convert source documents into usable Markdown with a repeatable `markitdown` workflow instead of ad hoc copy-paste cleanup.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)

## Standards snapshot
- Prefer the bundled `uvx markitdown` path over hand-written conversion steps.
- Keep the output faithful to document structure before optimizing style.
- Ask for the source file or URL first; do not invent conversions from descriptions alone.
- Preserve tables, headings, and links whenever the source format supports them.

## When to use
- The user wants a PDF, DOCX, PPTX, spreadsheet, HTML file, or similar content converted to Markdown.
- The user needs a repeatable conversion workflow rather than a one-off rewrite.
- The task is document extraction or format transformation, not full editorial rewriting.

## Required inputs
- Source file path, URL, or stdin source.
- Desired output path if the result should be written to disk.
- Any format hints needed for stdin workflows such as extension or MIME type.
- Whether higher-quality extraction via Azure Document Intelligence is available and desired.

## Deliverables
- Markdown output to stdout or a requested file path.
- A short note about any extraction limitations or formatting loss.
- Exact converter command used when reproducibility matters.

## Philosophy
- Favor deterministic conversion first, cleanup second.
- Keep guidance tool-backed and concrete rather than generic.
- Make extraction limits explicit so the user can decide whether a second pass is needed.

## Failure mode
- If the user wants content rewritten, summarized, or edited for style, route to a writing or docs skill after conversion.
- If the input format is unsupported or inaccessible, stop and report that directly.
- If a scan is too poor for reliable extraction, recommend a better source or the Azure-backed path instead of faking structure.

## Constraints
- Redact secrets, credentials, and sensitive content by default when showing sample output.
- Do not overwrite existing files unless the destination path is explicit.
- Keep the scope to conversion and extraction, not broader document redesign.

## Workflow
1. Confirm the source path or URL and the desired output destination.
2. Choose the simplest converter path that fits:
   - direct file conversion;
   - stdin with `-x` or `-m` hints;
   - Azure-backed extraction for difficult scans.
3. Run `uvx markitdown` with the smallest set of required flags.
4. Inspect the result for obvious structure failures:
   - missing headings;
   - broken tables;
   - collapsed lists;
   - missing links.
5. Return the Markdown output or saved-file path plus any caveats.

## Anti-patterns
- Treating conversion as if it were editorial cleanup.
- Inventing Markdown structure that the source did not reliably provide.
- Using heavyweight extraction options by default when the basic path is sufficient.

## Validation
- Fail fast: stop at the first broken input, unsupported format, or unreadable output.
- Verify the converter ran successfully and produced non-empty output.
- Spot-check that headings, tables, or lists survived when the source clearly contained them.
- If writing to a file, confirm the destination path contains the expected Markdown output.

## Examples
```bash
# Convert to stdout
uvx markitdown input.pdf

# Save to file
uvx markitdown report.docx -o report.md

# Convert stdin with a file hint
cat input.pdf | uvx markitdown -x .pdf > output.md

# Use Azure Document Intelligence for difficult scans
uvx markitdown scan.pdf -d -e "https://your-resource.cognitiveservices.azure.com/"
```

## References
- Contract: `Infrastructure/references/contract.yaml`
- Evals: `Infrastructure/references/evals.yaml`

## See Also

| Skill | When to use together |
|---|---|
| [[docs-expert]] | Polish converted docs to meet repository quality standards |
| [[visual-explainer]] | Present converted content as a visual HTML page |
| [[spreadsheet]] | Convert tabular data alongside markdown conversion |
| [[llm-wiki]] | Feed converted markdown into a persistent knowledge base for analysis |

**Topic map:** [[content-publishing]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
