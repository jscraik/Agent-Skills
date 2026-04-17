---
title: feat: Skill Authoring Family Contract Rollout
type: feat
status: complete
date: 2026-04-04
origin: docs/brainstorms/2026-04-03-skill-authoring-family-contract-requirements.md
requirements: docs/brainstorms/2026-04-03-skill-authoring-family-contract-requirements.md
spec: Docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md
---

# feat: Skill Authoring Family Contract Rollout

## Table of Contents
- [Overview](#overview)
- [Problem Frame](#problem-frame)
- [Requirements Trace](#requirements-trace)
- [Scope Boundaries](#scope-boundaries)
- [Context and Research](#context-and-research)
- [Key Technical Decisions](#key-technical-decisions)
- [Open Questions](#open-questions)
- [Implementation Units](#implementation-units)
- [Execution Control Gates](#execution-control-gates)
- [Task Graph (id and depends_on)](#task-graph-id-and-depends_on)
- [System-Wide Impact](#system-wide-impact)
- [Risks and Dependencies](#risks-and-dependencies)
- [Documentation and Operational Notes](#documentation-and-operational-notes)
- [Execution Ledger (Planning Mode)](#execution-ledger-planning-mode)
- [Acceptance Checklist](#acceptance-checklist)
- [Sources and References](#sources-and-references)

## Overview

Roll out the skill-authoring family contract so the repo exposes one coherent, April 2026-aligned authoring surface across:
- `skill-creator`
- `skill-builder`
- `skill-installer`
- `plugin-builder`

This plan implements the approved spec by:
- synchronizing phase-zero validator and frontmatter guidance,
- aligning family metadata and handoff copy to the new routing contract,
- adding routing and provenance regression coverage,
- and proving readiness across both `Skills/` and `Skills/` enforcement surfaces.

Plan mode: `standard-plan`  
Plan depth: `standard`  
Execution posture: docs-and-validator-first, then eval enforcement, then full-family readiness proof.

## Problem Frame

The repo now has a strong but ambiguous authoring family. The governing spec defines the right contract, but the implementation still has to align multiple surfaces that currently drift from one another:
- phase-zero frontmatter guidance still rejects or omits `compatibility` in some governed paths;
- `skill-builder` metadata still under-describes the actual expert-maintainer scope;
- family members do not yet all expose the same routing, handoff, packaging, and provenance story;
- validation coverage is still split across repo lint, helper validators, and skill evals, with cross-family coverage not yet guaranteed.

Without a deliberate rollout sequence, the repo could land a partially correct family contract that reads well in the spec but still routes inconsistently in real usage.

## Requirements Trace

- R1. Implement one canonical routing contract across `skill-creator`, `skill-builder`, `skill-installer`, and `plugin-builder`.
- R2. Preserve the two-tier authoring model: starter creation in `skill-creator`, expert lifecycle work in `skill-builder`.
- R3. Distinguish standalone-skill packaging from plugin packaging and keep the validation-first plugin gate intact.
- R4. Add explicit clarification and handoff behavior in user-visible family surfaces.
- R5. Align the authority model so spec truth, asset-local truth, and mirrored metadata do not conflict.
- R6. Bring all governed frontmatter validators and guidance back into sync with official keys, including `compatibility`.
- R7. Require trusted-source, provenance, staged validation, and rollback language for install/import and cross-surface packaging handoffs.
- R8. Add regression-ready routing and provenance coverage that spans both `Skills/` and `Skills/` surfaces.

## Scope Boundaries

In scope:
- governed authoring-family skills and metadata:
  - `Skills/skill-creator/`
  - `Skills/skill-installer/`
  - `Skills/skill-builder/`
  - `Skills/plugin-builder/`
- frontmatter and helper-validator enforcement for the family
- routing, packaging, clarification, handoff, and provenance eval coverage for this family
- readiness verification that proves the contract across both directory families

Out of scope:
- renaming, merging, or deleting family members
- rewriting the broader repo skill router
- general plugin marketplace redesign
- implementation of new runtime router code outside the skill and validator surfaces already named in the spec
- changing invocation policy for `skill-builder` unless the rollout evidence later shows it is necessary

## Context and Research

### Relevant Code and Patterns

- `Docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md`
  - authoritative phase-one family contract with clarification state, packaging split, handoff lifecycle, authority model, and acceptance matrix
- `docs/reference/managed-asset-lifecycle.md`
  - authoritative repo guidance for in-file truth versus derived views
- `docs/skill-graphs/question-lifecycle.md`
  - canonical `route_clarification` timing and ownership contract
- `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh`
  - repo-level frontmatter enforcement surface that must cover `compatibility`
- `Skills/skill-creator/Infrastructure/scripts/quick_validate.py`
  - family helper validator currently missing `compatibility` support
- `Skills/skill-builder/Infrastructure/scripts/quick_validate.py`
  - existing validator surface whose compatibility messaging also needs parity
- `Skills/skill-builder/Infrastructure/references/evals.yaml`
  - current concrete eval surface already owning routing and provenance-like cases
- `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`
  - runnable eval harness with existing smoke/release modes and path-based invocation
- `Skills/skill-builder/Infrastructure/scripts/test_run_skill_evals.py`
  - existing test surface for eval-runner behavior
- `Skills/skill-builder/agents/openai.yaml`
  - current under-scoped metadata surface for `skill-builder`

### Institutional Learnings

- The user explicitly asked for staged `ce-plan` and review-driven artifact flow, so this rollout should keep one canonical plan and verified evidence at each stage.
- In this repo, validation findings that represent durable work should end in concrete enforcement or follow-up artifacts, not chat-only conclusions.
- Repo guidance favors bounded, evidence-backed remediation over broad structural churn.

### External References

- None required for planning beyond the already-incorporated official guidance cited in the spec.

## Key Technical Decisions

- Decision 1: Treat phase-zero compatibility sync as the first delivery gate.
  - Rationale: the rest of the family contract is not trustworthy if the repo still rejects spec-valid frontmatter.

- Decision 2: Keep the spec as the authoritative family contract and do not create a second equal-authority family doc during the initial rollout.
  - Rationale: this preserves alignment with managed-asset lifecycle doctrine and avoids introducing a fresh source-of-truth conflict.

- Decision 3: Roll out mirrored routing copy before expanding eval assertions.
  - Rationale: evals should protect the final contract, not temporarily freeze stale descriptions.

- Decision 4: Use existing `skill-builder` eval infrastructure as the phase-one family harness.
  - Rationale: the repo already has a runnable eval runner and fixture surface there, so extending that path is cheaper and less ambiguous than introducing a second harness first.

- Decision 5: Treat trust/provenance wording as a contract requirement for installer and packaging surfaces, not just a validator-side concern.
  - Rationale: users need the boundary to be visible before execution, not only discoverable by failed checks.

## Open Questions

### Resolved During Planning

- Should planning require a new dedicated family reference doc?
  - Resolution: no. The spec remains authoritative in phase one. A derived family reference doc is optional follow-up only if execution proves it helps discoverability without creating a second authority source.

- Should the plan assume a new eval harness?
  - Resolution: no. Phase one extends `Skills/skill-builder/Infrastructure/references/evals.yaml` and `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`.

### Deferred to Implementation

- Whether `skill-builder` should become explicit-only after the family contract lands.
  - Deferred because the current spec treats this as a rollout-policy decision best informed by post-rollout routing evidence.

### Resolved for Execution

- `Skills/skill-installer/SKILL.md` must point to `plugin-builder` as the canonical plugin-packaging handoff inside the governed family contract.
  - `plugin-creator` may remain as an additional adjacent scaffold reference only if it does not replace or obscure the canonical family packaging handoff to `plugin-builder`.

## Implementation Units

- [ ] **P0 / Phase-Zero Compatibility and Validator Sync**

**Goal:** Remove stale frontmatter assumptions and make all named validation surfaces accept and describe the current official key set, including `compatibility`.

**Requirements:** R5, R6

**Dependencies:** None

**Files:**
- Modify: `Skills/skill-builder/SKILL.md`
- Modify: `Skills/skill-creator/SKILL.md`
- Modify: `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh`
- Modify: `Skills/skill-creator/Infrastructure/scripts/quick_validate.py`
- Modify: `Skills/skill-builder/Infrastructure/scripts/quick_validate.py`
- Test: `bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict`
- Test: `~/.venvs/pyyaml/bin/python Skills/skill-creator/Infrastructure/scripts/quick_validate.py Skills/skill-creator`
- Test: `~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/quick_validate.py Skills/skill-builder`

**Approach:**
- Update all governed guidance that still says only `license`, `allowed-tools`, and `metadata` are optional keys.
- Bring helper validator error messages and allowed-key sets into parity with the spec.
- Ensure validator guidance is path-aware and runtime-aware where commands are surfaced to users.
- Expand `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh` coverage to include `skills-system`, or land an equivalent mandatory family-wide lint path that proves `skill-creator` and `skill-installer` are governed by the same format contract as `Skills/skill-builder`.

**Patterns to follow:**
- Existing validator CLI shape in `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`
- Current spec observability and readiness checks in `Docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md`

**Test scenarios:**
- A skill using `compatibility` passes linter and helper validation.
- Unknown keys still fail cleanly with actionable messages.
- Command guidance no longer references bare non-runnable validator invocations.

**Verification:**
- All phase-zero enforcement surfaces accept `compatibility` and produce aligned messaging.
- Repo-level skill-format validation now covers both `Skills/` and `Skills/` family surfaces rather than relying on `Skills/` alone.

**Exit criteria:**
- No governed validator or family authoring skill still documents the stale key set.
- The three direct validation commands above succeed from repo root.
- The named repo linter path used for readiness proof includes `skills-system` coverage or an explicitly equivalent mandatory validator step.

- [ ] **P1 / Mirrored Routing Copy and Metadata Alignment**

**Goal:** Make each family surface describe its real role, strongest triggers, non-triggers, and handoff boundaries consistently with the spec.

**Requirements:** R1, R2, R3, R4, R5

**Dependencies:** P0

**Files:**
- Modify: `Skills/skill-builder/SKILL.md`
- Modify: `Skills/skill-builder/agents/openai.yaml`
- Modify: `Skills/skill-creator/SKILL.md`
- Modify: `Skills/skill-creator/agents/openai.yaml`
- Modify: `Skills/skill-installer/SKILL.md`
- Modify: `Skills/skill-installer/agents/openai.yaml`
- Modify: `Skills/plugin-builder/SKILL.md`
- Test: `rg -n "Create or update a skill|route_clarification|package a validated standalone skill|plugin package" Skills/skill-builder/SKILL.md Skills/skill-creator/SKILL.md Skills/skill-installer/SKILL.md Skills/plugin-builder/SKILL.md Skills/skill-builder/agents/openai.yaml`

**Approach:**
- Update `skill-builder` metadata and body text so it reads as the expert lifecycle maintainer rather than a starter creator.
- Tighten `skill-creator` wording so existing-skill edits stay inside scaffold-completion boundaries.
- Add or refine explicit handoff language across the family:
  - `skill-creator` -> `skill-builder`
  - `skill-builder` -> `skill-installer`
  - `skill-installer` -> `plugin-builder` for governed family plugin packaging adjacency
  - any governed surface -> `plugin-builder` when the deliverable becomes a plugin
- Make standalone-skill packaging and plugin packaging visibly distinct in surface-level prose and examples.

**Execution note:** copy and examples must mirror the spec; do not create new behavioral branches here.

**Patterns to follow:**
- `## See Also` and adjacency guidance already used in these skills
- Spec acceptance items `SA2`, `SA4`, `SA5`, `SA6`, `SA9`, `SA11`, `SA14`

**Test scenarios:**
- A maintainer can distinguish starter authoring from expert lifecycle work without reading all family surfaces end to end.
- Pure plugin packaging language no longer appears to belong to standalone skill surfaces.
- Mixed-intent prompts clearly indicate one primary owner plus a handoff path.

**Verification:**
- Family copy and metadata read consistently with the routing matrix and no longer under-describe `skill-builder`.
- `Skills/skill-installer/SKILL.md` exposes `plugin-builder` as the canonical governed plugin-packaging handoff.

**Exit criteria:**
- All governed family surfaces expose role-consistent copy and handoff guidance.
- `Skills/skill-builder/agents/openai.yaml` no longer says only "Create or update a skill."
- `Skills/skill-installer/SKILL.md` no longer leaves plugin-packaging adjacency ambiguous inside the governed family.

- [ ] **P2 / Routing, Clarification, and Provenance Eval Expansion**

**Goal:** Protect the family contract with regression-ready routing and provenance cases that cover the new clarification, packaging, and trust boundaries.

**Requirements:** R3, R4, R7, R8

**Dependencies:** P0, P1

**Files:**
- Modify: `Skills/skill-builder/Infrastructure/references/evals.yaml`
- Modify: `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`
- Modify: `Skills/skill-builder/Infrastructure/scripts/test_run_skill_evals.py`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --list-cases --eval-mode smoke`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --runner discovery-smoke --eval-mode smoke --case discovery-round-six --format json`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --case clarification-package-ambiguous`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --case provenance-import-rollback`

**Approach:**
- Add cases for:
  - clarification-required prompts
  - standalone-skill packaging versus plugin packaging
  - mixed authoring-and-install ownership
  - audit-plus-package validation-first gating
  - external import/install provenance and rollback expectations
- Use these exact new case IDs for the phase-one contract:
  - `clarification-package-ambiguous`
  - `provenance-import-rollback`
- Extend runner expectations only as needed to keep the new cases machine-checkable and stable.
- Keep empty-output live-runner failures classified as runner/execution failures rather than misleading regex/content failures.
- Keep one known-good runnable discovery-smoke command in the plan as a harness sanity check, and add or update runner tests so the new family cases are not only listed but also executable through the existing harness.
- Preserve the current phase-one harness instead of introducing a parallel family test runner.

**Patterns to follow:**
- Existing case taxonomy and runner behavior in `Skills/skill-builder/Infrastructure/references/evals.yaml`
- Existing runner tests in `Skills/skill-builder/Infrastructure/scripts/test_run_skill_evals.py`

**Test scenarios:**
- Ambiguous "package this" prompts fail to clarification or route to the right packaging owner based on explicit deliverable language.
- Plugin packaging does not preempt unresolved lifecycle hardening requests.
- External import cases require provenance, staged validation, and rollback language.

**Verification:**
- Smoke eval inventory contains the new family cases and the runner accepts the governed skill path cleanly.
- The existing harness can still execute at least one known-good smoke case end to end after the new family cases land.
- When a live runner exits non-zero before producing any final output, scorecards attribute the failure to runner execution rather than to acceptance-regex mismatch.
- At least one newly added clarification-or-packaging case and one newly added provenance case execute successfully in smoke mode.

**Exit criteria:**
- The eval surface covers all prompt classes called out by the spec.
- Runner tests pass and smoke mode executes the newly added family cases rather than only listing them.

- [ ] **P3 / Installer and Packaging Trust-Boundary Enforcement**

**Goal:** Make provenance, trust, and validation-first handoff requirements visible and enforceable in the installer and plugin-packaging surfaces.

**Requirements:** R3, R4, R7, R8

**Dependencies:** P1, P2

**Files:**
- Modify: `Skills/skill-installer/SKILL.md`
- Modify: `Skills/plugin-builder/SKILL.md`
- Modify: `Skills/skill-builder/SKILL.md`
- Test: `rg -n "trusted-source|pinned|provenance|quarantine|rollback|contract-valid|standalone skill" Skills/skill-installer/SKILL.md Skills/plugin-builder/SKILL.md Skills/skill-builder/SKILL.md`

**Approach:**
- Make installer guidance explicitly require trusted sources, pinned refs when remote content is involved, staged validation before activation, and atomic rollback language.
- Make plugin packaging guidance explicitly depend on already-valid standalone skill inputs when lifecycle judgment is unresolved.
- Keep `skill-builder` responsible for validation-first standalone packaging posture and explicit handoff into plugin packaging.

**Patterns to follow:**
- Existing provenance-sensitive eval case direction in `Skills/skill-builder/Infrastructure/references/evals.yaml`
- Spec invariants and recovery rules for `untrusted_import` and `validity_attestation_gap`

**Test scenarios:**
- Install/import flows cannot be read as "install arbitrary remote skill content and fix it later."
- Plugin packaging guidance cannot be read as bypassing lifecycle validation.
- Standalone packaging remains separate from plugin packaging in both wording and examples.

**Verification:**
- Family docs surface the trust boundary before execution and align with the spec's safety invariants.

**Exit criteria:**
- Installer and packaging surfaces expose trust/provenance and validation-first language that matches the spec.

- [ ] **P4 / Full-Family Readiness Proof**

**Goal:** Prove the family contract is stable across docs, validators, and evals before calling the rollout complete.

**Requirements:** R1, R5, R6, R7, R8

**Dependencies:** P0, P1, P2, P3

**Files:**
- Verify: `Docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md`
- Create: `docs/reference/skill-authoring-validation-maturity-matrix.md`
- Verify: `Skills/skill-builder/SKILL.md`
- Verify: `Skills/skill-creator/SKILL.md`
- Verify: `Skills/skill-installer/SKILL.md`
- Verify: `Skills/skill-creator/agents/openai.yaml`
- Verify: `Skills/skill-installer/agents/openai.yaml`
- Verify: `Skills/plugin-builder/SKILL.md`
- Verify: `Skills/skill-builder/agents/openai.yaml`
- Verify: `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh`
- Verify: `Skills/skill-creator/Infrastructure/scripts/quick_validate.py`
- Verify: `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`
- Test: `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required`
- Test: `bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict`
- Test: `~/.venvs/pyyaml/bin/python Skills/skill-creator/Infrastructure/scripts/quick_validate.py Skills/skill-creator`
- Test: `~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/quick_validate.py Skills/skill-builder`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --list-cases --eval-mode smoke`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --runner discovery-smoke --eval-mode smoke --case discovery-round-six --format json`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --case clarification-package-ambiguous`
- Test: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --case provenance-import-rollback`

**Approach:**
- Run the full readiness stack from repo root.
- Confirm coverage across both `Skills/` and `Skills/`.
- Treat any disagreement between spec, mirrored copy, validators, and evals as degraded rollout rather than partial success.
- Produce a derived April 2026 validation maturity matrix for the governed family, especially `skill-builder`, that classifies each validation layer as `meets | partial | missing | stale` against current best-practice expectations.
- Treat these validation layers as critical for rollout closeout and classify them explicitly in the matrix:
  - family-wide format enforcement
  - runnable helper validation
  - executable routing coverage
  - executable provenance and rollback coverage
- Keep the matrix evidence-focused rather than authoritative: it must summarize validation posture and follow-ups without redefining the family contract from the spec.
- Capture the final evidence set that proves the family contract is stable enough for later execution or issue handoff.

**Execution note:** fail fast at the first broken readiness gate, fix it, and rerun from the affected gate upward. If a closeout gate is blocked only by external live-runner connectivity or authentication after repo-local lint, validator, test, and discovery-smoke checks have passed, execution may continue only in degraded evidence-capture mode: update docs, reporting, and follow-up artifacts, but do not treat the blocked gate as satisfied or mark the rollout complete.

**Patterns to follow:**
- Repo preflight flow from `Infrastructure/scripts/codex-preflight/codex-preflight.sh`
- Spec readiness and observability sections

**Test scenarios:**
- Repo root validation passes with the new family contract in place.
- A maintainer can prove family compliance without reading only one directory family.
- No validation surface still requires planners or users to invent missing command arguments or runtime assumptions.
- Final readiness re-verifies executable eval behavior, not just case inventory, after the full family changes land.
- A maintainer can identify which validation layers already meet April 2026 best practice and which still need follow-up without re-auditing the entire family from scratch.

**Verification:**
- The family contract is simultaneously visible, runnable, and regression-protected across all governed surfaces.
- Final readiness reruns both a known-good smoke execution path and representative new-family executable eval cases in addition to inventory listing.
- The validation maturity matrix maps each governed validation surface to its current check, April 2026 expectation, status, and smallest follow-up when not yet meeting best practice.
- The matrix explicitly marks the critical validation layer set and uses that set to determine complete versus degraded rollout.

**Exit criteria:**
- The readiness stack passes.
- No critical validation layer in the matrix is still marked `stale` or `missing` without an explicit tracked follow-up and degraded-rollout note.
- Remaining open questions are limited to rollout-policy refinements, not contract correctness.

## Execution Control Gates

- **Gate G0 (Phase-zero sync):** Do not start P1 until all governed validator and guidance surfaces accept `compatibility` and the direct validator invocations succeed.
- **Gate G1 (Copy parity):** Do not start P2 until the family copy and metadata read consistently with the routing matrix.
- **Gate G2 (Eval protection):** Do not start P3 until routing/provenance eval inventory includes the new prompt classes, path-based runner invocation works, and at least one newly added clarification-or-packaging case plus one newly added provenance case execute successfully in smoke mode. If the only blocker is external live-runner connectivity or authentication, continue only in degraded evidence-capture mode for docs/reporting follow-up; G2 remains unsatisfied for closeout.
- **Gate G3 (Trust boundary):** Do not start P4 until installer and plugin-packaging surfaces expose the validation-first and provenance rules visibly.
- **Gate G4 (Rollout closeout):** Mark the rollout complete only when `AC1` through `AC7` are satisfied; otherwise mark it degraded with the exact failing surface and next fix.

## Task Graph (id and depends_on)

```yaml
tasks:
  - id: P0
    title: Sync compatibility guidance and helper validators across governed surfaces.
    depends_on: []
  - id: P1
    title: Align family routing copy, metadata, and handoff wording to the canonical contract.
    depends_on: [P0]
  - id: P2
    title: Expand routing and provenance eval coverage in the existing skill-builder harness.
    depends_on: [P0, P1]
  - id: P3
    title: Enforce installer and plugin trust-boundary language plus validation-first handoffs.
    depends_on: [P1, P2]
  - id: P4
    title: Run full-family readiness verification across docs, validators, and evals.
    depends_on: [P0, P1, P2, P3]
```

## System-Wide Impact

- **Interaction graph:** touches family skill discovery, metadata surfaces, repo validators, and the eval harness that guards routing behavior.
- **Error propagation:** validator drift should fail as lint/helper/eval feedback, not as user-facing routing confusion.
- **State lifecycle risks:** partial rollout can leave the repo in a degraded family-contract state even when one surface looks correct locally.
- **API surface parity:** skill prose, `agents/openai.yaml`, lint output, helper validators, and eval runner expectations must all tell the same story.
- **Integration coverage:** no single validator proves this rollout alone; readiness requires combined evidence from preflight, lint, helper validation, and eval inventory.

## Risks and Dependencies

- Risk: mirrored copy lands before validator sync, creating a spec-correct but runnable-invalid family.
  - Mitigation: enforce G0 before P1.

- Risk: eval expansion overfits to prose and becomes brittle.
  - Mitigation: add only stable contract-level routing/provenance cases and keep runner changes minimal.

- Risk: trust-boundary wording drifts again between installer and packaging surfaces.
  - Mitigation: treat P3 as a dedicated pass instead of burying it inside general copy cleanup.

- Dependency: `~/.venvs/pyyaml/bin/python` remains the repo-friendly interpreter for validator scripts that require `PyYAML`.
- Dependency: `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py` remains the phase-one family eval harness unless intentionally replaced in a later contract update.
- Dependency: April 2026 best-practice comparisons for the maturity matrix must stay derived from current official guidance and cannot silently rely on stale repo assumptions.

## Documentation and Operational Notes

- Keep the spec authoritative; do not introduce a separate equal-authority family contract doc during this rollout.
- If rollout work surfaces durable follow-up gaps, route them into a tracked issue rather than leaving them only in chat or review comments.
- Prior live-runner closeout blocker in `JSC-140` is resolved; keep one residual-risk note only: live Codex smoke showed one transient timeout during reruns before the final passing pair rerun.
- If a future follow-up introduces explicit-only invocation for `skill-builder`, treat that as a separate rollout-policy change gated by post-rollout routing evidence.

## Execution Ledger (Planning Mode)

STEP_ID | status | owner | evidence
P0 | completed | Codex | Commands: `bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh`; `python3 Plugins/skill-factory/skills/scaffolding_templates/skill-creator/scripts/quick_validate.py --help`; `python3 Skills/skill-creator/Infrastructure/scripts/quick_validate.py --help`. Evidence pointers: `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh`, `Plugins/skill-factory/skills/scaffolding_templates/skill-creator/scripts/quick_validate.py`, `Skills/skill-creator/Infrastructure/scripts/quick_validate.py`.
P1 | completed | Codex | Commands: content audit against `skill-creator`, `skill-builder`, `skill-installer`, `plugin-builder` skill docs. Evidence pointers: `Skills/skill-creator/SKILL.md`, `Skills/skill-builder/SKILL.md`, `Skills/skill-installer/SKILL.md`, `Plugins/plugin-factory/skills/plugin-builder/SKILL.md`.
P2 | completed | Codex | Command: `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --runner codex --case clarification-package-ambiguous --case provenance-import-rollback`. Evidence pointers: `Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py`, `/private/tmp/skill-builder-live-smoke-pair-rerun/skill-builder/20260404-164154-350888/summary.json`.
P3 | completed | Codex | Commands: installer and plugin packaging contract sweep for trust/pinning/quarantine/rollback language. Evidence pointers: `Skills/skill-installer/SKILL.md`, `Plugins/plugin-factory/skills/plugin-builder/SKILL.md`, `Docs/reference/managed-asset-lifecycle.md`.
P4 | completed | Codex | Commands: `bash Infrastructure/scripts/codex-preflight.sh --mode optional`; `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`; targeted eval smoke rerun noted in P2. Evidence pointers: `Infrastructure/scripts/codex-preflight.sh`, `Infrastructure/scripts/validation-and-linting/verify-work.sh`, `Docs/reference/skill-authoring-validation-maturity-matrix.md`. Residual risk only: one transient live-runner timeout was observed before the final passing pair rerun.

## Acceptance Checklist

- [x] AC1. Governed frontmatter guidance and helper validators accept official keys, including `compatibility`, across both `Skills/` and `Skills/`.
Traceability: R5, R6; spec `SA7`, `SA20`, `SA21`

- [x] AC2. `skill-builder`, `skill-creator`, `skill-installer`, `plugin-builder`, and `Skills/skill-builder/agents/openai.yaml` expose role-consistent routing and handoff copy aligned with the canonical contract.
Traceability: R1, R2, R3, R4, R5; spec `SA2`, `SA4`, `SA5`, `SA6`, `SA9`, `SA13`

- [x] AC3. The family visibly distinguishes clarification-required prompts, standalone-skill packaging, and plugin packaging without dual-owner ambiguity.
Traceability: R1, R3, R4; spec `SA11`, `SA14`, `SA15`, `SA16`

- [x] AC4. Installer and packaging surfaces expose trusted-source, pinned-ref, provenance, staged-validation, and rollback expectations that match the spec.
Traceability: R3, R7; spec `SA18`, `SA19`

- [x] AC5. The phase-one eval harness contains runnable routing and provenance coverage for create-only, improve-only, install-only, standalone packaging, plugin-only, mixed, and clarification-required prompts.
Traceability: R4, R7, R8; spec `SA8`, `SA22`

- [x] AC6. Repo readiness can be proven from repo root using preflight, lint, helper validators, and executable eval evidence without inventing missing runtime or positional arguments.
Traceability: R5, R6, R8; spec observability + readiness checks, `SA10`, `SA21`

- [x] AC7. `P4` produces a derived April 2026 validation maturity matrix for the governed family that identifies which validation layers meet current best practice, which are partial, and which require explicit follow-up.
Traceability: R5, R6, R7, R8; spec observability + readiness checks, `SA21`, `SA22`

## Sources and References

- Requirements: [2026-04-03-skill-authoring-family-contract-requirements.md](/Docs/brainstorms/2026-04-03-skill-authoring-family-contract-requirements.md)
- Spec: [2026-04-03-feat-skill-authoring-family-contract-spec.md](/Docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md)
- Managed asset doctrine: [managed-asset-lifecycle.md](/Docs/reference/managed-asset-lifecycle.md)
- Question lifecycle: [question-lifecycle.md](/Docs/skill-graphs/question-lifecycle.md)
- Validation surfaces:
  - [lint_openai_skill_format.sh](/Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh)
  - [quick_validate.py](/Plugins/skill-factory/skills/scaffolding_templates/skill-creator/scripts/quick_validate.py)
  - [run_skill_evals.py](/Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_skill_evals.py)
  - [test_run_skill_evals.py](/Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/test_run_skill_evals.py)
- Derived readiness artifact:
- [skill-authoring-validation-maturity-matrix.md](/Docs/reference/skill-authoring-validation-maturity-matrix.md)
