# PU-014: Skills SDK Lens-Routed Review Receipts Spec

## Metadata

- schema_version: 1
- stage: sy-spec
- status: implemented_pending_pr
- date: 2026-06-07
- branch: codex/skills-sdk-pu-014-lens-routed-review
- worktree: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review
- target: Skills SDK review planning surface
- owner surfaces:
  - Infrastructure/scripts/lib/ask/commands/sdk.py
  - Infrastructure/scripts/lib/ask/skills_sdk/lenses.py
  - Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py
  - Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json
  - Infrastructure/tests/test_skills_sdk_review_plan.py
  - Infrastructure/config/skills-sdk/capability-matrix.v1.json
  - artifacts/recommended-skills-sdk-pipeline.html

## Approved Intent

PU-013B made SDK lenses and determinism audit visible in capability truth as implemented read-only surfaces. PU-014 makes lens selection operational by producing and hardening a bounded review plan receipt that tells an agent or maintainer what to review, which lenses apply, why they were selected, which checks are recommended, and what evidence to collect.

As of implementation, the `sdk review plan` route, schema, capability status row, and pipeline artifact row exist in this worktree. Remaining PU-014 proof is contract hardening: parsed robot envelope assertions, schema/status/artifact alignment, safe receipt write boundaries, and evidence that the route stays read-only and local-only.

## User Outcome

A maintainer can run one read-only SDK command against a target path and receive a deterministic review route receipt that can be handed to a human reviewer, a Codex reviewer, or a later governed review lane without relying on chat memory.

## Current Evidence Checked

- `git status --short --branch` in the PU-014 worktree shows only PU-014 scoped changes on `codex/skills-sdk-pu-014-lens-routed-review`.
- `ask sdk status --json --robot` in the PU-014 worktree reports `sdk_lenses`, `review_plan`, and `determinism_audit` as implemented and non-mutating.
- `Infrastructure/scripts/lib/ask/commands/sdk.py` exposes `sdk review plan` as a nested SDK command route in this worktree.
- `Infrastructure/scripts/lib/ask/skills_sdk/lenses.py` already provides deterministic `select_lenses(...)` output with selected lens ids, paths, scores, and reasons.
- `Infrastructure/tests/test_skills_sdk_lenses.py` proves lens selection and CLI envelopes; `Infrastructure/tests/test_skills_sdk_review_plan.py` proves review-plan receipt behavior.
- Existing Skills SDK public schemas live under `Infrastructure/config/schemas/skills-sdk/`.

## Requirements

### R1: Provide Read-Only Review Plan Command

Given an explicit target path or skill handle, when the operator runs:

```bash
./bin/ask sdk review plan --target <path-or-handle> --intent <intent> --json --robot
```

then the SDK must emit a successful robot JSON envelope containing `data.review_plan` with schema version `skills-sdk.review-plan-receipt.v1`.

### R2: Use Existing Lens Selection

The review plan must call the existing lens selection logic rather than duplicating lens scoring. Selected lenses must include:

- `id`
- `path`
- `score`
- `reasons`

The command must accept:

- `--target <path-or-handle>`
- `--intent <known lens task intent>`; the review-plan public schema must allow the same intent set accepted by the CLI.
- `--prompt <summary>` optional; default derived from target and intent
- `--repo-file <path>` repeatable, optional additional routing signal
- `--max-lenses <n>` default aligned with existing lens selection
- `--receipt-out <path>` optional explicit receipt write

### R3: Emit Review Route Fields

The receipt must include:

- `schema_version`
- `schema_uri`
- `status`
- `target`
- `target_kind`
- `task_intent`
- `prompt`
- `selected_lenses`
- `review_focus`
- `recommended_checks`
- `evidence_to_collect`
- `risk_flags`
- `next_commands`
- `mutation_performed: false`
- `receipt_written`
- `receipt_path`

### R4: Keep Default Path Non-Mutating

By default, the command must not write files. It may write a receipt only when `--receipt-out <path>` is supplied. If `--receipt-out` is supplied, the path must resolve inside the current repository root; outside-repo paths and unsafe traversal must be refused with a robot error.

### R5: Refuse Ambiguous or Unsafe Inputs

The command must return an error envelope when:

- `--target` is missing.
- `--intent` is outside the known lens intent set.
- `--max-lenses` is less than 1.
- `--target` is a repo-relative or absolute path that does not exist or resolves outside the repository.
- The lens catalog fails validation.
- `--receipt-out` resolves unsafely.

Missing target files may still produce a receipt only when the target is a handle-like value; the receipt must classify `target_kind` as `unresolved_handle` and include a risk flag.

### R6: Schema-Backed Public Contract

Add `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json` and validate emitted receipts against it in tests. The schema must require all public receipt fields listed in R3 and must not use open-ended placeholder-only shape.

### R7: Capability Truth Update

Update `ask sdk status` and the SDK pipeline HTML so the SDK shows a new implemented read-only capability row, recommended id:

`review_plan`

The row must make clear this is advisory/read-only review routing, not independent review completion, CI proof, or merge readiness.

### R8: Deterministic Fixtures and Tests

Add focused tests that prove:

