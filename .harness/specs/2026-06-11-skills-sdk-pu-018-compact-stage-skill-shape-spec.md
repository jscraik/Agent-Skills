# PU-018: Skills SDK Compact Stage Skill Shape Spec

## Metadata

- schema_version: 1
- stage: slice-spec
- status: ready_for_execution_plan
- date: 2026-06-11
- branch: main
- target: Skills SDK governed stage skill product contract
- source_trace: retained_superseded_evidence at .harness/traces/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-trace-plan.md; this accepted slice spec materializes the product decision
- owner surfaces:
  - Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py
  - skills-system/skill-creator/scripts/init_skill.py
  - Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py
  - Infrastructure/config/skills-sdk/capability-matrix.v1.json
  - artifacts/recommended-skills-sdk-pipeline.html

## Approved Intent

PU-018 corrects the governed SDK stage skill product contract before implementation.

The current validator and scaffold require a long 17-heading `SKILL.md` shape for skills with `metadata.sdk_stage`. That shape is now classified as validator drift. A governed SDK stage skill must keep `SKILL.md` compact as the operator-facing instruction surface and move detailed governance into companion files.

This spec defines the compact visible contract, the companion-file governance boundary, the reference-file unit rule, and the upstream KnowledgeOS export boundary. It does not implement the validator, scaffold, migration, or knowledge-ingestion lane; those belong to the next execution-plan and implementation stages.

## Product Contract

A governed SDK stage skill is a skill whose `SKILL.md` frontmatter includes `metadata.sdk_stage`.

A governed SDK stage skill must have:

- Compact operator-facing `SKILL.md` instructions.
- Structured companion governance files.
- Provenance-indexed references.
- Agent execution metadata.
- No runtime dependency on upstream knowledge-authoring repositories.

### Required Frontmatter

The `SKILL.md` frontmatter must include:

```yaml
name: <handle>
description: "... Use when ..."
metadata:
  skill-type: <type>
  version: "<version>"
  sdk_stage: <stage-name>
  lifecycle_state: active
  command_visibility: orchestrator
```

The exact `skill-type` and `version` values remain owned by existing skill conventions. PU-018 does not rename handles or change command visibility.

### Required SKILL.md H2 Headings

The governed SDK stage `SKILL.md` must use this exact and complete H2 heading order:

1. When to use
2. Required inputs
3. Deliverables
4. Procedure
5. Validation
6. Handoff
7. Failure modes
8. Gotchas
9. References

`##` heading text is case-sensitive after trimming surrounding whitespace. Additional `##` headings are forbidden for governed SDK stage skills. Deeper headings such as `###` may be used inside these sections when they do not recreate the removed governance headings as visible top-level operator sections.

`When not to use` is intentionally not mandatory in PU-018. Refusal criteria, preconditions, forbidden writes, and execution boundaries belong in `references/contract.yaml` unless a stage has short operator-facing guidance that belongs under `Gotchas` or `Procedure`.

### Required Companion Files

A governed SDK stage skill must include:

```text
references/contract.yaml
references/evals.yaml
references/task-profile.json
references/source-context.yaml
agents/openai.yaml
```

`SKILL.md` must link to `./references/source-context.yaml` from the References section.

The validator and scaffold must not satisfy this contract with empty placeholder files. PU-018 requires a minimum companion-file validation contract:

| File | Required minimum keys |
| --- | --- |
| `references/contract.yaml` | `schema_version`, `skill`, `stage`, `preconditions`, `allowed_writes`, `forbidden_writes`, `execution_boundaries`, `exit_criteria` |
| `references/evals.yaml` | `schema_version`, `skill`, `stage`, `eval_scenarios`, `success_criteria` |
| `references/task-profile.json` | `schema_version`, `skill`, `stage`, `task_type`, `inputs`, `outputs`, `validation_profile` |
| `references/source-context.yaml` | source-context keys defined below |
| `agents/openai.yaml` | `schema_version`, `skill`, `stage`, `role`, `instructions`, `tool_policy`, `output_contract` |

### Governance Relocation

Governance detail must move out of visible `SKILL.md` headings:

