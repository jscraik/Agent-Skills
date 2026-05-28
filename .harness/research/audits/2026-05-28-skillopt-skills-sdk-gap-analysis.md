# SkillOpt Skills SDK Gap Analysis

Date: 2026-05-28
Primary evidence: `/Users/jamiecraik/Downloads/SkillOpt.pdf`, supplied SkillOpt/evo context, current Agent Skills Kit code tree.
Scope: Decide whether SkillOpt-style trainable skill optimization should change the Skills SDK contract, with `$autoresearch` as the local implementation comparison point.

## Executive Decision

Yes, there are several ideas worth adding to the Skills SDK, but not as a broad optimizer engine yet.

The highest-leverage addition is a small, schema-backed **skill optimization contract** that sits beside the existing package contract, eval contract, and optional skillflow contract. The SDK should make trainable-skill loops safe to run by requiring explicit splits, bounded edits, acceptance gates, rejected-edit evidence, promotion policy, and fixed-surface protection before any autonomous skill-improvement loop can claim a durable improvement.

The repo already has the right operating instincts in `$autoresearch`: baseline first, bounded hypotheses, guard commands, held-out/protected checks, `min_delta`, keep/discard decisions, and ledger-backed evidence. The gap is that these are mostly prose and local workflow convention, not yet a reusable SDK contract that another skill, repo, or agent can discover and validate mechanically.

Recommended stance:

- Add **SkillOpt-inspired optimization metadata and validators** now.
- Improve `$autoresearch` into the SDK lane that operates that contract.
- Do not build a full parallel tree-search/evo engine in this repo yet.
- Do not allow agents to rewrite canonical `SKILL.md` from optimizer output without a reviewed promotion step.

## Current Codebase Evidence

### Existing Strengths

`$autoresearch` already encodes the core loop in natural language:

- [`Skills/agent-ops/autoresearch/SKILL.md`](../../Skills/agent-ops/autoresearch/SKILL.md) says the loop is: baseline, hypothesize, patch, score, decide, record.
- The workflow requires parser contract, guard command, held-out checks, `noise_runs`, aggregation, `min_delta`, and confirmation before keeping changes.
- It rejects Goodhart behavior: if the benchmark always exits 0, if a protected task regresses, or if evaluator/data/cache edits inflate the score, discard or block.
- The contract declares fixed surfaces: benchmark harness, evaluator, data prep, datasets, tokenizer files, and guard commands in [`Skills/agent-ops/autoresearch/references/contract.yaml`](../../Skills/agent-ops/autoresearch/references/contract.yaml).
- Eval cases already cover missing stop condition, noisy metrics, evaluator contract setup, held-out/protected regression, prompt injection, and destructive command pressure in [`Skills/agent-ops/autoresearch/references/evals.yaml`](../../Skills/agent-ops/autoresearch/references/evals.yaml).

The package system now has a place to express deterministic skill mechanics:

- [`Infrastructure/config/schemas/skillflow.v1.schema.json`](../../Infrastructure/config/schemas/skillflow.v1.schema.json) defines an optional workflow graph for parts of a skill that should not improvise.
- [`Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`](../../Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py) detects `execution_mode`, validates `workflows/skillflow.json` presence when required, and reports a `skillflow-contract.v1` object in package readiness.

### Current Runtime Truth

Running:

```bash
./bin/ask skills package autoresearch --json --robot
```

showed:

- `status: warning`
- `workflow_contract.status: not_declared`
- `workflow_contract.execution_mode: prose`
- `readiness_summary.sdk_contract_missing_fields: commands, permission_profile, portability_profile`
- `reference_quality.status: blocked_validation` because the current package checker expects `claims` and `cases`, while `autoresearch/references/evals.yaml` currently has `cases` but no top-level `claims`.

This means `$autoresearch` is a strong operational skill, but not yet a fully declared Skills SDK package by the current readiness contract.

## SkillOpt Pattern Extraction

