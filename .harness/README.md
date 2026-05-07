# Harness Control Plane

`.harness` stores repo-specific Harness context. Track curated policy, decision,
execution, and review documents; keep local runtime output out of git.

## Tracked Surfaces

| Path | Classification | Authority |
| --- | --- | --- |
| `.harness/core/**.md` | policy | Non-negotiable repo invariants and operating rules. |
| `.harness/decisions/**.md` | policy/reference | Architecture decisions and tradeoffs. |
| `.harness/linear/**.md` | execution-input | Approved Linear destination, milestone, issue, priority, labels, dependencies, and execution route. |
| `.harness/refactors/**.md` | execution-input | Selected refactor or migration route, rollback rules, and anti-regression constraints. |
| `.harness/ideate/**.md` | lifecycle-artifact | Durable HE ideation output. |
| `.harness/brainstorm/**.md` | lifecycle-artifact | Durable HE brainstorm output. |
| `.harness/specs/**.md` | lifecycle-artifact | Durable HE spec output. |
| `.harness/plan/**.md` | lifecycle-artifact | Durable HE plan output. |
| `.harness/plan/**-ui-plan.md` | lifecycle-artifact | Dedicated UI implementation plans owned by `he-plan`. |
| `.harness/solutions/**.md` | lifecycle-artifact/reference | Verified reusable HE solution captures owned by `he-compound`. |
| `.harness/knowledge/**` | reference/policy | Project Brain knowledge synced from accepted solution captures and repo decisions. |
| `.harness/features/**.md` | secondary-context | Repo intent and feature guardrails. |
| `.harness/strategy/**.md` | secondary-context | Strategy and moat rationale. |
| `.harness/triage/**.md` | secondary-context | Prioritization and discarded paths. |
| `.harness/review/**.md` | secondary-context | Review evidence and critique. |
| `.harness/memory/LEARNINGS.md` | reference | Repo-local learned fixes and recurring operational knowledge. |
| `.harness/quality/**` | policy | Quality criteria and scorecards. |
| `.harness/*.json` | policy/generated-tracked | Contract JSON consumed by repo validators or Harness setup flows. |

Secondary context is not execution authority by itself. Implementation work must
be admitted by the selected `.harness/linear/**` or `.harness/refactors/**`
slice before `he-spec`, `he-plan`, or `he-work` can use it as scope.

For Linear-backed work, `.harness/linear/<repo-name>-linear-plan.md` should also
carry the live-delta boundary:

- `Approved Current Slice`: the single milestone, parent issue, refactor phase,
  or execution slice available to the next HE stage.
- `Linear Delta Capture`: new or changed Linear issues classified as
  `already_covered`, `duplicate_or_superseded`, `candidate_next_slice`,
  `blocker_for_current_slice`, `out_of_scope`, or `needs_human_triage`.
- `Label status`: confirmation that required Linear labels already exist, were
  created from approved reusable categories, or are blocked with a
  ready-to-create payload.
- `Approved Next Slice Queue`: ordered candidates admitted by the plan for the
  next bounded plugin HE spec, plan, or work pass.

New Linear issues do not drive implementation directly until this plan admits
one of them into the current slice or next-slice queue.

Legacy `docs/solutions/**`, `docs/ui-plan/**`, and `docs/ui-plans/**` may be
read as source evidence. New HE solution captures should use
`.harness/solutions/**`; new dedicated UI plans should use
`.harness/plan/**-ui-plan.md`.

When Project Brain is active, accepted solution captures feed
`.harness/knowledge/<domain>/knowledge.md` as reusable solved knowledge. UI
plans feed Project Brain as plan/decision context first and are promoted to
solution knowledge only after implementation or review proves a reusable
pattern.

## Ignored Surfaces

| Path | Classification | Rule |
| --- | --- | --- |
| `.harness/backups/**` | backup/scratch | Do not track. |
| `.harness/*.db` | runtime_state | Do not track unless moved under fixtures with a documented consumer. |
| `.harness/ci-migrate-snapshots/**` | historical_artifact | Do not track by default; preserve summaries or fixtures only. |

When a new `.harness` path appears, classify it before staging it. If the path is
not clearly policy, reference, execution input, lifecycle artifact, fixture, or a
tracked contract JSON file, keep it local until ownership is resolved.
