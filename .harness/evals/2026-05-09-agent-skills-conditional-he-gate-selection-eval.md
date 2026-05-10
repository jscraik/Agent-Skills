---
schema_version: 1
artifact_id: 2026-05-09-agent-skills-conditional-he-gate-selection-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-conditional-he-gate-selection
title: Agent Skills Conditional HE Gate Selection Eval
harness_stage: he-eval-report
status: blocked_release_confidence
date: 2026-05-09
traceability_required: true
origin: .harness/plan/2026-05-09-agent-skills-conditional-he-gate-selection-plan.md
linear_issue: JSC-299
linear_status: created
linear_milestone: HE Authority And Proof Hardening
---

# Agent Skills Conditional HE Gate Selection Eval

## Executive Eval Summary

Status: static wiring confidence and sliced live smoke confidence are supported;
plugin-wide release confidence remains blocked.

The conditional gate-selection slice implemented the planned contract, lifecycle
skill wiring, negative eval cases, validators, and rooted projections. Static
validation gates pass. The lifecycle release-eval lane no longer rejects the
planned command because `he-spec` and `he-code-review` are now supported by the
runner. A new case-filtered live smoke lane now passes for the changed
`he-router` and `he-eval-report` behavior, but the full lifecycle eval lane
still fails or times out and cannot be used as plugin-wide release proof.

Linear Completion Recommendation: `Blocked` for plugin-wide release-confidence
closure.

Recommended local status: keep the implementation as a candidate patch with
blocked plugin-wide release proof. It is now reasonable to claim changed-surface
sliced live smoke confidence for the two repaired cases, but not near-complete
plugin confidence until the full live lifecycle eval lane passes or is
explicitly replaced by an approved equivalent proof lane.

## Evaluated Slice

Linear Project: agent-skills.

Linear Milestone: HE Authority And Proof Hardening.

Linear Parent Issue: JSC-299.

Linear Sub-Issues: none.

Source Spec:

- `.harness/specs/2026-05-09-agent-skills-conditional-he-gate-selection-spec.md`

Source Plan:

- `.harness/plan/2026-05-09-agent-skills-conditional-he-gate-selection-plan.md`

Affected workflows:

- HE lifecycle route selection.
- HE closure-proof confidence claims.
- HE eval report closure recommendations.
- HE rooted projection sync and command-handle validation.

Affected canonical files:

- `Plugins/harness-engineering/references/gate-selection-contract.md`
- `Plugins/harness-engineering/references/domain-model-production-contract.md`
- `Plugins/harness-engineering/references/deferred-context-index.md`
- `Plugins/harness-engineering/references/lifecycle-exit-contract.md`
- `Plugins/harness-engineering/skills/he-router/SKILL.md`
- `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- `Plugins/harness-engineering/skills/he-code-review/SKILL.md`
- `Plugins/harness-engineering/skills/he-eval-report/SKILL.md`
- `Plugins/harness-engineering/skills/he-brainstorm/SKILL.md`
- `Plugins/harness-engineering/skills/he-plan/SKILL.md`
- `Plugins/harness-engineering/skills/he-work/SKILL.md`
- `Plugins/harness-engineering/skills/he-strategy/SKILL.md`
- `Plugins/harness-engineering/scripts/check_gate_selection_wiring.py`
- `Plugins/harness-engineering/scripts/check_domain_contract_wiring.py`
- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`

## Linear Definition of Done Status

Definition of Done Status: blocked for release confidence.

Reason: the eval artifact exists and static gates pass, but lifecycle live evals
do not pass. The source plan explicitly states lifecycle smoke evals block
release-confidence claims.

Safe closure classification:

- Static wiring confidence: supported.
- Release confidence: blocked.
- Linear closure recommendation: blocked for plugin-wide release confidence
  under `JSC-299` until lifecycle eval timeout proof is repaired.

## Linear Backlink Map

Linear Project: agent-skills.

Linear Milestone: HE Authority And Proof Hardening.

Linear Parent Issue: JSC-299.

Linear Sub-Issues: none.

Linear Status Recommendation: `Blocked` if mapped to a Linear closure decision.

Proof Artifact Links:

- `.harness/evals/2026-05-09-agent-skills-conditional-he-gate-selection-eval.md`
- `.harness/specs/2026-05-09-agent-skills-conditional-he-gate-selection-spec.md`
- `.harness/plan/2026-05-09-agent-skills-conditional-he-gate-selection-plan.md`
- `.harness/session-evidence/he-phase-heartbeat/conditional-gate-selection-20260509-summary.json`
- `Infrastructure/artifacts/skills/he-router/20260509-115700-063915/scorecard.json`
- `Infrastructure/artifacts/skills/he-eval-report/20260509-115709-391859/scorecard.json`

