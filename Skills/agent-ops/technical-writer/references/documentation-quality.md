# Documentation Quality Reference

Use this reference when a technical-writer task needs more than command accuracy.
Keep `SKILL.md` compact; load this file for prose quality, co-authoring, or
reader-testing decisions.

## Read When

- A document is accurate but hard to skim.
- A rewrite needs better headings, topic sentences, examples, or recovery steps.
- A user is co-authoring a substantial document, proposal, technical spec, or
  decision record.
- A document needs reader-state, citation, glossary, format-choice, or visual
  structure decisions before rewriting.
- Completion depends on whether a reader can use the document without hidden
  conversation context.

## Skimmable Docs Help Readers Find The Useful Part

- Put the main takeaway near the top of the document and each section.
- Use section titles that preview the point.
- Add a table of contents for longer documents.
- Keep paragraphs short.
- Start paragraphs and sections with standalone topic sentences.
- Put topic words near the start of topic sentences and bullets.
- Use bullets, tables, and bold text when they reduce search time.

## Clear Prose Reduces Reader Tax

- Use short sentences with one clear action or claim.
- Prefer sentence shapes that parse unambiguously on first read.
- Avoid left-branching sentences that delay the main object or verb.
- Avoid unclear demonstrative pronouns across sentences.
- Keep terminology, heading style, punctuation, and capitalization consistent.
- Do not presume what readers think, want, or already know.

## Broad Helpfulness Prevents Avoidable Stalls

- Write simply, especially for readers who are new to the tool, language, or
  domain.
- Write out abbreviations unless the expanded form is less clear.
- Prefer specific, accurate terminology over jargon.
- Explain common setup and validation failures when they could block the reader.
- Keep examples self-contained, dependency-light, and safe to copy.
- Never teach unsafe habits such as hardcoding API keys, tokens, or secrets.
- Prioritize common reader tasks before rare edge cases.

## Quality Rubric Connects Style To Reader Outcomes

For substantial documentation, evaluate the changed path against:

- Clear: the reader can identify the purpose, next action, and key claim
  without rereading.
- Relevant: the content serves the named reader job and prioritizes common
  reader tasks before rare edge cases.
- Accurate: every operational claim has live evidence, a citation, a command
  result, or a marked blocker.
- Brief: the doc uses the fewest sections, paragraphs, examples, and visuals
  that still preserve reader success.

The target reader outcome is:

- Understood: prerequisites are introduced or linked before use, and ambiguous
  terms are resolved.
- Logical: sections follow the reader's task sequence, not the writer's
  discovery sequence.
- Accepted: claims are supported by evidence, uncertainty is named, and
  validation outcomes are reported without overclaiming.

## README Reviews Need First-Run Proof

For README and onboarding docs, check whether a reader can succeed in the first
five minutes.

- Verify headline numbers, status claims, badges, generated counts, and command
  examples from live repository evidence.
- Explain related surfaces before listing many counts. For example, distinguish
  visible runtime skills, generated command handles, and canonical source skills.
- Add a table of contents when the README is long enough that a reader will jump
  between setup, command reference, layout, validation, and governance sections.
- Keep the quick start focused on the shortest safe path. Move exhaustive command
  catalogs below the first successful workflow.
- If a documented validation command currently fails, include the failure class,
  likely ownership, and the next recovery command or blocked status.
- Rate the document against accuracy, skimmability, first-run success, safety,
  and evidence quality before rewriting.

## Visuals Should Explain Relationships

Use visuals when they reduce cognitive load. Do not add decoration.

- Prefer small Mermaid diagrams, screenshots, images, or tables for ownership
  boundaries, routing flows, state transitions, validation pipelines, and real
  UI or runtime states the reader must recognize.
- Prefer screenshots or images when the reader needs to inspect what the product,
  UI, report, or output actually looks like.
- Include alt text or adjacent prose so the visual is not the only source of
  meaning.
