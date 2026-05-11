---
schema_version: 1
artifact_id: agent-skills-jsc-284-he-eval-report
artifact_type: he-eval-report
canonical_slug: agent-skills-jsc-284
title: Agent Skills JSC-284 Eval Report
harness_stage: he-eval-report
status: complete
traceability_required: true
origin: .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md
linear_issue: JSC-284
linear_status: complete
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-284 Eval Report

# Executive Eval Summary

Status: local implementation, local proof, and Linear closure are complete.

Linear Completion Recommendation: Complete

Primary Remaining Cautions:

- The repository worktree contains broader dirty/generated surfaces outside this evaluated slice, so any commit must stage only the selected HE-slice files after review.

Confidence: High for local implementation evidence, validation gates, and live Linear state verified through issue fetches.

# Evaluated Slice

Linear Project: `agent-skills`

Linear Milestone: `Command surface and ask reliability`

Linear Parent Issue: `JSC-284`

Linear Sub-Issues: `JSC-285`, `JSC-286`, `JSC-287`

Refactor Program: `.harness/refactors/ask-control-plane-decomposition.md`

Plugin Harness Engineering Spec: `.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`

Affected Files/Modules:

- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lib/ask/commands/plugins.py`
- `Infrastructure/scripts/lib/ask/services/plugin_cache.py`
- `Infrastructure/scripts/lib/ask/services/plugin_sources.py`
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
- `Infrastructure/tests/test_local_plugin_picker_surface.py`
- `Infrastructure/tests/test_ask_skills_sync_security.py`
- `Infrastructure/tests/test_skill_scope_precedence.py`
- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

Affected Workflows:

- `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`
- `./bin/ask skills resolve <handle> --json`
- `./bin/ask skills list --json`
- `./bin/ask repo doctor --json --robot`
- runtime-budget collision validation
- local plugin picker and plugin mirror validation

Related ADRs:

- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

Related Core Invariants:

- `.harness/core/architecture-invariants.md`
- `.harness/core/execution-invariants.md`
- `.harness/core/routing-invariants.md`
- `.harness/core/moat-invariants.md`
- `.harness/core/anti-drift-principles.md`

# Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-284` |
| Child issues | `JSC-285`, `JSC-286`, `JSC-287` |
| Project | `agent-skills` |
| Milestone | `Command surface and ask reliability` |
| Status | Done |
| Closure proof | Linear comment `a54b9452-af8c-4498-bbba-ed61f92bd773` |

# Linear Acceptance Traceability

| Linear issue | Acceptance IDs |
| --- | --- |
| `JSC-284` | `SA-ASK-001` through `SA-ASK-015` |
| `JSC-285` | `SA-ASK-001`, `SA-ASK-002`, `SA-ASK-010` |
| `JSC-286` | `SA-ASK-003`, `SA-ASK-004`, `SA-ASK-005`, `SA-ASK-006`, `SA-ASK-009`, `SA-ASK-010`, `SA-ASK-011`, `SA-ASK-012`, `SA-ASK-013` |
| `JSC-287` | `SA-ASK-007` |

# Linear Definition of Done Status

Artifact Path: `.harness/evals/agent-skills-jsc-284-eval.md`

Definition of Done Status: local proof complete; Linear tracker closure complete.

Closure Safety: Linear closure is complete for `JSC-284` through `JSC-287`; selected-file commit staging still requires review because the worktree contains broader generated/projection churn.

# Linear Backlink Map

Linear Project: `agent-skills`

Linear Milestone: `Command surface and ask reliability`

Linear Parent Issue: `JSC-284`

Linear Sub-Issues: `JSC-285`, `JSC-286`, `JSC-287`

Linear Status Recommendation: resolved; `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` are Done in Linear.

Proof Artifact Links:

- `.harness/evals/agent-skills-jsc-284-eval.md`
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

Missing Identifiers: none.

Traceability Repair: complete. Live Linear fetches verified `JSC-284` through `JSC-287` as Done, and closure proof comment `a54b9452-af8c-4498-bbba-ed61f92bd773` was posted to `JSC-284`.

# Source Artifact Trace

Linear Plan: `.harness/linear/agent-skills-linear-plan.md`

Refactor Program: `.harness/refactors/ask-control-plane-decomposition.md`

Plugin HE Spec: `.harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`

