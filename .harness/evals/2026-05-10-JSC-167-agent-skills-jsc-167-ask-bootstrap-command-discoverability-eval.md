---
schema_version: 1
artifact_id: agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-167-ask-bootstrap-command-discoverability
title: Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
traceability_required: true
origin: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md
linear_issue: JSC-167
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-167 Ask Bootstrap Command Discoverability Eval

## Executive Eval Summary
Status: focused implementation and aggregate validation complete; heartbeat closeout evidence blocked
Linear Completion Recommendation: Blocked pending heartbeat evidence bundle
Primary Blockers: he-phase-heartbeat recurring evidence bundle is missing
Confidence: 0.93 for focused JSC-167 behavior, 0.84 for full HE phase closure because heartbeat evidence remains unavailable

## Evaluated Slice
Linear Project: agent-skills
Linear Milestone: Command surface and ask reliability
Linear Parent Issue: JSC-167
Linear Sub-Issues: none in scope; JSC-168 and JSC-169 are deferred downstream issues
Refactor Program: not applicable
Plugin Harness Engineering Spec: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
Affected Files/Modules: Infrastructure/scripts/bootstrap-ask.sh; Infrastructure/scripts/lib/ask/bootstrap.py; Infrastructure/scripts/lib/ask/commands/repo.py; Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py; Infrastructure/scripts/validate_all.sh; Infrastructure/scripts/testing/test_ask_bootstrap.py; Infrastructure/tests/test_ask_repo_doctor.py; README.md; AGENTS.md; Docs/agents/5-minute-success-path.md; Docs/agents/README.md; Docs/agents/16-agent-operating-contract.md; Docs/agents/04-validation.md; .harness/media/2026-05-10-jsc-167-ask-bootstrap-before-after.png
Affected Workflows: first-contact ask bootstrap; repo doctor diagnostic advisory; docs consistency validation; focused bootstrap regression tests
Related ADRs: none identified for this bounded slice
Related Core Invariants: repo-local command wrappers are canonical; generated/runtime projections must not be edited as part of JSC-167

## Linear Definition of Done Status
Artifact Path: .harness/evals/2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md
Definition of Done Status: complete for JSC-167 implementation; partial for heartbeat-managed phase closeout
Closure Safety: safe to review as a JSC-167 implementation slice; defer full heartbeat closure until session evidence is available

## Linear Backlink Map
Linear Project: agent-skills
Linear Milestone: Command surface and ask reliability
Linear Parent Issue: JSC-167
Linear Sub-Issues: none in this slice
Linear Status Recommendation: blocked pending heartbeat evidence attachment
Proof Artifact Links: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md; .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md; .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review.md; .harness/media/2026-05-10-jsc-167-ask-bootstrap-before-after.png
Missing Identifiers: no additional Linear identifier needed for this eval; live Linear mutation was not performed
Traceability Repair: attach or reference this eval with the aggregate validation pass and the heartbeat evidence caveat

## Source Artifact Trace
Linear Plan: .harness/linear/agent-skills-linear-plan.md
Refactor Program: none
Plugin HE Spec: .harness/specs/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-spec.md
ADRs: none found for this slice
Core Invariants: Docs/agents/14-path-ownership-boundaries.md and repo guidance require canonical source edits rather than projection/runtime mirror edits
Other Source Artifacts: .harness/plan/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan.md; .harness/review/2026-05-10-agent-skills-jsc-167-ask-bootstrap-command-discoverability-plan-technical-review.md

## Planned Proof Check
Promised Proof From Source Artifacts: bootstrap JSON proof; non-executable and PATH fixture coverage; wrong-shim identity proof; docs contract proof; repo doctor signal proof; aggregate closeout evidence
Proof Planned Before Implementation: yes
Proof Produced: focused command, test, lint, type, docs, doctor, review, and aggregate changed-file validation evidence was produced; infographic proof artifact was stored under .harness/media
Proof Missing: he-phase-heartbeat recurring evidence was not available
Interpretation: implementation proof is strong and aggregate validation is green; heartbeat-managed closure still needs the required evidence bundle
Blocks Closure: no for JSC-167 implementation; yes for heartbeat-managed recurring phase closure

