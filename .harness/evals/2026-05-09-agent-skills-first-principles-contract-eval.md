---
schema_version: 1
artifact_id: agent-skills-first-principles-contract-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-first-principles-contract
title: First-Principles Contract Eval
harness_stage: he-eval-report
status: accepted
date: 2026-05-09
traceability_required: false
origin: .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md
linear_issue: not_created
linear_milestone: HE First-Principles Gate (proposed)
---

# First-Principles Contract Eval

## Executive Eval Summary

Status: Complete with follow-up.

Linear Completion Recommendation: no Linear mutation is required because no
Linear issue exists. The user accepted this eval on 2026-05-09, so if a Linear
issue is created later this slice may use `Complete with follow-up` with the
caveats below.

Primary Blockers: no implementation blocker found. Full runtime picker-cache
freshness remains caveated by the known workspace plugin picker cache permission
warning from sync.

Confidence: high for the selected implementation slice; medium for runtime
picker freshness because `.agents/plugins-runtime/cache/**` refresh still
reported a permission warning.

## Evaluated Slice

Linear Project: `agent-skills` proposed only.

Linear Milestone: `HE First-Principles Gate` proposed only.

Linear Parent Issue: not created.

Linear Sub-Issues: not created.

Refactor Program: not applicable.

Plugin Harness Engineering Spec:
`.harness/specs/2026-05-09-agent-skills-first-principles-contract-spec.md`.

Affected Files/Modules:

- `Plugins/harness-engineering/references/first-principles-contract.md`
- `Plugins/harness-engineering/references/deferred-context-index.md`
- `Plugins/harness-engineering/references/lifecycle-tracer-evals.yaml`
- `Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`
- `Plugins/harness-engineering/skills/he-brainstorm/**`
- `Plugins/harness-engineering/skills/he-spec/**`
- `Plugins/harness-engineering/skills/he-plan/**`
- `Plugins/harness-engineering/skills/he-strategy/**`
- `Plugins/harness-engineering/skills/he-linear-plan/**`
- `Plugins/harness-engineering/skills/he-eval-report/**`
- `Plugins/harness-engineering/skills/he-code-review/**`
- generated `.skillsets/**` projections and command surface

Affected Workflows: HE brainstorm survivor selection, spec scoping, plan
slicing, strategy compression, Linear planning, eval closure, and code review
readiness.

Related ADRs: none.

Related Core Invariants: deferred context loading, deterministic routing,
proof-before-closure, and no new standalone lifecycle stage without repeated
use evidence.

## Linear Definition of Done Status

Artifact Path:
`.harness/evals/2026-05-09-agent-skills-first-principles-contract-eval.md`.

Definition of Done Status: satisfied for the selected implementation slice. No
Linear object exists, and the user accepted this eval on 2026-05-09.

Closure Safety: safe to review. Linear closure is not applicable unless a Linear
issue or milestone is created.

## Linear Backlink Map

Linear Project: `agent-skills` proposed.

Linear Milestone: `HE First-Principles Gate` proposed.

Linear Parent Issue: missing because not created.

Linear Sub-Issues: missing because not created.

Linear Status Recommendation: leave uncreated unless the user wants tracked
execution state. If created later, use `Complete with follow-up` and preserve
the picker-cache caveat.

Proof Artifact Links:

- `.harness/specs/2026-05-09-agent-skills-first-principles-contract-spec.md`
- `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md`
- `.harness/review/2026-05-09-agent-skills-first-principles-contract-technical-review.md`
- `.harness/review/2026-05-09-agent-skills-first-principles-contract-plan-technical-review.md`
- this eval artifact

Missing Identifiers: Linear parent issue and milestone identifiers.

Traceability Repair: create or confirm Linear identifiers only if the user wants
this work tracked externally; otherwise keep the proof in `.harness`.

## Source Artifact Trace

Linear Plan:
`.harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md`.

Refactor Program: not applicable.

Plugin HE Spec:
`.harness/specs/2026-05-09-agent-skills-first-principles-contract-spec.md`.

ADRs: none.

Core Invariants: no dedicated core update was required; the invariant is encoded
as a shared HE reference contract.

Other Source Artifacts:

- `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md`
- `Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md`
- `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-contract.md`
- `Plugins/harness-engineering/skills/he-eval-report/references/eval-report-template.md`

## Planned Proof Check