| Concept | Owner |
| --- | --- |
| Stage contract | `references/contract.yaml` and `references/source-context.yaml` |
| Preconditions | `references/contract.yaml` |
| Allowed writes | `references/contract.yaml` |
| Forbidden writes | `references/contract.yaml` |
| Execution boundaries | `references/contract.yaml` and `agents/openai.yaml` |
| Examples | Optional focused `references/*.md`, `assets/`, or compact `Gotchas` note |
| Source and provenance | `references/source-context.yaml` |
| Eval expectations | `references/evals.yaml` and `references/task-profile.json` |

### Source Context Contract

`references/source-context.yaml` must remain the loading and provenance map. It must include at least these markers:

```yaml
schema_version:
skill:
stage:
template:
original_references:
references:
load_when:
provenance_policy:
allowed_claims:
forbidden_claims:
freshness:
context_budget:
```

Each source-context `references` entry must identify the referenced path, reference kind, provenance, load conditions, allowed claims, forbidden claims, freshness, and context budget impact. The PU-018 execution plan may refine exact field nesting, but it must preserve these controls as validator-visible fields rather than prose-only guidance.

## References Rule

For governed SDK stage skills, one Markdown reference file must represent one bounded unit:

- one expert viewpoint
- one evidence packet
- one prior-art source
- one runbook
- one rubric
- one substantial context unit

Do not combine unrelated authorities, evidence lanes, or large mixed dossiers in one skill-local Markdown reference. Structured governance belongs in YAML or JSON, not in Markdown reference piles.

This rule applies to SDK-local governed stage references. It must not be applied globally to every skill package, every repository document, or upstream generated export artifact.

The validator should enforce this rule through source-context metadata rather than brittle content heuristics. Required metadata should identify reference kind, authority/provenance, claim scope, allowed combinations, and whether a composite runbook is intentionally bounded. Fixture coverage must include an accepted bounded reference, an accepted intentionally bounded composite runbook, a rejected mixed dossier, and an upstream pack export that remains outside SDK-local reference validation.

## KnowledgeOS Boundary

KnowledgeOS and similar systems may produce monolithic upstream capability-pack exports. Those exports are valid upstream source artifacts for future SDK knowledge-capsule extraction, but they are not valid skill-local `references/*.md` output by themselves.

PU-018 must preserve this boundary:

- Upstream pack exports may be monolithic distribution artifacts.
- SDK-local Markdown references remain bounded capsule files.
- Governed skills must not require runtime access to `/Users/jamiecraik/dev/knowledge-OS`, KnowledgeOS `sources/`, or KnowledgeOS authoring internals.
- Future SDK knowledge ingestion should consume portable pack export surfaces such as registry, pack index, snapshot, normalized assets, eval export, and facet slices when available.
- Future SDK knowledge ingestion should vendor selected capsules into the skill package and record upstream pack id, selected asset ids, digests, and validation evidence.

Implementing knowledge-pack ingestion is out of scope for PU-018 and should become a later slice, tentatively PU-019: SDK Knowledge Capsule Ingestion.

## Requirements

### R1: Enforce Compact Governed Stage Headings

Given a `SKILL.md` with `metadata.sdk_stage`, when the SDK stage shape validator runs, then it must require the compact H2 heading contract and reject the old mandatory 17-heading contract.

### R2: Preserve Companion Governance

Given a governed SDK stage skill, when the validator runs, then it must require non-empty companion governance files, minimum companion keys, source-context claim controls, and `agents/openai.yaml` execution metadata without forcing governance concepts into visible `SKILL.md` H2 headings.

### R3: Generate Compact New Stage Skills

Given the skill creator scaffolds a governed SDK stage skill, when scaffold generation completes, then it must emit the compact `SKILL.md` heading shape and the required companion files.

### R4: Scope The Reference Unit Rule

Given SDK-local governed stage Markdown references, when validation runs, then references must be provenance-indexed and bounded to one viewpoint, evidence lane, runbook, rubric, prior-art source, or substantial context unit.

The validator must not reject monolithic upstream pack exports merely because they are large or mixed. Upstream exports are inputs, not SDK-local governed references.

### R5: Migrate Existing Governed Stage Skills

Given existing governed SDK stage skills that currently pass the long-heading validator, when PU-018 implementation completes, then every migrated stage skill must pass the compact validator without losing instruction content. Content should be retained under compact headings or moved into companion files.

The execution plan must discover and record the governed-stage inventory with an exact command before edits, use that inventory as the migration checklist, and prove after migration that the discovered set passes the updated validator.

