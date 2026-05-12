# Source Prompt Preservation

This reference preserves the behavioral intent of the original user-proposed
strategy prompts without loading the full prompt text into `SKILL.md`.

## Covered Prompt Families

- Repository Intent Extraction + Strategic Review
- Multi-Disciplinary Architecture & Skill Review
- Structural Triage & Execution Prioritization
- Full Repository Cognition Pipeline: intent + architecture review + triage
- Strategic Compression & Direction
- Architectural Decision Compression
- Core Knowledge Compression & Architectural Invariants

These are modes inside `he-strategy`, not separate top-level skills. When the
user asks for intent, architecture review, and triage together, use
`repo-cognition-pipeline` and load `repo-cognition-pipeline.md`.

When the user asks whether HE output is equivalent to one of these original
prompt workflows, load the shared source-prompt coverage contract at
`Plugins/harness-engineering/references/source-prompt-coverage-contract.md`.
Do not answer equivalence from the existence of matching artifacts alone.

## Preserved Requirements

- infer intent from implementation reality, not marketing language
- inspect repo source, configs, scripts, CI, tests, docs, prompts, skills,
  workflows, hooks, integrations, governance, memory, and context systems when
  relevant to the selected mode
- separate verified facts, strong inferences, weak assumptions, and speculation
- ask focused clarification questions only when ambiguity materially affects
  architecture, moat, governance, or agent workflow direction
- evaluate agent-native design, deterministic execution, context management,
  repository cognition, governance, validation loops, observability, typed
  boundaries, maintainability, security posture, CI/CD maturity, prompt/skill
  composability, operational resilience, and dependency discipline when relevant
- explicitly pressure-test moat claims and false sophistication
- define drift indicators and measurable anti-drift signals where possible
- compress findings into leverage, deletion candidates, safe rewrite zones,
  strategic priorities, non-negotiables, and future-agent guidance
- generate only high-value ADRs and only durable core invariant files
- prevent ADR, governance, and artifact explosion
- include an Evidence & Traceability Matrix for durable artifacts
- record source prompt family coverage, evidence depth, coverage gaps,
  not-inspected surfaces, authority limits, original prompt coverage, and
  downstream confidence when comparing against an original prompt method

## Real Output Patterns Observed

The current repos use both legacy stable names and dated Linear names:

- `.harness/features/agent-skills-intent.md`
- `.harness/review/2026-05-08-JSC-283-...-technical-review.md`
- `.harness/specs/2026-05-08-jsc-283-packaged-skill-behavior-assurance-spec.md`
- `.harness/plan/2026-05-08-architecture-JSC-283-packaged-skill-behavior-assurance-plan.md`
- `.harness/solutions/2026-05-08-jsc-283-packaged-skill-behavior-proof.md`
- `.harness/strategy/agent-skills-strategy.md`
- `.harness/decisions/ADR-007-portable-skill-and-memory-proof.md`
- `.harness/core/architecture-invariants.md`

For new lifecycle artifacts, prefer dated Linear filenames because they improve
regression search, issue traceability, chronological review, and agentic
retrieval. Keep stable canonical filenames for living policy surfaces such as
core invariant files, and keep numbered ADR filenames for decision records.

## Compression Rule

The original prompts are intentionally strong and skeptical. Preserve that
stance, but compress output to what the selected mode needs. Do not turn every
review observation into a work item, ADR, core rule, or Linear issue.

## Authority Rule

Feature, review, triage, and strategy documents are secondary context. ADRs and
core invariants may carry policy or decision weight, but implementation still
requires admission through an execution slice.

If source-prompt coverage is `partial`, `weak`, `sampled`, or `unknown`, the
strategy artifact may still be useful as local cognition, but it must not be
used as repo-wide authority for refactor, Linear, ADR, core, or closure claims
without a deeper refresh.
