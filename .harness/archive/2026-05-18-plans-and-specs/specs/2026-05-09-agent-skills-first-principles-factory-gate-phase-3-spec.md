---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-3-spec
artifact_type: he-spec
canonical_slug: agent-skills-first-principles-factory-gate-phase-3
title: First-Principles Factory Gate Phase 3 Spec
harness_stage: he-spec
status: deepened
date: 2026-05-09
deepened: 2026-05-09
traceability_required: false
origin: .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-eval.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
risk: medium
depth: bounded
ui: false
---

# First-Principles Factory Gate Phase 3 Spec

## Deepening Enhancement Summary

This deepening pass turns the Phase 3 spec from a general validator idea into a
bounded enforcement contract:

- selects an evidence-location policy that `he-plan` can implement without
  reopening product scope;
- chooses the initial enforcement posture: warning-only for existing active
  files and hard failure only for explicit new factory-output fixtures in
  tests;
- makes parser behavior deterministic enough for focused unit tests;
- separates authoring-family validator scope from Phase 4 behavior eval proof;
- adds false-positive controls for archived fixtures, generated projections,
  metadata-only changes, and unrelated package edits;
- defines closure blockers so Phase 3 cannot accidentally become a full
  factory-gate readiness claim.

## Mode Decision

Selected stage: `he-spec`.

Selected slice: Phase 3 from
`.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`:
`Validator And Test Enforcement`.

Slice status: ready for specification after Phase 1 and Phase 2 eval artifacts
validated successfully.

Tracker status: no Linear issue exists. Linear mutation is out of scope unless
the user explicitly asks for it.

Artifact route status: pass. This durable spec belongs under
`.harness/specs/`.

Linear delta status: not applicable. No live Linear objects were inspected or
mutated.

## Problem

Phase 1 made the first-principles factory gate visible in factory routers and
bundled `SessionStart` hook context. Phase 2 added the shared gate reference
and wired seven factory lanes to it. The gate is now present, but the repo has
no deterministic check that catches missing or malformed gate evidence when a
factory-created or factory-hardened artifact claims readiness.

Without Phase 3, future factory work can still drift back to copied templates:
a skill or plugin can be produced, hardened, or routed without recording the
actual user outcome, copied assumption rejected, smallest effective mechanism,
artifact decision, evidence, and validation proof. That would preserve the
words "first principles" while losing the behavior the gate was meant to
protect.

## Goals

- Add deterministic validator/test coverage for first-principles gate evidence
  in factory-created or factory-hardened artifacts.
- Start with warning-only or scoped failure behavior that prevents false
  positives on historical fixtures and unrelated packages.
- Make missing gate evidence visible in the authoring-family validation lane.
- Keep Phase 3 focused on structural enforcement; behavior-changing eval proof
  remains Phase 4.
- Preserve the Phase 2 reference as the single source of truth for field names,
  decision values, and gate semantics.
- Produce validator output that a future `he-eval-report` can cite directly
  without inferring whether enforcement was warning-only, strict, skipped, or
  not applicable.

## Non-Goals

- Do not add factory eval fixtures or benchmark scenarios that prove behavior
  changes. That is Phase 4.
- Do not require historical archived fixtures to be rewritten.
- Do not make `plugin_hooks` required.
- Do not add MCP tools, apps, new plugin surfaces, or generated projections.
- Do not mutate Linear.
- Do not edit user-level plugin copies, `.agents/**`, `.skillsets/**`, or
  runtime mirrors.
- Do not block all existing skills/plugins merely because they predate the
  gate.

## Linear Contract

Source Linear plan:
`.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md`.

Suggested parent payload:
`[agent-skills] Add first-principles gate to Skill and Plugin Factory`.

Suggested sub-issue payload:
`[agent-skills] Enforce first-principles gate evidence in factory validation`.

Payload status: suggested only. No Linear objects have been created.

## Boundary

In scope:

- authoring-family validation checks for first-principles gate evidence;
- focused unit tests for the validator behavior;
- one small parser/helper module if that is cleaner than embedding parsing in a
  shell script;
- optional helper functions or fixtures needed by those tests;
- focused updates to factory builder/validator surfaces only if the existing
  authoring-family gate cannot express the check cleanly;
