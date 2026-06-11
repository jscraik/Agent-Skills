# PU-018: Skills SDK Compact Stage Skill Shape Trace Plan

## Metadata

- schema_version: 1
- stage: sy-trace-plan
- status: superseded_by_slice_spec
- date: 2026-06-11
- branch: main
- worktree: /Users/jamiecraik/dev/agent-skills
- target: Skills SDK governed stage skill product contract
- source_context:
  - User correction that the current 17-heading SDK stage validator shape was not the agreed Skills SDK product shape.
  - User confirmation that `references/*.md` should mean one expert point of view, evidence packet, prior-art source, runbook, or substantial context unit per file.
  - User follow-up that KnowledgeOS may produce SDK-helpful capability pack exports, including monolithic upstream pack documents and future SDK-ready pack export directories.
  - Current local pipeline artifact: `artifacts/recommended-skills-sdk-pipeline.html`.
  - Current capability matrix: `Infrastructure/config/skills-sdk/capability-matrix.v1.json`.

## Decision

Create PU-018 as a product-contract correction before implementation. The agreed shape is:

- `SKILL.md` remains the compact operator-facing instruction surface.
- Governance detail moves into companion files such as `references/contract.yaml`, `references/source-context.yaml`, `references/evals.yaml`, `references/task-profile.json`, and `agents/openai.yaml`.
- Each `references/*.md` file represents one bounded expert viewpoint, evidence source, prior-art note, runbook, or substantial context unit.
- Upstream generated capability pack exports, such as KnowledgeOS pack-level Markdown, may be monolithic source artifacts. They are inputs to future SDK knowledge-capsule extraction, not valid skill-local `references/*.md` output by themselves.
- The current SDK stage validator's 17-heading requirement is treated as validator drift until reconciled with this compact product contract.

## Evidence Checked

- Active repo: `/Users/jamiecraik/dev/agent-skills`.
- Active branch: `main`.
- Local dirty files before this trace:
  - `Infrastructure/config/skills-sdk/capability-matrix.v1.json`
  - `artifacts/recommended-skills-sdk-pipeline.html`
- Current validator enforcing the long heading list:
  - `Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py`
- Current scaffold test mirroring the long heading list:
  - `Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py`
- Current scaffold generator emitting the long heading list:
  - `skills-system/skill-creator/scripts/init_skill.py`
- Current PU-017 spec:
  - `.harness/specs/2026-06-11-skills-sdk-pu-017-governed-review-execution-spec.md`
- Local pipeline/matrix already updated to name PU-018 shape reconciliation as the next slice.
- PU-018 slice spec created from this trace:
  - `.harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md`
- KnowledgeOS upstream export evidence:
  - `/Users/jamiecraik/dev/knowledge-OS/exports/skills/harness-engineering-pack.md` is a monolithic generated pack export.
  - `/Users/jamiecraik/dev/knowledge-OS/exports/evals/harness-engineering-scenarios.json` is a generated eval-scenario export.
  - Command evidence from `/Users/jamiecraik/dev/knowledge-OS`: `bash scripts/validate-assets.sh && bash scripts/smoke-export.sh exports/skills/harness-engineering-pack.md && bash scripts/smoke-export.sh exports/evals/harness-engineering-scenarios.json` -> pass on 2026-06-11, proving current KnowledgeOS local asset validation and export smoke checks for the referenced pack exports.

## Traceability Map