### Pattern: Trainable Skill Artifact

Description: Treat the skill document as an optimized external state of a frozen agent, not as static prompt prose.

Evidence: SkillOpt keeps the task-execution model fixed and trains only a text skill document. A separate optimizer model reads rollout evidence and proposes bounded add/delete/replace edits.

Codebase fit: High. The Skills SDK already treats skills as package artifacts with canonical source/projection boundaries. This should become an explicit optimization lane for skill packages, not a replacement for `SKILL.md`.

Implementation opportunity: Add `optimization` metadata to `references/contract.yaml` and expose it through `ask skills package`.

Risk: If treated as free self-modification, the agent can erase the safety value of the contract. Durable promotion must remain reviewed.

### Pattern: Train/Selection/Test Split Contract

Description: Use training examples for proposal generation, a held-out selection split to accept/reject candidate skill edits, and a disjoint test split for reported performance.

Evidence: SkillOpt uses deterministic train/selection/test splits; selection accepts or rejects candidate skills; headline scores come from held-out test data.

Codebase fit: Medium. `$autoresearch` mentions held-out/protected checks, but no schema requires split names, paths, seeds, or selection/test separation.

Implementation opportunity: Define `skill-optimization-contract.v1.schema.json` with:

```yaml
splits:
  train:
    path: ...
    role: proposal_generation
  selection:
    path: ...
    role: candidate_acceptance
  test:
    path: ...
    role: final_report_only
split_seed: 42
```

Risk: For open-ended skill quality tasks, automatic splits may be artificial. Allow `human_review` or `model_judge` gates, but require the evaluator authority to be explicit.

### Pattern: Bounded Text Edit Budget

Description: Limit each candidate update to a small number of patch-style edits, with schedules such as constant, linear, cosine, or autonomous.

Evidence: SkillOpt uses a textual learning rate/edit budget, default `Lt = 4` with cosine decay and floor `Lt = 2`.

Codebase fit: Partial. `$autoresearch` says one reversible hypothesis, but does not mechanically constrain candidate edit count, target file set, or patch mode.

Implementation opportunity: Add:

```yaml
edit_policy:
  mode: patch
  operations: [add, delete, replace]
  max_edits: 4
  schedule: cosine
  floor: 2
  protected_paths:
    - references/evals.yaml
    - evaluator/**
    - data/**
```

Risk: Too much constraint can block legitimate skill rewrites. Provide a separate `rewrite_required` decision that exits optimization and asks for human-approved redesign.

### Pattern: Strict Selection Gate

Description: Accept candidate skill edits only if they strictly improve selection score; ties are rejected.

Evidence: SkillOpt accepts a candidate only when selection score is strictly greater than the current score.

Codebase fit: Medium. `$autoresearch` has `min_delta`, guards, and keep/discard language, but the package contract does not expose a candidate acceptance gate.

Implementation opportunity:

```yaml
acceptance_gate:
  split: selection
  rule: strict_improvement
  ties: reject
  min_delta: 0.01
  guard_failure: discard
  report_test_score_only_after_acceptance: true
```

Risk: Noisy metrics can reject useful improvements or accept lucky runs. Keep `noise_runs`, aggregation, and confidence interval policy in the same schema.

### Pattern: Rejected-Edit Buffer

Description: Preserve rejected edits and failure patterns as negative feedback for later optimizer proposals.

Evidence: SkillOpt keeps a step buffer containing rejected edits and observed failure patterns; optional rejected-edit buffer appears in the ablations.

Codebase fit: Low. `$autoresearch` mentions discarded attempts and ledger history, but there is no rejected edit artifact schema or required path.

Implementation opportunity:

```yaml
rejected_buffer:
  path: .harness/evidence/autoresearch/<run_tag>/rejected-edits.jsonl
  retention: last_20
  fields:
    - candidate_id
    - patch_summary
    - score_delta
    - rejection_reason
    - guard_status
    - evidence_refs
```

