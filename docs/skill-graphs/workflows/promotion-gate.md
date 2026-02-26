# Promotion Gate Workflow (MVP)

Canonical promotions are human-gated and must include provenance + security evidence.

## Table of Contents

- [Inputs](#inputs)
- [Onboarding preconditions (all-skills migration)](#onboarding-preconditions-all-skills-migration)
- [Gate checks](#gate-checks)
- [Invocation boundary checks](#invocation-boundary-checks)
- [Decision states](#decision-states)
- [Commands](#commands)
- [CI enforcement](#ci-enforcement)
- [Output artifact](#output-artifact)

## Inputs

- `run.json`
- `iteration_journal.jsonl`
- candidate lesson payload
- reviewer identity

## Onboarding preconditions (all-skills migration)

Before wave promotion is allowed, verify:

1. **Per-skill profile presence**
   - `<skill>/references/task-profile.json` exists for every in-scope skill.
   - Profile validates required fields (`schema_version`, `profile_id`, `scope_skill`, `scope_profile`, `criteria[]`, `thresholds`, `delegation`).
2. **SKILL binding presence**
   - Every in-scope `SKILL.md` includes:
     - `knowledge_graph_profile: references/task-profile.json`
3. **Wave model sequencing**
   - `wave-0-controls` (control precedence + telemetry integrity) must pass before `wave-1-manual`.
   - `wave-1-manual` must pass before `wave-2-co-pilot`.
4. **Governance capacity**
   - Approver policy must include at least 2 approvers before wave promotion.
5. **Telemetry envelope integrity**
   - Decision window must report zero missing `events.jsonl` envelopes.

## Gate checks

1. **Runtime gate completeness**
   - Run has terminal status.
   - Stop reason is explicit.
2. **Evidence completeness**
   - Latest iteration includes evaluation + re-evaluation + criterion deltas.
3. **Provenance integrity**
   - Required immutable fields present (`schema_version`, `rubric_version`, `evaluator_version`, `persona_set_id`, `prompt_hash`).
4. **Security/privacy**
   - No secrets/PII in lesson body or attached logs.
   - Approved decisions must include lesson scan evidence (`lesson_source_path` + `lesson_content_sha256`).
   - Retention + redaction policy acknowledged.
5. **Reviewer checklist**
   - At least one authorized reviewer signs off.
   - Wave promotion decisions require two approvers from the allowlist.

## Invocation boundary checks

Before creating/validating a promotion decision, verify:

1. **Control files present and parsed**
   - `kill-switch.txt` (global kill switch)
   - `rollback-required.txt` (rollback requirement)
   - `rollout-mode.txt` or equivalent `--rollout-mode` override
   - auto_capture / auto_apply switches (`auto_capture.disabled`, `auto_apply.disabled`, plus per-skill switches when used)
2. **Invocation envelope completeness**
   - capture record contains:
     - `invocation_id`
     - `invocation_envelope.actor_id`
     - `invocation_envelope.rollout_mode` / `auto_capture_enabled` / `auto_apply_enabled`
   - run object records:
     - `runtime_controls`
     - `control_reasons` (or equivalent rationale field)
3. **Network + execution isolation assumptions**
   - confirm recursive run used isolated profile-scoped execution and explicit allowlist (if any external fetches occurred).
   - confirm destructive or side-effect commands had explicit run-mode guards and confirmation.

## Decision states

- `draft` -> `candidate` -> `approved`
- `draft` -> `rejected`
- `candidate` -> `rejected`

## Commands

Approve run:

```bash
bash scripts/human_promote_recursive_run.sh \
  --run-id <run_id> \
  --lesson-id <lesson_id> \
  --reviewer <reviewer_id> \
  --expected-version <version_token> \
  --lesson-file <path_to_lesson_file>
```

Validate decision directly:

```bash
python3 utilities/skill-creator/scripts/validate_recursive_promotion.py \
  --run-dir artifacts/skill-graphs/runs/<run_id> \
  --decision-file artifacts/skill-graphs/runs/<run_id>/promotion_decision.json \
  --lesson-file <path_to_lesson_file>
```

## CI enforcement

Promotion artifacts are validated in CI by:

```bash
bash scripts/validate_recursive_promotions.sh --changed-only --base-sha <base_sha> --head-sha <head_sha>
```

Workflow: `.github/workflows/recursive-promotion-gate.yml`.

## Output artifact

`promotion_decision.json` must include:

- `decision`: `approved|rejected|candidate|draft`
- `reviewer_ids[]`
- `gate_decision` summary
- `expected_version`
- security checklist fields
- provenance references (`run_id`, `iteration_ids`, `prompt_hash`)
- `lesson_source_path` and `lesson_content_sha256` for approved decisions
- confidence contract fields (`confidence.score`, `confidence.bucket`, `confidence.calibration_bucket`)
- evidence completeness linkage (`evidence_packet.evidence_packet_id`, `evidence_packet.completeness_score`)
- draft candidate payload(s) in `lesson_candidates[]` for queueing/reviewer triage
- retrieval attribution in `injected_lesson_ids[]` for traceability
- runtime control snapshot in `runtime_controls{rollout_mode, auto_capture_enabled, auto_apply_enabled}` for rollback audits
- counterfactual uplift contract: `counterfactual_uplift{treatment_outcome, control_outcome, uplift_delta, uplift_confidence_band, sample_size, match_quality_metrics, promotion_decision, auto_apply_decision}`

Approved promotions emit a deduplicated `promotion_approved` event in `run/events.jsonl`.

Related:
- [Reviewer rubric](/docs/skill-graphs/workflows/reviewer-rubric.md)
- [Human promotion guide](/docs/guides/recursive-promotion-gate.md)
- [Canonical lesson schema](/docs/skill-graphs/schemas/canonical-lesson.schema.md)