| ID | Intent | Evidence | Acceptance | Owner Files | Proof Needed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Define compact governed SDK stage skill product contract | User rejected the 17-heading list as not agreed | PU-018 spec states compact `SKILL.md` headings and separates visible operator instructions from companion governance | New spec: `.harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md` | Spec review plus later validator tests | ready_for_spec |
| R2 | Keep `SKILL.md` compact | Current validator requires `Stage Contract`, `Preconditions`, `Allowed writes`, `Forbidden writes`, `Execution boundaries`, and `Examples` as H2s | Compact heading contract is enforced for `metadata.sdk_stage` skills | `check_sdk_stage_skill_shape.py`, `init_skill.py`, scaffold tests, existing stage skills | Validator passes after migration | planned |
| R3 | Move governance out of visible headings | User agreed governance belongs in companion files | Governance fields are enforced in structured companion files, not forced visible H2s | `references/contract.yaml`, `references/source-context.yaml`, `references/evals.yaml`, `references/task-profile.json`, `agents/openai.yaml` | Tests prove required governance is present outside `SKILL.md` | planned |
| R4 | Enforce one bounded viewpoint or evidence source per `references/*.md` | User confirmed one expert point of view or evidence source equals one Markdown file | Validator or scaffold guidance checks SDK stage references for focused Markdown units without applying the rule globally to every skill package | `check_sdk_stage_skill_shape.py`, source-context schema or parser helpers, tests | Fixture tests cover focused reference files and mixed mega-file rejection for governed stage skills | planned |
| R5 | Preserve source-context as the loading/provenance map | Current validator already checks source-context markers | `source-context.yaml` indexes reference provenance, load_when, allowed claims, forbidden claims, freshness, and context budget | `references/source-context.yaml` template and validator | Scaffold test verifies expected keys and reference index entries | planned |
| R6 | Migrate existing SDK stage skills without losing content | Current repo has 12 SDK stage skills passing the long-heading validator | Existing long-heading content is either retained under compact sections or moved into companion files | All `SKILL.md` files with `sdk_stage:`, companion references | Shape validator passes and content migration is reviewable | planned |
| R7 | Keep pipeline/status truth aligned | HTML and matrix now identify PU-018 as next slice | Capability matrix, HTML artifact, and `ask sdk status` continue to agree after implementation | `capability-matrix.v1.json`, `recommended-skills-sdk-pipeline.html`, status tests | Status and artifact tests pass | planned |
| R8 | Preserve the KnowledgeOS upstream/export boundary | KnowledgeOS currently emits monolithic generated pack exports intended as neutral downstream artifacts | PU-018 spec says upstream pack exports may be monolithic, while SDK-local `references/*.md` remain bounded capsule files | PU-018 spec, later PU-019 knowledge-capsule spec | Spec review confirms PU-018 does not require SDK runtime dependency on KnowledgeOS | ready_for_spec |
| NG1 | Do not make every skill obey governed stage shape | Base Skills SDK package shape should remain smaller than governed stage shape | Validator scopes compact governed shape only to `metadata.sdk_stage` skills or explicit governed profiles | Validator discovery logic and tests | Non-stage fixture remains valid under base conformance tests | planned |
| NG2 | Do not use `references/` as a dumping ground | Current page already warns about context debt | Markdown references are focused, provenance-indexed, and claim-scoped | `source-context.yaml`, `references/*.md`, tests | Mixed-reference fixture fails in governed stage validator | planned |
| NG3 | Do not turn KnowledgeOS into an SDK runtime dependency | KnowledgeOS is a separate upstream authoring and export project | SDK may ingest portable pack exports later, but governed skills must not require local KnowledgeOS paths at runtime | Future `ask sdk knowledge` or `ask sdk refs` lane, capsule manifests | Later ingestion tests verify vendored capsules include provenance/digests and no runtime source dependency | planned_future |

## Proposed Compact Heading Contract

The PU-018 spec should define the governed SDK stage `SKILL.md` H2 contract as:

1. When to use
2. Required inputs
3. Deliverables
4. Procedure
5. Validation
6. Handoff
7. Failure modes
8. Gotchas
9. References

`When not to use` should remain a spec decision point. The default trace-plan recommendation is to keep it out of the mandatory compact shape unless the spec owner decides it is essential operator guidance.

The compact H2 list should be treated as the exact complete top-level `##` heading set for governed SDK stage skills. Additional `##` headings from the old long contract should fail validation; deeper headings may remain inside compact sections when needed.

## Governance Relocation Map

| Current Long Heading / Concept | New Owner |
| --- | --- |
| Stage Contract | `references/contract.yaml` and `references/source-context.yaml` |
| Preconditions | `references/contract.yaml` |
| Allowed writes | `references/contract.yaml` |
| Forbidden writes | `references/contract.yaml` |
| Execution boundaries | `references/contract.yaml` and `agents/openai.yaml` |
| Examples | Optional focused `references/*.md`, `assets/`, or a compact note under `Gotchas` when necessary |
| Source/provenance | `references/source-context.yaml` |
| Eval expectations | `references/evals.yaml` and `references/task-profile.json` |

## References Rule

For governed SDK stage skills:

- One expert point of view, evidence packet, prior-art source, runbook, or substantial context unit equals one focused `references/*.md` file.
- Do not combine unrelated authorities, evidence lanes, or large mixed dossiers in one Markdown reference.
- `references/source-context.yaml` indexes each reference with provenance, load conditions, allowed claims, forbidden claims, freshness, and budget.
- Structured machine-readable governance remains in YAML or JSON files, not Markdown reference piles.
- Validator enforcement should use source-context metadata such as reference kind, provenance, claim scope, allowed combinations, freshness, and context budget rather than naive word-count or size heuristics.

## KnowledgeOS Boundary Rule

KnowledgeOS pack exports are upstream source artifacts for future SDK knowledge-capsule extraction. They are not governed SDK stage skill reference files by default.

