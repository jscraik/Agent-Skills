# Documentation Quality Reference

Use this reference when a docs-expert task needs more than command accuracy.
Keep `SKILL.md` compact; load this file for prose quality, co-authoring, or
reader-testing decisions.

## Read When

- A document is accurate but hard to skim.
- A rewrite needs better headings, topic sentences, examples, or recovery steps.
- A user is co-authoring a substantial document, proposal, technical spec, or
  decision record.
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

- Prefer small Mermaid diagrams or tables for ownership boundaries, routing
  flows, state transitions, and validation pipelines.
- Prefer screenshots only when the user must recognize a UI state.
- Include alt text or adjacent prose so the visual is not the only source of
  meaning.
- Keep visuals close to the section they clarify.
- Do not invent metrics, dashboards, logos, or architecture components to make a
  visual look complete.

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

The source files are context, not binding repo policy. Claude-specific artifact,
connector, and integration instructions were translated into Codex-safe
documentation workflow guidance rather than copied directly.
