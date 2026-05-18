---
schema_version: 1
selected_stage: he-linear-plan
source_reframe: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
source_strategy: .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
source_strategy_status: missing_in_current_checkout
repo: agent-skills
slice: RF-1 doctor contract fixture for one skill
linear_mutation_status: created
live_linear_setup_status: partial
live_linear_checked_at: 2026-05-18
live_linear_current_status: Triage
live_linear_current_project: null
live_linear_current_assignee: null
linear_issue_id: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
label_status: partial
template_status: confirmation_required
decision_artifact_status: present
core_artifact_status: present
apparatus_lens_status: referenced_missing
apparatus_lens: Infrastructure/references/skills-sdk-apparatus-lens.md
apparatus_lens_file_status: missing_in_current_checkout
subagent_policy: not_used
roles_used: []
roles_recommended: [planning-specialist-agent, api-contract-reviewer, testing-reviewer]
roles_missing: []
---

# Agent Skills Kit Skill SDK Doctor Contract Linear Plan

## Command Summary

BLUF: This document's job is to convert RF-1 from the approved Skill SDK doctor-trust reframe into one live execution issue for Agent Skills Kit. It gives Jamie and future agents the Linear routing, scope, acceptance criteria, validation gates, rollback conditions, and evidence map for hardening ./bin/ask skills doctor context7 --json --robot as the first professional SDK readiness contract. The plan matters because the current baseline already separates runtime blockers, package metadata warnings, outcome proof gaps, operation context, lifecycle evidence, and safe next command, and the live issue is intentionally narrow so the SDK direction gets fixture-backed proof through the Skills SDK apparatus lens before broader package, harness, or marketplace work begins.

Decision Needed: Use the created Linear issue as the RF-1 execution handle, then plan RF-2 only after RF-1 closes with evidence.

Top Risks: Over-scoping RF-1 can turn a doctor fixture slice into a broad SDK rewrite; treating package warnings as runtime blockers would weaken the contract this issue is meant to prove; treating a polished skill artifact or AI review as readiness would bypass the verification apparatus; creating follow-on issues before RF-1 evidence would recreate backlog ceremony.

Next Action: Implement RF-1 against the live Linear issue after confirming the created issue routing is acceptable.

## Executive Linear Routing Summary

Classification: repo-specific implementation slice.

Selected slice: RF-1 from the SDK doctor-trust reframe.

Recommended action: use one live issue for RF-1. Do not create RF-2 through RF-6 yet.

Mutation status: created as JSC-329.

Live reconciliation, 2026-05-18: JSC-329 exists in Linear and remains in
Triage with no project assignment and no assignee. This matches the original
partial setup note. Treat JSC-329 as the active Skill SDK RF-1 execution handle,
but do not claim the local plan is fully routed until project assignment is
either intentionally left blank or updated in Linear.

## Target Linear Destination

- Team: Jscraik / JSC.
- Repo/location label: agent-skills was requested conceptually; exact label application depends on live label availability.
- Project: omitted unless Jamie confirms the exact healthy repo-control project.
- Cycle: empty.
- Initiative: empty.

live_linear_setup_status: partial.

live_linear_blocker: the issue was created without project assignment because exact repo-control project health and issue template IDs were not fully verified in this turn.

Live issue: JSC-329, https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7.

## Existing Project Match

- Project name: agent-skills repo control project.
- Live evidence source: not fully verified in this run.
- Status: partial.
- Duplicate or canceled alternatives: unknown.
- Mutation safety: one repo-scoped issue created without project assignment to avoid attaching to an unverified destination.

existing_project_match: partial.

## ADR / Decision Artifact Readiness

decision_artifact_status: present.

Evidence:

- Source strategy: .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
  (missing in the current checkout as of 2026-05-18; restore or replace before
  using it as live evidence)
- Source reframe: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
- Apparatus lens: Infrastructure/references/skills-sdk-apparatus-lens.md
  (missing in the current checkout as of 2026-05-18; apparatus signoff is
  blocked until restored or replaced with an existing validation contract)
- RF-1 is selected as the smallest reversible implementation slice.

## Core / Invariant Artifact Readiness

core_artifact_status: present.

Relevant invariants:

