---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-validator-solution
artifact_type: he-compound-solution
canonical_slug: agent-skills-first-principles-factory-gate-validator
title: First-Principles Factory Gate Validator Solution
harness_stage: he-compound
status: complete
date: 2026-05-09
traceability_required: true
origin: .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md
linear_issue: none
linear_milestone: First-Principles Factory Gate (proposed)
asset_family: skill and plugin factory governance
owner: Harness Engineering
source_artifact: .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md
freshness_reviewed_on: 2026-05-09
review_after_days: 90
project_brain_status: not_applicable
---

# First-Principles Factory Gate Validator Solution

Freshness: 2026-05-09

Project Brain status: not_applicable; no `.harness/knowledge/**` tree is
present in `agent-skills` at capture time.

## Governed Asset

- `Infrastructure/references/first-principles-factory-gate.md`
- `Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py`
- `Infrastructure/scripts/testing/test_validate_first_principles_gate.py`
- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
- `Plugins/skill-factory/skills/**`
- `Plugins/plugin-factory/skills/**`
- `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec.md`
- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`

## Problem

The first-principles factory gate was present as strategy, hook context, and
factory-lane procedure, but there was no deterministic check that made missing
or malformed gate evidence visible when `skill-factory` or `plugin-factory`
work claimed readiness.

The risky failure mode was ceremonial adoption: future factory work could say
"first principles" in prose while still copying an inherited package shape,
with no structured record of the user outcome, rejected assumption, smallest
effective mechanism, artifact decision, evidence, or validation proof.

## Resolution

Use a warning-first validator before strict enforcement.

The reusable pattern is:

1. Keep the gate vocabulary in one shared reference.
2. Add a dedicated parser helper for structured gate evidence.
3. Accept only explicit evidence from frontmatter, fenced YAML, or a labeled
   markdown section.
4. Reject prose-only mentions as non-evidence.
5. Classify inspected paths as `pass`, `warn`, `fail`, or `skipped`.
6. Keep default validation warning-first for active historical factory files.
7. Expose strict mode for focused tests and future rollout gates.
8. Scope authoring-family integration to active factory skill/plugin paths and
   skip archives, generated projections, runtime mirrors, caches, and unrelated
   docs.
9. Capture an eval that closes only the validator-enforcement phase and keeps
   behavior-changing proof open.

This avoids two bad outcomes at once: silent drift back to copied templates and
noisy hard-failure rollout against historical files that predate the gate.

## Blackboard Delta

```yaml
schema_version: he-blackboard-delta/v1
topic: first-principles-factory-gate-validator
finding:
  solved_problem: deterministic_warning_first_gate_validation
  reusable_pattern: warning_first_validator_before_strict_factory_governance
  active_validator: Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py
  integration_gate: Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
  accepted_evidence_locations:
    - YAML frontmatter
    - fenced YAML first_principles_gate block
    - labeled First-Principles Gate markdown section
  rejected_evidence:
    - prose-only first-principles mentions
    - blank or TODO/TBD placeholder gate fields
    - not_applicable without first_principles_gate_reason
  rollout_policy:
    default: warn
    strict: helper_only_until_later_rollout
  phase_boundary:
    phase_3: structural_validator_and_test_enforcement
    phase_4: behavior_changing_factory_output_eval_proof
```

## Evidence

Phase 3 source artifacts:

- `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec.md`
- `.harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec-technical-review.md`
- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`

Implementation artifacts:

- `Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py`
- `Infrastructure/scripts/testing/test_validate_first_principles_gate.py`
- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`

Validation evidence recorded in the Phase 3 eval:

- `python3 -m py_compile Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py Infrastructure/scripts/testing/test_validate_first_principles_gate.py`
  passed.
- `python3 -m pytest Infrastructure/scripts/testing/test_validate_first_principles_gate.py -q`
  passed with `11 passed in 0.03s`.
- `python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q`
  passed with `12 passed, 34 subtests passed in 0.19s`.
- `git diff --check -- Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py Infrastructure/scripts/testing/test_validate_first_principles_gate.py Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
  passed.
- `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py Infrastructure/scripts/testing/test_validate_first_principles_gate.py Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
  passed.
- `python3 Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md`
  emitted the expected warning for missing gate evidence and exited `0`.
- `python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`
  passed.

## Maintenance Ownership

Harness Engineering owns the lifecycle phase boundary and eval discipline.
Skill Factory and Plugin Factory own the factory lane behavior that eventually
uses the gate. The authoring-family validator owns warning-first structural
visibility until a later approved phase enables stricter enforcement.

Future field or decision changes should update the shared gate reference, the
validator helper constants, and the focused parser tests together.

## Future-Agent Rule

When adding governance checks to factory outputs, do not jump straight to a
hard CI failure. First prove the evidence shape deterministically, scope the
changed paths tightly, keep historical/archive/generated paths out of the
blast radius, and write an eval that separates structural validation from
behavior-changing factory output proof.

For this factory gate specifically:

- Phase 3 can be treated as complete with follow-up.
- The broader initiative is not complete until Phase 4 proves the gate changes
  factory output quality.
- A warning from `validate_first_principles_gate.py` is useful signal, not an
  automatic blocker, unless a future approved rollout runs `--strict`.

## Project Brain Status

```yaml
project_brain_status: not_applicable
project_brain_evidence:
  source: ".harness/solutions/2026-05-09-agent-skills-first-principles-factory-gate-validator-solution.md"
  target: null
  reason: "No .harness/knowledge/** Project Brain target exists in this repo at capture time."
```