Promised Proof From Source Artifacts: first-principles contract exists, deferred
context index references it, seven lifecycle skills reference it, required eval
case IDs exist, no `he-first-principles` skill exists, projections are synced,
and validation commands pass.

Proof Planned Before Implementation: yes.

Proof Produced: wiring checker passed; existing gate/domain/XP/deferred
validators passed; YAML eval files parsed; projections and command handles
passed; seven strict skill audits passed.

Proof Missing: full plugin-wide runtime eval lane was not run for this narrow
slice. It was not required by the plan except for plugin-level confidence
claims, which this eval does not make.

Interpretation: the selected phase met its planned implementation proof.

Blocks Closure: no.

Closure Caveat: Linear closure remains not applicable because no Linear issue
exists.

## Functional Validation Results

Command or Method:
`python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py --json`

Result: pass.

Evidence: returned `status: "pass"` with no errors.

Confidence: high.

Blocks Closure: no.

Command or Method:
`python3 -m py_compile Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`

Result: pass.

Evidence: exited `0`.

Confidence: high.

Blocks Closure: no.

Command or Method:
`./bin/ask skills sync --scope workspace --projection rooted --json --robot`

Result: partial.

Evidence: command returned `status: "success"` and validation status pass, but
reported warning `PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED` for
`.agents/plugins-runtime/cache/agent-skills-local/harness-engineering/.codex-repo-plugin-source`.

Confidence: high for rooted projections and manifests; medium for picker-cache
freshness.

Blocks Closure: no.

Closure Caveat: this blocks any claim that the workspace plugin picker cache has
fully refreshed.

Command or Method:
`./bin/ask skills handles --check --json --robot`

Result: pass.

Evidence: returned command surface status pass, 98 handles, 0 violations.

Confidence: high.

Blocks Closure: no.

Command or Method:
`python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope all`

Result: pass.

Evidence: all listed projection parity checks passed, including
`cache-harness-engineering`.

Confidence: high.

Blocks Closure: no.

Command or Method:
strict audits for `he-brainstorm`, `he-strategy`, `he-spec`, `he-plan`,
`he-linear-plan`, `he-eval-report`, and `he-code-review`.

Result: pass.

Evidence: every audit returned `status: "success"` and `RESULT: PASS`.

Confidence: high.

Blocks Closure: no.

Command or Method:
`./bin/ask repo doctor --json --robot`

Result: pass with diagnostic debt.

Evidence: `blocking: false`; reported repo surface diagnostic debt as
non-blocking.

Confidence: high.

Blocks Closure: no.

## Eval Gate Matrix

Gate: Contract wiring.

Expected: contract file, fields, deferred index, lifecycle skills, eval IDs, and
no standalone skill.

Actual: checker passed with no errors.

Status: pass.

Evidence:
`python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py --json`.

Confidence: high.

Blocks Closure: no.

Required Action: none.

Gate: Existing HE gate/domain/XP/deferred validators.

Expected: new contract does not break adjacent HE contracts.

Actual: gate selection, domain contract, XP contract, and deferred context index
checks passed.

Status: pass.

Evidence:

- `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json`
- `python3 Plugins/harness-engineering/scripts/check_domain_contract_wiring.py --json`
- `python3 Plugins/harness-engineering/scripts/check_xp_contract_wiring.py --json`
- `python3 Plugins/harness-engineering/scripts/check_deferred_context_index.py --json`

Confidence: high.

Blocks Closure: no.

Required Action: none.

Gate: Eval YAML parse.

Expected: touched eval files remain parseable YAML.

Actual: parse passed with the PyYAML virtualenv.

Status: pass.

Evidence:
`python3 -c "import pathlib,yaml; [yaml.safe_load(pathlib.Path(p).read_text()) for p in ['Plugins/skill-factory/skills/code_quality_review/skill-builder/references/evals.yaml','Plugins/plugin-factory/skills/code_quality_review/plugin-builder/references/evals.yaml']]; print('ok')"` -> pass.

Confidence: high.

Blocks Closure: no.

Required Action: none.

Gate: Projection sync.

Expected: rooted projections and command surface reflect canonical edits.

Actual: rooted sync succeeded, command handles passed, projection integrity
passed; plugin picker cache refresh warning remains.

Status: partial.

Evidence:

- `./bin/ask skills sync --scope workspace --projection rooted --json --robot`
- `./bin/ask skills handles --check --json --robot`
- `python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope all`

Confidence: medium-high.

Blocks Closure: no.

Closure Caveat: this blocks claims that plugin picker cache refresh is fully
clean.

Required Action: resolve `.agents/plugins-runtime/cache/**` permission warning
before claiming full picker-cache freshness.

Gate: Skill audits.

Expected: changed lifecycle skills pass strict audit.

Actual: all seven targeted lifecycle skill audits passed.

Status: pass.

Evidence: `./bin/ask skills audit <skill-path> --level strict --json --robot`.

Confidence: high.

Blocks Closure: no.

Required Action: none.

Gate: Linear traceability.

Expected: eval identifies Linear identifiers or states missing identifiers.

Actual: no Linear issue exists; eval records proposed project/milestone and
missing parent issue.

Status: partial.

Evidence: source `.harness/linear/**` plan and this eval.

Confidence: high.

Blocks Closure: no.

Required Action: create or confirm a Linear issue only if external tracking is
desired; if one is created later, link this accepted eval before closure.

## Agentic Eval Validity

Evaluated Capability / Task: HE lifecycle should reject copied-process expansion
unless a verified Harness Engineering failure exists.

Task Validity: high. The task is directly sourced from the approved spec and
plan.

Outcome Validity: high for static wiring and eval-case presence.

Trajectory / Transcript Evidence: implementation was performed phase-by-phase
from the approved plan; no standalone skill was created.

Grader Coverage: static checker covers contract, skill references, eval IDs, and
forbidden standalone skill. Strict skill audits cover package readiness.

Trial Policy: not applicable; no stochastic eval benchmark was run.

Pass@k / Pass^k Reporting: not applicable.

Authorization Validator: no external protected action was taken.

Saturation / Maintenance Signal: checker creates a deterministic regression
guard for future maintenance.

Blocks Completion: no

Closure Caveat: plugin-wide behavioral confidence still requires a full release
eval lane.

Required Action: run HE lifecycle release evals only before plugin-wide
confidence claims or release closure.

## Side-Effect Authorization

Protected Action: Linear creation, status mutation, PR mutation, commit, push,
or merge.

User Authorization Evidence: user authorized phase continuation, not external
mutation or commit.

Agent Justification: no protected external actions were performed.

External Party Influence: none.

Validator Decision: exempt

Validator Confidence: high

Suggested Next Step: preserve the accepted eval caveats before any Linear
closure or commit.

Blocks Completion: no

## Domain Model Integrity Check

Domain Model Status: not applicable.

Bounded Context: Harness Engineering lifecycle routing and proof artifacts.

Aggregate / Invariant Proof: no production domain aggregate changed.

Model-Code-Test Language Match: not applicable.

Translation Boundary: not applicable.

Closure Impact: no domain-model closure blocker.

Evidence: changed files are HE skill/reference/eval surfaces, not application
domain code.

Blocks Completion: no

## Drift Validation

Architecture Drift: Improved
Evidence: the contract blocks new lifecycle surface area that is justified only
by analogy or copied templates.

Routing Drift: Improved
Evidence: deferred context routing names when to load the contract while
avoiding a new public `he-first-principles` route.

Context Drift: Improved
Evidence: one shared reference adds context only when triggered; skill hooks
remain thin.

Governance Drift: Improved
Evidence: Linear and governance expansion now require verified failure evidence
and smallest-mechanism proof.

Agent-Native Drift: Improved
Evidence: headless assumptions and Type 1/Type 2 handling reduce hidden
ambiguity for future agents.

Moat Drift: Improved
Evidence: the change protects HE's proof-before-process philosophy and reduces
false sophistication.

## Architecture Integrity Check

Conclusion: preserved.

Evidence: no standalone `he-first-principles` skill directory was created; the
contract is a shared reference with thin lifecycle hooks.

Affected Files/Modules: HE references, lifecycle skills, eval files, checker.

Confidence: high.

Blocks Completion: no

## Domain Model Semantics Check

Conclusion: not applicable to production domain behavior.

Bounded Context: HE lifecycle.

Canonical Terms: first-principles contract, verified failure, smallest effective
mechanism, Type 1, Type 2, Do Not Create.

Aggregate Invariants: no aggregate changed.