- A monolithic generated pack export, such as `exports/skills/harness-engineering-pack.md`, is allowed at the KnowledgeOS export layer.
- SDK-local Markdown references remain bounded capsule files: one expert viewpoint, evidence lane, prior-art note, runbook, rubric, or substantial context unit per file.
- Future SDK ingestion should consume portable pack export surfaces such as a registry, pack index, snapshot, normalized assets, eval export, and facet slices when available.
- Future SDK ingestion should vendor selected capsules into the skill package and record upstream pack id, selected asset ids, digests, and validation evidence.
- Governed skills must not require runtime access to `/Users/jamiecraik/dev/knowledge-OS`, KnowledgeOS `sources/`, or KnowledgeOS authoring internals.
- PU-018 should include this boundary as future compatibility only. Implementing pack ingestion belongs in a later slice, tentatively PU-019: SDK Knowledge Capsule Ingestion.

## Work Bullets For Tracker Plan

1. Create the PU-018 spec.
   - Path: `.harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md`
   - Acceptance: names the exact compact `SKILL.md` heading contract, companion-file governance boundary, source-context claim controls, reference-file unit rule, KnowledgeOS upstream/export boundary, non-goals, and migration expectations.

2. Create the PU-018 execution plan.
   - Path: `.harness/plan/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-plan.md`
   - Acceptance: lists implementation files, deterministic governed-stage inventory command, migration steps, validation commands, and review focus.

3. Update the SDK stage shape validator.
   - File: `Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py`
   - Acceptance: enforces the exact complete compact headings, companion governance files with minimum keys, source-context reference index and claim-control markers, agent execution metadata, and focused `references/*.md` rule for governed SDK stage skills.

4. Update scaffold generation.
   - File: `skills-system/skill-creator/scripts/init_skill.py`
   - Acceptance: newly scaffolded governed stage skills emit compact `SKILL.md` and move governance into companion files.

5. Update scaffold and validator tests.
   - Files:
     - `Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py`
     - relevant SDK shape tests or new focused tests.
   - Acceptance: tests fail on the old long heading contract and pass on compact shape plus companion governance.

6. Migrate existing SDK stage skills.
   - Scope: every `SKILL.md` with `sdk_stage:`.
   - Acceptance: no instruction content is lost; governance details are moved or linked to companion files.

7. Keep truth surfaces aligned.
   - Files:
     - `Infrastructure/config/skills-sdk/capability-matrix.v1.json`
     - `artifacts/recommended-skills-sdk-pipeline.html`
   - Acceptance: status, HTML artifact, and tests agree about PU-018 without claiming hosted explorer or external readiness.

## Validation Plan

Run the narrowest useful local checks first:

- Command: `/Users/jamiecraik/.venvs/pyyaml/bin/python Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py`
- Command: `python3 -m unittest Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold -v`
- Command: `python3 Infrastructure/tests/test_skills_sdk_capability_status.py -v`
- Command: `python3 -m unittest Infrastructure.tests.test_skills_sdk_pipeline_status_artifact -v`
- Command: `./bin/ask sdk status --json --robot`

If the implementation touches broader authoring validators, add the repo's relevant authoring-family validation wrapper before closeout.

## Evidence Lane Status

- Local repo/worktree lane: pass.
- Product decision lane: pass, based on explicit user confirmation in this thread.
- Trace-plan artifact lane: pass, created by this file.
- Spec lane: pass, created by `.harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md`.
- Execution plan lane: not_started.
- Implementation lane: not_started.
- Validator/scaffold/test migration lane: not_started.
- PR/CI/review/mergeability lanes: not_checked.

## Open Risks

- If `When not to use` remains optional, some stage skills may hide important refusal criteria in companion files. The PU-018 spec should make an explicit keep/drop decision.
- A too-aggressive `references/*.md` validator could misclassify legitimate composite runbooks. The first implementation should scope the rule to governed SDK stage skills and use source-context metadata rather than naive word-count checks.
- A too-broad interpretation of the reference unit rule could reject valid upstream pack exports. PU-018 must scope the one-Markdown-unit rule to SDK-local governed references, not to external pack export artifacts.
- Migration can lose useful examples or boundary language if content is mechanically deleted. Preserve content by moving it to the right companion file or a focused reference.
- Existing tests may encode the old long-heading list in multiple places; run a bounded sibling sweep before closeout.

## Handoff Status

stage: trace-plan
status: superseded_by_slice_spec
next_stage: execution-plan

This trace originally identified PU-018 as the next product-contract slice. The user then selected that slice and routed it through `sy-slice-spec`, producing `.harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md`.

The current authoritative handoff is from the PU-018 slice spec to execution-plan. The execution-plan stage should create `.harness/plan/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-plan.md`, then route implementation only after the compact heading contract, companion governance contract, references rule, and KnowledgeOS boundary are accepted in the spec.