## Functional Validation Results
Command or Method: focused validation and aggregate changed-file gate
Result: focused validation passed; aggregate changed-file validation passed
Evidence: `python3 -m pytest Infrastructure/scripts/testing/test_ask_bootstrap.py Infrastructure/tests/test_ask_repo_doctor.py -q` passed with 39 tests; `ruff check ...` passed; `pyright ...` passed with 0 errors; `bash scripts/bootstrap-ask.sh --json` emitted ask-bootstrap.v1 warning with fallback pass and PATH warn; `./bin/ask repo doctor --json --robot` emitted ask_bootstrap warn; `bash Infrastructure/scripts/validate_all.sh --ephemeral --changed-files ...` passed with required_failures 0 and warn_only_issues 0
Confidence: high for focused behavior; high for implementation closure posture
Blocks Closure: no

## Eval Gate Matrix
Gate: bootstrap JSON contract
Expected: stable ask-bootstrap.v1 output with bounded checks and fallback proof
Actual: `bash scripts/bootstrap-ask.sh --json` returned ask-bootstrap.v1 with status warning, fallback pass, path warn, and shim skipped
Status: pass
Evidence: command output summary recorded in chat; full output available by rerunning the command
Confidence: high
Blocks Closure: no
Required Action: none for implementation; configure PATH shim only if desired as follow-up

Gate: focused regression tests
Expected: tests cover bootstrap helper behavior and repo-doctor warning mapping
Actual: `python3 -m pytest Infrastructure/scripts/testing/test_ask_bootstrap.py Infrastructure/tests/test_ask_repo_doctor.py -q` passed with 39 tests
Status: pass
Evidence: test output `39 passed in 1.30s`
Confidence: high
Blocks Closure: no
Required Action: retain tests with the patch

Gate: static and type validation
Expected: changed Python files pass lint, compile, and type checks
Actual: `ruff check ...` passed; `pyright ...` passed with 0 errors; `python3 -m py_compile ...` passed
Status: pass
Evidence: command outputs recorded during implementation
Confidence: high
Blocks Closure: no
Required Action: none

Gate: docs contract validation
Expected: normative first-contact docs include the bootstrap and fallback commands
Actual: `python3 Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py` passed
Status: pass
Evidence: output `ask bootstrap docs validation passed`
Confidence: high
Blocks Closure: no
Required Action: keep validator wired in validate_all

Gate: independent technical review
Expected: reviewer finds no unresolved material correctness issue
Actual: reviewer found a false-pass warning mapping; implementation was corrected and tested
Status: pass
Evidence: `_ask_bootstrap_signal` now reports PATH-missing shim-skipped state as warn; focused repo-doctor tests pass
Confidence: high
Blocks Closure: no
Required Action: none

Gate: aggregate changed-file validation
Expected: `bash Infrastructure/scripts/validate_all.sh --ephemeral --changed-files ...` passes or fails only for accepted non-slice blockers
Actual: passed with required_failures 0 and warn_only_issues 0
Status: pass
Evidence: `bash Infrastructure/scripts/validate_all.sh --ephemeral --changed-files ...` completed successfully; log root was `/tmp/agent-skills-validate-all.MAIjtQ` and ephemeral logs were removed automatically after the successful run
Confidence: high
Blocks Closure: no
Required Action: none

Gate: he-phase-heartbeat evidence
Expected: heartbeat phase loop has required session-collector evidence bundle before recurring continuation
Actual: required session-collector evidence bundle was not available under `/Users/jamiecraik/.agents/session-collector`
Status: fail
Evidence: local evidence lookup found no usable bundle for the requested heartbeat workflow
Confidence: medium
Blocks Closure: yes
Required Action: provide or regenerate the session evidence bundle, then rerun he-phase-heartbeat closeout