### R6: Keep Truth Surfaces Aligned

Given the capability matrix, HTML pipeline artifact, and `ask sdk status`, when PU-018 implementation completes, then they must agree that compact stage skill shape is the governed product contract without claiming hosted explorer, external review, CI, PR, or merge readiness.

## Acceptance Criteria

1. This slice spec defines the compact product contract, companion-file boundary, reference-unit rule, KnowledgeOS boundary, non-goals, validation expectations, and execution-plan handoff.
2. The stage shape validator enforces the exact complete compact H2 heading set for `metadata.sdk_stage` skills and rejects extra top-level H2 headings from the old long contract.
3. The validator rejects missing, empty, or schema-shallow companion governance files, including missing required `agents/openai.yaml` execution metadata.
4. The scaffold generator emits compact governed stage skills with required companion files and minimum companion keys.
5. Tests fail on the old mandatory long heading contract and pass on the compact shape plus companion governance.
6. `references/source-context.yaml` remains required and validator-visible fields cover reference index entries, allowed claims, forbidden claims, freshness, and context budget.
7. SDK-local `references/*.md` validation has fixture coverage for an accepted bounded reference, an accepted intentionally bounded composite runbook, a rejected mixed dossier, and an upstream pack export exemption.
8. Migration proof records the governed-stage inventory command, the pre-edit inventory, and post-migration validator proof for that inventory.
9. The spec and implementation preserve the KnowledgeOS upstream/export boundary and do not introduce a runtime dependency on KnowledgeOS.
10. Capability matrix, HTML pipeline artifact, and SDK status tests stay aligned after implementation.

## Non-Goals

- Do not implement KnowledgeOS ingestion, pack registry consumption, or knowledge capsule extraction in PU-018.
- Do not require every skill package to follow governed SDK stage shape.
- Do not apply the one-Markdown-reference rule globally outside governed SDK stage references.
- Do not delete useful existing stage-skill content during migration.
- Do not claim PR, CI, review-thread, tracker, hosted explorer, deployment, or merge readiness.
- Do not mutate runtime projections such as `.agents/**`, `.skillsets/**`, plugin caches, or user home skill roots as source.

## Validation Plan

The execution plan should start with the narrowest useful local checks and widen only as implementation scope requires:

```bash
/Users/jamiecraik/.venvs/pyyaml/bin/python Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py
python3 -m unittest Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold -v
python3 Infrastructure/tests/test_skills_sdk_capability_status.py -v
python3 -m unittest Infrastructure.tests.test_skills_sdk_pipeline_status_artifact -v
./bin/ask sdk status --json --robot
```

If implementation touches broader authoring validators, add the relevant repo wrapper before closeout.

For validator, scaffold, migration, or status-surface changes, the execution plan must also run `./bin/ask repo closeout --changed --json --robot` or record it as blocked with the concrete blocker and nearest meaningful fallback.

## Evidence Lane Status

- Local repo/worktree lane: pass, active worktree is `/Users/jamiecraik/dev/agent-skills` on `main`; command evidence: `git status --short --branch` showed existing dirty files in `Infrastructure/config/skills-sdk/capability-matrix.v1.json`, `artifacts/recommended-skills-sdk-pipeline.html`, and untracked PU-018 harness artifacts.
- Previous-stage artifact lane: retained_superseded_evidence; the cited trace remains available at `.harness/traces/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-trace-plan.md`, while its accepted product decision is materialized in this slice spec.
- Product decision lane: pass, based on the explicit user corrections and confirmations materialized by this slice spec.
- Slice-spec artifact lane: pass, created by this file.
- Execution-plan lane: not_started.
- Implementation lane: not_started.
- Validator/scaffold/test migration lane: not_started.
- PR/CI/review/mergeability lanes: not_checked.

## Exit Conditions

PU-018 slice-spec is complete when this spec exists, names the compact product contract, preserves the KnowledgeOS boundary, separates evidence lanes, and hands off only to execution-plan.

## Handoff To Execution Plan

stage: slice-spec
status: ready_for_execution_plan
next_stage: execution-plan

The execution-plan stage should create `.harness/plan/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-plan.md`, then sequence validator, scaffold, tests, migration, and truth-surface updates without implementing KnowledgeOS ingestion.
