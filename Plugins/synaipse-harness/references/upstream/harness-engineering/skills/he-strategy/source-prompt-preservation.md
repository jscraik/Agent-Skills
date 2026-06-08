# Source Prompt Preservation

This reference preserves the behavioral intent of the original user-proposed
strategy prompts without loading the full prompt text into `SKILL.md`.

## Covered Prompt Families

Covered families: repo intent/strategy, architecture review, structural triage,
repo cognition pipeline, strategic/decision/core compression.

These are modes inside `he-strategy`, not separate top-level skills. When the
user asks for intent, architecture review, and triage together, use
`repo-cognition-pipeline` and load `repo-cognition-pipeline.md`.

For equivalence checks, load
`Plugins/synaipse-harness/references/upstream/harness-engineering/source-prompt-coverage-contract.md`;
matching artifact names alone do not prove coverage.

## Preserved Requirements

- infer intent from implementation reality, not marketing language
- compare docs/prompts/product intent with code-implied intent; report
  alignment, contradiction, and missing proof
- inspect relevant source, configs, CI, tests, docs, prompts, skills, hooks,
  integrations, governance, memory, and context systems
- separate verified facts, strong inferences, weak assumptions, and speculation
- ask focused clarification questions only when ambiguity materially affects
  architecture, moat, governance, or agent workflow direction
- evaluate agent-native design, determinism, context, governance, validation,
  observability, typed boundaries, security, CI/CD, composability, resilience
- explicitly pressure-test moat claims and false sophistication
- define drift indicators and measurable anti-drift signals where possible
- for structural triage, consume prior intent/review artifacts without repeating
  them; compress findings into leverage, deletion candidates, priorities,
  non-negotiables, future-agent guidance, route, and `Do Not Create`
- generate only high-value ADRs and only durable core invariant files
- prevent ADR, governance, and artifact explosion
- include an Evidence & Traceability Matrix for durable artifacts
- for post-write review loops, save first, use `request_user_input` when
  available, apply material corrections, and record `post_artifact_review_status`
- record source prompt family coverage, evidence depth, coverage gaps,
  not-inspected surfaces, authority limits, original prompt coverage, and
  downstream confidence when comparing against an original prompt method

## Compression Rule

The original prompts are intentionally strong and skeptical. Preserve that
stance, but compress output to what the selected mode needs. Do not turn every
review observation into a work item, ADR, core rule, or Linear issue.

## Authority Rule

Feature, review, triage, and strategy documents are secondary context. ADRs and
core invariants may carry policy or decision weight, but implementation still
requires admission through an execution slice.

If coverage is `partial`, `weak`, `sampled`, or `unknown`, do not use the
artifact as repo-wide authority without a deeper refresh.