- validation evidence showing existing Phase 1/2 surfaces still pass.

Candidate implementation paths:

- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py`
- `Infrastructure/scripts/testing/test_validate_skill_authoring_family_benchmarks.py`
- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`
- `Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/skill_gate.py`
- `Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/test_skill_gate.py`
- `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.pyw`

Out of scope:

- `he-work` implementation for Phase 4 eval proof;
- broad package-generation behavior changes;
- live model eval execution;
- release-ready trusted live eval mode;
- plugin marketplace/install behavior;
- changes outside the factory authoring family unless a direct validator
  dependency requires them.
- automatic rewrites that insert gate evidence into existing skills/plugins.

## Baseline

Current validated evidence:

- Phase 1 eval validates as an HE eval report.
- Phase 2 eval validates as an HE eval report.
- `Infrastructure/references/first-principles-factory-gate.md` defines the
  gate schema and decisions.
- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py` already checks
  the shared reference exists and selected factory lanes link to it.
- `validate_skill_authoring_family.sh` already runs authoring-family structural
  checks, Python tests, plugin bundled hook tests when matching files change,
  and security/eval contract checks for selected family members.

Current gap:

- No validator currently checks that a generated, hardened, or readiness-claiming
  factory artifact contains a parseable `first_principles_gate` evidence record
  or an explicit not-applicable decision.

Deepened baseline decision:

- The first implementation should prefer a standalone Python helper invoked by
  the authoring-family shell gate over complex shell parsing. Existing shell
  code is already responsible for runner selection and scoping; gate evidence
  parsing is structured data work and belongs in Python.

## Domain Model

`first_principles_gate` evidence:

- A structured or parser-detectable record proving the factory decided what to
  build, improve, document, defer, or reject from fundamentals rather than from
  copied package shape.

Required gate fields:

- `desired_outcome`
- `user_specific_constraints`
- `copied_assumption_rejected`
- `fundamental_constraints`
- `smallest_effective_mechanism`
- `artifact_decision`
- `rejected_alternatives`
- `evidence_required`
- `validation_proof`
- `stop_or_pivot_condition`

Allowed decisions:

- `BUILD_SKILL`
- `BUILD_PLUGIN`
- `ADD_HOOK`
- `ADD_MCP_TOOL`
- `ADD_APP`
- `ADD_EVAL`
- `IMPROVE_EXISTING`
- `DOCS_ONLY`
- `DO_NOT_BUILD`

Valid exemption:

- `first_principles_gate: not_applicable` is allowed only for trivial
  metadata, typo, projection, or mechanical maintenance changes that do not
  create, harden, refactor, route, package, or claim readiness for a skill or
  plugin.
- A valid exemption must include a short reason field, such as
  `first_principles_gate_reason`, when the evidence shape supports structured
  fields.

Invalid exemption:

- A new skill/plugin, a factory hardening result, a package readiness claim, or
  a routing handoff cannot mark the gate not applicable merely to avoid writing
  the evidence.

## Lifecycle

1. A factory lane creates, hardens, refactors, routes, or packages a skill or
   plugin.
2. The lane records `first_principles_gate` evidence or a valid
   `not_applicable` exemption in its output, handoff, or generated artifact
   metadata.
3. The authoring-family validation lane detects whether the changed files imply
   factory output or factory readiness work.
4. The validator checks the gate record for required keys, allowed decisions,
   and empty-placeholder values.
5. In Phase 3, failures are scoped to new/changed factory-output surfaces or
   warning-only for existing historical fixtures, depending on the plan's final
   implementation choice.
6. The validator reports precise file/path evidence and remediation text.
7. Phase 4 later proves that this enforcement changes factory decisions.

## Enforcement Policy

Phase 3 should implement a warning-first rollout:

- changed active factory output or readiness files with missing/malformed gate
  evidence emit warnings by default;
- explicit validator unit-test fixtures for new factory outputs may assert hard
  failure behavior so strict mode is proven before it is enabled broadly;
- historical archive fixtures, generated projections, runtime mirrors, and
  unrelated package edits are skipped or warning-only;
- a future strict mode may be added only when the validator has evidence that
  it does not block historical fixtures or unrelated packages.

The validator may expose an internal `--strict` or test-only option if that
keeps failure behavior deterministic. The authoring-family default must remain
safe for the existing dirty repo and current fixture set.

## Evidence Location Policy

The validator should accept gate evidence from any of these locations:

- YAML frontmatter key `first_principles_gate`;
- fenced YAML block containing a top-level `first_principles_gate`;
- labeled markdown section whose heading contains `First-Principles Gate` and
  whose body contains parseable `key: value` lines for the required fields.

Preferred generated-artifact shape:

```yaml
first_principles_gate:
  desired_outcome: ""
  user_specific_constraints: []
  copied_assumption_rejected: ""
  fundamental_constraints: []
  smallest_effective_mechanism: ""
  artifact_decision: ""
  rejected_alternatives: []
  evidence_required: []
  validation_proof: []
  stop_or_pivot_condition: ""
