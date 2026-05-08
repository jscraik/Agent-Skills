---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-eval
artifact_type: he-eval-report
type: he-eval-report
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Eval
harness_stage: he-eval-report
status: phase_003_wrapper_blocked
date: 2026-05-08
traceability_required: true
origin: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
linear_issue: JSC-246
linear_status: existing
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-246 Agent First Golden Path Eval

## Executive Eval Summary
Status: `PLAN-JSC246-003` implementation is locally complete and phase review gates found no blocking phase findings.
Linear Completion Recommendation: Complete with follow-up
Primary Blockers: No blocker in the `PLAN-JSC246-003` implementation slice; repo wrapper validation is blocked by unrelated staged HE eval-report projection/progressive-disclosure churn.
Confidence: Medium-high from focused tests, live CLI probes, harness identity lint, traceability lint, diff check, and scoped repo validation blocker classification.

## Evaluated Slice
Linear Project: `agent-skills`
Linear Milestone: `Command surface and ask reliability`
Linear Parent Issue: `JSC-246`
Linear Sub-Issues: None admitted for this phase.
Refactor Program: `.harness/refactors/agent-first-golden-path.md`
Plugin Harness Engineering Spec: `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`, `Infrastructure/tests/test_ask_golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py`, `Infrastructure/tests/test_ask_skills_goal.py`, `Infrastructure/tests/test_ask_cli.py`, this eval artifact.
Affected Workflows: `./bin/ask repo doctor --json --robot`, `./bin/ask repo surface --json --robot`, `./bin/ask skills improve "<goal>" --json --robot`, `./bin/ask repo closeout --changed --json --robot`.
Related ADRs: Proof taxonomy ADR referenced by the JSC-246 plan; no new ADR required for this additive field change.
Related Core Invariants: Agent-first golden path, deterministic command output, traceable closeout proof, no closure without validation evidence.

## Linear Definition of Done Status
Artifact Path: `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`
Definition of Done Status: Satisfied for `PLAN-JSC246-002`; `PLAN-JSC246-003` focused validation and review gates passed, but wrapper validation is blocked by unrelated dirty HE eval-report changes; not sufficient for full JSC-246 closure until remaining plan phases and projection sync closeout pass.
Closure Safety: Safe to continue the plan from phase 002; not a recommendation to close the entire parent issue.

## Linear Backlink Map
Linear Project: `agent-skills`
Linear Milestone: `Command surface and ask reliability`
Linear Parent Issue: `JSC-246`
Linear Sub-Issues: None admitted for this phase.
Linear Status Recommendation: Leave parent issue open; record phase 002 proof as complete and phase 003 route-state proof after review gates pass.
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
| `JSC-246` | `PLAN-JSC246-001`, `PLAN-JSC246-002`, `PLAN-JSC246-003` |

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
Expected: `./bin/ask repo validate --changed-files Infrastructure/scripts/lib/ask/commands/skills.py Infrastructure/tests/test_ask_skills_goal.py Infrastructure/tests/test_ask_cli.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md --json --robot` passes.
Actual: Blocked with `required_failures: 2` in `Infrastructure/artifacts/validation/20260508T113613Z`.
Status: blocked
Evidence: `context-budget.log` reports `SKILLSET_SOURCE_HASH_STALE`; `skill-authoring-family.log` reports `Plugins/harness-engineering/skills/he-eval-report/SKILL.md removed 2 line(s) but no added context was found in references or Plugins/harness-engineering/references/deferred-context-index.md`.
Confidence: High that this blocker is outside the phase 003 route-state files.
Blocks Closure: yes for commit/parent closeout; no for focused phase behavior proof.
Required Action: Resolve the unrelated HE eval-report projection/progressive-disclosure changes before committing or closing the broader branch.

Gate: Phase Review Loop
Expected: Run simplify, bug-fix classification, and HE code-review before commit.
Actual: Simplify review found no actionable simplification; bug review found no correctness findings and classified residual risks as low; direct HE code-review found no blocking API-contract issue. The delegated code-review subagent did not execute and was replaced by direct review against the scoped diff.
Status: pass with noted reviewer-tool limitation
Evidence: Simplify review output: no actionable simplification. Bug review output: `findings: []`; residual risks around fallback token heuristics and blocked CLI envelope coverage. Direct review inspected `skills.py` lines 1973-2105, `test_ask_skills_goal.py` lines 147-343, and `test_ask_cli.py` lines 715-740.
Confidence: Medium-high
Blocks Closure: no for phase 003; wrapper blocker remains separate.
Required Action: Do not commit until unrelated wrapper blockers are resolved or explicitly accepted.

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
Evaluated Capability / Task: Validate the JSC-246 phase 002 doctor continuation metadata and phase 003 `skills improve` route-state contract.
Task Validity: The task directly exercises the claimed capability: agent-facing command output now separates advisory next commands from blocking recovery commands, and skill improvement output now exposes deterministic route states.
Outcome Validity: The outcome is valid when tests and live command output show `next_command_kind`, `next_command_blocks_task`, `route_state`, `route_state_reason`, and `goal_decision_status` while preserving existing compatibility fields.
Trajectory / Transcript Evidence: Evidence includes source diff inspection, focused pytest output, live `./bin/ask repo doctor --json --robot` inspection, and five live `./bin/ask skills improve ... --json --robot` probes.
Grader Coverage: Deterministic tests, CLI state checks, diff check, artifact identity lint, and Linear traceability lint.
Trial Policy: One deterministic local run is enough for this additive metadata phase; pass@k/pass^k reporting is not required because no stochastic model behavior is claimed.
Pass@k / Pass^k Reporting: Not required for this deterministic CLI slice.
Authorization Validator: No protected external side effect exists in phase 002.
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
Fact: The implementation adds metadata fields without removing existing fields.
Interpretation: This preserves existing consumers while improving agent interpretation of next commands.
Assumption: Downstream consumers tolerate additive JSON fields, which is already the repo command contract pattern.
Evidence: Tests for existing doctor/closeout behavior pass.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, repo-doctor tests.
Confidence: High
Operational Impact: Lower risk of agents treating diagnostic advisory commands as blockers.
Blocks Completion: no

