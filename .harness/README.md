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

1. JSC-329: register `skills doctor`, then prove the
   `skills doctor context7 --json --robot` contract for one representative
   skill. Current live CLI state as of 2026-05-20: `skills doctor` and
   `skills package` are not registered actions, so the first RF-1 proof is
   replacing the parser-level invalid-choice error with structured JSON.
2. RF-1 is additive: create `skills doctor` as a facade over existing
   `skills prove`, `skills proof`, `skills explain`, audit, and future
   package signals. Do not move or deprecate `prove`/`proof` in RF-1.
3. Bind RF-1 to
   `Infrastructure/config/schemas/skill-doctor.v1.schema.json` and require
   fixtures for `context7` plus one additional non-`context7` skill class.
4. Split validation into phase A registration proof and phase B contract proof;
   phase B gates are not runnable until phase A proves the command dispatches.
5. RF-2: create the negative-path readiness matrix only after JSC-329 closes
   with evidence.
6. Keep the SDK agent-native: command JSON, schemas, fixtures, eval artifacts,
   lifecycle events, and harness consumer tests are source of truth. Human
   docs are thin summaries of those contracts, not independent requirements.
7. Make skills improve through eval feedback loops: eval outcomes create
   classified learning records, bounded skill updates, fixture changes,
   rerun proof, and promotion or rollback evidence.
8. Use a terminology flywheel: controlled SDK terms from real use and evals
   must be encoded back into command JSON, schemas, fixtures, eval labels, and
   reports so future agents classify the same pattern consistently.
9. Post-RF-1 SDK package-doctor slice: use the 2026-05-19 Codex upstream
   runtime-contract research as input for skills package-doctor <skill>,
   including package layout, namespaces, permission deny, enablement states,
   lifecycle events, provenance, additive upgrades, and execution context.
10. JSC-230 family: keep commandable rooted handles bounded to command-surface
   reliability.
11. JSC-246 and broader golden paths: consume the stable doctor contract after
   RF-1, not before.
12. Installer and skill-builder gates such as JSC-142, JSC-143, JSC-146, and
   JSC-147: sequence after doctor/package/proof semantics are stable.

### Known Local Gaps

- `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md`,
  `Infrastructure/references/skills-sdk-apparatus-lens.md`, and
  `Infrastructure/config/schemas/skill-doctor.v1.schema.json` are now the
  thin authority set for RF-1. Do not add broader human-facing docs unless they
  reconcile executable contracts.
- `./bin/ask skills doctor context7 --json --robot` and
  `./bin/ask skills package context7 --json --robot` both exit 2 with parser
  invalid-choice errors as of 2026-05-20. Do not describe either command as a
  live readiness baseline until the CLI registration and dispatch path are
  implemented and tested.
  JSC-329 should therefore begin with a public facade decision: either add
  skills doctor over the existing prove/proof/explain surfaces, or retitle RF-1
  around the existing prove contract and defer doctor/package semantics.
- The same unknown-action error guidance currently mentions `external-review`
  in its suggested valid actions even though `./bin/ask skills --help` and the
  parser choices do not list that action. Treat parser/help output as the live
  source of truth until the guided-error text is reconciled.

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