```

Factory handoff text may be accepted in Phase 3 only if it is parser-detectable
and stable. Free prose such as "I thought from first principles" is not valid
gate evidence.

## Scope Detection Rules

The authoring-family gate should run the first-principles validator when
changed files intersect at least one of these categories:

- active factory skill entrypoints under `Plugins/skill-factory/skills/**` or
  `Plugins/plugin-factory/skills/**` that create, harden, refactor, route, or
  package skills/plugins;
- factory validator/helper scripts under
  `Infrastructure/scripts/validation-and-linting/**`;
- focused factory tests under `Infrastructure/tests/**` or
  `Infrastructure/scripts/testing/**`;
- new or modified factory output fixtures selected by the Phase 3 plan.

The check should skip or avoid hard failure for:

- `.agents/**`;
- `.skillsets/**`;
- `Plugins/**/fixtures/budget-archive/**`;
- generated projection/runtime mirrors;
- metadata-only changes that carry a valid `not_applicable` reason;
- unrelated docs or packages outside the factory authoring family.

## Interfaces

Validator interface:

- Accept a file or directory set derived from the authoring-family gate's
  changed-file scope.
- Detect first-principles gate evidence in markdown frontmatter, fenced YAML,
  or clearly labeled markdown sections.
- Validate required keys and allowed `artifact_decision` values.
- Reject records whose required values are blank placeholders.
- Classify outcomes as `pass`, `warn`, `fail`, or `skipped` so warning rollout
  can be tested separately from strict-mode behavior.
- Emit deterministic messages with a stable prefix suitable for CI logs, for
  example `[family-gate] first-principles gate warning:` or
  `[family-gate] ERROR: first-principles gate`.
- Return machine-readable JSON from the helper if practical; otherwise keep
  text output stable enough for unit tests.

Authoring-family interface:

- Continue supporting `--changed-files`.
- Run the new check only when changed files intersect factory-created,
  factory-hardened, or factory-validation surfaces.
- Print a clear skip message when the changed-file scope does not require the
  first-principles validator.
- Keep unrelated validation lanes unchanged.
- Preserve current live eval trust behavior; do not enable live eval mode by
  default.

Test interface:

- Include at least one passing fixture with a complete gate record.
- Include at least one failing fixture missing a required key.
- Include at least one failing fixture with an invalid `artifact_decision`.
- Include at least one valid `not_applicable` exemption case.
- Include a regression check that historical/archive fixtures are not forced
  through strict failure unless explicitly selected as new output.
- Include one changed-file scope test proving unrelated files do not invoke the
  validator as a blocker.

## Invariants

- Phase 3 enforcement must use the Phase 2 shared reference vocabulary.
- The validator must not invent extra required fields beyond the Phase 2
  minimum schema.
- `IMPROVE_EXISTING`, `DOCS_ONLY`, and `DO_NOT_BUILD` are successful decisions
  when evidence supports them.
- Existing archived fixtures must not become blockers unless the implementation
  explicitly scopes them as active outputs.
- Warning-only mode is acceptable for Phase 3 if strict mode creates false
  positives; the plan must state which mode is selected.
- The validator must improve proof without materially increasing always-loaded
  skill context.
- Passing Phase 3 does not imply full factory-gate readiness; Phase 4 eval
  proof remains required.
- The first-principles validator must be deterministic and local; no live model
  calls are allowed in Phase 3.
- The validator must not require `plugin_hooks = true`; it validates factory
  evidence, not runtime hook execution.

## Failure And Recovery

Failure: validator blocks historical fixtures.

Recovery: narrow enforcement to changed active factory outputs or downgrade
historical checks to warnings.

Failure: validator accepts placeholder gate records.

Recovery: add non-empty value checks and a negative unit test for placeholder
strings such as `""`, `TODO`, `TBD`, and `not sure`.

Failure: validator requires the gate for trivial metadata-only changes.

Recovery: allow explicit `not_applicable` only with a mechanical-change reason
and test that exemption.

Failure: implementation duplicates the full schema into multiple `SKILL.md`
entrypoints.

Recovery: revert duplicated prose and keep the schema in
`Infrastructure/references/first-principles-factory-gate.md`.

Failure: Phase 3 claims behavior improvement without eval proof.

Recovery: downgrade closure language to structural enforcement only and keep
Phase 4 open.

## Observability

The new validator output must make these states distinguishable:

- gate evidence found and valid;
- gate evidence missing;
- gate evidence malformed;
- decision value invalid;
- required field blank or placeholder;
- exemption accepted;
- historical fixture skipped or warned.
- changed-file scope skipped because no factory output/readiness file was
  selected.

The output should include enough path evidence for `he-code-review` and
`he-eval-report` to verify the finding without rerunning broad discovery.

## Gate Profile

```yaml
gate_profile:
  risk_class: mixed
  proven_risks:
    - validation behavior changes can block factory work
    - false positives on historical fixtures would create noisy governance
    - closure language could overclaim before Phase 4 eval proof
  required_contracts:
    - Plugins/harness-engineering/references/gate-selection-contract.md
    - Plugins/harness-engineering/references/first-principles-contract.md
    - Infrastructure/references/first-principles-factory-gate.md
    - Plugins/harness-engineering/references/artifact-routing-contract.md
  skipped_contracts:
    - contract: plugin-hook-capability-contract
      reason: Phase 3 validates gate evidence; it does not add hook runtime behavior.
    - contract: security specialist scan
      reason: no auth, secrets, permissions, sandbox, or external side-effect path is in scope.
    - contract: domain model production
      reason: domain language is limited to existing factory-gate vocabulary.
  minimum_proof_required:
    continue_to_next_stage: focused validator tests, authoring-family changed-file validation, artifact lints, and diff check pass
    safe_to_close: Phase 3 eval report records structural enforcement proof and keeps Phase 4 open
    block_next_stage: false positives on historical fixtures, missing negative tests, ambiguous warning/failure policy, or overclaiming behavior proof
  evidence_basis: harness
  downstream_route: he-plan
```

## First Principles Check

```yaml
first_principles_check:
  verified_failure: "Factory gate presence is currently advisory; no deterministic check catches missing or malformed gate evidence in readiness-claiming factory output."
  fundamental_constraint: "Validation must catch drift without forcing historical fixtures or unrelated packages through new strict rules."
  assumption_being_challenged: "Because the gate is documented and linked, future factory outputs will naturally use it."
  smallest_effective_mechanism: "A scoped validator/test enforcement slice in the existing authoring-family validation lane."
  analogy_or_template_rejected: "Adding a new governance stage, MCP tool, app, or broad package generator rewrite."
  proof_required: "Focused positive and negative tests plus authoring-family changed-file validation that proves missing/malformed gate evidence is reported without broad false positives."
  context_load_effect: neutral
  routing_effect: clearer
  decision_type: Type 1
  outcome: proceed
```

## Acceptance Matrix

| ID | Acceptance Criterion | Verification |
| --- | --- | --- |
| SA1 | Phase 3 introduces a deterministic first-principles gate evidence check in the existing authoring-family validation path or a directly invoked helper from that path. | Inspect validator implementation and run focused tests. |
| SA2 | The check validates the Phase 2 required keys and allowed `artifact_decision` values without adding new required schema fields. | Unit test complete, missing-key, and invalid-decision fixtures. |
| SA3 | The check rejects blank or placeholder required values. | Negative fixture with blank/TODO/TBD values fails or warns as selected by the plan. |
| SA4 | The check supports an explicit `first_principles_gate: not_applicable` exemption only for trivial/mechanical changes and requires a reason when structured evidence can carry one. | Unit test valid and invalid exemption cases. |
| SA5 | Historical fixtures and unrelated packages are not hard-blocked by default. | Regression test or changed-file scoped validation proves historical/archive paths are skipped or warning-only. |
| SA6 | Validator output includes precise file/path evidence and stable remediation language. | Test or captured command output asserts stable warning/error prefix and path text. |
| SA7 | Phase 3 validation passes the relevant focused tests, `git diff --check`, and authoring-family changed-file validation. | Record exact commands and outcomes in the Phase 3 plan/eval. |
| SA8 | Phase 3 closeout explicitly states that behavior-changing eval proof remains Phase 4. | Phase 3 eval report includes this boundary. |
| SA9 | The validator accepts gate evidence from frontmatter, fenced YAML, or a labeled markdown section, and rejects unstructured first-principles prose. | Parser unit tests cover all accepted locations and the prose-only negative case. |
| SA10 | The authoring-family gate emits an explicit skip/warn/fail/pass classification for first-principles validation. | Focused tests or captured command output assert classification text. |
| SA11 | Phase 3 does not add live model evals, plugin hook runtime requirements, generated projections, or broad package-generator rewrites. | Diff inspection and changed-file validation. |

## Linear Traceability

No Linear objects exist. Traceability is local to `.harness` artifacts until
the user asks for tracker mutation.

Suggested mapping if Linear is later created:

- Parent: `[agent-skills] Add first-principles gate to Skill and Plugin Factory`
- Sub-issue: `[agent-skills] Enforce first-principles gate evidence in factory validation`
- Acceptance IDs: SA1 through SA11
- Status recommendation after implementation: `Complete with follow-up` only
  if Phase 3 proof passes and Phase 4 remains explicitly open.

## Validation Plan

Minimum commands for Phase 3 implementation:

```bash
python3 -m py_compile <changed-python-validator-or-test-files>
python3 -m pytest <focused-test-targets> -q
git diff --check
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files <phase-3-changed-files>
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec.md
```

If a new validator helper is added, include direct unit tests for that helper.
If the existing authoring-family gate is changed, include one command that
proves `--changed-files` scopes Phase 3 correctly.

## Assumptions

- Phase 3 starts scoped and warning-first by default. Strict failure is allowed
  only in focused tests or behind an explicit implementation-mode flag until a
  later plan proves broad strict mode is safe.
- The existing authoring-family validation lane is the right enforcement
  surface because both factory plugins already use it for structural checks.
- Phase 4 will own behavioral eval fixtures and closure proof.
- Linear remains unmutated.

## First Slice

The first implementation slice should be one validator helper plus focused unit
tests. Wire it into `validate_skill_authoring_family.sh` only after the helper
can distinguish valid, missing, malformed, invalid-decision, placeholder, and
not-applicable cases.

Do not begin with broad script rewrites or package generator changes.

## Resolved Questions

- Phase 3 default behavior is warning-first; strict failure is testable but not
  broadly enabled by default.
- Gate evidence may live in frontmatter, fenced YAML, or a labeled markdown
  section if it is parser-detectable.
- `not_applicable` should carry a reason when the evidence format supports a
  reason field.

## Open Questions

- Should the implementation add a new Python helper path under
  `Infrastructure/scripts/validation-and-linting/`, or extend an existing
  Python validator used by `validate_skill_authoring_family.sh`?
- Which exact active generated-output fixture, if any, should Phase 3 use to
  prove strict failure without touching archive fixtures?
- Should the strict-mode flag be public CLI surface in Phase 3 or kept as a
  unit-test helper until Phase 4?

## Done

Phase 3 is done when:

- the bounded validator behavior is implemented;
- positive and negative tests pass;
- changed-file authoring-family validation passes;
- warning-first default behavior is recorded in the Phase 3 eval;
- Phase 3 eval report records enforcement proof;
- no Linear mutation has occurred unless separately authorized;
- Phase 4 remains open for behavior-changing eval proof.

## he-plan Handoff

Next stage: `he-plan`.

Plan target:
`.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md`.

Planning must resolve the helper location, exact changed-file trigger set,
strict-mode exposure, and focused test targets before authorizing `he-work`.