Traceability: linked to `JSC-299`. Static plugin source validation is supported,
but Linear closure remains blocked by plugin-wide release-confidence proof.

## Source Artifact Trace

Fact: the plan bounded the implementation to conditional gate selection and
explicitly excluded lifecycle eval-timeout repair from the original slice.

Evidence:

- The plan required a gate-selection contract, high-traffic lifecycle wiring,
  negative eval cases, static wiring checks, strict skill audits, rooted sync,
  and lifecycle smoke evidence.
- The plan stated lifecycle timeout repair should not be folded into the first
  implementation slice.

Interpretation: this eval is now evaluating the next validation-hardening phase,
not widening the original implementation claim.

Assumption: generated `Infrastructure/artifacts/skills/**` live-eval outputs are
acceptable proof artifacts for the blocked release lane.

## Functional Validation Results

| Gate | Command or method | Result | Evidence | Confidence | Blocks Closure |
| --- | --- | --- | --- | --- | --- |
| Gate wiring | `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json` | pass | status `pass`, errors `[]` | high | no |
| Domain wiring | `python3 Plugins/harness-engineering/scripts/check_domain_contract_wiring.py --json` | pass | status `pass`, errors `[]` | high | no |
| Deferred context | `python3 Plugins/harness-engineering/scripts/check_deferred_context_index.py --json` | pass | status `pass`, errors `[]` | high | no |
| Packaging hygiene | `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json` | pass | status `pass`, `blocked_paths: []` | high | no |
| Python compile | `PYTHONPYCACHEPREFIX=/tmp/he-release-evals-pycache python3 -m py_compile Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py` | pass | no output, exit 0 | high | no |
| Eval YAML parse | Ruby YAML parse for changed eval files | pass | `he-router` 12 cases, `he-eval-report` 13 cases | high | no |
| Strict audit | `./bin/ask skills audit Plugins/harness-engineering/skills/he-router --level strict --json --robot` | pass | status `success` | high | no |
| Strict audit | `./bin/ask skills audit Plugins/harness-engineering/skills/he-eval-report --level strict --json --robot` | pass | status `success` | high | no |
| Rooted sync | `./bin/ask skills sync --scope workspace --projection rooted --json --robot` | partial | status `success`; warning `PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED` | medium | yes for picker-cache proof |
| Handles | `./bin/ask skills handles --check --json --robot` | pass | 98 handles, 0 violations | high | no |
| Sliced live smoke | `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --eval-runner codex --model gpt-5.4-mini --per-skill-timeout-sec 180 --skill he-router --skill he-eval-report --case ambiguous-stage-route --case implementation-only-status --json` | pass | `he-router` and `he-eval-report` passed selected changed-surface cases | high | no for sliced confidence |
| Full lifecycle smoke | `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --skill he-spec --skill he-code-review --skill he-eval-report --per-skill-timeout-sec 180 --json` | fail | all four selected skills failed or timed out | high | yes for plugin-wide release confidence |
| Focused smoke rerun | `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --skill he-eval-report --per-skill-timeout-sec 240 --json` | fail | `he-router` failed before regex fix; `he-eval-report` timed out | high | yes for release confidence |
| Router smoke after regex fix | `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --per-skill-timeout-sec 240 --json` | timeout | timed out after 240 seconds | high | yes for release confidence |

## Eval Gate Matrix

Gate: Static gate-selection contract wiring

Expected: contract exists, lifecycle skills reference it, eval cases exist.

Actual: validator passes.

Status: pass

Evidence: `check_gate_selection_wiring.py --json`

Confidence: high

Blocks Closure: no for static confidence

Required Action: none.

Gate: Lifecycle runner command contract

Expected: planned command supports `he-router`, `he-spec`, `he-code-review`, and
`he-eval-report`.

Actual: runner now accepts all four skills.

Status: pass

Evidence: `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --help`

Confidence: high

Blocks Closure: no

Required Action: keep `he-spec` and `he-code-review` in the supported skill set.

Gate: Live lifecycle smoke evals

Expected: changed lifecycle skills pass smoke mode or produce non-blocking
justified exceptions.

Actual: `he-router`, `he-spec`, `he-code-review`, and `he-eval-report` did not
produce a passing smoke lane. Some failures were concrete eval failures; others
were runtime timeouts.

Status: fail

Evidence: release eval JSON output and generated scorecards.

Confidence: high

Blocks Closure: yes for release-confidence claims.

Required Action: create a separate lifecycle eval reliability slice to reduce
case count, support case-filtered changed-surface lanes, or raise the release
runner timeout policy with explicit cost/budget expectations.

Gate: Sliced live smoke evals

Expected: changed-surface cases can run independently so small repairs are
proved without requiring every lifecycle case to complete.

Actual: the HE lifecycle runner now supports direct Codex case/category slicing.
`he-router` passed `ambiguous-stage-route` and `he-eval-report` passed
`implementation-only-status` through the combined sliced command.