ADRs: `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

Core Invariants:

- `.harness/core/architecture-invariants.md`
- `.harness/core/execution-invariants.md`
- `.harness/core/routing-invariants.md`
- `.harness/core/moat-invariants.md`

Other Source Artifacts:

- `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
- `.harness/review/agent-skills-ask-control-plane-decomposition-spec-technical-review.md`
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`

# Functional Validation Results

Command or Method: `./bin/ask skills resolve he-spec --json`

Result: pass

Evidence: trace `4935af2f-98d2-4811-9dd0-7519366143b7`; resolved canonical `Plugins/harness-engineering/skills/he-spec/SKILL.md`.

Confidence: High

Blocks Closure: no

Command or Method: `./bin/ask skills list --json`

Result: pass

Evidence: trace `8dc6a05a-92f3-47c9-b937-b1c43604fd8b`; policy identity `8c69fbfa81b89658`.

Confidence: High

Blocks Closure: no

Command or Method: `./bin/ask skills sync --scope workspace --projection rooted --dry-run --json`

Result: pass

Evidence: trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`; `validation_status: pass`; `219` writes, `6` deletes, `1` symlink; command surface has `95` handles; plugin-cache logs and `plugin_cache_writes` are present.

Confidence: High

Blocks Closure: no

Command or Method: `./bin/ask repo doctor --json --robot`

Result: pass with diagnostic debt

Evidence: trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e`; `blocking: false`; catalog parity, runtime budget, projection sync, and command handles pass; repo surface reports `4544 diagnostic finding(s)`.

Confidence: High

Blocks Closure: no for local code closure; no for this slice's blocker gates; the diagnostic debt remains separate follow-up.

Command or Method: `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q`

Result: pass

Evidence: `9 passed`

Confidence: High

Blocks Closure: no

Command or Method: `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -q`

Result: pass

Evidence: `25 passed in 3.77s`

Confidence: High

Blocks Closure: no

Command or Method: `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`

Result: pass

Evidence: `PASS .harness/specs/agent-skills-ask-control-plane-decomposition-spec.md`

Confidence: High

Blocks Closure: no

Command or Method: `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`

Result: pass

Evidence: `PASS .harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`

Confidence: High

Blocks Closure: no

Command or Method: `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`

Result: pass

Evidence: `docs-lint mode=warn scanned_files=177 errors=0 warnings=0`

Confidence: High

Blocks Closure: no

Command or Method: `git diff --check`

Result: pass

Evidence: no output and exit code 0

Confidence: High

Blocks Closure: no

# Eval Gate Matrix

Gate: Routing Determinism

Expected: generated command handles continue resolving through canonical sources, and `skills list` remains readable.

Actual: `he-spec` resolves to the canonical Harness Engineering source; `skills list` passes with policy identity `8c69fbfa81b89658`.

Status: pass

Evidence: traces `4935af2f-98d2-4811-9dd0-7519366143b7` and `8dc6a05a-92f3-47c9-b937-b1c43604fd8b`.

Confidence: High

Blocks Closure: no

Required Action: none for local closure.

Gate: Plugin Cache Contract

Expected: rooted dry-run preserves plugin cache write fields, logs, command-surface handle count, and validation status.

Actual: rooted dry-run passes with `validation_status: pass`, `plugin_cache_writes`, plugin cache log lines, `95` command handles, and mutation counts `219/6/1`.

Status: pass

Evidence: trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`.

Confidence: High

Blocks Closure: no

Required Action: none for local closure.

Gate: Repo Health

Expected: repo doctor has no blocking catalog parity, runtime budget, projection sync, or command-handle failures.

Actual: repo doctor reports `blocking: false`; repo surface diagnostic debt remains warning-only.

Status: pass