Risk: Rejected buffers can preserve benchmark-specific leakage. Redact task answers and store only generalized failure patterns unless the evidence root is private and bounded.

### Pattern: Optimizer/Target Separation

Description: A separate optimizer reads rollout evidence and proposes edits; the frozen task model only sees the current skill and task.

Evidence: SkillOpt explicitly separates optimizer model prompts from task-execution model context.

Codebase fit: Medium. The repo has strong source/projection and parent/child task language, but no optimization-role contract that prevents the worker executing tasks from also freely editing the skill.

Implementation opportunity:

```yaml
roles:
  target_runner:
    may_edit: false
    sees: [current_skill, task]
  optimizer:
    may_edit: candidate_patch_only
    sees: [rollout_evidence, current_skill, rejected_buffer]
  promoter:
    may_edit: canonical_source_after_review
```

Risk: More roles increase ceremony. Keep this as metadata first; only enforce when `optimization.enabled: true`.

### Pattern: Best Skill Export And Promotion

Description: Export a compact `best_skill.md` after validation-gated optimization, then promote deliberately.

Evidence: SkillOpt exports `best_skill.md`; deployment has zero extra inference-time calls.

Codebase fit: Low to medium. The repo has evidence artifacts and promotion gates, but no standard `best_skill.md` candidate artifact or promotion manifest for optimized skills.

Implementation opportunity:

```yaml
promotion:
  candidate_artifact: .harness/evidence/autoresearch/<run_tag>/best_skill.md
  promotion_manifest: .harness/evidence/autoresearch/<run_tag>/promotion.json
  requires:
    - strict_audit_pass
    - selection_gate_pass
    - held_out_test_report
    - human_review_for_canonical_source_edit
```

Risk: A high-scoring candidate can overfit the eval suite. Require final test results and anti-cheat checks before canonical promotion.

### Pattern: Slow/Meta Update

Description: Maintain optimizer-side memory summarizing accepted and rejected patterns, but do not ship it to the runtime skill.

Evidence: SkillOpt uses an optimizer-side meta skill to guide future edit generation; it is not the deployed artifact.

Codebase fit: Partial. The repo has memory and learning ledgers, but no optimizer-only memory boundary for skill optimization.

Implementation opportunity: Add a private optimizer-memory artifact:

```yaml
optimizer_memory:
  shipped_to_runtime: false
  path: .harness/evidence/autoresearch/<run_tag>/optimizer-meta.md
  contains:
    - accepted_patterns
    - rejected_patterns
    - persistent_failures
    - stable_successes
```

Risk: If optimizer memory becomes runtime context, it can bloat hot-path skills and leak benchmark specifics.

## Gap Register

### GAP-001: No Skill Optimization Contract Schema

Category: SDK package contract

Current state: The repo has `skill-package.v1`, `skill-package-readiness.v1`, and `skillflow.v1`, but no schema for optimization loops.

Expected state: Skills that opt into trainable improvement declare the target artifact, fixed surfaces, split policy, edit budget, acceptance gate, rejected buffer, and promotion policy.

Code evidence:

- [`Infrastructure/config/schemas/`](../../Infrastructure/config/schemas/) contains package, readiness, runtime, and skillflow schemas, but no optimization schema.
- [`Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`](../../Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py) exposes workflow metadata, not optimization metadata.

Severity: High

Recommended fix: Add `Infrastructure/config/schemas/skill-optimization-contract.v1.schema.json`, parse `optimization:` from `references/contract.yaml`, and include `optimization_contract` in `ask skills package`.

Validation command: `python3 -m unittest Infrastructure.tests.test_ask_skills_package_contract`

### GAP-002: Autoresearch Evals Are Not Package-Ready Under Current Readiness Rules

Category: validation

Current state: `ask skills package autoresearch --json --robot` reports `reference_quality.status: blocked_validation` because `references/evals.yaml` lacks top-level `claims`.

