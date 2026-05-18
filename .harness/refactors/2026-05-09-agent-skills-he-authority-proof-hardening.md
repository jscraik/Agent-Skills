---
schema_version: 1
artifact_id: agent-skills-he-authority-proof-hardening-refactor
artifact_type: he-refactor-program
canonical_slug: agent-skills-he-authority-proof-hardening
title: HE Authority And Proof Hardening Refactor
harness_stage: he-refactor
status: active
date: 2026-05-09
traceability_required: false
origin: .harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md
linear_issue: ""
linear_milestone: ""
---

# HE Authority And Proof Hardening Refactor

## Refactor Classification

- selected candidate: HE authority and proof hardening
- output path: `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md`
- side-effect class for this run: artifact write only
- execution authority: not granted by this program
- execution determinism
- anti-drift hardening
- eval stabilization
- governance reduction
- skill discoverability improvement
- Linear execution hygiene
- moat reinforcement

## Problem Statement

Harness Engineering has the right lifecycle shape, but several trust boundaries
still rely on prose instead of measurable contracts.

The structural problem is not that HE lacks enough stages. The problem is that
the current lifecycle can still let agents:

- treat "tiny and low risk" as subjective execution permission;
- summarize validation as proof without non-narrative evidence;
- skip or degrade router sample execution without making release confidence
  fail clearly;
- allow artifact growth before active-artifact freshness and closure checks can
  consume it;
- add threat/model/tool-audit ceremony before downstream gates prove they use
  the output.

If left unresolved, HE can look production-grade while still allowing false
completion, unclear authority, and stale evidence.

## Root Cause Analysis

This emerged because the plugin matured through strong prompt contracts before
all of those contracts had equivalent fixtures, validators, and release gates.
That sequence was rational: skill behavior needed to be described before it
could be verified. It now creates pressure because prose guidance has outgrown
the enforcement layer.

Why it survived:

- HE skill wording correctly names many safety rules, so the remaining gaps are
  easy to miss.
- Some boundaries are already strong, such as Linear mutation and eval closure,
  which can make weaker execution shortcuts feel less urgent.
- Prior work emphasized adding lenses and contracts; the next leverage comes
  from making the smallest subset machine-checkable.

This is structural because authority, proof, routing, and closure are shared
across the lifecycle. A tactical fix to one skill would leave adjacent stages
able to reintroduce the same ambiguity.

## Source Prompt Coverage

```yaml
source_prompt_status: summarized
evidence_depth: representative
coverage_scope: subsystem
claim_scope: subsystem
coverage_gaps:
  - gap: "The original user roadmap was represented through the upstream strategy artifact rather than preserved verbatim in this refactor program."
    impact: "The refactor can guide HE control-plane hardening, but it must not claim full equivalence to every source-prompt detail."
    blocks_downstream_authority: no
not_inspected:
  - evidence_class: "live current CI/PR state"
    impact: "Phase validation requirements must be refreshed before implementation."
  - evidence_class: "live Linear project graph"
    impact: "Linear mapping remains proposed until a tracked planning stage resolves the tracker of record."
authority_limited_to:
  - allowed_claim: "valid subsystem refactor program for HE authority, routing, proof, and closure hardening"
    forbidden_claim: "repo-wide implementation approval or completion proof"
repo_specific_drift_signals:
  - signal: "subjective execution authority"
    severity: high
    indicator: "`he-work` low-risk shortcut wording remains prose-based"
    corrective_action: "replace with measurable thresholds and fixtures"
    blocks: "broad execution-authority expansion"
  - signal: "evidence-depth laundering"
    severity: high
    indicator: "closure can become narrative when validators or runner evidence are missing"
    corrective_action: "make missing/not-run validation a closure blocker"
    blocks: "eval closure and plugin-wide confidence claims"
  - signal: "artifact sprawl before active proof"
    severity: medium
    indicator: "broad artifact indexes are proposed before active closure checks consume them"
    corrective_action: "scope indexing to active closure chains first"
    blocks: "global historical artifact indexing"
original_prompt_coverage: partial
downstream_confidence: medium
next_route: continue
```

Authority note:

This program inherits the upstream strategy's direction and preserves it as a
bounded migration program. It is valid as input to `he-spec`, `he-plan`, or a
Linear planning stage. It is not valid as direct implementation permission.

## Evidence

Facts:

- `Plugins/harness-engineering/skills/he-work/SKILL.md` still says: "Use when
  execution is approved or tiny and low risk."
- `Plugins/harness-engineering/skills/he-eval-report/SKILL.md` already states
  implementation is not completion and closure requires proof.
