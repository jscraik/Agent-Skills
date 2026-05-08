---
schema_version: 1
artifact_id: agent-skills-he-source-prompt-reference-coverage-solution
artifact_type: he-compound-solution
canonical_slug: agent-skills-he-source-prompt-reference-coverage
title: HE Source Prompt Reference Coverage Solution
harness_stage: he-compound
status: complete
date: 2026-05-08
traceability_required: true
origin: .harness/review/2026-05-08-codex-agentic-workstation-original-prompt-gap-review.md
linear_issue: none
linear_milestone: none
asset_family: harness engineering source prompt preservation
owner: Agent Skills Team
source_artifact: .harness/review/2026-05-08-codex-agentic-workstation-original-prompt-gap-review.md
freshness_reviewed_on: 2026-05-08
review_after_days: 90
project_brain_status: not_applicable
---

# HE Source Prompt Reference Coverage Solution

Freshness: 2026-05-08

Project Brain status: not_applicable; no `.harness/knowledge/**` tree is
present in `agent-skills` at capture time.

## Governed Asset

- `Plugins/harness-engineering/skills/he-compound/SKILL.md`
- `Plugins/harness-engineering/skills/he-strategy/SKILL.md`
- `Plugins/harness-engineering/skills/he-strategy/references/source-prompt-preservation.md`
- `Plugins/harness-engineering/skills/he-strategy/references/strategy-output-contract.md`
- `Plugins/harness-engineering/references/stage-context-contract.md`
- `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- `Plugins/harness-engineering/references/artifact-routing-contract.md`
- `Plugins/harness-engineering/references/solution-capture-contract.md`

## Problem

When a user compares HE skill output against an older long-form prompt workflow,
the skill pipeline can appear complete because it writes every expected stage:
intent, architecture review, triage, strategy, ADR/core, refactor, and Linear
plan.

The failure mode is evidence-depth laundering. A sampled `he-strategy` pass can
produce useful first-pass artifacts, then `he-refactor` and `he-linear-plan` can
turn that sampled evidence into authoritative-looking execution artifacts. The
result may be directionally correct but weaker than the original prompt method,
especially when the original prompt required broad repository inspection,
multi-lens review, standards comparison, deletion analysis, drift thresholds,
and interactive correction.

## Resolution

When work like this appears again, `he-compound` should reconstruct the lifecycle
state and preserve the source prompt as active evidence before routing forward.
The next stage should not proceed as a generic strategy/refactor/Linear pass
until the reference set has been loaded and the coverage gap is explicit.

Minimum future handling:

1. Treat the original prompt text as source evidence, not chat noise.
2. Load the stage-specific source prompt preservation reference before
   compressing.
3. Load the output contract for the selected stage.
4. Load the stage context contract before handoff.
5. Record `evidence_depth`, `coverage_scope`, `coverage_gaps`,
   `original_prompt_coverage`, and `downstream_confidence`.
6. If the user wants equivalence to the original prompt method, route to a deep
   `he-strategy` refresh instead of accepting a sampled pipeline as complete.
7. If downstream artifacts already exist, preserve their local validity while
   marking any repo-wide authority gap.

## Blackboard Delta

```yaml
schema_version: he-blackboard-delta/v1
topic: he-source-prompt-reference-coverage
finding:
  previous_pipeline_gap: sampled HE strategy output was operationally useful but not equivalent to the original long-form prompt workflow
  recovery_stage: he-strategy_refresh_required_when_equivalence_is_requested
  source_prompt_status: preserve_as_source_evidence
  required_reference_set:
    - Plugins/harness-engineering/skills/he-strategy/references/source-prompt-preservation.md
    - Plugins/harness-engineering/skills/he-strategy/references/strategy-output-contract.md
    - Plugins/harness-engineering/references/stage-context-contract.md
    - Plugins/harness-engineering/references/agent-native-compression-contract.md
    - Plugins/harness-engineering/references/artifact-routing-contract.md
  required_fields:
    - evidence_depth
    - coverage_scope
    - coverage_gaps
    - original_prompt_coverage
    - downstream_confidence
```

## Evidence

- `.harness/features/2026-05-08-codex-agentic-workstation-intent.md`
  correctly identified the local agentic workstation thesis and TUI hotspot
  risk, but it did not cover the full original prompt checklist.
- `.harness/review/2026-05-08-codex-agentic-workstation-architecture-review.md`
  was a useful sampled architecture review, but it did not deeply apply every
  requested lens from the original prompt method.
- `.harness/refactors/2026-05-08-codex-agentic-workstation-tui-hotspot-decomposition.md`
  produced a strong first refactor program from the evidence available.
- `.harness/linear/2026-05-08-codex-agentic-workstation-tui-hotspot-decomposition-linear-plan.md`
  produced a disciplined Linear-ready active set, but correctly remained tied
  to the selected TUI refactor rather than claiming full repo-wide closure.
- `.harness/review/2026-05-08-codex-agentic-workstation-original-prompt-gap-review.md`
  records the specific gaps and required future guardrails.

## Maintenance Ownership

Harness Engineering owns the stage contracts and reference loading discipline.
Future improvements may tighten `he-strategy` or `he-compound`, but the durable
rule is broader than one skill: source prompts that define workflow equivalence
must be preserved as evidence and checked against the selected stage contracts.

## Future-Agent Rule

If Jamie asks whether HE skill output matches an older prompt pipeline, do not
answer from vibes. Compare the generated artifacts against the preserved prompt
requirements, mark coverage as `covered`, `partial`, `missing`, or `skipped`,
and record whether downstream refactor/Linear artifacts are locally valid or
repo-wide authoritative.

## Project Brain Status

```yaml
project_brain_status: not_applicable
project_brain_evidence:
  source: ".harness/solutions/2026-05-08-agent-skills-he-source-prompt-reference-coverage-solution.md"
  target: null
  reason: "No .harness/knowledge/** Project Brain target exists in this repo at capture time."
```
