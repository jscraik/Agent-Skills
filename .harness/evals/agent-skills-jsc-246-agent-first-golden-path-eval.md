---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-eval
artifact_type: he-eval-report
type: he-eval-report
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Eval
harness_stage: he-eval-report
status: phase_004_complete
date: 2026-05-08
traceability_required: true
origin: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
linear_issue: JSC-246
linear_status: existing
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-246 Agent First Golden Path Eval

## Executive Eval Summary
Status: `PLAN-JSC246-004` implementation and local review gates are complete after resolving the prior projection-closeout blocker.
Linear Completion Recommendation: Complete with follow-up
Primary Blockers: No current phase-004 blocker. Full parent closure still requires remaining phases `PLAN-JSC246-005` through `PLAN-JSC246-007`.
Confidence: Medium-high from focused tests, live CLI probes, harness identity lint, traceability lint, diff check, scoped repo validation, projection integrity, and closeout readiness evidence.

## Evaluated Slice
Linear Project: `agent-skills`
Linear Milestone: `Command surface and ask reliability`
Linear Parent Issue: `JSC-246`
Linear Sub-Issues: None admitted for this phase.
Refactor Program: `.harness/refactors/agent-first-golden-path.md`
Plugin Harness Engineering Spec: `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`, `Infrastructure/tests/test_ask_golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py`, `Infrastructure/tests/test_ask_skills_goal.py`, `Infrastructure/tests/test_ask_cli.py`, this eval artifact.
Affected Workflows: `./bin/ask repo doctor --json --robot`, `./bin/ask repo surface --json --robot`, `./bin/ask skills improve "<goal>" --json --robot`, `./bin/ask skills explain <handle> --json --robot`, `./bin/ask skills proof <handle> --json --robot`, `./bin/ask skills prove <handle> --json --robot`, `./bin/ask repo closeout --changed --json --robot`.
Related ADRs: Proof taxonomy ADR referenced by the JSC-246 plan; no new ADR required for this additive field change.
Related Core Invariants: Agent-first golden path, deterministic command output, traceable closeout proof, no closure without validation evidence.

## Linear Definition of Done Status
Artifact Path: `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`
Definition of Done Status: Satisfied for `PLAN-JSC246-002`, `PLAN-JSC246-003`, and `PLAN-JSC246-004`.
Closure Safety: Safe to continue the plan from phase 005; not a recommendation to close the entire parent issue.

