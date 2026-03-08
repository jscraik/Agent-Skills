---
name: docs-md
description: "Review and refactor overloaded Markdown docs into progressive-disclosure docs when the user asks for structural cleanup or document-splitting of README, runbooks, specs, or internal docs: keep the landing doc short, split deep or volatile sections into linked companion docs, add a table of contents, and flag contradictions/bloat. Do not use for AGENTS/CLAUDE/GEMINI refactors, proofreading, translation, tone polish, API-reference writing, or generic docs QA."
---

# Docs Md

## Table of Contents
- [Remember](#remember)
- [Philosophy](#philosophy)
- [Scope and triggers](#scope-and-triggers)
- [Response format (required)](#response-format-required)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Reference map](#reference-map)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Procedure](#procedure)

## Remember
The agent is capable of extraordinary documentation work in this domain. These constraints unlock better judgment rather than limit it: use judgment, explore options, adapt to context, and keep docs easy to scan in under two minutes.

## Philosophy

Prefer concise, verifiable docs over megadocs. Treat the primary document as a front door: it should orient the reader fast, then link to deeper references for details. Optimize for both humans and agents by making structure explicit, keeping headings stable, and moving volatile detail out of the landing page.

Guiding principles:
- Clarity over volume.
- Stable navigation over clever prose.
- Facts and commands must be verified from the repo.
- Keep one document focused on one job.
- Delete duplication before adding new text.
- Outputs should vary with context; no two restructures should look identical unless the inputs are materially the same.
- Default to canonical-only guidance unless compatibility is explicitly required.

Mandatory snippet (include verbatim when the target docs are workflow or agent oriented):
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Scope and triggers

Use this skill when:
- The user asks to structurally refactor a large, overloaded, or repetitive README, runbook, spec, onboarding guide, or internal Markdown doc.
- The user explicitly wants a long document split into linked, lower-cognitive-load companion docs.
- The user wants the same documentation set to work better for both humans and coding agents.
- The repo has drift, repetition, or mixed audiences inside one document.

Route elsewhere when:
- The task is specifically about `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`; use the dedicated md skill instead.
- The task is pure proofreading, translation, or tone polish with no structural rewrite.
- The task is API reference authoring or generic docs QA; use `docs-expert` unless progressive disclosure is the main need.

## Response format (required)
- Always include all three sections in every response:
  - `## When to use`
  - `## Outputs`
  - `## Inputs`
- Use the exact heading text and casing above.
- For out-of-scope requests, still start with `## When to use` and include the other two sections.
- Do not write text before `## When to use`.

### Response template (minimum)

```md
## When to use
- in scope

## Outputs
- ...

## Inputs
- ...
```

### Failure-mode template (out of scope)

```md
## When to use
- This skill applies when the user asks to create or refactor Markdown docs using progressive disclosure.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

Use the failure-mode template verbatim for out-of-scope requests.

## Required inputs
- Target document path(s) or docs area.
- Existing doc structure and any parent guidance files that apply.
- Verified commands, paths, and workflows from the repo.
- Primary audience: humans, agents, or both (default: both).
- Existing docs root convention (`docs/`, `instructions/`, package-local docs, etc.).
- Any sections that must stay inline for legal, compliance, or release reasons.
- Compatibility posture (default: canonical-only unless explicitly requested otherwise).

If inputs are incomplete, ask only the minimum needed to proceed safely.

## Deliverables
- A concise top-level doc draft or merge-safe refactor plan.
- A linked companion-doc structure under the repo's existing docs convention.
- A table of contents that matches real headings.
- A reader map showing what stays in the front door doc vs linked docs.
- A contradictions list with one question per conflict.
- A flag-for-deletion list for redundant, stale, vague, or over-obvious content.
- Output contract schema_version: 1.

## Constraints
- Redact secrets, tokens, credentials, and PII by default.
- Do not invent commands, scripts, headings, or paths.
- Reuse the repo's existing documentation tree; do not create a second competing docs root.
- Keep the landing doc concise; move deep examples, volatile details, and edge cases to linked docs.
- Use ASCII unless the repo already uses non-ASCII.
- Do not add dependencies, tooling, or compatibility layers unless explicitly requested.

## Workflow
1) Discover the current doc topology.
- Read the target doc plus nearby docs that define structure or command truth.
- Identify the current docs root and reuse it.
- Note mixed audiences, duplication, and volatile sections.

2) Verify facts before drafting.
- Source commands and paths from README, scripts, config, CI, or other canonical repo files.
- If a command or path cannot be verified, mark it `not observed` instead of inventing it.

3) Classify content by job.
- Front door: purpose, quick start, decision points, essential commands.
- Task docs: step-by-step workflows.
- Reference docs: exhaustive options, schemas, examples, edge cases.
- Volatile docs: generated output, changing metrics, release-state details.

4) Refactor using progressive disclosure.
- Keep the front door doc short and skimmable.
- Split deep or unstable content into linked companion docs.
- Prefer one stable heading tree over repeated inline explanation.
- Use plain language and short bullets before long prose.

5) Add navigation.
- Add a table of contents when the doc is long enough to need it.
- Add short "read this next" links between related docs.
- Keep link depth shallow: prefer one hop from the main doc to detailed docs.

6) Surface contradictions and cleanup.
- List conflicting instructions, duplicated guidance, stale sections, and obvious filler.
- Do not silently resolve conflicts that require a human decision; ask which version should win.

7) Validate before finalizing.
- Confirm headings, internal links, commands, and file paths are real.
- Confirm the TOC matches the final heading structure.
- Remove any sentence that does not help the next reader act faster.

## Reference map
- Deep patterns and splitting heuristics: `references/doc-split-patterns.md`
- Output contract: `references/contract.yaml`
- Eval cases: `references/evals.yaml`
- Build notes for this skill: `references/plan.md`

## Validation
- Fail fast: stop at the first failed gate, fix it, then rerun.
- Validate this skill with:
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py product/docs/docs-md`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py product/docs/docs-md`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py product/docs/docs-md`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py product/docs/docs-md --mode both`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py product/docs/docs-md`
- Validate each documentation refactor by checking headings, links, commands, and path existence.

## Anti-patterns
- NEVER split docs just to create more docs.
- DO NOT invent commands, file paths, tool choices, or a second docs root.
- Avoid repetitive, generic, or cookie-cutter restructures.
- Call out pitfalls, warnings, and contradictions instead of burying them.
- Duplicating the same workflow in README, docs, and runbooks.
- Leaving volatile release details in the landing page.
- Adding a table of contents that does not match the actual headings.
- Mixing human onboarding, operator runbooks, and deep reference material in one section.

## Examples
- Triggering prompt: "Refactor this README into progressive-disclosure docs so both humans and agents can use it faster."
- Triggering prompt: "Split this long runbook into a concise index plus linked procedures."
- Non-triggering prompt: "Proofread this paragraph and make it friendlier."
- Non-triggering prompt: "Update AGENTS.md to follow repo conventions."

## Procedure
1) Clarify scope only where necessary.
2) Execute the smallest useful doc split first.
3) Summarize what changed, what moved, and what still needs a human decision.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path product/docs/docs-md/SKILL.md --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
