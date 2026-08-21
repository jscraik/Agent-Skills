# PU-018: Skills SDK Compact Stage Skill Shape Execution Plan

## Metadata

- schema_version: 1
- stage: execution-plan
- status: ready_for_work
- date: 2026-06-11
- branch: main
- target: Skills SDK governed stage skill product contract
- source_spec: .harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md
- source_trace: retired_superseded_evidence; the accepted slice spec is the authoritative prior-stage contract
- next_stage: work

## Approved Intent

Implement PU-018 by changing the governed SDK stage skill contract from the old long 17-heading `SKILL.md` shape to the compact product contract defined by the slice spec.

The work stage must update validator behavior, scaffold output, scaffold tests, existing governed stage skills, and SDK truth surfaces. It must not implement KnowledgeOS ingestion or mutate runtime projections as source.

## Current Evidence

- Active repo: `/Users/jamiecraik/dev/agent-skills`
- Active branch: `main`
- Previous-stage artifact: `.harness/specs/2026-06-11-skills-sdk-pu-018-compact-stage-skill-shape-spec.md`
- Superseded trace artifact: retired after its accepted product contract was materialized by the slice spec.
- Historical reviewer output for this completed stage is not a current proof source.
- Final adversarial review status: round 3 clean across contract-boundary, implementation-readiness, and evidence-risk lanes.
- Current dirty baseline from `git status --short --branch`:
  - modified: `Infrastructure/config/skills-sdk/capability-matrix.v1.json`
  - modified: `artifacts/recommended-skills-sdk-pipeline.html`
  - untracked: PU-018 spec/review artifacts

## Governed-Stage Inventory

Use this exact command before implementation edits and record the output in the work evidence:

```bash
rg -l "sdk_stage:" --glob 'SKILL.md' --glob '!**/.agents/**' --glob '!**/.skillsets/**' --glob '!**/cache/**' | sort
```

Current inventory captured on 2026-06-11:

```text
plugins/synaipse-harness/skills/sy-brainstorm/SKILL.md
plugins/synaipse-harness/skills/sy-eval-report/SKILL.md
plugins/synaipse-harness/skills/sy-execution-plan/SKILL.md
plugins/synaipse-harness/skills/sy-reconcile/SKILL.md
plugins/synaipse-harness/skills/sy-reframe/SKILL.md
plugins/synaipse-harness/skills/sy-reinforce/SKILL.md
plugins/synaipse-harness/skills/sy-review/SKILL.md
plugins/synaipse-harness/skills/sy-slice-spec/SKILL.md
plugins/synaipse-harness/skills/sy-strategy/SKILL.md
plugins/synaipse-harness/skills/sy-trace-plan/SKILL.md
plugins/synaipse-harness/skills/sy-tracker-plan/SKILL.md
plugins/synaipse-harness/skills/sy-work/SKILL.md
```

If this command returns a different inventory at work time, the work stage must record the changed inventory and migrate the current discovered set. Do not rely on the stale count alone.

## File Targets

### Primary Implementation

- `Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py`
  - Replace the old 17-heading `EXPECTED_STAGE_HEADINGS` with the exact compact H2 set from the spec.
  - Reject extra top-level `##` headings for governed SDK stage skills.
  - Validate required companion files as non-empty structured mappings or JSON objects.
  - Validate required minimum keys for:
    - `references/contract.yaml`
    - `references/evals.yaml`
    - `references/task-profile.json`
    - `references/source-context.yaml`
    - `agents/openai.yaml`
  - Validate source-context claim controls:
    - `references`
    - `allowed_claims`
    - `forbidden_claims`
    - `freshness`
    - `context_budget`
  - Validate each source-context reference entry has path, kind, provenance, load condition, claim scope, freshness, and context budget metadata.
  - Enforce the SDK-local reference unit rule through metadata, not word count.
  - Preserve the existing SynAIpse copied-reference quality audit unless the compact contract makes a targeted adjustment necessary.

- `skills-system/skill-creator/scripts/init_skill.py`
  - Replace the scaffolded `SKILL_TEMPLATE` H2s with the compact set:
    - `When to use`
    - `Required inputs`
    - `Deliverables`
    - `Procedure`
    - `Validation`
    - `Handoff`
    - `Failure modes`
    - `Gotchas`
    - `References`
  - Move scaffolded stage contract, preconditions, allowed writes, forbidden writes, exit criteria, and execution boundaries into companion templates.
  - Update `SOURCE_CONTEXT_TEMPLATE` with required claim-control fields.
  - Update `CONTRACT_TEMPLATE`, `EVALS_TEMPLATE`, `TASK_PROFILE_TEMPLATE`, and OpenAI YAML generation if needed so scaffold output satisfies the validator.

