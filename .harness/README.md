# Harness Control Plane

`.harness` stores repo-specific Harness context. Track curated policy, decision,
execution, and review documents; keep local runtime output out of git.

## Tracked Surfaces

| Path | Classification | Authority |
| --- | --- | --- |
| `.harness/core/**.md` | policy | Non-negotiable repo invariants and operating rules. |
| `.harness/decisions/**.md` | policy | Architecture decisions and tradeoffs with execution authority when intentionally indexed. |
| `.harness/linear/**.md` | policy | Approved Linear destination, milestone, issue, priority, labels, dependencies, and execution route. |
| `.harness/refactors/**.md` | policy | Selected refactor or migration route, rollback rules, and anti-regression constraints. |
| `.harness/ideate/**.md` | reference | Durable HE ideation output used as non-authoritative context. |
| `.harness/brainstorm/**.md` | policy | Durable HE brainstorm output with execution authority when admitted by slice. |
| `.harness/specs/**.md` | reference | Durable HE spec output. |
| `.harness/plan/**.md` | reference | Durable HE plan output. |
| `.harness/plan/**-ui-plan.md` | reference | Dedicated UI implementation plans owned by `he-plan`. |
| `.harness/solutions/**.md` | policy | Verified reusable HE solution captures owned by `he-compound`. |
| `.harness/knowledge/**` | reference | Project Brain knowledge synced from accepted solution captures and repo decisions. |
| `.harness/features/**.md` | reference | Repo intent and feature guardrails as secondary context. |
| `.harness/strategy/**.md` | reference | Strategy and moat rationale as secondary context. |
| `.harness/triage/**.md` | reference | Prioritization and discarded paths as secondary context. |
| `.harness/review/**.md` | reference | Review evidence and critique as secondary context. |
| `.harness/memory/LEARNINGS.md` | reference | Repo-local learned fixes and recurring operational knowledge. |
| `.harness/quality/**` | policy | Quality criteria and scorecards. |
| `.harness/evals/**.md` | intentional_archive | Harness engineering eval reports and execution evidence. |
| `.harness/media/**.md` | intentional_archive | Prompt metadata and sidecar evidence artifacts (including blocked media attempts such as `2026-05-10-he-fix-bugs-codex-harness-skill.md`) kept for auditability. |
| `.harness/session-evidence/**` | intentional_archive | Deterministic command snapshots and session evidence bundles for harness engineering closure proof. |
| `.harness/*-contract.json` | policy | Contract JSON consumed by repo validators or Harness setup flows. |
| `.harness/*-generated.json` | generated_tracked | Generated contract JSON tracked for downstream consumers. |

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

## Active Local Routing Overlay

These entries are currently singled out because they bridge local planning,
Linear state, and Skill SDK execution order.

| Local document | Live Linear owner | Live status checked | Route |
| --- | --- | --- | --- |
| `.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md` | JSC-329 | 2026-05-18: Triage, no project, no assignee | Primary Skill SDK RF-1 execution handle. Complete before broader SDK, installer, or control-plane work expands. |
| `.harness/linear/2026-05-11-agent-skills-he-product-front-door-runtime-contract-linear-plan.md` | JSC-305 with JSC-306..JSC-310 | 2026-05-18: unstarted project lane | Adjacent HE runtime/front-door lane. Do not use it to preempt Skill SDK RF-1 unless the RF-1 implementation explicitly needs HE front-door proof. |

### Skill SDK Sequencing

The current Skill SDK route is:

1. JSC-329: prove the `skills doctor context7 --json --robot` contract for one
   representative skill.
2. RF-2: create the negative-path readiness matrix only after JSC-329 closes
   with evidence.
3. JSC-230 family: keep commandable rooted handles bounded to command-surface
   reliability.
4. JSC-246 and broader golden paths: consume the stable doctor contract after
   RF-1, not before.
5. Installer and skill-builder gates such as JSC-142, JSC-143, JSC-146, and
   JSC-147: sequence after doctor/package/proof semantics are stable.

### Known Local Gaps

- `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md` is referenced
  by the Skill SDK reframe and Linear plan, but is not present in this checkout
  as of 2026-05-18. Do not use that missing path as current evidence until the
  strategy is restored or the reference is replaced with an existing canonical
  source.
- `Infrastructure/references/skills-sdk-apparatus-lens.md` is also referenced
  by the Skill SDK plan, but is not present in this checkout as of 2026-05-18.
  Treat apparatus-lens signoff as blocked until the reference is restored or
  replaced with an existing validation contract.

## Ignored Surfaces

| Path | Classification | Rule |
| --- | --- | --- |
| `.harness/backups/**` | backup/scratch | Do not track. |
| `.harness/*.db` | runtime_state | Do not track unless moved under fixtures with a documented consumer. |
| `.harness/ci-migrate-snapshots/**` | historical_artifact | Do not track by default; preserve summaries or fixtures only. |

When a new `.harness` path appears, classify it before staging it. Use canonical
ownership classes: `source`, `fixture`, `policy`, `reference`,
`intentional_archive`, `generated_tracked`, `generated_ignored`,
`runtime_state`, `historical_artifact`, or `unknown`. Keep authority semantics
in the Authority column and keep unresolved ownership local until classified.

## Closeout Rule

Before closing a local plan, compare it against live Linear, update the routing
surface that owns the active slice, and record exact validation evidence. If
live Linear and the local plan disagree, mark the local plan as stale or blocked
instead of silently choosing one truth surface.
