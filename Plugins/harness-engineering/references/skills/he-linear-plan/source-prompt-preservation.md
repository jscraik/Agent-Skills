# Source Prompt Preservation

This reference preserves the behavior of the original user-proposed Linear
Execution Orchestration Prompt.

When a Linear plan consumes artifacts produced from an original prompt
comparison, also load
`Plugins/harness-engineering/references/source-prompt-coverage-contract.md`.
Linear plans must inherit upstream source-prompt coverage limits instead of
turning partial cognition into broad execution authority.

## Preserved Requirements

- read `.harness/features`, `.harness/review`, `.harness/triage`,
  `.harness/strategy`, `.harness/core`, `.harness/decisions`, and
  `.harness/reframes`
- read `.harness/refactors/**` as legacy reframe-program input when present;
  translate it into current `.harness/reframes/**` semantics and do not create
  new legacy refactor-root artifacts from this skill
- treat `.harness/decisions` as compressed architecture memory, not backlog
  input; if high-value ADRs are missing, mark decision readiness blocked or
  route to the upstream decision-compression step
- treat `.harness/core` as compressed invariant memory, not a Linear-plan output
  root; if architecture, routing, execution, governance, cognition, moat,
  anti-drift, or future-agent operating invariants are missing, mark core
  readiness blocked or `upstream_required` and route to `he-strategy` or
  `he-reframe`
- generate `.harness/linear/**` execution plans
- prefer dated Linear filenames for new plans
- use the existing JSC operating model when the request or artifacts confirm
  Jamie/JSC-managed work:
  - Workspace/team: Jscraik
  - Team key: JSC
  - Top-level initiative: Dev Portfolio
- Cross-repo control project: Portfolio Ops
- Repo-specific work: matching repo project
- mark `needs_human_triage` instead of assuming JSC values when the Linear
  workspace, team, initiative, project, or repo route cannot be proven
- do not create new initiatives or projects by default
- carry repo-specific identity with a repo/location label, preferably
  `Repo › ...`; legacy plain repo labels remain valid until migrated
- route repo-specific execution into the matching live repo control project
  when confirmed; use milestones and parent issues to keep the active slice
  bounded
- use projects only when they are live repo control surfaces, bounded
  deliverables, or cross-repo coordination containers with clear completion
  states
- leave project empty for speculative, exploratory, maintenance, operational
  debt, or ungrouped repo-owned work
- route cross-repo bounded deliverables to an appropriate project only when
  coordination, delivery tracking, or execution spanning multiple work items
  requires it
- keep active sets intentionally small
- use milestones for bounded execution slices
- use cycles only for current execution commitment
- classify work as `Now`, `Next`, `Later`, or `Do Not Create`
- convert reframe programs into minimal parent/sub-issue structures
- include validation gates, rollback conditions, dependency maps, labels,
  priority, and human/agent execution routing
- use existing labels first; propose new labels only when repeated work cannot
  fit existing Developer Experience, Reliability, Governance, Automation, type,
  roadmap, repo/location, or policy labels without losing routing value
- do not mutate Linear without explicit confirmation
- preserve upstream evidence depth, coverage gaps, not-inspected surfaces,
  repo-specific drift signals, authority limits, and downstream confidence

## Real Output Patterns Observed

Existing repos have stable Linear summary files:

- `.harness/linear/agent-skills-linear-plan.md`
- `.harness/linear/coding-harness-linear-plan.md`

For new issue-linked plans, prefer dated Linear filenames:

- `.harness/linear/YYYY-MM-DD-JSC-###-agent-skills-linear-plan.md`
- `.harness/linear/YYYY-MM-DD-JSC-###-coding-harness-linear-plan.md`
- `.harness/linear/YYYY-MM-DD-JSC-###-agent-skills-<slice-slug>-linear-plan.md`
- `.harness/linear/YYYY-MM-DD-JSC-###-coding-harness-<slice-slug>-linear-plan.md`

Stable files can remain as living summary or legacy artifacts, but dated files
are better for regression detection and agentic search.

## Linear Explosion Guard

Do not create one issue per finding. Prefer one milestone and one parent issue
per coherent execution phase, with sub-issues only where work is independently
verifiable.

If upstream coverage is partial, sampled, weak, inferred, or unknown, keep the
Linear plan local to the selected slice and classify uninspected prompt-method
concerns as `Next`, `Later`, `Do Not Create`, or `Blocked` instead of treating
them as closed.

## ADR Readiness Guard

Do not turn the Architectural Decision Compression prompt into Linear backlog.
The ADR phase exists to preserve expensive-to-reverse reasoning and anti-drift
constraints. If the required ADR set is absent, noisy, duplicated, or merely
generic architecture prose, the Linear plan must say so and avoid promoting that
uncertain decision surface into active execution.

## Core Invariant Readiness Guard

Do not turn the Core Knowledge Compression prompt into a Linear backlog or a
`.harness/core/**` write. The core phase exists to preserve irreducible
architecture, routing, execution, governance, cognition, moat, anti-drift, and
future-agent operating invariants. If the required core invariant layer is
absent, noisy, generic, or unreviewed, the Linear plan must report
`core_artifact_status: upstream_required` or `blocked`, route the work to
`he-strategy` or `he-reframe`, and avoid promoting missing invariant reasoning
into active Linear objects.

## Confirmation Gate

The final workflow may ask for confirmation before creating or updating Linear
objects. Until that confirmation exists, output only the plan and ready-to-create
payloads.

When `request_user_input` is available, use it for the post-plan confirmation
question before creating or updating Linear objects. When it is unavailable,
write `required_confirmation`, keep `linear_mutation_status:
confirmation_required`, and stop before live mutation.