- `Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py`
  - Update expected scaffold headings to the compact exact H2 set.
  - Add assertions for companion-file minimum keys.
  - Add assertions for `source-context.yaml` claim controls and per-reference metadata.
  - Add assertions for `agents/openai.yaml` execution metadata.

### Migration Targets

- All current governed stage skills from the inventory command:
  - `plugins/synaipse-harness/skills/sy-brainstorm/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-eval-report/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-execution-plan/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-reconcile/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-reframe/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-reinforce/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-review/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-slice-spec/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-strategy/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-trace-plan/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-tracker-plan/SKILL.md`
  - `plugins/synaipse-harness/skills/sy-work/SKILL.md`

For each skill:

- Keep compact operator-facing instructions in `SKILL.md`.
- Move stage contract, preconditions, allowed writes, forbidden writes, exit criteria, execution boundaries, and examples into companion files or focused references.
- Preserve links to `./references/source-context.yaml`.
- Keep frontmatter `metadata.sdk_stage`, `metadata.lifecycle_state: active`, and `metadata.command_visibility: orchestrator`.
- Update `references/source-context.yaml` to index focused references and required claim controls.
- Update `agents/openai.yaml` only where required to satisfy minimum execution metadata.

### Truth Surface Targets

- `Infrastructure/config/skills-sdk/capability-matrix.v1.json`
  - Keep PU-018 as the next/active compact-shape correction until implementation completes.
  - After implementation, record evidence refs for validator/scaffold/migration tests.
  - Do not claim hosted explorer, PR, CI, review-thread, tracker, or merge readiness.

- `artifacts/recommended-skills-sdk-pipeline.html`
  - Keep the public HTML pipeline aligned with the compact-shape contract and KnowledgeOS boundary.
  - Do not make the HTML artifact the authority over validator behavior.

## Work Order

1. Reconfirm baseline.
   - Run `git status --short --branch`.
   - Run the governed-stage inventory command.
   - Record the current inventory in the work evidence.
   - Do not stage or revert unrelated dirty files.

2. Update validator constants and parsing.
   - Change `EXPECTED_STAGE_HEADINGS` to the compact exact list.
   - Ensure `markdown_h2_headings` captures only top-level `##` headings.
   - Preserve exact-order equality so extra old headings fail.

3. Add companion-file validators.
   - Add helper readers for YAML and JSON companion files.
   - Fail on missing, empty, non-mapping/non-object, or schema-shallow companion files.
   - Validate required minimum keys from the spec.
   - Keep errors specific enough to identify the skill and file.

4. Add source-context and reference-unit validation.
   - Require source-context fields from the spec.
   - Require `references` entries to declare reference kind, path, provenance, load condition, claim scope, freshness, and context budget metadata.
   - Enforce the reference unit rule through metadata:
     - accepted bounded reference
     - accepted bounded composite runbook
     - rejected mixed dossier
     - upstream pack export exemption
   - Avoid word-count, file-size, or purely content-length heuristics.

5. Update scaffold templates.
   - Rewrite `SKILL_TEMPLATE` to the compact heading contract.
   - Move governance details into `CONTRACT_TEMPLATE` and related companion templates.
   - Expand `SOURCE_CONTEXT_TEMPLATE` to satisfy the validator.
   - Ensure generated `agents/openai.yaml` satisfies the minimum execution metadata contract.

6. Update tests and fixtures.
   - Update `Infrastructure/scripts/testing/test_skill_creator_lifecycle_scaffold.py`.
   - Add or update focused validator tests if an existing test module is available; otherwise add a narrow test file near the validator or in the closest repo test lane.
   - Cover old long heading rejection, extra H2 rejection, missing companion key rejection, empty companion rejection, source-context claim-control rejection, and reference-unit fixture cases.

7. Migrate existing governed stage skills.
   - Use the captured inventory as the migration checklist.
   - Migrate each `SKILL.md` to compact headings.
   - Move removed heading content into companion files without deleting useful instruction content.
   - Update source-context files and agent metadata so the validator can pass.
   - Keep changes scoped to governed SDK stage skills and their companion files.

8. Update truth surfaces.
   - Update capability matrix evidence/next-slice fields after validator and tests pass.
   - Update HTML artifact wording only where needed to match implemented PU-018 truth.
   - Preserve the KnowledgeOS boundary: no ingestion implementation, no runtime dependency claims.

9. Run validation gates in order.
   - Stop at the first required failure unless the failure is clearly unrelated and can be classified.
   - Record exact command, outcome, and blocker/fallback if blocked.