## Linear Backlink Map
Linear Project: `agent-skills`
Linear Milestone: `Command surface and ask reliability`
Linear Parent Issue: `JSC-246`
Linear Sub-Issues: None admitted for this phase.
Linear Status Recommendation: Leave parent issue open; record phase 002 doctor proof, phase 003 route-state proof, and phase 004 explain/prove taxonomy proof as complete.
Proof Artifact Links: `.harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md`; `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`; focused pytest and ask validation outputs listed below.
Missing Identifiers: None for the local phase artifact.
Traceability Repair: No repair required for this phase; live Linear mutation was not attempted from this eval.

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-246` |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Milestone | `Command surface and ask reliability` |
| Parent issue title | `Build repo surface contract and agent capability control-plane golden paths` |
| Priority | `2` |
| Status at plan time | `Todo` |
| Execution route | Agent-assisted; human review required for public command output contracts |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs |
| --- | --- |
| `JSC-246` | `PLAN-JSC246-001`, `PLAN-JSC246-002`, `PLAN-JSC246-003`, `PLAN-JSC246-004` |

## Source Artifact Trace
Linear Plan: `.harness/linear/agent-skills-linear-plan.md` and `.harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md`.
Refactor Program: `.harness/refactors/agent-first-golden-path.md`.
Plugin HE Spec: `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`.
ADRs: Existing proof taxonomy decision referenced by the plan.
Core Invariants: Deterministic routing, agent-visible proof, and no implementation-completion shortcut.
Other Source Artifacts: Live command outputs from `./bin/ask repo doctor`, `./bin/ask repo surface`, `./bin/ask skills improve`, `./bin/ask skills explain`, `./bin/ask skills prove`, and `./bin/ask repo closeout`.

## Functional Validation Results
Command or Method: `python3 -m pytest Infrastructure/tests/test_ask_golden_path.py Infrastructure/tests/test_ask_repo_doctor.py -q`
Result: pass; `27 passed`.
Evidence: Focused tests cover blocker sorting, normal inspection, diagnostic advisory, no-safe-command blocker, summary rendering, doctor/closeout behavior, and additive field mirror checks.
Confidence: High for the changed Python behavior.
Blocks Closure: no for phase 002; parent closure remains open for later plan phases.

Command or Method: `python3 -m pytest Infrastructure/tests/test_ask_skills_goal.py Infrastructure/tests/test_ask_cli.py -k "skills_improve or skills_goal" -q`
Result: pass; `12 passed, 53 deselected`.
Evidence: Focused tests cover `skills improve` route states for resolved, resolved-with-fallback, blocked ambiguity, blocked dependency, blocked reachability, and CLI JSON contract fields.
Confidence: High for the phase 003 route-state behavior.
Blocks Closure: no for phase 003; parent closure remains open for later plan phases.

Command or Method: `python3 -m pytest Infrastructure/tests/test_ask_cli.py -k 'skills_prove or explain' -q`
Result: pass; `15 passed, 42 deselected, 2 subtests passed`.
Evidence: Focused tests cover `skills explain` source/runtime/validation/proof handoff fields for `he-spec` and `simplify`, plus `skills prove` reachability, structural quality, analytics, and outcome-proof taxonomy for `he-spec`.
Confidence: High for the phase 004 explain/prove assertion behavior.
Blocks Closure: no for phase 004 focused behavior; parent closure remains open for later plan phases.

## Eval Gate Matrix
Gate: Focused Tests
Expected: Golden-path and repo-doctor tests pass after adding continuation metadata.
Actual: `python3 -m pytest Infrastructure/tests/test_ask_golden_path.py Infrastructure/tests/test_ask_repo_doctor.py -q` passed with `27 passed`.
Status: pass
Evidence: Local pytest output recorded in this artifact.
Confidence: High
Blocks Closure: no
Required Action: Continue to later JSC-246 phases before closing the parent.

Gate: Live Doctor Probe
Expected: `repo doctor` remains successful and exposes advisory continuation metadata without turning diagnostic debt into a blocking command.
Actual: `./bin/ask repo doctor --json --robot` returned `status: success`, `blocking: false`, `next_command_kind: diagnostic_advisory`, and `next_command_blocks_task: false`.
Status: pass
Evidence: Live command output inspected during the phase.
Confidence: Medium-high
Blocks Closure: no
Required Action: Preserve additive fields through remaining closeout work.

Gate: Harness Traceability
Expected: Eval artifact identity and Linear traceability lints pass.
Actual: `he_artifact_identity_lint.py` and `he_linear_traceability_lint.py` passed for this eval artifact.
Status: pass
Evidence: Validation table captured in the prior phase artifact.
Confidence: High
Blocks Closure: no
Required Action: Link this artifact back to Linear when updating the issue.

Gate: Skills Improve Route-State Contract
Expected: `skills improve` preserves `status` compatibility while exposing `route_state`, `route_state_reason`, and `goal_decision_status`.
Actual: Focused tests passed and live probes returned `resolved`, `resolved_with_fallback`, and `blocked_reachability` route states.
Status: pass
Evidence: `python3 -m pytest Infrastructure/tests/test_ask_skills_goal.py Infrastructure/tests/test_ask_cli.py -k "skills_improve or skills_goal" -q` passed with `12 passed, 53 deselected`.
Confidence: High
Blocks Closure: no for phase 003
Required Action: Keep parent issue open for later phases and final wrapper validation.

Gate: Repo Wrapper Validation
Expected: `./bin/ask repo validate --changed-files .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md Infrastructure/tests/test_ask_cli.py --json --robot` passes.
Actual: Earlier blocked wrapper validation was resolved by the projection-refresh lane and a closeout-loop fix. `./bin/ask repo doctor --json --robot` returned `status: success`, `blocking: false`, and `next_command_blocks_task: false`; `./bin/ask repo closeout --changed --json --robot` returned `status: success`, `ready: true`, `blockers: []`.
Status: pass for blocking gates; non-blocking repo-surface advisory remains.
Evidence: Projection sync, projection-tree sync, projection integrity, handle check, changed-file validation, repo doctor, and repo closeout were run during the blocker recovery.
Confidence: High that the old `SKILLSET_SOURCE_HASH_STALE` / projection drift blocker is resolved.
Blocks Closure: no for current blocking gates; parent closure still waits for remaining phases and end-of-phase review gates.
Required Action: Keep `repo surface` diagnostic debt as advisory unless strict closeout is requested.

Gate: Phase Review Loop
Expected: Run simplify, bug-fix classification when validation fails, and HE code-review before commit.
Actual: Phase 004 simplify and correctness reviews found no actionable findings and only low residual risk from hard-coded command-contract strings and exact source/owner mappings. Focused validation passed, so `he-fix-bugs` was not invoked. The delegated HE code-review subagent did not execute the review task and was replaced by direct scoped review of the phase diff; no blocking API-contract, traceability, validation, or agent-native workflow issue was found.
Status: pass with noted reviewer-tool limitation
Evidence: Simplify maintainability review returned `findings: []`; correctness review returned `findings: []`; focused tests and wrapper validation passed; direct review inspected the added `skills prove` / `skills explain` assertions and this eval artifact for stale phase wording, validation evidence, and Linear closure risk.
Confidence: Medium-high
Blocks Closure: no for phase 004; parent closure remains open for later phases.
Required Action: Continue with `PLAN-JSC246-005`.

## PLAN-JSC246-003 Route-State Evidence

Implementation:

- Added `route_state` and `route_state_reason` to `skills improve`.
- Preserved existing `status: resolved` and `status: resolved_with_fallback`.
- Preserved blocked unresolved and dependency cases as `status: blocked`.
- Normalized reachability failures to `status: blocked` with `route_state: blocked_reachability`.
- Kept existing `goal_decision_status`, `recommended_capability`, `why`, `reachability`, `proof`, and `next_command` fields.

Live representative probes:

| Goal | Result | Route state | Improvement status | Handle | Note |
| --- | --- | --- | --- | --- | --- |
| `make agents better at fixing PR review comments` | success | `resolved_with_fallback` | `resolved_with_fallback` | `autofix` | Fallback remains explicit and reachable. |
| `write a Linear-backed HE spec` | success | `resolved` | `resolved` | `he-spec` | Direct routing works. |
| `monitor a long-running HE work phase` | success | `resolved` | `resolved` | `he-work` | Live ranking selected `he-work`; this is evidence, not scope expansion. |
| `review this implementation against the spec` | success | `resolved_with_fallback` | `resolved_with_fallback` | `triage` | Fallback state is visible; exact handle ranking is left to later routing quality work. |
| `fix validation blockers after review` | error | `blocked_reachability` | `blocked` | `validation` | Reachability failure no longer leaks through `status`; next command is explicit. |

Handle resolution proof:

| Handle | Result | Source |
| --- | --- | --- |
| `autofix` | success | `Skills/agent-ops/autofix/SKILL.md` |
| `he-spec` | success | `Plugins/harness-engineering/skills/he-spec/SKILL.md` |
| `he-work` | success | `Plugins/harness-engineering/skills/he-work/SKILL.md` |
| `he-code-review` | success | `Plugins/harness-engineering/skills/he-code-review/SKILL.md` |
| `he-fix-bugs` | success | `Plugins/harness-engineering/skills/he-fix-bugs/SKILL.md` |

Interpretation:
Phase 003 proves the route-state vocabulary and safe blocked/fallback semantics. It does not claim that every representative goal ranks to the most semantically desirable handle; exact routing quality remains outside this phase unless a later Linear slice admits it.

## Agentic Eval Validity
Evaluated Capability / Task: Validate the JSC-246 phase 002 doctor continuation metadata, phase 003 `skills improve` route-state contract, and phase 004 `skills explain` / `skills prove` proof taxonomy contract.
Task Validity: The task directly exercises the claimed capability: agent-facing command output separates advisory next commands from blocking recovery commands, skill improvement output exposes deterministic route states, and explain/prove output exposes source, runtime, reachability, analytics, and outcome-proof taxonomy without adding schemas.
Outcome Validity: The outcome is valid when tests and live command output show `next_command_kind`, `next_command_blocks_task`, `route_state`, `route_state_reason`, `goal_decision_status`, canonical source paths, generated handles, proof handoff commands, reachability status, analytics evidence class, and outcome-proof evidence class while preserving existing compatibility fields.
Trajectory / Transcript Evidence: Evidence includes source diff inspection, focused pytest output, live `./bin/ask repo doctor --json --robot` inspection, five live `./bin/ask skills improve ... --json --robot` probes, and live `./bin/ask skills explain/proof/prove ... --json --robot` probes.
Grader Coverage: Deterministic tests, CLI state checks, diff check, artifact identity lint, and Linear traceability lint.
Trial Policy: One deterministic local run is enough for this additive metadata phase; pass@k/pass^k reporting is not required because no stochastic model behavior is claimed.
Pass@k / Pass^k Reporting: Not required for this deterministic CLI slice.
Authorization Validator: No protected external side effect exists in phases 002 through 004.
Saturation / Maintenance Signal: Later repeated review or CI failures in this command path should become eval seeds for the golden-path suite.
Blocks Completion: no
Required Action: Keep JSC-246 parent open for remaining plan phases.

## Side-Effect Authorization
Protected Action: No protected external side-effect; local code, tests, and harness artifacts only.
User Authorization Evidence: User approved implementation and continuation in this repository; no external mutation is part of this phase.
Agent Justification: The phase changes local CLI metadata and tests only.
External Party Influence: No
Validator Decision: exempt
Validator Confidence: high
Suggested Next Step: Continue local validation and link proof back to Linear during closeout.
Blocks Completion: no

## Drift Validation
Architecture Drift: Neutral
Routing Drift: Improved
Context Drift: Neutral
Governance Drift: Neutral
Agent-Native Drift: Improved
Moat Drift: Improved

## Architecture Integrity Check
Fact: The implementation adds assertions for existing metadata and taxonomy fields without removing existing fields.
Interpretation: This preserves existing consumers while improving agent interpretation of next commands, runtime projection, and proof readiness.
Assumption: Downstream consumers tolerate additive JSON fields, which is already the repo command contract pattern.
Evidence: Tests for existing doctor/closeout behavior pass, and phase 004 tests assert existing explain/prove output contracts.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`, repo-doctor tests, CLI tests.
Confidence: High
Operational Impact: Lower risk of agents treating diagnostic advisory commands as blockers.
Blocks Completion: no