## Agentic Eval Validity
Evaluated Capability / Task: agent and human first-contact bootstrap for the repo-local `ask` command
Task Validity: valid because JSC-167 specifically targets bootstrap and command discoverability
Outcome Validity: valid for implementation closure because focused behavior and aggregate validation are both proven
Trajectory / Transcript Evidence: implementation, review, focused validation, aggregate validation pass, and heartbeat evidence blocker were captured in this Codex thread
Grader Coverage: focused unit tests, docs validator, ruff, pyright, py_compile, repo doctor smoke, and aggregate validation logs
Trial Policy: single focused implementation trial with independent review correction; no multi-run saturation claimed
Pass@k / Pass^k Reporting: not applicable to this implementation slice
Authorization Validator: no external Linear mutation or protected action was taken
Saturation / Maintenance Signal: sufficient for this bounded implementation slice; insufficient for recurring heartbeat closure
Blocks Completion: no
Required Action: provide or regenerate heartbeat evidence before claiming heartbeat-managed recurring phase closure

## Side-Effect Authorization
Protected Action: Linear closeout, status mutation, or external comment
User Authorization Evidence: user asked to proceed with work and invoke he-eval-report, but did not authorize closing Linear
Agent Justification: no protected external action is needed for this eval
External Party Influence: no external party influence observed
Validator Decision: exempt
Validator Confidence: high
Suggested Next Step: keep Linear open and use this eval as local closure evidence after blockers are cleared
Blocks Completion: no

## Domain Model Integrity Check
Domain Model Status: not applicable to product domain model
Bounded Context: repository command bootstrap and validation control plane
Aggregate / Invariant Proof: bootstrap must remain repo-local, bounded, and non-global; focused tests enforce no-shell subprocess execution and safe chmod constraints
Model-Code-Test Language Match: plan terms such as fallback, PATH shim, repo identity, and docs contract are reflected in code and tests
Translation Boundary: command bootstrap errors defer dependency and lazy-loading failures to JSC-168 and JSC-169 rather than implementing them
Closure Impact: no domain-model blocker
Evidence: Infrastructure/scripts/lib/ask/bootstrap.py; Infrastructure/scripts/testing/test_ask_bootstrap.py; Infrastructure/tests/test_ask_repo_doctor.py
Blocks Completion: no

## Drift Validation
Architecture Drift: Improved
Routing Drift: Improved
Context Drift: Neutral
Governance Drift: Improved
Agent-Native Drift: Improved
Moat Drift: Neutral

## Architecture Integrity Check
Conclusion: improved within the slice
Evidence: bootstrap logic is importable Python behind a thin shell launcher; repo doctor consumes the same proof path instead of duplicating shell behavior
Affected Files/Modules: Infrastructure/scripts/bootstrap-ask.sh; Infrastructure/scripts/lib/ask/bootstrap.py; Infrastructure/scripts/lib/ask/commands/repo.py
Confidence: high
Blocks Completion: no

## Routing Determinism Check
Conclusion: improved but not fully closed
Evidence: `./bin/ask skills resolve he-eval-report --json` resolves to the canonical HE eval report skill; repo doctor now emits ask_bootstrap as a named diagnostic signal
Affected Files/Modules: Infrastructure/scripts/lib/ask/commands/repo.py; .agents/skills/he-eval-report/SKILL.md
Confidence: high
Blocks Completion: no

## Context Load Check
Conclusion: improved
Evidence: implementation adds focused bootstrap and docs proof without expanding skill runtime projections; aggregate context-budget now passes for the changed-file gate
Affected Files/Modules: Infrastructure/scripts/lib/ask/bootstrap.py; Infrastructure/scripts/testing/test_ask_bootstrap.py
Confidence: high
Blocks Completion: no

## Agent-Native Check
Conclusion: improved
Evidence: bootstrap emits machine-readable JSON; repo doctor exposes a machine-readable ask_bootstrap signal; docs validator prevents first-contact command drift
Affected Files/Modules: Infrastructure/scripts/lib/ask/bootstrap.py; Infrastructure/scripts/validation-and-linting/verify_ask_bootstrap_docs.py; README.md; AGENTS.md
Confidence: high
Blocks Completion: no

## Governance Simplicity Check
Conclusion: improved
Evidence: the patch uses repo-local wrappers, avoids global shell/profile mutation, preserves actual command telemetry, and passes the aggregate changed-file validation gate
Affected Files/Modules: Infrastructure/scripts/validate_all.sh; Infrastructure/scripts/lib/ask/bootstrap.py
Confidence: high
Blocks Completion: no