- CLI emits a valid robot envelope.
- Receipt validates against the public schema.
- Same inputs produce stable selected lens ids and next commands.
- `--receipt-out` writes a receipt only when explicitly supplied.
- Missing or handle-like target is classified without pretending file existence.
- Invalid `--max-lenses` and unsafe receipt paths fail.
- Status and pipeline artifacts include `review_plan`.
- Every known lens task intent accepted by the CLI validates against the public review-plan receipt schema.
- A typoed repo-relative path fails instead of being downgraded to `unresolved_handle`.
- `--repo-file` values are propagated as lens-selection routing signals.
- The default builder path uses local inputs only and does not call subprocesses or outbound network helpers.
- Lens catalog failures return a robot error envelope with no receipt write.

## Non-Goals

- Do not run subagents or review swarms.
- Do not claim CodeRabbit, Codex review, GitHub review-thread, CI, or mergeability readiness.
- Do not mutate target project files.
- Do not add external service calls.
- Do not change lens scoring semantics unless required for the receipt command.
- Do not implement determinism candidate promotion in this slice; that remains a later PU.

## Affected Surface Map

| Surface | Disposition | Notes |
| --- | --- | --- |
| `Infrastructure/scripts/lib/ask/commands/sdk.py` | change | Add `sdk review plan` parser and dispatcher. |
| `Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py` | change | New read-only receipt builder. |
| `Infrastructure/scripts/lib/ask/skills_sdk/lenses.py` | read_only | Reuse `select_lenses`; avoid duplicate scoring. |
| `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json` | change | New public schema. |
| `Infrastructure/config/skills-sdk/capability-matrix.v1.json` | change | Add `review_plan` implemented row and evidence refs. |
| `Infrastructure/tests/test_skills_sdk_review_plan.py` | change | New focused command/schema/receipt tests. |
| `Infrastructure/tests/test_skills_sdk_capability_status.py` | change | Assert status row. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | change | Assert HTML status row. |
| `artifacts/recommended-skills-sdk-pipeline.html` | change | Visual truth update. |
| GitHub/CircleCI/CodeRabbit | out_of_scope | Checked only during PR green-sweep after implementation. |

## Acceptance Criteria

1. Given a skill target and validation intent, when `ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --json --robot` runs, then parsed robot JSON contains `data.review_plan.status` as `pass`, `mutation_performed` as `false`, and at least one selected lens.
2. Given identical inputs, when the command runs twice, then selected lens ids and `next_commands` are stable.
3. Given no `--receipt-out`, when the command runs, then no receipt file is written and `receipt_written` is `false`.
4. Given `--receipt-out .harness/artifacts/sdk-review-plan/sample.json`, when the command runs, then the receipt is written and validates against `sdk-review-plan-receipt.v1.schema.json`.
5. Given an unsafe receipt output path, when the command runs, then the CLI returns an error envelope and does not write a receipt.
6. Given a handle-like missing target, when the command runs, then the receipt classifies the target as `unresolved_handle` and includes a risk flag rather than claiming file evidence.
7. Given a typoed repo-relative path such as `Skills/agent-ops/simplifie`, when the command runs, then the CLI returns an error envelope instead of treating the value as a handle.
8. Given any value in the known lens task intent set, when a review plan receipt is emitted, then it validates against `sdk-review-plan-receipt.v1.schema.json`.
9. Given repeated `--repo-file` inputs, when a review plan is built, then those values are propagated to lens selection after the primary target signal.
10. Given the builder path is exercised under network and subprocess guards, when a review plan is built, then no outbound network or subprocess helper is called.
11. Given `ask sdk status --json --robot`, when it runs after implementation, then `review_plan` appears as `implemented`, `feature_executed=true`, and `mutation_performed=false`.
12. Given the pipeline artifact, when status artifact tests run, then the HTML contains the `review_plan` row as implemented advisory/read-only capability.

## Validation Commands

Focused implementation validation:

```bash
uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_review_plan.py -q
uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q
./bin/ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --json --robot
./bin/ask sdk status --json --robot
bash scripts/validate-codestyle.sh --fast
```

PR or closeout validation, separate lane:

```bash
./bin/ask repo validate --json --robot
gh pr checks <pr-number> --watch=false
```

## Evidence Limits

- Local tests prove the SDK receipt contract and CLI behavior only.
- Local HTML files prove artifact content only after the file is inspected or rendered.
- Local validation does not prove GitHub CI, CircleCI, CodeRabbit, review-thread state, or mergeability.
- A review plan receipt recommends review actions; it is not itself review completion.

## Risks

- The new command could overclaim review readiness if receipt wording is not explicit.
- A receipt writer could accidentally permit writes outside the intended path.
- Duplicating lens scoring would create drift between `sdk lenses select` and `sdk review plan`.
- Adding another status row without artifact tests could recreate the truth drift PU-013B fixed.

## Rollback

Revert the PU-014 commit. This removes the review plan command, schema, tests, status row, and artifact update without affecting existing `sdk lenses`, `sdk determinism`, install, rollback, uninstall, or project conformance behavior.

## Blocked Inputs

None for spec and trace planning. Implementation may expose existing full-repo validation blockers; those must be classified separately from PU-014 changes.

## Next Stage

Prepare the implemented PU-014 worktree for PR: stage only PU-014 changes, commit, push `codex/skills-sdk-pu-014-lens-routed-review`, open the PR, and run the PR green-sweep lane separately from local implementation proof.
