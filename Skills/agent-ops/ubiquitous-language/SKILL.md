---
name: ubiquitous-language
description: Build shared project vocabulary, glossary terms, aliases, prompt translations, and agent instruction links when wording is fuzzy or overloaded.
metadata:
  skill-type: team_automation
---

# Ubiquitous Language

Create or update a project vocabulary so users, domain experts, and agents mean the same thing without forcing the user to know specialist terms.

## Philosophy

Make the user's natural language more powerful instead of making the user sound more technical.

## When To Use

- User mentions glossary, naming, vocabulary, terminology, DDD, domain model, or shared language.
- User says they do not know the technical term.
- A repo has overloaded phrases that agents keep interpreting inconsistently.

Do not use for ordinary symbol renaming, generic copyediting, or broad docs rewrites without reusable terminology.

## Required inputs

- Current conversation and the user's natural wording.
- Existing `UBIQUITOUS_LANGUAGE.md`, if present.
- Nearby project guidance such as `AGENTS.md`, `README.md`, `docs/**`, `instructions/**`, or handoff files.
- Session logs only when the user explicitly asks for history-backed vocabulary.

## Workflow

1. Determine scope and output path.
2. Read any existing glossary first and preserve intentional choices.
3. Extract domain nouns, workflow verbs, actor names, lifecycle states, aliases, and overloaded phrases.
4. Choose canonical terms that improve execution; keep natural-language aliases when useful.
5. Write or update `UBIQUITOUS_LANGUAGE.md`.
6. Add a concise pointer in the nearest active agent instruction surface.
7. Report the highest-value terms, prompt translations, sources, and skipped evidence.

## Deliverables

The glossary should include canonical terms, aliases, relationships, prompt translations, example dialogue, flagged ambiguities, and source notes. Structured output should include `schema_version: 1` when automation consumes it.

## Safety

- Do not copy raw private transcripts, secrets, tokens, or unnecessary personal data.
- Do not overwrite an existing glossary wholesale.
- Ask before finalizing a material policy or scope decision that cannot be inferred.
- Mark low-confidence terminology choices.

## Execution Boundaries

Edit only the requested glossary, instruction pointer, or skill reference surface. Do not rewrite unrelated docs, generated projections, runtime mirrors, or policy files unless the user explicitly names them.

## Anti-Patterns

- Turning the glossary into a generic programming dictionary.
- Copying private transcripts or secrets into vocabulary docs.
- Choosing impressive terms that make future prompts less clear.

## Examples

- "I keep saying make sure it works; turn that into exact validation wording."
- "We use account two ways in this repo; define the canonical terms."

## Failure mode

If the scope, source glossary, or authority for a terminology change is unclear, stop with one missing input rather than rewriting vocabulary by guesswork.

## Gotchas

- Natural user wording is evidence; do not erase it when choosing canonical terms.
- Avoid broad docs rewrites when a glossary pointer would solve the routing problem.

## Progressive Disclosure

Never drop required context for brevity; move it into references or deferred context and link it here.

- Local contract, evals, and task profile: `references/`
- Software-literature domain-language lenses: `Infrastructure/references/software-literature-expert-lens-pack.md`, `Infrastructure/references/software-literature-skill-expertise-map.md`
- Output template: `Infrastructure/references/deferred-skill-context/agent-ops-ubiquitous-language/references/output-format.md`
- Archived long-form workflow: `Infrastructure/references/deferred-skill-context/agent-ops-ubiquitous-language/`

## Validation

Confirm the glossary exists, every canonical term has a one-sentence definition, prompt translations include at least one user phrase when informal wording exists, and the agent instruction pointer references `UBIQUITOUS_LANGUAGE.md`. Fail fast: stop at the first failed gate and do not proceed until the blocker is fixed.