Status: pass

Evidence:
`python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --eval-runner codex --model gpt-5.4-mini --per-skill-timeout-sec 180 --skill he-router --skill he-eval-report --case ambiguous-stage-route --case implementation-only-status --json`

Confidence: high for changed-surface smoke confidence

Blocks Closure: no for this repair slice; yes remains for plugin-wide release
closure.

Required Action: use this lane for narrow changed-surface proof, then reserve
the full lane for release confidence.

Gate: Plugin picker cache freshness

Expected: rooted projections and plugin cache copies refresh.

Actual: rooted projections and handles validate; plugin cache refresh warns with
`PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED`.

Status: partial

Evidence: `./bin/ask skills sync --scope workspace --projection rooted --json --robot`

Confidence: high

Blocks Closure: yes for picker-cache proof, no for canonical source proof.

Required Action: run sync in an environment that can mutate
`.agents/plugins-runtime/cache` or repair the cache permission contract.

## Agentic Eval Validity

Evaluated Capability / Task: conditional HE gate-selection lifecycle routing,
closure proof, and live lifecycle smoke eval behavior.

Task Validity: supported for sliced changed-surface proof; partial for
plugin-wide release proof

Outcome Validity: supported for the two selected live cases; partial for full
lifecycle coverage

Trajectory / Transcript Evidence: live eval scorecards and timeout artifacts
were generated under `Infrastructure/artifacts/skills/**`; static validators and
strict audits passed.

Grader Coverage: partial

Trial Policy: single diagnostic smoke attempts only; not enough for release
confidence.

Pass@k / Pass^k Reporting: not-run

Authorization Validator: not-run

Saturation / Maintenance Signal: not-run

Blocks Completion: yes

Completion Scope: plugin-wide release confidence remains blocked; sliced
changed-surface confidence is supported.

Required Action: stabilize the full HE lifecycle eval lane before plugin-wide
release confidence. Use the new case-filtered changed-surface proof lane for
narrow repairs only.

## Side-Effect Authorization

Protected Action: Linear closure or external tracker status change.

User Authorization Evidence: none for this eval phase.

Agent Justification: not applicable; no external mutation was performed.

External Party Influence: none.

Validator Decision: blocked

Validator Confidence: high

Suggested Next Step: keep this as local proof only until the user explicitly
authorizes any Linear update after passing or accepted-blocked validation.

Blocks Completion: yes

## Domain Model Integrity Check

Domain model integrity classification: not-run

Evidence: this slice changes Harness Engineering routing and eval proof
contracts, not production domain behavior. Domain production wiring was checked
because the active worktree included the domain contract validator.

Affected files/modules:

- `Plugins/harness-engineering/references/domain-model-production-contract.md`
- `Plugins/harness-engineering/scripts/check_domain_contract_wiring.py`
- selected lifecycle skill references to the domain contract

Closure impact: no production domain closure is being requested. Domain-model
proof does not block static confidence for this slice, but the live lifecycle
eval failures still block release confidence.

## Drift Validation

Architecture Drift: Neutral

Evidence: the change adds a small contract and validator rather than a new
orchestration layer. It does not replace lifecycle ownership.

Routing Drift: Improved

Evidence: gate selection is now explicit and bounded by risk class. The runner
also supports the skills named by the source plan.

Context Drift: Improved

Evidence: conditional gate selection prevents broad context loading for trivial
or keyword-only work, and the lifecycle runner can now execute sliced live smoke
cases instead of forcing every lifecycle case for narrow repairs. Full live eval
timeout behavior still carries high context and runtime cost.

Governance Drift: Neutral

Evidence: the eval report blocks release confidence instead of creating extra
Linear noise.

Agent-Native Drift: Improved

Evidence: `gate_profile`, `risk_class`, and `skipped_contracts` give future
agents machine-readable routing cues. The release lane timeout remains an
agent-native reliability gap.

Moat Drift: Neutral

Evidence: eval quality improves when static checks prevent false release claims,
but live eval unreliability still weakens the proof moat.

## Architecture Integrity Check

No architecture invariant violation was found in the static wiring. The change
keeps HE lifecycle phases separate: router routes, spec defines contract,
code-review checks readiness, eval-report proves closure.

The release eval lane remains architecturally weak because it is both slow and
coarse-grained. That weakness predates this slice but now blocks any high
confidence completion claim.

## Routing Determinism Check

Routing determinism improved at the instruction level because the gate profile
requires evidence-backed risk classification before adjacent contracts load.

Remaining gap: full live eval behavior for the lifecycle set is not stable
enough to produce plugin-wide release proof.

## Context Load Check

Static context load is improved: trivial and small mixed requests now have a
negative gate against loading domain, strategy, refactor, Linear, security, and
eval context just because keywords appear.