## Moat Protection Check
Conclusion: neutral
Evidence: no product moat, external API, credential, or proprietary capability boundary changed in this slice
Affected Files/Modules: none beyond local command-control-plane files
Confidence: high
Blocks Completion: no

## Proof Artifacts
Produced: .harness/evals/2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md; .harness/media/2026-05-10-jsc-167-ask-bootstrap-before-after.png; focused test and lint command outputs in the Codex thread
Required: he-phase-heartbeat evidence bundle if recurring phase continuation remains required
Missing: session evidence bundle for he-phase-heartbeat
Planned Before Implementation: yes
Blocks Completion: no
Attach or Link Back to Linear: safe to attach with heartbeat evidence caveat

## Failures / Regressions
Failure or Regression: he-phase-heartbeat recurring evidence bundle unavailable
Evidence: earlier he-phase-heartbeat lookup did not find the required usable bundle under `/Users/jamiecraik/.agents/session-collector`
Required Corrective Action: provide or regenerate session evidence before claiming recurring heartbeat closure
Follow-Up Justified: yes, as heartbeat evidence repair only if recurring continuation remains required
Blocks Closure: no for implementation; yes for heartbeat-managed recurring phase closure

## Linear Completion Recommendation
Classification: Blocked
Recommended Linear Status: ready for human review or completion with heartbeat caveat
Required Linear Comment/Update: post eval summary with focused pass evidence, aggregate validation pass, and heartbeat evidence caveat
Issues to Close: none
Issues to Reopen: none
Issues to Leave Open: JSC-167 until the required he-phase-heartbeat evidence bundle is attached or explicitly waived
New Follow-Up Issues: do not create unless heartbeat evidence repair becomes recurring operational work
Labels to Add/Remove: none
Milestone Completion: do not advance milestone completion from this eval
Project Status Change: none
Status Update Needed: yes, with aggregate validation pass and heartbeat caveat
Proof Artifacts to Attach or Link: .harness/evals/2026-05-10-JSC-167-agent-skills-jsc-167-ask-bootstrap-command-discoverability-eval.md

## Follow-Up Work
Classification: Do Not Create
Target Linear Project: agent-skills
Parent Issue or Milestone: JSC-167 / Command surface and ask reliability
Reason: heartbeat evidence absence is a local closeout-evidence caveat unless it recurs across phases
Priority: medium for recurring closeout, not a code blocker
Labels: none
Agent-Safe or Human Review Required: agent-safe to rerun heartbeat evidence discovery; human review required before external Linear closure

## Core / ADR Update Recommendation
Core Update: not required
ADR Update: not required
Reason: JSC-167 adds a bounded bootstrap proof path and docs validator; it does not change the larger command-control-plane architecture decision

## Evidence & Traceability Matrix
Conclusion: implementation slice is materially complete; recurring heartbeat closeout evidence remains unavailable
Fact: focused tests, lint, typecheck, docs validation, bootstrap smoke, repo doctor smoke, eval validation, and aggregate changed-file validation passed after technical review and simplify remediation
Interpretation: the code behavior for JSC-167 is strong enough for review and implementation completion; only heartbeat-managed recurring phase closure remains caveated
Assumption: heartbeat evidence is not required to merge the JSC-167 bootstrap implementation, but is required before claiming the requested recurring phase loop is fully closed
Evidence: aggregate validation passed with required_failures 0 and warn_only_issues 0; he-phase-heartbeat evidence bundle remained unavailable earlier in the same run
Affected Files/Modules: Infrastructure/scripts/lib/ask/bootstrap.py; Infrastructure/scripts/lib/ask/commands/repo.py; Infrastructure/scripts/validate_all.sh; Infrastructure/scripts/testing/test_ask_bootstrap.py
Command or Inspection Method: focused command validation, simplify review, bug-fix reproduction, aggregate changed-file validation, eval validator
Confidence: high for implementation status; medium for heartbeat closure caveat
Operational Impact: agents now have a repo-local bootstrap proof path and a green changed-file validation gate
Blocks Completion: no