10. Review and closeout.
   - Run a focused diff review for accidental runtime projection edits.
   - Run closeout gate or record blocker.
   - Handoff to PR/commit lane only if separately requested.

## Validation Gates

Run these in this order from `/Users/jamiecraik/dev/agent-skills`.

### Required Narrow Gates

```bash
rg -l "sdk_stage:" --glob 'SKILL.md' --glob '!**/.agents/**' --glob '!**/.skillsets/**' --glob '!**/cache/**' | sort
```

Expected: lists the governed-stage migration inventory.

```bash
/Users/jamiecraik/.venvs/pyyaml/bin/python Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py
```

Expected after implementation: pass and report all governed stage skills.

```bash
python3 -m unittest Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold -v
```

Expected after implementation: pass with compact scaffold expectations.

```bash
python3 Infrastructure/tests/test_skills_sdk_capability_status.py -v
```

Expected after implementation: pass.

```bash
python3 -m unittest Infrastructure.tests.test_skills_sdk_pipeline_status_artifact -v
```

Expected after implementation: pass.

```bash
./bin/ask sdk status --json --robot
```

Expected after implementation: pass and align with matrix truth.

### Required Closeout Gate

```bash
./bin/ask repo closeout --changed --json --robot
```

Expected: pass or blocked with a concrete blocker and nearest meaningful fallback. A dirty-worktree blocker must be classified separately from PU-018 validator/scaffold correctness.

### Conditional Gates

Run these if the work stage touches the relevant surface:

- If package readiness or skill routing changes:
  ```bash
  ./bin/ask skills audit plugins/synaipse-harness/skills/sy-execution-plan --level strict --json --robot
  ```

- If plugin package metadata changes:
  ```bash
  python3 Infrastructure/scripts/validation-and-linting/check_plugin_active_archive_links.py
  python3 Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py
  ```

- If the work stage adds new validator test files, run the closest unittest or pytest target for that file.

## Rollback Plan

PU-018 implementation should be rollbackable by file class:

- Validator rollback:
  - Revert changes in `check_sdk_stage_skill_shape.py` if compact validation blocks unrelated work unexpectedly.
  - Keep the spec/plan artifacts; they describe the intended product contract even if implementation needs another pass.

- Scaffold rollback:
  - Revert `init_skill.py` template changes and scaffold test updates together.
  - Do not leave scaffold output and tests on different contracts.

- Migration rollback:
  - Revert migrated governed stage skill directories as one group if validator changes are abandoned.
  - Do not keep compact `SKILL.md` files under the old validator.

- Truth-surface rollback:
  - Revert capability matrix and HTML artifact wording if implementation does not land.
  - Preserve the KnowledgeOS boundary note unless the product decision changes.

Never use destructive git commands against user-owned dirty work. Use normal patch reversal or a scoped commit revert only after explicit authorization.

## Risk Controls

- Stage leakage:
  - Work stage may edit implementation files. This execution-plan stage must not.
  - PR, CI, review-thread, tracker, and mergeability lanes remain not checked.

- Scope creep:
  - PU-018 does not implement KnowledgeOS ingestion, pack registry consumption, or knowledge-capsule extraction.
  - Keep any KnowledgeOS references as upstream boundary language only.

- Validator brittleness:
  - Do not validate reference quality through file length, word count, or broad prose heuristics.
  - Use explicit source-context metadata and fixtures.

- Migration content loss:
  - Before deleting old long-heading content, decide whether it moves to `references/contract.yaml`, `agents/openai.yaml`, a focused reference, or a compact section.
  - The work evidence should call out any content intentionally removed as obsolete.

- Dirty worktree:
  - Existing HTML, matrix, trace, spec, and review artifacts are part of the current PU-018 lane.
  - Do not revert unrelated user or prior-agent changes.

## Evidence Lane Status

- Local repo/worktree lane: pass for planning; dirty state observed and recorded.
- Previous-stage artifact lane: pass; source spec exists and is ready for execution-plan.
- Execution-plan artifact lane: pass once this file exists.
- Implementation lane: not_started.
- Validator/scaffold/test migration lane: not_started.
- KnowledgeOS ingestion lane: intentionally_out_of_scope.
- PR/CI/review/tracker/mergeability lanes: not_checked.

## Exit Conditions

This execution-plan stage is complete when this file exists, names the concrete file targets, states implementation order, records validation gates, separates evidence lanes, and hands off to work without editing implementation sources.

## Handoff To Work

stage: execution-plan
status: ready_for_work
next_stage: work
blocked_by: []

The work stage should implement the plan in the order above, stop on the first required validation failure, and preserve the PU-018 KnowledgeOS boundary as a non-implementation contract.
