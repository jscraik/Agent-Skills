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
  `.harness/refactors`
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
- use projects only for bounded deliverables with clear completion states
- leave project empty for speculative, exploratory, maintenance, operational
  debt, or ungrouped repo-owned work
- route cross-repo bounded deliverables to an appropriate project only when
  coordination, delivery tracking, or execution spanning multiple work items
  requires it
- keep active sets intentionally small
- use milestones for bounded execution slices
- use cycles only for current execution commitment
- classify work as `Now`, `Next`, `Later`, or `Do Not Create`
- convert refactor programs into minimal parent/sub-issue structures
- include validation gates, rollback conditions, dependency maps, labels,
  priority, and human/agent execution routing
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

## Confirmation Gate

The final workflow may ask for confirmation before creating or updating Linear
objects. Until that confirmation exists, output only the plan and ready-to-create
payloads.