- Keep visuals close to the section they clarify.
- Do not invent metrics, dashboards, logos, screenshots, or architecture
  components to make a visual look complete.

## Shaping Substantial Docs

Use this loop when a doc needs more than command accuracy or local copy edits.
Keep the entrypoint small; do the detailed shaping here.

- Classify the mode: explore, shape, rewrite, or validate.
- Search the active glossary before introducing domain language. Prefer
  `UBIQUITOUS_LANGUAGE.md`, then repo-local `UBIQUITOUS.md`,
  `UBIQUITOUS-MAP.md`, or `glossary*` files when present.
- Build a Reader-State Map:
  `concept -> prerequisite | introduced here | cited evidence | missing foundation`.
- Draft or patch one block at a time. For each block, state what it does for
  the reader, what concepts it assumes, what it introduces, and which citation
  or evidence source supports it.
- Re-read the surrounding document before the next block so user edits and
  local context change the next move.

Reader-state checks:

- A block may lean only on concepts the reader already brings or that earlier
  text introduced.
- If a term is needed and the repo already has a glossary or ubiquitous-language
  entry, use that term and cite the source.
- If no term exists and the term is durable, add the plain term to the doc and
  the active glossary or ubiquitous-language surface with citation or assumption
  evidence.
- If a concept, example, ownership decision, command output, screenshot, or
  recovery path is missing, raise the gap with the writer and gather the missing
  information. Do not cut, invent, or bury the gap unless the user chooses that
  path.

Treat evidence as source material, not prose to paste. Quote only when exact
wording is the point. Otherwise paraphrase, then cite the file, line, command,
receipt, screenshot, or blocker that supports the claim.

## Format Choices Should Be Defensible

Choose the block format based on the reader job:

- Prose carries argument, sequence, and causality.
- Lists carry parallel items and reduce scan time.
- Tables fit three or more items with the same fields.
- Callouts fit tips, notes, and warnings only when they would derail the main
  path inline.
- Code blocks fit runnable, multi-line, or illustrative examples.
- Inline code fits a token, identifier, command name, path, handle, or field.
- Screenshots and images fit UI states, rendered artifacts, dashboards, or
  visual outputs the reader must recognize.
- Diagrams fit relationships, pipelines, ownership boundaries, and state
  transitions better than prose alone.

## Co-Authoring Needs Context Before Drafting

For substantial new documents, gather:

- document type;
- primary audience;
- desired reader impact;
- template or format constraints;
- known facts, decisions, alternatives, trade-offs, and risks;
- related files, discussions, links, or prior docs that can be verified.

Build the document section by section. Ask targeted questions for the current
section, draft only the chosen content, and revise surgically instead of
reprinting the whole document.

## Reader Testing Finds Hidden Assumptions

Before calling a substantial document ready, test whether the document works
without conversation context:

1. Predict realistic reader questions.
2. Ask whether the document answers those questions from its own text.
3. Check for ambiguous terms, false assumptions, missing setup, contradictions,
   and unsupported claims.
4. Patch the document or mark the gap as blocked.

Use subagents only when the active environment supports them and the task
benefits from a fresh-reader pass. Otherwise, provide a manual reader-test
checklist.

## Source Context

This reference was distilled from two operator-provided context files:

- `/Users/jamiecraik/Downloads/what_makes_documentation_good.md`
- `/Users/jamiecraik/Downloads/SKILL (15).md`
- `/Users/jamiecraik/Downloads/SKILL (23).md`
- `/Users/jamiecraik/Downloads/SKILL (24).md`
- `/Users/jamiecraik/Downloads/SKILL (25).md`

The source files are context, not binding repo policy. Claude-specific artifact,
connector, and integration instructions were translated into Codex-safe
documentation workflow guidance rather than copied directly. Writing-fragment,
beat, and shaping methods were translated into technical-doc reader-state,
citation, glossary, gap-gathering, and format-choice rules.