Lifecycle Ownership: contract owns doctrine; lifecycle skills own local trigger
points; eval files own stage-specific behavioral checks.

Translation Evidence: deferred context index maps trigger to reference; checker
asserts references and eval IDs.

Scenario or Test Evidence: static checker and stage-local eval case IDs.

Confidence: high.

Blocks Completion: no

## Routing Determinism Check

Conclusion: improved.

Evidence: deferred context index includes the contract in Runtime Reference Map
and Conditional Loading Map; lifecycle skills point to the same reference path.

Affected Files/Modules:
`Plugins/harness-engineering/references/deferred-context-index.md` and seven
lifecycle `SKILL.md` files.

Confidence: high.

Blocks Completion: no

## Context Load Check

Conclusion: acceptable.

Evidence: contract body is centralized; lifecycle skills only add one procedure
hook and one reference each.

Affected Files/Modules: lifecycle `SKILL.md` files and first-principles
reference.

Confidence: high.

Blocks Completion: no

## Agent-Native Check

Conclusion: improved.

Evidence: contract requires headless assumption records, smallest safe
assumption, confidence, overturning evidence, and recovery path; lifecycle eval
case covers headless behavior.

Affected Files/Modules:
`Plugins/harness-engineering/references/first-principles-contract.md` and
`Plugins/harness-engineering/references/lifecycle-tracer-evals.yaml`.

Confidence: high.

Blocks Completion: no

## Governance Simplicity Check

Conclusion: improved.

Evidence: HE Linear planning now points cognition-only observations to
`.harness`, `Later`, or `Do Not Create`; no new governance stage or handle was
created.

Affected Files/Modules:
`Plugins/harness-engineering/skills/he-linear-plan/SKILL.md` and
`Plugins/harness-engineering/references/first-principles-contract.md`.

Confidence: high.

Blocks Completion: no

## Moat Protection Check

Conclusion: improved.

Evidence: the contract reinforces HE's distinctive behavior: preserve intent,
avoid false completion, reject process copying, and require proof before closure.

Affected Files/Modules: HE lifecycle skills and eval surfaces.

Confidence: high.

Blocks Completion: no

## Proof Artifacts

Produced:

- first-principles contract reference
- lifecycle skill hooks
- deferred context index routing
- stage-local first-principles eval cases
- lifecycle tracer headless eval case
- static wiring checker
- rooted projection sync
- strict skill audit evidence
- this eval report

Required:

- accepted eval steering before closure recommendation is applied
- optional plugin-wide release eval lane before plugin-wide confidence claims

Missing:

- clean `.agents/plugins-runtime/cache/**` picker-cache refresh due permission
  warning
- Linear backlink identifiers because no Linear issue exists

Planned Before Implementation: yes.

Blocks Completion: no

Closure Caveat: external closure remains blocked only if new external tracking
is introduced without preserving this accepted eval result.

Attach or Link Back to Linear: attach this eval only if the proposed Linear issue
is created.

## Failures / Regressions

Failure or Regression: workspace plugin picker cache warning during sync.

Evidence:
`PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED` from `./bin/ask skills sync --scope workspace --projection rooted --json --robot`.

Required Corrective Action: rerun sync in an environment that can mutate
`.agents/plugins-runtime/cache/**` or repair sandbox permissions before claiming
picker-cache freshness.

Follow-Up Justified: Next, only if picker freshness matters for the immediate
PR/release claim.

Blocks Closure: no.

Closure Caveat: full runtime picker-cache confidence remains blocked by the
cache refresh permission warning.

Failure or Regression: repo surface diagnostic debt.

Evidence: `./bin/ask repo doctor --json --robot` reports 7444 repo-surface
diagnostic findings as non-blocking diagnostic debt.

Required Corrective Action: use `./bin/ask repo surface --json --robot` in a
separate surface-ownership slice.

Follow-Up Justified: Do Not Create for this slice because it pre-exists and is
not caused by the first-principles contract.

Blocks Closure: no.

## Linear Completion Recommendation

Classification: Complete with follow-up.

Recommended Linear Status: do not mutate Linear. If a Linear issue is created
later, mark it `Complete with follow-up` only with this eval linked and the
picker-cache caveat preserved.

Required Linear Comment/Update: "First-principles contract implementation
completed for the selected HE slice. Static wiring, eval case presence, YAML
parse, projections, command handles, projection integrity, and seven strict
skill audits passed. Picker-cache freshness remains limited by
PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED; no standalone he-first-principles skill
was created."

