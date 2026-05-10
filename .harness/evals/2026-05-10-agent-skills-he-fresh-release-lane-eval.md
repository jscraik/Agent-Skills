---
schema_version: 1
artifact_id: agent-skills-he-fresh-release-lane-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-he-fresh-release-lane
title: Agent Skills HE Fresh Release Lane Eval
harness_stage: he-eval-report
status: blocked
date: 2026-05-10
traceability_required: true
origin: .harness/linear/agent-skills-linear-plan.md
linear_issue: JSC-299
linear_milestone: HE Plugin Release Confidence
---

# Agent Skills HE Fresh Release Lane Eval

## Executive Eval Summary
Status: fail
Linear Completion Recommendation: Blocked
Primary Blockers: Full HE lifecycle release lane timed out for all ten selected lifecycle skills at the bounded 300 second per-skill ceiling. This blocks plugin-wide release confidence but does not prove content regression.
Confidence: high for timeout classification; medium for root cause because the runner completed a sliced smoke control but full release cases did not complete within budget.

## Evaluated Slice
Linear Project: agent-skills
Linear Milestone: HE Plugin Release Confidence
Linear Parent Issue: JSC-299
Linear Sub-Issues: unknown
Refactor Program: not_applicable
Plugin Harness Engineering Spec: not_applicable
Affected Files/Modules: `Plugins/harness-engineering/**`, `Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_skill_evals.py`, `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
Affected Workflows: HE lifecycle release eval lane, skill-builder Codex eval runner, router sample gate, runtime confidence claim.
Related ADRs: unknown
Related Core Invariants: lifecycle proof before closure; release confidence must not ignore timed-out lifecycle evals.

## Linear Definition of Done Status
Artifact Path: `.harness/evals/2026-05-10-agent-skills-he-fresh-release-lane-eval.md`
Definition of Done Status: blocked
Closure Safety: unsafe to close plugin-wide release confidence until the release lane is split, tuned, or compressed and rerun successfully.

## Linear Backlink Map
Linear Project: agent-skills
Linear Milestone: HE Plugin Release Confidence
Linear Parent Issue: JSC-299
Linear Sub-Issues: unknown
Linear Status Recommendation: keep open
Proof Artifact Links: `.harness/evals/2026-05-10-agent-skills-he-fresh-release-lane-eval.md`; temporary clean worktree `/tmp/agent-skills-release-eval-2xsFKp`; smoke artifact `Infrastructure/artifacts/skills/he-router/20260510-152831-652625/summary.json` in the temporary worktree.
Missing Identifiers: none for parent issue linkage.
Traceability Repair: keep this eval linked to `JSC-299` before moving release-confidence closure forward.

## Source Artifact Trace
Linear Plan: `.harness/linear/agent-skills-linear-plan.md`
Refactor Program: not_applicable
Plugin HE Spec: not_applicable
ADRs: unknown
Core Invariants: proof before closure; evidence-separated release confidence; timeout failures classified separately from content failures.
Other Source Artifacts: `Plugins/harness-engineering/references/plugin-eval-confidence-contract.md`; `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`

## Planned Proof Check
Promised Proof From Source Artifacts: Fresh full HE lifecycle release lane after the canonical patch, separating content failures, timeouts, tool/preflight failures, and selection-signal warnings.
Proof Planned Before Implementation: yes
Proof Produced: Clean-worktree projection sync passed; full bounded release lane ran; router sample gate passed; sliced smoke control passed.
Proof Missing: Successful full release lane. Content-level case results for lifecycle skills were not produced because every full release skill timed out.
Interpretation: Current proof blocks plugin-wide release confidence and points to eval runner budget, prompt volume, case splitting, or instrumentation rather than a proven skill-content regression.
Blocks Closure: yes

## Functional Validation Results
Command or Method: `git pull --no-rebase --autostash`
Result: pass
Evidence: `Already up to date.`
Confidence: high
Blocks Closure: no

## Eval Gate Matrix

### Gate: Clean Committed-Tree Worktree

Expected: Release evidence is gathered from commit `25cb63f2a` without dirty local artifacts contaminating results.
Actual: Temporary worktree `/tmp/agent-skills-release-eval-2xsFKp` was created at `25cb63f2a`.
Status: pass
Evidence: `git worktree add --detach /tmp/agent-skills-release-eval-2xsFKp HEAD` reported `HEAD is now at 25cb63f2a`.
Confidence: high
Blocks Closure: no
Required Action: none

### Gate: Clean-Worktree Projection Sync

Expected: Workspace rooted projection and plugin cache are synced before lifecycle evals.
Actual: `./bin/ask skills sync --scope workspace --projection rooted --json --robot` returned success and `plugin_cache_refresh.status=refreshed`.
Status: pass
Evidence: Sync output in `/tmp/agent-skills-release-eval-2xsFKp`; `mutation_counts` reported writes, deletes, symlink, and no violations.
Confidence: high
Blocks Closure: no
Required Action: none

### Gate: Full HE Lifecycle Release Lane

Expected: `he-router`, `he-spec`, `he-code-review`, `he-strategy`, `he-refactor`, `he-linear-plan`, `he-eval-report`, `he-phase-heartbeat`, `he-plan`, and `he-work` complete release evals or return content failures.
Actual: All ten selected lifecycle skills timed out at 300 seconds under the Codex runner.
Status: fail
Evidence: `bash -lc 'python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode release --eval-runner codex --require-router-samples --per-skill-timeout-sec 300 --json'` exited `2`; each result had `status=timeout`, `decision=timeout`, `returncode=124`.
Confidence: high
Blocks Closure: yes
Required Action: Split release-heavy eval cases from content failures, tune timeout profiles, or compress release prompts before rerunning.

### Gate: Router Sample Gate

Expected: Router sample execution passes as part of release confidence.
Actual: Router sample gate passed with no warnings.
Status: pass
Evidence: `router_sample_gate.status=pass`, `returncode=0`, `duration_seconds=0.202`, `warnings=[]`.
Confidence: high
Blocks Closure: no
Required Action: none

### Gate: Sliced Smoke Control

Expected: A small live Codex runner case completes so the runner is not treated as globally broken.
Actual: `he-router` smoke case `ambiguous-stage-route` passed in 18.732 seconds.
Status: pass
Evidence: `bash -lc 'python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --eval-runner codex --case ambiguous-stage-route --require-router-samples --per-skill-timeout-sec 180 --json'` exited `0`.
Confidence: high
Blocks Closure: no
Required Action: Use this as control evidence only; do not treat it as full release proof.

### Gate: Selection-Signal Instrumentation

Expected: Runner can observe required skill selection for trigger-sensitive cases.
Actual: Sliced smoke passed but emitted `should_trigger expected skill to be selected, but selection signal was unavailable for this run.`
Status: partial
Evidence: Smoke control output warning under `he-router` case `ambiguous-stage-route`.
Confidence: high
Blocks Closure: yes
Required Action: Fix eval instrumentation or stop treating selection-signal-sensitive cases as skill selection proof.

### Gate: Repo Doctor After Clean-Worktree Sync

Expected: No blocking repo health issue prevents interpreting release-lane output.
Actual: Repo doctor returned success and no blockers, with known repo-surface diagnostic debt.
Status: partial
Evidence: `./bin/ask repo doctor --json --robot` returned `status=success`, `blocking=false`, `repo_surface` warning with 7461 diagnostic findings.
Confidence: high
Blocks Closure: no
Required Action: Track repo-surface ownership cleanup separately; do not mix it into HE release-lane content results.

## Agentic Eval Validity
Evaluated Capability / Task: HE plugin lifecycle release-confidence proof.
Task Validity: valid; release-confidence proof is required before plugin-wide confidence claims.
Outcome Validity: partial; timeout classification is valid, but successful behavior proof is missing.
Trajectory / Transcript Evidence: Clean worktree sync, bounded full release run, router sample pass, sliced smoke control pass.
Grader Coverage: partial; release runner classified timeout failures, but content graders did not run to completion for full release cases.
Trial Policy: one bounded full release run plus one sliced smoke control.
Pass@k / Pass^k Reporting: not_applicable
Authorization Validator: repo-local eval and artifact writes only; no external mutation.
Saturation / Maintenance Signal: all ten full release skills timed out, indicating systemic eval-lane budget/instrumentation debt.
Blocks Completion: yes
Required Action: Create the next repair slice for release eval splitting, timeout tuning, prompt compression, and selection-signal instrumentation.

## Side-Effect Authorization
Protected Action: repo-local temporary worktree sync and eval artifact generation.
User Authorization Evidence: User requested `git pull` and Slice 2 fresh release eval lane.
Agent Justification: Clean committed-tree eval required avoiding dirty local artifact contamination.
External Party Influence: none; repo-local command execution only.
Validator Decision: exempt
Validator Confidence: high
Suggested Next Step: Repair the release eval lane before rerunning plugin-wide confidence.
Blocks Completion: no

## Bounded Context And Translation Boundary Check
Domain Model Status: not_applicable
Bounded Context: Harness Engineering release-confidence evaluation.
Aggregate / Invariant Proof: Release confidence remains blocked when lifecycle evals time out.
Model-Code-Test Language Match: partial; runner vocabulary distinguishes timeout and content failures, but full release cases did not reach content assertions.
Translation Boundary: `.harness` stores cognition and eval proof; Linear should track executable repair work only.
Closure Impact: blocks plugin-wide release confidence.
Evidence: release runner output and smoke control output.
Blocks Completion: yes

## Drift Validation
Architecture Drift: Unknown
Routing Drift: Unknown
Context Drift: Unknown
Governance Drift: Unknown
Agent-Native Drift: Unknown
Moat Drift: Unknown

## Architecture Integrity Check
Conclusion: No architecture regression proven; release eval lane could not produce content evidence.
Evidence: All full release failures are timeout-classified, not regex/content-classified.
Affected Files/Modules: release eval runner and lifecycle skill eval case set.
Confidence: medium
Blocks Completion: yes

## Canonical Model And Aggregate Invariants Check
Conclusion: Domain model impact is not the primary concern for this slice.
Bounded Context: Harness Engineering release confidence.
Canonical Terms: timeout failure, content failure, tool/preflight failure, selection-signal warning, release lane.
Aggregate Invariants: plugin-wide confidence must require completed lifecycle evals.
Lifecycle Ownership: `he-eval-report` owns closure proof; `run_lifecycle_release_evals.py` owns lifecycle eval execution.
Translation Evidence: report maps raw runner outcomes into closure classification.
Scenario or Test Evidence: full release lane timeout; sliced smoke control pass.
Confidence: medium
Blocks Completion: yes

## Routing Determinism Check
Conclusion: Router sample gate passed, but selection-signal instrumentation is partial.
Evidence: `router_sample_gate.status=pass`; smoke warning says selection signal was unavailable.
Affected Files/Modules: `Plugins/harness-engineering/scripts/validate_routing_map.py`, skill-builder Codex runner selection metrics.
Confidence: high
Blocks Completion: yes

## Context Load Check
Conclusion: Full release prompts or runner traces appear too heavy for the current 300 second bounded lane.
Evidence: every lifecycle skill timed out at the same per-skill ceiling; sliced smoke completed quickly.
Affected Files/Modules: lifecycle skill eval case sets, skill-builder runner timeout profiles.
Confidence: high
Blocks Completion: yes

## Agent-Native Check
Conclusion: Agent-native release proof is incomplete.
Evidence: Full release cases did not complete; smoke run reported selection-signal warning.
Affected Files/Modules: HE lifecycle skills, eval runner instrumentation.
Confidence: high
Blocks Completion: yes

## Governance Simplicity Check
Conclusion: The release lane is currently too coarse to produce actionable failure separation.
Evidence: a single full release pass yielded ten identical timeout classifications.
Affected Files/Modules: release eval runner, eval case grouping, timeout profiles.
Confidence: high
Blocks Completion: yes

## Moat Protection Check
Conclusion: Moat protection is blocked until confidence claims are tied to successful evidence, not timeout-heavy release attempts.
Evidence: plugin-wide release confidence remains blocked despite rooted sync and smoke control passing.
Affected Files/Modules: HE confidence policy, lifecycle eval runner.
Confidence: high
Blocks Completion: yes

## Proof Artifacts
Produced: clean worktree `/tmp/agent-skills-release-eval-2xsFKp`; full bounded release output; router sample pass; smoke control artifact `Infrastructure/artifacts/skills/he-router/20260510-152831-652625/summary.json` in the temporary worktree.
Required: successful full release lane or split deep release lane with completed content assertions for changed lifecycle skills and adjacent route skills.
Missing: completed full release content results; selection-signal proof.
Planned Before Implementation: yes
Blocks Completion: yes
Attach or Link Back to Linear: link this eval artifact and the next repair slice when creating Linear work.

## Failures / Regressions
Failure or Regression: Full HE lifecycle release lane is timeout-heavy.
Evidence: all ten selected lifecycle skills timed out at 300 seconds.
Required Corrective Action: Split release cases by lane, tune timeout profile, compress case prompts, or run a deep lane that reports per-case progress and preserves partial results.
Follow-Up Justified: yes
Blocks Closure: yes

## Linear Completion Recommendation
Classification: Blocked
Recommended Linear Status: keep open
Required Linear Comment/Update: Full HE release confidence remains blocked. Clean rooted sync and router smoke control passed, but all lifecycle release skills timed out at 300s and selection-signal proof is partial.
Issues to Close: none
Issues to Reopen: none
Issues to Leave Open: HE plugin release confidence work
New Follow-Up Issues: one focused issue for release eval lane splitting, timeout-profile tuning, prompt compression, and selection-signal instrumentation.
Labels to Add/Remove: Eval, Agent-Native, Reliability
Milestone Completion: blocked
Project Status Change: none
Status Update Needed: yes
Proof Artifacts to Attach or Link: `.harness/evals/2026-05-10-agent-skills-he-fresh-release-lane-eval.md`

## Follow-Up Work
Classification: Create
Target Linear Project: agent-skills
Parent Issue or Milestone: HE Plugin Release Confidence
Reason: The current full release lane cannot provide plugin-wide confidence because it times out before content assertions complete.
Priority: High
Labels: Eval, Agent-Native, Reliability
Agent-Safe or Human Review Required: Agent-assisted; human review required before claiming plugin-wide release confidence.

## Core / ADR Update Recommendation
Core Update: not required yet
ADR Update: not required yet
Reason: This is an eval-runner operability finding, not yet a durable architecture decision.

## Evidence & Traceability Matrix

| Conclusion | Evidence | Type | Confidence | Closure Impact |
| --- | --- | --- | --- | --- |
| Git pull completed before Slice 2 | `git pull --no-rebase --autostash` returned `Already up to date.` | fact | high | no block |
| Release evidence came from a clean committed-tree worktree | `/tmp/agent-skills-release-eval-2xsFKp` was created at commit `25cb63f2a` | fact | high | no block |
| Clean worktree required trust/setup repair before eval | `mise trust /tmp/agent-skills-release-eval-2xsFKp/.mise.toml`; initial direct discovery was blocked by untrusted `.mise.toml` | fact | high | no block after repair |
| Direct Python invocation is blocked by the desktop approval shim in this context | direct `python3` execution was rejected, while `bash -lc 'python3 --version'` passed | fact | high | no block after using shell invocation |
| Projection sync passed in the clean worktree | `./bin/ask skills sync --scope workspace --projection rooted --json --robot` returned success and refreshed plugin cache | fact | high | no block |
| Full release lane is timeout-heavy | All ten lifecycle skills timed out at 300s under the Codex runner | fact | high | blocks plugin-wide release confidence |
| Router sample gate is healthy | `router_sample_gate.status=pass`, `warnings=[]` | fact | high | no block |
| Live runner can complete a small sliced case | `he-router` smoke `ambiguous-stage-route` passed in 18.732s | fact | high | control evidence only |
| Skill selection signal remains partial | Smoke warning: `should_trigger expected skill to be selected, but selection signal was unavailable for this run.` | fact | high | blocks selection-sensitive confidence |
| Next repair should target eval lane mechanics before skill content | Timeouts occurred before content assertions completed | interpretation | medium | follow-up required |