Runtime context load improved for narrow repair proof through case-filtered live
smoke. Full live eval runs remain slow and generated timeouts for `he-spec`,
`he-code-review`, `he-eval-report`, and later `he-router`.

## Agent-Native Check

Improved:

- The gate-selection contract gives agents a predictable decision object.
- Negative cases prevent keyword-only specialist or broad-gate selection.
- Closure confidence is explicitly scoped when release eval proof is absent.

Blocked:

- Live lifecycle evals are not reliable enough for autonomous closure.

## Governance Simplicity Check

The implementation avoids a new review ceremony. It adds one contract, one
wiring validator, and eval cases. The eval report recommends one follow-up slice
rather than turning every timeout into multiple issues.

## Moat Protection Check

The change protects the cognition moat by reducing broad, expensive context
loading. It does not yet protect the eval moat because the live eval lane still
times out.

## Proof Artifacts

Present:

- Static validator outputs.
- Strict skill audit outputs.
- Rooted sync output.
- Command-handle check output.
- Live eval failure artifacts under `Infrastructure/artifacts/skills/**`.
- Session evidence bundle under `.harness/session-evidence/he-phase-heartbeat/`.

Missing or blocked:

- Passing full lifecycle smoke output for the changed lifecycle skills.
- Fully refreshed plugin picker cache copy.
- Passing Linear closure state after plugin-wide release proof.

## Failures / Regressions

Failure: full lifecycle smoke evals do not pass.

Impact: blocks release confidence and Linear closure recommendation.

Required repair: keep the new case-filtered changed-surface lane for narrow
proof, and create a lifecycle eval reliability slice that makes the full smoke
lane cheap enough to run consistently or defines explicit release/escalation
rules.

Failure: plugin cache refresh permission warning remains.

Impact: blocks claims that the plugin picker cache copy is fully refreshed.

Required repair: fix write permissions for `.agents/plugins-runtime/cache` or
run sync from a context that can mutate that cache.

## Linear Completion Recommendation

Classification: Blocked

Recommended Linear status: do not close if this becomes a Linear-tracked parent
issue.

Required Linear comment/update:

```text
Static HE gate-selection wiring passes, but release confidence is blocked.
Case-filtered live smoke now passes for the repaired he-router and
he-eval-report cases. Full lifecycle smoke evals for
he-router/he-spec/he-code-review/he-eval-report did not pass or timed out, and
plugin cache refresh reported PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED. Closure
requires lifecycle eval reliability repair or an approved equivalent full proof
lane.
```

Issues to close: none.

Issues to reopen: none.

Issues to leave open: any future issue representing release-confidence closure.

New follow-up issue: one candidate only.

## Follow-Up Work

Follow-up: stabilize HE lifecycle release eval lane.

Classification: `Now`

Target project: `agent-skills`

Reason: plugin-wide release-confidence proof is blocked by live eval
failures/timeouts even though sliced changed-surface live smoke now passes.

Priority: High

Labels: `Eval`, `Agent-Native`, `Reliability`

Execution route: agent-assisted; human review required before redefining release
confidence semantics.

Do Not Create:

- Separate issues for every timed-out skill.
- Separate issue for every generated eval artifact.
- Separate issue for every regex repair already made in this phase.

## Core / ADR Update Recommendation

Core update: not required yet. The gate-selection contract is still fresh and
should prove itself through passing live evals before becoming a core invariant.

ADR update: not required yet. No irreversible architecture decision was made in
this validation-hardening phase.

## Evidence & Traceability Matrix

| Conclusion | Evidence Type | Files / Commands | Confidence | Operational Impact |
| --- | --- | --- | --- | --- |
| Static gate-selection wiring is present | source, validator | `gate-selection-contract.md`, `check_gate_selection_wiring.py --json` | high | supports static confidence |
| Domain production contract wiring passes | source, validator | `domain-model-production-contract.md`, `check_domain_contract_wiring.py --json` | high | prevents domain wiring regression |
| Planned lifecycle command was stale and is now repaired | source, command help | `run_lifecycle_release_evals.py`, `--help` output | high | allows intended four-skill lane to run |
| Sliced changed-surface smoke passes | runtime eval | `run_lifecycle_release_evals.py --mode smoke --eval-runner codex ... --case ambiguous-stage-route --case implementation-only-status` | high | supports narrow repair confidence |
| Plugin-wide release confidence is blocked | runtime eval | legacy full `run_lifecycle_release_evals.py --mode smoke ...` | high | blocks closure |
| Plugin picker cache proof is incomplete | sync output | `PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED` | high | blocks cache freshness claim |
| Linear traceability is linked but closure remains blocked | artifact inspection | `JSC-299` is present in frontmatter and the Linear backlink map | high | blocks closure until release-confidence proof passes |