Evidence: trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e`.

Confidence: High

Blocks Closure: no for this local slice.

Required Action: keep repo-surface diagnostic debt outside this slice unless separately selected.

Gate: Linear Traceability

Expected: spec and plan traceability lint pass, and Linear identifiers map to `JSC-284` through `JSC-287`.

Actual: spec and plan traceability lint pass; local artifacts contain the Linear identifiers; live Linear fetches verified `JSC-284` through `JSC-287` are Done.

Status: pass

Evidence: traceability lint passed; Linear fetches verified completed statuses and completion timestamps for all four issues.

Confidence: High

Blocks Closure: no.

Required Action: none for Linear closure.

# Drift Validation

Architecture Drift: Improved

Routing Drift: Neutral

Context Drift: Improved

Governance Drift: Neutral

Agent-Native Drift: Improved

Moat Drift: Improved

# Architecture Integrity Check

Fact: Plugin cache behavior was extracted into service files while public command validation stayed green.

Interpretation: The slice reduces command-module responsibility without changing the public `./bin/ask` contract.

Assumption: The selected service extraction files are staged together and unrelated dirty surfaces are not included accidentally.

Evidence: `Infrastructure/scripts/lib/ask/services/plugin_cache.py`, `Infrastructure/scripts/lib/ask/services/plugin_sources.py`, rooted sync dry-run trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`, repo doctor trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e`.

Affected Files/Modules: `ask.commands.skills`, `ask.commands.plugins`, `ask.services.plugin_cache`, `ask.services.plugin_sources`.

Confidence: High

Operational Impact: Better local reasoning around plugin cache behavior with no observed command drift.

Blocks Completion: no for local implementation; yes for Linear closure until live tracker refresh is complete.

# Routing Determinism Check

Fact: `he-spec` resolution and `skills list` pass after the extraction.

Interpretation: Generated command handles and visible runtime surface remain usable.

Assumption: The live runtime projection remains consistent with the dry-run plan until the final commit stage.

Evidence: `./bin/ask skills resolve he-spec --json` trace `4935af2f-98d2-4811-9dd0-7519366143b7`; `./bin/ask skills list --json` trace `8dc6a05a-92f3-47c9-b937-b1c43604fd8b`.

Affected Files/Modules: `.agents/skills/**`, `.skillsets/command-surface.json`, `Infrastructure/scripts/lib/ask/commands/skills.py`.

Confidence: High

Operational Impact: Future agents can still resolve routed HE handles and inspect the runtime surface.

Blocks Completion: no.

# Context Load Check

Fact: The extraction moves plugin-cache internals out of the command module and records closure evidence in a dedicated eval report.

Interpretation: Future agents no longer need to reason through the whole command module for plugin-cache behavior.

Assumption: Future slices continue the staged decomposition instead of adding new responsibilities back into `commands/skills.py`.

Evidence: `.harness/refactors/ask-control-plane-decomposition.md`, `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`, service files under `Infrastructure/scripts/lib/ask/services/`.

Affected Files/Modules: `Infrastructure/scripts/lib/ask/commands/skills.py`, `Infrastructure/scripts/lib/ask/services/**`.

Confidence: High

Operational Impact: Reduced architecture cognition cost for the touched concern.

Blocks Completion: no.

# Agent-Native Check

Fact: The slice preserves machine-readable command outputs, trace IDs, and eval-backed closure evidence.

Interpretation: The change is agent-native in the operational sense: an agent can reproduce the validation path from local artifacts and commands.

Assumption: Final staging will preserve proof artifacts rather than committing only code.

Evidence: `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`, `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`, traces listed in Functional Validation Results.

Affected Files/Modules: `.harness/plan/**`, `.harness/evals/**`, `Infrastructure/scripts/lib/ask/**`.

Confidence: High

Operational Impact: Better future-agent handoff and less reliance on chat memory.

Blocks Completion: no.

# Governance Simplicity Check

Fact: No new Linear objects or labels were created during this closure eval; the report maps to existing `JSC-284` through `JSC-287`, and those existing issues are now Done.

Interpretation: Governance did not expand beyond the approved slice.

Assumption: The commit stage will avoid bundling unrelated `.harness/linear`, review, or generated surfaces unless explicitly selected.

Evidence: plan status `plan_ask_005_complete_linear_resolved`; Linear issue fetches verified Done statuses; closure proof comment `a54b9452-af8c-4498-bbba-ed61f92bd773` was posted to `JSC-284`.

Affected Files/Modules: `.harness/linear/agent-skills-linear-plan.md`, `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`, `.harness/evals/**`.

Confidence: High.

Operational Impact: Keeps local proof artifacts aligned with the tracker closure that was actually performed.

Blocks Completion: no.

# Moat Protection Check

Fact: The slice protects the `./bin/ask` control-plane contract, source/projection parity, runtime-budget policy, and proof taxonomy.

Interpretation: The work strengthens the operational moat by improving deterministic command internals and proof-backed lifecycle language.

Assumption: Future work does not treat structural audit as outcome proof and does not promote skills without proof gates.

Evidence: `.harness/core/architecture-invariants.md`, `.harness/core/execution-invariants.md`, `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`, repo doctor trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e`.

Affected Files/Modules: `./bin/ask` command implementation, runtime-budget validator, proof taxonomy ADR, `.harness/core/**`.

Confidence: High

Operational Impact: Better trust in the control plane and clearer proof semantics.

Blocks Completion: no.

# Proof Artifacts

Produced:

- `.harness/evals/agent-skills-jsc-284-eval.md`
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

Required:

- HE eval report for `JSC-284`
- detailed local closure eval
- proof taxonomy ADR for `JSC-287`
- traceability lint evidence
- focused test evidence
- repo doctor evidence

Missing: none for Linear closure.

Blocks Completion: no.

Attach or Link Back to Linear: complete through `JSC-284` closure proof comment `a54b9452-af8c-4498-bbba-ed61f92bd773`.

# Failures / Regressions

Failure or Regression: previous live Linear refresh unavailable.

Evidence: earlier recorded connector blocker `INVALID_ARGUMENT` / `Tool research not found`; later Linear issue fetches succeeded and verified Done state.

Required Corrective Action: complete.

Follow-Up Justified: no for Linear closure.

Blocks Closure: no.

Failure or Regression: repo-surface diagnostic debt remains.

Evidence: repo doctor trace `5954fd8e-642d-4fc6-8d9b-b723cff7269e` reports `4544 diagnostic finding(s)` while `blocking: false`.

Required Corrective Action: do not fold into this slice unless separately selected; consider a future repo-surface triage slice.

Follow-Up Justified: later, not now.

Blocks Closure: no for this HE slice.

# Linear Completion Recommendation

Classification: Complete

Recommended Linear Status: done. `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` are completed in Linear.

Required Linear Comment/Update: complete. Closure proof comment `a54b9452-af8c-4498-bbba-ed61f92bd773` was posted to `JSC-284`.

Issues Closed: `JSC-285`, `JSC-286`, `JSC-287`, then `JSC-284`.

Issues to Reopen: none known.

Issues to Leave Open: none for this closure set.

New Follow-Up Issues: none from this eval. Do not create issue noise for repo-surface debt inside this slice.

Labels to Add/Remove: none.

Milestone Completion: Linear issue closure complete; selected-files commit review remains separate from tracker closure.

Project Status Change: none.

Status Update Needed: no for issue closure.

Proof Artifacts to Attach or Link:

- `.harness/evals/agent-skills-jsc-284-eval.md`
- `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
- `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md`

# Follow-Up Work

Classification: Now

Target Linear Project: `agent-skills`

Parent Issue or Milestone: `JSC-284`

Reason: live Linear refresh requirement is already satisfied for this slice; only selected-file commit staging review remains.

Priority: High for closure; not a code blocker.

Labels: existing `architecture`, `Agent`, `Refactor` labels are sufficient.

Agent-Safe or Human-Review Required: Agent-assisted; human review required before final status mutation.

Classification: Later

Target Linear Project: `agent-skills`

Parent Issue or Milestone: separate future repo-surface triage slice if selected.

Reason: repo doctor reports non-blocking repo-surface diagnostic debt.

Priority: Normal unless it becomes blocking.

Labels: `Governance` or existing architecture label only if selected.

Agent-Safe or Human-Review Required: Agent-assisted.

# Core / ADR Update Recommendation

Core Update: no core update required.

ADR Update: no ADR update required for this slice.

Rationale: the proof taxonomy ADR is present, and existing core invariants already cover source/projection separation, command contract preservation, staged reversible execution, and proof-backed closure.

Required Action: none before local closure; refresh Linear before tracker closure.

# Evidence & Traceability Matrix

Conclusion: local implementation satisfies approved slice boundaries.

Fact: service extraction completed for plugin cache behavior and later phases were not started.

Interpretation: architecture drift improved by moving a bounded concern out of the command module.

Assumption: final commit will stage only selected slice files.

Evidence: `Infrastructure/scripts/lib/ask/services/plugin_cache.py`; `Infrastructure/scripts/lib/ask/services/plugin_sources.py`; detailed eval changed-files section.

Affected Files/Modules: `ask.commands.skills`, `ask.commands.plugins`, `ask.services.plugin_cache`, `ask.services.plugin_sources`.

Command Output or Inspection Method: file inspection plus rooted sync dry-run trace `ae7aa5a8-0578-4f32-9fb9-6de30ea455a7`.

Confidence: High

Operational Impact: lower future change amplification in the ask control plane.

Blocks Completion: no for local closure.

Conclusion: public command behavior is preserved for the evaluated gates.

Fact: resolve, list, rooted sync dry-run, repo doctor, focused tests, docs lint, traceability lint, and diff check passed.

Interpretation: no observed public command drift in the selected behavior surface.

Assumption: untested command paths outside plugin cache are unaffected by the extracted helpers.

Evidence: validation traces and test outcomes recorded above.

Affected Files/Modules: `./bin/ask`, skill command surfaces, plugin cache dry-run outputs.

Command Output or Inspection Method: exact validation commands in Functional Validation Results.

Confidence: High for tested paths; medium for unrelated command paths.

Operational Impact: preserves agent-facing command reliability.

Blocks Completion: no for local closure.

Conclusion: Linear closure is complete.

Fact: live Linear issue fetches verified `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` are Done.

Interpretation: the implementation slice and tracker closure now agree.

Assumption: selected-file commit staging remains a separate delivery gate because the worktree includes broader generated/projection churn.

Evidence: live Linear fetches returned `status: Done` / `statusType: completed` for all four issues; `JSC-284` completion proof comment id is `a54b9452-af8c-4498-bbba-ed61f92bd773`.

Affected Files/Modules: `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`, `.harness/evals/**`, Linear `JSC-284` through `JSC-287`.

Command Output or Inspection Method: recorded connector failure and local artifact inspection.

Confidence: High

Operational Impact: prevents stale local artifacts from contradicting completed tracker state.

Blocks Completion: no.