- Agent Skills Kit owns SDK contract shape and canonical skill source.
- Coding-harness consumes stable JSON contracts and must not parse skill internals.
- skills doctor composes readiness signals; it does not replace package, eval, audit, or lifecycle events.
- Jamie's mantra is the operating shape: Thin surface. Strong guardrails. Durable memory. Professional output.
- Skill readiness is trusted only to the degree that the verification apparatus signs off the exact claim: typed contract assertions, doctor/package/prove/eval commands, structural audits, representativeness probes, closeout validation, and rollback evidence.
- High-signal steering uptake is RF-0 and must remain a preflight gate.

## Proposed Milestones

No new milestone is required for RF-1.

## Proposed Parent Issues

Do not create a parent issue unless the full RF-1 to RF-6 program is promoted.

## Proposed Sub-Issues

### Issue 1: Harden skills doctor contract fixture for context7

template: Feature

issue_type: feature

priority: 2

repo_location_label: agent-skills

project_assignment_reason: bounded repo-specific implementation slice from an approved reframe.

cycle_assignment_reason: empty.

Objective: Harden the skills doctor JSON contract around context7 so Agent Skills Kit has a fixture-backed first proof point for professional Skill SDK readiness.

Source Artifacts:

- .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
  (referenced but missing in this checkout)
- .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
- .harness/quality/steering-uptake.md
- Infrastructure/references/skills-sdk-apparatus-lens.md
  (referenced but missing in this checkout)

Why This Matters: Agent Skills Kit is becoming a professional SDK of Codex skills. RF-1 proves the smallest readiness spine: doctor must expose stable fields, status precedence, and safe next action without confusing runtime blockers, package warnings, or outcome-proof gaps.

Scope:

- Add a focused doctor JSON contract fixture or snapshot for context7.
- Add tests asserting required fields: schema_version, status, target_summary, checks, blockers, warnings, operation_context, contract_schemas, agent_summary, and next_command.
- Assert status precedence: blocked outranks warning, warning outranks pass, and pass requires no blockers or warnings.
- Assert next_command is present for blocked, warning, and pass states, and is null only when no safe next command exists.
- Preserve separate reporting for runtime reachability, package readiness, and outcome proof.
- Capture before and after doctor output and document tolerated environmental differences such as trace IDs and timestamps.
- Map readiness claims to the apparatus that signs them off: typed field assertions, focused tests, doctor/package probes, structural audit, representativeness, changed-file validation, and rollback evidence.
- Include at least one counterexample-style assertion so malformed fields, skipped/not-run critical evidence, or blocker-first next_command drift cannot produce pass.
- Run one read-only representativeness check against an additional skill class selected during implementation.

Out of Scope:

- Broad SDK metadata migration.
- Publishing, sharing, or installing skills.
- Editing runtime projections by hand.
- Coding-harness consumer implementation.
- RF-2 negative-path matrix beyond the minimum needed to prove RF-1.

Execution Notes:

- Start with the current baseline: ./bin/ask skills doctor context7 --json --robot returns blocked_runtime with outcome_proof_missing warning.
- Use ./bin/ask skills package context7 --json --robot only as package-readiness comparison evidence.
- Keep RF-0 steering uptake validator passing before closeout.
- Do not treat package metadata gaps as runtime blockers.
- Do not claim outcome proof from package readiness.
- Do not claim readiness from source presence, package presence, AI review, or coherent prose unless the apparatus evidence is named.

Validation Gates:

- python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
- python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q
- ./bin/ask skills doctor context7 --json --robot
- ./bin/ask skills package context7 --json --robot
- Focused pytest for the new doctor contract fixture
- Apparatus signoff table in the eval or closeout artifact
- ./bin/ask repo validate --changed-files <changed-files> --json --robot

Rollback Conditions:

- Remove the RF-1 fixture and tests.
- Revert any doctor implementation changes introduced by RF-1.
- Verify post-rollback skills doctor context7 output matches the recorded pre-change snapshot except tolerated environmental fields.

Acceptance criteria:

- Doctor fixture asserts all required SDK readiness fields for context7.
- Status precedence is covered by tests or helper-level assertions.
- Runtime reachability, package readiness, and outcome proof remain separate in JSON output and agent summary.
- next_command contract is asserted for the observed blocked baseline and any warning/pass fixture used.
- Readiness claims cite command/test/audit/eval/probe/validation evidence rather than source presence, package presence, AI review, or prose alone.
- Counterexample-style coverage exists for malformed fields, critical skipped/not-run state, blocker-first next_command behavior, or second-skill representativeness.
- Before and after snapshots record tolerated dynamic fields.
- RF-0 steering uptake checks still pass.

