# he-spec Mode Rules

Read when: choosing whether to write, revise, deepen, or skip a spec.

## Source Ladder

Use the strongest available source: active Linear issue and parent/child context; current tracked spec by frontmatter, issue key, branch, or explicit path; explicit brainstorm, QA report, UI source, or parent spec; normalized session-collector evidence; matching repo specs; raw feature description.

Separate the current active source from a merely latest-dated artifact before drafting.

## Mode Selection

Use `standard-spec` for system, service, workflow, backend, full-stack, plugin, CLI, or behavior contracts. Use `dedicated-ui-spec` when component inventory, states, tokens, accessibility, responsive behavior, and visual acceptance criteria matter. Use `spec_depth: none` only when overhead outweighs value and the user did not explicitly ask for a spec; explicit `he-spec` requests still get the smallest useful contract. Use `lite` for medium-risk multi-module or integration work; use `full` for services, daemons, state machines, agent behavior, data integrity, security, concurrency, or multiple recovery paths.

## Revision And Deepening

Use folded `he-deepen-spec` behavior when an existing spec has contradictions, vague acceptance criteria, unclear source parity, missing failure/observability/validation behavior, or targeted-confidence review needs.

For revisions, emit complete replacement sections or a complete replacement artifact. Do not hand `he-plan` a pile of deltas that require interpretation.
