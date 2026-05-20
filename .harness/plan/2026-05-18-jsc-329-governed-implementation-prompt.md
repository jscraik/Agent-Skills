# JSC-329 Governed Implementation Prompt

Use this prompt to continue the implementation lane without reopening sequencing or scope.

## Objective

Implement JSC-329 first: harden `./bin/ask skills doctor context7 --json --robot` as the fixture-backed Agent Skills Kit readiness spine for the Skills SDK route.

## Source Of Truth

- Plan: `.harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md`
- Spec: `.harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md`
- Linear: JSC-329
- Ubiquitous language: `UBIQUITOUS_LANGUAGE.md`

## Ordered Phases

1. he-work: implement PU-001 through PU-006, bounded to doctor contract code, tests, and evidence artifacts.
2. he-code-review: review the diff for introduced risk and validation gaps.
3. simplify: remove unnecessary complexity while preserving behavior.
4. unslopify: check for dead, stale, or orphaned additions.
5. improve-codebase-architecture: verify boundaries and SDK vocabulary.
6. testing-reviewer: review focused and missing test coverage.
7. ubiquitous-language: verify terminology uses Agent Skills Kit, Skills SDK route, Canonical Skill Source, Runtime Projection, Validation, Packaging, Runtime Adapters, Evidence, and Memory consistently.
8. Between phases, run the smallest relevant validation gate before moving on.
9. Stage only intended files, then run final three-agent review: coderabbit, agent-native-reviewer, adversarial-reviewer.

## Implementation Guardrails

- The stable readiness surface is `data.skill_doctor`, not the outer ask robot envelope.
- The doctor contract owns readiness truth for skills; golden paths and HE front doors may route to it but must not redefine it.
- Do not create concrete schema files unless an existing schema home is discovered or the focused tests cannot honestly validate `contract_schemas` without one.
- Known readiness signals must expose `sdk_layer` in production doctor JSON, not only test-side normalization.
- `next_command` must select actionable blockers before warnings or outcome-proof commands.
- Package readiness, runtime reachability, and outcome proof must remain separate signals.
- A non-zero command exit with parseable `data.skill_doctor.status=blocked` is blocked-readiness evidence, not transport failure.
- Preserve unrelated dirty worktree files and stage nothing until explicit staging phase.

## Validation Spine

- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q`
- `python3 -m py_compile Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `./bin/ask skills doctor context7 --json --robot`
- `./bin/ask skills package context7 --json --robot`
- `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`
- `python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q`
- `rg -n "skill_doctor|next_command|blocked_runtime|outcome_proof_missing|capability_contract_incomplete" Infrastructure/tests Infrastructure/scripts/lib/ask/commands/skills_impl.py`

## Stop Conditions

- The implementation would flatten `data.skill_doctor` into the outer envelope.
- The work would widen into JSC-246, JSC-167, or HE front-door behavior.
- Required validation cannot run and no focused fallback can prove the changed behavior.
- Similar-case feedback requires a wider pattern sweep than the approved JSC-329 slice.