## Routing Determinism Check
Fact: The doctor output now classifies the next command as diagnostic advisory and non-blocking.
Interpretation: Agents get a deterministic routing signal instead of inferring urgency from free text.
Assumption: Future plan phases will preserve this field through closeout and proof commands.
Evidence: Live doctor probe and focused tests.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`.
Confidence: Medium-high
Operational Impact: Better command selection in the agent-first loop.
Blocks Completion: no

## Context Load Check
Fact: The change adds small structured fields rather than new long prompt text.
Interpretation: Context load is neutral for agents and humans.
Assumption: No additional generated projection bloat is introduced by the field itself.
Evidence: Diff inspection.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`.
Confidence: Medium
Operational Impact: No meaningful token or reading burden increase.
Blocks Completion: no

## Agent-Native Check
Fact: The command output now exposes whether a suggested next command blocks the task.
Interpretation: This improves action parity and completion/resume signaling for agents.
Assumption: Later phases will add broader proof promotion checks.
Evidence: `next_command_kind` and `next_command_blocks_task` in live doctor output.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py`.
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
Produced: Focused pytest output, live ask doctor probe, repo surface probe, live skills improve route-state probes, artifact identity lint, Linear traceability lint, diff check, scoped repo validation.
Required: Link this eval artifact and command evidence back to the Linear parent or milestone summary.
Missing: Final parent-issue closure proof for all JSC-246 phases.
Blocks Completion: no for phase 002; yes for full parent closure.
Attach or Link Back to Linear: Link this eval artifact when updating `JSC-246`.

## Failures / Regressions
Failure or Regression: Full parent closeout still has broader projection/sync work outside the phase 002 implementation.
Evidence: Prior closeout probe reported `sync_required`.
Required Corrective Action: Complete remaining JSC-246 phases and run the projection-refresh lane before parent closure.
Follow-Up Justified: Yes, already represented by the remaining approved plan phases.
Blocks Closure: no for phase 002; yes for parent issue closure.

## Linear Completion Recommendation
Classification: Complete with follow-up
Recommended Linear Status: Keep `JSC-246` open; record phase 002 as complete.
Required Linear Comment/Update: Note that phase 002 passed focused tests and live doctor proof; phase 003 passed focused route-state tests and live skills-improve probes after review gates; full parent closure awaits remaining plan phases and final sync validation.
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
Reason: Remaining plan phases `PLAN-JSC246-004` through `PLAN-JSC246-007` must complete before parent closure.
Priority: Existing Linear priority `2`.
Labels: Existing labels `Roadmap: Next`, `Agent`, `Infra`, `Improvement`.
Agent-Safe or Human Review Required: Agent-safe implementation with human review for public command output contract changes.

## Core / ADR Update Recommendation
Core Update: Not required for this phase.
ADR Update: Not required for this phase.
Reason: The phase implements an approved additive contract; it does not introduce a new irreversible architectural decision.

## Evidence & Traceability Matrix
Conclusion: Phases 002 and 003 are safe to mark complete with follow-up, but not enough to close the JSC-246 parent.
Fact: Focused tests passed and live command output exposes advisory/non-blocking continuation metadata plus deterministic skills-improve route states.
Interpretation: The implementation improves routing determinism without breaking existing command fields.
Assumption: Later phases will preserve the additive fields through closeout, explain, and proof surfaces.
Evidence: `27 passed` for phase 002 tests; `12 passed, 53 deselected` for phase 003 focused tests; live `repo doctor` output; live `skills improve` route-state probes; traceability and identity lints; scoped repo validation.
Affected Files/Modules: `Infrastructure/scripts/lib/ask/golden_path.py`, `Infrastructure/scripts/lib/ask/commands/skills.py`, `Infrastructure/tests/test_ask_golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py`, `Infrastructure/tests/test_ask_skills_goal.py`, `Infrastructure/tests/test_ask_cli.py`, this eval artifact.
Command or Inspection Method: Pytest, live `./bin/ask` commands, harness lints, diff inspection.
Confidence: Medium-high
Operational Impact: Agents get a clearer safe next step, explicit fallback/dependency/reachability states, and fewer false blockers.
Blocks Completion: no for phases 002 and 003; yes for full parent issue closure until remaining plan phases complete.