## Routing Determinism Check
Fact: Doctor output classifies advisory next commands, `skills improve` exposes route states, and explain/prove expose proof handoff and taxonomy fields.
Interpretation: Agents get deterministic routing and proof-readiness signals instead of inferring urgency or readiness from free text.
Assumption: Future plan phases will preserve these fields through closeout, docs compression, and fresh-agent evaluation.
Evidence: Live doctor probe, live skills improve/explain/proof/prove probes, and focused tests.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`.
Confidence: Medium-high
Operational Impact: Better command selection in the agent-first loop.
Blocks Completion: no

## Context Load Check
Fact: The change verifies small structured fields rather than adding long prompt text or new proof schemas.
Interpretation: Context load is neutral for agents and humans.
Assumption: No additional generated projection bloat is introduced by the assertions or existing fields.
Evidence: Diff inspection.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`.
Confidence: Medium
Operational Impact: No meaningful token or reading burden increase.
Blocks Completion: no

## Agent-Native Check
Fact: Command output now exposes whether a suggested next command blocks the task and whether a skill is reachable/provable through command handles.
Interpretation: This improves action parity, completion/resume signaling, and proof-readiness inspection for agents.
Assumption: Later phases will add broader closeout and fresh-agent checks.
Evidence: `next_command_kind` and `next_command_blocks_task` in live doctor output; `skills explain`, `skills proof`, and `skills prove` live probes.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`, `Infrastructure/tests/test_ask_repo_doctor.py`, `Infrastructure/tests/test_ask_cli.py`.
Confidence: High
Operational Impact: Agents can continue work when repo-surface debt is advisory.
Blocks Completion: no

## Governance Simplicity Check
Fact: No new governance stage or Linear issue explosion was introduced.
Interpretation: The phase adds machine-readable clarity without process overhead.
Assumption: Remaining JSC-246 phases stay within the approved plan.
Evidence: Changed files are code/tests/eval artifact only.
Affected Files/Modules: JSC-246 plan and eval artifacts.
Confidence: Medium-high
Operational Impact: Governance remains lightweight.
Blocks Completion: no

## PLAN-JSC246-004 Explain And Prove Taxonomy Evidence

Implementation:

- Added CLI contract tests for `skills explain he-spec` and `skills explain simplify`.
- Added CLI contract tests for `skills prove he-spec`.
- Preserved existing proof schemas: `command-handle-proof.v1`, `skill-proof-scorecard.v1`, `skills-explain.v1`, and `skill-explanation.v1`.
- Did not introduce lifecycle promotion states, proof artifact schemas, or trusted/default-visible status.

Live representative probes:

| Command | Result | Key evidence |
| --- | --- | --- |
| `./bin/ask skills explain he-spec --json --robot` | success | canonical source `Plugins/harness-engineering/skills/he-spec/SKILL.md`; generated handle `.agents/skills/he-spec/SKILL.md`; projection `rooted`; visibility `latent`; next command `./bin/ask skills proof he-spec --json --robot`. |
| `./bin/ask skills explain simplify --json --robot` | success | canonical source `Skills/agent-ops/simplify/SKILL.md`; generated handle `.agents/skills/simplify/SKILL.md`; projection `rooted`; visibility `latent`; validation command present. |
| `./bin/ask skills proof he-spec --json --robot` | success | reachability gates pass for resolver, generated command handle, workspace handle, and `.agents` user link. |
| `./bin/ask skills prove he-spec --json --robot` | success | proof status `reachable_without_outcome_proof`; reachability `pass`; structural quality `pass`; analytics evidence class `native_skill_invocation_projection`; outcome evidence class `outcome_proof`. |

Interpretation:
Phase 004 proves that explain/proof/prove already expose the required golden-path taxonomy using existing command contracts. The remaining gap is not schema shape; it is the expected absence of outcome proof until a workout is run or explicitly linked.
Operational Impact: Agents can inspect source/runtime/proof readiness without guessing which command to run next.
Blocks Completion: no for phase 004; yes for full parent closure until later phases complete.

## Moat Protection Check
Fact: The change strengthens deterministic agent command interpretation.
Interpretation: This protects the harness moat by making proof and routing less dependent on agent guesswork.
Assumption: The metadata remains visible in final closeout outputs.
Evidence: Live doctor output and tests.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`.
Confidence: Medium-high
Operational Impact: Better operational reliability and cognition quality.
Blocks Completion: no

