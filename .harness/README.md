# Harness Local Document Routing

This directory contains local Harness Engineering planning, routing, evidence,
and scratch artifacts for this checkout. Treat it as an execution control
surface, not as the canonical product documentation set.

## Routing Rules

- Use `.harness/linear/` for local plans that have been reconciled with live
  Linear issues.
- Use `.harness/reframes/` for approved problem reframes that feed an
  implementation plan.
- Use `.harness/refactors/` for refactor planning artifacts that are not live
  Linear execution handles by themselves.
- Use `.harness/media/` for generated prompts, diagrams, and explanatory
  artifacts. These are supporting references, not execution plans.
- Use `.harness/memory/LEARNINGS.md` for durable learned-fix entries that
  should affect future agent behavior.
- Do not treat generated artifacts under `Infrastructure/artifacts/**` as
  active plans unless a routed plan links to the exact artifact.

## Active Local Plans

| Local document | Live Linear owner | Live status checked | Route |
| --- | --- | --- | --- |
| `.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md` | JSC-329 | 2026-05-18: Triage, no project, no assignee | Primary Skill SDK RF-1 execution handle. Complete before broader SDK, installer, or control-plane work expands. |
| `.harness/linear/2026-05-11-agent-skills-he-product-front-door-runtime-contract-linear-plan.md` | JSC-305 with JSC-306..JSC-310 | 2026-05-18: unstarted project lane | Adjacent HE runtime/front-door lane. Do not use it to preempt Skill SDK RF-1 unless the RF-1 implementation explicitly needs HE front-door proof. |

## Skill SDK Sequencing

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

## Known Local Gaps

- `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md` is referenced
  by the Skill SDK reframe and Linear plan, but is not present in this checkout
  as of 2026-05-18. Do not use that missing path as current evidence until the
  strategy is restored or the reference is replaced with an existing canonical
  source.
- `Infrastructure/references/skills-sdk-apparatus-lens.md` is also referenced
  by the Skill SDK plan, but is not present in this checkout as of 2026-05-18.
  Treat apparatus-lens signoff as blocked until the reference is restored or
  replaced with an existing validation contract.
- This checkout is behind `origin/main` at the time of routing. Refresh remote
  state before closing or archiving plans.

## Closeout Rule

Before closing a local plan, compare it against live Linear, update this routing
index, and record exact validation evidence. If live Linear and the local plan
disagree, mark the local plan as stale or blocked instead of silently choosing
one truth surface.