Expected state: `$autoresearch` should be package-ready before it becomes the optimizer lane for the Skills SDK.

Code evidence:

- [`Skills/agent-ops/autoresearch/references/evals.yaml`](../../Skills/agent-ops/autoresearch/references/evals.yaml) declares `schema_version`, `skill_name`, and `cases`, but no `claims`.
- The package checker reports missing `claims` and `cases`; `cases` exists, so the detector may also need normalization for this v2 eval shape.

Severity: High

Recommended fix: Add `claims` to autoresearch evals and, if needed, repair the checker so it correctly recognizes `cases` in v2 eval files.

Validation command: `./bin/ask skills package autoresearch --json --robot`

### GAP-003: No Train/Selection/Test Split Model

Category: evals

Current state: The skill tells agents to define held-out checks, but there is no declared split object or seed in the SDK.

Expected state: Optimization-enabled skills declare train, selection, and test surfaces with separate authority.

Severity: High

Recommended fix: Add split fields to `optimization_contract`; update `$autoresearch` to block when selection/test roles are conflated.

Validation command: `./bin/ask skills package autoresearch --json --robot | jq '.data.skill_package.package_contract.sdk_contract.values.optimization_contract'`

### GAP-004: No Rejected-Edit Buffer Artifact

Category: traceability

Current state: Autoresearch ledgers can record discarded attempts, but no schema requires rejected edit records or uses them as optimizer feedback.

Expected state: Every rejected candidate emits a structured JSONL record with rejection reason, score delta, guard state, and generalized failure pattern.

Severity: Medium

Recommended fix: Add `skill-optimization-ledger.v1` or include buffer fields in the optimization schema. Create a lightweight validator that checks every `discard` has `reason`, `score_delta`, `guard_status`, and `evidence_refs`.

Validation command: `python3 Infrastructure/scripts/validation-and-linting/validate_skill_optimization_ledger.py --path <evidence-dir> --json`

### GAP-005: No Best-Skill Candidate Promotion Protocol

Category: governance

Current state: The repo can patch canonical skills and record evidence, but there is no standard candidate artifact analogous to `best_skill.md`.

Expected state: Optimization runs write a candidate artifact and promotion manifest. Canonical source changes require review and validation.

Severity: Medium

Recommended fix: Standardize:

- `.harness/evidence/autoresearch/<run_tag>/best_skill.md`
- `.harness/evidence/autoresearch/<run_tag>/promotion.json`
- `.harness/evidence/autoresearch/<run_tag>/selection-results.json`
- `.harness/evidence/autoresearch/<run_tag>/test-results.json`

Validation command: `./bin/ask skills optimize promote --dry-run <run-tag> --json --robot` once the command exists.

### GAP-006: Optimizer Role Boundaries Are Prose-Only

Category: governance

Current state: `$autoresearch` says parent owns final decision and fixed surfaces are protected, but the package payload does not expose target-runner, optimizer, auditor, and promoter roles.

Expected state: Optimization metadata makes it impossible for an agent to confuse running tasks, proposing candidate patches, and promoting canonical skill changes.

Severity: Medium

Recommended fix: Add role policy under `optimization.roles` and emit it in `agent_contract` when `optimization.enabled`.

Validation command: package-contract unit test asserting role-policy fields appear.

### GAP-007: No Anti-Cheat Audit Contract

Category: safety

Current state: `$autoresearch` refuses evaluator/data/cache edits by instruction. There is no explicit machine-readable anti-cheat audit for optimized skill candidates.

Expected state: Candidate acceptance requires proving protected evaluator/data/split files did not change, and that edits do not hardcode held-out answers.

Severity: High

Recommended fix: Add `anti_cheat` to optimization contract:

```yaml
anti_cheat:
  protected_paths:
    - references/evals.yaml
    - evals/**
    - data/**
    - evaluator/**
  checks:
    - protected_paths_unchanged
    - no_answer_key_literals
    - no_selection_or_test_leakage
```

