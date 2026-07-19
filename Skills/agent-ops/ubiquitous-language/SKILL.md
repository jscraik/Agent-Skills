---
name: ubiquitous-language
description: Builds a project glossary that maps everyday wording to canonical terms, repository actions, and reusable engineering rules. Use when a user asks "what does X mean here?", "define our terms", "standardize this naming", "turn this phrase into a repo action", "grill the domain language", or whether a local correction should apply to similar code.
metadata:
  version: "0.1.0"
  skill-type: team_automation
---

# Ubiquitous Language

Create or update a project vocabulary so users, domain experts, and agents mean the same thing without forcing the user to know specialist terms.

## Outputs

Produce canonical terms, aliases, relationships, ambiguities, sources, and
prompt translations. When corrective feedback is the source, also produce its
intent radius, generalized rule, pattern sweep, dispositions, and enforcement
handoff. Use `schema_version: 1` when automation consumes the output.

## Workflow

1. Determine scope and output path.
2. Resolve the active glossary with the [output-format routing](references/output-format.md); ask only when multiple contexts remain ambiguous.
3. Read any existing glossary first and preserve intentional choices.
4. Extract domain nouns, workflow verbs, actor names, lifecycle states, aliases, and overloaded phrases.
5. When the input is corrective feedback, run Corrective Feedback Mode before choosing scope.
6. Choose canonical terms that improve execution; keep natural-language aliases when useful.
7. Write or update the active ubiquitous-language file.
8. Add a concise pointer in the nearest active agent instruction surface.
9. Report the highest-value terms, prompt translations, sources, pattern-sweep dispositions, enforcement handoffs, and skipped evidence.

## Corrective Feedback Mode

Use this mode when the user corrects a specific line, function, file, command,
API, workflow, or implementation detail and the correction may express wider
engineering intent.

1. Treat the visible example as evidence, not as the presumed scope boundary.
2. Classify the **Feedback Intent Radius** as `line`, `function`, `file`,
   `package`, `repository`, `architecture_rule`, or `durable_memory`.
3. Run a bounded **Pattern Sweep** across structurally similar implementations,
   glossary entries, prompt translations, validators, schemas, tests, and policy
   surfaces. Do not equate textual similarity with equivalent semantics.
4. State the **Generalized Feedback Rule** without the incidental identifier,
   path, function, error, or example that exposed it.
5. Give every relevant sibling a **Similar-Case Disposition**: align now,
   different semantics, defer with reason, or not applicable.
6. Decide whether language alone is sufficient. When recurrence needs mechanical
   prevention, route the rule to the owning validator, lint rule, schema,
   reusable abstraction, shared utility, repository convention, style rule, CI
   check, or architecture policy.
7. Preserve authority boundaries. Systemic intent justifies broader inspection,
   not unrelated or cross-repository mutation; record or hand off out-of-scope
   enforcement work explicitly.

### Worked Corrective-Feedback Output

Input: "This parser fix is not doing what I want; do not patch only this function."

```text
Feedback Intent Radius: repository
Generalized Feedback Rule: Parse failures use typed results; callers never infer failure from missing values.
Pattern Sweep: parsers/** and their direct callers
Similar-Case Dispositions: 3 aligned now; 1 different semantics; 1 deferred to another owner
Enforcement: schema constraint plus parser-contract regression test
```

### Worked Glossary Output

Input: "What does 'make it available' mean in this repository?"

```md
**Runtime Projection**:
The generated skill surface visible to the active agent runtime.
_Avoid_: installed skill, copied source

## Prompt Translations

| User phrase | Canonical action |
| --- | --- |
| "make it available" | Run `./bin/ask skills sync --scope workspace --json`, then `./bin/ask skills sync --scope user --json`, and verify the runtime links. |
```

## Domain Grill Mode

Use this mode when the user asks to be grilled, challenged, interviewed deeply,
or stress-tested against the project domain model. Follow the focused
[domain-grill procedure](references/domain-grill.md).

## Output Format

Use [the output template](references/output-format.md) for new single-context or
multi-context glossaries. Preserve `UBIQUITOUS_LANGUAGE.md` when an existing
repository contract consumes that filename. Translate external `CONTEXT.md`
wording to the active local glossary surface before writing.

## Term Rules

- Be opinionated. When multiple words exist for the same concept, pick one canonical term and list the others as aliases to avoid.
- Flag conflicts explicitly. If a term is ambiguous, add it to `Flagged Ambiguities` with a clear resolution.
- Keep definitions tight: one or two sentences, defining what the term is rather than what it does.
- Show relationships. Use bold term names and express cardinality where obvious.
- Include only concepts specific to this project's context. General programming concepts do not belong just because the project uses them.
- Group terms under subheadings when natural clusters emerge. Use a flat list when all terms belong to one cohesive area.
- Write an example dialogue between a developer and a domain expert that demonstrates how terms interact and clarifies boundaries between related concepts.
- Preserve the principle behind corrective feedback independently of the local example that revealed it.

## Safety

- Do not copy raw private transcripts, secrets, tokens, or unnecessary personal data.
- Do not overwrite an existing glossary wholesale.
- Ask before finalizing a material policy or scope decision that cannot be inferred.
- Mark low-confidence terminology choices.

## Execution Boundaries

- Read only the current conversation, active instruction files, existing ubiquitous-language files, and directly relevant project docs unless the user asks for history-backed vocabulary.
- Write only the active ubiquitous-language file, context map, and the smallest necessary agent-instruction pointer.
- Do not run network commands, publish artifacts, change runtime projections, or edit unrelated docs for a terminology-only update.
- Do not infer domain authority from generic code symbols; require project-specific source evidence or user wording before adding a term.
- Do not use this skill for ordinary symbol renaming, generic copyediting, or broad documentation rewrites without reusable terminology.
- Do not create ADRs, Linear notes, `.harness/decisions/**`, or architecture
  artifacts from this skill. Hand off to the repo's decision-record or
  architecture workflow after the terminology question is resolved.

## Failure Mode

If the scope, source glossary, or authority for a terminology change is unclear, stop with one missing input rather than rewriting vocabulary by guesswork.

## Validation

Confirm the active glossary exists, every canonical term has a one- or
two-sentence definition, aliases to avoid are listed for terms with competing
names, flagged ambiguities include a resolution, prompt translations include at
least one user phrase when informal wording exists, and the agent instruction
pointer references the active ubiquitous-language file. For corrective feedback,
also confirm the intent radius, generalized rule, searched scope, similar-case
dispositions, and enforcement decision are explicit; a local-only result must be
supported by the pattern sweep rather than assumed from the named example. Fail
fast: stop at the first failed gate and do not proceed until the blocker is fixed.

## References

Never drop required context for brevity; move it into references or deferred context and link it here.

- Local contract, evals, and task profile: `references/`
- Output template: [references/output-format.md](references/output-format.md)
- Domain-grill procedure: [references/domain-grill.md](references/domain-grill.md)
- Archived long-form workflow: `Infrastructure/references/deferred-skill-context/agent-ops-ubiquitous-language/`

## When to use

Use this skill when a named concept, boundary, or domain term is ambiguous across source, tests, interfaces, or operator language and a governed vocabulary decision is required.

## Required Inputs

Provide the target repository or product surface, the terminology under review, authoritative sources where available, and the intended consumer of the resulting vocabulary decision.

## Gotchas

Do not turn one naming preference into a global rule without an independent pattern sweep. Keep generated text, retrospective evidence, and user terminology distinct from canonical domain authority, and stop when ownership or approval is missing.
