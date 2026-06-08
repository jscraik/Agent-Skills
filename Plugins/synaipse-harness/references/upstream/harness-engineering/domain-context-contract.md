# Domain Context Contract

Read when: Harness Engineering work depends on project terminology, cross-artifact meaning, external review/log input, or a handoff between Linear, specs, plans, PRs, validation, Project Brain, heartbeats, goals, or session evidence.

This contract translates domain-driven design practices into agent-native HE checks. Use it to preserve meaning without expanding every active `SKILL.md`.
For production-sensitive behavior, pair this vocabulary layer with
`domain-model-production-contract.md` so term stability is checked against
Production Model Integrity, bounded context ownership, and aggregate invariants.

## Core Rule

HE stages preserve intent by translating between bounded contexts, not by copying wording blindly. A stage that changes or consumes domain meaning must name the source context, translation, conflict status, and next owner before handing off.

## Domain Language Envelope

Use this envelope when terminology affects behavior, acceptance criteria, tracker wording, code names, review findings, or user expectations:

```yaml
domain_language:
  status: stable|ambiguous|conflicted|not_applicable
  canonical_terms: []
  avoided_aliases: []
  unresolved_terms: []
  language_file: UBIQUITOUS.md|UBIQUITOUS-MAP.md|domain-context-contract.md|legacy_CONTEXT.md|not_applicable
```

Stage guidance:

- `he-brainstorm`: surface fuzzy terms, avoided aliases, and the question that will settle meaning. In `domain_interview` mode, use `request_user_input` for one bounded branch question at a time when available and update the owning ubiquitous language file as soon as a glossary term is resolved.
- `he-spec`: lock canonical terms into behavior, acceptance IDs, and non-goals.
- `he-plan`: preserve canonical terms in plan units without renumbering source IDs.
- `he-work`: stop when implementation reveals term drift and update the owning artifact before coding past it.
- `he-code-review`: flag code, docs, spec, plan, or Linear term drift before readiness synthesis.
- `he-reconcile`: reconcile stale or conflicting lifecycle artifacts before selecting the next stage.
- `he-reinforce`: capture verified solved-problem learning or refresh stale learning artifacts after evidence is proven.

## Context Map Envelope

Use this compact context map when HE state moves between artifacts:

```yaml
context_map:
  source_of_truth: user_request|linear|spec|plan|worktree|pr|validation|project_brain|heartbeat|goal|session_evidence|not_applicable
  translated_from: []
  relationship: source_of_truth|translation|handoff|evidence_only|stale_snapshot|not_applicable
  conflict_status: none|blocked|resolved|not_applicable
  conflict_rule: stop|refresh|prefer_source|record_blocker|not_applicable
```

Default conflict rules:

- Prefer the freshest owning artifact for the current stage.
- Treat session memory and old summaries as evidence labels until refreshed.
- Stop when Linear, spec, plan, or PR names disagree about behavior and the disagreement changes acceptance or implementation.
- Record the smallest refresh command, artifact path, or user question when a context cannot be reconciled.

## Anti-Corruption Translation

External or neighboring models must be translated before they change HE artifacts:

| Input model | Translate into | Do not treat as |
| --- | --- | --- |
| User shorthand | canonical HE task, stage, and missing evidence | direct implementation permission |
| Linear issue wording | tracker contract and acceptance source | complete spec by itself |
| CodeRabbit/Codex/human review | finding, disproven signal, deferred item, or HE follow-up | unquestioned blocker |
| CI or test log | reproduced failure, blocker, or validation evidence | root cause without reproduction |
| Session evidence | bounded evidence label with freshness | current repository truth |
| External source material | invariant, eval, contract field, reference, or explicit rejection | pasted doctrine |

## Core Domain

The HE core domain is preserving intent, evidence, and lifecycle truth across agent work. Protect these concepts first:

- stage boundary
- source traceability
- evidence freshness
- acceptance IDs
- validation evidence
- tracker state
- blackboard delta
- blocked exit
- next stage
- domain language and term drift
- ubiquitous language file ownership
- Production Model Integrity
- aggregate invariants

Supporting docs, examples, reviewer fanout, and implementation sketches are secondary. Move them to references or artifacts when context pressure rises.

## Completion Check

Before a domain-sensitive HE handoff, verify:

- canonical terms and avoided aliases are recorded or marked not applicable;
- the relevant `UBIQUITOUS.md`, `UBIQUITOUS-MAP.md`, or legacy context evidence
  is named;
- source context and target context are explicit when artifacts disagree;
- conflict resolution is `resolved`, `blocked`, or `not_applicable`;
- external inputs have been translated through the anti-corruption table;
- the next stage knows the owning artifact and smallest refresh step.