## Proof Artifacts
Produced: Focused pytest output, live ask doctor probe, repo surface probe, live skills improve route-state probes, live skills explain/proof/prove probes, artifact identity lint, Linear traceability lint, diff check, scoped repo validation.
Required: Link this eval artifact and command evidence back to the Linear parent or milestone summary.
Missing: Final parent-issue closure proof for all JSC-246 phases.
Blocks Completion: no for phases 002 through 004; yes for full parent closure.
Attach or Link Back to Linear: Link this eval artifact when updating `JSC-246`.

## Failures / Regressions
Failure or Regression: Earlier parent closeout was blocked by projection drift and a generated-only `sync_required` loop.
Evidence: Prior closeout probe reported `sync_required`; projection integrity reported cache mirror drift. Recovery commands resolved both, and current closeout is ready with no blockers.
Required Corrective Action: Continue remaining JSC-246 phases and run final phase review/closeout gates before parent closure.
Follow-Up Justified: Yes, already represented by the remaining approved plan phases.
Blocks Closure: no for blocking repo-wrapper gates; yes for parent issue closure until phases 005-007 complete.

## Linear Completion Recommendation
Classification: Complete with follow-up
Recommended Linear Status: Keep `JSC-246` open; record phases 002, 003, and 004 as complete.
Required Linear Comment/Update: Note that phase 002 passed focused tests and live doctor proof; phase 003 passed focused route-state tests and live skills-improve probes after review gates; phase 004 passed focused explain/prove tests, live probes, and local review gates; full parent closure awaits phases 005-007 and final closeout.
Issues to Close: None.
Issues to Reopen: None.
Issues to Leave Open: `JSC-246`.
New Follow-Up Issues: None; avoid issue explosion.
Labels to Add/Remove: None.
Milestone Completion: Not complete from this phase alone.
Project Status Change: No change.
Status Update Needed: Yes when the phase proof is linked.
Proof Artifacts to Attach or Link: This eval artifact and validation command summary.

