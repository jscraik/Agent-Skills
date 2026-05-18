# HE Ideation Mode

Folded `he-ideate` mode is served by `he-brainstorm`. Use it when the user asks
for options, improvement ideas, surprising directions, or "what should we
change" before one idea is ready for requirements brainstorming.

Do not use this mode for an already selected idea, an approved spec, a delivery
plan, or implementation. Route those to `he-brainstorm`, `he-spec`, `he-plan`,
or `he-work` as appropriate.

## Valid Imported Patterns

These patterns are valid for Harness Engineering:

- Identify the subject first. If the request is only "improvements", "ideas",
  "quick wins", or another catch-all phrase, ask what the agent should ideate
  about before generating candidates.
- Resume recent `.harness/ideate/**.md` artifacts when the topic overlaps,
  instead of creating duplicate ideation records.
- Ground before ideating. Use repo files, Linear state, session evidence,
  existing `.harness` artifacts, or explicitly supplied context before naming
  options.
- Run web research by default for `he-ideate` unless the user says to skip
  external research. Record whether web research ran, was skipped, or was
  unavailable.
- Generate many candidates internally, then critique all of them. Surface only
  the strongest survivors.
- Every survivor needs a basis tagged as `direct`, `repo`, `external`, or
  `reasoned`. No basis means the idea is rejected.
- For broad subjects, decompose the topic into 3-5 plain-language axes so
  survivors do not all cluster on the same surface.
- Include a rejection summary. The user should be able to see what was cut and
  why.
- Treat ideation as complete in conversation unless the user asks to save,
  hand off, or continue into brainstorming.

This file also preserves the compact entrypoint meaning that was expanded for
folded ideation mode:

```text
Explore first; separate evidence from guesses; before writing durable docs
choose the routed `.harness` path from the artifact routing contract; for
durable tracked work resolve/create the Linear issue before handoff; in
coding-harness-managed repos load the command bridge and record the Harness
transition.
```

These patterns are not valid defaults for Harness Engineering:

- Large fixed multi-agent fan-out. Use HE subagent policy only when the idea
  surface is large enough to justify it.
- Proof-specific persistence. HE durable artifacts live under `.harness`.
- Non-software universal ideation branches unless the user explicitly asks HE
  to reason about a non-engineering decision.

## Flow

1. Check whether the subject is identifiable.
2. Check `.harness/ideate/` for a recent overlapping artifact before creating a
   new one.
3. Classify the focus as repo, Linear, workflow, product, operations, content,
   or mixed. Keep the label internal unless it clarifies the handoff.
4. Build a short grounding summary from the smallest relevant repo, Linear,
   session, and `.harness` evidence set.
5. Run web research for current external context unless the user said "no
   external research", "skip web research", or equivalent. If web research
   fails, note it as unavailable and continue from internal grounding; do not
   mark external evidence as present.
6. If the subject is broad, name 3-5 axes in the topic's own language.
7. Generate candidates internally across different lenses: pain, removal,
   assumption break, leverage, analogy, and constraint flip.
8. Reject weak candidates with one-line reasons.
9. Present 2-7 survivors with title, description, axis when used, basis,
   rationale, downside, confidence, complexity, and next HE route.
10. Save only when asked or when a tracked HE handoff needs a durable artifact.

## Survivor Basis

Use one basis tag per survivor:

- `direct`: explicit user statement, Linear text, artifact line, or quoted
  source material.
- `repo`: observed repository structure, command output, tests, code, docs, or
  `.harness` evidence.
- `external`: current external research or named prior art.
- `reasoned`: a written first-principles argument grounded in the known
  constraints.

Reject ideas with vague basis language such as "could help", "best practice",
or "might improve things" unless the rationale is made concrete.

## Artifact Shape

Default path:

```text
.harness/ideate/YYYY-MM-DD-<topic>-options.md
```

Use frontmatter:

```yaml
schema_version: 1
source: he-brainstorm
mode: he-ideate
created: YYYY-MM-DD
topic: <topic>
scope_tier: lightweight|standard|deep-feature|deep-product
next_stage: he-brainstorm|he-spec|he-plan|he-work|done|blocked
```

Required sections:

- Grounding Summary
- Web Research Status
- Topic Axes, or `Decomposition skipped` with reason
- Ranked Survivors
- Rejection Summary
- Handoff Recommendation

## Handoff

Route one selected survivor to `he-brainstorm` when the idea still needs
requirements meaning, tradeoff definition, or success criteria. Route directly
to `he-spec` only when the selected idea is already clear enough for acceptance
criteria. Do not route from ideation straight to `he-plan` or `he-work` unless
an approved spec or execution slice already exists.