Validation command: `git diff --name-only -- <protected-paths>` plus a dedicated validator for answer leakage once task datasets are declared.

## What Is Worth Adding To The Skills SDK

### Add Now

1. `skill-optimization-contract.v1.schema.json`

This should be optional and only required when `optimization.enabled: true`.

2. `optimization_contract` in `ask skills package`

Expose status, blockers, split policy, edit policy, acceptance gate, rejected buffer path, promotion paths, and what it proves/does not prove.

3. Autoresearch package hardening

Make `$autoresearch` the first reference implementation of this contract. It should package cleanly before it becomes the sanctioned optimization lane.

4. Rejected-edit and candidate-artifact paths

These are cheap and high-signal. They make optimization runs auditable before any engine exists.

5. Anti-cheat/protected-surface gate

This is essential if the SDK allows agents to optimize skills against evals.

### Add Soon, After Contract Lands

1. `ask skills optimize doctor <handle>`

Validate whether a skill is safe to optimize before running any loop.

2. `ask skills optimize plan <handle>`

Emit the run plan: split sources, evaluator, edit budget, protected paths, stop condition, and evidence root.

3. `ask skills optimize promote --dry-run <run-tag>`

Check whether an optimized candidate can be promoted to canonical source.

4. Macro-eval integration

Connect repeated skill-failure patterns to optimizer hypotheses so the loop optimizes population-level failures, not only one-off cases.

### Defer

1. Full parallel exploration engine

Useful, but premature until the contract and evidence artifacts are stable.

2. Tree-search branch merging

Valuable for later, but a governance risk before promotion and anti-cheat gates exist.

3. Continuous 24/7 tuning

Not yet. Start with manually invoked, bounded runs and explicit promotion.

4. Automatic durable amendments

Allow autonomous adaptation inside a run. Require review for canonical skill amendment.

## Relationship To Skillflow

Skillflow and SkillOpt solve different problems and should not be conflated.

Skillflow answers:

> Which parts of this skill should execute deterministically every time?

Skill optimization answers:

> How do we safely improve the skill artifact over repeated evaluated runs?

They complement each other:

- `SKILL.md`: judgment layer and hot-path context.
- `workflows/skillflow.json`: deterministic graph for hardened mechanics.
- `optimization_contract`: safe improvement loop for skill artifacts.
- `references/evals.yaml`: scoring and behavior checks.
- `best_skill.md`: candidate output from an optimization run, not canonical source until promoted.

The SDK should let a skill be:

- prose-only
- prose plus deterministic workflow
- prose plus optimization contract
- prose plus workflow plus optimization contract

But each layer must state what it proves.

## Proposed Minimal Contract Shape

```yaml
optimization:
  enabled: true
  schema_version: "skill-optimization-contract.v1"
  target_artifact: "SKILL.md"
  optimizer_mode: "bounded_patch"
  roles:
    target_runner:
      may_edit: false
    optimizer:
      may_edit: candidate_patch_only
    promoter:
      may_edit: canonical_source_after_review
  splits:
    train:
      path: ".harness/evals/<skill>/train.jsonl"
      role: "proposal_generation"
    selection:
      path: ".harness/evals/<skill>/selection.jsonl"
      role: "candidate_acceptance"
    test:
      path: ".harness/evals/<skill>/test.jsonl"
      role: "final_report_only"
    split_seed: 42
  edit_policy:
    mode: "patch"
    operations: ["add", "delete", "replace"]
    max_edits: 4
    schedule: "cosine"
    floor: 2
  acceptance_gate:
    metric: "success_rate"
    direction: "maximize"
    rule: "strict_improvement"
    ties: "reject"
    min_delta: 0.01
    noise_runs: 3
    guard_failure: "discard"
  anti_cheat:
    protected_paths:
      - "references/evals.yaml"
      - ".harness/evals/**"
      - "data/**"
      - "evaluator/**"
    checks:
      - "protected_paths_unchanged"
      - "no_answer_key_literals"
      - "no_selection_or_test_leakage"
  evidence:
    root: ".harness/evidence/autoresearch/<run_tag>"
    rollout_jsonl: "rollouts.jsonl"
    rejected_buffer_jsonl: "rejected-edits.jsonl"
    candidate_artifact: "best_skill.md"
    promotion_manifest: "promotion.json"
  promotion:
    canonical_edit_requires_review: true
    required_checks:
      - "strict_audit_pass"
      - "selection_gate_pass"
      - "held_out_test_report"
      - "anti_cheat_pass"
```