## Follow-Up Work
Classification: Next
Target Linear Project: `agent-skills`
Parent Issue or Milestone: `JSC-246` / `Command surface and ask reliability`
Reason: Remaining plan phases `PLAN-JSC246-005` through `PLAN-JSC246-007` must complete before parent closure.
Priority: Existing Linear priority `2`.
Labels: Existing labels `Roadmap: Next`, `Agent`, `Infra`, `Improvement`.
Agent-Safe or Human Review Required: Agent-safe implementation with human review for public command output contract changes.

## Core / ADR Update Recommendation
Core Update: Not required for this phase.
ADR Update: Not required for this phase.
Reason: The phase implements an approved additive contract; it does not introduce a new irreversible architectural decision.

## Evidence & Traceability Matrix
Conclusion: Phases 002, 003, and 004 are safe to mark complete with follow-up; the JSC-246 parent must remain open for phases 005-007.
Fact: Focused tests passed and live command output exposes advisory/non-blocking continuation metadata, deterministic skills-improve route states, and explain/prove taxonomy fields.
Interpretation: The implementation improves routing/proof determinism without breaking existing command fields or adding proof schema.
Assumption: Later phases will preserve the additive fields through closeout, docs compression, and fresh-agent evaluation.
Evidence: `27 passed` for phase 002 tests; `12 passed, 53 deselected` for phase 003 focused tests; `15 passed, 42 deselected, 2 subtests passed` for phase 004 focused tests; live `repo doctor`, `skills improve`, `skills explain`, `skills proof`, and `skills prove` probes; traceability and identity lints; scoped repo validation.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`, `Infrastructure/tests/test_ask_golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py`, `Infrastructure/tests/test_ask_skills_goal.py`, `Infrastructure/tests/test_ask_cli.py`, this eval artifact.
Command or Inspection Method: Pytest, live `./bin/ask` commands, harness lints, diff inspection.
Confidence: Medium-high
Operational Impact: Agents get a clearer safe next step, explicit fallback/dependency/reachability states, and fewer false blockers.
Blocks Completion: no for phases 002 through 004; yes for full parent issue closure until remaining plan phases complete.
