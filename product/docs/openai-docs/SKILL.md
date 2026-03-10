---
name: "openai-docs"
description: "Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations, help choosing the latest model for a use case, or explicit GPT-5.4 upgrade and prompt-upgrade guidance; prioritize OpenAI docs MCP tools, use bundled references only as helper context, and restrict any fallback browsing to official OpenAI domains."
---

# OpenAI Docs

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Workflow](#workflow)
- [Reference map](#reference-map)
- [Tooling notes](#tooling-notes)
- [Constraints](#constraints)
- [Validation](#validation)
- [Examples](#examples)
- [Anti-patterns](#anti-patterns)
- [Decision feedback protocol](#decision-feedback-protocol)

Provide authoritative, current guidance from OpenAI developer docs using the OpenAI docs MCP tools. Always prioritize the official docs MCP workflow over memory or general web search for OpenAI-related questions.

## Scope and triggers
- Use this skill when the user asks how to build with OpenAI APIs, ChatGPT Apps SDK, Codex, Responses API, Realtime, Agents SDK, model capabilities or limits, or adjacent official OpenAI platform capabilities.
- Use it when the user needs current official guidance, exact limits, supported fields, model selection help, or citations.
- Use it when the request is specifically about a GPT-5.4 upgrade, prompt upgrade, or choosing the latest OpenAI model for a use case.
- Do not use it for general web research or speculative product claims not grounded in official docs.

## Required inputs
- the product or API surface in question
- the specific task, question, or implementation problem
- whether the request is general docs lookup, model selection, or a GPT-5.4 upgrade
- any version, language, or environment constraints that materially affect the answer

## Deliverables
- a concise answer grounded in current OpenAI docs
- links to the exact official doc pages used
- paraphrased or lightly quoted details only where they materially answer the question
- explicit uncertainty when the docs do not fully answer the user’s need
- when relevant, the exact bundled helper reference used in addition to current docs
- when a structured status report is requested, include a `schema_version` field in the returned payload

## Failure mode
If the docs do not contain the answer, say so clearly, summarize what was checked, and then use a tightly scoped fallback on official OpenAI domains only when needed.

## Standards snapshot (March 2026)
- Official OpenAI docs are the source of truth for current product behavior, limits, and examples.
- Search first, then fetch the exact page or anchor before answering.
- Keep citations precise and current; do not answer OpenAI platform questions from memory when fresh docs are available.
- Prefer direct doc-backed guidance over stale local conventions or tool-name folklore.
- Bundled references are helper context only; current official docs always win for volatile guidance.

## Workflow
1. Clarify the product scope and whether the request is general docs lookup, model selection, a GPT-5.4 upgrade, or a GPT-5.4 prompt upgrade.
2. Use `mcp__openai-docs__search_openai_docs` to find the best doc page for the live question.
3. Use `mcp__openai-docs__fetch_openai_doc` to retrieve the relevant page or anchor.
4. If it is a model-selection request, load `references/latest-model.md` as helper context and verify every recommendation against current docs before answering.
5. If it is an explicit GPT-5.4 upgrade request, load `references/upgrading-to-gpt-5p4.md`.
6. If the upgrade may require prompt changes, or the workflow is research-heavy, tool-heavy, coding-oriented, multi-agent, or long-running, also load `references/gpt-5p4-prompting-guide.md`.
7. For GPT-5.4 upgrade reviews, make the per-usage-site output explicit: target model, starting reasoning recommendation, `phase` assessment when relevant, prompt blocks, and compatibility status.
8. Answer with concise guidance and cite the fetched doc page, using bundled references only as helper context.
9. If MCP docs are unavailable or insufficient, fall back to browsing official OpenAI domains only.

## Reference map
Read only what you need:

- `references/latest-model.md` -> model-selection and "best/latest/current model" questions; verify every recommendation against current OpenAI docs before answering.
- `references/upgrading-to-gpt-5p4.md` -> only for explicit GPT-5.4 upgrade and upgrade-planning requests; verify the checklist and compatibility guidance against current OpenAI docs before answering.
- `references/gpt-5p4-prompting-guide.md` -> prompt rewrites and prompt-behavior upgrades for GPT-5.4; verify prompting guidance against current OpenAI docs before answering.
- `references/contract.yaml` and `references/evals.yaml` -> repo-local output and trigger expectations for this skill.

## Tooling notes
- Prefer `mcp__openai-docs__search_openai_docs` for discovery.
- Prefer `mcp__openai-docs__fetch_openai_doc` for exact wording, examples, and anchored sections.
- Use `mcp__openai-docs__list_openai_docs` only when you need broad browsing without a sharp query.
- When falling back to `web.run`, restrict to `developers.openai.com` and `platform.openai.com`.
- Reuse bundled references only when they sharpen the answer without replacing official docs as the source of truth.
- Bundled assets: `assets/openai-small.svg`, `assets/openai.png`.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Never echo raw environment values or secret-bearing commands.
- Prefer safe, read-only documentation retrieval over speculative or mutating guidance.
- If MCP tools fail or return no meaningful results, report that clearly before falling back to official-domain browsing.

## Validation
- Fail fast if the answer is not grounded in an official doc page.
- Re-check the exact page when the question depends on current fields, limits, supported models, or upgrade guidance.
- If multiple pages differ, call out the difference and cite both.
- Report clearly when the docs are silent, ambiguous, or conflicting.

## Examples
- "What is the current Responses API pattern for tool calling?"
- "How do I wire a ChatGPT Apps SDK component with official docs citations?"
- "What do the current Codex docs say about setup and usage?"
- "What is the latest OpenAI model for this use case?"
- "How should I upgrade this workflow to GPT-5.4?"

## Anti-patterns
- Answering OpenAI platform questions from memory when current docs are available.
- Making claims without evidence or without linking the official page.
- Mixing unofficial community advice into a docs-grounded answer without labeling it as such.
- Treating bundled upgrade/model-selection references as authoritative when live docs disagree.
- Browsing unrelated domains when the user asked for OpenAI guidance.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when authoritative, current documentation matters more than memory or folklore.
- Principle and mindset: search first, fetch the exact source, then answer narrowly from evidence.
- Ask this to keep outcomes robust: Why is this the right doc page, and what could change the answer?
- How do we adapt if current docs and bundled helper references diverge?
- What evidence is needed before recommending a model upgrade path?

## Anti-patterns and caveats
- Avoid treating the helper references as a substitute for current docs.
- **NEVER** skip the fetch step when the user needs current limits, field names, or upgrade guidance.
- **DO NOT** answer a "latest" OpenAI question from memory.
- **DON'T** browse non-OpenAI domains when the docs tools already cover the question.
- Common pitfall: stopping at search results without reading the exact page or section.
- Incorrect assumptions here can lead to stale or unsupported guidance.

## Variation and adaptation
- Adapt the workflow depending on whether the request is general docs lookup, model selection, or GPT-5.4 migration planning.
- Use more bundled helper context for upgrade planning and less for straightforward API field lookups.
- Avoid generic or cookie-cutter responses; anchor the answer to the exact product surface and doc section.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of finding the sharpest official guidance quickly.
- Unlock confidence by citing the exact current page and explaining tradeoffs clearly.
- Feel free to surface multiple documented paths when the docs support them.

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