## Implementation Roadmap

### Phase 1: Contract And Package Readiness

Objective: Make optimization readiness inspectable without running optimization.

Changes:

- Add `Infrastructure/config/schemas/skill-optimization-contract.v1.schema.json`.
- Add parser in `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`.
- Include `optimization_contract` in `sdk_contract.values`.
- Add `optimization_declared`, `optimization_status`, and `optimization_mode` to progressive disclosure.
- Add package-contract unit tests.

Validation:

```bash
python3 -m unittest Infrastructure.tests.test_ask_skills_package_contract
./bin/ask skills package autoresearch --json --robot
```

### Phase 2: Autoresearch As Reference Implementation

Objective: Make `$autoresearch` the canonical Skills SDK optimization lane.

Changes:

- Add `claims` to `Skills/agent-ops/autoresearch/references/evals.yaml`.
- Add optional `optimization:` block to `Skills/agent-ops/autoresearch/references/contract.yaml`.
- Update `Skills/agent-ops/autoresearch/SKILL.md` to distinguish setup, candidate generation, selection gate, rejected buffer, and promotion.
- Add eval cases for strict selection gate, rejected buffer, anti-cheat, and best-skill promotion.

Validation:

```bash
./bin/ask skills package autoresearch --json --robot
./bin/ask evals run Skills/agent-ops/autoresearch --mode smoke --json --robot
./bin/ask skills audit Skills/agent-ops/autoresearch --level strict --json --robot
```

### Phase 3: Evidence Validators

Objective: Make optimization run artifacts auditable.

Changes:

- Add a validator for `.harness/evidence/autoresearch/<run_tag>`.
- Require ledger records for baseline, candidate, selection gate, rejected edits, and test result.
- Add protected-path and answer-leakage checks.

Validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_skill_optimization_evidence.py .harness/evidence/autoresearch/<run-tag> --json
```

### Phase 4: Optional Command Facade

Objective: Give agents a small public spine.

Commands:

```bash
./bin/ask skills optimize doctor <handle> --json --robot
./bin/ask skills optimize plan <handle> --json --robot
./bin/ask skills optimize promote --dry-run <run-tag> --json --robot
```

Do not add a runner until these return useful contract output.

## Final Assessment

The SkillOpt paper supports the direction this repo is already taking: skills are not just markdown prompts; they are governed operational artifacts that can be evaluated, projected, optimized, and promoted.

The useful addition is not “let agents rewrite skills.” The useful addition is:

> A skill can opt into a bounded optimization contract where candidate edits are generated from rollout evidence, accepted only through held-out gates, recorded with rejected-edit evidence, and promoted only after anti-cheat and review checks.

Most immediate patch:

1. Add `skill-optimization-contract.v1.schema.json`.
2. Parse and expose `optimization_contract` in `ask skills package`.
3. Harden `$autoresearch` so it packages cleanly and becomes the reference optimization lane.

Highest-risk missing system:

- Anti-cheat/protected-surface validation. Without it, any self-improvement loop will eventually optimize the benchmark rather than the skill.

Best first validation command to add:

```bash
./bin/ask skills package autoresearch --json --robot
```

It should move from warning/blocking reference-quality output to an explicit optimization-readiness status with precise blockers.