## Now / Next / Later / Do Not Create

Now: implement RF-1 using the live Linear issue as the execution handle.

Next: RF-2 negative-path readiness matrix after RF-1 closes with evidence.

Later: RF-3 profile/freshness determinism; RF-4 coding-harness schema consumer boundary; RF-5 review feedback intent radius; RF-6 migration of high-value HE/factory skills.

Do Not Create: one issue per SDK field; a broad package metadata migration issue before RF-1 proves doctor contract value; a coding-harness implementation issue before Agent Skills Kit owns a stable fixture.

## Dependency Map

- RF-0 steering uptake environment gate must stay green before RF-1 closeout.
- RF-1 blocks RF-2, RF-4, and RF-6.
- RF-3 can start after RF-1 only if fixture ownership is clear.
- RF-4 must not start until Agent Skills Kit exposes stable doctor/package/profile/event schemas.

## Eval Gate Map

- RF-1 eval artifact target: .harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md
- Required evidence: baseline doctor output for context7; package-readiness comparison output for context7; doctor fixture test result; changed-file repo validation result; explicit blocked/warning/pass classification evidence or recorded coverage gap for unavailable classes.

## Human vs Agent Execution Map

Agent-safe: draft tests and fixtures; run doctor/package probes; run focused pytest and repo validation; update eval artifact and implementation notes.

Human review required: review any change that alters public doctor JSON semantics; decide whether RF-1 should be current-cycle work.

## Story / Value Basis

As Jamie, I need skills doctor to produce stable SDK-grade readiness evidence for one representative skill so future agents and harness workflows can trust the command before relying on broader skill readiness claims.

Feedback signal: the fixture either proves the current doctor contract is already close enough, or exposes exactly which fields and status rules need implementation hardening.

Risk reduction: avoids broad SDK ceremony before proving one command-backed readiness spine.

## Recommended Labels

Conceptual labels: agent-skills; Feature; Roadmap Next; Developer Experience; Governance; Reliability.

label_status: partial.

## Repo / Location Label

repo_location_label: agent-skills.

## Priority Mapping

Priority: 2 High.

Reason: RF-1 is a migration blocker for the professional Skill SDK direction and for reliable harness consumption of skill readiness.

## Project / Cycle Justification

project_assignment_reason: bounded deliverable from approved reframe; project omitted until exact healthy repo control project is confirmed.

cycle_assignment_reason: empty.

## Project Reactivation Recommendation

Do not reactivate or create projects from this plan. If the canonical agent-skills repo project is archived, canceled, duplicated, or trashed, block project assignment and ask Jamie to confirm the target.

## Portfolio Ops Items

No Portfolio Ops item is recommended for RF-1.

## Dev Portfolio Impact

This is repo-specific Agent Skills Kit execution work. It supports Dev Portfolio indirectly by improving skill readiness evidence, but it does not need an initiative-level mutation for RF-1.

## GitHub PR Tracking

github_tracking_rule: include the Linear issue identifier in the branch name, commit message context, or PR body.

## Delivery Evidence

delivery_evidence_rule: a merged PR is implementation evidence, not shipped evidence. Closure should cite the RF-1 eval artifact, passing fixture tests, and changed-file repo validation.

## Evidence & Traceability Matrix

| Claim | Evidence |
| --- | --- |
| RF-1 is selected | .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md |
| North star is doctor-driven trust | .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md is referenced but missing in this checkout; use only after restoration or replace with an existing canonical source |
| Apparatus lens is the reusable reference | Infrastructure/references/skills-sdk-apparatus-lens.md is referenced but missing in this checkout; apparatus signoff is blocked until restored or replaced |
| Current doctor baseline is blocked runtime | ./bin/ask skills doctor context7 --json --robot |
| Package baseline is warning-level metadata incompleteness | ./bin/ask skills package context7 --json --robot |
| Steering uptake is a preflight gate | .harness/quality/steering-uptake.md and validate_steering_uptake.py |
| Live Linear issue exists | JSC-329 verified live on 2026-05-18: Triage, no project, no assignee |

## Visual References / Diagrams

RF-0 steering uptake gate -> RF-1 doctor contract fixture -> RF-2 negative-path matrix -> RF-4 harness consumer boundary.

RF-1 also enables RF-3 profile and freshness determinism, RF-5 review intent radius, and RF-6 high-value skill migration.