- `Plugins/harness-engineering/skills/he-linear-plan/SKILL.md` already
  separates `.harness` cognition/proof from Linear execution tracking and
  forbids direct Linear mutation by default.
- `Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md` already
  separates scheduling/gating from implementation, commit, push, merge, close,
  and destructive authority.
- `.harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md`
  identifies trust defects, boundary hardening, proof infrastructure, and new
  capability as separate execution bands.
- `.harness/evals/2026-05-09-agent-skills-conditional-he-gate-selection-eval.md`
  records prior lifecycle release smoke failures/timeouts and blocks
  plugin-wide release confidence.

Interpretation:

- `he-work` is the highest-risk current authority loophole because it is the
  execution skill.
- `he-eval-report` should be hardened by enforcing existing doctrine, not by
  adding a new completion model.
- Band 1 defects are tactical individually, but together they are the first
  phase of a structural migration from prose trust to measurable trust.

Assumptions:

- No current Linear issue key was provided for this refactor; Linear mapping is
  therefore proposed, not trace-bound.
- Existing dirty worktree changes may include partial related work; this
  program does not authorize overwriting them.

## Architectural Impact

Affected systems:

- HE lifecycle skills: `he-work`, `he-eval-report`, `he-router`,
  `he-code-review`, `he-plan`, `he-spec`, `he-phase-heartbeat`.
- HE release/eval scripts under `Plugins/harness-engineering/scripts/`.
- HE validation fixtures and skill tests.
- `.harness` artifact identity and closure proof expectations.
- Future Linear planning for HE plugin hardening.

Blast radius:

- Medium for HE plugin behavior.
- Low for non-HE repository code if phases stay bounded.
- High for release confidence wording, because closure claims must become more
  conservative until gates pass.

Systems that must not be touched by this refactor program:

- Runtime skill projections as source of truth.
- External Linear objects.
- PR merge/close status.
- Broad plugin-factory or skill-factory behavior unless a later approved slice
  explicitly admits them.

## Desired End State

HE has a compact measurable trust layer:

- `he-work` uses explicit low-risk thresholds and routes anything outside them
  upstream.
- Router and trigger behavior is covered by fixtures for high-risk lifecycle
  routes.
- Release validation fails clearly when router sample execution is skipped or
  unavailable.
- `he-eval-report` blocks closure when required validators are missing,
  not-run, or only narrated.
- Artifact/evidence checks start with active closure artifacts, not the entire
  historical `.harness` tree.
- Threat model, tool audit, and parallel-agent capability remain deferred until
  downstream gates prove their output changes decisions.

The reasoning model becomes:

```text
prose contract -> fixture/validator -> release gate -> eval proof -> closure
```

## Migration Strategy

Migrate in bands. Do not add broad new capability until the prior band produces
observable proof.

1. Repair current trust defects.
2. Harden routing and authority boundaries.
3. Add proof infrastructure only where a false closure case is known.
4. Add threat-model/tool-audit/parallel-agent capability only after proof
   infrastructure consumes their outputs.

Coexistence rules:

- Existing skill prose remains valid during migration.
- New thresholds and validators become blocking only after fixtures prove the
  expected behavior.
- New capability starts as routed/optional until closure evals prove it affects
  downstream gates.

Rollback strategy:

- Each phase is reversible by removing its new validator/fixture and restoring
  prior skill wording.
- Do not delete old behavior until the new gate passes and an eval artifact
  records the replacement.
- If a gate blocks legitimate low-risk work, revert the gate to warning and
  keep the fixture as evidence for refinement.

## Smallest Reversible Step

Band 1 only:

```text
Fix packaging hygiene, the he-eval-report missing/not-run validator blocker,
ask-missing degraded behavior, and router-sample release failure semantics.
```

What it teaches:

- Whether the release lane can produce trustworthy hard-failure signals before
  the plugin adds more governance.

Stop or pivot condition:

- If failures are caused by unavailable local command surfaces rather than HE
  behavior, pause feature work and repair degraded-mode command behavior first.

## Execution Phases

### Phase 1: Trust Defect Repair

Objective:

Fix the known hard defects before adding new HE surfaces.

Affected systems:

- `Plugins/harness-engineering/scripts/check_packaging_hygiene.py`
- `Plugins/harness-engineering/skills/he-eval-report/tests/`
- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
- router sample validation behavior

Expected risk:

- Low to medium.

Feedback expected from this phase:

- Release/eval lane returns deterministic pass/fail/blocked outcomes instead of
  skipped or ambiguous confidence.

Stop or pivot condition:

- Stop if the runner cannot distinguish missing `ask` from skill failure.

Can run in parallel: `no`

Validation requirements:

- Command: `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py`
  Acceptance: exit code 0; stdout contains "packaging hygiene: pass"
  Script: Plugins/harness-engineering/scripts/check_packaging_hygiene.py

- Command: `python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/ -q`
  Acceptance: exit code 0; all tests pass with no failures
  Script: Plugins/harness-engineering/skills/he-eval-report/tests/

- Command: `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --degraded-mode`
  Acceptance: exit code 0; stdout contains "degraded mode: pass" or expected degraded behavior reported
  Script: Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py

- Command: `python3 -m pytest Plugins/harness-engineering/scripts/ -k "router_sample" -q`
  Acceptance: exit code 0; router sample skip/fail behavior confirmed
  Script: Plugins/harness-engineering/scripts/ (router sample test)

Rollback conditions:

- Revert only the changed validator/runner behavior if it blocks unrelated
  lifecycle cases without actionable diagnostics.

Linear mapping:

- Proposed target: agent-skills repo project.
- Proposed milestone: HE Authority And Proof Hardening.
- Parent issue: `[agent-skills] Repair HE trust defects before new capability`.

Agent-safe: `assisted`

Human review required: `yes`

### Phase 2: Routing And Authority Boundary Hardening

Objective:

Replace subjective stage/authority decisions with fixtures and measurable
thresholds.

Affected systems:

- `he-router`
- `he-work`
- skill trigger descriptions
- route/trigger fixtures
- authority contract references

Expected risk:

- Medium.

Feedback expected from this phase:

- Ambiguous requests route to ask/block/defer instead of guessing.
- `he-work` accepts only measurable low-risk work.

Stop or pivot condition:

- Stop if trigger fixtures show multiple skills are equally valid for the same
  non-ambiguous request; repair descriptions before adding more policy.

Can run in parallel: `no`

Validation requirements:

- Route fixtures for high-risk lifecycle requests.
- Trigger fixtures for `he-router`, `he-work`, `he-eval-report`,
  `he-linear-plan`, `he-code-review`, and `he-phase-heartbeat`.
- Threshold tests for low-risk execution.

Rollback conditions:

- If thresholds over-block common safe tasks, move the threshold from blocking
  to assisted review and record the missing safe case.

Linear mapping:

- Parent issue: `[agent-skills] Make HE routing and work authority measurable`.

Agent-safe: `assisted`

Human review required: `yes`

### Phase 3: Active Proof Infrastructure

Objective:

Add the smallest artifact/evidence checks that block known false-closure modes.

Affected systems:

- `he-eval-report`
- artifact identity/frontmatter linting
- active `.harness` artifact set
- evidence provenance rules

Expected risk:

- Medium.

Feedback expected from this phase:

- Eval reports block unsupported closure and cite concrete command/tool/CI
  evidence.

Stop or pivot condition:

- Stop if artifact indexing expands to historical `.harness` cleanup before it
  blocks one known false closure case.

Can run in parallel: `yes`

Validation requirements:

- Eval case for missing/not-run validators.
- Eval case for implementation-only closure request.
- Artifact freshness check for active closure chain only.

Rollback conditions:

- If active-artifact indexing creates noisy false positives, reduce scope to
  eval/spec/plan artifacts for the current slice.

Linear mapping:

- Parent issue: `[agent-skills] Add active proof gates for HE closure`.

Agent-safe: `assisted`

Human review required: `yes`

### Phase 4: Deferred Risk Capability

Objective:

Introduce threat model, tool audit, and parallel-agent capability only when
proof infrastructure can consume their outputs.

Affected systems:

- possible `he-threat-model`
- possible `he-tool-audit`
- `he-spec`
- `he-plan`
- `he-code-review`
- `he-eval-report`

Expected risk:

- High if done too early; medium if downstream gates exist.

Feedback expected from this phase:

- A high-risk skills/plugins/tools/MCP change produces a risk artifact that
  changes spec acceptance, plan validation, review findings, and eval closure.

Stop or pivot condition:

- If the risk artifact does not change downstream gates, collapse it into
  `he-spec` risk classification and do not create a standalone skill.

Can run in parallel: `no`

Validation requirements:

- One end-to-end high-risk route case.
- Closure eval proving the risk artifact was consumed.
- Negative eval proving low-risk work is not forced through the new stage.

Rollback conditions:

- Remove or demote standalone stage if downstream gates ignore it.

Linear mapping:

- Parent issue: `[agent-skills] Add routed HE risk capability only after proof gates`.

Agent-safe: `no`

Human review required: `yes`

## Linear Mapping

Workspace/team: Jscraik

Team key: JSC

Top-level initiative: Dev Portfolio

Target project:

- agent-skills repo project, if active.
- Portfolio Ops only if this becomes cross-repo HE operating policy.

Recommended milestone:

- HE Authority And Proof Hardening

Recommended parent issue sequence:

1. `[agent-skills] Repair HE trust defects before new capability`
2. `[agent-skills] Make HE routing and work authority measurable`
3. `[agent-skills] Add active proof gates for HE closure`
4. `[agent-skills] Add routed HE risk capability only after proof gates`

Suggested priority:

- Phase 1: High
- Phase 2: High
- Phase 3: Normal
- Phase 4: Normal / later

Suggested labels:

- Architecture
- Agent-Native
- Eval
- Governance
- Refactor
- Drift-Risk

Do not create Linear objects from this program without explicit user
confirmation.

## Anti-Regression Constraints

Future agents must not reintroduce:

- subjective `tiny`, `small`, or `low risk` execution authority without
  measurable thresholds;
- closure recommendations based only on implementation status;
- release-confidence claims when lifecycle release evals are skipped, timed out,
  or stale;
- Linear mutation from `he-linear-plan` without explicit authorization;
- universal threat modeling for low-risk work;
- artifact indexes that track historical clutter before active closure chains;
- parallel-agent workflows before ownership and evidence gates exist.

## Eval Requirements

Expected eval artifact:

```text
.harness/evals/YYYY-MM-DD-agent-skills-he-authority-proof-hardening-eval.md
```

Required gates:

- Packaging hygiene.
- `he-eval-report` missing/not-run validator closure block.
- Router sample execution skip/fail behavior.
- `ask` unavailable degraded-mode behavior.
- `he-work` measurable threshold routing.
- Active artifact/evidence closure check.
- Negative eval proving low-risk work avoids unnecessary threat-model ceremony.

No related Linear parent, milestone, or execution slice should be recommended
complete without this eval artifact or a documented exception.

## Success Criteria

- Release/eval runner reports skipped router samples as blocking when sample
  execution is required.
- `he-eval-report` blocks closure when required validators are missing or
  not-run.
- `he-work` has measurable shortcut thresholds and test coverage.
- Trigger/route fixtures cover the highest-risk lifecycle skills.
- Active artifact/evidence checks block at least one known false closure mode.
- Threat-model/tool-audit/parallel-agent work remains deferred until consumed by
  downstream gates.

## Safe Rollback Conditions

Rollback is allowed when:

- a new gate blocks unrelated existing safe workflows;
- fixture expectations conflict with observed canonical `./bin/ask` behavior;
- release runner changes cannot distinguish environmental unavailability from
  skill failure;
- active artifact checks produce stale-document noise unrelated to the current
  slice.

Rollback is not allowed merely because:

- a gate correctly blocks missing proof;
- plugin-wide confidence becomes more conservative;
- a new fixture exposes ambiguous skill descriptions.

If rollback is triggered, Linear status should be `Needs rework` rather than
`Complete`.

## Future-Agent Guidance

- Treat this program as a migration safety rail, not implementation permission.
- Start with Phase 1 only.
- Do not build `he-threat-model`, `he-tool-audit`, or parallel-agent workflows
  until phases 1-3 prove the downstream gates exist.
- Prefer deleting or collapsing policy over adding another stage when an eval
  can catch the failure.
- Preserve `.harness` as cognition/proof and Linear as execution tracking.
- Record any broader ideas as `Later` unless they prevent a verified recurring
  failure.

## Related Systems

- `.harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md`
- `.harness/evals/2026-05-09-agent-skills-conditional-he-gate-selection-eval.md`
- `Plugins/harness-engineering/skills/he-work/SKILL.md`
- `Plugins/harness-engineering/skills/he-eval-report/SKILL.md`
- `Plugins/harness-engineering/skills/he-router/SKILL.md`
- `Plugins/harness-engineering/skills/he-linear-plan/SKILL.md`
- `Plugins/harness-engineering/skills/he-code-review/SKILL.md`
- `Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md`
- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
- `Plugins/harness-engineering/scripts/check_packaging_hygiene.py`

## Do Not Create Decisions

Do not create separate refactor programs now for:

- universal threat modeling;
- full `.harness` historical artifact indexing;
- parallel-agent execution;
- broad supply-chain governance beyond HE skills/plugins/tools;
- automatic Linear mutation.

Reason:

Each is potentially useful, but each should wait until authority, routing, and
proof gates are already measurable.

## Validation Record

| Command | Outcome |
| --- | --- |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` | pass |
| `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` | pass |
| `./bin/ask skills audit Plugins/harness-engineering/skills/he-refactor --level strict --json --robot` | pass |