Issues to Close: none.

Issues to Reopen: none.

Issues to Leave Open: none.

New Follow-Up Issues: do not create by default.

Labels to Add/Remove: none.

Milestone Completion: not applicable until milestone exists.

Project Status Change: none.

Status Update Needed: no.

Proof Artifacts to Attach or Link: this eval and the validation summary above.

## Follow-Up Work

Classification: Next.

Target Linear Project: `agent-skills`.

Parent Issue or Milestone: `HE First-Principles Gate`, if created.

Reason: resolve `.agents/plugins-runtime/cache/**` permission warning if full
picker-cache confidence is needed.

Priority: Normal.

Labels: `Infrastructure`, `Plugin`, or existing closest equivalents.

Agent-Safe or Human Review Required: agent-assisted; permission model may need
human review.

Classification: Do Not Create.

Target Linear Project: none.

Parent Issue or Milestone: none.

Reason: repo surface diagnostic debt is broad and pre-existing; creating a
follow-up from this slice would be issue noise.

Priority: No priority.

Labels: none.

Agent-Safe or Human Review Required: not applicable.

## Core / ADR Update Recommendation

Core Update: not required. The durable operating rule is encoded in the shared
HE reference contract and lifecycle evals.

ADR Update: not required. No irreversible architecture decision was made beyond
rejecting a standalone skill, and the wiring checker preserves that constraint.

Reason: adding an ADR/core file would duplicate the contract and increase
context load without extra enforcement.

## Evidence & Traceability Matrix

Conclusion: contract implemented as reference, not new skill.

Fact: `Plugins/harness-engineering/references/first-principles-contract.md`
exists and `Plugins/harness-engineering/skills/he-first-principles` does not.

Interpretation: this matches the plan's smallest-mechanism approach.

Assumption: future first-principles usage remains cross-cutting rather than a
standalone workflow.

Evidence: `check_first_principles_contract_wiring.py --json` passed.

Affected Files/Modules: HE reference and lifecycle skill surfaces.

Command or Inspection Method: static checker plus `git status`.

Confidence: high.

Operational Impact: reduces process-copying drift without adding a handle.

Blocks Completion: no

Conclusion: lifecycle behavior is wired.

Fact: seven lifecycle skills reference the first-principles contract.

Interpretation: the contract can influence survivor selection, specs, plans,
strategy, Linear plans, eval closure, and code review.

Assumption: stage-local hooks are enough because the contract is reference-owned.

Evidence: `rg -n "first-principles"` and strict skill audits.

Affected Files/Modules: `he-brainstorm`, `he-spec`, `he-plan`, `he-strategy`,
`he-linear-plan`, `he-eval-report`, `he-code-review`.

Command or Inspection Method: `rg`, `./bin/ask skills audit ...`.

Confidence: high.

Operational Impact: improves deterministic steering and future-agent restraint.

Blocks Completion: no

Conclusion: eval coverage exists.

Fact: nine first-principles eval IDs exist in expected files.

Interpretation: future regressions can be detected as behavior fixtures rather
than relying on prose.

Assumption: the eval runner consumes these YAML fixtures as the existing HE
workflow expects.

Evidence: `rg` for eval IDs and PyYAML parse pass.

Affected Files/Modules: stage-local eval YAML files and lifecycle tracer evals.

Command or Inspection Method: `rg`; PyYAML safe-load.

Confidence: high for file validity; medium for behavioral scoring until release
evals are run.

Operational Impact: improves anti-drift enforcement.

Blocks Completion: no

Conclusion: projections are current enough for source handoff.

Fact: rooted sync, command handles, and projection integrity passed.

Interpretation: canonical and projected skill state are aligned, with a scoped
picker-cache caveat.

Assumption: picker-cache warning does not affect rooted handle validation.

Evidence: sync success, handles pass, projection integrity pass, sync warning.

Affected Files/Modules: `.skillsets/**`, command surface, plugin cache mirror.

Command or Inspection Method: `./bin/ask skills sync`, `./bin/ask skills handles`,
projection integrity script.

Confidence: medium-high.

Operational Impact: skill handles and projections are usable; picker-cache claim
must stay caveated.

Blocks Completion: no

Closure Caveat: full picker-cache freshness claims remain blocked.
