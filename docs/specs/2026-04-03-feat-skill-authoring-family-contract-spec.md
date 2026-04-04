---
title: Skill Authoring Family Contract
type: feat
status: draft
date: 2026-04-03
origin: docs/brainstorms/2026-04-03-skill-authoring-family-contract-requirements.md
risk: medium
spec_depth: lite
ui_required: false
deepened: 2026-04-03
---

# Skill Authoring Family Contract Spec

## Table of Contents
- [Enhancement Summary](#enhancement-summary)
- [Problem Statement](#problem-statement)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [System Boundary](#system-boundary)
- [Core Domain Model](#core-domain-model)
- [Main Flow / Lifecycle](#main-flow--lifecycle)
- [Interfaces and Dependencies](#interfaces-and-dependencies)
- [Invariants / Safety Requirements](#invariants--safety-requirements)
- [Failure Model and Recovery](#failure-model-and-recovery)
- [Observability](#observability)
- [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)

## Enhancement Summary

**Deepened on:** 2026-04-03
**Mode:** targeted-confidence
**Key areas improved:** clarification-state handling, packaging boundaries, handoff lifecycle, authority model, trust/provenance controls, and full-family validation coverage

- Added an explicit `route_clarification` branch, aligned to the repo question-lifecycle contract, so low-confidence authoring-family prompts fail to clarification instead of guessed ownership.
- Split standalone-skill packaging from plugin packaging and defined validation-first gating plus explicit handoff states so packaging cannot preempt lifecycle judgment.
- Reworked the authority model so this spec is the phase-one family-contract source of truth, while any family reference doc is a derived operational view and runtime-facing asset metadata remains authoritative for each managed surface.
- Expanded provenance, validity-evidence, and validation requirements so install/import and cross-family routing remain auditable across both `utilities/` and `skills-system/` surfaces.

## Problem Statement

The repo's skill-authoring surface has evolved into a useful but ambiguous family:
- `skill-creator` still presents as the starter authoring path for creating or updating a skill in [skills-system/skill-creator/SKILL.md](/Users/jamiecraik/dev/agent-skills/skills-system/skill-creator/SKILL.md#L1)
- `skill-builder` now spans creation, improvement, audit, packaging, and install-distribute work in [utilities/skill-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/utilities/skill-builder/SKILL.md#L51)
- `skill-installer` still owns focused install and curated import flows in [skills-system/skill-installer/SKILL.md](/Users/jamiecraik/dev/agent-skills/skills-system/skill-installer/SKILL.md#L1)
- `codex-plugin-builder` remains the packaging path when the deliverable is a plugin in [utilities/codex-plugin-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/utilities/codex-plugin-builder/SKILL.md#L1)

This family is operationally strong, but not contractually clear:
- `skill-builder` still advertises itself as "Create or update a skill" in [utilities/skill-builder/agents/openai.yaml](/Users/jamiecraik/dev/agent-skills/utilities/skill-builder/agents/openai.yaml#L1) even though its actual scope is much broader
- repo format guidance still omits the current `compatibility` frontmatter key in [utilities/skill-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/utilities/skill-builder/SKILL.md#L79) and [scripts/lint_openai_skill_format.sh](/Users/jamiecraik/dev/agent-skills/scripts/lint_openai_skill_format.sh#L9)
- there is no family-level routing contract that defines which skill should own ambiguous prompts or how handoffs should work

Without a formal contract, planning and implementation would have to invent routing boundaries, validation expectations, and handoff semantics ad hoc.

## Goals

- Define one canonical routing contract across `skill-creator`, `skill-builder`, `skill-installer`, and `codex-plugin-builder`.
- Establish a two-tier authoring model:
  - starter authoring via `skill-creator`
  - expert lifecycle improvement via `skill-builder`
- Preserve focused ownership for `skill-installer` and `codex-plugin-builder`.
- Align frontmatter, metadata, and in-skill routing guidance with current official April 2026 skill guidance.
- Add regression-ready acceptance criteria so routing drift can be detected rather than rediscovered by users.

## Non-Goals

- Do not merge, rename, or delete the family members in this phase.
- Do not specify file-by-file implementation steps or sequencing; that belongs to planning.
- Do not redesign unrelated repo-wide skill routing beyond the four-surface authoring family.
- Do not turn this contract into a general plugin marketplace spec.
- Do not create a dedicated UI spec; this is a system/workflow contract with `ui_required: false`.

## System Boundary

Owned by this spec:
- the canonical routing roles for `skill-creator`, `skill-builder`, `skill-installer`, and `codex-plugin-builder`
- the rules for which skill should win for create, improve, install, package, and mixed prompts
- the handoff rules when a prompt crosses a skill boundary
- the requirement that family-level copy, metadata, and examples reflect the contract
- the requirement that routing regression evals and frontmatter-sync checks protect the contract

Not owned by this spec:
- detailed patch plans for each skill file
- plugin marketplace taxonomy beyond the packaging boundary already owned by `codex-plugin-builder`
- consolidation or deprecation strategy for the family
- broader repo routing across unrelated skills
- implementation details of eval harness internals beyond the required contract shape

## Core Domain Model

### Primary entities

- `SkillSurface`
  - One discoverable skill surface in the authoring family.
  - Phase-one members:
    - `skill-creator`
    - `skill-builder`
    - `skill-installer`
    - `codex-plugin-builder`

- `PrimaryJob`
  - The single strongest user-visible purpose of a `SkillSurface`.
  - Required phase-one values:
    - `starter_authoring`
    - `expert_lifecycle_maintenance`
    - `skill_installation`
    - `plugin_packaging`

- `RoutingIntent`
  - The normalized intent inferred from a user request before a family member is chosen.
  - Required phase-one values:
    - `create_skill`
    - `improve_skill`
    - `audit_or_validate_skill`
    - `install_skill`
    - `package_standalone_skill`
    - `package_as_plugin`
    - `mixed_authoring_and_install`

- `RouteClarification`
  - A route-phase clarification event used when the family contract cannot safely pick one dominant intent or owner.
  - Must include:
    - `question_type: route_clarification`
    - top candidate `SkillSurface` values
    - uncertainty reasons
    - the minimum question needed to resolve ownership
  - The clarification event is a router-owned runtime state, not a family member claiming speculative ownership.

- `RoutingDecision`
  - The chosen family member plus rationale, produced only after route confidence is sufficient or route clarification resolves ambiguity.
  - Must include:
    - chosen `SkillSurface`
    - matched `RoutingIntent`
    - optional delegated companion surface
    - short reason grounded in the family contract

- `HandoffState`
  - The explicit transfer lifecycle when a request crosses a family boundary after a primary owner is already chosen.
  - Required phase-one states:
    - `owned`
    - `handoff_proposed`
    - `handoff_confirmed`
    - `rerouted`
    - `terminal_with_referral`

- `FamilyContract`
  - The canonical durable statement of family roles, strongest triggers, non-triggers, and handoff rules.
  - Phase-one authoritative source: this spec file.
  - A future `docs/reference/skill-authoring-family-contract.md` document, if created, is a derived operational reference and must be mechanically regenerated or parity-checked against this spec instead of acting as equal authority.
  - Must be mirrored into family metadata and examples.
  - Mirrored descriptions, `See Also` guidance, and `agents/openai.yaml` metadata are subordinate views and must not silently override the canonical contract.

- `ContractValidityEvidence`
  - The explicit proof that a skill package is valid enough to install, package, or hand off across family boundaries.
  - Phase-one minimum evidence:
    - frontmatter validation that accepts current official keys, including `compatibility`
    - routing and boundary eval coverage for the active prompt class
    - provenance details for imported or external content
    - a validator-visible pass/fail artifact rather than prose-only assurance

- `RoutingEvalCase`
  - A stable ambiguous or boundary prompt used to verify the family contract.
  - Must include:
    - prompt text
    - expected winning skill
    - acceptable alternative if explicitly allowed
    - failure reason when routing diverges

- `FrontmatterCompatibilityRule`
  - The repo's local interpretation of allowed top-level skill frontmatter keys.
  - Phase-one requirement:
    - include current official keys, including `compatibility`
    - fail clearly when local guidance drifts from the contract

### Canonical routing roles for phase one

| Skill surface | Primary job | Strongest triggers | Non-triggers |
|---|---|---|---|
| `skill-creator` | `starter_authoring` | create first version, scaffold a new skill, finish a just-created scaffold without changing routing or validation posture | deep lifecycle auditing, existing-skill hardening, install execution, plugin packaging |
| `skill-builder` | `expert_lifecycle_maintenance` | improve routing, harden workflow, audit validators/evals, compare variants, package a validated standalone skill for reuse | generic feature coding, plugin conversion, unrelated docs cleanup |
| `skill-installer` | `skill_installation` | list installable skills, install curated skills, import a skill from another repo | authoring from scratch, plugin packaging, broad lifecycle review |
| `codex-plugin-builder` | `plugin_packaging` | scaffold or convert plugin packages, package plugin-owned skills, validate plugin packaging | standalone skill editing when the deliverable is not a plugin |

## Main Flow / Lifecycle

### 1. Assess route confidence before ownership

When a user prompt enters the skill-authoring family, the router must first decide whether ownership is confident enough to continue without clarification.

Clarification rules:
- if top family candidates are too close, route confidence is below the runtime threshold, or the prompt leaves the deliverable boundary ambiguous, emit a `RouteClarification`
- `RouteClarification` must use the repo's canonical `route_clarification` question type and stay in the route phase
- no family member may claim primary ownership while a `RouteClarification` is outstanding
- once clarification resolves the missing intent or deliverable boundary, normal routing resumes from the clarified prompt state

### 2. Normalize the request

Once route confidence is sufficient, the request must normalize to one dominant `RoutingIntent`.

Normalization rules:
- if the user primarily wants a first version of a skill, normalize to `create_skill`
- if the user primarily wants to improve, audit, compare, or quality-gate an existing skill, normalize to `improve_skill` or `audit_or_validate_skill`
- if the user primarily wants to install or import a skill, normalize to `install_skill`
- if the user primarily wants to package a validated standalone skill for reuse outside a plugin boundary, normalize to `package_standalone_skill`
- if the user primarily wants a plugin package or plugin conversion, normalize to `package_as_plugin`
- if the prompt explicitly combines authoring and installation, normalize to `mixed_authoring_and_install`

Existing-skill update discriminator:
- requests to modify an existing skill default to `improve_skill`
- only treat an existing-skill change as `create_skill` when it is limited to finishing an initial scaffold or making scaffold-level edits that do not change:
  - routing boundaries or trigger language
  - validation expectations, evals, or helper scripts
  - bundled-resource shape such as `references/`, `scripts/`, or packaging posture
  - handoff behavior, installation behavior, or plugin-deliverable intent
- ambiguous prompts such as "update this skill" must route to `skill-builder` unless the request explicitly stays inside that narrow scaffold-completion envelope

Packaging discriminator:
- `package_standalone_skill` applies when the output remains a standalone skill bundle or reusable skill asset rather than a plugin package
- `package_as_plugin` applies only when the requested deliverable is explicitly a plugin package, a plugin conversion, or plugin-owned packaging work
- if the prompt says "package this" but does not make clear whether the output should be a standalone skill or a plugin, emit `RouteClarification` instead of guessing

### 3. Select the primary owner

The family contract must choose exactly one primary `SkillSurface` for a request.

Selection rules:
- `create_skill` -> `skill-creator`
- `improve_skill` -> `skill-builder`
- `audit_or_validate_skill` -> `skill-builder`
- `install_skill` -> `skill-installer`
- `package_standalone_skill` -> `skill-builder`
- `package_as_plugin` -> `codex-plugin-builder`
- `mixed_authoring_and_install` -> start with the surface that matches the higher-risk or more contract-defining concern
  - if the user needs lifecycle judgment first, choose `skill-builder`
  - if the package is already built and the work is pure installation, choose `skill-installer`

Precedence rule for mixed prompts:
- when a prompt contains both authoring and installation language, lifecycle-shaping work wins over execution work
- installation wins only when:
  - the skill package is already accepted as valid by `ContractValidityEvidence`, and
  - no routing, workflow, safety, portability, or packaging judgment is still being requested
- if the prompt also implies plugin packaging, `codex-plugin-builder` becomes the primary owner only after lifecycle judgment and validation concerns are already settled, because packaging changes the deliverable boundary itself
- if the prompt includes audit, validation, hardening, or routing work alongside plugin packaging, `skill-builder` remains primary until the skill is contract-valid and then hands off explicitly to `codex-plugin-builder`

### 4. Apply handoff rules

If the chosen skill encounters work outside its primary job, it must hand off explicitly rather than silently absorbing the whole task.

Required handoff rules:
- `skill-creator` may hand off to `skill-builder` once the work becomes primarily about quality gates, variant comparison, or lifecycle hardening
- `skill-builder` may hand off to `skill-installer` once the package is already valid and the remaining task is projection, installation, or runtime visibility
- any family member must hand off to `codex-plugin-builder` when the deliverable becomes a plugin package rather than a bare skill

Handoff integrity rules:
- handoffs must preserve a single primary owner at any given step
- handoffs must follow the explicit state machine:
  - `owned` when the current owner still matches the dominant concern
  - `handoff_proposed` when the current owner detects that another family surface now matches the dominant concern
  - `handoff_confirmed` when the transfer conditions and required validity evidence are satisfied
  - `rerouted` when the downstream owner becomes the sole primary owner
  - `terminal_with_referral` when the current surface cannot safely continue and must stop with a user-visible referral rather than speculative execution
- the originating surface may recommend the next owner, but must not continue to claim full ownership once the request has crossed the contract boundary
- if the downstream owner would still require route ambiguity to be resolved, the flow must return to `RouteClarification` rather than pretending the handoff itself solved the ambiguity
- family docs must explain the most common handoff paths so the behavior is understandable before runtime, not only during troubleshooting

### 5. Keep family copy honest

After the routing contract is defined, each family member must expose copy that reflects its canonical role.

Required effects:
- frontmatter descriptions must say what the skill does and when to use it
- `agents/openai.yaml` metadata, when present, must match the true scope
- positive and negative examples must reflect the family contract instead of historical ambiguity

### 6. Protect the contract with validation

The family contract is not complete until it is protected by regression-ready checks.

Phase-one protection requirements:
- routing eval cases must exist for create-only, improve-only, install-only, standalone-packaging, plugin-only, and mixed prompts
- local frontmatter-validation guidance must include `compatibility`
- family validation coverage must include both `utilities/` and `skills-system/` surfaces governed by this contract
- imported or external skill flows must produce validator-visible provenance and rollback evidence before activation
- phase-one routing and provenance eval ownership lives in `utilities/skill-builder/references/evals.yaml`, executed by `utilities/skill-builder/scripts/run_skill_evals.py`, until a broader family harness replaces it explicitly
- contract failures must be observable as test or lint failures rather than only as chat-level confusion

## Interfaces and Dependencies

### Repo interfaces

- `skills-system/skill-creator/SKILL.md`
  - current starter authoring surface
- `utilities/skill-builder/SKILL.md`
  - current expert-maintainer candidate with broad lifecycle scope
- `skills-system/skill-installer/SKILL.md`
  - current installation surface with explicit helper-script ownership
- `utilities/codex-plugin-builder/SKILL.md`
  - current plugin-packaging surface
- `utilities/skill-builder/agents/openai.yaml`
  - currently exposes narrow UI metadata that must be reconciled with the family contract
- `scripts/lint_openai_skill_format.sh`
  - current repo-level frontmatter-compatibility enforcement
- `skills-system/skill-creator/scripts/quick_validate.py`
  - current `skill-creator` helper validator that must remain compatible with the family frontmatter contract
- `utilities/skill-builder/references/evals.yaml`
  - current concrete eval surface already capable of owning phase-one routing and provenance cases for this family
- `utilities/skill-builder/scripts/run_skill_evals.py`
  - concrete runner for family routing and provenance eval enforcement

### Contract-source boundary

Phase-one source-of-truth rule:
- this spec is the authoritative family contract for role boundaries, mixed-intent precedence, handoff semantics, and validation expectations
- if `docs/reference/skill-authoring-family-contract.md` is created, it is a derived operational reference and must not independently widen, narrow, or contradict this spec
- individual family surfaces must mirror that contract in:
  - frontmatter descriptions
  - `agents/openai.yaml` metadata when present
  - positive and negative examples
  - `See Also` and handoff guidance
- each managed asset still keeps its own authoritative runtime-facing representation:
  - canonical skills use in-file `SKILL.md` metadata and prose for their asset-local representation
  - plugin packages use `.codex-plugin/plugin.json`
  - the family contract coordinates these assets but does not create a second equal-authority editor for their local lifecycle truth
- if a mirrored surface conflicts with the canonical contract, that surface is in degraded contract state until reconciled

### External guidance dependencies

As of **2026-04-03**, the family contract depends on current official guidance that says:
- keep each skill focused on one job
- prefer clear descriptions that say what the skill does and when to use it
- test prompts against skill descriptions to confirm trigger behavior

Authoritative sources:
- [OpenAI Codex Skills best practices](https://developers.openai.com/codex/skills/#best-practices)
- [OpenAI Codex best practices: Turn repeatable work into skills](https://developers.openai.com/codex/learn/best-practices/#turn-repeatable-work-into-skills)
- [Agent Skills specification](https://agentskills.io/specification)

## Invariants / Safety Requirements

- Every family member must have one primary job, even if it can coordinate bounded handoffs.
- No prompt may route to multiple primary owners at the same time.
- Low-confidence or deliverable-ambiguous prompts must fail to `RouteClarification` rather than guessed routing.
- `skill-builder` must not continue to present itself as a narrow starter skill if it remains a broad expert-maintainer surface.
- `skill-installer` must remain the canonical owner of pure installation/import execution.
- `skill-builder` is the canonical owner of standalone-skill packaging when the deliverable remains a skill rather than a plugin.
- `codex-plugin-builder` must remain the canonical owner of plugin packaging decisions.
- Local frontmatter-validation rules must not reject spec-valid `compatibility` usage.
- Family-level examples and metadata must not contradict the canonical routing matrix.
- Handoffs must be explicit and user-visible in docs/examples, not only implied by maintainers' tribal knowledge.
- External install/import work must enforce trusted-source policy, pinned ref or commit when remote content is involved, provenance capture, staged validation before activation, and atomic rollback on failure.
- `skill-installer` and `codex-plugin-builder` must not self-attest contract validity without `ContractValidityEvidence`.

## Failure Model and Recovery

### Failure classes

- `routing_ambiguity`
  - A prompt could plausibly trigger multiple family members because the contract is underspecified or contradictory.

- `metadata_drift`
  - A skill's frontmatter or UI metadata no longer matches its actual role.

- `contract_drift`
  - The durable family contract diverges from individual skill descriptions, examples, or See Also guidance.

- `validation_drift`
  - Eval coverage or lint rules fail to protect the contract, allowing regressions to ship silently.

- `spec_drift`
  - Local frontmatter rules diverge from the current official skill specification, including missing `compatibility` support.

- `partial_rollout_drift`
  - Some family members or validators adopt the new contract while others still reflect legacy boundaries, creating inconsistent routing depending on entrypoint.

- `unresolved_clarification`
  - Route ambiguity or deliverable ambiguity remains unresolved, but an implementation attempts to force ownership anyway.

- `untrusted_import`
  - External skill import or installation proceeds without the required trust, provenance, or rollback controls.

- `validity_attestation_gap`
  - A surface claims a package is installable, packageable, or handoff-ready without the required validator-visible evidence.

### Recovery requirements

- `routing_ambiguity`
  - recover by tightening the routing matrix, examples, or non-trigger guidance before broadening scope further, and by failing to `RouteClarification` until ambiguity is resolved
- `metadata_drift`
  - recover by updating the affected skill's frontmatter and UI metadata to match the canonical role
- `contract_drift`
  - recover by treating the canonical family contract as source of truth and reconciling downstream copies
- `validation_drift`
  - recover by adding or repairing routing evals and lint enforcement before calling the family stable
- `spec_drift`
  - recover with a phase-zero patch that updates repo guidance and frontmatter validators to current official keys, including `compatibility`, across all governed surfaces
- `partial_rollout_drift`
  - recover by treating the family as not yet contract-stable until all primary mirrored surfaces and enforcement points are updated together or explicitly marked as compatibility-only wrappers
- `unresolved_clarification`
  - recover by asking the minimum route clarification question and blocking auto-selection until one dominant intent or deliverable boundary becomes clear
- `untrusted_import`
  - recover by quarantining the imported content, recording provenance, and refusing activation until trust and rollback checks pass
- `validity_attestation_gap`
  - recover by requiring explicit validator outputs before install, packaging, or family handoff can continue

Readiness gate:
- the family contract may be documented as drafted before rollout is complete, but it must not be treated as operationally stable until:
  - this spec is referenced as the canonical family contract by the participating implementation work
  - all four family members expose role-consistent routing copy
  - the frontmatter validation layer accepts `compatibility` across both `utilities/` and `skills-system/` enforcement points
  - routing and provenance eval coverage exists for the defined prompt classes
  - low-confidence routing paths fail to clarification instead of silent owner selection

## Observability

The family contract must be observable through repo-visible signals, not just maintainer judgment.

Required signals:
- this spec is identifiable as the authoritative family contract and any derived family reference stays parity-checked against it
- each family member exposes role-consistent metadata and examples
- frontmatter compatibility lint passes with current official keys, including `compatibility`, across both `utilities/` and `skills-system/` validators
- routing regression evals report pass/fail against stable ambiguous prompts, including clarification-required cases
- standalone-skill packaging and plugin packaging have different expected owners and different pass/fail fixtures
- mixed-intent prompts have documented expected primary owners and handoff behavior
- external install/import flows surface provenance, quarantine, validation, and rollback outcomes
- rollout readiness can distinguish `drafted contract` from `stable contract`

Suggested verification surfaces:
- targeted routing eval fixtures for the authoring family
- `bash scripts/lint_openai_skill_format.sh --mode strict`
- helper-validator invocation must be path-aware and environment-aware:
  - use a Python interpreter with `PyYAML` available for `skills-system/skill-creator/scripts/quick_validate.py`
  - current repo-friendly example: `~/.venvs/pyyaml/bin/python skills-system/skill-creator/scripts/quick_validate.py skills-system/skill-creator`
- routing/provenance eval invocation must include the governed skill path:
  - current repo-friendly example: `python3 utilities/skill-builder/scripts/run_skill_evals.py utilities/skill-builder --eval-mode smoke`
- any family-specific regression checks added in planning

Minimum readiness checks for planning:
- confirm the implementation work references this spec as the phase-one canonical family contract
- confirm `utilities/skill-builder/agents/openai.yaml` no longer under-describes the skill if the broad expert-maintainer posture remains
- confirm frontmatter lint and helper validators accept `compatibility` in both help text and enforcement logic across governed surfaces
- confirm validator guidance specifies the required runtime and positional skill path instead of naming bare non-runnable commands
- confirm mixed-intent routing cases report one owner plus explicit handoff behavior instead of dual ownership ambiguity
- confirm clarification-required prompts fail to `RouteClarification`
- confirm install/import checks cover provenance capture, staged validation, and rollback evidence

## Acceptance and Test Matrix

- SA1. This spec is the phase-one canonical family contract defining the primary job, strongest triggers, and non-triggers for `skill-creator`, `skill-builder`, `skill-installer`, and `codex-plugin-builder`.
- SA2. The canonical routing matrix routes create-only prompts to `skill-creator`, improve/audit prompts to `skill-builder`, install-only prompts to `skill-installer`, standalone-skill packaging prompts to `skill-builder`, and plugin-packaging prompts to `codex-plugin-builder`.
- SA3. Mixed authoring-and-install prompts define a single primary owner plus explicit handoff rules instead of dual ownership.
- SA4. `skill-builder` metadata and routing copy no longer describe it as merely "Create or update a skill" if its broad expert-maintainer role is preserved.
- SA5. `skill-installer` remains the canonical owner of pure installation and import execution paths.
- SA6. `codex-plugin-builder` remains the canonical owner when the output is a plugin package rather than a standalone skill.
- SA7. The repo's frontmatter-validation guidance accepts current official top-level keys, including `compatibility`, and fails cleanly on unknown keys.
- SA8. Routing regression evals exist for at least these prompt classes:
  - create-only
  - improve-only
  - install-only
  - standalone-skill packaging
  - plugin-only
  - mixed authoring and install
- SA9. Family members include user-visible handoff guidance where requests cross ownership boundaries.
- SA10. Planning can consume this spec without inventing ownership boundaries, validation goals, or the relationship between the phase-zero patch and the broader family contract.
- SA11. Mixed authoring-and-install prompts apply the precedence rule consistently:
  - lifecycle-shaping work routes first to `skill-builder`
  - pure already-valid package installation routes to `skill-installer`
  - pure already-valid plugin packaging routes to `codex-plugin-builder` only after lifecycle judgment is settled
- SA12. The family contract distinguishes `drafted` from `stable` rollout status, and partial adoption across family members is treated as degraded rather than silently acceptable.
- SA13. The chosen canonical contract source is mirrored into family descriptions, examples, and handoff guidance without contradictory copies remaining in active surfaces.
- SA14. Prompts that combine audit, validation, hardening, or routing work with plugin packaging keep `skill-builder` as the primary owner until the skill is contract-valid, then hand off explicitly to `codex-plugin-builder`.
- SA15. Low-confidence or deliverable-ambiguous prompts fail to a route-phase `RouteClarification` state instead of guessed owner selection.
- SA16. Handoffs follow the explicit lifecycle `owned -> handoff_proposed -> handoff_confirmed -> rerouted` or stop safely at `terminal_with_referral` when transfer conditions are not met.
- SA17. Any `docs/reference/skill-authoring-family-contract.md` file, if introduced, behaves as a derived operational view and cannot independently redefine the authoritative family contract in this spec.
- SA18. External install/import flows require trusted-source policy, pinned remote refs when applicable, provenance capture, quarantine or staged validation before activation, and atomic rollback on failure.
- SA19. `ContractValidityEvidence` is required before pure installation, standalone-skill packaging, or plugin-packaging handoff can proceed.
- SA20. Phase-zero compatibility enforcement updates land across all governed validation surfaces, including `scripts/lint_openai_skill_format.sh` and `skills-system/skill-creator/scripts/quick_validate.py`.
- SA21. Family validation coverage includes the governed surfaces in both `utilities/` and `skills-system/`, not only one directory family.
- SA22. `utilities/skill-builder/references/evals.yaml` and `utilities/skill-builder/scripts/run_skill_evals.py` own the phase-one routing and provenance eval contract until a replacement harness is explicitly adopted.

## Open Questions

- Should `skill-builder` become explicit-only immediately, or should invocation-policy changes wait until routing evals establish a baseline?

## Definition of Done

- A standard planning pass can name the exact files and validations needed to implement the contract without reopening role boundaries.
- The family routing matrix is explicit enough that ambiguous prompts either have defined expected owners or fail to `RouteClarification`.
- The phase-zero `compatibility` sync patch is captured as part of the contract, not as an unrelated cleanup note.
- The spec now distinguishes canonical family authority, asset-local authoritative representations, mirrored surfaces, and degraded rollout states clearly enough that planning can sequence rollout without inventing readiness rules.
- The spec defines standalone-skill packaging versus plugin packaging strongly enough that packaging cannot bypass lifecycle validation.
- The spec is verified for required sections, frontmatter, and stable `SA` IDs.
